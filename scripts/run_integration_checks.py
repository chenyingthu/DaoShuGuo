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


def find_yaml_by_fields(root: Path, filename: str, expected_fields: dict[str, Any]) -> Path:
    matches: list[Path] = []
    for path in sorted(root.glob(f"**/{filename}")):
        data = load_yaml(path)
        if all(_read_field(data, field) == expected for field, expected in expected_fields.items()):
            matches.append(path)
    if not matches:
        raise AssertionError(f"no {filename} under {root} matched {expected_fields}")
    return matches[-1]


def _read_field(data: dict[str, Any], field: str) -> Any:
    current: Any = data
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def main() -> int:
    commands = [
        ["python", "scripts/validate_schemas.py"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "literature-alignment-plan"],
        ["python", "-m", "py_compile", "orchestrator/main.py"],
        ["python", "orchestrator/main.py", "verify-task001-pipeline"],
    ]
    for command in commands:
        run_command(command)

    upgrade_root = REPO_ROOT / "analysis/task001"
    medium_upgrade = find_yaml_by_fields(
        upgrade_root,
        "cognition_upgrade.yaml",
        {"decision": "retain", "evidence_strength": "medium"},
    )
    high_upgrade = find_yaml_by_fields(
        upgrade_root,
        "cognition_upgrade.yaml",
        {"decision": "upgrade", "evidence_strength": "high"},
    )
    high_novelty = high_upgrade.parent / "novelty_assessment.yaml"
    checks = [
        (medium_upgrade, "decision", "retain"),
        (medium_upgrade, "evidence_strength", "medium"),
        (high_upgrade, "decision", "upgrade"),
        (high_upgrade, "evidence_strength", "high"),
        (high_novelty, "continue_investment", "prioritize"),
    ]
    for path, field, expected in checks:
        assert_field(path, field, expected)

    assert_exists(REPO_ROOT / "literature/sources/capacitor_tlbo_2014.fulltext.yaml")
    assert_exists(REPO_ROOT / "literature/excerpts/capacitor_tlbo_2014-explanation-point-1.yaml")
    assert_exists(high_upgrade.parent / "upgraded_cognition.yaml")

    upgraded_ref = load_yaml(high_upgrade)["upgraded_cognition_ref"]
    assert_exists(REPO_ROOT / "cognition/cards" / f"{upgraded_ref.split('.')[-1]}.yaml")

    print("Integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
