#!/usr/bin/env python3
"""Fixture workers for generic loop engine verification."""

from __future__ import annotations

from typing import Any


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {"task_package": "fixture_loop", "worker": "skill_worker"},
        "fields": {
            "base_skill_ref": "skill.power.fixture_loop_base",
            "allowed_change_scope": ["candidate_weight"],
            "blocked_paths": ["evaluator_logic"],
            "required_tests": [
                "Run the same fixture candidate against the fixture evaluator.",
                "Preserve the fixed candidate search envelope.",
            ],
            "output_skill_path": "analysis/generic_loop_engine_fixture/candidates/fixture_candidate.yaml",
            "summary": "Create a bounded fixture candidate inside the declared search envelope.",
        },
    }


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {"task_package": "fixture_loop", "worker": "skill_worker"},
        "fields": {
            "produced_skill_ref": "skill.power.fixture_loop_candidate",
            "code_paths": ["skills/active_dev/fixture_loop_candidate.py"],
            "change_summary": ["Wrote a bounded fixture candidate artifact."],
            "expected_behavior_change": ["The candidate remains inside the declared search envelope."],
            "command": "fixture.skill_execution",
            "raw_output_path": "analysis/generic_loop_engine_fixture/candidates/fixture_candidate.yaml",
            "self_reported_risks": ["This is a fixture worker output for Phase 3 verification only."],
            "run_ref": "run.power.fixture_loop.verify_0001",
        },
    }


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {"task_package": "fixture_loop", "worker": "effectiveness_worker"},
        "fields": {
            "baseline_ref": "baseline.power.fixture_loop.default",
            "evaluator_ref": "evaluator.power.fixture_loop.default",
            "run_ref": "run.power.fixture_loop.verify_0001",
            "run_passed": False,
            "metric_summary": {
                "candidate_score": 0.4,
                "baseline_score": 0.3,
            },
            "comparison_summary": "The candidate changed behavior but did not yet justify a stronger claim.",
            "judgment_summary": "Bounded candidate established without strong effectiveness evidence.",
            "recommended_cognition_action": "Check whether the issue is still in skill use or requires structure changes.",
        },
    }


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {"task_package": "fixture_loop", "worker": "cognition_worker"},
        "fields": {
            "problem_class": "skill_use_problem",
            "judgment_summary": "The fixture result supports another bounded skill iteration before broader expansion.",
            "boundary_notes": ["The result is still limited to the fixture search envelope."],
            "uncertainty_notes": ["No second candidate has been compared yet."],
            "recommended_next_worker": "skill_worker",
            "recommended_action": "continue_skill_evolution",
            "continue_loop": True,
        },
        "cognition_to_skill_update": {
            "metadata": {"task_package": "fixture_loop", "loop_source": "generic_loop_engine_fixture"},
            "fields": {
                "next_iteration_skill_constraints": ["Keep candidate changes inside the declared fixture envelope."],
                "next_iteration_evaluator_constraints": ["Keep the same evaluator for controlled comparison."],
                "next_iteration_task_refinements": ["Do not widen the fixture scope in the verification run."],
                "search_priority_updates": ["Prioritize one more bounded candidate before any envelope expansion."],
                "required_discriminating_tests": ["Compare the next bounded candidate against the same baseline."],
                "summary": "The next iteration should remain bounded and comparable.",
            },
        },
    }
