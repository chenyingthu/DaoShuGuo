#!/usr/bin/env python3
"""Build the next skill-worker context from workbench evidence and constraints."""

from __future__ import annotations

import json

from apply_workbench_constraints_to_loop import build_skill_worker_context
from workbench_common import rel, topic_dir, write_json


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    context = build_skill_worker_context(args.topic, allow_dry_run_fallback=args.dry_run)
    output = topic_dir(args.topic) / "skill_worker_context.json"
    if not args.dry_run:
        write_json(output, context)
    print(
        json.dumps(
            {
                "status": context["status"],
                "topic": args.topic,
                "target_worker": context["target_worker"],
                "constraint_count": len(context["active_routing_constraint_refs"]),
                "path": rel(output),
                "dry_run": args.dry_run,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
