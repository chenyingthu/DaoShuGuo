#!/usr/bin/env python3
"""Generic task onboarding readiness check."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_ROUTE = {
    "ready_to_run": "run_research_pipeline",
    "ready_for_framing_only": "framing_only",
    "blocked_missing_task_contract": "repair_task_package",
    "blocked_missing_baseline": "repair_task_package",
    "blocked_missing_evaluator": "repair_evaluator",
    "blocked_missing_runtime": "repair_adapter",
    "blocked_missing_skill": "repair_skill_binding",
    "blocked_missing_metrics_mapping": "repair_adapter",
    "blocked_missing_claim_gate": "repair_evaluator",
    "blocked_missing_adapter": "repair_adapter",
    "pause_for_human_review": "pause_for_human_review",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def path_exists(path_text: str) -> bool:
    return (REPO_ROOT / path_text).exists()


def collect_yaml_object_ids(root: Path) -> set[str]:
    object_ids: set[str] = set()
    for path in root.glob("**/*.yaml"):
        try:
            obj = load_yaml(path)
        except Exception:
            continue
        object_id = obj.get("object_id")
        if isinstance(object_id, str):
            object_ids.add(object_id)
    return object_ids


def collect_registry_skill_ids() -> set[str]:
    registry_path = REPO_ROOT / "skills" / "registry.json"
    if not registry_path.exists():
        return set()
    try:
        import json

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    skills = registry.get("skills")
    if not isinstance(skills, list):
        return set()
    skill_ids: set[str] = set()
    for item in skills:
        if not isinstance(item, dict):
            continue
        object_id = item.get("object_id")
        if isinstance(object_id, str):
            skill_ids.add(object_id)
    return skill_ids


def collect_known_skill_ids() -> set[str]:
    skill_ids = collect_yaml_object_ids(REPO_ROOT / "skills")
    skill_ids.update(collect_yaml_object_ids(REPO_ROOT / "schemas" / "samples"))
    skill_ids.update(collect_registry_skill_ids())
    return skill_ids


def collect_task_contract(adapter: dict[str, Any], missing: list[str], available: list[str]) -> dict[str, Any] | None:
    package_path = adapter.get("task_package_path")
    if not isinstance(package_path, str):
        missing.append("adapter.task_package_path")
        return None
    task_path = REPO_ROOT / package_path / "task.yaml"
    if not task_path.exists():
        missing.append(rel(task_path))
        return None
    available.append(rel(task_path))
    task = load_yaml(task_path)
    for item in task.get("input_artifacts", []):
        if not isinstance(item, dict):
            continue
        artifact_path = item.get("path")
        if not isinstance(artifact_path, str):
            continue
        if path_exists(artifact_path):
            available.append(artifact_path)
        else:
            missing.append(artifact_path)
    return task


def available_skill_refs(refs: list[str]) -> set[str]:
    if not refs:
        return set()
    skill_ids = collect_known_skill_ids()
    return {ref for ref in refs if ref in skill_ids}


def determine_status(adapter: dict[str, Any], missing: list[str], available: list[str]) -> str:
    if any(item.endswith("task.yaml") or item.startswith("adapter.task_package_path") for item in missing):
        return "blocked_missing_task_contract"
    baseline_path = adapter.get("baseline_path")
    if not isinstance(baseline_path, str) or not path_exists(baseline_path):
        missing.append("adapter.baseline_path" if not isinstance(baseline_path, str) else baseline_path)
        return "blocked_missing_baseline"
    available.append(baseline_path)
    evaluator_path = adapter.get("evaluator_path")
    if not isinstance(evaluator_path, str) or not path_exists(evaluator_path):
        missing.append("adapter.evaluator_path" if not isinstance(evaluator_path, str) else evaluator_path)
        return "blocked_missing_evaluator"
    available.append(evaluator_path)
    runtime_entry = adapter.get("runtime_entry")
    if not isinstance(runtime_entry, dict) or not runtime_entry.get("path"):
        missing.append("adapter.runtime_entry.path")
        return "blocked_missing_runtime"
    runtime_path = runtime_entry.get("path")
    if not isinstance(runtime_path, str) or not path_exists(runtime_path):
        missing.append("adapter.runtime_entry.path" if not isinstance(runtime_path, str) else runtime_path)
        return "blocked_missing_runtime"
    available.append(runtime_path)
    metrics_mapping = adapter.get("metrics_mapping")
    primary = metrics_mapping.get("primary") if isinstance(metrics_mapping, dict) else None
    if not isinstance(primary, list) or not primary:
        missing.append("adapter.metrics_mapping.primary")
        return "blocked_missing_metrics_mapping"
    candidate_refs = adapter.get("candidate_skill_refs", [])
    fallback_refs = adapter.get("fallback_skill_refs", [])
    declared_skill_refs = [
        ref for ref in [*candidate_refs, *fallback_refs] if isinstance(ref, str)
    ]
    found_skill_refs = available_skill_refs(declared_skill_refs)
    available.extend(sorted(found_skill_refs))
    if not found_skill_refs:
        if declared_skill_refs:
            missing.extend(f"skill_ref:{ref}" for ref in declared_skill_refs)
        else:
            missing.append("adapter.candidate_skill_refs|adapter.fallback_skill_refs")
        return "blocked_missing_skill"
    claim_gates = adapter.get("claim_gates")
    if not isinstance(claim_gates, list) or not claim_gates:
        missing.append("adapter.claim_gates")
        return "blocked_missing_claim_gate"
    if any(isinstance(gate, dict) and gate.get("status") in {"needs_standard_repair", "blocked"} for gate in claim_gates):
        return "ready_for_framing_only"
    return "ready_to_run"


def report_status(status: str) -> str:
    if status == "ready_to_run":
        return "ready"
    if status == "ready_for_framing_only":
        return "framing_only"
    return "blocked"


def build_report(task_id: str) -> dict[str, Any]:
    adapter_path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    missing: list[str] = []
    available: list[str] = []
    now = utc_now()
    if not adapter_path.exists():
        status = "blocked_missing_adapter"
        adapter = {"object_id": "task_adapter.missing", "task_ref": f"task.unknown.{task_id}"}
    else:
        adapter = load_yaml(adapter_path)
        available.append(rel(adapter_path))
        collect_task_contract(adapter, missing, available)
        status = determine_status(adapter, missing, available)
    route = STATUS_ROUTE[status]
    blocked_stages = [] if status == "ready_to_run" else ["run", "review", "structural_learning"]
    supported_stages = adapter.get("supported_downstream_stages", [])
    if status == "ready_for_framing_only":
        supported_stages = ["framing"]
        blocked_stages = ["run", "skill_evolution", "structural_claim"]
    next_actions = {
        "ready_to_run": ["Run generic research pipeline."],
        "ready_for_framing_only": ["Run framing or evaluator repair before skill evolution."],
        "blocked_missing_task_contract": ["Repair task package contract."],
        "blocked_missing_baseline": ["Add or bind baseline.yaml."],
        "blocked_missing_evaluator": ["Add evaluator YAML and runtime entry."],
        "blocked_missing_runtime": ["Add runnable runtime entry in adapter."],
        "blocked_missing_skill": ["Bind candidate or fallback skill refs."],
        "blocked_missing_metrics_mapping": ["Define primary metrics mapping in adapter."],
        "blocked_missing_claim_gate": ["Declare at least one claim gate."],
        "blocked_missing_adapter": ["Create adapters/{task_id}.yaml."],
        "pause_for_human_review": ["Ask human reviewer to resolve ambiguity."],
    }[status]
    task_ref = adapter.get("task_ref", f"task.unknown.{task_id}")
    known_risks = adapter.get("known_task_risks", [])
    risk_summary = ""
    if isinstance(known_risks, list) and known_risks:
        risk_summary = "; risks: " + "; ".join(str(item) for item in known_risks)
    return {
        "schema_version": "0.1.0",
        "object_type": "task_readiness_report",
        "object_id": f"task_readiness.{task_id}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": report_status(status),
        "metadata": {
            "protocol": "generic-task-onboarding",
            "known_task_risks": known_risks if isinstance(known_risks, list) else [],
        },
        "task_id": task_id,
        "adapter_ref": adapter.get("object_id", "task_adapter.missing"),
        "task_ref": task_ref,
        "readiness_status": status,
        "recommended_route": route,
        "missing_items": sorted(set(missing)),
        "available_items": sorted(set(available)),
        "blocked_stages": blocked_stages,
        "supported_stages": supported_stages,
        "evidence_refs": [task_ref, adapter.get("object_id", "task_adapter.missing")],
        "next_actions": next_actions,
        "summary": f"{task_id} onboarding status: {status}; route: {route}{risk_summary}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run generic task onboarding check.")
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    report = build_report(args.task)
    output = REPO_ROOT / "analysis" / "onboarding" / args.task / "task_readiness_report.yaml"
    write_yaml(output, report)
    print(f"Task onboarding report written to {rel(output)}")
    print(f"Status: {report['readiness_status']}")
    print(f"Route: {report['recommended_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
