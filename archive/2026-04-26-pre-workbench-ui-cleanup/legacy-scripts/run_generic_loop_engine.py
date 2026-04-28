#!/usr/bin/env python3
"""Run the minimal generic loop engine skeleton."""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from worker_chain_helpers import (
    WorkerChainContext,
    rel,
    load_yaml,
    verify_worker_chain_root,
    write_cognition_diagnosis,
    write_cognition_to_skill_update,
    write_diagnosis_input,
    write_effectiveness_assessment,
    write_json,
    write_loop_review,
    write_loop_routing_decision,
    write_skill_change_request,
    write_skill_change_result,
    write_yaml,
)
from generic_diagnosis_layer import (
    build_diagnosis_input,
    derive_routing_decision_fields,
    validate_worker_output,
)
from backend_registry import backend_worker_module_path, require_backend_runnable, resolve_backend


REPO_ROOT = Path(__file__).resolve().parents[1]
STANDARD_PHASES = [
    "skill_change_request",
    "skill_execution",
    "effectiveness_assessment",
    "cognition_diagnosis",
    "loop_routing_decision",
]
DEFAULT_WORKSPACE_ROOT = REPO_ROOT / "analysis" / "full_loop_validation" / "runs"


@dataclass
class PhaseResult:
    artifact_path: Path
    payload: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_task_ref(task_ref: str) -> tuple[str, str]:
    parts = task_ref.split(".")
    if len(parts) < 3 or parts[0] != "task":
        raise RuntimeError(f"invalid task_ref for generic loop engine: {task_ref}")
    return parts[1], parts[2]


def slugify(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def load_python_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load worker module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenericLoopEngine:
    def __init__(
        self,
        *,
        task_adapter_path: Path,
        workspace_root: Path,
        run_intent: str,
        loop_config: dict[str, Any],
        verifier_config: dict[str, Any],
        backend: str,
        backend_config: dict[str, Any],
        worker_module_override: Path | None = None,
    ) -> None:
        self.task_adapter_path = task_adapter_path
        self.adapter = load_yaml(task_adapter_path)
        self.workspace_root = workspace_root
        self.run_intent = run_intent
        self.loop_config = loop_config
        self.verifier_config = verifier_config
        self.backend = backend
        self.backend_config = backend_config
        self.worker_module_override = worker_module_override
        self.domain, self.problem_name = parse_task_ref(self.adapter["task_ref"])
        self.worker_module_path = self.resolve_worker_module_path()
        self.worker_module = load_python_module(self.worker_module_path)
        self.ctx = WorkerChainContext(
            repo_root=REPO_ROOT,
            output_root=self.workspace_root / "artifacts",
            domain=self.domain,
            problem_name=self.problem_name,
            task_ref=self.adapter["task_ref"],
            task_package=self.adapter.get("metadata", {}).get("task_package", self.problem_name),
        )
        self.run_record_path = self.workspace_root / "run.yaml"
        self.phase_transition_root = self.workspace_root / "phase_transitions"
        self.review_root = self.workspace_root / "review"
        self.artifact_index_path = self.workspace_root / "artifact_index.json"
        self.phase_results: dict[str, PhaseResult] = {}
        self.phase_sequence = 0
        self.iteration_index = int(self.adapter.get("experimental", {}).get("iteration_index", 1))

    def resolve_worker_module_path(self) -> Path:
        if self.worker_module_override is not None:
            path = self.worker_module_override
            return path if path.is_absolute() else REPO_ROOT / path
        if self.backend_config:
            return backend_worker_module_path(self.backend_config)
        experimental = self.adapter.get("experimental", {})
        module_path = experimental.get("worker_module")
        if not module_path:
            raise RuntimeError("generic loop engine requires adapter.experimental.worker_module in Phase 3")
        path = Path(module_path)
        return path if path.is_absolute() else REPO_ROOT / path

    def initialize_workspace(self) -> None:
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        for generated_dir in ["artifacts", "phase_transitions", "review"]:
            path = self.workspace_root / generated_dir
            if path.exists():
                shutil.rmtree(path)
        for generated_file in ["run.yaml", "artifact_index.json"]:
            path = self.workspace_root / generated_file
            if path.exists():
                path.unlink()
        self.phase_transition_root.mkdir(parents=True, exist_ok=True)
        self.review_root.mkdir(parents=True, exist_ok=True)
        self.write_run_record(status="running", verification={"status": "not_run"})

    def write_run_record(self, *, status: str, verification: dict[str, Any]) -> None:
        payload = {
            "schema_version": "0.1.0",
            "object_type": "run",
            "object_id": f"run.{self.domain}.{self.problem_name}.{self.workspace_root.name}",
            "object_version": "0.1.0",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "status": status,
            "metadata": {
                "engine": "generic_loop_engine_skeleton",
                "run_intent": self.run_intent,
                "backend": self.backend,
            },
            "task_ref": self.adapter["task_ref"],
            "task_adapter_ref": self.adapter["object_id"],
            "workspace_root": rel(REPO_ROOT, self.workspace_root),
            "loop_config": self.loop_config,
            "verifier_config": self.verifier_config,
            "phase_statuses": {
                phase: {
                    "completed": phase in self.phase_results,
                    "artifact_ref": self.phase_results[phase].payload["object_id"] if phase in self.phase_results else None,
                }
                for phase in STANDARD_PHASES
            },
            "review_ref": self.phase_results["loop_review"].payload["object_id"] if "loop_review" in self.phase_results else None,
            "verification": verification,
        }
        write_yaml(self.run_record_path, payload)

    def write_phase_transition(self, *, phase: str, status: str, output_ref: str | None = None) -> None:
        self.phase_sequence += 1
        payload = {
            "phase": phase,
            "sequence": self.phase_sequence,
            "status": status,
            "timestamp": utc_now(),
            "task_ref": self.adapter["task_ref"],
            "task_adapter_ref": self.adapter["object_id"],
            "output_ref": output_ref,
        }
        write_yaml(self.phase_transition_root / f"{self.phase_sequence:02d}_{phase}.yaml", payload)

    def write_artifact_index(self) -> None:
        payload = {
            "task_ref": self.adapter["task_ref"],
            "task_adapter_ref": self.adapter["object_id"],
            "workspace_root": rel(REPO_ROOT, self.workspace_root),
            "artifacts": {
                phase: {
                    "object_id": result.payload["object_id"],
                    "path": rel(REPO_ROOT, result.artifact_path),
                }
                for phase, result in self.phase_results.items()
            },
        }
        write_json(self.artifact_index_path, payload)

    def worker_inputs(self, phase: str) -> dict[str, Any]:
        inputs = {
            "task_adapter": self.adapter,
            "run_intent": self.run_intent,
            "workspace_root": rel(REPO_ROOT, self.workspace_root),
            "loop_config": self.loop_config,
            "backend_config": self.backend_config,
            "prior_artifacts": {name: result.payload for name, result in self.phase_results.items()},
            "prior_paths": {name: rel(REPO_ROOT, result.artifact_path) for name, result in self.phase_results.items()},
        }
        if phase == "cognition_diagnosis":
            chain_issues = verify_worker_chain_root(
                self.ctx.output_root,
                iterations=self.iteration_index,
                require_supporting=False,
            )
            inputs["diagnosis_input"] = build_diagnosis_input(
                task_adapter=self.adapter,
                skill_change_request=self.phase_results.get("skill_change_request").payload
                if self.phase_results.get("skill_change_request")
                else None,
                skill_change_result=self.phase_results.get("skill_execution").payload
                if self.phase_results.get("skill_execution")
                else None,
                effectiveness_assessment=self.phase_results.get("effectiveness_assessment").payload
                if self.phase_results.get("effectiveness_assessment")
                else None,
                chain_verification_issues=[
                    issue
                    for issue in chain_issues
                    if "missing required object cognition_diagnosis" not in issue
                    and "missing required object loop_routing_decision" not in issue
                ],
            )
        return inputs

    def call_worker(self, phase: str) -> dict[str, Any]:
        worker_name = f"{phase}_worker"
        worker: Callable[[dict[str, Any]], dict[str, Any]] | None = getattr(self.worker_module, worker_name, None)
        if worker is None:
            raise RuntimeError(f"missing worker function {worker_name} in {self.worker_module_path}")
        output = worker(self.worker_inputs(phase))
        if not isinstance(output, dict):
            raise RuntimeError(f"{worker_name} must return a dict")
        return output

    def run_skill_change_request(self) -> None:
        self.write_phase_transition(phase="skill_change_request", status="started")
        output = self.call_worker("skill_change_request")
        path, payload = write_skill_change_request(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata=output["metadata"],
            iteration_index=self.iteration_index,
            base_skill_ref=output["fields"]["base_skill_ref"],
            allowed_change_scope=output["fields"]["allowed_change_scope"],
            blocked_paths=output["fields"]["blocked_paths"],
            required_tests=output["fields"]["required_tests"],
            output_skill_path=output["fields"]["output_skill_path"],
            summary=output["fields"]["summary"],
        )
        self.phase_results["skill_change_request"] = PhaseResult(path, payload)
        self.write_phase_transition(phase="skill_change_request", status="completed", output_ref=payload["object_id"])

    def run_skill_execution(self) -> None:
        self.write_phase_transition(phase="skill_execution", status="started")
        output = self.call_worker("skill_execution")
        request = self.phase_results["skill_change_request"].payload
        path, payload = write_skill_change_result(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata=output["metadata"],
            request_ref=request["object_id"],
            produced_skill_ref=output["fields"]["produced_skill_ref"],
            code_paths=output["fields"]["code_paths"],
            change_summary=output["fields"]["change_summary"],
            expected_behavior_change=output["fields"]["expected_behavior_change"],
            command=output["fields"]["command"],
            raw_output_path=output["fields"]["raw_output_path"],
            self_reported_risks=output["fields"]["self_reported_risks"],
            run_ref=output["fields"]["run_ref"],
        )
        self.phase_results["skill_execution"] = PhaseResult(path, payload)
        self.write_phase_transition(phase="skill_execution", status="completed", output_ref=payload["object_id"])

    def run_effectiveness_assessment(self) -> None:
        self.write_phase_transition(phase="effectiveness_assessment", status="started")
        output = self.call_worker("effectiveness_assessment")
        result = self.phase_results["skill_execution"].payload
        path, payload = write_effectiveness_assessment(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata=output["metadata"],
            result_ref=result["object_id"],
            baseline_ref=output["fields"]["baseline_ref"],
            evaluator_ref=output["fields"]["evaluator_ref"],
            run_ref=output["fields"]["run_ref"],
            run_passed=output["fields"]["run_passed"],
            metric_summary=output["fields"]["metric_summary"],
            comparison_summary=output["fields"]["comparison_summary"],
            judgment_summary=output["fields"]["judgment_summary"],
            recommended_cognition_action=output["fields"]["recommended_cognition_action"],
        )
        self.phase_results["effectiveness_assessment"] = PhaseResult(path, payload)
        self.write_phase_transition(
            phase="effectiveness_assessment", status="completed", output_ref=payload["object_id"]
        )

    def run_cognition_diagnosis(self) -> None:
        self.write_phase_transition(phase="cognition_diagnosis", status="started")
        diagnosis_input = self.worker_inputs("cognition_diagnosis")["diagnosis_input"]
        input_path, input_payload = write_diagnosis_input(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata={"task_package": self.ctx.task_package, "worker": "diagnosis_substrate"},
            fields=diagnosis_input,
        )
        self.phase_results["diagnosis_input"] = PhaseResult(input_path, input_payload)
        output = self.call_worker("cognition_diagnosis")
        validation_issues = validate_worker_output(output, diagnosis_input)
        if validation_issues:
            raise RuntimeError("invalid cognition_diagnosis_worker output: " + "; ".join(validation_issues))
        request = self.phase_results["skill_change_request"].payload
        result = self.phase_results["skill_execution"].payload
        assessment = self.phase_results["effectiveness_assessment"].payload
        path, payload = write_cognition_diagnosis(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata=output["metadata"],
            problem_class=output["fields"]["problem_class"],
            judgment_summary=output["fields"]["judgment_summary"],
            evidence_refs=[request["object_id"], result["object_id"], assessment["object_id"]],
            boundary_notes=output["fields"]["boundary_notes"],
            uncertainty_notes=output["fields"]["uncertainty_notes"],
            recommended_next_worker=output["fields"]["recommended_next_worker"],
            recommended_action=output["fields"]["recommended_action"],
            continue_loop=output["fields"]["continue_loop"],
        )
        self.phase_results["cognition_diagnosis"] = PhaseResult(path, payload)
        update_fields = output.get("cognition_to_skill_update")
        if update_fields:
            update_path, update_payload = write_cognition_to_skill_update(
                ctx=self.ctx,
                iteration=self.iteration_index,
                metadata=update_fields["metadata"],
                source_cognition_ref=payload["object_id"],
                source_event_ref=payload["object_id"],
                next_iteration_skill_constraints=update_fields["fields"]["next_iteration_skill_constraints"],
                next_iteration_evaluator_constraints=update_fields["fields"]["next_iteration_evaluator_constraints"],
                next_iteration_task_refinements=update_fields["fields"]["next_iteration_task_refinements"],
                search_priority_updates=update_fields["fields"]["search_priority_updates"],
                required_discriminating_tests=update_fields["fields"]["required_discriminating_tests"],
                summary=update_fields["fields"]["summary"],
            )
            self.phase_results["cognition_to_skill_update"] = PhaseResult(update_path, update_payload)
        self.write_phase_transition(phase="cognition_diagnosis", status="completed", output_ref=payload["object_id"])

    def run_loop_routing_decision(self) -> None:
        self.write_phase_transition(phase="loop_routing_decision", status="started")
        diagnosis = self.phase_results["cognition_diagnosis"].payload
        routing_fields = derive_routing_decision_fields(diagnosis)
        request = self.phase_results["skill_change_request"].payload
        result = self.phase_results["skill_execution"].payload
        assessment = self.phase_results["effectiveness_assessment"].payload
        path, payload = write_loop_routing_decision(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata={"task_package": self.ctx.task_package, "controller_mode": "non_authoring"},
            diagnosis_ref=diagnosis["object_id"],
            evidence_refs=[
                request["object_id"],
                result["object_id"],
                assessment["object_id"],
                diagnosis["object_id"],
            ],
            selected_next_worker=routing_fields["selected_next_worker"],
            selected_action=routing_fields["selected_action"],
            continue_loop=routing_fields["continue_loop"],
            policy_basis=routing_fields["policy_basis"],
            summary="Controller routes from diagnosis output without authoring worker judgments.",
        )
        self.phase_results["loop_routing_decision"] = PhaseResult(path, payload)
        self.write_phase_transition(
            phase="loop_routing_decision", status="completed", output_ref=payload["object_id"]
        )

    def write_loop_review(self) -> None:
        assessment = self.phase_results["effectiveness_assessment"].payload
        routing = self.phase_results["loop_routing_decision"].payload
        update = self.phase_results.get("cognition_to_skill_update")
        require_loop_review = bool(self.adapter.get("experimental", {}).get("require_loop_review", True))
        if update is None and require_loop_review:
            raise RuntimeError("generic loop engine expects cognition_to_skill_update for Phase 3 review output")
        if update is None:
            return
        review_path, review_payload = write_loop_review(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata={"task_package": self.ctx.task_package, "review_mode": "generic_loop_engine_skeleton"},
            event_ref=assessment["object_id"],
            controller_update_ref=update.payload["object_id"],
            iteration_plan_ref=self.phase_results["skill_change_request"].payload["object_id"],
            routing_decision_ref=routing["object_id"],
            search_space_reduction="Phase skeleton preserved a fixed five-phase flow and captured a complete artifact chain.",
            failure_explanation_improvement="The engine separated worker judgment from controller routing.",
            evaluator_refinement="The skeleton kept evaluator output as a dedicated effectiveness artifact.",
            claim_tightening="The skeleton records only bounded routing and review summaries.",
            verdict="substantiated",
            summary="The generic loop engine skeleton completed the standard phases and persisted the review artifact.",
        )
        self.phase_results["loop_review"] = PhaseResult(review_path, review_payload)

    def verify(self) -> dict[str, Any]:
        issues = verify_worker_chain_root(self.ctx.output_root, iterations=self.iteration_index, require_supporting=True)
        return {"status": "passed" if not issues else "failed", "issues": issues}

    def run(self) -> int:
        self.initialize_workspace()
        self.run_skill_change_request()
        self.run_skill_execution()
        self.run_effectiveness_assessment()
        self.run_cognition_diagnosis()
        self.run_loop_routing_decision()
        self.write_loop_review()
        self.write_artifact_index()
        verification = self.verify() if self.verifier_config.get("verify_worker_chain", True) else {"status": "skipped"}
        final_status = "completed" if verification.get("status") == "passed" else "failed_experiment"
        self.write_run_record(status=final_status, verification=verification)
        if verification.get("status") != "passed":
            for issue in verification.get("issues", []):
                print(issue)
            return 1
        print(f"Generic loop engine run completed at {rel(REPO_ROOT, self.workspace_root)}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the minimal generic loop engine skeleton.")
    parser.add_argument("--task-adapter", type=Path, required=True)
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--run-intent", default="candidate_run")
    parser.add_argument("--backend", default="deterministic")
    parser.add_argument("--backend-registry", type=Path)
    parser.add_argument(
        "--worker-module",
        type=Path,
        help="Optional generic worker module override for backend-specific harness tests.",
    )
    parser.add_argument("--loop-config", type=Path)
    parser.add_argument("--verifier-config", type=Path)
    args = parser.parse_args()

    loop_config = load_yaml(args.loop_config) if args.loop_config else {"max_iterations": 1, "phases": STANDARD_PHASES}
    verifier_config = load_yaml(args.verifier_config) if args.verifier_config else {"verify_worker_chain": True}
    adapter = load_yaml(args.task_adapter)
    backend_config = resolve_backend(args.backend, args.backend_registry)
    if args.worker_module is None:
        require_backend_runnable(backend_config)
    workspace_root = args.workspace_root
    if workspace_root is None:
        task_slug = slugify(adapter.get("task_ref", args.task_adapter.stem).replace("task.", ""))
        workspace_root = DEFAULT_WORKSPACE_ROOT / args.backend / task_slug / "iter_0001"
    engine = GenericLoopEngine(
        task_adapter_path=args.task_adapter,
        workspace_root=workspace_root,
        run_intent=args.run_intent,
        loop_config=loop_config,
        verifier_config=verifier_config,
        backend=args.backend,
        backend_config=backend_config,
        worker_module_override=args.worker_module,
    )
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())
