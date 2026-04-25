#!/usr/bin/env python3
"""Verify the effectiveness/delivery layer artifacts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS = ["task003", "task004"]
REQUIRED = [
    "validation_plan.yaml",
    "experiment_matrix.yaml",
    "application_assessment.yaml",
    "deliverable_package.yaml",
    "claim_routing.yaml",
]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def verify_task(task_name: str) -> None:
    root = REPO_ROOT / "effectiveness" / task_name
    missing = [name for name in REQUIRED if not (root / name).exists()]
    if missing:
        raise RuntimeError(f"{task_name} missing effectiveness artifacts: {missing}")
    deliverable = load_yaml(root / "deliverable_package.yaml")
    routing = load_yaml(root / "claim_routing.yaml")
    application = load_yaml(root / "application_assessment.yaml")
    validation = load_yaml(root / "validation_plan.yaml")
    if deliverable.get("readiness_level") not in {
        "internal_report_ready",
        "patent_candidate",
        "paper_candidate",
        "not_ready",
    }:
        raise RuntimeError(f"{task_name} invalid readiness_level")
    if routing.get("route") not in {
        "internal_report_ready",
        "patent_candidate",
        "paper_candidate",
        "continue_research",
        "not_ready",
    }:
        raise RuntimeError(f"{task_name} invalid claim route")
    if not routing.get("allowed_claims") or not routing.get("forbidden_claims"):
        raise RuntimeError(f"{task_name} claim routing must include allowed and forbidden claims")
    if not application.get("applicable_scenarios") or not application.get("not_applicable_scenarios"):
        raise RuntimeError(f"{task_name} application assessment must include applicable and excluded scenarios")
    if not validation.get("covered_dimensions"):
        raise RuntimeError(f"{task_name} validation plan must include covered dimensions")


def main() -> int:
    for task_name in TASKS:
        verify_task(task_name)
    print("Effectiveness layer verification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Effectiveness layer verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
