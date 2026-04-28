#!/usr/bin/env python3
"""Build a lightweight experiment index for task002/task003/task004."""

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


def index_run(task_name: str, run_dir: Path) -> dict[str, Any]:
    run = load_yaml(run_dir / "run.yaml")
    return {
        "task": task_name,
        "stage": "run",
        "object_type": run["object_type"],
        "object_id": run["object_id"],
        "path": str((run_dir / "run.yaml").relative_to(REPO_ROOT)),
        "status": run.get("run_status", ""),
        "trigger_reason": run.get("trigger_reason", ""),
    }


def build_index() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for task_name in ["task002", "task003", "task004"]:
        runs_dir = REPO_ROOT / "runs" / task_name
        if runs_dir.exists():
            for run_dir in sorted(runs_dir.glob("run_*")):
                if (run_dir / "run.yaml").exists():
                    entries.append(index_run(task_name, run_dir))
        analysis_dir = REPO_ROOT / "analysis" / task_name
        if analysis_dir.exists():
            for path in sorted(analysis_dir.glob("*/*")):
                if path.is_file() and path.suffix == ".yaml":
                    payload = load_yaml(path)
                    object_type = payload.get("object_type")
                    object_id = payload.get("object_id")
                    status = payload.get("status")
                    if not isinstance(object_type, str) or not isinstance(object_id, str):
                        continue
                    entries.append(
                        {
                            "task": task_name,
                            "stage": path.parent.name.split("_")[0],
                            "object_type": object_type,
                            "object_id": object_id,
                            "path": str(path.relative_to(REPO_ROOT)),
                            "status": status if isinstance(status, str) else "",
                        }
                    )
    return {"generated_at": utc_now(), "entries": entries}


def render_markdown(index: dict[str, Any]) -> str:
    lines = ["# Experiment Index", "", f"- generated_at: {index['generated_at']}", "", "| task | stage | object_type | status | path |", "| --- | --- | --- | --- | --- |"]
    for entry in index["entries"]:
        lines.append(f"| {entry['task']} | {entry['stage']} | {entry['object_type']} | {entry['status']} | {entry['path']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DaoShuGuo experiment index.")
    parser.add_argument("--json-output", default="analysis/experiment_index.json")
    parser.add_argument("--md-output", default="analysis/experiment_index.md")
    args = parser.parse_args()
    index = build_index()
    json_path = REPO_ROOT / args.json_output
    md_path = REPO_ROOT / args.md_output
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(index), encoding="utf-8")
    print(f"Experiment index written to {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
