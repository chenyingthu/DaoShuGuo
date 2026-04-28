#!/usr/bin/env python3
"""Verify the research-plan-execute MVP protocol artifacts."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02"
ROLES = ["skill_worker", "effectiveness_worker", "cognition_worker", "review_worker"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing artifact: {path.relative_to(REPO_ROOT)}")


def verify_context_pack(role: str, batch: dict[str, Any], objects: dict[str, dict[str, Any]]) -> None:
    binding_path = ROOT / f"worker_runtime_binding.{role}.yaml"
    context_path = ROOT / f"agent_context_pack.{role}.yaml"
    require(binding_path)
    require(context_path)
    binding = load_yaml(binding_path)
    context = load_yaml(context_path)
    objects[binding["object_id"]] = binding
    objects[context["object_id"]] = context

    if binding["batch_ref"] != batch["object_id"]:
        raise RuntimeError(f"{role}: runtime binding batch_ref mismatch")
    if binding["worker_role"] != role:
        raise RuntimeError(f"{role}: runtime binding role mismatch")
    if not binding.get("provider") or not binding.get("model"):
        raise RuntimeError(f"{role}: provider/model missing")
    if not binding.get("raw_transcript_path"):
        raise RuntimeError(f"{role}: raw transcript path missing")

    if context["batch_ref"] != batch["object_id"]:
        raise RuntimeError(f"{role}: context batch_ref mismatch")
    if context["worker_role"] != role:
        raise RuntimeError(f"{role}: context worker_role mismatch")
    if context["runtime_binding_ref"] != binding["object_id"]:
        raise RuntimeError(f"{role}: context runtime binding ref mismatch")
    if not context.get("artifact_provenance_digest", "").startswith("sha256:"):
        raise RuntimeError(f"{role}: missing sha256 provenance digest")
    if not context.get("blocked_paths"):
        raise RuntimeError(f"{role}: blocked paths missing")
    if not context.get("allowed_changes"):
        raise RuntimeError(f"{role}: allowed changes missing")
    if not context.get("review_history_refs"):
        raise RuntimeError(f"{role}: review history refs missing")
    if not context.get("prior_artifact_refs"):
        raise RuntimeError(f"{role}: prior artifact refs missing")
    if "cognition causality" not in " ".join(context.get("stop_conditions", [])):
        raise RuntimeError(f"{role}: causality stop condition missing")
    rendered_prompt = REPO_ROOT / context["rendered_prompt_path"]
    require(rendered_prompt)
    prompt_text = rendered_prompt.read_text(encoding="utf-8")
    if context["mission"] not in prompt_text:
        raise RuntimeError(f"{role}: rendered prompt does not include mission")


def verify_ledger(batch: dict[str, Any], objects: dict[str, dict[str, Any]]) -> None:
    ledger_path = ROOT / "execution_ledger.yaml"
    require(ledger_path)
    ledger = load_yaml(ledger_path)
    objects[ledger["object_id"]] = ledger
    if ledger["batch_ref"] != batch["object_id"]:
        raise RuntimeError("ledger batch_ref mismatch")
    allowed_states = {"validation_passed", "review_completed", "repair_requested", "approved"}
    if ledger["current_state"] not in allowed_states:
        raise RuntimeError(
            "ledger current_state must be validation_passed or a valid downstream gate state"
        )
    event_refs = {event.get("artifact_ref") for event in ledger.get("events", [])}
    for role in ROLES:
        expected = f"agent_context_pack.power.ieee69_renewable_reactive_opt.{role}.0002"
        if expected not in event_refs:
            raise RuntimeError(f"ledger missing context_created event for {role}")


def verify() -> None:
    require(ROOT / "research_batch.yaml")
    batch = load_yaml(ROOT / "research_batch.yaml")
    if batch["object_type"] != "research_batch":
        raise RuntimeError("research_batch.yaml has wrong object_type")
    if batch["worker_sequence"] != ROLES:
        raise RuntimeError("research batch worker sequence is not the expected MVP sequence")
    if not batch["review_gate_required"]:
        raise RuntimeError("research batch must require review gate")
    objects: dict[str, dict[str, Any]] = {batch["object_id"]: batch}
    for role in ROLES:
        verify_context_pack(role, batch, objects)
    verify_ledger(batch, objects)


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Research plan-execute protocol verification failed: {exc}", file=sys.stderr)
        return 1
    print("Research plan-execute protocol verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
