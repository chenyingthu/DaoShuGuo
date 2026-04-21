"""Weak-bus shunt optimizer adaptation for task002."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from tasks.task002.runtime_helpers import evaluate_shunt_setting, objective, weakest_buses


def _candidate_shunt_sets(buses: list[int], q_grid: list[float], max_shunts: int) -> list[list[dict[str, float]]]:
    candidates: list[list[dict[str, float]]] = [[]]
    for size in range(1, max_shunts + 1):
        for bus_group in combinations(buses, size):
            for q_mvar in q_grid:
                candidates.append(
                    [{"bus": bus, "q_mvar": -float(q_mvar), "p_mw": 0.0} for bus in bus_group]
                )
    return candidates


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    weak_bus_count = int(constraint_set.get("weak_bus_count", 6))
    q_grid = constraint_set.get("shunt_q_mvar_grid", [0.05, 0.1, 0.2, 0.3, 0.5])
    max_shunts = int(constraint_set.get("max_shunts", 2))
    candidate_buses = weakest_buses(weak_bus_count)

    best = None
    evaluated = 0
    for shunts in _candidate_shunt_sets(candidate_buses, q_grid, max_shunts):
        result = evaluate_shunt_setting(shunts)
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
            "shunts": best["shunts"],
            "ext_grid_vm_pu": best["vm_pu"],
            "candidate_buses": candidate_buses,
            "evaluated_candidates": evaluated,
        },
        "solver_status": "ok",
    }
