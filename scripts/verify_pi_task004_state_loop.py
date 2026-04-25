#!/usr/bin/env python3
"""Verify the light Pi task004 state-loop artifacts."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_state"
STATE = ROOT / "state" / "research_state.json"

EXPECTED_STEPS = [
    "init_step",
    "task_trial_step",
    "boundary_judgment_step",
    "effectiveness_status_step",
    "iteration_review_step",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if not STATE.exists():
        raise RuntimeError("missing research_state.json")
    state = load_json(STATE)
    if state.get("current_step") != "iteration_review_step":
        raise RuntimeError(f"unexpected current_step: {state.get('current_step')}")

    for step in EXPECTED_STEPS:
        req = ROOT / "state" / "requests" / f"{step}.json"
        res = ROOT / "state" / "results" / f"{step}.json"
        if not req.exists() or not res.exists():
            raise RuntimeError(f"missing request/result for {step}")
        payload = load_json(res)
        if payload.get("status") != "completed":
            raise RuntimeError(f"{step} not completed")

    loop_jsonl = ROOT / "research_loop.jsonl"
    loop_md = ROOT / "research_loop.md"
    if not loop_jsonl.exists() or not loop_md.exists():
        raise RuntimeError("missing durable loop files")

    entries = [line for line in loop_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    needed = [
        "init_research_task",
        "task004_trial",
        "boundary_judgment",
        "effectiveness_status",
        "iteration_review",
    ]
    for name in needed:
        if not any(f'"event":"{name}"' in line for line in entries):
            raise RuntimeError(f"missing event in research_loop.jsonl: {name}")

    print("Pi task004 state-loop verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
