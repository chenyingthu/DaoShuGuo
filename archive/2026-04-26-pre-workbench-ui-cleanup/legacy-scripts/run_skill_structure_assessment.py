#!/usr/bin/env python3
"""Assess whether a skill loop produced structural skill improvement."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02"
TASK_REF = "task.power.ieee69_renewable_reactive_opt"
TARGET_SKILL_REF = "skill.power.renewable_inverter_reactive_optimizer_task003_iter02"
BLOCKED_STRUCTURAL_CLAIMS = [
    "verified structural skill improvement",
    "method/process/standard improved",
    "agentic_skill_evolution_verified",
]


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


def score_dimension(items: list[str], *, validated: bool) -> int:
    if not items:
        return 0
    if validated:
        return 3
    return 1


def has_validated_ablation() -> bool:
    for path in ROOT.glob("ablation_result*.yaml"):
        result = load_yaml(path)
        if result.get("causal_claim_supported") is True:
            return True
    return False


def decide_verdict(
    *,
    method_score: int,
    process_score: int,
    standard_score: int,
    skill_use_score: int,
    diagnosis: dict[str, Any],
) -> tuple[str, str, list[str], list[str]]:
    structural_max = max(method_score, process_score, standard_score)
    validated = structural_max >= 3
    required_next_evidence = [
        "Run fixed-budget ablation against metric-only tuning.",
        "Validate at least one method/process/standard change under the same evaluator.",
        "Add robustness or multi-condition check before general structural claims.",
    ]
    blocked_claims = list(BLOCKED_STRUCTURAL_CLAIMS)

    if diagnosis.get("diagnosis_class") == "verified_structural_improvement" and not validated:
        return (
            "rejected_overclaim",
            "none",
            blocked_claims,
            required_next_evidence,
        )
    if validated:
        return (
            "verified_structural_improvement",
            "mixed_structural",
            [],
            [],
        )
    if structural_max > 0 and skill_use_score >= structural_max:
        return (
            "structural_attempt_ready",
            "mixed_structural",
            blocked_claims,
            required_next_evidence,
        )
    if skill_use_score > structural_max:
        return (
            "skill_use_improvement_only",
            "skill_use",
            blocked_claims,
            required_next_evidence,
        )
    return (
        "insufficient_evidence",
        "none",
        blocked_claims,
        required_next_evidence,
    )


def build_assessment(task: str, iteration: int) -> Path:
    if task != "task003" or iteration != 2:
        raise RuntimeError("MVP supports only --task task003 --iteration 2")
    paths = {
        "diagnosis": ROOT / "skill_structure_diagnosis.yaml",
        "request": ROOT / "structural_skill_change_request.yaml",
        "review": REPO_ROOT / "analysis" / "research_plan_execute" / "task003_iter02" / "research_review.yaml",
    }
    for path in paths.values():
        require(path)
    diagnosis = load_yaml(paths["diagnosis"])
    request = load_yaml(paths["request"])
    review = load_yaml(paths["review"])
    validated = has_validated_ablation()

    method_score = score_dimension(request.get("method_changes", []), validated=validated)
    process_score = score_dimension(request.get("process_changes", []), validated=validated)
    standard_score = score_dimension(request.get("standard_changes", []), validated=validated)
    skill_use_score = 2 if diagnosis.get("diagnosis_class") == "skill_use_improvement_only" else 1
    verdict, improvement_class, blocked_claims, required_next_evidence = decide_verdict(
        method_score=method_score,
        process_score=process_score,
        standard_score=standard_score,
        skill_use_score=skill_use_score,
        diagnosis=diagnosis,
    )
    now = utc_now()
    assessment = {
        "schema_version": "0.1.0",
        "object_type": "skill_structure_assessment",
        "object_id": "skill_structure_assessment.power.ieee69_renewable_reactive_opt.0002",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "metadata": {
            "protocol": "structural-learning-worker",
            "task_package": "task003",
            "score_scale": "0=no evidence, 1=planned/weak, 2=implemented, 3=validated",
        },
        "task_ref": TASK_REF,
        "source_review_ref": review["object_id"],
        "diagnosis_ref": diagnosis["object_id"],
        "change_request_ref": request["object_id"],
        "target_skill_ref": TARGET_SKILL_REF,
        "method_score": method_score,
        "process_score": process_score,
        "standard_score": standard_score,
        "skill_use_score": skill_use_score,
        "evidence_refs": [
            review["object_id"],
            diagnosis["object_id"],
            request["object_id"],
        ],
        "structural_verdict": verdict,
        "improvement_class": improvement_class,
        "blocked_claims": blocked_claims,
        "required_next_evidence": required_next_evidence,
        "summary": (
            "Structural attempt is ready, but task003 iter02 remains skill-use evidence until fixed-budget ablation validates method/process/standard change."
            if verdict == "structural_attempt_ready"
            else f"Skill structure assessment verdict: {verdict}"
        ),
    }
    output = ROOT / "skill_structure_assessment.yaml"
    write_yaml(output, assessment)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skill structure assessment.")
    parser.add_argument("--task", default="task003")
    parser.add_argument("--iteration", type=int, default=2)
    args = parser.parse_args()
    output = build_assessment(args.task, args.iteration)
    assessment = load_yaml(output)
    print(f"Skill structure assessment wrote {output.relative_to(REPO_ROOT)}")
    print(f"Verdict: {assessment['structural_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
