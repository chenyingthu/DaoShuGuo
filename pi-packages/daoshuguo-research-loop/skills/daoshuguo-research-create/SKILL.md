---
name: daoshuguo-research-create
description: Initialize a DaoShuGuo research-loop session in Pi.
---

# DaoShuGuo Research Create

Use this skill to start a bounded DaoShuGuo research-loop session.

## Steps

1. Identify the current task reference and objective.
2. Call `init_research_task` with the task reference and objective.
3. Read `research_loop.md`.
4. Keep all future skill work bounded by the current task, evaluator, and evidence scope.
5. After each meaningful action, call `log_research_iteration`.
6. After a concrete skill trial, call `record_skill_trial`.

## Rules

- Skill agents modify candidate skill code only.
- Cognition agents update next-round constraints only.
- Do not turn one run into a broad scientific claim.
- If the task/evaluator boundary is unclear, log `blocked` rather than guessing.
