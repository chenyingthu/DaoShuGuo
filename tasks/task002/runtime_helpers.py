"""Runtime helpers for real task002 execution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/daoshuguo-mpl")

import pandapower as pp


DATA_PATH = Path(__file__).with_name("ieee69bus.txt")
BASE_KV = 12.66


def _parse_rows() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    raw = DATA_PATH.read_text(encoding="utf-8").strip()
    for chunk in raw.split():
        pass
    parts = raw.split()
    if len(parts) % 7 != 0:
        raise ValueError("ieee69bus.txt must contain 7 values per branch row")
    for idx in range(0, len(parts), 7):
        row = parts[idx : idx + 7]
        rows.append(
            {
                "from_bus": int(row[0]),
                "to_bus": int(row[1]),
                "p_kw": float(row[2]),
                "q_kvar": float(row[3]),
                "r_ohm": float(row[4]),
                "x_ohm": float(row[5]),
                "max_i_a": float(row[6]),
            }
        )
    return rows


def load_network() -> pp.pandapowerNet:
    """Load the bundled IEEE69 radial distribution system."""
    rows = _parse_rows()
    net = pp.create_empty_network(sn_mva=10.0)
    buses = {bus_idx: pp.create_bus(net, vn_kv=BASE_KV, name=f"bus_{bus_idx}") for bus_idx in range(1, 70)}
    pp.create_ext_grid(net, buses[1], vm_pu=1.0, name="grid_connection")
    seen_loads: set[int] = set()
    for row in rows:
        from_bus = buses[int(row["from_bus"])]
        to_bus = buses[int(row["to_bus"])]
        pp.create_line_from_parameters(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=1.0,
            r_ohm_per_km=float(row["r_ohm"]),
            x_ohm_per_km=float(row["x_ohm"]),
            c_nf_per_km=0.0,
            max_i_ka=float(row["max_i_a"]) / 1000.0,
            name=f"line_{int(row['from_bus'])}_{int(row['to_bus'])}",
        )
        to_bus_idx = int(row["to_bus"])
        if to_bus_idx not in seen_loads and (row["p_kw"] != 0.0 or row["q_kvar"] != 0.0):
            pp.create_load(
                net,
                bus=to_bus,
                p_mw=float(row["p_kw"]) / 1000.0,
                q_mvar=float(row["q_kvar"]) / 1000.0,
                name=f"load_{to_bus_idx}",
            )
            seen_loads.add(to_bus_idx)
    return net


def apply_ext_grid_vm_pu(net: pp.pandapowerNet, vm_pu: float) -> None:
    """Apply ext_grid voltage setpoint to the network."""
    net.ext_grid.at[0, "vm_pu"] = vm_pu


def apply_shunts(net: pp.pandapowerNet, shunts: list[dict[str, float]]) -> None:
    """Apply shunt compensation settings to a network."""
    for idx, shunt in enumerate(shunts):
        pp.create_shunt(
            net,
            bus=int(shunt["bus"]) - 1,
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
    """Shared scalar objective for candidate search."""
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
    return [int(bus) + 1 for bus in ranked if int(bus) != slack_bus][:count]
