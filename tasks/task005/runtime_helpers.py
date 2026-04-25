"""Runtime helpers for task005 restoration and resilience task."""

from __future__ import annotations

from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parents[1] / "task002" / "ieee69bus.txt"


def parse_rows() -> list[dict[str, float]]:
    parts = DATA_PATH.read_text(encoding="utf-8").split()
    rows: list[dict[str, float]] = []
    for idx in range(0, len(parts), 7):
        row = parts[idx : idx + 7]
        rows.append(
            {
                "from_bus": int(row[0]),
                "to_bus": int(row[1]),
                "p_kw": float(row[2]),
                "q_kvar": float(row[3]),
            }
        )
    return rows


def load_graph() -> tuple[dict[int, list[int]], dict[int, float]]:
    graph: dict[int, list[int]] = {}
    loads: dict[int, float] = {}
    for row in parse_rows():
        graph.setdefault(row["from_bus"], []).append(row["to_bus"])
        loads[row["to_bus"]] = loads.get(row["to_bus"], 0.0) + row["p_kw"] / 1000.0
    return graph, loads


def descendants(graph: dict[int, list[int]], root: int) -> set[int]:
    stack = [root]
    seen: set[int] = set()
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph.get(node, []))
    return seen


def fault_isolated_buses(constraint_set: dict[str, Any]) -> set[int]:
    graph, _ = load_graph()
    fault = constraint_set["faulted_branch"]
    return descendants(graph, int(fault["to_bus"]))


def total_load_mw() -> float:
    _, loads = load_graph()
    return sum(loads.values())


def critical_load_mw(constraint_set: dict[str, Any], buses: set[int]) -> float:
    _, loads = load_graph()
    critical = set(int(bus) for bus in constraint_set.get("critical_load_buses", []))
    return sum(loads.get(bus, 0.0) for bus in buses if bus in critical)


def isolated_load_mw(buses: set[int]) -> float:
    _, loads = load_graph()
    return sum(loads.get(bus, 0.0) for bus in buses)


def baseline_restoration(constraint_set: dict[str, Any]) -> dict[str, Any]:
    isolated = fault_isolated_buses(constraint_set)
    total = total_load_mw()
    isolated_load = isolated_load_mw(isolated)
    critical_unserved = critical_load_mw(constraint_set, isolated)
    restored = max(total - isolated_load, 0.0)
    return {
        "restored_load_ratio": restored / total if total > 0 else 0.0,
        "unserved_critical_load": critical_unserved,
        "constraint_violation": 0,
        "restoration_action_cost_proxy": 0.0,
        "isolated_buses": sorted(isolated),
        "restored_load_mw": restored,
    }


def renewable_support_restoration(constraint_set: dict[str, Any]) -> dict[str, Any]:
    isolated = fault_isolated_buses(constraint_set)
    total = total_load_mw()
    isolated_load = isolated_load_mw(isolated)
    support_sites = constraint_set.get("renewable_support", [])
    support_mw = sum(float(site["island_support_mw"]) for site in support_sites if int(site["bus"]) in isolated)
    restored_extra = min(isolated_load, support_mw)
    critical_unserved = max(critical_load_mw(constraint_set, isolated) - restored_extra, 0.0)
    restored = max(total - isolated_load + restored_extra, 0.0)
    return {
        "restored_load_ratio": restored / total if total > 0 else 0.0,
        "unserved_critical_load": critical_unserved,
        "constraint_violation": 0 if restored_extra > 0 else 1,
        "restoration_action_cost_proxy": 1.5,
        "isolated_buses": sorted(isolated),
        "restored_load_mw": restored,
        "restored_extra_mw": restored_extra,
    }
