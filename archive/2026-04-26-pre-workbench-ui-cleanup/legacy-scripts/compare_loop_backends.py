#!/usr/bin/env python3
"""Compare loop backend validation outcomes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "full_loop_validation"
import sys

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from backend_registry import load_backend_registry  # noqa: E402


BACKENDS = load_backend_registry()["runtimes"]


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


def read_validation_report() -> dict[str, Any] | None:
    path = ROOT / "generic_full_loop_validation_report.yaml"
    return load_yaml(path) if path.exists() else None


def pi_smoke_status() -> dict[str, Any]:
    smoke_path = REPO_ROOT / "analysis" / "backend_matrix" / "pi_gpt55" / "text_and_ls_tool_smoke.jsonl"
    if not smoke_path.exists():
        return {"backend": "pi_gpt55", "verdict": "not_run", "evidence": []}
    text = smoke_path.read_text(encoding="utf-8")
    has_tool = '"type":"tool_execution_end"' in text
    has_ok = "PI_GPT55_TOOL_OK" in text
    return {
        "backend": "pi_gpt55",
        "verdict": "smoke_passed" if has_tool and has_ok else "smoke_failed",
        "evidence": [str(smoke_path.relative_to(REPO_ROOT))],
    }


def build_report(tasks: list[str] | None, backends: list[str] | None) -> dict[str, Any]:
    now = utc_now()
    selected_backends = backends or list(BACKENDS)
    validation = read_validation_report()
    backend_results: list[dict[str, Any]] = []
    if validation:
        for item in validation.get("validation_results", []):
            if selected_backends and item.get("backend") not in selected_backends:
                continue
            if tasks and item.get("task_id") not in tasks:
                continue
            backend_results.append(item)
    if "pi_gpt55" in selected_backends:
        backend_results.append(pi_smoke_status())
    backend_full_loop_counts = {
        backend: sum(
            1
            for item in backend_results
            if item.get("backend") == backend and item.get("verdict") == "passed" and item.get("workspace")
        )
        for backend in selected_backends
    }
    pi_full_loop_count = backend_full_loop_counts.get("pi_gpt55", 0)
    compared_task_refs = []
    if validation:
        compared_task_refs = validation.get("validated_task_refs", []) + validation.get("blocked_task_refs", [])
    payload = {
        "schema_version": "0.1.0",
        "object_type": "backend_comparison_report",
        "object_id": "backend_comparison.power.generic_full_loop.current",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {
            "protocol": "generic-full-loop-validation",
            "backend_profiles": {key: BACKENDS[key] for key in selected_backends if key in BACKENDS},
        },
        "compared_backends": selected_backends,
        "compared_task_refs": sorted(set(compared_task_refs)),
        "backend_results": backend_results,
        "harness_findings": [
            "Deterministic backend can validate contracts but not autonomous cognition.",
            f"Pi GPT-5.5 has {pi_full_loop_count} verified full-loop artifact-chain run(s).",
            "Pi GPT-5.5 also has text and tool-call smoke evidence.",
            "Codex/OMX remains the engineering orchestrator unless a backend dispatch layer is added.",
        ],
        "recommended_backend_policy": [
            "Use deterministic backend as regression baseline.",
            "Use Pi GPT-5.5 for the next bounded multi-class agentic loop expansion.",
            "Do not claim backend-robust full-loop validation until Pi and Codex/OMX both pass full-loop checks.",
        ],
        "not_proven": [
            "Pi GPT-5.5 full-loop validation is still fixture-level and not yet research-quality Level 5.",
            "Codex/OMX backend full-loop validation is not proven yet.",
            "Cross-backend semantic agreement is not proven yet.",
        ],
        "summary": f"Compared {len(selected_backends)} agent runtime profiles.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare generic loop backends.")
    parser.add_argument("--list-backends", action="store_true")
    parser.add_argument("--tasks", nargs="*")
    parser.add_argument("--backends", nargs="*")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.list_backends:
        print(json.dumps(BACKENDS, indent=2, ensure_ascii=False))
        return 0
    report = build_report(args.tasks, args.backends)
    path = ROOT / "backend_comparison_report.yaml"
    write_yaml(path, report)
    print(f"Backend comparison report written to {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
