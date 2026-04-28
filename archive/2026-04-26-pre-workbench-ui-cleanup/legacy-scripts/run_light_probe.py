#!/usr/bin/env python3
"""Run a light readiness probe for DaoShuGuo."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(args),
        "returncode": result.returncode,
        "stdout_excerpt": result.stdout.strip()[:300],
        "stderr_excerpt": result.stderr.strip()[:300],
        "ok": result.returncode == 0,
    }


def build_probe() -> dict[str, Any]:
    commands = [
        ["python", "scripts/validate_schemas.py"],
        ["python", "orchestrator/main.py", "verify-task004-pipeline"],
    ]
    results = [run_command(command) for command in commands]
    blocking = [item["command"] for item in results if not item["ok"]]
    status = "ready" if not blocking else "blocked"
    return {
        "generated_at": utc_now(),
        "status": status,
        "checked_items": results,
        "blocking_issues": blocking,
        "recommended_next_step": (
            "可以进入正式执行。"
            if status == "ready"
            else "当前不建议进入正式执行，应先修复 probe 中的失败项。"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a light readiness probe.")
    parser.add_argument("--output", default="analysis/preflight/light_probe.json")
    args = parser.parse_args()
    report = build_probe()
    output = REPO_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Light probe written to {output}")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
