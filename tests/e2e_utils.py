"""Shared helpers for harness end-to-end tests."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import json
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from agents.validation_agent import ValidationAgent, ValidationResult
from scripts.run_generic_loop_engine import GenericLoopEngine, STANDARD_PHASES as BASE_STANDARD_PHASES
from scripts.run_generic_loop_engine_with_harness import GenericLoopEngineWithHarness
from scripts.verify_research_quality import calculate_quality_score

FIXTURE_WORKER_MODULE = REPO_ROOT / "scripts" / "generic_loop_engine_fixture_workers.py"
DEFAULT_E2E_ROOT = REPO_ROOT / "runs" / "harness_e2e"
QUALITY_PHASES = [
    "skill_change_request",
    "skill_execution",
    "effectiveness_assessment",
    "cognition_diagnosis",
]


@dataclass(frozen=True)
class PhaseQuality:
    phase: str
    valid: bool
    score: float
    missing_fields: list[str]
    shallow_fields: list[str]
    content_errors: list[str]
    warnings: list[str]
    content_length: int


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to a mapping")
    return data


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def clean_run_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def task_adapter_path(task_id: str) -> Path:
    path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Task adapter not found: {path}")
    return path


def standard_loop_config() -> dict[str, Any]:
    return {"phases": list(BASE_STANDARD_PHASES), "review": {"enabled": True}}


def backend_config() -> dict[str, str]:
    return {"backend_id": "deterministic", "worker_module": str(FIXTURE_WORKER_MODULE.relative_to(REPO_ROOT))}


def run_engine_with_harness(task_id: str = "task007_fixture", run_name: str | None = None) -> Path:
    run_name = run_name or f"with_harness_{utc_stamp()}"
    run_dir = clean_run_dir(DEFAULT_E2E_ROOT / run_name)
    engine = GenericLoopEngineWithHarness(
        task_adapter_path=task_adapter_path(task_id),
        workspace_root=run_dir,
        run_intent=f"E2E harness run for {task_id}",
        loop_config=standard_loop_config(),
        verifier_config={"verify_worker_chain": True},
        backend="deterministic",
        backend_config=backend_config(),
        worker_module_override=FIXTURE_WORKER_MODULE,
        validation_enabled=True,
        strict_mode=True,
    )
    engine.run()
    return run_dir


def run_engine_without_harness(task_id: str = "task007_fixture", run_name: str | None = None) -> Path:
    run_name = run_name or f"without_harness_{utc_stamp()}"
    run_dir = clean_run_dir(DEFAULT_E2E_ROOT / run_name)
    engine = GenericLoopEngine(
        task_adapter_path=task_adapter_path(task_id),
        workspace_root=run_dir,
        run_intent=f"E2E baseline run for {task_id}",
        loop_config=standard_loop_config(),
        verifier_config={"verify_worker_chain": True},
        backend="deterministic",
        backend_config=backend_config(),
        worker_module_override=FIXTURE_WORKER_MODULE,
    )
    result = engine.run()
    if result != 0:
        raise RuntimeError(f"Baseline engine failed with exit code {result}")
    return run_dir


def _load_fixture_worker_module():
    spec = importlib.util.spec_from_file_location("generic_loop_engine_fixture_workers", FIXTURE_WORKER_MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load fixture worker module from {FIXTURE_WORKER_MODULE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def baseline_phase_outputs() -> dict[str, dict[str, Any]]:
    """Return raw no-harness fixture worker outputs for A/B quality scoring."""
    module = _load_fixture_worker_module()
    outputs: dict[str, dict[str, Any]] = {}
    inputs: dict[str, Any] = {"task_adapter": load_yaml(task_adapter_path("task007_fixture")), "prior_artifacts": {}}
    outputs["skill_change_request"] = module.skill_change_request_worker(inputs)
    inputs["prior_artifacts"]["skill_change_request"] = outputs["skill_change_request"]
    outputs["skill_execution"] = module.skill_execution_worker(inputs)
    inputs["prior_artifacts"]["skill_execution"] = outputs["skill_execution"]
    outputs["effectiveness_assessment"] = module.effectiveness_assessment_worker(inputs)
    inputs["prior_artifacts"]["effectiveness_assessment"] = outputs["effectiveness_assessment"]
    outputs["cognition_diagnosis"] = module.cognition_diagnosis_worker(inputs)
    return outputs


def harness_phase_outputs() -> dict[str, dict[str, Any]]:
    module = _load_fixture_worker_module()
    outputs: dict[str, dict[str, Any]] = {}
    inputs: dict[str, Any] = {
        "task_adapter": load_yaml(task_adapter_path("task007_fixture")),
        "prior_artifacts": {},
        "_harness_requirements": "test requirements",
        "_harness_phase_config": {"name": "skill_change_request"},
    }
    outputs["skill_change_request"] = module.skill_change_request_worker(inputs)
    inputs["prior_artifacts"]["skill_change_request"] = outputs["skill_change_request"]
    inputs["_harness_phase_config"] = {"name": "skill_execution"}
    outputs["skill_execution"] = module.skill_execution_worker(inputs)
    inputs["prior_artifacts"]["skill_execution"] = outputs["skill_execution"]
    inputs["_harness_phase_config"] = {"name": "effectiveness_assessment"}
    outputs["effectiveness_assessment"] = module.effectiveness_assessment_worker(inputs)
    inputs["prior_artifacts"]["effectiveness_assessment"] = outputs["effectiveness_assessment"]
    inputs["_harness_phase_config"] = {"name": "cognition_diagnosis"}
    outputs["cognition_diagnosis"] = module.cognition_diagnosis_worker(inputs)
    return outputs


def validation_agent() -> ValidationAgent:
    return ValidationAgent(
        schema_dir=str(REPO_ROOT / "schemas"),
        config_path=str(REPO_ROOT / "configs" / "phase_requirements.yaml"),
    )


def validate_phase_payload(payload: dict[str, Any], phase: str, agent: ValidationAgent | None = None) -> ValidationResult:
    agent = agent or validation_agent()
    return agent.validate_phase_output(payload, phase)


def quality_for_outputs(outputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    agent = validation_agent()
    phases: list[PhaseQuality] = []
    for phase in QUALITY_PHASES:
        result = validate_phase_payload(outputs[phase], phase, agent)
        phases.append(
            PhaseQuality(
                phase=phase,
                valid=result.valid,
                score=calculate_quality_score(result),
                missing_fields=list(result.missing_fields),
                shallow_fields=list(result.shallow_fields),
                content_errors=list(result.content_errors),
                warnings=list(result.warnings),
                content_length=result.content_length,
            )
        )
    return summarize_phase_quality(phases)


def summarize_phase_quality(phases: list[PhaseQuality]) -> dict[str, Any]:
    total_required = 0
    missing_count = 0
    agent = validation_agent()
    for phase_quality in phases:
        required = agent.phase_requirements.get(phase_quality.phase, {}).get("must_include", [])
        total_required += len(required)
        missing_count += len(phase_quality.missing_fields)
    average_score = sum(item.score for item in phases) / len(phases) if phases else 0.0
    required_coverage = 100.0 if total_required == 0 else ((total_required - missing_count) / total_required) * 100
    return {
        "average_score": round(average_score, 1),
        "required_coverage": round(required_coverage, 1),
        "total_missing_fields": missing_count,
        "total_shallow_fields": sum(len(item.shallow_fields) for item in phases),
        "total_content_errors": sum(len(item.content_errors) for item in phases),
        "phase_results": [item.__dict__ for item in phases],
    }


def calculate_quality_metrics(run_dir: Path) -> dict[str, Any]:
    artifact_index = load_yaml(run_dir / "artifact_index.json") if (run_dir / "artifact_index.json").exists() else None
    if artifact_index is None:
        raise FileNotFoundError(f"Missing artifact_index.json in {run_dir}")
    if artifact_index.get("harness_validation"):
        phases = [
            PhaseQuality(
                phase=phase,
                valid=payload["valid"],
                score=_score_from_validation_payload(payload),
                missing_fields=list(payload.get("missing_fields", [])),
                shallow_fields=list(payload.get("shallow_fields", [])),
                content_errors=list(payload.get("content_errors", [])),
                warnings=list(payload.get("warnings", [])),
                content_length=int(payload.get("content_length", 0)),
            )
            for phase, payload in sorted(artifact_index["harness_validation"].items())
            if phase in QUALITY_PHASES
        ]
        return summarize_phase_quality(phases)
    agent = validation_agent()
    phases: list[PhaseQuality] = []
    phase_to_artifact = {
        "skill_change_request": "skill_change_request",
        "skill_execution": "skill_execution",
        "effectiveness_assessment": "effectiveness_assessment",
        "cognition_diagnosis": "cognition_diagnosis",
    }
    for phase, artifact_name in phase_to_artifact.items():
        entry = artifact_index["artifacts"][artifact_name]
        payload = load_yaml(REPO_ROOT / entry["path"])
        result = validate_phase_payload(payload, phase, agent)
        phases.append(
            PhaseQuality(
                phase=phase,
                valid=result.valid,
                score=calculate_quality_score(result),
                missing_fields=list(result.missing_fields),
                shallow_fields=list(result.shallow_fields),
                content_errors=list(result.content_errors),
                warnings=list(result.warnings),
                content_length=result.content_length,
            )
        )
    return summarize_phase_quality(phases)


def _score_from_validation_payload(payload: dict[str, Any]) -> float:
    score = 100.0
    score -= len(payload.get("missing_fields", [])) * 10
    score -= len(payload.get("shallow_fields", [])) * 5
    score -= len(payload.get("content_errors", [])) * 15
    score -= len(payload.get("warnings", [])) * 2
    min_required_length = payload.get("min_required_length", 0)
    if min_required_length:
        length_ratio = min(payload.get("content_length", 0) / min_required_length, 2.0)
        score += (length_ratio - 1.0) * 10
    return max(0.0, min(100.0, score))


def generate_e2e_report(report_path: Path, baseline: dict[str, Any], experiment: dict[str, Any]) -> dict[str, Any]:
    improvement = 0.0
    if baseline["average_score"] > 0:
        improvement = ((experiment["average_score"] - baseline["average_score"]) / baseline["average_score"]) * 100
    report = {
        "schema_version": "0.1.0",
        "object_type": "harness_e2e_test_report",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "test_summary": {
            "baseline_average_score": baseline["average_score"],
            "harness_average_score": experiment["average_score"],
            "score_improvement_percent": round(improvement, 1),
            "harness_required_coverage": experiment["required_coverage"],
        },
        "quality_comparison": {
            "without_harness": baseline,
            "with_harness": experiment,
        },
        "conclusion": (
            "Harness quality gate improves deterministic fixture record completeness"
            if improvement >= 50 and experiment["required_coverage"] == 100.0
            else "Harness quality improvement did not meet the configured E2E threshold"
        ),
    }
    if report_path.suffix.lower() in {".yaml", ".yml"}:
        write_yaml(report_path, report)
    else:
        lines = [
            "# Harness E2E Test Report",
            "",
            f"- Baseline average score: {baseline['average_score']}",
            f"- Harness average score: {experiment['average_score']}",
            f"- Score improvement: {report['test_summary']['score_improvement_percent']}%",
            f"- Harness required coverage: {experiment['required_coverage']}%",
            "",
            report["conclusion"],
            "",
        ]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines), encoding="utf-8")
    return report
