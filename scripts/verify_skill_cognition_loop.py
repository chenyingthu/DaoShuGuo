#!/usr/bin/env python3
"""Verify the generated skill-cognition loop artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOOP_ROOT = REPO_ROOT / "analysis" / "loop"
TASKS = ["task003", "task004", "task005"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def latest_yaml(path: Path) -> Path:
    files = sorted(path.glob("*.yaml"))
    if not files:
        raise RuntimeError(f"no yaml files in {path}")
    return files[-1]


def verify_task(task_name: str) -> None:
    root = LOOP_ROOT / task_name
    event = load_yaml(latest_yaml(root / "events"))
    update = load_yaml(latest_yaml(root / "updates"))
    plan = load_yaml(latest_yaml(root / "plans"))
    review = load_yaml(latest_yaml(root / "reviews"))

    if update.get("source_event_ref") != event.get("object_id"):
        raise RuntimeError(f"{task_name} update does not point to event")
    if plan.get("controller_update_ref") != update.get("object_id"):
        raise RuntimeError(f"{task_name} plan does not point to update")
    if review.get("event_ref") != event.get("object_id"):
        raise RuntimeError(f"{task_name} review does not point to event")
    if review.get("controller_update_ref") != update.get("object_id"):
        raise RuntimeError(f"{task_name} review does not point to update")
    if review.get("iteration_plan_ref") != plan.get("object_id"):
        raise RuntimeError(f"{task_name} review does not point to plan")

    if not event.get("source_refs"):
        raise RuntimeError(f"{task_name} event missing source_refs")
    if not update.get("next_iteration_skill_constraints"):
        raise RuntimeError(f"{task_name} update missing skill constraints")
    if not update.get("required_discriminating_tests"):
        raise RuntimeError(f"{task_name} update missing discriminating tests")
    if not plan.get("planned_actions") or not plan.get("planned_validation"):
        raise RuntimeError(f"{task_name} plan missing actions or validation")
    if review.get("verdict") not in {"substantiated", "partial", "not_substantiated"}:
        raise RuntimeError(f"{task_name} review has invalid verdict")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify skill-cognition loop artifacts.")
    parser.add_argument("--tasks", nargs="*", choices=TASKS, default=TASKS)
    args = parser.parse_args()

    for task_name in args.tasks:
        verify_task(task_name)
    print("Skill-cognition loop verification passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Skill-cognition loop verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
