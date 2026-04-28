#!/usr/bin/env python3
"""Compile active human objects into routing constraints."""

from __future__ import annotations

import json

from workbench_common import build_agent_response, compile_constraints


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    constraints = compile_constraints(args.topic, dry_run=args.dry_run)
    response = None
    if constraints:
        response = build_agent_response(
            args.topic,
            constraints[0]["source_human_object_ref"],
            [item["object_id"] for item in constraints],
            dry_run=args.dry_run,
        )
    print(json.dumps({"status": "compiled", "topic": args.topic, "constraint_refs": [item["object_id"] for item in constraints], "agent_response_ref": response["object_id"] if response else None, "dry_run": args.dry_run}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
