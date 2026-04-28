#!/usr/bin/env python3
"""Build researcher-readable communication briefs."""

from __future__ import annotations

import json

from workbench_common import build_briefs, write_briefs


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    briefs = build_briefs(args.topic)
    if not args.dry_run:
        write_briefs(args.topic)
    print(json.dumps({"status": "built", "topic": args.topic, "brief_refs": [item["object_id"] for item in briefs.values()], "dry_run": args.dry_run}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
