# Research Loop File Contract

## Purpose

DaoShuGuo-on-Pi uses two durable loop files:

- `research_loop.md`
- `research_loop.jsonl`

They serve different purposes and should not be mixed.

## `research_loop.md`

Human-readable, resumable research memory.

Should contain:

- task reference
- bounded objective
- current constraints
- what has been tried
- high-level summaries of important trials and constraints

Should not contain:

- raw command output dumps
- full evaluator payloads
- append-only machine logs

## `research_loop.jsonl`

Append-only structured loop log.

Each line is one event.

Recommended top-level fields:

- `timestamp`
- `event`
- `task_ref`
- `data`

## Recommended Event Types

- `init_research_task`
- `research_iteration`
- `skill_trial`
- `cognition_constraint`
- `iteration_review`
- `blocked_reason`
- `effectiveness_note`

## Write Policy

### Markdown

Write only short, durable, human-readable summaries.

### JSONL

Write structured event facts that may be replayed or parsed later.

## Current Tool Mapping

- `init_research_task`
  - writes both markdown and jsonl
- `log_research_iteration`
  - writes both markdown and jsonl
- `record_skill_trial`
  - writes both markdown and jsonl
- `record_cognition_constraint`
  - writes both markdown and jsonl
- `record_iteration_review`
  - writes both markdown and jsonl

## Resume Rule

A future Pi agent should be able to resume by reading:

1. `research_loop.md`
2. latest relevant lines from `research_loop.jsonl`

without depending on hidden prompt history.
