#!/usr/bin/env python3
"""Build researcher lens for a workbench topic."""

from __future__ import annotations

import json

from workbench_common import build_topic_bundle, write_topic_bundle


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    bundle = build_topic_bundle(args.topic)
    if not args.dry_run:
        write_topic_bundle(bundle)
    print(json.dumps({"status": "built", "topic": args.topic, "researcher_lens_ref": bundle["researcher_lens"]["object_id"], "dry_run": args.dry_run}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
