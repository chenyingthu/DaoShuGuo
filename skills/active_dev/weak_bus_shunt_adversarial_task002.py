"""Adversarial weak-bus shunt candidate for task002 failure-path testing."""

from __future__ import annotations

from typing import Any

from tasks.task002.runtime_helpers import evaluate_shunt_setting, weakest_buses


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Intentionally worsen the IEEE69 case to exercise failure cognition."""
    del network_model
    failure_q_mvar = float(constraint_set.get("failure_probe_q_mvar", 1.0))
    max_shunts = int(constraint_set.get("max_shunts", 2))
    candidate_buses = weakest_buses(max_shunts)
    shunts = [{"bus": bus, "q_mvar": failure_q_mvar, "p_mw": 0.0} for bus in candidate_buses[:max_shunts]]
    result = evaluate_shunt_setting(shunts)
    return {
        "network_model": "ieee69",
        "constraint_set": constraint_set,
        "reactive_power_settings": result["metrics"],
        "control_settings": {
            "shunts": result["shunts"],
            "ext_grid_vm_pu": result["vm_pu"],
            "candidate_buses": candidate_buses,
            "evaluated_candidates": 1,
            "failure_probe": True,
            "failure_probe_q_mvar": failure_q_mvar,
        },
        "solver_status": "ok",
    }
