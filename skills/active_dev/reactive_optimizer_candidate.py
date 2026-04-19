"""Experimental candidate optimizer for task001."""

from __future__ import annotations

from typing import Any

from tasks.task001.runtime_helpers import evaluate_vm_setting, objective


def solve(network_model: str, constraint_set: dict[str, Any]) -> dict[str, Any]:
    """Search a deliberately poor voltage range to preserve a failure path."""
    vm_candidates = constraint_set.get("experimental_vm_grid", [0.97, 0.98, 0.99])
    best = None
    for vm_pu in vm_candidates:
        result = evaluate_vm_setting(float(vm_pu))
        score = objective(result["metrics"])
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
