# Research Loop State Contract

## Purpose

`research_loop.md` and `research_loop.jsonl` are not enough for stable Pi execution.

The step-based runner also writes:

- `state/research_state.json`
- `state/requests/<step>.json`
- `state/results/<step>.json`

This file defines their purpose.

## `research_state.json`

Current execution snapshot.

Recommended fields:

- `task_ref`
- `iteration`
- `current_step`
- `provider`
- `model`
- `workdir`
- `steps`

Each step entry contains:

- `status`
- `started_at`
- `finished_at`
- `provider`
- `model`
- `prompt`
- `exit_code`
- `stderr`
- `stdout_excerpt`
- `extracted`

## `state/requests/<step>.json`

One request payload per step.

Purpose:

- make each step reproducible
- allow post-hoc review of what the model was asked to do
- support resume without hidden context

## `state/results/<step>.json`

One result payload per step.

Purpose:

- preserve execution result even if the conversation fails later
- make step-level debugging possible

## Resume Rule

Resume order:

1. read `research_state.json`
2. find first step whose status is not `completed`
3. restart from that step
4. do not rerun completed steps unless explicitly reset

## Idempotency Rule

Completed steps are not rerun by default.

This prevents:

- duplicate loop file pollution
- unnecessary repeated task runs
- repeated tool invocations after successful completion
