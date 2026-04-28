#!/usr/bin/env python3
"""Run the iter02 fixed/uniform/sensitivity ablation for task004."""

from __future__ import annotations

import copy
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.task004.runtime_helpers import default_inverter_settings, find_hosting_capacity_boundary
from workbench_common import utc_now, write_yaml

ROOT = REPO_ROOT / "analysis" / "real_task_001_upgrade" / "skill_worker_iter02"
DETAIL_PATH = ROOT / "ablation_detail.json"
RESULT_PATH = ROOT / "ablation_result.yaml"
PLAN_REF = "ablation_plan.power.ieee69_hosting_capacity.skill_worker.0002"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def boundary_solution(label: str, inverter_settings: list[dict[str, float]], constraint_set: dict[str, Any]) -> dict[str, Any]:
    result = find_hosting_capacity_boundary(inverter_settings=inverter_settings, constraint_set=constraint_set)
    return {
        "label": label,
        "control_settings": {
            "strategy": label,
            "inverter_q": result["boundary_point"]["inverter_q"],
            "hosting_capacity_level": result["boundary_point"]["scale"],
        },
        "metrics": result["boundary_point"]["metrics"],
        "first_violation_point": result["first_violation_point"],
        "boundary_trace": result["scan_trace"],
    }


def run_ablation() -> dict[str, Any]:
    constraints = load_yaml(REPO_ROOT / "tasks" / "task004" / "constraints.yaml")
    constraint_set = copy.deepcopy(constraints["solver"])
    total_q = 0.35
    constraint_set["candidate_q_step_mvar"] = total_q
    constraint_set["candidate_total_q_mvar"] = total_q
    network_model = str(constraint_set.get("network_model", "ieee69_hosting_capacity"))

    sensitivity_solver = load_module(
        "voltage_sensitivity_capacity_optimizer_task004",
        REPO_ROOT / "skills" / "active_dev" / "voltage_sensitivity_capacity_optimizer_task004.py",
    )
    evaluator = load_module("task004_evaluator", REPO_ROOT / "evaluators" / "task004_evaluator.py")

    fixed = boundary_solution(
        "fixed_q_baseline",
        default_inverter_settings(constraint_set, float(constraint_set.get("baseline_inverter_q_mvar", 0.0))),
        constraint_set,
    )
    uniform = boundary_solution(
        "uniform_q_support_equal_effort",
        default_inverter_settings(constraint_set, total_q / len(constraint_set.get("renewable_sites", [1]))),
        constraint_set,
    )
    sensitivity_raw = sensitivity_solver.solve(network_model, constraint_set)
    sensitivity = {
        "label": "voltage_sensitivity_q_allocation",
        "control_settings": sensitivity_raw["control_settings"],
        "metrics": sensitivity_raw["reactive_power_settings"],
        "first_violation_point": sensitivity_raw["first_violation_point"],
        "boundary_trace": sensitivity_raw["boundary_trace"],
    }

    fixed_vs_sensitivity = evaluator.evaluate_real_solution(
        {"control_settings": fixed["control_settings"], "metrics": fixed["metrics"]},
        {"control_settings": sensitivity["control_settings"], "metrics": sensitivity["metrics"]},
    )
    uniform_vs_sensitivity = evaluator.evaluate_real_solution(
        {"control_settings": uniform["control_settings"], "metrics": uniform["metrics"]},
        {"control_settings": sensitivity["control_settings"], "metrics": sensitivity["metrics"]},
    )
    return {
        "network_model": network_model,
        "controlled_total_q_mvar": total_q,
        "variants": {
            "fixed_q_baseline": fixed,
            "uniform_q_support_equal_effort": uniform,
            "voltage_sensitivity_q_allocation": sensitivity,
        },
        "comparisons": {
            "fixed_vs_sensitivity": fixed_vs_sensitivity["comparisons"],
            "uniform_vs_sensitivity": uniform_vs_sensitivity["comparisons"],
        },
        "passes": {
            "fixed_vs_sensitivity": bool(fixed_vs_sensitivity["passed"]),
            "uniform_vs_sensitivity": bool(uniform_vs_sensitivity["passed"]),
            "boundary_triggered": bool(fixed_vs_sensitivity["boundary_triggered"] or uniform_vs_sensitivity["boundary_triggered"]),
        },
    }


def build_result(detail: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    passes = detail["passes"]
    causal_supported = bool(
        passes["fixed_vs_sensitivity"]
        and passes["uniform_vs_sensitivity"]
        and passes["boundary_triggered"]
    )
    return {
        "schema_version": "0.1.0",
        "object_type": "ablation_result",
        "object_id": "ablation_result.power.ieee69_hosting_capacity.skill_worker.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "completed" if causal_supported else "inconclusive",
        "metadata": {
            "detail_path": str(DETAIL_PATH.relative_to(REPO_ROOT)),
            "controlled_total_q_mvar": detail["controlled_total_q_mvar"],
        },
        "ablation_plan_ref": PLAN_REF,
        "variant_result_refs": [
            "variant.fixed_q_baseline",
            "variant.uniform_q_support_equal_effort",
            "variant.voltage_sensitivity_q_allocation",
        ],
        "comparison_summary": (
            "Voltage-sensitivity allocation passed both primary boundary comparisons under equal effort."
            if causal_supported
            else "Voltage-sensitivity allocation did not satisfy the equal-effort boundary-improvement gate."
        ),
        "causal_claim_supported": causal_supported,
        "remaining_confounders": [
            "single static snapshot only",
            "heuristic sensitivity allocation, not OPF",
            "boundary scan envelope remains task004-specific",
        ],
        "summary": "Ablation result remains inconclusive for verified structural skill improvement."
        if not causal_supported
        else "Ablation supports a bounded candidate structural improvement claim under this evaluator.",
    }


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    detail = run_ablation()
    DETAIL_PATH.write_text(json.dumps(detail, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = build_result(detail)
    write_yaml(RESULT_PATH, result)
    print(json.dumps({"status": result["status"], "causal_claim_supported": result["causal_claim_supported"], "path": str(RESULT_PATH.relative_to(REPO_ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
