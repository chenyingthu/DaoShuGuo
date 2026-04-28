#!/usr/bin/env python3
"""Compatibility entrypoint for generic task onboarding.

With ``--task`` this writes one readiness report, matching the roadmap command
shape. Without arguments it runs the aggregate onboarding verifier.
"""

from __future__ import annotations

import argparse

from run_task_onboarding_check import build_report, rel, write_yaml, REPO_ROOT
from verify_task_onboarding import main as verify_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify generic task onboarding.")
    parser.add_argument("--task", help="Write and verify one task readiness report.")
    args = parser.parse_args()
    if not args.task:
        return verify_all()

    report = build_report(args.task)
    output = REPO_ROOT / "analysis" / "onboarding" / args.task / "task_readiness_report.yaml"
    write_yaml(output, report)
    print(f"Task onboarding report written to {rel(output)}")
    print(f"Status: {report['readiness_status']}")
    print(f"Route: {report['recommended_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
