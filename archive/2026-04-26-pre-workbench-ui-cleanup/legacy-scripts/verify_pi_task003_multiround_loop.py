#!/usr/bin/env python3
"""Verify the task003 multi-round short-turn loop artifacts."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task003_multiround"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    state = load_json(ROOT / "state" / "multiround_state.json")
    iter1 = state["iterations"].get("iter_001")
    if not iter1:
        raise RuntimeError("missing iter_001")
    for step in ["task_trial_step", "skill_record_step", "cognition_constraint_step", "iteration_review_step"]:
        payload = iter1["steps"].get(step)
        if not payload or payload.get("status") != "completed":
            raise RuntimeError(f"iter_001 missing completed step: {step}")

    iter2 = state["iterations"].get("iter_002")
    if not iter2:
        raise RuntimeError("missing iter_002")
    if "request" not in iter2:
        raise RuntimeError("iter_002 missing request")
    trial = iter2["steps"].get("task_trial_step")
    if not trial or trial.get("status") != "completed":
        raise RuntimeError("iter_002 task_trial_step not completed")

    comparison = ROOT / "state" / "iterations" / "comparison_review.json"
    if not comparison.exists():
        raise RuntimeError("missing comparison_review.json")

    print("Pi task003 multiround loop verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
