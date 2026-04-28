#!/usr/bin/env python3
"""Run a multi-round short-turn Pi task003 loop."""

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

from scripts.pi_runtime import get_default_pi_profile
from scripts.run_pi_task003_loop import run_pi_prompt, write_json

PI_PROFILE = get_default_pi_profile()

ROUND_STEPS = [
    "task_trial_step",
    "skill_record_step",
    "cognition_constraint_step",
    "iteration_review_step",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def state_paths(workdir: Path) -> tuple[Path, Path]:
    state_dir = workdir / "state"
    return state_dir / "multiround_state.json", state_dir / "iterations"


def load_state(state_path: Path, iterations: int) -> dict[str, Any]:
    if state_path.exists():
        return load_json(state_path)
    return {
        "task_ref": "task.power.ieee69_renewable_reactive_opt",
        "provider": PI_PROFILE["provider"],
        "model": PI_PROFILE["model"],
        "planned_iterations": iterations,
        "current_iteration": 1,
        "iterations": {},
    }


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    write_json(state_path, state)


def iteration_dir(base: Path, iteration: int) -> Path:
    return base / f"iter_{iteration:03d}"


def generate_iteration_request(iteration: int, state: dict[str, Any]) -> dict[str, Any]:
    task_ref = state["task_ref"]
    if iteration == 1:
        return {
            "iteration": 1,
            "task_ref": task_ref,
            "strategy": "inverter-support",
            "rationale": "Start from the renewable-aware effective path.",
            "blocked_paths": ["pure_weak_shunt_substitution"],
            "required_test": "Establish the bounded effective baseline path under the current evaluator.",
        }

    prev = state["iterations"][f"iter_{iteration - 1:03d}"]
    prev_request = prev["request"]
    prev_trial = prev["steps"]["task_trial_step"]["extracted"]
    prev_constraint = prev["steps"]["cognition_constraint_step"]["extracted"]["details"]
    prev_strategy = prev_request["strategy"]

    if prev_strategy == "inverter-support" and "matched comparison" in prev_constraint.get("constraint", "").lower():
        return {
            "iteration": iteration,
            "task_ref": task_ref,
            "strategy": "inverter-underperformer",
            "rationale": "Run a semantically matched renewable-aware alternative under the same evaluator.",
            "blocked_paths": ["pure_weak_shunt_substitution"],
            "required_test": f"Compare against {prev_trial['runRef']} as the effective renewable-aware baseline path.",
        }

    return {
        "iteration": iteration,
        "task_ref": task_ref,
        "strategy": "inverter-support",
        "rationale": "Return to the effective renewable-aware path after the matched underperformer comparison.",
        "blocked_paths": ["pure_weak_shunt_substitution"],
        "required_test": "Contrast performance failure against the bounded effective path without changing task semantics.",
    }


def prompt_for_step(step: str, request: dict[str, Any], prior: dict[str, Any] | None) -> str:
    task_ref = request["task_ref"]
    iteration = request["iteration"]
    strategy = request["strategy"]
    if step == "task_trial_step":
        return (
            f"Use run_task003_trial with strategy {strategy} and repo_root {REPO_ROOT}. "
            f"This is iteration {iteration}. Rationale: {request['rationale']}"
        )

    if step == "skill_record_step":
        prior_trial = prior["steps"]["task_trial_step"]["extracted"] if prior else None
        if strategy == "inverter-underperformer":
            next_constraint = "Do not discard semantically aligned underperformer; separate semantic alignment from performance failure."
            outcome = "failure"
        else:
            next_constraint = "Maintain bounded renewable-aware success path while preparing matched comparison."
            outcome = "success"
        current_trial = request["trial_extracted"]
        return (
            "Use record_skill_trial with "
            f"task_ref {task_ref}, "
            f"skill_ref skill.power.renewable_{'inverter_underperformer' if strategy == 'inverter-underperformer' else 'inverter_reactive_optimizer'}_task003, "
            f"run_ref {current_trial['runRef']}, "
            f"outcome {outcome}, "
            f"evidence_path {current_trial['runDir']}/run.yaml, "
            f"and next_constraint '{next_constraint}'"
        )

    if step == "cognition_constraint_step":
        current_trial = request["trial_extracted"]
        if strategy == "inverter-underperformer":
            compare_against = prior["steps"]["task_trial_step"]["extracted"]["runRef"]
            return (
                "Use record_cognition_constraint with "
                f"task_ref {task_ref}, "
                f"source_run_ref {current_trial['runRef']}, "
                "constraint 'Keep semantically aligned renewable-aware alternatives in scope even when they fail on performance; require direct comparison against the successful renewable-aware baseline.', "
                "blocked_path pure_weak_shunt_substitution, "
                f"and required_test 'Compare {current_trial['runRef']} against {compare_against} under the same evaluator.'"
            )
        return (
            "Use record_cognition_constraint with "
            f"task_ref {task_ref}, "
            f"source_run_ref {current_trial['runRef']}, "
            "constraint 'Keep renewable-aware control and require a matched comparison before broader claims.', "
            "blocked_path pure_weak_shunt_substitution, "
            "and required_test 'Compare against a semantically matched renewable-aware variant under the same evaluator.'"
        )

    if step == "iteration_review_step":
        verdict = "real_progress"
        if strategy == "inverter-underperformer":
            summary = "Iteration 2 captured a semantically matched renewable-aware underperformer to sharpen the cognition boundary."
        else:
            summary = f"Iteration {iteration} executed a bounded renewable-aware task003 trial and wrote loop artifacts."
        return (
            "Use record_iteration_review with "
            f"task_ref {task_ref}, "
            f"iteration {iteration}, "
            f"verdict {verdict}, "
            f"and summary '{summary}'"
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


def run_iteration(workdir: Path, iterdir: Path, request: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    results: dict[str, Any] = {}
    write_json(iterdir / "request.json", request)
    for step in ROUND_STEPS:
        prompt = prompt_for_step(step, request, prior)
        run = run_pi_prompt(prompt, workdir)
        extracted = extract_from_events(step, run["events"])
        if step == "task_trial_step":
            request["trial_extracted"] = extracted
        result_payload = {
            "step": step,
            "status": "completed" if run["exit_code"] == 0 else "failed",
            "started_at": utc_now(),
            "finished_at": utc_now(),
            "provider": PI_PROFILE["provider"],
            "model": PI_PROFILE["model"],
            "prompt": prompt,
            "exit_code": run["exit_code"],
            "stderr": run["stderr"],
            "stdout_excerpt": run["stdout"][:8000],
            "extracted": extracted,
        }
        write_json(iterdir / f"{step}.json", result_payload)
        results[step] = result_payload
        if run["exit_code"] != 0:
            break
    return {"request": request, "steps": results}


def build_comparison(state: dict[str, Any], base: Path) -> None:
    iterations = state["iterations"]
    if len(iterations) < 2:
        return
    first = iterations["iter_001"]
    second = iterations["iter_002"]
    comparison = {
        "iteration_1_strategy": first["request"]["strategy"],
        "iteration_1_run_ref": first["steps"]["task_trial_step"]["extracted"]["runRef"],
        "iteration_2_strategy": second["request"]["strategy"],
        "iteration_2_run_ref": second["steps"]["task_trial_step"]["extracted"]["runRef"],
        "driver": second["request"]["rationale"],
        "constraint_source": first["steps"]["cognition_constraint_step"]["extracted"]["details"],
    }
    write_json(base / "comparison_review.json", comparison)


def run_multiround(workdir: Path, iterations: int) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    state_path, iterations_root = state_paths(workdir)
    iterations_root.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path, iterations)
    state["planned_iterations"] = iterations

    prior: dict[str, Any] | None = None
    for iteration in range(1, iterations + 1):
        key = f"iter_{iteration:03d}"
        if key in state["iterations"]:
            prior = state["iterations"][key]
            continue
        request = generate_iteration_request(iteration, state)
        result = run_iteration(workdir, iteration_dir(iterations_root, iteration), request, prior)
        state["iterations"][key] = result
        state["current_iteration"] = iteration
        save_state(state_path, state)
        prior = result
    build_comparison(state, iterations_root)
    return {
        "workdir": str(workdir),
        "state_path": str(state_path),
        "iterations": state["iterations"],
        "comparison_review": str(iterations_root / "comparison_review.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a multi-round short-turn Pi task003 loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/pi_json_loop_task003_multiround")
    parser.add_argument("--iterations", type=int, default=2)
    args = parser.parse_args()
    result = run_multiround(REPO_ROOT / args.workdir, args.iterations)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
