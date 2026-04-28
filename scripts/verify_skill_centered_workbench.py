#!/usr/bin/env python3
"""Verify skill-centered workbench outputs."""

from __future__ import annotations

from workbench_common import fail_or_print, read_json, topic_dir


def main() -> int:
    from workbench_common import cli_topic_arg

    args = cli_topic_arg().parse_args()
    root = topic_dir(args.topic)
    issues: list[str] = []

    skill_path = root / "skill_cockpit.json"
    judgment_path = root / "skill_judgment_card.json"
    attention_path = root / "human_attention_queue.json"
    if not skill_path.exists():
        issues.append("missing skill_cockpit.json")
    if not judgment_path.exists():
        issues.append("missing skill_judgment_card.json")
    if not attention_path.exists():
        issues.append("missing human_attention_queue.json")
    if issues:
        return fail_or_print(issues, {"status": "passed", "topic": args.topic})

    skill = read_json(skill_path)
    judgment = read_json(judgment_path)
    attention = read_json(attention_path)
    evidence = skill.get("metric_evidence", {})

    if args.topic == "real-task-001":
        if skill.get("active_skill_ref") != "skill.power.renewable_capacity_optimizer_task004":
            issues.append("active_skill_ref does not identify renewable_capacity_optimizer_task004")
        if skill.get("candidate_family") != "voltage_sensitivity_q_allocation":
            issues.append("candidate_family is not voltage_sensitivity_q_allocation")
        if skill.get("skill_status") == "verified_structural_improvement":
            issues.append("skill_status incorrectly claims verified structural improvement")
        if evidence.get("primary_delta") != 0.0:
            issues.append("primary_delta should remain 0.0 for current evidence")
        if evidence.get("boundary_triggered") is not False:
            issues.append("boundary_triggered should remain false for current evidence")
        forbidden = " ".join(skill.get("forbidden_claims", []) + judgment.get("forbidden_claims", []))
        if "verified structural skill improvement" not in forbidden:
            issues.append("forbidden_claims must reject verified structural skill improvement")
        if "hosting-capacity boundary improvement" not in forbidden:
            issues.append("forbidden_claims must reject hosting-capacity boundary improvement")
        if not any("skill direction" in item.get("question", "").lower() for item in attention):
            issues.append("human_attention_queue lacks a skill-direction question")

    return fail_or_print(
        issues,
        {
            "status": "passed",
            "topic": args.topic,
            "active_skill_ref": skill.get("active_skill_ref"),
            "candidate_family": skill.get("candidate_family"),
            "skill_status": skill.get("skill_status"),
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
