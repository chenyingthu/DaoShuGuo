"""Runtime helpers for task004 hosting-capacity evaluation."""

from __future__ import annotations

from typing import Any

import pandapower as pp

from tasks.task003.runtime_helpers import (
    apply_ext_grid_vm_pu,
    apply_inverter_q,
    bounded_inverter_settings,
    renewable_sites_from_constraints,
)
from tasks.task002.runtime_helpers import load_network as load_base_network, run_power_flow


def scaled_renewable_sites(constraint_set: dict[str, Any], scale: float) -> list[dict[str, float]]:
    sites = []
    for site in renewable_sites_from_constraints(constraint_set):
        sites.append(
            {
                **site,
                "p_mw": float(site["p_mw"]) * scale,
            }
        )
    return sites


def load_network(constraint_set: dict[str, Any], scale: float) -> Any:
    """Load network and apply renewable scaling."""
    net = load_base_network()
    for idx, site in enumerate(scaled_renewable_sites(constraint_set, scale)):
        pp.create_sgen(
            net,
            bus=int(site["bus"]) - 1,
            p_mw=float(site["p_mw"]),
            q_mvar=0.0,
            sn_mva=float(site["sn_mva"]),
            name=f"pv_inverter_{idx}_{int(site['bus'])}",
        )
    return net


def default_inverter_settings(constraint_set: dict[str, Any], q_mvar: float) -> list[dict[str, float]]:
    return [{"bus": int(site["bus"]), "q_mvar": float(q_mvar)} for site in renewable_sites_from_constraints(constraint_set)]


def compute_boundary_metrics(
    net: Any,
    *,
    scale: float,
    inverter_settings: list[dict[str, float]],
    constraint_set: dict[str, Any],
) -> dict[str, Any]:
    limits = constraint_set.get("voltage_limits", {})
    vm_min = float(limits.get("min", 0.95))
    vm_max = float(limits.get("max", 1.05))
    vm = net.res_bus.vm_pu
    min_vm = float(vm.min())
    max_vm = float(vm.max())
    violation_count = int(((vm < vm_min) | (vm > vm_max)).sum())
    if min_vm < vm_min:
        trigger = "undervoltage"
    elif max_vm > vm_max:
        trigger = "overvoltage"
    else:
        trigger = "feasible"
    return {
        "hosting_capacity_level": scale,
        "violation_trigger_type": trigger,
        "loss_at_boundary": float(net.res_line.pl_mw.sum() * 1000.0),
        "voltage_margin": float(min(min_vm - vm_min, vm_max - max_vm)),
        "constraint_violation": violation_count,
        "reactive_support_effort": sum(abs(item["q_mvar"]) for item in inverter_settings),
        "min_vm": min_vm,
        "max_vm": max_vm,
    }


def evaluate_hosting_capacity_point(
    *,
    scale: float,
    inverter_settings: list[dict[str, float]],
    constraint_set: dict[str, Any],
) -> dict[str, Any]:
    net = load_network(constraint_set, scale)
    apply_ext_grid_vm_pu(net, 1.0)
    bounded_settings = bounded_inverter_settings(inverter_settings, constraint_set)
    apply_inverter_q(net, bounded_settings)
    run_power_flow(net)
    metrics = compute_boundary_metrics(
        net,
        scale=scale,
        inverter_settings=bounded_settings,
        constraint_set=constraint_set,
    )
    return {"scale": scale, "inverter_q": bounded_settings, "metrics": metrics}


def find_hosting_capacity_boundary(
    *,
    inverter_settings: list[dict[str, float]],
    constraint_set: dict[str, Any],
) -> dict[str, Any]:
    scale_values = [float(v) for v in constraint_set.get("renewable_scale_values", [1.0])]
    last_feasible = None
    first_violation = None
    trace = []
    for scale in scale_values:
        point = evaluate_hosting_capacity_point(scale=scale, inverter_settings=inverter_settings, constraint_set=constraint_set)
        trace.append(point)
        if point["metrics"]["constraint_violation"] == 0 and point["metrics"]["violation_trigger_type"] == "feasible":
            last_feasible = point
        else:
            first_violation = point
            break
    boundary = last_feasible or trace[0]
    return {
        "boundary_point": boundary,
        "first_violation_point": first_violation,
        "scan_trace": trace,
    }
