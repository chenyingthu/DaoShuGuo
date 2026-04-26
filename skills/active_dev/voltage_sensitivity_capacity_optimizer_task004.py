"""Voltage-sensitivity hosting-capacity scanner for task004."""

from __future__ import annotations

from typing import Any

from tasks.task004.runtime_helpers import find_hosting_capacity_boundary, voltage_sensitivity_inverter_settings


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    total_q = float(constraint_set.get("candidate_total_q_mvar", constraint_set.get("candidate_q_step_mvar", 0.35)))
    probe_scale = float(constraint_set.get("sensitivity_probe_scale", 1.0))
    settings = voltage_sensitivity_inverter_settings(
        constraint_set,
        total_q_mvar=total_q,
        probe_scale=probe_scale,
    )
    result = find_hosting_capacity_boundary(inverter_settings=settings, constraint_set=constraint_set)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": result["boundary_point"]["metrics"],
        "control_settings": {
            "strategy": "voltage_sensitivity_q_allocation_capacity_scan",
            "inverter_q": result["boundary_point"]["inverter_q"],
            "hosting_capacity_level": result["boundary_point"]["scale"],
            "candidate_total_q_mvar": total_q,
            "sensitivity_probe_scale": probe_scale,
        },
        "boundary_trace": result["scan_trace"],
        "first_violation_point": result["first_violation_point"],
        "solver_status": "ok",
    }
