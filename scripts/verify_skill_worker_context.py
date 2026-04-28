#!/usr/bin/env python3
"""Verify the workbench emits a consumable skill-worker context."""

from __future__ import annotations

from apply_workbench_constraints_to_loop import build_skill_worker_context
from workbench_common import fail_or_print, read_json, topic_dir


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    path = topic_dir(args.topic) / "skill_worker_context.json"
    context = read_json(path) if path.exists() and not args.dry_run else build_skill_worker_context(args.topic, allow_dry_run_fallback=args.dry_run)
    issues: list[str] = []

    if context.get("target_worker") != "skill_worker":
        issues.append("context does not target skill_worker")
    if context.get("status") != "ready":
        issues.append(f"context status is not ready: {context.get('status')}")

    skill_target = context.get("skill_target", {})
    evidence = context.get("evidence_boundary", {})
    constraints = context.get("routing_constraints", {})

    if args.topic == "real-task-001":
        if skill_target.get("active_skill_ref") != "skill.power.renewable_capacity_optimizer_task004":
            issues.append("active skill is not propagated to skill worker context")
        if skill_target.get("candidate_family") != "voltage_sensitivity_q_allocation":
            issues.append("candidate family is not propagated to skill worker context")
        if skill_target.get("skill_status") == "verified_structural_improvement":
            issues.append("context inflates skill status to verified structural improvement")
        if evidence.get("primary_delta") != 0.0:
            issues.append("primary_delta boundary is not preserved")
        if evidence.get("boundary_triggered") is not False:
            issues.append("boundary_triggered=false is not preserved")
        forbidden = " ".join(evidence.get("forbidden_claims", []) + evidence.get("forbidden_shortcuts", []))
        if "hosting-capacity boundary improvement" not in forbidden:
            issues.append("forbidden claims do not block hosting-capacity boundary improvement")
        if not constraints.get("must_do"):
            issues.append("skill worker context has no must_do constraints")
        if not constraints.get("must_not_do"):
            issues.append("skill worker context has no must_not_do constraints")
        merged_constraints = " ".join(
            item.get("content", "")
            for group in constraints.values()
            for item in group
        )
        if "equal or bounded control effort" not in merged_constraints:
            issues.append("equal or bounded control effort constraint is missing")
        if "boundary_triggered=true" not in merged_constraints:
            issues.append("boundary_triggered=true claim gate is missing")

    return fail_or_print(
        issues,
        {
            "status": "passed",
            "topic": args.topic,
            "target_worker": context.get("target_worker"),
            "constraint_count": len(context.get("active_routing_constraint_refs", [])),
            "active_skill_ref": skill_target.get("active_skill_ref"),
            "candidate_family": skill_target.get("candidate_family"),
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
