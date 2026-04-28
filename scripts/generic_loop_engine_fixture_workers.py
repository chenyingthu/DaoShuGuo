#!/usr/bin/env python3
"""Fixture workers for generic loop engine verification.

The normal worker contract is ``{"metadata": ..., "fields": ...}`` because the
loop engine persists canonical chain objects itself.  When the validation
harness is enabled it validates the worker return value before persistence, so
these fixtures also expose research-record fields at top level.  That keeps the
engine contract intact while giving the harness real quality content to check.
"""

from __future__ import annotations

from typing import Any


def _harness_enabled(inputs: dict[str, Any]) -> bool:
    return "_harness_phase_config" in inputs or "_harness_requirements" in inputs


def _with_harness_record(base: dict[str, Any], record: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    if not _harness_enabled(inputs):
        return base
    enriched = dict(base)
    enriched.update(record)
    return enriched


def _common_failure_capsule() -> dict[str, Any]:
    return {
        "known_limitations": [
            {
                "limitation": "The fixture uses a deterministic task package and does not prove behavior on full IEEE feeders.",
                "impact": "Evidence is suitable for harness regression but not for external performance claims.",
                "severity": "medium",
            }
        ],
        "local_failures": [
            {
                "failure": "No runtime evaluator execution is bundled with this fixture phase.",
                "mitigation": "Keep claims limited to schema, evidence, and record-quality validation.",
            }
        ],
        "generalizability_gaps": [
            "Only task007_fixture is exercised in this deterministic E2E lane.",
        ],
    }


def _common_next_actions() -> dict[str, Any]:
    return {
        "immediate": [
            {
                "action": "Run the same deterministic fixture through the no-harness baseline and compare quality metrics.",
                "rationale": "A/B comparison is required to show the harness adds measurable record quality.",
            }
        ],
        "short_term": [
            {
                "action": "Add a second task adapter after the fixture lane is stable.",
                "rationale": "A second task separates framework behavior from fixture-specific compatibility.",
            }
        ],
    }


def _skill_execution_record() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "execution_record",
        "phase": "skill_execution",
        "sequence": 2,
        "task_ref": "task.power.task007_fixture",
        "skill_ref": "skill.power.fixture_loop_candidate",
        "execution": {
            "status": "completed",
            "timestamp": "2026-04-28T00:00:00Z",
            "duration_seconds": 1.0,
            "exit_code": 0,
            "inputs": {
                "grid_model": "task007_fixture",
                "base_load_mw": 1.0,
                "compensation_nodes": [7],
                "compensation_mvar_per_node": 0.1,
                "simulator": "deterministic_fixture",
                "simulator_version": "0.1.0",
            },
            "outputs": {
                "raw_result_path": "analysis/generic_loop_engine_fixture/candidates/fixture_candidate.yaml",
                "metrics_path": "analysis/generic_loop_engine_fixture/candidates/fixture_metrics.yaml",
                "artifacts_dir": "analysis/generic_loop_engine_fixture/candidates",
            },
        },
        "skill_implementation": {
            "metadata": {
                "skill_name": "fixture_loop_candidate",
                "skill_version": "0.1.0",
                "skill_family": "deterministic_fixture",
                "author": "generic_loop_engine_fixture_workers",
                "created_at": "2026-04-28T00:00:00Z",
            },
            "code": {
                "main_file": "scripts/generic_loop_engine_fixture_workers.py",
                "structure": [
                    {
                        "function": "skill_execution_worker",
                        "purpose": "Return a deterministic candidate execution record for harness E2E validation.",
                        "algorithm": "Deterministic Fixture Candidate",
                        "complexity": "O(1)",
                    }
                ],
            },
            "design_decisions": [
                {
                    "decision": "Use a deterministic fixture worker instead of an LLM worker.",
                    "context": "E2E regression must be stable and fast while still exercising real engine persistence.",
                    "alternatives_considered": ["Call a live agent backend", "Mock the validation agent"],
                    "trade_offs": ["Determinism improves regression value but limits external research claims."],
                }
            ],
        },
        "results": {
            "primary_metrics": {
                "candidate_score": {"value": 0.4, "unit": "score", "context": "fixture candidate score"},
                "baseline_score": {"value": 0.3, "unit": "score", "context": "fixture baseline score"},
            }
        },
        "failure_capsule": _common_failure_capsule(),
        "next_actions": _common_next_actions(),
    }


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    base = {
        "metadata": {"task_package": "fixture_loop", "worker": "skill_worker"},
        "fields": {
            "base_skill_ref": "skill.power.fixture_loop_base",
            "allowed_change_scope": ["candidate_weight"],
            "blocked_paths": ["evaluator_logic"],
            "required_tests": [
                "Run the same fixture candidate against the fixture evaluator.",
                "Preserve the fixed candidate search envelope.",
            ],
            "output_skill_path": "analysis/generic_loop_engine_fixture/candidates/fixture_candidate.yaml",
            "summary": "Create a bounded fixture candidate inside the declared search envelope.",
        },
    }
    record = {
        "schema_version": "0.1.0",
        "object_type": "work_brief",
        "phase": "skill_change_request",
        "sequence": 1,
        "hypothesis": {
            "statement": "A bounded deterministic fixture candidate can expose whether the harness enforces record completeness before persistence.",
            "rationale": "The fixture preserves the real loop-engine phase order while keeping task behavior stable enough for repeatable quality comparison.",
            "testable_prediction": "Harness-enabled records will reach >= 80 quality score and 100% required-field coverage.",
        },
        "method": {
            "name": "HarnessFixtureABMethod",
            "description": "HarnessFixtureABMethod runs the same task007_fixture worker chain with and without validation, then compares required-field coverage, shallow-field counts, and average quality score.",
            "algorithm": {
                "type": "HarnessFixtureABMethod",
                "steps": [
                    "Run the baseline engine without validation.",
                    "Run the harness engine with validation requirements injected into worker inputs.",
                    "Validate both output sets with the same quality scorer.",
                ],
            },
            "code_location": "tests/e2e_utils.py",
            "baseline_comparison": "The baseline uses the same fixture worker without harness requirement injection.",
        },
    }
    return _with_harness_record(base, record, inputs)


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    base = {
        "metadata": {"task_package": "fixture_loop", "worker": "skill_worker"},
        "fields": {
            "produced_skill_ref": "skill.power.fixture_loop_candidate",
            "code_paths": ["skills/active_dev/fixture_loop_candidate.py"],
            "change_summary": ["Wrote a bounded fixture candidate artifact."],
            "expected_behavior_change": ["The candidate remains inside the declared search envelope."],
            "command": "fixture.skill_execution",
            "raw_output_path": "analysis/generic_loop_engine_fixture/candidates/fixture_candidate.yaml",
            "self_reported_risks": ["This is a fixture worker output for Phase 3 verification only."],
            "run_ref": "run.power.fixture_loop.verify_0001",
        },
    }
    return _with_harness_record(base, _skill_execution_record(), inputs)


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    base = {
        "metadata": {"task_package": "fixture_loop", "worker": "effectiveness_worker"},
        "fields": {
            "baseline_ref": "baseline.power.fixture_loop.default",
            "evaluator_ref": "evaluator.power.fixture_loop.default",
            "run_ref": "run.power.fixture_loop.verify_0001",
            "run_passed": False,
            "metric_summary": {
                "candidate_score": 0.4,
                "baseline_score": 0.3,
            },
            "comparison_summary": "The candidate changed behavior but did not yet justify a stronger claim.",
            "judgment_summary": "Bounded candidate established without strong effectiveness evidence.",
            "recommended_cognition_action": "Check whether the issue is still in skill use or requires structure changes.",
        },
    }
    record = {
        "schema_version": "0.1.0",
        "object_type": "assessment_packet",
        "phase": "effectiveness_assessment",
        "sequence": 3,
        "task_ref": "task.power.task007_fixture",
        "run_ref": "run.power.fixture_loop.verify_0001",
        "interpretation": {
            "summary": "The fixture candidate records a controlled score improvement from 0.30 to 0.40, but that evidence only supports harness and record-quality validation.",
            "supports_hypothesis": "partially",
            "support_evidence": [
                "candidate_score=0.40 is greater than baseline_score=0.30 under the fixture evaluator.",
                "The same deterministic worker can be run with and without harness injection for quality comparison.",
            ],
            "contradicts_hypothesis": [
                "No full runtime evaluator or external feeder benchmark is executed in this fixture lane."
            ],
            "data_quality_assessment": {
                "completeness": "partial",
                "reliability": "medium",
                "limitations": "Stable deterministic records are useful for regression but not for research-effectiveness claims.",
            },
        },
        "failure_capsule": _common_failure_capsule(),
        "next_actions": _common_next_actions(),
        "review_checklist": {
            "hypothesis_clear": True,
            "method_reproducible": True,
            "data_available": True,
            "results_quantified": True,
            "limitations_acknowledged": True,
            "next_actions_concrete": True,
            "reviewer_notes": [
                "Claims are intentionally limited to harness behavior and record quality."
            ],
        },
        "effectiveness_rating": {
            "level": "proof_of_concept",
            "readiness_percent": 65,
            "gaps_to_next_level": [
                "Run against a non-fixture task adapter.",
                "Bind to a real evaluator runtime instead of fixture scores.",
            ],
        },
    }
    return _with_harness_record(base, record, inputs)


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    base = {
        "metadata": {"task_package": "fixture_loop", "worker": "cognition_worker"},
        "fields": {
            "problem_class": "skill_use_problem",
            "judgment_summary": "The fixture result supports another bounded skill iteration before broader expansion.",
            "boundary_notes": ["The result is still limited to the fixture search envelope."],
            "uncertainty_notes": ["No second candidate has been compared yet."],
            "recommended_next_worker": "skill_worker",
            "recommended_action": "continue_skill_evolution",
            "continue_loop": True,
        },
        "cognition_to_skill_update": {
            "metadata": {"task_package": "fixture_loop", "loop_source": "generic_loop_engine_fixture"},
            "fields": {
                "next_iteration_skill_constraints": ["Keep candidate changes inside the declared fixture envelope."],
                "next_iteration_evaluator_constraints": ["Keep the same evaluator for controlled comparison."],
                "next_iteration_task_refinements": ["Do not widen the fixture scope in the verification run."],
                "search_priority_updates": ["Prioritize one more bounded candidate before any envelope expansion."],
                "required_discriminating_tests": ["Compare the next bounded candidate against the same baseline."],
                "summary": "The next iteration should remain bounded and comparable.",
            },
        },
    }
    record = {
        "current_cognition_state": {
            "summary": "The deterministic fixture proves harness record enforcement but does not yet prove skill effectiveness on a real power-system task.",
            "evidence_state": "Three persisted worker-chain objects are available before cognition routing.",
            "claim_boundary": "Only E2E harness behavior and record quality can be claimed from this run.",
        },
        "identified_constraints": [
            "The task007_fixture adapter intentionally has a narrow deterministic search envelope.",
            "The fixture evaluator score is static and cannot support broad research-performance claims.",
            "The next iteration should preserve A/B comparability before adding real task complexity.",
        ],
        "blocked_paths": [
            "Do not claim general autonomous research capability from this fixture-only evidence.",
            "Do not widen the evaluator or task package inside the A/B harness regression test.",
        ],
        "next_cognition_direction": {
            "question": "Does the harness quality gain persist on a second adapter with a real evaluator binding?",
            "recommended_probe": "Add a non-fixture task package after the deterministic A/B lane remains stable.",
            "success_signal": "Required-field coverage remains 100% and average quality remains >= 80.",
        },
    }
    return _with_harness_record(base, record, inputs)
