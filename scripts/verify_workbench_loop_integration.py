#!/usr/bin/env python3
"""Verify that workbench human decisions can affect next-loop context."""

from __future__ import annotations

from apply_workbench_constraints_to_loop import build_context, build_skill_worker_context
from workbench_common import fail_or_print, topic_dir


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    context = build_context(args.topic, allow_dry_run_fallback=args.dry_run)
    worker_context = build_skill_worker_context(args.topic, allow_dry_run_fallback=args.dry_run)
    issues: list[str] = []
    if not context["active_routing_constraint_refs"]:
        issues.append("no active routing constraints available for loop integration")
    if not all(item.get("source_human_object_ref") for item in context["constraint_summaries"]):
        issues.append("at least one constraint lacks source_human_object_ref")
    if not args.dry_run and not (topic_dir(args.topic) / "loop_context.json").exists():
        issues.append("loop_context.json has not been written")
    if worker_context.get("target_worker") != "skill_worker":
        issues.append("skill_worker_context does not target skill_worker")
    if not worker_context.get("active_routing_constraint_refs"):
        issues.append("skill_worker_context has no active routing constraints")
    if not args.dry_run and not (topic_dir(args.topic) / "skill_worker_context.json").exists():
        issues.append("skill_worker_context.json has not been written")
    return fail_or_print(
        issues,
        {
            "status": "passed",
            "topic": args.topic,
            "constraint_count": len(context["active_routing_constraint_refs"]),
            "skill_worker_constraint_count": len(worker_context["active_routing_constraint_refs"]),
            "dry_run": args.dry_run,
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
