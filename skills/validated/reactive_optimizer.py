"""Validated shared ext-grid optimizer."""

from __future__ import annotations

from typing import Any

from tasks.runtime_loader import runtime_helpers_for_task, task_package_from_constraints


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Search ext_grid voltage setpoint over a bounded grid."""
    helpers = runtime_helpers_for_task(task_package_from_constraints(constraint_set))
    vm_candidates = constraint_set.get("candidate_vm_grid", [0.99, 1.0, 1.01, 1.02, 1.03, 1.04])
    best = None
    for vm_pu in vm_candidates:
        result = helpers.evaluate_vm_setting(float(vm_pu))
        score = helpers.objective(result["metrics"])
        if best is None or score < best["score"]:
            best = {"score": score, **result}
    assert best is not None
    return {
        "network_model": network_model,
        "constraint_set": constraint_set,
        "reactive_power_settings": best["metrics"],
        "control_settings": {"ext_grid_vm_pu": best["vm_pu"]},
        "solver_status": "ok",
    }
