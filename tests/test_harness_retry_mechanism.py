from pathlib import Path

import pytest

from e2e_utils import REPO_ROOT
from scripts.run_generic_loop_engine_with_harness import GenericLoopEngineWithHarness, PhaseConfig


class AlwaysInvalidWorker:
    def __init__(self):
        self.calls = []

    def __call__(self, inputs):
        self.calls.append(inputs)
        return {
            "metadata": {"task_package": "fixture_loop", "worker": "invalid_worker"},
            "fields": {
                "base_skill_ref": "skill.power.invalid",
                "allowed_change_scope": [],
                "blocked_paths": [],
                "required_tests": [],
                "output_skill_path": "",
                "summary": "bad",
            },
        }


def make_engine(tmp_path: Path) -> GenericLoopEngineWithHarness:
    engine = GenericLoopEngineWithHarness(
        task_adapter_path=REPO_ROOT / "adapters" / "task007_fixture.yaml",
        workspace_root=tmp_path / "retry_engine",
        run_intent="retry unit test",
        loop_config={"phases": ["skill_change_request"], "review": {"enabled": False}},
        verifier_config={},
        backend="deterministic",
        backend_config={"backend_id": "deterministic", "worker_module": "scripts/generic_loop_engine_fixture_workers.py"},
        worker_module_override=REPO_ROOT / "scripts" / "generic_loop_engine_fixture_workers.py",
        validation_enabled=True,
        strict_mode=False,
    )
    engine.phase_configs["skill_change_request"] = retry_phase_config()
    return engine


def retry_phase_config() -> PhaseConfig:
    return PhaseConfig(
        name="skill_change_request",
        description="retry test",
        required_outputs=[],
        schema="schemas/work_brief.schema.json",
        must_include=["hypothesis.statement", "hypothesis.rationale", "method.description"],
        max_retries=2,
        strict=False,
    )


def test_max_retries(tmp_path):
    engine = make_engine(tmp_path)
    worker = AlwaysInvalidWorker()

    output = engine._call_worker_with_validation("skill_change_request", worker)

    assert len(worker.calls) == 2
    assert output["object_type"] == "phase_failure_capsule"
    assert output["fields"]["validation_summary"]["missing_fields_count"] >= 3


def test_retry_prompt_contains_feedback(tmp_path):
    engine = make_engine(tmp_path)
    worker = AlwaysInvalidWorker()

    engine._call_worker_with_validation("skill_change_request", worker)

    assert "_harness_validation_feedback" in worker.calls[1]
    assert "hypothesis.statement" in worker.calls[1]["_harness_validation_feedback"]["missing_fields"]
    assert "上次输出验证失败" in worker.calls[1]["_harness_requirements"]


def test_failure_capsule_on_max_retries(tmp_path):
    engine = make_engine(tmp_path)
    validation = engine.validation_agent.validate_phase_output({}, "skill_change_request")

    capsule = engine._create_failure_capsule("skill_change_request", retry_phase_config(), validation)

    assert capsule["status"] == "failed_validation"
    assert capsule["fields"]["validation_summary"]["missing_fields_count"] > 0
    assert capsule["fields"]["next_actions"]["immediate"]


def test_strict_retry_raises_after_max_retries(tmp_path):
    engine = make_engine(tmp_path)
    engine.strict_mode = True
    worker = AlwaysInvalidWorker()

    with pytest.raises(RuntimeError, match="failed validation"):
        engine._call_worker_with_validation("skill_change_request", worker)
