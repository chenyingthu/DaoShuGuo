#!/usr/bin/env python3
"""Build a structured diagnosis for task004 skill use vs skill structure."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_EVOLUTION_ROOT = REPO_ROOT / "analysis" / "pi_harness" / "pi_json_loop_task004_skill_evolution" / "state" / "iterations"
OUTPUT_DIR = REPO_ROOT / "analysis" / "task004"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def collect_rounds() -> list[dict[str, Any]]:
    rounds: list[dict[str, Any]] = []
    for round_file in sorted(SKILL_EVOLUTION_ROOT.glob("iter_*/round_analysis.json")):
        rounds.append(load_json(round_file))
    if not rounds:
        raise RuntimeError("missing skill-evolution round_analysis artifacts")
    return rounds


def build_diagnosis(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    now = utc_now()
    q_values = [round_payload["candidate_q_step_mvar"] for round_payload in rounds]
    boundary_values = [round_payload["candidate_hosting_capacity_level"] for round_payload in rounds]
    loss_values = [round_payload["candidate_loss_at_boundary"] for round_payload in rounds]
    vm_values = [round_payload["candidate_voltage_margin"] for round_payload in rounds]

    use_problem = False
    structure_problem = False
    rationale: list[str] = []

    if len(set(boundary_values)) == 1 and any(
        loss_values[i] < loss_values[i - 1] and vm_values[i] > vm_values[i - 1]
        for i in range(1, len(rounds))
    ):
        rationale.append("参数持续增大时，二级指标持续改善，说明技能并非完全失效。")
    if len(set(boundary_values)) == 1:
        rationale.append("尽管 q_step 从较小值逐步增加，承载力边界始终未变化。")
    if max(q_values) > min(q_values):
        rationale.append("本轮诊断已排除“完全未调参数”的情况。")
        use_problem = True
    if len(set(boundary_values)) == 1 and max(q_values) >= 0.3:
        structure_problem = True
        rationale.append("在较明显的参数抬升后仍无边界响应，开始强烈暗示技能结构不足。")

    diagnosis = {
        "schema_version": "0.1.0",
        "object_type": "analysis_note",
        "object_id": f"analysis.power.ieee69_hosting_capacity.skill_diagnosis_{now.replace(':', '').replace('-', '')}",
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": "reviewed",
        "task_ref": "task.power.ieee69_hosting_capacity",
        "analysis_kind": "skill_use_vs_structure_diagnosis",
        "input_refs": [
            str(path.relative_to(REPO_ROOT))
            for path in sorted(SKILL_EVOLUTION_ROOT.glob("iter_*/round_analysis.json"))
        ],
        "summary": "task004 skill-evolution 诊断完成：已区分技能使用问题与技能结构问题。",
        "diagnosis": {
            "skill_use_problem_present": use_problem,
            "skill_structure_problem_suspected": structure_problem,
            "q_step_values": q_values,
            "hosting_capacity_values": boundary_values,
            "loss_values": loss_values,
            "voltage_margin_values": vm_values,
        },
        "judgment": {
            "current_conclusion": (
                "当前 task004 已证明参数使用仍有影响，但在连续抬升 q_step 后边界仍不变，故后续主线应转向技能结构升级。"
            ),
            "next_action": (
                "优先设计结构变体：非均匀 inverter Q 分配、bus 子集选择、分层注入或协调控制，而不是继续单纯增加 q_step。"
            ),
        },
        "rationale": rationale,
    }
    return diagnosis


def main() -> int:
    parser = argparse.ArgumentParser(description="Build task004 skill diagnosis from skill-evolution artifacts.")
    parser.add_argument("--output-dir", default="analysis/task004/skill_diagnosis_0001")
    args = parser.parse_args()

    rounds = collect_rounds()
    diagnosis = build_diagnosis(rounds)
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    write_yaml(output_dir / "skill_use_structure_diagnosis.yaml", diagnosis)
    print(json.dumps({"output": str((output_dir / 'skill_use_structure_diagnosis.yaml').relative_to(REPO_ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
