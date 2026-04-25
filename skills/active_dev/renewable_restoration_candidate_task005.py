"""Minimal renewable-aware restoration candidate for task005."""

from __future__ import annotations

from typing import Any

from tasks.task005.runtime_helpers import renewable_support_restoration


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = renewable_support_restoration(constraint_set)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": result,
        "control_settings": {"strategy": "renewable_island_support"},
        "solver_status": "ok",
    }
