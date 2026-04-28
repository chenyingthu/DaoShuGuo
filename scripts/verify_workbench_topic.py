#!/usr/bin/env python3
"""Verify workbench topic aggregation outputs."""

from __future__ import annotations

from workbench_common import build_topic_bundle, fail_or_print, verify_topic_outputs, write_topic_bundle


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    if args.dry_run:
        bundle = build_topic_bundle(args.topic)
        issues = []
        if not bundle["topic"].get("summary"):
            issues.append("dry-run topic summary is empty")
    else:
        issues = verify_topic_outputs(args.topic)
    return fail_or_print(issues, {"status": "passed", "topic": args.topic, "dry_run": args.dry_run})


if __name__ == "__main__":
    raise SystemExit(main())
