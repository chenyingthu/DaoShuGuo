#!/usr/bin/env python3
"""Generic diagnosis substrate for loop worker outputs.

This module does not author research judgment. It validates that a cognition
worker's judgment is evidence-bound, classifiable, and routable.
"""

from __future__ import annotations

from typing import Any


PROBLEM_CLASSES = {
    "framework_problem",
    "task_adapter_problem",
    "skill_use_problem",
    "skill_structure_problem",
    "evaluator_design_problem",
}

RECOMMENDED_NEXT_WORKERS = {
    "skill_worker",
    "effectiveness_worker",
    "cognition_worker",
    "adapter_repair_worker",
    "framework_repair_worker",
    "human_review",
}

ROUTING_POLICY: dict[str, dict[str, Any]] = {
    "framework_problem": {
        "workers": {"framework_repair_worker", "human_review"},
        "continue_loop": False,
        "actions": {"repair_framework", "human_review"},
    },
    "task_adapter_problem": {
        "workers": {"adapter_repair_worker", "human_review"},
        "continue_loop": False,
        "actions": {"repair_adapter", "repair_task_adapter", "human_review"},
    },
    "skill_use_problem": {
        "workers": {"skill_worker", "cognition_worker", "human_review"},
        "continue_loop": True,
        "actions": {"continue_skill_evolution", "repair_skill_use", "human_review"},
    },
    "skill_structure_problem": {
        "workers": {"skill_worker", "cognition_worker", "human_review"},
        "continue_loop": True,
        "actions": {"continue_skill_evolution", "redesign_skill_structure", "human_review"},
    },
    "evaluator_design_problem": {
        "workers": {"effectiveness_worker", "adapter_repair_worker", "human_review"},
        "continue_loop": False,
        "actions": {"repair_evaluator", "repair_adapter", "human_review"},
    },
}

REQUIRED_DIAGNOSIS_FIELDS = [
    "problem_class",
    "judgment_summary",
    "boundary_notes",
    "uncertainty_notes",
    "recommended_next_worker",
    "recommended_action",
    "continue_loop",
]


def _object_ref(payload: dict[str, Any] | None) -> str | None:
    if not payload:
        return None
    object_id = payload.get("object_id")
    return object_id if isinstance(object_id, str) and object_id else None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def build_diagnosis_input(
    *,
    task_adapter: dict[str, Any],
    skill_change_request: dict[str, Any] | None,
    skill_change_result: dict[str, Any] | None,
    effectiveness_assessment: dict[str, Any] | None,
    chain_verification_issues: list[str],
) -> dict[str, Any]:
    """Build the deterministic input package given to cognition workers."""

    task_adapter_checks = {
        "has_baseline_binding": bool(task_adapter.get("baseline_binding", {}).get("baseline_refs")),
        "has_candidate_binding": bool(task_adapter.get("candidate_binding")),
        "has_evaluator_binding": bool(task_adapter.get("evaluator_binding", {}).get("evaluator_ref")),
        "has_search_envelope": bool(task_adapter.get("search_envelope")),
        "has_diagnosis_hook_config": bool(task_adapter.get("diagnosis_hook_config")),
    }
    required_refs = {
        "skill_change_request_ref": _object_ref(skill_change_request),
        "skill_change_result_ref": _object_ref(skill_change_result),
        "effectiveness_assessment_ref": _object_ref(effectiveness_assessment),
    }
    missing_refs = [name for name, value in required_refs.items() if value is None]
    adapter_missing = [name for name, ok in task_adapter_checks.items() if not ok]
    return {
        "task_ref": task_adapter.get("task_ref"),
        "task_adapter_ref": task_adapter.get("object_id"),
        "required_evidence_refs": [value for value in required_refs.values() if value],
        "missing_required_evidence": missing_refs,
        "task_adapter_checks": task_adapter_checks,
        "adapter_missing_inputs": adapter_missing,
        "artifact_chain_verification": {
            "status": "passed" if not chain_verification_issues else "failed",
            "issues": chain_verification_issues,
        },
        "diagnosis_hook_config": task_adapter.get("diagnosis_hook_config", {}),
    }


def validate_diagnosis_fields(fields: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_DIAGNOSIS_FIELDS:
        if field not in fields:
            issues.append(f"cognition_diagnosis missing required field {field}")

    problem_class = fields.get("problem_class")
    if problem_class not in PROBLEM_CLASSES:
        issues.append(f"cognition_diagnosis has invalid problem_class {problem_class!r}")

    if not _non_empty_string(fields.get("judgment_summary")):
        issues.append("cognition_diagnosis.judgment_summary must be a non-empty string")
    if not _string_list(fields.get("boundary_notes")):
        issues.append("cognition_diagnosis.boundary_notes must be a non-empty string list")
    if not _string_list(fields.get("uncertainty_notes")):
        issues.append("cognition_diagnosis.uncertainty_notes must be a non-empty string list")

    next_worker = fields.get("recommended_next_worker")
    if next_worker not in RECOMMENDED_NEXT_WORKERS:
        issues.append(f"cognition_diagnosis has invalid recommended_next_worker {next_worker!r}")

    if not _non_empty_string(fields.get("recommended_action")):
        issues.append("cognition_diagnosis.recommended_action must be a non-empty string")
    if not isinstance(fields.get("continue_loop"), bool):
        issues.append("cognition_diagnosis.continue_loop must be boolean")

    if problem_class in ROUTING_POLICY:
        policy = ROUTING_POLICY[problem_class]
        if next_worker not in policy["workers"]:
            issues.append(
                f"cognition_diagnosis routes {problem_class} to {next_worker!r}, "
                f"expected one of {sorted(policy['workers'])}"
            )
        if isinstance(fields.get("continue_loop"), bool) and fields["continue_loop"] != policy["continue_loop"]:
            issues.append(
                f"cognition_diagnosis continue_loop={fields['continue_loop']} conflicts with "
                f"{problem_class} policy continue_loop={policy['continue_loop']}"
            )

    return issues


def validate_worker_output(output: dict[str, Any], diagnosis_input: dict[str, Any]) -> list[str]:
    """Validate raw cognition worker output before persistence."""

    issues: list[str] = []
    fields = output.get("fields")
    if not isinstance(fields, dict):
        return ["cognition_diagnosis_worker output must include mapping field 'fields'"]

    issues.extend(validate_diagnosis_fields(fields))
    if diagnosis_input.get("missing_required_evidence"):
        issues.append(
            "diagnosis_input is missing required evidence: "
            + ", ".join(diagnosis_input["missing_required_evidence"])
        )
    if diagnosis_input.get("artifact_chain_verification", {}).get("status") != "passed":
        issues.append("diagnosis_input artifact chain verification did not pass")
    return issues


def validate_persisted_diagnosis(
    diagnosis: dict[str, Any],
    diagnosis_input: dict[str, Any] | None = None,
) -> list[str]:
    """Validate a persisted cognition_diagnosis object."""

    issues = validate_diagnosis_fields(diagnosis)
    evidence_refs = diagnosis.get("evidence_refs")
    if not _string_list(evidence_refs):
        issues.append("cognition_diagnosis.evidence_refs must be a non-empty string list")

    if diagnosis_input:
        for required_ref in diagnosis_input.get("required_evidence_refs", []):
            if required_ref not in (evidence_refs or []):
                issues.append(f"cognition_diagnosis missing required evidence ref {required_ref}")
        if diagnosis_input.get("adapter_missing_inputs"):
            problem_class = diagnosis.get("problem_class")
            if problem_class not in {"task_adapter_problem", "framework_problem"}:
                issues.append(
                    "diagnosis_input reports missing adapter inputs, but cognition_diagnosis "
                    f"classified problem as {problem_class!r}"
                )

    return issues


def derive_routing_decision_fields(diagnosis: dict[str, Any]) -> dict[str, Any]:
    """Return controller-safe routing fields copied from diagnosis."""

    issues = validate_persisted_diagnosis(diagnosis)
    if issues:
        raise RuntimeError("invalid diagnosis for routing: " + "; ".join(issues))
    return {
        "selected_next_worker": diagnosis["recommended_next_worker"],
        "selected_action": diagnosis["recommended_action"],
        "continue_loop": bool(diagnosis["continue_loop"]),
        "policy_basis": [
            "Route only from cognition_diagnosis and complete object-chain evidence.",
            f"Problem class {diagnosis['problem_class']} follows generic diagnosis routing policy.",
        ],
    }
