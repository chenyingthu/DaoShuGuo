# Pre-Workbench UI Cleanup Archive - 2026-04-26

This archive preserves non-mainline project material before the collaborative workbench UI pass.

Current mainline kept in the active workspace:

- Collaborative workbench handoff, plan, review, and cleanup plan.
- Workbench data, schemas, samples, and file-backed scripts.
- Core project design docs and research-quality constraints.
- Minimal task/evaluator/adapter/run/analysis evidence needed by workbench smoke tests.

## Archived Sections

- `analysis-archive/`: historical autonomous-loop, Pi-runtime, generic-loop, onboarding, portfolio, structural-learning, and task-analysis outputs.
- `historical-plans/`: older plans from pre-workbench directions.
- `historical-reviews/`: older plan reviews and runtime reviews from pre-workbench directions.
- `legacy-scripts/`: execution and verification scripts for archived loop/runtime experiments.
- `legacy-docs/`: old loop/Pi/onboarding/protocol notes and logs not needed for the current workbench UI milestone.
- `legacy-agents/`: generated agent job specs, prompts, outputs, and runtime config experiments.
- `runs-archive/`: historical run outputs; only the latest `task003` run remains active for workbench smoke testing.
- `task-fixtures/`: synthetic and mismatch fixtures from generic-loop validation.
- `dependency-cache/`: installed dependency folders such as `node_modules`.
- `local-runtime/`: local caches, OMX state/logs, Python bytecode caches, and backup bundles.

## Restore Rule

If a future task needs one of these files, move back only the specific file or directory required for that task. Do not bulk-restore this archive into the active workspace.

Before claiming the workbench mainline is intact, run:

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
