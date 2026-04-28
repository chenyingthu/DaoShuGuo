#!/usr/bin/env python3
"""Verify LLM cognition job outputs and guardrails."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "agents" / "cognition" / "outputs"
REVIEW_DIR = REPO_ROOT / "agents" / "cognition" / "reviews"
REQUIRED = {
    "job_id",
    "agent_role",
    "input_refs",
    "interpretation_summary",
    "evidence_used",
    "agreement_with_rule_baseline",
    "new_insights",
    "overclaim_warnings",
    "missing_evidence",
    "recommended_action",
    "confidence",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to object")
    return data


def verify_output(path: Path) -> None:
    payload = load_json(path)
    if "interpretation_summary" not in payload and "strongest_supported_claim" in payload:
        payload = {
            **payload,
            "interpretation_summary": payload.get("strongest_supported_claim", ""),
            "missing_evidence": payload.get("discriminating_missing_evidence", []),
        }
    missing = REQUIRED - set(payload)
    if missing:
        raise RuntimeError(f"{path} missing fields: {sorted(missing)}")
    input_refs = set(payload.get("input_refs") or [])
    evidence_values = []
    for item in payload.get("evidence_used") or []:
        if isinstance(item, str):
            evidence_values.append(item)
        elif isinstance(item, dict) and isinstance(item.get("ref"), str):
            evidence_values.append(item["ref"])
        else:
            raise RuntimeError(f"{path} evidence_used entries must be strings or objects with ref")
    evidence_used = set(evidence_values)
    unknown = sorted(evidence_used - input_refs)
    if unknown:
        raise RuntimeError(f"{path} evidence_used contains refs outside input_refs: {unknown}")
    confidence = payload.get("confidence")
    if isinstance(confidence, dict):
        confidence = confidence.get("level")
    if confidence not in {"low", "medium", "high"}:
        raise RuntimeError(f"{path} invalid confidence")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify LLM cognition outputs.")
    parser.add_argument("--output-dir", default="agents/cognition/outputs")
    args = parser.parse_args()
    output_dir = REPO_ROOT / args.output_dir
    files = sorted(output_dir.glob("*.json"))
    if not files:
        raise RuntimeError("no LLM cognition outputs found")
    for path in files:
        verify_output(path)
    review_files = sorted(REVIEW_DIR.glob("*.yaml"))
    if not review_files:
        raise RuntimeError("no LLM cognition reviews found")
    print("LLM cognition output verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
