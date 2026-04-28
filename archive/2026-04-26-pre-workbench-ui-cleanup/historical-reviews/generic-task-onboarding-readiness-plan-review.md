# Generic Task Onboarding Readiness Plan Review

---

## Code Review Round 1 — 2026-04-25

**Scope**: `plans/generic-task-onboarding-readiness-plan.md`, onboarding docs, adapter schemas, adapters, fixture task, onboarding CLI, verifier, tests, and generated readiness reports.

**Build Status**: PASS

### Issues

No blocking issues remain after the implementation pass.

During implementation, one issue was found and fixed:

#### Issue 1 (High): Skill references were checked only against YAML skill files

**File**: `scripts/run_task_onboarding_check.py`

The first implementation scanned only `skills/**/*.yaml`, causing task003/task004/task005 to be incorrectly diagnosed as `blocked_missing_skill`. This was not a task readiness failure; it was a framework indexing failure because accepted skill references also live in `skills/registry.json` and schema sample skill objects.

**Fix**: Skill reference resolution now builds a generic skill-id index from:

- `skills/**/*.yaml`
- `schemas/samples/*.yaml`
- `skills/registry.json`

No task-specific branch was added.

#### Issue 2 (Medium): Fixture evaluator reference conflicted with schema reference validation

**File**: `adapters/task007_fixture.yaml`

The fixture adapter initially pointed to a missing evaluator object to trigger `blocked_missing_evaluator`. That proved blocked routing but violated global schema reference integrity.

**Fix**: Added `evaluators/task007_fixture_evaluator.yaml` as a draft evaluator contract while intentionally not adding `evaluators/task007_fixture_evaluator.py`. The fixture now validates as data but is diagnosed by onboarding as `blocked_missing_runtime`.

### Verification

Passed:

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

Observed readiness:

- `task003`: `ready_to_run`
- `task004`: `ready_to_run`
- `task005`: `ready_for_framing_only`
- `task007_fixture`: `blocked_missing_runtime`

### Historical Execution Deviation

The first execution attempt used a legacy `plan-execute` skill loaded from `~/.agents/skills`. That legacy skill expected implementation through a Claude-oriented Codex wrapper. The wrapper invocation failed with:

```text
script: unexpected number of arguments
```

This failure occurred before code execution. The implementation was completed directly in that session under the same plan/review/test discipline.

This was later diagnosed as skill-root contamination: Codex/OMX had loaded legacy `~/.agents/skills` alongside canonical `~/.codex/skills`. The legacy skill root has since been archived, `omx setup --force` was rerun, and a Codex/OMX-native `plan-execute` skill was added under `~/.codex/skills/plan-execute`.

### Verdict: APPROVED

The generic onboarding/readiness layer is now implemented and verified for the current scope. It proves task-agnostic readiness diagnosis, not full task-agnostic autonomous research execution.

---

## Code Review Round 2 — 2026-04-25

**Scope**: Re-verification under canonical Codex/OMX-native `plan-execute`.

**Verification Status**: PASS

### Issues

No new issues found.

The plan file is fully checked off, and no task-specific Python script was added for `task007_fixture`. The onboarding CLI remains generic: it loads `adapters/{task_id}.yaml`, checks declared paths and refs, and writes `analysis/onboarding/{task_id}/task_readiness_report.yaml`.

### Execution Deviations

No legacy Claude wrapper or `~/.agents/skills` path was used in this round.

`omx doctor` confirms:

```text
Legacy skill roots: no ~/.agents/skills overlap detected
Skills: 26 skills installed
```

### Verification

Passed:

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

Observed readiness:

- `task003`: `ready_to_run`, route `run_research_pipeline`
- `task004`: `ready_to_run`, route `run_research_pipeline`
- `task005`: `ready_for_framing_only`, route `framing_only`
- `task007_fixture`: `blocked_missing_runtime`, route `repair_adapter`

### Verdict: APPROVED

The generic task onboarding readiness plan is complete under the canonical Codex/OMX-native execution path.
