# DaoShuGuo Pi Harness 总体工作计划

## 1. 计划定位

本计划不是一个“小实验清单”，而是 DaoShuGuo 下一阶段的**总体研发计划**。

目标不是继续在现有 Codex/Claude Code 框架上打补丁，而是系统性地完成一件事：

> 将 DaoShuGuo 的底层 agent harness 迁移到 Pi 可扩展环境上，形成一个可控、可记忆、可约束、可持续迭代的科研 agent runtime。

这意味着，后续工作不再以“能不能再试一步”为核心，而是以：

1. 底层 runtime 是否稳
2. extension / skill / package 分层是否清楚
3. 研究循环是否能被 durable artifacts 承载
4. 真实 task 是否能在该 runtime 上稳定执行
5. cognition 与 skill 是否能在同一个 harness 中闭环

为核心。

## 2. 总体目标

Pi 迁移工作的总体目标分为四层。

### 2.1 Runtime 层

建立一个以 Pi 为核心的 agent runtime，使其：

- 可安装
- 可配置
- 可扩展
- 可被外部 orchestrator 控制
- 可长期保存研究循环状态

### 2.2 Research Loop 层

把 DaoShuGuo 的核心研究循环对象显式化并固化到 Pi package 中：

- task initialization
- skill trial
- cognition constraint
- iteration review
- effectiveness boundary

### 2.3 Vertical Slice 层

至少以 `task003` 为主线，完成：

- 真实 trial
- 结构化记录
- bounded claim
- 下一轮约束生成

### 2.4 Framework 层

最终形成：

- Pi extension
- Pi skills
- DaoShuGuo package
- runtime memory files
- bridge to Python evaluators/tasks
- 可复用的研究框架文档

## 3. 核心原则

### 3.1 不再和成熟 coding agent 产品搏斗

Codex/Claude Code 仍可作为协作式 coding assistant 使用，但不再视为 DaoShuGuo 的底层 autonomous harness。

### 3.2 Pi 负责 harness，不负责重写全部领域底座

Pi 是上层 agent runtime。

现有 DaoShuGuo Python 底座仍继续承担：

- evaluator
- task runtime
- schema validation
- run artifact generation
- cognition card / evidence / report object generation

### 3.3 先做垂直切片，不先做“大一统”

先以 `task003` 做最小完整闭环。

`task004`、`task005` 放入第二阶段扩展，而不是一开始就一起迁移。

### 3.4 cognition 不直接写代码

Pi 中的 cognition worker 只能输出：

- next constraints
- blocked paths
- required tests
- claim ceilings

skill worker 才能改 candidate skill 文件。

### 3.5 durable memory 必须先行

Pi runtime 中，科研循环必须始终落到 durable files：

- `research_loop.md`
- `research_loop.jsonl`

后续可扩展：

- `research_constraints.json`
- `research_dashboard.json`

## 4. 建议架构

建议将 DaoShuGuo-on-Pi 分为四个 workstream。

### Workstream A: Pi Package 基础设施

内容：

- package 结构
- extension 生命周期
- tool 注册
- command 注册
- skill 注册
- package 安装/发现

### Workstream B: DaoShuGuo Research Loop Runtime

内容：

- `research_loop.md`
- `research_loop.jsonl`
- loop event schema
- task init
- skill trial log
- cognition constraint log
- iteration review log

### Workstream C: Python Runtime Bridge

内容：

- task003 bridge
- evaluator bridge
- run artifact bridge
- safe shell invocation policy
- result parsing

### Workstream D: Research Vertical Slice

内容：

- task003 real trial
- cognition constraint generation
- next-iteration request generation
- bounded reporting

## 5. 阶段划分

整个计划建议分 6 个阶段。

---

## Phase 1: Pi Runtime 定型

### 目标

将 Pi 确立为 DaoShuGuo 的底层 harness 候选，并形成稳定本地开发环境。

### 工作内容

- [x] 固化 Pi 本地开发目录与安装方式
- [x] 固化隔离 HOME / session dir / package dir 规范
- [x] 固化本机构建与运行说明
- [x] 确认 `pi --mode json`
- [x] 确认 package install/remove/list/update 行为
- [ ] 确认 extension reload 行为

### 交付物

- Pi runtime setup note
- 本地开发约定文档
- 可重现的构建命令

### 验收标准

- [ ] 任意新环境可按文档复现 Pi build
- [ ] DaoShuGuo Pi package 可以稳定 install/list
- [ ] JSON mode 可输出可解析事件流

### 风险

- Pi 版本升级后 API 变化
- 本地构建依赖网络模型列表抓取

### 风险缓解

- 固化当前验证版本
- 记录构建前提和已知问题

---

## Phase 2: DaoShuGuo Pi Package 1.0

### 目标

完成 DaoShuGuo 在 Pi 中的第一版正式 package，而不是临时原型。

### 工作内容

- [x] 整理 package 目录结构
- [x] 抽象 extension 中的文件写入逻辑
- [x] 明确 skill 的职责边界
- [x] 增加 package README
- [x] 明确 tools 与 commands 的 naming
- [x] 为 package 增加本地 smoke test

### 建议工具集合

- `init_research_task`
- `log_research_iteration`
- `record_skill_trial`
- `record_cognition_constraint`
- `record_iteration_review`
- `run_task003_trial`

### 建议命令集合

- `/daoshuguo`
- `/daoshuguo-init`
- `/daoshuguo-status`

### 交付物

- `pi-packages/daoshuguo-research-loop/`
- package README
- smoke verification script

### 验收标准

- [ ] package 结构清晰且可安装
- [ ] tool/command/skill 语义分层清楚
- [ ] smoke test 可验证 package discovery

---

## Phase 3: Durable Research Loop Runtime

### 目标

把 DaoShuGuo 核心循环从“prompt 内记忆”升级为“文件化 durable runtime”。

### 工作内容

- [x] 规范 `research_loop.md`
- [x] 规范 `research_loop.jsonl`
- [x] 设计 loop event 最小字段
- [x] 明确哪些写 markdown，哪些写 jsonl
- [x] 增加 research loop append helpers
- [x] 增加 session resume 规则

### 推荐 event types

- `init_research_task`
- `skill_trial`
- `cognition_constraint`
- `iteration_review`
- `effectiveness_note`
- `blocked_reason`

### 交付物

- research loop file contract
- example task003 loop files
- helper utilities

### 验收标准

- [ ] 新 session 可仅靠 `research_loop.md/jsonl` 恢复状态
- [ ] 一轮 skill trial 可被完整记录
- [ ] 一轮 cognition constraint 可被完整记录

### 风险

- markdown 与 jsonl 双写不一致

### 风险缓解

- markdown 只写 human-readable summary
- jsonl 保持 append-only 结构化记录

---

## Phase 4: Python Runtime Bridge

### 目标

把 Pi harness 与现有 DaoShuGuo Python runtime 稳定桥接起来。

### 工作内容

- [x] 将 `run_task003_trial` 做成正式 tool
- [x] 统一 bridge 返回格式
- [x] 解析 `orchestrator/main.py real-run-task003` 输出
- [x] 将 run path / run id / report path 写回 loop log
- [x] 增加失败场景记录
- [x] 形成 bridge verification script

### 第二阶段可扩展 bridge

- `run_task004_trial`
- `run_task005_trial`

但本阶段只先做 `task003`。

### 交付物

- extension tool: `run_task003_trial`
- bridge verifier
- demo run artifact

### 验收标准

- [ ] Pi tool 可真实触发 task003 run
- [ ] run result 能写入 `research_loop.jsonl`
- [ ] 错误/失败也能结构化记录

### 风险

- shell bridge 过于脆弱

### 风险缓解

- 只允许固定命令模板
- 不让 Pi 任意拼接危险 shell

---

## Phase 5: Task003 Pi Vertical Slice

### 目标

在 Pi harness 上完成 task003 的最小研究闭环。

### 最小闭环定义

1. init task
2. run task003 trial
3. record skill trial
4. record cognition constraint
5. record iteration review

### 工作内容

- [ ] 定义 task003 loop 启动方式
- [ ] trial 完成后自动/半自动记录结果
- [ ] 增加 `record_cognition_constraint`
- [ ] 增加 `record_iteration_review`
- [ ] 输出 task003 bridge demo 目录
- [ ] 验证下一轮约束可落回 `research_loop.md/jsonl`

### 交付物

- `analysis/pi_harness/task003_*`
- 完整 task003 loop log
- cognition constraint sample
- iteration review sample

### 验收标准

- [ ] task003 至少形成 1 轮真实 loop
- [ ] skill trial 与 cognition constraint 被分开记录
- [ ] claim boundary 被记录
- [ ] loop files 可供 Pi 下一个 session 继续

---

## Phase 6: Pi-based Skill-Cognition Loop 设计收敛

### 目标

在 task003 vertical slice 基础上，明确 Pi 环境下 skill/cognition 双循环的正式设计。

### 工作内容

- [ ] 定义 skill worker responsibilities
- [ ] 定义 cognition worker responsibilities
- [ ] 定义 next-iteration request contract
- [ ] 定义哪些约束必须写入 loop files
- [ ] 定义哪些内容仍留在 Python runtime
- [ ] 更新 AGENTS.md / Agent.md 研究结论

### 交付物

- Pi-based loop design note
- task003 lessons learned
- task004/task005 扩展建议

### 验收标准

- [ ] 可以明确回答 Pi 环境下什么属于 extension、skill、runtime、cognition
- [ ] 可以形成下一阶段 task004/task005 迁移路线

## 6. 不纳入本轮的工作

为了防止计划膨胀，以下内容不纳入当前计划：

- [ ] 直接在 Pi 上重建全部 DaoShuGuo schema 系统
- [ ] 一次性把 task004、task005 全迁过去
- [ ] 做完整的 Pi RPC orchestration 平台
- [ ] 实现 fully autonomous paper-writing agent
- [ ] 解决所有 LLM provider 接入问题

## 7. 里程碑

### M1: Pi Runtime 可复现

判据：

- Pi build 可复现
- package install/list 正常
- JSON mode 正常

### M2: DaoShuGuo Pi Package 稳定

判据：

- repo-local package 可安装
- extension/skill/command/tool 定义稳定

### M3: task003 bridge 可运行

判据：

- Pi tool 触发真实 task003 run
- 结果写入 loop files

### M4: task003 最小 loop 成立

判据：

- trial + cognition constraint + iteration review 三类记录齐全

### M5: Pi-based loop design 定型

判据：

- 明确下一阶段如何在 Pi 上做真正 skill-cognition 闭环

## 8. 风险与停机点

### 风险 1：Pi runtime 过于灵活，缺少强约束

缓解：

- 把关键行为收敛到 tool contract
- 不让 agent 直接自由操纵全部 shell

### 风险 2：Pi package 只是换了壳，研究循环仍然散

缓解：

- 强制所有关键循环写入 `research_loop.md/jsonl`

### 风险 3：bridge 过度依赖现有 Python runtime

缓解：

- 当前允许依赖
- 但要明确 runtime/extension 边界，后续再决定是否下沉

### 风险 4：过早重新追求多轮 autonomous loop

缓解：

- 本阶段先只做 task003 一轮完整 vertical slice
- 不直接回到“两轮真实 autonomous coding + cognition”重压测试

### 停机点

若出现以下情况，应停止扩展而先做总结：

- Pi package 无法稳定安装/发现
- extension tool 无法稳定调用真实 task runtime
- durable loop files 不能支持 session resume
- task003 vertical slice 连一轮都走不通

## 9. 建议执行顺序

推荐严格按下列顺序执行，不要跳：

1. Pi runtime 定型
2. DaoShuGuo Pi package 1.0
3. durable research loop runtime
4. task003 bridge
5. task003 vertical slice
6. Pi-based loop design 收敛

## 10. 成功标准

本计划成功不等于“Pi 能跑起来”，而是：

1. DaoShuGuo 有了可持续的 Pi package 形态
2. research loop 变成 durable runtime，而不是 prompt 记忆
3. task003 能被 Pi harness 真实执行并记录
4. Pi 成为下一阶段 skill-cognition loop 的可信底座

## 当前状态

截至当前批次，已完成：

- Phase 1 的大部分 runtime 定型工作
- Phase 2 的 Pi package 1.0 基础收敛
- Phase 3 的 durable loop file contract 基础收敛
- Phase 4 的 task003 bridge 最小可运行验证

尚未完成但应作为下一批次重点推进：

- extension reload 行为验证
- `record_iteration_review`
- `record_cognition_constraint` 在真实流程中的使用
- `record_iteration_review` 在真实流程中的使用
- Pi JSON/RPC mode 触发真实工具调用而非外部 verifier 脚本

## 最新边界结论

已验证：

- Pi JSON mode 可以成功启动
- repo-local DaoShuGuo package 可以成功加载
- `/skill:daoshuguo-research-create` 可以成功展开为 skill payload

当前阻塞：

- Pi agent 在尝试联系 provider 时因 `Connection error` 失败
- 因此尚未进入真正的 tool-calling 阶段

这说明当前下一步的关键不再是 package scaffolding，而是二选一：

1. 提供可用的 Pi provider/auth 路径
2. 用 Pi SDK/customTools 建立无外部 LLM 的本地 stub loop

## 最新进展

当前已额外验证：

- 通过 `openai` provider + `gpt-5.4` + `https://relay.nf.video/v1`
- Pi 已真实生成 `toolCall`
- Pi 已真实执行 DaoShuGuo 自定义工具
- `init_research_task` 与 `record_iteration_review` 已完成真实 `tool_execution_*`
- durable loop files 已被真实工具调用写入

因此，本计划已经跨过：

> “Pi package 可被加载”

进入到：

> “Pi 在真实 provider 下已能驱动 DaoShuGuo 工具调用”

当前剩余问题主要集中在：

- `openai-responses` continuation / reasoning item persistence compatibility
- 多步 loop 稳定性，而不是 package/harness 可用性
