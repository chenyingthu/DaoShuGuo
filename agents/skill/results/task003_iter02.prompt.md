You are the skill agent for a bounded task003 iteration.
Modify or create exactly one new candidate skill file.
Do not edit evaluator, task definitions, cognition files, or unrelated modules.
Return a short summary as plain text after edits.

## Request
schema_version: 0.1.0
object_type: skill_agent_iteration_request
object_id: skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.0002
object_version: 0.1.0
created_at: '2026-04-22T07:47:11Z'
updated_at: '2026-04-22T07:47:11Z'
status: ready
metadata:
  task_package: task003
  execution_mode: real_codex_agent
task_ref: task.power.ieee69_renewable_reactive_opt
source_update_ref: agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0001
iteration_index: 2
base_skill_ref: skill.power.renewable_inverter_reactive_optimizer_task003_iter01
allowed_change_scope:
- candidate_inverter_grid search logic
- coordination between inverter_q and weak-bus shunts
- selection logic over evaluated candidates
blocked_paths:
- pure_weak_shunt_substitution
required_tests:
- Head-to-head comparison against a semantically matched renewable-aware alternative
  rather than against a strategy labeled as mismatch
- Evidence clarifying whether the unchanged constraint_violation=8 is acceptable task-level
  feasibility or a boundary that limits practical interpretation
- constraint_violation=8 在任务中的真实含义：这是可接受上限、未恶化即算通过，还是说明任务核心约束仍未被解决。
- Direct head-to-head evaluation between run_0007 and semantically matched inverter-aware
  alternatives under the same evaluator
- Clarification of what constraint_violation = 8 means operationally and whether unchanged
  violation count should materially limit claims
- Evidence that the observed gain is stable across a broader continuous inverter-Q
  search space rather than an isolated fixed 0.1 Mvar setting
output_skill_path: skills/active_dev/renewable_inverter_reactive_optimizer_task003_iter02.py
summary: Add one semantically matched renewable-aware variant for direct comparison.;
  Prioritize candidates that may reduce constraint_violation without leaving renewable-aware
  control.; Expand inverter_q search beyond the fixed sign-only grid with bounded
  additional candidate points.; Keep shunt + inverter coordination available; do not
  collapse back to inverter-only or shunt-only search.

## Base Skill
Path: skills/active_dev/renewable_inverter_reactive_optimizer_task003_iter01.py
```python
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

```
## Runtime Helpers
```python
"""Runtime helpers for task003 renewable reactive optimization."""

from __future__ import annotations

import os
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/daoshuguo-mpl")

import pandapower as pp

from tasks.task002.runtime_helpers import (
    apply_ext_grid_vm_pu,
    apply_shunts,
    load_network as load_base_network,
    run_power_flow,
)


def renewable_sites_from_constraints(constraint_set: dict[str, Any]) -> list[dict[str, float]]:
    sites = constraint_set.get("renewable_sites", [])
    return [
        {
            "bus": int(site["bus"]),
            "p_mw": float(site["p_mw"]),
            "sn_mva": float(site["sn_mva"]),
            "q_mvar_limit": float(site["q_mvar_limit"]),
        }
        for site in sites
    ]


def load_network(constraint_set: dict[str, Any] | None = None) -> pp.pandapowerNet:
    """Load IEEE69 and add renewable inverter injections."""
    net = load_base_network()
    for idx, site in enumerate(renewable_sites_from_constraints(constraint_set or {})):
        pp.create_sgen(
            net,
            bus=int(site["bus"]) - 1,
            p_mw=float(site["p_mw"]),
            q_mvar=0.0,
            sn_mva=float(site["sn_mva"]),
            name=f"pv_inverter_{idx}_{int(site['bus'])}",
        )
    return net


def _site_by_bus(sites: list[dict[str, float]]) -> dict[int, dict[str, float]]:
    return {int(site["bus"]): site for site in sites}


def bounded_inverter_settings(
    settings: list[dict[str, float]], constraint_set: dict[str, Any]
) -> list[dict[str, float]]:
    sites = _site_by_bus(renewable_sites_from_constraints(constraint_set))
    bounded: list[dict[str, float]] = []
    for setting in settings:
        bus = int(setting["bus"])
        limit = float(sites[bus]["q_mvar_limit"])
        q_mvar = max(-limit, min(limit, float(setting["q_mvar"])))
        bounded.append({"bus": bus, "q_mvar": q_mvar})
    return bounded


def apply_inverter_q(net: pp.pandapowerNet, settings: list[dict[str, float]]) -> None:
    """Apply inverter reactive support to renewable static generators."""
    for setting in settings:
        bus_idx = int(setting["bus"]) - 1
        matches = net.sgen.index[net.sgen.bus == bus_idx].tolist()
        if not matches:
            raise ValueError(f"no renewable inverter at bus {setting['bus']}")
        net.sgen.at[matches[0], "q_mvar"] = float(setting["q_mvar"])


def reactive_support_effort(settings: list[dict[str, float]], constraint_set: dict[str, Any]) -> float:
    sites = _site_by_bus(renewable_sites_from_constraints(constraint_set))
    effort = 0.0
    for setting in settings:
        bus = int(setting["bus"])
        limit = float(sites[bus]["q_mvar_limit"])
        if limit > 0:
            effort += abs(float(setting["q_mvar"])) / limit
    return effort


def compute_metrics(
    net: pp.pandapowerNet,
    *,
    inverter_settings: list[dict[str, float]],
    constraint_set: dict[str, Any],
) -> dict[str, float]:
    limits = constraint_set.get("voltage_limits", {})
    vm_min = float(limits.get("min", 0.95))
    vm_max = float(limits.get("max", 1.05))
    vm = net.res_bus.vm_pu
    return {
        "loss": float(net.res_line.pl_mw.sum() * 1000.0),
        "voltage_deviation": float((vm - 1.0).abs().mean()),
        "constraint_violation": int(((vm < vm_min) | (vm > vm_max)).sum()),
        "reactive_support_effort": reactive_support_effort(inverter_settings, constraint_set),
    }


def objective(metrics: dict[str, float]) -> float:
    """Scalar objective with a light penalty for reactive support effort."""
    return (
        metrics["loss"]
        + 1000.0 * metrics["voltage_deviation"]
        + 10000.0 * metrics["constraint_violation"]
        + 5.0 * metrics["reactive_support_effort"]
    )


def evaluate_inverter_setting(
    inverter_settings: list[dict[str, float]],
    constraint_set: dict[str, Any],
    *,
    shunts: list[dict[str, float]] | None = None,
    vm_pu: float = 1.0,
) -> dict[str, Any]:
    """Run task003 with inverter Q and optional shunts."""
    settings = bounded_inverter_settings(inverter_settings, constraint_set)
    net = load_network(constraint_set)
    apply_ext_grid_vm_pu(net, vm_pu)
    apply_inverter_q(net, settings)
    if shunts:
        apply_shunts(net, shunts)
    run_power_flow(net)
    return {
        "inverter_q": settings,
        "shunts": shunts or [],
        "vm_pu": vm_pu,
        "metrics": compute_metrics(net, inverter_settings=settings, constraint_set=constraint_set),
    }


def evaluate_shunt_setting(shunts: list[dict[str, float]], vm_pu: float = 1.0) -> dict[str, Any]:
    """Compatibility surface for old weak-shunt skills that ignore inverter control."""
    constraint_set = {
        "renewable_sites": [
            {"bus": 18, "p_mw": 0.35, "sn_mva": 0.5, "q_mvar_limit": 0.35},
            {"bus": 35, "p_mw": 0.45, "sn_mva": 0.65, "q_mvar_limit": 0.45},
            {"bus": 61, "p_mw": 0.55, "sn_mva": 0.8, "q_mvar_limit": 0.55},
```
## Evaluator
```python
#!/usr/bin/env python3
"""Evaluator for task003 renewable reactive optimization."""

from __future__ import annotations

from typing import Any

from evaluators.task001_evaluator import compare_metrics
from tasks.task003.runtime_helpers import evaluate_inverter_setting


METRIC_DIRECTIONS = {
    "loss": "lower_is_better",
    "voltage_deviation": "lower_is_better",
    "constraint_violation": "constraint_only",
    "reactive_support_effort": "lower_is_better",
}


def compare_task003_metrics(
    candidate: dict[str, float], baseline: dict[str, float]
) -> dict[str, dict[str, Any]]:
    comparisons = compare_metrics(
        {key: candidate[key] for key in ("loss", "voltage_deviation", "constraint_violation")},
        {key: baseline[key] for key in ("loss", "voltage_deviation", "constraint_violation")},
    )
    effort_improved = candidate["reactive_support_effort"] <= max(1.0, baseline["reactive_support_effort"])
    comparisons["reactive_support_effort"] = {
        "candidate": candidate["reactive_support_effort"],
        "baseline": baseline["reactive_support_effort"],
        "direction": "lower_is_better",
        "improved": effort_improved,
        "delta": candidate["reactive_support_effort"] - baseline["reactive_support_effort"],
    }
    return comparisons


def evaluate_candidate(candidate: dict[str, float], baseline: dict[str, float]) -> dict[str, Any]:
    comparisons = compare_task003_metrics(candidate, baseline)
    key_metrics_pass = comparisons["loss"]["improved"] and comparisons["voltage_deviation"]["improved"]
    constraints_pass = comparisons["constraint_violation"]["improved"]
    effort_recorded = "reactive_support_effort" in candidate
    passed = key_metrics_pass and constraints_pass and effort_recorded
    return {
        "passed": passed,
        "key_metrics_pass": key_metrics_pass,
        "constraints_pass": constraints_pass,
        "comparisons": comparisons,
        "summary": "candidate improved renewable reactive objective" if passed else "candidate did not meet task003 evaluator criteria",
    }


def evaluate_real_solution(
    baseline_solution: dict[str, Any], candidate_solution: dict[str, Any]
) -> dict[str, Any]:
    baseline_metrics = baseline_solution["metrics"]
    candidate_metrics = candidate_solution["metrics"]
    evaluation = evaluate_candidate(candidate_metrics, baseline_metrics)
    evaluation["baseline_solution"] = baseline_solution
    evaluation["candidate_solution"] = candidate_solution
    return evaluation


def build_solution_from_control(settings: list[dict[str, float]], constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_inverter_setting(settings, constraint_set)
    return {
        "control_settings": {
            "inverter_q": result["inverter_q"],
            "shunts": result["shunts"],
            "ext_grid_vm_pu": result["vm_pu"],
        },
        "metrics": result["metrics"],
    }

```
## Hard Constraints
- Preserve renewable-aware control family.
- Prefer adding explicit shunt + inverter coordination or better candidate ranking.
- Keep file importable as a Python module with a `solve(network_model, constraint_set)` function.
- Write output only to skills/active_dev/renewable_inverter_reactive_optimizer_task003_iter02.py.