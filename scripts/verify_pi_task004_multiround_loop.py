#!/usr/bin/env python3
"""Verify the task004 multiround Pi loop artifacts."""

from __future__ import annotations

import json
import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_multiround"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the task004 multiround Pi loop artifacts.")
    parser.add_argument("--expected-iterations", type=int, default=2)
    args = parser.parse_args()

    state = load_json(ROOT / "state" / "multiround_state.json")
    payloads = []
    for iteration in range(1, args.expected_iterations + 1):
        payload = state["iterations"].get(f"iter_{iteration:03d}")
        if not payload:
            raise RuntimeError(f"missing task004 multiround iteration {iteration}")
        payloads.append(payload)

    for payload in payloads:
        for step in [
            "task_trial_step",
            "boundary_judgment_step",
            "effectiveness_status_step",
            "iteration_review_step",
        ]:
            step_payload = payload["steps"].get(step)
            if not step_payload or step_payload.get("status") != "completed":
                raise RuntimeError(f"missing completed step: {step}")
        if "round_analysis" not in payload or "progress_type" not in payload["round_analysis"]:
            raise RuntimeError("missing round_analysis payload")

    review = load_json(ROOT / "state" / "iterations" / "multiround_review.json")
    if review.get("round_count") != args.expected_iterations:
        raise RuntimeError("unexpected task004 multiround review count")

    print("Pi task004 multiround loop verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
