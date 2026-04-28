# Generic Task Onboarding Readiness Plan

## 1. Plan Position

This is a corrective plan.

The project has built many useful mechanisms: research-plan-execute, review gate, structural learning, skill-structure assessment, and cross-task portfolio assessment. However, too much of the implementation still depends on task-specific replay paths such as `task003_iter02`.

This plan exists to fix that.

The goal is:

> A new task package such as `task007` must be checkable, diagnosable, and routable through common framework code without writing a new framework script for that task.

If this plan fails, the project remains a collection of task-specific experiments, not a reusable autonomous research framework.

## 2. Non-Negotiable Principle

Do not implement another task-specific replay.

Every implementation in this plan must answer:

> Does this make task007/task008 onboarding possible without changing framework code?

If not, it is out of scope.

## 3. Definitions

### 3.1 Task Package

A task package is a directory under `tasks/{task_id}` containing enough material to define a research task.

Minimum expected package files:

- `task.yaml`
- `baseline.yaml`
- task context files declared by `task.yaml.input_artifacts`
- constraints or assumptions files when declared by the task

### 3.2 Task Adapter

A task adapter is a configuration object, not a new script.

It declares:

- task ref
- task package path
- baseline ref and path
- evaluator ref and path
- runtime entry
- metrics mapping
- candidate skill refs
- fallback skill refs
- claim gates
- known task risks
- supported downstream stages

The adapter must remain thin. It must not implement loop logic, review logic, learning logic, or portfolio logic.

### 3.3 Readiness Report

A readiness report is a structured object saying whether a task can enter the framework.

It must produce one of:

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

It must include:

- missing items
- available items
- recommended route
- blocked stages
- supported stages
- evidence refs
- next actions

## 4. Required Deliverables

### 4.1 Documentation

- [x] Create `docs/generic-task-onboarding-readiness.md`
- [x] Document the task package contract
- [x] Document adapter config requirements
- [x] Document readiness statuses and routing rules
- [x] Document the difference between framework code and task package data

### 4.2 Schemas

- [x] Add `task_adapter.schema.yaml`
- [x] Add `task_readiness_report.schema.yaml`
- [x] Add samples for both schemas
- [x] Register both object types in `scripts/validate_schemas.py`
- [x] Add artifact set `generic-task-onboarding`

### 4.3 Adapter Registry

- [x] Add `adapters/task003.yaml`
- [x] Add `adapters/task004.yaml`
- [x] Add `adapters/task005.yaml`
- [x] Add `adapters/task007_fixture.yaml`
- [x] The registry must be data-only YAML files
- [x] No task-specific Python code is allowed for task007 fixture

### 4.4 Onboarding CLI

- [x] Implement `scripts/run_task_onboarding_check.py`
- [x] It must accept `--task task003`, `--task task004`, `--task task005`, `--task task007_fixture`
- [x] It must read adapter YAML and task package files
- [x] It must not import task-specific runtime helpers
- [x] It must generate `analysis/onboarding/{task_id}/task_readiness_report.yaml`
- [x] It must exit nonzero only on tool/runtime error, not on blocked readiness
- [x] It must include machine-readable status and route

### 4.5 Verifier

- [x] Implement `scripts/verify_task_onboarding.py`
- [x] It must verify all expected readiness reports exist
- [x] It must verify task003/task004/task005 do not require task-specific framework code
- [x] It must verify task007_fixture is diagnosed through data-only adapter
- [x] It must verify missing or intentionally incomplete fields produce blocked reports, not crashes

### 4.6 Fixture Task

- [x] Add `tasks/task007_fixture/task.yaml`
- [x] Add minimal fixture context files
- [x] Add `adapters/task007_fixture.yaml`
- [x] The fixture must be intentionally incomplete enough to test blocked routing
- [x] No evaluator implementation is required for task007 fixture

### 4.7 Tests

- [x] Add `tests/test_task_onboarding.py`
- [x] Test that task003/task004/task005 produce readiness reports through the same CLI
- [x] Test that task007_fixture produces a blocked report without code changes
- [x] Test that missing evaluator/runtime or missing metrics mapping is reported explicitly
- [x] Test that the CLI does not crash for blocked tasks

### 4.8 Records

- [x] Update `docs/实验过程与讨论记录.md`
- [x] Add review file `reviews/generic-task-onboarding-readiness-plan-review.md`
- [x] Explain whether the framework is now closer to task-agnostic onboarding

## 5. Design Requirements

### 5.1 Do Not Hardcode Task003 Logic

The onboarding CLI may contain generic validation functions only.

Forbidden:

- `if task == "task003": ...`
- `if task == "task004": ...`
- `if task == "task005": ...`
- importing `tasks/task003/runtime_helpers.py`
- reading `runs/task003/run_0021` inside onboarding logic

Allowed:

- loading `adapters/{task_id}.yaml`
- reading paths declared in the adapter
- checking if declared files and refs exist

### 5.2 Readiness Is Not Success

`ready_to_run` only means the task package is complete enough to enter the framework.

It does not mean:

- the task is scientifically valuable
- the skill will improve
- the evaluator is perfect
- the task should receive more research resources

Portfolio assessment remains responsible for research allocation.

### 5.3 Blocked Is A Valid Outcome

If task007_fixture is blocked, that is success if the report explains why.

The framework must prefer:

`blocked_missing_evaluator`

over:

runtime crash, silent pass, or task-specific patch.

### 5.4 Generic Downstream Routing

Readiness report must route to one of:

- `run_research_pipeline`
- `repair_task_package`
- `repair_adapter`
- `repair_evaluator`
- `repair_skill_binding`
- `framing_only`
- `pause_for_human_review`

## 6. Implementation Sequence

### Phase 1: Contract And Schemas

- [x] Write docs
- [x] Add schemas
- [x] Add samples
- [x] Register schema object types
- [x] Add artifact validation set

### Phase 2: Adapters And Fixture

- [x] Add adapters for task003/task004/task005
- [x] Add task007 fixture package
- [x] Add task007 fixture adapter
- [x] Ensure adapter files are data-only

### Phase 3: Onboarding CLI

- [x] Implement generic adapter loader
- [x] Implement package file checks
- [x] Implement ref/path checks
- [x] Implement metrics mapping checks
- [x] Implement status/routing decision
- [x] Write readiness report

### Phase 4: Verification And Tests

- [x] Implement verifier
- [x] Add tests
- [x] Run onboarding for task003/task004/task005/task007_fixture
- [x] Run schema validation
- [x] Run light probe

### Phase 5: Review And Records

- [x] Write implementation review
- [x] Update discussion log
- [x] Summarize what is now generic and what remains task-specific

## 7. Acceptance Criteria

This plan is complete only when all commands pass:

```bash
python scripts/run_task_onboarding_check.py --task task003
python scripts/run_task_onboarding_check.py --task task004
python scripts/run_task_onboarding_check.py --task task005
python scripts/run_task_onboarding_check.py --task task007_fixture
python scripts/verify_task_onboarding.py
python scripts/validate_schemas.py --artifacts generic-task-onboarding
pytest tests/test_task_onboarding.py -q
python scripts/run_light_probe.py
```

Expected readiness:

- `task003`: `ready_to_run` or `ready_for_framing_only` if a generic runtime binding is intentionally incomplete, but not a crash.
- `task004`: `ready_to_run` or explicitly routed to evaluator/claim-gate repair if adapter declares missing support.
- `task005`: not allowed to silently claim skill readiness if cost-benefit standard is missing; it may route to `repair_evaluator`.
- `task007_fixture`: must produce a blocked report such as `blocked_missing_runtime` or `blocked_missing_metrics_mapping` without any framework code change.

## 8. Definition Of Done

The implementation is done when:

1. All checklist items above are completed.
2. The same CLI handles all four tasks.
3. task007_fixture proves new task packages can be diagnosed without framework code changes.
4. No new task-specific Python script is added for task007_fixture.
5. Review log states whether the implementation is approved.
6. Discussion log records the lesson: generic onboarding is the boundary between framework and task-specific replay.
