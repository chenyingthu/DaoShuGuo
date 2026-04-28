"""Common helpers for the file-backed collaborative research workbench."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_ROOT = REPO_ROOT / "workbench_data"
OBJECT_VERSION = "0.1.0"

TOPIC_TASK = {
    "real-task-001": "task004",
    "task003": "task003",
    "task004": "task004",
    "task005": "task005",
    "synthetic-topic-fixture": "synthetic",
}

HUMAN_OBJECT_DIR = {
    "human_review": "human_reviews",
    "research_decision": "decisions",
    "direction_override": "decisions",
    "expert_annotation": "annotations",
    "claim_approval": "claim_approvals",
    "iteration_steering": "steering",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug[:48] or "item"


def safe_id(object_type: str, topic_id: str, slug: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{object_type}.{topic_id}.{stamp}.{slugify(slug)}"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{rel(path)} did not parse to a mapping")
    return data


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))


def write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def base_object(object_type: str, object_id: str, status: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": "0.1.0",
        "object_type": object_type,
        "object_id": object_id,
        "object_version": OBJECT_VERSION,
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": metadata or {},
    }


def topic_task_id(topic_id: str) -> str:
    return TOPIC_TASK.get(topic_id, topic_id)


def task_ref_for(topic_id: str) -> str:
    task_id = topic_task_id(topic_id)
    if task_id == "synthetic":
        return "task.synthetic.workbench_fixture"
    task_path = REPO_ROOT / "tasks" / task_id / "task.yaml"
    if task_path.exists():
        try:
            return read_yaml(task_path).get("object_id", f"task.{task_id}")
        except Exception:
            return f"task.{task_id}"
    return f"task.{task_id}"


def topic_dir(topic_id: str) -> Path:
    return WORKBENCH_ROOT / "topics" / topic_id


def latest_run_dir(task_id: str) -> Path | None:
    run_root = REPO_ROOT / "runs" / task_id
    if not run_root.exists():
        return None
    dirs = sorted(path for path in run_root.glob("run_*") if path.is_dir())
    return dirs[-1] if dirs else None


def load_optional_yaml(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return read_yaml(path)
    except Exception:
        return None


def load_optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except Exception:
        return None


def source_ref(path: Path, obj: dict[str, Any] | None) -> str:
    if obj and isinstance(obj.get("object_id"), str):
        return obj["object_id"]
    return rel(path)


def real_task_skill_source_paths(topic_id: str) -> dict[str, Path]:
    if topic_id != "real-task-001":
        return {}
    base = REPO_ROOT / "analysis" / "real_task_001"
    upgrade = REPO_ROOT / "analysis" / "real_task_001_upgrade"
    return {
        "method_family_map": base / "literature" / "method_family_map.yaml",
        "metric_taxonomy": base / "literature" / "metric_taxonomy.yaml",
        "claim_thresholds": base / "literature" / "claim_thresholds.yaml",
        "experiment_design": base / "literature" / "experiment_design_recommendation.yaml",
        "skill_structure_diagnosis": base / "reframing" / "skill_structure_diagnosis.yaml",
        "structural_skill_change_request": base / "reframing" / "structural_skill_change_request.yaml",
        "effectiveness_assessment": upgrade / "reports" / "upgrade_effectiveness_assessment.yaml",
        "cognition_diagnosis": upgrade / "reports" / "upgrade_cognition_diagnosis.yaml",
        "loop_review": upgrade / "reports" / "upgrade_loop_review.yaml",
        "taste_assessment": upgrade / "delivery" / "taste_assessment.yaml",
    }


def real_task_skill_sources(topic_id: str) -> dict[str, Any]:
    paths = real_task_skill_source_paths(topic_id)
    loaded: dict[str, Any] = {}
    refs: list[str] = []
    missing: list[str] = []
    for name, path in paths.items():
        obj = load_optional_yaml(path)
        if obj is None:
            missing.append(rel(path))
            continue
        loaded[name] = obj
        refs.append(source_ref(path, obj))
    return {
        "topic_id": topic_id,
        "objects": loaded,
        "source_refs": refs,
        "missing_sources": missing,
    }


def list_field(obj: dict[str, Any] | None, field: str) -> list[Any]:
    if not obj:
        return []
    value = obj.get(field)
    return value if isinstance(value, list) else []


def find_method_family(method_family_map: dict[str, Any] | None, family_id: str) -> dict[str, Any] | None:
    for item in list_field(method_family_map, "method_families"):
        if item.get("family_id") == family_id:
            return item
    return None


def first_or_unknown(values: list[Any]) -> Any:
    return values[0] if values else "unknown"


def build_skill_cockpit(topic: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    objects = sources.get("objects", {})
    request = objects.get("structural_skill_change_request")
    diagnosis = objects.get("skill_structure_diagnosis")
    method_map = objects.get("method_family_map")
    metrics = objects.get("metric_taxonomy")
    experiment = objects.get("experiment_design")
    effectiveness = objects.get("effectiveness_assessment")
    cognition = objects.get("cognition_diagnosis")
    taste = objects.get("taste_assessment")

    if not request:
        return {
            "topic_id": topic["topic_id"],
            "status": "degraded",
            "active_skill_ref": "unknown",
            "candidate_family": "unknown",
            "candidate_dimension": "unknown",
            "skill_status": "insufficient_skill_evidence",
            "skill_use_vs_structure_judgment": "No structural skill request is available for this topic.",
            "method_changes": [],
            "process_changes": [],
            "standard_changes": [],
            "forbidden_shortcuts": [],
            "required_validation": [],
            "metric_evidence": {},
            "next_worker": "unknown",
            "next_action": "repair_skill_evidence",
            "source_refs": sources.get("source_refs", []),
            "missing_sources": sources.get("missing_sources", []),
        }

    candidate_family = "voltage_sensitivity_q_allocation"
    family = find_method_family(method_map, candidate_family)
    metric_summary = effectiveness.get("metric_summary", {}) if effectiveness else {}
    forbidden_claims = list_field(taste, "forbidden_claims")
    if not forbidden_claims:
        forbidden_claims = list_field(diagnosis, "claim_boundary")
    skill_status = "structural_attempt_not_verified"
    if metric_summary.get("primary_delta") not in (None, 0, 0.0) and metric_summary.get("boundary_triggered"):
        skill_status = "potential_structural_improvement_requires_review"

    return {
        "topic_id": topic["topic_id"],
        "status": "ready" if not sources.get("missing_sources") else "degraded",
        "active_skill_ref": request.get("target_skill_ref", "unknown"),
        "candidate_family": candidate_family,
        "candidate_dimension": family.get("skill_dimension", "method") if family else "method",
        "candidate_relation": family.get("relation_to_task004", "recommended structural candidate") if family else "unknown",
        "skill_status": skill_status,
        "skill_use_vs_structure_judgment": diagnosis.get("skill_use_vs_structure_judgment", cognition.get("judgment_summary", "")) if diagnosis or cognition else "",
        "method_changes": list_field(request, "method_changes"),
        "process_changes": list_field(request, "process_changes"),
        "standard_changes": list_field(request, "standard_changes"),
        "forbidden_shortcuts": list_field(request, "forbidden_usage_only_shortcuts") or list_field(experiment, "excluded_shortcuts"),
        "required_validation": list_field(request, "required_validation") or list_field(experiment, "minimum_zhuoshi_evidence"),
        "metric_evidence": {
            "primary_delta": metric_summary.get("primary_delta"),
            "loss_delta": metric_summary.get("loss_delta"),
            "voltage_margin_delta": metric_summary.get("voltage_margin_delta"),
            "boundary_trigger_delta": metric_summary.get("boundary_trigger_delta"),
            "control_effort_delta": metric_summary.get("control_effort_delta"),
            "boundary_triggered": metric_summary.get("boundary_triggered"),
            "claim_support_level": metric_summary.get("claim_support_level"),
            "metric_claim_boundaries": list_field(metrics, "claim_boundaries"),
        },
        "effectiveness_judgment": effectiveness.get("judgment_summary", "") if effectiveness else "",
        "cognition_judgment": cognition.get("judgment_summary", "") if cognition else "",
        "claim_ceiling": taste.get("claim_ceiling", topic.get("claim_ceiling", "unknown")) if taste else topic.get("claim_ceiling", "unknown"),
        "taste_grade": taste.get("grade", topic.get("taste_grade", "unknown")) if taste else topic.get("taste_grade", "unknown"),
        "forbidden_claims": forbidden_claims,
        "next_worker": cognition.get("recommended_next_worker", "skill_worker") if cognition else "skill_worker",
        "next_action": cognition.get("recommended_action", "redesign_skill_structure") if cognition else "redesign_skill_structure",
        "method_families": list_field(method_map, "method_families"),
        "experiment_matrix": list_field(experiment, "recommended_matrix"),
        "source_refs": sources.get("source_refs", []),
        "missing_sources": sources.get("missing_sources", []),
    }


def build_skill_progression(topic: dict[str, Any], sources: dict[str, Any], skill: dict[str, Any]) -> dict[str, Any]:
    objects = sources.get("objects", {})
    sequence = [
        ("method_family_map", "method families framed"),
        ("structural_skill_change_request", "structural skill request prepared"),
        ("effectiveness_assessment", "candidate evaluated"),
        ("cognition_diagnosis", "cognition diagnosis reviewed"),
        ("taste_assessment", "claim/taste gate applied"),
    ]
    steps = []
    for name, label in sequence:
        obj = objects.get(name)
        steps.append(
            {
                "step": name,
                "label": label,
                "status": "ready" if obj else "missing",
                "object_ref": obj.get("object_id") if obj else None,
            }
        )
    return {
        "topic_id": topic["topic_id"],
        "active_skill_ref": skill["active_skill_ref"],
        "current_position": "cognition_diagnosis" if objects.get("cognition_diagnosis") else "skill_evidence_incomplete",
        "steps": steps,
        "next_worker": skill["next_worker"],
        "next_action": skill["next_action"],
        "source_refs": skill["source_refs"],
    }


def build_skill_judgment_card(topic: dict[str, Any], skill: dict[str, Any]) -> dict[str, Any]:
    evidence = skill.get("metric_evidence", {})
    return {
        "topic_id": topic["topic_id"],
        "active_skill_ref": skill["active_skill_ref"],
        "candidate_family": skill["candidate_family"],
        "dimension": skill["candidate_dimension"],
        "status": skill["skill_status"],
        "baseline": "fixed_q_baseline / uniform_q_support",
        "primary_metric_delta": evidence.get("primary_delta"),
        "secondary_gain": "loss and voltage margin improved" if evidence.get("loss_delta") or evidence.get("voltage_margin_delta") else "not established",
        "cost_delta": evidence.get("control_effort_delta"),
        "boundary_triggered": evidence.get("boundary_triggered"),
        "judgment": skill.get("effectiveness_judgment") or skill.get("skill_use_vs_structure_judgment"),
        "forbidden_claims": skill.get("forbidden_claims", []),
        "next_worker": skill["next_worker"],
        "next_action": skill["next_action"],
        "source_refs": skill["source_refs"],
    }


def collect_topic_sources(topic_id: str) -> dict[str, Any]:
    task_id = topic_task_id(topic_id)
    sources: dict[str, Any] = {"topic_id": topic_id, "task_id": task_id, "evidence_refs": []}
    if topic_id == "synthetic-topic-fixture":
        sources.update(
            {
                "title": "Synthetic Workbench Fixture",
                "status": "degraded",
                "claim_ceiling": "technical_note",
                "taste_grade": "diaomu",
                "blocking_issue": "Synthetic fixture intentionally lacks full research artifacts.",
                "recommended_action": "Use this fixture only to test generic onboarding and degraded summaries.",
                "summary": "Synthetic topic verifies that the workbench is not hardwired to real-task-001.",
                "current_stage": "framing",
            }
        )
        return sources

    task_path = REPO_ROOT / "tasks" / task_id / "task.yaml"
    if task_path.exists():
        task = load_optional_yaml(task_path)
        if task:
            sources["title"] = task.get("title") or task.get("name") or task_id
            sources["task_ref"] = task.get("object_id", task_ref_for(topic_id))
            sources["evidence_refs"].append(sources["task_ref"])
    else:
        sources["title"] = topic_id

    if topic_id == "real-task-001":
        delivery_root = REPO_ROOT / "analysis" / "real_task_001_upgrade" / "delivery"
        report_root = REPO_ROOT / "analysis" / "real_task_001_upgrade" / "reports"
        taste = load_optional_yaml(delivery_root / "taste_assessment.yaml") or load_optional_yaml(
            REPO_ROOT / "analysis" / "real_task_001" / "delivery" / "taste_assessment.yaml"
        )
        delivery = load_optional_yaml(delivery_root / "delivery_readiness.yaml") or load_optional_yaml(
            REPO_ROOT / "analysis" / "real_task_001" / "delivery" / "delivery_readiness.yaml"
        )
        effectiveness = load_optional_yaml(report_root / "upgrade_effectiveness_assessment.yaml")
        diagnosis = load_optional_yaml(report_root / "upgrade_cognition_diagnosis.yaml")
        if taste:
            sources["taste_grade"] = taste.get("grade", "diaomu")
            sources["evidence_refs"].append(taste.get("object_id", "analysis.real_task_001_upgrade.delivery.taste_assessment"))
        if delivery:
            sources["claim_ceiling"] = delivery.get("readiness_level", "internal_report_ready")
            sources["evidence_refs"].append(delivery.get("object_id", "analysis.real_task_001_upgrade.delivery.delivery_readiness"))
        if effectiveness:
            metrics = effectiveness.get("metric_summary", {})
            primary_delta = metrics.get("primary_delta")
            boundary = metrics.get("boundary_triggered")
            sources["blocking_issue"] = (
                f"Primary hosting-capacity delta remains {primary_delta}; boundary_triggered={boundary}."
            )
            sources["evidence_refs"].append(effectiveness.get("object_id", "analysis.real_task_001_upgrade.effectiveness"))
        if diagnosis:
            sources["recommended_action"] = (
                "Design a boundary-triggering scenario before claiming hosting-capacity improvement."
            )
            sources["evidence_refs"].append(diagnosis.get("object_id", "analysis.real_task_001_upgrade.diagnosis"))
        sources.setdefault("current_stage", "cognition_reframing")
        sources.setdefault("summary", "Real task 001 shows framework reframing progress but no primary scientific claim upgrade.")
        sources.setdefault("claim_ceiling", "internal_report_ready")
        sources.setdefault("taste_grade", "diaomu")
        sources.setdefault("blocking_issue", "No primary metric improvement is proven.")
        sources.setdefault("recommended_action", "Pause claim escalation and ask expert to steer next scenario design.")
        return sources

    latest = latest_run_dir(task_id)
    if latest:
        run = load_optional_yaml(latest / "run.yaml")
        taste = load_optional_yaml(latest / "taste_assessment.yaml")
        report = load_optional_yaml(latest / "report.yaml")
        if run:
            sources["evidence_refs"].append(run.get("object_id", f"run.{task_id}.{latest.name}"))
        if taste:
            sources["taste_grade"] = taste.get("grade", "unknown")
            sources["claim_ceiling"] = taste.get("recommended_report_type", "technical_note")
            sources["evidence_refs"].append(taste.get("object_id", f"taste.{task_id}.{latest.name}"))
        if report:
            sources["evidence_refs"].append(report.get("object_id", f"report.{task_id}.{latest.name}"))
        sources["current_stage"] = "delivery_review"
        sources["blocking_issue"] = "Generic topic summary is based on the latest available run only."
        sources["recommended_action"] = "Review evidence and decide whether further loop execution is worthwhile."
        sources["summary"] = f"{topic_id} workbench topic generated from latest run {latest.name}."
        sources.setdefault("claim_ceiling", "technical_note")
        sources.setdefault("taste_grade", "unknown")
    else:
        sources["current_stage"] = "framing"
        sources["claim_ceiling"] = "technical_note"
        sources["taste_grade"] = "unknown"
        sources["blocking_issue"] = "No run artifacts were found for this topic."
        sources["recommended_action"] = "Run onboarding or attach artifacts before deeper evaluation."
        sources["summary"] = f"{topic_id} has a task package but no run evidence."
    return sources


def build_workbench_topic(topic_id: str) -> dict[str, Any]:
    src = collect_topic_sources(topic_id)
    status = "ready" if src.get("evidence_refs") else "degraded"
    obj = base_object(
        "workbench_topic",
        f"workbench_topic.{topic_id}",
        src.get("status", status),
        {"builder": "build_workbench_topic", "source": "file_backed"},
    )
    obj.update(
        {
            "topic_id": topic_id,
            "task_id": src["task_id"],
            "title": src.get("title", topic_id),
            "current_stage": src.get("current_stage", "unknown"),
            "claim_ceiling": src.get("claim_ceiling", "unknown"),
            "taste_grade": src.get("taste_grade", "unknown"),
            "blocking_issue": src.get("blocking_issue", "unknown"),
            "recommended_action": src.get("recommended_action", "review topic evidence"),
            "evidence_refs": sorted(set(src.get("evidence_refs", []))),
            "summary": src.get("summary", "Workbench topic summary is degraded."),
        }
    )
    return obj


def timeline_events(topic: dict[str, Any]) -> list[dict[str, Any]]:
    now = utc_now()
    topic_id = topic["topic_id"]
    events = [
        {
            **base_object(
                "workbench_timeline_event",
                f"workbench_timeline_event.{topic_id}.topic_summary",
                "active",
                {"source": "workbench_topic"},
            ),
            "topic_id": topic_id,
            "event_time": now,
            "stage": topic["current_stage"],
            "event_type": "topic_summary",
            "headline": topic["title"],
            "summary": topic["summary"],
            "source_refs": topic["evidence_refs"] or [topic["object_id"]],
        }
    ]
    return events


def attention_items(topic: dict[str, Any], skill: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    topic_id = topic["topic_id"]
    if skill and skill.get("active_skill_ref") != "unknown":
        evidence_refs = skill.get("source_refs") or topic["evidence_refs"] or [topic["object_id"]]
        definitions = [
            (
                "skill_direction",
                "skill",
                "Should voltage_sensitivity_q_allocation remain the next skill direction?",
                "The next iteration must decide whether to keep investing in the current structural method candidate.",
                "Keep the skill worker focused on structural redesign with equal-effort comparison.",
                "direction_override",
            ),
            (
                "scenario_boundary",
                "evaluation",
                "Should the next iteration first repair boundary-triggering scenario evidence?",
                "The current primary delta is zero and boundary_triggered is false, so scenario evidence may be blocking interpretation.",
                "Run extended-until-violation and boundary-neighborhood checks before stronger claims.",
                "iteration_steering",
            ),
            (
                "effort_gate",
                "evaluation",
                "Should control effort be a hard gate for skill improvement?",
                "The current candidate improves secondary metrics while increasing control effort, which can create hidden-cost improvement.",
                "Require equal or bounded control effort for candidate comparison.",
                "human_review",
            ),
            (
                "claim_boundary",
                "delivery",
                "Should the claim remain an internal technical note at diaomu level?",
                "Claim quality and research direction require expert taste and boundary judgment.",
                skill.get("next_action") or topic["recommended_action"],
                "claim_approval",
            ),
        ]
        items: list[dict[str, Any]] = []
        for suffix, stage, question, why, recommendation, writeback in definitions:
            item = base_object(
                "human_attention_item",
                f"human_attention_item.{topic_id}.{suffix}",
                "open",
                {"source": "skill_cockpit"},
            )
            item.update(
                {
                    "topic_id": topic_id,
                    "severity": "high" if suffix in {"skill_direction", "scenario_boundary"} else "medium",
                    "stage": stage,
                    "question": question,
                    "why_human_needed": why,
                    "agent_recommendation": recommendation,
                    "evidence_refs": evidence_refs,
                    "allowed_actions": ["approve", "request_more_evidence", "override_direction", "pause"],
                    "writeback_object_type": writeback,
                }
            )
            items.append(item)
        return items

    item = base_object(
        "human_attention_item",
        f"human_attention_item.{topic_id}.claim_boundary",
        "open",
        {"source": "workbench_topic"},
    )
    item.update(
        {
            "topic_id": topic_id,
            "severity": "high" if topic["blocking_issue"] != "unknown" else "medium",
            "stage": "delivery",
            "question": "Should the current claim ceiling be accepted or challenged?",
            "why_human_needed": "Claim quality and research direction require expert taste and boundary judgment.",
            "agent_recommendation": topic["recommended_action"],
            "evidence_refs": topic["evidence_refs"] or [topic["object_id"]],
            "allowed_actions": ["approve", "request_more_evidence", "override_direction", "pause"],
            "writeback_object_type": "direction_override",
        }
    )
    return [item]


def explanation_cards(topic: dict[str, Any], skill: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    topic_id = topic["topic_id"]
    card = base_object(
        "agent_explanation_card",
        f"agent_explanation_card.{topic_id}.claim_ceiling",
        "active" if topic["evidence_refs"] else "ungrounded_draft",
        {"source": "workbench_topic"},
    )
    card.update(
        {
            "topic_id": topic_id,
            "stage": "delivery",
            "recommendation": topic["recommended_action"],
            "short_answer": (
                f"Current claim ceiling is {topic['claim_ceiling']} with taste grade {topic['taste_grade']}."
            ),
            "evidence_used": topic["evidence_refs"] or [topic["object_id"]],
            "alternatives_considered": [
                {
                    "option": "upgrade claim strength",
                    "rejected_reason": "The current evidence does not prove the required stronger outcome.",
                }
            ],
            "risk": ["Overclaim if secondary or degraded evidence is treated as primary scientific progress."],
            "uncertainty": [topic["blocking_issue"]],
            "human_decision_needed": True,
            "suggested_human_actions": ["Review claim boundary", "Write direction override if route is insufficient"],
            "generated_by_worker_ref": topic["object_id"],
        }
    )
    if skill and skill.get("active_skill_ref") != "unknown":
        card["stage"] = "skill"
        card["recommendation"] = skill.get("next_action", topic["recommended_action"])
        card["short_answer"] = (
            f"{skill['candidate_family']} is a {skill['skill_status']} for {skill['active_skill_ref']}."
        )
        card["evidence_used"] = skill.get("source_refs") or card["evidence_used"]
        card["risk"] = [
            "Overclaim if secondary operational-quality gains are treated as primary hosting-capacity improvement.",
            "Overclaim if a structural attempt is treated as verified structural skill improvement.",
        ]
        card["uncertainty"] = [
            f"boundary_triggered={skill.get('metric_evidence', {}).get('boundary_triggered')}",
            skill.get("skill_use_vs_structure_judgment", ""),
        ]
        card["suggested_human_actions"] = [
            "Choose whether the next skill worker should redesign method, scenario, or evaluation standard.",
            "Keep forbidden shortcuts explicit in the next routing constraints.",
        ]
    return [card]


def evidence_graph(topic: dict[str, Any], events: list[dict[str, Any]], attentions: list[dict[str, Any]], cards: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [{"id": topic["object_id"], "type": "workbench_topic", "label": topic["title"]}]
    edges: list[dict[str, str]] = []
    for ref in topic["evidence_refs"]:
        nodes.append({"id": ref, "type": "evidence", "label": ref})
        edges.append({"source": topic["object_id"], "target": ref, "relation": "summarizes"})
    for collection in (events, attentions, cards):
        for obj in collection:
            nodes.append({"id": obj["object_id"], "type": obj["object_type"], "label": obj.get("headline") or obj.get("question") or obj.get("short_answer", obj["object_id"])})
            edges.append({"source": obj["object_id"], "target": topic["object_id"], "relation": "belongs_to"})
    return {"topic_id": topic["topic_id"], "nodes": nodes, "edges": edges}


def researcher_lens(topic: dict[str, Any], attentions: list[dict[str, Any]], cards: list[dict[str, Any]], skill: dict[str, Any] | None = None) -> dict[str, Any]:
    metric_evidence = skill.get("metric_evidence", {}) if skill else {}
    obj = base_object(
        "researcher_lens",
        f"researcher_lens.{topic['topic_id']}",
        topic["status"],
        {"builder": "build_researcher_lens"},
    )
    obj.update(
        {
            "topic_id": topic["topic_id"],
            "executive_layer": {
                "headline": topic["title"],
                "claim_ceiling": topic["claim_ceiling"],
                "taste_grade": topic["taste_grade"],
                "blocking_issue": topic["blocking_issue"],
                "recommended_action": topic["recommended_action"],
                "active_skill_ref": skill.get("active_skill_ref") if skill else "unknown",
                "candidate_family": skill.get("candidate_family") if skill else "unknown",
                "skill_status": skill.get("skill_status") if skill else "unknown",
                "primary_metric_delta": metric_evidence.get("primary_delta"),
                "boundary_triggered": metric_evidence.get("boundary_triggered"),
                "control_effort_delta": metric_evidence.get("control_effort_delta"),
            },
            "research_layer": {
                "current_stage": topic["current_stage"],
                "what_it_means": [
                    "This summary is intended for expert steering, not raw artifact browsing.",
                    topic["summary"],
                ],
                "human_questions": [item["question"] for item in attentions],
                "method_changes": skill.get("method_changes", []) if skill else [],
                "process_changes": skill.get("process_changes", []) if skill else [],
                "standard_changes": skill.get("standard_changes", []) if skill else [],
                "skill_use_vs_structure_judgment": skill.get("skill_use_vs_structure_judgment", "") if skill else "",
                "forbidden_shortcuts": skill.get("forbidden_shortcuts", []) if skill else [],
                "required_validation": skill.get("required_validation", []) if skill else [],
                "human_skill_questions": [
                    item["question"] for item in attentions if item.get("stage") in {"skill", "evaluation"}
                ],
            },
            "audit_layer": {
                "topic_ref": topic["object_id"],
                "evidence_refs": topic["evidence_refs"],
                "skill_source_refs": skill.get("source_refs", []) if skill else [],
                "missing_skill_sources": skill.get("missing_sources", []) if skill else [],
            },
            "human_attention_refs": [item["object_id"] for item in attentions],
            "explanation_card_refs": [card["object_id"] for card in cards],
        }
    )
    return obj


def build_topic_bundle(topic_id: str) -> dict[str, Any]:
    topic = build_workbench_topic(topic_id)
    skill_sources = real_task_skill_sources(topic_id)
    skill_cockpit = build_skill_cockpit(topic, skill_sources)
    skill_progression = build_skill_progression(topic, skill_sources, skill_cockpit)
    skill_judgment_card = build_skill_judgment_card(topic, skill_cockpit)
    events = timeline_events(topic)
    attentions = attention_items(topic, skill_cockpit)
    cards = explanation_cards(topic, skill_cockpit)
    graph = evidence_graph(topic, events, attentions, cards)
    lens = researcher_lens(topic, attentions, cards, skill_cockpit)
    return {
        "topic": topic,
        "skill_cockpit": skill_cockpit,
        "skill_progression": skill_progression,
        "skill_judgment_card": skill_judgment_card,
        "timeline": events,
        "attention": attentions,
        "explanation_cards": cards,
        "evidence_graph": graph,
        "researcher_lens": lens,
    }


def write_topic_bundle(bundle: dict[str, Any]) -> None:
    topic = bundle["topic"]
    root = topic_dir(topic["topic_id"])
    write_yaml(root / "topic.yaml", topic)
    write_json(root / "cockpit.json", topic)
    write_json(root / "skill_cockpit.json", bundle["skill_cockpit"])
    write_json(root / "skill_progression.json", bundle["skill_progression"])
    write_json(root / "skill_judgment_card.json", bundle["skill_judgment_card"])
    write_json(root / "timeline.json", bundle["timeline"])
    atomic_write_text(
        root / "timeline.jsonl",
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in bundle["timeline"]),
    )
    write_json(root / "evidence_graph.json", bundle["evidence_graph"])
    write_json(root / "human_attention_queue.json", bundle["attention"])
    write_json(root / "question_cards.json", bundle["explanation_cards"])
    write_yaml(root / "researcher_lens.yaml", bundle["researcher_lens"])
    write_json(root / "researcher_lens.json", bundle["researcher_lens"])
    for item in bundle["attention"]:
        write_yaml(WORKBENCH_ROOT / "attention" / f"{item['object_id']}.yaml", item)
    for card in bundle["explanation_cards"]:
        write_yaml(WORKBENCH_ROOT / "explanation_cards" / f"{card['object_id']}.yaml", card)


def ensure_topic(topic_id: str) -> dict[str, Any]:
    topic_path = topic_dir(topic_id) / "topic.yaml"
    if not topic_path.exists():
        bundle = build_topic_bundle(topic_id)
        write_topic_bundle(bundle)
        return bundle["topic"]
    return read_yaml(topic_path)


def human_base(object_type: str, topic_id: str, slug: str, status: str = "active") -> dict[str, Any]:
    task_id = task_ref_for(topic_id)
    obj = base_object(object_type, safe_id(object_type, topic_id, slug), status, {"source": "workbench_writer"})
    obj.update(
        {
            "topic_id": topic_id,
            "task_id": task_id,
            "created_by": "expert",
            "source": "cli",
            "target_refs": [f"workbench_topic.{topic_id}"],
            "evidence_refs": [f"workbench_topic.{topic_id}"],
        }
    )
    return obj


def default_human_object(object_type: str, topic_id: str) -> dict[str, Any]:
    topic = ensure_topic(topic_id)
    if object_type == "human_review":
        obj = human_base(object_type, topic_id, "review_claim_boundary")
        obj.update(
            {
                "review_target_ref": topic["object_id"],
                "reviewer_role": "principal_investigator",
                "decision": "revise",
                "rationale": "The topic needs expert-readable evidence before stronger claims.",
                "required_changes": ["Keep claim ceiling explicit.", "Preserve evidence refs in summaries."],
                "claim_boundary": [f"Do not exceed {topic['claim_ceiling']} without evaluator evidence."],
            }
        )
        return obj
    if object_type == "research_decision":
        obj = human_base(object_type, topic_id, "research_direction")
        obj.update(
            {
                "decision_scope": "task",
                "selected_option": "Prioritize evidence-grounded reframing before stronger claims.",
                "rejected_options": [{"option": "Continue local tuning", "reason": "May deepen local trap."}],
                "decision_drivers": ["claim boundary", "expert steering", "evidence quality"],
                "human_rationale": "The next step should improve research framing rather than only produce more files.",
                "agent_recommendation_ref": f"agent_explanation_card.{topic_id}.claim_ceiling",
            }
        )
        return obj
    if object_type == "direction_override":
        obj = human_base(object_type, topic_id, "boundary_triggering_scenario")
        skill = build_skill_cockpit(topic, real_task_skill_sources(topic_id))
        if skill.get("active_skill_ref") != "unknown":
            obj["metadata"]["target_worker"] = "skill_worker"
            obj["metadata"]["active_skill_ref"] = skill["active_skill_ref"]
            obj["metadata"]["candidate_family"] = skill["candidate_family"]
            obj.update(
                {
                    "source_routing_ref": f"agent_explanation_card.{topic_id}.claim_ceiling",
                    "override_action": "Route the next iteration to skill_worker for skill-structure redesign.",
                    "why_agent_route_is_insufficient": "Current evidence shows a structural attempt and secondary gains, but no primary hosting-capacity improvement or boundary trigger.",
                    "new_constraints": [
                        "Compare voltage_sensitivity_q_allocation against uniform_q_support under equal or bounded control effort.",
                        "Run extended-until-violation and boundary-neighborhood checks before claiming boundary movement.",
                        "Report method, process, and standard changes separately in the next skill_change_request.",
                    ],
                    "must_not_do": [
                        "Do not use q_step-only escalation as a claimed skill improvement path.",
                        "Do not treat secondary loss or voltage-margin improvement as primary hosting-capacity improvement.",
                        "Do not claim boundary improvement unless boundary_triggered=true under the evaluator.",
                    ],
                }
            )
            return obj
        obj.update(
            {
                "source_routing_ref": f"agent_explanation_card.{topic_id}.claim_ceiling",
                "override_action": "Prioritize boundary-triggering scenario design before further claim escalation.",
                "why_agent_route_is_insufficient": "Current route can generate activity without proving the primary research claim.",
                "new_constraints": ["Next loop must address the blocking issue before skill or claim upgrade."],
                "must_not_do": ["Do not treat parameter or presentation changes as structural skill improvement."],
            }
        )
        return obj
    if object_type == "expert_annotation":
        obj = human_base(object_type, topic_id, "taste_warning")
        obj.update(
            {
                "target_ref": topic["object_id"],
                "annotation_type": "taste_note",
                "content": "Keep the report at the evidence-supported level; do not let readable writing inflate result quality.",
                "severity": "high",
                "action_required": True,
            }
        )
        return obj
    if object_type == "claim_approval":
        obj = human_base(object_type, topic_id, "conditional_claim_boundary")
        obj.update(
            {
                "deliverable_ref": topic["object_id"],
                "approved_claims": ["The framework can present an evidence-grounded workbench summary."],
                "rejected_claims": ["The scientific result is upgraded beyond evaluator support."],
                "required_qualifiers": [f"Claim ceiling remains {topic['claim_ceiling']}."],
                "max_report_type": "technical_note",
                "approval_status": "conditional",
            }
        )
        return obj
    if object_type == "iteration_steering":
        obj = human_base(object_type, topic_id, "next_iteration_steering")
        skill = build_skill_cockpit(topic, real_task_skill_sources(topic_id))
        if skill.get("active_skill_ref") != "unknown":
            obj["metadata"]["target_worker"] = "skill_worker"
            obj["metadata"]["active_skill_ref"] = skill["active_skill_ref"]
            obj.update(
                {
                    "source_loop_ref": topic["object_id"],
                    "target_next_iteration": 1,
                    "steering_goal": "Make the next loop resolve skill-structure evidence gaps before claim escalation.",
                    "priority": "high",
                    "preferred_actions": [
                        skill["next_action"],
                        "Use equal-effort comparison and boundary-triggering evidence for candidate evaluation.",
                    ],
                    "forbidden_actions": [
                        "Do not run another loop without explaining what changed in method, process, or standard.",
                        "Do not present structural attempt as verified structural skill improvement.",
                    ],
                    "required_evidence": skill.get("source_refs") or topic["evidence_refs"] or [topic["object_id"]],
                    "stop_condition": "Pause if the next run still has primary_delta=0 and boundary_triggered=false without a scenario diagnosis.",
                    "human_rationale": "Expert attention should steer skill development toward structural improvement rather than local tuning.",
                }
            )
            return obj
        obj.update(
            {
                "source_loop_ref": topic["object_id"],
                "target_next_iteration": 1,
                "steering_goal": "Make the next loop resolve the main blocking issue instead of adding local artifacts.",
                "priority": "high",
                "preferred_actions": [topic["recommended_action"]],
                "forbidden_actions": ["Do not run another loop without explaining what changed structurally."],
                "required_evidence": topic["evidence_refs"] or [topic["object_id"]],
                "stop_condition": "Pause if no evaluator or evidence refs are available.",
                "human_rationale": "Expert attention should steer the loop toward research value.",
            }
        )
        return obj
    raise ValueError(f"unsupported human object type: {object_type}")


def human_object_path(obj: dict[str, Any]) -> Path:
    folder = HUMAN_OBJECT_DIR[obj["object_type"]]
    return WORKBENCH_ROOT / folder / f"{obj['object_id']}.yaml"


def write_human_object(obj: dict[str, Any], *, dry_run: bool) -> Path:
    path = human_object_path(obj)
    if path.exists() and not dry_run:
        raise RuntimeError(f"refusing to overwrite existing object {rel(path)}")
    if not dry_run:
        write_yaml(path, obj)
        append_jsonl(topic_dir(obj["topic_id"]) / "timeline.jsonl", {"event": "human_object_written", "object_ref": obj["object_id"], "created_at": utc_now()})
    return path


def active_human_objects(topic_id: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for folder in sorted(set(HUMAN_OBJECT_DIR.values())):
        root = WORKBENCH_ROOT / folder
        if not root.exists():
            continue
        for path in sorted(root.glob(f"*.{topic_id}.*.yaml")):
            obj = load_optional_yaml(path)
            if obj and obj.get("status") == "active":
                objects.append(obj)
    return objects


def compile_constraints(topic_id: str, *, dry_run: bool) -> list[dict[str, Any]]:
    ensure_topic(topic_id)
    constraints: list[dict[str, Any]] = []
    for human in active_human_objects(topic_id):
        object_type = human["object_type"]
        contents: list[tuple[str, str, str]] = []
        if object_type == "direction_override":
            stage = "skill" if human.get("metadata", {}).get("target_worker") == "skill_worker" else "loop"
            contents.extend((stage, "must_do", item) for item in human.get("new_constraints", []))
            contents.extend((stage, "must_not_do", item) for item in human.get("must_not_do", []))
        elif object_type == "research_decision":
            contents.append(("framing", "prefer", human.get("selected_option", "")))
        elif object_type == "human_review":
            contents.extend(("delivery", "claim_limit", item) for item in human.get("claim_boundary", []))
            contents.extend(("loop", "require_evidence", item) for item in human.get("required_changes", []))
        elif object_type == "claim_approval":
            contents.extend(("delivery", "claim_limit", item) for item in human.get("required_qualifiers", []))
        elif object_type == "iteration_steering":
            stage = "skill" if human.get("metadata", {}).get("target_worker") == "skill_worker" else "loop"
            contents.extend((stage, "prefer", item) for item in human.get("preferred_actions", []))
            contents.extend((stage, "must_not_do", item) for item in human.get("forbidden_actions", []))
        elif object_type == "expert_annotation" and human.get("action_required"):
            contents.append(("loop", "require_evidence", human.get("content", "")))
        for idx, (stage, constraint_type, content) in enumerate(contents):
            if not content:
                continue
            constraint = base_object(
                "routing_constraint",
                f"routing_constraint.{topic_id}.{slugify(human['object_id'])}.{idx}",
                "active",
                {"compiled_from": human["object_id"]},
            )
            constraint.update(
                {
                    "topic_id": topic_id,
                    "task_id": human["task_id"],
                    "source_human_object_ref": human["object_id"],
                    "applies_to_stage": stage,
                    "constraint_type": constraint_type,
                    "content": content,
                    "priority": "high" if object_type in {"direction_override", "iteration_steering"} else "medium",
                    "active": True,
                    "expires_after_iteration": 1,
                    "conflicts_with": [],
                    "resolution_status": "none",
                }
            )
            if human.get("metadata", {}).get("target_worker"):
                constraint["metadata"]["target_worker"] = human["metadata"]["target_worker"]
            if human.get("metadata", {}).get("active_skill_ref"):
                constraint["metadata"]["active_skill_ref"] = human["metadata"]["active_skill_ref"]
            constraints.append(constraint)
    if not dry_run:
        for constraint in constraints:
            path = WORKBENCH_ROOT / "routing_constraints" / f"{constraint['object_id']}.yaml"
            write_yaml(path, constraint)
    return constraints


def build_agent_response(topic_id: str, human_ref: str, constraint_refs: list[str], *, dry_run: bool) -> dict[str, Any]:
    topic = ensure_topic(topic_id)
    obj = base_object(
        "agent_response_to_human",
        safe_id("agent_response_to_human", topic_id, "accepted_human_constraint"),
        "active",
        {"source": "compile_human_decision_constraints"},
    )
    obj.update(
        {
            "topic_id": topic_id,
            "task_id": topic["task_id"],
            "human_object_ref": human_ref,
            "response_type": "accepted",
            "rationale": "The human intervention is compatible with evaluator and taste gates and is converted into loop constraints.",
            "changed_routing_constraints": constraint_refs,
            "next_actions": ["Inject active routing constraints before the next loop run."],
            "evidence_refs": [human_ref, topic["object_id"]],
        }
    )
    if not dry_run:
        write_yaml(WORKBENCH_ROOT / "agent_responses" / f"{obj['object_id']}.yaml", obj)
    return obj


def skill_for_topic(topic_id: str) -> dict[str, Any]:
    topic = ensure_topic(topic_id)
    skill_path = topic_dir(topic_id) / "skill_cockpit.json"
    loaded = load_optional_json(skill_path)
    if isinstance(loaded, dict):
        return loaded
    return build_skill_cockpit(topic, real_task_skill_sources(topic_id))


def build_briefs(topic_id: str) -> dict[str, dict[str, Any]]:
    topic = ensure_topic(topic_id)
    skill = skill_for_topic(topic_id)
    evidence_refs = topic["evidence_refs"] or [topic["object_id"]]
    skill_refs = skill.get("source_refs") or evidence_refs
    metric_evidence = skill.get("metric_evidence", {})
    mentor = base_object("mentor_brief", f"mentor_brief.{topic_id}.current", "active" if topic["evidence_refs"] else "degraded", {"builder": "research_communication"})
    mentor.update(
        {
            "topic_id": topic_id,
            "iteration": 1,
            "headline": f"{topic['title']}: {skill.get('candidate_family', 'skill evidence')} is {skill.get('skill_status', 'unknown')}",
            "one_minute_summary": (
                f"Current active skill is {skill.get('active_skill_ref', 'unknown')}. "
                f"The candidate family is {skill.get('candidate_family', 'unknown')} and the evidence judgment is {skill.get('skill_status', 'unknown')}. "
                f"Primary delta is {metric_evidence.get('primary_delta')}; boundary_triggered={metric_evidence.get('boundary_triggered')}; "
                f"control_effort_delta={metric_evidence.get('control_effort_delta')}. "
                f"Recommended next action: {skill.get('next_action') or topic['recommended_action']}."
            ),
            "what_changed": [
                {
                    "change_type": "skill",
                    "summary": f"Skill work is now framed around {skill.get('candidate_family', 'unknown')} with explicit method/process/standard changes.",
                    "evidence_refs": skill_refs,
                }
            ],
            "what_it_means": [
                skill.get("effectiveness_judgment") or "The researcher can inspect the skill evidence without opening raw files first.",
                skill.get("cognition_judgment") or "The system still requires evidence drill-down before stronger claims.",
            ],
            "what_is_not_proven": [
                "Verified structural skill improvement is not proven by this evidence.",
                "Hosting-capacity boundary improvement is not proven while primary_delta is 0 and boundary_triggered is false.",
                "Secondary operational-quality gains must not be treated as primary skill improvement.",
            ],
            "human_questions_to_consider": [
                "Should voltage_sensitivity_q_allocation remain the next skill direction?",
                "Should the next iteration repair boundary-triggering scenario evidence before more method work?",
                "Should control effort become a hard gate for skill improvement?",
            ],
            "recommended_human_action": skill.get("next_action") or topic["recommended_action"],
            "drilldown_refs": skill_refs,
        }
    )
    digest = base_object("iteration_digest", f"iteration_digest.{topic_id}.current", mentor["status"], {"builder": "research_communication"})
    digest.update(
        {
            "topic_id": topic_id,
            "compared_iterations": ["current"],
            "substantive_changes": [
                f"Candidate skill family is {skill.get('candidate_family', 'unknown')}.",
                "Method, process, and standard changes are explicit in the structural skill request.",
            ],
            "non_changes": [
                "Primary hosting-capacity improvement is not established.",
                "Structural attempt is not the same as verified structural skill improvement.",
            ],
            "evidence_refs": skill_refs,
            "summary": "Iteration digest separates skill-structure evidence from secondary operational-quality gains.",
        }
    )
    decision = base_object("decision_brief", f"decision_brief.{topic_id}.claim_boundary", mentor["status"], {"builder": "research_communication"})
    decision.update(
        {
            "topic_id": topic_id,
            "decision_question": "Should the next skill iteration prioritize method redesign, boundary scenario repair, or effort-gated evaluation?",
            "options": [
                {"option": "continue voltage_sensitivity_q_allocation", "risk": "May remain unproven if boundary evidence is still weak."},
                {"option": "repair boundary-triggering scenario first", "risk": "Delays method changes but improves interpretability."},
                {"option": "enforce equal-effort comparison", "risk": "May reduce apparent secondary gains."},
            ],
            "recommended_option": "write direction override targeting skill_worker if the next loop must avoid local tuning shortcuts",
            "risks": ["Overclaim", "Local task trap", "Confusing secondary metric improvement with structural skill improvement"],
            "evidence_refs": skill_refs,
            "writable_actions": ["human_review", "research_decision", "direction_override", "iteration_steering"],
            "summary": "Decision brief is designed to make the expert intervention point explicit.",
        }
    )
    failure = base_object("failure_brief", f"failure_brief.{topic_id}.current", mentor["status"], {"builder": "research_communication"})
    failure.update(
        {
            "topic_id": topic_id,
            "failure_type": "skill_structure_not_verified",
            "what_failed": f"Primary delta is {metric_evidence.get('primary_delta')} and boundary_triggered={metric_evidence.get('boundary_triggered')}.",
            "what_it_exposes": [
                "The candidate can improve secondary operational-quality metrics without proving hosting-capacity improvement.",
                "The next loop should resolve boundary and equal-effort evidence before claiming skill improvement.",
            ],
            "whether_to_continue": "Continue only with explicit skill-worker constraints or stronger boundary evidence.",
            "evidence_refs": skill_refs,
            "summary": "Failure brief turns a bounded structural attempt into a readable skill-development lesson.",
        }
    )
    claim = base_object("claim_brief", f"claim_brief.{topic_id}.current", mentor["status"], {"builder": "research_communication"})
    claim.update(
        {
            "topic_id": topic_id,
            "supported_claims": ["Structural method attempt with bounded operational-quality improvement."],
            "forbidden_claims": skill.get("forbidden_claims") or ["Do not claim scientific upgrade without evaluator and taste-gate evidence."],
            "claim_ceiling": skill.get("claim_ceiling", topic["claim_ceiling"]),
            "taste_grade": skill.get("taste_grade", topic["taste_grade"]),
            "evidence_refs": skill_refs,
            "summary": f"Claim brief keeps skill claims bounded at {skill.get('claim_ceiling', topic['claim_ceiling'])} / {skill.get('taste_grade', topic['taste_grade'])}.",
        }
    )
    return {
        "mentor_brief": mentor,
        "iteration_digest": digest,
        "decision_brief": decision,
        "failure_brief": failure,
        "claim_brief": claim,
    }


def write_briefs(topic_id: str) -> dict[str, dict[str, Any]]:
    briefs = build_briefs(topic_id)
    for brief in briefs.values():
        write_yaml(WORKBENCH_ROOT / "briefs" / f"{brief['object_id']}.yaml", brief)
    root = topic_dir(topic_id)
    atomic_write_text(
        root / "mentor_briefs.jsonl",
        "".join(json.dumps(brief, ensure_ascii=False) + "\n" for brief in briefs.values()),
    )
    write_json(root / "briefs.json", briefs)
    return briefs


def verify_topic_outputs(topic_id: str) -> list[str]:
    root = topic_dir(topic_id)
    required = [
        root / "topic.yaml",
        root / "cockpit.json",
        root / "timeline.jsonl",
        root / "evidence_graph.json",
        root / "researcher_lens.yaml",
        root / "human_attention_queue.json",
        root / "question_cards.json",
    ]
    issues = [f"missing {rel(path)}" for path in required if not path.exists()]
    if not issues:
        topic = read_yaml(root / "topic.yaml")
        if topic.get("topic_id") != topic_id:
            issues.append("topic_id mismatch")
        graph = read_json(root / "evidence_graph.json")
        if not graph.get("nodes"):
            issues.append("evidence graph has no nodes")
    return issues


def verify_briefs(topic_id: str) -> list[str]:
    root = topic_dir(topic_id)
    issues: list[str] = []
    expected = {
        "mentor_brief": f"mentor_brief.{topic_id}.current.yaml",
        "iteration_digest": f"iteration_digest.{topic_id}.current.yaml",
        "decision_brief": f"decision_brief.{topic_id}.claim_boundary.yaml",
        "failure_brief": f"failure_brief.{topic_id}.current.yaml",
        "claim_brief": f"claim_brief.{topic_id}.current.yaml",
    }
    for name, filename in expected.items():
        path = WORKBENCH_ROOT / "briefs" / filename
        if not path.exists():
            issues.append(f"missing {rel(path)}")
            continue
        data = read_yaml(path)
        text = json.dumps(data, ensure_ascii=False)
        if "workbench_data/" in text and len(data.get("summary", "")) < 30:
            issues.append(f"{name} looks like a file listing rather than a readable brief")
    mentor_path = WORKBENCH_ROOT / "briefs" / f"mentor_brief.{topic_id}.current.yaml"
    if mentor_path.exists():
        mentor = read_yaml(mentor_path)
        for field in ["one_minute_summary", "what_it_means", "what_is_not_proven", "human_questions_to_consider"]:
            value = mentor.get(field)
            if not value:
                issues.append(f"mentor_brief missing readable field {field}")
    return issues


def cli_topic_arg() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def fail_or_print(issues: list[str], ok_payload: dict[str, Any]) -> int:
    if issues:
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print(json.dumps(ok_payload, indent=2, ensure_ascii=False))
    return 0
