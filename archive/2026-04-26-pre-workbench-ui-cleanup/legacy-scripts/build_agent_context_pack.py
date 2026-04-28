#!/usr/bin/env python3
"""Build persisted research-plan-execute context packs.

This script reconstructs the task003 iteration-2 agent inputs as protocol
objects. It does not run workers and does not judge research conclusions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROLES = ["skill_worker", "effectiveness_worker", "cognition_worker", "review_worker"]
TASK003_REF = "task.power.ieee69_renewable_reactive_opt"
TASK003_BASELINE_REF = "baseline.power.ieee69_renewable_reactive_opt.fixed_inverter_q"
TASK003_EVALUATOR_REF = "evaluator.power.ieee69_renewable_reactive_opt.default"
ROLE_OUTPUT_SCHEMA = {
    "skill_worker": "schema.skill_agent_iteration_request",
    "effectiveness_worker": "schema.run",
    "cognition_worker": "schema.agentic_cognition_to_skill_update",
    "review_worker": "schema.research_review",
}
ROLE_MISSION = {
    "skill_worker": "Create or revise a bounded candidate skill artifact from approved constraints only.",
    "effectiveness_worker": "Assess baseline and candidate evidence without changing skills or task definitions.",
    "cognition_worker": "Interpret evidence, uncertainty, and next constraints without rewriting skill logic.",
    "review_worker": "Apply the hard review gate and decide approval, bounded progress, or repair routing.",
}
ROLE_BOUNDARY = {
    "skill_worker": [
        "Do not judge final research value.",
        "Do not modify evaluator, task, review, or cognition artifacts.",
        "Do not make causality claims.",
    ],
    "effectiveness_worker": [
        "Do not modify candidate skill code.",
        "Do not convert metric improvement into cognition causality.",
        "Do not weaken evaluator or baseline requirements.",
    ],
    "cognition_worker": [
        "Do not write skill code.",
        "Do not invent evidence beyond referenced artifacts.",
        "Separate facts, interpretation, constraints, and uncertainty.",
    ],
    "review_worker": [
        "Do not repair artifacts directly.",
        "Do not approve causality claims without ablation.",
        "Route failures to repair requests instead of controller-side fixes.",
    ],
}
ROLE_ALLOWED_CHANGES = {
    "skill_worker": [
        "candidate skill file",
        "skill iteration result",
        "self report of implementation risks",
    ],
    "effectiveness_worker": [
        "evaluation run artifact",
        "metrics comparison artifact",
        "metric boundary note",
    ],
    "cognition_worker": [
        "cognition diagnosis",
        "cognition-to-skill update",
        "uncertainty note",
    ],
    "review_worker": [
        "research review",
        "repair request",
        "approval record",
    ],
}
ROLE_BLOCKED_PATHS = {
    "skill_worker": [
        "evaluators/**",
        "tasks/**",
        "analysis/agentic_loop/**",
        "cognition/**",
        "docs/**",
    ],
    "effectiveness_worker": [
        "skills/active_dev/**",
        "tasks/**",
        "cognition/**",
    ],
    "cognition_worker": [
        "skills/active_dev/**",
        "evaluators/**",
        "tasks/**",
    ],
    "review_worker": [
        "skills/active_dev/**",
        "evaluators/**",
        "tasks/**",
        "agents/skill/results/**",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to an object")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def digest_refs(refs: list[str]) -> str:
    h = hashlib.sha256()
    for ref in sorted(dict.fromkeys(refs)):
        h.update(ref.encode("utf-8"))
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


def require_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path.relative_to(REPO_ROOT)}")


def task003_artifacts(iteration: int) -> dict[str, Any]:
    tag = f"iter{iteration:02d}"
    request_path = REPO_ROOT / "agents" / "skill" / "requests" / f"task003_{tag}.yaml"
    result_path = REPO_ROOT / "agents" / "skill" / "results" / f"task003_{tag}.yaml"
    update_path = REPO_ROOT / "analysis" / "agentic_loop" / "task003" / "updates" / f"{tag}.yaml"
    review_path = REPO_ROOT / "analysis" / "agentic_loop" / "task003" / "reviews" / f"{tag}.yaml"
    run_path = REPO_ROOT / "runs" / "task003" / f"run_{20 + iteration - 1:04d}" / "run.yaml"
    metrics_path = REPO_ROOT / "runs" / "task003" / f"run_{20 + iteration - 1:04d}" / "metrics.json"
    for path in [request_path, result_path, update_path, review_path, run_path, metrics_path]:
        require_file(path)
    request = load_yaml(request_path)
    result = load_yaml(result_path)
    update = load_yaml(update_path)
    review = load_yaml(review_path)
    run = load_yaml(run_path)
    metrics = load_json(metrics_path)
    prior_refs = [
        request["object_id"],
        result["object_id"],
        update["object_id"],
        review["object_id"],
        run["object_id"],
    ]
    return {
        "request": request,
        "result": result,
        "update": update,
        "review": review,
        "run": run,
        "metrics": metrics,
        "prior_refs": prior_refs,
        "review_refs": [review["object_id"]],
        "run_ref": run["object_id"],
    }


def build_batch(*, task: str, iteration: int, out_dir: Path, now: str) -> dict[str, Any]:
    batch = {
        "schema_version": "0.1.0",
        "object_type": "research_batch",
        "object_id": f"research_batch.power.ieee69_renewable_reactive_opt.{iteration:04d}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {
            "protocol": "research-plan-execute",
            "task_package": task,
            "source_case": "task003_iter02",
        },
        "plan_ref": "plan.research_plan_execute_protocol",
        "batch_index": iteration,
        "task_ref": TASK003_REF,
        "batch_goal": "Reconstruct task003 iter02 into auditable worker context packs.",
        "worker_sequence": DEFAULT_ROLES,
        "required_outputs": [
            "worker_runtime_binding",
            "agent_context_pack",
            "rendered_prompt",
            "execution_ledger",
        ],
        "review_gate_required": True,
    }
    write_yaml(out_dir / "research_batch.yaml", batch)
    return batch


def build_runtime_binding(*, role: str, batch_ref: str, out_dir: Path, now: str) -> dict[str, Any]:
    binding = {
        "schema_version": "0.1.0",
        "object_type": "worker_runtime_binding",
        "object_id": f"worker_runtime_binding.power.ieee69_renewable_reactive_opt.{role}.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {"protocol": "research-plan-execute", "task_package": "task003"},
        "batch_ref": batch_ref,
        "worker_role": role,
        "runtime_kind": "codex_cli",
        "provider": "openai",
        "model": "gpt-5.4",
        "tool_permission_profile": "workspace-write",
        "session_reuse_policy": "reuse_within_batch_only",
        "timeout_seconds": 1800,
        "retry_policy": {"max_attempts": 1, "retry_on": ["runtime_timeout", "provider_error"]},
        "raw_transcript_path": str((out_dir / "raw" / f"{role}.raw.txt").relative_to(REPO_ROOT)),
    }
    write_yaml(out_dir / f"worker_runtime_binding.{role}.yaml", binding)
    return binding


def current_hypothesis(role: str, artifacts: dict[str, Any]) -> str:
    metrics = artifacts["metrics"]
    baseline = metrics.get("baseline_solution", {}).get("metrics", {})
    candidate = metrics.get("candidate_solution", {}).get("metrics", {})
    verdict = artifacts["review"].get("verdict", "unknown")
    if role == "skill_worker":
        return "Bounded candidate changes may improve task003 metrics, but only within review-approved constraints."
    if role == "effectiveness_worker":
        return (
            "Current evidence reports loss "
            f"{baseline.get('loss')} -> {candidate.get('loss')} and constraint_violation "
            f"{baseline.get('constraint_violation')} -> {candidate.get('constraint_violation')}."
        )
    if role == "cognition_worker":
        return "The evidence may justify next constraints, but not causality claims without ablation."
    return f"The previous loop review verdict is {verdict}; only approved verdicts proceed freely."


def build_context_pack(
    *,
    role: str,
    batch_ref: str,
    binding_ref: str,
    artifacts: dict[str, Any],
    out_dir: Path,
    now: str,
) -> dict[str, Any]:
    prior_refs = list(dict.fromkeys(artifacts["prior_refs"]))
    if role in {"effectiveness_worker", "cognition_worker", "review_worker"}:
        prior_refs = list(dict.fromkeys(prior_refs + ["run.power.ieee69_renewable_reactive_opt.0021"]))
    context = {
        "schema_version": "0.1.0",
        "object_type": "agent_context_pack",
        "object_id": f"agent_context_pack.power.ieee69_renewable_reactive_opt.{role}.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {
            "protocol": "research-plan-execute",
            "task_package": "task003",
            "source_iteration": 2,
        },
        "batch_ref": batch_ref,
        "worker_role": role,
        "runtime_binding_ref": binding_ref,
        "mission": ROLE_MISSION[role],
        "role_boundary": ROLE_BOUNDARY[role],
        "task_refs": [TASK003_REF],
        "prior_artifact_refs": prior_refs,
        "allowed_changes": ROLE_ALLOWED_CHANGES[role],
        "blocked_paths": ROLE_BLOCKED_PATHS[role],
        "evaluator_refs": [TASK003_EVALUATOR_REF],
        "baseline_refs": [TASK003_BASELINE_REF],
        "review_history_refs": artifacts["review_refs"],
        "current_hypothesis": current_hypothesis(role, artifacts),
        "required_output_schema_ref": ROLE_OUTPUT_SCHEMA[role],
        "stop_conditions": [
            "missing required artifact reference",
            "attempt to relax evaluator or baseline",
            "attempt to claim cognition causality without ablation",
        ],
        "token_budget": 16000,
        "context_budget": 32000,
        "artifact_provenance_digest": digest_refs(prior_refs + [batch_ref, binding_ref]),
        "redaction_policy": "Never include provider tokens, local secrets, or ~/.claude and ~/.pi auth material.",
        "expected_failure_modes": [
            "controller overreach",
            "overclaiming from metric-only evidence",
            "schema enum drift",
            "missing raw transcript provenance",
        ],
        "previous_repair_attempt_refs": [],
        "rendered_prompt_path": str((out_dir / "prompts" / f"{role}.prompt.md").relative_to(REPO_ROOT)),
    }
    write_yaml(out_dir / f"agent_context_pack.{role}.yaml", context)
    return context


def render_prompt(context: dict[str, Any], out_dir: Path) -> None:
    lines = [
        f"# Research Plan-Execute Context: {context['worker_role']}",
        "",
        f"Mission: {context['mission']}",
        "",
        "## Role Boundary",
        *[f"- {item}" for item in context["role_boundary"]],
        "",
        "## Task And Evidence",
        f"- Task refs: {', '.join(context['task_refs'])}",
        f"- Evaluator refs: {', '.join(context['evaluator_refs'])}",
        f"- Baseline refs: {', '.join(context['baseline_refs'])}",
        f"- Prior artifact refs: {', '.join(context['prior_artifact_refs'])}",
        f"- Review history refs: {', '.join(context['review_history_refs'])}",
        "",
        "## Allowed Changes",
        *[f"- {item}" for item in context["allowed_changes"]],
        "",
        "## Blocked Paths",
        *[f"- {item}" for item in context["blocked_paths"]],
        "",
        "## Current Hypothesis",
        context["current_hypothesis"],
        "",
        "## Output Contract",
        f"- Required output schema: {context['required_output_schema_ref']}",
        f"- Runtime binding: {context['runtime_binding_ref']}",
        f"- Provenance digest: {context['artifact_provenance_digest']}",
        "",
        "## Stop Conditions",
        *[f"- {item}" for item in context["stop_conditions"]],
        "",
        "## Redaction Policy",
        context["redaction_policy"],
    ]
    write_text(REPO_ROOT / context["rendered_prompt_path"], "\n".join(lines) + "\n")


def build_ledger(*, batch_ref: str, context_refs: list[str], out_dir: Path, now: str) -> None:
    events = [{"at": now, "state": "started", "artifact_ref": batch_ref}]
    events.extend({"at": now, "state": "context_created", "artifact_ref": ref} for ref in context_refs)
    events.append({"at": now, "state": "validation_passed", "artifact_ref": batch_ref})
    ledger = {
        "schema_version": "0.1.0",
        "object_type": "execution_ledger",
        "object_id": "execution_ledger.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "completed",
        "metadata": {"protocol": "research-plan-execute", "task_package": "task003"},
        "batch_ref": batch_ref,
        "current_state": "validation_passed",
        "events": events,
    }
    write_yaml(out_dir / "execution_ledger.yaml", ledger)


def build(task: str, iteration: int) -> Path:
    if task != "task003" or iteration != 2:
        raise RuntimeError("MVP supports only --task task003 --iteration 2")
    out_dir = REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02"
    now = utc_now()
    artifacts = task003_artifacts(iteration)
    batch = build_batch(task=task, iteration=iteration, out_dir=out_dir, now=now)
    context_refs: list[str] = []
    for role in DEFAULT_ROLES:
        binding = build_runtime_binding(role=role, batch_ref=batch["object_id"], out_dir=out_dir, now=now)
        context = build_context_pack(
            role=role,
            batch_ref=batch["object_id"],
            binding_ref=binding["object_id"],
            artifacts=artifacts,
            out_dir=out_dir,
            now=now,
        )
        render_prompt(context, out_dir)
        context_refs.append(context["object_id"])
    build_ledger(batch_ref=batch["object_id"], context_refs=context_refs, out_dir=out_dir, now=now)
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build research-plan-execute context packs.")
    parser.add_argument("--task", default="task003")
    parser.add_argument("--iteration", type=int, default=2)
    args = parser.parse_args()
    out_dir = build(args.task, args.iteration)
    print(f"Built research-plan-execute context packs in {out_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
