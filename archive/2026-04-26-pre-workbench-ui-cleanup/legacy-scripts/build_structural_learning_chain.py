#!/usr/bin/env python3
"""Build the MVP structural-learning chain for task003 iter02.

This builder is deterministic and uses current repository artifacts. It does
not perform web search. Curated seed insights are explicitly marked as seed
material so they cannot be mistaken for a complete literature review.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02"
TASK_REF = "task.power.ieee69_renewable_reactive_opt"
REVIEW_REF = "research_review.power.ieee69_renewable_reactive_opt.0002"
TARGET_SKILL_REF = "skill.power.renewable_inverter_reactive_optimizer_task003_iter02"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required artifact: {path.relative_to(REPO_ROOT)}")


def source_refs() -> list[str]:
    refs: list[str] = []
    for path in sorted((REPO_ROOT / "literature" / "cards" / "methods").glob("*.yaml"))[:3]:
        try:
            obj = load_yaml(path)
        except Exception:
            continue
        object_id = obj.get("object_id")
        if isinstance(object_id, str):
            refs.append(object_id)
    if refs:
        return refs
    return ["method_card.power.task003_seed.structural_learning"]


def build_learning_need(now: str, review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "learning_need",
        "object_id": "learning_need.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {
            "protocol": "structural-learning-worker",
            "task_package": "task003",
            "source_verdict": review["verdict"],
        },
        "task_ref": TASK_REF,
        "source_review_ref": review["object_id"],
        "observation_type": "skill_use_improvement",
        "skill_dimension_focus": ["method", "process", "standard"],
        "learning_questions": [
            "What method principle could explain the observed inverter-Q improvement beyond search-envelope expansion?",
            "What process should separate candidate generation, evaluation, and claim review?",
            "What standard is needed to distinguish structural skill improvement from skill-use tuning?",
        ],
        "required_source_types": ["method_card", "paper_record", "code_reference"],
        "exclusion_criteria": [
            "Do not use sources without applicability boundary.",
            "Do not use metric-only gains as method principles.",
            "Do not lower evaluator criteria to create progress.",
        ],
        "success_criteria": [
            "Identify at least one candidate method principle.",
            "Identify at least one process improvement target.",
            "Identify at least one standard/evaluator improvement target.",
        ],
        "claim_boundary": [
            "This learning need does not prove structural skill improvement.",
            "The strongest current claim remains skill-use improvement under task003 single-condition evidence.",
        ],
    }


def build_learning_context(now: str, need: dict[str, Any]) -> dict[str, Any]:
    refs = source_refs()
    return {
        "schema_version": "0.1.0",
        "object_type": "learning_context_pack",
        "object_id": "learning_context_pack.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {
            "protocol": "structural-learning-worker",
            "task_package": "task003",
            "source_mode": "curated_seed" if refs[0].startswith("method_card.power.task003_seed") else "local_repository_sources",
        },
        "learning_need_ref": need["object_id"],
        "source_refs": refs,
        "source_summaries": [
            {
                "source_ref": refs[0],
                "relevance": "Used to force separation between search-space expansion and method/process/standard improvement.",
            }
        ],
        "method_insights": [
            "The task003 iter02 gain is currently explained by broader inverter-Q search; a structural method change needs an explicit control-policy principle.",
            "A method-level candidate should explain how inverter reactive support is selected, not only enumerate more Q points.",
        ],
        "process_insights": [
            "Candidate generation, evaluation, ablation, and claim review should be separate steps with separate artifacts.",
            "The loop should create a structural request only after learning material is reviewed.",
        ],
        "standard_insights": [
            "Structural claims require fixed-budget comparison against metric-only tuning.",
            "Evaluation should include cost, robustness, and single-condition boundary checks before claiming generality.",
        ],
        "applicability_boundaries": [
            "This MVP context is curated seed learning, not a complete literature survey.",
            "Insights apply to task003 single-representative-condition evidence only.",
        ],
        "confidence": "medium",
        "gaps": [
            "Needs real external literature retrieval before high-confidence method claims.",
            "Needs ablation separating cognition-guided structure from metric-only tuning.",
        ],
        "curator_notes": "Learning worker output is intentionally conservative and does not decide the cognition conclusion.",
    }


def build_diagnosis(now: str, context: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "skill_structure_diagnosis",
        "object_id": "skill_structure_diagnosis.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {
            "protocol": "structural-learning-worker",
            "task_package": "task003",
            "source_review_verdict": review["verdict"],
        },
        "task_ref": TASK_REF,
        "learning_context_ref": context["object_id"],
        "source_review_ref": review["object_id"],
        "diagnosis_class": "skill_use_improvement_only",
        "method_diagnosis": "The current task003 improvement comes from broader inverter-Q search, not a verified reusable control-policy method.",
        "process_diagnosis": "The previous loop still allowed candidate search and claim formation to be too close; ablation must become a separate process step.",
        "standard_diagnosis": "The current evaluator proves metric improvement under one condition but not structural superiority, robustness, or cost-quality balance.",
        "skill_use_vs_structure_judgment": "This is useful skill-use evidence that should guide a structural attempt, but it is not verified skill-structure improvement.",
        "reusable_principle_candidates": [
            "Separate control-policy principle design from search-envelope expansion.",
            "Require fixed-budget ablation before attributing improvement to cognition-guided structure.",
            "Treat method, process, and standard changes as separate skill dimensions.",
        ],
        "unresolved_uncertainty": [
            "No metric-only tuning baseline exists under the same budget.",
            "No multi-condition robustness evidence exists.",
            "No external literature-backed control-policy principle has been validated yet.",
        ],
        "claim_boundary": [
            "Do not claim structural skill improvement.",
            "Do not claim cognition caused skill improvement.",
            "May claim the learning layer identified structural questions for the next skill attempt.",
        ],
    }


def build_change_request(now: str, diagnosis: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "structural_skill_change_request",
        "object_id": "structural_skill_change_request.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "ready",
        "metadata": {
            "protocol": "structural-learning-worker",
            "task_package": "task003",
        },
        "task_ref": TASK_REF,
        "diagnosis_ref": diagnosis["object_id"],
        "target_skill_ref": TARGET_SKILL_REF,
        "change_type": "mixed_structural_change",
        "method_changes": [
            "Introduce an explicit inverter-Q control-policy principle that justifies candidate selection beyond grid expansion.",
            "Separate renewable inverter capability handling from candidate enumeration.",
        ],
        "process_changes": [
            "Produce separate artifacts for candidate generation, fixed-budget evaluation, and claim review.",
            "Run metric-only tuning baseline before review gate can upgrade skill-structure claims.",
        ],
        "standard_changes": [
            "Add fixed-budget ablation and cost/robustness boundary checks.",
            "Record whether gains come from method principle, process control, standard change, or usage tuning.",
        ],
        "forbidden_usage_only_shortcuts": [
            "Do not only add more Q grid points.",
            "Do not increase search budget without a matched baseline.",
            "Do not relax constraint_violation or reactive_support_effort interpretation.",
        ],
        "required_validation": [
            "Compare structural request against metric-only tuning under the same evaluator and fixed search budget.",
            "Report method/process/standard deltas separately.",
            "Keep causality and structural-improvement claims frozen until ablation passes.",
        ],
        "claim_boundary": [
            "This request authorizes a structural attempt, not a verified structural improvement.",
        ],
    }


def build(task: str, iteration: int) -> Path:
    if task != "task003" or iteration != 2:
        raise RuntimeError("MVP supports only --task task003 --iteration 2")
    review_path = REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02" / "research_review.yaml"
    require(review_path)
    review = load_yaml(review_path)
    now = utc_now()
    need = build_learning_need(now, review)
    context = build_learning_context(now, need)
    diagnosis = build_diagnosis(now, context, review)
    request = build_change_request(now, diagnosis)
    write_yaml(OUT_DIR / "learning_need.yaml", need)
    write_yaml(OUT_DIR / "learning_context_pack.yaml", context)
    write_yaml(OUT_DIR / "skill_structure_diagnosis.yaml", diagnosis)
    write_yaml(OUT_DIR / "structural_skill_change_request.yaml", request)
    return OUT_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description="Build structural learning chain.")
    parser.add_argument("--task", default="task003")
    parser.add_argument("--iteration", type=int, default=2)
    args = parser.parse_args()
    out_dir = build(args.task, args.iteration)
    print(f"Built structural learning chain in {out_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
