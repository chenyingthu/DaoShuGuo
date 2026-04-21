# task003 设计草案：新能源接入下的无功补偿与优化调控

## 1. 设计定位

`task003` 不再只是验证“框架能否迁移到相邻算例”，而是开始验证：

> 系统能否将一个更接近真实科研表达的任务意图，形式化为可执行、可验证、可失败、可形成认知的研究任务。

因此，`task003` 的核心不是单纯做一个更复杂的 benchmark，而是检验：

- 任务接入能力
- 问题定义能力
- success / failure 双通路能力
- 新能源场景下的 skill / evaluator / taste 约束是否仍然成立

## 2. 核心命题

`task003` 要回答的问题不是：

- 某个旧技能在更复杂系统上还能不能再赢一次

而是：

1. 当研究 brief 更接近真实科研表达时，系统能否把任务立住
2. 当新能源接入引入新的控制对象和目标冲突时，evaluator 是否仍可成立
3. 系统能否区分：
   - `skill mismatch`
   - `task mismatch`
4. 当任务本身没有被定义清楚时，系统能否停止过度执行并形成负向认知

## 3. 推荐任务定义

推荐将 `task003` 定义为：

> 考虑新能源接入的配电网无功补偿与优化调控任务接入验证

最小研究对象建议为：

- 配电网
- 含若干新能源接入点
- 新能源设备具备有限无功支撑能力
- 仍保留传统无功补偿或调压对象作为对照

建议先保持：

- 单时刻或少量代表性工况
- 小规模系统
- 最小控制变量集合

避免一开始引入：

- 长时间序列
- 大规模不确定性传播
- 多层级经济调度

## 4. task003 的两条主线

### 4.1 主线 A：任务明确型 success path

该路径用于验证：

- 当研究对象、控制变量、边界和 evaluator 被清楚定义时
- 框架是否能把任务接入并形成有效的 success cognition

最小设定建议：

- 网络中引入若干新能源接入点
- 控制对象包括：
  - 逆变器无功支撑
  - 传统 shunt / capacitor 补偿
- baseline 为较朴素的控制策略
- candidate 为更贴近问题本体的优化调控技能
- evaluator 比较：
  - loss
  - voltage_deviation
  - constraint_violation
  - 可选：renewable_reactive_support_utilization 或 curtailment_proxy

### 4.2 主线 B：任务失配型 failure path

该路径用于验证：

- 不是 skill 执行失败
- 而是任务本身没有被正确定义

系统理想行为不是硬跑，而是形成：

- 任务定义不足
- evaluator 尚不稳定
- 当前结果不能支撑完整结论
- 应冻结或收窄 task claim

## 5. 什么是 skill mismatch

在 `task003` 中，`skill mismatch` 的含义是：

- 任务本身是清楚的
- evaluator 是成立的
- baseline 和 candidate 可比较
- 但所选 skill 不适合新能源接入后的控制空间

示例：

- 仍使用只适合静态 shunt 搜索的技能
- 但 task003 的真实控制对象已经变成：
  - inverter reactive support
  - shunt + inverter coordination

此时失败原因主要在：

- skill 没跟上任务
- 控制对象不匹配
- 方法家族不匹配

这属于 `skill mismatch`。

## 6. 什么是 task mismatch

在 `task003` 中，`task mismatch` 的含义是：

- 题目名义上很合理
- 但任务形式化并没有成立

典型表现：

1. 新能源对象没有定义清楚
   - 是 PV 还是风电
   - 是单点还是多点
   - 是静态接入还是时变出力

2. 控制对象没有定义清楚
   - 只调 inverter Q
   - 只调 shunt
   - 还是多对象协同

3. evaluator 目标互相打架
   - 网损
   - 电压质量
   - 调节代价
   - 新能源消纳
   但没有说明优先级或权衡方式

4. 想研究“新能源接入场景”
   - 却只给一个静态工况
   - 却想支撑波动性结论

此时问题不在 skill，而在：

- task 没立稳
- 结论边界先天失真

这属于 `task mismatch`。

## 7. 最小 Failure Probe 设计

`task003` 建议保留两类 failure probe。

### 7.1 Skill-mismatch failure probe

目标：

- 验证旧技能迁移到新能源任务时会因控制对象不匹配而失败

最小方式：

- 使用只做传统弱节点 shunt 搜索的 candidate
- 不显式利用新能源逆变器无功支撑
- 在 evaluator 中与含 inverter reactive support 的 baseline / candidate 进行对照

期望输出：

- 失败 run
- failure cognition
- “当前旧技能不适合新能源接入场景” 的边界认知

### 7.2 Task-mismatch failure probe

目标：

- 验证系统能否识别“题目尚未构成合格研究任务”

最小方式：

- 故意提供一个不完整 research brief
- 缺失以下任一关键项：
  - 控制对象
  - 新能源能力边界
  - evaluator 权重/优先级
  - 工况定义

理想行为：

- 系统不直接生成强结论
- 可形成：
  - `task_refinement_note`
  - `assumption_gap`
  - `failure cognition`
  - `冻结/收窄结论`

## 8. 推荐最小任务包

`task003` 建议采用“brief -> task package”的两阶段形式。

### 8.1 输入层

建议新增或模拟以下输入对象：

- `research_brief.md`
- `grid_context.yaml`
- `renewable_context.yaml`
- `control_scope.yaml`

这些文件不必一开始都复杂，但必须体现：

- 输入更接近真实科研描述
- 不再是已经完全整理好的 benchmark task

### 8.2 形式化任务包

系统应据此生成或完善：

- `tasks/task003/task.md`
- `tasks/task003/task.yaml`
- `tasks/task003/constraints.yaml`
- `tasks/task003/baseline.yaml`
- `tasks/task003/targets.yaml`
- `tasks/task003/assumptions.yaml`

必要时可新增：

- `tasks/task003/framing_note.md`
- `tasks/task003/evaluator_rationale.md`

## 9. 推荐 evaluator 结构

`task003` evaluator 建议仍然保持“简单但真实”的原则。

最小指标建议：

1. `loss`
2. `voltage_deviation`
3. `constraint_violation`
4. `reactive_support_effort` 或类似代理指标

其中：

- 前三项保证与前序任务连续
- 第四项体现新能源接入后的场景变化

不建议第一版就加入太多经济性或时序复杂指标。

## 10. 推荐 baseline / candidate 结构

### 10.1 baseline

推荐 baseline 保持朴素、稳定、可解释，例如：

- 固定 inverter 功率因数
- 默认 ext_grid / shunt 设置
- 不做多对象协同优化

### 10.2 candidate

推荐 candidate 不必追求最强，但应体现问题语义提升，例如：

- inverter reactive support 调节
- shunt + inverter 协同
- 按新能源接入点邻近电压特征做局部补偿

## 11. 产物要求

`task003` 的最小产物不应低于 `task002`，且建议新增两类中间记录。

### 必要产物

- run
- metrics
- evidence_bundle
- taste_assessment
- report
- cognition
- failure cognition

### 推荐新增产物

- task_framing_note
- evaluator_derivation_note
- assumption_gap_note
- task_refinement_note

## 12. 开发顺序建议

建议按以下顺序推进。

### Step 1

先写一个 `task003` 的 research brief，不急着写 solver。

### Step 2

定义 task003 的最小 task package 和 evaluator。

### Step 3

实现一个保守 baseline。

### Step 4

实现一个最小新能源 candidate。

### Step 5

实现一个 `skill mismatch` failure probe。

### Step 6

实现一个 `task mismatch` detection / freeze 机制。

### Step 7

补 comparison / literature / cognition upgrade。

## 13. 测试顺序建议

### 必要测试

1. task003 task package 校验通过
2. success path 可跑通
3. failure path 可跑通
4. success cognition 成立
5. failure cognition 成立
6. taste / report 在 success/failure 下都正确约束

### 扩展测试

1. 文献对齐是否仍成立
2. 新能源相关解释对齐是否可形成
3. task refinement 是否可写回

## 14. 当前建议结论

当前最合理的 `task003` 路线不是：

- 更大网络
- 更多工况
- 更复杂算法

而是：

> 保持电力无功优化主线连续，同时把任务输入升级为更接近真实科研 brief，并引入 `skill mismatch` 与 `task mismatch` 两类 failure 验证。

如果 `task003` 做成这样，它将真正开始回答：

> Agent 到底是在“会做题”，还是开始具备“把题立住”的科研能力。

## 15. 第一轮实现后的修正认识

task003 第一轮实现后，一个关键认识被进一步明确：

> 指标改善不等于研究语义成立。

在 `weak-shunt-mismatch` probe 中，旧式 weak-shunt 技能可以显著改善 loss、voltage deviation 和 constraint violation。

但它没有使用 task003 的新能源 inverter 控制空间，因此不应被包装成新能源接入场景下的有效 candidate。

这说明 task003 的 failure path 不应只理解为“指标失败”，还应覆盖：

- 控制对象失配
- 研究问题未被回答
- 方法家族不对应当前任务语义

在第一轮补充实现后，task003 进一步确认还需要单独覆盖：

- `performance failure`

也就是：

- 使用了正确控制空间
- 任务定义也成立
- 但当前 candidate 没有形成成效证据

这类失败不能被混同为 skill mismatch，也不能被误判为 task mismatch。

因此，task003 的判定应区分两层：

1. evaluator metric result
2. research semantic fit

只有两者同时成立，才应进入 success cognition。

## 16. 第一轮实现后的下一步

下一步更适合推进的不是继续堆算例，而是补齐：

1. shunt + inverter 协同 candidate
2. task003 文献对齐
3. 新能源解释对齐
4. cognition upgrade

其中最优先的是：

> 将“指标成功但研究语义失配”的判断固化为更正式的 taste / evaluator 协同规则。

## 17. 第三阶段后的修正认识

在 task003 第三阶段完成后，项目进一步确认：

> 本地认知可以先长出来，但最终必须接受外部方法空间的校准。

当前 task003 已经能够做到：

- 将 `inverter-support` 定位到 smart inverter / DER reactive support 家族
- 将 `weak-shunt-mismatch` 定位到传统 capacitor placement 家族
- 将 `performance failure` 解释为方法家族内的局部实现/参数失败，而不是直接否定方法方向

这说明 task003 当前的认知升级已经不再只是：

- 自己觉得合理

而是开始变成：

- 有本地证据
- 有外部方法参照
- 有 excerpt 级解释支撑

这种双重约束，才更接近真正的科研认知升级。
