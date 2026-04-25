# task005 计划：新能源接入下的配电网故障恢复与韧性重构

## 1. 计划目标

`task005` 的目标不是继续在稳态无功优化或承载力评估上做变体，而是验证：

> 系统能否将“故障恢复与韧性重构”这一事件驱动、序列决策型研究问题，形式化为可执行、可验证、可失败、可形成认知的任务。

在 `task001` 到 `task004` 已有框架基础上，`task005` 需要进一步验证：

- 系统能否从静态稳态问题推进到事件驱动恢复问题
- 恢复动作集合是否能被清晰形式化
- 新能源/分布式资源是否能进入恢复决策语义
- success / failure / mismatch / overclaim 是否仍可被结构化判断
- 结果是否能形成更接近工程应用的成效与交付判断

## 2. 任务定位

### 2.1 主目标

验证“故障发生 -> 候选恢复策略 -> 恢复结果比较 -> 认知提炼”的最小闭环。

### 2.2 副目标

观察新能源接入资源在故障恢复场景中的作用边界。

### 2.3 非目标

本阶段不追求：

- 完整时序恢复优化
- 全网多故障级联恢复
- 保护整定与动作细节全建模
- 多阶段随机恢复
- 实时调度级工程部署

## 3. 推荐任务定义

推荐将 `task005` 定义为：

> 新能源接入下的配电网单故障恢复与韧性重构任务。

第一版建议限定：

- 单故障场景
- 单代表工况
- 中小规模配电网
- 少量恢复动作
- 以“恢复多少、恢复是否安全、恢复代价如何”为核心

## 4. task005 的核心问题

task005 要回答的，不再是：

- 某个稳态控制策略是否更优

而是：

1. 故障发生后系统是否还能恢复
2. 哪类动作组合能提高恢复水平
3. 新能源/储能/可控负荷对恢复是否真正有帮助
4. 恢复结果在什么条件下成立
5. failure 是来自：
   - skill mismatch
   - task mismatch
   - performance failure
   - resilience overclaim

## 5. 推荐任务结构

### 5.1 输入层

建议文件：

- `tasks/task005/research_brief.md`
- `tasks/task005/grid_context.yaml`
- `tasks/task005/fault_context.yaml`
- `tasks/task005/renewable_context.yaml`
- `tasks/task005/restoration_scope.yaml`

### 5.2 形式化任务包

建议文件：

- `tasks/task005/task.md`
- `tasks/task005/task.yaml`
- `tasks/task005/constraints.yaml`
- `tasks/task005/baseline.yaml`
- `tasks/task005/targets.yaml`
- `tasks/task005/assumptions.yaml`
- `tasks/task005/framing_note.md`
- `tasks/task005/evaluator_rationale.md`

## 6. 最小故障定义

第一版建议采用：

- 单线路或单支路故障切除

原因：

- 便于明确故障前后网络状态
- 便于定义可恢复负荷和不可恢复负荷
- 不会一下子引入过多保护逻辑变量

建议在 brief 中明确：

- 故障位置
- 故障后默认开断状态
- 哪些负荷被隔离

## 7. 最小恢复动作集合

第一版建议只允许以下动作中的一个小子集：

1. 开关重构
2. 新能源/储能支撑
3. 负荷恢复顺序控制
4. 可选：部分负荷切除/保留

第一版不建议同时引入过多动作。

## 8. 推荐 baseline / candidate

### 8.1 baseline

建议 baseline 采用：

- 保守恢复策略
- 少量固定重构动作
- 不显式利用新能源资源

目标是给出一个稳定、可解释的最低恢复基线。

### 8.2 candidate

建议 candidate 体现“新能源接入下的恢复决策”：

- 显式利用新能源/储能支撑
- 或在恢复路径中优先考虑含新能源节点的供电恢复

第一版不要求复杂最优算法，只要体现控制语义变化即可。

## 9. 推荐 evaluator

task005 evaluator 应围绕恢复结果展开。

第一版建议至少定义：

1. `restored_load_ratio`
2. `unserved_critical_load`
3. `constraint_violation`
4. `restoration_action_cost_proxy`

可选：

5. `restoration_depth` 或 `switch_operations`

其中：

- `restored_load_ratio` 是核心
- `unserved_critical_load` 用于体现韧性价值
- `constraint_violation` 保证恢复不是“带病恢复”
- `restoration_action_cost_proxy` 保证恢复不是无代价叠加动作

## 10. success / failure 设计

### 10.1 success path

success 的最低标准不是“最优恢复”，而是：

- 在故障场景下形成比 baseline 更好的恢复结果
- 结果是可审计的
- 边界条件明确

### 10.2 skill-mismatch failure

示例：

- 仍用只适合稳态优化的 skill，直接去做恢复问题

系统应识别：

- 该 skill 可能能改善局部指标
- 但不一定真正回答恢复任务本体

### 10.3 task-mismatch failure

示例：

- fault 定义不清
- 恢复动作范围不清
- 关键负荷定义缺失

系统应冻结，而不是盲目执行。

### 10.4 performance failure

示例：

- candidate 语义正确
- 但恢复结果没有优于 baseline

### 10.5 resilience overclaim

这是 task005 特有的 overclaim failure。

示例：

- 在单故障单工况下的恢复结果
- 被误写成“系统具有韧性”或“普适恢复能力”

系统应将其识别为：

- 韧性过度表述
- claim 必须降级

## 11. 成功标准

以下条件同时满足，视为 task005 第一阶段成功：

1. 故障与恢复问题被明确形式化
2. baseline 可输出结构化恢复结果
3. 至少一个 candidate 与 baseline 可比较
4. 系统能识别 skill mismatch
5. 系统能识别 task mismatch
6. 系统能识别 performance failure
7. 系统能识别 resilience overclaim
8. integration checks 覆盖 task005

## 12. 失败也算成功的条件

如果 candidate 未提高恢复结果，只要满足以下条件，仍然视为有研究价值：

- evaluator 真正运行
- 恢复结果被结构化记录
- failure 类型被明确区分
- claim 被正确收窄
- failure cognition 被写回

## 13. 实施步骤

## Phase 1: 故障恢复问题定义

目标：

在实现前先把故障、恢复和韧性边界定义清楚。

执行内容：

- [ ] 编写 `research_brief.md`
- [ ] 定义 fault 场景
- [ ] 定义恢复动作集合
- [ ] 定义关键负荷
- [ ] 明确 claim 上限
- [x] 编写 `research_brief.md`
- [x] 定义 fault 场景
- [x] 定义恢复动作集合
- [x] 定义关键负荷
- [x] 明确 claim 上限

完成判据：

- [x] task005 不存在故障/恢复语义歧义

## Phase 2: task package 形式化

目标：

将恢复任务形式化为可执行 task package。

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

- [x] task005 task package 可通过 schema / artifact 校验

## Phase 3: baseline 恢复路径

目标：

建立最小 baseline 恢复能力。

执行内容：

- [x] 实现 task005 runtime helpers
- [x] 实现 baseline 恢复策略
- [x] 输出恢复结果与约束状态

完成判据：

- [x] baseline 可输出结构化恢复结果

## Phase 4: candidate 恢复比较

目标：

让新能源资源真正进入恢复决策。

执行内容：

- [x] 实现一个新能源-aware candidate
- [x] 与 baseline 比较恢复结果
- [x] 生成 run / evidence / taste / report / cognition

完成判据：

- [x] 至少一个 candidate 与 baseline 可比较

## Phase 5: failure taxonomy

目标：

建立 task005 的 failure 路径。

执行内容：

- [x] skill mismatch failure
- [x] task mismatch freeze
- [x] performance failure
- [x] resilience overclaim detection

完成判据：

- [x] 四类 failure 都可被结构化记录

## Phase 6: 认知与收口

目标：

从恢复结果中提炼结构化认知。

执行内容：

- [ ] 提炼恢复边界认知
- [ ] 提炼新能源资源作用认知
- [ ] 更新实验记录和设计文档
- [x] 扩展 integration checks

完成判据：

- [x] task005 第一阶段通过最小纵向验证

## 14. 风险

### 风险 1：故障恢复问题过大

缓解：

- 第一版只做单故障、单工况、少动作集合

### 风险 2：恢复动作集合不清，导致 task mismatch

缓解：

- 先把 restoration scope 写清楚，再实现

### 风险 3：把局部恢复结果误写成系统韧性

缓解：

- 单独引入 `resilience overclaim` failure

### 风险 4：又退回成稳态优化问题

缓解：

- evaluator 必须以恢复结果和未恢复负荷为核心，而不是只看稳态指标

## 15. 当前结论

task005 最值得验证的，不是某个单点控制策略有多强，而是：

> 系统是否能把“事件驱动的恢复问题”接入当前框架，并形成结构化的恢复认知与交付判断。
