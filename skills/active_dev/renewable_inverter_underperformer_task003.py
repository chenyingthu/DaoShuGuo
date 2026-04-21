"""Semantically valid but underperforming inverter candidate for task003."""

from __future__ import annotations

from typing import Any

from tasks.task003.runtime_helpers import evaluate_inverter_setting, renewable_sites_from_constraints


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Use inverter Q in the wrong direction to trigger performance failure."""
    settings = [
        {"bus": int(site["bus"]), "q_mvar": -min(float(site["q_mvar_limit"]), 0.1)}
        for site in renewable_sites_from_constraints(constraint_set)
    ]
    result = evaluate_inverter_setting(settings, constraint_set)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": result["metrics"],
        "control_settings": {
            "inverter_q": result["inverter_q"],
            "shunts": result["shunts"],
            "ext_grid_vm_pu": result["vm_pu"],
            "evaluated_candidates": 1,
            "performance_failure_probe": True,
        },
        "solver_status": "ok",
    }
