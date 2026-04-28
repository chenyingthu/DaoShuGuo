#!/usr/bin/env python3
"""Verify the structural-learning worker MVP artifacts."""

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
    paths = {
        "need": ROOT / "learning_need.yaml",
        "context": ROOT / "learning_context_pack.yaml",
        "diagnosis": ROOT / "skill_structure_diagnosis.yaml",
        "request": ROOT / "structural_skill_change_request.yaml",
    }
    for path in paths.values():
        require(path)
    need = load_yaml(paths["need"])
    context = load_yaml(paths["context"])
    diagnosis = load_yaml(paths["diagnosis"])
    request = load_yaml(paths["request"])

    if context["learning_need_ref"] != need["object_id"]:
        raise RuntimeError("learning_context_pack does not reference learning_need")
    if diagnosis["learning_context_ref"] != context["object_id"]:
        raise RuntimeError("skill_structure_diagnosis does not reference learning_context_pack")
    if request["diagnosis_ref"] != diagnosis["object_id"]:
        raise RuntimeError("structural_skill_change_request does not reference diagnosis")
    if need["source_review_ref"] != diagnosis["source_review_ref"]:
        raise RuntimeError("learning need and diagnosis must share source review")
    if not context.get("source_refs"):
        raise RuntimeError("learning context must include source refs")
    if not context.get("applicability_boundaries"):
        raise RuntimeError("learning context must include applicability boundaries")
    if diagnosis["diagnosis_class"] == "verified_structural_improvement":
        raise RuntimeError("MVP must not verify structural improvement without validation evidence")
    judgment = diagnosis.get("skill_use_vs_structure_judgment", "")
    if "skill-use" not in judgment or "skill-structure" not in judgment:
        raise RuntimeError("diagnosis must explicitly distinguish skill-use and skill-structure")
    if request["change_type"] == "skill_use_tuning":
        raise RuntimeError("MVP structural request must not collapse back to skill_use_tuning")
    combined_changes = (
        request.get("method_changes", [])
        + request.get("process_changes", [])
        + request.get("standard_changes", [])
    )
    if len(combined_changes) < 3:
        raise RuntimeError("structural request must include method/process/standard changes")
    forbidden_text = " ".join(request.get("forbidden_usage_only_shortcuts", []))
    if "Q grid" not in forbidden_text and "search" not in forbidden_text:
        raise RuntimeError("request must forbid usage-only search expansion shortcuts")


def main() -> int:
    try:
        verify()
    except Exception as exc:
        print(f"Structural learning chain verification failed: {exc}", file=sys.stderr)
        return 1
    print("Structural learning chain verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
