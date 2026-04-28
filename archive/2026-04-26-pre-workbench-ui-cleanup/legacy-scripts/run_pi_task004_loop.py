#!/usr/bin/env python3
"""Run a light Pi task004 loop focused on boundary and effectiveness judgment."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pi_runtime import get_default_pi_profile, run_pi_prompt, write_json


STEP_SEQUENCE = [
    "init_step",
    "task_trial_step",
    "boundary_judgment_step",
    "effectiveness_status_step",
    "iteration_review_step",
]
PI_PROFILE = get_default_pi_profile()


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
        "task_ref": "task.power.ieee69_hosting_capacity",
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
            "'Validate the first light Pi-driven DaoShuGuo task004 loop focused on boundary and effectiveness judgment.'"
        )
    if step == "task_trial_step":
        return (
            "Use run_task004_trial with strategy inverter-support and repo_root "
            f"{REPO_ROOT}."
        )
    if step == "boundary_judgment_step":
        trial = state["steps"]["task_trial_step"]["extracted"]
        return (
            "Use record_boundary_judgment with "
            f"task_ref {task_ref}, "
            f"run_ref {trial['runRef']}, "
            "boundary_statement 'The current result only supports a control-strategy-conditioned static hosting-capacity boundary observation under the present scan envelope.', "
            "claim_ceiling 'Do not describe this as intrinsic system hosting capacity or a paper-level hosting-capacity conclusion.', "
            "boundary_type control_strategy_conditioned_static_capacity"
        )
    if step == "effectiveness_status_step":
        return (
            "Use record_effectiveness_status with "
            f"task_ref {task_ref}, "
            "readiness_level internal_report_ready, "
            "supported_output internal_report_ready, "
            "missing_for_next_level 'multi-scenario hosting capacity, actual boundary-triggering envelope, stronger external benchmark'"
        )
    if step == "iteration_review_step":
        return (
            "Use record_iteration_review with "
            f"task_ref {task_ref}, "
            "iteration 1, "
            "verdict real_progress, "
            "and summary 'Pi executed a bounded task004 boundary trial and recorded boundary and effectiveness artifacts.'"
        )
    raise RuntimeError(step)


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
            else:
                extracted["toolName"] = event.get("toolName")
                extracted["details"] = details
    return extracted


def is_completed_step(step: str, run: dict[str, Any], extracted: dict[str, Any]) -> bool:
    if run["exit_code"] != 0:
        return False
    if step == "task_trial_step":
        return bool(extracted.get("runDir") and extracted.get("runRef"))
    return bool(extracted.get("toolName"))


def run_loop(workdir: Path, *, provider: str | None = None, model: str | None = None, thinking: str | None = None) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    state_path, requests_dir, results_dir = state_paths(workdir)
    requests_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    state = load_state(state_path)
    state["provider"] = provider or state.get("provider") or PI_PROFILE["provider"]
    state["model"] = model or state.get("model") or PI_PROFILE["model"]
    effective_thinking = thinking or PI_PROFILE["thinking"]
    state["workdir"] = str(workdir)
    all_results: list[dict[str, Any]] = []

    for step in STEP_SEQUENCE:
        existing = state["steps"].get(step, {})
        if existing.get("status") == "completed":
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

        run = run_pi_prompt(
            prompt,
            workdir,
            provider=state["provider"],
            model=state["model"],
            thinking=effective_thinking,
        )
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
    parser = argparse.ArgumentParser(description="Run a light Pi task004 loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/pi_json_loop_task004_state")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--thinking", default=None)
    args = parser.parse_args()
    result = run_loop(
        REPO_ROOT / args.workdir,
        provider=args.provider,
        model=args.model,
        thinking=args.thinking,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
