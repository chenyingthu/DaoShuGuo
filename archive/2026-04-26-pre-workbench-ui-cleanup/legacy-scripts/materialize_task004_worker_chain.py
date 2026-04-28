#!/usr/bin/env python3
"""Materialize task004 worker-chain artifacts through generic object-chain helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from worker_chain_helpers import (
    WorkerChainContext,
    load_json,
    rel,
    write_cognition_diagnosis,
    write_cognition_to_skill_update,
    write_effectiveness_assessment,
    write_loop_review,
    write_loop_routing_decision,
    write_skill_change_request,
    write_skill_change_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_skill_evolution" / "state" / "iterations"
OUTPUT_ROOT = REPO_ROOT / "analysis" / "worker_chain" / "task004"

TASK004_CONTEXT = WorkerChainContext(
    repo_root=REPO_ROOT,
    output_root=OUTPUT_ROOT,
    domain="power",
    problem_name="ieee69_hosting_capacity",
    task_ref="task.power.ieee69_hosting_capacity",
    task_package="task004",
)


def build_skill_change_request(
    ctx: WorkerChainContext, iteration: int, request: dict[str, Any], previous_skill_ref: str | None
) -> tuple[Path, dict[str, Any]]:
    q_step = request["candidate_q_step_mvar"]
    return write_skill_change_request(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "execution_mode": "parameterized_skill_evolution"},
        iteration_index=iteration,
        base_skill_ref=previous_skill_ref or "skill.power.renewable_capacity_optimizer_task004",
        allowed_change_scope=["candidate_q_step_mvar"],
        blocked_paths=["single_point_operation_proxy"],
        required_tests=[
            "Run the same inverter-support skill under the current evaluator.",
            "Check whether hosting_capacity_level improves relative to the previous candidate.",
        ],
        output_skill_path="parameterized:tasks/task004/constraints.yaml:candidate_q_step_mvar",
        summary=f"Set candidate_q_step_mvar to {q_step:.2f} and test whether the same skill improves.",
    )


def build_skill_change_result(
    ctx: WorkerChainContext,
    iteration: int,
    request_payload: dict[str, Any],
    request_path: Path,
    request: dict[str, Any],
    run_ref: str,
) -> tuple[Path, dict[str, Any]]:
    q_step = request["candidate_q_step_mvar"]
    return write_skill_change_result(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "executor": "pi_parameterized_skill_loop"},
        request_ref=request_payload["object_id"],
        produced_skill_ref="skill.power.renewable_capacity_optimizer_task004",
        code_paths=["skills/active_dev/renewable_capacity_optimizer_task004.py"],
        change_summary=[f"candidate_q_step_mvar set to {q_step:.2f}"],
        expected_behavior_change=[
            "Increase reactive support effort while keeping the same hosting-capacity scan structure.",
        ],
        command=(
            "python orchestrator/main.py real-run-task004 --strategy inverter-support "
            f"--candidate-q-step-mvar {q_step}"
        ),
        raw_output_path=rel(ctx.repo_root, request_path),
        self_reported_risks=[
            "This is a parameterized skill variant, not yet a structural redesign.",
        ],
        run_ref=run_ref,
    )


def build_effectiveness_assessment(
    ctx: WorkerChainContext, iteration: int, analysis: dict[str, Any], result_payload: dict[str, Any]
) -> tuple[Path, dict[str, Any]]:
    return write_effectiveness_assessment(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "worker": "effectiveness_worker"},
        result_ref=result_payload["object_id"],
        baseline_ref="baseline.power.ieee69_hosting_capacity.default",
        evaluator_ref="evaluator.power.ieee69_hosting_capacity.default",
        run_ref=analysis["run_ref"],
        run_passed=analysis["run_passed"],
        metric_summary={
            "candidate_hosting_capacity_level": analysis["candidate_hosting_capacity_level"],
            "baseline_hosting_capacity_level": analysis["baseline_hosting_capacity_level"],
            "candidate_loss_at_boundary": analysis["candidate_loss_at_boundary"],
            "candidate_voltage_margin": analysis["candidate_voltage_margin"],
        },
        comparison_summary=analysis["evaluation_summary"],
        judgment_summary=analysis["improvement_judgment"],
        recommended_cognition_action=(
            "Decide whether this remains a skill-use issue or has become a skill-structure issue."
        ),
    )


def build_cognition_diagnosis(
    ctx: WorkerChainContext,
    iteration: int,
    analysis: dict[str, Any],
    request_payload: dict[str, Any],
    result_payload: dict[str, Any],
    assessment_payload: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    if analysis["progress_type"] == "parameter_change_no_boundary_gain":
        problem_class = "skill_structure_problem"
        judgment_summary = "连续参数调整后边界仍不变，主线问题已从参数使用转向技能结构不足。"
        recommended_action = "Stop enlarging q_step as the main path and explore structural skill variants."
    else:
        problem_class = "skill_use_problem"
        judgment_summary = "当前轮次主要用于建立参数化技能基线，仍适合在同一技能家族内受控推进。"
        recommended_action = "Keep the same skill family and continue controlled parameterized exploration."
    return write_cognition_diagnosis(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "worker": "cognition_worker"},
        problem_class=problem_class,
        judgment_summary=judgment_summary,
        evidence_refs=[
            request_payload["object_id"],
            result_payload["object_id"],
            assessment_payload["object_id"],
        ],
        boundary_notes=[
            "Current judgment remains bounded by the present hosting-capacity scan envelope.",
        ],
        uncertainty_notes=[
            "No structural variant has been compared yet in the current iteration set.",
        ],
        recommended_next_worker="skill_worker",
        recommended_action=recommended_action,
        continue_loop=True,
    )


def build_cognition_to_skill_update(
    ctx: WorkerChainContext, iteration: int, analysis: dict[str, Any], diagnosis_payload: dict[str, Any]
) -> tuple[Path, dict[str, Any]]:
    if analysis["progress_type"] == "parameter_change_no_boundary_gain":
        summary = "连续参数调整后边界仍不变，后续主线应转向技能结构升级。"
        next_constraints = ["不得再把继续加 q_step 当作主线技能升级。"]
        next_refinements = ["需要引入非均匀 inverter Q 分配或 bus 子集选择。"]
        priorities = ["优先探索技能结构变体，而不是继续扩大同幅注入参数。"]
    else:
        summary = "先建立当前参数化技能基线。"
        next_constraints = ["继续在同一 skill 家族内受控调整参数。"]
        next_refinements = ["保持相同 evaluator 与任务定义。"]
        priorities = ["观察参数变化是否带来边界提升。"]
    return write_cognition_to_skill_update(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "loop_source": "worker_materialization"},
        source_cognition_ref=diagnosis_payload["object_id"],
        source_event_ref=diagnosis_payload["object_id"],
        next_iteration_skill_constraints=next_constraints,
        next_iteration_evaluator_constraints=[
            "仍以 hosting_capacity_level 为首要判据。",
        ],
        next_iteration_task_refinements=next_refinements,
        search_priority_updates=priorities,
        required_discriminating_tests=[
            "比较结构变体 skill 与当前参数化 skill 是否真正提高 hosting_capacity_level。",
        ],
        summary=summary,
    )


def build_loop_routing_decision(
    ctx: WorkerChainContext,
    iteration: int,
    request_payload: dict[str, Any],
    result_payload: dict[str, Any],
    assessment_payload: dict[str, Any],
    diagnosis_payload: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    continue_loop = bool(diagnosis_payload["continue_loop"])
    return write_loop_routing_decision(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "controller_mode": "non_authoring"},
        diagnosis_ref=diagnosis_payload["object_id"],
        evidence_refs=[
            request_payload["object_id"],
            result_payload["object_id"],
            assessment_payload["object_id"],
            diagnosis_payload["object_id"],
        ],
        selected_next_worker=diagnosis_payload["recommended_next_worker"],
        selected_action=diagnosis_payload["recommended_action"],
        continue_loop=continue_loop,
        policy_basis=[
            "Route only from cognition_diagnosis and complete object-chain evidence.",
        ],
        summary="Controller routes the next step from diagnosis evidence without authoring worker judgments.",
    )


def build_loop_review(
    ctx: WorkerChainContext,
    iteration: int,
    request_payload: dict[str, Any],
    assessment_payload: dict[str, Any],
    update_payload: dict[str, Any],
    routing_payload: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    return write_loop_review(
        ctx=ctx,
        iteration=iteration,
        metadata={"task_package": ctx.task_package, "review_mode": "worker_boundary_enforced"},
        event_ref=assessment_payload["object_id"],
        controller_update_ref=update_payload["object_id"],
        iteration_plan_ref=request_payload["object_id"],
        routing_decision_ref=routing_payload["object_id"],
        search_space_reduction="本轮将下一步从继续调参收缩为结构变体探索。",
        failure_explanation_improvement="效果不再被直接解释为 skill 无效，而是拆分为 use / structure 两层。",
        evaluator_refinement="保留 hosting_capacity_level 首要判据。",
        claim_tightening="没有边界提升时不得声称 skill improvement。",
        verdict="substantiated",
        summary="本轮 generic worker 对象链已物化，controller 不再直接下场解释结果。",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize task004 worker chain from skill-evolution results.")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--input-root", type=Path, default=INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    ctx = WorkerChainContext(
        repo_root=REPO_ROOT,
        output_root=args.output_root,
        domain=TASK004_CONTEXT.domain,
        problem_name=TASK004_CONTEXT.problem_name,
        task_ref=TASK004_CONTEXT.task_ref,
        task_package=TASK004_CONTEXT.task_package,
    )
    previous_skill_ref: str | None = None
    outputs: dict[str, str] = {}
    for iteration in range(1, args.iterations + 1):
        analysis = load_json(args.input_root / f"iter_{iteration:03d}" / "round_analysis.json")
        request = load_json(args.input_root / f"iter_{iteration:03d}" / "request.json")
        request_path, request_payload = build_skill_change_request(ctx, iteration, request, previous_skill_ref)
        _, result_payload = build_skill_change_result(ctx, iteration, request_payload, request_path, request, analysis["run_ref"])
        _, assessment_payload = build_effectiveness_assessment(ctx, iteration, analysis, result_payload)
        _, diagnosis_payload = build_cognition_diagnosis(
            ctx, iteration, analysis, request_payload, result_payload, assessment_payload
        )
        _, update_payload = build_cognition_to_skill_update(ctx, iteration, analysis, diagnosis_payload)
        _, routing_payload = build_loop_routing_decision(
            ctx, iteration, request_payload, result_payload, assessment_payload, diagnosis_payload
        )
        review_path, _ = build_loop_review(
            ctx, iteration, request_payload, assessment_payload, update_payload, routing_payload
        )
        outputs[f"iter_{iteration:02d}"] = rel(ctx.repo_root, review_path)
        previous_skill_ref = "skill.power.renewable_capacity_optimizer_task004"

    import json

    print(json.dumps(outputs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
