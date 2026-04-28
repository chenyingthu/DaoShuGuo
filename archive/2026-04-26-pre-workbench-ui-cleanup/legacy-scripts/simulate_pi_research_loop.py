#!/usr/bin/env python3
"""Simulate the DaoShuGuo Pi research-loop tools without an LLM provider."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ensure_markdown(path: Path, task_ref: str, objective: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(
        "\n".join(
            [
                f"# DaoShuGuo Research Loop: {task_ref}",
                "",
                "## Objective",
                objective,
                "",
                "## Current Constraints",
                "- Keep task, evaluator, and evidence boundaries explicit.",
                "- Skill agents change candidate skill code only.",
                "- Cognition agents change next-round constraints only.",
                "- Effectiveness claims must stay below the evidence ceiling.",
                "",
                "## What Has Been Tried",
                "- Initialized Pi research loop.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def simulate(workdir: Path) -> dict[str, Any]:
    task_ref = "task.power.ieee69_renewable_reactive_opt"
    objective = "Validate a Pi-harnessed task003 skill trial with durable loop memory."
    md_path = workdir / "research_loop.md"
    jsonl_path = workdir / "research_loop.jsonl"
    ensure_markdown(md_path, task_ref, objective)
    append_jsonl(
        jsonl_path,
        {
            "timestamp": utc_now(),
            "event": "init_research_task",
            "task_ref": task_ref,
            "data": {"objective": objective},
        },
    )
    append_jsonl(
        jsonl_path,
        {
            "timestamp": utc_now(),
            "event": "skill_trial",
            "task_ref": task_ref,
            "data": {
                "skill_ref": "skill.power.renewable_inverter_reactive_optimizer_task003",
                "run_ref": "run.power.ieee69_renewable_reactive_opt.0001",
                "outcome": "inconclusive",
                "evidence_path": "runs/task003/run_0001/run.yaml",
                "next_constraint": "Keep renewable-aware control but require matched comparison.",
                "run_dir": "runs/task003/run_0001",
                "report_ref": "report.power.ieee69_renewable_reactive_opt.note_0001",
            },
        },
    )
    append_jsonl(
        jsonl_path,
        {
            "timestamp": utc_now(),
            "event": "cognition_constraint",
            "task_ref": task_ref,
            "data": {
                "source_run_ref": "run.power.ieee69_renewable_reactive_opt.0001",
                "constraint": "Keep renewable-aware control but require matched comparison.",
                "blocked_path": "pure_weak_shunt_substitution",
                "required_test": "Compare against a semantically matched renewable-aware variant.",
            },
        },
    )
    append_jsonl(
        jsonl_path,
        {
            "timestamp": utc_now(),
            "event": "iteration_review",
            "task_ref": task_ref,
            "data": {
                "iteration": 1,
                "verdict": "real_progress",
                "summary": "Pi durable loop files were initialized and a bounded task003 trial was recorded.",
            },
        },
    )
    with md_path.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n### Skill Trial: skill.power.renewable_inverter_reactive_optimizer_task003\n"
            "- run_dir: runs/task003/run_0001\n"
            "- run_ref: run.power.ieee69_renewable_reactive_opt.0001\n"
            "- report_ref: report.power.ieee69_renewable_reactive_opt.note_0001\n"
            "- outcome: inconclusive\n"
            "- evidence_path: runs/task003/run_0001/run.yaml\n"
            "- next_constraint: Keep renewable-aware control but require matched comparison.\n"
            "\n### Cognition Constraint from run.power.ieee69_renewable_reactive_opt.0001\n"
            "- constraint: Keep renewable-aware control but require matched comparison.\n"
            "- blocked_path: pure_weak_shunt_substitution\n"
            "- required_test: Compare against a semantically matched renewable-aware variant.\n"
            "\n### Iteration Review 1\n"
            "- verdict: real_progress\n"
            "- summary: Pi durable loop files were initialized and a bounded task003 trial was recorded.\n"
        )
    return {
        "workdir": str(workdir),
        "markdown": str(md_path),
        "jsonl": str(jsonl_path),
        "entries": sum(1 for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate DaoShuGuo Pi research loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/task003_sim")
    args = parser.parse_args()
    result = simulate(REPO_ROOT / args.workdir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
