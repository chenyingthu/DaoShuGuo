# 真实 Agentic Skill-Cognition 多轮闭环计划

## 1. 计划目标

当前仓库已经证明了两件事：

1. 规则化底座可以支持 skill / cognition / effectiveness 的对象化、验证与写回
2. 真实 Codex agent 已经可以参与 cognition workflow，并在单轮测试中暴露规则层盲点

但当前还没有证明下面这件更关键的事情：

> 真实的 `skill agent` 与 `cognition agent` 能否在同一个任务上形成 **超过 1 轮** 的联动闭环，并且每一轮的认知都真实改变下一轮技能探索。

因此，本计划的目标不是继续补单轮认知 demo，而是建立一个 **多轮真实 agentic loop experiment**，用它回答：

1. 真实 agent 能否驱动 skill iteration，而不是只做 cognition 评论
2. 真实 cognition agent 能否产生对下一轮有约束力的更新，而不是泛泛建议
3. skill agent 在认知约束下是否真的会改变候选技能实现
4. 连续 2+ 轮后，系统哪些地方会前进，哪些地方会卡住
5. 哪些环节适合 agent，哪些环节仍必须由规则和 evaluator 托底

## 2. 为什么现在必须做这件事

当前已有多轮迭代，主要发生在：

- 规则化 compare / semantic / upgrade / literature / explanation / effectiveness 链路
- 预定义 skill 函数的真实执行

而真实 agentic 的情况是：

- cognition 侧已有真实 agent 单轮和 workflow 单轮
- skill 侧仍主要依赖预写好的 Python solver
- loop controller 目前仍是 bootstrap controller，而不是由真实 cognition worker 驱动

这意味着当前系统更准确的状态是：

- **规则化研究框架 + 单轮真实 cognition agents**

而不是：

- **真实 skill agent 与 cognition agent 共同演化的多轮研究系统**

如果不补这一步，就无法回答最初设计里的核心问题：

> 为什么一定要把 agent 纳入这个系统？

## 3. 核心判断

### 3.1 这次必须用真实 agent，不再允许“伪多轮”

这里的“伪多轮”包括：

- 规则脚本生成 `cognition_to_skill_update`，但没有 agent 参与
- 预先写死多种 skill，然后仅靠切换 strategy 名称假装是 skill evolution
- cognition agent 只做总结，没有输出下一轮明确约束
- 没有真正生成新的候选 skill 资产，只是从已有 skill 中重新挑选

本计划要求：

- 至少一部分 skill iteration 必须由真实 agent 产出
- 至少一部分 cognition-to-skill update 必须由真实 cognition agent 产出
- 必须连续运行 2+ 轮，并记录每轮的约束变化

### 3.2 规则层仍然必须存在

这次不是用 agent 替代全部系统。

规则层仍然负责：

- task / run / evidence / report / taste 的结构化对象
- evaluator
- schema validation
- reference existence
- overclaim guard
- deterministic pass/fail gating

agent 的职责是：

- 生成或修改 candidate skill
- 解释结果与 failure
- 将认知翻译为下一轮 search-space constraints

### 3.3 闭环必须由对象流串起来

本次 experiment 不是“让两个 agent 对话看看”。

必须有正式对象流：

1. `skill_agent_iteration_request`
2. `skill_agent_output`
3. `run`
4. `cognition_event`
5. `llm_cognition_workflow_output`
6. `agentic_cognition_to_skill_update`
7. `next skill iteration request`

否则无法证明 agent 真的参与了 loop，而不是聊天式辅助。

## 4. 我们现在能做什么，不能做什么

### 4.1 当前明确能做的

基于现有仓库，已经具备：

- 可运行的真实 task slices：`task003` / `task004` / `task005`
- 可运行的真实 evaluator
- 可运行的真实 candidate skill Python modules
- 可运行的真实 cognition jobs / workflows
- 可验证的 loop artifacts
- 可记录 failure taxonomy / overclaim / mismatch / cognition upgrade

这意味着我们已经能做：

1. 让 agent 基于已有 skill 代码与 loop update 生成一个新 candidate skill 版本
2. 运行该 skill，并得到真实 run artifacts
3. 让 cognition workflow 读取这些 artifacts，输出下一轮 update
4. 再让下一个 skill agent iteration 在这个 update 下继续

### 4.2 当前明确做不到或风险很高的

当前还不适合直接追求：

1. 开放式无限技能发明
2. 自动联网查文献后再动态改技能
3. 大规模并行多 agent 自治而无强 guardrails
4. 多任务同时进化
5. 完整科学论文级别自主结论生成

当前最合理的做法是：

- 选定一个 task slice
- 选定一个 skill family
- 在强约束下做 2 到 3 轮真实闭环

## 5. 为什么首选 task003

建议第一轮真实多迭代闭环以 `task003` 为主试点。

原因：

1. `task003` 已经有最清楚的语义结构
   - success
   - skill mismatch
   - performance failure
2. task 本体清晰
   - 新能源接入场景下的无功支撑/优化控制
3. 认知约束已经相对明确
   - 不应退回 weak-shunt 替代主线
   - 应继续在 renewable-aware control family 内演化
4. skill 修改成本较低
   - 主要是 inverter Q / coordination 逻辑调整
5. 更容易观察“认知是否真的改变 skill 探索”

`task004` 和 `task005` 适合作为第二阶段扩展：

- `task004` 适合测边界与 overclaim
- `task005` 适合测事件驱动恢复与 task freeze

但它们在第一轮多迭代中更容易受 task definition 和 evaluator 复杂度影响。

## 6. 这次 experiment 的最小成功标准

本计划的成功，不是“agent 运行了两次”，而是以下条件同时成立：

1. 至少有 2 轮连续真实 skill agent 迭代
2. 每一轮 skill 代码或参数逻辑都发生了明确变化
3. 至少有 2 轮连续真实 cognition workflow
4. cognition 输出显式改变了下一轮 skill 请求
5. 每一轮都保留真实 run / evidence / cognition / update artifacts
6. 最终能分析出：
   - 什么前进了
   - 什么没前进
   - 什么其实不适合 agent 当前能力

## 7. 新增对象建议

本轮建议新增最小对象，不一次做重型 schema 体系。

### 7.1 `skill_agent_iteration_request`

用途：

- 明确给 skill agent 的输入约束

建议字段：

- `task_ref`
- `source_update_ref`
- `base_skill_ref`
- `iteration_index`
- `allowed_change_scope`
- `blocked_paths`
- `required_tests`
- `output_skill_path`

### 7.2 `skill_agent_iteration_result`

用途：

- 记录本轮 skill agent 具体做了什么

建议字段：

- `request_ref`
- `produced_skill_ref`
- `code_paths`
- `change_summary`
- `self_reported_risks`
- `expected_behavior_change`

### 7.3 `agentic_cognition_to_skill_update`

用途：

- 与当前 bootstrap `cognition_to_skill_update` 区分
- 明确这是由真实 cognition workflow 生成的 update

建议字段：

- `task_ref`
- `source_event_ref`
- `source_workflow_output_refs`
- `source_run_refs`
- `next_iteration_skill_constraints`
- `next_iteration_evaluator_constraints`
- `search_priority_updates`
- `blocked_skill_families`
- `required_discriminating_tests`
- `confidence`

### 7.4 `agentic_loop_iteration_review`

用途：

- 逐轮判断这次 agentic iteration 是否真的推进了系统

建议字段：

- `iteration_index`
- `task_ref`
- `skill_iteration_result_ref`
- `cognition_update_ref`
- `actual_progress`
- `stagnation_signals`
- `cheating_signals`
- `verdict`

## 8. 推荐总体技术路线

### 路线 A：最小真实 agentic loop

做法：

1. 由主 orchestrator 生成 `skill_agent_iteration_request`
2. 真实 Codex agent 读取 request，修改或新增一个 candidate skill 文件
3. orchestrator 运行这个新 skill
4. cognition workflow 读取新 run artifacts
5. cognition workflow 生成 `agentic_cognition_to_skill_update`
6. 再生成下一轮 `skill_agent_iteration_request`

优点：

- 与现有仓库兼容最好
- 最容易验证
- 最容易查作弊

缺点：

- agent autonomy 仍受 orchestrator 强约束

### 路线 B：让 cognition workflow 直接产出 skill patch brief

做法：

- 在路线 A 基础上，cognition workflow 直接输出下一轮 skill patch brief

优点：

- loop 更紧密

缺点：

- 更容易让 cognition 退化成弱代码规划器
- 可能过早把高层 cognition 拉到低层代码细节

### 路线 C：多 agent 自治共识 loop

做法：

- 多 skill agents + 多 cognition agents 自主协商

不建议现在做。

原因：

- 难验证
- 难查作弊
- 当前 evaluator / task slices 还不足以支撑

**建议决策：先做路线 A，并有限吸收路线 B。**

## 9. 第一阶段 experiment 设计

## Phase 1: Agentic Loop Infrastructure

目标：

建立真实 agentic multi-iteration 所需的最小对象和 runner。

执行内容：

- [ ] 定义 `skill_agent_iteration_request`
- [ ] 定义 `skill_agent_iteration_result`
- [ ] 定义 `agentic_cognition_to_skill_update`
- [ ] 定义 `agentic_loop_iteration_review`
- [ ] 新增专用目录：
  - `agents/skill/requests/`
  - `agents/skill/results/`
  - `analysis/agentic_loop/task003/`
- [ ] 实现最小 runner：
  - 生成 request
  - 调用真实 Codex skill agent
  - 写回 result

完成判据：

- [ ] 可以正式发起一轮真实 `skill agent` 请求并记录结果

## Phase 2: Single Iteration End-to-End

目标：

跑通第 1 轮真实 `skill agent -> run -> cognition workflow -> update`

执行内容：

- [ ] 为 `task003` 选择 base skill
- [ ] 基于已有 loop update 生成第 1 轮 skill request
- [ ] 让真实 Codex agent 生成/修改候选 skill
- [ ] 运行真实 task003 run
- [ ] 运行真实 cognition workflow
- [ ] 生成第 1 个 `agentic_cognition_to_skill_update`
- [ ] 输出 iteration review

完成判据：

- [ ] 第 1 轮完整闭环可运行且 artifacts 完整

## Phase 3: Second Iteration Driven by First Cognition

目标：

证明第 2 轮不是重复第 1 轮，而是真正受第 1 轮 cognition 驱动。

执行内容：

- [ ] 用第 1 轮 cognition update 生成第 2 轮 request
- [ ] 检查 request 是否与第 1 轮显著不同
- [ ] 让真实 Codex skill agent 执行第 2 轮
- [ ] 运行真实 run 与 cognition workflow
- [ ] 生成第 2 轮 update 和 review

完成判据：

- [ ] 第 2 轮 request 与第 1 轮存在可解释的受约束变化
- [ ] skill agent 的实现变化与该约束一致

## Phase 4: Anti-Cheating Review

目标：

检查多轮闭环是否只是形式上的“换壳”。

执行内容：

- [ ] 检查 skill agent 是否只是改变量名/注释
- [ ] 检查 cognition update 是否只是重复旧建议
- [ ] 检查第 2 轮 skill 变化是否真的来自第 1 轮 cognition
- [ ] 记录所有作弊信号

完成判据：

- [ ] 对每轮都能说明“为什么它是真变化”或“为什么它是假变化”

## Phase 5: Capability Boundary Analysis

目标：

从 experiment 中总结 agentic loop 的真实能力边界。

执行内容：

- [ ] 总结 agent 擅长的变化类型
- [ ] 总结 agent 不擅长的变化类型
- [ ] 总结哪些约束能稳定驱动 skill 演化
- [ ] 总结哪些 cognition 输出仍太泛，无法驱动下一轮
- [ ] 形成下一阶段建议

完成判据：

- [ ] 能清楚回答“what can be done / what can not”

## 10. 推荐实现细节

### 10.1 skill agent 的工作边界

skill agent 不应被允许：

- 随意改 evaluator
- 随意改 task definition
- 一轮中跨多个任务乱改
- 直接修改 cognition artifacts

skill agent 只允许：

- 修改指定 skill 文件
- 新增一个候选 skill 文件
- 在 request 允许范围内调整搜索逻辑、参数逻辑或协同控制逻辑

### 10.2 cognition agent 的工作边界

cognition agent 不应：

- 直接输出代码 patch
- 直接决定 evaluator pass/fail
- 越过 evidence 做宏大 claim

cognition agent 应：

- 输出下一轮 skill search constraints
- 输出 blocked paths
- 输出 discriminating tests
- 输出当前 claim ceiling

### 10.3 iteration review 必须审“变化”

每轮 review 必须回答：

1. 本轮 skill 改了什么
2. 本轮 cognition 发现了什么新东西
3. 下一轮为什么必须改成这样
4. 有没有重复空转

## 11. 推荐第一批测试问题

对 `task003`：

### Iteration 1

问题：

- 在保持 renewable-aware control family 的前提下，能否让 skill agent 生成一个 `shunt + inverter` 协同 candidate？

### Iteration 2

问题：

- 如果 iteration 1 仍未过 evaluator，cognition agent 能否指出是：
  - 参数方向错误
  - evaluator 盲点
  - control space 仍太弱
  - 还是 task boundary 太窄

并据此真正改变 iteration 2 的 skill request？

## 12. 风险

### 风险 1：skill agent 只是做表面改动

缓解：

- 必须记录 `change_summary`
- 必须有 diff-based review
- 必须运行真实 run

### 风险 2：cognition agent 只输出泛泛建议

缓解：

- 强制输出：
  - `blocked_paths`
  - `required_discriminating_tests`
  - `search_priority_updates`

### 风险 3：第 2 轮其实没有被第 1 轮驱动

缓解：

- request 必须显式引用上一轮 update
- review 必须审 request 差异

### 风险 4：loop 进入无效空转

缓解：

- iteration review 中加入 `stagnation_signals`
- 超过 2 轮无实质变化就停止并总结

## 13. 成功标准

本计划成功的标准不是“agent 参与了”，而是：

1. 至少一个 task 完成 2 轮真实 agentic loop
2. 第 2 轮 skill request 明显由第 1 轮 cognition update 改写
3. 至少一轮 skill agent 产生了真实可执行的新 candidate skill 变体
4. 至少一轮 cognition workflow 产生了真正可操作的下一轮约束
5. 最终可以明确写出：
   - agent 适合做什么
   - agent 目前做不好什么
   - 规则底座仍必须守住哪些环节

## 14. 建议输出

本计划执行后，应至少得到：

- 多轮 agentic loop artifacts
- 一份 anti-cheating review
- 一份 capability boundary report
- 对 AGENTS.md / Agent.md 的进一步修正

最终我们要的不是一句“agent 也能 loop”，而是：

> 一份有证据的、能解释真实能力边界的结论。
