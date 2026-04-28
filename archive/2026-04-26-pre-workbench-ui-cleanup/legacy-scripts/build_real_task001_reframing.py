#!/usr/bin/env python3
"""Build real-task-001 research-framing and cognition-reframing artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pi_runtime import run_pi_prompt, write_json

TASK_REF = "task.power.ieee69_hosting_capacity"
ROOT = REPO_ROOT / "analysis" / "real_task_001"
REFRAMING = ROOT / "reframing"
LITERATURE = ROOT / "literature"
RAW = ROOT / "llm_worker_raw" / "reframing"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def extract_json(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise RuntimeError("worker response did not contain a JSON object")


def assistant_text(events: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for block in message.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    return "\n".join(parts)


def object_payload(object_type: str, object_id: str, status: str, fields: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    payload = {
        "schema_version": "0.1.0",
        "object_type": object_type,
        "object_id": object_id,
        "object_version": "0.1.0",
        "created_at": now,
        "updated_at": now,
        "status": status,
        "metadata": {
            "real_task": "real-task-001",
            "protocol": "research-framing-learning-worker",
        },
    }
    payload.update(fields)
    return payload


def source_refs() -> list[str]:
    return [
        "method_card.power.hosting_capacity_pv_2017",
        "method_card.power.smart_inverter_hosting_2020",
        "method_card.power.hosting_capacity_method_review_2021",
        "method_card.power.smart_inverter_voltvar_2019",
        "method_card.power.der_reactive_support_2021",
        "method_card.power.single_point_operation_2019",
    ]


def build_evidence_pack() -> dict[str, Any]:
    round_refs: list[dict[str, Any]] = []
    for idx in range(1, 4):
        round_dir = ROOT / "rounds" / f"round_{idx:03d}"
        analysis = read_json(round_dir / "round_analysis.json")
        round_refs.append(
            {
                "round": idx,
                "run_ref": analysis["run_ref"],
                "action_id": analysis["action_id"],
                "primary_delta": analysis.get("delta_vs_baseline", {}).get("hosting_capacity_level"),
                "secondary_improved": analysis["secondary_improved"],
                "mismatch_probe": analysis["mismatch_probe"],
                "analysis_path": str((round_dir / "round_analysis.json").relative_to(REPO_ROOT)),
            }
        )
    return object_payload(
        "evidence_bundle",
        "evidence.power.real_task_001.reframing_input",
        "active",
        {
            "task_ref": TASK_REF,
            "evaluator_ref": "evaluator.power.ieee69_hosting_capacity.default",
            "run_refs": [item["run_ref"] for item in round_refs],
            "artifact_refs": [
                {"kind": "round_analysis", "path": item["analysis_path"]} for item in round_refs
            ]
            + [
                {"kind": "research_report", "path": "analysis/real_task_001/reports/real_task_research_report.md"},
                {"kind": "cognition_upgrade", "path": "analysis/real_task_001/reports/cognition_upgrade.yaml"},
                {"kind": "taste_assessment", "path": "analysis/real_task_001/delivery/taste_assessment.yaml"},
                {"kind": "delivery_readiness", "path": "analysis/real_task_001/delivery/delivery_readiness.yaml"},
            ],
            "claim_scope": {
                "supported_claims": [
                    "secondary operational-quality improvement was observed in bounded inverter-support scans",
                    "primary hosting-capacity boundary improvement was not observed",
                    "single-point mismatch evidence cannot replace boundary-scan evidence",
                ]
            },
            "skill_refs": [
                "skill.power.renewable_capacity_optimizer_task004",
                "skill.power.single_point_capacity_mismatch_task004",
            ],
            "cognition_refs": ["cognition_upgrade.power.real_task_001.0001"],
            "gaps": [
                "No boundary-triggering scan envelope in the first two rounds",
                "No non-uniform inverter allocation skill family was tested",
                "No explicit control-effort claim gate was included",
            ],
            "taste_assessment_ref": "taste.power.real_task_001.0001",
            "report_refs": ["report.power.real_task_001.technical_note_0001"],
            "round_summaries": round_refs,
        },
    )


def build_gap_summary() -> dict[str, Any]:
    return object_payload(
        "cognition_upgrade",
        "cognition_upgrade.power.real_task_001.gap_summary",
        "reviewed",
        {
            "task_ref": TASK_REF,
            "source_cognition_ref": "cognition_upgrade.power.real_task_001.0001",
            "decision": "retain",
            "rationale": (
                "real-task-001 established claim discipline but not research-framing agency: "
                "the loop blocked overclaim yet did not redesign the hosting-capacity problem, evaluator, or skill family."
            ),
            "claim_adjustment": "Treat the current state as claim-gate success and research-framing gap, not as skill improvement.",
            "evidence_strength": "medium",
        },
    )


def build_learning_need() -> dict[str, Any]:
    return object_payload(
        "learning_need",
        "learning_need.power.ieee69_hosting_capacity.reframing_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "source_review_ref": "evidence.power.real_task_001.reframing_input",
            "observation_type": "cognition_gap",
            "skill_dimension_focus": ["method", "process", "standard"],
            "learning_questions": [
                "Which hosting-capacity problem framings match task004 and which are out of scope?",
                "Which method family moves beyond uniform inverter-Q parameter tuning?",
                "Which metrics are needed to separate boundary improvement from operational-quality improvement?",
                "What evidence is required before a diaomu result can move toward zhuoshi?",
            ],
            "required_source_types": ["method_card", "paper_record", "paper_excerpt"],
            "exclusion_criteria": [
                "Do not treat secondary loss or voltage-margin improvement as hosting-capacity improvement.",
                "Do not use single-point operating evidence as boundary evidence.",
            ],
            "success_criteria": [
                "Produce problem, method, metric, claim, and experiment maps.",
                "Identify at least one structural skill family beyond q_step tuning.",
            ],
            "claim_boundary": [
                "Curated task004 source pack can support reframing and low/medium-confidence design, not literature-complete novelty claims.",
            ],
        },
    )


def build_learning_context(need: dict[str, Any]) -> dict[str, Any]:
    return object_payload(
        "learning_context_pack",
        "learning_context_pack.power.ieee69_hosting_capacity.reframing_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "learning_need_ref": need["object_id"],
            "source_refs": source_refs(),
            "source_summaries": [
                {
                    "source_ref": "method_card.power.hosting_capacity_pv_2017",
                    "relevance": "Static PV hosting capacity is framed as a boundary under explicit voltage constraints.",
                },
                {
                    "source_ref": "method_card.power.smart_inverter_hosting_2020",
                    "relevance": "Smart inverter control can condition the hosting-capacity boundary and must be stated as part of the claim.",
                },
                {
                    "source_ref": "method_card.power.hosting_capacity_method_review_2021",
                    "relevance": "Hosting-capacity results are not comparable unless scenario, constraints, control assumptions, and boundary definitions are preserved.",
                },
                {
                    "source_ref": "method_card.power.single_point_operation_2019",
                    "relevance": "Operating-point analysis is weaker evidence than boundary evaluation.",
                },
            ],
            "method_insights": [
                "Uniform inverter-Q support is a use condition, not a full method family by itself.",
                "A structural method attempt should change allocation logic, such as voltage-sensitivity allocation or boundary-neighborhood refinement.",
            ],
            "process_insights": [
                "The workflow should first trigger or bracket a boundary before claiming boundary movement.",
                "Negative-control and mismatch lanes should remain separate from candidate evidence.",
            ],
            "standard_insights": [
                "Primary hosting-capacity claims require boundary-level improvement, not only loss or voltage-margin improvement.",
                "Control effort and boundary stability are needed to prevent high-cost pseudo-progress.",
            ],
            "applicability_boundaries": [
                "Source pack is curated from existing task004 artifacts and seed literature objects.",
                "No full systematic literature review is claimed.",
                "Current task remains static single-snapshot hosting capacity.",
            ],
            "confidence": "medium",
            "gaps": [
                "No time-series or probabilistic hosting capacity evidence is included.",
                "No OPF-grade method is implemented in this pack.",
            ],
            "curator_notes": "This pack supports research reframing and structural upgrade design for real-task-001.",
        },
    )


def build_literature_maps(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    context_ref = context["object_id"]
    common = {"task_ref": TASK_REF, "learning_context_ref": context_ref}
    return {
        "problem_framing_map": object_payload(
            "research_framing_map",
            "research_framing_map.power.ieee69_hosting_capacity.0001",
            "ready",
            {
                **common,
                "framing_entries": [
                    {
                        "framing_id": "static_hc",
                        "description": "Static hosting capacity under explicit voltage constraints and a fixed snapshot.",
                        "relation_to_task004": "direct_match",
                        "source_refs": ["method_card.power.hosting_capacity_pv_2017"],
                        "claim_boundary": "Can support static scan-boundary claims only.",
                    },
                    {
                        "framing_id": "control_strategy_conditioned_hc",
                        "description": "Hosting capacity conditioned on inverter or Volt/VAR control strategy.",
                        "relation_to_task004": "target_reframe",
                        "source_refs": ["method_card.power.smart_inverter_hosting_2020"],
                        "claim_boundary": "Must name the control policy and compare against fixed baseline.",
                    },
                    {
                        "framing_id": "time_series_or_probabilistic_hc",
                        "description": "Hosting capacity across temporal or uncertainty scenarios.",
                        "relation_to_task004": "out_of_scope_current_round",
                        "source_refs": ["method_card.power.hosting_capacity_method_review_2021"],
                        "claim_boundary": "Cannot be claimed from task004 current snapshot evidence.",
                    },
                    {
                        "framing_id": "opf_search_hc",
                        "description": "Optimization/search-based boundary finding with control variables.",
                        "relation_to_task004": "future_extension",
                        "source_refs": ["method_card.power.hosting_capacity_method_review_2021"],
                        "claim_boundary": "Current upgrade may approximate this with simple structural search only.",
                    },
                ],
                "applicability_boundaries": ["single snapshot", "voltage-driven boundary", "control-strategy-conditioned claims"],
                "confidence": "medium",
                "gaps": ["No time-series/probabilistic evidence in current task package."],
            },
        ),
        "method_family_map": object_payload(
            "method_family_map",
            "method_family_map.power.ieee69_hosting_capacity.0001",
            "ready",
            {
                **common,
                "method_families": [
                    {
                        "family_id": "scale_scan",
                        "skill_dimension": "process",
                        "relation_to_task004": "existing baseline process",
                        "minimum_validation": "Report last feasible and first violation points.",
                    },
                    {
                        "family_id": "uniform_q_support",
                        "skill_dimension": "use_condition",
                        "relation_to_task004": "existing candidate",
                        "minimum_validation": "Must not be called structural unless allocation logic or standard changes.",
                    },
                    {
                        "family_id": "voltage_sensitivity_q_allocation",
                        "skill_dimension": "method",
                        "relation_to_task004": "recommended minimal structural candidate",
                        "minimum_validation": "Compare with uniform support at same total effort and same scan envelope.",
                    },
                    {
                        "family_id": "boundary_neighborhood_refinement",
                        "skill_dimension": "process",
                        "relation_to_task004": "recommended evaluator/process upgrade",
                        "minimum_validation": "Record first violation, boundary margin, and stability near transition.",
                    },
                    {
                        "family_id": "control_effort_limited_search",
                        "skill_dimension": "standard",
                        "relation_to_task004": "future extension",
                        "minimum_validation": "Add effort budget and compare within fixed budget.",
                    },
                ],
                "applicability_boundaries": ["No complex OPF is implemented in this phase."],
                "confidence": "medium",
                "gaps": ["Sensitivity allocation still needs upgraded effectiveness evidence."],
            },
        ),
        "metric_taxonomy": object_payload(
            "metric_taxonomy",
            "metric_taxonomy.power.ieee69_hosting_capacity.0001",
            "ready",
            {
                **common,
                "metric_entries": [
                    {
                        "metric_id": "hosting_capacity_level",
                        "role": "primary",
                        "supports_claims": ["hosting-capacity boundary movement"],
                        "unsupported_claims": ["loss reduction alone"],
                    },
                    {
                        "metric_id": "boundary_trigger_scale",
                        "role": "primary_support",
                        "supports_claims": ["boundary is actually bracketed"],
                        "unsupported_claims": ["paper novelty without method comparison"],
                    },
                    {
                        "metric_id": "loss_at_boundary",
                        "role": "secondary",
                        "supports_claims": ["operational-quality improvement"],
                        "unsupported_claims": ["hosting capacity improvement by itself"],
                    },
                    {
                        "metric_id": "control_effort",
                        "role": "cost_gate",
                        "supports_claims": ["improvement is not free or hidden-cost"],
                        "unsupported_claims": ["better skill if effort is unbounded"],
                    },
                ],
                "primary_metric_refs": ["hosting_capacity_level", "boundary_trigger_scale"],
                "secondary_metric_refs": ["loss_at_boundary", "voltage_margin", "control_effort", "scenario_robustness"],
                "claim_boundaries": [
                    "Secondary metric gains do not support primary hosting-capacity claims.",
                    "Boundary-trigger evidence is required before claiming boundary movement.",
                ],
                "confidence": "medium",
                "gaps": ["Thermal constraints and probabilistic robustness are not included."],
            },
        ),
        "claim_thresholds": object_payload(
            "claim_threshold_map",
            "claim_threshold_map.power.ieee69_hosting_capacity.0001",
            "ready",
            {
                **common,
                "thresholds": [
                    {
                        "claim_level": "diaomu_internal_report",
                        "required_evidence": ["real run", "baseline/candidate comparison", "claim boundary"],
                        "taste_ceiling": "diaomu",
                    },
                    {
                        "claim_level": "zhuoshi_candidate",
                        "required_evidence": [
                            "boundary-triggering scenario",
                            "structural method/process/standard change",
                            "same-evaluator baseline comparison",
                            "control-effort gate",
                            "literature-framed claim boundary",
                        ],
                        "taste_ceiling": "zhuoshi",
                    },
                ],
                "forbidden_claims": [
                    "Do not claim hosting-capacity improvement from loss or voltage-margin improvements alone.",
                    "Do not claim structural skill improvement from q_step increase alone.",
                    "Do not claim time-series or probabilistic hosting capacity from static snapshot evidence.",
                ],
                "confidence": "medium",
                "gaps": ["No multi-scenario robustness evidence yet."],
            },
        ),
        "experiment_design_recommendation": object_payload(
            "experiment_design_recommendation",
            "experiment_design_recommendation.power.ieee69_hosting_capacity.0001",
            "ready",
            {
                **common,
                "recommended_matrix": [
                    {
                        "factor": "scenario_envelope",
                        "levels": ["original_scan", "extended_until_violation"],
                        "purpose": "Ensure the boundary is bracketed rather than assumed at scan limit.",
                    },
                    {
                        "factor": "control_strategy",
                        "levels": ["fixed_q_baseline", "uniform_q_support", "voltage_sensitivity_q_allocation"],
                        "purpose": "Separate usage tuning from structural allocation logic.",
                    },
                    {
                        "factor": "standard",
                        "levels": ["primary_boundary", "secondary_quality", "control_effort"],
                        "purpose": "Prevent secondary metric overclaim and hidden-cost improvement.",
                    },
                ],
                "minimum_zhuoshi_evidence": [
                    "A boundary-triggering scan exists.",
                    "A non-uniform allocation candidate is compared with uniform support under comparable effort.",
                    "Primary/secondary/cost metrics are all reported.",
                    "Claim remains static and control-strategy-conditioned.",
                ],
                "excluded_shortcuts": ["q_step-only escalation", "lowering voltage standards", "single-point mismatch as boundary evidence"],
                "confidence": "medium",
                "gaps": ["This is still not a time-series or probabilistic HC design."],
            },
        ),
    }


def ask_cognition_worker(context: dict[str, Any], provider: str, model: str, thinking: str) -> dict[str, Any]:
    RAW.mkdir(parents=True, exist_ok=True)
    required_shape = {
        "diagnosis_class": "one of potential_method_improvement, potential_process_improvement, potential_standard_improvement, insufficient_learning_evidence",
        "method_diagnosis": "short string",
        "process_diagnosis": "short string",
        "standard_diagnosis": "short string",
        "skill_use_vs_structure_judgment": "short string",
        "reusable_principle_candidates": ["string"],
        "unresolved_uncertainty": ["string"],
        "claim_boundary": ["string"],
        "research_framing_upgrade": "short string",
        "evaluator_upgrade_request": ["string"],
        "skill_family_upgrade_request": ["string"],
        "scenario_upgrade_request": ["string"],
        "zhuoshi_threshold": ["string"],
    }
    prompt = f"""
You are DaoShuGuo's cognition_reframing_worker.

Return exactly one JSON object. Do not include Markdown.
You are not the controller. Make research judgments only from the evidence and learning maps.
Do not claim verified structural improvement. The current stage is diagnosis and change-request design.

Context:
{json.dumps(context, ensure_ascii=False, indent=2)}

Required JSON shape:
{json.dumps(required_shape, ensure_ascii=False, indent=2)}
""".strip()
    last_error = "not run"
    for attempt in range(1, 3):
        result = run_pi_prompt(prompt, RAW, provider=provider, model=model, thinking=thinking)
        write_json(
            RAW / f"cognition_reframing_worker_attempt_{attempt}.json",
            {
                "attempt": attempt,
                "provider": provider,
                "model": model,
                "thinking": thinking,
                "exit_code": result["exit_code"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            },
        )
        if result["exit_code"] != 0:
            last_error = result["stderr"]
            continue
        try:
            payload = extract_json(assistant_text(result["events"]) or result["stdout"])
        except RuntimeError as exc:
            last_error = str(exc)
            prompt = "Return only one valid JSON object matching the required shape. No prose."
            continue
        if str(payload.get("diagnosis_class")) not in {
            "potential_method_improvement",
            "potential_process_improvement",
            "potential_standard_improvement",
            "insufficient_learning_evidence",
        }:
            last_error = "invalid diagnosis_class"
            prompt = "Return corrected JSON. diagnosis_class must use the allowed enum values in the required shape."
            continue
        return payload
    raise RuntimeError(f"cognition_reframing_worker failed: {last_error}")


def build_reframing_objects(worker: dict[str, Any], context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    learning_ref = context["learning_context_pack"]["object_id"]
    diagnosis = object_payload(
        "skill_structure_diagnosis",
        "skill_structure_diagnosis.power.ieee69_hosting_capacity.reframing_0001",
        "reviewed",
        {
            "task_ref": TASK_REF,
            "learning_context_ref": learning_ref,
            "source_review_ref": "evidence.power.real_task_001.reframing_input",
            "diagnosis_class": worker["diagnosis_class"],
            "method_diagnosis": worker["method_diagnosis"],
            "process_diagnosis": worker["process_diagnosis"],
            "standard_diagnosis": worker["standard_diagnosis"],
            "skill_use_vs_structure_judgment": worker["skill_use_vs_structure_judgment"],
            "reusable_principle_candidates": worker.get("reusable_principle_candidates", []),
            "unresolved_uncertainty": worker.get("unresolved_uncertainty", []),
            "claim_boundary": worker.get("claim_boundary", []),
        },
    )
    structural_request = object_payload(
        "structural_skill_change_request",
        "structural_skill_change_request.power.ieee69_hosting_capacity.reframing_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "diagnosis_ref": diagnosis["object_id"],
            "target_skill_ref": "skill.power.renewable_capacity_optimizer_task004",
            "change_type": "mixed_structural_change",
            "method_changes": worker.get("skill_family_upgrade_request", []),
            "process_changes": worker.get("scenario_upgrade_request", []),
            "standard_changes": worker.get("evaluator_upgrade_request", []),
            "forbidden_usage_only_shortcuts": ["q_step-only escalation", "single-point evidence as boundary evidence"],
            "required_validation": worker.get("zhuoshi_threshold", []),
            "claim_boundary": worker.get("claim_boundary", []),
        },
    )
    framing_upgrade = object_payload(
        "cognition_upgrade",
        "cognition_upgrade.power.ieee69_hosting_capacity.reframing_0001",
        "reviewed",
        {
            "task_ref": TASK_REF,
            "source_cognition_ref": "cognition_upgrade.power.real_task_001.0001",
            "decision": "upgrade",
            "rationale": worker.get("research_framing_upgrade", ""),
            "evidence_strength": "medium",
            "claim_adjustment": "Upgrade the research frame, not the result claim: the current outcome remains diaomu until upgraded evidence passes.",
        },
    )
    evaluator_request = object_payload(
        "structural_skill_change_request",
        "structural_skill_change_request.power.ieee69_hosting_capacity.evaluator_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "diagnosis_ref": diagnosis["object_id"],
            "target_skill_ref": "evaluator.power.ieee69_hosting_capacity.default",
            "change_type": "standard_change",
            "method_changes": [],
            "process_changes": [],
            "standard_changes": worker.get("evaluator_upgrade_request", []),
            "forbidden_usage_only_shortcuts": ["Changing evaluator to lower the bar"],
            "required_validation": ["Report primary, secondary, boundary-trigger, and control-effort fields."],
            "claim_boundary": ["Evaluator upgrade cannot by itself prove skill improvement."],
        },
    )
    scenario_request = object_payload(
        "structural_skill_change_request",
        "structural_skill_change_request.power.ieee69_hosting_capacity.scenario_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "diagnosis_ref": diagnosis["object_id"],
            "target_skill_ref": "task.power.ieee69_hosting_capacity",
            "change_type": "process_change",
            "method_changes": [],
            "process_changes": worker.get("scenario_upgrade_request", []),
            "standard_changes": [],
            "forbidden_usage_only_shortcuts": ["Lowering voltage constraints to manufacture improvement"],
            "required_validation": ["Run an extended scan envelope and preserve original claim boundary."],
            "claim_boundary": ["Scenario stress is a test condition, not a lowered standard."],
        },
    )
    zhuoshi = object_payload(
        "claim_threshold_map",
        "claim_threshold_map.power.ieee69_hosting_capacity.zhuoshi_0001",
        "ready",
        {
            "task_ref": TASK_REF,
            "learning_context_ref": learning_ref,
            "thresholds": [
                {
                    "claim_level": "zhuoshi",
                    "required_evidence": worker.get("zhuoshi_threshold", []),
                    "taste_ceiling": "zhuoshi",
                }
            ],
            "forbidden_claims": [
                "Do not upgrade to zhuoshi without boundary-trigger and structural-change evidence.",
                "Do not treat secondary metric gain as hosting-capacity gain.",
            ],
            "confidence": "medium",
            "gaps": worker.get("unresolved_uncertainty", []),
        },
    )
    return {
        "skill_structure_diagnosis": diagnosis,
        "structural_skill_change_request": structural_request,
        "research_framing_upgrade": framing_upgrade,
        "evaluator_upgrade_request": evaluator_request,
        "scenario_upgrade_request": scenario_request,
        "zhuoshi_threshold": zhuoshi,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build real-task-001 reframing artifacts.")
    parser.add_argument("--provider", default="codex-relay")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--thinking", default="off")
    args = parser.parse_args()

    evidence = build_evidence_pack()
    gap = build_gap_summary()
    need = build_learning_need()
    context_pack = build_learning_context(need)
    maps = build_literature_maps(context_pack)
    worker_context = {
        "evidence_pack": evidence,
        "current_gap_summary": gap,
        "learning_context_pack": context_pack,
        "maps": maps,
    }
    worker = ask_cognition_worker(worker_context, args.provider, args.model, args.thinking)
    reframing_objects = build_reframing_objects(worker, worker_context)

    write_yaml(REFRAMING / "input_evidence_pack.yaml", evidence)
    write_yaml(REFRAMING / "current_gap_summary.yaml", gap)
    write_yaml(LITERATURE / "learning_need.yaml", need)
    write_yaml(LITERATURE / "learning_context_pack.yaml", context_pack)
    for filename, payload in maps.items():
        write_yaml(LITERATURE / f"{filename}.yaml", payload)
    write_yaml(LITERATURE / "next_skill_family_candidates.yaml", maps["method_family_map"])
    for filename, payload in reframing_objects.items():
        write_yaml(REFRAMING / f"{filename}.yaml", payload)
    write_json(RAW / "cognition_reframing_worker.final.json", worker)
    print(
        json.dumps(
            {
                "status": "passed",
                "evidence_pack": evidence["object_id"],
                "learning_context": context_pack["object_id"],
                "diagnosis": reframing_objects["skill_structure_diagnosis"]["object_id"],
                "structural_request": reframing_objects["structural_skill_change_request"]["object_id"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
