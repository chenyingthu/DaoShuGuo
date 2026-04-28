#!/usr/bin/env python3
"""Verify the minimal generic loop engine skeleton with a fixture adapter."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from worker_chain_helpers import verify_worker_chain_root, load_yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_SCRIPT = REPO_ROOT / "scripts" / "run_generic_loop_engine.py"
FIXTURE_ADAPTER = REPO_ROOT / "analysis" / "generic_loop_engine_fixture" / "task_adapter.yaml"
TASK004_ADAPTER = REPO_ROOT / "analysis" / "generic_loop_engine_task004" / "task_adapter.yaml"
TASK005_ADAPTER = REPO_ROOT / "analysis" / "generic_loop_engine_task005" / "task_adapter.yaml"


def verify_adapter(task_adapter: Path, workspace_name: str) -> None:
    with tempfile.TemporaryDirectory(prefix="generic_loop_engine_verify_") as tmp_dir:
        workspace_root = Path(tmp_dir) / workspace_name
        command = [
            sys.executable,
            str(ENGINE_SCRIPT),
            "--task-adapter",
            str(task_adapter),
            "--workspace-root",
            str(workspace_root),
            "--run-intent",
            "verification_run",
        ]
        result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "generic loop engine execution failed")

        issues = verify_worker_chain_root(workspace_root / "artifacts", iterations=1, require_supporting=True)
        if issues:
            raise RuntimeError("\n".join(issues))

        run_record = load_yaml(workspace_root / "run.yaml")
        if run_record.get("status") != "completed":
            raise RuntimeError(f"generic loop engine run did not complete: {run_record.get('status')}")

        phase_transition_root = workspace_root / "phase_transitions"
        if len(list(phase_transition_root.glob("*.yaml"))) != 10:
            raise RuntimeError("generic loop engine did not record start/completed transitions for all five phases")

        artifact_index_path = workspace_root / "artifact_index.json"
        if not artifact_index_path.exists():
            raise RuntimeError("generic loop engine did not write artifact_index.json")

        review_path = workspace_root / "artifacts" / "loop_review" / "iter01.yaml"
        if not review_path.exists():
            raise RuntimeError("generic loop engine did not write loop_review")


def main() -> int:
    verify_adapter(FIXTURE_ADAPTER, "run_fixture_loop_0001")
    verify_adapter(TASK004_ADAPTER, "run_task004_adapter_0001")
    verify_adapter(TASK005_ADAPTER, "run_task005_adapter_0001")

    print("Generic loop engine verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
