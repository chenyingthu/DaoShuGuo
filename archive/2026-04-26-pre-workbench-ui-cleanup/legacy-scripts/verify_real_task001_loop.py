#!/usr/bin/env python3
"""Verify real-task-001 multi-round research-loop artifacts."""

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

ROOT = REPO_ROOT / "analysis" / "real_task_001"
TASK_REF = "task.power.ieee69_hosting_capacity"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing {path.relative_to(REPO_ROOT)}")


def verify_round(index: int) -> dict[str, Any]:
    round_dir = ROOT / "rounds" / f"round_{index:03d}"
    require(round_dir / "round_analysis.json")
    require(round_dir / "run_record.yaml")
    require(round_dir / "artifact_index.json")
    analysis = load_json(round_dir / "round_analysis.json")
    run_ref = analysis.get("run_ref")
    if not isinstance(run_ref, str) or not run_ref.startswith("run.power.ieee69_hosting_capacity."):
        raise RuntimeError(f"round {index}: invalid run_ref {run_ref!r}")
    run_serial = run_ref.rsplit(".", 1)[1]
    require(REPO_ROOT / "runs" / "task004" / f"run_{run_serial}" / "metrics.json")
    issues = verify_worker_chain_root(round_dir / "artifacts", require_supporting=True)
    if issues:
        raise RuntimeError(f"round {index}: " + "; ".join(issues))
    verification = load_json(round_dir / "verification.json")
    if verification.get("status") != "passed":
        raise RuntimeError(f"round {index}: verification status {verification.get('status')}")
    return analysis


def verify() -> dict[str, Any]:
    require(ROOT / "readiness" / "task_readiness_report.yaml")
    readiness = load_yaml(ROOT / "readiness" / "task_readiness_report.yaml")
    if readiness.get("readiness_status") != "ready_to_run":
        raise RuntimeError(f"readiness is {readiness.get('readiness_status')}")
    analyses = [verify_round(index) for index in range(1, 4)]
    if any(item.get("task_ref") and item["task_ref"] != TASK_REF for item in analyses):
        raise RuntimeError("analysis task_ref mismatch")
    if any(item["primary_improved"] for item in analyses):
        raise RuntimeError("real-task-001 verifier expected no primary hosting-capacity improvement in current evidence")
    if not any(item["secondary_improved"] for item in analyses):
        raise RuntimeError("expected at least one secondary metric improvement")
    if not any(item["mismatch_probe"] for item in analyses):
        raise RuntimeError("expected mismatch negative-control round")
    deliverable = load_yaml(ROOT / "delivery" / "delivery_readiness.yaml")
    if deliverable.get("readiness_level") != "internal_report_ready":
        raise RuntimeError("deliverable must route to internal_report_ready")
    report_path = ROOT / "reports" / "real_task_research_report.md"
    require(report_path)
    report_text = report_path.read_text(encoding="utf-8")
    if "did not improve the primary" not in report_text:
        raise RuntimeError("report does not state primary metric non-improvement")
    return {
        "status": "passed",
        "rounds": len(analyses),
        "run_refs": [item["run_ref"] for item in analyses],
        "deliverable": deliverable.get("readiness_level"),
    }


def main() -> int:
    try:
        result = verify()
    except Exception as exc:
        print(f"real-task-001 verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
