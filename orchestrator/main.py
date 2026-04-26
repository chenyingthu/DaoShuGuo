#!/usr/bin/env python3
"""Minimal orchestrator for DaoShuGuo-v1 MVP."""

from __future__ import annotations

import argparse
import json
import subprocess
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
TASK002_DIR = REPO_ROOT / "tasks" / "task002"
TASK003_DIR = REPO_ROOT / "tasks" / "task003"
TASK004_DIR = REPO_ROOT / "tasks" / "task004"
TASK005_DIR = REPO_ROOT / "tasks" / "task005"
RUNS_DIR = REPO_ROOT / "runs" / "task001"
RUNS_TASK002_DIR = REPO_ROOT / "runs" / "task002"
RUNS_TASK003_DIR = REPO_ROOT / "runs" / "task003"
RUNS_TASK004_DIR = REPO_ROOT / "runs" / "task004"
RUNS_TASK005_DIR = REPO_ROOT / "runs" / "task005"
ANALYSIS_DIR = REPO_ROOT / "analysis" / "task001"
ANALYSIS_TASK002_DIR = REPO_ROOT / "analysis" / "task002"
ANALYSIS_TASK003_DIR = REPO_ROOT / "analysis" / "task003"
ANALYSIS_TASK004_DIR = REPO_ROOT / "analysis" / "task004"
ANALYSIS_TASK005_DIR = REPO_ROOT / "analysis" / "task005"
LITERATURE_DIR = REPO_ROOT / "literature"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_schemas.py"
EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task001_evaluator.py"
TASK002_EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task002_evaluator.py"
TASK003_EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task003_evaluator.py"
TASK004_EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task004_evaluator.py"
TASK005_EVALUATOR_MODULE_PATH = REPO_ROOT / "evaluators" / "task005_evaluator.py"
BASELINE_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "baseline_solver.py"
VALIDATED_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "reactive_optimizer.py"
EXPERIMENTAL_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "reactive_optimizer_candidate.py"
WEAK_SHUNT_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_optimizer.py"
TASK002_FAILURE_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_adversarial_task002.py"
TASK003_BASELINE_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "baseline_solver_task003.py"
TASK003_RENEWABLE_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_inverter_reactive_optimizer_task003.py"
TASK003_UNDERPERFORMER_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_inverter_underperformer_task003.py"
TASK003_WEAK_SHUNT_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_optimizer.py"
TASK004_BASELINE_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "baseline_solver_task004.py"
TASK004_CANDIDATE_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_capacity_optimizer_task004.py"
TASK004_SENSITIVITY_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "voltage_sensitivity_capacity_optimizer_task004.py"
TASK004_MISMATCH_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "single_point_capacity_mismatch_task004.py"
TASK005_BASELINE_SOLVER_PATH = REPO_ROOT / "skills" / "validated" / "baseline_solver_task005.py"
TASK005_CANDIDATE_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_restoration_candidate_task005.py"
TASK005_MISMATCH_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "steady_state_restoration_mismatch_task005.py"
TASK005_PERF_SOLVER_PATH = REPO_ROOT / "skills" / "active_dev" / "renewable_underperformer_task005.py"
SKILL_REGISTRY_PATH = REPO_ROOT / "skills" / "registry.json"
COGNITION_REGISTRY_PATH = REPO_ROOT / "cognition" / "registry.json"
COGNITION_CARDS_DIR = REPO_ROOT / "cognition" / "cards"
COGNITION_FAILED_DIR = REPO_ROOT / "cognition" / "failed"

TASK_RUN_CONTEXTS = {
    "task001": {
        "task_dir": TASK_DIR,
        "runs_dir": RUNS_DIR,
        "analysis_dir": ANALYSIS_DIR,
        "problem_name": "ieee33_reactive_opt",
        "case_label": "case33bw",
        "evaluator_path": REPO_ROOT / "evaluators" / "task001_evaluator.yaml",
    },
    "task002": {
        "task_dir": TASK002_DIR,
        "runs_dir": RUNS_TASK002_DIR,
        "analysis_dir": ANALYSIS_TASK002_DIR,
        "problem_name": "ieee69_reactive_opt",
        "case_label": "IEEE69",
        "evaluator_path": REPO_ROOT / "evaluators" / "task002_evaluator.yaml",
    },
    "task003": {
        "task_dir": TASK003_DIR,
        "runs_dir": RUNS_TASK003_DIR,
        "analysis_dir": ANALYSIS_TASK003_DIR,
        "problem_name": "ieee69_renewable_reactive_opt",
        "case_label": "IEEE69 renewable snapshot",
        "evaluator_path": REPO_ROOT / "evaluators" / "task003_evaluator.yaml",
    },
    "task004": {
        "task_dir": TASK004_DIR,
        "runs_dir": RUNS_TASK004_DIR,
        "analysis_dir": ANALYSIS_TASK004_DIR,
        "problem_name": "ieee69_hosting_capacity",
        "case_label": "IEEE69 hosting capacity screening",
        "evaluator_path": REPO_ROOT / "evaluators" / "task004_evaluator.yaml",
    },
    "task005": {
        "task_dir": TASK005_DIR,
        "runs_dir": RUNS_TASK005_DIR,
        "analysis_dir": ANALYSIS_TASK005_DIR,
        "problem_name": "ieee69_restoration_resilience",
        "case_label": "IEEE69 single fault restoration",
        "evaluator_path": REPO_ROOT / "evaluators" / "task005_evaluator.yaml",
    },
}


TASK_REF_TO_PACKAGE = {
    "task.power.ieee33_reactive_opt": "task001",
    "task.power.ieee69_reactive_opt": "task002",
    "task.power.ieee69_renewable_reactive_opt": "task003",
    "task.power.ieee69_hosting_capacity": "task004",
    "task.power.ieee69_restoration_resilience": "task005",
}

SKILL_COGNITION_LOOP_BUILDER = REPO_ROOT / "scripts" / "build_skill_cognition_loop.py"
SKILL_COGNITION_LOOP_VERIFIER = REPO_ROOT / "scripts" / "verify_skill_cognition_loop.py"
REAL_AGENTIC_LOOP_RUNNER = REPO_ROOT / "scripts" / "run_real_agentic_loop.py"
REAL_AGENTIC_LOOP_VERIFIER = REPO_ROOT / "scripts" / "verify_real_agentic_loop.py"


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


def run_python_script(script: Path, *args: str) -> None:
    result = subprocess.run(
        ["python", str(script), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed: python {script.relative_to(REPO_ROOT)} {' '.join(args)}")
    if result.stdout.strip():
        print(result.stdout.strip())


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


def repo_path(ref: str) -> Path:
    path = (REPO_ROOT / ref).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {ref}") from exc
    return path


def ensure_valid_schemas() -> None:
    validator = load_validator()
    errors = validator.validate_samples(REPO_ROOT / "schemas")
    if errors:
        lines = [f"- {err.source}: {err.message}" for err in errors]
        raise RuntimeError("schema validation failed before orchestration:\n" + "\n".join(lines))


def next_run_serial() -> str:
    existing = sorted(RUNS_DIR.glob("run_*"))
    return f"{len(existing) + 1:04d}"


def next_run_serial_for_dir(runs_dir: Path) -> str:
    existing = sorted(runs_dir.glob("run_*"))
    return f"{len(existing) + 1:04d}"


def load_real_inputs_for_task(
    task_package: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = TASK_RUN_CONTEXTS[task_package]
    task_dir = context["task_dir"]
    task = load_yaml(task_dir / "task.yaml")
    baseline = load_yaml(task_dir / "baseline.yaml")
    evaluator = load_yaml(context["evaluator_path"])
    constraints = load_yaml(task_dir / "constraints.yaml")
    return task, baseline, evaluator, constraints


def load_solver_from_artifact(module_name: str, artifact: dict[str, Any], fallback: Path) -> Any:
    artifact_path = artifact.get("path")
    if not isinstance(artifact_path, str) or not artifact_path:
        return load_module(module_name, fallback)
    return load_module(module_name, repo_path(artifact_path))


def grade_from_result(passed: bool) -> str:
    return "zhuoshi" if passed else "huimo"


def report_type_from_grade(grade: str) -> str:
    return "technical_note" if grade == "zhuoshi" else "discussion_memo"


def skill_version_for_id(skill_id: str) -> str:
    versions = {
        "skill.power.reactive_optimizer": "0.1.0",
        "skill.power.reactive_optimizer_candidate": "0.2.0",
        "skill.power.weak_bus_shunt_optimizer": "0.1.0",
        "skill.power.weak_bus_shunt_adversarial_task002": "0.1.0",
        "skill.power.renewable_inverter_reactive_optimizer_task003": "0.1.0",
        "skill.power.renewable_inverter_underperformer_task003": "0.1.0",
        "skill.power.renewable_capacity_optimizer_task004": "0.1.0",
        "skill.power.single_point_capacity_mismatch_task004": "0.1.0",
        "skill.power.renewable_restoration_candidate_task005": "0.1.0",
        "skill.power.steady_state_restoration_mismatch_task005": "0.1.0",
        "skill.power.renewable_underperformer_task005": "0.1.0",
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


def build_task002_cognition(passed: bool, serial: str, run_id: str, mode_tag: str) -> dict[str, Any]:
    now = utc_now()
    if "adversarial-failure" in mode_tag:
        success_statement = (
            "当前 task002 failure probe 意外优于基线，这意味着失败探针设计需要重新审视。"
        )
        failure_statement = (
            "当前真实 task002 failure probe 表明，在 IEEE69 任务设定下，错误极性的弱节点 shunt 设置会稳定恶化损耗/电压表现，并可引入额外约束违反，因此该路线只能作为失败边界材料。"
        )
    else:
        success_statement = (
            "当前真实 task002 迁移运行表明，在 IEEE69 任务设定下，弱节点 shunt 补偿技能可相对基线形成阶段性改进。"
        )
        failure_statement = (
            "当前真实 task002 迁移运行表明，在 IEEE69 任务设定下，弱节点 shunt 补偿技能未能稳定满足评估要求。"
        )
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": (
            f"cognition.power.ieee69_reactive_opt_runtime_{serial}"
            if passed
            else f"cognition.power.ieee69_reactive_opt_runtime_failure_{serial}"
        ),
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "cognition_type": "candidate" if passed else "failure",
        "statement": success_statement if passed else failure_statement,
        "evidence_refs": [run_id],
        "scope_boundary": {
            "task": "task.power.ieee69_reactive_opt",
            "mode": mode_tag,
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [run_id],
        "promotion_status": "proposed",
    }


def load_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_real_inputs_for_task("task001")


def load_task002_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_real_inputs_for_task("task002")


def load_task003_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_real_inputs_for_task("task003")


def load_task004_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_real_inputs_for_task("task004")


def load_task005_real_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_real_inputs_for_task("task005")


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
    if ".ieee69_restoration_resilience." in run_id:
        return RUNS_TASK005_DIR / f"run_{serial_from_run_id(run_id)}"
    if ".ieee69_hosting_capacity." in run_id:
        return RUNS_TASK004_DIR / f"run_{serial_from_run_id(run_id)}"
    if ".ieee69_renewable_reactive_opt." in run_id:
        return RUNS_TASK003_DIR / f"run_{serial_from_run_id(run_id)}"
    if ".ieee69_reactive_opt." in run_id:
        return RUNS_TASK002_DIR / f"run_{serial_from_run_id(run_id)}"
    return RUNS_DIR / f"run_{serial_from_run_id(run_id)}"


def task_package_from_ref(task_ref: str) -> str:
    package = TASK_REF_TO_PACKAGE.get(task_ref)
    if package is None:
        raise ValueError(f"unsupported task_ref: {task_ref}")
    return package


def task_package_from_run_id(run_id: str) -> str:
    if ".ieee69_restoration_resilience." in run_id:
        return "task005"
    if ".ieee69_hosting_capacity." in run_id:
        return "task004"
    if ".ieee69_renewable_reactive_opt." in run_id:
        return "task003"
    if ".ieee69_reactive_opt." in run_id:
        return "task002"
    if ".ieee33_reactive_opt." in run_id:
        return "task001"
    raise ValueError(f"unsupported run_id: {run_id}")


def task_context_from_ref(task_ref: str) -> dict[str, Any]:
    return TASK_RUN_CONTEXTS[task_package_from_ref(task_ref)]


def problem_name_from_task_ref(task_ref: str) -> str:
    return str(task_context_from_ref(task_ref)["problem_name"])


def analysis_dir_from_task_ref(task_ref: str) -> Path:
    return task_context_from_ref(task_ref)["analysis_dir"]


def case_label_from_task_ref(task_ref: str) -> str:
    return str(task_context_from_ref(task_ref)["case_label"])


def objective_for_task(task_ref: str, metrics: dict[str, float]) -> float:
    if task_package_from_ref(task_ref) == "task005":
        return -1000.0 * float(metrics["restored_load_ratio"]) + 500.0 * float(metrics["unserved_critical_load"])
    if task_package_from_ref(task_ref) == "task004":
        # task004 compares hosting-capacity level first, then supporting boundary metrics
        return float(metrics["hosting_capacity_level"]) * -1000.0 + float(metrics["loss_at_boundary"])
    if task_package_from_ref(task_ref) == "task003":
        from tasks.task003.runtime_helpers import objective
    elif task_package_from_ref(task_ref) == "task002":
        from tasks.task002.runtime_helpers import objective
    else:
        from tasks.task001.runtime_helpers import objective
    return float(objective(metrics))


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


def literature_task_package(task_or_ref: str | None = None) -> str:
    if task_or_ref is None:
        return "task001"
    if task_or_ref.startswith("task."):
        return task_package_from_ref(task_or_ref)
    return task_or_ref


def load_seed_papers(task_or_ref: str | None = None) -> list[dict[str, Any]]:
    task_package = literature_task_package(task_or_ref)
    data = load_yaml(LITERATURE_DIR / f"{task_package}-seed-papers.yaml")
    return data.get("seed_papers", [])


def load_source_overlays(task_or_ref: str | None = None) -> list[dict[str, Any]]:
    task_package = literature_task_package(task_or_ref)
    overlay_path = LITERATURE_DIR / f"{task_package}-source-overlays.yaml"
    if not overlay_path.exists():
        return []
    data = load_yaml(overlay_path)
    return data.get("overlay_sources", [])


def load_source_inputs() -> list[dict[str, Any]]:
    input_dir = LITERATURE_DIR / "source_inputs"
    if not input_dir.exists():
        return []
    return [load_yaml(path) for path in sorted(input_dir.glob("*.yaml"))]


def load_raw_excerpt_inputs(task_or_ref: str | None = None) -> list[dict[str, Any]]:
    task_package = literature_task_package(task_or_ref)
    raw_dir = LITERATURE_DIR / "raw_excerpts" / task_package
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
    if method_family == "renewable_inverter_reactive_support":
        return [
            "控制对象直接作用于 PV/DER inverter 的无功支撑能力",
            "典型目标包括降低网损、缓解电压偏差并保持 inverter 能力边界",
            "方法语义更接近新能源接入场景下的 Volt/Var 或 reactive support 问题本体",
        ]
    if method_family == "coordinated_volt_var_control":
        return [
            "控制对象覆盖 inverter 与传统 Volt/Var 设备的协同调节",
            "典型目标包括在多控制对象之间协调损耗、电压质量与设备边界",
            "方法语义更接近新能源接入下的协调 Volt/Var 控制",
        ]
    if method_family == "hosting_capacity_assessment":
        return [
            "承载力必须在明确场景和约束下定义",
            "边界判断关注的是最大可容纳接入水平，而不是单点运行结果",
            "若不显式说明条件，边界结论容易被过度表述",
        ]
    if method_family == "hosting_capacity_controlled":
        return [
            "承载力边界会随控制策略改变",
            "控制策略相关边界不应被写成系统唯一固有承载力",
            "边界比较本身就是 hosting capacity 研究的一部分",
        ]
    if method_family == "single_point_operating_evaluation":
        return [
            "单点运行结果只能说明局部工况，不等于边界扫描结果",
            "将 operating point 结果直接提升为承载力结论会产生语义失配",
            "该方法更接近运行状态评估，而非 hosting capacity 边界评估",
        ]
    return [
        "控制对象更偏向电压边界、调压设备或协调控制器",
        "目标同样可能包括损耗、电压质量和约束满足",
        "方法语义更接近 Volt/Var control 控制问题，而非直接补偿配置问题",
    ]


def default_concept_tags_for_family(method_family: str) -> list[str]:
    if method_family == "capacitor_placement_optimization":
        return ["capacitor placement", "reactive compensation", "weak bus"]
    if method_family == "renewable_inverter_reactive_support":
        return ["smart inverter", "reactive support", "volt/var control", "DER"]
    if method_family == "coordinated_volt_var_control":
        return ["coordinated volt/var control", "smart inverter", "capacitor coordination", "DER"]
    if method_family == "hosting_capacity_assessment":
        return ["hosting capacity", "boundary assessment", "renewable integration"]
    if method_family == "hosting_capacity_controlled":
        return ["hosting capacity", "control-conditioned boundary", "smart inverter"]
    if method_family == "single_point_operating_evaluation":
        return ["operating point", "boundary mismatch", "hosting capacity"]
    return ["volt/var control", "voltage regulation", "distribution control"]


def ingest_seed_literature(task_package: str = "task001") -> Path:
    ensure_valid_schemas()
    sources_dir = literature_sources_dir()
    now = utc_now()
    # Seed-curated default sources
    for paper in load_seed_papers(task_package):
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
                f"由 {task_package}-seed-papers.yaml 物化生成的轻量文献源对象",
                f"source_kind={paper.get('source_kind', 'seed_curated')}",
            ],
        }
        for optional_field in ("year", "doi", "url"):
            optional_value = paper.get(optional_field)
            if optional_value is not None:
                source_object[optional_field] = optional_value
        write_yaml(sources_dir / f"{paper_key}.yaml", source_object)
    # Higher-fidelity overlay sources
    paper_index = {paper["ref_id"]: paper for paper in load_seed_papers(task_package)}
    for overlay in load_source_overlays(task_package):
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
    for raw_input in load_raw_excerpt_inputs(task_package):
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


def load_literature_sources(task_package: str | None = None) -> list[dict[str, Any]]:
    sources_dir = literature_sources_dir()
    source_files = sorted(sources_dir.glob("*.yaml"))
    if not source_files:
        ingest_seed_literature(task_package or "task001")
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


def build_literature_cards(max_source_kind: str | None = None, task_package: str | None = None) -> Path:
    ensure_valid_schemas()
    if task_package is not None:
        ingest_seed_literature(task_package)
    papers_dir = LITERATURE_DIR / "papers"
    excerpts_dir = LITERATURE_DIR / "excerpts"
    methods_dir = LITERATURE_DIR / "cards" / "methods"
    explanations_dir = LITERATURE_DIR / "cards" / "explanations"
    for path in [papers_dir, excerpts_dir, methods_dir, explanations_dir]:
        path.mkdir(parents=True, exist_ok=True)

    now = utc_now()
    literature_sources = load_literature_sources(task_package)
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
        elif method_family == "renewable_inverter_reactive_support":
            method_summary = selected_source.get("method_notes", [""])[0] or "该文献属于新能源 inverter reactive support / Volt-Var 方法家族。"
            control_signature = "inverter_q_support"
            optimization_style = "renewable_inverter_support"
        elif method_family == "coordinated_volt_var_control":
            method_summary = selected_source.get("method_notes", [""])[0] or "该文献属于新能源接入下的协调 Volt/Var 控制方法家族。"
            control_signature = "coordinated_volt_var_control"
            optimization_style = "coordinated_control"
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
    "inverter",
    "smart inverter",
    "reactive support",
    "reactive power support",
    "volt/var control",
    "der",
    "hosting capacity",
    "boundary",
    "capacity boundary",
    "screening",
    "single-point",
    "operating point",
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
    "coordinated",
    "distributed",
    "smart inverter",
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
    cognition_guard_tokens = (
        "问题本体",
        "弱节点 shunt 补偿",
        "无功补偿",
        "补偿技能",
        "inverter 控制空间",
        "新能源 inverter",
        "性能失败",
        "方向错误",
        "reactive support",
        "承载力",
        "边界扫描",
        "单点运行",
        "控制策略",
        "hosting capacity",
        "boundary",
    )
    if not contains_any_token(cognition_statement, cognition_guard_tokens):
        return "unclear", "当前规则未覆盖该类本地认知。", "cognition_guard"

    content = str(excerpt.get("content", ""))
    has_direct_support = contains_any_token(content, EXCERPT_DIRECT_SUPPORT_TOKENS)
    has_target_similarity = contains_any_token(content, EXCERPT_TARGET_SIMILARITY_TOKENS)
    has_boundary = contains_any_token(content, EXCERPT_BOUNDARY_TOKENS)
    has_conflict = contains_any_token(content, EXCERPT_CONFLICT_TOKENS)
    has_contrast = contains_any_token(content, EXCERPT_CONTRAST_TOKENS)

    if has_conflict:
        return "conflicts", "片段文本直接包含负向或冲突性表述，应记为冲突证据。", "excerpt_content"

    hosting_mode = contains_any_token(cognition_statement, ("承载力", "hosting capacity", "边界扫描", "boundary"))
    if hosting_mode:
        if contains_any_token(content, ("hosting capacity", "boundary", "capacity boundary", "screening")):
            if contains_any_token(content, ("single-point", "operating point")) and contains_any_token(cognition_statement, ("单点运行", "single-point")):
                return "supports", "片段文本直接支持单点结果不能替代边界扫描的判断。", "excerpt_content"
            if contains_any_token(content, ("control strategy", "control", "volt/var control", "strategy")) and contains_any_token(cognition_statement, ("控制策略", "边界判断")):
                return "supports", "片段文本直接支持承载力边界依赖控制策略条件。", "excerpt_content"
            return "supports", "片段文本直接涉及承载力边界定义，可作为支持证据。", "excerpt_content"
        if contains_any_token(content, ("constraint", "voltage", "scenario", "假设")):
            return "supplements", "片段文本主要在补充边界条件与场景假设。", "excerpt_content"

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
    cognition = load_yaml(resolve_cognition_path(cognition_ref))
    literature_alignment = load_yaml(literature_dir / "literature_alignment.yaml")
    task_ref = literature_alignment["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    explanation_serial = f"{len(sorted(analysis_dir.glob('explanations_*'))) + 1:04d}"
    explanation_dir = analysis_dir / f"explanations_{explanation_serial}"
    explanation_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
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
        "object_id": f"explanation_alignment.power.{problem_name}.{explanation_serial}",
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
        elif method_family == "renewable_inverter_reactive_support" and paper_family in {
            "renewable_inverter_reactive_support",
            "coordinated_volt_var_control",
        }:
            matches.append(paper)
        elif method_family == "hosting_capacity_strategy_scan" and paper_family in {
            "hosting_capacity_assessment",
            "hosting_capacity_controlled",
        }:
            matches.append(paper)
        elif method_family == "single_point_operating_evaluation" and paper_family == "single_point_operating_evaluation":
            matches.append(paper)
        elif method_family in {"ext_grid_vm_search", "experimental_ext_grid_search"} and paper_family == "volt_var_control":
            matches.append(paper)
    return matches


def strategy_semantic_profile(
    *, run_obj: dict[str, Any], metrics_payload: dict[str, Any]
) -> dict[str, Any]:
    skill_id = produced_skill_id_from_run(run_obj)
    control_settings = metrics_payload["candidate_solution"]["control_settings"]
    if run_obj.get("task_ref") == "task.power.ieee69_hosting_capacity":
        return semantic_profile_for_task004(
            run_obj=run_obj,
            metrics_payload=metrics_payload,
            skill_id=skill_id,
            control_settings=control_settings,
        )
    if run_obj.get("task_ref") == "task.power.ieee69_restoration_resilience":
        return semantic_profile_for_task005(
            run_obj=run_obj,
            metrics_payload=metrics_payload,
            skill_id=skill_id,
            control_settings=control_settings,
        )
    if run_obj.get("task_ref") == "task.power.ieee69_renewable_reactive_opt":
        return semantic_profile_for_task003(
            run_obj=run_obj,
            metrics_payload=metrics_payload,
            skill_id=skill_id,
            control_settings=control_settings,
        )
    return semantic_profile_for_skill(skill_id=skill_id, control_settings=control_settings)


def performance_status_for_run(run_obj: dict[str, Any], metrics_payload: dict[str, Any]) -> str:
    if run_obj.get("trigger_reason") == "real_weak-shunt-mismatch":
        return "mismatch"
    if run_obj.get("trigger_reason") == "real_inverter-underperformer":
        return "failed"
    if run_obj.get("run_status") == "completed":
        return "successful"
    if "task_mismatch" in str(run_obj.get("trigger_reason", "")):
        return "frozen"
    evaluation = metrics_payload.get("evaluation", {})
    return "failed" if evaluation.get("passed") is False else "unknown"


def semantic_profile_for_task003(
    *,
    run_obj: dict[str, Any],
    metrics_payload: dict[str, Any],
    skill_id: str,
    control_settings: dict[str, Any],
) -> dict[str, Any]:
    performance_status = performance_status_for_run(run_obj, metrics_payload)
    if skill_id == "skill.power.renewable_inverter_reactive_optimizer_task003":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "high",
            "control_realism": "high",
            "reuse_potential": "high",
            "method_family": "renewable_inverter_reactive_support",
            "control_signature": "inverter_q_support",
            "renewable_awareness": "high",
            "control_space_match": "high",
            "performance_status": performance_status,
            "notes": [
                f"inverter_q={control_settings.get('inverter_q', [])}",
                f"reactive_support_effort={metrics_payload['candidate_solution']['metrics'].get('reactive_support_effort')}",
            ],
        }
    if skill_id == "skill.power.renewable_inverter_underperformer_task003":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "medium",
            "control_realism": "medium",
            "reuse_potential": "medium",
            "method_family": "renewable_inverter_reactive_support",
            "control_signature": "inverter_q_support",
            "renewable_awareness": "high",
            "control_space_match": "high",
            "performance_status": performance_status,
            "notes": [
                "语义正确但参数方向不佳",
                f"inverter_q={control_settings.get('inverter_q', [])}",
            ],
        }
    if skill_id == "skill.power.weak_bus_shunt_optimizer":
        return {
            "skill_id": skill_id,
            "problem_alignment": "medium",
            "research_value": "medium",
            "control_realism": "medium",
            "reuse_potential": "medium",
            "method_family": "weak_bus_shunt_search",
            "control_signature": "reactive_compensation",
            "renewable_awareness": "low",
            "control_space_match": "low",
            "performance_status": performance_status,
            "notes": [
                "未显式利用 inverter Q 控制空间",
                f"shunts={control_settings.get('shunts', [])}",
            ],
        }
    return {
        "skill_id": skill_id,
        "problem_alignment": "low",
        "research_value": "low",
        "control_realism": "low",
        "reuse_potential": "low",
        "method_family": "unknown",
        "control_signature": "unknown",
        "renewable_awareness": "low",
        "control_space_match": "low",
        "performance_status": performance_status,
        "notes": [],
    }


def semantic_profile_for_task004(
    *,
    run_obj: dict[str, Any],
    metrics_payload: dict[str, Any],
    skill_id: str,
    control_settings: dict[str, Any],
) -> dict[str, Any]:
    trigger = str(run_obj.get("trigger_reason", ""))
    performance_status = "successful" if run_obj.get("run_status") == "completed" else "failed"
    if trigger == "real_single-point-mismatch":
        performance_status = "mismatch"
    if skill_id == "skill.power.renewable_capacity_optimizer_task004":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "high",
            "control_realism": "high",
            "reuse_potential": "high",
            "method_family": "hosting_capacity_strategy_scan",
            "control_signature": "capacity_boundary_scan",
            "hosting_capacity_awareness": "high",
            "boundary_conditioning": "high",
            "boundary_claim_discipline": "high",
            "performance_status": performance_status,
            "notes": [
                f"hosting_capacity_level={metrics_payload['candidate_solution']['metrics'].get('hosting_capacity_level')}",
                f"strategy={control_settings.get('strategy')}",
            ],
        }
    if skill_id == "skill.power.single_point_capacity_mismatch_task004":
        return {
            "skill_id": skill_id,
            "problem_alignment": "medium",
            "research_value": "medium",
            "control_realism": "low",
            "reuse_potential": "low",
            "method_family": "single_point_operating_evaluation",
            "control_signature": "single_point_result",
            "hosting_capacity_awareness": "low",
            "boundary_conditioning": "low",
            "boundary_claim_discipline": "low",
            "performance_status": performance_status,
            "notes": [
                "单点结果不能替代边界扫描",
                f"hosting_capacity_level={metrics_payload['candidate_solution']['metrics'].get('hosting_capacity_level')}",
            ],
        }
    return {
        "skill_id": skill_id,
        "problem_alignment": "low",
        "research_value": "low",
        "control_realism": "low",
        "reuse_potential": "low",
        "method_family": "unknown",
        "control_signature": "unknown",
        "hosting_capacity_awareness": "low",
        "boundary_conditioning": "low",
        "boundary_claim_discipline": "low",
        "performance_status": performance_status,
        "notes": [],
    }


def semantic_profile_for_task005(
    *,
    run_obj: dict[str, Any],
    metrics_payload: dict[str, Any],
    skill_id: str,
    control_settings: dict[str, Any],
) -> dict[str, Any]:
    trigger = str(run_obj.get("trigger_reason", ""))
    performance_status = "successful" if run_obj.get("run_status") == "completed" else "failed"
    if trigger == "real_steady-state-mismatch":
        performance_status = "mismatch"
    if skill_id == "skill.power.renewable_restoration_candidate_task005":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "high",
            "control_realism": "high",
            "reuse_potential": "high",
            "method_family": "renewable_restoration_support",
            "control_signature": "restoration_support",
            "resilience_awareness": "high",
            "restoration_scope_match": "high",
            "performance_status": performance_status,
            "notes": [
                f"strategy={control_settings.get('strategy')}",
                f"restored_load_ratio={metrics_payload['candidate_solution']['metrics'].get('restored_load_ratio')}",
            ],
        }
    if skill_id == "skill.power.steady_state_restoration_mismatch_task005":
        return {
            "skill_id": skill_id,
            "problem_alignment": "medium",
            "research_value": "medium",
            "control_realism": "low",
            "reuse_potential": "low",
            "method_family": "steady_state_operating_adjustment",
            "control_signature": "steady_state_result",
            "resilience_awareness": "low",
            "restoration_scope_match": "low",
            "performance_status": performance_status,
            "notes": ["单点稳态结果不能替代恢复决策语义"],
        }
    if skill_id == "skill.power.renewable_underperformer_task005":
        return {
            "skill_id": skill_id,
            "problem_alignment": "high",
            "research_value": "medium",
            "control_realism": "medium",
            "reuse_potential": "medium",
            "method_family": "renewable_restoration_support",
            "control_signature": "restoration_support",
            "resilience_awareness": "high",
            "restoration_scope_match": "high",
            "performance_status": performance_status,
            "notes": ["语义正确但恢复结果未优于 baseline"],
        }
    return {
        "skill_id": skill_id,
        "problem_alignment": "low",
        "research_value": "low",
        "control_realism": "low",
        "reuse_potential": "low",
        "method_family": "unknown",
        "control_signature": "unknown",
        "resilience_awareness": "low",
        "restoration_scope_match": "low",
        "performance_status": performance_status,
        "notes": [],
    }


def semantic_profile_for_skill(*, skill_id: str, control_settings: dict[str, Any]) -> dict[str, Any]:
    if skill_id in {"skill.power.weak_bus_shunt_optimizer", "skill.power.weak_bus_shunt_optimizer_task002"}:
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
    left_run, left_metrics_payload, _ = load_run_payload(left_run_id)
    right_run, right_metrics_payload, _ = load_run_payload(right_run_id)
    if left_run["task_ref"] != right_run["task_ref"]:
        raise ValueError("compare_strategy_semantics requires both runs to share the same task_ref")
    task_ref = left_run["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    semantic_serial = f"{len(sorted(analysis_dir.glob('semantic_*'))) + 1:04d}"
    semantic_dir = analysis_dir / f"semantic_{semantic_serial}"
    semantic_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
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
    if task_ref == "task.power.ieee69_renewable_reactive_opt":
        dimensions["renewable_awareness"] = {
            "left": left_profile["renewable_awareness"],
            "right": right_profile["renewable_awareness"],
            "winner": compare_scale_dimension(left_profile["renewable_awareness"], right_profile["renewable_awareness"]),
        }
        dimensions["control_space_match"] = {
            "left": left_profile["control_space_match"],
            "right": right_profile["control_space_match"],
            "winner": compare_scale_dimension(left_profile["control_space_match"], right_profile["control_space_match"]),
        }
        dimensions["performance_status"] = {
            "left": left_profile["performance_status"],
            "right": right_profile["performance_status"],
            "winner": (
                "left"
                if left_profile["performance_status"] == "successful" and right_profile["performance_status"] != "successful"
                else "right"
                if right_profile["performance_status"] == "successful" and left_profile["performance_status"] != "successful"
                else "different"
            ),
        }
    if task_ref == "task.power.ieee69_hosting_capacity":
        dimensions["hosting_capacity_awareness"] = {
            "left": left_profile["hosting_capacity_awareness"],
            "right": right_profile["hosting_capacity_awareness"],
            "winner": compare_scale_dimension(left_profile["hosting_capacity_awareness"], right_profile["hosting_capacity_awareness"]),
        }
        dimensions["boundary_conditioning"] = {
            "left": left_profile["boundary_conditioning"],
            "right": right_profile["boundary_conditioning"],
            "winner": compare_scale_dimension(left_profile["boundary_conditioning"], right_profile["boundary_conditioning"]),
        }
        dimensions["boundary_claim_discipline"] = {
            "left": left_profile["boundary_claim_discipline"],
            "right": right_profile["boundary_claim_discipline"],
            "winner": compare_scale_dimension(left_profile["boundary_claim_discipline"], right_profile["boundary_claim_discipline"]),
        }
        dimensions["performance_status"] = {
            "left": left_profile["performance_status"],
            "right": right_profile["performance_status"],
            "winner": (
                "left"
                if left_profile["performance_status"] == "successful" and right_profile["performance_status"] != "successful"
                else "right"
                if right_profile["performance_status"] == "successful" and left_profile["performance_status"] != "successful"
                else "different"
            ),
        }
    if task_ref == "task.power.ieee69_restoration_resilience":
        dimensions["resilience_awareness"] = {
            "left": left_profile["resilience_awareness"],
            "right": right_profile["resilience_awareness"],
            "winner": compare_scale_dimension(left_profile["resilience_awareness"], right_profile["resilience_awareness"]),
        }
        dimensions["restoration_scope_match"] = {
            "left": left_profile["restoration_scope_match"],
            "right": right_profile["restoration_scope_match"],
            "winner": compare_scale_dimension(left_profile["restoration_scope_match"], right_profile["restoration_scope_match"]),
        }
        dimensions["critical_load_relevance"] = {
            "left": "high" if left_profile["problem_alignment"] == "high" else "medium",
            "right": "high" if right_profile["problem_alignment"] == "high" else "medium",
            "winner": compare_scale_dimension(
                "high" if left_profile["problem_alignment"] == "high" else "medium",
                "high" if right_profile["problem_alignment"] == "high" else "medium",
            ),
        }
        dimensions["performance_status"] = {
            "left": left_profile["performance_status"],
            "right": right_profile["performance_status"],
            "winner": (
                "left"
                if left_profile["performance_status"] == "successful" and right_profile["performance_status"] != "successful"
                else "right"
                if right_profile["performance_status"] == "successful" and left_profile["performance_status"] != "successful"
                else "different"
            ),
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
        "object_id": f"semantic_comparison.power.{problem_name}.{semantic_serial}",
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
            (
                "task003 语义比较完成：已显式区分新能源-aware success、skill mismatch 与 performance failure。"
                if task_ref == "task.power.ieee69_renewable_reactive_opt"
                else "task004 语义比较完成：已显式区分边界扫描候选与单点结果失配。"
                if task_ref == "task.power.ieee69_hosting_capacity"
                else "task005 语义比较完成：已显式区分恢复候选与稳态结果失配。"
                if task_ref == "task.power.ieee69_restoration_resilience"
                else f"语义比较完成：{left_profile['skill_id']} 与 {right_profile['skill_id']} 在研究语义层面存在显著差异。"
            )
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
    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    task_ref = comparison["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    alignment_serial = f"{len(sorted(analysis_dir.glob('literature_*'))) + 1:04d}"
    alignment_dir = analysis_dir / f"literature_{alignment_serial}"
    alignment_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    seed_papers = load_seed_papers(task_ref)

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

    if task_ref == "task.power.ieee69_renewable_reactive_opt":
        theory_mappings = {
            "renewable_inverter_reactive_support": "inverter_based_volt_var_control",
            "coordinated_volt_var_control": "coordinated_volt_var_control",
            "weak_bus_shunt_search": "traditional_compensation_configuration",
        }
        alignment_summary = (
            "当前对齐表明，inverter-support 路线更接近 smart inverter / DER reactive support 家族，"
            "weak-shunt 路线更接近传统 capacitor placement 家族。"
        )
    elif task_ref == "task.power.ieee69_hosting_capacity":
        theory_mappings = {
            "hosting_capacity_strategy_scan": "hosting_capacity_assessment",
            "single_point_operating_evaluation": "operating_point_analysis",
        }
        alignment_summary = (
            "当前对齐表明，task004 的边界扫描路线更接近 hosting capacity assessment 家族，"
            "而 single-point mismatch 路线更接近 operating-point analysis，不能直接替代边界评估。"
        )
    else:
        theory_mappings = {
            "ext_grid_vm_search": "volt_var_control",
            "weak_bus_shunt_search": "capacitor_placement_optimization",
        }
        alignment_summary = (
            "当前对齐表明，ext-grid 路线更接近 Volt/Var control 家族，而 weak-shunt 路线更接近 capacitor placement / reactive compensation 家族。"
        )

    alignment = {
        "schema_version": "0.1.0",
        "object_type": "literature_alignment",
        "object_id": f"literature_alignment.power.{problem_name}.{alignment_serial}",
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
        "theory_mappings": theory_mappings,
        "novelty_position": novelty_position,
        "alignment_summary": alignment_summary,
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
    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    task_ref = comparison["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    upgrade_serial = f"{len(sorted(analysis_dir.glob('upgrade_*'))) + 1:04d}"
    upgrade_dir = analysis_dir / f"upgrade_{upgrade_serial}"
    upgrade_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
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
        "object_id": f"novelty.power.{problem_name}.{upgrade_serial}",
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
            "object_id": f"cognition.power.upgraded_strategy_comparison_{problem_name}_{upgrade_serial}",
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
        "object_id": f"cognition_upgrade.power.{problem_name}.{upgrade_serial}",
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


def verify_task002_pipeline() -> None:
    """Verify the minimal task002 migration slice is coherent."""
    ensure_valid_schemas()
    required_paths = [
        TASK002_DIR / "task.yaml",
        TASK002_DIR / "baseline.yaml",
        TASK002_DIR / "constraints.yaml",
        TASK002_DIR / "targets.yaml",
        TASK002_DIR / "runtime_helpers.py",
        TASK002_DIR / "ieee69bus.txt",
        REPO_ROOT / "evaluators" / "task002_evaluator.py",
        REPO_ROOT / "evaluators" / "task002_evaluator.yaml",
        REPO_ROOT / "skills" / "validated" / "baseline_solver_task002.py",
        REPO_ROOT / "skills" / "active_dev" / "weak_bus_shunt_optimizer.py",
        SKILL_REGISTRY_PATH,
        COGNITION_REGISTRY_PATH,
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing required task002 paths: {missing}")

    baseline = load_yaml(TASK002_DIR / "baseline.yaml")
    artifact_ref = baseline.get("artifact_ref", {})
    if artifact_ref.get("path") != "skills/validated/baseline_solver_task002.py":
        raise RuntimeError("task002 baseline does not point to skills/validated/baseline_solver_task002.py")

    latest_run = None
    for run_dir in sorted(RUNS_TASK002_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_payload = load_yaml(run_dir / "run.yaml")
        if run_payload.get("run_status") == "completed":
            latest_run = run_dir
            break
    if latest_run is None:
        raise RuntimeError("no completed task002 run found for success-path verification")
    for filename in [
        "run.yaml",
        "metrics.json",
        "cognition.yaml",
        "agent_trace.yaml",
        "prompt_observation.yaml",
        "taste_assessment.yaml",
        "evidence_bundle.yaml",
        "report.yaml",
        "writeback.json",
    ]:
        if not (latest_run / filename).exists():
            raise RuntimeError(f"latest task002 run missing {filename}: {latest_run}")

    latest_run_payload = load_yaml(latest_run / "run.yaml")
    if latest_run_payload.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 run does not point to task.power.ieee69_reactive_opt")
    if latest_run_payload.get("run_status") != "completed":
        raise RuntimeError("latest task002 run is not completed")

    metrics = load_json(latest_run / "metrics.json")
    evaluation = metrics.get("evaluation", {})
    if evaluation.get("passed") is not True:
        raise RuntimeError("latest task002 run did not pass evaluator")

    candidate_control = metrics.get("candidate_solution", {}).get("control_settings", {})
    if not candidate_control.get("shunts"):
        raise RuntimeError("latest task002 run does not contain weak-shunt controls")

    cognition = load_yaml(latest_run / "cognition.yaml")
    if cognition.get("scope_boundary", {}).get("task") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 cognition has wrong task boundary")


def verify_task002_failure_path() -> None:
    ensure_valid_schemas()
    latest_failure_run = None
    for run_dir in sorted(RUNS_TASK002_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir():
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if run_obj.get("trigger_reason") == "real_adversarial-failure":
            latest_failure_run = run_dir
            break
    if latest_failure_run is None:
        raise RuntimeError("no task002 adversarial failure run found")

    run_obj = load_yaml(latest_failure_run / "run.yaml")
    metrics = load_json(latest_failure_run / "metrics.json")
    cognition = load_yaml(latest_failure_run / "cognition.yaml")
    taste = load_yaml(latest_failure_run / "taste_assessment.yaml")
    report = load_yaml(latest_failure_run / "report.yaml")

    if run_obj.get("run_status") != "failed_experiment":
        raise RuntimeError("task002 failure run is not marked failed_experiment")
    if cognition.get("cognition_type") != "failure":
        raise RuntimeError("task002 failure run did not produce failure cognition")
    if taste.get("grade") != "huimo":
        raise RuntimeError("task002 failure run did not downgrade to huimo")
    if report.get("report_type") != "discussion_memo":
        raise RuntimeError("task002 failure run did not emit discussion_memo")
    if "负向边界" not in str(report.get("summary", "")) and "失败" not in str(report.get("summary", "")):
        raise RuntimeError("task002 failure report does not state the failure boundary")

    evaluation = metrics.get("evaluation", {})
    if evaluation.get("passed") is not False:
        raise RuntimeError("task002 failure run unexpectedly passed evaluator")
    comparisons = evaluation.get("comparisons", {})
    if comparisons.get("loss", {}).get("improved") is not False:
        raise RuntimeError("task002 failure run did not worsen loss as expected")
    if comparisons.get("voltage_deviation", {}).get("improved") is not False:
        raise RuntimeError("task002 failure run did not worsen voltage deviation as expected")


def check_task003_mismatch(source_dir: Path | None = None) -> Path:
    """Check whether task003 has enough framing inputs to execute."""
    ensure_valid_schemas()
    source = source_dir or TASK003_DIR
    required = {
        "research_brief": source / "research_brief.md",
        "grid_context": source / "grid_context.yaml",
        "renewable_context": source / "renewable_context.yaml",
        "control_scope": source / "control_scope.yaml",
        "constraints": source / "constraints.yaml",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    gaps: list[str] = []
    if not missing:
        renewable_context = load_yaml(required["renewable_context"])
        control_scope = load_yaml(required["control_scope"])
        constraints = load_yaml(required["constraints"])
        if not renewable_context.get("sites"):
            gaps.append("renewable_context.sites")
        controls = control_scope.get("allowed_controls", {})
        inverter_control = controls.get("inverter_q_mvar", {})
        if not isinstance(inverter_control, dict) or inverter_control.get("enabled") is not True:
            gaps.append("control_scope.allowed_controls.inverter_q_mvar")
        solver = constraints.get("solver", {})
        if not solver.get("renewable_sites"):
            gaps.append("constraints.solver.renewable_sites")
        if not solver.get("voltage_limits"):
            gaps.append("constraints.solver.voltage_limits")

    serial = utc_now().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    output_dir = REPO_ROOT / "analysis" / "task003" / f"mismatch_{serial}"
    output_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    is_blocked = bool(missing or gaps)
    result = {
        "schema_version": "0.1.0",
        "object_type": "task_mismatch_check",
        "object_id": f"task_mismatch.power.ieee69_renewable_reactive_opt.{serial}",
        "created_at": now,
        "status": "blocked" if is_blocked else "ready",
        "task_ref": "task.power.ieee69_renewable_reactive_opt",
        "source_dir": str(source.relative_to(REPO_ROOT)) if source.is_relative_to(REPO_ROOT) else str(source),
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "decision": "freeze" if is_blocked else "execute",
        "rationale": (
            "任务定义缺失关键输入，不应进入真实执行。"
            if is_blocked
            else "任务定义具备最小执行条件。"
        ),
    }
    write_yaml(output_dir / "task_mismatch_check.yaml", result)
    note = {
        "created_at": now,
        "task_ref": result["task_ref"],
        "decision": result["decision"],
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "required_next_inputs": missing + gaps,
    }
    write_yaml(output_dir / "task_refinement_note.yaml", note)
    if is_blocked:
        cognition = {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.ieee69_renewable_reactive_opt_task_mismatch_{serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {"mismatch_type": "task_mismatch"},
            "cognition_type": "failure",
            "statement": "当前 task003 brief 缺失关键任务定义项，应冻结执行并先补齐任务边界。",
            "evidence_refs": [result["object_id"]],
            "scope_boundary": {
                "task": result["task_ref"],
                "mode": "task_mismatch_check",
            },
            "confidence_level": "medium",
            "promotion_status": "proposed",
        }
        write_yaml(output_dir / "cognition.yaml", cognition)
        write_cognition_asset_and_registry(cognition, run_id=result["object_id"], when=now)
    return output_dir


def verify_task003_pipeline() -> None:
    ensure_valid_schemas()
    required_paths = [
        TASK003_DIR / "research_brief.md",
        TASK003_DIR / "grid_context.yaml",
        TASK003_DIR / "renewable_context.yaml",
        TASK003_DIR / "control_scope.yaml",
        TASK003_DIR / "task.yaml",
        TASK003_DIR / "constraints.yaml",
        TASK003_DIR / "baseline.yaml",
        TASK003_DIR / "targets.yaml",
        TASK003_DIR / "assumptions.yaml",
        TASK003_DIR / "runtime_helpers.py",
        REPO_ROOT / "evaluators" / "task003_evaluator.py",
        REPO_ROOT / "evaluators" / "task003_evaluator.yaml",
        TASK003_BASELINE_SOLVER_PATH,
        TASK003_RENEWABLE_SOLVER_PATH,
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing required task003 paths: {missing}")

    latest_success_run = None
    for run_dir in sorted(RUNS_TASK003_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if (
            run_obj.get("run_status") == "completed"
            and run_obj.get("trigger_reason") == "real_inverter-support"
        ):
            latest_success_run = run_dir
            break
    if latest_success_run is None:
        raise RuntimeError("no completed task003 run found")

    for filename in [
        "run.yaml",
        "metrics.json",
        "cognition.yaml",
        "agent_trace.yaml",
        "prompt_observation.yaml",
        "taste_assessment.yaml",
        "evidence_bundle.yaml",
        "report.yaml",
        "writeback.json",
    ]:
        if not (latest_success_run / filename).exists():
            raise RuntimeError(f"latest task003 success run missing {filename}")
    metrics = load_json(latest_success_run / "metrics.json")
    evaluation = metrics.get("evaluation", {})
    if evaluation.get("passed") is not True:
        raise RuntimeError("latest task003 success run did not pass evaluator")
    if "reactive_support_effort" not in metrics.get("candidate_solution", {}).get("metrics", {}):
        raise RuntimeError("task003 candidate metrics missing reactive_support_effort")
    cognition = load_yaml(latest_success_run / "cognition.yaml")
    if cognition.get("cognition_type") != "candidate":
        raise RuntimeError("task003 success run did not produce candidate cognition")


def verify_task003_failure_path() -> None:
    ensure_valid_schemas()
    latest_failure_run = None
    for run_dir in sorted(RUNS_TASK003_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if run_obj.get("trigger_reason") == "real_weak-shunt-mismatch":
            latest_failure_run = run_dir
            break
    if latest_failure_run is None:
        raise RuntimeError("no task003 skill mismatch failure run found")
    run_obj = load_yaml(latest_failure_run / "run.yaml")
    cognition = load_yaml(latest_failure_run / "cognition.yaml")
    taste = load_yaml(latest_failure_run / "taste_assessment.yaml")
    report = load_yaml(latest_failure_run / "report.yaml")
    if run_obj.get("run_status") != "failed_experiment":
        raise RuntimeError("task003 mismatch run is not failed_experiment")
    if run_obj.get("metadata", {}).get("mismatch_type") != "skill_mismatch":
        raise RuntimeError("task003 mismatch run missing skill_mismatch metadata")
    if cognition.get("cognition_type") != "failure":
        raise RuntimeError("task003 mismatch run did not produce failure cognition")
    if taste.get("grade") != "huimo":
        raise RuntimeError("task003 mismatch run did not downgrade taste")
    if report.get("report_type") != "discussion_memo":
        raise RuntimeError("task003 mismatch run did not emit discussion_memo")

    latest_mismatch = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "mismatch_*")
    mismatch = load_yaml(latest_mismatch / "task_mismatch_check.yaml")
    if mismatch.get("decision") not in {"execute", "freeze"}:
        raise RuntimeError("task003 mismatch checker decision invalid")

    latest_perf_run = None
    for run_dir in sorted(RUNS_TASK003_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if run_obj.get("trigger_reason") == "real_inverter-underperformer":
            latest_perf_run = run_dir
            break
    if latest_perf_run is None:
        raise RuntimeError("no task003 performance failure run found")
    perf_run = load_yaml(latest_perf_run / "run.yaml")
    perf_cognition = load_yaml(latest_perf_run / "cognition.yaml")
    if perf_run.get("run_status") != "failed_experiment":
        raise RuntimeError("task003 performance failure run is not failed_experiment")
    if perf_run.get("metadata", {}).get("mismatch_type") != "performance_failure":
        raise RuntimeError("task003 performance failure run missing performance_failure metadata")
    if perf_cognition.get("cognition_type") != "failure":
        raise RuntimeError("task003 performance failure run did not produce failure cognition")


def verify_task003_cognition_stage() -> None:
    ensure_valid_schemas()
    latest_semantic = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "semantic_*")
    latest_upgrade = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "upgrade_*")
    semantic = load_yaml(latest_semantic / "strategy_semantic_comparison.yaml")
    upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    novelty = load_yaml(latest_upgrade / "novelty_assessment.yaml")
    if semantic.get("task_ref") != "task.power.ieee69_renewable_reactive_opt":
        raise RuntimeError("task003 semantic comparison has wrong task_ref")
    dims = semantic.get("semantic_dimensions", {})
    for key in ["renewable_awareness", "control_space_match", "performance_status"]:
        if key not in dims:
            raise RuntimeError(f"task003 semantic comparison missing {key}")
    if upgrade.get("task_ref") != "task.power.ieee69_renewable_reactive_opt":
        raise RuntimeError("task003 cognition upgrade has wrong task_ref")
    if upgrade.get("decision") not in {"upgrade", "retain", "freeze"}:
        raise RuntimeError("task003 cognition upgrade decision invalid")
    if novelty.get("continue_investment") not in {"observe", "continue", "prioritize"}:
        raise RuntimeError("task003 novelty assessment continue_investment invalid")


def verify_task003_literature_stage() -> None:
    ensure_valid_schemas()
    latest_literature = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "literature_*")
    latest_explanations = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "explanations_*")
    latest_upgrade = latest_nonempty_dir(ANALYSIS_TASK003_DIR, "upgrade_*")
    literature_alignment = load_yaml(latest_literature / "literature_alignment.yaml")
    explanation_alignment = load_yaml(latest_explanations / "explanation_alignment.yaml")
    cognition_upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    if literature_alignment.get("task_ref") != "task.power.ieee69_renewable_reactive_opt":
        raise RuntimeError("task003 literature alignment has wrong task_ref")
    if not literature_alignment.get("literature_refs"):
        raise RuntimeError("task003 literature alignment missing literature refs")
    if explanation_alignment.get("task_ref") != "task.power.ieee69_renewable_reactive_opt":
        raise RuntimeError("task003 explanation alignment has wrong task_ref")
    if explanation_alignment.get("evidence_strength") not in {"medium", "high"}:
        raise RuntimeError("task003 explanation alignment evidence strength too weak")
    if not explanation_alignment.get("evidence_excerpt_refs"):
        raise RuntimeError("task003 explanation alignment missing excerpt refs")
    if cognition_upgrade.get("literature_alignment_ref") is None:
        raise RuntimeError("task003 cognition upgrade missing literature_alignment_ref")
    if cognition_upgrade.get("explanation_alignment_ref") is None:
        raise RuntimeError("task003 cognition upgrade missing explanation_alignment_ref")


def build_task004_cognition(
    *,
    passed: bool,
    serial: str,
    run_id: str,
    strategy: str,
    mismatch_type: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    if mismatch_type == "skill_mismatch":
        statement = "当前 task004 skill-mismatch probe 表明，单点运行结果不能直接替代承载力边界扫描。"
    else:
        statement = (
            "当前 task004 真实运行表明，在当前扫描包络内，candidate 相对 baseline 提高了新能源接入承载边界。"
            if passed
            else "当前 task004 真实运行表明，candidate 未提高当前扫描包络内的承载边界，只能作为边界或失败材料。"
        )
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": (
            f"cognition.power.ieee69_hosting_capacity_runtime_{serial}"
            if passed
            else f"cognition.power.ieee69_hosting_capacity_runtime_failure_{serial}"
        ),
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"strategy": strategy, "mismatch_type": mismatch_type or ""},
        "cognition_type": "candidate" if (passed and mismatch_type is None) else "failure",
        "statement": statement,
        "evidence_refs": [run_id],
        "scope_boundary": {
            "task": "task.power.ieee69_hosting_capacity",
            "mode": f"real_{strategy}",
            "boundary_type": "control_strategy_conditioned_static_capacity",
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [run_id],
        "promotion_status": "proposed",
    }


def check_task004_boundary_overclaim(run_dir: Path) -> Path:
    run_obj = load_yaml(run_dir / "run.yaml")
    report = load_yaml(run_dir / "report.yaml")
    serial = utc_now().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    output_dir = ANALYSIS_TASK004_DIR / f"boundary_overclaim_{serial}"
    output_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    summary_text = " ".join([report.get("summary", ""), report.get("boundary_statement", ""), *report.get("claim_summary", [])])
    flagged = any(token in summary_text for token in ["系统固有承载力", "普适承载力", "长期承载力"])
    result = {
        "schema_version": "0.1.0",
        "object_type": "boundary_overclaim_check",
        "object_id": f"boundary_overclaim.power.ieee69_hosting_capacity.{serial}",
        "created_at": now,
        "status": "flagged" if flagged else "controlled",
        "task_ref": run_obj["task_ref"],
        "run_ref": run_obj["object_id"],
        "decision": "downgrade" if flagged else "accept",
        "rationale": "报告出现超出扫描包络边界的承载力表述。" if flagged else "报告当前边界表述受控。",
    }
    write_yaml(output_dir / "boundary_overclaim_check.yaml", result)
    return output_dir


def check_task004_mismatch(source_dir: Path | None = None) -> Path:
    ensure_valid_schemas()
    source = source_dir or TASK004_DIR
    required = {
        "research_brief": source / "research_brief.md",
        "grid_context": source / "grid_context.yaml",
        "renewable_context": source / "renewable_context.yaml",
        "hosting_capacity_scope": source / "hosting_capacity_scope.yaml",
        "control_scope": source / "control_scope.yaml",
        "constraints": source / "constraints.yaml",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    gaps: list[str] = []
    if not missing:
        scope = load_yaml(required["hosting_capacity_scope"])
        controls = load_yaml(required["control_scope"])
        constraints = load_yaml(required["constraints"])
        if not scope.get("capacity_definition"):
            gaps.append("hosting_capacity_scope.capacity_definition")
        if not controls.get("baseline_strategy"):
            gaps.append("control_scope.baseline_strategy")
        if not constraints.get("solver", {}).get("renewable_scale_values"):
            gaps.append("constraints.solver.renewable_scale_values")
    serial = utc_now().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    output_dir = ANALYSIS_TASK004_DIR / f"mismatch_{serial}"
    output_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    blocked = bool(missing or gaps)
    result = {
        "schema_version": "0.1.0",
        "object_type": "task_mismatch_check",
        "object_id": f"task_mismatch.power.ieee69_hosting_capacity.{serial}",
        "created_at": now,
        "status": "blocked" if blocked else "ready",
        "task_ref": "task.power.ieee69_hosting_capacity",
        "source_dir": str(source.relative_to(REPO_ROOT)) if source.is_relative_to(REPO_ROOT) else str(source),
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "decision": "freeze" if blocked else "execute",
        "rationale": "task004 承载力定义缺失关键输入，不应进入真实执行。" if blocked else "task004 承载力任务具备最小执行条件。",
    }
    write_yaml(output_dir / "task_mismatch_check.yaml", result)
    note = {
        "created_at": now,
        "task_ref": result["task_ref"],
        "decision": result["decision"],
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "required_next_inputs": missing + gaps,
    }
    write_yaml(output_dir / "task_refinement_note.yaml", note)
    if blocked:
        cognition = {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.ieee69_hosting_capacity_task_mismatch_{serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {"mismatch_type": "task_mismatch"},
            "cognition_type": "failure",
            "statement": "当前 task004 brief 缺失承载力定义关键项，应冻结执行并补齐边界与控制策略条件。",
            "evidence_refs": [result["object_id"]],
            "scope_boundary": {"task": result["task_ref"], "mode": "task_mismatch_check"},
            "confidence_level": "medium",
            "promotion_status": "proposed",
        }
        write_yaml(output_dir / "cognition.yaml", cognition)
        write_cognition_asset_and_registry(cognition, run_id=result["object_id"], when=now)
    return output_dir


def run_real_task004(strategy: str, candidate_q_step_mvar: float | None = None) -> Path:
    ensure_valid_schemas()
    evaluator_module = load_module("task004_evaluator", TASK004_EVALUATOR_MODULE_PATH)
    task, baseline, evaluator, constraints = load_task004_real_inputs()
    baseline_solver = load_solver_from_artifact(
        "task004_baseline_solver",
        baseline.get("artifact_ref", {}),
        TASK004_BASELINE_SOLVER_PATH,
    )
    if strategy == "inverter-support":
        candidate_skill_id = "skill.power.renewable_capacity_optimizer_task004"
        solver_path = TASK004_CANDIDATE_SOLVER_PATH
        mismatch_type = None
    elif strategy == "voltage-sensitivity":
        candidate_skill_id = "skill.power.voltage_sensitivity_capacity_optimizer_task004"
        solver_path = TASK004_SENSITIVITY_SOLVER_PATH
        mismatch_type = None
    elif strategy == "single-point-mismatch":
        candidate_skill_id = "skill.power.single_point_capacity_mismatch_task004"
        solver_path = TASK004_MISMATCH_SOLVER_PATH
        mismatch_type = "skill_mismatch"
    else:
        raise ValueError(f"unsupported task004 strategy: {strategy}")
    candidate_solver = load_module("task004_candidate_solver", solver_path)
    serial = next_run_serial_for_dir(RUNS_TASK004_DIR)
    run_dir = RUNS_TASK004_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    constraint_set = dict(constraints["solver"])
    if candidate_q_step_mvar is not None:
        constraint_set["candidate_q_step_mvar"] = float(candidate_q_step_mvar)
    network_model = str(constraint_set.get("network_model", "ieee69_hosting_capacity"))
    baseline_raw = baseline_solver.solve(network_model, constraint_set)
    candidate_raw = candidate_solver.solve(network_model, constraint_set)
    baseline_solution = {"control_settings": baseline_raw["control_settings"], "metrics": baseline_raw["baseline_solution"]}
    candidate_solution = {"control_settings": candidate_raw["control_settings"], "metrics": candidate_raw["reactive_power_settings"]}
    evaluation = evaluator_module.evaluate_real_solution(baseline_solution, candidate_solution)

    run_id = f"run.power.ieee69_hosting_capacity.{serial}"
    grade = grade_from_result(evaluation["passed"])
    report_type = report_type_from_grade(grade)
    taste_id = f"taste.power.ieee69_hosting_capacity.{serial}"
    evidence_id = f"evidence.power.ieee69_hosting_capacity.{serial}"
    trace_id = f"agent_trace.power.ieee69_hosting_capacity.{serial}"
    prompt_obs_id = f"prompt_observation.power.ieee69_hosting_capacity.{serial}"
    report_id = f"report.power.ieee69_hosting_capacity.{'note' if evaluation['passed'] else 'memo'}_{serial}"
    effective_passed = bool(evaluation["passed"]) and mismatch_type is None
    cognition = build_task004_cognition(
        passed=effective_passed,
        serial=serial,
        run_id=run_id,
        strategy=strategy,
        mismatch_type=mismatch_type,
    )
    run_object = {
        "schema_version": "0.1.0",
        "object_type": "run",
        "object_id": run_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "archived",
        "metadata": {
            "boundary_type": "control_strategy_conditioned_static_capacity",
            "mismatch_type": mismatch_type or "",
            "candidate_q_step_mvar": constraint_set.get("candidate_q_step_mvar"),
        },
        "title": f"task004 real {strategy} run {serial}",
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_status": "completed" if effective_passed else "failed_experiment",
        "started_at": now,
        "ended_at": now,
        "attempt_index": int(serial),
        "trigger_reason": f"real_{strategy}",
        "input_snapshot": {
            "task": {"object_id": task["object_id"], "object_version": task["object_version"]},
            "evaluator": {"object_id": evaluator["object_id"], "object_version": evaluator["object_version"]},
        },
        "skill_refs": {
            "used": [{"object_id": "skill.power.baseline_solver", "object_version": "0.1.0"}],
            "produced": [{"object_id": candidate_skill_id, "object_version": skill_version_for_id(candidate_skill_id)}],
        },
        "result_summary": {
            "metrics": evaluation["candidate_solution"]["metrics"],
            "baseline_comparison": "improved" if evaluation["passed"] else "worse",
            "notes": evaluation["summary"],
        },
        "artifact_refs": [{"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")}],
        "agent_trace_refs": [{"kind": "trace", "object_id": trace_id}],
    }
    if not effective_passed:
        run_object["failure_summary"] = (
            "skill mismatch: single-point operating result cannot substitute hosting-capacity boundary"
            if mismatch_type == "skill_mismatch"
            else "candidate did not improve hosting-capacity boundary"
        )
    evidence = {
        "schema_version": "0.1.0",
        "object_type": "evidence_bundle",
        "object_id": evidence_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_refs": [run_id],
        "artifact_refs": [
            {"kind": "run", "path": str(run_dir.relative_to(REPO_ROOT) / "run.yaml")},
            {"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")},
        ],
        "claim_scope": {"supported_claims": ["当前扫描包络内、给定控制策略下的静态承载力边界"]},
        "skill_refs": [candidate_skill_id],
        "cognition_refs": [cognition["object_id"]],
        "gaps": ["未覆盖系统真实极限承载力", "未覆盖长期时序 hosting capacity"],
        "taste_assessment_ref": taste_id,
        "report_refs": [report_id],
    }
    taste = {
        "schema_version": "0.1.0",
        "object_type": "taste_assessment",
        "object_id": taste_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_refs": [run_id],
        "grade": grade_from_result(effective_passed),
        "grade_reasoning": (
            "task004 candidate 在当前扫描包络内提高了控制策略相关承载力边界。"
            if effective_passed
            else "task004 skill mismatch probe 只给出单点结果，不能替代承载力边界扫描。"
            if mismatch_type == "skill_mismatch"
            else "task004 candidate 未提高当前扫描包络内承载力边界，只适合作为失败或边界材料。"
        ),
        "claim_ceiling": (
            "只能报告当前扫描包络内、给定控制策略下的静态承载力边界变化。"
            if effective_passed
            else "只能报告当前扫描包络内 candidate 未提高边界，不得写成系统固有承载力结论。"
        ),
        "recommended_report_type": report_type,
        "evidence_refs": [evidence_id],
        "review_status": "reviewed",
    }
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
        "observation_kind": "quality_improvement" if effective_passed else "process_drift",
        "statement": "task004 当前边界结论被限制在扫描包络和控制策略条件内。",
        "severity": "medium",
        "suggested_action": "继续控制 boundary overclaim。",
    }
    agent_trace = {
        "schema_version": "0.1.0",
        "object_type": "agent_trace",
        "object_id": trace_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "agent_role": "orchestrator",
        "trace_summary": "系统完成 task004 静态承载力边界扫描、评估、分级、证据组织和报告写回。",
        "event_count": 7,
        "prompt_observation_refs": [prompt_obs_id],
        "notable_behaviors": [
            "以扫描包络内边界为输出对象",
            "显式记录控制策略条件",
            "继续受 taste_assessment 约束",
        ],
    }
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
        "title": f"task004 real {strategy} report {serial}",
        "summary": (
            "task004 candidate 在当前扫描包络内提高了静态承载力边界。"
            if effective_passed
            else "task004 skill mismatch probe 不能作为承载力边界结果，应作为失败材料归档。"
            if mismatch_type == "skill_mismatch"
            else "task004 candidate 未提高当前扫描包络内静态承载力边界，应作为失败材料归档。"
        ),
        "evidence_bundle_refs": [evidence_id],
        "taste_assessment_ref": taste_id,
        "audience": "internal_team",
        "boundary_statement": "本报告仅对应当前扫描包络内、给定控制策略下的静态承载力边界，不构成系统普适承载力结论。",
        "failure_summary": run_object.get("failure_summary"),
        "next_steps": ["增加 boundary overclaim checker", "扩展更高接入包络或多工况"],
        "claim_summary": [taste["claim_ceiling"]],
    }
    write_run_outputs(
        run_dir,
        run_object,
        cognition,
        taste,
        evidence,
        agent_trace,
        prompt_observation,
        report,
        {"baseline_solution": baseline_solution, "candidate_solution": candidate_solution, "evaluation": evaluation},
        now,
    )
    return run_dir


def run_real_task005(strategy: str) -> Path:
    evaluator_module = load_module("task005_evaluator", TASK005_EVALUATOR_MODULE_PATH)
    task, baseline, evaluator, constraints = load_task005_real_inputs()
    baseline_solver = load_solver_from_artifact(
        "task005_baseline_solver",
        baseline.get("artifact_ref", {}),
        TASK005_BASELINE_SOLVER_PATH,
    )
    if strategy == "renewable-restoration":
        candidate_skill_id = "skill.power.renewable_restoration_candidate_task005"
        solver_path = TASK005_CANDIDATE_SOLVER_PATH
        mismatch_type = None
    elif strategy == "steady-state-mismatch":
        candidate_skill_id = "skill.power.steady_state_restoration_mismatch_task005"
        solver_path = TASK005_MISMATCH_SOLVER_PATH
        mismatch_type = "skill_mismatch"
    elif strategy == "renewable-underperformer":
        candidate_skill_id = "skill.power.renewable_underperformer_task005"
        solver_path = TASK005_PERF_SOLVER_PATH
        mismatch_type = "performance_failure"
    else:
        raise ValueError(f"unsupported task005 strategy: {strategy}")
    candidate_solver = load_module("task005_candidate_solver", solver_path)
    serial = next_run_serial_for_dir(RUNS_TASK005_DIR)
    run_dir = RUNS_TASK005_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    constraint_set = constraints["solver"]
    baseline_raw = baseline_solver.solve("ieee69_restoration", constraint_set)
    candidate_raw = candidate_solver.solve("ieee69_restoration", constraint_set)
    baseline_solution = {"control_settings": baseline_raw["control_settings"], "metrics": baseline_raw["baseline_solution"]}
    candidate_solution = {"control_settings": candidate_raw["control_settings"], "metrics": candidate_raw["reactive_power_settings"]}
    evaluation = evaluator_module.evaluate_real_solution(baseline_solution, candidate_solution)
    effective_passed = bool(evaluation["passed"]) and mismatch_type is None

    run_id = f"run.power.ieee69_restoration_resilience.{serial}"
    grade = grade_from_result(effective_passed)
    report_type = report_type_from_grade(grade)
    taste_id = f"taste.power.ieee69_restoration_resilience.{serial}"
    evidence_id = f"evidence.power.ieee69_restoration_resilience.{serial}"
    trace_id = f"agent_trace.power.ieee69_restoration_resilience.{serial}"
    prompt_obs_id = f"prompt_observation.power.ieee69_restoration_resilience.{serial}"
    report_id = f"report.power.ieee69_restoration_resilience.{'note' if effective_passed else 'memo'}_{serial}"
    cognition = build_task005_cognition(
        passed=effective_passed,
        serial=serial,
        run_id=run_id,
        strategy=strategy,
        mismatch_type=mismatch_type,
    )
    run_object = {
        "schema_version": "0.1.0",
        "object_type": "run",
        "object_id": run_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "archived",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "title": f"task005 real {strategy} run {serial}",
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_status": "completed" if effective_passed else "failed_experiment",
        "started_at": now,
        "ended_at": now,
        "attempt_index": int(serial),
        "trigger_reason": f"real_{strategy}",
        "input_snapshot": {
            "task": {"object_id": task["object_id"], "object_version": task["object_version"]},
            "evaluator": {"object_id": evaluator["object_id"], "object_version": evaluator["object_version"]},
        },
        "skill_refs": {
            "used": [{"object_id": "skill.power.baseline_solver", "object_version": "0.1.0"}],
            "produced": [{"object_id": candidate_skill_id, "object_version": skill_version_for_id(candidate_skill_id)}],
        },
        "result_summary": {
            "metrics": evaluation["candidate_solution"]["metrics"],
            "baseline_comparison": "improved" if evaluation["passed"] else "worse",
            "notes": evaluation["summary"],
        },
        "artifact_refs": [{"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")}],
        "agent_trace_refs": [{"kind": "trace", "object_id": trace_id}],
    }
    if not effective_passed:
        run_object["failure_summary"] = (
            "skill mismatch: steady-state result cannot substitute event-driven restoration"
            if mismatch_type == "skill_mismatch"
            else "candidate did not improve restoration result"
        )
    evidence = {
        "schema_version": "0.1.0",
        "object_type": "evidence_bundle",
        "object_id": evidence_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_refs": [run_id],
        "artifact_refs": [
            {"kind": "run", "path": str(run_dir.relative_to(REPO_ROOT) / "run.yaml")},
            {"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")},
        ],
        "claim_scope": {"supported_claims": ["当前 fault 场景和动作集合下的局部恢复结果"]},
        "skill_refs": [candidate_skill_id],
        "cognition_refs": [cognition["object_id"]],
        "gaps": ["未覆盖多故障", "未覆盖时序恢复"],
        "taste_assessment_ref": taste_id,
        "report_refs": [report_id],
    }
    taste = {
        "schema_version": "0.1.0",
        "object_type": "taste_assessment",
        "object_id": taste_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_refs": [run_id],
        "grade": grade,
        "grade_reasoning": (
            "task005 candidate 在当前 fault 场景下提高了恢复结果。"
            if effective_passed
            else "task005 当前结果只适合作为失败、边界或恢复线索材料。"
        ),
        "claim_ceiling": (
            "只能报告当前 fault 场景与动作集合下的恢复结果变化。"
            if effective_passed
            else "只能报告当前 fault 场景下的局部恢复结果，不得写成系统普适韧性结论。"
        ),
        "recommended_report_type": report_type,
        "evidence_refs": [evidence_id],
        "review_status": "reviewed",
    }
    prompt_observation = {
        "schema_version": "0.1.0",
        "object_type": "prompt_observation",
        "object_id": prompt_obs_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "observation_kind": "quality_improvement" if effective_passed else "process_drift",
        "statement": "task005 当前恢复结论被限制在 fault 场景与动作集合条件内。",
        "severity": "medium",
        "suggested_action": "继续控制 resilience overclaim。",
    }
    agent_trace = {
        "schema_version": "0.1.0",
        "object_type": "agent_trace",
        "object_id": trace_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "agent_role": "orchestrator",
        "trace_summary": "系统完成 task005 单故障恢复结果评估、分级、证据组织和报告写回。",
        "event_count": 7,
        "prompt_observation_refs": [prompt_obs_id],
        "notable_behaviors": [
            "以恢复结果而非稳态最优为核心",
            "显式记录关键负荷未恢复量",
            "继续受 taste_assessment 约束",
        ],
    }
    report = {
        "schema_version": "0.1.0",
        "object_type": "report",
        "object_id": report_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "report_type": report_type,
        "title": f"task005 real {strategy} report {serial}",
        "summary": (
            "task005 candidate 在当前 fault 场景下改善了局部恢复结果。"
            if effective_passed
            else "task005 当前结果未改善恢复结果，应作为失败或边界材料归档。"
        ),
        "evidence_bundle_refs": [evidence_id],
        "taste_assessment_ref": taste_id,
        "audience": "internal_team",
        "boundary_statement": "本报告仅对应当前单故障单工况与动作集合下的局部恢复结果，不构成系统普适韧性结论。",
        "failure_summary": run_object.get("failure_summary"),
        "next_steps": ["增加 resilience overclaim checker", "增加更丰富恢复动作"],
        "claim_summary": [taste["claim_ceiling"]],
    }
    write_run_outputs(
        run_dir,
        run_object,
        cognition,
        taste,
        evidence,
        agent_trace,
        prompt_observation,
        report,
        {"baseline_solution": baseline_solution, "candidate_solution": candidate_solution, "evaluation": evaluation},
        now,
    )
    return run_dir


def verify_task005_pipeline() -> None:
    required_paths = [
        TASK005_DIR / "research_brief.md",
        TASK005_DIR / "fault_context.yaml",
        TASK005_DIR / "restoration_scope.yaml",
        TASK005_DIR / "task.yaml",
        TASK005_DIR / "constraints.yaml",
        TASK005_DIR / "baseline.yaml",
        REPO_ROOT / "evaluators" / "task005_evaluator.py",
        REPO_ROOT / "evaluators" / "task005_evaluator.yaml",
        TASK005_BASELINE_SOLVER_PATH,
        TASK005_CANDIDATE_SOLVER_PATH,
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing required task005 paths: {missing}")
    latest = latest_nonempty_dir(RUNS_TASK005_DIR, "run_*")
    run_obj = load_yaml(latest / "run.yaml")
    if run_obj.get("task_ref") != "task.power.ieee69_restoration_resilience":
        raise RuntimeError("task005 run has wrong task_ref")
    metrics = load_json(latest / "metrics.json")
    if "restored_load_ratio" not in metrics.get("candidate_solution", {}).get("metrics", {}):
        raise RuntimeError("task005 metrics missing restored_load_ratio")


def verify_task005_failure_path() -> None:
    latest = None
    for run_dir in sorted(RUNS_TASK005_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if run_obj.get("trigger_reason") == "real_steady-state-mismatch":
            latest = run_dir
            break
    if latest is None:
        raise RuntimeError("no task005 skill mismatch run found")
    run_obj = load_yaml(latest / "run.yaml")
    cognition = load_yaml(latest / "cognition.yaml")
    if run_obj.get("run_status") != "failed_experiment":
        raise RuntimeError("task005 mismatch run is not failed_experiment")
    if cognition.get("cognition_type") != "failure":
        raise RuntimeError("task005 mismatch run did not produce failure cognition")


def verify_task005_cognition_stage() -> None:
    latest_semantic = latest_nonempty_dir(ANALYSIS_TASK005_DIR, "semantic_*")
    latest_upgrade = latest_nonempty_dir(ANALYSIS_TASK005_DIR, "upgrade_*")
    semantic = load_yaml(latest_semantic / "strategy_semantic_comparison.yaml")
    upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    if semantic.get("task_ref") != "task.power.ieee69_restoration_resilience":
        raise RuntimeError("task005 semantic comparison has wrong task_ref")
    dims = semantic.get("semantic_dimensions", {})
    for key in ["restoration_scope_match", "resilience_awareness", "critical_load_relevance", "performance_status"]:
        if key not in dims:
            raise RuntimeError(f"task005 semantic comparison missing {key}")
    if upgrade.get("task_ref") != "task.power.ieee69_restoration_resilience":
        raise RuntimeError("task005 cognition upgrade has wrong task_ref")


def upgrade_task005_cognition(comparison_dir: Path, semantic_dir: Path) -> Path:
    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    task_ref = comparison["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    upgrade_serial = f"{len(sorted(analysis_dir.glob('upgrade_*'))) + 1:04d}"
    upgrade_dir = analysis_dir / f"upgrade_{upgrade_serial}"
    upgrade_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    dims = semantic["semantic_dimensions"]
    right_status = dims.get("performance_status", {}).get("right")
    scope_winner = dims.get("restoration_scope_match", {}).get("winner")

    if right_status == "mismatch":
        decision = "upgrade"
        summary = "故障恢复任务必须显式面向 fault 后动作与恢复路径，稳态局部结果不能替代恢复策略。"
        statement = "task005 对照表明，稳态局部结果不能替代事件驱动恢复策略。"
        continue_investment = "prioritize"
    else:
        decision = "retain"
        summary = "语义正确但恢复性能失败的 candidate 不应与 skill mismatch 混同，应保留为可继续演化的恢复方向。"
        statement = "task005 对照表明，语义正确但性能失败的恢复策略仍应保留为后续可改进方向。"
        continue_investment = "continue"

    novelty = {
        "schema_version": "0.1.0",
        "object_type": "novelty_assessment",
        "object_id": f"novelty.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task005_failure_taxonomy"},
        "task_ref": task_ref,
        "assessed_object_ref": semantic.get("right_skill_ref", ""),
        "supporting_refs": [comparison["object_id"], semantic["object_id"]],
        "novelty_level": "medium",
        "research_value_level": "high",
        "continue_investment": continue_investment,
        "evidence_strength": "low",
        "summary": summary,
        "reasons": [
            f"restoration_scope_match winner={scope_winner}",
            f"performance_status right={right_status}",
        ],
    }
    upgraded_cognition = {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": f"cognition.power.upgraded_{problem_name}_{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mode": "task005_restoration_upgrade"},
        "cognition_type": "candidate",
        "statement": statement,
        "evidence_refs": [comparison["object_id"], semantic["object_id"], novelty["object_id"]],
        "scope_boundary": {"task": task_ref, "mode": "task005_comparative_upgrade"},
        "confidence_level": "medium",
        "derived_from_run_refs": [comparison["left_run_ref"], comparison["right_run_ref"]],
        "promotion_status": "proposed",
    }
    upgraded_path = write_cognition_asset_and_registry(upgraded_cognition, run_id=comparison["left_run_ref"], when=now)
    cognition_upgrade = {
        "schema_version": "0.1.0",
        "object_type": "cognition_upgrade",
        "object_id": f"cognition_upgrade.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task005_failure_taxonomy"},
        "task_ref": task_ref,
        "source_cognition_ref": comparison["cognition_refs"][0],
        "semantic_comparison_ref": semantic["object_id"],
        "novelty_assessment_ref": novelty["object_id"],
        "upgraded_cognition_ref": upgraded_cognition["object_id"],
        "evidence_strength": "low",
        "decision": decision,
        "rationale": summary,
        "claim_adjustment": "task005 恢复认知只支持当前 fault 场景、动作集合和单工况条件下的局部恢复判断。",
    }
    write_yaml(upgrade_dir / "novelty_assessment.yaml", novelty)
    write_yaml(upgrade_dir / "cognition_upgrade.yaml", cognition_upgrade)
    write_yaml(upgrade_dir / "upgraded_cognition.yaml", upgraded_cognition)
    with (upgrade_dir / "writeback.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "novelty_assessment": str((upgrade_dir / "novelty_assessment.yaml").relative_to(REPO_ROOT)),
                "cognition_upgrade": str((upgrade_dir / "cognition_upgrade.yaml").relative_to(REPO_ROOT)),
                "upgraded_cognition_asset": str(upgraded_path.relative_to(REPO_ROOT)),
                "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")
    return upgrade_dir
def verify_task004_pipeline() -> None:
    ensure_valid_schemas()
    required_paths = [
        TASK004_DIR / "research_brief.md",
        TASK004_DIR / "grid_context.yaml",
        TASK004_DIR / "renewable_context.yaml",
        TASK004_DIR / "hosting_capacity_scope.yaml",
        TASK004_DIR / "control_scope.yaml",
        TASK004_DIR / "task.yaml",
        TASK004_DIR / "constraints.yaml",
        TASK004_DIR / "baseline.yaml",
        TASK004_DIR / "targets.yaml",
        TASK004_DIR / "assumptions.yaml",
        TASK004_DIR / "runtime_helpers.py",
        REPO_ROOT / "evaluators" / "task004_evaluator.py",
        REPO_ROOT / "evaluators" / "task004_evaluator.yaml",
        TASK004_BASELINE_SOLVER_PATH,
        TASK004_CANDIDATE_SOLVER_PATH,
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"missing required task004 paths: {missing}")
    latest_success = latest_nonempty_dir(RUNS_TASK004_DIR, "run_*")
    run_obj = load_yaml(latest_success / "run.yaml")
    if run_obj.get("task_ref") != "task.power.ieee69_hosting_capacity":
        raise RuntimeError("task004 run has wrong task_ref")
    metrics = load_json(latest_success / "metrics.json")
    if "hosting_capacity_level" not in metrics.get("candidate_solution", {}).get("metrics", {}):
        raise RuntimeError("task004 candidate metrics missing hosting_capacity_level")


def verify_task004_boundary_overclaim() -> None:
    analysis_dir = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "boundary_overclaim_*")
    check = load_yaml(analysis_dir / "boundary_overclaim_check.yaml")
    if check.get("decision") not in {"accept", "downgrade"}:
        raise RuntimeError("task004 boundary overclaim check decision invalid")


def verify_task004_failure_path() -> None:
    latest_failure = None
    for run_dir in sorted(RUNS_TASK004_DIR.glob("run_*"), reverse=True):
        if not run_dir.is_dir() or not any(run_dir.iterdir()):
            continue
        run_obj = load_yaml(run_dir / "run.yaml")
        if run_obj.get("trigger_reason") == "real_single-point-mismatch":
            latest_failure = run_dir
            break
    if latest_failure is None:
        raise RuntimeError("no task004 skill mismatch run found")
    run_obj = load_yaml(latest_failure / "run.yaml")
    cognition = load_yaml(latest_failure / "cognition.yaml")
    taste = load_yaml(latest_failure / "taste_assessment.yaml")
    if run_obj.get("run_status") != "failed_experiment":
        raise RuntimeError("task004 mismatch run is not failed_experiment")
    if run_obj.get("metadata", {}).get("mismatch_type") != "skill_mismatch":
        raise RuntimeError("task004 mismatch run missing skill_mismatch metadata")
    if cognition.get("cognition_type") != "failure":
        raise RuntimeError("task004 mismatch run did not produce failure cognition")
    if taste.get("grade") != "huimo":
        raise RuntimeError("task004 mismatch run did not downgrade taste")


def verify_task004_cognition_stage() -> None:
    latest_semantic = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "semantic_*")
    latest_upgrade = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "upgrade_*")
    semantic = load_yaml(latest_semantic / "strategy_semantic_comparison.yaml")
    upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    if semantic.get("task_ref") != "task.power.ieee69_hosting_capacity":
        raise RuntimeError("task004 semantic comparison has wrong task_ref")
    dims = semantic.get("semantic_dimensions", {})
    for key in ["hosting_capacity_awareness", "boundary_conditioning", "performance_status"]:
        if key not in dims:
            raise RuntimeError(f"task004 semantic comparison missing {key}")
    if upgrade.get("task_ref") != "task.power.ieee69_hosting_capacity":
        raise RuntimeError("task004 cognition upgrade has wrong task_ref")


def verify_task004_literature_stage() -> None:
    latest_literature = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "literature_*")
    latest_explanations = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "explanations_*")
    latest_upgrade = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "upgrade_*")
    literature_alignment = load_yaml(latest_literature / "literature_alignment.yaml")
    explanation_alignment = load_yaml(latest_explanations / "explanation_alignment.yaml")
    cognition_upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    if literature_alignment.get("task_ref") != "task.power.ieee69_hosting_capacity":
        raise RuntimeError("task004 literature alignment has wrong task_ref")
    if not literature_alignment.get("literature_refs"):
        raise RuntimeError("task004 literature alignment missing refs")
    if explanation_alignment.get("evidence_strength") not in {"medium", "high"}:
        raise RuntimeError("task004 explanation alignment evidence strength too weak")
    if cognition_upgrade.get("literature_alignment_ref") is None:
        raise RuntimeError("task004 cognition upgrade missing literature_alignment_ref")
    if cognition_upgrade.get("explanation_alignment_ref") is None:
        raise RuntimeError("task004 cognition upgrade missing explanation_alignment_ref")


def upgrade_task004_cognition(
    comparison_dir: Path,
    semantic_dir: Path,
    literature_dir: Path | None = None,
    explanation_dir: Path | None = None,
) -> Path:
    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    literature_alignment = (
        load_yaml(literature_dir / "literature_alignment.yaml") if literature_dir is not None else None
    )
    explanation_alignment = (
        load_yaml(explanation_dir / "explanation_alignment.yaml") if explanation_dir is not None else None
    )
    task_ref = comparison["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    upgrade_serial = f"{len(sorted(analysis_dir.glob('upgrade_*'))) + 1:04d}"
    upgrade_dir = analysis_dir / f"upgrade_{upgrade_serial}"
    upgrade_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    dims = semantic["semantic_dimensions"]
    right_status = dims.get("performance_status", {}).get("right")
    boundary_winner = dims.get("boundary_conditioning", {}).get("winner")
    explanation_strength = explanation_alignment.get("evidence_strength", "low") if explanation_alignment else "low"
    explanation_excerpt_refs = (
        explanation_alignment_excerpt_refs(explanation_alignment) if explanation_alignment is not None else []
    )

    if right_status == "mismatch":
        decision = "upgrade"
        summary = "承载力评估必须以边界扫描为对象，单点运行结果不能替代条件化边界判断。"
        statement = "task004 对照表明，单点运行结果不能替代控制策略相关的承载力边界扫描。"
        continue_investment = "prioritize"
    else:
        decision = "retain"
        summary = "承载力边界必须被表述为控制策略相关边界，而不是系统固有唯一承载力。"
        statement = "task004 对照表明，当前边界判断应始终绑定控制策略和扫描包络条件。"
        continue_investment = "continue"

    novelty = {
        "schema_version": "0.1.0",
        "object_type": "novelty_assessment",
        "object_id": f"novelty.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task004_boundary_cognition"},
        "task_ref": task_ref,
        "assessed_object_ref": semantic.get("right_skill_ref", ""),
        "supporting_refs": [
            comparison["object_id"],
            semantic["object_id"],
            *([literature_alignment["object_id"]] if literature_alignment is not None else []),
            *([explanation_alignment["object_id"]] if explanation_alignment is not None else []),
            *explanation_excerpt_refs,
        ],
        "novelty_level": "medium",
        "research_value_level": "high",
        "continue_investment": continue_investment,
        "evidence_strength": explanation_strength,
        "summary": summary,
        "reasons": [
            f"boundary_conditioning winner={boundary_winner}",
            f"performance_status right={right_status}",
            *(
                [f"novelty_position={literature_alignment.get('novelty_position', 'unclear')}"]
                if literature_alignment is not None
                else []
            ),
            *(
                [f"explanation_relation={explanation_alignment.get('overall_relation', 'unclear')}"]
                if explanation_alignment is not None
                else []
            ),
        ],
    }
    upgraded_cognition = {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": f"cognition.power.upgraded_{problem_name}_{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mode": "task004_boundary_upgrade"},
        "cognition_type": "candidate",
        "statement": statement,
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
            "mode": "task004_boundary_upgrade",
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [comparison["left_run_ref"], comparison["right_run_ref"]],
        "promotion_status": "proposed",
    }
    upgraded_path = write_cognition_asset_and_registry(upgraded_cognition, run_id=comparison["left_run_ref"], when=now)
    cognition_upgrade = {
        "schema_version": "0.1.0",
        "object_type": "cognition_upgrade",
        "object_id": f"cognition_upgrade.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task004_boundary_cognition"},
        "task_ref": task_ref,
        "source_cognition_ref": comparison["cognition_refs"][0],
        "semantic_comparison_ref": semantic["object_id"],
        "novelty_assessment_ref": novelty["object_id"],
        "literature_alignment_ref": literature_alignment["object_id"] if literature_alignment is not None else None,
        "explanation_alignment_ref": explanation_alignment["object_id"] if explanation_alignment is not None else None,
        "explanation_excerpt_refs": explanation_excerpt_refs,
        "upgraded_cognition_ref": upgraded_cognition["object_id"],
        "evidence_strength": explanation_strength,
        "decision": decision,
        "rationale": summary
        + (
            f" 当前文献对齐将其定位为 `{literature_alignment.get('novelty_position', 'unclear')}`。"
            if literature_alignment is not None
            else ""
        )
        + (
            f" explanation alignment 提供了 {len(explanation_excerpt_refs)} 条 excerpt 级证据，evidence_strength=`{explanation_strength}`。"
            if explanation_alignment is not None
            else ""
        ),
        "claim_adjustment": "task004 边界认知只支持当前扫描包络内、给定控制策略下的静态边界判断。",
    }
    write_yaml(upgrade_dir / "novelty_assessment.yaml", novelty)
    write_yaml(upgrade_dir / "cognition_upgrade.yaml", cognition_upgrade)
    write_yaml(upgrade_dir / "upgraded_cognition.yaml", upgraded_cognition)
    with (upgrade_dir / "writeback.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "novelty_assessment": str((upgrade_dir / "novelty_assessment.yaml").relative_to(REPO_ROOT)),
                "cognition_upgrade": str((upgrade_dir / "cognition_upgrade.yaml").relative_to(REPO_ROOT)),
                "upgraded_cognition_asset": str(upgraded_path.relative_to(REPO_ROOT)),
                "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")
    return upgrade_dir


def verify_task004_task_mismatch() -> None:
    latest = latest_nonempty_dir(ANALYSIS_TASK004_DIR, "mismatch_*")
    check = load_yaml(latest / "task_mismatch_check.yaml")
    if check.get("decision") not in {"execute", "freeze"}:
        raise RuntimeError("task004 task mismatch decision invalid")


def build_task005_cognition(
    *,
    passed: bool,
    serial: str,
    run_id: str,
    strategy: str,
    mismatch_type: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    if mismatch_type == "skill_mismatch":
        statement = "当前 task005 skill-mismatch probe 表明，稳态结果不能直接替代事件驱动恢复策略。"
    else:
        statement = (
            "当前 task005 真实运行表明，candidate 在当前 fault 场景下改善了恢复结果。"
            if passed
            else "当前 task005 真实运行表明，candidate 未改善当前 fault 场景下的恢复结果。"
        )
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": (
            f"cognition.power.ieee69_restoration_resilience_runtime_{serial}"
            if passed and mismatch_type is None
            else f"cognition.power.ieee69_restoration_resilience_runtime_failure_{serial}"
        ),
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"strategy": strategy, "mismatch_type": mismatch_type or ""},
        "cognition_type": "candidate" if passed and mismatch_type is None else "failure",
        "statement": statement,
        "evidence_refs": [run_id],
        "scope_boundary": {
            "task": "task.power.ieee69_restoration_resilience",
            "mode": f"real_{strategy}",
            "fault": "single_line_outage",
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [run_id],
        "promotion_status": "proposed",
    }


def check_task005_resilience_overclaim(run_dir: Path) -> Path:
    report = load_yaml(run_dir / "report.yaml")
    run_obj = load_yaml(run_dir / "run.yaml")
    serial = utc_now().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    output_dir = ANALYSIS_TASK005_DIR / f"resilience_overclaim_{serial}"
    output_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    summary_text = " ".join([report.get("summary", ""), report.get("boundary_statement", ""), *report.get("claim_summary", [])])
    flagged = any(token in summary_text for token in ["系统具有韧性", "普适恢复能力", "任意故障"])
    result = {
        "schema_version": "0.1.0",
        "object_type": "boundary_overclaim_check",
        "object_id": f"boundary_overclaim.power.ieee69_restoration_resilience.{serial}",
        "created_at": now,
        "status": "flagged" if flagged else "controlled",
        "task_ref": run_obj["task_ref"],
        "run_ref": run_obj["object_id"],
        "decision": "downgrade" if flagged else "accept",
        "rationale": "报告出现超出单故障单工况边界的韧性表述。" if flagged else "报告当前韧性边界表述受控。",
    }
    write_yaml(output_dir / "boundary_overclaim_check.yaml", result)
    return output_dir


def check_task005_mismatch(source_dir: Path | None = None) -> Path:
    source = source_dir or TASK005_DIR
    required = {
        "research_brief": source / "research_brief.md",
        "grid_context": source / "grid_context.yaml",
        "fault_context": source / "fault_context.yaml",
        "renewable_context": source / "renewable_context.yaml",
        "restoration_scope": source / "restoration_scope.yaml",
        "constraints": source / "constraints.yaml",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    gaps: list[str] = []
    if not missing:
        fault = load_yaml(required["fault_context"])
        scope = load_yaml(required["restoration_scope"])
        if not fault.get("faulted_branch"):
            gaps.append("fault_context.faulted_branch")
        if not scope.get("critical_load_buses"):
            gaps.append("restoration_scope.critical_load_buses")
    serial = utc_now().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    output_dir = ANALYSIS_TASK005_DIR / f"mismatch_{serial}"
    output_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    blocked = bool(missing or gaps)
    result = {
        "schema_version": "0.1.0",
        "object_type": "task_mismatch_check",
        "object_id": f"task_mismatch.power.ieee69_restoration_resilience.{serial}",
        "created_at": now,
        "status": "blocked" if blocked else "ready",
        "task_ref": "task.power.ieee69_restoration_resilience",
        "source_dir": str(source.relative_to(REPO_ROOT)) if source.is_relative_to(REPO_ROOT) else str(source),
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "decision": "freeze" if blocked else "execute",
        "rationale": "task005 故障恢复定义缺失关键输入，不应进入真实执行。" if blocked else "task005 恢复任务具备最小执行条件。",
    }
    write_yaml(output_dir / "task_mismatch_check.yaml", result)
    note = {
        "created_at": now,
        "task_ref": result["task_ref"],
        "decision": result["decision"],
        "missing_inputs": missing,
        "assumption_gaps": gaps,
        "required_next_inputs": missing + gaps,
    }
    write_yaml(output_dir / "task_refinement_note.yaml", note)
    if blocked:
        cognition = {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.ieee69_restoration_resilience_task_mismatch_{serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {"mismatch_type": "task_mismatch"},
            "cognition_type": "failure",
            "statement": "当前 task005 brief 缺失故障恢复定义关键项，应冻结执行并补齐故障与恢复边界。",
            "evidence_refs": [result["object_id"]],
            "scope_boundary": {"task": result["task_ref"], "mode": "task_mismatch_check"},
            "confidence_level": "medium",
            "promotion_status": "proposed",
        }
        write_yaml(output_dir / "cognition.yaml", cognition)
        write_cognition_asset_and_registry(cognition, run_id=result["object_id"], when=now)
    return output_dir


def upgrade_task003_cognition(
    comparison_dir: Path,
    semantic_dir: Path,
    literature_dir: Path | None = None,
    explanation_dir: Path | None = None,
) -> Path:
    ensure_valid_schemas()
    comparison = load_yaml(comparison_dir / "strategy_comparison.yaml")
    semantic = load_yaml(semantic_dir / "strategy_semantic_comparison.yaml")
    literature_alignment = (
        load_yaml(literature_dir / "literature_alignment.yaml") if literature_dir is not None else None
    )
    explanation_alignment = (
        load_yaml(explanation_dir / "explanation_alignment.yaml") if explanation_dir is not None else None
    )
    task_ref = comparison["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    upgrade_serial = f"{len(sorted(analysis_dir.glob('upgrade_*'))) + 1:04d}"
    upgrade_dir = analysis_dir / f"upgrade_{upgrade_serial}"
    upgrade_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    dims = semantic["semantic_dimensions"]
    left_run_ref = comparison["left_run_ref"]
    right_run_ref = comparison["right_run_ref"]
    left_skill_ref = semantic.get("left_skill_ref", "")
    right_skill_ref = semantic.get("right_skill_ref", "")
    control_space_winner = dims.get("control_space_match", {}).get("winner")
    performance_dimension = dims.get("performance_status", {})
    right_status = performance_dimension.get("right")
    explanation_strength = explanation_alignment.get("evidence_strength", "low") if explanation_alignment else "low"
    explanation_excerpt_refs = (
        explanation_alignment_excerpt_refs(explanation_alignment) if explanation_alignment is not None else []
    )

    if control_space_winner == "left" and right_status == "mismatch":
        decision = "upgrade"
        summary = "显式使用新能源 inverter 控制空间，是判断 candidate 是否回答 task003 本体的重要条件。"
        statement = (
            "task003 对照表明，旧 weak-shunt 路线即使数值更好，也不能替代显式使用 inverter 控制空间的 candidate。"
        )
        continue_investment = "prioritize"
    elif right_status == "failed":
        decision = "retain"
        summary = "语义正确但性能失败的 candidate 不应与 skill mismatch 混同，应保留为后续可演化实现边界。"
        statement = (
            "task003 对照表明，使用正确新能源控制空间但当前性能失败的 candidate，仍应保留为可继续改进的方向。"
        )
        continue_investment = "continue"
    else:
        decision = "freeze"
        summary = "当前比较只支持局部判断，尚不足以上升为更强认知。"
        statement = "task003 当前比较材料不足以支持更高层升级认知。"
        continue_investment = "observe"

    novelty = {
        "schema_version": "0.1.0",
        "object_type": "novelty_assessment",
        "object_id": f"novelty.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task003_failure_taxonomy"},
        "task_ref": task_ref,
        "assessed_object_ref": right_skill_ref,
        "supporting_refs": [
            comparison["object_id"],
            semantic["object_id"],
            *([literature_alignment["object_id"]] if literature_alignment is not None else []),
            *([explanation_alignment["object_id"]] if explanation_alignment is not None else []),
            *explanation_excerpt_refs,
        ],
        "novelty_level": "medium",
        "research_value_level": "high" if continue_investment in {"continue", "prioritize"} else "medium",
        "continue_investment": continue_investment,
        "evidence_strength": explanation_strength,
        "summary": summary,
        "reasons": [
            f"control_space_match winner={control_space_winner}",
            f"performance_status right={right_status}",
            f"left_skill={left_skill_ref}",
            f"right_skill={right_skill_ref}",
            *(
                [f"novelty_position={literature_alignment.get('novelty_position', 'unclear')}"]
                if literature_alignment is not None
                else []
            ),
            *(
                [f"explanation_relation={explanation_alignment.get('overall_relation', 'unclear')}"]
                if explanation_alignment is not None
                else []
            ),
        ],
    }

    upgraded_cognition = None
    upgraded_cognition_path = None
    if decision in {"upgrade", "retain"}:
        upgraded_cognition = {
            "schema_version": "0.1.0",
            "object_type": "cognition",
            "object_id": f"cognition.power.upgraded_{problem_name}_{upgrade_serial}",
            "object_version": "0.1.0",
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "metadata": {"mode": "task003_cognition_upgrade"},
            "cognition_type": "candidate",
            "statement": statement,
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
                "mode": "task003_comparative_upgrade",
            },
            "confidence_level": "medium",
            "derived_from_run_refs": [left_run_ref, right_run_ref],
            "promotion_status": "proposed",
            "uncertainty_notes": (
                "当前仍只基于单代表工况与最小策略集合。"
                if literature_alignment is None
                else "当前认知已结合 task003 文献对齐与 excerpt 级 explanation 证据，但仍未覆盖时序新能源工况。"
            ),
        }
        upgraded_cognition_path = write_cognition_asset_and_registry(
            upgraded_cognition,
            run_id=left_run_ref,
            when=now,
        )

    cognition_upgrade = {
        "schema_version": "0.1.0",
        "object_type": "cognition_upgrade",
        "object_id": f"cognition_upgrade.power.{problem_name}.{upgrade_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task003_failure_taxonomy"},
        "task_ref": task_ref,
        "source_cognition_ref": comparison["cognition_refs"][0],
        "semantic_comparison_ref": semantic["object_id"],
        "novelty_assessment_ref": novelty["object_id"],
        "literature_alignment_ref": literature_alignment["object_id"] if literature_alignment is not None else None,
        "explanation_alignment_ref": explanation_alignment["object_id"] if explanation_alignment is not None else None,
        "explanation_excerpt_refs": explanation_excerpt_refs,
        "upgraded_cognition_ref": upgraded_cognition["object_id"] if upgraded_cognition else None,
        "evidence_strength": explanation_strength,
        "decision": decision,
        "rationale": summary
        + (
            f" 当前文献对齐将其定位为 `{literature_alignment.get('novelty_position', 'unclear')}`。"
            if literature_alignment is not None
            else ""
        )
        + (
            f" explanation alignment 提供了 {len(explanation_excerpt_refs)} 条 excerpt 级证据，evidence_strength=`{explanation_strength}`。"
            if explanation_alignment is not None
            else ""
        ),
        "claim_adjustment": "task003 当前认知升级仍只支持单代表工况下的 failure taxonomy 与任务本体判断。",
    }
    write_yaml(upgrade_dir / "novelty_assessment.yaml", novelty)
    write_yaml(upgrade_dir / "cognition_upgrade.yaml", cognition_upgrade)
    if upgraded_cognition is not None:
        write_yaml(upgrade_dir / "upgraded_cognition.yaml", upgraded_cognition)
    with (upgrade_dir / "writeback.json").open("w", encoding="utf-8") as f:
        payload = {
            "novelty_assessment": str((upgrade_dir / "novelty_assessment.yaml").relative_to(REPO_ROOT)),
            "cognition_upgrade": str((upgrade_dir / "cognition_upgrade.yaml").relative_to(REPO_ROOT)),
            "cognition_registry": str(COGNITION_REGISTRY_PATH.relative_to(REPO_ROOT)),
        }
        if upgraded_cognition_path is not None:
            payload["upgraded_cognition_asset"] = str(upgraded_cognition_path.relative_to(REPO_ROOT))
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return upgrade_dir


def build_task003_cognition(
    *,
    passed: bool,
    serial: str,
    run_id: str,
    strategy: str,
    mismatch_type: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    if mismatch_type == "skill_mismatch":
        statement = (
            "当前 task003 skill-mismatch probe 表明，仅沿用传统 weak-shunt 而不显式利用 inverter 无功支撑，"
            "不足以代表新能源接入场景下的优化调控能力。"
        )
        cognition_type = "failure"
    elif mismatch_type == "performance_failure":
        statement = (
            "当前 task003 performance-failure probe 表明，candidate 使用了新能源 inverter 控制空间，"
            "但当前参数方向未能优于固定 Q 基线，因此只能保留为语义正确但性能失败的边界认知。"
        )
        cognition_type = "failure"
    elif passed:
        statement = (
            "当前 task003 真实运行表明，在单代表工况下，显式利用 PV inverter 无功支撑的 candidate "
            "可相对固定 Q 基线改善网损和电压偏差，且未新增约束违反。"
        )
        cognition_type = "candidate"
    else:
        statement = (
            "当前 task003 真实运行表明，新能源-aware candidate 未能稳定满足 evaluator 要求，"
            "只能作为边界材料而非有效方法。"
        )
        cognition_type = "failure"
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": (
            f"cognition.power.ieee69_renewable_reactive_opt_runtime_{serial}"
            if cognition_type == "candidate"
            else f"cognition.power.ieee69_renewable_reactive_opt_runtime_failure_{serial}"
        ),
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"strategy": strategy, "mismatch_type": mismatch_type or ""},
        "cognition_type": cognition_type,
        "statement": statement,
        "evidence_refs": [run_id],
        "scope_boundary": {
            "task": "task.power.ieee69_renewable_reactive_opt",
            "mode": f"real_{strategy}",
            "snapshot": "single_representative",
        },
        "confidence_level": "medium",
        "derived_from_run_refs": [run_id],
        "promotion_status": "proposed",
    }


def task003_solver_for_strategy(strategy: str) -> tuple[str, Path, str | None]:
    if strategy == "inverter-support":
        return "skill.power.renewable_inverter_reactive_optimizer_task003", TASK003_RENEWABLE_SOLVER_PATH, None
    if strategy == "inverter-underperformer":
        return (
            "skill.power.renewable_inverter_underperformer_task003",
            TASK003_UNDERPERFORMER_SOLVER_PATH,
            "performance_failure",
        )
    if strategy == "weak-shunt-mismatch":
        return "skill.power.weak_bus_shunt_optimizer", TASK003_WEAK_SHUNT_SOLVER_PATH, "skill_mismatch"
    raise ValueError(f"unsupported task003 strategy: {strategy}")


def run_real_task003(strategy: str) -> Path:
    ensure_valid_schemas()
    evaluator_module = load_module("task003_evaluator", TASK003_EVALUATOR_MODULE_PATH)
    task, baseline, evaluator, constraints = load_task003_real_inputs()
    baseline_solver = load_solver_from_artifact(
        "task003_baseline_solver",
        baseline.get("artifact_ref", {}),
        TASK003_BASELINE_SOLVER_PATH,
    )
    candidate_skill_id, solver_path, mismatch_type = task003_solver_for_strategy(strategy)
    candidate_solver = load_module("task003_candidate_solver", solver_path)
    serial = next_run_serial_for_dir(RUNS_TASK003_DIR)
    run_dir = RUNS_TASK003_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    constraint_set = constraints["solver"]
    network_model = str(constraint_set.get("network_model", "ieee69_with_renewables"))
    baseline_solution_raw = baseline_solver.solve(network_model, constraint_set)
    candidate_solution_raw = candidate_solver.solve(network_model, constraint_set)
    baseline_solution = {
        "control_settings": baseline_solution_raw["control_settings"],
        "metrics": baseline_solution_raw["baseline_solution"],
    }
    candidate_solution = {
        "control_settings": candidate_solution_raw["control_settings"],
        "metrics": candidate_solution_raw["reactive_power_settings"],
    }
    evaluation = evaluator_module.evaluate_real_solution(baseline_solution, candidate_solution)
    effective_passed = bool(evaluation["passed"]) and mismatch_type is None

    run_id = f"run.power.ieee69_renewable_reactive_opt.{serial}"
    grade = grade_from_result(effective_passed)
    report_type = report_type_from_grade(grade)
    taste_id = f"taste.power.ieee69_renewable_reactive_opt.{serial}"
    evidence_id = f"evidence.power.ieee69_renewable_reactive_opt.{serial}"
    trace_id = f"agent_trace.power.ieee69_renewable_reactive_opt.{serial}"
    prompt_obs_id = f"prompt_observation.power.ieee69_renewable_reactive_opt.{serial}"
    report_id = f"report.power.ieee69_renewable_reactive_opt.{'note' if effective_passed else 'memo'}_{serial}"
    cognition = build_task003_cognition(
        passed=effective_passed,
        serial=serial,
        run_id=run_id,
        strategy=strategy,
        mismatch_type=mismatch_type,
    )

    failure_summary = None
    if not effective_passed:
        failure_summary = (
            "skill mismatch: candidate did not use the renewable inverter control space"
            if mismatch_type == "skill_mismatch"
            else "candidate did not satisfy task003 evaluator pass criteria"
        )
    run_object = {
        "schema_version": "0.1.0",
        "object_type": "run",
        "object_id": run_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "archived",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "title": f"task003 real {strategy} run {serial}",
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_status": "completed" if effective_passed else "failed_experiment",
        "started_at": now,
        "ended_at": now,
        "attempt_index": int(serial),
        "trigger_reason": f"real_{strategy}",
        "input_snapshot": {
            "task": {"object_id": task["object_id"], "object_version": task["object_version"]},
            "evaluator": {"object_id": evaluator["object_id"], "object_version": evaluator["object_version"]},
        },
        "skill_refs": {
            "used": [{"object_id": "skill.power.baseline_solver", "object_version": "0.1.0"}],
            "produced": [{"object_id": candidate_skill_id, "object_version": skill_version_for_id(candidate_skill_id)}],
        },
        "result_summary": {
            "metrics": evaluation["candidate_solution"]["metrics"],
            "baseline_comparison": "improved" if evaluation["passed"] else "worse",
            "notes": evaluation["summary"],
        },
        "artifact_refs": [{"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")}],
        "agent_trace_refs": [{"kind": "trace", "object_id": trace_id}],
    }
    if failure_summary is not None:
        run_object["failure_summary"] = failure_summary

    evidence = {
        "schema_version": "0.1.0",
        "object_type": "evidence_bundle",
        "object_id": evidence_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_refs": [run_id],
        "artifact_refs": [
            {"kind": "run", "path": str(run_dir.relative_to(REPO_ROOT) / "run.yaml")},
            {"kind": "metrics", "path": str(run_dir.relative_to(REPO_ROOT) / "metrics.json")},
        ],
        "claim_scope": {"supported_claims": ["当前新能源接入单代表工况下的阶段性结论"]},
        "skill_refs": [candidate_skill_id],
        "cognition_refs": [cognition["object_id"]],
        "gaps": ["未覆盖时序波动", "未覆盖经济代价"],
        "taste_assessment_ref": taste_id,
        "report_refs": [report_id],
    }
    if mismatch_type == "skill_mismatch":
        evidence["claim_scope"] = {"supported_claims": ["旧 skill 在新能源控制空间中的失配边界"]}
        evidence["gaps"].append("该 failure probe 不代表真实新能源-aware candidate")

    taste = {
        "schema_version": "0.1.0",
        "object_type": "taste_assessment",
        "object_id": taste_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_refs": [run_id],
        "grade": grade,
        "grade_reasoning": (
            "task003 inverter support candidate 在单代表工况下相对基线形成阶段性改进。"
            if effective_passed
            else "task003 skill mismatch probe 即使指标改善，也未使用新能源 inverter 控制空间，只能作为语义失配边界材料。"
            if mismatch_type == "skill_mismatch"
            else "task003 performance failure probe 使用了新能源 inverter 控制空间，但当前参数方向未能形成成效证据。"
            if mismatch_type == "performance_failure"
            else "task003 failure path 只能作为边界或失配材料。"
        ),
        "claim_ceiling": (
            "可报告为单代表工况下新能源 inverter 无功支撑的阶段性有效路径，不得上升为普适新能源调控结论。"
            if effective_passed
            else "只能报告当前失配或失败边界，不得包装成有效新能源控制方法。"
        ),
        "recommended_report_type": report_type,
        "evidence_refs": [evidence_id],
        "review_status": "reviewed",
    }
    prompt_observation = {
        "schema_version": "0.1.0",
        "object_type": "prompt_observation",
        "object_id": prompt_obs_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "observation_kind": "quality_improvement" if effective_passed else "process_drift",
        "statement": (
            "task003 success path 保留了新能源任务的 claim 边界。"
            if effective_passed
            else "task003 failure path 将失配或性能失败结果压到边界材料。"
        ),
        "severity": "medium",
        "suggested_action": "继续区分新能源-aware candidate 与 failure probe。",
    }
    agent_trace = {
        "schema_version": "0.1.0",
        "object_type": "agent_trace",
        "object_id": trace_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "run_ref": run_id,
        "agent_role": "orchestrator",
        "trace_summary": "系统完成 task003 brief-derived task package 的真实运行、评估、分级、证据组织和报告写回。",
        "event_count": 7,
        "prompt_observation_refs": [prompt_obs_id],
        "notable_behaviors": [
            "复用 task002 IEEE69 基础网络",
            "显式记录 reactive_support_effort",
            "报告继续受 taste_assessment 约束",
        ],
    }
    report = {
        "schema_version": "0.1.0",
        "object_type": "report",
        "object_id": report_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mismatch_type": mismatch_type or ""},
        "task_ref": task["object_id"],
        "report_type": report_type,
        "title": f"task003 real {strategy} report {serial}",
        "summary": (
            "task003 inverter support candidate 在单代表工况下相对固定 Q 基线获得阶段性改进。"
            if effective_passed
            else "task003 failure probe 暴露控制对象失配边界，应作为失败认知材料归档。"
        ),
        "evidence_bundle_refs": [evidence_id],
        "taste_assessment_ref": taste_id,
        "audience": "internal_team",
        "boundary_statement": "本报告仅对应当前新能源接入单代表工况，不构成时序或普适调控结论。",
        "failure_summary": failure_summary,
        "next_steps": ["增加 task mismatch freeze 检查", "补充新能源文献对齐"],
        "claim_summary": [taste["claim_ceiling"]],
    }
    write_run_outputs(
        run_dir,
        run_object,
        cognition,
        taste,
        evidence,
        agent_trace,
        prompt_observation,
        report,
        {"baseline_solution": baseline_solution, "candidate_solution": candidate_solution, "evaluation": evaluation},
        now,
    )
    return run_dir


def build_internal_task002_comparison(run_id: str) -> Path:
    ensure_valid_schemas()
    run_obj, metrics_payload, report = load_run_payload(run_id)
    task_ref = run_obj["task_ref"]
    if task_ref != "task.power.ieee69_reactive_opt":
        raise ValueError("build_internal_task002_comparison only supports task002 runs")
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    comparison_serial = f"{len(sorted(analysis_dir.glob('compare_*'))) + 1:04d}"
    compare_dir = analysis_dir / f"compare_{comparison_serial}"
    compare_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    left_strategy = "baseline.default_ext_grid"
    right_strategy = "candidate.weak_shunt"
    left_metrics = metrics_payload["baseline_solution"]["metrics"]
    right_metrics = metrics_payload["candidate_solution"]["metrics"]
    directions = {
        "loss": "lower_is_better",
        "voltage_deviation": "lower_is_better",
        "constraint_violation": "constraint_only",
    }
    metric_comparisons = {
        metric: compare_metric_pair(left_metrics[metric], right_metrics[metric], direction)
        for metric, direction in directions.items()
    }
    left_score = objective_for_task(task_ref, left_metrics)
    right_score = objective_for_task(task_ref, right_metrics)
    winner_label = "left" if left_score < right_score else "right" if right_score < left_score else "tie"
    winner_run_ref = run_id if winner_label in {"left", "right"} else ""

    comparison_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_comparison",
        "object_id": f"comparison.power.{problem_name}.{comparison_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"comparison_mode": "within_run_baseline_vs_candidate"},
        "task_ref": task_ref,
        "left_run_ref": run_id,
        "right_run_ref": run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "metric_comparisons": metric_comparisons,
        "objective_scores": {"left": left_score, "right": right_score},
        "winner_run_ref": winner_run_ref,
        "summary": f"在当前 task002 run 内，baseline 与 weak-shunt candidate 的结构化对照完成，winner={winner_label}。",
        "report_refs": [report["object_id"]],
    }

    cognition = build_comparison_cognition(
        serial=comparison_serial,
        task_ref=task_ref,
        left_run_id=run_id,
        right_run_id=run_id,
        left_strategy=left_strategy,
        right_strategy=right_strategy,
        metric_comparisons=metric_comparisons,
        winner_label=winner_label,
        winner_run_ref=winner_run_ref,
    )
    cognition_path = write_cognition_asset_and_registry(cognition, run_id=run_id, when=now)
    comparison_object["cognition_refs"] = [cognition["object_id"]]
    comparison_report = {
        "created_at": now,
        "run_ref": run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "winner": winner_label,
        "winner_run_ref": winner_run_ref,
        "summary": comparison_object["summary"],
        "claim_ceiling": "该比较仅支持当前 task002 单run内 baseline 与 candidate 的局部判断，不支持普适结论。",
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


def build_internal_task002_semantic(run_id: str) -> Path:
    ensure_valid_schemas()
    run_obj, metrics_payload, _ = load_run_payload(run_id)
    task_ref = run_obj["task_ref"]
    if task_ref != "task.power.ieee69_reactive_opt":
        raise ValueError("build_internal_task002_semantic only supports task002 runs")
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    semantic_serial = f"{len(sorted(analysis_dir.glob('semantic_*'))) + 1:04d}"
    semantic_dir = analysis_dir / f"semantic_{semantic_serial}"
    semantic_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    baseline_control = metrics_payload["baseline_solution"]["control_settings"]
    candidate_control = metrics_payload["candidate_solution"]["control_settings"]
    left_profile = semantic_profile_for_skill(
        skill_id="skill.power.baseline_solver",
        control_settings=baseline_control,
    )
    left_profile.update(
        {
            "problem_alignment": "medium",
            "research_value": "low",
            "control_realism": "medium",
            "reuse_potential": "high",
            "method_family": "ext_grid_vm_search",
            "control_signature": "boundary_voltage_tuning",
            "notes": [f"ext_grid_vm_pu={baseline_control.get('ext_grid_vm_pu')}"],
        }
    )
    right_profile = semantic_profile_for_skill(
        skill_id=produced_skill_id_from_run(run_obj),
        control_settings=candidate_control,
    )

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

    preferred_for_research = run_id if dimensions["research_value"]["winner"] == "right" else ""
    semantic_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_semantic_comparison",
        "object_id": f"semantic_comparison.power.{problem_name}.{semantic_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"comparison_mode": "within_run_baseline_vs_candidate"},
        "task_ref": task_ref,
        "left_run_ref": run_id,
        "right_run_ref": run_id,
        "left_skill_ref": left_profile["skill_id"],
        "right_skill_ref": right_profile["skill_id"],
        "semantic_dimensions": dimensions,
        "preferred_for_research_ref": preferred_for_research,
        "summary": "task002 baseline 与 weak-shunt candidate 的研究语义比较完成，candidate 更贴近无功补偿问题本体。",
        "notes": [*left_profile["notes"], *right_profile["notes"]],
    }
    semantic_report = {
        "created_at": now,
        "run_ref": run_id,
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


def analyze_task002_migration(run_id: str | None = None) -> dict[str, Path]:
    ensure_valid_schemas()
    target_run_id = run_id
    if target_run_id is None:
        latest_run = latest_nonempty_dir(RUNS_TASK002_DIR, "run_*")
        target_run_id = load_yaml(latest_run / "run.yaml")["object_id"]

    compare_dir = build_internal_task002_comparison(target_run_id)
    semantic_dir = build_internal_task002_semantic(target_run_id)
    literature_dir = align_literature(compare_dir, semantic_dir)
    run_cognition = load_yaml(run_dir_from_id(target_run_id) / "cognition.yaml")
    explanation_dir = align_explanations(run_cognition["object_id"], literature_dir)
    upgrade_dir = upgrade_cognition_from_analysis(compare_dir, semantic_dir, literature_dir, explanation_dir)
    return {
        "compare_dir": compare_dir,
        "semantic_dir": semantic_dir,
        "literature_dir": literature_dir,
        "explanation_dir": explanation_dir,
        "upgrade_dir": upgrade_dir,
    }


def verify_task002_analysis() -> None:
    ensure_valid_schemas()
    analysis_dir = ANALYSIS_TASK002_DIR
    latest_compare = latest_nonempty_dir(analysis_dir, "compare_*")
    latest_semantic = latest_nonempty_dir(analysis_dir, "semantic_*")
    latest_literature = latest_nonempty_dir(analysis_dir, "literature_*")
    latest_explanations = latest_nonempty_dir(analysis_dir, "explanations_*")
    latest_upgrade = latest_nonempty_dir(analysis_dir, "upgrade_*")

    comparison = load_yaml(latest_compare / "strategy_comparison.yaml")
    semantic = load_yaml(latest_semantic / "strategy_semantic_comparison.yaml")
    literature_alignment = load_yaml(latest_literature / "literature_alignment.yaml")
    explanation_alignment = load_yaml(latest_explanations / "explanation_alignment.yaml")
    cognition_upgrade = load_yaml(latest_upgrade / "cognition_upgrade.yaml")
    novelty = load_yaml(latest_upgrade / "novelty_assessment.yaml")

    if comparison.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 comparison has wrong task_ref")
    if comparison.get("left_run_ref") != comparison.get("right_run_ref"):
        raise RuntimeError("task002 comparison should currently be within a single run")
    if semantic.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 semantic comparison has wrong task_ref")
    if literature_alignment.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 literature alignment has wrong task_ref")
    if explanation_alignment.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 explanation alignment has wrong task_ref")
    if cognition_upgrade.get("task_ref") != "task.power.ieee69_reactive_opt":
        raise RuntimeError("latest task002 cognition upgrade has wrong task_ref")
    if cognition_upgrade.get("decision") not in {"retain", "upgrade"}:
        raise RuntimeError("task002 cognition upgrade decision is not evidence-backed")
    if not explanation_alignment.get("evidence_excerpt_refs"):
        raise RuntimeError("task002 explanation alignment is missing excerpt evidence")
    if cognition_upgrade.get("evidence_strength") != explanation_alignment.get("evidence_strength"):
        raise RuntimeError("task002 cognition upgrade evidence strength mismatches explanation alignment")
    if novelty.get("continue_investment") not in {"continue", "prioritize", "observe"}:
        raise RuntimeError("task002 novelty assessment continue_investment is invalid")


def build_comparison_cognition(
    *,
    serial: str,
    task_ref: str,
    left_run_id: str,
    right_run_id: str,
    left_strategy: str,
    right_strategy: str,
    metric_comparisons: dict[str, Any],
    winner_label: str,
    winner_run_ref: str,
) -> dict[str, Any]:
    now = utc_now()
    case_label = case_label_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    if winner_label == "left":
        statement = (
            f"在当前单工况 {case_label} 任务中，策略 `{left_strategy}` 在 evaluator 指标上整体优于 `{right_strategy}`。"
        )
    elif winner_label == "right":
        statement = (
            f"在当前单工况 {case_label} 任务中，策略 `{right_strategy}` 在 evaluator 指标上整体优于 `{left_strategy}`。"
        )
    else:
        statement = (
            f"在当前单工况 {case_label} 任务中，策略 `{left_strategy}` 与 `{right_strategy}` 未形成明确的单边优势。"
        )
    return {
        "schema_version": "0.1.0",
        "object_type": "cognition",
        "object_id": f"cognition.power.strategy_comparison_{problem_name}_{serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "metadata": {},
        "cognition_type": "candidate",
        "statement": statement,
        "evidence_refs": [left_run_id, right_run_id],
        "scope_boundary": {
            "task": task_ref,
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
    left_run, left_metrics_payload, left_report = load_run_payload(left_run_id)
    right_run, right_metrics_payload, right_report = load_run_payload(right_run_id)
    if left_run["task_ref"] != right_run["task_ref"]:
        raise ValueError("compare_runs requires both runs to share the same task_ref")
    if left_run["task_ref"] == "task.power.ieee69_hosting_capacity":
        return compare_task004_runs(left_run_id, right_run_id)
    if left_run["task_ref"] == "task.power.ieee69_restoration_resilience":
        return compare_task005_runs(left_run_id, right_run_id)
    task_ref = left_run["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    comparison_serial = f"{len(sorted(analysis_dir.glob('compare_*'))) + 1:04d}"
    compare_dir = analysis_dir / f"compare_{comparison_serial}"
    compare_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    left_strategy = strategy_name_from_run(left_run)
    right_strategy = strategy_name_from_run(right_run)
    left_metrics = left_metrics_payload["candidate_solution"]["metrics"]
    right_metrics = right_metrics_payload["candidate_solution"]["metrics"]
    directions = {
        "loss": "lower_is_better",
        "voltage_deviation": "lower_is_better",
        "constraint_violation": "constraint_only",
    }
    if "reactive_support_effort" in left_metrics and "reactive_support_effort" in right_metrics:
        directions["reactive_support_effort"] = "lower_is_better"
    metric_comparisons = {
        metric: compare_metric_pair(left_metrics[metric], right_metrics[metric], direction)
        for metric, direction in directions.items()
    }
    left_score = objective_for_task(task_ref, left_metrics)
    right_score = objective_for_task(task_ref, right_metrics)
    winner_label = "left" if left_score < right_score else "right" if right_score < left_score else "tie"
    winner_run_ref = left_run_id if winner_label == "left" else right_run_id if winner_label == "right" else ""

    comparison_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_comparison",
        "object_id": f"comparison.power.{problem_name}.{comparison_serial}",
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
        task_ref=task_ref,
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


def compare_task004_runs(left_run_id: str, right_run_id: str) -> Path:
    left_run, left_metrics_payload, left_report = load_run_payload(left_run_id)
    right_run, right_metrics_payload, right_report = load_run_payload(right_run_id)
    task_ref = left_run["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    comparison_serial = f"{len(sorted(analysis_dir.glob('compare_*'))) + 1:04d}"
    compare_dir = analysis_dir / f"compare_{comparison_serial}"
    compare_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    left_strategy = strategy_name_from_run(left_run)
    right_strategy = strategy_name_from_run(right_run)
    left_metrics = left_metrics_payload["candidate_solution"]["metrics"]
    right_metrics = right_metrics_payload["candidate_solution"]["metrics"]
    directions = {
        "hosting_capacity_level": "higher_is_better",
        "loss_at_boundary": "lower_is_better",
        "voltage_margin": "higher_is_better",
    }
    metric_comparisons = {
        metric: compare_metric_pair(left_metrics[metric], right_metrics[metric], direction)
        for metric, direction in directions.items()
    }
    left_score = objective_for_task(task_ref, left_metrics)
    right_score = objective_for_task(task_ref, right_metrics)
    winner_label = "left" if left_score < right_score else "right" if right_score < left_score else "tie"
    winner_run_ref = left_run_id if winner_label == "left" else right_run_id if winner_label == "right" else ""
    comparison_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_comparison",
        "object_id": f"comparison.power.{problem_name}.{comparison_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task004_boundary_comparison"},
        "task_ref": task_ref,
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "metric_comparisons": metric_comparisons,
        "objective_scores": {"left": left_score, "right": right_score},
        "winner_run_ref": winner_run_ref,
        "summary": f"task004 承载力比较完成，{left_strategy} 与 {right_strategy} 的边界差异已结构化。",
        "report_refs": [left_report["object_id"], right_report["object_id"]],
    }
    cognition = build_comparison_cognition(
        serial=comparison_serial,
        task_ref=task_ref,
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
    write_yaml(compare_dir / "strategy_comparison.yaml", comparison_object)
    write_yaml(compare_dir / "cognition.yaml", cognition)
    with (compare_dir / "comparison_report.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "created_at": now,
                "left_run_ref": left_run_id,
                "right_run_ref": right_run_id,
                "summary": comparison_object["summary"],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
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


def compare_task005_runs(left_run_id: str, right_run_id: str) -> Path:
    left_run, left_metrics_payload, left_report = load_run_payload(left_run_id)
    right_run, right_metrics_payload, right_report = load_run_payload(right_run_id)
    task_ref = left_run["task_ref"]
    analysis_dir = analysis_dir_from_task_ref(task_ref)
    problem_name = problem_name_from_task_ref(task_ref)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    comparison_serial = f"{len(sorted(analysis_dir.glob('compare_*'))) + 1:04d}"
    compare_dir = analysis_dir / f"compare_{comparison_serial}"
    compare_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    left_strategy = strategy_name_from_run(left_run)
    right_strategy = strategy_name_from_run(right_run)
    left_metrics = left_metrics_payload["candidate_solution"]["metrics"]
    right_metrics = right_metrics_payload["candidate_solution"]["metrics"]
    directions = {
        "restored_load_ratio": "higher_is_better",
        "unserved_critical_load": "lower_is_better",
        "constraint_violation": "constraint_only",
        "restoration_action_cost_proxy": "lower_is_better",
    }
    metric_comparisons = {
        metric: compare_metric_pair(left_metrics[metric], right_metrics[metric], direction)
        for metric, direction in directions.items()
    }
    left_score = objective_for_task(task_ref, left_metrics)
    right_score = objective_for_task(task_ref, right_metrics)
    winner_label = "left" if left_score < right_score else "right" if right_score < left_score else "tie"
    winner_run_ref = left_run_id if winner_label == "left" else right_run_id if winner_label == "right" else ""
    comparison_object = {
        "schema_version": "0.1.0",
        "object_type": "strategy_comparison",
        "object_id": f"comparison.power.{problem_name}.{comparison_serial}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {"mode": "task005_restoration_comparison"},
        "task_ref": task_ref,
        "left_run_ref": left_run_id,
        "right_run_ref": right_run_id,
        "left_strategy": left_strategy,
        "right_strategy": right_strategy,
        "metric_comparisons": metric_comparisons,
        "objective_scores": {"left": left_score, "right": right_score},
        "winner_run_ref": winner_run_ref,
        "summary": f"task005 恢复比较完成，{left_strategy} 与 {right_strategy} 的恢复差异已结构化。",
        "report_refs": [left_report["object_id"], right_report["object_id"]],
    }
    cognition = build_comparison_cognition(
        serial=comparison_serial,
        task_ref=task_ref,
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
    write_yaml(compare_dir / "strategy_comparison.yaml", comparison_object)
    write_yaml(compare_dir / "cognition.yaml", cognition)
    with (compare_dir / "comparison_report.json").open("w", encoding="utf-8") as f:
        json.dump({"created_at": now, "summary": comparison_object["summary"]}, f, indent=2, ensure_ascii=False)
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


def run_real_task002(strategy: str) -> Path:
    ensure_valid_schemas()
    evaluator_module = load_module("task002_evaluator", TASK002_EVALUATOR_MODULE_PATH)

    task, baseline, evaluator, constraints = load_task002_real_inputs()
    baseline_solver = load_solver_from_artifact(
        "task002_baseline_solver",
        baseline.get("artifact_ref", {}),
        BASELINE_SOLVER_PATH,
    )
    if strategy == "weak-shunt":
        candidate_skill_id, solver_path = solver_for_strategy(strategy, "success")
        mode_tag = f"real_{strategy}_success"
    elif strategy == "adversarial-failure":
        candidate_skill_id = "skill.power.weak_bus_shunt_adversarial_task002"
        solver_path = TASK002_FAILURE_SOLVER_PATH
        mode_tag = "real_adversarial-failure"
    else:
        raise ValueError(f"unsupported task002 strategy: {strategy}")
    candidate_solver = load_module("task002_candidate_solver", solver_path)
    serial = next_run_serial_for_dir(RUNS_TASK002_DIR)
    run_dir = RUNS_TASK002_DIR / f"run_{serial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    now = utc_now()

    constraint_set = constraints["solver"]
    network_model = str(constraint_set.get("network_model", "ieee69"))
    baseline_solution_raw = baseline_solver.solve(network_model, constraint_set)
    candidate_solution_raw = candidate_solver.solve(network_model, constraint_set)
    baseline_solution = {
        "control_settings": baseline_solution_raw["control_settings"],
        "metrics": baseline_solution_raw["baseline_solution"],
    }
    candidate_solution = {
        "control_settings": candidate_solution_raw["control_settings"],
        "metrics": candidate_solution_raw["reactive_power_settings"],
    }
    evaluation = evaluator_module.evaluate_real_solution(baseline_solution, candidate_solution)

    run_id = f"run.power.ieee69_reactive_opt.{serial}"
    grade = grade_from_result(evaluation["passed"])
    report_type = report_type_from_grade(grade)
    taste_id = f"taste.power.ieee69_reactive_opt.{serial}"
    evidence_id = f"evidence.power.ieee69_reactive_opt.{serial}"
    trace_id = f"agent_trace.power.ieee69_reactive_opt.{serial}"
    prompt_obs_id = f"prompt_observation.power.ieee69_reactive_opt.{serial}"
    report_id = f"report.power.ieee69_reactive_opt.{'note' if evaluation['passed'] else 'memo'}_{serial}"
    cognition = build_task002_cognition(evaluation["passed"], serial, run_id, mode_tag)

    run_object = {
        "schema_version": "0.1.0",
        "object_type": "run",
        "object_id": run_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "archived",
        "metadata": {},
        "title": f"task002 real {strategy} run {serial}",
        "task_ref": task["object_id"],
        "evaluator_ref": evaluator["object_id"],
        "run_status": "completed" if evaluation["passed"] else "failed_experiment",
        "started_at": now,
        "ended_at": now,
        "attempt_index": int(serial),
        "trigger_reason": mode_tag,
        "input_snapshot": {
            "task": {"object_id": task["object_id"], "object_version": task["object_version"]},
            "evaluator": {"object_id": evaluator["object_id"], "object_version": evaluator["object_version"]},
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
        "agent_trace_refs": [{"kind": "trace", "object_id": trace_id}],
    }
    if not evaluation["passed"]:
        run_object["failure_summary"] = "candidate did not satisfy evaluator pass criteria"

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
        "claim_scope": {"supported_claims": ["当前 IEEE69 迁移任务设定下的阶段性结论"]},
        "skill_refs": [candidate_skill_id],
        "cognition_refs": [cognition["object_id"]],
        "gaps": ["未覆盖多工况比较", "未覆盖 comparison/semantic/literature 分析"],
        "taste_assessment_ref": taste_id,
        "report_refs": [report_id],
    }
    if strategy == "adversarial-failure":
        evidence["claim_scope"] = {"supported_claims": ["当前 IEEE69 failure probe 下的失败边界结论"]}
        evidence["gaps"].append("failure probe 仅验证负向边界，不代表真实候选设计空间")
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
            "task002 真实迁移运行相对基线获得阶段性改进，但证据范围仍受限于单任务单工况。"
            if evaluation["passed"]
            else (
                "task002 failure probe 稳定劣于基线，说明错误极性的弱节点 shunt 设置可作为明确失败边界。"
                if strategy == "adversarial-failure"
                else "task002 真实迁移运行未达到评估要求，只适合作为失败讨论材料。"
            )
        ),
        "claim_ceiling": (
            "可报告为当前 IEEE69 迁移任务设定下的阶段性有效方法，不可上升为普适规律。"
            if evaluation["passed"]
            else (
                "只能报告当前 IEEE69 failure probe 暴露出的负向边界，不得包装成有效方法。"
                if strategy == "adversarial-failure"
                else "只能报告当前 IEEE69 迁移失败，不得包装成有效成果。"
            )
        ),
        "recommended_report_type": report_type,
        "evidence_refs": [evidence_id],
        "review_status": "reviewed",
    }
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
            "task002 迁移运行中，基线比较与分级约束继续抑制了过度表述。"
            if evaluation["passed"]
            else (
                "task002 failure probe 失败运行中，系统将结果压到负向边界材料而非正向成果。"
                if strategy == "adversarial-failure"
                else "task002 迁移失败运行中，系统仍将结果压到失败讨论材料。"
            )
        ),
        "severity": "medium",
        "suggested_action": "保持 task001 的基线比较与成果分级为迁移任务默认约束。",
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
        "trace_summary": "系统完成了 task002 真实任务加载、求解、评估、分级、证据组织和报告写回。",
        "event_count": 7,
        "prompt_observation_refs": [prompt_obs_id],
        "notable_behaviors": [
            "先比较基线再评估 candidate",
            "迁移运行后再做 taste assessment",
            "报告继续受 taste_assessment 约束",
        ],
    }
    if strategy == "adversarial-failure":
        agent_trace["notable_behaviors"].append("failure probe 显式验证负向认知路径")
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
        "title": f"task002 real {strategy} report {serial}",
        "summary": (
            "task002 真实迁移运行相对基线获得阶段性改进。"
            if evaluation["passed"]
            else (
                "task002 failure probe 稳定暴露负向边界，应作为失败认知材料归档。"
                if strategy == "adversarial-failure"
                else "task002 真实迁移运行未达到评估要求，应作为失败材料归档。"
            )
        ),
        "evidence_bundle_refs": [evidence_id],
        "taste_assessment_ref": taste_id,
        "audience": "internal_team",
        "boundary_statement": "本报告仅对应当前 IEEE69 单工况迁移任务，不构成普适结论。",
        "failure_summary": None if evaluation["passed"] else run_object["failure_summary"],
        "next_steps": (
            ["将失败边界写入 task002 迁移经验", "比较真实候选与 failure probe 的边界差异"]
            if strategy == "adversarial-failure"
            else ["补齐 task002 comparison/semantic 路径", "增加多工况复现"]
        ),
        "claim_summary": [taste["claim_ceiling"]],
    }

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
    task002_real = sub.add_parser("real-run-task002", help="Run a real pandapower-backed task002 cycle")
    task002_real.add_argument("--strategy", choices=["weak-shunt", "adversarial-failure"], default="weak-shunt")
    task003_real = sub.add_parser("real-run-task003", help="Run a real task003 renewable reactive cycle")
    task003_real.add_argument(
        "--strategy",
        choices=["inverter-support", "inverter-underperformer", "weak-shunt-mismatch"],
        default="inverter-support",
    )
    task004_real = sub.add_parser("real-run-task004", help="Run a real task004 hosting-capacity cycle")
    task004_real.add_argument("--strategy", choices=["inverter-support", "voltage-sensitivity", "single-point-mismatch"], default="inverter-support")
    task004_real.add_argument("--candidate-q-step-mvar", type=float, required=False)
    task005_real = sub.add_parser("real-run-task005", help="Run a real task005 restoration cycle")
    task005_real.add_argument(
        "--strategy",
        choices=["renewable-restoration", "steady-state-mismatch", "renewable-underperformer"],
        default="renewable-restoration",
    )
    task002_analysis = sub.add_parser("analyze-task002-migration", help="Build the minimal task002 analysis chain")
    task002_analysis.add_argument("--run-id", required=False)
    task003_mismatch = sub.add_parser("check-task003-mismatch", help="Check task003 task-mismatch readiness")
    task003_mismatch.add_argument("--source-dir", required=False)
    task004_mismatch = sub.add_parser("check-task004-mismatch", help="Check task004 task-mismatch readiness")
    task004_mismatch.add_argument("--source-dir", required=False)
    task005_mismatch = sub.add_parser("check-task005-mismatch", help="Check task005 task-mismatch readiness")
    task005_mismatch.add_argument("--source-dir", required=False)
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
    build_lit.add_argument("--task-package", required=False, choices=["task001", "task003", "task004"])
    explain = sub.add_parser("align-explanations", help="Align a local cognition with literature explanation cards")
    explain.add_argument("--cognition-ref", required=True)
    explain.add_argument("--literature-dir", required=True)
    upgrade = sub.add_parser("upgrade-cognition", help="Upgrade cognition from comparison artifacts")
    upgrade.add_argument("--comparison-dir", required=True)
    upgrade.add_argument("--semantic-dir", required=True)
    upgrade.add_argument("--literature-dir", required=False)
    upgrade.add_argument("--explanation-dir", required=False)
    task003_upgrade = sub.add_parser("upgrade-task003-cognition", help="Upgrade task003 cognition from comparison artifacts")
    task003_upgrade.add_argument("--comparison-dir", required=True)
    task003_upgrade.add_argument("--semantic-dir", required=True)
    task003_upgrade.add_argument("--literature-dir", required=False)
    task003_upgrade.add_argument("--explanation-dir", required=False)
    task004_upgrade = sub.add_parser("upgrade-task004-cognition", help="Upgrade task004 cognition from comparison artifacts")
    task004_upgrade.add_argument("--comparison-dir", required=True)
    task004_upgrade.add_argument("--semantic-dir", required=True)
    task004_upgrade.add_argument("--literature-dir", required=False)
    task004_upgrade.add_argument("--explanation-dir", required=False)
    task005_upgrade = sub.add_parser("upgrade-task005-cognition", help="Upgrade task005 cognition from comparison artifacts")
    task005_upgrade.add_argument("--comparison-dir", required=True)
    task005_upgrade.add_argument("--semantic-dir", required=True)
    sub.add_parser("verify-task001-pipeline", help="Verify the task001 vertical research loop")
    sub.add_parser("verify-task002-pipeline", help="Verify the task002 vertical research loop")
    sub.add_parser("verify-task002-analysis", help="Verify the task002 Phase 5 analysis slice")
    sub.add_parser("verify-task002-failure-path", help="Verify the task002 negative-cognition failure lane")
    sub.add_parser("verify-task003-pipeline", help="Verify the task003 renewable vertical research loop")
    sub.add_parser("verify-task003-failure-path", help="Verify the task003 mismatch failure lanes")
    sub.add_parser("verify-task003-cognition-stage", help="Verify the task003 stage2 cognition artifacts")
    sub.add_parser("verify-task003-literature-stage", help="Verify the task003 stage3 literature artifacts")
    sub.add_parser("verify-task004-pipeline", help="Verify the task004 hosting-capacity vertical loop")
    sub.add_parser("verify-task004-boundary-overclaim", help="Verify the task004 boundary overclaim checker")
    sub.add_parser("verify-task004-failure-path", help="Verify the task004 skill-mismatch failure lane")
    sub.add_parser("verify-task004-cognition-stage", help="Verify the task004 cognition-stage artifacts")
    sub.add_parser("verify-task004-task-mismatch", help="Verify the task004 task-mismatch freeze artifacts")
    sub.add_parser("verify-task004-literature-stage", help="Verify the task004 literature-stage artifacts")
    sub.add_parser("verify-task005-pipeline", help="Verify the task005 restoration vertical loop")
    sub.add_parser("verify-task005-failure-path", help="Verify the task005 failure lanes")
    sub.add_parser("verify-task005-cognition-stage", help="Verify the task005 cognition-stage artifacts")
    sub.add_parser("build-skill-cognition-loop", help="Build the skill-cognition loop artifacts")
    sub.add_parser("verify-skill-cognition-loop", help="Verify the skill-cognition loop artifacts")
    real_agentic = sub.add_parser("run-real-agentic-loop", help="Run the real task003 agentic multi-iteration loop")
    real_agentic.add_argument("--iterations", type=int, default=2)
    sub.add_parser("verify-real-agentic-loop", help="Verify the real task003 agentic loop artifacts")

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

    if args.command == "real-run-task002":
        run_dir = run_real_task002(args.strategy)
        print(f"Task002 real run written to {run_dir}")
        return 0

    if args.command == "real-run-task003":
        run_dir = run_real_task003(args.strategy)
        print(f"Task003 real run written to {run_dir}")
        return 0

    if args.command == "real-run-task004":
        run_dir = run_real_task004(args.strategy, candidate_q_step_mvar=args.candidate_q_step_mvar)
        print(f"Task004 real run written to {run_dir}")
        return 0

    if args.command == "real-run-task005":
        run_dir = run_real_task005(args.strategy)
        print(f"Task005 real run written to {run_dir}")
        return 0

    if args.command == "build-skill-cognition-loop":
        run_python_script(SKILL_COGNITION_LOOP_BUILDER)
        return 0

    if args.command == "verify-skill-cognition-loop":
        run_python_script(SKILL_COGNITION_LOOP_VERIFIER)
        return 0

    if args.command == "run-real-agentic-loop":
        run_python_script(REAL_AGENTIC_LOOP_RUNNER, "--iterations", str(args.iterations))
        return 0

    if args.command == "verify-real-agentic-loop":
        run_python_script(REAL_AGENTIC_LOOP_VERIFIER)
        return 0

    if args.command == "analyze-task002-migration":
        outputs = analyze_task002_migration(args.run_id)
        print("Task002 analysis written:")
        for key, value in outputs.items():
            print(f"- {key}: {value}")
        return 0

    if args.command == "check-task003-mismatch":
        output_dir = check_task003_mismatch(Path(args.source_dir) if args.source_dir else None)
        print(f"Task003 mismatch check written to {output_dir}")
        return 0

    if args.command == "check-task004-mismatch":
        output_dir = check_task004_mismatch(Path(args.source_dir) if args.source_dir else None)
        print(f"Task004 mismatch check written to {output_dir}")
        return 0

    if args.command == "check-task005-mismatch":
        output_dir = check_task005_mismatch(Path(args.source_dir) if args.source_dir else None)
        print(f"Task005 mismatch check written to {output_dir}")
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
        literature_root = build_literature_cards(args.max_source_kind, args.task_package)
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

    if args.command == "upgrade-task003-cognition":
        upgrade_dir = upgrade_task003_cognition(
            Path(args.comparison_dir),
            Path(args.semantic_dir),
            Path(args.literature_dir) if args.literature_dir else None,
            Path(args.explanation_dir) if args.explanation_dir else None,
        )
        print(f"Task003 cognition upgrade written to {upgrade_dir}")
        return 0

    if args.command == "upgrade-task004-cognition":
        upgrade_dir = upgrade_task004_cognition(
            Path(args.comparison_dir),
            Path(args.semantic_dir),
            Path(args.literature_dir) if args.literature_dir else None,
            Path(args.explanation_dir) if args.explanation_dir else None,
        )
        print(f"Task004 cognition upgrade written to {upgrade_dir}")
        return 0

    if args.command == "upgrade-task005-cognition":
        upgrade_dir = upgrade_task005_cognition(Path(args.comparison_dir), Path(args.semantic_dir))
        print(f"Task005 cognition upgrade written to {upgrade_dir}")
        return 0

    if args.command == "verify-task001-pipeline":
        verify_task001_pipeline()
        print("Task001 pipeline verification passed.")
        return 0

    if args.command == "verify-task002-pipeline":
        verify_task002_pipeline()
        print("Task002 pipeline verification passed.")
        return 0

    if args.command == "verify-task002-analysis":
        verify_task002_analysis()
        print("Task002 analysis verification passed.")
        return 0

    if args.command == "verify-task002-failure-path":
        verify_task002_failure_path()
        print("Task002 failure-path verification passed.")
        return 0

    if args.command == "verify-task003-pipeline":
        verify_task003_pipeline()
        print("Task003 pipeline verification passed.")
        return 0

    if args.command == "verify-task003-failure-path":
        verify_task003_failure_path()
        print("Task003 failure-path verification passed.")
        return 0

    if args.command == "verify-task003-cognition-stage":
        verify_task003_cognition_stage()
        print("Task003 cognition-stage verification passed.")
        return 0

    if args.command == "verify-task003-literature-stage":
        verify_task003_literature_stage()
        print("Task003 literature-stage verification passed.")
        return 0

    if args.command == "verify-task004-pipeline":
        verify_task004_pipeline()
        print("Task004 pipeline verification passed.")
        return 0

    if args.command == "verify-task004-boundary-overclaim":
        verify_task004_boundary_overclaim()
        print("Task004 boundary-overclaim verification passed.")
        return 0

    if args.command == "verify-task004-failure-path":
        verify_task004_failure_path()
        print("Task004 failure-path verification passed.")
        return 0

    if args.command == "verify-task004-cognition-stage":
        verify_task004_cognition_stage()
        print("Task004 cognition-stage verification passed.")
        return 0

    if args.command == "verify-task004-task-mismatch":
        verify_task004_task_mismatch()
        print("Task004 task-mismatch verification passed.")
        return 0

    if args.command == "verify-task004-literature-stage":
        verify_task004_literature_stage()
        print("Task004 literature-stage verification passed.")
        return 0

    if args.command == "verify-task005-pipeline":
        verify_task005_pipeline()
        print("Task005 pipeline verification passed.")
        return 0

    if args.command == "verify-task005-failure-path":
        verify_task005_failure_path()
        print("Task005 failure-path verification passed.")
        return 0

    if args.command == "verify-task005-cognition-stage":
        verify_task005_cognition_stage()
        print("Task005 cognition-stage verification passed.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
