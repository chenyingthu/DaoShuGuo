#!/usr/bin/env python3
"""Run integration checks for the task001 autonomous research slice."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(args: list[str]) -> None:
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed: {' '.join(args)}")
    if result.stdout.strip():
        print(result.stdout.strip())


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def assert_field(path: Path, field: str, expected: Any) -> None:
    data = load_yaml(path)
    actual = data
    for part in field.split("."):
        if not isinstance(actual, dict) or part not in actual:
            raise AssertionError(f"{path}: missing field {field}")
        actual = actual[part]
    if actual != expected:
        raise AssertionError(f"{path}: expected {field}={expected!r}, got {actual!r}")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing expected path: {path}")


def main() -> int:
    commands = [
        ["python", "scripts/validate_schemas.py"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "literature-alignment-plan"],
        ["python", "-m", "py_compile", "orchestrator/main.py"],
        ["python", "orchestrator/main.py", "verify-task001-pipeline"],
    ]
    for command in commands:
        run_command(command)

    checks = [
        (
            REPO_ROOT / "analysis/task001/upgrade_0017/cognition_upgrade.yaml",
            "decision",
            "retain",
        ),
        (
            REPO_ROOT / "analysis/task001/upgrade_0017/cognition_upgrade.yaml",
            "evidence_strength",
            "medium",
        ),
        (
            REPO_ROOT / "analysis/task001/upgrade_0018/cognition_upgrade.yaml",
            "decision",
            "upgrade",
        ),
        (
            REPO_ROOT / "analysis/task001/upgrade_0018/cognition_upgrade.yaml",
            "evidence_strength",
            "high",
        ),
        (
            REPO_ROOT / "analysis/task001/upgrade_0018/novelty_assessment.yaml",
            "continue_investment",
            "prioritize",
        ),
    ]
    for path, field, expected in checks:
        assert_field(path, field, expected)

    required_paths = [
        "literature/sources/capacitor_tlbo_2014.fulltext.yaml",
        "literature/excerpts/capacitor_tlbo_2014-explanation-point-1.yaml",
        "analysis/task001/explanations_0014/explanation_alignment.yaml",
        "analysis/task001/upgrade_0018/upgraded_cognition.yaml",
        "cognition/cards/upgraded_strategy_comparison_0018.yaml",
    ]
    for rel_path in required_paths:
        assert_exists(REPO_ROOT / rel_path)

    print("Integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
