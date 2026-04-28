#!/usr/bin/env python3
"""Write or dry-run a default claim_approval object."""

from __future__ import annotations

import json

from workbench_common import default_human_object, rel, write_human_object


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    obj = default_human_object("claim_approval", args.topic)
    path = write_human_object(obj, dry_run=args.dry_run)
    print(json.dumps({"status": "dry_run" if args.dry_run else "written", "object_ref": obj["object_id"], "path": rel(path)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
