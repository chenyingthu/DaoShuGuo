#!/usr/bin/env python3
"""Run integration checks for the autonomous research slices."""

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
        ["python", "scripts/validate_schemas.py", "--artifacts", "task002-pipeline"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task003-pipeline"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task003-cognition-stage"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task003-literature-stage"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task004-pipeline"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task004-cognition-stage"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task004-literature-stage"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task005-pipeline"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "task005-cognition-stage"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "effectiveness-delivery-layer"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "skill-cognition-loop"],
        ["python", "scripts/validate_schemas.py", "--artifacts", "real-agentic-loop"],
        ["python", "-m", "py_compile", "orchestrator/main.py"],
        ["python", "scripts/run_preflight_checks.py"],
        ["python", "scripts/run_light_probe.py"],
        ["python", "scripts/build_experiment_index.py"],
        ["python", "scripts/update_diagnosis_memory.py"],
        ["python", "scripts/verify_effectiveness_layer.py"],
        ["python", "scripts/build_skill_cognition_loop.py"],
        ["python", "scripts/verify_skill_cognition_loop.py"],
        ["python", "scripts/build_llm_cognition_jobs.py"],
        ["python", "scripts/run_llm_cognition_job.py", "agents/cognition/jobs/task003_semantic_critic_001.json", "--dry-run", "--output-dir", "agents/cognition/dry_run_outputs"],
        ["python", "scripts/run_llm_cognition_job.py", "agents/cognition/jobs/task004_literature_reviewer_001.json", "--dry-run", "--output-dir", "agents/cognition/dry_run_outputs"],
        ["python", "scripts/run_llm_cognition_job.py", "agents/cognition/jobs/task005_result_interpreter_001.json", "--dry-run", "--output-dir", "agents/cognition/dry_run_outputs"],
        ["python", "scripts/run_llm_cognition_job.py", "agents/cognition/jobs/effectiveness_reviewer_001.json", "--dry-run", "--output-dir", "agents/cognition/dry_run_outputs"],
        ["python", "scripts/verify_llm_cognition_outputs.py", "--output-dir", "agents/cognition/dry_run_outputs"],
        ["python", "orchestrator/main.py", "verify-task001-pipeline"],
        ["python", "orchestrator/main.py", "verify-task002-pipeline"],
        ["python", "orchestrator/main.py", "verify-task002-analysis"],
        ["python", "orchestrator/main.py", "verify-task002-failure-path"],
        ["python", "orchestrator/main.py", "verify-task003-pipeline"],
        ["python", "orchestrator/main.py", "verify-task003-failure-path"],
        ["python", "orchestrator/main.py", "verify-task003-cognition-stage"],
        ["python", "orchestrator/main.py", "verify-task003-literature-stage"],
        ["python", "orchestrator/main.py", "verify-task004-pipeline"],
        ["python", "orchestrator/main.py", "verify-task004-failure-path"],
        ["python", "orchestrator/main.py", "verify-task004-boundary-overclaim"],
        ["python", "orchestrator/main.py", "verify-task004-task-mismatch"],
        ["python", "orchestrator/main.py", "verify-task004-cognition-stage"],
        ["python", "orchestrator/main.py", "verify-task004-literature-stage"],
        ["python", "orchestrator/main.py", "verify-task005-pipeline"],
        ["python", "orchestrator/main.py", "verify-task005-failure-path"],
        ["python", "orchestrator/main.py", "verify-task005-cognition-stage"],
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
    assert_exists(REPO_ROOT / "analysis/task002")
    assert_exists(REPO_ROOT / "analysis/preflight/preflight_report.json")
    assert_exists(REPO_ROOT / "analysis/preflight/light_probe.json")
    assert_exists(REPO_ROOT / "analysis/experiment_index.json")
    assert_exists(REPO_ROOT / "memory/diagnosis_memory.jsonl")
    assert_exists(REPO_ROOT / "analysis/loop/task003/writeback.json")
    assert_exists(REPO_ROOT / "analysis/loop/task004/writeback.json")
    assert_exists(REPO_ROOT / "analysis/loop/task005/writeback.json")
    assert_exists(REPO_ROOT / "agents/cognition/jobs/task003_semantic_critic_001.json")
    assert_exists(REPO_ROOT / "agents/cognition/outputs/task003_semantic_critic_001.json")

    upgraded_ref = load_yaml(high_upgrade)["upgraded_cognition_ref"]
    assert_exists(REPO_ROOT / "cognition/cards" / f"{upgraded_ref.split('.')[-1]}.yaml")

    task002_upgrade = find_yaml_by_fields(
        REPO_ROOT / "analysis/task002",
        "cognition_upgrade.yaml",
        {"task_ref": "task.power.ieee69_reactive_opt"},
    )
    task002_explanation = find_yaml_by_fields(
        REPO_ROOT / "analysis/task002",
        "explanation_alignment.yaml",
        {"task_ref": "task.power.ieee69_reactive_opt"},
    )
    task002_literature = find_yaml_by_fields(
        REPO_ROOT / "analysis/task002",
        "literature_alignment.yaml",
        {"task_ref": "task.power.ieee69_reactive_opt"},
    )
    task002_failure_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task002",
        "run.yaml",
        {"trigger_reason": "real_adversarial-failure", "run_status": "failed_experiment"},
    )
    task002_failure_cognition = task002_failure_run.parent / "cognition.yaml"
    task002_failure_taste = task002_failure_run.parent / "taste_assessment.yaml"
    task002_failure_report = task002_failure_run.parent / "report.yaml"
    task003_success_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task003",
        "run.yaml",
        {"trigger_reason": "real_inverter-support", "run_status": "completed"},
    )
    task003_failure_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task003",
        "run.yaml",
        {"trigger_reason": "real_weak-shunt-mismatch", "run_status": "failed_experiment"},
    )
    task003_performance_failure_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task003",
        "run.yaml",
        {"trigger_reason": "real_inverter-underperformer", "run_status": "failed_experiment"},
    )
    task003_success_cognition = task003_success_run.parent / "cognition.yaml"
    task003_failure_cognition = task003_failure_run.parent / "cognition.yaml"
    task003_failure_taste = task003_failure_run.parent / "taste_assessment.yaml"
    task003_failure_report = task003_failure_run.parent / "report.yaml"
    task003_perf_cognition = task003_performance_failure_run.parent / "cognition.yaml"
    task003_perf_taste = task003_performance_failure_run.parent / "taste_assessment.yaml"
    task003_perf_report = task003_performance_failure_run.parent / "report.yaml"
    task003_semantic = find_yaml_by_fields(
        REPO_ROOT / "analysis/task003",
        "strategy_semantic_comparison.yaml",
        {"task_ref": "task.power.ieee69_renewable_reactive_opt"},
    )
    task003_upgrade = find_yaml_by_fields(
        REPO_ROOT / "analysis/task003",
        "cognition_upgrade.yaml",
        {"task_ref": "task.power.ieee69_renewable_reactive_opt"},
    )
    task003_literature = find_yaml_by_fields(
        REPO_ROOT / "analysis/task003",
        "literature_alignment.yaml",
        {"task_ref": "task.power.ieee69_renewable_reactive_opt"},
    )
    task003_explanation = find_yaml_by_fields(
        REPO_ROOT / "analysis/task003",
        "explanation_alignment.yaml",
        {"task_ref": "task.power.ieee69_renewable_reactive_opt"},
    )
    task004_success_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task004",
        "run.yaml",
        {"trigger_reason": "real_inverter-support"},
    )
    task004_failure_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task004",
        "run.yaml",
        {"trigger_reason": "real_single-point-mismatch", "run_status": "failed_experiment"},
    )
    task004_success_cognition = task004_success_run.parent / "cognition.yaml"
    task004_failure_cognition = task004_failure_run.parent / "cognition.yaml"
    task004_failure_taste = task004_failure_run.parent / "taste_assessment.yaml"
    task004_overclaim = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "boundary_overclaim_check.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task004_semantic = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "strategy_semantic_comparison.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task004_upgrade = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "cognition_upgrade.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task004_mismatch = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "task_mismatch_check.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task004_literature = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "literature_alignment.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task004_explanation = find_yaml_by_fields(
        REPO_ROOT / "analysis/task004",
        "explanation_alignment.yaml",
        {"task_ref": "task.power.ieee69_hosting_capacity"},
    )
    task005_success_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task005",
        "run.yaml",
        {"trigger_reason": "real_renewable-restoration"},
    )
    task005_failure_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task005",
        "run.yaml",
        {"trigger_reason": "real_steady-state-mismatch", "run_status": "failed_experiment"},
    )
    task005_perf_run = find_yaml_by_fields(
        REPO_ROOT / "runs/task005",
        "run.yaml",
        {"trigger_reason": "real_renewable-underperformer", "run_status": "failed_experiment"},
    )
    task005_success_cognition = task005_success_run.parent / "cognition.yaml"
    task005_failure_cognition = task005_failure_run.parent / "cognition.yaml"
    task005_perf_cognition = task005_perf_run.parent / "cognition.yaml"
    task005_overclaim = find_yaml_by_fields(
        REPO_ROOT / "analysis/task005",
        "boundary_overclaim_check.yaml",
        {"task_ref": "task.power.ieee69_restoration_resilience"},
    )
    task005_mismatch = find_yaml_by_fields(
        REPO_ROOT / "analysis/task005",
        "task_mismatch_check.yaml",
        {"task_ref": "task.power.ieee69_restoration_resilience"},
    )
    task005_semantic = find_yaml_by_fields(
        REPO_ROOT / "analysis/task005",
        "strategy_semantic_comparison.yaml",
        {"task_ref": "task.power.ieee69_restoration_resilience"},
    )
    task005_upgrade = find_yaml_by_fields(
        REPO_ROOT / "analysis/task005",
        "cognition_upgrade.yaml",
        {"task_ref": "task.power.ieee69_restoration_resilience"},
    )
    checks.extend(
        [
            (task002_upgrade, "task_ref", "task.power.ieee69_reactive_opt"),
            (task002_literature, "task_ref", "task.power.ieee69_reactive_opt"),
            (task002_explanation, "task_ref", "task.power.ieee69_reactive_opt"),
            (task002_failure_cognition, "cognition_type", "failure"),
            (task002_failure_taste, "grade", "huimo"),
            (task002_failure_report, "report_type", "discussion_memo"),
            (task003_success_cognition, "cognition_type", "candidate"),
            (task003_failure_cognition, "cognition_type", "failure"),
            (task003_failure_taste, "grade", "huimo"),
            (task003_failure_report, "report_type", "discussion_memo"),
            (task003_perf_cognition, "cognition_type", "failure"),
            (task003_perf_taste, "grade", "huimo"),
            (task003_perf_report, "report_type", "discussion_memo"),
            (task003_semantic, "task_ref", "task.power.ieee69_renewable_reactive_opt"),
            (task003_upgrade, "task_ref", "task.power.ieee69_renewable_reactive_opt"),
            (task003_literature, "task_ref", "task.power.ieee69_renewable_reactive_opt"),
            (task003_explanation, "task_ref", "task.power.ieee69_renewable_reactive_opt"),
            (task004_success_cognition, "scope_boundary.task", "task.power.ieee69_hosting_capacity"),
            (task004_failure_cognition, "cognition_type", "failure"),
            (task004_failure_taste, "grade", "huimo"),
            (task004_overclaim, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task004_semantic, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task004_upgrade, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task004_mismatch, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task004_literature, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task004_explanation, "task_ref", "task.power.ieee69_hosting_capacity"),
            (task005_success_cognition, "scope_boundary.task", "task.power.ieee69_restoration_resilience"),
            (task005_failure_cognition, "cognition_type", "failure"),
            (task005_perf_cognition, "cognition_type", "failure"),
            (task005_overclaim, "task_ref", "task.power.ieee69_restoration_resilience"),
            (task005_mismatch, "task_ref", "task.power.ieee69_restoration_resilience"),
            (task005_semantic, "task_ref", "task.power.ieee69_restoration_resilience"),
            (task005_upgrade, "task_ref", "task.power.ieee69_restoration_resilience"),
        ]
    )

    for path, field, expected in checks:
        assert_field(path, field, expected)

    print("Integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
