#!/usr/bin/env python3
"""Verify next skill-worker iteration artifacts are constraint-grounded."""

from __future__ import annotations

from pathlib import Path

from workbench_common import fail_or_print, read_json, read_yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "real_task_001_upgrade" / "skill_worker_iter02"


def main() -> int:
    context = read_json(REPO_ROOT / "workbench_data" / "topics" / "real-task-001" / "skill_worker_context.json")
    request = read_yaml(ROOT / "skill_agent_iteration_request.yaml")
    plan = read_yaml(ROOT / "skill_iteration_plan.yaml")
    ablation = read_yaml(ROOT / "ablation_plan.yaml")
    pack = read_yaml(ROOT / "agent_context_pack.skill_worker.yaml")
    issues: list[str] = []

    target = context["skill_target"]
    evidence = context["evidence_boundary"]
    if request["base_skill_ref"] != target["active_skill_ref"]:
        issues.append("request base_skill_ref does not match skill_worker_context active skill")
    if target["candidate_family"] not in ablation["variants"]:
        issues.append("ablation plan does not include the target candidate family")
    if "uniform_q_support_equal_effort" not in ablation["variants"]:
        issues.append("ablation plan lacks uniform_q_support equal-effort baseline")
    if "control_effort" not in ablation["required_metrics"]:
        issues.append("ablation plan lacks control_effort metric")
    if evidence.get("primary_delta") != 0.0:
        issues.append("context primary_delta boundary changed unexpectedly")
    if evidence.get("boundary_triggered") is not False:
        issues.append("context boundary_triggered boundary changed unexpectedly")

    blocked = " ".join(request.get("blocked_paths", []) + plan.get("blocked_paths", []) + pack.get("blocked_paths", []))
    if "q_step-only escalation" not in blocked:
        issues.append("blocked paths do not include q_step-only escalation")
    if "verified structural skill improvement" not in " ".join(ablation.get("claim_blocked_until_passed", [])):
        issues.append("ablation plan does not block verified structural skill improvement claim")
    if "hosting-capacity boundary improvement" not in " ".join(ablation.get("claim_blocked_until_passed", [])):
        issues.append("ablation plan does not block hosting-capacity boundary improvement claim")
    if "equal or bounded control effort" not in " ".join(request.get("required_tests", []) + plan.get("success_criteria", [])):
        issues.append("request/plan does not require equal or bounded control effort")

    return fail_or_print(
        issues,
        {
            "status": "passed",
            "request_ref": request["object_id"],
            "plan_ref": plan["object_id"],
            "ablation_ref": ablation["object_id"],
            "candidate_family": target["candidate_family"],
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
