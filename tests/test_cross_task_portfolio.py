from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = REPO_ROOT / "analysis" / "portfolio" / "skill_structure_portfolio_20260425.yaml"


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_portfolio_routes_tasks_instead_of_continuing_all_topics():
    subprocess.run(
        [sys.executable, "scripts/run_cross_task_portfolio_assessment.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    portfolio = load_yaml(PORTFOLIO)
    by_task = {item["task_ref"]: item for item in portfolio["task_assessments"]}

    assert by_task["task.power.ieee69_renewable_reactive_opt"]["recommendation"] == "continue_with_fixed_budget_ablation"
    assert "pause_parameter_tuning" in by_task["task.power.ieee69_hosting_capacity"]["recommendation"]
    assert "standard_or_evaluator" in by_task["task.power.ieee69_restoration_resilience"]["recommendation"]
    assert any("Stop task004 q_step-only escalation" in item for item in portfolio["stop_or_pause_recommendations"])
