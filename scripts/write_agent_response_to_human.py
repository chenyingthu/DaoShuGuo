#!/usr/bin/env python3
"""Write or dry-run an agent_response_to_human object."""

from __future__ import annotations

import argparse
import json

from workbench_common import build_agent_response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--human-ref", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    human_ref = args.human_ref or f"human_review.{args.topic}.dry_run"
    obj = build_agent_response(args.topic, human_ref, [], dry_run=args.dry_run)
    print(json.dumps({"status": "dry_run" if args.dry_run else "written", "object_ref": obj["object_id"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
