#!/usr/bin/env python3
"""Evaluator for task002.

Reuses the task001 comparison logic while binding real execution to task002.
"""

from __future__ import annotations

from typing import Any

from evaluators.task001_evaluator import (
    METRIC_DIRECTIONS,
    compare_metrics,
    evaluate_candidate,
    evaluate_real_solution,
)
from tasks.task002.runtime_helpers import compute_metrics, load_network, run_power_flow


def build_solution_from_control(vm_pu: float) -> dict[str, Any]:
    """Build a solved task002 network result for a given ext_grid voltage setpoint."""
    net = load_network()
    net.ext_grid.at[0, "vm_pu"] = vm_pu
    run_power_flow(net)
    return {
        "control_settings": {"ext_grid_vm_pu": vm_pu},
        "metrics": compute_metrics(net),
    }

