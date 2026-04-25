# Literature Reviewer Agent

## Role

You review literature and explanation alignment quality. Your job is to detect superficial similarity, novelty overclaim, and missing literature signals.

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

- Do not assume keyword similarity means method equivalence.
- Ground every judgment in listed literature/explanation artifacts.
- If current literature seed coverage is weak, say so.
- Do not invent papers or citations.


## Job
{
  "schema_version": "0.1.0",
  "object_type": "llm_cognition_job",
  "job_id": "task004_literature_reviewer_001",
  "created_at": "2026-04-22T07:43:48Z",
  "agent_role": "literature_reviewer",
  "prompt_ref": "agents/cognition/prompts/literature_reviewer.md",
  "input_refs": [
    "analysis/task004/literature_0002/literature_alignment.yaml",
    "analysis/task004/explanations_0002/explanation_alignment.yaml",
    "analysis/task004/upgrade_0002/cognition_upgrade.yaml"
  ],
  "rule_baseline_refs": [
    "analysis/task004/upgrade_0002/cognition_upgrade.yaml"
  ],
  "expected_output_schema": "agents/cognition/job_spec.yaml"
}

## Artifact Excerpts
### analysis/task004/literature_0002/literature_alignment.yaml
schema_version: 0.1.0
object_type: literature_alignment
object_id: literature_alignment.power.ieee69_hosting_capacity.0002
object_version: 0.1.0
created_at: '2026-04-21T06:30:05Z'
updated_at: '2026-04-21T06:30:05Z'
status: reviewed
metadata: {}
task_ref: task.power.ieee69_hosting_capacity
assessed_object_refs:
- skill.power.renewable_capacity_optimizer_task004
- skill.power.single_point_capacity_mismatch_task004
literature_refs:
- paper.hosting_capacity_pv_2017
- paper.smart_inverter_hosting_2020
- paper.hosting_capacity_method_review_2021
- paper.single_point_operation_2019
method_mappings:
  skill.power.renewable_capacity_optimizer_task004:
  - paper.hosting_capacity_pv_2017
  - paper.smart_inverter_hosting_2020
  - paper.hosting_capacity_method_review_2021
  skill.power.single_point_capacity_mismatch_task004:
  - paper.single_point_operation_2019
theory_mappings:
  hosting_capacity_strategy_scan: hosting_capacity_assessment
  single_point_operating_evaluation: operating_point_analysis
novelty_position: variant
alignment_summary: 当前对齐表明，task004 的边界扫描路线更接近 hosting capacity assessment 家族，而 single-point
  mismatch 路线更接近 operating-point analysis，不能直接替代边界评估。
notes:
- 当前只基于种子文献做方法家族级对齐
- 尚未进行片段级解释对齐


### analysis/task004/explanations_0002/explanation_alignment.yaml
schema_version: 0.1.0
object_type: explanation_alignment
object_id: explanation_alignment.power.ieee69_hosting_capacity.0002
object_version: 0.1.0
created_at: '2026-04-21T06:30:30Z'
updated_at: '2026-04-21T06:30:30Z'
status: reviewed
metadata: {}
task_ref: task.power.ieee69_hosting_capacity
assessed_cognition_ref: cognition.power.upgraded_ieee69_hosting_capacity_0001
explanation_card_refs:
- explanation_card.power.hosting_capacity_pv_2017
- explanation_card.power.smart_inverter_hosting_2020
- explanation_card.power.hosting_capacity_method_review_2021
- explanation_card.power.single_point_operation_2019
per_card_relations:
  explanation_card.power.hosting_capacity_pv_2017:
    paper_ref: paper_record.power.hosting_capacity_pv_2017
    relation: supports
    reason: 存在直接指向补偿配置/问题本体的解释片段，可作为支持证据。
    explanation_points:
    - Boundary judgments must remain conditioned on scenario and constraints.
    - Voltage screening is a common first boundary.
    relation_counts:
      supports: 3
      supplements: 0
      similar: 0
      conflicts: 0
      unclear: 0
    excerpt_relations:
    - excerpt_ref: paper_excerpt.power.hosting_capacity_pv_2017.explanation
      granularity: summary
      source_ref: literature_source.power.hosting_capacity_pv_2017.abstract
      source_kind: abstract_excerpt
      evidence_strength: medium
      relation: supports
      reason: 片段文本直接涉及承载力边界定义，可作为支持证据。
      evidence_basis: excerpt_content
      content: The hosting-capacity boundary only has meaning when the scenario and
        triggering constraints are explicitly stated.
    - excerpt_ref: paper_excerpt.power.hosting_capacity_pv_2017.explanation_point_1
      granularity: point
      source_ref: literature_source.power.hosting_capacity_pv_2017.abstract
      source_kind: abstract_excerpt
      evidence_strength: medium
      relation: supports
      reason: 片段文本直接涉及承载力边界定义，可作为支持证据。
      evidence_basis: excerpt_content
      content: Boundary judgments must remain conditioned on sc

### analysis/task004/upgrade_0002/cognition_upgrade.yaml
schema_version: 0.1.0
object_type: cognition_upgrade
object_id: cognition_upgrade.power.ieee69_hosting_capacity.0002
object_version: 0.1.0
created_at: '2026-04-21T06:30:55Z'
updated_at: '2026-04-21T06:30:55Z'
status: reviewed
metadata:
  mode: task004_boundary_cognition
task_ref: task.power.ieee69_hosting_capacity
source_cognition_ref: cognition.power.strategy_comparison_ieee69_hosting_capacity_0002
semantic_comparison_ref: semantic_comparison.power.ieee69_hosting_capacity.0002
novelty_assessment_ref: novelty.power.ieee69_hosting_capacity.0002
literature_alignment_ref: literature_alignment.power.ieee69_hosting_capacity.0002
explanation_alignment_ref: explanation_alignment.power.ieee69_hosting_capacity.0002
explanation_excerpt_refs:
- paper_excerpt.power.hosting_capacity_pv_2017.explanation
- paper_excerpt.power.hosting_capacity_pv_2017.explanation_point_1
- paper_excerpt.power.hosting_capacity_pv_2017.explanation_point_2
- paper_excerpt.power.smart_inverter_hosting_2020.explanation
- paper_excerpt.power.smart_inverter_hosting_2020.explanation_point_1
- paper_excerpt.power.smart_inverter_hosting_2020.explanation_point_2
- paper_excerpt.power.hosting_capacity_method_review_2021.explanation
- paper_excerpt.power.single_point_operation_2019.explanation
- paper_excerpt.power.single_point_operation_2019.explanation_point_1
upgraded_cognition_ref: cognition.power.upgraded_ieee69_hosting_capacity_0002
evidence_strength: medium
decision: upgrade
rationale: 承载力评估必须以边界扫描为对象，单点运行结果不能替代条件化边界判断。 当前文献对齐将其定位为 `variant`。 explanation alignment
  提供了 9 条 excerpt 级证据，evidence_strength=`medium`。
claim_adjustment: task004 边界认知只支持当前扫描包络内、给定控制策略下的静态边界判断。

