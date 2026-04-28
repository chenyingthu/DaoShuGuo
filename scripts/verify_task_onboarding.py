#!/usr/bin/env python3
"""Verify generic task onboarding readiness reports."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS = ["task003", "task004", "task005", "task007_fixture"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing file: {path.relative_to(REPO_ROOT)}")


def verify_adapter_is_data_only(task_id: str) -> None:
    adapter_path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    require(adapter_path)
    text = adapter_path.read_text(encoding="utf-8")
    forbidden = ["def ", "import ", "subprocess", "if task"]
    for pattern in forbidden:
        if pattern in text:
            raise RuntimeError(f"{task_id} adapter appears to contain code pattern `{pattern}`")


def verify_report(task_id: str) -> dict[str, Any]:
    report_path = REPO_ROOT / "analysis" / "onboarding" / task_id / "task_readiness_report.yaml"
    require(report_path)
    report = load_yaml(report_path)
    if report["task_id"] != task_id:
        raise RuntimeError(f"{task_id}: task_id mismatch")
    if not report.get("recommended_route"):
        raise RuntimeError(f"{task_id}: missing route")
    if report["readiness_status"].startswith("blocked") and not report.get("next_actions"):
        raise RuntimeError(f"{task_id}: blocked report lacks next actions")
    return report


def verify() -> None:
    reports = {task_id: verify_report(task_id) for task_id in TASKS}
    for task_id in TASKS:
        verify_adapter_is_data_only(task_id)
    if reports["task003"]["readiness_status"] not in {"ready_to_run", "ready_for_framing_only"}:
        raise RuntimeError("task003 must not be blocked")
    if reports["task004"]["readiness_status"] not in {"ready_to_run", "ready_for_framing_only"}:
        raise RuntimeError("task004 must not be blocked")
    if reports["task005"]["readiness_status"] != "ready_for_framing_only":
        raise RuntimeError("task005 must route to framing/evaluator work due claim-gate standard gap")
    fixture_status = reports["task007_fixture"]["readiness_status"]
    if fixture_status not in {"blocked_missing_evaluator", "blocked_missing_runtime", "blocked_missing_metrics_mapping"}:
        raise RuntimeError("task007_fixture must be blocked by generic diagnosis")
    if not reports["task007_fixture"]["missing_items"]:
        raise RuntimeError("task007_fixture blocked report must list missing items")


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Task onboarding verification failed: {exc}", file=sys.stderr)
        return 1
    print("Task onboarding verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
