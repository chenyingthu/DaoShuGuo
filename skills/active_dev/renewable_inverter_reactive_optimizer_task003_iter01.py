"""Coordinated renewable-aware reactive support candidate for task003."""

from __future__ import annotations

from typing import Any

from tasks.task003.runtime_helpers import (
    candidate_inverter_grid,
    evaluate_inverter_setting,
    objective,
    renewable_sites_from_constraints,
    weakest_buses,
)


def _zero_inverter_settings(constraint_set: dict[str, Any]) -> list[dict[str, float]]:
    return [
        {"bus": int(site["bus"]), "q_mvar": 0.0}
        for site in renewable_sites_from_constraints(constraint_set)
    ]


def _needs_coordination(
    inverter_result: dict[str, Any],
    constraint_set: dict[str, Any],
) -> bool:
    metrics = inverter_result["metrics"]
    if int(metrics["constraint_violation"]) > 0:
        return True
    threshold = float(constraint_set.get("candidate_voltage_threshold", 0.97))
    return float(metrics["voltage_deviation"]) >= max(0.0, 1.0 - threshold)


def _candidate_shunts(constraint_set: dict[str, Any]) -> list[list[dict[str, float]]]:
    weak_bus_count = int(constraint_set.get("weak_bus_count", 4))
    max_shunts = max(1, int(constraint_set.get("max_shunts", 1)))
    q_grid = [float(value) for value in constraint_set.get("shunt_q_mvar_grid", [0.1])]
    buses = weakest_buses(weak_bus_count)
    shunt_candidates: list[list[dict[str, float]]] = []
    for bus in buses[:max_shunts]:
        for q_mvar in q_grid[:2]:
            shunt_candidates.append([{"bus": int(bus), "q_mvar": q_mvar}])
    if len(buses) >= 2 and max_shunts >= 2 and q_grid:
        q_mvar = q_grid[min(1, len(q_grid) - 1)]
        shunt_candidates.append(
            [
                {"bus": int(buses[0]), "q_mvar": q_mvar},
                {"bus": int(buses[1]), "q_mvar": q_mvar},
            ]
        )
    return shunt_candidates


def _coordinated_candidates(constraint_set: dict[str, Any]) -> list[tuple[list[dict[str, float]], list[dict[str, float]]]]:
    zero_settings = _zero_inverter_settings(constraint_set)
    inverter_only_candidates = candidate_inverter_grid(constraint_set)
    coordinated: list[tuple[list[dict[str, float]], list[dict[str, float]]]] = []
    shunt_candidates = _candidate_shunts(constraint_set)
    for settings in inverter_only_candidates:
        coordinated.append((settings, []))
        inverter_result = evaluate_inverter_setting(settings, constraint_set)
        if not _needs_coordination(inverter_result, constraint_set):
            continue
        if settings == zero_settings:
            continue
        for shunts in shunt_candidates:
            coordinated.append((settings, shunts))
    return coordinated


def _ranking_tuple(result: dict[str, Any]) -> tuple[float, ...]:
    metrics = result["metrics"]
    shunt_count = float(len(result["shunts"]))
    return (
        float(metrics["constraint_violation"]),
        float(metrics["voltage_deviation"]),
        objective(metrics),
        float(metrics["reactive_support_effort"]),
        shunt_count,
        float(metrics["loss"]),
    )


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    best = None
    evaluated = 0
    for inverter_settings, shunts in _coordinated_candidates(constraint_set):
        result = evaluate_inverter_setting(inverter_settings, constraint_set, shunts=shunts)
        evaluated += 1
        if best is None or _ranking_tuple(result) < _ranking_tuple(best):
            best = result
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
            "coordinated_search": True,
        },
        "solver_status": "ok",
    }
