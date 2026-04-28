#!/usr/bin/env python3
"""Run cross-task portfolio assessment for structural skill work."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "analysis" / "portfolio"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to an object")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path.relative_to(REPO_ROOT)}")


def task003_assessment() -> dict[str, Any]:
    assessment_path = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02" / "skill_structure_assessment.yaml"
    require(assessment_path)
    assessment = load_yaml(assessment_path)
    return {
        "task_ref": "task.power.ieee69_renewable_reactive_opt",
        "topic": "renewable reactive optimization",
        "evidence_refs": [assessment["object_id"]],
        "skill_use_signal": "strong",
        "structural_signal": assessment["structural_verdict"],
        "recommendation": "continue_with_fixed_budget_ablation",
        "rationale": (
            "task003 has real metric improvement and a structural request, but skill-use evidence is still stronger than method/process/standard evidence."
        ),
        "risk": "local search-envelope tuning trap",
        "next_test": "Compare structural request with metric-only tuning under fixed evaluator and fixed search budget.",
    }


def task004_assessment() -> dict[str, Any]:
    metrics_path = REPO_ROOT / "runs" / "task004" / "run_0011" / "metrics.json"
    diagnosis_path = REPO_ROOT / "analysis" / "task004" / "skill_diagnosis_0001" / "skill_use_structure_diagnosis.yaml"
    overclaim_path = REPO_ROOT / "analysis" / "task004" / "boundary_overclaim_20260421_033407" / "boundary_overclaim_check.yaml"
    for path in [metrics_path, diagnosis_path, overclaim_path]:
        require(path)
    metrics = load_json(metrics_path)
    diagnosis = load_yaml(diagnosis_path)
    overclaim = load_yaml(overclaim_path)
    comparison = metrics.get("evaluation", {}).get("comparisons", {})
    hosting_delta = comparison.get("hosting_capacity_level", {}).get("delta")
    loss_improved = comparison.get("loss_at_boundary", {}).get("improved")
    voltage_improved = comparison.get("voltage_margin", {}).get("improved")
    recommendation = "redirect_to_structural_method_or_pause_parameter_tuning"
    if hosting_delta == 0 and loss_improved and voltage_improved:
        rationale = (
            "secondary metrics improve as Q increases, but the primary hosting_capacity_level remains unchanged; further parameter tuning risks local trap."
        )
    else:
        rationale = "task004 evidence is mixed and should not be pushed without a sharper structural hypothesis."
    return {
        "task_ref": "task.power.ieee69_hosting_capacity",
        "topic": "hosting capacity boundary",
        "evidence_refs": [diagnosis["object_id"], overclaim["object_id"]],
        "skill_use_signal": "strong_secondary_metric_signal",
        "structural_signal": "suspected_but_unverified",
        "recommendation": recommendation,
        "rationale": rationale,
        "risk": "boundary overclaim and primary-metric stagnation",
        "next_test": "Stop q_step escalation; test non-uniform inverter allocation or bus-subset control against fixed-q baseline.",
    }


def task005_assessment() -> dict[str, Any]:
    metrics_path = REPO_ROOT / "runs" / "task005" / "run_0001" / "metrics.json"
    mismatch_path = REPO_ROOT / "analysis" / "task005" / "mismatch_20260422_001023" / "task_mismatch_check.yaml"
    overclaim_path = REPO_ROOT / "analysis" / "task005" / "resilience_overclaim_20260422_001023" / "boundary_overclaim_check.yaml"
    for path in [metrics_path, mismatch_path, overclaim_path]:
        require(path)
    metrics = load_json(metrics_path)
    mismatch = load_yaml(mismatch_path)
    overclaim = load_yaml(overclaim_path)
    comparison = metrics.get("evaluation", {}).get("comparisons", {})
    cost = comparison.get("restoration_action_cost_proxy", {})
    cost_delta = cost.get("delta")
    recommendation = "continue_as_standard_or_evaluator_work_before_skill_structure"
    rationale = (
        "task005 has restoration benefit, but cost and resilience-claim semantics dominate; structural skill work is premature until standard/evaluator quality improves."
    )
    if isinstance(cost_delta, (int, float)) and cost_delta > 0:
        rationale += " The candidate improves restoration while increasing action cost, so evaluation standards need explicit tradeoff treatment."
    return {
        "task_ref": "task.power.ieee69_restoration_resilience",
        "topic": "restoration resilience",
        "evidence_refs": [mismatch["object_id"], overclaim["object_id"]],
        "skill_use_signal": "moderate",
        "structural_signal": "standard_gap_dominant",
        "recommendation": recommendation,
        "rationale": rationale,
        "risk": "resilience overclaim and cost-benefit ambiguity",
        "next_test": "Build a cost-benefit standard and resilience claim gate before another skill-structure loop.",
    }


def build_portfolio() -> dict[str, Any]:
    now = utc_now()
    task_assessments = [task003_assessment(), task004_assessment(), task005_assessment()]
    return {
        "schema_version": "0.1.0",
        "object_type": "research_portfolio_assessment",
        "object_id": "portfolio_assessment.power.skill_structure.20260425",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {
            "protocol": "cross-task-skill-structure",
            "assessor": "deterministic_mvp",
        },
        "assessed_task_refs": [item["task_ref"] for item in task_assessments],
        "portfolio_question": "Which tasks should receive further structural skill work, and which should pause or redirect?",
        "task_assessments": task_assessments,
        "cross_task_findings": [
            "task003 is the best immediate ablation target, but only for fixed-budget structural validation.",
            "task004 should not continue q_step tuning; it needs a structural method hypothesis for hosting-capacity boundary movement.",
            "task005 should prioritize standard/evaluator work because cost-benefit and resilience-claim semantics dominate current uncertainty.",
            "A research loop should stop or redirect when primary metrics stagnate or when evaluation semantics are weaker than skill implementation.",
        ],
        "recommended_allocation": [
            "40% task003 fixed-budget structural-vs-metric-only ablation.",
            "35% task004 structural method design for non-uniform/bus-aware hosting-capacity control.",
            "25% task005 standard/evaluator redesign for cost-benefit resilience claims.",
        ],
        "stop_or_pause_recommendations": [
            "Pause task003 raw search-grid expansion until ablation is defined.",
            "Stop task004 q_step-only escalation because primary hosting-capacity boundary did not move.",
            "Pause task005 skill-structure claim work until restoration cost-benefit standard is explicit.",
        ],
        "next_tests": [
            "task003: fixed-budget ablation comparing structural request with metric-only tuning.",
            "task004: non-uniform inverter-Q allocation or bus-subset strategy under unchanged evaluator.",
            "task005: evaluator standard revision that separates restoration benefit, action cost, and resilience claim boundary.",
        ],
        "summary": (
            "The portfolio view prevents local-trap behavior: task003 remains useful for ablation, task004 should redirect from parameter tuning to structural method design, and task005 should focus on standards before further skill evolution."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run cross-task portfolio assessment.")
    parser.parse_args()
    payload = build_portfolio()
    output = OUT_DIR / "skill_structure_portfolio_20260425.yaml"
    write_yaml(output, payload)
    print(f"Portfolio assessment written to {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
