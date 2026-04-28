#!/usr/bin/env python3
"""Verify loop worker boundaries and generic object-chain completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from worker_chain_helpers import verify_worker_chain_root


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_task004_skill_evolution(root: Path) -> list[str]:
    issues: list[str] = []
    state_path = root / "state" / "skill_evolution_state.json"
    if not state_path.exists():
        issues.append("missing skill_evolution_state.json")
        return issues
    state = load_json(state_path)
    for key, payload in state.get("iterations", {}).items():
        request = payload.get("request", {})
        analysis = payload.get("round_analysis", {})
        if "candidate_q_step_mvar" not in request:
            issues.append(f"{key}: missing explicit skill change request field candidate_q_step_mvar")
        if "progress_type" not in analysis:
            issues.append(f"{key}: missing round_analysis.progress_type")
        if analysis.get("progress_type") == "cognition_deepened":
            issues.append(f"{key}: cognition judgment present in skill-evolution loop without cognition worker object")
    return issues


def verify_task004_multiround(root: Path) -> list[str]:
    issues: list[str] = []
    state_path = root / "state" / "multiround_state.json"
    if not state_path.exists():
        issues.append("missing multiround_state.json")
        return issues
    state = load_json(state_path)
    for key, payload in state.get("iterations", {}).items():
        analysis = payload.get("round_analysis", {})
        if analysis.get("progress_type") == "cognition_deepened":
            issues.append(f"{key}: controller-scripted cognition judgment detected")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify loop worker boundaries.")
    parser.add_argument("--task004-skill-evolution", action="store_true")
    parser.add_argument("--task004-multiround", action="store_true")
    parser.add_argument("--task004-worker-chain", action="store_true")
    parser.add_argument("--worker-chain-root", type=Path)
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()

    all_issues: list[str] = []
    if args.task004_skill_evolution:
        all_issues.extend(
            verify_task004_skill_evolution(
                REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_skill_evolution"
            )
        )
    if args.task004_multiround:
        all_issues.extend(
            verify_task004_multiround(
                REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_multiround"
            )
        )
    if args.task004_worker_chain:
        all_issues.extend(
            verify_worker_chain_root(
                REPO_ROOT / "analysis" / "worker_chain" / "task004",
                iterations=args.iterations,
            )
        )
    if args.worker_chain_root is not None:
        all_issues.extend(verify_worker_chain_root(args.worker_chain_root, iterations=args.iterations))

    if all_issues:
        for issue in all_issues:
            print(issue)
        return 1

    print("Loop worker boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
