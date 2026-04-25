"""Performance failure probe for task005."""

from __future__ import annotations

from typing import Any

from tasks.task005.runtime_helpers import baseline_restoration


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = baseline_restoration(constraint_set)
    result["restoration_action_cost_proxy"] = 2.0
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": result,
        "control_settings": {"strategy": "renewable_underperformer"},
        "solver_status": "ok",
    }
