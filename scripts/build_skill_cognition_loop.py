#!/usr/bin/env python3
"""Build the minimal skill-cognition loop artifacts from existing task analyses."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_ROOT = REPO_ROOT / "analysis"
LOOP_ROOT = ANALYSIS_ROOT / "loop"

TASK_CONFIGS = {
    "task003": {
        "task_ref": "task.power.ieee69_renewable_reactive_opt",
        "problem_name": "ieee69_renewable_reactive_opt",
        "event": {
            "object_id": "cognition_event.power.ieee69_renewable_reactive_opt.0001",
            "event_type": "metric_semantic_divergence",
            "status": "active",
            "severity": "medium",
            "sources": [
                "analysis/task003/semantic_0002/strategy_semantic_comparison.yaml",
                "analysis/task003/upgrade_0006/cognition_upgrade.yaml",
            ],
        },
        "update": {
            "object_id": "cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0001",
            "blocked_skill_families": ["pure_weak_shunt_substitution"],
            "target_skill_family": "renewable_inverter_reactive_support",
            "candidate_skill_refs": [
                "skill.power.renewable_inverter_reactive_optimizer_task003",
                "skill.power.renewable_inverter_underperformer_task003",
            ],
        },
        "plan": {
            "object_id": "skill_iteration_plan.power.ieee69_renewable_reactive_opt.0001",
        },
        "review": {
            "object_id": "loop_review.power.ieee69_renewable_reactive_opt.0001",
            "verdict": "substantiated",
        },
    },
    "task004": {
        "task_ref": "task.power.ieee69_hosting_capacity",
        "problem_name": "ieee69_hosting_capacity",
        "event": {
            "object_id": "cognition_event.power.ieee69_hosting_capacity.0001",
            "event_type": "claim_overreach_detected",
            "status": "active",
            "severity": "high",
            "sources": [
                "analysis/task004/boundary_overclaim_20260421_033407/boundary_overclaim_check.yaml",
                "analysis/task004/upgrade_0002/cognition_upgrade.yaml",
            ],
        },
        "update": {
            "object_id": "cognition_to_skill_update.power.ieee69_hosting_capacity.0001",
            "blocked_skill_families": ["single_point_operation_proxy"],
            "target_skill_family": "hosting_capacity_boundary_scan",
            "candidate_skill_refs": [
                "skill.power.renewable_capacity_optimizer_task004",
                "skill.power.single_point_capacity_mismatch_task004",
            ],
        },
        "plan": {
            "object_id": "skill_iteration_plan.power.ieee69_hosting_capacity.0001",
        },
        "review": {
            "object_id": "loop_review.power.ieee69_hosting_capacity.0001",
            "verdict": "substantiated",
        },
    },
    "task005": {
        "task_ref": "task.power.ieee69_restoration_resilience",
        "problem_name": "ieee69_restoration_resilience",
        "event": {
            "object_id": "cognition_event.power.ieee69_restoration_resilience.0001",
            "event_type": "skill_mismatch_detected",
            "status": "active",
            "severity": "high",
            "sources": [
                "analysis/task005/mismatch_20260422_001023/task_mismatch_check.yaml",
                "analysis/task005/upgrade_0002/cognition_upgrade.yaml",
            ],
        },
        "update": {
            "object_id": "cognition_to_skill_update.power.ieee69_restoration_resilience.0001",
            "blocked_skill_families": ["steady_state_operation_substitution"],
            "target_skill_family": "event_driven_restoration_with_renewable_support",
            "candidate_skill_refs": [
                "skill.power.renewable_restoration_candidate_task005",
                "skill.power.renewable_underperformer_task005",
                "skill.power.steady_state_restoration_mismatch_task005",
            ],
        },
        "plan": {
            "object_id": "skill_iteration_plan.power.ieee69_restoration_resilience.0001",
        },
        "review": {
            "object_id": "loop_review.power.ieee69_restoration_resilience.0001",
            "verdict": "substantiated",
        },
    },
}


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


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def build_task003_payloads(config: dict[str, Any], created_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    semantic = load_yaml(REPO_ROOT / config["event"]["sources"][0])
    upgrade = load_yaml(REPO_ROOT / config["event"]["sources"][1])

    event = {
        "schema_version": "0.1.0",
        "object_type": "cognition_event",
        "object_id": config["event"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": config["event"]["status"],
        "metadata": {"task_package": "task003", "generation_mode": "rule_bootstrap"},
        "task_ref": config["task_ref"],
        "event_type": config["event"]["event_type"],
        "severity": config["event"]["severity"],
        "trigger_summary": semantic["summary"],
        "source_refs": [semantic["object_id"], upgrade["object_id"]],
        "evidence_strength": upgrade.get("evidence_strength", "medium"),
        "recommended_cognition_action": "保留新能源 inverter 控制空间，要求下一轮围绕协同扩展而非回退替代路径。",
    }
    update = {
        "schema_version": "0.1.0",
        "object_type": "cognition_to_skill_update",
        "object_id": config["update"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task003", "controller_mode": "minimum_viable_loop"},
        "task_ref": config["task_ref"],
        "source_cognition_ref": upgrade["upgraded_cognition_ref"],
        "source_event_ref": event["object_id"],
        "next_iteration_skill_constraints": [
            "不得因单次性能失败而放弃 inverter_q_support 方法家族。",
            "下一轮候选必须保持新能源感知控制空间，不允许退回 weak-shunt 替代主线。",
        ],
        "next_iteration_evaluator_constraints": [
            "必须显式区分 admissibility 与 efficacy。",
            "性能失败与任务失配必须分离记录。",
        ],
        "next_iteration_task_refinements": [
            "仍限定单代表工况，避免在当前阶段过早扩展到时序波动。",
        ],
        "search_priority_updates": [
            "优先探索 shunt + inverter 协同 candidate。",
            "保留 inverter-only 作为受控对照路径。",
        ],
        "blocked_skill_families": config["update"]["blocked_skill_families"],
        "required_discriminating_tests": [
            "补协同 candidate 与 inverter-only candidate 的对照。",
            "验证 evaluator 是否给出 admissibility 与 efficacy 的分离结果。",
        ],
        "summary": "task003 的认知层要求下一轮技能在新能源感知方法族内部进化，而不是回到语义更弱的替代路径。",
    }
    plan = {
        "schema_version": "0.1.0",
        "object_type": "skill_iteration_plan",
        "object_id": config["plan"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "ready",
        "metadata": {"task_package": "task003", "loop_source": "cognition_to_skill_update"},
        "task_ref": config["task_ref"],
        "controller_update_ref": update["object_id"],
        "target_skill_family": config["update"]["target_skill_family"],
        "planned_actions": [
            "新增 shunt + inverter 协同 candidate。",
            "保留 inverter-only candidate 作为对照。",
            "记录性能失败但语义正确的候选，不与 mismatch 合并。",
        ],
        "planned_validation": [
            "比较协同 candidate 与 inverter-only candidate 在 admissibility / efficacy 双轴上的差异。",
            "检查 failure taxonomy 是否仍稳定地区分 mismatch 与 underperformer。",
        ],
        "blocked_paths": [
            "不以 weak-shunt 路线替代新能源感知主线。",
        ],
        "candidate_skill_refs": config["update"]["candidate_skill_refs"],
        "success_criteria": [
            "下一轮候选仍属于新能源感知控制空间。",
            "evaluator 输出明确区分 admissibility 与 efficacy。",
            "failure taxonomy 不再混淆性能失败与任务失配。",
        ],
        "summary": "task003 的下一轮技能工作应在新能源控制方法族内部做更细粒度扩展和判别。",
    }
    review = {
        "schema_version": "0.1.0",
        "object_type": "loop_review",
        "object_id": config["review"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task003", "review_mode": "bootstrap_reflection"},
        "task_ref": config["task_ref"],
        "event_ref": event["object_id"],
        "controller_update_ref": update["object_id"],
        "iteration_plan_ref": plan["object_id"],
        "search_space_reduction": "从泛化候选盲试收缩为新能源 inverter 控制方法族内部的协同扩展。",
        "failure_explanation_improvement": "语义正确但性能失败不再与 task mismatch 混同。",
        "evaluator_refinement": "下一轮明确要求 evaluator 给出 admissibility 与 efficacy 分离。",
        "claim_tightening": "继续限制在单代表工况，不外推到新能源时序波动情形。",
        "verdict": config["review"]["verdict"],
        "summary": "task003 已证明认知层可以重写下一轮技能搜索边界，而不是只做事后评论。",
    }
    return event, update, plan, review


def build_task004_payloads(config: dict[str, Any], created_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    overclaim = load_yaml(REPO_ROOT / config["event"]["sources"][0])
    upgrade = load_yaml(REPO_ROOT / config["event"]["sources"][1])

    event = {
        "schema_version": "0.1.0",
        "object_type": "cognition_event",
        "object_id": config["event"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": config["event"]["status"],
        "metadata": {"task_package": "task004", "generation_mode": "rule_bootstrap"},
        "task_ref": config["task_ref"],
        "event_type": config["event"]["event_type"],
        "severity": config["event"]["severity"],
        "trigger_summary": overclaim["rationale"],
        "source_refs": [overclaim["object_id"], upgrade["object_id"]],
        "evidence_strength": upgrade.get("evidence_strength", "medium"),
        "recommended_cognition_action": "保持承载力边界类表述受控，并要求下一轮补更完整的边界扫描与多场景对照。",
    }
    update = {
        "schema_version": "0.1.0",
        "object_type": "cognition_to_skill_update",
        "object_id": config["update"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task004", "controller_mode": "minimum_viable_loop"},
        "task_ref": config["task_ref"],
        "source_cognition_ref": upgrade["upgraded_cognition_ref"],
        "source_event_ref": event["object_id"],
        "next_iteration_skill_constraints": [
            "承载力探索必须围绕边界扫描，禁止用单点运行结果替代条件化边界。",
        ],
        "next_iteration_evaluator_constraints": [
            "保留 boundary overclaim gate，避免报告超出扫描包络。",
            "对比对象必须覆盖多场景或扩展扫描包络。",
        ],
        "next_iteration_task_refinements": [
            "明确 claim 仅在当前扫描包络和控制策略下成立。",
            "下一轮应补多场景 hosting capacity 对照。",
        ],
        "search_priority_updates": [
            "优先扩大 scan envelope。",
            "引入多场景 boundary scan，而不是继续强化单点操作路径。",
        ],
        "blocked_skill_families": config["update"]["blocked_skill_families"],
        "required_discriminating_tests": [
            "补充多场景 hosting capacity 对照。",
            "检查边界表达是否仍通过 overclaim gate。",
        ],
        "summary": "task004 的认知层要求下一轮承载力技能工作围绕边界扫描的真实性和边界表达的克制展开。",
    }
    plan = {
        "schema_version": "0.1.0",
        "object_type": "skill_iteration_plan",
        "object_id": config["plan"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "ready",
        "metadata": {"task_package": "task004", "loop_source": "cognition_to_skill_update"},
        "task_ref": config["task_ref"],
        "controller_update_ref": update["object_id"],
        "target_skill_family": config["update"]["target_skill_family"],
        "planned_actions": [
            "扩大承载力扫描包络。",
            "新增多场景 hosting capacity 对照。",
            "保留 smart inverter 支撑路径，但禁止用单点结果直接代表边界。",
        ],
        "planned_validation": [
            "检查新增场景是否改变边界判断。",
            "运行 boundary overclaim gate 验证报告是否仍受控。",
        ],
        "blocked_paths": [
            "不再以 single-point operation 代理 hosting capacity 主线。",
        ],
        "candidate_skill_refs": config["update"]["candidate_skill_refs"],
        "success_criteria": [
            "下一轮输出明确是条件化边界而非系统固有承载力。",
            "多场景对照被纳入 evaluator/analysis 主轴。",
            "boundary overclaim 风险被提前拦截。",
        ],
        "summary": "task004 的下一轮技能应围绕边界扫描与场景覆盖做真实扩展。",
    }
    review = {
        "schema_version": "0.1.0",
        "object_type": "loop_review",
        "object_id": config["review"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task004", "review_mode": "bootstrap_reflection"},
        "task_ref": config["task_ref"],
        "event_ref": event["object_id"],
        "controller_update_ref": update["object_id"],
        "iteration_plan_ref": plan["object_id"],
        "search_space_reduction": "从单点运行类盲试收缩为边界扫描与多场景验证主线。",
        "failure_explanation_improvement": "过度表述被识别为 claim 问题，而不是误当作技能成功。",
        "evaluator_refinement": "boundary overclaim gate 被提升为下一轮必保留约束。",
        "claim_tightening": "承载力表述被限定在当前扫描包络与控制策略下。",
        "verdict": config["review"]["verdict"],
        "summary": "task004 已证明闭环可把边界认知转成下一轮技能与评估约束。",
    }
    return event, update, plan, review


def build_task005_payloads(config: dict[str, Any], created_at: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    mismatch = load_yaml(REPO_ROOT / config["event"]["sources"][0])
    upgrade = load_yaml(REPO_ROOT / config["event"]["sources"][1])
    overclaim = load_yaml(REPO_ROOT / "analysis/task005/resilience_overclaim_20260422_001023/boundary_overclaim_check.yaml")

    event = {
        "schema_version": "0.1.0",
        "object_type": "cognition_event",
        "object_id": config["event"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": config["event"]["status"],
        "metadata": {"task_package": "task005", "generation_mode": "rule_bootstrap"},
        "task_ref": config["task_ref"],
        "event_type": config["event"]["event_type"],
        "severity": config["event"]["severity"],
        "trigger_summary": mismatch["rationale"],
        "source_refs": [mismatch["object_id"], upgrade["object_id"], overclaim["object_id"]],
        "evidence_strength": upgrade.get("evidence_strength", "low"),
        "recommended_cognition_action": "冻结缺输入的伪执行路径，同时保留事件驱动恢复方向并要求下一轮补 fault-sensitive 判别试验。",
    }
    update = {
        "schema_version": "0.1.0",
        "object_type": "cognition_to_skill_update",
        "object_id": config["update"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task005", "controller_mode": "minimum_viable_loop"},
        "task_ref": config["task_ref"],
        "source_cognition_ref": upgrade["upgraded_cognition_ref"],
        "source_event_ref": event["object_id"],
        "next_iteration_skill_constraints": [
            "稳态操作结果不得替代事件驱动恢复主线。",
            "保留语义正确但性能失败的恢复 candidate，作为可继续演化对象。",
        ],
        "next_iteration_evaluator_constraints": [
            "将 critical_load_relevance 纳入 evaluator 主轴。",
            "恢复性能与 restoration admissibility 必须分离评价。",
        ],
        "next_iteration_task_refinements": [
            "下一轮必须补充 fault 拓扑与恢复范围定义。",
            "明确 claim 仅支持当前 fault 场景、动作集合和单工况。",
        ],
        "search_priority_updates": [
            "优先比较不同 fault 拓扑下的恢复行为。",
            "探索带新能源支撑的事件驱动恢复策略，而不是稳态代理。",
        ],
        "blocked_skill_families": config["update"]["blocked_skill_families"],
        "required_discriminating_tests": [
            "补 fault topology 对照。",
            "验证 critical_load_relevance 是否改变 candidate 排序。",
            "确保任务缺关键输入时进入 freeze 而非伪执行。",
        ],
        "summary": "task005 的认知层要求下一轮恢复技能工作围绕事件驱动语义、fault 敏感性和关键负荷相关性开展。",
    }
    plan = {
        "schema_version": "0.1.0",
        "object_type": "skill_iteration_plan",
        "object_id": config["plan"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "ready",
        "metadata": {"task_package": "task005", "loop_source": "cognition_to_skill_update"},
        "task_ref": config["task_ref"],
        "controller_update_ref": update["object_id"],
        "target_skill_family": config["update"]["target_skill_family"],
        "planned_actions": [
            "围绕事件驱动恢复建立多 fault topology 对照。",
            "保留 renewable-aware restoration candidate 与 underperformer 路线。",
            "禁止 steady-state restoration mismatch 进入主恢复主线。",
        ],
        "planned_validation": [
            "比较不同 fault topology 下的恢复 admissibility 与 performance。",
            "把 critical_load_relevance 纳入 evaluator 并检查排序变化。",
            "验证任务缺关键输入时是否稳定 freeze。",
        ],
        "blocked_paths": [
            "不以 steady-state 操作结果替代恢复策略评估。",
        ],
        "candidate_skill_refs": config["update"]["candidate_skill_refs"],
        "success_criteria": [
            "恢复结果对 fault topology 与关键负荷相关性敏感。",
            "稳态代理路径被排除出主线。",
            "任务定义缺关键输入时不会进入伪执行。",
        ],
        "summary": "task005 的下一轮技能应围绕事件驱动恢复语义和多故障对照做受控扩展。",
    }
    review = {
        "schema_version": "0.1.0",
        "object_type": "loop_review",
        "object_id": config["review"]["object_id"],
        "object_version": "0.1.0",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "reviewed",
        "metadata": {"task_package": "task005", "review_mode": "bootstrap_reflection"},
        "task_ref": config["task_ref"],
        "event_ref": event["object_id"],
        "controller_update_ref": update["object_id"],
        "iteration_plan_ref": plan["object_id"],
        "search_space_reduction": "从把稳态代理混入恢复主线的盲试收缩为事件驱动恢复与 fault topology 对照主线。",
        "failure_explanation_improvement": "任务定义缺失、语义正确但性能失败、claim 受控三类现象被明确拆分。",
        "evaluator_refinement": "下一轮显式要求 critical_load_relevance 与恢复 admissibility 进入 evaluator。",
        "claim_tightening": "恢复 claim 被限定在当前 fault 场景、动作集合和单工况条件下。",
        "verdict": config["review"]["verdict"],
        "summary": "task005 已把 failure taxonomy、task freeze 与恢复认知转成下一轮技能和 evaluator 约束。",
    }
    return event, update, plan, review


BUILDERS = {
    "task003": build_task003_payloads,
    "task004": build_task004_payloads,
    "task005": build_task005_payloads,
}


def build_task(task_name: str) -> dict[str, str]:
    created_at = utc_now()
    config = TASK_CONFIGS[task_name]
    event, update, plan, review = BUILDERS[task_name](config, created_at)

    task_root = LOOP_ROOT / task_name
    event_path = task_root / "events" / f"{event['object_id'].split('.')[-1]}.yaml"
    update_path = task_root / "updates" / f"{update['object_id'].split('.')[-1]}.yaml"
    plan_path = task_root / "plans" / f"{plan['object_id'].split('.')[-1]}.yaml"
    review_path = task_root / "reviews" / f"{review['object_id'].split('.')[-1]}.yaml"

    write_yaml(event_path, event)
    write_yaml(update_path, update)
    write_yaml(plan_path, plan)
    write_yaml(review_path, review)

    writeback = {
        "task": task_name,
        "generated_at": created_at,
        "artifacts": {
            "event": rel(event_path),
            "update": rel(update_path),
            "iteration_plan": rel(plan_path),
            "loop_review": rel(review_path),
        },
    }
    write_json(task_root / "writeback.json", writeback)
    return writeback["artifacts"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build skill-cognition loop artifacts.")
    parser.add_argument("--tasks", nargs="*", choices=sorted(TASK_CONFIGS), default=sorted(TASK_CONFIGS))
    args = parser.parse_args()

    outputs: dict[str, Any] = {}
    for task_name in args.tasks:
        outputs[task_name] = build_task(task_name)
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
