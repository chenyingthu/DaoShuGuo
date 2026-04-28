#!/usr/bin/env python3
"""Run the research-plan-execute review gate for the MVP task003 batch.

The gate evaluates evidence and routing rules only. It does not repair
artifacts, modify skills, or create the next skill request.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02"
TASK_REF = "task.power.ieee69_renewable_reactive_opt"
CASE_ID = "power.ieee69_renewable_reactive_opt.0002"
CAUSAL_CLAIMS = [
    "cognition caused skill improvement",
    "research taste improved the method",
    "agent autonomously discovered a superior principle",
]
REPAIR_VERDICTS = {
    "needs_fix",
    "stagnation",
    "cheating_suspected",
    "insufficient_evidence",
    "pause_for_human_review",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to an object")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path.relative_to(REPO_ROOT)}")


def metric_improved(metrics: dict[str, Any]) -> tuple[bool, list[str]]:
    baseline = metrics.get("baseline_solution", {}).get("metrics", {})
    candidate = metrics.get("candidate_solution", {}).get("metrics", {})
    evidence: list[str] = []
    checks = [
        ("loss", "lower"),
        ("voltage_deviation", "lower"),
        ("constraint_violation", "not_greater"),
    ]
    passed = True
    for key, direction in checks:
        base_value = baseline.get(key)
        candidate_value = candidate.get(key)
        if not isinstance(base_value, (int, float)) or not isinstance(candidate_value, (int, float)):
            evidence.append(f"{key}: missing numeric comparison")
            passed = False
            continue
        if direction == "lower":
            ok = candidate_value < base_value
        else:
            ok = candidate_value <= base_value
        evidence.append(f"{key}: {base_value} -> {candidate_value}")
        passed = passed and ok
    return passed, evidence


def has_ablation_result() -> bool:
    return any(ROOT.glob("ablation_result*.yaml"))


def collect_inputs() -> dict[str, Any]:
    paths = {
        "batch": ROOT / "research_batch.yaml",
        "ledger": ROOT / "execution_ledger.yaml",
        "skill_result": REPO_ROOT / "agents" / "skill" / "results" / "task003_iter02.yaml",
        "cognition_update": REPO_ROOT
        / "analysis"
        / "agentic_loop"
        / "task003"
        / "updates"
        / "iter02.yaml",
        "loop_review": REPO_ROOT
        / "analysis"
        / "agentic_loop"
        / "task003"
        / "reviews"
        / "iter02.yaml",
        "run": REPO_ROOT / "runs" / "task003" / "run_0021" / "run.yaml",
        "metrics": REPO_ROOT / "runs" / "task003" / "run_0021" / "metrics.json",
        "review_context": ROOT / "agent_context_pack.review_worker.yaml",
    }
    for path in paths.values():
        require(path)
    return {
        "batch": load_yaml(paths["batch"]),
        "ledger": load_yaml(paths["ledger"]),
        "skill_result": load_yaml(paths["skill_result"]),
        "cognition_update": load_yaml(paths["cognition_update"]),
        "loop_review": load_yaml(paths["loop_review"]),
        "run": load_yaml(paths["run"]),
        "metrics": load_json(paths["metrics"]),
        "review_context": load_yaml(paths["review_context"]),
    }


def decide_review(inputs: dict[str, Any]) -> dict[str, Any]:
    evidence_summary: list[str] = []
    required_repairs: list[str] = []
    required_ablations: list[str] = []
    claim_boundary = [
        "Allowed: skill performance improved under the current task003 evaluator and single representative condition.",
        "Classified: current improvement is skill-use improvement, not verified skill-structure improvement.",
        "Blocked: cognition caused skill improvement until an ablation_result exists.",
        "Blocked: method/process/standard improved until the review identifies a structural change beyond search-envelope expansion.",
        "Blocked: general renewable reactive optimization superiority beyond task003 single-condition evidence.",
    ]

    metric_ok, metric_evidence = metric_improved(inputs["metrics"])
    evidence_summary.extend(metric_evidence)
    skill_result = inputs["skill_result"]
    loop_review = inputs["loop_review"]
    cognition_update = inputs["cognition_update"]

    raw_output = skill_result.get("raw_output_path")
    if not isinstance(raw_output, str) or not (REPO_ROOT / raw_output).exists():
        required_repairs.append("repair_runtime_binding")
        evidence_summary.append("missing raw skill-agent transcript")
    else:
        evidence_summary.append(f"raw skill-agent transcript exists: {raw_output}")

    if loop_review.get("verdict") == "cheating_suspected" or loop_review.get("cheating_signals"):
        verdict = "cheating_suspected"
        required_repairs.append("human_review")
    elif not metric_ok:
        verdict = "needs_fix"
        required_repairs.append("repair_skill")
    elif not cognition_update.get("required_discriminating_tests"):
        verdict = "insufficient_evidence"
        required_repairs.append("repair_cognition_prompt")
    elif not has_ablation_result():
        verdict = "approved_with_ablation_required"
        required_ablations.append(
            "Compare cognition-guided request against a metric-only or deterministic request under the same evaluator and fixed search budget."
        )
    else:
        verdict = "approved"

    if required_repairs and verdict not in REPAIR_VERDICTS:
        verdict = "needs_fix"

    approval_allowed = verdict in {"approved", "approved_with_ablation_required"}
    if verdict == "real_progress":
        approval_allowed = False

    return {
        "verdict": verdict,
        "approval_allowed": approval_allowed,
        "evidence_summary": evidence_summary,
        "claim_boundary": claim_boundary,
        "required_repairs": sorted(set(required_repairs)),
        "required_ablations": required_ablations,
    }


def build_review(inputs: dict[str, Any], decision: dict[str, Any], now: str) -> dict[str, Any]:
    reviewed_refs = [
        inputs["batch"]["object_id"],
        inputs["review_context"]["object_id"],
        inputs["skill_result"]["object_id"],
        inputs["run"]["object_id"],
        inputs["cognition_update"]["object_id"],
        inputs["loop_review"]["object_id"],
    ]
    return {
        "schema_version": "0.1.0",
        "object_type": "research_review",
        "object_id": f"research_review.{CASE_ID}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {
            "protocol": "research-plan-execute",
            "task_package": "task003",
            "gate": "phase3_mvp",
        },
        "batch_ref": inputs["batch"]["object_id"],
        "reviewed_artifact_refs": reviewed_refs,
        "verdict": decision["verdict"],
        "evidence_summary": decision["evidence_summary"],
        "claim_boundary": decision["claim_boundary"],
        "required_repairs": decision["required_repairs"],
        "required_ablations": decision["required_ablations"],
        "approval_allowed": decision["approval_allowed"],
        "summary": (
            "Review gate approves continued execution only with ablation-required causality freeze."
            if decision["verdict"] == "approved_with_ablation_required"
            else f"Review gate verdict: {decision['verdict']}"
        ),
    }


def build_approval(review: dict[str, Any], now: str) -> dict[str, Any]:
    approval_type = (
        "approved" if review["verdict"] == "approved" else "approved_with_ablation_required"
    )
    status = "approved" if approval_type == "approved" else "bounded"
    return {
        "schema_version": "0.1.0",
        "object_type": "approval_record",
        "object_id": f"approval_record.{CASE_ID}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": {"protocol": "research-plan-execute", "task_package": "task003"},
        "batch_ref": review["batch_ref"],
        "source_review_ref": review["object_id"],
        "approval_type": approval_type,
        "approved_next_state": "bounded_next_iteration" if status == "bounded" else "next_iteration",
        "evidence_refs": review["reviewed_artifact_refs"],
        "frozen_claims": CAUSAL_CLAIMS if status == "bounded" else [],
        "summary": "Execution may continue, but cognition-causality claims remain frozen until ablation passes.",
    }


def build_repair_request(review: dict[str, Any], now: str) -> dict[str, Any]:
    repair_type = review["required_repairs"][0] if review["required_repairs"] else "human_review"
    return {
        "schema_version": "0.1.0",
        "object_type": "repair_request",
        "object_id": f"repair_request.{CASE_ID}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {"protocol": "research-plan-execute", "task_package": "task003"},
        "batch_ref": review["batch_ref"],
        "source_review_ref": review["object_id"],
        "repair_type": repair_type,
        "attempt_index": 1,
        "max_auto_attempts": 2,
        "issue_summary": review["summary"],
        "required_actions": review["required_repairs"] or ["human_review"],
        "blocked_fixes": [
            "Do not weaken evaluator criteria.",
            "Do not delete required references.",
            "Do not convert metric improvement into cognition causality.",
        ],
    }


def update_ledger(inputs: dict[str, Any], review: dict[str, Any], now: str, terminal_ref: str) -> None:
    ledger = inputs["ledger"]
    events = list(ledger.get("events", []))
    events.append({"at": now, "state": "review_completed", "artifact_ref": review["object_id"]})
    if review["approval_allowed"]:
        current_state = "approved"
        events.append({"at": now, "state": "approved", "artifact_ref": terminal_ref})
    else:
        current_state = "repair_requested"
        events.append({"at": now, "state": "repair_requested", "artifact_ref": terminal_ref})
    ledger["updated_at"] = now
    ledger["current_state"] = current_state
    ledger["events"] = events
    write_yaml(ROOT / "execution_ledger.yaml", ledger)


def run_gate(task: str, iteration: int) -> Path:
    if task != "task003" or iteration != 2:
        raise RuntimeError("MVP supports only --task task003 --iteration 2")
    inputs = collect_inputs()
    now = utc_now()
    decision = decide_review(inputs)
    review = build_review(inputs, decision, now)
    review_path = ROOT / "research_review.yaml"
    write_yaml(review_path, review)

    if review["approval_allowed"]:
        approval = build_approval(review, now)
        approval_path = ROOT / "approval_record.yaml"
        write_yaml(approval_path, approval)
        repair_path = ROOT / "repair_request.yaml"
        if repair_path.exists():
            repair_path.unlink()
        update_ledger(inputs, review, now, approval["object_id"])
    else:
        repair = build_repair_request(review, now)
        repair_path = ROOT / "repair_request.yaml"
        write_yaml(repair_path, repair)
        approval_path = ROOT / "approval_record.yaml"
        if approval_path.exists():
            approval_path.unlink()
        update_ledger(inputs, review, now, repair["object_id"])
    return review_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run research-plan-execute review gate.")
    parser.add_argument("--task", default="task003")
    parser.add_argument("--iteration", type=int, default=2)
    args = parser.parse_args()
    review_path = run_gate(args.task, args.iteration)
    review = load_yaml(review_path)
    print(f"Research review gate wrote {review_path.relative_to(REPO_ROOT)}")
    print(f"Verdict: {review['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
