# Project Cleanup Report - 2026-04-26

## Scope

Cleaned the active workspace before the collaborative workbench UI milestone.

The cleanup preserved the current mainline:

- file-backed collaborative workbench data and scripts
- workbench / human-in-the-loop / communication schemas and samples
- current collaborative workbench handoff, plan, and review
- project-level research quality docs
- minimal evidence required by workbench smoke tests

## What Stayed Active

- `workbench_data/`
- `scripts/workbench_common.py`
- `scripts/build_workbench_topic.py`
- `scripts/verify_workbench_topic.py`
- `scripts/build_researcher_lens.py`
- `scripts/verify_researcher_lens.py`
- `scripts/build_research_communication_briefs.py`
- `scripts/verify_research_communication_briefs.py`
- `scripts/write_*human/research/claim/steering*.py`
- `scripts/compile_human_decision_constraints.py`
- `scripts/apply_workbench_constraints_to_loop.py`
- `scripts/verify_workbench_loop_integration.py`
- `scripts/validate_schemas.py`
- `plans/collaborative-research-workbench-plan.md`
- `reviews/collaborative-research-workbench-plan-review.md`
- `docs/collaborative-workbench-handoff-2026-04-26.md`

## What Was Archived

Archive root:

```text
archive/2026-04-26-pre-workbench-ui-cleanup/
```

Archived categories:

- historical autonomous-loop / Pi-runtime / generic-loop analysis outputs
- historical plans and plan reviews
- legacy runtime, loop, Pi, onboarding, and worker scripts
- legacy loop/Pi/onboarding/protocol docs
- generated agent prompts, jobs, outputs, and configs
- historical runs except the latest `task003` run used by the workbench smoke path
- synthetic/mismatch task fixtures from generic validation experiments
- local runtime state, caches, backup bundle, and dependency cache

The archive includes its own index at:

```text
archive/2026-04-26-pre-workbench-ui-cleanup/README.md
```

## Verification

Passed after cleanup:

```bash
python scripts/verify_workbench_topic.py --topic real-task-001
python scripts/verify_workbench_topic.py --topic task003
python scripts/verify_workbench_topic.py --topic synthetic-topic-fixture
python scripts/verify_researcher_lens.py --topic real-task-001
python scripts/verify_research_communication_briefs.py --topic real-task-001
python scripts/compile_human_decision_constraints.py --topic real-task-001 --dry-run
python scripts/verify_workbench_loop_integration.py --topic real-task-001 --dry-run
python scripts/validate_schemas.py --artifacts workbench
```

Results:

- all topic verification commands returned `status: passed`
- researcher lens returned `status: passed`
- communication briefs returned `status: passed`
- constraint compilation returned `status: compiled` with 10 constraints in dry-run
- loop integration returned `status: passed` with 10 constraints in dry-run
- schema validation returned `Schema validation passed. Artifact validation passed for: workbench.`

## Remaining Risks

- Schema files and samples remain broad because `validate_schemas.py` currently loads the full schema/sample library even for `--artifacts workbench`.
- Task/evaluator/adapter support files remain active because the workbench artifact validator scans them as support objects.
- The archive is large because it intentionally preserves raw historical evidence rather than deleting it.
