#!/usr/bin/env python3
"""Verify the task004 skill-evolution Pi loop artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_skill_evolution"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify task004 skill-evolution loop.")
    parser.add_argument("--expected-iterations", type=int, default=3)
    args = parser.parse_args()

    state = load_json(ROOT / "state" / "skill_evolution_state.json")
    for iteration in range(1, args.expected_iterations + 1):
        payload = state["iterations"].get(f"iter_{iteration:03d}")
        if not payload:
            raise RuntimeError(f"missing iteration {iteration}")
        for step in [
            "task_trial_step",
            "boundary_judgment_step",
            "effectiveness_status_step",
            "iteration_review_step",
        ]:
            step_payload = payload["steps"].get(step)
            if not step_payload or step_payload.get("status") != "completed":
                raise RuntimeError(f"missing completed step: {step}")
        if "round_analysis" not in payload or "candidate_q_step_mvar" not in payload["round_analysis"]:
            raise RuntimeError("missing round_analysis payload")

    review = load_json(ROOT / "state" / "iterations" / "skill_evolution_review.json")
    if review.get("round_count") != args.expected_iterations:
        raise RuntimeError("unexpected review round count")

    print("Pi task004 skill-evolution loop verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
