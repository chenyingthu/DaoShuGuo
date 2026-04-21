"""Baseline solver for task002."""

from __future__ import annotations

from typing import Any

from tasks.task002.runtime_helpers import evaluate_vm_setting


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    vm_pu = float(constraint_set.get("baseline_vm_pu", 1.0))
    result = evaluate_vm_setting(vm_pu)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "baseline_solution": result["metrics"],
        "control_settings": {"ext_grid_vm_pu": result["vm_pu"]},
        "solver_status": "ok",
    }
