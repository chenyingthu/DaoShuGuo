# 技能-认知闭环计划：从技能探索到认知反馈再到技能进化

## 1. 计划目标

本计划的目标不是简单增加更多技能，也不是让认知层继续写更多评论，而是建立项目中真正关键的闭环：

> 让技能（术）与认知（道）之间形成一个持续迭代、相互塑造、不断走向更高更强更深刻的研究循环。

这里的核心不是：

- skill 做完之后写一段 cognition
- cognition 写完之后再试一个 skill

而是：

> cognition 必须显式改变下一轮 skill 的搜索空间、约束空间、评估空间与任务空间；  
> skill 必须持续为 cognition 暴露新的现象、失败、冲突和边界。

## 2. 为什么这是当前最关键的一步

到当前阶段，项目已经完成：

- 技能层：
  - task002 / task003 / task004 / task005 的 baseline 与 candidate
  - failure taxonomy
  - 可写回 skill 资产
- 认知层：
  - comparison
  - semantic comparison
  - cognition upgrade
  - literature alignment
  - explanation alignment
- 成效层：
  - validation plan
  - application assessment
  - deliverable routing
- LLM 认知层：
  - single-pass jobs
  - real Codex tests
  - multi-role cognition workflow prototype

但当前仍然有一个本质问题：

> skill、cognition、effectiveness 虽然都存在，但还没有形成真正自推进的双向闭环。

如果不补这一层，系统仍然可能退化为：

- skill 盲试
- cognition 总结
- effectiveness 打分

而不是：

- cognition 驱动更高质量的下一轮技能演化

## 3. 闭环要解决的核心问题

本计划要回答的不是：

- 有没有更多新的 skill

而是：

1. cognition 如何反向改变 skill 的搜索空间
2. 什么时候必须从 skill 层切换到 cognition 层
3. cognition 产出的什么内容可以真正指导下一轮 skill work
4. skill 的哪些现象值得上升为认知事件
5. 如何判断循环是“变强了”，而不是“多绕了一圈”

## 4. 本计划中的基本判断

### 4.1 认知不应直接控制代码细节

认知层不应该直接输出：

- 改哪一行代码
- 把参数改成多少

那样它会退化成弱规划器。

认知层应输出：

- 下一轮允许/禁止什么类型的 skill
- 下一轮优先搜索什么控制空间
- 下一轮必须新增什么比较或验证
- 下一轮必须修正什么 evaluator blind spot
- 下一轮必须收窄或扩大什么 task boundary

也就是说：

> cognition 控制的是 search space，而不是代码行。

### 4.2 技能层的价值不只是“改进结果”

技能层必须同时暴露：

- 新现象
- 新失败
- evaluator blind spot
- task mismatch
- control-space mismatch
- overclaim 风险

这些都应成为 cognition 事件。

### 4.3 loop 必须是事件驱动的

不是每次都固定“做一轮技能 + 做一轮认知”。

而是当以下事件发生时，才强制进入 cognition：

- 指标改善但任务语义存疑
- 指标失败但方向看似合理
- failure 重复出现
- boundary / resilience overclaim 出现
- 新控制空间或新方法家族出现
- 文献对齐结果与本地认知冲突

## 5. 闭环中的关键对象

本计划建议新增一组专门用于循环控制的对象。

### 5.1 cognition_event

用于表达：

- 哪个运行或比较触发了认知工作
- 触发类型是什么

示例类型：

- `metric_semantic_divergence`
- `skill_mismatch_detected`
- `performance_failure_detected`
- `evaluator_blind_spot`
- `claim_overreach_detected`
- `literature_conflict_detected`

### 5.2 cognition_to_skill_update

这是本计划的核心对象。

用于表达：

- cognition 对下一轮 skill 工作施加的约束与偏置

建议字段：

- `task_ref`
- `source_cognition_ref`
- `source_event_ref`
- `next_iteration_skill_constraints`
- `next_iteration_evaluator_constraints`
- `next_iteration_task_refinements`
- `search_priority_updates`
- `blocked_skill_families`
- `required_discriminating_tests`

### 5.3 skill_iteration_plan

用于表达：

- 下一轮 skill work 应围绕哪些受控变化展开

### 5.4 loop_review

用于表达：

- 这一轮 loop 是否真的缩小了盲搜空间
- 是否真的提升了 failure 解释质量
- 是否真的推动了 evaluator 或 task refinement

## 6. 建议的闭环结构

本计划建议把 loop 设计为五层。

### Layer A: Skill Exploration

输入：

- task
- evaluator
- current skill graph
- current cognition_to_skill_update

输出：

- run
- failure
- local improvement
- candidate mutation

### Layer B: Event Extraction

输入：

- runs
- comparisons
- semantic comparisons
- overclaim checks

输出：

- cognition_event

### Layer C: Cognition Work

输入：

- cognition_event
- evidence bundle
- literature alignment
- explanation alignment
- prior cognition graph

输出：

- cognition upgrade
- bounded interpretation
- failure diagnosis
- task refinement proposals

### Layer D: Cognition-to-Skill Controller

输入：

- upgraded cognition
- novelty assessment
- effectiveness review

输出：

- cognition_to_skill_update

### Layer E: Next Skill Iteration

输入：

- cognition_to_skill_update

输出：

- constrained next-round skill plan

## 7. 最重要的新层：Cognition-to-Skill Controller

这是整个闭环的关键。

如果没有这层，认知就仍然只是总结。

它的职责是把 cognition 翻译成：

### 7.1 对 skill 的约束

例如：

- 禁止继续把 `steady_state_operating_adjustment` 当作 `task005` 主恢复 skill
- 在 `task003` 中优先搜索 `inverter_q_support`
- 暂停 `single_point_operating_evaluation` 家族在 `task004` 的主线尝试

### 7.2 对 evaluator 的约束

例如：

- 必须加入 critical load relevance
- 必须加入 resilience claim gate
- 必须把 admissibility 和 efficacy 分开

### 7.3 对 task 的约束

例如：

- 下轮必须补多 fault scenario
- 下轮必须明确 hosting capacity envelope
- 下轮必须把 claim 收窄到特定场景

### 7.4 对实验的约束

例如：

- 必须做 same-island vs cross-island 比较
- 必须补一个 coordination candidate
- 必须补一个 counterexample

## 8. 当前最适合试点这个 loop 的任务

不建议一开始在所有 task 上都做。

推荐试点：

### 8.1 task003

原因：

- 已有明显的 `metric vs task-semantic divergence`
- 已有文献与 explanation alignment
- 特别适合测试：
  - cognition 如何约束下一轮 skill family

### 8.2 task004

原因：

- 已有 boundary overclaim
- 已有 hosting-capacity method family distinction
- 特别适合测试：
  - cognition 如何约束边界表达与控制策略搜索

### 8.3 task005

原因：

- 已有事件驱动恢复问题
- 已有 failure taxonomy
- 特别适合测试：
  - cognition 是否能驱动更好的恢复策略设计

## 9. 推荐第一轮 loop 测试问题

### task003

要回答：

- inverter-support 路线为什么仍应继续，而不是因为数值不敌 weak-shunt 就放弃？

期待的 cognition_to_skill_update：

- 强制下一轮补 `shunt + inverter` 协同 candidate
- 强制 evaluator 把 task semantic admissibility 与 metric efficacy 区分开

### task004

要回答：

- 当前 hosting capacity 结果为什么只能算条件化边界，而不是系统固有承载力？

期待的 cognition_to_skill_update：

- 强制下一轮扩大 scan envelope
- 强制补多场景 hosting capacity 对照
- 强制保留 boundary overclaim gate

### task005

要回答：

- 稳态结果为什么不能替代事件驱动恢复？
- 语义正确但性能失败的恢复策略该如何继续？

期待的 cognition_to_skill_update：

- 强制下一轮比较不同 fault 拓扑
- 强制下一轮把 `critical_load_relevance` 放入 evaluator 主轴
- 强制限制稳态 skill 进入恢复主线

## 10. 推荐测试标准

闭环的成功不能只看“又跑了一轮”。

必须看以下四件事是否变好。

### 10.1 搜索空间是否收缩

判断标准：

- 下一轮 skill 尝试是否更聚焦
- 是否减少明显无效路径

### 10.2 failure 解释是否更清楚

判断标准：

- failure 是否越来越少被归类为未知失败
- 是否越来越多被稳定纳入 taxonomy

### 10.3 evaluator 是否被修正

判断标准：

- cognition 是否推动了 evaluator blind spot 修复

### 10.4 claim 是否更稳

判断标准：

- overclaim 是否减少
- report 是否更贴近证据边界

## 11. 实施步骤

## Phase 1: Loop Object Design

目标：

定义闭环对象和最小字段。

执行内容：

- [x] 定义 `cognition_event`
- [x] 定义 `cognition_to_skill_update`
- [x] 定义 `skill_iteration_plan`
- [x] 定义 `loop_review`

完成判据：

- [x] 闭环中的“流动对象”被明确对象化

## Phase 2: Event Extraction Prototype

目标：

从当前 task003/004/005 artifacts 中自动提取认知事件。

执行内容：

- [x] 为 task003 提取 `metric_semantic_divergence`
- [x] 为 task004 提取 `boundary_overclaim`
- [x] 为 task005 提取 `skill_mismatch` / `performance_failure`

完成判据：

- [x] 至少三类 cognition_event 可被生成

## Phase 3: Cognition-to-Skill Controller Prototype

目标：

实现最小 controller，把 cognition 变成下一轮 skill 约束。

执行内容：

- [x] 为 task003 生成下一轮 skill constraints
- [x] 为 task004 生成下一轮 evaluator/task constraints
- [x] 为 task005 生成下一轮 restoration strategy constraints

完成判据：

- [x] 至少三条 `cognition_to_skill_update` 可被生成

## Phase 4: Controlled Next-Iteration Plans

目标：

让 skill 下一轮工作显式受 cognition 引导。

执行内容：

- [x] 生成 `skill_iteration_plan` for task003
- [x] 生成 `skill_iteration_plan` for task004
- [x] 生成 `skill_iteration_plan` for task005

完成判据：

- [x] 下一轮 skill 计划不再是无约束盲试

## Phase 5: Loop Review

目标：

验证这个 loop 是否真的让系统更强。

执行内容：

- [x] 记录 search-space reduction
- [x] 记录 failure explanation improvement
- [x] 记录 evaluator refinement
- [x] 记录 claim tightening

完成判据：

- [x] 至少在一个任务上证明 loop 不是形式主义

## Phase 6: Integration

目标：

把 loop 纳入现有框架。

执行内容：

- [x] 增加 verifier
- [x] 增加 artifact validation
- [x] 接入 integration checks
- [x] 更新实验记录和设计文档

完成判据：

- [x] skill / cognition / effectiveness / loop 四层形成更高层闭环

## 14. 本轮执行结果

本计划已完成一个 **最小可验证闭环层** 的正式实现，包含：

- `schemas/quality/cognition_event.schema.yaml`
- `schemas/quality/cognition_to_skill_update.schema.yaml`
- `schemas/quality/skill_iteration_plan.schema.yaml`
- `schemas/quality/loop_review.schema.yaml`
- `scripts/build_skill_cognition_loop.py`
- `scripts/verify_skill_cognition_loop.py`
- `analysis/loop/task003/*`
- `analysis/loop/task004/*`
- `analysis/loop/task005/*`

当前实现的性质是：

- 它已经是正式框架层，而不是临时笔记
- 它已经接入 schema 校验、CLI 入口与 integration checks
- 但 `Cognition-to-Skill Controller` 仍是 **bootstrap controller**
- 当前 controller 依据既有 task003/004/005 的比较、upgrade、mismatch、overclaim 资产生成约束
- 它还不是由 LLM cognition workflow 直接闭环地产生下一轮 skill plan

因此，本轮工作完成的是：

> “把认知约束下一轮技能搜索空间” 这一件事，从概念变成了可验证对象流。

而尚未完成的是：

> “让 agent-native cognition worker 直接主导 controller，并驱动真实下一轮 skill 开发”。

## 12. 成功标准

本计划成功的标准不是“多了一层对象”，而是：

1. cognition 能显式约束下一轮 skill work
2. 至少一个 task 的下一轮 skill 计划被认知重写
3. 至少一个 evaluator blind spot 被 loop 推动修正
4. 至少一个 overclaim 风险在下一轮被提前规避
5. 有证据说明 loop 让系统更聚焦、更少盲试

## 13. 风险

### 风险 1：loop 退化成“认知总结 -> 技能继续盲试”

缓解：

- 必须有 `cognition_to_skill_update`

### 风险 2：认知直接控制代码细节

缓解：

- cognition 只控制搜索空间、实验空间、评估空间

### 风险 3：loop 没有变强，只是多了一层 bureaucracy

缓解：

- 必须做 loop review
- 必须证明至少一个任务上的真实收益

## 14. 当前结论

这是当前项目真正核心的一步。

因为只有当：

- 技能会产生产生新现象
- 认知会解释这些现象
- 认知又会反向重写技能搜索空间

时，当前系统才真正接近一个“像研究者一样持续成长”的框架。 
