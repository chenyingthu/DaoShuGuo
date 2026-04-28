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
4. Use `run_task_trial` with task_id and strategy to execute trials.
   - Example: `run_task_trial(task_id="task003", strategy="inverter-support")`
   - Example: `run_task_trial(task_id="task004", strategy="inverter-support", candidate_params={"q_step_mvar": 0.5})`
5. Keep all future skill work bounded by the current task, evaluator, and evidence scope.
6. After each meaningful action, call `log_research_iteration`.
7. After a concrete skill trial, call `record_skill_trial`.

## Tools Reference

### Preferred (Generic)

- `run_task_trial(task_id, strategy, candidate_params?)` - Execute any task via unified CLI

### Deprecated (Task-Specific)

- `run_task003_trial(strategy)` - Use `run_task_trial(task_id="task003", ...)` instead
- `run_task004_trial(strategy, candidate_q_step_mvar?)` - Use `run_task_trial(task_id="task004", ...)` instead

## Rules

- Skill agents modify candidate skill code only.
- Cognition agents update next-round constraints only.
- Do not turn one run into a broad scientific claim.
- If the task/evaluator boundary is unclear, log `blocked` rather than guessing.
- Use generic `run_task_trial` for new tasks; deprecated tools remain for backward compatibility.
