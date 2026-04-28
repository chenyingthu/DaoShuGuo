#!/usr/bin/env python3
"""Verify real-task-001 upgraded real-task loop artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from worker_chain_helpers import verify_worker_chain_root

ROOT = REPO_ROOT / "analysis" / "real_task_001_upgrade"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def require(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing {path.relative_to(REPO_ROOT)}")
    return load_yaml(path)


def verify() -> dict[str, Any]:
    issues = verify_worker_chain_root(ROOT / "artifacts", iterations=1, require_supporting=True)
    if issues:
        raise RuntimeError("; ".join(issues))
    effectiveness = require(ROOT / "reports" / "upgrade_effectiveness_assessment.yaml")
    diagnosis = require(ROOT / "reports" / "upgrade_cognition_diagnosis.yaml")
    taste = require(ROOT / "delivery" / "taste_assessment.yaml")
    delivery = require(ROOT / "delivery" / "delivery_readiness.yaml")
    evidence = require(ROOT / "delivery" / "evidence_bundle.yaml")
    report_path = ROOT / "reports" / "real_task_upgrade_report.md"
    if not report_path.exists():
        raise RuntimeError("missing real_task_upgrade_report.md")
    metric_summary = effectiveness.get("metric_summary", {})
    if metric_summary.get("primary_delta") != 0.0:
        raise RuntimeError("expected upgraded evidence to report no primary HC improvement")
    if metric_summary.get("boundary_triggered") is not False:
        raise RuntimeError("expected upgraded evidence to report no boundary trigger")
    if taste.get("grade") != "diaomu":
        raise RuntimeError("upgrade taste must remain diaomu unless primary/boundary evidence improves")
    if delivery.get("readiness_level") != "internal_report_ready":
        raise RuntimeError("upgrade delivery must remain internal_report_ready")
    if diagnosis.get("problem_class") != "skill_structure_problem":
        raise RuntimeError("upgrade diagnosis should classify remaining problem as skill_structure_problem")
    if not evidence.get("run_refs"):
        raise RuntimeError("upgrade evidence missing run_refs")
    return {
        "status": "passed",
        "run_refs": evidence.get("run_refs", []),
        "taste": taste.get("grade"),
        "delivery": delivery.get("readiness_level"),
        "problem_class": diagnosis.get("problem_class"),
    }


def main() -> int:
    try:
        result = verify()
    except Exception as exc:
        print(f"real-task-001 upgrade verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
