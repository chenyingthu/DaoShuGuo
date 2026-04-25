# Generic Diagnosis Layer Spec

## 1. 文档目的

本规范定义 `generic diagnosis layer` 的职责、输入输出、分类体系和 routing 约束。

该层的任务不是写“总结报告”，而是在证据约束下判断问题归属，并决定下一轮应交给哪个 worker 或是否应暂停 loop。

## 2. 定位

`generic diagnosis layer` 位于：

- 上游：`skill_change_request`、`skill_change_result`、`effectiveness_assessment`
- 下游：`loop_routing_decision`

它是 worker judgment layer，不是 controller，也不是 task adapter。

## 3. 核心职责

diagnosis layer 必须负责：

- 读取当前轮 worker 对象链
- 判断当前问题主要归属
- 明确证据是否足够
- 判断是否继续 skill evolution
- 给出下一轮推荐 worker 类型
- 给出暂停、修复或扩边界建议

它不负责：

- 直接修改 skill
- 直接执行 evaluator
- 直接改 task definition
- 直接生成 controller routing 结果

## 4. controller 与 diagnosis 的边界

### 4.1 diagnosis 负责 judgment

diagnosis 负责回答：

- 这是哪类问题
- 为什么这样判断
- 证据来自哪里
- 下一步更适合哪个 worker
- 是否应该暂停 loop

### 4.2 controller 负责 routing

controller 只负责回答：

- 根据 diagnosis 和 policy，下一步走哪条路
- 是否允许进入下一轮

因此：

- diagnosis 可以建议 `pause_skill_evolution`
- controller 可以据此写 `loop_routing_decision`
- controller 不能跳过 diagnosis 自己写“这是 evaluator 问题”

## 5. 输入契约

diagnosis layer 至少读取以下输入：

- `skill_change_request`
- `skill_change_result`
- `effectiveness_assessment`
- `task_adapter` 提供的 `diagnosis_hook_config`
- `artifact_chain_verification_result`

必要时可补充：

- 历史轮次摘要
- search envelope 摘要
- baseline/evaluator 元信息

但不得绕过对象链，直接把高层报告当成原始证据。

## 6. 输出契约

diagnosis layer 至少输出两个对象：

1. `cognition_diagnosis`
2. `cognition_to_skill_update` 或等价建议块

其中 Phase 1 最低要求是先固定 `cognition_diagnosis` 的语义结构。

`cognition_diagnosis` 至少应包含：

- `problem_class`
- `judgment_summary`
- `evidence_refs`
- `boundary_notes`
- `uncertainty_notes`
- `recommended_next_worker`
- `recommended_action`
- `continue_loop`

## 7. 标准问题分类

Phase 1 固定以下五类问题归属：

1. `framework_problem`
2. `task_adapter_problem`
3. `skill_use_problem`
4. `skill_structure_problem`
5. `evaluator_design_problem`

### 7.1 framework_problem

定义：

- 框架层对象缺失
- 阶段绑定错误
- controller overreach
- 运行状态机失配

典型信号：

- worker 对象链不完整
- routing decision 未引用 diagnosis
- candidate 未被规范 materialize

推荐动作：

- 先修框架，不继续 skill evolution

### 7.2 task_adapter_problem

定义：

- baseline binding、candidate binding、evaluator binding、search envelope 或 diagnosis hook 提供不当

典型信号：

- baseline 选择不一致
- candidate 和 evaluator 输入不匹配
- search envelope 约束失真
- diagnosis hook 缺少关键 task-specific blind spot

推荐动作：

- 先修 adapter，不继续解释为 skill 问题

### 7.3 skill_use_problem

定义：

- 技能本身可能可用，但本轮使用方式、组合方式或输入设置不当

典型信号：

- skill candidate 明显未按适用条件使用
- 参数、prompt、调用顺序错误
- 同一 skill 在相近条件下历史上可工作，本轮失效主要来自调用方式

推荐动作：

- 继续 skill evolution，但重点修正使用策略

### 7.4 skill_structure_problem

定义：

- 当前 skill 的结构、能力边界或实现方式不足，单纯改调用方式难以解决

典型信号：

- 多轮合理使用后仍无法满足 evaluator
- failure pattern 稳定重复
- search envelope 内的轻量改动无效

推荐动作：

- 发起新的 skill change request，进行结构性修改

### 7.5 evaluator_design_problem

定义：

- evaluator 自身存在盲区、信号失真、比较不公平或成功判据不可靠

典型信号：

- baseline/candidate 无法公平比较
- 关键指标与任务价值错位
- evaluator 输出波动过大，难以支持稳定判断
- worker 结果与 evaluator 结论明显冲突

推荐动作：

- 暂停 skill evolution，先修 evaluator 或补基线

## 8. 诊断方法

diagnosis layer 的标准工作顺序应为：

1. 检查对象链是否完整
2. 检查 controller 是否 overreach
3. 检查 adapter binding 是否成立
4. 检查 evaluator 信号是否可信
5. 最后再判断 skill-use 或 skill-structure

原因：

- 若框架层或 evaluator 层先出错，把问题归到 skill 上通常是误诊

## 9. 证据规则

每条 diagnosis 必须满足：

1. 有对象级 `evidence_refs`
2. 区分事实、解释和建议
3. 显式写出边界与不确定性
4. 不以报告摘要代替原始对象

最低证据来源建议包括：

- `skill_change_request`
- `skill_change_result`
- `effectiveness_assessment`

若缺少上述任意关键对象，diagnosis 应优先输出：

- `insufficient_evidence`

而不是强行分类。

## 10. continue / stop 规则

diagnosis layer 必须显式支持“拒绝继续 loop”。

### 10.1 应继续 skill evolution 的情况

- 证据表明主要是 `skill_use_problem`
- 证据表明主要是 `skill_structure_problem`
- evaluator 和 adapter 基本可信

### 10.2 应暂停 skill evolution 的情况

- `framework_problem`
- `task_adapter_problem`
- `evaluator_design_problem`
- 证据不足

### 10.3 应扩 search envelope 的情况

- skill-use 与 skill-structure 都不完全成立
- 当前 envelope 太窄，导致无法测试关键假设
- 但 evaluator 与 adapter 本身仍可信

## 11. recommended_next_worker 规则

诊断层输出的 `recommended_next_worker` 建议至少支持：

- `skill_worker`
- `effectiveness_worker`
- `cognition_worker`
- `adapter_repair_worker`
- `framework_repair_worker`
- `human_review`

说明：

- `human_review` 用于高歧义或高风险情况
- controller 只能从这些建议中做 policy-constrained routing，不能发明新判断

## 12. 最小对象形态

```yaml
schema_version: "0.1"
object_type: "cognition_diagnosis"
object_id: "cognition.power.task004.run0007"
object_version: "0.1.0"
problem_class: "evaluator_design_problem"
judgment_summary: "当前评估信号不足以区分 candidate 失效与 evaluator 盲区。"
evidence_refs:
  - "skill_change_request.power.task004.run0007"
  - "skill_change_result.power.task004.run0007"
  - "effectiveness_assessment.power.task004.run0007"
boundary_notes:
  - "当前判断仅适用于 task004 当前 evaluator 配置。"
uncertainty_notes:
  - "尚未完成替代 evaluator 复核。"
recommended_next_worker: "adapter_repair_worker"
recommended_action: "检查 baseline/evaluator 绑定并补充 blind_spot 说明。"
continue_loop: false
metadata: {}
```

## 13. 与 worker 边界规范的对齐

本层必须严格对齐 [loop-worker-boundary-spec.md](/home/chenying/root-research/DaoShuGuo-v1/docs/loop-worker-boundary-spec.md)：

- diagnosis judgment 不能由 controller 代写
- diagnosis 必须引用 worker 产物
- routing 决定必须晚于 diagnosis

因此，若发现以下模式，应直接标记为 `framework_problem`：

1. controller 直接写“这是 skill-structure 问题”
2. controller 跳过 diagnosis 直接指定下一轮技能修改
3. diagnosis 没有任何 worker 证据引用

## 14. 对后续实现的约束

后续任何 diagnosis 实现都必须满足：

1. 先查框架与 adapter，再判断 skill
2. 可输出 `continue_loop: false`
3. 问题分类固定在五类主类中
4. 每条判断都要带 evidence refs
5. 不把 diagnosis 写成报告性空话

若不满足以上约束，该实现只能视为：

- 结果总结器
- 经验备注器

不能视为：

- generic diagnosis layer
