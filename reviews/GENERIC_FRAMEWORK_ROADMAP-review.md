---

## Code Review Round 1 - 2026-04-27

**Scope**: Execute Phase 0 of `plans/GENERIC_FRAMEWORK_ROADMAP.md`: restore the generic loop engine skeleton, restore generic task onboarding, add `task007_fixture`, and verify readiness routing.
**Verification Status**: PASS

### Issues

No unresolved critical or high issues for Phase 0.

### Execution Deviations

- Used copy-style restoration from `archive/2026-04-26-pre-workbench-ui-cleanup/` instead of `mv`, preserving the archive as evidence.
- Treated `task007_fixture` as a generic onboarding fixture, not a runnable research task. Its successful result is a blocked readiness report with route `repair_adapter`.
- Added `scripts/verify_generic_task_onboarding.py` as a thin CLI wrapper over the restored onboarding implementation so the roadmap's command shape works.
- Restored `configs/agent_runtimes/registry.yaml` and `scripts/generic_full_loop_validation_workers.py` because `scripts/run_generic_loop_engine.py` requires them for the default deterministic smoke path.
- Adjusted the restored deterministic worker default route from `portfolio_worker` to `cognition_worker` for `evidence_insufficiency` so it matches `scripts/generic_diagnosis_layer.py` routing policy.
- Did not execute Phase 1-4. The orchestrator unified `real-run` CLI and Pi Skill migration remain future work.

### Verification Evidence

- `python scripts/run_generic_loop_engine.py --help` passed.
- `python -m py_compile scripts/run_generic_loop_engine.py scripts/backend_registry.py scripts/generic_diagnosis_layer.py scripts/worker_chain_helpers.py scripts/generic_loop_engine_fixture_workers.py scripts/generic_loop_engine_task004_workers.py scripts/generic_loop_engine_task005_workers.py scripts/generic_full_loop_validation_workers.py scripts/run_task_onboarding_check.py scripts/verify_task_onboarding.py scripts/verify_generic_task_onboarding.py` passed.
- `python scripts/verify_generic_task_onboarding.py --task task007_fixture` passed and wrote `analysis/onboarding/task007_fixture/task_readiness_report.yaml` with `blocked_missing_runtime`, route `repair_adapter`, and risk `fixture is intentionally incomplete`.
- `python scripts/verify_generic_task_onboarding.py --task task003` passed with `ready_to_run`.
- `python scripts/verify_generic_task_onboarding.py --task task004` passed with `ready_to_run`.
- `python scripts/verify_generic_task_onboarding.py` passed aggregate onboarding verification for task003, task004, task005, and task007_fixture.
- `python scripts/verify_generic_loop_engine.py` passed.
- `pytest -q tests/test_task_onboarding.py` passed: 4 tests.
- `python scripts/validate_schemas.py` passed.

### Verdict: APPROVED
