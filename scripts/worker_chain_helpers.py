#!/usr/bin/env python3
"""Generic worker-chain object writers and verifiers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from generic_diagnosis_layer import validate_persisted_diagnosis


REQUIRED_CHAIN_TYPES = [
    "skill_change_request",
    "skill_change_result",
    "effectiveness_assessment",
    "cognition_diagnosis",
    "loop_routing_decision",
]

SUPPORTING_CHAIN_TYPES = [
    "diagnosis_input",
    "cognition_to_skill_update",
    "loop_review",
]

ROUTING_JUDGMENT_FIELDS = [
    "problem_class",
    "judgment_summary",
    "boundary_notes",
    "uncertainty_notes",
]


@dataclass(frozen=True)
class WorkerChainContext:
    repo_root: Path
    output_root: Path
    domain: str
    problem_name: str
    task_ref: str
    task_package: str

    def object_ref(self, object_type: str, iteration: int) -> str:
        return f"{object_type}.{self.domain}.{self.problem_name}.{iteration:04d}"

    def artifact_path(self, object_type: str, iteration: int) -> Path:
        return self.output_root / object_type / f"iter{iteration:02d}.yaml"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rel(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def build_object_payload(
    *,
    ctx: WorkerChainContext,
    object_type: str,
    iteration: int,
    status: str,
    metadata: dict[str, Any],
    fields: dict[str, Any],
    object_version: str = "0.1.0",
) -> dict[str, Any]:
    now = utc_now()
    payload: dict[str, Any] = {
        "schema_version": "0.1.0",
        "object_type": object_type,
        "object_id": ctx.object_ref(object_type, iteration),
        "object_version": object_version,
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": metadata,
        "task_ref": ctx.task_ref,
    }
    payload.update(fields)
    return payload


def write_chain_object(
    *,
    ctx: WorkerChainContext,
    object_type: str,
    iteration: int,
    status: str,
    metadata: dict[str, Any],
    fields: dict[str, Any],
    object_version: str = "0.1.0",
) -> tuple[Path, dict[str, Any]]:
    path = ctx.artifact_path(object_type, iteration)
    payload = build_object_payload(
        ctx=ctx,
        object_type=object_type,
        iteration=iteration,
        status=status,
        metadata=metadata,
        fields=fields,
        object_version=object_version,
    )
    write_yaml(path, payload)
    return path, payload


def write_skill_change_request(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    iteration_index: int,
    base_skill_ref: str,
    allowed_change_scope: list[str],
    blocked_paths: list[str],
    required_tests: list[str],
    output_skill_path: str,
    summary: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="skill_change_request",
        iteration=iteration,
        status="ready",
        metadata=metadata,
        fields={
            "iteration_index": iteration_index,
            "base_skill_ref": base_skill_ref,
            "allowed_change_scope": allowed_change_scope,
            "blocked_paths": blocked_paths,
            "required_tests": required_tests,
            "output_skill_path": output_skill_path,
            "summary": summary,
        },
    )


def write_skill_change_result(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    request_ref: str,
    produced_skill_ref: str,
    code_paths: list[str],
    change_summary: list[str],
    expected_behavior_change: list[str],
    command: str,
    raw_output_path: str,
    self_reported_risks: list[str],
    run_ref: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="skill_change_result",
        iteration=iteration,
        status="completed",
        metadata=metadata,
        fields={
            "request_ref": request_ref,
            "produced_skill_ref": produced_skill_ref,
            "code_paths": code_paths,
            "change_summary": change_summary,
            "expected_behavior_change": expected_behavior_change,
            "command": command,
            "raw_output_path": raw_output_path,
            "self_reported_risks": self_reported_risks,
            "run_ref": run_ref,
        },
    )


def write_effectiveness_assessment(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    result_ref: str,
    baseline_ref: str,
    evaluator_ref: str,
    run_ref: str,
    run_passed: bool,
    metric_summary: dict[str, Any],
    comparison_summary: str,
    judgment_summary: str,
    recommended_cognition_action: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="effectiveness_assessment",
        iteration=iteration,
        status="completed",
        metadata=metadata,
        fields={
            "result_ref": result_ref,
            "baseline_ref": baseline_ref,
            "evaluator_ref": evaluator_ref,
            "run_ref": run_ref,
            "run_passed": run_passed,
            "metric_summary": metric_summary,
            "comparison_summary": comparison_summary,
            "judgment_summary": judgment_summary,
            "recommended_cognition_action": recommended_cognition_action,
        },
    )


def write_diagnosis_input(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    fields: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="diagnosis_input",
        iteration=iteration,
        status="ready",
        metadata=metadata,
        fields=fields,
    )


def write_cognition_diagnosis(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    problem_class: str,
    judgment_summary: str,
    evidence_refs: list[str],
    boundary_notes: list[str],
    uncertainty_notes: list[str],
    recommended_next_worker: str,
    recommended_action: str,
    continue_loop: bool,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="cognition_diagnosis",
        iteration=iteration,
        status="reviewed",
        metadata=metadata,
        fields={
            "problem_class": problem_class,
            "judgment_summary": judgment_summary,
            "evidence_refs": evidence_refs,
            "boundary_notes": boundary_notes,
            "uncertainty_notes": uncertainty_notes,
            "recommended_next_worker": recommended_next_worker,
            "recommended_action": recommended_action,
            "continue_loop": continue_loop,
        },
    )


def write_cognition_to_skill_update(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    source_cognition_ref: str,
    source_event_ref: str,
    next_iteration_skill_constraints: list[str],
    next_iteration_evaluator_constraints: list[str],
    next_iteration_task_refinements: list[str],
    search_priority_updates: list[str],
    required_discriminating_tests: list[str],
    summary: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="cognition_to_skill_update",
        iteration=iteration,
        status="reviewed",
        metadata=metadata,
        fields={
            "source_cognition_ref": source_cognition_ref,
            "source_event_ref": source_event_ref,
            "next_iteration_skill_constraints": next_iteration_skill_constraints,
            "next_iteration_evaluator_constraints": next_iteration_evaluator_constraints,
            "next_iteration_task_refinements": next_iteration_task_refinements,
            "search_priority_updates": search_priority_updates,
            "required_discriminating_tests": required_discriminating_tests,
            "summary": summary,
        },
    )


def write_loop_routing_decision(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    diagnosis_ref: str,
    evidence_refs: list[str],
    selected_next_worker: str,
    selected_action: str,
    continue_loop: bool,
    policy_basis: list[str],
    summary: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="loop_routing_decision",
        iteration=iteration,
        status="reviewed",
        metadata=metadata,
        fields={
            "diagnosis_ref": diagnosis_ref,
            "evidence_refs": evidence_refs,
            "selected_next_worker": selected_next_worker,
            "selected_action": selected_action,
            "continue_loop": continue_loop,
            "policy_basis": policy_basis,
            "summary": summary,
        },
    )


def write_loop_review(
    *,
    ctx: WorkerChainContext,
    iteration: int,
    metadata: dict[str, Any],
    event_ref: str,
    controller_update_ref: str,
    iteration_plan_ref: str,
    routing_decision_ref: str,
    search_space_reduction: str,
    failure_explanation_improvement: str,
    evaluator_refinement: str,
    claim_tightening: str,
    verdict: str,
    summary: str,
) -> tuple[Path, dict[str, Any]]:
    return write_chain_object(
        ctx=ctx,
        object_type="loop_review",
        iteration=iteration,
        status="reviewed",
        metadata=metadata,
        fields={
            "event_ref": event_ref,
            "controller_update_ref": controller_update_ref,
            "iteration_plan_ref": iteration_plan_ref,
            "routing_decision_ref": routing_decision_ref,
            "search_space_reduction": search_space_reduction,
            "failure_explanation_improvement": failure_explanation_improvement,
            "evaluator_refinement": evaluator_refinement,
            "claim_tightening": claim_tightening,
            "verdict": verdict,
            "summary": summary,
        },
    )


def _collect_iterations(root: Path) -> list[int]:
    request_root = root / "skill_change_request"
    if not request_root.exists():
        return []
    iterations: list[int] = []
    for path in sorted(request_root.glob("iter*.yaml")):
        stem = path.stem
        suffix = stem.replace("iter", "")
        if suffix.isdigit():
            iterations.append(int(suffix))
    return iterations


def verify_worker_chain_root(
    root: Path,
    iterations: int | None = None,
    require_supporting: bool = False,
) -> list[str]:
    issues: list[str] = []
    check_iterations = list(range(1, iterations + 1)) if iterations is not None else _collect_iterations(root)
    if not check_iterations:
        return [f"{root}: no worker-chain iterations found"]

    for iteration in check_iterations:
        loaded: dict[str, dict[str, Any]] = {}
        suffix = f"iter{iteration:02d}.yaml"
        for object_type in REQUIRED_CHAIN_TYPES + SUPPORTING_CHAIN_TYPES:
            path = root / object_type / suffix
            if path.exists():
                loaded[object_type] = load_yaml(path)
            elif object_type in REQUIRED_CHAIN_TYPES or (require_supporting and object_type == "diagnosis_input"):
                issues.append(f"iter{iteration:02d}: missing required object {object_type}")

        request = loaded.get("skill_change_request")
        result = loaded.get("skill_change_result")
        assessment = loaded.get("effectiveness_assessment")
        diagnosis = loaded.get("cognition_diagnosis")
        routing = loaded.get("loop_routing_decision")
        review = loaded.get("loop_review")
        update = loaded.get("cognition_to_skill_update")
        diagnosis_input = loaded.get("diagnosis_input")

        if request and request.get("object_type") != "skill_change_request":
            issues.append(f"iter{iteration:02d}: skill_change_request has wrong object_type")
        if result and result.get("request_ref") != (request or {}).get("object_id"):
            issues.append(f"iter{iteration:02d}: skill_change_result.request_ref does not point to skill_change_request")
        if assessment and assessment.get("result_ref") != (result or {}).get("object_id"):
            issues.append(
                f"iter{iteration:02d}: effectiveness_assessment.result_ref does not point to skill_change_result"
            )
        if diagnosis:
            issues.extend(
                f"iter{iteration:02d}: {issue}"
                for issue in validate_persisted_diagnosis(diagnosis, diagnosis_input)
            )
            evidence_refs = diagnosis.get("evidence_refs", [])
            for required_ref in [
                (request or {}).get("object_id"),
                (result or {}).get("object_id"),
                (assessment or {}).get("object_id"),
            ]:
                if required_ref and required_ref not in evidence_refs:
                    issues.append(
                        f"iter{iteration:02d}: cognition_diagnosis missing evidence ref {required_ref}"
                    )
        if routing:
            if routing.get("diagnosis_ref") != (diagnosis or {}).get("object_id"):
                issues.append(
                    f"iter{iteration:02d}: loop_routing_decision.diagnosis_ref does not point to cognition_diagnosis"
                )
            evidence_refs = routing.get("evidence_refs", [])
            if (diagnosis or {}).get("object_id") and (diagnosis or {}).get("object_id") not in evidence_refs:
                issues.append(
                    f"iter{iteration:02d}: loop_routing_decision missing cognition_diagnosis evidence ref"
                )
            for field in ROUTING_JUDGMENT_FIELDS:
                if field in routing:
                    issues.append(
                        f"iter{iteration:02d}: controller_overreach detected in loop_routing_decision field {field}"
                    )
        if update and update.get("source_cognition_ref") != (diagnosis or {}).get("object_id"):
            issues.append(
                f"iter{iteration:02d}: cognition_to_skill_update.source_cognition_ref does not point to cognition_diagnosis"
            )
        if review:
            if review.get("controller_update_ref") != (update or {}).get("object_id"):
                issues.append(
                    f"iter{iteration:02d}: loop_review.controller_update_ref does not point to cognition_to_skill_update"
                )
            if review.get("routing_decision_ref") != (routing or {}).get("object_id"):
                issues.append(
                    f"iter{iteration:02d}: loop_review.routing_decision_ref does not point to loop_routing_decision"
                )

    return issues
