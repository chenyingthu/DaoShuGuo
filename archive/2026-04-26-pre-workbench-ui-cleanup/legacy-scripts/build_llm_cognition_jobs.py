#!/usr/bin/env python3
"""Build offline LLM cognition job bundles."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = REPO_ROOT / "agents" / "cognition" / "prompts"
JOB_DIR = REPO_ROOT / "agents" / "cognition" / "jobs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: str) -> str:
    return str(Path(path))


def job_payload(job_id: str, role: str, prompt_name: str, input_refs: list[str], baseline_refs: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "llm_cognition_job",
        "job_id": job_id,
        "created_at": utc_now(),
        "agent_role": role,
        "prompt_ref": f"agents/cognition/prompts/{prompt_name}",
        "input_refs": input_refs,
        "rule_baseline_refs": baseline_refs,
        "expected_output_schema": "agents/cognition/job_spec.yaml",
    }


def latest_run_ref(task_name: str, trigger_reason: str) -> tuple[str, str]:
    runs_dir = REPO_ROOT / "runs" / task_name
    matches = []
    for run_yaml in sorted(runs_dir.glob("run_*/run.yaml")):
        data = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("trigger_reason") == trigger_reason:
            matches.append(run_yaml.parent)
    if not matches:
        raise RuntimeError(f"no run for {task_name} trigger={trigger_reason}")
    run_dir = matches[-1]
    return (
        str((run_dir / "run.yaml").relative_to(REPO_ROOT)),
        str(run_dir.relative_to(REPO_ROOT)),
    )


def render_prompt(job: dict[str, Any]) -> str:
    prompt = load_text(REPO_ROOT / job["prompt_ref"])
    lines = [
        prompt,
        "",
        "## Job",
        json.dumps(job, indent=2, ensure_ascii=False),
        "",
        "## Artifact Excerpts",
    ]
    for ref in job["input_refs"][:12]:
        path = REPO_ROOT / ref
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8")
            lines.extend([f"### {ref}", text[:2000], ""])
    return "\n".join(lines)


def build_jobs() -> list[dict[str, Any]]:
    task005_run_yaml, task005_run_dir = latest_run_ref("task005", "real_renewable-restoration")
    return [
        job_payload(
            "task003_semantic_critic_001",
            "semantic_critic",
            "semantic_critic.md",
            [
                "analysis/task003/compare_0001/strategy_comparison.yaml",
                "analysis/task003/semantic_0001/strategy_semantic_comparison.yaml",
                "runs/task003/run_0001/run.yaml",
                "runs/task003/run_0003/run.yaml",
            ],
            ["analysis/task003/semantic_0001/strategy_semantic_comparison.yaml"],
        ),
        job_payload(
            "task004_literature_reviewer_001",
            "literature_reviewer",
            "literature_reviewer.md",
            [
                "analysis/task004/literature_0002/literature_alignment.yaml",
                "analysis/task004/explanations_0002/explanation_alignment.yaml",
                "analysis/task004/upgrade_0002/cognition_upgrade.yaml",
            ],
            ["analysis/task004/upgrade_0002/cognition_upgrade.yaml"],
        ),
        job_payload(
            "task005_result_interpreter_001",
            "result_interpreter",
            "result_interpreter.md",
            [
                f"{task005_run_dir}/run.yaml",
                f"{task005_run_dir}/metrics.json",
                f"{task005_run_dir}/taste_assessment.yaml",
                f"{task005_run_dir}/report.yaml",
            ],
            [f"{task005_run_dir}/cognition.yaml"],
        ),
        job_payload(
            "effectiveness_reviewer_001",
            "effectiveness_reviewer",
            "effectiveness_reviewer.md",
            [
                "effectiveness/task003/validation_plan.yaml",
                "effectiveness/task003/application_assessment.yaml",
                "effectiveness/task003/deliverable_package.yaml",
                "effectiveness/task003/claim_routing.yaml",
                "effectiveness/task004/validation_plan.yaml",
                "effectiveness/task004/application_assessment.yaml",
                "effectiveness/task004/deliverable_package.yaml",
                "effectiveness/task004/claim_routing.yaml",
            ],
            [
                "effectiveness/task003/claim_routing.yaml",
                "effectiveness/task004/claim_routing.yaml",
            ],
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build offline LLM cognition jobs.")
    parser.add_argument("--output-dir", default="agents/cognition/jobs")
    args = parser.parse_args()
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    for job in build_jobs():
        job_path = output_dir / f"{job['job_id']}.json"
        prompt_path = output_dir / f"{job['job_id']}.prompt.md"
        job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        prompt_path.write_text(render_prompt(job), encoding="utf-8")
    print(f"LLM cognition jobs written to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
