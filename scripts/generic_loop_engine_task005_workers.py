#!/usr/bin/env python3
"""Task005 workers for the generic loop engine smoke adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def _task005_state(task_adapter: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    experimental = task_adapter.get("experimental", {})
    run_root = REPO_ROOT / experimental["run_root"]
    run_record = load_yaml(run_root / "run.yaml")
    metrics = load_json(run_root / "metrics.json")
    cognition = load_yaml(REPO_ROOT / experimental["cognition_ref"])
    return run_record, metrics, cognition


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    previous_skill_ref = task_adapter.get("experimental", {}).get(
        "previous_skill_ref", "skill.power.renewable_underperformer_task005"
    )
    return {
        "metadata": {"task_package": "task005", "worker": "skill_worker"},
        "fields": {
            "base_skill_ref": previous_skill_ref,
            "allowed_change_scope": ["renewable_restoration_policy", "critical_load_priority"],
            "blocked_paths": ["steady_state_operation_proxy", "evaluator_logic"],
            "required_tests": [
                "Run candidate and baseline under the same fault context.",
                "Compare restored_load_ratio, unserved_critical_load, and restoration_action_cost_proxy.",
            ],
            "output_skill_path": "skills/active_dev/renewable_underperformer_task005.py",
            "summary": "Use the archived task005 performance-failure candidate as a smoke-path skill variant.",
        },
    }


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    run_record, _, _ = _task005_state(task_adapter)
    produced_skill = run_record["skill_refs"]["produced"][0]["object_id"]
    return {
        "metadata": {"task_package": "task005", "worker": "skill_worker"},
        "fields": {
            "produced_skill_ref": produced_skill,
            "code_paths": ["skills/active_dev/renewable_underperformer_task005.py"],
            "change_summary": [
                "Materialized archived renewable-underperformer restoration candidate for adapter smoke validation.",
            ],
            "expected_behavior_change": [
                "The candidate should preserve restoration semantics while exposing a performance-failure case.",
            ],
            "command": "archived:python orchestrator/main.py real-run-task005 --strategy renewable-underperformer",
            "raw_output_path": task_adapter["experimental"]["run_root"] + "/run.yaml",
            "self_reported_risks": [
                "This adapter smoke uses an archived run; it validates framework transfer rather than new performance.",
            ],
            "run_ref": run_record["object_id"],
        },
    }


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    run_record, metrics, _ = _task005_state(task_adapter)
    comparison = metrics["evaluation"]["comparisons"]
    candidate = metrics["candidate_solution"]["metrics"]
    baseline = metrics["baseline_solution"]["metrics"]
    return {
        "metadata": {"task_package": "task005", "worker": "effectiveness_worker"},
        "fields": {
            "baseline_ref": task_adapter["baseline_binding"]["baseline_refs"][0],
            "evaluator_ref": task_adapter["evaluator_binding"]["evaluator_ref"],
            "run_ref": run_record["object_id"],
            "run_passed": bool(metrics["evaluation"]["passed"]),
            "metric_summary": {
                "candidate_restored_load_ratio": candidate["restored_load_ratio"],
                "baseline_restored_load_ratio": baseline["restored_load_ratio"],
                "candidate_unserved_critical_load": candidate["unserved_critical_load"],
                "baseline_unserved_critical_load": baseline["unserved_critical_load"],
                "candidate_action_cost_proxy": candidate["restoration_action_cost_proxy"],
                "baseline_action_cost_proxy": baseline["restoration_action_cost_proxy"],
                "restored_load_delta": comparison["restored_load_ratio"]["delta"],
            },
            "comparison_summary": metrics["evaluation"]["summary"],
            "judgment_summary": run_record["failure_summary"],
            "recommended_cognition_action": (
                "Classify whether this is semantic mismatch, skill-use failure, or structure-level restoration weakness."
            ),
        },
    }


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    task_adapter = inputs["task_adapter"]
    _, metrics, cognition = _task005_state(task_adapter)
    candidate = metrics["candidate_solution"]["metrics"]
    baseline = metrics["baseline_solution"]["metrics"]
    same_recovery = candidate["restored_load_ratio"] == baseline["restored_load_ratio"]
    higher_cost = candidate["restoration_action_cost_proxy"] > baseline["restoration_action_cost_proxy"]
    if same_recovery and higher_cost:
        problem_class = "skill_structure_problem"
        recommended_action = "redesign_skill_structure"
        judgment_summary = (
            "task005 candidate keeps restoration semantics, but equal restored load with higher action cost "
            "indicates a structure-level weakness in the restoration skill."
        )
        next_constraints = [
            "Do not treat renewable action insertion as improvement unless restored_load_ratio or critical-load service improves.",
            "Preserve event-driven restoration semantics when redesigning the skill.",
        ]
        priorities = [
            "Introduce fault-topology-sensitive switching or critical-load priority logic before more renewable support actions.",
        ]
    else:
        problem_class = "skill_use_problem"
        recommended_action = "continue_skill_evolution"
        judgment_summary = "task005 smoke path supports another bounded skill-use iteration under the same evaluator."
        next_constraints = ["Keep the same fault context and evaluator while testing the next restoration candidate."]
        priorities = ["Compare the next candidate against the same conservative baseline."]

    return {
        "metadata": {"task_package": "task005", "worker": "cognition_worker"},
        "fields": {
            "problem_class": problem_class,
            "judgment_summary": judgment_summary,
            "boundary_notes": [
                "This diagnosis is limited to the archived single-fault task005 run.",
                cognition["scope_boundary"]["mode"],
            ],
            "uncertainty_notes": [
                "No multi-fault or time-series restoration evidence is included in this smoke adapter.",
            ],
            "recommended_next_worker": "skill_worker",
            "recommended_action": recommended_action,
            "continue_loop": True,
        },
        "cognition_to_skill_update": {
            "metadata": {"task_package": "task005", "loop_source": "generic_loop_engine_task005"},
            "fields": {
                "next_iteration_skill_constraints": next_constraints,
                "next_iteration_evaluator_constraints": [
                    "Keep restored_load_ratio and unserved_critical_load as primary restoration metrics.",
                    "Treat higher action cost without restoration gain as a negative signal.",
                ],
                "next_iteration_task_refinements": [
                    "Keep the current single-fault context for smoke-path comparability.",
                ],
                "search_priority_updates": priorities,
                "required_discriminating_tests": [
                    "Compare the redesigned restoration skill against both conservative baseline and underperformer candidate.",
                ],
                "summary": "task005 adapter smoke routes semantic performance failure toward structure-level skill redesign.",
            },
        },
    }
