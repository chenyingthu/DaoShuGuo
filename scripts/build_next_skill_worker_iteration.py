#!/usr/bin/env python3
"""Build the next skill-worker iteration artifacts from workbench context."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from workbench_common import read_json, topic_dir, utc_now, write_yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OBJECT_VERSION = "0.1.0"
TASK_REF = "task.power.ieee69_hosting_capacity"
EVALUATOR_REF = "evaluator.power.ieee69_hosting_capacity.default"
BASELINE_REF = "baseline.power.ieee69_hosting_capacity.fixed_inverter_q_capacity_scan"
STRUCTURAL_REQUEST_REF = "structural_skill_change_request.power.ieee69_hosting_capacity.reframing_0001"
ITER01_RESULT_REF = "skill_change_result.power.ieee69_hosting_capacity_upgrade.0001"


def base_object(object_type: str, object_id: str, status: str) -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": OBJECT_VERSION,
        "object_type": object_type,
        "object_id": object_id,
        "object_version": OBJECT_VERSION,
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": {
            "real_task": "real-task-001-upgrade",
            "iteration": 2,
            "source_context_path": "workbench_data/topics/real-task-001/skill_worker_context.json",
        },
    }


def load_context(topic: str) -> dict[str, Any]:
    path = topic_dir(topic) / "skill_worker_context.json"
    if not path.exists():
        raise RuntimeError(f"missing {path}; run scripts/build_skill_worker_context.py --topic {topic}")
    context = read_json(path)
    if not isinstance(context, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return context


def flattened_constraints(context: dict[str, Any], names: tuple[str, ...]) -> list[str]:
    grouped = context.get("routing_constraints", {})
    values: list[str] = []
    for name in names:
        for item in grouped.get(name, []):
            content = item.get("content")
            if isinstance(content, str) and content not in values:
                values.append(content)
    return values


def build_request(context: dict[str, Any]) -> dict[str, Any]:
    target = context["skill_target"]
    requirements = context["skill_change_requirements"]
    must_do = flattened_constraints(context, ("must_do", "prefer"))
    blocked = context["evidence_boundary"].get("forbidden_shortcuts", []) + flattened_constraints(context, ("must_not_do",))
    request = base_object(
        "skill_agent_iteration_request",
        "skill_agent_iteration_request.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    request["metadata"].update(
        {
            "active_skill_ref": target["active_skill_ref"],
            "candidate_family": target["candidate_family"],
            "skill_worker_context_path": "workbench_data/topics/real-task-001/skill_worker_context.json",
            "prior_result_ref": ITER01_RESULT_REF,
        }
    )
    request.update(
        {
            "task_ref": TASK_REF,
            "source_update_ref": STRUCTURAL_REQUEST_REF,
            "iteration_index": 2,
            "base_skill_ref": target["active_skill_ref"],
            "allowed_change_scope": ["method_change", "process_change", "standard_change"],
            "blocked_paths": blocked,
            "required_tests": requirements.get("required_validation", []) + must_do,
            "output_skill_path": "skills/active_dev/voltage_sensitivity_capacity_optimizer_task004.py",
            "summary": (
                "Use the workbench skill-worker context to redesign the voltage-sensitivity "
                "candidate under equal-effort, boundary-triggering, and claim-boundary constraints."
            ),
        }
    )
    return request


def build_research_batch() -> dict[str, Any]:
    batch = base_object(
        "research_batch",
        "research_batch.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    batch["metadata"].update({"protocol": "skill-centered-workbench", "source": "workbench_skill_worker_context"})
    batch.update(
        {
            "plan_ref": "skill_iteration_plan.power.ieee69_hosting_capacity.skill_worker.0002",
            "batch_index": 2,
            "task_ref": TASK_REF,
            "batch_goal": "Prepare a bounded next skill-worker iteration from workbench constraints.",
            "worker_sequence": ["skill_worker", "effectiveness_worker", "cognition_worker"],
            "required_outputs": [
                "skill_agent_iteration_request",
                "skill_agent_iteration_result",
                "ablation_result",
            ],
            "review_gate_required": True,
        }
    )
    return batch


def build_iteration_plan(context: dict[str, Any], request_ref: str) -> dict[str, Any]:
    target = context["skill_target"]
    requirements = context["skill_change_requirements"]
    evidence = context["evidence_boundary"]
    plan = base_object(
        "skill_iteration_plan",
        "skill_iteration_plan.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    plan["metadata"].update(
        {
            "request_ref": request_ref,
            "primary_delta_before": evidence.get("primary_delta"),
            "boundary_triggered_before": evidence.get("boundary_triggered"),
        }
    )
    plan.update(
        {
            "task_ref": TASK_REF,
            "controller_update_ref": STRUCTURAL_REQUEST_REF,
            "target_skill_family": target["candidate_family"],
            "planned_actions": [
                "Preserve voltage_sensitivity_q_allocation as the candidate family.",
                "Run equal-effort comparison against uniform_q_support before any claim upgrade.",
                "Add or select an extended-until-violation and boundary-neighborhood scenario for validation.",
                "Write the next skill change result with method, process, and standard changes separated.",
            ],
            "planned_validation": requirements.get("required_validation", []),
            "blocked_paths": context["evidence_boundary"].get("forbidden_shortcuts", []) + flattened_constraints(context, ("must_not_do",)),
            "candidate_skill_refs": ["skill.power.voltage_sensitivity_capacity_optimizer_task004"],
            "success_criteria": [
                "A baseline and candidate run both include explicit last-feasible and first-violation boundary evidence.",
                "Candidate comparison is made under equal or bounded control effort.",
                "Primary hosting-capacity, secondary operational-quality, and control-effort metrics are reported separately.",
                "No structural skill improvement is claimed unless primary boundary evidence changes.",
            ],
            "summary": "Plan the next skill-worker iteration around boundary-triggering evidence and equal-effort candidate comparison.",
        }
    )
    return plan


def build_runtime_binding() -> dict[str, Any]:
    binding = base_object(
        "worker_runtime_binding",
        "worker_runtime_binding.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    binding["metadata"].update({"protocol": "skill-centered-workbench", "context_artifact": "skill_worker_context.json"})
    binding.update(
        {
            "batch_ref": "research_batch.power.ieee69_hosting_capacity.skill_worker.0002",
            "worker_role": "skill_worker",
            "runtime_kind": "codex_cli",
            "provider": "openai",
            "model": "gpt-5.5",
            "tool_permission_profile": "workspace-write",
            "session_reuse_policy": "reuse_current_session",
            "timeout_seconds": 1800,
            "retry_policy": {"max_attempts": 1, "retry_on": ["runtime_timeout"]},
            "raw_transcript_path": "analysis/real_task_001_upgrade/skill_worker_iter02/raw/skill_worker.raw.txt",
        }
    )
    return binding


def build_context_pack(context: dict[str, Any], request_ref: str, runtime_ref: str) -> dict[str, Any]:
    target = context["skill_target"]
    pack = base_object(
        "agent_context_pack",
        "agent_context_pack.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    pack["metadata"].update({"request_ref": request_ref, "skill_status": target["skill_status"]})
    pack.update(
        {
            "batch_ref": "research_batch.power.ieee69_hosting_capacity.skill_worker.0002",
            "worker_role": "skill_worker",
            "runtime_binding_ref": runtime_ref,
            "mission": "Produce the next bounded skill change without weakening evaluator or claim gates.",
            "role_boundary": context["worker_role_boundary"]["allowed"] + context["worker_role_boundary"]["not_allowed"],
            "task_refs": [TASK_REF],
            "prior_artifact_refs": context["source_refs"].get("skill_source_refs", []) + [ITER01_RESULT_REF],
            "allowed_changes": context["skill_change_requirements"].get("method_changes", [])[:3],
            "blocked_paths": context["evidence_boundary"].get("forbidden_shortcuts", []) + flattened_constraints(context, ("must_not_do",)),
            "evaluator_refs": [EVALUATOR_REF],
            "baseline_refs": [BASELINE_REF],
            "review_history_refs": context["source_refs"].get("loop_constraint_refs", []),
            "current_hypothesis": (
                "Voltage-sensitivity allocation may become a reusable structural candidate only if it survives "
                "equal-effort and boundary-triggering validation."
            ),
            "required_output_schema_ref": "schema.skill_agent_iteration_result",
            "stop_conditions": [
                "missing evaluator reference",
                "attempt to claim verified structural improvement before boundary evidence changes",
                "candidate comparison lacks equal or bounded control effort",
            ],
            "token_budget": 12000,
            "context_budget": 24000,
            "artifact_provenance_digest": "workbench_data/topics/real-task-001/skill_worker_context.json",
            "redaction_policy": "Do not include secrets or provider tokens.",
            "expected_failure_modes": [
                "overclaiming secondary metrics",
                "treating q_step-only escalation as skill improvement",
                "missing first-violation boundary evidence",
            ],
            "previous_repair_attempt_refs": [],
            "rendered_prompt_path": "analysis/real_task_001_upgrade/skill_worker_iter02/prompts/skill_worker.prompt.md",
        }
    )
    return pack


def build_ablation_plan(context: dict[str, Any], plan_ref: str) -> dict[str, Any]:
    ablation = base_object(
        "ablation_plan",
        "ablation_plan.power.ieee69_hosting_capacity.skill_worker.0002",
        "ready",
    )
    ablation["metadata"].update({"skill_iteration_plan_ref": plan_ref})
    ablation.update(
        {
            "task_ref": TASK_REF,
            "source_review_ref": "loop_review.power.ieee69_hosting_capacity_upgrade.0001",
            "hypothesis": (
                "Voltage-sensitivity allocation improves reusable skill structure only if it beats uniform support "
                "under the same evaluator and equal or bounded control effort."
            ),
            "controlled_variables": [
                "same evaluator",
                "same renewable scale envelope",
                "same or bounded total reactive support effort",
                "same boundary-neighborhood scenario",
            ],
            "variants": [
                "fixed_q_baseline",
                "uniform_q_support_equal_effort",
                context["skill_target"]["candidate_family"],
            ],
            "required_metrics": [
                "hosting_capacity_level",
                "boundary_trigger_scale",
                "first_violation_type",
                "loss_at_boundary",
                "voltage_margin",
                "control_effort",
            ],
            "claim_allowed_if_passed": [
                "candidate shows bounded evidence for a reusable structural method change under this evaluator"
            ],
            "claim_blocked_until_passed": [
                "verified structural skill improvement",
                "hosting-capacity boundary improvement",
                "paper-candidate result",
            ],
        }
    )
    return ablation


def render_prompt(context: dict[str, Any], request: dict[str, Any], plan: dict[str, Any]) -> str:
    return f"""# Skill Worker Iteration 0002

Read `workbench_data/topics/real-task-001/skill_worker_context.json` before editing code.

## Mission

{request["summary"]}

## Target

- active skill: {context["skill_target"]["active_skill_ref"]}
- candidate family: {context["skill_target"]["candidate_family"]}
- current status: {context["skill_target"]["skill_status"]}

## Required Output

Produce a `skill_agent_iteration_result` for `{request["object_id"]}`.

## Must Do

{yaml.safe_dump(context["routing_constraints"].get("must_do", []), sort_keys=False, allow_unicode=True)}

## Must Not Do

{yaml.safe_dump(context["routing_constraints"].get("must_not_do", []), sort_keys=False, allow_unicode=True)}

## Evidence Boundary

{yaml.safe_dump(context["evidence_boundary"], sort_keys=False, allow_unicode=True)}

## Success Criteria

{yaml.safe_dump(plan["success_criteria"], sort_keys=False, allow_unicode=True)}
"""


def write_outputs(topic: str, *, dry_run: bool) -> list[Path]:
    context = load_context(topic)
    root = REPO_ROOT / "analysis" / "real_task_001_upgrade" / "skill_worker_iter02"
    batch = build_research_batch()
    request = build_request(context)
    plan = build_iteration_plan(context, request["object_id"])
    runtime = build_runtime_binding()
    pack = build_context_pack(context, request["object_id"], runtime["object_id"])
    ablation = build_ablation_plan(context, plan["object_id"])
    prompt = render_prompt(context, request, plan)
    outputs = [
        (root / "research_batch.yaml", batch),
        (root / "skill_agent_iteration_request.yaml", request),
        (root / "skill_iteration_plan.yaml", plan),
        (root / "worker_runtime_binding.skill_worker.yaml", runtime),
        (root / "agent_context_pack.skill_worker.yaml", pack),
        (root / "ablation_plan.yaml", ablation),
    ]
    paths = [path for path, _ in outputs] + [root / "prompts" / "skill_worker.prompt.md"]
    if not dry_run:
        for path, payload in outputs:
            write_yaml(path, payload)
        (root / "prompts").mkdir(parents=True, exist_ok=True)
        (root / "prompts" / "skill_worker.prompt.md").write_text(prompt, encoding="utf-8")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="real-task-001")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    paths = write_outputs(args.topic, dry_run=args.dry_run)
    print(
        yaml.safe_dump(
            {
                "status": "built",
                "topic": args.topic,
                "paths": [str(path.relative_to(REPO_ROOT)) for path in paths],
                "dry_run": args.dry_run,
            },
            sort_keys=False,
            allow_unicode=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
