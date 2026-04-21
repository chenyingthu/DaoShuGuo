"""Minimal renewable inverter reactive support candidate for task003."""

from __future__ import annotations

from typing import Any

from tasks.task003.runtime_helpers import candidate_inverter_grid, evaluate_inverter_setting, objective


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    best = None
    evaluated = 0
    for settings in candidate_inverter_grid(constraint_set):
        result = evaluate_inverter_setting(settings, constraint_set)
        evaluated += 1
        score = objective(result["metrics"])
        if best is None or score < best["score"]:
            best = {"score": score, **result}
    assert best is not None
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": best["metrics"],
        "control_settings": {
            "inverter_q": best["inverter_q"],
            "shunts": best["shunts"],
            "ext_grid_vm_pu": best["vm_pu"],
            "evaluated_candidates": evaluated,
        },
        "solver_status": "ok",
    }
