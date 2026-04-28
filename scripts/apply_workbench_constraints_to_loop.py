#!/usr/bin/env python3
"""Build next-loop context from active workbench routing constraints."""

from __future__ import annotations

import json
from typing import Any

from workbench_common import (
    WORKBENCH_ROOT,
    default_human_object,
    ensure_topic,
    read_yaml,
    rel,
    skill_for_topic,
    topic_dir,
    write_json,
)


def active_constraints(topic: str) -> list[dict[str, Any]]:
    root = WORKBENCH_ROOT / "routing_constraints"
    if not root.exists():
        return []
    constraints = []
    for path in sorted(root.glob(f"routing_constraint.{topic}.*.yaml")):
        obj = read_yaml(path)
        if obj.get("active") and obj.get("status") == "active":
            constraints.append(obj)
    return constraints


def build_context(topic: str, *, allow_dry_run_fallback: bool = False) -> dict[str, Any]:
    topic_obj = ensure_topic(topic)
    constraints = active_constraints(topic)
    if not constraints and allow_dry_run_fallback:
        human = default_human_object("direction_override", topic)
        # Do not persist the fallback object; build a representative constraint from the default intervention.
        constraints = [
            {
                "object_id": f"routing_constraint.{topic}.dry_run.0",
                "applies_to_stage": "loop",
                "constraint_type": "must_do",
                "priority": "high",
                "content": human["new_constraints"][0],
                "source_human_object_ref": human["object_id"],
            }
        ]
    return {
        "topic_id": topic,
        "topic_ref": topic_obj["object_id"],
        "status": "ready" if constraints else "degraded_no_active_constraints",
        "active_routing_constraint_refs": [item["object_id"] for item in constraints],
        "constraint_summaries": [
            {
                "stage": item["applies_to_stage"],
                "type": item["constraint_type"],
                "priority": item["priority"],
                "content": item["content"],
                "source_human_object_ref": item["source_human_object_ref"],
                "target_worker": item.get("metadata", {}).get("target_worker", "unspecified"),
                "active_skill_ref": item.get("metadata", {}).get("active_skill_ref", "unspecified"),
            }
            for item in constraints
        ],
        "next_loop_instruction": "Respect active human routing constraints before generating skill/cognition actions.",
    }


def group_constraints_for_skill_worker(constraints: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {
        "must_do": [],
        "must_not_do": [],
        "prefer": [],
        "require_evidence": [],
        "claim_limit": [],
        "pause_condition": [],
    }
    for item in constraints:
        target_worker = item.get("metadata", {}).get("target_worker")
        stage = item.get("applies_to_stage")
        constraint_type = item.get("constraint_type")
        if target_worker != "skill_worker" and stage not in {"skill", "evaluation", "delivery"}:
            continue
        if constraint_type not in grouped:
            continue
        grouped[constraint_type].append(
            {
                "constraint_ref": item["object_id"],
                "stage": stage,
                "priority": item.get("priority", "medium"),
                "content": item.get("content", ""),
                "source_human_object_ref": item.get("source_human_object_ref", ""),
            }
        )
    return grouped


def build_skill_worker_context(topic: str, *, allow_dry_run_fallback: bool = False) -> dict[str, Any]:
    topic_obj = ensure_topic(topic)
    skill = skill_for_topic(topic)
    loop_context = build_context(topic, allow_dry_run_fallback=allow_dry_run_fallback)
    constraints = active_constraints(topic)
    if not constraints and allow_dry_run_fallback:
        human = default_human_object("direction_override", topic)
        constraints = [
            {
                "object_id": f"routing_constraint.{topic}.dry_run.0",
                "applies_to_stage": "skill",
                "constraint_type": "must_do",
                "priority": "high",
                "content": human["new_constraints"][0],
                "source_human_object_ref": human["object_id"],
                "metadata": human.get("metadata", {}),
            }
        ]
    grouped = group_constraints_for_skill_worker(constraints)
    metric_evidence = skill.get("metric_evidence", {})
    constraint_refs = [
        item["constraint_ref"]
        for items in grouped.values()
        for item in items
    ]
    status = "ready" if constraint_refs and skill.get("active_skill_ref") != "unknown" else "degraded"
    return {
        "topic_id": topic,
        "topic_ref": topic_obj["object_id"],
        "status": status,
        "target_worker": "skill_worker",
        "worker_role_boundary": {
            "allowed": [
                "Propose skill change requests.",
                "Separate method, process, and standard changes.",
                "Prepare candidate skill variants for evaluator comparison.",
            ],
            "not_allowed": [
                "Claim effectiveness without evaluator evidence.",
                "Summarize cognition diagnosis as if it were verified skill improvement.",
                "Change claim ceiling or taste grade directly.",
            ],
        },
        "skill_target": {
            "active_skill_ref": skill.get("active_skill_ref", "unknown"),
            "candidate_family": skill.get("candidate_family", "unknown"),
            "candidate_dimension": skill.get("candidate_dimension", "unknown"),
            "skill_status": skill.get("skill_status", "unknown"),
            "next_action": skill.get("next_action", "unknown"),
        },
        "skill_change_requirements": {
            "method_changes": skill.get("method_changes", []),
            "process_changes": skill.get("process_changes", []),
            "standard_changes": skill.get("standard_changes", []),
            "required_validation": skill.get("required_validation", []),
        },
        "evidence_boundary": {
            "primary_delta": metric_evidence.get("primary_delta"),
            "boundary_triggered": metric_evidence.get("boundary_triggered"),
            "control_effort_delta": metric_evidence.get("control_effort_delta"),
            "skill_use_vs_structure_judgment": skill.get("skill_use_vs_structure_judgment", ""),
            "forbidden_claims": skill.get("forbidden_claims", []),
            "forbidden_shortcuts": skill.get("forbidden_shortcuts", []),
        },
        "routing_constraints": grouped,
        "active_routing_constraint_refs": constraint_refs,
        "source_refs": {
            "skill_source_refs": skill.get("source_refs", []),
            "loop_constraint_refs": loop_context.get("active_routing_constraint_refs", []),
            "topic_ref": topic_obj["object_id"],
        },
        "worker_instruction": (
            "Before generating the next candidate, satisfy the must_do constraints, reject the must_not_do paths, "
            "and keep the result at structural_attempt_not_verified unless evaluator evidence changes primary_delta "
            "and boundary_triggered."
        ),
    }


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    context = build_context(args.topic, allow_dry_run_fallback=args.dry_run)
    output = topic_dir(args.topic) / "loop_context.json"
    skill_worker_output = topic_dir(args.topic) / "skill_worker_context.json"
    if not args.dry_run:
        write_json(output, context)
        write_json(skill_worker_output, build_skill_worker_context(args.topic, allow_dry_run_fallback=False))
    print(json.dumps({"status": context["status"], "topic": args.topic, "constraint_count": len(context["active_routing_constraint_refs"]), "path": rel(output), "skill_worker_context_path": rel(skill_worker_output), "dry_run": args.dry_run}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
