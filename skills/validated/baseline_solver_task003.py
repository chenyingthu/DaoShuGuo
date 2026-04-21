"""Baseline solver for task003."""

from __future__ import annotations

from typing import Any

from tasks.task003.runtime_helpers import evaluate_baseline_setting


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_baseline_setting(constraint_set)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "baseline_solution": result["metrics"],
        "control_settings": {
            "inverter_q": result["inverter_q"],
            "shunts": result["shunts"],
            "ext_grid_vm_pu": result["vm_pu"],
        },
        "solver_status": "ok",
    }
