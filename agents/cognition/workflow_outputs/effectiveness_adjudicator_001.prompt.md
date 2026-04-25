# Effectiveness Adjudicator Agent

## Role

You adjudicate between effectiveness proposer and counter outputs, producing a final bounded deliverable recommendation.

## Required Output

- same JSON structure as semantic/literature adjudicator, including:
  - `accepted_interpretation`
  - `rejected_interpretation`
  - `claim_ceiling_recommendation`

## Rules

- Produce a final route: internal report / patent candidate / paper candidate / continue research / not ready.
- The output must remain bounded to evidence and validation coverage.


## Job
{
  "schema_version": "0.1.0",
  "object_type": "llm_cognition_job",
  "job_id": "effectiveness_adjudicator_001",
  "workflow_id": "effectiveness_workflow_001",
  "workflow_role": "adjudicator",
  "created_at": "2026-04-22T02:58:32Z",
  "agent_role": "effectiveness_adjudicator",
  "prompt_ref": "agents/cognition/prompts/effectiveness_adjudicator.md",
  "input_refs": [
    "effectiveness/task003/validation_plan.yaml",
    "effectiveness/task003/application_assessment.yaml",
    "effectiveness/task003/deliverable_package.yaml",
    "effectiveness/task003/claim_routing.yaml",
    "effectiveness/task004/validation_plan.yaml",
    "effectiveness/task004/application_assessment.yaml",
    "effectiveness/task004/deliverable_package.yaml",
    "effectiveness/task004/claim_routing.yaml"
  ],
  "predecessor_output_refs": [
    "agents/cognition/outputs/effectiveness_proposer_001.json",
    "agents/cognition/outputs/effectiveness_counter_001.json",
    "effectiveness/task003/claim_routing.yaml",
    "effectiveness/task004/claim_routing.yaml"
  ],
  "expected_output_schema": "agents/cognition/workflow_spec.yaml"
}

## Input Artifact Excerpts
### effectiveness/task003/validation_plan.yaml
schema_version: "0.1.0"
object_type: "validation_plan"
object_id: "validation.power.task003.validation_plan"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_renewable_reactive_opt"
covered_dimensions:
  - "baseline coverage"
  - "candidate coverage"
  - "failure coverage"
  - "literature support"
  - "explanation support"
missing_dimensions:
  - "multi-scenario renewable variation"
  - "shunt + inverter coordinated candidate"
  - "engineering cost validation"
blocking_for:
  paper_candidate:
    - "multi-scenario renewable variation"
  patent_candidate: []
  internal_report_ready: []
summary: "task003 已具备内部报告和方法线索交付条件，但尚不足以支撑完整论文级结论。"


### effectiveness/task003/application_assessment.yaml
schema_version: "0.1.0"
object_type: "application_assessment"
object_id: "application.power.task003"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_renewable_reactive_opt"
applicable_scenarios:
  - "单代表工况下的 PV inverter 无功支撑方法验证"
  - "新能源接入控制对象建模与评估流程验证"
not_applicable_scenarios:
  - "长期新能源波动控制"
  - "工程级多设备协调调度"
  - "经济性最优调控"
application_value: "可作为新能源 inverter reactive support 方法原型与研究任务接入案例。"
limitations:
  - "单工况"
  - "简化 inverter Q 控制"
  - "未覆盖协调控制"


### effectiveness/task003/deliverable_package.yaml
schema_version: "0.1.0"
object_type: "deliverable_package"
object_id: "deliverable.power.task003"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_renewable_reactive_opt"
readiness_level: "patent_candidate"
supported_outputs:
  - "internal_report_ready"
  - "patent_candidate"
not_ready_outputs:
  - "paper_candidate"
supporting_refs:
  - "run.power.ieee69_renewable_reactive_opt.0001"
  - "cognition_upgrade.power.ieee69_renewable_reactive_opt.0006"
missing_for_paper:
  - "multi-scenario validation"
  - "stronger coordinated candidate"
summary: "task003 当前更适合内部报告和方法/技术路线型专利线索，不足以直接作为完整论文候选。"


### effectiveness/task003/claim_routing.yaml
schema_version: "0.1.0"
object_type: "claim_routing"
object_id: "claim_routing.power.task003"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_renewable_reactive_opt"
route: "patent_candidate"
allowed_claims:
  - "当前单代表工况下 inverter reactive support 可改善局部指标"
  - "显式使用 inverter 控制空间是回答新能源任务本体的重要条件"
forbidden_claims:
  - "普适新能源 Volt/Var 最优控制方法"
  - "完整工程级协调控制方案"
next_actions:
  - "补多工况验证"
  - "补 shunt + inverter 协同 candidate"


### effectiveness/task004/validation_plan.yaml
schema_version: "0.1.0"
object_type: "validation_plan"
object_id: "validation.power.task004.validation_plan"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_hosting_capacity"
covered_dimensions:
  - "baseline coverage"
  - "candidate coverage"
  - "failure coverage"
  - "boundary coverage"
  - "literature support"
  - "explanation support"
missing_dimensions:
  - "larger scan envelope"
  - "multi-scenario hosting capacity"
  - "engineering-standard voltage threshold validation"
blocking_for:
  paper_candidate:
    - "multi-scenario hosting capacity"
  patent_candidate:
    - "stronger control strategy novelty"
  internal_report_ready: []
summary: "task004 已具备边界研究内部报告条件，但仍不足以支撑论文或专利级成果。"


### effectiveness/task004/application_assessment.yaml
schema_version: "0.1.0"
object_type: "application_assessment"
object_id: "application.power.task004"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_hosting_capacity"
applicable_scenarios:
  - "静态 screening 层的新能源接入边界评估"
  - "控制策略相关 hosting capacity 概念验证"
not_applicable_scenarios:
  - "系统真实极限承载力"
  - "长期时序承载力"
  - "工程标准级规划结论"
application_value: "可作为承载力评估框架原型和边界 claim 控制样例。"
limitations:
  - "扫描包络有限"
  - "单工况"
  - "screening threshold 非工程最终标准"


### effectiveness/task004/deliverable_package.yaml
schema_version: "0.1.0"
object_type: "deliverable_package"
object_id: "deliverable.power.task004"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_hosting_capacity"
readiness_level: "internal_report_ready"
supported_outputs:
  - "internal_report_ready"
not_ready_outputs:
  - "patent_candidate"
  - "paper_candidate"
supporting_refs:
  - "run.power.ieee69_hosting_capacity.0001"
  - "cognition_upgrade.power.ieee69_hosting_capacity.0002"
missing_for_paper:
  - "multi-scenario hosting capacity"
  - "actual boundary-triggering envelope"
  - "stronger external benchmark"
summary: "task004 当前适合内部报告和框架验证材料，不足以作为论文或专利候选。"


### effectiveness/task004/claim_routing.yaml
schema_version: "0.1.0"
object_type: "claim_routing"
object_id: "claim_routing.power.task004"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_hosting_capacity"
route: "internal_report_ready"
allowed_claims:
  - "当前扫描包络内可形成控制策略相关的静态承载力边界判断"
  - "单点运行结果不能替代承载力边界扫描"
forbidden_claims:
  - "系统固有唯一承载力"
  - "长期时序承载力"
  - "工程标准级承载力结论"
next_actions:
  - "扩展 scan envelope"
  - "补多工况验证"
  - "补更强控制策略"


## Predecessor Output Excerpts
### effectiveness/task003/claim_routing.yaml
schema_version: "0.1.0"
object_type: "claim_routing"
object_id: "claim_routing.power.task003"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_renewable_reactive_opt"
route: "patent_candidate"
allowed_claims:
  - "当前单代表工况下 inverter reactive support 可改善局部指标"
  - "显式使用 inverter 控制空间是回答新能源任务本体的重要条件"
forbidden_claims:
  - "普适新能源 Volt/Var 最优控制方法"
  - "完整工程级协调控制方案"
next_actions:
  - "补多工况验证"
  - "补 shunt + inverter 协同 candidate"


### effectiveness/task004/claim_routing.yaml
schema_version: "0.1.0"
object_type: "claim_routing"
object_id: "claim_routing.power.task004"
created_at: "2026-04-22T00:00:00Z"
status: "reviewed"
task_ref: "task.power.ieee69_hosting_capacity"
route: "internal_report_ready"
allowed_claims:
  - "当前扫描包络内可形成控制策略相关的静态承载力边界判断"
  - "单点运行结果不能替代承载力边界扫描"
forbidden_claims:
  - "系统固有唯一承载力"
  - "长期时序承载力"
  - "工程标准级承载力结论"
next_actions:
  - "扩展 scan envelope"
  - "补多工况验证"
  - "补更强控制策略"

