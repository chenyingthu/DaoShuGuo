#!/usr/bin/env python3
"""Verify researcher-readable communication briefs."""

from __future__ import annotations

from workbench_common import fail_or_print, verify_briefs


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    issues = [] if args.dry_run else verify_briefs(args.topic)
    return fail_or_print(issues, {"status": "passed", "topic": args.topic, "dry_run": args.dry_run})


if __name__ == "__main__":
    raise SystemExit(main())
