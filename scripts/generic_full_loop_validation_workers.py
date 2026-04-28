#!/usr/bin/env python3
"""Data-driven workers for generic full-loop validation tasks."""

from __future__ import annotations

from typing import Any


DEFAULT_SCENARIO = {
    "base_skill_ref": "skill.power.baseline_solver",
    "produced_skill_id": "skill.power.baseline_solver",
    "allowed_change_scope": ["declared_task_adapter_scope"],
    "blocked_paths": ["evaluator_logic", "task_definition"],
    "required_tests": ["Compare candidate and baseline under the declared evaluator."],
    "output_skill_path": "analysis/full_loop_validation/generated_skill_candidate.yaml",
    "synthetic_run_id": "run.power.generic_full_loop_validation.0001",
    "run_passed": True,
    "metric_summary": {
        "baseline_score": 1.0,
        "candidate_score": 1.0,
        "delta": 0.0,
    },
    "comparison_summary": "Generic validation candidate matches the baseline under the declared evaluator.",
    "effectiveness_judgment": "No effectiveness improvement is claimed.",
    "recommended_cognition_action": "Classify whether the result warrants continuation, repair, or stop.",
    "problem_class": "evidence_insufficiency",
    "cognition_judgment": "The evidence is sufficient to complete the loop but insufficient for a research claim.",
    "recommended_action": "pause_for_review",
    "continue_loop": False,
    "next_worker": "cognition_worker",
}


def scenario(inputs: dict[str, Any]) -> dict[str, Any]:
    adapter = inputs["task_adapter"]
    data = dict(DEFAULT_SCENARIO)
    data.update(adapter.get("experimental", {}).get("validation_scenario", {}))
    return data


def task_package(inputs: dict[str, Any]) -> str:
    return inputs["task_adapter"].get("metadata", {}).get("task_package", "generic_full_loop_validation")


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    return {
        "metadata": {"task_package": task_package(inputs), "worker": "skill_worker"},
        "fields": {
            "base_skill_ref": data["base_skill_ref"],
            "allowed_change_scope": data["allowed_change_scope"],
            "blocked_paths": data["blocked_paths"],
            "required_tests": data["required_tests"],
            "output_skill_path": data["output_skill_path"],
            "summary": data.get("skill_request_summary", "Generate a bounded candidate under the adapter contract."),
        },
    }


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    return {
        "metadata": {"task_package": task_package(inputs), "worker": "skill_worker"},
        "fields": {
            "produced_skill_ref": data["produced_skill_id"],
            "code_paths": data.get("code_paths", [data["output_skill_path"]]),
            "change_summary": data.get("change_summary", ["Materialized the declared validation candidate."]),
            "expected_behavior_change": data.get(
                "expected_behavior_change",
                ["Candidate behavior follows the validation scenario declared in the adapter."],
            ),
            "command": data.get("command", "data_driven_validation_worker"),
            "raw_output_path": data.get("raw_output_path", data["output_skill_path"]),
            "self_reported_risks": data.get("self_reported_risks", ["Validation scenario is data driven."]),
            "run_ref": data["synthetic_run_id"],
        },
    }


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    adapter = inputs["task_adapter"]
    baseline_refs = adapter.get("baseline_binding", {}).get("baseline_refs", [])
    evaluator_ref = adapter.get("evaluator_binding", {}).get("evaluator_ref", "evaluator.power.validation.default")
    return {
        "metadata": {"task_package": task_package(inputs), "worker": "effectiveness_worker"},
        "fields": {
            "baseline_ref": baseline_refs[0] if baseline_refs else "baseline.power.validation.default",
            "evaluator_ref": evaluator_ref,
            "run_ref": data["synthetic_run_id"],
            "run_passed": bool(data["run_passed"]),
            "metric_summary": data["metric_summary"],
            "comparison_summary": data["comparison_summary"],
            "judgment_summary": data["effectiveness_judgment"],
            "recommended_cognition_action": data["recommended_cognition_action"],
        },
    }


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    return {
        "metadata": {"task_package": task_package(inputs), "worker": "cognition_worker"},
        "fields": {
            "problem_class": data["problem_class"],
            "judgment_summary": data["cognition_judgment"],
            "boundary_notes": data.get("boundary_notes", ["Bounded by the declared validation scenario."]),
            "uncertainty_notes": data.get("uncertainty_notes", ["No broader research claim is made."]),
            "recommended_next_worker": data["next_worker"],
            "recommended_action": data["recommended_action"],
            "continue_loop": bool(data["continue_loop"]),
        },
        "cognition_to_skill_update": {
            "metadata": {"task_package": task_package(inputs), "loop_source": "generic_full_loop_validation"},
            "fields": {
                "next_iteration_skill_constraints": data.get(
                    "next_iteration_skill_constraints",
                    ["Preserve task and evaluator definitions."],
                ),
                "next_iteration_evaluator_constraints": data.get(
                    "next_iteration_evaluator_constraints",
                    ["Use the declared evaluator for the next comparable run."],
                ),
                "next_iteration_task_refinements": data.get("next_iteration_task_refinements", []),
                "search_priority_updates": data.get("search_priority_updates", ["Follow the routing decision."]),
                "required_discriminating_tests": data.get(
                    "required_discriminating_tests",
                    ["Run one discriminating candidate-vs-baseline comparison."],
                ),
                "summary": data.get("update_summary", "Route the next step according to cognition diagnosis."),
            },
        },
    }
