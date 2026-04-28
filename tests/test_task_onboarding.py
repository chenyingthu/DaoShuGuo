from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "run_task_onboarding_check.py"


def load_onboarding_module():
    spec = importlib.util.spec_from_file_location("run_task_onboarding_check", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def run_onboarding(task_id: str) -> dict:
    subprocess.run(
        [sys.executable, "scripts/run_task_onboarding_check.py", "--task", task_id],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return load_yaml(REPO_ROOT / "analysis" / "onboarding" / task_id / "task_readiness_report.yaml")


def test_existing_tasks_use_same_onboarding_cli():
    expected = {
        "task003": ("ready_to_run", "run_research_pipeline"),
        "task004": ("ready_to_run", "run_research_pipeline"),
        "task005": ("ready_for_framing_only", "framing_only"),
    }

    for task_id, (status, route) in expected.items():
        report = run_onboarding(task_id)
        assert report["readiness_status"] == status
        assert report["recommended_route"] == route
        assert report["adapter_ref"].startswith("task_adapter.")


def test_task007_fixture_is_blocked_without_crashing():
    report = run_onboarding("task007_fixture")

    assert report["readiness_status"] == "blocked_missing_runtime"
    assert report["recommended_route"] == "repair_adapter"
    assert "evaluators/task007_fixture_evaluator.py" in report["missing_items"]


def test_missing_metrics_mapping_is_reported_explicitly():
    onboarding = load_onboarding_module()
    adapter = load_yaml(REPO_ROOT / "adapters" / "task003.yaml")
    adapter = copy.deepcopy(adapter)
    adapter["metrics_mapping"] = {}
    missing: list[str] = []
    available: list[str] = []

    onboarding.collect_task_contract(adapter, missing, available)
    status = onboarding.determine_status(adapter, missing, available)

    assert status == "blocked_missing_metrics_mapping"
    assert "adapter.metrics_mapping.primary" in missing


def test_missing_skill_binding_uses_registry_aware_resolution():
    onboarding = load_onboarding_module()
    adapter = load_yaml(REPO_ROOT / "adapters" / "task003.yaml")
    adapter = copy.deepcopy(adapter)
    adapter["candidate_skill_refs"] = ["skill.power.does_not_exist"]
    adapter["fallback_skill_refs"] = []
    missing: list[str] = []
    available: list[str] = []

    onboarding.collect_task_contract(adapter, missing, available)
    status = onboarding.determine_status(adapter, missing, available)

    assert status == "blocked_missing_skill"
    assert "skill_ref:skill.power.does_not_exist" in missing
