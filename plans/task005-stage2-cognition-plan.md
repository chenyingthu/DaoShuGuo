# task005 第二阶段计划：恢复认知与失败类型认知升级

## 1. 计划目标

`task005` 第一阶段已经证明：

- 故障恢复问题可被形式化为 task package
- success path 可真实运行
- failure path 已分化为：
  - `skill mismatch`
  - `task mismatch`
  - `performance failure`
  - `resilience overclaim`
- success / failure 都已受 taste 与 report 约束

因此，`task005` 第二阶段的目标不再是继续补最小执行链，而是验证：

> 系统能否将 task005 已有的 success / failure 材料上升为结构化比较认知，并形成更高层的恢复任务认知。

## 2. 第二阶段核心问题

task005 第二阶段要回答的，不是“candidate 还能不能再多恢复一点负荷”，而是：

1. `renewable-restoration`、`steady-state-mismatch`、`renewable-underperformer` 三类结果在同一研究语境中分别意味着什么
2. 什么叫“真正回答了故障恢复问题本体”
3. 什么叫“稳态结果失配”
4. 什么叫“语义正确但恢复性能失败”
5. 局部恢复结果为什么不能被写成系统韧性
6. 哪些失败应该冻结，哪些失败应继续投入

## 3. 第二阶段范围

本阶段聚焦：

- strategy comparison
- semantic comparison
- failure taxonomy cognition
- 最小 cognition upgrade

本阶段暂不优先做：

- 更复杂恢复 solver
- 多故障级联恢复
- 更丰富动作集
- 工程级恢复调度
- 文献对齐

文献对齐与 explanation alignment 放到 task005 第三阶段再处理。

## 4. 当前可复用材料

task005 当前已经有以下运行材料：

### success run

- `runs/task005/run_0001`
  - `renewable-restoration`
  - 形成 candidate cognition

### skill mismatch run

- `runs/task005/run_0002`
  - `steady-state-mismatch`
  - 已被压为 failure cognition

### performance failure run

- `runs/task005/run_0003`
  - `renewable-underperformer`
  - 已被压为 failure cognition

### task mismatch freeze

- `analysis/task005/mismatch_*`

### resilience overclaim check

- `analysis/task005/resilience_overclaim_*`

这些材料足以支撑 task005 第二阶段的最小认知升级。

## 5. task005 第二阶段的最小认知框架

建议将 task005 的认知对象分成三层。

### 5.1 运行层认知

来源：

- success run
- failure run
- mismatch / overclaim check

功能：

- 对单次恢复结果和单次 failure 给出局部判断

这一层已经基本具备。

### 5.2 比较层认知

来源：

- success run 与 skill mismatch run 的对照
- success run 与 performance failure run 的对照

功能：

- 不只是说“谁恢复得更多”
- 而是说“谁真正回答了恢复问题，谁没有”

### 5.3 升级层认知

来源：

- comparison
- semantic comparison
- 任务边界与 overclaim 判断

功能：

- 将局部恢复事实升级为更稳定的 task005 认知

## 6. 推荐最小比较对象

第一版建议先做两组比较。

### Compare A

`renewable-restoration` vs `steady-state-mismatch`

目标：

- 区分“局部稳态结果”与“真正恢复决策”不是一回事

重点问题：

- 为什么稳态结果即使在某些局部指标上不差，也不能作为恢复策略

### Compare B

`renewable-restoration` vs `renewable-underperformer`

目标：

- 区分“语义正确但性能失败”和“语义失配”

重点问题：

- 为什么 underperformer 不应被冻结为方向错误
- 而应保留为后续可改进的恢复策略方向

## 7. 推荐 semantic dimensions

相比 task003/task004，task005 semantic comparison 需要新增更贴近恢复问题的维度。

建议最小维度：

1. `problem_alignment`
2. `restoration_scope_match`
3. `resilience_awareness`
4. `critical_load_relevance`
5. `performance_status`
6. `research_value`
7. `reuse_potential`

解释：

- `problem_alignment`: 是否回答了故障恢复问题本体
- `restoration_scope_match`: 是否真正作用于恢复动作集合
- `resilience_awareness`: 是否把恢复边界和韧性条件视为问题的一部分
- `critical_load_relevance`: 是否真正关心关键负荷恢复
- `performance_status`: 当前实现是成功、失败还是冻结
- `research_value`: 是否值得继续投入
- `reuse_potential`: 是否可继续演化为更强恢复技能

## 8. 推荐最小认知升级目标

本阶段至少应形成两条升级认知。

### 认知 A

> 在 task005 中，稳态局部结果不能替代事件驱动恢复策略；恢复任务必须显式面向 fault 后的动作与关键负荷恢复。

来源：

- success run vs skill mismatch run

### 认知 B

> 在 task005 中，语义正确但性能失败的恢复策略，不应与 skill mismatch 混同，应保留为可继续演化的恢复方向。

来源：

- success run vs performance failure run

## 9. resilience overclaim 在本阶段的位置

task005 当前已经有 `resilience overclaim` 检查，但第二阶段要把它提升为认知层约束的一部分。

本阶段应至少回答：

- 为什么“当前局部恢复成功”不能等于“系统具有韧性”
- 什么条件下恢复结果只能作为局部 fault 场景结论

也就是说：

`resilience overclaim` 不应只留在 report 层，而应进入 task005 的高层认知逻辑。

## 10. 推荐新增对象

本阶段建议新增：

- `analysis/task005/compare_*`
- `analysis/task005/semantic_*`
- `analysis/task005/upgrade_*`

第一版不额外发明新 schema，优先复用：

- `strategy_comparison`
- `strategy_semantic_comparison`
- `novelty_assessment`
- `cognition_upgrade`

## 11. 实施步骤

## Phase 1: task005 compare artifacts

目标：

建立最小恢复对照对象。

执行内容：

- [x] 选择固定 task005 代表 runs
- [x] 建立 Compare A：success vs skill mismatch
- [x] 建立 Compare B：success vs performance failure
- [x] 输出结构化 comparison 对象

完成判据：

- [x] 至少两个 comparison 对象可被验证

## Phase 2: task005 semantic comparison

目标：

把恢复问题中的 failure 类型差异显式结构化。

执行内容：

- [x] 定义 task005 semantic dimensions
- [x] 实现 semantic comparison 逻辑
- [x] 区分：
  - success
  - skill mismatch
  - performance failure
  - task mismatch

完成判据：

- [x] semantic comparison 能明确写出 task005 failure taxonomy

## Phase 3: cognition extraction / upgrade

目标：

从 comparison 和 semantic comparison 中提炼更高层认知。

执行内容：

- [x] 提炼“恢复任务本体回答条件”认知
- [x] 提炼“性能失败不等于方向错误”认知
- [x] 将 resilience overclaim 纳入认知升级的 claim adjustment
- [x] 形成最小 cognition upgrade / upgraded cognition

完成判据：

- [x] 至少两条 task005 认知升级对象形成

## Phase 4: 验证与收口

目标：

将 task005 第二阶段纳入可验证状态。

执行内容：

- [x] 扩展 schema/artifact validation
- [x] 扩展 integration checks
- [x] 增加 task005 cognition-stage verifier
- [x] 更新实验记录和设计文档

完成判据：

- [x] task005 第二阶段通过最小认知验证

## 12. 成功标准

以下条件同时满足，视为第二阶段成功：

1. task005 success 与 failure 三类材料被统一纳入比较框架
2. semantic comparison 能区分：
   - skill mismatch
   - performance failure
   - task mismatch
3. 至少两条 task005 升级认知形成
4. resilience overclaim 被提升为认知层约束
5. verifier 与 integration checks 覆盖第二阶段对象

## 13. 风险

### 风险 1：task005 第二阶段退化成“只看恢复比例”

缓解：

- semantic comparison 必须包含 `restoration_scope_match` 与 `critical_load_relevance`

### 风险 2：resilience overclaim 仍然停留在报告层

缓解：

- 在 cognition upgrade 中显式加入 claim adjustment

### 风险 3：failure taxonomy 过于主观

缓解：

- 第一版只用少数明确维度
- 不做复杂韧性理论系统

## 14. 当前结论

task005 第二阶段最值得做的，不是继续堆动作和 solver，而是把已经出现的 success / failure 结果真正升级为结构化恢复认知。

如果这一阶段成立，task005 就不再只是“能做一个恢复实验”，而开始真正回答：

> 什么样的结果，才算真正回答了故障恢复与韧性重构这个研究问题。 
