# Task Adapter Contract

## 1. 文档目的

本规范定义 `task adapter` 的最小职责、字段边界和接入要求。

它的目标是让新 task 的接入变成“补一个薄 adapter”，而不是“重写一套 loop”。

## 2. 定位

`task adapter` 是 task-facing binding layer。

它位于：

- 上游：task definition、baseline、candidate、evaluator 等 task-specific 资源
- 下游：generic loop engine 和 generic diagnosis layer

它的责任是把 task-specific 事实组织成通用 contract，而不是承接编排或归因工作。

## 3. adapter 允许做什么

adapter 允许：

- 提供 task definition 引用
- 提供 baseline binding
- 提供 candidate binding
- 提供 evaluator binding
- 提供 search envelope
- 提供 task-specific diagnosis hook 输入
- 提供 task execution context 的最小组装

adapter 不允许：

- 重写 loop 状态机
- 直接做 evaluator judgment
- 直接输出 cognition diagnosis
- 直接给出下一轮 skill 修改方案
- 把 controller 逻辑搬进 task adapter

## 4. 薄 adapter 原则

adapter 必须薄，薄的含义是：

- 主要做绑定，不做 authoring
- 主要交付引用和上下文，不交付 judgment
- 主要声明边界，不实现闭环策略

出现以下情况时，说明 adapter 已过厚：

1. adapter 内含多阶段状态跳转逻辑
2. adapter 内直接判断“这是 skill-structure 问题”
3. adapter 内直接判断 candidate 是否有效
4. adapter 内直接决定下一轮参数或 prompt 修改
5. adapter 为某一 task 实现了专用 loop 分支

## 5. 最小字段契约

每个 task adapter 至少应提供以下核心字段：

- `schema_version`
- `object_type`
- `object_id`
- `object_version`
- `task_ref`
- `task_definition_ref`
- `baseline_binding`
- `candidate_binding`
- `evaluator_binding`
- `search_envelope`
- `diagnosis_hook_config`
- `workspace_binding`
- `metadata`

## 6. 字段语义

### 6.1 task_ref

指向该 adapter 服务的稳定 task 身份。

要求：

- 一个 adapter 只服务一个明确 task scope
- 不得用文件路径代替 task identity

### 6.2 task_definition_ref

指向 task definition 对象或等价任务包。

作用：

- 向 loop engine 提供研究对象、边界、约束和成功意图

要求：

- task definition 必须先于 adapter 存在
- adapter 不得改写 task 定义本体

### 6.3 baseline_binding

定义 baseline 从哪里来、如何取到、如何被 evaluator 使用。

至少应包含：

- `baseline_refs`
- `selection_rule`
- `comparison_scope`

要求：

- baseline 选择逻辑必须显式
- 不得在 loop engine 中重新猜 baseline

### 6.4 candidate_binding

定义 candidate 如何被创建、定位、命名和交给 evaluator。

至少应包含：

- `candidate_kind`
- `candidate_locator`
- `materialization_rule`
- `artifact_expectations`

要求：

- 不得把 candidate 的创建逻辑写成 task-specific loop 代码
- 允许声明 candidate 的落盘与命名规则

### 6.5 evaluator_binding

定义该 task 使用哪个 evaluator，以及 evaluator 的执行入口和输入适配方式。

至少应包含：

- `evaluator_ref`
- `execution_entry`
- `input_mapping`
- `output_mapping`

要求：

- evaluator judgment 仍由 effectiveness worker 负责
- adapter 只做绑定与映射

### 6.6 search_envelope

定义本 task 允许搜索或变更的空间边界。

至少应包含：

- `modifiable_dimensions`
- `frozen_dimensions`
- `budget_constraints`
- `termination_hints`

作用：

- 防止 skill worker 无边界扩散
- 为 diagnosis layer 判断“该扩 search envelope 还是该修 skill”提供依据

### 6.7 diagnosis_hook_config

为 diagnosis layer 提供 task-specific 解释所需的最小钩子输入。

至少应包含：

- `expected_failure_modes`
- `task_specific_blind_spots`
- `adapter_level_checks`

要求：

- 这里是提示 diagnosis 该看什么，不是直接给 diagnosis 结论
- 不得写成“如果 A 就是 skill-use，如果 B 就是 evaluator-design”的硬编码结论器

### 6.8 workspace_binding

定义本 task 在 run workspace 中的输入输出组织方式。

至少应包含：

- `input_roots`
- `output_roots`
- `naming_convention`

要求：

- 只能规定 task-specific 数据在哪里
- 不得重定义框架级 artifacts 目录职责

## 7. 输入输出边界

### 7.1 adapter 输入

adapter 的上游输入至少包括：

- task definition
- baseline definition 或 baseline refs
- evaluator definition
- task-specific execution resources

### 7.2 adapter 输出

adapter 向 loop engine 至少输出：

- 可执行的 task package
- baseline binding package
- candidate binding package
- evaluator binding package
- diagnosis hook package

### 7.3 adapter 不输出的内容

adapter 不得输出：

- `effectiveness_assessment`
- `cognition_diagnosis`
- `loop_routing_decision`

这些对象分别属于 effectiveness worker、cognition worker 和 controller。

## 8. 与 diagnosis layer 的关系

adapter 只向 diagnosis layer 提供：

- task-specific 上下文
- blind spot 提示
- adapter-level 自检项

adapter 不得：

- 替 diagnosis 归因
- 替 diagnosis 决定下一轮 worker
- 替 diagnosis 决定暂停或继续 loop

## 9. 与 loop engine 的关系

loop engine 对 adapter 的唯一合法使用方式是：

1. 读取 contract
2. 获取 task-specific binding
3. 将 binding 交给对应 worker
4. 在 routing 时只依赖 worker 输出与 policy

engine 不得：

- 绕过 adapter 直接读取 task-specific 实现细节
- 在 engine 内部补写 adapter 应提供的绑定信息

## 10. 最小样例形态

```yaml
schema_version: "0.1"
object_type: "task_adapter"
object_id: "task_adapter.power.task004"
object_version: "0.1.0"
task_ref: "task.power.task004"
task_definition_ref: "task.power.task004"
baseline_binding:
  baseline_refs:
    - "baseline.power.task004.default"
  selection_rule: "fixed_default"
  comparison_scope: "same_task_same_evaluator"
candidate_binding:
  candidate_kind: "skill_variant"
  candidate_locator: "tasks/task004/candidates/"
  materialization_rule: "worker_writes_candidate_then_registers_ref"
  artifact_expectations:
    - "skill_change_result"
evaluator_binding:
  evaluator_ref: "evaluator.power.task004.default"
  execution_entry:
    type: "python_script"
    path: "evaluators/task004_evaluator.py"
  input_mapping: {}
  output_mapping: {}
search_envelope:
  modifiable_dimensions:
    - "skill_prompt"
    - "skill_parameters"
  frozen_dimensions:
    - "task_definition"
    - "evaluator_logic"
  budget_constraints:
    max_iterations: 5
diagnosis_hook_config:
  expected_failure_modes:
    - "candidate_not_materialized"
    - "evaluator_signal_ambiguous"
  task_specific_blind_spots:
    - "baseline_may_be_too_weak"
  adapter_level_checks:
    - "baseline_and_candidate_use_same_evaluator"
workspace_binding:
  input_roots:
    - "tasks/task004/"
  output_roots:
    - "runs/task004/"
  naming_convention: "task_scoped_serial"
metadata: {}
```

## 11. adapter 校验规则

一个 adapter 至少应满足以下校验：

1. 能明确指出 task definition
2. 能明确指出 baseline 与 evaluator
3. search envelope 显式存在
4. diagnosis hook 只提供输入，不直接给结论
5. 不包含 loop phase branching 逻辑

出现以下情况时应判为不合格：

1. adapter 内嵌 evaluator 结果判断
2. adapter 直接输出 cognition diagnosis
3. adapter 通过 task-specific if/else 重写 loop 分支
4. adapter 未声明 baseline binding 就要求比较改进

## 12. 对后续实现的约束

后续实现任何 task adapter 时，都必须能回答：

1. 这个 task 的 baseline 是谁
2. 这个 task 的 candidate 怎样被 materialize
3. evaluator 怎么绑定
4. search envelope 的边界在哪里
5. diagnosis layer 需要哪些 task-specific hook 输入

若答不清这些问题，就说明该 task 还没有准备好接入 generic loop engine。
