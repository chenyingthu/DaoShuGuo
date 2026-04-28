#!/usr/bin/env python3
"""Project-local schema validator.

Checks:
1. Required fields
2. Simple type validation
3. Controlled enum validation
4. Nested substructure required fields
5. Reference existence
6. A small set of semantic compatibility rules
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


OBJECT_TYPE_TO_PREFIX = {
    "task": "task",
    "baseline": "baseline",
    "evaluator": "evaluator",
    "run": "run",
    "skill": "skill",
    "cognition": "cognition",
    "agent_trace": "agent_trace",
    "prompt_observation": "prompt_observation",
    "taste_assessment": "taste",
    "evidence_bundle": "evidence",
    "strategy_comparison": "comparison",
    "strategy_semantic_comparison": "semantic_comparison",
    "novelty_assessment": "novelty",
    "cognition_upgrade": "cognition_upgrade",
    "literature_alignment": "literature_alignment",
    "paper_record": "paper_record",
    "paper_excerpt": "paper_excerpt",
    "method_card": "method_card",
    "explanation_card": "explanation_card",
    "explanation_alignment": "explanation_alignment",
    "literature_source": "literature_source",
    "validation_plan": "validation",
    "experiment_matrix": "experiment_matrix",
    "application_assessment": "application",
    "deliverable_package": "deliverable",
    "claim_routing": "claim_routing",
    "report": "report",
    "cognition_event": "cognition_event",
    "cognition_to_skill_update": "cognition_to_skill_update",
    "skill_iteration_plan": "skill_iteration_plan",
    "loop_review": "loop_review",
    "skill_agent_iteration_request": "skill_agent_iteration_request",
    "skill_agent_iteration_result": "skill_agent_iteration_result",
    "agentic_cognition_to_skill_update": "agentic_cognition_to_skill_update",
    "agentic_loop_iteration_review": "agentic_loop_iteration_review",
    "research_batch": "research_batch",
    "worker_runtime_binding": "worker_runtime_binding",
    "agent_context_pack": "agent_context_pack",
    "execution_ledger": "execution_ledger",
    "research_review": "research_review",
    "repair_request": "repair_request",
    "repair_result": "repair_result",
    "approval_record": "approval_record",
    "ablation_plan": "ablation_plan",
    "ablation_result": "ablation_result",
    "learning_need": "learning_need",
    "learning_context_pack": "learning_context_pack",
    "skill_structure_diagnosis": "skill_structure_diagnosis",
    "structural_skill_change_request": "structural_skill_change_request",
    "skill_structure_assessment": "skill_structure_assessment",
    "research_portfolio_assessment": "portfolio_assessment",
    "research_framing_map": "research_framing_map",
    "method_family_map": "method_family_map",
    "metric_taxonomy": "metric_taxonomy",
    "claim_threshold_map": "claim_threshold_map",
    "experiment_design_recommendation": "experiment_design_recommendation",
    "task_adapter": "task_adapter",
    "task_readiness_report": "task_readiness",
    "full_loop_validation_report": "full_loop_validation",
    "backend_comparison_report": "backend_comparison",
    "workbench_topic": "workbench_topic",
    "workbench_timeline_event": "workbench_timeline_event",
    "human_review": "human_review",
    "research_decision": "research_decision",
    "direction_override": "direction_override",
    "expert_annotation": "expert_annotation",
    "claim_approval": "claim_approval",
    "iteration_steering": "iteration_steering",
    "routing_constraint": "routing_constraint",
    "agent_response_to_human": "agent_response_to_human",
    "agent_explanation_card": "agent_explanation_card",
    "human_attention_item": "human_attention_item",
    "researcher_lens": "researcher_lens",
    "mentor_brief": "mentor_brief",
    "iteration_digest": "iteration_digest",
    "decision_brief": "decision_brief",
    "failure_brief": "failure_brief",
    "claim_brief": "claim_brief",
}

PREFIX_TO_OBJECT_TYPE = {v: k for k, v in OBJECT_TYPE_TO_PREFIX.items()}

GRADE_TO_ALLOWED_REPORT_TYPES = {
    "tuoyu": {"paper_draft", "technical_note"},
    "zhuoshi": {"paper_draft", "technical_note"},
    "diaomu": {"technical_note", "experiment_record"},
    "huimo": {"discussion_memo"},
}

ARTIFACT_SETS = {
    "literature-alignment-plan": {
        "target_globs": [
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "analysis/task001/compare_*/strategy_comparison.yaml",
            "analysis/task001/compare_*/cognition.yaml",
            "analysis/task001/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task001/literature_*/literature_alignment.yaml",
            "analysis/task001/explanations_*/explanation_alignment.yaml",
            "analysis/task001/upgrade_*/novelty_assessment.yaml",
            "analysis/task001/upgrade_*/cognition_upgrade.yaml",
            "analysis/task001/upgrade_*/upgraded_cognition.yaml",
            "cognition/cards/upgraded_strategy_comparison_*.yaml",
        ],
        "support_globs": [
            "tasks/task001/*.yaml",
            "tasks/task002/*.yaml",
            "evaluators/*.yaml",
            "runs/task001/run_*/run.yaml",
            "runs/task002/run_*/run.yaml",
            "runs/task001/run_*/agent_trace.yaml",
            "runs/task001/run_*/prompt_observation.yaml",
            "runs/task001/run_*/taste_assessment.yaml",
            "runs/task001/run_*/evidence_bundle.yaml",
            "runs/task001/run_*/report.yaml",
            "runs/task001/run_*/cognition.yaml",
            "analysis/task002/compare_*/strategy_comparison.yaml",
            "analysis/task002/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task002/literature_*/literature_alignment.yaml",
            "analysis/task002/explanations_*/explanation_alignment.yaml",
            "analysis/task002/upgrade_*/novelty_assessment.yaml",
            "analysis/task002/upgrade_*/cognition_upgrade.yaml",
            "cognition/cards/strategy_comparison_*.yaml",
            "cognition/cards/strategy_comparison_ieee69_reactive_opt_*.yaml",
            "cognition/cards/ieee33_reactive_opt_runtime_*.yaml",
            "cognition/cards/ieee69_reactive_opt_runtime_*.yaml",
            "cognition/failed/*.yaml",
            "schemas/samples/*.yaml",
        ],
    },
    "task002-pipeline": {
        "target_globs": [
            "tasks/task002/task.yaml",
            "tasks/task002/baseline.yaml",
            "evaluators/task002_evaluator.yaml",
            "runs/task002/run_*/run.yaml",
            "runs/task002/run_*/agent_trace.yaml",
            "runs/task002/run_*/prompt_observation.yaml",
            "runs/task002/run_*/taste_assessment.yaml",
            "runs/task002/run_*/evidence_bundle.yaml",
            "runs/task002/run_*/report.yaml",
            "runs/task002/run_*/cognition.yaml",
            "analysis/task002/compare_*/strategy_comparison.yaml",
            "analysis/task002/compare_*/cognition.yaml",
            "analysis/task002/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task002/literature_*/literature_alignment.yaml",
            "analysis/task002/explanations_*/explanation_alignment.yaml",
            "analysis/task002/upgrade_*/novelty_assessment.yaml",
            "analysis/task002/upgrade_*/cognition_upgrade.yaml",
            "analysis/task002/upgrade_*/upgraded_cognition.yaml",
            "cognition/cards/ieee69_reactive_opt_runtime_*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "skills/**/*.yaml",
            "tasks/task001/*.yaml",
            "tasks/task002/*.yaml",
            "evaluators/*.yaml",
            "runs/task001/run_*/run.yaml",
            "runs/task002/run_*/run.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
        ],
    },
    "task003-pipeline": {
        "target_globs": [
            "tasks/task003/task.yaml",
            "tasks/task003/baseline.yaml",
            "evaluators/task003_evaluator.yaml",
            "runs/task003/run_*/run.yaml",
            "runs/task003/run_*/agent_trace.yaml",
            "runs/task003/run_*/prompt_observation.yaml",
            "runs/task003/run_*/taste_assessment.yaml",
            "runs/task003/run_*/evidence_bundle.yaml",
            "runs/task003/run_*/report.yaml",
            "runs/task003/run_*/cognition.yaml",
            "cognition/cards/ieee69_renewable_reactive_opt_runtime_*.yaml",
            "cognition/failed/ieee69_renewable_reactive_opt_runtime_failure_*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "skills/**/*.yaml",
            "tasks/task001/*.yaml",
            "tasks/task002/*.yaml",
            "tasks/task003/*.yaml",
            "evaluators/*.yaml",
            "runs/task001/run_*/run.yaml",
            "runs/task002/run_*/run.yaml",
            "runs/task003/run_*/run.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task003-cognition-stage": {
        "target_globs": [
            "analysis/task003/compare_*/strategy_comparison.yaml",
            "analysis/task003/compare_*/cognition.yaml",
            "analysis/task003/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task003/upgrade_*/novelty_assessment.yaml",
            "analysis/task003/upgrade_*/cognition_upgrade.yaml",
            "analysis/task003/upgrade_*/upgraded_cognition.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "tasks/task003/*.yaml",
            "evaluators/*.yaml",
            "runs/task003/run_*/run.yaml",
            "runs/task003/run_*/report.yaml",
            "runs/task003/run_*/cognition.yaml",
            "analysis/task003/literature_*/literature_alignment.yaml",
            "analysis/task003/explanations_*/explanation_alignment.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task003-literature-stage": {
        "target_globs": [
            "analysis/task003/literature_*/literature_alignment.yaml",
            "analysis/task003/explanations_*/explanation_alignment.yaml",
            "analysis/task003/upgrade_*/novelty_assessment.yaml",
            "analysis/task003/upgrade_*/cognition_upgrade.yaml",
            "analysis/task003/upgrade_*/upgraded_cognition.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "literature/task003-seed-papers.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "tasks/task003/*.yaml",
            "runs/task003/run_*/run.yaml",
            "analysis/task003/compare_*/strategy_comparison.yaml",
            "analysis/task003/semantic_*/strategy_semantic_comparison.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task004-pipeline": {
        "target_globs": [
            "tasks/task004/task.yaml",
            "tasks/task004/baseline.yaml",
            "evaluators/task004_evaluator.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/agent_trace.yaml",
            "runs/task004/run_*/prompt_observation.yaml",
            "runs/task004/run_*/taste_assessment.yaml",
            "runs/task004/run_*/evidence_bundle.yaml",
            "runs/task004/run_*/report.yaml",
            "runs/task004/run_*/cognition.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task004/*.yaml",
            "evaluators/*.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/report.yaml",
            "runs/task004/run_*/cognition.yaml",
            "analysis/task004/boundary_overclaim_*/boundary_overclaim_check.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task004-cognition-stage": {
        "target_globs": [
            "analysis/task004/compare_*/strategy_comparison.yaml",
            "analysis/task004/compare_*/cognition.yaml",
            "analysis/task004/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task004/upgrade_*/novelty_assessment.yaml",
            "analysis/task004/upgrade_*/cognition_upgrade.yaml",
            "analysis/task004/upgrade_*/upgraded_cognition.yaml",
            "analysis/task004/mismatch_*/task_mismatch_check.yaml",
            "analysis/task004/mismatch_*/cognition.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task004/*.yaml",
            "evaluators/*.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/report.yaml",
            "runs/task004/run_*/cognition.yaml",
            "analysis/task004/boundary_overclaim_*/boundary_overclaim_check.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task004-cognition-stage": {
        "target_globs": [
            "analysis/task004/compare_*/strategy_comparison.yaml",
            "analysis/task004/compare_*/cognition.yaml",
            "analysis/task004/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task004/upgrade_*/novelty_assessment.yaml",
            "analysis/task004/upgrade_*/cognition_upgrade.yaml",
            "analysis/task004/upgrade_*/upgraded_cognition.yaml",
            "analysis/task004/mismatch_*/task_mismatch_check.yaml",
            "analysis/task004/mismatch_*/cognition.yaml",
            "analysis/task004/boundary_overclaim_*/boundary_overclaim_check.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "tasks/task004/*.yaml",
            "evaluators/*.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/report.yaml",
            "runs/task004/run_*/cognition.yaml",
            "analysis/task004/literature_*/literature_alignment.yaml",
            "analysis/task004/explanations_*/explanation_alignment.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task004-literature-stage": {
        "target_globs": [
            "analysis/task004/literature_*/literature_alignment.yaml",
            "analysis/task004/explanations_*/explanation_alignment.yaml",
            "analysis/task004/upgrade_*/novelty_assessment.yaml",
            "analysis/task004/upgrade_*/cognition_upgrade.yaml",
            "analysis/task004/upgrade_*/upgraded_cognition.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "literature/task004-seed-papers.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "tasks/task004/*.yaml",
            "runs/task004/run_*/run.yaml",
            "analysis/task004/compare_*/strategy_comparison.yaml",
            "analysis/task004/semantic_*/strategy_semantic_comparison.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task005-pipeline": {
        "target_globs": [
            "tasks/task005/task.yaml",
            "tasks/task005/baseline.yaml",
            "evaluators/task005_evaluator.yaml",
            "runs/task005/run_*/run.yaml",
            "runs/task005/run_*/agent_trace.yaml",
            "runs/task005/run_*/prompt_observation.yaml",
            "runs/task005/run_*/taste_assessment.yaml",
            "runs/task005/run_*/evidence_bundle.yaml",
            "runs/task005/run_*/report.yaml",
            "runs/task005/run_*/cognition.yaml",
            "analysis/task005/mismatch_*/task_mismatch_check.yaml",
            "analysis/task005/mismatch_*/cognition.yaml",
            "analysis/task005/resilience_overclaim_*/boundary_overclaim_check.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task005/*.yaml",
            "evaluators/*.yaml",
            "runs/task005/run_*/run.yaml",
            "runs/task005/run_*/report.yaml",
            "runs/task005/run_*/cognition.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "task005-cognition-stage": {
        "target_globs": [
            "analysis/task005/compare_*/strategy_comparison.yaml",
            "analysis/task005/compare_*/cognition.yaml",
            "analysis/task005/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task005/upgrade_*/novelty_assessment.yaml",
            "analysis/task005/upgrade_*/cognition_upgrade.yaml",
            "analysis/task005/upgrade_*/upgraded_cognition.yaml",
            "analysis/task005/mismatch_*/task_mismatch_check.yaml",
            "analysis/task005/mismatch_*/cognition.yaml",
            "analysis/task005/resilience_overclaim_*/boundary_overclaim_check.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task005/*.yaml",
            "evaluators/*.yaml",
            "runs/task005/run_*/run.yaml",
            "runs/task005/run_*/report.yaml",
            "runs/task005/run_*/cognition.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "effectiveness-delivery-layer": {
        "target_globs": [
            "effectiveness/task*/validation_plan.yaml",
            "effectiveness/task*/experiment_matrix.yaml",
            "effectiveness/task*/application_assessment.yaml",
            "effectiveness/task*/deliverable_package.yaml",
            "effectiveness/task*/claim_routing.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
            "tasks/task003/*.yaml",
            "tasks/task004/*.yaml",
            "runs/task003/run_*/run.yaml",
            "runs/task004/run_*/run.yaml",
            "analysis/task003/upgrade_*/cognition_upgrade.yaml",
            "analysis/task004/upgrade_*/cognition_upgrade.yaml",
            "analysis/task003/literature_*/literature_alignment.yaml",
            "analysis/task004/literature_*/literature_alignment.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "skill-cognition-loop": {
        "target_globs": [
            "analysis/loop/task*/events/*.yaml",
            "analysis/loop/task*/updates/*.yaml",
            "analysis/loop/task*/plans/*.yaml",
            "analysis/loop/task*/reviews/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task003/*.yaml",
            "tasks/task004/*.yaml",
            "tasks/task005/*.yaml",
            "runs/task003/run_*/run.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task005/run_*/run.yaml",
            "analysis/task003/semantic_*/strategy_semantic_comparison.yaml",
            "analysis/task003/upgrade_*/cognition_upgrade.yaml",
            "analysis/task004/boundary_overclaim_*/boundary_overclaim_check.yaml",
            "analysis/task004/upgrade_*/cognition_upgrade.yaml",
            "analysis/task005/mismatch_*/task_mismatch_check.yaml",
            "analysis/task005/resilience_overclaim_*/boundary_overclaim_check.yaml",
            "analysis/task005/upgrade_*/cognition_upgrade.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "real-agentic-loop": {
        "target_globs": [
            "agents/skill/requests/*.yaml",
            "agents/skill/results/*.yaml",
            "analysis/agentic_loop/task*/updates/*.yaml",
            "analysis/agentic_loop/task*/reviews/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task003/*.yaml",
            "skills/active_dev/*.yaml",
            "runs/task003/run_*/run.yaml",
            "analysis/loop/task003/events/*.yaml",
            "analysis/loop/task003/updates/*.yaml",
            "agents/cognition/workflow_outputs/*.json",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
        ],
    },
    "research-plan-execute-protocol": {
        "target_globs": [
            "analysis/research_plan_execute/task*/research_batch.yaml",
            "analysis/research_plan_execute/task*/worker_runtime_binding.*.yaml",
            "analysis/research_plan_execute/task*/agent_context_pack.*.yaml",
            "analysis/research_plan_execute/task*/execution_ledger.yaml",
            "analysis/research_plan_execute/task*/research_review*.yaml",
            "analysis/research_plan_execute/task*/repair_request*.yaml",
            "analysis/research_plan_execute/task*/repair_result*.yaml",
            "analysis/research_plan_execute/task*/approval_record*.yaml",
            "analysis/research_plan_execute/task*/ablation_plan*.yaml",
            "analysis/research_plan_execute/task*/ablation_result*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task003/*.yaml",
            "evaluators/*.yaml",
            "runs/task003/run_*/run.yaml",
            "agents/skill/requests/*.yaml",
            "agents/skill/results/*.yaml",
            "analysis/agentic_loop/task003/updates/*.yaml",
            "analysis/agentic_loop/task003/reviews/*.yaml",
            "cognition/cards/*.yaml",
            "cognition/failed/*.yaml",
            "skills/active_dev/*.yaml",
        ],
    },
    "structural-learning-worker": {
        "target_globs": [
            "analysis/structural_learning/task*/learning_need.yaml",
            "analysis/structural_learning/task*/learning_context_pack.yaml",
            "analysis/structural_learning/task*/skill_structure_diagnosis.yaml",
            "analysis/structural_learning/task*/structural_skill_change_request.yaml",
            "analysis/structural_learning/task*/skill_structure_assessment.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task003/*.yaml",
            "evaluators/*.yaml",
            "skills/active_dev/*.yaml",
            "analysis/research_plan_execute/task*/research_review.yaml",
            "analysis/research_plan_execute/task*/approval_record.yaml",
            "analysis/agentic_loop/task003/updates/*.yaml",
            "analysis/agentic_loop/task003/reviews/*.yaml",
            "runs/task003/run_*/run.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
        ],
    },
    "cross-task-portfolio": {
        "target_globs": [
            "analysis/portfolio/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task003/*.yaml",
            "tasks/task004/*.yaml",
            "tasks/task005/*.yaml",
            "evaluators/*.yaml",
            "runs/task003/run_*/run.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task005/run_*/run.yaml",
            "analysis/structural_learning/task*/skill_structure_assessment.yaml",
            "analysis/task004/skill_diagnosis_*/*.yaml",
            "analysis/task004/boundary_overclaim_*/*.yaml",
            "analysis/task005/mismatch_*/*.yaml",
            "analysis/task005/resilience_overclaim_*/*.yaml",
        ],
    },
    "generic-task-onboarding": {
        "target_globs": [
            "adapters/*.yaml",
            "analysis/onboarding/*/task_readiness_report.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task*/**/*.yaml",
            "evaluators/*.yaml",
            "skills/**/*.yaml",
        ],
    },
    "generic-full-loop-validation": {
        "target_globs": [
            "analysis/full_loop_validation/*_report.yaml",
            "analysis/runtime_matrix/agent_runtime_experiment_matrix.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "adapters/*.yaml",
            "tasks/task*/**/*.yaml",
            "evaluators/*.yaml",
            "skills/**/*.yaml",
            "analysis/onboarding/*/task_readiness_report.yaml",
        ],
    },
    "real-task-001": {
        "target_globs": [
            "analysis/real_task_001/readiness/*.yaml",
            "analysis/real_task_001/reports/*.yaml",
            "analysis/real_task_001/delivery/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task004/*.yaml",
            "adapters/task004.yaml",
            "evaluators/task004_evaluator.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/cognition.yaml",
            "runs/task004/run_*/evidence_bundle.yaml",
            "runs/task004/run_*/taste_assessment.yaml",
            "runs/task004/run_*/report.yaml",
            "analysis/real_task_001/rounds/round_*/artifacts/**/*.yaml",
        ],
    },
    "real-task-001-reframing": {
        "target_globs": [
            "analysis/real_task_001/reframing/*.yaml",
            "analysis/real_task_001/literature/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task004/*.yaml",
            "adapters/task004.yaml",
            "evaluators/task004_evaluator.yaml",
            "analysis/real_task_001/readiness/*.yaml",
            "analysis/real_task_001/reports/*.yaml",
            "analysis/real_task_001/delivery/*.yaml",
            "analysis/real_task_001/rounds/round_*/artifacts/**/*.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/cognition.yaml",
            "runs/task004/run_*/evidence_bundle.yaml",
            "runs/task004/run_*/taste_assessment.yaml",
            "runs/task004/run_*/report.yaml",
            "literature/sources/*.yaml",
            "literature/papers/*.yaml",
            "literature/excerpts/*.yaml",
            "literature/cards/methods/*.yaml",
            "literature/cards/explanations/*.yaml",
        ],
    },
    "real-task-001-upgrade": {
        "target_globs": [
            "analysis/real_task_001_upgrade/delivery/*.yaml",
            "analysis/real_task_001_upgrade/reports/report.yaml",
            "analysis/real_task_001_upgrade/skill_worker_iter02/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task004/*.yaml",
            "adapters/task004.yaml",
            "evaluators/task004_evaluator.yaml",
            "analysis/real_task_001/**/*.yaml",
            "analysis/real_task_001_upgrade/artifacts/**/*.yaml",
            "analysis/real_task_001_upgrade/skill_worker_iter02/*.yaml",
            "analysis/real_task_001_upgrade/reports/upgrade_*.yaml",
            "workbench_data/**/*.yaml",
            "literature/**/*.yaml",
            "skills/**/*.yaml",
            "runs/task004/run_*/run.yaml",
            "runs/task004/run_*/cognition.yaml",
            "runs/task004/run_*/evidence_bundle.yaml",
            "runs/task004/run_*/taste_assessment.yaml",
            "runs/task004/run_*/report.yaml",
        ],
    },
    "workbench": {
        "target_globs": [
            "workbench_data/**/*.yaml",
        ],
        "support_globs": [
            "schemas/samples/*.yaml",
            "tasks/task*/**/*.yaml",
            "adapters/*.yaml",
            "evaluators/*.yaml",
            "runs/task*/run_*/*.yaml",
            "analysis/real_task_001_upgrade/delivery/*.yaml",
            "analysis/real_task_001_upgrade/reports/upgrade_*.yaml",
            "analysis/real_task_001/literature/*.yaml",
            "analysis/real_task_001/reframing/*.yaml",
            "analysis/real_task_001/delivery/*.yaml",
            "analysis/real_task_001/reports/*.yaml",
            "cognition/**/*.yaml",
        ],
    },
}


@dataclass
class ValidationError:
    source: str
    message: str


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


def collect_schema_files(schema_root: Path) -> list[Path]:
    groups = ["core", "assets", "quality", "reporting"]
    files: list[Path] = []
    for group in groups:
        files.extend(sorted((schema_root / group).glob("*.yaml")))
    return files


def collect_sample_files(schema_root: Path) -> list[Path]:
    return sorted((schema_root / "samples").glob("*.yaml"))


def collect_globbed_files(root: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                files.append(path)
    return files


def schema_map(schema_files: list[Path]) -> dict[str, dict[str, Any]]:
    by_object_type: dict[str, dict[str, Any]] = {}
    for path in schema_files:
        schema = load_yaml(path)
        object_type = schema.get("object_type")
        if not isinstance(object_type, str):
            raise ValueError(f"{path} missing object_type")
        by_object_type[object_type] = schema
    return by_object_type


def object_map(sample_files: list[Path]) -> dict[str, dict[str, Any]]:
    objects: dict[str, dict[str, Any]] = {}
    for path in sample_files:
        obj = load_yaml(path)
        object_id = obj.get("object_id")
        if not isinstance(object_id, str):
            raise ValueError(f"{path} missing object_id")
        objects[object_id] = obj
    return objects


def object_map_from_paths(paths: list[Path]) -> dict[str, dict[str, Any]]:
    objects: dict[str, dict[str, Any]] = {}
    for path in paths:
        obj = load_yaml(path)
        object_type = obj.get("object_type")
        object_id = obj.get("object_id")
        if not isinstance(object_type, str) or not isinstance(object_id, str):
            continue
        objects[object_id] = obj
    return objects


def build_object_index(
    paths: list[Path], *, require_object: bool
) -> tuple[dict[str, dict[str, Any]], list[ValidationError]]:
    objects: dict[str, dict[str, Any]] = {}
    errors: list[ValidationError] = []
    for path in paths:
        try:
            obj = load_yaml(path)
        except Exception as exc:
            errors.append(ValidationError(str(path), f"failed to load yaml: {exc}"))
            continue
        object_type = obj.get("object_type")
        object_id = obj.get("object_id")
        if not isinstance(object_type, str) or not isinstance(object_id, str):
            if require_object:
                errors.append(
                    ValidationError(str(path), "expected structured object with object_type and object_id")
                )
            continue
        objects[object_id] = obj
    return objects, errors


def validate_required_fields(data: dict[str, Any], required_fields: list[str], source: str):
    errors: list[ValidationError] = []
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(ValidationError(source, f"missing required field `{field}`"))
    return errors


def is_iso_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def type_matches(spec_type: str, value: Any) -> bool:
    if spec_type == "string":
        return isinstance(value, str)
    if spec_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if spec_type == "boolean":
        return isinstance(value, bool)
    if spec_type == "datetime":
        return isinstance(value, str) and is_iso_datetime(value)
    if spec_type == "object":
        return isinstance(value, dict)
    if spec_type == "array[string]":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if spec_type == "array[object]":
        return isinstance(value, list) and all(isinstance(v, dict) for v in value)
    if spec_type == "enum":
        return True
    return True


def candidate_subschema_name(field_name: str, substructures: dict[str, Any]) -> str | None:
    if field_name in substructures:
        return field_name
    if field_name.endswith("s") and field_name[:-1] in substructures:
        return field_name[:-1]
    return None


def validate_value_against_spec(
    value: Any,
    spec: dict[str, Any],
    source: str,
    field_name: str,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if value is None and spec.get("required", True) is False:
        return errors
    spec_type = spec.get("type")
    if spec_type and not type_matches(spec_type, value):
        errors.append(
            ValidationError(
                source,
                f"field `{field_name}` expected type `{spec_type}` but got `{type(value).__name__}`",
            )
        )
        return errors
    if spec_type == "enum":
        allowed = spec.get("allowed", [])
        if value not in allowed:
            errors.append(
                ValidationError(
                    source,
                    f"field `{field_name}` has invalid enum value `{value}`; allowed={allowed}",
                )
            )
    return errors


def validate_substructure(data: dict[str, Any], schema: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    errors.extend(validate_required_fields(data, schema.get("required_fields", []), source))
    field_specs = schema.get("field_specs", {})

    for field_name, spec in field_specs.items():
        if field_name not in data:
            continue
        value = data[field_name]
        errors.extend(validate_value_against_spec(value, spec, source, field_name))
        nested_required = spec.get("required_fields")
        if nested_required and isinstance(value, dict):
            errors.extend(validate_required_fields(value, nested_required, f"{source}:{field_name}"))
    return errors


def validate_object(data: dict[str, Any], schema: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    errors.extend(validate_required_fields(data, schema.get("required_fields", []), source))

    field_specs = schema.get("field_specs", {})
    substructures = schema.get("substructures", {})

    for field_name, spec in field_specs.items():
        if field_name not in data:
            continue
        value = data[field_name]
        errors.extend(validate_value_against_spec(value, spec, source, field_name))

        spec_type = spec.get("type")
        if spec_type == "object" and isinstance(value, dict):
            sub_name = candidate_subschema_name(field_name, substructures)
            if sub_name:
                errors.extend(
                    validate_substructure(value, substructures[sub_name], f"{source}:{field_name}")
                )

        if spec_type == "array[object]" and isinstance(value, list):
            sub_name = candidate_subschema_name(field_name, substructures)
            if sub_name:
                for idx, item in enumerate(value):
                    errors.extend(
                        validate_substructure(
                            item, substructures[sub_name], f"{source}:{field_name}[{idx}]"
                        )
                    )

    errors.extend(validate_object_identity(data, source))
    return errors


def validate_object_identity(data: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    object_type = data.get("object_type")
    object_id = data.get("object_id")
    if not isinstance(object_type, str) or not isinstance(object_id, str):
        return errors
    expected_prefix = OBJECT_TYPE_TO_PREFIX.get(object_type)
    if expected_prefix and not object_id.startswith(expected_prefix + "."):
        errors.append(
            ValidationError(
                source,
                f"object_id `{object_id}` does not match expected prefix `{expected_prefix}.` for object_type `{object_type}`",
            )
        )
    return errors


def looks_like_object_id(value: str) -> bool:
    if "." not in value:
        return False
    prefix = value.split(".", 1)[0]
    return prefix in PREFIX_TO_OBJECT_TYPE


def iter_references(node: Any, path: str = ""):
    if isinstance(node, dict):
        if "object_id" in node and isinstance(node["object_id"], str):
            yield path + ".object_id", node["object_id"]
        for key, value in node.items():
            next_path = f"{path}.{key}" if path else key
            if key.endswith("_ref") and isinstance(value, str):
                yield next_path, value
            elif key.endswith("_refs") and isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, str):
                        yield f"{next_path}[{idx}]", item
                    elif isinstance(item, dict):
                        yield from iter_references(item, f"{next_path}[{idx}]")
            else:
                yield from iter_references(value, next_path)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            yield from iter_references(item, f"{path}[{idx}]")


def validate_references(data: dict[str, Any], objects_by_id: dict[str, dict[str, Any]], source: str):
    errors: list[ValidationError] = []
    for ref_path, ref_value in iter_references(data):
        if not looks_like_object_id(ref_value):
            continue
        if ref_value not in objects_by_id:
            errors.append(
                ValidationError(source, f"reference `{ref_path}` points to missing object `{ref_value}`")
            )
    return errors


def validate_semantics(objects_by_id: dict[str, dict[str, Any]]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    for object_id, obj in objects_by_id.items():
        object_type = obj.get("object_type")

        if object_type == "report":
            taste_ref = obj.get("taste_assessment_ref")
            report_type = obj.get("report_type")
            if isinstance(taste_ref, str) and taste_ref in objects_by_id:
                taste = objects_by_id[taste_ref]
                grade = taste.get("grade")
                allowed = GRADE_TO_ALLOWED_REPORT_TYPES.get(grade)
                if allowed and report_type not in allowed:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"report_type `{report_type}` is incompatible with taste grade `{grade}`; allowed={sorted(allowed)}",
                        )
                    )

        if object_type == "taste_assessment":
            grade = obj.get("grade")
            recommended = obj.get("recommended_report_type")
            if grade in GRADE_TO_ALLOWED_REPORT_TYPES and recommended is not None:
                allowed = GRADE_TO_ALLOWED_REPORT_TYPES[grade]
                if recommended not in allowed:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"recommended_report_type `{recommended}` is incompatible with grade `{grade}`; allowed={sorted(allowed)}",
                        )
                    )

        if object_type == "cognition":
            cognition_type = obj.get("cognition_type")
            evidence_refs = obj.get("evidence_refs", [])
            if cognition_type == "stable" and not evidence_refs:
                errors.append(
                    ValidationError(object_id, "stable cognition must include non-empty evidence_refs")
                )

        if object_type == "literature_alignment":
            for idx, paper_ref in enumerate(obj.get("literature_refs", [])):
                if not isinstance(paper_ref, str) or "." not in paper_ref:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"literature_refs[{idx}] must use `paper.<name>` format",
                        )
                    )
                    continue
                paper_record_ref = f"paper_record.power.{paper_ref.split('.', 1)[1]}"
                if paper_record_ref not in objects_by_id:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"literature_refs[{idx}] `{paper_ref}` does not resolve to `{paper_record_ref}`",
                        )
                    )

            method_mappings = obj.get("method_mappings", {})
            if isinstance(method_mappings, dict):
                for skill_ref, paper_refs in method_mappings.items():
                    if not isinstance(paper_refs, list):
                        continue
                    for idx, paper_ref in enumerate(paper_refs):
                        if not isinstance(paper_ref, str) or "." not in paper_ref:
                            errors.append(
                                ValidationError(
                                    object_id,
                                    f"method_mappings[{skill_ref}][{idx}] must use `paper.<name>` format",
                                )
                            )
                            continue
                        paper_record_ref = f"paper_record.power.{paper_ref.split('.', 1)[1]}"
                        if paper_record_ref not in objects_by_id:
                            errors.append(
                                ValidationError(
                                    object_id,
                                    f"method_mappings[{skill_ref}][{idx}] `{paper_ref}` does not resolve to `{paper_record_ref}`",
                                )
                            )

    return errors


def validate_samples(schema_root: Path) -> list[ValidationError]:
    schema_files = collect_schema_files(schema_root)
    sample_files = collect_sample_files(schema_root)
    schemas = schema_map(schema_files)
    objects = object_map(sample_files)
    errors: list[ValidationError] = []

    for sample_path in sample_files:
        data = load_yaml(sample_path)
        object_type = data.get("object_type")
        if object_type not in schemas:
            errors.append(
                ValidationError(str(sample_path), f"no schema found for object_type `{object_type}`")
            )
            continue
        schema = schemas[object_type]
        errors.extend(validate_object(data, schema, str(sample_path)))
        errors.extend(validate_references(data, objects, str(sample_path)))

    errors.extend(validate_semantics(objects))
    return errors


def validate_artifact_set(
    *,
    repo_root: Path,
    schema_root: Path,
    artifact_set: str,
) -> list[ValidationError]:
    schema_files = collect_schema_files(schema_root)
    schemas = schema_map(schema_files)
    config = ARTIFACT_SETS[artifact_set]
    target_files = collect_globbed_files(repo_root, config["target_globs"])
    support_files = collect_globbed_files(repo_root, config["support_globs"])
    target_objects, errors = build_object_index(target_files, require_object=True)
    support_objects, support_errors = build_object_index(
        support_files + target_files,
        require_object=False,
    )
    objects = {**support_objects, **target_objects}
    errors.extend(support_errors)

    for artifact_path in target_files:
        data = load_yaml(artifact_path)
        object_type = data.get("object_type")
        object_id = data.get("object_id")
        if not isinstance(object_type, str) or not isinstance(object_id, str):
            continue
        if object_type not in schemas:
            errors.append(
                ValidationError(str(artifact_path), f"no schema found for object_type `{object_type}`")
            )
            continue
        schema = schemas[object_type]
        errors.extend(validate_object(data, schema, str(artifact_path)))
        errors.extend(validate_references(data, objects, str(artifact_path)))

    errors.extend(validate_semantics(objects))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local schema samples.")
    parser.add_argument(
        "--schema-root",
        default="schemas",
        help="Root directory containing schema specs and samples.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used for artifact validation.",
    )
    parser.add_argument(
        "--artifacts",
        choices=sorted(ARTIFACT_SETS),
        nargs="*",
        default=[],
        help="Optional named artifact sets to validate in addition to schema samples.",
    )
    args = parser.parse_args()

    schema_root = Path(args.schema_root)
    repo_root = Path(args.repo_root)
    errors = validate_samples(schema_root)
    for artifact_set in args.artifacts:
        errors.extend(
            validate_artifact_set(
                repo_root=repo_root,
                schema_root=schema_root,
                artifact_set=artifact_set,
            )
        )

    if errors:
        print("Schema validation failed:\n")
        for err in errors:
            print(f"- {err.source}: {err.message}")
        return 1

    if args.artifacts:
        print(f"Schema validation passed. Artifact validation passed for: {', '.join(args.artifacts)}.")
    else:
        print("Schema validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
