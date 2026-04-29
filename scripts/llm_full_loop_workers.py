#!/usr/bin/env python3
"""Generic LLM worker module for full-loop validation.

The loop engine owns persistence, verification, and routing. This module only
asks the configured LLM runtime to author phase-local worker JSON, then maps
that JSON back into the existing worker contract.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generic_diagnosis_layer import PROBLEM_CLASSES, ROUTING_POLICY, validate_diagnosis_fields
from scripts.generic_full_loop_validation_workers import scenario, task_package
from scripts.pi_runtime import run_pi_prompt, write_json


DEFAULT_BACKEND_CONFIG = {
    "backend_id": "llm_unknown",
    "runner": "pi",
    "agent_profile": "pi:codex-relay:gpt-5.5",
    "thinking_profile": "off",
    "raw_output_root": "analysis/full_loop_validation/llm_worker_raw",
    "max_json_attempts": 2,
}


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def _extract_json(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise RuntimeError("LLM response did not contain a JSON object")


def _assistant_text(events: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for block in message.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    return "\n".join(parts)


def _assistant_error(events: list[dict[str, Any]]) -> str | None:
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        error = message.get("errorMessage")
        if isinstance(error, str) and error.strip():
            return error
        if message.get("stopReason") == "error":
            return "assistant stopped with error"
    return None


def _backend_config(inputs: dict[str, Any]) -> dict[str, Any]:
    config = dict(DEFAULT_BACKEND_CONFIG)
    injected = inputs.get("backend_config")
    if isinstance(injected, dict):
        config.update(injected)
    return config


def _agent_profile_parts(config: dict[str, Any]) -> dict[str, str]:
    profile = str(config.get("agent_profile", DEFAULT_BACKEND_CONFIG["agent_profile"]))
    parts = profile.split(":")
    if len(parts) < 2:
        raise RuntimeError(f"invalid agent_profile {profile!r}")
    family = parts[0]
    if family == "pi":
        if len(parts) < 3:
            raise RuntimeError(f"Pi agent_profile must be pi:<profile-provider>:<profile-model>, got {profile!r}")
        return {
            "family": family,
            "profile": profile,
            "provider_profile": parts[1],
            "model_profile": ":".join(parts[2:]),
            "thinking_profile": str(config.get("thinking_profile", "off")),
        }
    return {
        "family": family,
        "profile": profile,
        "provider_profile": family,
        "model_profile": ":".join(parts[1:]),
        "thinking_profile": str(config.get("thinking_profile", "off")),
    }


def _raw_root(config: dict[str, Any]) -> Path:
    root = Path(str(config.get("raw_output_root", DEFAULT_BACKEND_CONFIG["raw_output_root"])))
    return root if root.is_absolute() else REPO_ROOT / root


def _context(inputs: dict[str, Any]) -> dict[str, Any]:
    adapter = inputs["task_adapter"]
    data = scenario(inputs)
    backend = _backend_config(inputs)
    profile = _agent_profile_parts(backend)
    return {
        "backend": {
            "backend_id": backend.get("backend_id"),
            "runtime_id": backend.get("runtime_id"),
            "runtime_type": backend.get("runtime_type"),
            "runner": backend.get("runner"),
            "agent_profile": profile["profile"],
            "thinking_profile": profile["thinking_profile"],
            "prompt_profile": backend.get("prompt_profile"),
            "output_contract": backend.get("output_contract"),
        },
        "task_ref": adapter.get("task_ref"),
        "task_adapter_ref": adapter.get("object_id"),
        "task_package": task_package(inputs),
        "metrics_mapping": adapter.get("metrics_mapping", {}),
        "claim_gates": adapter.get("claim_gates", []),
        "validation_scenario": data,
        "prior_artifact_refs": {
            name: payload.get("object_id")
            for name, payload in inputs.get("prior_artifacts", {}).items()
            if isinstance(payload, dict)
        },
    }


def _run_llm_prompt(prompt: str, raw_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    runner = config.get("runner")
    if runner != "pi":
        raise RuntimeError(
            f"backend {config.get('backend_id')} runner {runner!r} is not implemented in generic LLM runtime"
        )
    profile = _agent_profile_parts(config)
    return run_pi_prompt(
        prompt,
        raw_dir,
        provider=profile["provider_profile"],
        model=profile["model_profile"],
        thinking=profile["thinking_profile"],
    )


def _contract_guidance(phase: str) -> dict[str, Any]:
    if phase != "cognition_diagnosis_worker":
        return {}
    return {
        "allowed_problem_classes": sorted(PROBLEM_CLASSES),
        "routing_policy": {
            problem_class: {
                "recommended_next_worker": sorted(policy["workers"]),
                "recommended_action": sorted(policy["actions"]),
                "continue_loop": policy["continue_loop"],
            }
            for problem_class, policy in sorted(ROUTING_POLICY.items())
        },
        "instruction": (
            "Use only the exact enum strings listed here. If your semantic label is more specific, "
            "put it in judgment_summary or boundary_notes, not in problem_class or recommended_next_worker."
        ),
    }


def _ask_llm(
    phase: str,
    inputs: dict[str, Any],
    required_shape: dict[str, Any],
    *,
    semantic_validator: Callable[[dict[str, Any]], list[str]] | None = None,
) -> dict[str, Any]:
    config = _backend_config(inputs)
    context = _context(inputs)
    raw_dir = _raw_root(config) / str(config.get("backend_id")) / _slug(context["task_ref"]) / phase
    raw_dir.mkdir(parents=True, exist_ok=True)
    prompt = f"""
You are the {phase} in DaoShuGuo's generic skill-effectiveness-cognition loop.

Return exactly one JSON object. Do not include Markdown. Do not write files.
The loop controller will persist your judgment, so do not claim controller authority.
Keep every string short. Use at most 2 array items per field.

Context:
{json.dumps(context, ensure_ascii=False, indent=2)}

Required JSON shape:
{json.dumps(required_shape, ensure_ascii=False, indent=2)}

Contract guidance:
{json.dumps(_contract_guidance(phase), ensure_ascii=False, indent=2)}
""".strip()
    last_error = "not run"
    attempts = int(config.get("max_json_attempts", 2))
    for attempt in range(1, attempts + 1):
        run = _run_llm_prompt(prompt, raw_dir, config)
        record = {
            "backend_id": config.get("backend_id"),
            "runtime_id": config.get("runtime_id"),
            "runner": config.get("runner"),
            "agent_profile": config.get("agent_profile"),
            "thinking_profile": config.get("thinking_profile"),
            "phase": phase,
            "attempt": attempt,
            "exit_code": run["exit_code"],
            "stdout": run["stdout"],
            "stderr": run["stderr"],
        }
        write_json(raw_dir / f"attempt_{attempt}.json", record)
        write_json(raw_dir / "latest.json", record)
        if run["exit_code"] != 0:
            last_error = f"exit code {run['exit_code']}: {run['stderr']}"
            continue
        assistant_error = _assistant_error(run["events"])
        if assistant_error:
            last_error = assistant_error
            continue
        text = _assistant_text(run["events"])
        if not text and run["events"]:
            last_error = "LLM response did not contain assistant text"
            continue
        text = text or run["stdout"]
        try:
            payload = _extract_json(text)
        except RuntimeError as exc:
            last_error = str(exc)
            prompt = (
                "Your previous answer was not parseable as one complete JSON object. "
                "Return only a compact complete JSON object now. No Markdown, no prose.\n\n"
                f"Required JSON shape:\n{json.dumps(required_shape, ensure_ascii=False, indent=2)}\n\n"
                f"Contract guidance:\n{json.dumps(_contract_guidance(phase), ensure_ascii=False, indent=2)}\n\n"
                f"Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
            )
            continue
        semantic_issues = semantic_validator(payload) if semantic_validator else []
        if not semantic_issues:
            return payload
        last_error = "; ".join(semantic_issues)
        prompt = (
            "Your previous JSON was parseable but violated the required contract. "
            "Return only a corrected JSON object using the allowed vocabulary exactly.\n\n"
            f"Contract errors:\n{json.dumps(semantic_issues, ensure_ascii=False, indent=2)}\n\n"
            f"Required JSON shape:\n{json.dumps(required_shape, ensure_ascii=False, indent=2)}\n\n"
            f"Contract guidance:\n{json.dumps(_contract_guidance(phase), ensure_ascii=False, indent=2)}\n\n"
            f"Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
        )
    raise RuntimeError(f"LLM {phase} worker failed to return parseable JSON after retry: {last_error}")


def _metadata(inputs: dict[str, Any], worker: str) -> dict[str, Any]:
    config = _backend_config(inputs)
    return {
        "task_package": task_package(inputs),
        "worker": worker,
        "backend": config.get("backend_id"),
        "runner": config.get("runner"),
        "agent_profile": config.get("agent_profile"),
        "thinking_profile": config.get("thinking_profile"),
    }


def _as_string_list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        items = [item for item in value if isinstance(item, str) and item.strip()]
        if items:
            return items
    if isinstance(value, str) and value.strip():
        return [value]
    return fallback


def _as_bool(value: Any, fallback: bool) -> bool:
    return value if isinstance(value, bool) else fallback


def skill_change_request_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    payload = _ask_llm(
        "skill_change_request_worker",
        inputs,
        {
            "summary": "string",
            "allowed_change_scope": ["string"],
            "blocked_paths": ["string"],
            "required_tests": ["string"],
        },
    )
    return {
        "metadata": _metadata(inputs, "skill_worker"),
        "fields": {
            "base_skill_ref": data["base_skill_ref"],
            "allowed_change_scope": _as_string_list(payload.get("allowed_change_scope"), data["allowed_change_scope"]),
            "blocked_paths": _as_string_list(payload.get("blocked_paths"), data["blocked_paths"]),
            "required_tests": _as_string_list(payload.get("required_tests"), data["required_tests"]),
            "output_skill_path": data["output_skill_path"],
            "summary": str(payload.get("summary") or data.get("skill_request_summary") or "LLM-authored bounded skill request."),
        },
    }


def skill_execution_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    config = _backend_config(inputs)
    payload = _ask_llm(
        "skill_execution_worker",
        inputs,
        {
            "change_summary": ["string"],
            "expected_behavior_change": ["string"],
            "self_reported_risks": ["string"],
        },
    )
    raw_latest = (
        _raw_root(config)
        / str(config.get("backend_id"))
        / _slug(inputs["task_adapter"]["task_ref"])
        / "skill_execution_worker"
        / "latest.json"
    )
    return {
        "metadata": _metadata(inputs, "skill_worker"),
        "fields": {
            "produced_skill_ref": data["produced_skill_id"],
            "code_paths": data.get("code_paths", [data["output_skill_path"]]),
            "change_summary": _as_string_list(
                payload.get("change_summary"), data.get("change_summary", ["LLM materialized the declared candidate."])
            ),
            "expected_behavior_change": _as_string_list(
                payload.get("expected_behavior_change"),
                data.get("expected_behavior_change", ["Behavior follows the declared validation scenario."]),
            ),
            "command": f"{config.get('runner')}:{config.get('agent_profile')}:skill_execution_worker",
            "raw_output_path": str(raw_latest.relative_to(REPO_ROOT)),
            "self_reported_risks": _as_string_list(
                payload.get("self_reported_risks"),
                data.get("self_reported_risks", ["LLM worker output is constrained by prompt-following reliability."]),
            ),
            "run_ref": data["synthetic_run_id"],
        },
    }


def effectiveness_assessment_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    adapter = inputs["task_adapter"]
    baseline_refs = adapter.get("baseline_binding", {}).get("baseline_refs", [])
    evaluator_ref = adapter.get("evaluator_binding", {}).get("evaluator_ref", "evaluator.power.validation.default")
    payload = _ask_llm(
        "effectiveness_assessment_worker",
        inputs,
        {
            "comparison_summary": "string",
            "judgment_summary": "string",
            "recommended_cognition_action": "string",
            "run_passed": "boolean",
        },
    )
    return {
        "metadata": _metadata(inputs, "effectiveness_worker"),
        "fields": {
            "baseline_ref": baseline_refs[0] if baseline_refs else "baseline.power.validation.default",
            "evaluator_ref": evaluator_ref,
            "run_ref": data["synthetic_run_id"],
            "run_passed": _as_bool(payload.get("run_passed"), bool(data["run_passed"])),
            "metric_summary": data["metric_summary"],
            "comparison_summary": str(payload.get("comparison_summary") or data["comparison_summary"]),
            "judgment_summary": str(payload.get("judgment_summary") or data["effectiveness_judgment"]),
            "recommended_cognition_action": str(
                payload.get("recommended_cognition_action") or data["recommended_cognition_action"]
            ),
        },
    }


def cognition_diagnosis_worker(inputs: dict[str, Any]) -> dict[str, Any]:
    data = scenario(inputs)
    required_shape = {
        "problem_class": "one of the allowed diagnosis problem classes",
        "judgment_summary": "string",
        "boundary_notes": ["string"],
        "uncertainty_notes": ["string"],
        "recommended_next_worker": "allowed worker name",
        "recommended_action": "allowed routing action",
        "continue_loop": "boolean",
        "next_iteration_skill_constraints": ["string"],
        "next_iteration_evaluator_constraints": ["string"],
        "search_priority_updates": ["string"],
        "required_discriminating_tests": ["string"],
        "update_summary": "string",
    }

    def validate_payload(payload: dict[str, Any]) -> list[str]:
        fields = {
            "problem_class": str(payload.get("problem_class") or data["problem_class"]),
            "judgment_summary": str(payload.get("judgment_summary") or data["cognition_judgment"]),
            "boundary_notes": _as_string_list(
                payload.get("boundary_notes"), data.get("boundary_notes", ["Bounded by validation scenario."])
            ),
            "uncertainty_notes": _as_string_list(
                payload.get("uncertainty_notes"), data.get("uncertainty_notes", ["No broader claim."])
            ),
            "recommended_next_worker": str(payload.get("recommended_next_worker") or data["next_worker"]),
            "recommended_action": str(payload.get("recommended_action") or data["recommended_action"]),
            "continue_loop": _as_bool(payload.get("continue_loop"), bool(data["continue_loop"])),
        }
        return validate_diagnosis_fields(fields)

    payload = _ask_llm(
        "cognition_diagnosis_worker",
        inputs,
        required_shape,
        semantic_validator=validate_payload,
    )
    fields = {
        "problem_class": str(payload.get("problem_class") or data["problem_class"]),
        "judgment_summary": str(payload.get("judgment_summary") or data["cognition_judgment"]),
        "boundary_notes": _as_string_list(
            payload.get("boundary_notes"), data.get("boundary_notes", ["Bounded by the declared validation scenario."])
        ),
        "uncertainty_notes": _as_string_list(
            payload.get("uncertainty_notes"), data.get("uncertainty_notes", ["No broader research claim is made."])
        ),
        "recommended_next_worker": str(payload.get("recommended_next_worker") or data["next_worker"]),
        "recommended_action": str(payload.get("recommended_action") or data["recommended_action"]),
        "continue_loop": _as_bool(payload.get("continue_loop"), bool(data["continue_loop"])),
    }
    return {
        "metadata": _metadata(inputs, "cognition_worker"),
        "fields": fields,
        "cognition_to_skill_update": {
            "metadata": {
                "task_package": task_package(inputs),
                "loop_source": "generic_full_loop_validation",
                "backend": _backend_config(inputs).get("backend_id"),
            },
            "fields": {
                "next_iteration_skill_constraints": _as_string_list(
                    payload.get("next_iteration_skill_constraints"),
                    data.get("next_iteration_skill_constraints", ["Preserve task and evaluator definitions."]),
                ),
                "next_iteration_evaluator_constraints": _as_string_list(
                    payload.get("next_iteration_evaluator_constraints"),
                    data.get("next_iteration_evaluator_constraints", ["Use the declared evaluator."]),
                ),
                "next_iteration_task_refinements": _as_string_list(
                    payload.get("next_iteration_task_refinements"),
                    data.get("next_iteration_task_refinements", []),
                )
                if payload.get("next_iteration_task_refinements")
                else data.get("next_iteration_task_refinements", []),
                "search_priority_updates": _as_string_list(
                    payload.get("search_priority_updates"),
                    data.get("search_priority_updates", ["Follow the routing decision."]),
                ),
                "required_discriminating_tests": _as_string_list(
                    payload.get("required_discriminating_tests"),
                    data.get("required_discriminating_tests", ["Run one discriminating comparison."]),
                ),
                "summary": str(payload.get("update_summary") or data.get("update_summary") or "LLM-authored next-step update."),
            },
        },
    }
