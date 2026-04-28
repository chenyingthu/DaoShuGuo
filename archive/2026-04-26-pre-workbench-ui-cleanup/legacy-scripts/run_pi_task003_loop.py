#!/usr/bin/env python3
"""Run a stabilized step-based Pi task003 research loop."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.pi_runtime import get_default_pi_profile, run_pi_prompt as run_pi_runtime_prompt, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
PI_PROFILE = get_default_pi_profile()

STEP_SEQUENCE = [
    "init_step",
    "task_trial_step",
    "skill_record_step",
    "cognition_constraint_step",
    "iteration_review_step",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def state_paths(workdir: Path) -> tuple[Path, Path, Path]:
    state_dir = workdir / "state"
    return (
        state_dir / "research_state.json",
        state_dir / "requests",
        state_dir / "results",
    )


def load_state(state_path: Path) -> dict[str, Any]:
    if state_path.exists():
        return load_json(state_path)
    return {
        "task_ref": "task.power.ieee69_renewable_reactive_opt",
        "iteration": 1,
        "current_step": STEP_SEQUENCE[0],
        "steps": {},
        "provider": PI_PROFILE["provider"],
        "model": PI_PROFILE["model"],
        "workdir": "",
    }


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    write_json(state_path, state)


def prompt_for_step(step: str, state: dict[str, Any]) -> str:
    task_ref = state["task_ref"]
    if step == "init_step":
        return (
            "Use init_research_task with "
            f"task_ref {task_ref} and objective "
            "'Validate the first stable step-based Pi-driven DaoShuGuo task003 loop.'"
        )
    if step == "task_trial_step":
        return (
            "Use run_task003_trial with strategy inverter-support and repo_root "
            f"{REPO_ROOT}."
        )
    if step == "skill_record_step":
        run_ref = state["steps"].get("task_trial_step", {}).get("extracted", {}).get(
            "runRef", "run.power.ieee69_renewable_reactive_opt.unknown"
        )
        run_dir = state["steps"].get("task_trial_step", {}).get("extracted", {}).get(
            "runDir", "runs/task003/unknown"
        )
        return (
            "Use record_skill_trial with "
            f"task_ref {task_ref}, "
            "skill_ref skill.power.renewable_inverter_reactive_optimizer_task003, "
            f"run_ref {run_ref}, "
            "outcome success, "
            f"evidence_path {run_dir}/run.yaml, "
            "and next_constraint 'Require a bounded cognition constraint before the next iteration.'"
        )
    if step == "cognition_constraint_step":
        run_ref = state["steps"].get("task_trial_step", {}).get("extracted", {}).get(
            "runRef", "run.power.ieee69_renewable_reactive_opt.unknown"
        )
        return (
            "Use record_cognition_constraint with "
            f"task_ref {task_ref}, "
            f"source_run_ref {run_ref}, "
            "constraint 'Keep renewable-aware control and require a matched comparison before broader claims.', "
            "blocked_path pure_weak_shunt_substitution, "
            "and required_test 'Compare against a semantically matched renewable-aware variant under the same evaluator.'"
        )
    if step == "iteration_review_step":
        return (
            "Use record_iteration_review with "
            f"task_ref {task_ref}, "
            "iteration 1, "
            "verdict real_progress, "
            "and summary 'Pi executed a bounded task003 trial and wrote durable loop artifacts.'"
        )
    raise RuntimeError(f"unknown step: {step}")


def extract_from_events(step: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for event in events:
        if event.get("type") == "tool_execution_end":
            result = event.get("result", {})
            details = result.get("details", {})
            if step == "task_trial_step":
                for key in ("runDir", "runRef", "reportRef", "strategy", "repo_root"):
                    if key in details:
                        extracted[key] = details[key]
            elif step in {"init_step", "skill_record_step", "cognition_constraint_step", "iteration_review_step"}:
                extracted["toolName"] = event.get("toolName")
                extracted["details"] = details
    return extracted


def run_has_agent_error(run: dict[str, Any]) -> bool:
    for event in run["events"]:
        message = event.get("message")
        if isinstance(message, dict) and message.get("stopReason") == "error":
            return True
    return False


def is_completed_step(step: str, run: dict[str, Any], extracted: dict[str, Any]) -> bool:
    if run["exit_code"] != 0 or run_has_agent_error(run):
        return False
    if step == "task_trial_step":
        return bool(extracted.get("runDir") and extracted.get("runRef"))
    if step in {"init_step", "skill_record_step", "cognition_constraint_step", "iteration_review_step"}:
        return bool(extracted.get("toolName"))
    return False


def run_pi_prompt(prompt: str, cwd: Path) -> dict[str, Any]:
    return run_pi_runtime_prompt(
        prompt,
        cwd,
        provider=PI_PROFILE["provider"],
        model=PI_PROFILE["model"],
        thinking=PI_PROFILE["thinking"],
    )


def is_step_complete(step: str, step_data: dict[str, Any]) -> bool:
    if step_data.get("status") != "completed":
        return False
    if step == "task_trial_step":
        extracted = step_data.get("extracted", {})
        return bool(extracted.get("runDir") and extracted.get("runRef"))
    return True


def run_loop(workdir: Path) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    state_path, requests_dir, results_dir = state_paths(workdir)
    requests_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    state = load_state(state_path)
    state["workdir"] = str(workdir)
    all_results: list[dict[str, Any]] = []

    for step in STEP_SEQUENCE:
        existing = state["steps"].get(step, {})
        if is_step_complete(step, existing):
            all_results.append({"step": step, **existing})
            continue

        prompt = prompt_for_step(step, state)
        request = {
            "step": step,
            "created_at": utc_now(),
            "prompt": prompt,
            "task_ref": state["task_ref"],
            "provider": state["provider"],
            "model": state["model"],
        }
        write_json(requests_dir / f"{step}.json", request)

        state["current_step"] = step
        state["steps"][step] = {
            "status": "running",
            "started_at": utc_now(),
            "provider": state["provider"],
            "model": state["model"],
            "prompt": prompt,
        }
        save_state(state_path, state)

        run = run_pi_prompt(prompt, workdir)
        extracted = extract_from_events(step, run["events"])
        status = "completed" if is_completed_step(step, run, extracted) else "failed"
        result_payload = {
            "step": step,
            "status": status,
            "started_at": state["steps"][step]["started_at"],
            "finished_at": utc_now(),
            "provider": state["provider"],
            "model": state["model"],
            "prompt": prompt,
            "exit_code": run["exit_code"],
            "stderr": run["stderr"],
            "stdout_excerpt": run["stdout"][:8000],
            "extracted": extracted,
        }
        write_json(results_dir / f"{step}.json", result_payload)
        state["steps"][step] = result_payload
        save_state(state_path, state)
        all_results.append(result_payload)
        if status != "completed":
            break

    return {
        "workdir": str(workdir),
        "state_path": str(state_path),
        "steps": all_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a stabilized Pi task003 loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/pi_json_loop_task003_state")
    args = parser.parse_args()
    result = run_loop(REPO_ROOT / args.workdir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
