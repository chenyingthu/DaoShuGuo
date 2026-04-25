#!/usr/bin/env python3
"""Evaluator for task005 restoration task."""

from __future__ import annotations

from typing import Any


def evaluate_real_solution(
    baseline_solution: dict[str, Any], candidate_solution: dict[str, Any]
) -> dict[str, Any]:
    baseline = baseline_solution["metrics"]
    candidate = candidate_solution["metrics"]
    comparisons = {
        "restored_load_ratio": {
            "candidate": candidate["restored_load_ratio"],
            "baseline": baseline["restored_load_ratio"],
            "direction": "higher_is_better",
            "improved": candidate["restored_load_ratio"] > baseline["restored_load_ratio"],
            "delta": candidate["restored_load_ratio"] - baseline["restored_load_ratio"],
        },
        "unserved_critical_load": {
            "candidate": candidate["unserved_critical_load"],
            "baseline": baseline["unserved_critical_load"],
            "direction": "lower_is_better",
            "improved": candidate["unserved_critical_load"] <= baseline["unserved_critical_load"],
            "delta": candidate["unserved_critical_load"] - baseline["unserved_critical_load"],
        },
        "constraint_violation": {
            "candidate": candidate["constraint_violation"],
            "baseline": baseline["constraint_violation"],
            "direction": "constraint_only",
            "improved": candidate["constraint_violation"] <= baseline["constraint_violation"],
            "delta": candidate["constraint_violation"] - baseline["constraint_violation"],
        },
        "restoration_action_cost_proxy": {
            "candidate": candidate["restoration_action_cost_proxy"],
            "baseline": baseline["restoration_action_cost_proxy"],
            "direction": "lower_is_better",
            "improved": candidate["restoration_action_cost_proxy"] < baseline["restoration_action_cost_proxy"],
            "acceptable": candidate["restoration_action_cost_proxy"] <= baseline["restoration_action_cost_proxy"] + 2.0,
            "delta": candidate["restoration_action_cost_proxy"] - baseline["restoration_action_cost_proxy"],
        },
    }
    passed = comparisons["restored_load_ratio"]["improved"] and comparisons["constraint_violation"]["improved"]
    return {
        "passed": passed,
        "key_metrics_pass": comparisons["restored_load_ratio"]["improved"],
        "constraints_pass": comparisons["constraint_violation"]["improved"],
        "comparisons": comparisons,
        "summary": "candidate improved restoration result" if passed else "candidate did not improve restoration result",
        "baseline_solution": baseline_solution,
        "candidate_solution": candidate_solution,
    }
