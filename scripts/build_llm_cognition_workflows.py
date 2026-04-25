#!/usr/bin/env python3
"""Build multi-role LLM cognition workflow bundles."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "agents" / "cognition" / "workflows"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def workflow_job(
    workflow_id: str,
    job_id: str,
    workflow_role: str,
    agent_role: str,
    prompt_ref: str,
    input_refs: list[str],
    predecessor_output_refs: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "llm_cognition_job",
        "job_id": job_id,
        "workflow_id": workflow_id,
        "workflow_role": workflow_role,
        "created_at": utc_now(),
        "agent_role": agent_role,
        "prompt_ref": prompt_ref,
        "input_refs": input_refs,
        "predecessor_output_refs": predecessor_output_refs,
        "expected_output_schema": "agents/cognition/workflow_spec.yaml",
    }


def build_workflows() -> list[tuple[str, list[dict[str, Any]]]]:
    workflows: list[tuple[str, list[dict[str, Any]]]] = []

    task003_inputs = [
        "analysis/task003/compare_0001/strategy_comparison.yaml",
        "analysis/task003/semantic_0001/strategy_semantic_comparison.yaml",
        "runs/task003/run_0001/run.yaml",
        "runs/task003/run_0003/run.yaml",
    ]
    workflows.append(
        (
            "task003_semantic_workflow_001",
            [
                workflow_job(
                    "task003_semantic_workflow_001",
                    "task003_semantic_proposer_001",
                    "proposer",
                    "semantic_proposer",
                    "agents/cognition/prompts/semantic_proposer.md",
                    task003_inputs,
                    [],
                ),
                workflow_job(
                    "task003_semantic_workflow_001",
                    "task003_semantic_counter_001",
                    "counter",
                    "semantic_counter",
                    "agents/cognition/prompts/semantic_counter.md",
                    task003_inputs,
                    ["agents/cognition/outputs/task003_semantic_proposer_001.json"],
                ),
                workflow_job(
                    "task003_semantic_workflow_001",
                    "task003_semantic_adjudicator_001",
                    "adjudicator",
                    "semantic_adjudicator",
                    "agents/cognition/prompts/semantic_adjudicator.md",
                    task003_inputs,
                    [
                        "agents/cognition/outputs/task003_semantic_proposer_001.json",
                        "agents/cognition/outputs/task003_semantic_counter_001.json",
                        "analysis/task003/semantic_0001/strategy_semantic_comparison.yaml",
                    ],
                ),
            ],
        )
    )

    task004_inputs = [
        "analysis/task004/literature_0002/literature_alignment.yaml",
        "analysis/task004/explanations_0002/explanation_alignment.yaml",
        "analysis/task004/upgrade_0002/cognition_upgrade.yaml",
    ]
    workflows.append(
        (
            "task004_literature_workflow_001",
            [
                workflow_job(
                    "task004_literature_workflow_001",
                    "task004_literature_proposer_001",
                    "proposer",
                    "literature_proposer",
                    "agents/cognition/prompts/literature_proposer.md",
                    task004_inputs,
                    [],
                ),
                workflow_job(
                    "task004_literature_workflow_001",
                    "task004_literature_counter_001",
                    "counter",
                    "literature_counter",
                    "agents/cognition/prompts/literature_counter.md",
                    task004_inputs,
                    ["agents/cognition/outputs/task004_literature_proposer_001.json"],
                ),
                workflow_job(
                    "task004_literature_workflow_001",
                    "task004_literature_adjudicator_001",
                    "adjudicator",
                    "literature_adjudicator",
                    "agents/cognition/prompts/literature_adjudicator.md",
                    task004_inputs,
                    [
                        "agents/cognition/outputs/task004_literature_proposer_001.json",
                        "agents/cognition/outputs/task004_literature_counter_001.json",
                        "analysis/task004/literature_0002/literature_alignment.yaml",
                    ],
                ),
            ],
        )
    )

    effectiveness_inputs = [
        "effectiveness/task003/validation_plan.yaml",
        "effectiveness/task003/application_assessment.yaml",
        "effectiveness/task003/deliverable_package.yaml",
        "effectiveness/task003/claim_routing.yaml",
        "effectiveness/task004/validation_plan.yaml",
        "effectiveness/task004/application_assessment.yaml",
        "effectiveness/task004/deliverable_package.yaml",
        "effectiveness/task004/claim_routing.yaml",
    ]
    workflows.append(
        (
            "effectiveness_workflow_001",
            [
                workflow_job(
                    "effectiveness_workflow_001",
                    "effectiveness_proposer_001",
                    "proposer",
                    "effectiveness_proposer",
                    "agents/cognition/prompts/effectiveness_proposer.md",
                    effectiveness_inputs,
                    [],
                ),
                workflow_job(
                    "effectiveness_workflow_001",
                    "effectiveness_counter_001",
                    "counter",
                    "effectiveness_counter",
                    "agents/cognition/prompts/effectiveness_counter.md",
                    effectiveness_inputs,
                    ["agents/cognition/outputs/effectiveness_proposer_001.json"],
                ),
                workflow_job(
                    "effectiveness_workflow_001",
                    "effectiveness_adjudicator_001",
                    "adjudicator",
                    "effectiveness_adjudicator",
                    "agents/cognition/prompts/effectiveness_adjudicator.md",
                    effectiveness_inputs,
                    [
                        "agents/cognition/outputs/effectiveness_proposer_001.json",
                        "agents/cognition/outputs/effectiveness_counter_001.json",
                        "effectiveness/task003/claim_routing.yaml",
                        "effectiveness/task004/claim_routing.yaml",
                    ],
                ),
            ],
        )
    )

    task005_inputs = [
        "runs/task005/run_0004/run.yaml",
        "runs/task005/run_0004/metrics.json",
        "runs/task005/run_0004/taste_assessment.yaml",
        "runs/task005/run_0004/report.yaml",
        "analysis/task005/semantic_0002/strategy_semantic_comparison.yaml",
    ]
    workflows.append(
        (
            "task005_result_workflow_001",
            [
                workflow_job(
                    "task005_result_workflow_001",
                    "task005_result_proposer_001",
                    "proposer",
                    "interpretation_proposer",
                    "agents/cognition/prompts/result_interpreter.md",
                    task005_inputs,
                    [],
                ),
                workflow_job(
                    "task005_result_workflow_001",
                    "task005_result_counter_001",
                    "counter",
                    "counter_interpreter",
                    "agents/cognition/prompts/semantic_counter.md",
                    task005_inputs,
                    ["agents/cognition/workflow_outputs/task005_result_proposer_001.json"],
                ),
                workflow_job(
                    "task005_result_workflow_001",
                    "task005_result_adjudicator_001",
                    "adjudicator",
                    "semantic_adjudicator",
                    "agents/cognition/prompts/semantic_adjudicator.md",
                    task005_inputs,
                    [
                        "agents/cognition/workflow_outputs/task005_result_proposer_001.json",
                        "agents/cognition/workflow_outputs/task005_result_counter_001.json",
                    ],
                ),
            ],
        )
    )

    return workflows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LLM cognition workflow bundles.")
    parser.add_argument("--output-dir", default="agents/cognition/workflows")
    args = parser.parse_args()
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    for workflow_id, jobs in build_workflows():
        path = output_dir / f"{workflow_id}.json"
        path.write_text(json.dumps({"workflow_id": workflow_id, "jobs": jobs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LLM cognition workflows written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
