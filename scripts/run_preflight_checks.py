#!/usr/bin/env python3
"""Minimal preflight checks for DaoShuGuo."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check_paths() -> list[dict[str, Any]]:
    required = [
        ("schemas", REPO_ROOT / "schemas"),
        ("orchestrator", REPO_ROOT / "orchestrator" / "main.py"),
        ("task002", REPO_ROOT / "tasks" / "task002" / "task.yaml"),
        ("task003", REPO_ROOT / "tasks" / "task003" / "task.yaml"),
        ("task004", REPO_ROOT / "tasks" / "task004" / "task.yaml"),
    ]
    return [{"name": name, "path": str(path.relative_to(REPO_ROOT)), "ok": path.exists()} for name, path in required]


def check_artifacts() -> list[dict[str, Any]]:
    required = [
        ("task002_analysis", REPO_ROOT / "analysis" / "task002"),
        ("task003_literature", REPO_ROOT / "analysis" / "task003" / "literature_0002" / "literature_alignment.yaml"),
        ("task004_cognition", REPO_ROOT / "analysis" / "task004" / "upgrade_0001" / "cognition_upgrade.yaml"),
    ]
    return [{"name": name, "path": str(path.relative_to(REPO_ROOT)), "ok": path.exists()} for name, path in required]


def build_report() -> dict[str, Any]:
    path_checks = check_paths()
    artifact_checks = check_artifacts()
    blocking = [item["name"] for item in [*path_checks, *artifact_checks] if not item["ok"]]
    status = "ready" if not blocking else "blocked"
    return {
        "generated_at": utc_now(),
        "status": status,
        "checked_items": {"paths": path_checks, "artifacts": artifact_checks},
        "blocking_issues": blocking,
        "recommended_next_step": (
            "可以进入 light probe 或正式执行。"
            if status == "ready"
            else "先补齐 blocking issues 再进入正式执行。"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run minimal DaoShuGuo preflight checks.")
    parser.add_argument("--output", default="analysis/preflight/preflight_report.json")
    args = parser.parse_args()

    report = build_report()
    output = REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Preflight report written to {output}")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
