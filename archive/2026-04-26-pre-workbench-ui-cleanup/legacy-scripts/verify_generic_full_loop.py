#!/usr/bin/env python3
"""Verify generic full-loop validation artifacts."""

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

from worker_chain_helpers import verify_worker_chain_root  # noqa: E402


FULL_LOOP_ROOT = REPO_ROOT / "analysis" / "full_loop_validation"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def slug_task_ref(task_ref: str) -> str:
    return task_ref.replace("task.", "").replace(".", "_")


def task_ref_from_task_id(task_id: str) -> str:
    adapter_path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    if adapter_path.exists():
        return str(load_yaml(adapter_path).get("task_ref", f"task.power.{task_id}"))
    return f"task.power.{task_id}"


def candidate_workspaces(task_id: str, backend: str) -> list[Path]:
    task_ref = task_ref_from_task_id(task_id)
    slugs = [
        task_ref.replace("task.", "").replace(".", "_"),
        task_ref.replace("task.", "").replace(".", "."),
        task_id,
    ]
    roots: list[Path] = []
    for slug in slugs:
        roots.extend(sorted((FULL_LOOP_ROOT / "runs" / backend / slug).glob("*")))
    return [path for path in roots if path.is_dir()]


def latest_workspace(task_id: str, backend: str) -> Path:
    workspaces = candidate_workspaces(task_id, backend)
    if not workspaces:
        raise RuntimeError(f"{task_id}/{backend}: no full-loop workspace found")
    return sorted(workspaces, key=lambda p: p.stat().st_mtime)[-1]


def verify_workspace(task_id: str, backend: str) -> dict[str, Any]:
    workspace = latest_workspace(task_id, backend)
    run_path = workspace / "run.yaml"
    if not run_path.exists():
        raise RuntimeError(f"{task_id}/{backend}: missing run.yaml in {workspace}")
    run = load_yaml(run_path)
    issues: list[str] = []
    if run.get("status") != "completed":
        issues.append(f"run status is {run.get('status')}")
    artifacts_root = workspace / "artifacts"
    issues.extend(verify_worker_chain_root(artifacts_root, iterations=1, require_supporting=True))
    if not (workspace / "artifact_index.json").exists():
        issues.append("missing artifact_index.json")
    onboarding_path = REPO_ROOT / "analysis" / "onboarding" / task_id / "task_readiness_report.yaml"
    if onboarding_path.exists():
        onboarding = load_yaml(onboarding_path)
        if onboarding.get("readiness_status", "").startswith("blocked"):
            issues.append(f"blocked task entered full loop: {onboarding.get('readiness_status')}")
    return {
        "task_id": task_id,
        "task_ref": run.get("task_ref", task_ref_from_task_id(task_id)),
        "backend": backend,
        "workspace": str(workspace.relative_to(REPO_ROOT)),
        "verdict": "passed" if not issues else "failed",
        "issues": issues,
        "required_objects_present": not issues,
    }


def verify_blocked(task_id: str, backend: str) -> dict[str, Any]:
    onboarding_path = REPO_ROOT / "analysis" / "onboarding" / task_id / "task_readiness_report.yaml"
    if not onboarding_path.exists():
        raise RuntimeError(f"{task_id}: missing onboarding report")
    onboarding = load_yaml(onboarding_path)
    readiness = onboarding.get("readiness_status", "")
    workspaces = candidate_workspaces(task_id, backend)
    issues: list[str] = []
    if not str(readiness).startswith("blocked"):
        issues.append(f"expected blocked readiness, got {readiness}")
    if workspaces:
        issues.append("blocked task has full-loop workspace")
    return {
        "task_id": task_id,
        "task_ref": onboarding.get("task_ref", task_ref_from_task_id(task_id)),
        "backend": backend,
        "workspace": None,
        "verdict": "blocked_ok" if not issues else "failed",
        "issues": issues,
        "readiness_status": readiness,
    }


def write_report(results: list[dict[str, Any]]) -> Path:
    now = utc_now()
    validated = [item["task_ref"] for item in results if item["verdict"] == "passed"]
    blocked = [item["task_ref"] for item in results if item["verdict"] == "blocked_ok"]
    failed = [item for item in results if item["verdict"] not in {"passed", "blocked_ok"}]
    proof_level = "level_1_deterministic_full_loop"
    agentic_passes = [
        item for item in results if item["backend"] != "deterministic" and item["verdict"] == "passed"
    ]
    agentic_blocked = [
        item for item in results if item["backend"] != "deterministic" and item["verdict"] == "blocked_ok"
    ]
    if agentic_passes:
        proof_level = "level_2_single_agentic_full_loop"
    agentic_task_ids = {item["task_id"] for item in agentic_passes}
    agentic_validated_classes = {
        "task006_near_neighbor",
        "task008_bad_candidate",
        "task009_evaluator_gap",
        "task010_literature_required",
        "task011_portfolio_stop",
    }
    if (
        {"task006_near_neighbor", "task008_bad_candidate", "task009_evaluator_gap"}.issubset(agentic_task_ids)
        and agentic_blocked
    ):
        proof_level = "level_3_cross_task_agentic_full_loop_partial"
    if agentic_validated_classes.issubset(agentic_task_ids) and agentic_blocked:
        proof_level = "level_3_cross_task_agentic_full_loop"
    payload = {
        "schema_version": "0.1.0",
        "object_type": "full_loop_validation_report",
        "object_id": "full_loop_validation.power.generic_full_loop.current",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed" if not failed else "blocked",
        "metadata": {"protocol": "generic-full-loop-validation"},
        "proof_level": proof_level,
        "validated_task_refs": sorted(set(validated)),
        "blocked_task_refs": sorted(set(blocked)),
        "backend_refs": sorted(set(item["backend"] for item in results)),
        "validation_results": results,
        "framework_gaps": [
            f"{item['task_id']}/{item['backend']}: {issue}"
            for item in failed
            for issue in item.get("issues", [])
        ],
        "task_gaps": [],
        "not_proven": [
            "Level 4 backend-robust agentic full loop is not proven unless both Codex/OMX and Pi full loops pass.",
            "Level 5 research-quality autonomous cognition is not proven by fixture-level validation runs.",
        ],
        "summary": f"Generic full-loop validation checked {len(results)} task/backend outcomes.",
    }
    path = FULL_LOOP_ROOT / "generic_full_loop_validation_report.yaml"
    write_yaml(path, payload)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify generic full-loop artifacts.")
    parser.add_argument("--task")
    parser.add_argument("--backend", default="deterministic")
    parser.add_argument("--blocked", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    try:
        if args.all:
            matrix_path = FULL_LOOP_ROOT / "validation_matrix.json"
            if not matrix_path.exists():
                raise RuntimeError("missing analysis/full_loop_validation/validation_matrix.json")
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            results = []
            for item in matrix.get("checks", []):
                if item.get("expected") == "blocked":
                    results.append(verify_blocked(item["task_id"], item["backend"]))
                else:
                    results.append(verify_workspace(item["task_id"], item["backend"]))
            report_path = write_report(results)
            failures = [item for item in results if item["verdict"] not in {"passed", "blocked_ok"}]
            print(f"Generic full-loop validation report written to {report_path.relative_to(REPO_ROOT)}")
            if failures:
                print(json.dumps(failures, indent=2, ensure_ascii=False), file=sys.stderr)
                return 1
            return 0
        if not args.task:
            raise RuntimeError("--task is required unless --all is used")
        result = verify_blocked(args.task, args.backend) if args.blocked else verify_workspace(args.task, args.backend)
    except Exception as exc:
        print(f"Generic full-loop verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["verdict"] in {"passed", "blocked_ok"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
