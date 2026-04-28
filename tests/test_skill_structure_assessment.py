from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "run_skill_structure_assessment.py"
ROOT = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02"


def load_assessment_module():
    spec = importlib.util.spec_from_file_location("run_skill_structure_assessment", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_skill_use_only_diagnosis_blocks_structural_claim():
    subprocess.run(
        [sys.executable, "scripts/run_skill_structure_assessment.py", "--task", "task003", "--iteration", "2"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assessment = load_yaml(ROOT / "skill_structure_assessment.yaml")

    assert assessment["structural_verdict"] == "structural_attempt_ready"
    assert assessment["improvement_class"] == "mixed_structural"
    assert assessment["skill_use_score"] >= assessment["method_score"]
    assert "verified structural skill improvement" in assessment["blocked_claims"]
    assert any("fixed-budget ablation" in item for item in assessment["required_next_evidence"])


def test_overclaim_is_rejected_without_validated_evidence():
    module = load_assessment_module()
    verdict, improvement_class, blocked_claims, required_next_evidence = module.decide_verdict(
        method_score=1,
        process_score=1,
        standard_score=1,
        skill_use_score=1,
        diagnosis={"diagnosis_class": "verified_structural_improvement"},
    )

    assert verdict == "rejected_overclaim"
    assert improvement_class == "none"
    assert "verified structural skill improvement" in blocked_claims
    assert required_next_evidence
