#!/usr/bin/env python3
"""Task004 workers for the generic loop engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iteration_state(task_adapter: dict[str, Any]) -> tuple[int, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    experimental = task_adapter.get("experimental", {})
    iteration_index = int(experimental.get("iteration_index", 1))
    iteration_root = REPO_ROOT / experimental["iteration_root"]
    request = load_json(iteration_root / "request.json")
    round_analysis = load_json(iteration_root / "round_analysis.json")
    boundary_judgment = load_json(iteration_root / "boundary_judgment_step.json")
    effectiveness_status = load_json(iteration_root / "effectiveness_status_step.json")
    iteration_review = load_json(iteration_root / "iteration_review_step.json")
    return iteration_index, request, round_analysis, boundary_judgment, effectiveness_status, iteration_review


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    iteration_index, request, _, _, _, _ = _iteration_state(task_adapter)
    previous_skill_ref = task_adapter.get("experimental", {}).get(
        "previous_skill_ref", "skill.power.renewable_capacity_optimizer_task004"
    )
    q_step = request["candidate_q_step_mvar"]
    return {
        "metadata": {"task_package": "task004", "execution_mode": "parameterized_skill_evolution"},
        "fields": {
            "base_skill_ref": previous_skill_ref,
            "allowed_change_scope": ["candidate_q_step_mvar"],
            "blocked_paths": ["single_point_operation_proxy"],
            "required_tests": [
                "Run the same inverter-support skill under the current evaluator.",
                "Check whether hosting_capacity_level improves relative to the previous candidate.",
            ],
            "output_skill_path": "parameterized:tasks/task004/constraints.yaml:candidate_q_step_mvar",
            "summary": f"Set candidate_q_step_mvar to {q_step:.2f} and test whether the same skill improves.",
        },
    }


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    _, request, round_analysis, _, _, _ = _iteration_state(task_adapter)
    q_step = request["candidate_q_step_mvar"]
    return {
        "metadata": {"task_package": "task004", "executor": "pi_parameterized_skill_loop"},
        "fields": {
            "produced_skill_ref": "skill.power.renewable_capacity_optimizer_task004",
            "code_paths": ["skills/active_dev/renewable_capacity_optimizer_task004.py"],
            "change_summary": [f"candidate_q_step_mvar set to {q_step:.2f}"],
            "expected_behavior_change": [
                "Increase reactive support effort while keeping the same hosting-capacity scan structure.",
            ],
            "command": (
                "python orchestrator/main.py real-run-task004 --strategy inverter-support "
                f"--candidate-q-step-mvar {q_step}"
            ),
            "raw_output_path": task_adapter["experimental"]["iteration_root"] + "/request.json",
            "self_reported_risks": [
                "This is a parameterized skill variant, not yet a structural redesign.",
            ],
            "run_ref": round_analysis["run_ref"],
        },
    }


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    _, _, round_analysis, _, effectiveness_status, _ = _iteration_state(task_adapter)
    missing = effectiveness_status["extracted"]["details"]["missing_for_next_level"]
    return {
        "metadata": {"task_package": "task004", "worker": "effectiveness_worker"},
        "fields": {
            "baseline_ref": task_adapter["baseline_binding"]["baseline_refs"][0],
            "evaluator_ref": task_adapter["evaluator_binding"]["evaluator_ref"],
            "run_ref": round_analysis["run_ref"],
            "run_passed": round_analysis["run_passed"],
            "metric_summary": {
                "candidate_hosting_capacity_level": round_analysis["candidate_hosting_capacity_level"],
                "baseline_hosting_capacity_level": round_analysis["baseline_hosting_capacity_level"],
                "candidate_loss_at_boundary": round_analysis["candidate_loss_at_boundary"],
                "candidate_voltage_margin": round_analysis["candidate_voltage_margin"],
                "missing_for_next_level": missing,
            },
            "comparison_summary": round_analysis["evaluation_summary"],
            "judgment_summary": round_analysis["improvement_judgment"],
            "recommended_cognition_action": (
                "Decide whether this remains a skill-use issue or has become a skill-structure issue."
            ),
        },
    }


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    _, _, round_analysis, boundary_judgment, _, iteration_review = _iteration_state(task_adapter)
    boundary_details = boundary_judgment["extracted"]["details"]
    review_details = iteration_review["extracted"]["details"]
    if round_analysis["progress_type"] == "parameter_change_no_boundary_gain":
        problem_class = "skill_structure_problem"
        judgment_summary = "连续参数调整后边界仍不变，主线问题已从参数使用转向技能结构不足。"
        recommended_action = "redesign_skill_structure"
        next_constraints = ["不得再把继续加 q_step 当作主线技能升级。"]
        next_refinements = ["需要引入非均匀 inverter Q 分配或 bus 子集选择。"]
        priorities = ["优先探索技能结构变体，而不是继续扩大同幅注入参数。"]
        update_summary = "连续参数调整后边界仍不变，后续主线应转向技能结构升级。"
    else:
        problem_class = "skill_use_problem"
        judgment_summary = "当前轮次主要用于建立参数化技能基线，仍适合在同一技能家族内受控推进。"
        recommended_action = "continue_skill_evolution"
        next_constraints = ["继续在同一 skill 家族内受控调整参数。"]
        next_refinements = ["保持相同 evaluator 与任务定义。"]
        priorities = ["观察参数变化是否带来边界提升。"]
        update_summary = "先建立当前参数化技能基线。"

    return {
        "metadata": {"task_package": "task004", "worker": "cognition_worker"},
        "fields": {
            "problem_class": problem_class,
            "judgment_summary": judgment_summary,
            "boundary_notes": [boundary_details["boundary_statement"]],
            "uncertainty_notes": [review_details["summary"]],
            "recommended_next_worker": "skill_worker",
            "recommended_action": recommended_action,
            "continue_loop": True,
        },
        "cognition_to_skill_update": {
            "metadata": {"task_package": "task004", "loop_source": "generic_loop_engine_task004"},
            "fields": {
                "next_iteration_skill_constraints": next_constraints,
                "next_iteration_evaluator_constraints": [
                    "仍以 hosting_capacity_level 为首要判据。",
                ],
                "next_iteration_task_refinements": next_refinements,
                "search_priority_updates": priorities,
                "required_discriminating_tests": [
                    "比较结构变体 skill 与当前参数化 skill 是否真正提高 hosting_capacity_level。",
                ],
                "summary": update_summary,
            },
        },
    }
