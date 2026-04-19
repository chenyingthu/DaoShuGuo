#!/usr/bin/env python3
"""Minimal orchestrator for DaoShuGuo-v1 MVP."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
TASK_DIR = REPO_ROOT / "tasks" / "task001"
RUNS_DIR = REPO_ROOT / "runs" / "task001"
ANALYSIS_DIR = REPO_ROOT / "analysis" / "task001"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_schemas.py"
EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task001_evaluator.py"
BASELINE_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "baseline_solver.py"
VALIDATED_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "reactive_optimizer.py"
EXPERIMENTAL_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "reactive_optimizer_candidate.py"
WEAK_SHUNT_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_optimizer.py"
SKILL_REGISTRY_PATH = REPO_ROOT / "skills" / "registry.json"
COGNITION_REGISTRY_PATH = REPO_ROOT / "cognition" / "registry.json"
COGNITION_CARDS_DIR = REPO_ROOT / "cognition" / "cards"
COGNITION_FAILED_DIR = REPO_ROOT / "cognition" / "failed"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def object_tail(object_id: str) -> str:
    return object_id.split(".")[-1]


def update_skill_registry(
    run_id: str,
    when: str,
    used_skill_refs: list[dict[str, str]],
    produced_skill_refs: list[dict[str, str]],
) -> None:
    registry = load_json(SKILL_REGISTRY_PATH)
    skills = registry.setdefault("skills", [])
    index = {
        (entry.get("object_id"), entry.get("object_version")): entry
        for entry in skills
        if isinstance(entry, dict)
    }

    def ensure_entry(
        skill_ref: dict[str, str], role: str, default_status: str, default_path: str | None = None
    ) -> None:
        key = (skill_ref.get("object_id"), skill_ref.get("object_version"))
        entry = index.get(key)
        if entry is None:
            entry = {
                "object_id": skill_ref["object_id"],
                "object_version": skill_ref["object_version"],
                "path": default_path or "",
                "status": default_status,
            }
            skills.append(entry)
            index[key] = entry
        entry["last_seen_run_ref"] = run_id
        entry["last_seen_at"] = when
        if role == "used":
            entry["last_used_run_ref"] = run_id
            entry["last_used_at"] = when
        if role == "produced":
            entry["last_produced_run_ref"] = run_id
            entry["last_produced_at"] = when

    for skill_ref in used_skill_refs:
        ensure_entry(skill_ref, "used", "active")

    for skill_ref in produced_skill_refs:
        default_status = "draft" if "candidate" in skill_ref["object_id"] else "active"
        ensure_entry(skill_ref, "produced", default_status)

    registry["generated_at"] = when
    write_json(SKILL_REGISTRY_PATH, registry)


def write_cognition_asset_and_registry(cognition: dict[str, Any], run_id: str, when: str) -> Path:
    if cognition["cognition_type"] == "failure":
        target_dir = COGNITION_FAILED_DIR
    else:
        target_dir = COGNITION_CARDS_DIR
    filename = f"{object_tail(cognition['object_id'])}.yaml"
    target_path = target_dir / filename
    write_yaml(target_path, cognition)

    registry = load_json(COGNITION_REGISTRY_PATH)
    entries = registry.setdefault("cognition", [])
    key = (cognition["object_id"], cognition["object_version"])
    existing = None
    for entry in entries:
        if (
            isinstance(entry, dict)
            and entry.get("object_id") == key[0]
            and entry.get("object_version") == key[1]
        ):
            existing = entry
            break

    rel_path = str(target_path.relative_to(REPO_ROOT))
    if existing is None:
        entries.append(
            {
                "object_id": cognition["object_id"],
                "object_version": cognition["object_version"],
                "path": rel_path,
                "status": cognition["status"],
                "source_run_ref": run_id,
                "written_at": when,
            }
        )
    else:
        existing["path"] = rel_path
        existing["status"] = cognition["status"]
        existing["source_run_ref"] = run_id
        existing["written_at"] = when

    registry["generated_at"] = when
    write_json(COGNITION_REGISTRY_PATH, registry)
    return target_path


def load_validator():
    spec = spec_from_file_location("validate_schemas", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load validator module")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_evaluator_module():
    spec = spec_from_file_location("task001_evaluator", EVALUATOR_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load evaluator module")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_module(module_name: str, module_path: Path):
    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module {module_name}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ensure_valid_schemas() -> None:
    validator = load_validator()
    errors = validator.validate_samples(REPO_ROOT / "schemas")
    if errors:
        lines = [f"- {err.source}: {err.message}" for err in errors]
        raise RuntimeError("schema validation failed before orchestration:\n" + "\n".join(lines))


def next_run_serial() -> str:
    existing = sorted(RUNS_DIR.glob("run_*"))
    return f"{len(existing) + 1:04d}"


def grade_from_result(passed: bool) -> str:
    return "zhuoshi" if passed else "huimo"


def report_type_from_grade(grade: str) -> str:
    return "technical_note" if grade == "zhuoshi" else "discussion_memo"


def skill_version_for_id(skill_id: str) -> str:
    versions = {
        "skill.power.reactive_optimizer": "0.1.0",
        "skill.power.reactive_optimizer_candidate": "0.2.0",
        "skill.power.weak_bus_shunt_optimizer": "0.1.0",
    }
    return versions.get(skill_id, "0.1.0")


def build_cognition(passed: bool, serial: str, run_id: str, mode_tag: str) -> dict[str, Any]:
    now = utc_now()
    if mode_tag.startswith("real_weak-shunt"):
        success_statement = (
            "当前真实 weak-shunt 运行表明，在该任务设定下，基于弱节点识别的 shunt 补偿技能可相对基线形成阶段性改进。"
        )
        failure_statement = (
            "当前真实 weak-shunt 运行表明，该任务设定下的弱节点 shunt 补偿技能未能稳定满足评估要求。"
        )
    elif mode_tag.startswith("real_"):
        success_statement = (
            "当前真实运行表明，在该任务设定下，候选技能可相对基线形成阶段性改进。"
        )
        failure_statement = (
            "当前真实失败运行表明，替代候选技能在该任务设定下不能稳定满足约束。"
        )
    else:
        success_statement = (
            "当前demo运行表明，在该任务设定下，候选技能可相对基线形成阶段性改进。"
        )
        failure_statement = (
            "当前demo失败运行表明，替代候选技能在该任务设定下不能稳定满足约束。"
        )
    if passed:
        return {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.ieee33_reactive_opt_runtime_{serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {},
            "cognition_type": "candidate",
            "statement": success_statement,
            "evidence_refs": [run_id],
            "scope_boundary": {
                "task": "task.power.ieee33_reactive_opt",
                "mode": mode_tag
            },
            "confidence_level": "medium",
            "derived_from_run_refs": [run_id],
            "promotion_status": "proposed",
        }
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": f"cognition.power.ieee33_reactive_opt_runtime_failure_{serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "cognition_type": "failure",
        "statement": failure_statement,
        "evidence_refs": [run_id],
        "scope_boundary": {
            "task": "task.power.ieee33_reactive_opt",
            "mode": mode_tag
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [run_id],
        "promotion_status": "proposed",
    }


def load_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = load_yaml(TASK_DIR / "task.yaml")
    baseline = load_yaml(TASK_DIR / "baseline.yaml")
    evaluator = load_yaml(REPO_ROOT / "evaluators" / "task001_evaluator.yaml")
    constraints = load_yaml(TASK_DIR / "constraints.yaml")
    return task, baseline, evaluator, constraints


def build_run_artifacts(
    *,
    serial: str,
    now: str,
    task: dict[str, Any],
    evaluator: dict[str, Any],
    candidate_skill_id: str,
    evaluation: dict[str, Any],
    mode_tag: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    run_id = f"run.power.ieee33_reactive_opt.{serial}"
    run_dir = RUNS_DIR / f"run_{serial}"
    run_object = {
        "schema_version": "0.1.0",
        "object_type": "run",
        "object_id": run_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "archived",
        "metadata": {},
        "title": f"task001 {mode_tag} run {serial}",
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_status": "completed" if evaluation["passed"] else "failed_experiment",
        "started_at": now,
        "ended_at": now,
        "attempt_index": int(serial),
        "trigger_reason": mode_tag,
        "input_snapshot": {
            "task": {"object_id": task["object_id"], "object_version": task["object_version"]},
            "evaluator": {
                "object_id": evaluator["object_id"],
                "object_version": evaluator["object_version"],
            },
        },
        "skill_refs": {
            "used": [{"object_id": "skill.power.baseline_solver", "object_version": "0.1.0"}],
            "produced": [
                {
                    "object_id": candidate_skill_id,
                    "object_version": skill_version_for_id(candidate_skill_id),
                }
            ],
        },
        "result_summary": {
            "metrics": evaluation["candidate_solution"]["metrics"],
            "baseline_comparison": "improved" if evaluation["passed"] else "worse",
            "notes": evaluation["summary"],
        },
        "artifact_refs": [
            {"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")},
        ],
    }
    if not evaluation["passed"]:
        run_object["failure_summary"] = "candidate did not satisfy evaluator pass criteria"

    grade = grade_from_result(evaluation["passed"])
    taste_id = f"taste.power.ieee33_reactive_opt.{serial}"
    report_type = report_type_from_grade(grade)
    cognition = build_cognition(evaluation["passed"], serial, run_id, mode_tag)
    evidence_id = f"evidence.power.ieee33_reactive_opt.{serial}"
    evidence = {
        "schema_version": "0.1.0",
        "object_type": "evidence_bundle",
        "object_id": evidence_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_refs": [run_id],
        "artifact_refs": [
            {"kind": "run", "path": str(run_dir.relative_to(REPO_ROOT) / "run.yaml")},
            {"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")},
        ],
        "claim_scope": {"supported_claims": ["当前任务设定下的阶段性结论"]},
        "skill_refs": [candidate_skill_id],
        "cognition_refs": [cognition["object_id"]],
        "gaps": ["未覆盖多工况比较"],
    }
    taste = {
        "schema_version": "0.1.0",
        "object_type": "taste_assessment",
        "object_id": taste_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": task["object_id"],
        "run_refs": [run_id],
        "grade": grade,
        "grade_reasoning": (
            "真实运行相对基线获得阶段性改进，但证据范围仍受限于单任务单工况。"
            if evaluation["passed"]
            else "真实运行未达到评估要求，只适合作为失败讨论材料。"
        ),
        "claim_ceiling": (
            "可报告为当前真实任务设定下的阶段性有效方法，不可上升为普遍规律。"
            if evaluation["passed"]
            else "只能报告当前真实任务失败，不得包装成有效成果。"
        ),
        "recommended_report_type": report_type,
        "evidence_refs": [evidence_id],
        "review_status": "reviewed",
    }
    trace_id = f"agent_trace.power.ieee33_reactive_opt.{serial}"
    prompt_obs_id = f"prompt_observation.power.ieee33_reactive_opt.{serial}"
    prompt_observation = {
        "schema_version": "0.1.0",
        "object_type": "prompt_observation",
        "object_id": prompt_obs_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "observation_kind": "quality_improvement" if evaluation["passed"] else "process_drift",
        "statement": (
            "真实运行中，基线比较与分级约束继续抑制了过度表述。"
            if evaluation["passed"]
            else "真实失败运行中，系统仍将结果压到失败讨论材料。"
        ),
        "severity": "medium",
        "suggested_action": "保留基线比较与成果分级为真实任务默认约束。",
    }
    agent_trace = {
        "schema_version": "0.1.0",
        "object_type": "agent_trace",
        "object_id": trace_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "agent_role": "orchestrator",
        "trace_summary": "系统完成了真实任务加载、真实求解、评估、分级、证据组织和报告写回。",
        "event_count": 7,
        "prompt_observation_refs": [prompt_obs_id],
        "notable_behaviors": [
            "先比较基线再评估 candidate",
            "真实运行后再做 taste assessment",
            "报告继续受 taste_assessment 约束",
        ],
    }
    report_id = f"report.power.ieee33_reactive_opt.{'note' if evaluation['passed'] else 'memo'}_{serial}"
    report = {
        "schema_version": "0.1.0",
        "object_type": "report",
        "object_id": report_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": task["object_id"],
        "report_type": report_type,
        "title": f"task001 {mode_tag} report {serial}",
        "summary": (
            "真实运行相对基线获得阶段性改进。"
            if evaluation["passed"]
            else "真实运行未达到评估要求，应作为失败材料归档。"
        ),
        "evidence_bundle_refs": [evidence_id],
        "taste_assessment_ref": taste_id,
        "audience": "internal_team",
        "boundary_statement": "本报告仅对应当前 case33bw 单工况任务，不构成普适结论。",
        "failure_summary": None if evaluation["passed"] else run_object["failure_summary"],
        "next_steps": ["增加多工况复现", "评估更强 candidate 技能"],
        "claim_summary": [taste["claim_ceiling"]],
    }
    run_object["agent_trace_refs"] = [{"kind": "trace", "object_id": trace_id}]
    evidence["taste_assessment_ref"] = taste_id
    evidence["report_refs"] = [report_id]
    return run_object, cognition, taste, evidence, agent_trace, prompt_observation, report


def write_run_outputs(
    run_dir: Path,
    run_object: dict[str, Any],
    cognition: dict[str, Any],
    taste: dict[str, Any],
    evidence: dict[str, Any],
    agent_trace: dict[str, Any],
    prompt_observation: dict[str, Any],
    report: dict[str, Any],
    metrics_payload: dict[str, Any],
    now: str,
) -> None:
    with (run_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)
    outputs = {
        "run.yaml": run_object,
        "cognition.yaml": cognition,
        "taste_assessment.yaml": taste,
        "evidence_bundle.yaml": evidence,
        "agent_trace.yaml": agent_trace,
        "prompt_observation.yaml": prompt_observation,
        "report.yaml": report,
    }
    for filename, payload in outputs.items():
        write_yaml(run_dir / filename, payload)
    update_skill_registry(
        run_id=run_object["object_id"],
        when=now,
        used_skill_refs=run_object["skill_refs"]["used"],
        produced_skill_refs=run_object["skill_refs"]["produced"],
    )
    cognition_asset_path = write_cognition_asset_and_registry(
        cognition, run_id=run_object["object_id"], when=now
    )
    write_yaml(run_dir / "evidence_bundle.yaml", evidence)
    write_yaml(run_dir / "cognition.yaml", cognition)
    with (run_dir / "writeback.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "skills_registry": str(SKILL_REGISTRY_PATH.relative_to(REPO_ROOT)),
                "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
                "cognition_asset": str(cognition_asset_path.relative_to(REPO_ROOT)),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")


def serial_from_run_id(run_id: str) -> str:
    return run_id.split(".")[-1]


def run_dir_from_id(run_id: str) -> Path:
    return RUNS_DIR / f"run_{serial_from_run_id(run_id)}"


def load_run_payload(run_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    run_dir = run_dir_from_id(run_id)
    return (
        load_yaml(run_dir / "run.yaml"),
        load_json(run_dir / "metrics.json"),
        load_yaml(run_dir / "report.yaml"),
    )


def compare_metric_pair(left: float, right: float, direction: str) -> dict[str, Any]:
    if direction == "lower_is_better":
        winner = "left" if left < right else "right" if right < left else "tie"
    elif direction == "higher_is_better":
        winner = "left" if left > right else "right" if right > left else "tie"
    elif direction == "constraint_only":
        winner = "left" if left < right else "right" if right < left else "tie"
    else:
        winner = "tie"
    return {"left": left, "right": right, "direction": direction, "winner": winner, "delta_right_minus_left": right - left}


def strategy_name_from_run(run_obj: dict[str, Any]) -> str:
    return str(run_obj.get("trigger_reason", "unknown"))


def build_comparison_cognition(
    *,
    serial: str,
    left_run_id: str,
    right_run_id: str,
    left_strategy: str,
    right_strategy: str,
    metric_comparisons: dict[str, Any],
    winner_label: str,
    winner_run_ref: str,
) -> dict[str, Any]:
    now = utc_now()
    if winner_label == "left":
        statement = (
            f"在当前单工况 case33bw 任务中，策略 `{left_strategy}` 在 evaluator 指标上整体优于 `{right_strategy}`。"
        )
    elif winner_label == "right":
        statement = (
            f"在当前单工况 case33bw 任务中，策略 `{right_strategy}` 在 evaluator 指标上整体优于 `{left_strategy}`。"
        )
    else:
        statement = (
            f"在当前单工况 case33bw 任务中，策略 `{left_strategy}` 与 `{right_strategy}` 未形成明确的单边优势。"
        )
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": f"cognition.power.strategy_comparison_{serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "cognition_type": "candidate",
        "statement": statement,
        "evidence_refs": [left_run_id, right_run_id],
        "scope_boundary": {
            "task": "task.power.ieee33_reactive_opt",
            "mode": "strategy_comparison",
            "left_strategy": left_strategy,
            "right_strategy": right_strategy,
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [left_run_id, right_run_id],
        "promotion_status": "proposed",
        "uncertainty_notes": (
            f"该认知仅基于单工况比较，winner={winner_label}，关键比较={metric_comparisons}"
        ),
    }


def compare_runs(left_run_id: str, right_run_id: str) -> Path:
    ensure_valid_schemas()
    from tasks.task001.runtime_helpers import objective

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    comparison_serial = f"{len(sorted(ANALYSIS_DIR.glob('compare_*'))) + 1:04d}"
    compare_dir = ANALYSIS_DIR / f"compare_{comparison_serial}"
    compare_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    left_run, left_metrics_payload, left_report = load_run_payload(left_run_id)
    right_run, right_metrics_payload, right_report = load_run_payload(right_run_id)
    left_strategy = strategy_name_from_run(left_run)
    right_strategy = strategy_name_from_run(right_run)
    left_metrics = left_metrics_payload["candidate_solution"]["metrics"]
    right_metrics = right_metrics_payload["candidate_solution"]["metrics"]
    directions = {
        "loss": "lower_is_better",
        "voltage_deviation": "lower_is_better",
        "constraint_violation": "constraint_only",
    }
    metric_comparisons = {
        metric: compare_metric_pair(left_metrics[metric], right_metrics[metric], direction)
        for metric, direction in directions.items()
    }
    left_score = objective(left_metrics)
    right_score = objective(right_metrics)
    winner_label = "left" if left_score < right_score else "right" if right_score < left_score else "tie"
    winner_run_ref = left_run_id if winner_label == "left" else right_run_id if winner_label == "right" else ""

    comparison_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_comparison",
        "object_id": f"comparison.power.ieee33_reactive_opt.{comparison_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": left_run["task_ref"],
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "metric_comparisons": metric_comparisons,
        "objective_scores": {"left": left_score, "right": right_score},
        "winner_run_ref": winner_run_ref,
        "summary": (
            f"在当前任务下，{left_strategy} 与 {right_strategy} 的对照完成，winner={winner_label}。"
        ),
        "report_refs": [
            left_report["object_id"],
            right_report["object_id"],
        ],
    }

    cognition = build_comparison_cognition(
        serial=comparison_serial,
        left_run_id=left_run_id,
        right_run_id=right_run_id,
        left_strategy=left_strategy,
        right_strategy=right_strategy,
        metric_comparisons=metric_comparisons,
        winner_label=winner_label,
        winner_run_ref=winner_run_ref,
    )
    cognition_path = write_cognition_asset_and_registry(cognition, run_id=winner_run_ref or left_run_id, when=now)
    comparison_object["cognition_refs"] = [cognition["object_id"]]
    comparison_report = {
        "created_at": now,
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "winner": winner_label,
        "winner_run_ref": winner_run_ref,
        "summary": comparison_object["summary"],
        "claim_ceiling": "该比较仅支持当前单工况下的策略相对判断，不支持普适结论。",
    }

    write_yaml(compare_dir / "strategy_comparison.yaml", comparison_object)
    write_yaml(compare_dir / "cognition.yaml", cognition)
    with (compare_dir / "comparison_report.json").open("w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with (compare_dir / "writeback.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "comparison_object": str((compare_dir / "strategy_comparison.yaml").relative_to(REPO_ROOT)),
                "cognition_asset": str(cognition_path.relative_to(REPO_ROOT)),
                "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")
    return compare_dir


def run_demo(mode: str) -> Path:
    ensure_valid_schemas()
    evaluator_module = load_evaluator_module()

    task = load_yaml(TASK_DIR / "task.yaml")
    baseline = load_yaml(TASK_DIR / "baseline.yaml")
    evaluator = load_yaml(REPO_ROOT / "evaluators" / "task001_evaluator.yaml")

    baseline_metrics = baseline["metric_expectations"]
    candidate_metrics = evaluator_module.demo_candidate_metrics(mode)
    evaluation = evaluator_module.evaluate_candidate(candidate_metrics, baseline_metrics)

    serial = next_run_serial()
    run_dir = RUNS_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    candidate_skill_id = (
        "skill.power.reactive_optimizer"
        if evaluation["passed"]
        else "skill.power.reactive_optimizer_candidate"
    )
    run_object, cognition, taste, evidence, agent_trace, prompt_observation, report = build_run_artifacts(
        serial=serial,
        now=now,
        task=task,
        evaluator=evaluator,
        candidate_skill_id=candidate_skill_id,
        evaluation={
            **evaluation,
            "baseline_solution": {"metrics": baseline_metrics},
            "candidate_solution": {"metrics": candidate_metrics},
        },
        mode_tag=f"demo_{mode}",
    )
    write_run_outputs(
        run_dir,
        run_object,
        cognition,
        taste,
        evidence,
        agent_trace,
        prompt_observation,
        report,
        {
            "candidate_metrics": candidate_metrics,
            "baseline_metrics": baseline_metrics,
            "evaluation": evaluation,
        },
        now,
    )

    return run_dir


def solver_for_strategy(strategy: str, mode: str) -> tuple[str, Path]:
    if strategy == "ext-grid":
        if mode == "success":
            return "skill.power.reactive_optimizer", VALIDATED_SOLVER_PATH
        return "skill.power.reactive_optimizer_candidate", EXPERIMENTAL_SOLVER_PATH
    if strategy == "weak-shunt":
        return "skill.power.weak_bus_shunt_optimizer", WEAK_SHUNT_SOLVER_PATH
    raise ValueError(f"unsupported strategy: {strategy}")


def run_real(mode: str, strategy: str) -> Path:
    ensure_valid_schemas()
    evaluator_module = load_evaluator_module()
    baseline_solver = load_module("task001_baseline_solver", BASELINE_SOLVER_PATH)
    candidate_skill_id, solver_path = solver_for_strategy(strategy, mode)
    candidate_solver = load_module("task001_candidate_solver", solver_path)

    task, baseline, evaluator, constraints = load_real_inputs()
    serial = next_run_serial()
    run_dir = RUNS_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    constraint_set = constraints["solver"]
    baseline_solution_raw = baseline_solver.solve("case33bw", constraint_set)
    candidate_solution_raw = candidate_solver.solve("case33bw", constraint_set)
    baseline_solution = {
        "control_settings": baseline_solution_raw["control_settings"],
        "metrics": baseline_solution_raw["baseline_solution"],
    }
    candidate_solution = {
        "control_settings": candidate_solution_raw["control_settings"],
        "metrics": candidate_solution_raw["reactive_power_settings"],
    }
    evaluation = evaluator_module.evaluate_real_solution(baseline_solution, candidate_solution)

    run_object, cognition, taste, evidence, agent_trace, prompt_observation, report = build_run_artifacts(
        serial=serial,
        now=now,
        task=task,
        evaluator=evaluator,
        candidate_skill_id=candidate_skill_id,
        evaluation=evaluation,
        mode_tag=f"real_{strategy}_{mode}",
    )
    write_run_outputs(
        run_dir,
        run_object,
        cognition,
        taste,
        evidence,
        agent_trace,
        prompt_observation,
        report,
        {
            "baseline_solution": baseline_solution,
            "candidate_solution": candidate_solution,
            "evaluation": evaluation,
        },
        now,
    )
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="DaoShuGuo-v1 orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate schema samples")
    demo = sub.add_parser("demo-run", help="Run a demo task001 orchestration cycle")
    demo.add_argument("--mode", choices=["success", "failure"], default="success")
    real = sub.add_parser("real-run", help="Run a real pandapower-backed task001 cycle")
    real.add_argument("--mode", choices=["success", "failure"], default="success")
    real.add_argument("--strategy", choices=["ext-grid", "weak-shunt"], default="ext-grid")
    compare = sub.add_parser("compare-runs", help="Compare two task001 runs structurally")
    compare.add_argument("--left-run-id", required=True)
    compare.add_argument("--right-run-id", required=True)

    args = parser.parse_args()

    if args.command == "validate":
        ensure_valid_schemas()
        print("Schema validation passed.")
        return 0

    if args.command == "demo-run":
        run_dir = run_demo(args.mode)
        print(f"Demo run written to {run_dir}")
        return 0

    if args.command == "real-run":
        run_dir = run_real(args.mode, args.strategy)
        print(f"Real run written to {run_dir}")
        return 0

    if args.command == "compare-runs":
        compare_dir = compare_runs(args.left_run_id, args.right_run_id)
        print(f"Comparison written to {compare_dir}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
