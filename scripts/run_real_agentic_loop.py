#!/usr/bin/env python3
"""Run a real two-iteration agentic skill-cognition loop for task003."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SKILL_REQUESTS_DIR = REPO_ROOT / "agents" / "skill" / "requests"
SKILL_RESULTS_DIR = REPO_ROOT / "agents" / "skill" / "results"
AGENTIC_LOOP_DIR = REPO_ROOT / "analysis" / "agentic_loop" / "task003"
WORKFLOW_OUTPUT_DIR = REPO_ROOT / "agents" / "cognition" / "workflow_outputs"

TASK_REF = "task.power.ieee69_renewable_reactive_opt"
BASE_SKILL_REF = "skill.power.renewable_inverter_reactive_optimizer_task003"
BASE_SKILL_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_inverter_reactive_optimizer_task003.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def latest_yaml(path: Path) -> Path:
    files = sorted(path.glob("*.yaml"))
    if not files:
        raise RuntimeError(f"no yaml files in {path}")
    return files[-1]


def next_iteration_index() -> int:
    reviews_dir = AGENTIC_LOOP_DIR / "reviews"
    files = sorted(reviews_dir.glob("*.yaml"))
    return len(files) + 1


def output_skill_path(iteration: int) -> Path:
    return REPO_ROOT / "skills" / "active_dev" / f"renewable_inverter_reactive_optimizer_task003_iter{iteration:02d}.py"


def skill_ref_for_iteration(iteration: int) -> str:
    return f"skill.power.renewable_inverter_reactive_optimizer_task003_iter{iteration:02d}"


def build_request(iteration: int, source_update_ref: str | None, blocked_paths: list[str], priorities: list[str], tests: list[str]) -> Path:
    path = SKILL_REQUESTS_DIR / f"task003_iter{iteration:02d}.yaml"
    if path.exists():
        existing = load_yaml(path)
        tests_text = " ".join(existing.get("required_tests", []))
        looks_executable = (
            len(existing.get("required_tests", [])) <= 6
            and len(existing.get("summary", "")) <= 800
            and "time-series" not in tests_text.lower()
            and "formal evaluator semantics" not in tests_text.lower()
            and "claim" not in tests_text.lower()
        )
        if looks_executable:
            return path
    now = utc_now()
    payload = {
        "schema_version": "0.1.0",
        "object_type": "skill_agent_iteration_request",
        "object_id": f"skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.{iteration:04d}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {"task_package": "task003", "execution_mode": "real_codex_agent"},
        "task_ref": TASK_REF,
        "source_update_ref": source_update_ref,
        "iteration_index": iteration,
        "base_skill_ref": BASE_SKILL_REF if iteration == 1 else skill_ref_for_iteration(iteration - 1),
        "allowed_change_scope": [
            "candidate_inverter_grid search logic",
            "coordination between inverter_q and weak-bus shunts",
            "selection logic over evaluated candidates",
        ],
        "blocked_paths": blocked_paths,
        "required_tests": tests,
        "output_skill_path": str(output_skill_path(iteration).relative_to(REPO_ROOT)),
        "summary": "; ".join(priorities),
    }
    write_yaml(path, payload)
    return path


def build_codex_prompt(request: dict[str, Any], iteration: int) -> str:
    base_path = BASE_SKILL_PATH if iteration == 1 else output_skill_path(iteration - 1)
    base_code = base_path.read_text(encoding="utf-8")
    runtime_helpers = (REPO_ROOT / "tasks" / "task003" / "runtime_helpers.py").read_text(encoding="utf-8")
    evaluator = (REPO_ROOT / "evaluators" / "task003_evaluator.py").read_text(encoding="utf-8")
    return "\n".join(
        [
            "You are the skill agent for a bounded task003 iteration.",
            "Modify or create exactly one new candidate skill file.",
            "Do not edit evaluator, task definitions, cognition files, or unrelated modules.",
            "Return a short summary as plain text after edits.",
            "",
            "## Request",
            yaml.safe_dump(request, sort_keys=False, allow_unicode=True),
            "## Base Skill",
            f"Path: {base_path.relative_to(REPO_ROOT)}",
            "```python",
            base_code,
            "```",
            "## Runtime Helpers",
            "```python",
            runtime_helpers[:5000],
            "```",
            "## Evaluator",
            "```python",
            evaluator[:4000],
            "```",
            "## Hard Constraints",
            "- Preserve renewable-aware control family.",
            "- Prefer adding explicit shunt + inverter coordination or better candidate ranking.",
            "- Keep file importable as a Python module with a `solve(network_model, constraint_set)` function.",
            f"- Write output only to {request['output_skill_path']}.",
        ]
    )


def run_codex_skill_agent(request_path: Path, iteration: int) -> Path:
    request = load_yaml(request_path)
    SKILL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = SKILL_RESULTS_DIR / f"task003_iter{iteration:02d}.raw.txt"
    prompt_path = SKILL_RESULTS_DIR / f"task003_iter{iteration:02d}.prompt.md"
    result_path = SKILL_RESULTS_DIR / f"task003_iter{iteration:02d}.yaml"
    output_path = output_skill_path(iteration)
    if result_path.exists() and output_path.exists():
        return result_path
    prompt = build_codex_prompt(request, iteration)
    prompt_path.write_text(prompt, encoding="utf-8")
    command = [
        "codex",
        "exec",
        "--full-auto",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--cd",
        str(REPO_ROOT),
        "-o",
        str(raw_path),
        "-",
    ]
    result = subprocess.run(command, input=prompt, cwd=REPO_ROOT, text=True, capture_output=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"codex skill agent failed: {result.stderr or result.stdout}")
    now = utc_now()
    if not output_path.exists():
        raise RuntimeError(f"skill agent did not create expected file: {output_path}")
    summary_lines = [line.strip() for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()][:8]
    result_payload = {
        "schema_version": "0.1.0",
        "object_type": "skill_agent_iteration_result",
        "object_id": f"skill_agent_iteration_result.power.ieee69_renewable_reactive_opt.{iteration:04d}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "completed",
        "metadata": {"task_package": "task003", "executor": "codex_exec"},
        "task_ref": TASK_REF,
        "request_ref": request["object_id"],
        "produced_skill_ref": skill_ref_for_iteration(iteration),
        "code_paths": [str(output_path.relative_to(REPO_ROOT))],
        "change_summary": summary_lines or [f"generated {output_path.name}"],
        "self_reported_risks": ["agent output may still overfit to current representative snapshot"],
        "expected_behavior_change": [
            "candidate search should differ from previous iteration",
            "renewable-aware control family should remain intact",
        ],
        "command": " ".join(command[:-1]) + " <prompt>",
        "raw_output_path": str(raw_path.relative_to(REPO_ROOT)),
    }
    write_yaml(result_path, result_payload)
    materialize_skill_asset(iteration, result_payload)
    return result_path


def materialize_skill_asset(iteration: int, result_payload: dict[str, Any]) -> Path:
    import orchestrator.main as orch

    skill_id = result_payload["produced_skill_ref"]
    skill_path = output_skill_path(iteration)
    asset_path = REPO_ROOT / "skills" / "active_dev" / f"{skill_id.split('.')[-1]}.yaml"
    now = utc_now()
    payload = {
        "schema_version": "0.1.0",
        "object_type": "skill",
        "object_id": skill_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "draft",
        "metadata": {"task_package": "task003", "origin": "real_codex_skill_agent"},
        "name": f"Renewable Inverter Reactive Optimizer Task003 Iteration {iteration:02d}",
        "title": f"task003 agentic iteration {iteration:02d} renewable-aware candidate",
        "capability_statement": "在 task003 的新能源感知控制空间内，生成受认知约束驱动的候选无功支撑策略。",
        "input_contract": {"required_inputs": ["network_model", "constraint_set"]},
        "output_contract": {
            "outputs": ["reactive_power_settings", "control_settings", "solver_status"]
        },
        "applicability": {
            "domain": "power",
            "scenarios": ["ieee69_renewable_reactive_opt"],
            "limits": ["single_representative_snapshot", "agentic_iteration_candidate"],
        },
        "implementation_ref": {
            "type": "python_module",
            "path": str(skill_path.relative_to(REPO_ROOT)),
        },
        "origin_run_refs": [f"run.power.ieee69_renewable_reactive_opt.{iteration + 4:04d}"],
        "failure_conditions": ["may overfit to current representative renewable snapshot"],
        "maturity_level": "candidate",
        "usage_notes": "Generated by the real agentic loop; bounded by task003 single-snapshot scope.",
    }
    write_yaml(asset_path, payload)

    registry = orch.load_json(orch.SKILL_REGISTRY_PATH)
    skills = registry.setdefault("skills", [])
    for entry in skills:
        if entry.get("object_id") == skill_id and entry.get("object_version") == "0.1.0":
            entry["path"] = str(asset_path.relative_to(REPO_ROOT))
            entry["status"] = "draft"
            entry["last_seen_at"] = now
            break
    else:
        skills.append(
            {
                "object_id": skill_id,
                "object_version": "0.1.0",
                "path": str(asset_path.relative_to(REPO_ROOT)),
                "status": "draft",
                "last_seen_at": now,
            }
        )
    registry["generated_at"] = now
    orch.write_json(orch.SKILL_REGISTRY_PATH, registry)
    return asset_path


def run_real_task003_with_skill(skill_path: Path, skill_ref: str, iteration: int) -> tuple[Path, dict[str, Any]]:
    import orchestrator.main as orch

    original_solver = orch.TASK003_RENEWABLE_SOLVER_PATH
    try:
        orch.TASK003_RENEWABLE_SOLVER_PATH = skill_path
        run_dir = orch.run_real_task003("inverter-support")
    finally:
        orch.TASK003_RENEWABLE_SOLVER_PATH = original_solver

    run_obj = load_yaml(run_dir / "run.yaml")
    run_obj["skill_refs"]["produced"] = [{"object_id": skill_ref, "object_version": "0.1.0"}]
    write_yaml(run_dir / "run.yaml", run_obj)
    return run_dir, run_obj


def workflow_command() -> str:
    return (
        "codex exec --full-auto --sandbox workspace-write --skip-git-repo-check "
        f"--cd {REPO_ROOT} -"
    )


def build_agentic_update(iteration: int, request: dict[str, Any], result: dict[str, Any], run_obj: dict[str, Any], workflow_refs: list[str]) -> Path:
    path = AGENTIC_LOOP_DIR / "updates" / f"iter{iteration:02d}.yaml"
    if path.exists():
        return path
    source_event = load_yaml(latest_yaml(REPO_ROOT / "analysis" / "loop" / "task003" / "events"))
    proposer = json.loads((WORKFLOW_OUTPUT_DIR / workflow_refs[0]).read_text(encoding="utf-8"))
    counter = json.loads((WORKFLOW_OUTPUT_DIR / workflow_refs[1]).read_text(encoding="utf-8"))
    adjudicator = json.loads((WORKFLOW_OUTPUT_DIR / workflow_refs[2]).read_text(encoding="utf-8"))

    def merge_lines(*values: Any) -> list[str]:
        merged: list[str] = []
        for value in values:
            if isinstance(value, str) and value.strip():
                merged.append(value.strip())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.strip():
                        merged.append(item.strip())
        return merged

    def compress_for_skill_agent(
        search_lines: list[str],
        test_lines: list[str],
    ) -> tuple[list[str], list[str], list[str]]:
        lowered_search = " ".join(search_lines).lower()
        lowered_tests = [line.lower() for line in test_lines]
        skill_search: list[str] = []
        skill_tests: list[str] = []
        deferred: list[str] = []

        if "matched" in lowered_search or "comparison" in lowered_search:
            skill_search.append("Add one semantically matched renewable-aware variant for direct comparison.")
        if "constraint" in lowered_search or any("constraint_violation" in line for line in lowered_tests):
            skill_search.append("Prioritize candidates that may reduce constraint_violation without leaving renewable-aware control.")
        if "continuous inverter-q" in lowered_search or any("continuous inverter-q" in line for line in lowered_tests):
            skill_search.append("Expand inverter_q search beyond the fixed sign-only grid with bounded additional candidate points.")
        if "coordination" not in lowered_search:
            skill_search.append("Keep shunt + inverter coordination available; do not collapse back to inverter-only or shunt-only search.")

        for line in test_lines:
            lower = line.lower()
            if any(
                token in lower
                for token in [
                    "matched",
                    "head-to-head",
                    "constraint_violation",
                    "continuous inverter-q",
                    "fixed 0.1",
                    "same evaluator",
                ]
            ):
                skill_tests.append(line)
            else:
                deferred.append(line)

        if not skill_search:
            skill_search.append("Refine the current renewable-aware candidate with one additional local search improvement.")
        if not skill_tests:
            skill_tests.append("Produce one materially different renewable-aware candidate under the same evaluator.")
        return skill_search[:4], skill_tests[:6], deferred

    search_updates = merge_lines(
        proposer.get("recommended_action"),
        counter.get("alternative_interpretation"),
        adjudicator.get("accepted_interpretation"),
    )
    discriminating_tests = merge_lines(
        proposer.get("discriminating_missing_evidence"),
        counter.get("discriminating_missing_evidence"),
        adjudicator.get("discriminating_missing_evidence"),
    )
    compressed_search, compressed_tests, deferred_research = compress_for_skill_agent(
        search_updates,
        discriminating_tests,
    )
    blocked = ["pure_weak_shunt_substitution"]
    if iteration >= 2:
        blocked.append("repeat_previous_search_without_new_coordination")
    summary = adjudicator.get("claim_ceiling_recommendation") or adjudicator.get("strongest_supported_claim") or "bounded task003 update"
    payload = {
        "schema_version": "0.1.0",
        "object_type": "agentic_cognition_to_skill_update",
        "object_id": f"agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.{iteration:04d}",
        "object_version": "0.1.0",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "status": "reviewed",
        "metadata": {"task_package": "task003", "workflow": "real_codex_semantic_lane"},
        "task_ref": TASK_REF,
        "iteration_index": iteration,
        "source_event_ref": source_event["object_id"],
        "source_run_refs": [run_obj["object_id"]],
        "source_workflow_output_refs": [str((WORKFLOW_OUTPUT_DIR / ref).relative_to(REPO_ROOT)) for ref in workflow_refs],
        "next_iteration_skill_constraints": merge_lines(
            adjudicator.get("strongest_supported_claim"),
            adjudicator.get("strongest_unsupported_claim"),
        ) or ["maintain renewable-aware control family"],
        "next_iteration_evaluator_constraints": merge_lines(adjudicator.get("overclaim_warnings")),
        "search_priority_updates": compressed_search,
        "blocked_skill_families": blocked,
        "required_discriminating_tests": compressed_tests,
        "summary": summary,
        "confidence": adjudicator.get("confidence", "medium"),
    }
    if deferred_research:
        payload["metadata"]["deferred_research_questions"] = deferred_research[:8]
    write_yaml(path, payload)
    return path


def build_iteration_review(iteration: int, result: dict[str, Any], update: dict[str, Any], request: dict[str, Any], previous_request: dict[str, Any] | None) -> Path:
    path = AGENTIC_LOOP_DIR / "reviews" / f"iter{iteration:02d}.yaml"
    if path.exists():
        return path
    change_lines = result.get("change_summary", [])
    stagnation = []
    cheating = []
    if previous_request is not None and request.get("summary") == previous_request.get("summary"):
        stagnation.append("request summary did not materially change from previous iteration")
    if all("generated" in line.lower() for line in change_lines):
        cheating.append("skill result summary is too thin to prove substantive code change")
    if not update.get("search_priority_updates"):
        stagnation.append("cognition update did not supply search priority changes")
    verdict = "real_progress"
    if cheating:
        verdict = "cheating_suspected"
    elif stagnation:
        verdict = "stagnation"
    payload = {
        "schema_version": "0.1.0",
        "object_type": "agentic_loop_iteration_review",
        "object_id": f"agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.{iteration:04d}",
        "object_version": "0.1.0",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "status": "reviewed",
        "metadata": {"task_package": "task003"},
        "task_ref": TASK_REF,
        "iteration_index": iteration,
        "skill_iteration_result_ref": result["object_id"],
        "cognition_update_ref": update["object_id"],
        "actual_progress": [
            "real skill file produced by Codex",
            "real task003 run executed on produced file",
            "real cognition workflow outputs used to build next update",
        ],
        "stagnation_signals": stagnation,
        "cheating_signals": cheating,
        "verdict": verdict,
        "summary": f"iteration {iteration} review: {verdict}",
    }
    write_yaml(path, payload)
    return path


def run_semantic_workflow(run_dir: Path, iteration: int) -> list[str]:
    comparison = REPO_ROOT / "analysis" / "task003" / "compare_0001" / "strategy_comparison.yaml"
    semantic = REPO_ROOT / "analysis" / "task003" / "semantic_0001" / "strategy_semantic_comparison.yaml"
    workflow_id = f"task003_agentic_semantic_workflow_iter{iteration:02d}"
    jobs = []
    names = [
        ("proposer", "semantic_proposer", "agents/cognition/prompts/semantic_proposer.md"),
        ("counter", "semantic_counter", "agents/cognition/prompts/semantic_counter.md"),
        ("adjudicator", "semantic_adjudicator", "agents/cognition/prompts/semantic_adjudicator.md"),
    ]
    for idx, (role, agent_role, prompt_ref) in enumerate(names):
        predecessor_refs = []
        if role == "counter":
            predecessor_refs = [f"agents/cognition/workflow_outputs/task003_agentic_semantic_proposer_iter{iteration:02d}.json"]
        if role == "adjudicator":
            predecessor_refs = [
                f"agents/cognition/workflow_outputs/task003_agentic_semantic_proposer_iter{iteration:02d}.json",
                f"agents/cognition/workflow_outputs/task003_agentic_semantic_counter_iter{iteration:02d}.json",
                str(semantic.relative_to(REPO_ROOT)),
            ]
        jobs.append(
            {
                "schema_version": "0.1.0",
                "object_type": "llm_cognition_job",
                "job_id": f"task003_agentic_semantic_{role}_iter{iteration:02d}",
                "workflow_id": workflow_id,
                "workflow_role": role,
                "created_at": utc_now(),
                "agent_role": agent_role,
                "prompt_ref": prompt_ref,
                "input_refs": [
                    str((run_dir / "run.yaml").relative_to(REPO_ROOT)),
                    str((run_dir / "metrics.json").relative_to(REPO_ROOT)),
                    str((run_dir / "report.yaml").relative_to(REPO_ROOT)),
                    str(comparison.relative_to(REPO_ROOT)),
                    str(semantic.relative_to(REPO_ROOT)),
                ],
                "predecessor_output_refs": predecessor_refs,
                "expected_output_schema": "agents/cognition/workflow_spec.yaml",
            }
        )
    expected_refs = [f"task003_agentic_semantic_{role}_iter{iteration:02d}.json" for role in ("proposer", "counter", "adjudicator")]
    if all((WORKFLOW_OUTPUT_DIR / ref).exists() for ref in expected_refs):
        return expected_refs
    workflow_path = REPO_ROOT / "agents" / "cognition" / "workflows" / f"{workflow_id}.json"
    write_json(workflow_path, {"workflow_id": workflow_id, "jobs": jobs})
    command = workflow_command()
    for job in jobs:
        expected_path = WORKFLOW_OUTPUT_DIR / f"{job['job_id']}.json"
        if expected_path.exists():
            continue
        single_job_path = REPO_ROOT / "agents" / "cognition" / "jobs" / f"{job['job_id']}.json"
        single_prompt_path = REPO_ROOT / "agents" / "cognition" / "jobs" / f"{job['job_id']}.prompt.md"
        write_json(single_job_path, job)
        prompt = "\n".join(
            [
                (REPO_ROOT / job["prompt_ref"]).read_text(encoding="utf-8"),
                "",
                "## Job",
                json.dumps(job, indent=2, ensure_ascii=False),
                "",
                "## Input Artifact Excerpts",
            ]
        )
        for ref in job["input_refs"][:12]:
            p = REPO_ROOT / ref
            if p.exists() and p.is_file():
                prompt += f"\n### {ref}\n{p.read_text(encoding='utf-8')[:1800]}\n"
        prompt += "\n## Predecessor Output Excerpts\n"
        for ref in job.get("predecessor_output_refs", [])[:12]:
            p = REPO_ROOT / ref
            if p.exists() and p.is_file():
                prompt += f"\n### {ref}\n{p.read_text(encoding='utf-8')[:1800]}\n"
        single_prompt_path.write_text(prompt, encoding="utf-8")
        result = subprocess.run(
            [
                "python",
                "scripts/run_llm_cognition_job.py",
                str(single_job_path.relative_to(REPO_ROOT)),
                "--command",
                command,
                "--output-dir",
                "agents/cognition/workflow_outputs",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=900,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
    return [f"{job['job_id']}.json" for job in jobs]


def verify_artifacts() -> None:
    result = subprocess.run(
        ["python", "scripts/validate_schemas.py", "--artifacts", "real-agentic-loop"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)


def run_iteration(iteration: int, previous_update: dict[str, Any] | None, previous_request: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    if previous_update is None:
        blocked = ["pure_weak_shunt_substitution", "metric_only_search_without renewable awareness"]
        priorities = [
            "Preserve renewable-aware control family.",
            "Add explicit shunt + inverter coordination candidate generation.",
            "Do not regress into weak-shunt-only substitutes.",
        ]
        tests = [
            "task003 run must remain importable and executable",
            "candidate should explore coordination beyond sign-only inverter grid",
        ]
        source_update_ref = "cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0001"
    else:
        blocked = previous_update.get("blocked_skill_families", [])
        priorities = previous_update.get("search_priority_updates", []) or ["Refine previous task003 agentic candidate."]
        tests = previous_update.get("required_discriminating_tests", []) or ["produce materially different search logic from previous iteration"]
        source_update_ref = previous_update["object_id"]
    request_path = build_request(iteration, source_update_ref, blocked, priorities, tests)
    request = load_yaml(request_path)
    result_path = run_codex_skill_agent(request_path, iteration)
    result = load_yaml(result_path)
    run_dir, run_obj = run_real_task003_with_skill(output_skill_path(iteration), result["produced_skill_ref"], iteration)
    workflow_refs = run_semantic_workflow(run_dir, iteration)
    update_path = build_agentic_update(iteration, request, result, run_obj, workflow_refs)
    update = load_yaml(update_path)
    build_iteration_review(iteration, result, update, request, previous_request)
    return update, request


def build_capability_report() -> Path:
    review_paths = sorted((AGENTIC_LOOP_DIR / "reviews").glob("*.yaml"))
    reviews = [load_yaml(path) for path in review_paths]
    report = {
        "generated_at": utc_now(),
        "task_ref": TASK_REF,
        "iterations_observed": len(reviews),
        "what_can_be_done": [
            "real Codex can generate importable task003 candidate skill variants under bounded scope",
            "real cognition workflow can produce next-iteration constraints from fresh run artifacts",
            "two-round loop can preserve task semantics while changing search priorities",
        ],
        "what_can_not_be_done_yet": [
            "open-ended autonomous skill invention without strong request boundaries",
            "reliable evaluator redesign from cognition output alone",
            "high-confidence multi-task concurrent evolution",
        ],
        "risks": [
            "skill agent may still overfit to current representative snapshot",
            "cognition update extraction remains partly scripted after workflow output",
        ],
        "review_refs": [str(path.relative_to(REPO_ROOT)) for path in review_paths],
    }
    path = AGENTIC_LOOP_DIR / "capability_boundary_report.json"
    write_json(path, report)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real agentic skill-cognition loop.")
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--materialize-existing", action="store_true")
    args = parser.parse_args()
    if args.materialize_existing:
        for result_path in sorted(SKILL_RESULTS_DIR.glob("task003_iter*.yaml")):
            result_payload = load_yaml(result_path)
            iter_idx = int(result_path.stem.replace("task003_iter", ""))
            materialize_skill_asset(iter_idx, result_payload)
        print("Existing agentic skill assets materialized.")
        return 0
    if args.iterations < 2:
        raise RuntimeError("use at least 2 iterations for the real agentic loop")
    previous_update = None
    previous_request = None
    for iteration in range(1, args.iterations + 1):
        previous_update, previous_request = run_iteration(iteration, previous_update, previous_request)
    build_capability_report()
    verify_artifacts()
    print(f"Real agentic loop completed for {args.iterations} iterations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
