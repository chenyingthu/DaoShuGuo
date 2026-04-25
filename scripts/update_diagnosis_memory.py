#!/usr/bin/env python3
"""Build/update a lightweight diagnosis memory from existing failure artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def collect_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted((REPO_ROOT / "cognition" / "failed").glob("*.yaml")):
        payload = load_yaml(path)
        entries.append(
            {
                "timestamp": utc_now(),
                "task_ref": payload.get("scope_boundary", {}).get("task", ""),
                "failure_type": payload.get("metadata", {}).get("mismatch_type", payload.get("cognition_type", "")),
                "summary": payload.get("statement", ""),
                "evidence_ref": (payload.get("evidence_refs") or [""])[0],
                "recommended_action": payload.get("promotion_status", "review"),
                "source_path": str(path.relative_to(REPO_ROOT)),
            }
        )
    for path in sorted((REPO_ROOT / "analysis").glob("task*/boundary_overclaim_*/boundary_overclaim_check.yaml")):
        payload = load_yaml(path)
        entries.append(
            {
                "timestamp": utc_now(),
                "task_ref": payload.get("task_ref", ""),
                "failure_type": "boundary_overclaim",
                "summary": payload.get("rationale", ""),
                "evidence_ref": payload.get("run_ref", ""),
                "recommended_action": payload.get("decision", "review"),
                "source_path": str(path.relative_to(REPO_ROOT)),
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Update diagnosis memory from failure cognitions.")
    parser.add_argument("--output", default="memory/diagnosis_memory.jsonl")
    args = parser.parse_args()
    output = REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = collect_entries()
    with output.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Diagnosis memory written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
