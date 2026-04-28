#!/usr/bin/env python3
"""Verify research-plan-execute review gate artifacts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02"
REPAIR_VERDICTS = {
    "needs_fix",
    "stagnation",
    "cheating_suspected",
    "insufficient_evidence",
    "pause_for_human_review",
}
FROZEN_CAUSAL_CLAIM = "cognition caused skill improvement"
SKILL_USE_BOUNDARY = "skill-use improvement"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing artifact: {path.relative_to(REPO_ROOT)}")


def forbid(path: Path) -> None:
    if path.exists():
        raise RuntimeError(f"unexpected artifact: {path.relative_to(REPO_ROOT)}")


def verify() -> None:
    batch_path = ROOT / "research_batch.yaml"
    review_path = ROOT / "research_review.yaml"
    ledger_path = ROOT / "execution_ledger.yaml"
    require(batch_path)
    require(review_path)
    require(ledger_path)
    batch = load_yaml(batch_path)
    review = load_yaml(review_path)
    ledger = load_yaml(ledger_path)

    if batch.get("review_gate_required") is not True:
        raise RuntimeError("batch does not require review gate")
    if review["batch_ref"] != batch["object_id"]:
        raise RuntimeError("review does not reference batch")
    if not review.get("reviewed_artifact_refs"):
        raise RuntimeError("reviewed_artifact_refs missing")
    if review["verdict"] == "approved" and review.get("required_ablations"):
        raise RuntimeError("approved verdict must not carry required ablations")
    if review["verdict"] == "real_progress" and review.get("approval_allowed"):
        raise RuntimeError("real_progress must not be unconditional approval")
    if review["verdict"] in REPAIR_VERDICTS and not review.get("required_repairs"):
        raise RuntimeError("repair verdict must include required_repairs")
    boundary_text = " ".join(review.get("claim_boundary", []))
    if SKILL_USE_BOUNDARY not in boundary_text:
        raise RuntimeError("review must classify skill-use versus skill-structure improvement")
    if "skill-structure" not in boundary_text:
        raise RuntimeError("review must preserve skill-structure claim boundary")

    approval_path = ROOT / "approval_record.yaml"
    repair_path = ROOT / "repair_request.yaml"
    if review.get("approval_allowed"):
        require(approval_path)
        forbid(repair_path)
        approval = load_yaml(approval_path)
        if approval["source_review_ref"] != review["object_id"]:
            raise RuntimeError("approval record does not reference review")
        if review["verdict"] == "approved_with_ablation_required":
            if approval["approval_type"] != "approved_with_ablation_required":
                raise RuntimeError("bounded approval type mismatch")
            if FROZEN_CAUSAL_CLAIM not in approval.get("frozen_claims", []):
                raise RuntimeError("causality claim is not frozen")
            if not review.get("required_ablations"):
                raise RuntimeError("ablation-required verdict must include required_ablations")
        if ledger["current_state"] != "approved":
            raise RuntimeError("ledger must end in approved for approval_allowed review")
    else:
        require(repair_path)
        forbid(approval_path)
        repair = load_yaml(repair_path)
        if repair["source_review_ref"] != review["object_id"]:
            raise RuntimeError("repair request does not reference review")
        if ledger["current_state"] != "repair_requested":
            raise RuntimeError("ledger must end in repair_requested for blocked review")

    event_states = [event.get("state") for event in ledger.get("events", [])]
    if "review_completed" not in event_states:
        raise RuntimeError("ledger missing review_completed event")
    if review.get("approval_allowed") and "approved" not in event_states:
        raise RuntimeError("ledger missing approved event")
    if not review.get("approval_allowed") and "repair_requested" not in event_states:
        raise RuntimeError("ledger missing repair_requested event")


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Research review gate verification failed: {exc}", file=sys.stderr)
        return 1
    print("Research review gate verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
