# task004 计划：新能源接入承载力评估任务

## 1. 计划目标

`task004` 的目标不是继续围绕单一无功优化策略做更多变体，而是验证：

> 系统能否将“新能源接入承载力评估”这一更高层研究问题，形式化为可执行、可验证、可失败、可形成认知的研究任务。

在 `task001`、`task002`、`task003` 的基础上，`task004` 需要进一步验证：

- 系统能否从“优化一个控制量”上升到“判断系统边界”
- 承载力定义是否可以被清晰形式化
- 控制策略是否能改变承载力边界
- 边界判断能否形成结构化认知并受 taste 约束

## 2. 任务定位

### 2.1 主目标

验证“新能源接入承载边界”这一问题能否进入现有自主科研框架。

### 2.2 副目标

比较不同控制策略下的承载力边界变化，并形成边界认知。

### 2.3 非目标

本阶段不追求：

- 完整长期时序 hosting capacity 分析
- 论文级最优承载力算法
- 经济性与市场因素联合建模
- 暂态稳定或保护约束下的综合承载力
- 自动化最新文献检索

## 3. task004 的核心问题

task004 要回答的，不再是：

- 某个 candidate 是否优于 baseline

而是：

1. 在给定约束下，新能源接入边界如何定义
2. 承载力是电网固有边界，还是控制策略相关边界
3. 不同控制策略会如何改变该边界
4. 哪类边界判断是真正可报告的，哪类只是在局部工况下成立
5. failure 是来自：
   - skill mismatch
   - task mismatch
   - performance failure
   - 还是 boundary overclaim

## 4. 推荐任务定义

推荐将 `task004` 定义为：

> 新能源接入下的配电网静态承载力评估任务。

这里的“承载力”第一版建议明确限定为：

> 在单代表工况下、给定控制策略和约束条件下，系统能够容纳的最大新能源接入水平。

建议先限定：

- 静态代表工况
- 配电网
- 电压与约束驱动的 hosting capacity
- 可选考虑损耗，但不把经济目标作为第一版核心

## 5. 承载力定义必须先钉死

task004 开始前，必须先明确以下定义。

### 5.1 评估对象

第一版建议评估：

- 新能源有功接入水平

而不是：

- 多种接入规模与运行方式的全部组合

### 5.2 约束条件

第一版建议至少包括：

- 电压约束
- constraint violation
- inverter reactive support 边界
- 基本配电网运行约束

### 5.3 承载力定义形式

第一版建议采用：

- “给定控制策略下最大允许接入水平”

而不是模糊表述：

- “系统大概能接多少”

### 5.4 控制策略在承载力中的位置

必须明确：

- task004 评估的不是“系统固有唯一承载力”
- 而是“在某种控制策略 / 控制空间下的承载力边界”

这点非常关键，否则会造成过度 claim。

## 6. 推荐任务结构

### 6.1 输入层

建议文件：

- `tasks/task004/research_brief.md`
- `tasks/task004/grid_context.yaml`
- `tasks/task004/renewable_context.yaml`
- `tasks/task004/hosting_capacity_scope.yaml`
- `tasks/task004/control_scope.yaml`

### 6.2 形式化任务包

建议文件：

- `tasks/task004/task.md`
- `tasks/task004/task.yaml`
- `tasks/task004/constraints.yaml`
- `tasks/task004/baseline.yaml`
- `tasks/task004/targets.yaml`
- `tasks/task004/assumptions.yaml`
- `tasks/task004/framing_note.md`
- `tasks/task004/evaluator_rationale.md`

## 7. 推荐 baseline / candidate 结构

### 7.1 baseline

建议 baseline 不是某个复杂算法，而是：

- 固定 inverter Q 或保守 reactive support 策略
- 在该策略下逐步增加新能源接入水平
- 记录第一次触碰边界的位置

### 7.2 candidate

建议 candidate 体现“控制策略影响承载力”这一问题，例如：

- inverter reactive support aware strategy
- 后续扩展可以是协调控制策略

第一版不要求多 candidate。

## 8. 推荐 evaluator

task004 evaluator 不再只是单点指标比较，而应围绕“边界”展开。

第一版建议至少定义：

1. `hosting_capacity_level`
2. `violation_trigger_type`
3. `loss_at_boundary`
4. `voltage_margin`

其中：

- `hosting_capacity_level` 是核心
- 其他指标用于约束边界解释

## 9. success / failure 设计

### 9.1 success path

success 的最低标准不是“算法很强”，而是：

- 能在明确约束下输出一个结构化承载力边界
- 能说明该边界依赖什么控制策略
- 能说明 claim 上限

### 9.2 skill-mismatch failure

示例：

- 用只适合单点无功优化的技能，直接去做承载力边界判断

系统应识别：

- 它可能会产生局部结果
- 但不一定适合做边界评估

### 9.3 task-mismatch failure

示例：

- 研究 brief 里没有说清楚承载力定义
- 没有说清楚约束边界
- 没有说清楚控制策略是否属于边界定义的一部分

系统应冻结而不是盲跑。

### 9.4 boundary overclaim failure

这是 task004 新增的一类 failure。

示例：

- 只在单工况下得到一个边界
- 却宣称这是系统普适承载力

系统应将其识别为：

- 边界过度表述
- claim 必须降级

## 10. 成功标准

以下条件同时满足，视为 task004 第一阶段成功：

1. 承载力定义被明确形式化
2. baseline 可以输出一个结构化边界结果
3. 至少一个 candidate 能与 baseline 比较
4. 系统能识别 skill mismatch
5. 系统能识别 task mismatch
6. 系统能识别 boundary overclaim
7. 结论受 taste / report 约束
8. integration checks 覆盖 task004

## 11. 失败也算成功的条件

如果 candidate 未提高承载力边界，只要满足以下条件，仍然视为有研究价值：

- evaluator 真正运行
- 边界结果被结构化记录
- failure 类型被明确区分
- claim 被正确收窄
- failure cognition 被写回

## 12. 实施步骤

## Phase 1: 承载力问题定义

目标：

在写任何 solver 之前，把“承载力”先定义清楚。

执行内容：

- [x] 编写 `research_brief.md`
- [x] 明确承载力定义
- [x] 明确边界约束
- [x] 明确控制策略在边界中的位置
- [x] 明确 claim 上限

完成判据：

- [x] task004 不存在“承载力”概念歧义

## Phase 2: task package 形式化

目标：

将承载力问题形式化为可执行任务包。

执行内容：

- [x] 编写 `task.md`
- [x] 编写 `task.yaml`
- [x] 编写 `constraints.yaml`
- [x] 编写 `baseline.yaml`
- [x] 编写 `targets.yaml`
- [x] 编写 `assumptions.yaml`
- [x] 编写 `framing_note.md`
- [x] 编写 `evaluator_rationale.md`

完成判据：

- [x] task004 task package 可通过 schema / artifact 校验

## Phase 3: baseline 承载力扫描

目标：

建立最小 baseline hosting capacity 扫描能力。

执行内容：

- [x] 实现最小 runtime helpers
- [x] 实现 baseline 容量扫描
- [x] 输出承载力边界与边界触发条件

完成判据：

- [x] baseline 可输出结构化边界结果

## Phase 4: candidate 承载力比较

目标：

让控制策略真正进入承载力问题。

执行内容：

- [x] 实现一个新能源-aware candidate
- [x] 与 baseline 做 hosting capacity 比较
- [x] 生成 run / evidence / taste / report / cognition

完成判据：

- [x] 至少一个 candidate 与 baseline 可比较

## Phase 5: failure taxonomy

目标：

建立 task004 特有 failure 路径。

执行内容：

- [x] skill mismatch failure
- [x] task mismatch freeze
- [x] boundary overclaim detection

完成判据：

- [x] 三类 failure 都可被结构化记录

## Phase 6: 认知与收口

目标：

从边界评估中提炼结构化认知。

执行内容：

- [x] 提炼边界认知
- [x] 提炼控制策略作用认知
- [x] 更新实验记录和设计文档
- [x] 扩展 integration checks

完成判据：

- [x] task004 第一阶段通过最小纵向验证

## 13.1 当前阶段完成情况

- [x] 承载力定义被明确形式化
- [x] baseline 输出结构化边界结果
- [x] candidate 与 baseline 可比较
- [x] skill mismatch 被识别
- [x] task mismatch 被识别并冻结
- [x] boundary overclaim 被识别
- [x] 边界认知形成
- [x] 控制策略作用认知形成
- [x] integration checks 覆盖 task004 当前阶段
- [x] task004 外部文献参照已接入

## 13. 风险

### 风险 1：承载力定义不清，导致任务失配

缓解：

- 先做 Phase 1，不急着实现 solver

### 风险 2：把控制策略相关边界误写成系统固有承载力

缓解：

- 在 task 与 report 中强制写明控制策略条件

### 风险 3：边界判断缺乏适用条件

缓解：

- 输出 violation trigger 与 boundary statement

### 风险 4：又退回成“优化一个控制量”

缓解：

- evaluator 以边界结果为核心，而不是只看单点性能

## 14. 当前结论

task004 最值得验证的，不是某个新算法是否更强，而是：

> 系统是否能从“局部优化问题”上升到“系统边界判断问题”。

如果 task004 成立，项目将进一步接近真正的科研问题：

- 不只是求一个更优解
- 而是判断系统在什么条件下可行、可接纳、可扩展
