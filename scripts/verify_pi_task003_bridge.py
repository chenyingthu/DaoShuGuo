#!/usr/bin/env python3
"""Verify the Pi-style task003 bridge by invoking the existing orchestrator entrypoint."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = subprocess.run(
        ["python", "orchestrator/main.py", "real-run-task003", "--strategy", "inverter-support"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    payload = {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
