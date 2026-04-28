from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "run_research_review_gate.py"


def load_gate_module():
    spec = importlib.util.spec_from_file_location("run_research_review_gate", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def base_inputs() -> dict:
    return {
        "metrics": {
            "baseline_solution": {
                "metrics": {
                    "loss": 10.0,
                    "voltage_deviation": 0.02,
                    "constraint_violation": 2,
                }
            },
            "candidate_solution": {
                "metrics": {
                    "loss": 8.0,
                    "voltage_deviation": 0.01,
                    "constraint_violation": 1,
                }
            },
        },
        "skill_result": {"raw_output_path": "agents/skill/results/task003_iter02.raw.txt"},
        "loop_review": {"verdict": "real_progress", "cheating_signals": []},
        "cognition_update": {"required_discriminating_tests": ["ablation needed"]},
    }


def test_gate_routes_metric_failure_to_skill_repair():
    gate = load_gate_module()
    inputs = base_inputs()
    inputs["metrics"]["candidate_solution"]["metrics"]["loss"] = 12.0

    decision = gate.decide_review(inputs)

    assert decision["verdict"] == "needs_fix"
    assert decision["approval_allowed"] is False
    assert "repair_skill" in decision["required_repairs"]


def test_gate_blocks_missing_cognition_tests_as_insufficient_evidence():
    gate = load_gate_module()
    inputs = copy.deepcopy(base_inputs())
    inputs["cognition_update"]["required_discriminating_tests"] = []

    decision = gate.decide_review(inputs)

    assert decision["verdict"] == "insufficient_evidence"
    assert decision["approval_allowed"] is False
    assert "repair_cognition_prompt" in decision["required_repairs"]


def test_gate_preserves_skill_use_boundary_for_metric_improvement():
    gate = load_gate_module()
    decision = gate.decide_review(base_inputs())

    boundary_text = " ".join(decision["claim_boundary"])

    assert "skill-use improvement" in boundary_text
    assert "skill-structure improvement" in boundary_text
    assert "search-envelope expansion" in boundary_text
