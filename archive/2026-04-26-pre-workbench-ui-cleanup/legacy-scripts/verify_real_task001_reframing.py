#!/usr/bin/env python3
"""Verify real-task-001 research-framing learning chain."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "real_task_001"
REFRAMING = ROOT / "reframing"
LITERATURE = ROOT / "literature"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def require(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing {path.relative_to(REPO_ROOT)}")
    return load_yaml(path)


def require_contains(items: list[Any], needle: str, label: str) -> None:
    text = json.dumps(items, ensure_ascii=False)
    if needle not in text:
        raise RuntimeError(f"{label} does not contain {needle!r}")


def verify() -> dict[str, Any]:
    evidence = require(REFRAMING / "input_evidence_pack.yaml")
    gap = require(REFRAMING / "current_gap_summary.yaml")
    need = require(LITERATURE / "learning_need.yaml")
    context = require(LITERATURE / "learning_context_pack.yaml")
    framing = require(LITERATURE / "problem_framing_map.yaml")
    methods = require(LITERATURE / "method_family_map.yaml")
    metrics = require(LITERATURE / "metric_taxonomy.yaml")
    claims = require(LITERATURE / "claim_thresholds.yaml")
    design = require(LITERATURE / "experiment_design_recommendation.yaml")
    diagnosis = require(REFRAMING / "skill_structure_diagnosis.yaml")
    request = require(REFRAMING / "structural_skill_change_request.yaml")
    upgrade = require(REFRAMING / "research_framing_upgrade.yaml")
    evaluator_request = require(REFRAMING / "evaluator_upgrade_request.yaml")
    scenario_request = require(REFRAMING / "scenario_upgrade_request.yaml")
    zhuoshi = require(REFRAMING / "zhuoshi_threshold.yaml")

    if len(evidence.get("run_refs", [])) < 3:
        raise RuntimeError("evidence pack must include at least three real-task run refs")
    if need.get("source_review_ref") != evidence["object_id"]:
        raise RuntimeError("learning_need does not reference input evidence pack")
    if context.get("learning_need_ref") != need["object_id"]:
        raise RuntimeError("learning_context_pack does not reference learning_need")
    for obj, name in [(framing, "framing"), (methods, "methods"), (metrics, "metrics"), (claims, "claims"), (design, "design")]:
        if obj.get("learning_context_ref") != context["object_id"]:
            raise RuntimeError(f"{name} map does not reference learning_context_pack")
    if diagnosis.get("learning_context_ref") != context["object_id"]:
        raise RuntimeError("skill_structure_diagnosis does not reference learning_context_pack")
    if request.get("diagnosis_ref") != diagnosis["object_id"]:
        raise RuntimeError("structural_skill_change_request does not reference diagnosis")
    if evaluator_request.get("diagnosis_ref") != diagnosis["object_id"]:
        raise RuntimeError("evaluator upgrade request does not reference diagnosis")
    if scenario_request.get("diagnosis_ref") != diagnosis["object_id"]:
        raise RuntimeError("scenario upgrade request does not reference diagnosis")
    if upgrade.get("decision") != "upgrade":
        raise RuntimeError("research framing cognition upgrade must use decision=upgrade")
    if zhuoshi.get("learning_context_ref") != context["object_id"]:
        raise RuntimeError("zhuoshi threshold does not reference learning context")

    require_contains(methods.get("method_families", []), "voltage_sensitivity_q_allocation", "method_family_map")
    require_contains(metrics.get("primary_metric_refs", []), "hosting_capacity_level", "metric_taxonomy")
    forbidden_claims = json.dumps(claims.get("forbidden_claims", []), ensure_ascii=False)
    if "secondary" not in forbidden_claims and "次级" not in forbidden_claims and "loss" not in forbidden_claims:
        raise RuntimeError("claim_thresholds does not prevent secondary-metric overclaim")
    require_contains(design.get("excluded_shortcuts", []), "q_step", "experiment_design_recommendation")
    if request.get("change_type") == "skill_use_tuning":
        raise RuntimeError("structural request degraded to skill_use_tuning")
    if not request.get("method_changes"):
        raise RuntimeError("structural request must include method changes")

    return {
        "status": "passed",
        "evidence_pack": evidence["object_id"],
        "learning_context": context["object_id"],
        "diagnosis": diagnosis["object_id"],
        "structural_request": request["object_id"],
        "gap_summary": gap["object_id"],
    }


def main() -> int:
    try:
        result = verify()
    except Exception as exc:
        print(f"real-task-001 reframing verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
