#!/usr/bin/env python3
"""Evaluator for task003 renewable reactive optimization."""

from __future__ import annotations

from typing import Any

from evaluators.task001_evaluator import compare_metrics
from tasks.task003.runtime_helpers import evaluate_inverter_setting


METRIC_DIRECTIONS = {
    "loss": "lower_is_better",
    "voltage_deviation": "lower_is_better",
    "constraint_violation": "constraint_only",
    "reactive_support_effort": "lower_is_better",
}


def compare_task003_metrics(
    candidate: dict[str, float], baseline: dict[str, float]
) -> dict[str, dict[str, Any]]:
    comparisons = compare_metrics(
        {key: candidate[key] for key in ("loss", "voltage_deviation", "constraint_violation")},
        {key: baseline[key] for key in ("loss", "voltage_deviation", "constraint_violation")},
    )
    effort_improved = candidate["reactive_support_effort"] <= max(1.0, baseline["reactive_support_effort"])
    comparisons["reactive_support_effort"] = {
        "candidate": candidate["reactive_support_effort"],
        "baseline": baseline["reactive_support_effort"],
        "direction": "lower_is_better",
        "improved": effort_improved,
        "delta": candidate["reactive_support_effort"] - baseline["reactive_support_effort"],
    }
    return comparisons


def evaluate_candidate(candidate: dict[str, float], baseline: dict[str, float]) -> dict[str, Any]:
    comparisons = compare_task003_metrics(candidate, baseline)
    key_metrics_pass = comparisons["loss"]["improved"] and comparisons["voltage_deviation"]["improved"]
    constraints_pass = comparisons["constraint_violation"]["improved"]
    effort_recorded = "reactive_support_effort" in candidate
    passed = key_metrics_pass and constraints_pass and effort_recorded
    return {
        "passed": passed,
        "key_metrics_pass": key_metrics_pass,
        "constraints_pass": constraints_pass,
        "comparisons": comparisons,
        "summary": "candidate improved renewable reactive objective" if passed else "candidate did not meet task003 evaluator criteria",
    }


def evaluate_real_solution(
    baseline_solution: dict[str, Any], candidate_solution: dict[str, Any]
) -> dict[str, Any]:
    baseline_metrics = baseline_solution["metrics"]
    candidate_metrics = candidate_solution["metrics"]
    evaluation = evaluate_candidate(candidate_metrics, baseline_metrics)
    evaluation["baseline_solution"] = baseline_solution
    evaluation["candidate_solution"] = candidate_solution
    return evaluation


def build_solution_from_control(settings: list[dict[str, float]], constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_inverter_setting(settings, constraint_set)
    return {
        "control_settings": {
            "inverter_q": result["inverter_q"],
            "shunts": result["shunts"],
            "ext_grid_vm_pu": result["vm_pu"],
        },
        "metrics": result["metrics"],
    }
