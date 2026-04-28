#!/usr/bin/env python3
"""Verify generic diagnosis classification and routing guards."""

from __future__ import annotations

from generic_diagnosis_layer import (
    build_diagnosis_input,
    derive_routing_decision_fields,
    validate_worker_output,
)


def assert_issue_contains(issues: list[str], expected: str) -> None:
    if not any(expected in issue for issue in issues):
        raise RuntimeError(f"expected issue containing {expected!r}, got {issues!r}")


def main() -> int:
    adapter = {
        "object_id": "task_adapter.power.fixture_loop",
        "task_ref": "task.power.fixture_loop",
        "baseline_binding": {"baseline_refs": ["baseline.power.fixture_loop.default"]},
        "candidate_binding": {"candidate_kind": "skill_variant"},
        "evaluator_binding": {"evaluator_ref": "evaluator.power.fixture_loop.default"},
        "search_envelope": {"modifiable_dimensions": ["candidate_weight"]},
        "diagnosis_hook_config": {"expected_failure_modes": ["bounded_candidate"]},
    }
    request = {"object_id": "skill_change_request.power.fixture_loop.0001"}
    result = {"object_id": "skill_change_result.power.fixture_loop.0001"}
    assessment = {"object_id": "effectiveness_assessment.power.fixture_loop.0001"}
    diagnosis_input = build_diagnosis_input(
        task_adapter=adapter,
        skill_change_request=request,
        skill_change_result=result,
        effectiveness_assessment=assessment,
        chain_verification_issues=[],
    )

    valid_output = {
        "fields": {
            "problem_class": "skill_structure_problem",
            "judgment_summary": "The fixture skill needs structural redesign.",
            "boundary_notes": ["Bounded fixture evidence only."],
            "uncertainty_notes": ["No second candidate was tested."],
            "recommended_next_worker": "skill_worker",
            "recommended_action": "redesign_skill_structure",
            "continue_loop": True,
        }
    }
    issues = validate_worker_output(valid_output, diagnosis_input)
    if issues:
        raise RuntimeError(f"valid diagnosis output rejected: {issues}")

    routing = derive_routing_decision_fields(
        {
            **valid_output["fields"],
            "evidence_refs": [
                request["object_id"],
                result["object_id"],
                assessment["object_id"],
            ],
        }
    )
    if routing["selected_next_worker"] != "skill_worker":
        raise RuntimeError("routing did not derive selected_next_worker from diagnosis")

    invalid_stop_output = {
        "fields": {
            **valid_output["fields"],
            "problem_class": "evaluator_design_problem",
            "recommended_next_worker": "skill_worker",
            "recommended_action": "redesign_skill_structure",
            "continue_loop": True,
        }
    }
    issues = validate_worker_output(invalid_stop_output, diagnosis_input)
    assert_issue_contains(issues, "evaluator_design_problem")
    assert_issue_contains(issues, "continue_loop=True conflicts")

    invalid_class_output = {"fields": {**valid_output["fields"], "problem_class": "insufficient_evidence"}}
    issues = validate_worker_output(invalid_class_output, diagnosis_input)
    assert_issue_contains(issues, "invalid problem_class")

    missing_input = build_diagnosis_input(
        task_adapter=adapter,
        skill_change_request=request,
        skill_change_result=None,
        effectiveness_assessment=assessment,
        chain_verification_issues=[],
    )
    issues = validate_worker_output(valid_output, missing_input)
    assert_issue_contains(issues, "missing required evidence")

    print("Generic diagnosis layer verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
