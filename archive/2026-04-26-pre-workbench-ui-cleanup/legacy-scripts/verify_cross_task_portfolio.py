#!/usr/bin/env python3
"""Verify cross-task portfolio assessment."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = REPO_ROOT / "analysis" / "portfolio" / "skill_structure_portfolio_20260425.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def verify() -> None:
    if not PORTFOLIO.exists():
        raise RuntimeError(f"missing portfolio assessment: {PORTFOLIO.relative_to(REPO_ROOT)}")
    data = load_yaml(PORTFOLIO)
    assessments = data.get("task_assessments", [])
    if len(assessments) < 3:
        raise RuntimeError("portfolio must assess at least three tasks")
    by_ref = {item.get("task_ref"): item for item in assessments if isinstance(item, dict)}
    required = {
        "task.power.ieee69_renewable_reactive_opt",
        "task.power.ieee69_hosting_capacity",
        "task.power.ieee69_restoration_resilience",
    }
    if set(by_ref) != required:
        raise RuntimeError("portfolio task set mismatch")
    if "ablation" not in by_ref["task.power.ieee69_renewable_reactive_opt"]["recommendation"]:
        raise RuntimeError("task003 must be routed to ablation rather than raw continuation")
    task004_text = " ".join(
        [
            by_ref["task.power.ieee69_hosting_capacity"]["recommendation"],
            by_ref["task.power.ieee69_hosting_capacity"]["rationale"],
            by_ref["task.power.ieee69_hosting_capacity"]["next_test"],
        ]
    )
    if "q_step" not in task004_text and "parameter" not in task004_text:
        raise RuntimeError("task004 must address q_step/parameter local-trap risk")
    task005_text = " ".join(
        [
            by_ref["task.power.ieee69_restoration_resilience"]["recommendation"],
            by_ref["task.power.ieee69_restoration_resilience"]["rationale"],
            by_ref["task.power.ieee69_restoration_resilience"]["next_test"],
        ]
    )
    if "standard" not in task005_text or "cost" not in task005_text:
        raise RuntimeError("task005 must be routed through standard/cost work")
    if not data.get("stop_or_pause_recommendations"):
        raise RuntimeError("portfolio must include stop/pause recommendations")


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Cross-task portfolio verification failed: {exc}", file=sys.stderr)
        return 1
    print("Cross-task portfolio verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
