#!/usr/bin/env python3
"""Verify the real agentic skill-cognition loop artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUESTS_DIR = REPO_ROOT / "agents" / "skill" / "requests"
RESULTS_DIR = REPO_ROOT / "agents" / "skill" / "results"
LOOP_DIR = REPO_ROOT / "analysis" / "agentic_loop" / "task003"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to object")
    return data


def verify() -> None:
    request_files = sorted(REQUESTS_DIR.glob("task003_iter*.yaml"))
    result_files = sorted(RESULTS_DIR.glob("task003_iter*.yaml"))
    update_files = sorted((LOOP_DIR / "updates").glob("iter*.yaml"))
    review_files = sorted((LOOP_DIR / "reviews").glob("iter*.yaml"))
    if len(request_files) < 2 or len(result_files) < 2 or len(update_files) < 2 or len(review_files) < 2:
        raise RuntimeError("real agentic loop must contain at least two iterations")

    previous_summary = None
    for idx, request_path in enumerate(request_files):
        iteration = idx + 1
        request = load_yaml(request_path)
        result = load_yaml(result_files[idx])
        update = load_yaml(update_files[idx])
        review = load_yaml(review_files[idx])

        output_path = REPO_ROOT / request["output_skill_path"]
        if not output_path.exists():
            raise RuntimeError(f"missing output skill path: {output_path}")
        if result["request_ref"] != request["object_id"]:
            raise RuntimeError(f"iteration {iteration}: result does not reference request")
        if review["skill_iteration_result_ref"] != result["object_id"]:
            raise RuntimeError(f"iteration {iteration}: review does not reference result")
        if review["cognition_update_ref"] != update["object_id"]:
            raise RuntimeError(f"iteration {iteration}: review does not reference update")
        if iteration > 1 and request.get("source_update_ref") != load_yaml(update_files[idx - 1])["object_id"]:
            raise RuntimeError(f"iteration {iteration}: request does not reference previous update")
        if previous_summary is not None and request["summary"] == previous_summary:
            raise RuntimeError(f"iteration {iteration}: request summary did not change from previous iteration")
        previous_summary = request["summary"]

        raw_output = REPO_ROOT / result["raw_output_path"]
        if not raw_output.exists():
            raise RuntimeError(f"iteration {iteration}: missing raw skill-agent output")
        if not update.get("source_workflow_output_refs"):
            raise RuntimeError(f"iteration {iteration}: missing workflow output refs")
        for ref in update["source_workflow_output_refs"]:
            if not (REPO_ROOT / ref).exists():
                raise RuntimeError(f"iteration {iteration}: missing workflow output {ref}")
        if review["verdict"] not in {"real_progress", "stagnation", "cheating_suspected"}:
            raise RuntimeError(f"iteration {iteration}: invalid review verdict")

    report = load_json(LOOP_DIR / "capability_boundary_report.json")
    if report.get("iterations_observed", 0) < 2:
        raise RuntimeError("capability report must observe at least two iterations")


def main() -> int:
    verify()
    print("Real agentic loop verification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Real agentic loop verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
