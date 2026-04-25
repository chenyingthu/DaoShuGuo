#!/usr/bin/env python3
"""Run a multi-round Pi task004 loop with explicit round-to-round change analysis."""

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
    return state_dir / "multiround_state.json", state_dir / "iterations"


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


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    write_json(state_path, state)


def iteration_dir(base: Path, iteration: int) -> Path:
    return base / f"iter_{iteration:03d}"


def read_run_metrics(run_dir: str) -> dict[str, Any]:
    metrics_path = Path(run_dir) / "metrics.json"
    payload = load_json(metrics_path)
    candidate_metrics = payload["candidate_solution"]["metrics"]
    baseline_metrics = payload["baseline_solution"]["metrics"]
    evaluation = payload["evaluation"]
    return {
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "evaluation_summary": evaluation.get("summary", ""),
        "passed": evaluation.get("passed", False),
    }


def generate_iteration_request(iteration: int, state: dict[str, Any]) -> dict[str, Any]:
    task_ref = state["task_ref"]
    if iteration == 1:
        return {
            "iteration": 1,
            "task_ref": task_ref,
            "strategy": "inverter-support",
            "rationale": "Establish the bounded inverter-support hosting-capacity baseline candidate under the current scan envelope.",
            "expected_gain": "Check whether the candidate improves hosting-capacity boundary first, then secondary boundary metrics.",
        }

    prev = state["iterations"][f"iter_{iteration - 1:03d}"]
    prev_request = prev["request"]
    prev_analysis = prev.get("round_analysis", {})
    prev_trial = prev["steps"]["task_trial_step"]["extracted"]
    prev_strategy = prev_request["strategy"]

    if prev_strategy == "inverter-support" and prev_analysis.get("hosting_capacity_improved") is False:
        return {
            "iteration": iteration,
            "task_ref": task_ref,
            "strategy": "single-point-mismatch",
            "rationale": (
                "Force a known mismatch lane to confirm that single-point operating-point evidence cannot replace hosting-capacity boundary evidence."
            ),
            "expected_gain": "Deepen boundary cognition, not improve task performance.",
            "compare_against": prev_trial["runRef"],
        }

    return {
        "iteration": iteration,
        "task_ref": task_ref,
        "strategy": "inverter-support",
        "rationale": (
            "Return to the bounded inverter-support lane after the mismatch contrast to see whether the system can recover task alignment."
        ),
        "expected_gain": "Recover semantic alignment while preserving the strengthened claim ceiling.",
        "compare_against": prev_trial["runRef"],
    }


def prompt_for_step(step: str, request: dict[str, Any], prior: dict[str, Any] | None) -> str:
    task_ref = request["task_ref"]
    iteration = request["iteration"]
    strategy = request["strategy"]
    if step == "task_trial_step":
        return (
            f"Use run_task004_trial with strategy {strategy} and repo_root {REPO_ROOT}. "
            f"This is iteration {iteration}. Rationale: {request['rationale']}"
        )

    if step == "boundary_judgment_step":
        trial = request["trial_extracted"]
        if strategy == "single-point-mismatch":
            return (
                "Use record_boundary_judgment with "
                f"task_ref {task_ref}, "
                f"run_ref {trial['runRef']}, "
                "boundary_statement 'This run is a single-point mismatch probe and cannot be used as hosting-capacity boundary evidence.', "
                "claim_ceiling 'Do not compare this directly to hosting-capacity scan conclusions except as a task-mismatch or semantic-contrast artifact.', "
                "boundary_type task_mismatch_single_point_non_boundary"
            )
        return (
            "Use record_boundary_judgment with "
            f"task_ref {task_ref}, "
            f"run_ref {trial['runRef']}, "
            "boundary_statement 'The current result only supports a control-strategy-conditioned static hosting-capacity boundary observation under the present scan envelope.', "
            "claim_ceiling 'Do not describe this as intrinsic system hosting capacity or a paper-level hosting-capacity conclusion.', "
            "boundary_type control_strategy_conditioned_static_capacity"
        )

    if step == "effectiveness_status_step":
        if strategy == "single-point-mismatch":
            return (
                "Use record_effectiveness_status with "
                f"task_ref {task_ref}, "
                "readiness_level boundary_failure_material, "
                "supported_output boundary_failure_material, "
                "missing_for_next_level 'Return to hosting-capacity scan lane; recover boundary-valid evidence before discussing deliverable upgrade'"
            )
        return (
            "Use record_effectiveness_status with "
            f"task_ref {task_ref}, "
            "readiness_level internal_report_ready, "
            "supported_output internal_report_ready, "
            "missing_for_next_level 'multi-scenario hosting capacity, actual boundary-triggering envelope, stronger external benchmark'"
        )

    if step == "iteration_review_step":
        if prior is None:
            summary = "Iteration 1 established the initial bounded task004 hosting-capacity boundary sample."
        elif strategy == "single-point-mismatch":
            summary = "Iteration 2 did not improve task performance, but it deepened cognition by proving the non-substitutability of single-point evidence."
        else:
            summary = "This iteration returned to the hosting-capacity scan lane after the mismatch contrast."
        return (
            "Use record_iteration_review with "
            f"task_ref {task_ref}, "
            f"iteration {iteration}, "
            "verdict real_progress, "
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


def is_step_complete(step: str, result_payload: dict[str, Any]) -> bool:
    if result_payload.get("status") != "completed":
        return False
    extracted = result_payload.get("extracted", {})
    if step == "task_trial_step":
        return bool(extracted.get("runDir") and extracted.get("runRef"))
    return bool(extracted.get("toolName"))


def analyze_iteration(
    request: dict[str, Any],
    result: dict[str, Any],
    prior: dict[str, Any] | None,
) -> dict[str, Any]:
    trial = result["steps"]["task_trial_step"]["extracted"]
    metrics = read_run_metrics(trial["runDir"])
    candidate = metrics["candidate_metrics"]
    baseline = metrics["baseline_metrics"]
    analysis = {
        "iteration": request["iteration"],
        "strategy": request["strategy"],
        "run_ref": trial["runRef"],
        "hosting_capacity_improved": candidate["hosting_capacity_level"] > baseline["hosting_capacity_level"],
        "loss_improved_vs_baseline": candidate["loss_at_boundary"] < baseline["loss_at_boundary"],
        "voltage_margin_improved_vs_baseline": candidate["voltage_margin"] > baseline["voltage_margin"],
        "baseline_hosting_capacity_level": baseline["hosting_capacity_level"],
        "candidate_hosting_capacity_level": candidate["hosting_capacity_level"],
        "baseline_loss_at_boundary": baseline["loss_at_boundary"],
        "candidate_loss_at_boundary": candidate["loss_at_boundary"],
        "baseline_voltage_margin": baseline["voltage_margin"],
        "candidate_voltage_margin": candidate["voltage_margin"],
        "run_passed": metrics["passed"],
        "evaluation_summary": metrics["evaluation_summary"],
    }
    if prior is None:
        analysis["delta_vs_prior"] = None
        analysis["progress_type"] = (
            "skill_improvement"
            if analysis["hosting_capacity_improved"]
            else "bounded_baseline_established"
        )
        analysis["improvement_judgment"] = (
            "No hosting-capacity improvement yet; this round only establishes the initial bounded sample."
        )
        return analysis

    prior_analysis = prior["round_analysis"]
    analysis["delta_vs_prior"] = {
        "hosting_capacity_level": candidate["hosting_capacity_level"] - prior_analysis["candidate_hosting_capacity_level"],
        "loss_at_boundary": candidate["loss_at_boundary"] - prior_analysis["candidate_loss_at_boundary"],
        "voltage_margin": candidate["voltage_margin"] - prior_analysis["candidate_voltage_margin"],
    }
    if request["strategy"] == "single-point-mismatch":
        analysis["progress_type"] = "cognition_deepened"
        analysis["improvement_judgment"] = (
            "Task performance did not improve; cognition improved because this round proved a boundary-invalid evidence lane."
        )
    elif analysis["hosting_capacity_improved"]:
        analysis["progress_type"] = "skill_improvement"
        analysis["improvement_judgment"] = (
            "This round improved hosting-capacity boundary relative to the prior candidate."
        )
    else:
        analysis["progress_type"] = "no_skill_improvement"
        analysis["improvement_judgment"] = (
            "This round did not improve hosting-capacity boundary relative to the prior candidate."
        )
    return analysis


def build_multiround_review(state: dict[str, Any], base: Path) -> None:
    iterations = state["iterations"]
    ordered = [iterations[key] for key in sorted(iterations.keys())]
    review = {
        "task_ref": state["task_ref"],
        "provider": state["provider"],
        "model": state["model"],
        "round_count": len(ordered),
        "rounds": [
            {
                "iteration": item["request"]["iteration"],
                "strategy": item["request"]["strategy"],
                "run_ref": item["round_analysis"]["run_ref"],
                "progress_type": item["round_analysis"]["progress_type"],
                "improvement_judgment": item["round_analysis"]["improvement_judgment"],
            }
            for item in ordered
        ],
        "overall_conclusion": (
            "The loop produced cognition deepening but did not produce hosting-capacity boundary improvement."
            if any(item["round_analysis"]["progress_type"] == "cognition_deepened" for item in ordered)
            and not any(item["round_analysis"]["progress_type"] == "skill_improvement" for item in ordered)
            else "The loop produced at least one genuine skill improvement."
        ),
    }
    write_json(base / "multiround_review.json", review)


def run_iteration(workdir: Path, iterdir: Path, request: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    results: dict[str, Any] = {}
    write_json(iterdir / "request.json", request)
    for step in ROUND_STEPS:
        prompt = prompt_for_step(step, request, prior)
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
        if not is_step_complete(step, result_payload):
            break
    payload = {"request": request, "steps": results}
    payload["round_analysis"] = analyze_iteration(request, payload, prior) if is_step_complete("task_trial_step", results["task_trial_step"]) else {}
    write_json(iterdir / "round_analysis.json", payload["round_analysis"])
    return payload


def run_multiround(workdir: Path, iterations: int) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    state_path, iterations_root = state_paths(workdir)
    iterations_root.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path, iterations)
    state["planned_iterations"] = iterations
    state["provider"] = PI_PROFILE["provider"]
    state["model"] = PI_PROFILE["model"]

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
    build_multiround_review(state, iterations_root)
    return {
        "workdir": str(workdir),
        "state_path": str(state_path),
        "iterations": state["iterations"],
        "multiround_review": str(iterations_root / "multiround_review.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a multi-round Pi task004 loop.")
    parser.add_argument("--workdir", default="analysis/pi_harness/pi_json_loop_task004_multiround")
    parser.add_argument("--iterations", type=int, default=2)
    args = parser.parse_args()
    result = run_multiround(REPO_ROOT / args.workdir, args.iterations)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
