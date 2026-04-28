#!/usr/bin/env python3
"""Verify researcher lens output."""

from __future__ import annotations

from pathlib import Path

from workbench_common import REPO_ROOT, fail_or_print, read_yaml, topic_dir


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    issues: list[str] = []
    path = topic_dir(args.topic) / "researcher_lens.yaml"
    if args.dry_run:
        issues = []
    elif not path.exists():
        issues.append(f"missing {path.relative_to(REPO_ROOT)}")
    else:
        lens = read_yaml(path)
        for field in ["executive_layer", "research_layer", "audit_layer", "human_attention_refs", "explanation_card_refs"]:
            if not lens.get(field):
                issues.append(f"researcher_lens missing {field}")
    return fail_or_print(issues, {"status": "passed", "topic": args.topic, "dry_run": args.dry_run})


if __name__ == "__main__":
    raise SystemExit(main())
