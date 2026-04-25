# Pi 真实 Research Loop 稳定化计划

## 1. 计划目标

当前 DaoShuGuo-on-Pi 已经完成一个关键跨越：

> 第一条真实 Pi tool-calling loop 已经成立。

我们已经证明：

- Pi package 可加载
- 真实 provider 可调用
- 模型可生成真实 `toolCall`
- Pi 可执行 DaoShuGuo 自定义工具
- `research_loop.md/jsonl` 可被真实工具写入

但当前 loop 仍不稳定，主要问题已经收敛为：

1. 某些 provider / relay 对 `openai-responses` continuation 的兼容性不足
2. 单个长回合中混合过多步骤，容易触发 reasoning item / store / continuation 问题
3. loop runner 仍然更像“顺序调用 prompt”，而不是一个有明确状态推进和停机点的 loop runtime

因此，本计划的目标是：

> 将当前“已经能跑起来”的 Pi tool-calling loop，收敛成一个可重复、可调试、可扩展的稳定 runtime。

## 2. 总体原则

### 2.1 不再追求“大而全”的单回合

Pi agent 不应在一个超长回合中完成：

- task init
- real run
- skill trial record
- cognition constraint
- iteration review
- 再继续下一轮

这会放大 provider continuation 风险。

应改为：

> 一轮一个 bounded step，一步一个 bounded turn。

### 2.2 优先保证 loop 可持续，而不是一次性聪明

当前最重要的不是让模型一口气“像研究生一样思考完整”。

更重要的是：

- 每一步都能可靠落盘
- 每一步都能恢复
- 每一步都可被外部 orchestrator 观察

### 2.3 research loop 必须可恢复

每一轮必须依赖 durable state，而不是 prompt 历史。

核心文件：

- `research_loop.md`
- `research_loop.jsonl`
- 可扩展：
  - `research_state.json`
  - `research_requests/`
  - `research_reviews/`

## 3. 工作主线

后续稳定化工作分为五条主线：

### 主线 A：Provider/Model 稳定性分层

目标：

明确哪些 provider/model 适合：

- 单步工具调用
- 多步短回合
- 长回合连续 loop

### 主线 B：Loop Runner 重构

目标：

把当前 `run_pi_task003_loop.py` 从简单 prompt 串行器，升级为真正的 loop runner。

### 主线 C：Durable State 强化

目标：

让 loop 状态不仅写 markdown/jsonl，还具备结构化推进语义。

### 主线 D：Task003 稳定化

目标：

让 task003 成为 Pi runtime 上的稳定最小垂直切片。

### 主线 E：向 task004/task005 扩展的预研

目标：

不是马上迁移，而是提前规划其适配点。

## 4. 阶段划分

---

## Phase 1: Provider / Model Compatibility Matrix

### 目标

建立 Pi 真实运行下的 provider/model 兼容性矩阵。

### 要回答的问题

1. 哪些 provider/model 能正常输出文本
2. 哪些 provider/model 能正常产生 `toolCall`
3. 哪些 provider/model 能完成一次 `tool_execution`
4. 哪些 provider/model 能稳定完成两次以上短回合调用
5. 哪些 provider/model 会在 continuation 处失败

### 建议测试对象

- `openai / gpt-5.4 / relay.nf.video`
- `openai / gpt-5.4 with thinking=off`
- `openai / gpt-5.4 with minimal bounded single-step prompts`
- `anthropic-compatible / baidu adapter` 作为候选线保留
- 其他本机可用 provider 作为对照

### 工作内容

- [x] 抽象 `provider_smoke_runner`
- [x] 记录 text-only pass/fail
- [x] 记录 single-tool-call pass/fail
- [x] 记录 multi-turn continuation pass/fail
- [ ] 输出兼容性矩阵

### 交付物

- `analysis/pi_harness/provider_matrix/*.json`
- `analysis/pi_harness/provider_matrix/*.md`

### 验收标准

- [ ] 至少明确一条“可稳定单步工具调用”的 provider/model 组合
- [ ] 明确一条“当前不适合长回合 continuation”的 provider/model 组合

---

## Phase 2: Loop Runner Refactor

### 目标

将 `run_pi_task003_loop.py` 重构为分段、可恢复的 loop runtime。

### 当前问题

现在 runner 的问题是：

- 一次启动中串多个 prompt
- 每个 prompt 的结果只粗暴收集 stdout
- 没有清晰 state machine
- 没有 step-level recovery

### 目标架构

建议把 loop runner 拆为：

1. `init_step`
2. `task_trial_step`
3. `skill_record_step`
4. `cognition_constraint_step`
5. `iteration_review_step`

每个 step：

- 独立 prompt
- 独立结果
- 独立可重试
- 独立写状态

### 工作内容

- [x] 定义 step state enum
- [x] 增加 `research_state.json`
- [x] 为每个 step 记录：
  - started_at
  - finished_at
  - status
  - provider/model
  - last_error
- [x] 支持从未完成 step 恢复
- [x] 将 loop 结果写入专门目录

### 交付物

- `scripts/run_pi_task003_loop.py` 重构版
- `analysis/pi_harness/pi_json_loop_task003_state/`

### 验收标准

- [ ] 任意中断后能从最后未完成 step 恢复
- [ ] 不会因为前一步完成而重复污染 loop files

---

## Phase 3: Durable State 强化

### 目标

让 Pi 研究循环不只靠 `research_loop.md/jsonl`，还拥有明确的 machine-readable state。

### 建议新增文件

- `research_state.json`
- `research_requests/iter_XXX.json`
- `research_reviews/iter_XXX.json`

### 含义

#### `research_loop.md`

人读的摘要

#### `research_loop.jsonl`

append-only event log

#### `research_state.json`

当前状态快照

#### `research_requests/*`

下一轮技能/认知请求

#### `research_reviews/*`

对本轮 loop 的结构化评审

### 工作内容

- [x] 设计 `research_state.json` 字段
- [x] 设计 request/review 文件格式
- [x] 明确这些文件由谁写
- [x] 明确 resume 时优先读什么

### 交付物

- `docs/research-loop-state-contract.md`
- `analysis/pi_harness/task003_state_demo/*`

### 验收标准

- [ ] 新 session 可只靠这些文件恢复
- [ ] loop runner 不依赖隐式 prompt 历史

---

## Phase 4: Task003 Stable Vertical Slice

### 目标

把 task003 从“能跑一次”推进到“可重复跑、可分析、可复盘”。

### 工作内容

- [x] 确认 task003 单步 trial 稳定
- [x] 确认 skill trial record 稳定
- [x] 让 `record_cognition_constraint` 进入真实 loop
- [x] 让 `record_iteration_review` 进入真实 loop
- [x] 输出一条完整且整洁的 task003 loop artifact 链

### 完整链条

1. `init_research_task`
2. `run_task003_trial`
3. `record_skill_trial`
4. `record_cognition_constraint`
5. `record_iteration_review`

### 交付物

- `analysis/pi_harness/task003_stable_loop/`

### 验收标准

- [ ] 上述五步都能真实完成
- [ ] `research_loop.md/jsonl` 与 state files 一致
- [ ] run / report / review 都可追踪

---

## Phase 5: Multi-step Short-turn Loop

### 目标

尝试在同一 task 上完成 2 轮 Pi short-turn loop，但不再要求一个长回合里自动完成。

### 核心思想

将：

- 长回合、多 tool、多 continuation

改为：

- 短回合、单步推进、每步落盘

### 工作内容

- [x] iteration 1 完整完成
- [x] 生成 iteration 2 request
- [x] 用 iteration 1 的 cognition constraint 驱动 iteration 2
- [x] 记录失败/停滞信号

### 验收标准

- [x] iteration 2 明显受 iteration 1 约束影响
- [x] 即便中途失败，也能判断是 provider 问题还是 loop 设计问题

---

## Phase 6: Toward task004/task005

### 目标

为更复杂任务做迁移预研，而不是立刻迁移。

### task004 关注点

- boundary overclaim
- task mismatch
- hosting capacity boundary

### task005 关注点

- event-driven restoration
- more complex run artifacts
- cognition constraint 粒度更高

### 工作内容

- [ ] 识别 task004 所需新工具
- [ ] 识别 task005 所需新工具
- [ ] 判断哪些逻辑必须继续留在 Python runtime
- [ ] 输出扩展路线

## 5. 关键设计约束

### 5.1 不要求 provider 完美，要求 loop 可诊断

provider 失败不是最坏情况。

最坏情况是：

- provider 失败但系统不知道失败在哪

所以：

- 每一步必须记录 provider/model
- 每一步必须记录错误类型

### 5.2 尽量避免长上下文持续对话

当前 relay 已暴露 `openai-responses` continuation 问题。

因此：

- 优先用短回合
- 每回合只解决一步
- 多用 durable state 串联，而不是多用上下文串联

### 5.3 避免让模型自己“猜状态”

loop runner 必须显式告诉它：

- 现在是哪个 step
- 上一步成功还是失败
- 当前应调用哪个工具

## 6. 风险

### 风险 1：provider 兼容性继续不稳定

缓解：

- provider matrix
- short-turn loop
- stateful resume

### 风险 2：tool 太多，模型仍然乱选

缓解：

- 用 `promptSnippet` / `promptGuidelines`
- 必要时动态开关 active tools

### 风险 3：loop files 被重复污染

缓解：

- step state
- idempotent write policy
- append-only + snapshot 分层

### 风险 4：task003 之外扩展过快

缓解：

- 先把 task003 做稳
- 再做 task004/task005 预研

## 7. 建议执行顺序

建议按如下顺序推进，不跳步：

1. provider/model compatibility matrix
2. loop runner refactor
3. durable state 强化
4. task003 stable vertical slice
5. multi-step short-turn loop
6. task004/task005 迁移预研

## 8. 成功标准

本计划成功意味着：

1. Pi 真实 tool-calling loop 能稳定完成一条 task003 垂直切片
2. loop 不再依赖长回合 continuation
3. 状态恢复和失败诊断清晰
4. DaoShuGuo-on-Pi 从“能跑”变成“可重复运行”

## 当前状态

截至当前批次，以下内容已在 `task003` 上成立：

- 一条真实 provider 驱动的 Pi tool-calling loop
- step-based runner
- `research_state.json`
- per-step request/result artifacts
- durable loop files与 state files 的一致性校验

当前下一批次应重点推进：

- 输出 provider/model compatibility matrix
- 开始 `Phase 6: Toward task004/task005`
- 输出 `iteration 1 / 2` 的抽象经验
