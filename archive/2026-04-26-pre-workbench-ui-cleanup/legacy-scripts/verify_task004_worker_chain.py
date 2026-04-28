#!/usr/bin/env python3
"""Verify task004 worker-chain artifacts form a complete generic object chain."""

from __future__ import annotations

import argparse
from pathlib import Path

from worker_chain_helpers import verify_worker_chain_root


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "analysis" / "worker_chain" / "task004"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify task004 worker chain artifacts.")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    issues = verify_worker_chain_root(args.root, iterations=args.iterations)
    if issues:
        for issue in issues:
            print(issue)
        raise SystemExit(1)

    print("Task004 worker-chain verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
