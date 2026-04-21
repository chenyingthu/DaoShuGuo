# task003 计划：新能源接入下的无功补偿与优化调控任务接入验证

## 1. 计划目标

`task003` 的目标不是继续增加一个更复杂算例，而是验证：

> 系统能否将一个更接近真实科研表达的新能源无功优化研究意图，转化为可执行、可验证、可失败、可形成认知的研究任务包。

`task003` 需要在 `task001` 与 `task002` 已有框架基础上，进一步验证：

- 任务接入能力
- 问题定义能力
- 新能源控制对象建模能力
- success / failure 双通路能力
- skill mismatch 与 task mismatch 的识别能力

## 2. 任务定位

### 2.1 主目标

验证“真实科研 brief -> 可执行 task package -> success/failure evidence -> cognition writeback”的任务接入链路。

### 2.2 副目标

观察现有无功补偿技能在新能源接入场景下的适用边界。

### 2.3 非目标

本阶段不追求：

- 完整新能源时序优化
- 大规模不确定性建模
- 论文级最优算法
- 多目标经济调度完整建模
- 自动文献检索驱动选题

## 3. 推荐任务定义

推荐 `task003` 定义为：

> 含新能源接入的配电网无功补偿与优化调控任务接入验证。

最小设定：

- 使用小规模或中等规模配电网
- 接入少量 PV / inverter 型新能源节点
- 新能源逆变器具备有限无功支撑能力
- 控制对象至少包括：
  - inverter reactive support
  - traditional shunt / capacitor compensation
- evaluator 保持与前序任务连续：
  - loss
  - voltage_deviation
  - constraint_violation
  - reactive_support_effort

## 4. task003 要回答的关键问题

1. 研究 brief 能否被形式化为 task package
2. 新能源接入后 evaluator 是否仍可独立成立
3. 旧 weak-shunt 技能在新能源任务中的边界是什么
4. 新 candidate 是否能显式利用 inverter reactive support
5. failure path 是否能区分 skill mismatch 与 task mismatch
6. taste 是否仍能限制新能源场景下的过度表述

## 5. 必须复用的框架能力

task003 必须复用：

- schema envelope
- task / baseline / evaluator / run
- skill registry
- cognition registry
- evidence bundle
- taste assessment
- report
- writeback
- integration check 风格
- success/failure 双通路验证方式

task003 不允许：

- 重新定义平行 schema
- 绕过 evaluator 直接写结论
- 绕过 taste 生成报告
- 把 task mismatch 包装成算法失败
- 把 failure probe 包装成真实 candidate

## 6. 允许变化

task003 允许变化：

- 网络模型
- renewable/inverter 数据入口
- 控制变量
- evaluator 指标扩展
- baseline 策略
- candidate skill
- failure probe 类型

## 7. 最小任务结构

### 7.1 输入层

task003 应先提供 research brief，而不是直接从完整 task.yaml 开始。

建议文件：

- `tasks/task003/research_brief.md`
- `tasks/task003/grid_context.yaml`
- `tasks/task003/renewable_context.yaml`
- `tasks/task003/control_scope.yaml`

### 7.2 形式化任务包

建议文件：

- `tasks/task003/task.md`
- `tasks/task003/task.yaml`
- `tasks/task003/constraints.yaml`
- `tasks/task003/baseline.yaml`
- `tasks/task003/targets.yaml`
- `tasks/task003/assumptions.yaml`
- `tasks/task003/framing_note.md`
- `tasks/task003/evaluator_rationale.md`

## 8. 最小执行对象

### 8.1 baseline

建议 baseline：

- 固定 inverter 功率因数或固定 Q
- 不做多对象协同优化
- 可解释、稳定、可重复

### 8.2 candidate

建议 candidate：

- 显式利用 inverter reactive support
- 可选结合 shunt / capacitor
- 先做简单启发式，不追求最优

### 8.3 skill-mismatch failure probe

目标：

- 验证旧 weak-shunt 思路在新能源接入场景中可能控制对象不匹配

建议方式：

- 使用不考虑 inverter reactive support 的旧式 shunt candidate
- 与新能源-aware baseline/candidate 比较

### 8.4 task-mismatch failure probe

目标：

- 验证系统能否识别任务定义不足

建议方式：

- 构造一个不完整 brief
- 缺失控制对象、inverter 能力边界、evaluator 优先级或工况定义之一
- 系统应生成 task refinement / assumption gap / freeze conclusion

## 9. 推荐 evaluator

最小指标：

1. `loss`
2. `voltage_deviation`
3. `constraint_violation`
4. `reactive_support_effort`

其中：

- `loss`、`voltage_deviation`、`constraint_violation` 保持与 task001/task002 连续
- `reactive_support_effort` 用于表达新能源逆变器无功支撑代价或使用程度

第一版不引入复杂经济权重。

## 10. 成功标准

以下条件同时满足，视为 `task003` 第一阶段成功：

1. research brief 被形式化为 task package
2. success path 可真实运行
3. 至少一个 candidate 能产生可比较结果
4. failure path 至少覆盖 skill mismatch
5. task mismatch 能被检测并冻结/收窄
6. 成功与失败都能生成 cognition
7. success/failure 都受 taste/report 约束
8. integration checks 覆盖 task003

## 11. 失败也算成功的条件

如果新能源 candidate 未能优于 baseline，只要满足以下条件，仍视为有研究价值：

- evaluator 真正运行
- failure 被结构化记录
- 失败被区分为 skill mismatch 或 task mismatch
- cognition 明确收窄边界
- report 不把失败包装为成果

## 12. 实施步骤

## Phase 1: research brief 与任务接入层

目标：

建立更接近真实科研输入的 task003 brief 层。

执行内容：

- [x] 编写 `research_brief.md`
- [x] 编写 `grid_context.yaml`
- [x] 编写 `renewable_context.yaml`
- [x] 编写 `control_scope.yaml`
- [x] 明确 brief 中哪些信息是确定的，哪些是假设

完成判据：

- [x] task003 的研究意图、对象、边界和控制范围可被独立阅读理解

## Phase 2: task package 形式化

目标：

将 brief 形式化为可执行 task package。

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

- [x] task003 task package 可通过 schema / artifact 校验
- [x] task003 明确说明其 claim 边界

## Phase 3: runtime 与 evaluator

目标：

建立最小新能源接入运行环境与独立 evaluator。

执行内容：

- [x] 实现 task003 runtime helpers
- [x] 支持新能源接入点和 inverter Q 控制
- [x] 实现 baseline solution
- [x] 实现 evaluator
- [x] 输出 `loss / voltage_deviation / constraint_violation / reactive_support_effort`

完成判据：

- [x] baseline 可真实运行
- [x] evaluator 可独立评价 baseline/candidate

## Phase 4: success candidate

目标：

实现一个最小新能源-aware candidate。

执行内容：

- [x] 实现 inverter reactive support candidate
- [ ] 必要时加入 shunt + inverter 简单协同
- [x] 生成 run / metrics / evidence / taste / report / cognition

完成判据：

- [x] success path 至少能生成一个完整 run
- [x] 若 candidate 不优于 baseline，也必须形成诚实边界认知

## Phase 5: skill-mismatch failure probe

目标：

验证旧技能或控制对象不匹配时，系统能形成负向认知。

执行内容：

- [x] 接入旧式 weak-shunt candidate 作为 skill mismatch probe
- [x] 与新能源-aware task/evaluator 对照
- [x] 生成 failure cognition
- [x] taste 降级并限制 report

完成判据：

- [x] skill mismatch failure path 可被 verifier 检查

## Phase 6: task-mismatch detection / freeze

目标：

验证系统能否识别任务定义不足，而不是盲目执行。

执行内容：

- [x] 构造一个不完整 research brief
- [x] 实现最小 task mismatch checker
- [x] 输出 assumption gap / task refinement note
- [x] 形成 freeze 或 retain 类 cognition

完成判据：

- [x] task mismatch 不会被包装成可执行成功任务
- [x] 系统能给出需要补充的信息清单

## Phase 7: 集成测试与收口

目标：

证明 task003 是复用框架，不是重造系统。

执行内容：

- [x] 扩展 schema artifact set
- [x] 扩展 integration checks
- [x] 增加 task003 success verifier
- [x] 增加 task003 failure verifier
- [x] 更新实验记录和设计文档

完成判据：

- [x] task003 通过最小纵向验证
- [x] task003 success/failure 双通路均可验证

## 13. 验收标准

### 13.1 功能验收

- [x] task003 brief 层建立
- [x] task003 task package 建立
- [x] baseline 可运行
- [x] evaluator 可运行
- [x] success candidate 可运行
- [x] skill mismatch failure probe 可运行
- [x] task mismatch detection 可运行
- [x] success/failure cognition 均形成

### 13.2 质量验收

- [x] 没有重新发明 task001/task002 已有机制
- [x] brief -> task package 的转换过程有记录
- [x] evaluator 指标与新能源任务语义一致
- [x] failure probe 不被包装成真实 candidate
- [x] task mismatch 不被包装成 skill failure
- [x] report 继续受 taste 约束

## 14. 风险

### 风险 1：新能源任务过大

缓解：

- 第一版只做单时刻或少量代表工况
- 不做完整时序优化

### 风险 2：指标体系过早复杂化

缓解：

- 只新增一个新能源相关指标
- 暂不引入复杂经济权重

### 风险 3：task mismatch checker 变成主观文本判断

缓解：

- 第一版只检查必填定义项
- 不做复杂语义推理

### 风险 4：旧 skill failure 与 task mismatch 混淆

缓解：

- 明确区分：
  - evaluator 成立但 skill 不适配 -> skill mismatch
  - evaluator/task 本身未成立 -> task mismatch

## 15. 当前结论

`task003` 的真正价值在于：

> 从“会运行一个任务”进一步走向“能把真实科研意图立成合格任务”。

如果 `task003` 成立，系统将开始具备更接近科研研究生的能力：

- 能理解任务意图
- 能形式化问题边界
- 能识别任务定义缺口
- 能区分技能失败与任务失败
- 能将成功和失败都沉淀为认知
