# Generic Task Onboarding Readiness

## 1. Purpose

This document defines the generic onboarding layer for new research tasks.

The goal is to make a new task package checkable and routable without writing task-specific framework code.

If a task can only run after adding a custom Python onboarding script, the system is still in fixture/replay mode and must not be described as a generic autonomous research framework.

## 2. Task Package Contract

A task package lives under:

`tasks/{task_id}/`

Minimum expected files:

- `task.yaml`
- `baseline.yaml`
- all context files declared by `task.yaml.input_artifacts`

The package may also contain:

- `constraints.yaml`
- `assumptions.yaml`
- `runtime_helpers.py`
- domain-specific context files

The onboarding layer checks these files. It does not import runtime helper modules.

## 3. Adapter Contract

Each task has a data-only adapter:

`adapters/{task_id}.yaml`

The adapter declares:

- task ref and package path
- baseline ref and path
- evaluator ref and path
- runtime entry
- metrics mapping
- candidate and fallback skill refs
- claim gates
- known task risks
- supported downstream stages

The adapter must remain thin. It must not encode loop logic, cognition logic, skill implementation, or review-gate rules.

## 4. Readiness Statuses

The onboarding CLI emits one readiness report with one of:

- `ready_to_run`
- `ready_for_framing_only`
- `blocked_missing_task_contract`
- `blocked_missing_baseline`
- `blocked_missing_evaluator`
- `blocked_missing_runtime`
- `blocked_missing_skill`
- `blocked_missing_metrics_mapping`
- `blocked_missing_claim_gate`
- `blocked_missing_adapter`
- `pause_for_human_review`

Blocked statuses are valid outcomes. A blocked report is better than a runtime crash or a silent pass.

## 5. Routing Rules

Readiness status maps to a route:

- `ready_to_run` -> `run_research_pipeline`
- `ready_for_framing_only` -> `framing_only`
- `blocked_missing_task_contract` -> `repair_task_package`
- `blocked_missing_baseline` -> `repair_task_package`
- `blocked_missing_evaluator` -> `repair_evaluator`
- `blocked_missing_runtime` -> `repair_adapter`
- `blocked_missing_skill` -> `repair_skill_binding`
- `blocked_missing_metrics_mapping` -> `repair_adapter`
- `blocked_missing_claim_gate` -> `repair_evaluator`
- `blocked_missing_adapter` -> `repair_adapter`
- `pause_for_human_review` -> `pause_for_human_review`

## 6. Framework Code Versus Task Data

Framework code:

- loads adapters
- checks declared paths and refs
- writes readiness reports
- verifies generic invariants

Task data:

- task package files
- adapter YAML
- evaluator path declarations
- skill refs
- metrics mapping

Adding a new task should normally add task data only. If new framework code is required, the gap must be recorded as a framework limitation.

## 7. Acceptance Example

The same CLI must handle all of:

```bash
python scripts/run_task_onboarding_check.py --task task003
python scripts/run_task_onboarding_check.py --task task004
python scripts/run_task_onboarding_check.py --task task005
python scripts/run_task_onboarding_check.py --task task007_fixture
```

`task007_fixture` is intentionally incomplete. It has a valid evaluator contract but no evaluator runtime implementation, proving that a new task can be diagnosed as blocked without a task-specific script.
