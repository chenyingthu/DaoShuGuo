## Code Review Round 1 — 2026-04-22

**Scope**: `plans/llm-agent-cognition-layer-plan.md` 第一轮实现审查，覆盖 agent prompts、job spec、offline job bundles、dry-run runner、guardrail verifier 与 integration checks
**Build Status**: PASS

### Issues

无 High/Critical 问题。

### Notes

- 已在 `AGENTS.md` 中明确写入：规则不是认知，LLM agent 必须作为认知工作者接入。
- 已新增四类认知 agent prompt：
  - result interpreter
  - semantic critic
  - literature reviewer
  - effectiveness reviewer
- 已新增 job spec：
  - `agents/cognition/job_spec.yaml`
- 已新增离线 job builder：
  - `scripts/build_llm_cognition_jobs.py`
- 已新增 dry-run / callable runner：
  - `scripts/run_llm_cognition_job.py`
- 已新增 guardrail verifier：
  - `scripts/verify_llm_cognition_outputs.py`
- 已生成 task003/task004/task005/effectiveness 四个离线 job bundle 和 dry-run output。
- 目前还没有真实调用 LLM，因此本阶段只完成接口、离线审查与 guardrail，不声称 LLM 已产生更深认知。

### Verification

- `python scripts/build_llm_cognition_jobs.py`
- `python scripts/run_llm_cognition_job.py agents/cognition/jobs/task003_semantic_critic_001.json --dry-run`
- `python scripts/run_llm_cognition_job.py agents/cognition/jobs/task004_literature_reviewer_001.json --dry-run`
- `python scripts/run_llm_cognition_job.py agents/cognition/jobs/task005_result_interpreter_001.json --dry-run`
- `python scripts/run_llm_cognition_job.py agents/cognition/jobs/effectiveness_reviewer_001.json --dry-run`
- `python scripts/verify_llm_cognition_outputs.py`
- `python scripts/run_integration_checks.py`

### Real LLM Test

- 已使用 Codex 真实执行 `task005_result_interpreter_001`。
- 已使用 Codex 真实执行 `task003_semantic_critic_001`、`task004_literature_reviewer_001`、`effectiveness_reviewer_001`。
- 真实 LLM 输出发现 `task005_evaluator.py` 中 `restoration_action_cost_proxy` 的解释问题：该指标标注为 `lower_is_better`，但旧逻辑曾将成本增加标记为 `improved`。
- 已修复 evaluator：`improved` 现在只表示成本更低，成本容忍性用 `acceptable` 表达。
- 已新增 `llm_vs_rule_task005_result_interpreter_001.yaml` 记录 LLM vs rule 的增益与风险。
- 真实 task003 semantic critic 明确指出了“metric improvement != task-semantic success”的 evaluator-intent gap。
- 真实 task004 literature reviewer 明确指出了当前文献证据主要支持“boundary-of-validity clarification”，而不是强 novelty claim。
- 真实 effectiveness reviewer 对 task003 / task004 的 deliverable routing 给出了比规则层更细的交付边界解释。

### Remaining Scope

- 当前四类角色都已至少完成一次真实执行。
- 但每类角色目前仅有少量样本，尚不足以证明稳定增益。
- 尚未形成严格的 LLM-vs-rule comparison rubric 和统计性评估。

### Verdict: APPROVED
