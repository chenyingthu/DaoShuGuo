# task003 第二阶段计划：比较认知与失败类型认知升级

## 1. 计划目标

`task003` 第一阶段已经证明：

- research brief 可被形式化为 task package
- success path 可真实运行
- failure path 已分化为：
  - `skill mismatch`
  - `task mismatch`
  - `performance failure`
- success / failure 均受 taste 与 report 约束

因此，`task003` 第二阶段的目标不再是继续补最小执行链，而是验证：

> 系统能否将 task003 已有的 success / failure 材料上升为结构化比较认知，并形成更高层的失败类型认知。

## 2. 第二阶段核心问题

task003 第二阶段要回答的不是“candidate 能否再变强”，而是：

1. `inverter-support`、`weak-shunt-mismatch`、`inverter-underperformer` 三类结果在同一研究语境中分别意味着什么
2. 什么叫“回答了新能源任务本体”
3. 什么叫“语义失配”
4. 什么叫“语义正确但性能失败”
5. 哪些失败应该冻结，哪些失败应继续投入
6. 这些判断能否被对象化，而不是停留在人工解释

## 3. 第二阶段范围

本阶段聚焦：

- strategy comparison
- semantic comparison
- failure taxonomy cognition
- 最小 cognition upgrade

本阶段暂不优先做：

- 新 solver
- shunt + inverter 协同 candidate
- 大规模多工况
- 经济性建模
- 新一轮任务接入

文献对齐与 explanation alignment 属于第二阶段后半，可做为可选增强项。

## 4. 现有可复用材料

当前已经有以下 task003 运行材料：

### success run

- `runs/task003/run_0001`
  - `inverter-support`
  - 形成 candidate cognition

### skill mismatch run

- `runs/task003/run_0003`
  - `weak-shunt-mismatch`
  - 指标可能改善，但研究语义失配
  - 已被压为 failure cognition

### performance failure run

- `runs/task003/run_0004`
  - `inverter-underperformer`
  - 语义正确，但性能未优于 baseline
  - 已被压为 failure cognition

### task mismatch freeze

- `analysis/task003/mismatch_*`
  - 不完整 brief -> `freeze`

这些材料足以支撑第二阶段的比较认知工作。

## 5. 第二阶段的最小认知框架

建议将 task003 的认知对象分成三层。

### 5.1 运行层认知

来源：

- success run
- failure run
- mismatch check

功能：

- 对单次运行或单次冻结给出局部结论

这一层已经基本具备。

### 5.2 比较层认知

来源：

- success run 与 skill mismatch run 的对照
- success run 与 performance failure run 的对照
- failure 类型之间的对照

功能：

- 不是只说“谁好谁坏”
- 而是说“谁回答了新能源任务本体，谁没有”

### 5.3 升级层认知

来源：

- 比较层认知
- semantic comparison
- 必要时引入文献对齐

功能：

- 将局部运行事实升级为更稳定的 task003 认知
- 例如：
  - 新能源任务中，显式利用 inverter 控制空间是必要条件之一
  - 使用正确控制空间但性能失败，不应直接否定研究方向

## 6. 本阶段建议的比较对象

建议最小比较先做两组。

### Compare A

`inverter-support` vs `weak-shunt-mismatch`

目标：

- 区分“数值改善”和“回答研究问题”不是同一件事

重点问题：

- 为什么旧 weak-shunt 虽然指标更好，仍然不能作为新能源-aware candidate

### Compare B

`inverter-support` vs `inverter-underperformer`

目标：

- 区分“语义正确但性能失败”和“语义失配”

重点问题：

- 为什么 underperformer 不应被冻结为方向错误
- 而应保留为“当前实现失败，但方向可继续演化”

## 7. 推荐新增对象

本阶段建议新增：

- `analysis/task003/compare_*`
- `analysis/task003/semantic_*`
- `analysis/task003/upgrade_*`

必要时可新增：

- `analysis/task003/failure_taxonomy_*`

但第一版也可以先将 failure taxonomy 写入 `semantic comparison` 或 `cognition upgrade` 对象中，不额外发明新 schema。

## 8. 推荐 semantic dimensions

相比 task001/task002，task003 semantic comparison 需要新增更贴近新能源任务的维度。

建议最小维度：

1. `problem_alignment`
2. `control_space_match`
3. `renewable_awareness`
4. `research_value`
5. `performance_status`
6. `reuse_potential`

解释：

- `problem_alignment`: 是否回答了当前 task003 问题本体
- `control_space_match`: 是否真正使用了 inverter reactive support 控制空间
- `renewable_awareness`: 是否把新能源接入视为任务对象，而不是背景噪声
- `research_value`: 是否值得继续投入
- `performance_status`: 当前实现是成功、失败还是冻结
- `reuse_potential`: 是否可作为后续 skill 或认知继续复用

## 9. 推荐最小认知升级目标

本阶段至少应形成两条升级认知。

### 认知 A

> 在 task003 中，是否显式使用新能源 inverter 控制空间，是判断 candidate 是否真正回答了任务本体的重要条件。

来源：

- success run vs skill mismatch run

### 认知 B

> 在 task003 中，语义正确但性能失败的 candidate 不应与 skill mismatch 混同，应保留为可继续演化的实现边界。

来源：

- success run vs performance failure run

## 10. 文献对齐是否纳入本阶段

建议分两步：

### 必要步骤

先不依赖文献对齐，先把本地比较认知走通。

原因：

- task003 当前最有价值的是 failure taxonomy
- 若过早接入文献，会稀释本阶段重点

### 可选增强

在本地比较认知稳定后，再引入最小新能源文献种子：

- inverter Volt/Var control
- DER reactive support
- coordinated Volt/Var optimization

目标：

- 看 task003 的 success cognition 是否可被定位为某类已知方法家族
- 看 skill mismatch / performance failure 是否可被文献语义辅助解释

## 11. 实施步骤

## Phase 1: task003 compare artifacts

目标：

建立最小对照对象。

执行内容：

- [x] 选择固定 task003 代表 runs
- [x] 建立 Compare A：success vs skill mismatch
- [x] 建立 Compare B：success vs performance failure
- [x] 输出结构化 comparison 对象

完成判据：

- [x] 至少两个 comparison 对象可被验证

## Phase 2: task003 semantic comparison

目标：

把 failure 类型差异显式结构化。

执行内容：

- [x] 定义 task003 semantic dimensions
- [x] 实现 semantic comparison 逻辑
- [x] 区分：
  - success
  - skill mismatch
  - performance failure
  - task mismatch

完成判据：

- [x] semantic comparison 能明确写出 failure taxonomy

## Phase 3: cognition extraction / upgrade

目标：

从 comparison 和 semantic comparison 中提炼更高层认知。

执行内容：

- [x] 提炼“新能源任务本体回答条件”认知
- [x] 提炼“性能失败不等于方向错误”认知
- [x] 形成最小 cognition upgrade / upgraded cognition

完成判据：

- [x] 至少两条 task003 认知升级对象形成

## Phase 4: 可选文献对齐

目标：

为 task003 认知提供外部方法家族参照。

执行内容：

- [ ] 新增 task003 最小新能源文献种子
- [ ] 做方法家族级 literature alignment
- [ ] 视情况做 explanation alignment

完成判据：

- [ ] 若接入，则文献对齐不破坏现有 comparison/semantic 结论

## Phase 5: 验证与收口

目标：

将第二阶段纳入可验证状态。

执行内容：

- [x] 扩展 schema/artifact validation
- [x] 扩展 integration checks
- [x] 增加 task003 cognition-stage verifier
- [x] 更新实验记录和设计文档

完成判据：

- [x] task003 第二阶段通过最小认知验证

## 12. 成功标准

以下条件同时满足，视为第二阶段成功：

1. task003 success 与 failure 三类材料被统一放入比较框架
2. semantic comparison 能区分：
   - skill mismatch
   - performance failure
   - task mismatch
3. 至少两条 task003 升级认知形成
4. 认知升级仍受证据边界约束
5. verifier 与 integration checks 覆盖第二阶段对象

## 13. 风险

### 风险 1：第二阶段重新退化成“人工解释”

缓解：

- comparison 和 semantic comparison 必须对象化
- 不能只写在实验记录里

### 风险 2：failure taxonomy 过于主观

缓解：

- 只用少数明确维度
- 不做过早复杂语义系统

### 风险 3：文献对齐过早进入主线

缓解：

- 文献对齐作为后半阶段可选增强
- 先保证本地认知升级成立

## 14. 当前结论

task003 第二阶段最值得做的，不是继续补更多 solver，而是把已经出现的 success / failure 类型真正转化为结构化研究认知。

如果这一阶段成立，系统将不再只是“能跑新能源任务”，而是开始真正回答：

> 什么样的结果才算回答了新能源接入无功优化这个研究问题。 
