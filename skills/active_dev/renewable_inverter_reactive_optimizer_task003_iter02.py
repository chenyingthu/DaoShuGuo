"""Broader renewable-aware reactive support candidate for task003."""

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


def _settings_key(settings: list[dict[str, float]]) -> tuple[tuple[int, float], ...]:
    ordered = sorted(
        ((int(setting["bus"]), round(float(setting["q_mvar"]), 6)) for setting in settings),
        key=lambda item: item[0],
    )
    return tuple(ordered)


def _needs_coordination(
    inverter_result: dict[str, Any],
    constraint_set: dict[str, Any],
) -> bool:
    metrics = inverter_result["metrics"]
    if int(metrics["constraint_violation"]) > 0:
        return True
    threshold = float(constraint_set.get("candidate_voltage_threshold", 0.97))
    return float(metrics["voltage_deviation"]) >= max(0.0, 1.0 - threshold)


def _expanded_inverter_candidates(constraint_set: dict[str, Any]) -> list[list[dict[str, float]]]:
    step = float(constraint_set.get("candidate_q_step_mvar", 0.1))
    half_step = max(step / 2.0, 0.01)
    sites = renewable_sites_from_constraints(constraint_set)
    candidates: list[list[dict[str, float]]] = []
    seen: set[tuple[tuple[int, float], ...]] = set()

    def add(settings: list[dict[str, float]]) -> None:
        key = _settings_key(settings)
        if key in seen:
            return
        seen.add(key)
        candidates.append(settings)

    for settings in candidate_inverter_grid(constraint_set):
        add(settings)

    uniform_levels = [half_step, step, step + half_step, 2.0 * step, 3.0 * step]
    for sign in (-1.0, 1.0):
        for level in uniform_levels:
            add(
                [
                    {"bus": int(site["bus"]), "q_mvar": sign * min(float(site["q_mvar_limit"]), level)}
                    for site in sites
                ]
            )

    positive_profile = [half_step, step, step + half_step]
    add(
        [
            {"bus": int(site["bus"]), "q_mvar": min(float(site["q_mvar_limit"]), positive_profile[idx])}
            for idx, site in enumerate(sites)
        ]
    )
    add(
        [
            {
                "bus": int(site["bus"]),
                "q_mvar": min(float(site["q_mvar_limit"]), positive_profile[len(sites) - idx - 1]),
            }
            for idx, site in enumerate(sites)
        ]
    )
    return candidates


def _candidate_shunts(
    constraint_set: dict[str, Any],
    *,
    aggressive: bool,
) -> list[list[dict[str, float]]]:
    weak_bus_count = int(constraint_set.get("weak_bus_count", 4))
    max_shunts = max(1, int(constraint_set.get("max_shunts", 1)))
    q_grid = [float(value) for value in constraint_set.get("shunt_q_mvar_grid", [0.1])]
    buses = weakest_buses(weak_bus_count)
    bus_limit = min(len(buses), max_shunts + (1 if aggressive else 0))
    q_limit = min(len(q_grid), 3 if aggressive else 2)
    shunt_candidates: list[list[dict[str, float]]] = []

    for bus in buses[:bus_limit]:
        for q_mvar in q_grid[:q_limit]:
            shunt_candidates.append([{"bus": int(bus), "q_mvar": q_mvar}])

    if len(buses) >= 2 and max_shunts >= 2 and q_grid:
        q_choices = q_grid[:q_limit]
        for q_mvar in q_choices:
            shunt_candidates.append(
                [
                    {"bus": int(buses[0]), "q_mvar": q_mvar},
                    {"bus": int(buses[1]), "q_mvar": q_mvar},
                ]
            )
        if aggressive and len(buses) >= 3 and q_choices:
            shunt_candidates.append(
                [
                    {"bus": int(buses[0]), "q_mvar": q_choices[-1]},
                    {"bus": int(buses[2]), "q_mvar": q_choices[-1]},
                ]
            )
    return shunt_candidates


def _inverter_result_rank(result: dict[str, Any]) -> tuple[float, ...]:
    metrics = result["metrics"]
    return (
        float(metrics["constraint_violation"]),
        float(metrics["voltage_deviation"]),
        objective(metrics),
        float(metrics["reactive_support_effort"]),
        float(metrics["loss"]),
    )


def _solution_rank(result: dict[str, Any]) -> tuple[float, ...]:
    metrics = result["metrics"]
    return (
        float(metrics["constraint_violation"]),
        float(metrics["voltage_deviation"]),
        objective(metrics),
        float(len(result["shunts"])),
        float(metrics["reactive_support_effort"]),
        float(metrics["loss"]),
    )


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    zero_settings = _zero_inverter_settings(constraint_set)
    inverter_candidates = _expanded_inverter_candidates(constraint_set)
    inverter_results: list[dict[str, Any]] = []

    for settings in inverter_candidates:
        inverter_results.append(evaluate_inverter_setting(settings, constraint_set))

    inverter_results.sort(key=_inverter_result_rank)
    best = inverter_results[0]
    evaluated = len(inverter_results)

    coordination_budget = int(constraint_set.get("coordination_candidate_budget", 4))
    coordinated_candidates: list[tuple[list[dict[str, float]], list[dict[str, float]]]] = []
    for inverter_result in inverter_results[:coordination_budget]:
        settings = inverter_result["inverter_q"]
        if settings == zero_settings or not _needs_coordination(inverter_result, constraint_set):
            continue
        shunt_candidates = _candidate_shunts(
            constraint_set,
            aggressive=int(inverter_result["metrics"]["constraint_violation"]) > 0,
        )
        for shunts in shunt_candidates:
            coordinated_candidates.append((settings, shunts))

    for inverter_settings, shunts in coordinated_candidates:
        result = evaluate_inverter_setting(inverter_settings, constraint_set, shunts=shunts)
        evaluated += 1
        if _solution_rank(result) < _solution_rank(best):
            best = result

    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": best["metrics"],
        "control_settings": {
            "inverter_q": best["inverter_q"],
            "shunts": best["shunts"],
            "ext_grid_vm_pu": best["vm_pu"],
            "evaluated_candidates": evaluated,
            "evaluated_inverter_only_candidates": len(inverter_results),
            "evaluated_coordinated_candidates": len(coordinated_candidates),
            "coordinated_search": True,
            "broader_continuous_q_search": True,
        },
        "solver_status": "ok",
    }
