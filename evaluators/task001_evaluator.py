#!/usr/bin/env python3
"""Evaluator for task001.

Supports both the legacy demo path and real pandapower-backed execution.
"""

from __future__ import annotations

from typing import Any

from tasks.task001.runtime_helpers import compute_metrics, load_network, run_power_flow


METRIC_DIRECTIONS = {
    "loss": "lower_is_better",
    "voltage_deviation": "lower_is_better",
    "constraint_violation": "constraint_only",
}


def demo_candidate_metrics(mode: str = "success") -> dict[str, float]:
    if mode == "success":
        return {
            "loss": 123.4,
            "voltage_deviation": 0.032,
            "constraint_violation": 0,
        }
    if mode == "failure":
        return {
            "loss": 140.8,
            "voltage_deviation": 0.051,
            "constraint_violation": 2,
        }
    raise ValueError(f"unsupported demo mode: {mode}")


def compare_metrics(
    candidate: dict[str, float], baseline: dict[str, float]
) -> dict[str, dict[str, Any]]:
    comparisons: dict[str, dict[str, Any]] = {}
    for metric_id, direction in METRIC_DIRECTIONS.items():
        cand = candidate[metric_id]
        base = baseline[metric_id]
        improved = False
        if direction == "lower_is_better":
            improved = cand < base
        elif direction == "higher_is_better":
            improved = cand > base
        elif direction == "target_is_best":
            improved = cand == base
        elif direction == "constraint_only":
            improved = cand <= base
        comparisons[metric_id] = {
            "candidate": cand,
            "baseline": base,
            "direction": direction,
            "improved": improved,
            "delta": cand - base,
        }
    return comparisons


def evaluate_candidate(
    candidate: dict[str, float], baseline: dict[str, float]
) -> dict[str, Any]:
    comparisons = compare_metrics(candidate, baseline)
    key_metrics_pass = comparisons["loss"]["improved"] and comparisons["voltage_deviation"][
        "improved"
    ]
    constraints_pass = comparisons["constraint_violation"]["improved"]
    passed = key_metrics_pass and constraints_pass
    return {
        "passed": passed,
        "key_metrics_pass": key_metrics_pass,
        "constraints_pass": constraints_pass,
        "comparisons": comparisons,
        "summary": "candidate improved relative to baseline" if passed else "candidate did not meet evaluator criteria",
    }


def evaluate_real_solution(
    baseline_solution: dict[str, Any], candidate_solution: dict[str, Any]
) -> dict[str, Any]:
    """Evaluate real baseline/candidate metrics with the same comparison logic."""
    baseline_metrics = baseline_solution["metrics"]
    candidate_metrics = candidate_solution["metrics"]
    evaluation = evaluate_candidate(candidate_metrics, baseline_metrics)
    evaluation["baseline_solution"] = baseline_solution
    evaluation["candidate_solution"] = candidate_solution
    return evaluation


def build_solution_from_control(vm_pu: float) -> dict[str, Any]:
    """Build a solved network result for a given ext_grid voltage setpoint."""
    net = load_network()
    net.ext_grid.at[0, "vm_pu"] = vm_pu
    run_power_flow(net)
    return {
        "control_settings": {"ext_grid_vm_pu": vm_pu},
        "metrics": compute_metrics(net),
    }
