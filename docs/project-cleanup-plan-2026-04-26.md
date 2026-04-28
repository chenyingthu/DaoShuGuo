# Project Cleanup Plan - 2026-04-26

## Cleanup Goal

Reduce repository noise before building the collaborative research workbench UI.

The current mainline is the human-Agent collaborative research workbench:

```text
CLI artifacts -> workbench_data -> researcher-facing briefs / cockpit / evidence graph / timeline
-> human decisions -> routing constraints -> next CLI / Agent loop
```

## Keep In Main Workspace

- Core project guidance and design docs.
- Current collaborative workbench handoff, plan, and review.
- Workbench schemas and samples.
- Workbench build, verify, write, and constraint compilation scripts.
- `workbench_data/`.
- Current task, evaluator, adapter, and evidence files needed by the workbench smoke tests.
- Current `real-task-001`, `task003`, and synthetic fixture evidence needed for workbench validation.

## Archive Instead Of Delete

- Historical plans and reviews from earlier autonomous-loop, Pi-runtime, and generic-loop stages.
- Old analysis matrices, raw LLM worker dumps, provider/runtime experiments, and bulk validation outputs.
- Old run directories not needed by the current workbench smoke path.
- Local runtime state, caches, and installed dependency folders.

## Safety Checks

Before and after cleanup, run:

```bash
python scripts/verify_workbench_topic.py --topic real-task-001
python scripts/verify_researcher_lens.py --topic real-task-001
python scripts/verify_research_communication_briefs.py --topic real-task-001
python scripts/validate_schemas.py --artifacts workbench
```

## Archive Root

Archived files go under:

```text
archive/2026-04-26-pre-workbench-ui-cleanup/
```

This preserves history while making the active project surface reflect the current workbench direction.
