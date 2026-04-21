"""Shared real baseline solver for task tasks."""

from __future__ import annotations

from typing import Any

from tasks.runtime_loader import runtime_helpers_for_task, task_package_from_constraints


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Solve the baseline using the default ext_grid setpoint."""
    helpers = runtime_helpers_for_task(task_package_from_constraints(constraint_set))
    vm_pu = float(constraint_set.get("baseline_vm_pu", 1.0))
    result = helpers.evaluate_vm_setting(vm_pu)
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "baseline_solution": result["metrics"],
        "control_settings": {"ext_grid_vm_pu": result["vm_pu"]},
        "solver_status": "ok",
    }
