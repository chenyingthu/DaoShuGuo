#!/usr/bin/env python3
"""Build real-task-001 upgraded-loop artifacts from a task004 run."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from worker_chain_helpers import (
    WorkerChainContext,
    verify_worker_chain_root,
    write_cognition_diagnosis,
    write_cognition_to_skill_update,
    write_diagnosis_input,
    write_effectiveness_assessment,
    write_loop_review,
    write_loop_routing_decision,
    write_skill_change_request,
    write_skill_change_result,
    write_yaml,
)

ROOT = REPO_ROOT / "analysis" / "real_task_001_upgrade"
ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"
DELIVERY = ROOT / "delivery"
TASK_REF = "task.power.ieee69_hosting_capacity"
EVALUATOR_REF = "evaluator.power.ieee69_hosting_capacity.default"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def object_payload(object_type: str, object_id: str, status: str, fields: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    payload = {
        "schema_version": "0.1.0",
        "object_type": object_type,
        "object_id": object_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": {
            "real_task": "real-task-001-upgrade",
            "source_plan": "plans/real-research-loop-convergence-plan.md",
        },
    }
    payload.update(fields)
    return payload


def run_ref_from_dir(run_dir: Path) -> str:
    run = load_yaml(run_dir / "run.yaml")
    return str(run["object_id"])


def summarize(metrics: dict[str, Any]) -> dict[str, Any]:
    evaluation = metrics["evaluation"]
    comparisons = evaluation["comparisons"]
    return {
        "primary_delta": comparisons["hosting_capacity_level"]["delta"],
        "loss_delta": comparisons["loss_at_boundary"]["delta"],
        "voltage_margin_delta": comparisons["voltage_margin"]["delta"],
        "boundary_trigger_delta": comparisons["boundary_trigger_scale"]["delta"],
        "control_effort_delta": comparisons["control_effort"]["delta"],
        "boundary_triggered": evaluation["boundary_triggered"],
        "claim_support_level": evaluation["claim_support_level"],
    }


def build(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir if run_dir.is_absolute() else REPO_ROOT / run_dir
    run_ref = run_ref_from_dir(run_dir)
    metrics = load_json(run_dir / "metrics.json")
    summary = summarize(metrics)
    ctx = WorkerChainContext(
        repo_root=REPO_ROOT,
        output_root=ARTIFACTS,
        domain="power",
        problem_name="ieee69_hosting_capacity_upgrade",
        task_ref=TASK_REF,
        task_package="task004",
    )
    metadata = {
        "real_task": "real-task-001-upgrade",
        "run_ref": run_ref,
        "structural_request_ref": "structural_skill_change_request.power.ieee69_hosting_capacity.reframing_0001",
    }
    _, request = write_skill_change_request(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        iteration_index=1,
        base_skill_ref="skill.power.renewable_capacity_optimizer_task004",
        allowed_change_scope=["method_change", "standard_change"],
        blocked_paths=["q_step-only escalation", "single-point mismatch evidence"],
        required_tests=["task004 voltage-sensitivity real run", "primary/secondary/control-effort comparison"],
        output_skill_path="skills/active_dev/voltage_sensitivity_capacity_optimizer_task004.py",
        summary="Implement voltage-sensitivity non-uniform inverter-Q allocation and upgraded evaluator metrics.",
    )
    _, result = write_skill_change_result(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        request_ref=request["object_id"],
        produced_skill_ref="skill.power.voltage_sensitivity_capacity_optimizer_task004",
        code_paths=[
            "skills/active_dev/voltage_sensitivity_capacity_optimizer_task004.py",
            "tasks/task004/runtime_helpers.py",
            "evaluators/task004_evaluator.py",
            "evaluators/task004_evaluator.yaml",
        ],
        change_summary=[
            "Added non-uniform voltage-sensitivity inverter-Q allocation.",
            "Added boundary-trigger and control-effort metrics to evaluator output.",
        ],
        expected_behavior_change=[
            "Improve operational-quality metrics under comparable scan envelope.",
            "Do not claim hosting-capacity gain unless primary boundary improves.",
        ],
        command=f"python orchestrator/main.py real-run-task004 --strategy voltage-sensitivity --candidate-q-step-mvar 0.35",
        raw_output_path=str((run_dir / "metrics.json").relative_to(REPO_ROOT)),
        self_reported_risks=[
            "Voltage-sensitivity allocation is a minimal heuristic, not OPF.",
            "Current scenario still may not trigger a hosting-capacity boundary.",
        ],
        run_ref=run_ref,
    )
    _, effectiveness = write_effectiveness_assessment(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        result_ref=result["object_id"],
        baseline_ref="baseline.power.ieee69_hosting_capacity.fixed_inverter_q_capacity_scan",
        evaluator_ref=EVALUATOR_REF,
        run_ref=run_ref,
        run_passed=bool(metrics["evaluation"]["passed"]),
        metric_summary=summary,
        comparison_summary=(
            "Primary hosting_capacity_level did not improve; loss and voltage_margin improved; "
            "control_effort increased; boundary was not triggered."
        ),
        judgment_summary="This is a structural method attempt with operational-quality gains, not verified hosting-capacity improvement.",
        recommended_cognition_action="retain_diaomu_and_request_boundary_scenario_or_better_method",
    )
    _, diagnosis_input = write_diagnosis_input(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        fields={
            "metric_summary": summary,
            "worker_judgment_context": [
                "Structural method attempt exists.",
                "Primary boundary improvement is absent.",
                "Boundary trigger is absent.",
                "Secondary metrics improved with added control effort.",
            ],
        },
    )
    _, diagnosis = write_cognition_diagnosis(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        problem_class="skill_structure_problem",
        judgment_summary=(
            "Voltage-sensitivity allocation is a real structural attempt, but current evidence still supports only "
            "bounded operational-quality improvement, not zhuoshi-grade hosting-capacity advancement."
        ),
        evidence_refs=[request["object_id"], result["object_id"], effectiveness["object_id"], diagnosis_input["object_id"]],
        boundary_notes=[
            "hosting_capacity_level delta is zero",
            "boundary_triggered is false",
            "control_effort increased by 0.35",
        ],
        uncertainty_notes=[
            "Scenario may be too weak to expose boundary differences.",
            "Heuristic sensitivity allocation is not yet OPF-grade.",
        ],
        recommended_next_worker="skill_worker",
        recommended_action="redesign_skill_structure",
        continue_loop=True,
    )
    _, update = write_cognition_to_skill_update(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        source_cognition_ref=diagnosis["object_id"],
        source_event_ref=effectiveness["object_id"],
        next_iteration_skill_constraints=[
            "Keep non-uniform allocation but compare under equal effort against uniform support.",
            "Do not increase q_step without an effort budget.",
        ],
        next_iteration_evaluator_constraints=[
            "Require first violation or explicit proof that no voltage boundary exists in envelope.",
            "Keep primary boundary metric separate from secondary operational quality.",
        ],
        next_iteration_task_refinements=[
            "Create a boundary-triggering stress scenario or pause primary HC claim.",
        ],
        search_priority_updates=[
            "Prioritize scenario/evaluator bracketing over more parameter tuning.",
        ],
        required_discriminating_tests=[
            "same-effort uniform vs sensitivity allocation",
            "extended envelope with first violation recording",
        ],
        summary="The next useful loop should repair scenario boundary evidence before another skill-performance claim.",
    )
    _, routing = write_loop_routing_decision(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        diagnosis_ref=diagnosis["object_id"],
        evidence_refs=[diagnosis["object_id"], effectiveness["object_id"]],
        selected_next_worker="skill_worker",
        selected_action="redesign_skill_structure",
        continue_loop=True,
        policy_basis=[
            "No primary boundary improvement.",
            "No boundary trigger.",
            "Operational-quality gains cannot support zhuoshi.",
        ],
        summary="Continue only after redesigning the skill/scenario structure to expose boundary evidence.",
    )
    _, review = write_loop_review(
        ctx=ctx,
        iteration=1,
        metadata=metadata,
        event_ref=result["object_id"],
        controller_update_ref=update["object_id"],
        iteration_plan_ref="plans/real-research-loop-convergence-plan.md",
        routing_decision_ref=routing["object_id"],
        search_space_reduction="q_step-only escalation remains excluded.",
        failure_explanation_improvement="The system now distinguishes structural attempt from verified structural improvement.",
        evaluator_refinement="Boundary trigger and control effort are visible in the evidence.",
        claim_tightening="The result remains diaomu and internal-report ready.",
        verdict="partial",
        summary="The upgraded loop is valid as a negative/diagnostic result, not as a paper-grade improvement.",
    )
    issues = verify_worker_chain_root(ARTIFACTS, iterations=1, require_supporting=True)
    if issues:
        raise RuntimeError("; ".join(issues))

    evidence = object_payload(
        "evidence_bundle",
        "evidence.power.real_task_001_upgrade.0001",
        "active",
        {
            "task_ref": TASK_REF,
            "evaluator_ref": EVALUATOR_REF,
            "run_refs": [run_ref],
            "artifact_refs": [
                {"kind": "metrics", "path": str((run_dir / "metrics.json").relative_to(REPO_ROOT))},
                {"kind": "worker_chain", "path": str(ARTIFACTS.relative_to(REPO_ROOT))},
            ],
            "claim_scope": {
                "supported_claims": [
                    "voltage-sensitivity allocation improved loss and voltage margin under current envelope",
                    "voltage-sensitivity allocation did not improve measured hosting-capacity boundary",
                    "current scenario did not trigger a boundary",
                ]
            },
            "skill_refs": ["skill.power.voltage_sensitivity_capacity_optimizer_task004"],
            "cognition_refs": [diagnosis["object_id"]],
            "gaps": [
                "No boundary-triggering scenario",
                "No same-effort uniform-vs-sensitivity ablation",
                "No time-series or probabilistic hosting-capacity evidence",
            ],
        },
    )
    taste = object_payload(
        "taste_assessment",
        "taste.power.real_task_001_upgrade.0001",
        "reviewed",
        {
            "task_ref": TASK_REF,
            "run_refs": [run_ref],
            "grade": "diaomu",
            "grade_reasoning": (
                "The upgraded run adds a real structural method attempt and stronger evaluator visibility, "
                "but it still does not improve primary hosting_capacity_level or trigger a boundary."
            ),
            "claim_ceiling": "Internal technical note on structural attempt and bounded operational-quality improvement.",
            "risk_notes": ["Scenario weakness may hide boundary differences."],
            "forbidden_claims": [
                "verified structural skill improvement",
                "hosting-capacity boundary improvement",
                "paper-candidate result",
            ],
            "recommended_report_type": "technical_note",
            "evidence_refs": [evidence["object_id"]],
            "review_status": "reviewed",
        },
    )
    delivery = {
        "schema_version": "0.1.0",
        "object_type": "deliverable_package",
        "object_id": "deliverable.power.real_task_001_upgrade",
        "created_at": utc_now(),
        "status": "reviewed",
        "task_ref": TASK_REF,
        "readiness_level": "internal_report_ready",
        "supported_outputs": ["technical_note", "experiment_record"],
        "not_ready_outputs": ["paper_candidate", "patent_candidate"],
        "supporting_refs": [evidence["object_id"], taste["object_id"], review["object_id"]],
        "missing_for_paper": [
            "Primary hosting-capacity improvement",
            "Boundary-triggering scenario",
            "Same-effort ablation",
            "External novelty evidence beyond curated seed",
        ],
        "summary": "The upgraded loop supports an internal report, not zhuoshi or paper-candidate routing.",
    }
    report = object_payload(
        "report",
        "report.power.real_task_001_upgrade.technical_note_0001",
        "reviewed",
        {
            "task_ref": TASK_REF,
            "report_type": "technical_note",
            "title": "real-task-001 Upgrade Report",
            "summary": (
                "Voltage-sensitivity allocation is a genuine structural attempt and improves secondary operational metrics, "
                "but it does not improve the primary hosting-capacity boundary under the current scenario."
            ),
            "evidence_bundle_refs": [evidence["object_id"]],
            "taste_assessment_ref": taste["object_id"],
            "audience": "internal_team",
            "boundary_statement": "This report only supports static, control-strategy-conditioned, current-envelope conclusions.",
            "failure_summary": "No primary boundary gain and no boundary trigger.",
            "next_steps": [
                "Build boundary-triggering scenario before another skill-performance claim.",
                "Run same-effort uniform vs sensitivity allocation ablation.",
            ],
            "claim_summary": [taste["claim_ceiling"]],
        },
    )
    dump_yaml(DELIVERY / "evidence_bundle.yaml", evidence)
    dump_yaml(DELIVERY / "taste_assessment.yaml", taste)
    dump_yaml(DELIVERY / "delivery_readiness.yaml", delivery)
    dump_yaml(REPORTS / "upgrade_effectiveness_assessment.yaml", effectiveness)
    dump_yaml(REPORTS / "upgrade_cognition_diagnosis.yaml", diagnosis)
    dump_yaml(REPORTS / "upgrade_loop_review.yaml", review)
    dump_yaml(REPORTS / "report.yaml", report)
    (REPORTS / "real_task_upgrade_report.md").write_text(
        "\n".join(
            [
                "# real-task-001 Upgrade Report",
                "",
                "## Verdict",
                "",
                "The upgraded task004 loop completed one structural method attempt using voltage-sensitivity inverter-Q allocation.",
                "",
                "It did not improve the primary `hosting_capacity_level` and did not trigger a boundary. It did improve loss and voltage margin while increasing control effort.",
                "",
                "## Evidence",
                "",
                f"- Run: `{run_ref}`",
                f"- Primary delta: `{summary['primary_delta']}`",
                f"- Loss delta: `{summary['loss_delta']}`",
                f"- Voltage margin delta: `{summary['voltage_margin_delta']}`",
                f"- Control effort delta: `{summary['control_effort_delta']}`",
                f"- Boundary triggered: `{summary['boundary_triggered']}`",
                "",
                "## Judgment",
                "",
                "This is a valid structural attempt, not a verified structural skill improvement. The result remains `diaomu` and `internal_report_ready`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "status": "passed",
        "run_ref": run_ref,
        "claim_support_level": summary["claim_support_level"],
        "taste": taste["grade"],
        "delivery": delivery["readiness_level"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real-task-001 upgrade artifacts.")
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    try:
        result = build(Path(args.run_dir))
    except Exception as exc:
        print(f"real-task-001 upgrade build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
