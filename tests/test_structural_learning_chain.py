from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02"


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_structural_learning_chain_preserves_skill_use_boundary():
    subprocess.run(
        [sys.executable, "scripts/build_structural_learning_chain.py", "--task", "task003", "--iteration", "2"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    diagnosis = load_yaml(ROOT / "skill_structure_diagnosis.yaml")
    request = load_yaml(ROOT / "structural_skill_change_request.yaml")

    assert diagnosis["diagnosis_class"] == "skill_use_improvement_only"
    assert "not verified skill-structure improvement" in diagnosis["skill_use_vs_structure_judgment"]
    assert request["change_type"] == "mixed_structural_change"
    assert request["method_changes"]
    assert request["process_changes"]
    assert request["standard_changes"]
    assert any("Q grid" in item for item in request["forbidden_usage_only_shortcuts"])
