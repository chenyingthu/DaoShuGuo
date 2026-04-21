"""Skill-mismatch probe for task004 hosting-capacity assessment."""

from __future__ import annotations

from typing import Any

from tasks.task004.runtime_helpers import default_inverter_settings, evaluate_hosting_capacity_point


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Use a single-point operating result as a fake boundary to trigger mismatch handling."""
    scale_values = [float(v) for v in constraint_set.get("renewable_scale_values", [1.0])]
    mid_scale = scale_values[min(len(scale_values) // 2, len(scale_values) - 1)]
    point = evaluate_hosting_capacity_point(
        scale=mid_scale,
        inverter_settings=default_inverter_settings(constraint_set, 0.0),
        constraint_set=constraint_set,
    )
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": point["metrics"],
        "control_settings": {
            "strategy": "single_point_capacity_mismatch",
            "inverter_q": point["inverter_q"],
            "hosting_capacity_level": point["scale"],
        },
        "boundary_trace": [point],
        "first_violation_point": None,
        "solver_status": "ok",
    }
