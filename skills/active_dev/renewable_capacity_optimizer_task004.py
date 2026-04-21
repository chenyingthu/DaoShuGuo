"""Candidate hosting-capacity scanner with inverter support for task004."""

from __future__ import annotations

from typing import Any

from tasks.task004.runtime_helpers import default_inverter_settings, find_hosting_capacity_boundary


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    step = float(constraint_set.get("candidate_q_step_mvar", 0.1))
    settings = default_inverter_settings(constraint_set, step)
    result = find_hosting_capacity_boundary(inverter_settings=settings, constraint_set=constraint_set)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": result["boundary_point"]["metrics"],
        "control_settings": {
            "strategy": "inverter_support_capacity_scan",
            "inverter_q": result["boundary_point"]["inverter_q"],
            "hosting_capacity_level": result["boundary_point"]["scale"],
        },
        "boundary_trace": result["scan_trace"],
        "first_violation_point": result["first_violation_point"],
        "solver_status": "ok",
    }
