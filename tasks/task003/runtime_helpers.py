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
        ],
        "voltage_limits": {"min": 0.95, "max": 1.05},
    }
    inverter_settings = [{"bus": int(site["bus"]), "q_mvar": 0.0} for site in constraint_set["renewable_sites"]]
    return evaluate_inverter_setting(inverter_settings, constraint_set, shunts=shunts, vm_pu=vm_pu)


def evaluate_baseline_setting(constraint_set: dict[str, Any]) -> dict[str, Any]:
    q_value = float(constraint_set.get("baseline_inverter_q_mvar", 0.0))
    settings = [
        {"bus": int(site["bus"]), "q_mvar": q_value}
        for site in renewable_sites_from_constraints(constraint_set)
    ]
    return evaluate_inverter_setting(settings, constraint_set)


def weakest_buses(count: int = 5) -> list[int]:
    """Return lowest-voltage buses under the default renewable baseline."""
    constraint_set = {
        "renewable_sites": [
            {"bus": 18, "p_mw": 0.35, "sn_mva": 0.5, "q_mvar_limit": 0.35},
            {"bus": 35, "p_mw": 0.45, "sn_mva": 0.65, "q_mvar_limit": 0.45},
            {"bus": 61, "p_mw": 0.55, "sn_mva": 0.8, "q_mvar_limit": 0.55},
        ],
        "voltage_limits": {"min": 0.95, "max": 1.05},
    }
    net = load_network(constraint_set)
    run_power_flow(net)
    ranked = net.res_bus.vm_pu.sort_values().index.tolist()
    slack_bus = int(net.ext_grid.at[0, "bus"])
    return [int(bus) + 1 for bus in ranked if int(bus) != slack_bus][:count]


def candidate_inverter_grid(constraint_set: dict[str, Any]) -> list[list[dict[str, float]]]:
    step = float(constraint_set.get("candidate_q_step_mvar", 0.1))
    candidates: list[list[dict[str, float]]] = []
    for sign in (-1.0, 1.0):
        settings = []
        for site in renewable_sites_from_constraints(constraint_set):
            q_mvar = sign * min(float(site["q_mvar_limit"]), step)
            settings.append({"bus": int(site["bus"]), "q_mvar": q_mvar})
        candidates.append(settings)
    candidates.append([
        {"bus": int(site["bus"]), "q_mvar": 0.0}
        for site in renewable_sites_from_constraints(constraint_set)
    ])
    return candidates
