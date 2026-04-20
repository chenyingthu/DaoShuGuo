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
LITERATURE_DIR = REPO_ROOT / "literature"
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


def latest_nonempty_dir(parent: Path, pattern: str) -> Path:
    candidates = []
    for path in sorted(parent.glob(pattern)):
        if path.is_dir() and any(path.iterdir()):
            candidates.append(path)
    if not candidates:
        raise FileNotFoundError(f"no non-empty directories matching {parent / pattern}")
    return candidates[-1]


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


def produced_skill_id_from_run(run_obj: dict[str, Any]) -> str:
    produced = run_obj.get("skill_refs", {}).get("produced", [])
    if produced and isinstance(produced[0], dict):
        return str(produced[0].get("object_id", "unknown"))
    return "unknown"


def scale_value(label: str) -> int:
    mapping = {"low": 1, "medium": 2, "high": 3}
    return mapping.get(label, 0)


def load_seed_papers() -> list[dict[str, Any]]:
    data = load_yaml(LITERATURE_DIR / "task001-seed-papers.yaml")
    return data.get("seed_papers", [])


def load_source_overlays() -> list[dict[str, Any]]:
    overlay_path = LITERATURE_DIR / "task001-source-overlays.yaml"
    if not overlay_path.exists():
        return []
    data = load_yaml(overlay_path)
    return data.get("overlay_sources", [])


def load_source_inputs() -> list[dict[str, Any]]:
    input_dir = LITERATURE_DIR / "source_inputs"
    if not input_dir.exists():
        return []
    return [load_yaml(path) for path in sorted(input_dir.glob("*.yaml"))]


def load_raw_excerpt_inputs() -> list[dict[str, Any]]:
    raw_dir = LITERATURE_DIR / "raw_excerpts" / "task001"
    if not raw_dir.exists():
        return []
    return [load_yaml(path) for path in sorted(raw_dir.glob("*.yaml"))]


def literature_sources_dir() -> Path:
    path = LITERATURE_DIR / "sources"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_explanation_points_for_family(method_family: str) -> list[str]:
    if method_family == "capacitor_placement_optimization":
        return [
            "控制对象直接作用于无功补偿设备或电容器配置",
            "典型目标包括降低网损、改善电压偏差和约束满足",
            "方法语义更接近配电网无功补偿问题本体",
        ]
    return [
        "控制对象更偏向电压边界、调压设备或协调控制器",
        "目标同样可能包括损耗、电压质量和约束满足",
        "方法语义更接近 Volt/Var control 控制问题，而非直接补偿配置问题",
    ]


def default_concept_tags_for_family(method_family: str) -> list[str]:
    if method_family == "capacitor_placement_optimization":
        return ["capacitor placement", "reactive compensation", "weak bus"]
    return ["volt/var control", "voltage regulation", "distribution control"]


def ingest_seed_literature() -> Path:
    ensure_valid_schemas()
    sources_dir = literature_sources_dir()
    now = utc_now()
    # Seed-curated default sources
    for paper in load_seed_papers():
        paper_key = paper_key_from_ref_id(paper["ref_id"])
        source_object = {
            "schema_version": "0.1.0",
            "object_type": "literature_source",
            "object_id": f"literature_source.power.{paper_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref_id": paper["ref_id"],
            "title": paper["title"],
            "source_kind": paper.get("source_kind", "seed_curated"),
            "method_family": paper["method_family"],
            "tags": paper.get("tags", []),
            "relevance_notes": paper.get("relevance_notes", ""),
            "method_notes": [paper.get("method_excerpt_seed", paper.get("relevance_notes", ""))],
            "explanation_notes": [paper.get("explanation_excerpt_seed", paper.get("relevance_notes", ""))],
            "explanation_point_notes": paper.get("explanation_point_notes", []),
            "provenance_notes": [
                "由 task001-seed-papers.yaml 物化生成的轻量文献源对象",
                f"source_kind={paper.get('source_kind', 'seed_curated')}",
            ],
        }
        for optional_field in ("year", "doi", "url"):
            optional_value = paper.get(optional_field)
            if optional_value is not None:
                source_object[optional_field] = optional_value
        write_yaml(sources_dir / f"{paper_key}.yaml", source_object)
    # Higher-fidelity overlay sources
    paper_index = {paper["ref_id"]: paper for paper in load_seed_papers()}
    for overlay in load_source_overlays():
        base = paper_index.get(overlay["paper_ref_id"])
        if base is None:
            continue
        paper_key = paper_key_from_ref_id(overlay["paper_ref_id"])
        source_key = overlay.get("source_key", overlay["source_kind"])
        source_object = {
            "schema_version": "0.1.0",
            "object_type": "literature_source",
            "object_id": f"literature_source.power.{paper_key}.{source_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref_id": overlay["paper_ref_id"],
            "title": base["title"],
            "source_kind": overlay["source_kind"],
            "method_family": base["method_family"],
            "tags": base.get("tags", []),
            "relevance_notes": base.get("relevance_notes", ""),
            "method_notes": overlay.get("method_notes", []),
            "explanation_notes": overlay.get("explanation_notes", []),
            "explanation_point_notes": overlay.get("explanation_point_notes", []),
            "provenance_notes": overlay.get("provenance_notes", []),
        }
        for optional_field in ("year", "doi", "url"):
            optional_value = base.get(optional_field)
            if optional_value is not None:
                source_object[optional_field] = optional_value
        write_yaml(sources_dir / f"{paper_key}.{source_key}.yaml", source_object)
    # External/manual source input files
    for source_input in load_source_inputs():
        base = paper_index.get(source_input["paper_ref_id"])
        if base is None:
            continue
        paper_key = paper_key_from_ref_id(source_input["paper_ref_id"])
        source_key = source_input.get("source_key", source_input["source_kind"])
        source_object = {
            "schema_version": "0.1.0",
            "object_type": "literature_source",
            "object_id": f"literature_source.power.{paper_key}.{source_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref_id": source_input["paper_ref_id"],
            "title": base["title"],
            "source_kind": source_input["source_kind"],
            "method_family": base["method_family"],
            "tags": base.get("tags", []),
            "relevance_notes": base.get("relevance_notes", ""),
            "method_notes": source_input.get("method_notes", []),
            "explanation_notes": source_input.get("explanation_notes", []),
            "explanation_point_notes": source_input.get("explanation_point_notes", []),
            "provenance_notes": source_input.get("provenance_notes", []),
        }
        for optional_field in ("year", "doi", "url"):
            optional_value = base.get(optional_field)
            if optional_value is not None:
                source_object[optional_field] = optional_value
        write_yaml(sources_dir / f"{paper_key}.{source_key}.yaml", source_object)
    # Raw excerpt inputs are a lightweight bridge toward semi-automated fulltext ingestion.
    for raw_input in load_raw_excerpt_inputs():
        base = paper_index.get(raw_input["paper_ref_id"])
        if base is None:
            continue
        paper_key = paper_key_from_ref_id(raw_input["paper_ref_id"])
        source_key = raw_input.get("source_key", "raw_fulltext")
        source_object = {
            "schema_version": "0.1.0",
            "object_type": "literature_source",
            "object_id": f"literature_source.power.{paper_key}.{source_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref_id": raw_input["paper_ref_id"],
            "title": base["title"],
            "source_kind": raw_input.get("source_kind", "fulltext_excerpt"),
            "method_family": base["method_family"],
            "tags": base.get("tags", []),
            "relevance_notes": base.get("relevance_notes", ""),
            "method_notes": raw_input.get("method_fragments", []),
            "explanation_notes": raw_input.get("explanation_fragments", []),
            "explanation_point_notes": raw_input.get("explanation_fragments", []),
            "provenance_notes": raw_input.get("provenance_notes", []),
        }
        for optional_field in ("year", "doi", "url"):
            optional_value = base.get(optional_field)
            if optional_value is not None:
                source_object[optional_field] = optional_value
        write_yaml(sources_dir / f"{paper_key}.{source_key}.yaml", source_object)
    return sources_dir


def load_literature_sources() -> list[dict[str, Any]]:
    sources_dir = literature_sources_dir()
    source_files = sorted(sources_dir.glob("*.yaml"))
    if not source_files:
        ingest_seed_literature()
        source_files = sorted(sources_dir.glob("*.yaml"))
    return [load_yaml(path) for path in source_files]


def source_priority(source_kind: str) -> int:
    priorities = {
        "seed_curated": 1,
        "manual_summary": 2,
        "abstract_excerpt": 3,
        "fulltext_excerpt": 4,
    }
    return priorities.get(source_kind, 0)


def source_strength_label(source_kind: str) -> str:
    if source_kind == "fulltext_excerpt":
        return "high"
    if source_kind == "abstract_excerpt":
        return "medium"
    return "low"


def paper_key_from_ref_id(ref_id: str) -> str:
    return ref_id.split(".", 1)[1] if "." in ref_id else ref_id


def build_literature_cards(max_source_kind: str | None = None) -> Path:
    ensure_valid_schemas()
    papers_dir = LITERATURE_DIR / "papers"
    excerpts_dir = LITERATURE_DIR / "excerpts"
    methods_dir = LITERATURE_DIR / "cards" / "methods"
    explanations_dir = LITERATURE_DIR / "cards" / "explanations"
    for path in [papers_dir, excerpts_dir, methods_dir, explanations_dir]:
        path.mkdir(parents=True, exist_ok=True)

    now = utc_now()
    literature_sources = load_literature_sources()
    grouped_sources: dict[str, list[dict[str, Any]]] = {}
    for source in literature_sources:
        grouped_sources.setdefault(source["paper_ref_id"], []).append(source)

    for paper_ref_id, source_group in grouped_sources.items():
        source_candidates = source_group
        if max_source_kind is not None:
            max_priority = source_priority(max_source_kind)
            source_candidates = [
                item
                for item in source_group
                if source_priority(item.get("source_kind", "seed_curated")) <= max_priority
            ]
        if not source_candidates:
            source_candidates = source_group
        selected_source = sorted(
            source_candidates,
            key=lambda item: source_priority(item.get("source_kind", "seed_curated")),
            reverse=True,
        )[0]
        paper_key = paper_key_from_ref_id(paper_ref_id)
        method_family = selected_source.get("method_family", "unknown")
        tags = selected_source.get("tags", [])
        relevance_notes = selected_source.get("relevance_notes", "")
        year = selected_source.get("year")
        doi = selected_source.get("doi")
        url = selected_source.get("url")
        source_kind = selected_source.get("source_kind", "seed_curated")
        source_ref = selected_source["object_id"]
        paper_record = {
            "schema_version": "0.1.0",
            "object_type": "paper_record",
            "object_id": f"paper_record.power.{paper_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "title": selected_source["title"],
            "year": year,
            "method_family": method_family,
            "tags": tags,
            "relevance_notes": relevance_notes,
        }
        if doi is not None:
            paper_record["doi"] = doi
        if url is not None:
            paper_record["url"] = url
        method_excerpt = {
            "schema_version": "0.1.0",
            "object_type": "paper_excerpt",
            "object_id": f"paper_excerpt.power.{paper_key}.method",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref": paper_record["object_id"],
            "source_ref": source_ref,
            "source_kind": source_kind,
            "excerpt_kind": "method",
            "granularity": "summary",
            "content": selected_source.get("method_notes", [""])[0],
            "notes": [f"当前由 {source_ref} 的 method_notes 驱动的方法摘要片段"],
        }
        explanation_excerpt = {
            "schema_version": "0.1.0",
            "object_type": "paper_excerpt",
            "object_id": f"paper_excerpt.power.{paper_key}.explanation",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {},
            "paper_ref": paper_record["object_id"],
            "source_ref": source_ref,
            "source_kind": source_kind,
            "excerpt_kind": "explanation",
            "granularity": "summary",
            "content": selected_source.get(
                "explanation_notes",
                ["该文献代表的控制/优化路线可作为当前本地策略的外部语义参照。"],
            )[0],
            "notes": [f"当前由 {source_ref} 的 explanation_notes 驱动的解释摘要片段"],
        }

        if method_family == "capacitor_placement_optimization":
            method_summary = selected_source.get("method_notes", [""])[0] or "该文献属于电容器/无功补偿配置优化方法家族。"
            control_signature = "reactive_compensation"
            optimization_style = "placement_and_sizing"
        else:
            method_summary = selected_source.get("method_notes", [""])[0] or "该文献属于 Volt/Var control 方法家族。"
            control_signature = "boundary_voltage_tuning"
            optimization_style = "volt_var_control"
        explanation_summary = selected_source.get("explanation_notes", [""])[0] or "该文献提供当前问题的外部解释参照。"
        explanation_points = selected_source.get("explanation_point_notes") or default_explanation_points_for_family(
            method_family
        )
        concept_tags = list(
            dict.fromkeys([*default_concept_tags_for_family(method_family), *selected_source.get("tags", [])])
        )

        explanation_excerpt_refs = [explanation_excerpt["object_id"]]
        point_excerpt_payloads = []
        for idx, point in enumerate(explanation_points, start=1):
            point_excerpt = {
                "schema_version": "0.1.0",
                "object_type": "paper_excerpt",
                "object_id": f"paper_excerpt.power.{paper_key}.explanation_point_{idx}",
                "object_version": "0.1.0",
                "created_at": now,
                "updated_at": now,
                "status": "reviewed",
                "metadata": {},
                "paper_ref": paper_record["object_id"],
                "source_ref": source_ref,
                "source_kind": source_kind,
                "excerpt_kind": "explanation",
                "granularity": "point",
                "content": point,
                "notes": [f"当前由 {source_ref} 的 explanation_point_notes 驱动的细粒度解释片段。"],
            }
            point_excerpt_payloads.append(point_excerpt)
            explanation_excerpt_refs.append(point_excerpt["object_id"])

        method_card = {
            "schema_version": "0.1.0",
            "object_type": "method_card",
            "object_id": f"method_card.power.{paper_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {"source_ref": source_ref, "source_kind": source_kind},
            "paper_ref": paper_record["object_id"],
            "method_family": method_family,
            "method_summary": method_summary,
            "control_signature": control_signature,
            "optimization_style": optimization_style,
            "excerpt_refs": [method_excerpt["object_id"]],
            "notes": [
                relevance_notes or f"当前由 {source_ref} 提供文献方法语义。",
                f"selected_source_kind={source_kind}",
            ],
        }

        explanation_card = {
            "schema_version": "0.1.0",
            "object_type": "explanation_card",
            "object_id": f"explanation_card.power.{paper_key}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "reviewed",
            "metadata": {"source_ref": source_ref, "source_kind": source_kind},
            "paper_ref": paper_record["object_id"],
            "explanation_summary": explanation_summary,
            "explanation_points": explanation_points,
            "scope_boundary": {"task": "task.power.ieee33_reactive_opt"},
            "concept_tags": concept_tags,
            "excerpt_refs": explanation_excerpt_refs,
            "notes": [f"当前优先由 {source_ref} 驱动解释卡片生成，不是原文全文抽取。"],
        }

        write_yaml(papers_dir / f"{paper_key}.yaml", paper_record)
        write_yaml(excerpts_dir / f"{paper_key}-method.yaml", method_excerpt)
        write_yaml(excerpts_dir / f"{paper_key}-explanation.yaml", explanation_excerpt)
        for idx, point_excerpt in enumerate(point_excerpt_payloads, start=1):
            write_yaml(excerpts_dir / f"{paper_key}-explanation-point-{idx}.yaml", point_excerpt)
        write_yaml(methods_dir / f"{paper_key}.yaml", method_card)
        write_yaml(explanations_dir / f"{paper_key}.yaml", explanation_card)

    return LITERATURE_DIR


def resolve_cognition_path(cognition_ref: str) -> Path:
    registry = load_json(COGNITION_REGISTRY_PATH)
    for entry in registry.get("cognition", []):
        if isinstance(entry, dict) and entry.get("object_id") == cognition_ref:
            return REPO_ROOT / str(entry["path"])
    raise FileNotFoundError(f"cognition ref not found in registry: {cognition_ref}")


def resolve_paper_excerpt_path(excerpt_ref: str) -> Path:
    if not excerpt_ref.startswith("paper_excerpt.power."):
        raise FileNotFoundError(f"unsupported excerpt ref: {excerpt_ref}")
    suffix = excerpt_ref.replace("paper_excerpt.power.", "")
    if ".method" in excerpt_ref:
        paper_key = suffix.rsplit(".method", 1)[0]
        return LITERATURE_DIR / "excerpts" / f"{paper_key}-method.yaml"
    if ".explanation_point_" in excerpt_ref:
        paper_key, point_part = suffix.split(".explanation_point_", 1)
        return LITERATURE_DIR / "excerpts" / f"{paper_key}-explanation-point-{point_part}.yaml"
    if ".explanation" in excerpt_ref:
        paper_key = suffix.rsplit(".explanation", 1)[0]
        return LITERATURE_DIR / "excerpts" / f"{paper_key}-explanation.yaml"
    raise FileNotFoundError(f"unable to resolve excerpt ref: {excerpt_ref}")


EXCERPT_DIRECT_SUPPORT_TOKENS = (
    "问题本体",
    "无功补偿",
    "补偿配置",
    "补偿设备",
    "电容器",
    "电容补偿",
    "容量配置",
    "位置与容量",
    "选址定容",
    "候选节点",
    "shunt",
    "capacitor placement",
    "reactive compensation",
)

EXCERPT_TARGET_SIMILARITY_TOKENS = (
    "损耗",
    "loss",
    "电压",
    "voltage",
    "电压偏差",
    "电压质量",
    "经济性",
    "成本",
    "稳定性",
    "约束",
)

EXCERPT_BOUNDARY_TOKENS = (
    "volt/var",
    "调压",
    "协调",
    "oltc",
    "分接头",
    "robust",
    "鲁棒",
    "der",
    "prosumer",
    "regulator",
    "controller",
    "协调调度",
)

EXCERPT_CONFLICT_TOKENS = (
    "不适用",
    "无助于",
    "无法改善",
    "恶化",
    "冲突",
)

EXCERPT_CONTRAST_TOKENS = (
    "而不是",
    "区别于",
    "不同于",
    "更接近",
)


def contains_any_token(content: str, tokens: tuple[str, ...]) -> bool:
    normalized = content.lower()
    return any(token.lower() in normalized for token in tokens)


def classify_explanation_excerpt_relation(
    *,
    cognition_statement: str,
    card: dict[str, Any],
    excerpt: dict[str, Any],
) -> tuple[str, str, str]:
    if "问题本体" not in cognition_statement:
        return "unclear", "当前规则未覆盖该类本地认知。", "cognition_guard"

    content = str(excerpt.get("content", ""))
    has_direct_support = contains_any_token(content, EXCERPT_DIRECT_SUPPORT_TOKENS)
    has_target_similarity = contains_any_token(content, EXCERPT_TARGET_SIMILARITY_TOKENS)
    has_boundary = contains_any_token(content, EXCERPT_BOUNDARY_TOKENS)
    has_conflict = contains_any_token(content, EXCERPT_CONFLICT_TOKENS)
    has_contrast = contains_any_token(content, EXCERPT_CONTRAST_TOKENS)

    if has_conflict:
        return "conflicts", "片段文本直接包含负向或冲突性表述，应记为冲突证据。", "excerpt_content"

    if has_direct_support:
        if has_boundary and not has_target_similarity:
            return "supplements", "片段虽涉及邻近控制语境，但没有直接给出问题本体支持。", "excerpt_content"
        return "supports", "片段文本直接提到补偿配置/候选节点/问题本体，可作为支持证据。", "excerpt_content"

    if has_boundary and (has_contrast or excerpt.get("granularity") == "point"):
        return "supplements", "片段文本主要在界定 Volt/Var/调压类边界，可作为补充参照。", "excerpt_content"

    if has_target_similarity:
        return "similar", "片段文本只体现目标层面的相似性，尚不足以形成直接支持。", "excerpt_content"

    concept_tags = set(card.get("concept_tags", []))
    if "reactive compensation" in concept_tags:
        return "supplements", "当前只从卡片标签推知其属于补偿配置家族，但 excerpt 文本证据不足。", "card_tag_fallback"
    if "volt/var control" in concept_tags:
        return "supplements", "当前只从卡片标签推知其属于 Volt/Var 家族，但 excerpt 文本证据不足。", "card_tag_fallback"
    return "unclear", "当前无法确定该解释片段与本地认知的关系。", "no_signal"


def build_explanation_relation_summary(per_card_relations: dict[str, dict[str, Any]]) -> str:
    card_counts = {"supports": 0, "supplements": 0, "similar": 0, "conflicts": 0, "unclear": 0}
    excerpt_counts = {"supports": 0, "supplements": 0, "similar": 0, "conflicts": 0, "unclear": 0}
    for card_relation in per_card_relations.values():
        relation = card_relation.get("relation")
        if relation in card_counts:
            card_counts[relation] += 1
        relation_counts = card_relation.get("relation_counts", {})
        if isinstance(relation_counts, dict):
            for key in excerpt_counts:
                excerpt_counts[key] += int(relation_counts.get(key, 0))

    parts: list[str] = []
    if card_counts["supports"] > 0:
        parts.append(
            f"{card_counts['supports']} 张 explanation card 含 excerpt 级直接支持（{excerpt_counts['supports']} 条 excerpt）"
        )
    if card_counts["supplements"] > 0:
        parts.append(
            f"{card_counts['supplements']} 张 card 主要提供边界性补充（{excerpt_counts['supplements']} 条 excerpt）"
        )
    if card_counts["similar"] > 0:
        parts.append(
            f"{card_counts['similar']} 张 card 仅体现目标相似（{excerpt_counts['similar']} 条 excerpt）"
        )
    if card_counts["conflicts"] > 0:
        parts.append(
            f"{card_counts['conflicts']} 张 card 出现冲突证据（{excerpt_counts['conflicts']} 条 excerpt）"
        )
    if not parts:
        parts.append("当前没有形成明确的 excerpt 级支持/补充/相似判断")
    return "；".join(parts) + "。"


def explanation_alignment_excerpt_refs(alignment: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for card_relation in alignment.get("per_card_relations", {}).values():
        if not isinstance(card_relation, dict):
            continue
        for excerpt_relation in card_relation.get("excerpt_relations", []):
            if not isinstance(excerpt_relation, dict):
                continue
            ref = excerpt_relation.get("excerpt_ref")
            relation = excerpt_relation.get("relation")
            if isinstance(ref, str) and relation in {"supports", "supplements", "similar", "conflicts"} and ref not in refs:
                refs.append(ref)
    return refs


def align_explanations(cognition_ref: str, literature_dir: Path) -> Path:
    ensure_valid_schemas()
    explanation_serial = f"{len(sorted(ANALYSIS_DIR.glob('explanations_*'))) + 1:04d}"
    explanation_dir = ANALYSIS_DIR / f"explanations_{explanation_serial}"
    explanation_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    cognition = load_yaml(resolve_cognition_path(cognition_ref))
    literature_alignment = load_yaml(literature_dir / "literature_alignment.yaml")
    explanation_cards_dir = LITERATURE_DIR / "cards" / "explanations"

    explanation_card_refs: list[str] = []
    per_card_relations: dict[str, dict[str, Any]] = {}
    evidence_excerpt_refs: list[str] = []
    card_relations_seen: set[str] = set()
    strongest_strength = "low"

    for paper_ref in literature_alignment["literature_refs"]:
        paper_key = paper_key_from_ref_id(paper_ref)
        card = load_yaml(explanation_cards_dir / f"{paper_key}.yaml")
        card_ref = card["object_id"]
        explanation_card_refs.append(card_ref)

        excerpt_relations = []
        relation_counts = {"supports": 0, "supplements": 0, "similar": 0, "conflicts": 0, "unclear": 0}
        for excerpt_ref in card.get("excerpt_refs", []):
            excerpt = load_yaml(resolve_paper_excerpt_path(excerpt_ref))
            excerpt_relation, excerpt_reason, evidence_basis = classify_explanation_excerpt_relation(
                cognition_statement=cognition["statement"],
                card=card,
                excerpt=excerpt,
            )
            relation_counts[excerpt_relation] = relation_counts.get(excerpt_relation, 0) + 1
            if excerpt_relation in {"supports", "supplements", "similar", "conflicts"} and excerpt_ref not in evidence_excerpt_refs:
                evidence_excerpt_refs.append(excerpt_ref)
            excerpt_strength = source_strength_label(str(excerpt.get("source_kind", "seed_curated")))
            if {"low": 1, "medium": 2, "high": 3}[excerpt_strength] > {"low": 1, "medium": 2, "high": 3}[strongest_strength]:
                strongest_strength = excerpt_strength
            excerpt_relations.append(
                {
                    "excerpt_ref": excerpt_ref,
                    "granularity": excerpt.get("granularity", "summary"),
                    "source_ref": excerpt.get("source_ref"),
                    "source_kind": excerpt.get("source_kind"),
                    "evidence_strength": excerpt_strength,
                    "relation": excerpt_relation,
                    "reason": excerpt_reason,
                    "evidence_basis": evidence_basis,
                    "content": excerpt["content"],
                }
            )

        if relation_counts["conflicts"] > 0:
            relation = "conflicts"
            reason = "至少存在一个解释片段与本地认知形成冲突。"
        elif relation_counts["supports"] > 0:
            relation = "supports"
            reason = "存在直接指向补偿配置/问题本体的解释片段，可作为支持证据。"
        elif relation_counts["supplements"] > 0:
            relation = "supplements"
            reason = "当前片段主要提供对照性补充参照，而不是直接支持。"
        elif relation_counts["similar"] > 0:
            relation = "similar"
            reason = "当前片段只体现目标层面的相似性，尚不足以形成支持。"
        else:
            relation = "unclear"
            reason = "当前无法确定该解释卡片与本地认知的关系。"
        card_relations_seen.add(relation)

        per_card_relations[card_ref] = {
            "paper_ref": card["paper_ref"],
            "relation": relation,
            "reason": reason,
            "explanation_points": card.get("explanation_points", []),
            "relation_counts": relation_counts,
            "excerpt_relations": excerpt_relations,
        }

    if "conflicts" in card_relations_seen and card_relations_seen <= {"conflicts", "unclear"}:
        overall_relation = "conflicts"
    elif "supports" in card_relations_seen and len(card_relations_seen - {"unclear"}) > 1:
        overall_relation = "mixed"
    elif "supports" in card_relations_seen:
        overall_relation = "supports"
    elif "supplements" in card_relations_seen:
        overall_relation = "supplements"
    elif "similar" in card_relations_seen:
        overall_relation = "similar"
    else:
        overall_relation = "unclear"
    alignment = {
        "schema_version": "0.1.0",
        "object_type": "explanation_alignment",
        "object_id": f"explanation_alignment.power.ieee33_reactive_opt.{explanation_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": literature_alignment["task_ref"],
        "assessed_cognition_ref": cognition_ref,
        "explanation_card_refs": explanation_card_refs,
        "per_card_relations": per_card_relations,
        "evidence_excerpt_refs": evidence_excerpt_refs,
        "evidence_strength": strongest_strength,
        "relation_summary": build_explanation_relation_summary(per_card_relations),
        "overall_relation": overall_relation,
        "notes": [
            "当前 relation judgment 以 excerpt 文本证据为主，card 标签仅作兜底提示",
            "支持与仅相似已显式区分，但仍未进行原文全文语义匹配",
        ],
    }
    write_yaml(explanation_dir / "explanation_alignment.yaml", alignment)
    return explanation_dir


def literature_matches_for_profile(profile: dict[str, Any], seed_papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    method_family = profile.get("method_family", "")
    matches: list[dict[str, Any]] = []
    for paper in seed_papers:
        paper_family = paper.get("method_family", "")
        if method_family == "weak_bus_shunt_search" and paper_family == "capacitor_placement_optimization":
            matches.append(paper)
        elif method_family in {"ext_grid_vm_search", "experimental_ext_grid_search"} and paper_family == "volt_var_control":
            matches.append(paper)
    return matches


def strategy_semantic_profile(
    *, run_obj: dict[str, Any], metrics_payload: dict[str, Any]
) -> dict[str, Any]:
    skill_id = produced_skill_id_from_run(run_obj)
    control_settings = metrics_payload["candidate_solution"]["control_settings"]
    if skill_id == "skill.power.weak_bus_shunt_optimizer":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "high",
            "control_realism": "high",
            "reuse_potential": "medium",
            "method_family": "weak_bus_shunt_search",
            "control_signature": "reactive_compensation",
            "notes": [
                f"candidate_buses={control_settings.get('candidate_buses', [])}",
                f"evaluated_candidates={control_settings.get('evaluated_candidates')}",
            ],
        }
    if skill_id == "skill.power.reactive_optimizer":
        return {
            "skill_id": skill_id,
            "problem_alignment": "medium",
            "research_value": "medium",
            "control_realism": "low",
            "reuse_potential": "medium",
            "method_family": "ext_grid_vm_search",
            "control_signature": "boundary_voltage_tuning",
            "notes": [f"ext_grid_vm_pu={control_settings.get('ext_grid_vm_pu')}"],
        }
    if skill_id == "skill.power.reactive_optimizer_candidate":
        return {
            "skill_id": skill_id,
            "problem_alignment": "medium",
            "research_value": "low",
            "control_realism": "low",
            "reuse_potential": "low",
            "method_family": "experimental_ext_grid_search",
            "control_signature": "boundary_voltage_tuning",
            "notes": [f"ext_grid_vm_pu={control_settings.get('ext_grid_vm_pu')}"],
        }
    return {
        "skill_id": skill_id,
        "problem_alignment": "low",
        "research_value": "low",
        "control_realism": "low",
        "reuse_potential": "low",
        "method_family": "unknown",
        "control_signature": "unknown",
        "notes": [],
    }


def compare_scale_dimension(left: str, right: str) -> str:
    if scale_value(left) > scale_value(right):
        return "left"
    if scale_value(right) > scale_value(left):
        return "right"
    return "tie"


def compare_strategy_semantics(left_run_id: str, right_run_id: str) -> Path:
    ensure_valid_schemas()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    semantic_serial = f"{len(sorted(ANALYSIS_DIR.glob('semantic_*'))) + 1:04d}"
    semantic_dir = ANALYSIS_DIR / f"semantic_{semantic_serial}"
    semantic_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    left_run, left_metrics_payload, _ = load_run_payload(left_run_id)
    right_run, right_metrics_payload, _ = load_run_payload(right_run_id)
    left_profile = strategy_semantic_profile(run_obj=left_run, metrics_payload=left_metrics_payload)
    right_profile = strategy_semantic_profile(run_obj=right_run, metrics_payload=right_metrics_payload)

    dimensions = {
        "problem_alignment": {
            "left": left_profile["problem_alignment"],
            "right": right_profile["problem_alignment"],
            "winner": compare_scale_dimension(left_profile["problem_alignment"], right_profile["problem_alignment"]),
        },
        "research_value": {
            "left": left_profile["research_value"],
            "right": right_profile["research_value"],
            "winner": compare_scale_dimension(left_profile["research_value"], right_profile["research_value"]),
        },
        "control_realism": {
            "left": left_profile["control_realism"],
            "right": right_profile["control_realism"],
            "winner": compare_scale_dimension(left_profile["control_realism"], right_profile["control_realism"]),
        },
        "reuse_potential": {
            "left": left_profile["reuse_potential"],
            "right": right_profile["reuse_potential"],
            "winner": compare_scale_dimension(left_profile["reuse_potential"], right_profile["reuse_potential"]),
        },
        "method_family": {
            "left": left_profile["method_family"],
            "right": right_profile["method_family"],
            "winner": "tie" if left_profile["method_family"] == right_profile["method_family"] else "different",
        },
        "control_signature": {
            "left": left_profile["control_signature"],
            "right": right_profile["control_signature"],
            "winner": "tie" if left_profile["control_signature"] == right_profile["control_signature"] else "different",
        },
    }

    preferred_for_research = (
        left_run_id
        if dimensions["research_value"]["winner"] == "left"
        else right_run_id
        if dimensions["research_value"]["winner"] == "right"
        else ""
    )
    semantic_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_semantic_comparison",
        "object_id": f"semantic_comparison.power.ieee33_reactive_opt.{semantic_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": left_run["task_ref"],
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_skill_ref": left_profile["skill_id"],
        "right_skill_ref": right_profile["skill_id"],
        "semantic_dimensions": dimensions,
        "preferred_for_research_ref": preferred_for_research,
        "summary": (
            f"语义比较完成：{left_profile['skill_id']} 与 {right_profile['skill_id']} 在研究语义层面存在显著差异。"
        ),
        "notes": [
            *left_profile["notes"],
            *right_profile["notes"],
        ],
    }
    semantic_report = {
        "created_at": now,
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_skill_ref": left_profile["skill_id"],
        "right_skill_ref": right_profile["skill_id"],
        "preferred_for_research_ref": preferred_for_research,
        "summary": semantic_object["summary"],
    }
    write_yaml(semantic_dir / "strategy_semantic_comparison.yaml", semantic_object)
    with (semantic_dir / "semantic_report.json").open("w", encoding="utf-8") as f:
        json.dump(semantic_report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return semantic_dir


def align_literature(comparison_dir: Path, semantic_dir: Path) -> Path:
    ensure_valid_schemas()
    alignment_serial = f"{len(sorted(ANALYSIS_DIR.glob('literature_*'))) + 1:04d}"
    alignment_dir = ANALYSIS_DIR / f"literature_{alignment_serial}"
    alignment_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    seed_papers = load_seed_papers()

    left_profile = {
        "skill_id": semantic.get("left_skill_ref"),
        "method_family": semantic["semantic_dimensions"]["method_family"]["left"],
    }
    right_profile = {
        "skill_id": semantic.get("right_skill_ref"),
        "method_family": semantic["semantic_dimensions"]["method_family"]["right"],
    }

    left_matches = literature_matches_for_profile(left_profile, seed_papers)
    right_matches = literature_matches_for_profile(right_profile, seed_papers)
    literature_refs = []
    for paper in [*left_matches, *right_matches]:
        if paper["ref_id"] not in literature_refs:
            literature_refs.append(paper["ref_id"])

    if right_matches and not left_matches:
        novelty_position = "potential_extension"
    elif right_matches and left_matches:
        novelty_position = "variant"
    else:
        novelty_position = "unclear"

    alignment = {
        "schema_version": "0.1.0",
        "object_type": "literature_alignment",
        "object_id": f"literature_alignment.power.ieee33_reactive_opt.{alignment_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": comparison["task_ref"],
        "assessed_object_refs": [semantic.get("left_skill_ref", ""), semantic.get("right_skill_ref", "")],
        "literature_refs": literature_refs,
        "method_mappings": {
            semantic.get("left_skill_ref", ""): [paper["ref_id"] for paper in left_matches],
            semantic.get("right_skill_ref", ""): [paper["ref_id"] for paper in right_matches],
        },
        "theory_mappings": {
            "ext_grid_vm_search": "volt_var_control",
            "weak_bus_shunt_search": "capacitor_placement_optimization",
        },
        "novelty_position": novelty_position,
        "alignment_summary": (
            "当前对齐表明，ext-grid 路线更接近 Volt/Var control 家族，而 weak-shunt 路线更接近 capacitor placement / reactive compensation 家族。"
        ),
        "notes": [
            "当前只基于种子文献做方法家族级对齐",
            "尚未进行片段级解释对齐",
        ],
    }
    report = {
        "created_at": now,
        "assessed_object_refs": alignment["assessed_object_refs"],
        "literature_refs": literature_refs,
        "novelty_position": novelty_position,
        "summary": alignment["alignment_summary"],
    }
    write_yaml(alignment_dir / "literature_alignment.yaml", alignment)
    with (alignment_dir / "literature_report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return alignment_dir


def upgrade_cognition_from_analysis(
    comparison_dir: Path,
    semantic_dir: Path,
    literature_dir: Path | None = None,
    explanation_dir: Path | None = None,
) -> Path:
    ensure_valid_schemas()
    upgrade_serial = f"{len(sorted(ANALYSIS_DIR.glob('upgrade_*'))) + 1:04d}"
    upgrade_dir = ANALYSIS_DIR / f"upgrade_{upgrade_serial}"
    upgrade_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    literature_alignment = (
        load_yaml(literature_dir / "literature_alignment.yaml") if literature_dir is not None else None
    )
    explanation_alignment = (
        load_yaml(explanation_dir / "explanation_alignment.yaml") if explanation_dir is not None else None
    )
    explanation_excerpt_refs = (
        explanation_alignment_excerpt_refs(explanation_alignment) if explanation_alignment is not None else []
    )
    task_ref = comparison["task_ref"]
    comparison_cognition_ref = comparison["cognition_refs"][0]
    preferred_for_research_ref = semantic.get("preferred_for_research_ref", "")
    novelty_level = "medium"
    research_value_level = "high" if preferred_for_research_ref == comparison["right_run_ref"] else "medium"
    continue_investment = "continue" if research_value_level == "high" else "observe"
    if literature_alignment is not None:
        novelty_position = literature_alignment.get("novelty_position", "unclear")
        novelty_level = "medium" if novelty_position in {"variant", "potential_extension"} else "low"
    explanation_strength = explanation_alignment.get("evidence_strength", "low") if explanation_alignment is not None else "low"
    if explanation_strength == "high" and continue_investment == "continue":
        continue_investment = "prioritize"
    decision = "upgrade" if explanation_strength == "high" else "retain" if explanation_strength == "medium" else "freeze"

    novelty = {
        "schema_version": "0.1.0",
        "object_type": "novelty_assessment",
        "object_id": f"novelty.power.ieee33_reactive_opt.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": task_ref,
        "assessed_object_ref": semantic.get("right_skill_ref", ""),
        "supporting_refs": [
            comparison["object_id"],
            semantic["object_id"],
            *([literature_alignment["object_id"]] if literature_alignment is not None else []),
            *([explanation_alignment["object_id"]] if explanation_alignment is not None else []),
            *explanation_excerpt_refs,
        ],
        "novelty_level": novelty_level,
        "research_value_level": research_value_level,
        "continue_investment": continue_investment,
        "evidence_strength": explanation_strength,
        "summary": (
            "当前 weak-shunt 路线虽然在本地结果上弱于 ext-grid，但在问题贴合度和研究语义上更值得继续演化。"
        ),
        "reasons": [
            "控制对象更接近无功补偿问题本体",
            "方法语义更接近可复用研究技能",
            "当前比较仍局限于单工况",
            *(
                [f"文献对齐位置={literature_alignment.get('novelty_position', 'unclear')}"]
                if literature_alignment is not None
                else []
            ),
            *(
                [f"解释对齐关系={explanation_alignment.get('overall_relation', 'unclear')}"]
                if explanation_alignment is not None
                else []
            ),
            *(
                [f"解释证据强度={explanation_strength}"]
                if explanation_alignment is not None
                else []
            ),
            *([f"解释片段证据数={len(explanation_excerpt_refs)}"] if explanation_excerpt_refs else []),
        ],
    }

    upgraded_cognition = None
    upgraded_cognition_path = None
    if decision == "upgrade":
        upgraded_cognition = {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.upgraded_strategy_comparison_{upgrade_serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {},
            "cognition_type": "candidate",
            "statement": (
                "当前单工况对照表明，ext-grid 路线在指标上更优，但 weak-shunt 路线在无功优化语义上更贴近问题本体，因此更适合作为后续技能演化对象。"
            ),
            "evidence_refs": [
                comparison["object_id"],
                semantic["object_id"],
                novelty["object_id"],
                *([literature_alignment["object_id"]] if literature_alignment is not None else []),
                *([explanation_alignment["object_id"]] if explanation_alignment is not None else []),
                *explanation_excerpt_refs,
            ],
            "scope_boundary": {
                "task": task_ref,
                "mode": "comparative_cognition_upgrade",
            },
            "confidence_level": "medium",
            "derived_from_run_refs": [comparison["left_run_ref"], comparison["right_run_ref"]],
            "promotion_status": "proposed",
            "uncertainty_notes": (
                "该认知仍仅基于单工况与有限策略集合。"
                if literature_alignment is None
                else (
                    "该认知当前已结合种子文献对齐，"
                    + (
                        f"解释对齐关系={explanation_alignment.get('overall_relation', 'unclear')}，"
                        if explanation_alignment is not None
                        else ""
                    )
                    + (
                        f"解释证据强度={explanation_strength}，"
                        if explanation_alignment is not None
                        else ""
                    )
                    + (
                        f"解释片段证据数={len(explanation_excerpt_refs)}，" if explanation_excerpt_refs else ""
                    )
                    + f"novelty_position={literature_alignment.get('novelty_position', 'unclear')}。"
                )
            ),
        }
        upgraded_cognition_path = write_cognition_asset_and_registry(
            upgraded_cognition,
            run_id=comparison["winner_run_ref"] or comparison["left_run_ref"],
            when=now,
        )
    cognition_upgrade = {
        "schema_version": "0.1.0",
        "object_type": "cognition_upgrade",
        "object_id": f"cognition_upgrade.power.ieee33_reactive_opt.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {},
        "task_ref": task_ref,
        "source_cognition_ref": comparison_cognition_ref,
        "semantic_comparison_ref": semantic["object_id"],
        "novelty_assessment_ref": novelty["object_id"],
        "literature_alignment_ref": literature_alignment["object_id"] if literature_alignment is not None else None,
        "explanation_alignment_ref": explanation_alignment["object_id"] if explanation_alignment is not None else None,
        "explanation_excerpt_refs": explanation_excerpt_refs,
        "upgraded_cognition_ref": upgraded_cognition["object_id"] if upgraded_cognition else None,
        "evidence_strength": explanation_strength,
        "decision": decision,
        "rationale": (
            "虽然 ext-grid 路线在当前指标上更强，但 weak-shunt 路线的控制变量和方法语义更接近无功优化问题本体，因此比较认知应从“谁更强”升级为“谁更值得继续演化”。"
            + (
                f" 当前种子文献对齐将其定位为 `{literature_alignment.get('novelty_position', 'unclear')}`，支持将其视为值得继续投入的变体/潜在扩展。"
                if literature_alignment is not None
                else ""
            )
            + (
                f" 解释对齐进一步提供了 {len(explanation_excerpt_refs)} 条 excerpt 级证据，使该升级结论可回链到具体解释片段。"
                if explanation_excerpt_refs
                else ""
            )
            + (
                f" 当前证据强度为 `{explanation_strength}`，因此决策为 `{decision}`。"
            )
        ),
        "claim_adjustment": "应维持对 weak-shunt 当前性能的克制表述，但允许提高其研究价值判断。",
    }
    write_yaml(upgrade_dir / "novelty_assessment.yaml", novelty)
    write_yaml(upgrade_dir / "cognition_upgrade.yaml", cognition_upgrade)
    if upgraded_cognition is not None:
        write_yaml(upgrade_dir / "upgraded_cognition.yaml", upgraded_cognition)
    with (upgrade_dir / "writeback.json").open("w", encoding="utf-8") as f:
        writeback = {
            "novelty_assessment": str((upgrade_dir / "novelty_assessment.yaml").relative_to(REPO_ROOT)),
            "cognition_upgrade": str((upgrade_dir / "cognition_upgrade.yaml").relative_to(REPO_ROOT)),
            "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
        }
        if upgraded_cognition_path is not None:
            writeback["upgraded_cognition_asset"] = str(upgraded_cognition_path.relative_to(REPO_ROOT))
        json.dump(writeback, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return upgrade_dir


def verify_task001_pipeline() -> None:
    """Verify the current task001 vertical slice is coherent."""
    ensure_valid_schemas()
    validator = load_validator()
    artifact_errors = validator.validate_artifact_set(
        repo_root=Path.cwd(),
        schema_root=REPO_ROOT / "schemas",
        artifact_set="literature-alignment-plan",
    )
    if artifact_errors:
        lines = [f"- {err.source}: {err.message}" for err in artifact_errors]
        raise RuntimeError("artifact validation failed:\n" + "\n".join(lines))

    required_paths = [
        TASK_DIR / "task.yaml",
        TASK_DIR / "baseline.yaml",
        REPO_ROOT / "evaluators" / "task001_evaluator.py",
        REPO_ROOT / "skills" / "validated" / "baseline_solver.py",
        REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_optimizer.py",
        SKILL_REGISTRY_PATH,
        COGNITION_REGISTRY_PATH,
        LITERATURE_DIR / "task001-seed-papers.yaml",
        LITERATURE_DIR / "sources",
        LITERATURE_DIR / "excerpts",
        LITERATURE_DIR / "cards" / "explanations",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing required pipeline paths: {missing}")

    latest_run = latest_nonempty_dir(RUNS_DIR, "run_*")
    for filename in [
        "run.yaml",
        "metrics.json",
        "taste_assessment.yaml",
        "evidence_bundle.yaml",
        "report.yaml",
        "writeback.json",
    ]:
        if not (latest_run / filename).exists():
            raise RuntimeError(f"latest run missing {filename}: {latest_run}")

    latest_explanations = latest_nonempty_dir(ANALYSIS_DIR, "explanations_*")
    explanation_alignment = load_yaml(latest_explanations / "explanation_alignment.yaml")
    if explanation_alignment.get("evidence_strength") != "high":
        raise RuntimeError("latest explanation alignment does not have high evidence_strength")
    if not explanation_alignment.get("evidence_excerpt_refs"):
        raise RuntimeError("latest explanation alignment has no evidence_excerpt_refs")

    latest_upgrade = latest_nonempty_dir(ANALYSIS_DIR, "upgrade_*")
    novelty = load_yaml(latest_upgrade / "novelty_assessment.yaml")
    cognition_upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    upgraded_cognition = load_yaml(latest_upgrade / "upgraded_cognition.yaml")
    if novelty.get("evidence_strength") != "high":
        raise RuntimeError("latest novelty assessment does not have high evidence_strength")
    if novelty.get("continue_investment") != "prioritize":
        raise RuntimeError("latest novelty assessment does not prioritize continued investment")
    if not cognition_upgrade.get("explanation_excerpt_refs"):
        raise RuntimeError("latest cognition upgrade lacks explanation_excerpt_refs")
    if not any(str(ref).startswith("paper_excerpt.") for ref in upgraded_cognition.get("evidence_refs", [])):
        raise RuntimeError("latest upgraded cognition does not cite excerpt-level evidence")
    if cognition_upgrade.get("evidence_strength") != "high":
        raise RuntimeError("latest cognition upgrade does not record high evidence_strength")
    if cognition_upgrade.get("decision") != "upgrade":
        raise RuntimeError("latest cognition upgrade is not driven to upgrade by high evidence strength")

    cognition_registry = load_json(COGNITION_REGISTRY_PATH)
    upgraded_ref = upgraded_cognition["object_id"]
    if not any(entry.get("object_id") == upgraded_ref for entry in cognition_registry.get("cognition", [])):
        raise RuntimeError(f"upgraded cognition not found in registry: {upgraded_ref}")


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
    semantic = sub.add_parser("compare-semantics", help="Compare semantic properties of two task001 runs")
    semantic.add_argument("--left-run-id", required=True)
    semantic.add_argument("--right-run-id", required=True)
    literature = sub.add_parser("align-literature", help="Align local strategy comparison with literature seeds")
    literature.add_argument("--comparison-dir", required=True)
    literature.add_argument("--semantic-dir", required=True)
    ingest_lit = sub.add_parser("ingest-seed-literature", help="Materialize literature_source objects from seed papers")
    build_lit = sub.add_parser("build-literature-cards", help="Materialize literature objects from task seed papers")
    build_lit.add_argument(
        "--max-source-kind",
        choices=["seed_curated", "manual_summary", "abstract_excerpt", "fulltext_excerpt"],
        required=False,
    )
    explain = sub.add_parser("align-explanations", help="Align a local cognition with literature explanation cards")
    explain.add_argument("--cognition-ref", required=True)
    explain.add_argument("--literature-dir", required=True)
    upgrade = sub.add_parser("upgrade-cognition", help="Upgrade cognition from comparison artifacts")
    upgrade.add_argument("--comparison-dir", required=True)
    upgrade.add_argument("--semantic-dir", required=True)
    upgrade.add_argument("--literature-dir", required=False)
    upgrade.add_argument("--explanation-dir", required=False)
    sub.add_parser("verify-task001-pipeline", help="Verify the task001 vertical research loop")

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

    if args.command == "compare-semantics":
        semantic_dir = compare_strategy_semantics(args.left_run_id, args.right_run_id)
        print(f"Semantic comparison written to {semantic_dir}")
        return 0

    if args.command == "align-literature":
        alignment_dir = align_literature(Path(args.comparison_dir), Path(args.semantic_dir))
        print(f"Literature alignment written to {alignment_dir}")
        return 0

    if args.command == "ingest-seed-literature":
        sources_dir = ingest_seed_literature()
        print(f"Literature sources written under {sources_dir}")
        return 0

    if args.command == "build-literature-cards":
        literature_root = build_literature_cards(args.max_source_kind)
        print(f"Literature cards written under {literature_root}")
        return 0

    if args.command == "align-explanations":
        explanation_dir = align_explanations(args.cognition_ref, Path(args.literature_dir))
        print(f"Explanation alignment written to {explanation_dir}")
        return 0

    if args.command == "upgrade-cognition":
        upgrade_dir = upgrade_cognition_from_analysis(
            Path(args.comparison_dir),
            Path(args.semantic_dir),
            Path(args.literature_dir) if args.literature_dir else None,
            Path(args.explanation_dir) if args.explanation_dir else None,
        )
        print(f"Cognition upgrade written to {upgrade_dir}")
        return 0

    if args.command == "verify-task001-pipeline":
        verify_task001_pipeline()
        print("Task001 pipeline verification passed.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
