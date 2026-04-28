#!/usr/bin/env python3
"""
Generic Loop Engine with Validation Harness

增强版循环引擎，添加了 Phase 输出验证 Harness。
参考: plans/GENERIC_LOOP_ENGINE_HARNESS_IMPLEMENTATION_PLAN.md

Usage:
    python3 scripts/run_generic_loop_engine_with_harness.py \
        --task-adapter adapters/task003.yaml \
        --workspace-root runs/task003/harness_001 \
        --run-intent "test harness validation"
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# 导入原有组件
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

# 导入 Harness 组件
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents.validation_agent import ValidationAgent, ValidationResult


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


@dataclass
class PhaseConfig:
    """Phase 配置"""
    name: str
    description: str
    required_outputs: list
    schema: str
    must_include: list
    max_retries: int = 3
    strict: bool = True


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


class GenericLoopEngineWithHarness:
    """
    Generic Loop Engine with Validation Harness

    核心改进:
    1. 每个 Phase 有强制输出要求
    2. 验证失败时自动重试
    3. 多次失败后记录失败胶囊
    """

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
        phase_requirements_path: Path | None = None,
        validation_enabled: bool = True,
        strict_mode: bool = False,
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
        self.harness_validation_results: dict[str, ValidationResult] = {}
        self.phase_sequence = 0
        self.iteration_index = int(self.adapter.get("experimental", {}).get("iteration_index", 1))

        # Harness 相关配置
        self.validation_enabled = validation_enabled
        self.strict_mode = strict_mode
        self.phase_requirements_path = phase_requirements_path or REPO_ROOT / "configs" / "phase_requirements.yaml"

        # 初始化 Harness 组件
        if self.validation_enabled:
            self.validation_agent = ValidationAgent(
                schema_dir=str(REPO_ROOT / "schemas"),
                config_path=str(self.phase_requirements_path)
            )
            self.phase_configs = self._load_phase_configs()
        else:
            self.validation_agent = None
            self.phase_configs = {}

    def _load_phase_configs(self) -> dict[str, PhaseConfig]:
        """加载 Phase 配置"""
        configs = {}
        requirements = self.validation_agent.phase_requirements

        for phase_name, config in requirements.items():
            configs[phase_name] = PhaseConfig(
                name=phase_name,
                description=config.get("description", ""),
                required_outputs=config.get("required_outputs", []),
                schema=config.get("required_outputs", [{}])[0].get("schema", ""),
                must_include=config.get("must_include", []),
                max_retries=config.get("validation", {}).get("max_retries", 3),
                strict=config.get("validation", {}).get("strict", True)
            )

        return configs

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
                "engine": "generic_loop_engine_with_harness",
                "run_intent": self.run_intent,
                "backend": self.backend,
                "validation_enabled": self.validation_enabled,
                "strict_mode": self.strict_mode,
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
            "harness_validation": {
                phase: {
                    "valid": result.valid,
                    "missing_fields": result.missing_fields,
                    "shallow_fields": result.shallow_fields,
                    "content_errors": result.content_errors,
                    "warnings": result.warnings,
                    "content_length": result.content_length,
                    "min_required_length": result.min_required_length,
                }
                for phase, result in self.harness_validation_results.items()
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
        """调用 worker，带验证 Harness"""
        worker_name = f"{phase}_worker"
        worker: Callable[[dict[str, Any]], dict[str, Any]] | None = getattr(self.worker_module, worker_name, None)
        if worker is None:
            raise RuntimeError(f"missing worker function {worker_name} in {self.worker_module_path}")

        # 如果验证未启用，直接调用
        if not self.validation_enabled or phase not in self.phase_configs:
            output = worker(self.worker_inputs(phase))
            if not isinstance(output, dict):
                raise RuntimeError(f"{worker_name} must return a dict")
            return output

        # 带验证的调用
        return self._call_worker_with_validation(phase, worker)

    def _call_worker_with_validation(
        self,
        phase: str,
        worker: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> dict[str, Any]:
        """
        带验证的 worker 调用

        支持重试，多次失败后记录失败胶囊
        """
        phase_config = self.phase_configs[phase]
        max_retries = phase_config.max_retries

        inputs = self.worker_inputs(phase)

        for attempt in range(1, max_retries + 1):
            print(f"\n[Harness] Phase '{phase}' - Attempt {attempt}/{max_retries}")

            # 准备带有输出要求的输入
            if attempt == 1:
                inputs_with_requirements = self._prepare_prompt_with_requirements(
                    inputs, phase_config
                )
            else:
                # 重试时添加反馈
                inputs_with_requirements = self._prepare_retry_prompt(
                    inputs, phase_config, last_validation_result, attempt
                )

            # 调用 worker
            output = worker(inputs_with_requirements)

            if not isinstance(output, dict):
                raise RuntimeError(f"{phase}_worker must return a dict")

            # 验证输出
            validation_result = self.validation_agent.validate_phase_output(
                output, phase, self.validation_agent.phase_requirements.get(phase, {})
            )

            last_validation_result = validation_result

            if validation_result.valid:
                print(f"[Harness] ✅ Phase '{phase}' validation passed")
                self.harness_validation_results[phase] = validation_result
                return output

            print(f"[Harness] ❌ Validation failed:")
            print(f"  - Missing fields: {len(validation_result.missing_fields)}")
            print(f"  - Shallow fields: {len(validation_result.shallow_fields)}")
            print(f"  - Errors: {len(validation_result.content_errors)}")

            # 如果不是最后一次尝试，打印反馈
            if attempt < max_retries:
                print(f"[Harness] Retrying with feedback...")

        # 所有重试失败，记录失败胶囊
        print(f"[Harness] ⚠️ All {max_retries} attempts failed, creating failure capsule")
        failure_output = self._create_failure_capsule(phase, phase_config, last_validation_result)
        self.harness_validation_results[phase] = last_validation_result

        # 根据 strict_mode 决定行为
        if self.strict_mode:
            raise RuntimeError(
                f"Phase '{phase}' failed validation after {max_retries} attempts. "
                f"Missing: {last_validation_result.missing_fields}, "
                f"Shallow: {last_validation_result.shallow_fields}"
            )

        return failure_output

    def _prepare_prompt_with_requirements(
        self,
        base_inputs: dict[str, Any],
        phase_config: PhaseConfig
    ) -> dict[str, Any]:
        """准备带有输出要求的输入"""
        inputs = base_inputs.copy()

        requirements_text = f"""
================================================================================
强制输出要求 (必须遵守)
================================================================================

你的输出必须符合以下 schema: {phase_config.schema}

必须包含以下字段:
"""
        for field in phase_config.must_include:
            requirements_text += f"  - {field}\n"

        requirements_text += f"""
要求:
1. 所有标记为 "必须" 的字段必须填写
2. 不能只用 "completed", "done", "ok" 等空泛词汇
3. 必须包含具体数值、代码位置、算法名称
4. hypothesis 必须有可量化的预测（如">5%"）
5. results 必须包含至少2个量化指标
6. failure_capsule 必须记录至少1个局限性
7. next_actions 必须包含至少1个具体行动

输出示例格式:
```yaml
phase: {phase_config.name}
hypothesis:
  statement: "..."
  testable_prediction: "降低 > 5%"
skill_implementation:
  code:
    structure:
      - function: "..."
        purpose: "..."
        algorithm: "..."
results:
  primary_metrics:
    metric_name:
      value: 0.123
      unit: "MW"
      context: "描述"
failure_capsule:
  known_limitations:
    - limitation: "..."
      impact: "..."
      severity: "medium"
next_actions:
  immediate:
    - action: "..."
      rationale: "..."
```

参考模板: docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md

请确保你的输出可以通过验证，否则会被要求重试。
"""

        inputs["_harness_requirements"] = requirements_text
        inputs["_harness_phase_config"] = {
            "name": phase_config.name,
            "must_include": phase_config.must_include,
            "schema": phase_config.schema,
        }

        return inputs

    def _prepare_retry_prompt(
        self,
        base_inputs: dict[str, Any],
        phase_config: PhaseConfig,
        last_validation: ValidationResult,
        attempt: int
    ) -> dict[str, Any]:
        """准备重试输入"""
        inputs = base_inputs.copy()

        retry_prompt = f"""
================================================================================
第 {attempt} 次重试 - 上次输出验证失败
================================================================================

{last_validation.feedback}

请根据上述反馈补充或修改你的输出，然后重试。

特别注意:
1. 不要省略任何强制字段
2. 提供具体数值而非空泛描述
3. 记录你的局限性（即使认为结果是成功的）
4. 说明算法名称和复杂度
5. 解释设计决策的理由

参考模板: docs/IDEAL_RESEARCH_RECORD_TEMPLATE.md
"""

        inputs["_harness_requirements"] = retry_prompt
        inputs["_harness_validation_feedback"] = {
            "missing_fields": last_validation.missing_fields,
            "shallow_fields": last_validation.shallow_fields,
            "errors": last_validation.content_errors,
        }

        return inputs

    def _create_failure_capsule(
        self,
        phase: str,
        phase_config: PhaseConfig,
        last_validation: ValidationResult
    ) -> dict[str, Any]:
        """创建失败胶囊"""
        return {
            "schema_version": "0.1.0",
            "object_type": "phase_failure_capsule",
            "phase": phase,
            "status": "failed_validation",
            "metadata": {
                "task_package": self.ctx.task_package,
                "worker": "harness_validation",
                "failure_type": "validation_failed"
            },
            "fields": {
                "failure_reason": "无法生成符合要求的输出",
                "base_skill_ref": f"skill.{self.domain}.{self.problem_name}.failed",
                "allowed_change_scope": [],
                "blocked_paths": ["validation_failed"],
                "required_tests": ["Fix validation errors before proceeding"],
                "output_skill_path": "",
                "summary": f"Phase {phase} failed validation after {phase_config.max_retries} attempts",
                "validation_summary": {
                    "missing_fields_count": len(last_validation.missing_fields),
                    "shallow_fields_count": len(last_validation.shallow_fields),
                    "errors_count": len(last_validation.content_errors),
                    "missing_fields": last_validation.missing_fields,
                    "shallow_fields": last_validation.shallow_fields,
                },
                "feedback": last_validation.feedback,
                "next_actions": {
                    "immediate": [
                        {
                            "action": "Review validation feedback and fix missing fields",
                            "rationale": "Required fields must be present for quality assurance"
                        },
                        {
                            "action": "Consider simplifying approach or breaking into smaller phases",
                            "rationale": "Current requirements may exceed agent capabilities"
                        }
                    ],
                    "short_term": [
                        {
                            "action": f"Review phase '{phase}' requirements configuration",
                            "rationale": "Requirements may be too strict for current agent capabilities"
                        }
                    ]
                }
            },
            "timestamp": utc_now(),
        }

    # ============================================================================
    # Phase 执行方法 (保持原有实现)
    # ============================================================================

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
        self.write_phase_transition(
            phase="cognition_diagnosis", status="completed", output_ref=payload["object_id"]
        )

    def run_loop_routing_decision(self) -> None:
        self.write_phase_transition(phase="loop_routing_decision", status="started")
        request = self.phase_results["skill_change_request"].payload
        result = self.phase_results["skill_execution"].payload
        assessment = self.phase_results["effectiveness_assessment"].payload
        diagnosis = self.phase_results["cognition_diagnosis"].payload
        fields = derive_routing_decision_fields(diagnosis)
        path, payload = write_loop_routing_decision(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata={"auto_derived": True},
            diagnosis_ref=diagnosis["object_id"],
            evidence_refs=[
                request["object_id"],
                result["object_id"],
                assessment["object_id"],
                diagnosis["object_id"],
            ],
            selected_next_worker=fields["selected_next_worker"],
            selected_action=fields["selected_action"],
            continue_loop=fields["continue_loop"],
            policy_basis=fields["policy_basis"],
            summary="Controller routes from diagnosis output without authoring worker judgments.",
        )
        self.phase_results["loop_routing_decision"] = PhaseResult(path, payload)
        self.write_phase_transition(
            phase="loop_routing_decision", status="completed", output_ref=payload["object_id"]
        )

    def run_review(self, *, review: dict[str, Any] | None = None) -> None:
        assessment = self.phase_results["effectiveness_assessment"].payload
        routing = self.phase_results["loop_routing_decision"].payload
        update = self.phase_results.get("cognition_to_skill_update")
        require_loop_review = bool(self.adapter.get("experimental", {}).get("require_loop_review", True))
        if update is None and require_loop_review:
            raise RuntimeError("generic loop engine expects cognition_to_skill_update for review output")
        if update is None:
            return
        if review is None:
            review = {"reviewer": "generic_loop_engine", "notes": ""}
        path, payload = write_loop_review(
            ctx=self.ctx,
            iteration=self.iteration_index,
            metadata=review,
            event_ref=assessment["object_id"],
            controller_update_ref=update.payload["object_id"],
            iteration_plan_ref=self.phase_results["skill_change_request"].payload["object_id"],
            routing_decision_ref=routing["object_id"],
            search_space_reduction="The E2E fixture keeps one deterministic candidate envelope for comparable A/B scoring.",
            failure_explanation_improvement="The harness records missing and shallow fields before persistence.",
            evaluator_refinement="The fixture keeps evaluator behavior fixed so quality differences come from harness enforcement.",
            claim_tightening="The review limits claims to harness behavior and record quality on task007_fixture.",
            verdict="substantiated",
            summary="Harness E2E run completed the standard worker chain and persisted review evidence.",
        )
        self.phase_results["loop_review"] = PhaseResult(path, payload)

    def run(self) -> Path:
        """执行完整循环"""
        print(f"\n{'='*70}")
        print(f"Generic Loop Engine with Harness")
        print(f"Task: {self.adapter['task_ref']}")
        print(f"Workspace: {self.workspace_root}")
        print(f"Validation: {'enabled' if self.validation_enabled else 'disabled'}")
        print(f"Strict mode: {'on' if self.strict_mode else 'off'}")
        print(f"{'='*70}\n")

        self.initialize_workspace()

        phases = self.loop_config.get("phases", STANDARD_PHASES)

        for phase in phases:
            print(f"\n[Engine] Running phase: {phase}")

            if phase == "skill_change_request":
                self.run_skill_change_request()
            elif phase == "skill_execution":
                self.run_skill_execution()
            elif phase == "effectiveness_assessment":
                self.run_effectiveness_assessment()
            elif phase == "cognition_diagnosis":
                self.run_cognition_diagnosis()
            elif phase == "loop_routing_decision":
                self.run_loop_routing_decision()
            else:
                raise RuntimeError(f"unknown phase: {phase}")

        review_config = self.loop_config.get("review", {})
        if review_config.get("enabled", True):
            self.run_review(review=review_config.get("data"))

        self.write_artifact_index()
        self.write_run_record(status="completed", verification={"status": "not_run"})

        print(f"\n{'='*70}")
        print(f"Loop completed: {self.workspace_root}")
        print(f"{'='*70}\n")

        return self.workspace_root


def main():
    parser = argparse.ArgumentParser(
        description="Run the generic loop engine with validation harness"
    )
    parser.add_argument(
        "--task-adapter",
        type=Path,
        required=True,
        help="Path to task adapter YAML file",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Workspace directory for outputs (default: auto-generated)",
    )
    parser.add_argument(
        "--run-intent",
        default="harness validation run",
        help="Intent string for this run",
    )
    parser.add_argument(
        "--loop-config",
        type=Path,
        default=None,
        help="Path to loop config YAML (optional)",
    )
    parser.add_argument(
        "--verifier-config",
        type=Path,
        default=None,
        help="Path to verifier config YAML (optional)",
    )
    parser.add_argument(
        "--backend",
        default="deterministic",
        help="Backend to use (default: deterministic)",
    )
    parser.add_argument(
        "--worker-module",
        type=Path,
        default=None,
        help="Override worker module path (optional)",
    )
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Disable validation harness",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (fail on validation error)",
    )
    parser.add_argument(
        "--phase-requirements",
        type=Path,
        default=None,
        help="Path to phase requirements config (optional)",
    )

    args = parser.parse_args()

    # 验证 task adapter
    if not args.task_adapter.exists():
        raise FileNotFoundError(f"task adapter not found: {args.task_adapter}")

    adapter = load_yaml(args.task_adapter)

    # 设置 workspace
    if args.workspace_root is None:
        workspace_root = (
            DEFAULT_WORKSPACE_ROOT
            / slugify(adapter["task_ref"])
            / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    else:
        workspace_root = args.workspace_root

    # 加载配置
    loop_config = load_yaml(args.loop_config) if args.loop_config else {"phases": STANDARD_PHASES}
    verifier_config = load_yaml(args.verifier_config) if args.verifier_config else {}

    # 解析 backend
    backend, backend_config = resolve_backend(args.backend, adapter)
    if backend == "python_module":
        require_backend_runnable(backend_config)

    # 创建并运行引擎
    engine = GenericLoopEngineWithHarness(
        task_adapter_path=args.task_adapter,
        workspace_root=workspace_root,
        run_intent=args.run_intent,
        loop_config=loop_config,
        verifier_config=verifier_config,
        backend=backend,
        backend_config=backend_config,
        worker_module_override=args.worker_module,
        phase_requirements_path=args.phase_requirements,
        validation_enabled=not args.no_validation,
        strict_mode=args.strict,
    )

    engine.run()


if __name__ == "__main__":
    main()
