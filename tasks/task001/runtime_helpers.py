"""Runtime helpers for real task001 execution."""

from __future__ import annotations

import os
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/daoshuguo-mpl")

import pandapower as pp
import pandapower.networks as pn


def load_network() -> pp.pandapowerNet:
    """Load the IEEE 33-bus distribution network."""
    return pn.case33bw()


def apply_ext_grid_vm_pu(net: pp.pandapowerNet, vm_pu: float) -> None:
    """Apply ext_grid voltage setpoint to the network."""
    net.ext_grid.at[0, "vm_pu"] = vm_pu


def apply_shunts(net: pp.pandapowerNet, shunts: list[dict[str, float]]) -> None:
    """Apply shunt compensation settings to a network."""
    for idx, shunt in enumerate(shunts):
        pp.create_shunt(
            net,
            bus=int(shunt["bus"]),
            q_mvar=float(shunt["q_mvar"]),
            p_mw=float(shunt.get("p_mw", 0.0)),
            name=f"candidate_shunt_{idx}",
        )


def run_power_flow(net: pp.pandapowerNet) -> None:
    """Run a Newton-Raphson power flow."""
    pp.runpp(net)


def compute_metrics(
    net: pp.pandapowerNet, vm_min: float = 0.95, vm_max: float = 1.05
) -> dict[str, float]:
    """Compute the MVP metrics from a solved network."""
    vm = net.res_bus.vm_pu
    return {
        "loss": float(net.res_line.pl_mw.sum() * 1000.0),
        "voltage_deviation": float((vm - 1.0).abs().mean()),
        "constraint_violation": int(((vm < vm_min) | (vm > vm_max)).sum()),
    }


def objective(metrics: dict[str, float]) -> float:
    """Scalar objective for candidate search.

    Loss is in kW and voltage deviation is unitless; penalties strongly
    discourage violating bus-voltage constraints.
    """
    return (
        metrics["loss"]
        + 1000.0 * metrics["voltage_deviation"]
        + 10000.0 * metrics["constraint_violation"]
    )


def evaluate_vm_setting(vm_pu: float) -> dict[str, Any]:
    """Run the network at a given ext_grid voltage setpoint and return metrics."""
    net = load_network()
    apply_ext_grid_vm_pu(net, vm_pu)
    run_power_flow(net)
    metrics = compute_metrics(net)
    return {"vm_pu": vm_pu, "metrics": metrics}


def evaluate_shunt_setting(shunts: list[dict[str, float]], vm_pu: float = 1.0) -> dict[str, Any]:
    """Run the network with shunt settings and return metrics."""
    net = load_network()
    apply_ext_grid_vm_pu(net, vm_pu)
    apply_shunts(net, shunts)
    run_power_flow(net)
    return {"shunts": shunts, "vm_pu": vm_pu, "metrics": compute_metrics(net)}


def weakest_buses(count: int = 5) -> list[int]:
    """Return the lowest-voltage buses from the baseline case."""
    net = load_network()
    run_power_flow(net)
    ranked = net.res_bus.vm_pu.sort_values().index.tolist()
    slack_bus = int(net.ext_grid.at[0, "bus"])
    return [int(bus) for bus in ranked if int(bus) != slack_bus][:count]
