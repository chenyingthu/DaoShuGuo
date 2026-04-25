#!/usr/bin/env python3
"""Run a task004 skill-evolution loop with explicit parameter changes."""

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

from scripts.pi_runtime import get_default_pi_profile, run_pi_prompt
from scripts.run_pi_task003_loop import write_json


PI_PROFILE = get_default_pi_profile()

ROUND_STEPS = [
    "task_trial_step",
    "boundary_judgment_step",
    "effectiveness_status_step",
    "iteration_review_step",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def state_paths(workdir: Path) -> tuple[Path, Path]:
    state_dir = workdir / "state"
    return state_dir / "skill_evolution_state.json", state_dir / "iterations"


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    write_json(state_path, state)


def load_state(state_path: Path, iterations: int) -> dict[str, Any]:
    if state_path.exists():
        return load_json(state_path)
    return {
        "task_ref": "task.power.ieee69_hosting_capacity",
        "provider": PI_PROFILE["provider"],
        "model": PI_PROFILE["model"],
        "planned_iterations": iterations,
        "current_iteration": 1,
        "iterations": {},
    }


def iteration_dir(base: Path, iteration: int) -> Path:
    return base / f"iter_{iteration:03d}"


def read_run_metrics(run_dir: str) -> dict[str, Any]:
    payload = load_json(Path(run_dir) / "metrics.json")
    return {
        "baseline_metrics": payload["baseline_solution"]["metrics"],
        "candidate_metrics": payload["candidate_solution"]["metrics"],
        "evaluation": payload["evaluation"],
    }


def planned_q_step(iteration: int) -> float:
    schedule = {1: 0.10, 2: 0.20, 3: 0.30, 4: 0.35}
    return schedule.get(iteration, 0.35)


def generate_iteration_request(iteration: int, state: dict[str, Any]) -> dict[str, Any]:
    task_ref = state["task_ref"]
    q_step = planned_q_step(iteration)
    if iteration == 1:
        rationale = "Start from the current default inverter-support step to establish the initial skill candidate."
    else:
        prior = state["iterations"][f"iter_{iteration - 1:03d}"]
        prior_q = prior["request"]["candidate_q_step_mvar"]
        rationale = (
            f"Increase candidate_q_step_mvar from {prior_q:.2f} to {q_step:.2f} and test whether the same skill becomes stronger."
        )
    return {
        "iteration": iteration,
        "task_ref": task_ref,
        "strategy": "inverter-support",
        "candidate_q_step_mvar": q_step,
        "rationale": rationale,
    }


def prompt_for_step(step: str, request: dict[str, Any]) -> str:
    task_ref = request["task_ref"]
    iteration = request["iteration"]
    q_step = request["candidate_q_step_mvar"]
    if step == "task_trial_step":
        return (
            "Use run_task004_trial with "
            "strategy inverter-support, "
            f"candidate_q_step_mvar {q_step}, "
            f"repo_root {REPO_ROOT}. "
            f"This is iteration {iteration}. Rationale: {request['rationale']}"
        )
    if step == "boundary_judgment_step":
        trial = request["trial_extracted"]
        return (
            "Use record_boundary_judgment with "
            f"task_ref {task_ref}, "
            f"run_ref {trial['runRef']}, "
            "boundary_statement 'This run still only supports a control-strategy-conditioned static hosting-capacity boundary observation under the present scan envelope.', "
            "claim_ceiling 'Do not claim paper-level hosting-capacity improvement unless hosting-capacity level itself increases.', "
            "boundary_type control_strategy_conditioned_static_capacity"
        )
    if step == "effectiveness_status_step":
        return (
            "Use record_effectiveness_status with "
            f"task_ref {task_ref}, "
            "readiness_level internal_report_ready, "
            "supported_output internal_report_ready, "
            "missing_for_next_level 'Need actual hosting-capacity boundary improvement, broader scan envelope, and stronger external benchmark'"
        )
    if step == "iteration_review_step":
        return (
            "Use record_iteration_review with "
            f"task_ref {task_ref}, "
            f"iteration {iteration}, "
            "verdict real_progress, "
            f"and summary 'Iteration {iteration} changed candidate_q_step_mvar to {q_step:.2f} and checked whether the same skill improved.'"
        )
    raise RuntimeError(step)


def extract_from_events(step: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for event in events:
        if event.get("type") == "tool_execution_end":
            result = event.get("result", {})
            details = result.get("details", {})
            if step == "task_trial_step":
                for key in ("runDir", "runRef", "reportRef", "strategy", "repo_root", "candidate_q_step_mvar"):
                    if key in details:
                        extracted[key] = details[key]
            else:
                extracted["toolName"] = event.get("toolName")
                extracted["details"] = details
    return extracted


def is_step_complete(step: str, payload: dict[str, Any]) -> bool:
    if payload.get("status") != "completed":
        return False
    extracted = payload.get("extracted", {})
    if step == "task_trial_step":
        return bool(extracted.get("runDir") and extracted.get("runRef"))
    return bool(extracted.get("toolName"))


def analyze_iteration(request: dict[str, Any], result: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    trial = result["steps"]["task_trial_step"]["extracted"]
    payload = read_run_metrics(trial["runDir"])
    baseline = payload["baseline_metrics"]
    candidate = payload["candidate_metrics"]
    evaluation = payload["evaluation"]
    analysis = {
        "iteration": request["iteration"],
        "run_ref": trial["runRef"],
        "candidate_q_step_mvar": request["candidate_q_step_mvar"],
        "hosting_capacity_improved_vs_baseline": candidate["hosting_capacity_level"] > baseline["hosting_capacity_level"],
        "loss_improved_vs_baseline": candidate["loss_at_boundary"] < baseline["loss_at_boundary"],
        "voltage_margin_improved_vs_baseline": candidate["voltage_margin"] > baseline["voltage_margin"],
        "candidate_hosting_capacity_level": candidate["hosting_capacity_level"],
        "candidate_loss_at_boundary": candidate["loss_at_boundary"],
        "candidate_voltage_margin": candidate["voltage_margin"],
        "baseline_hosting_capacity_level": baseline["hosting_capacity_level"],
        "run_passed": evaluation.get("passed", False),
        "evaluation_summary": evaluation.get("summary", ""),
    }
    if prior is None:
        analysis["delta_vs_prior"] = None
        analysis["progress_type"] = "initial_skill_candidate"
        analysis["improvement_judgment"] = "Initial skill candidate established."
        return analysis

    prior_analysis = prior["round_analysis"]
    analysis["delta_vs_prior"] = {
        "candidate_q_step_mvar": request["candidate_q_step_mvar"] - prior_analysis["candidate_q_step_mvar"],
        "hosting_capacity_level": candidate["hosting_capacity_level"] - prior_analysis["candidate_hosting_capacity_level"],
        "loss_at_boundary": candidate["loss_at_boundary"] - prior_analysis["candidate_loss_at_boundary"],
        "voltage_margin": candidate["voltage_margin"] - prior_analysis["candidate_voltage_margin"],
    }
    if candidate["hosting_capacity_level"] > prior_analysis["candidate_hosting_capacity_level"]:
        analysis["progress_type"] = "skill_improved"
        analysis["improvement_judgment"] = "This round improved hosting-capacity boundary relative to the prior skill candidate."
    elif candidate["hosting_capacity_level"] == prior_analysis["candidate_hosting_capacity_level"]:
        analysis["progress_type"] = "parameter_change_no_boundary_gain"
        analysis["improvement_judgment"] = "This round changed the skill parameter but still did not improve hosting-capacity boundary."
    else:
        analysis["progress_type"] = "skill_regressed"
        analysis["improvement_judgment"] = "This round changed the skill parameter and made hosting-capacity boundary worse."
    return analysis


def run_iteration(workdir: Path, iterdir: Path, request: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    results: dict[str, Any] = {}
    write_json(iterdir / "request.json", request)
    for step in ROUND_STEPS:
        prompt = prompt_for_step(step, request)
        run = run_pi_prompt(
            prompt,
            workdir,
            provider=PI_PROFILE["provider"],
            model=PI_PROFILE["model"],
            thinking=PI_PROFILE["thinking"],
        )
        extracted = extract_from_events(step, run["events"])
        if step == "task_trial_step":
            request["trial_extracted"] = extracted
        payload = {
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
        write_json(iterdir / f"{step}.json", payload)
        results[step] = payload
        if not is_step_complete(step, payload):
            break
    iteration_payload = {"request": request, "steps": results}
    iteration_payload["round_analysis"] = analyze_iteration(request, iteration_payload, prior)
    write_json(iterdir / "round_analysis.json", iteration_payload["round_analysis"])
    return iteration_payload


def build_review(state: dict[str, Any], base: Path) -> None:
    ordered = [state["iterations"][key] for key in sorted(state["iterations"].keys())]
    review = {
        "task_ref": state["task_ref"],
        "provider": state["provider"],
        "model": state["model"],
        "round_count": len(ordered),
        "rounds": [
            {
                "iteration": item["request"]["iteration"],
                "candidate_q_step_mvar": item["request"]["candidate_q_step_mvar"],
                "run_ref": item["round_analysis"]["run_ref"],
                "progress_type": item["round_analysis"]["progress_type"],
                "improvement_judgment": item["round_analysis"]["improvement_judgment"],
            }
            for item in ordered
        ],
    }
    write_json(base / "skill_evolution_review.json", review)


def run_loop(workdir: Path, iterations: int) -> dict[str, Any]:
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
    build_review(state, iterations_root)
    return {
        "workdir": str(workdir),
        "state_path": str(state_path),
        "iterations": state["iterations"],
        "review_path": str(iterations_root / "skill_evolution_review.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a task004 skill-evolution loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/pi_json_loop_task004_skill_evolution")
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()
    result = run_loop(REPO_ROOT / args.workdir, args.iterations)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
