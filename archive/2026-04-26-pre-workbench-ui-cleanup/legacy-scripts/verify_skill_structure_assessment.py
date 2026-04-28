#!/usr/bin/env python3
"""Verify skill-structure assessment gates."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "structural_learning" / "task003_iter02"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing artifact: {path.relative_to(REPO_ROOT)}")


def verify() -> None:
    assessment_path = ROOT / "skill_structure_assessment.yaml"
    diagnosis_path = ROOT / "skill_structure_diagnosis.yaml"
    request_path = ROOT / "structural_skill_change_request.yaml"
    for path in [assessment_path, diagnosis_path, request_path]:
        require(path)
    assessment = load_yaml(assessment_path)
    diagnosis = load_yaml(diagnosis_path)
    request = load_yaml(request_path)

    if assessment["diagnosis_ref"] != diagnosis["object_id"]:
        raise RuntimeError("assessment does not reference diagnosis")
    if assessment["change_request_ref"] != request["object_id"]:
        raise RuntimeError("assessment does not reference structural request")
    if assessment["structural_verdict"] == "verified_structural_improvement":
        if max(assessment["method_score"], assessment["process_score"], assessment["standard_score"]) < 3:
            raise RuntimeError("verified structural improvement requires validated structural score")
        if assessment.get("blocked_claims"):
            raise RuntimeError("verified structural improvement must not keep blocked structural claims")
    else:
        if "verified structural skill improvement" not in assessment.get("blocked_claims", []):
            raise RuntimeError("non-verified assessment must block structural improvement claim")
    if diagnosis["diagnosis_class"] == "skill_use_improvement_only":
        if assessment["structural_verdict"] == "verified_structural_improvement":
            raise RuntimeError("skill-use-only diagnosis cannot verify structural improvement")
        if assessment["skill_use_score"] < max(
            assessment["method_score"],
            assessment["process_score"],
            assessment["standard_score"],
        ):
            raise RuntimeError("skill-use-only diagnosis must not score structural evidence above skill-use evidence")
    if request["change_type"] != "skill_use_tuning":
        if not assessment.get("required_next_evidence") and assessment["structural_verdict"] != "verified_structural_improvement":
            raise RuntimeError("structural attempt requires next evidence unless already verified")


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Skill structure assessment verification failed: {exc}", file=sys.stderr)
        return 1
    print("Skill structure assessment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
