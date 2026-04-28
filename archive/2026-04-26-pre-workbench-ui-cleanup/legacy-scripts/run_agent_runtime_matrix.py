#!/usr/bin/env python3
"""Run a task x agent-runtime validation matrix."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from backend_registry import load_backend_registry  # noqa: E402


OUT_ROOT = REPO_ROOT / "analysis" / "runtime_matrix"
DEFAULT_TASKS = [
    "task006_near_neighbor",
    "task008_bad_candidate",
    "task009_evaluator_gap",
    "task010_literature_required",
    "task011_portfolio_stop",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def runtime_profile(runtime_id: str) -> dict[str, Any]:
    registry = load_backend_registry()
    runtime = registry["runtimes"].get(runtime_id)
    if not isinstance(runtime, dict):
        raise RuntimeError(f"unknown runtime {runtime_id}")
    return runtime


def run_command(command: list[str], *, timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_sec": round(time.monotonic() - started, 3),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"timeout after {timeout}s",
            "duration_sec": round(time.monotonic() - started, 3),
            "timed_out": True,
        }


def run_case(task_id: str, runtime_id: str, timeout: int) -> dict[str, Any]:
    runtime = runtime_profile(runtime_id)
    case_dir = OUT_ROOT / "cases" / runtime_id / task_id
    adapter = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    if not adapter.exists():
        return {
            "task_id": task_id,
            "runtime_id": runtime_id,
            "status": "failed",
            "failure_class": "missing_adapter",
            "issues": [f"missing {adapter.relative_to(REPO_ROOT)}"],
            "runtime_profile": runtime.get("agent_profile"),
        }

    if runtime.get("status") == "blocked":
        return {
            "task_id": task_id,
            "runtime_id": runtime_id,
            "status": "blocked",
            "failure_class": "runtime_blocked",
            "issues": runtime.get("known_limitations", []),
            "runtime_profile": runtime.get("agent_profile"),
        }

    command = [
        sys.executable,
        "scripts/run_generic_loop_engine.py",
        "--task-adapter",
        str(adapter.relative_to(REPO_ROOT)),
        "--backend",
        runtime_id,
        "--run-intent",
        "runtime_matrix_validation",
    ]
    run = run_command(command, timeout=timeout)
    write_text(case_dir / "run.stdout.txt", run["stdout"])
    write_text(case_dir / "run.stderr.txt", run["stderr"])
    status = "run_failed"
    failure_class = None
    verifier = None
    issues: list[str] = []
    if run["returncode"] == 0:
        verify_command = [
            sys.executable,
            "scripts/verify_generic_full_loop.py",
            "--task",
            task_id,
            "--backend",
            runtime_id,
        ]
        verifier = run_command(verify_command, timeout=timeout)
        write_text(case_dir / "verify.stdout.txt", verifier["stdout"])
        write_text(case_dir / "verify.stderr.txt", verifier["stderr"])
        if verifier["returncode"] == 0:
            status = "passed"
        else:
            status = "verify_failed"
            failure_class = "artifact_verification_failed"
            issues.append(verifier["stderr"] or verifier["stdout"])
    else:
        failure_class = "runtime_execution_failed"
        if run["timed_out"]:
            failure_class = "timeout"
        issues.append(run["stderr"] or run["stdout"])

    result = {
        "task_id": task_id,
        "runtime_id": runtime_id,
        "runtime_profile": runtime.get("agent_profile"),
        "status": status,
        "failure_class": failure_class,
        "issues": [issue[:1000] for issue in issues if issue],
        "run_returncode": run["returncode"],
        "run_duration_sec": run["duration_sec"],
        "verify_returncode": verifier["returncode"] if verifier else None,
        "verify_duration_sec": verifier["duration_sec"] if verifier else None,
        "case_dir": str(case_dir.relative_to(REPO_ROOT)),
    }
    write_json(case_dir / "result.json", result)
    return result


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_runtime: dict[str, dict[str, Any]] = {}
    by_task: dict[str, dict[str, Any]] = {}
    for result in results:
        runtime = by_runtime.setdefault(result["runtime_id"], {"passed": 0, "failed": 0, "blocked": 0, "total": 0})
        task = by_task.setdefault(result["task_id"], {"passed": 0, "failed": 0, "blocked": 0, "total": 0})
        for bucket in (runtime, task):
            bucket["total"] += 1
            if result["status"] == "passed":
                bucket["passed"] += 1
            elif result["status"] == "blocked":
                bucket["blocked"] += 1
            else:
                bucket["failed"] += 1
    return {
        "by_runtime": by_runtime,
        "by_task": by_task,
        "passed": sum(1 for item in results if item["status"] == "passed"),
        "failed": sum(1 for item in results if item["status"] not in {"passed", "blocked"}),
        "blocked": sum(1 for item in results if item["status"] == "blocked"),
        "total": len(results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run agent runtime validation matrix.")
    parser.add_argument("--tasks", nargs="*", default=DEFAULT_TASKS)
    parser.add_argument("--runtimes", nargs="*", required=True)
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    started_at = utc_now()
    cases = [(task, runtime) for runtime in args.runtimes for task in args.tasks]
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_case = {
            executor.submit(run_case, task, runtime, args.timeout): (task, runtime)
            for task, runtime in cases
        }
        for future in concurrent.futures.as_completed(future_to_case):
            task, runtime = future_to_case[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "task_id": task,
                    "runtime_id": runtime,
                    "status": "failed",
                    "failure_class": "runner_exception",
                    "issues": [str(exc)],
                }
            results.append(result)
            print(f"{runtime}/{task}: {result['status']}")

    payload = {
        "schema_version": "0.1.0",
        "object_type": "agent_runtime_matrix_report",
        "object_id": "agent_runtime_matrix.full_loop.current",
        "created_at": started_at,
        "updated_at": utc_now(),
        "tasks": args.tasks,
        "runtimes": args.runtimes,
        "summary": summarize(results),
        "results": sorted(results, key=lambda item: (item["runtime_id"], item["task_id"])),
    }
    write_json(OUT_ROOT / "agent_runtime_matrix_report.json", payload)
    write_yaml(OUT_ROOT / "agent_runtime_matrix_report.yaml", payload)
    failures = [item for item in results if item["status"] not in {"passed", "blocked"}]
    print(f"Matrix report written to {OUT_ROOT.relative_to(REPO_ROOT)}/agent_runtime_matrix_report.yaml")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
