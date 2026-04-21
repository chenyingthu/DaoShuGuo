#!/usr/bin/env python3
"""Evaluator for task004 hosting-capacity assessment."""

from __future__ import annotations

from typing import Any


def evaluate_real_solution(
    baseline_solution: dict[str, Any], candidate_solution: dict[str, Any]
) -> dict[str, Any]:
    baseline_metrics = baseline_solution["metrics"]
    candidate_metrics = candidate_solution["metrics"]
    comparisons = {
        "hosting_capacity_level": {
            "candidate": candidate_metrics["hosting_capacity_level"],
            "baseline": baseline_metrics["hosting_capacity_level"],
            "direction": "higher_is_better",
            "improved": candidate_metrics["hosting_capacity_level"] > baseline_metrics["hosting_capacity_level"],
            "delta": candidate_metrics["hosting_capacity_level"] - baseline_metrics["hosting_capacity_level"],
        },
        "loss_at_boundary": {
            "candidate": candidate_metrics["loss_at_boundary"],
            "baseline": baseline_metrics["loss_at_boundary"],
            "direction": "lower_is_better",
            "improved": candidate_metrics["loss_at_boundary"] <= baseline_metrics["loss_at_boundary"],
            "delta": candidate_metrics["loss_at_boundary"] - baseline_metrics["loss_at_boundary"],
        },
        "voltage_margin": {
            "candidate": candidate_metrics["voltage_margin"],
            "baseline": baseline_metrics["voltage_margin"],
            "direction": "higher_is_better",
            "improved": candidate_metrics["voltage_margin"] >= baseline_metrics["voltage_margin"],
            "delta": candidate_metrics["voltage_margin"] - baseline_metrics["voltage_margin"],
        },
    }
    passed = comparisons["hosting_capacity_level"]["improved"]
    return {
        "passed": passed,
        "key_metrics_pass": comparisons["hosting_capacity_level"]["improved"],
        "constraints_pass": True,
        "comparisons": comparisons,
        "summary": "candidate improved hosting-capacity boundary" if passed else "candidate did not improve hosting-capacity boundary",
        "baseline_solution": baseline_solution,
        "candidate_solution": candidate_solution,
    }
