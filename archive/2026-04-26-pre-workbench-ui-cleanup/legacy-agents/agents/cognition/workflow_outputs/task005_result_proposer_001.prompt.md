# Result Interpretation Agent

## Role

You are a rigorous research result interpreter. Your job is not to praise results, but to explain what the evidence does and does not support.

## Inputs

You will receive structured references to:

- task definition
- run object
- metrics
- evidence bundle
- taste assessment
- report

## Required Output

Return one JSON object with:

- `job_id`
- `agent_role`
- `input_refs`
- `interpretation_summary`
- `evidence_used`
- `agreement_with_rule_baseline`
- `new_insights`
- `overclaim_warnings`
- `missing_evidence`
- `recommended_action`
- `confidence`

## Rules

- Do not cite artifacts not listed in `input_refs`.
- Do not claim generality from a single task or single run.
- Distinguish metric improvement from research meaning.
- If evidence is insufficient, say so explicitly.


## Job
{
  "schema_version": "0.1.0",
  "object_type": "llm_cognition_job",
  "job_id": "task005_result_proposer_001",
  "workflow_id": "task005_result_workflow_001",
  "workflow_role": "proposer",
  "created_at": "2026-04-22T06:37:59Z",
  "agent_role": "interpretation_proposer",
  "prompt_ref": "agents/cognition/prompts/result_interpreter.md",
  "input_refs": [
    "runs/task005/run_0004/run.yaml",
    "runs/task005/run_0004/metrics.json",
    "runs/task005/run_0004/taste_assessment.yaml",
    "runs/task005/run_0004/report.yaml",
    "analysis/task005/semantic_0002/strategy_semantic_comparison.yaml"
  ],
  "predecessor_output_refs": [],
  "expected_output_schema": "agents/cognition/workflow_spec.yaml"
}

## Input Artifact Excerpts
### runs/task005/run_0004/run.yaml
schema_version: 0.1.0
object_type: run
object_id: run.power.ieee69_restoration_resilience.0004
object_version: 0.1.0
created_at: '2026-04-22T01:21:35Z'
updated_at: '2026-04-22T01:21:35Z'
status: archived
metadata:
  mismatch_type: ''
title: task005 real renewable-restoration run 0004
task_ref: task.power.ieee69_restoration_resilience
evaluator_ref: evaluator.power.ieee69_restoration_resilience.default
run_status: completed
started_at: '2026-04-22T01:21:35Z'
ended_at: '2026-04-22T01:21:35Z'
attempt_index: 4
trigger_reason: real_renewable-restoration
input_snapshot:
  task:
    object_id: task.power.ieee69_restoration_resilience
    object_version: 0.1.0
  evaluator:
    object_id: evaluator.power.ieee69_restoration_resilience.default
    object_version: 0.1.0
skill_refs:
  used:
  - object_id: skill.power.baseline_solver
    object_version: 0.1.0
  produced:
  - object_id: skill.power.renewable_restoration_candidate_task005
    object_version: 0.1.0
result_summary:
  metrics:
    restored_load_ratio: 0.681211187067485
    unserved_critical_load: 1.121
    constraint_violation: 0
    restoration_action_cost_proxy: 1.5
    isolated_buses:
    - 61
    - 62
    - 63
    - 64
    - 65
    restored_load_mw: 2.58989
    restored_extra_mw: 0.35
  baseline_comparison: improved
  notes: candidate improved restoration result
artifact_refs:
- kind: metrics
  path: runs/task005/run_0004/metrics.json
agent_trace_refs:
- kind: trace
  object_id: agent_trace.power.ieee69_restoration_resilience.0004


### runs/task005/run_0004/metrics.json
{
  "baseline_solution": {
    "control_settings": {
      "strategy": "conservative_restoration"
    },
    "metrics": {
      "restored_load_ratio": 0.5891517113856529,
      "unserved_critical_load": 1.471,
      "constraint_violation": 0,
      "restoration_action_cost_proxy": 0.0,
      "isolated_buses": [
        61,
        62,
        63,
        64,
        65
      ],
      "restored_load_mw": 2.23989
    }
  },
  "candidate_solution": {
    "control_settings": {
      "strategy": "renewable_island_support"
    },
    "metrics": {
      "restored_load_ratio": 0.681211187067485,
      "unserved_critical_load": 1.121,
      "constraint_violation": 0,
      "restoration_action_cost_proxy": 1.5,
      "isolated_buses": [
        61,
        62,
        63,
        64,
        65
      ],
      "restored_load_mw": 2.58989,
      "restored_extra_mw": 0.35
    }
  },
  "evaluation": {
    "passed": true,
    "key_metrics_pass": true,
    "constraints_pass": true,
    "comparisons": {
      "restored_load_ratio": {
        "candidate": 0.681211187067485,
        "baseline": 0.5891517113856529,
        "direction": "higher_is_better",
        "improved": true,
        "delta": 0.09205947568183204
      },
      "unserved_critical_load": {
        "candidate": 1.121,
        "baseline": 1.471,
        "direction": "lower_is_better",
        "improved": true,
        "delta": -0.3500000000000001
      },
      "constraint_violation": {
        "candidate": 0,
        "baseline": 0,
        "direction": "constraint_only",
        "improved": true,
        "delta": 0
      },
      "restoration_action_cost_proxy": {
        "candidate": 1.5,
        "baseline": 0.0,
        "direction": "lower_is_better",
        "improved": false,
        "acceptable": true,
        "delt

### runs/task005/run_0004/taste_assessment.yaml
schema_version: 0.1.0
object_type: taste_assessment
object_id: taste.power.ieee69_restoration_resilience.0004
object_version: 0.1.0
created_at: '2026-04-22T01:21:35Z'
updated_at: '2026-04-22T01:21:35Z'
status: reviewed
metadata:
  mismatch_type: ''
task_ref: task.power.ieee69_restoration_resilience
run_refs:
- run.power.ieee69_restoration_resilience.0004
grade: zhuoshi
grade_reasoning: task005 candidate 在当前 fault 场景下提高了恢复结果。
claim_ceiling: 只能报告当前 fault 场景与动作集合下的恢复结果变化。
recommended_report_type: technical_note
evidence_refs:
- evidence.power.ieee69_restoration_resilience.0004
review_status: reviewed


### runs/task005/run_0004/report.yaml
schema_version: 0.1.0
object_type: report
object_id: report.power.ieee69_restoration_resilience.note_0004
object_version: 0.1.0
created_at: '2026-04-22T01:21:35Z'
updated_at: '2026-04-22T01:21:35Z'
status: reviewed
metadata:
  mismatch_type: ''
task_ref: task.power.ieee69_restoration_resilience
report_type: technical_note
title: task005 real renewable-restoration report 0004
summary: task005 candidate 在当前 fault 场景下改善了局部恢复结果。
evidence_bundle_refs:
- evidence.power.ieee69_restoration_resilience.0004
taste_assessment_ref: taste.power.ieee69_restoration_resilience.0004
audience: internal_team
boundary_statement: 本报告仅对应当前单故障单工况与动作集合下的局部恢复结果，不构成系统普适韧性结论。
failure_summary: null
next_steps:
- 增加 resilience overclaim checker
- 增加更丰富恢复动作
claim_summary:
- 只能报告当前 fault 场景与动作集合下的恢复结果变化。


### analysis/task005/semantic_0002/strategy_semantic_comparison.yaml
schema_version: 0.1.0
object_type: strategy_semantic_comparison
object_id: semantic_comparison.power.ieee69_restoration_resilience.0002
object_version: 0.1.0
created_at: '2026-04-22T00:25:12Z'
updated_at: '2026-04-22T00:25:12Z'
status: reviewed
metadata: {}
task_ref: task.power.ieee69_restoration_resilience
left_run_ref: run.power.ieee69_restoration_resilience.0001
right_run_ref: run.power.ieee69_restoration_resilience.0003
left_skill_ref: skill.power.renewable_restoration_candidate_task005
right_skill_ref: skill.power.renewable_underperformer_task005
semantic_dimensions:
  problem_alignment:
    left: high
    right: high
    winner: tie
  research_value:
    left: high
    right: medium
    winner: left
  control_realism:
    left: high
    right: medium
    winner: left
  reuse_potential:
    left: high
    right: medium
    winner: left
  method_family:
    left: renewable_restoration_support
    right: renewable_restoration_support
    winner: tie
  control_signature:
    left: restoration_support
    right: restoration_support
    winner: tie
  resilience_awareness:
    left: high
    right: high
    winner: tie
  restoration_scope_match:
    left: high
    right: high
    winner: tie
  critical_load_relevance:
    left: high
    right: high
    winner: tie
  performance_status:
    left: successful
    right: failed
    winner: left
preferred_for_research_ref: run.power.ieee69_restoration_resilience.0001
summary: task005 语义比较完成：已显式区分恢复候选与稳态结果失配。
notes:
- strategy=renewable_island_support
- restored_load_ratio=0.681211187067485
- 语义正确但恢复结果未优于 baseline


## Predecessor Output Excerpts