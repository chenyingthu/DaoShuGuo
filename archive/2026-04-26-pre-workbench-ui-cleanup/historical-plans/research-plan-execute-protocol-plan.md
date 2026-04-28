# Research Plan-Execute Protocol 计划

## 1. 计划定位

本计划用于定义本项目下一阶段的主线工作：

> 将当前已经跑通的真实 agentic skill-cognition loop，升级为类似 `$plan-execute` 的科研执行协议。

这里的重点不是新增一个 task，也不是继续追求某个 task003/task004/task005 指标更好，而是把项目从“能跑起来的研究原型”推进到“有执行纪律、可监管、可返工、可复用的科研 Agent workflow”。

## 2. 背景判断

当前项目已经完成了几个重要突破：

1. `skill / cognition / effectiveness` 三类资产已经可以对象化。
2. `generic loop engine + task adapter + diagnosis layer` 已经能跑通 fixture、task004、task005 adapter。
3. task003 的真实 agentic loop 已经完成至少两轮真实闭环。
4. 第二轮真实 skill agent 产生了有效 candidate，并在 task003 run_0021 中改善了关键指标。
5. LLM cognition workflow 能基于 run evidence 生成下一轮 skill constraints。

但当前系统仍然暴露出明显不足：

1. review 仍是记录性 artifact，还没有成为真正的执行硬门。
2. repair loop 还没有制度化，schema 失败、认知失配、技能退化仍主要靠人工介入修复。
3. controller 仍存在加工 cognition 输出的痕迹，例如压缩 search priorities、归一化字段、选择下一步。
4. agent context 还没有形成稳定协议，每轮 prompt/context 组织仍散落在脚本中。
5. 成熟 workflow 的质量纪律不足，无法像 `$plan-execute` 一样形成稳定的“执行 -> review -> fix -> approve”循环。

因此，下一阶段最重要的不是继续扩展 task006，而是先把科研执行协议固化。

## 3. 与 `$plan-execute` 的对照

`$plan-execute` 的成熟机制可以概括为：

1. 读取计划。
2. 拆分执行批次。
3. 调用实现 Agent。
4. Orchestrator 不直接写代码，只做 review 和调度。
5. Review 形成正式 artifact。
6. 如果 `NEEDS_FIX`，将问题交回实现 Agent。
7. 迭代直到 `APPROVED`。
8. 更新计划进度并汇报。

本项目应学习的不是它的 coding 场景，而是它的执行纪律：

- 角色清晰。
- 证据清晰。
- 质量门清晰。
- 返工路径清晰。
- 结束条件清晰。

科研版协议需要保留这些优点，但扩展为：

- 不只检查 build，还检查 evaluator、baseline、claim、taste、evidence。
- 不只修代码，还修 skill、evaluator、adapter、cognition prompt、task framing。
- 不只判断 pass/fail，还判断研究价值、边界、可推广性和成果等级。

## 4. Research Plan-Execute 的目标

建立一个统一科研执行协议，名称暂定为：

`research-plan-execute`

它的目标是：

1. 接收一个 research plan。
2. 将计划拆成可执行 research batches。
3. 为每个 batch 构造 agent context pack。
4. 调用对应 worker：
   - skill worker
   - effectiveness worker
   - cognition worker
   - delivery worker
   - repair worker
5. 生成对象化产物。
6. 通过 review gate 审查。
7. 根据 verdict 决定 approve、repair、pause 或 stop。
8. 将结论、失败、认知和后续路线写回计划与资产库。

## 5. 核心原则

### 5.1 Review Gate 是硬门

后续所有真实 agentic loop 不得只因为阶段脚本运行完就进入下一轮。

必须满足：

- 有 review artifact。
- review artifact 明确 verdict。
- verdict 为 `approved` 才能无条件进入下一轮。
- verdict 为 `real_progress` 时只能进入 `bounded_next_iteration`，且必须带有 claim boundary、required ablation 或 required repair note。
- verdict 为 `needs_fix`、`stagnation`、`cheating_suspected`、`insufficient_evidence` 时必须进入 repair path。

### 5.2 Repair Loop 必须制度化

任何失败都必须路由到具体 repair worker，而不是由 controller 临场修改。

标准 repair 类型包括：

1. `repair_skill`
2. `repair_evaluator`
3. `repair_adapter`
4. `repair_cognition_prompt`
5. `repair_context_pack`
6. `repair_schema`
7. `repair_runtime_binding`
8. `human_review`

Repair loop 必须有上限：

- 同一 `repair_request` 最多自动重试 2 次。
- 第 3 次仍失败时必须转入 `human_review`。
- 不允许通过放宽 evaluator、删除 required refs 或降低 schema 要求来“修复”失败。
- 每次 repair 都必须产生 `repair_result`，并回链到原始 failure artifact。

### 5.3 Controller 仍然不下场

research-plan-execute controller 只能：

- 调度 worker。
- 组装输入对象。
- 执行 verifier。
- 写状态和索引。
- 根据 review/diagnosis verdict 路由。

不得：

- 直接改 skill。
- 直接解释研究结果。
- 直接决定成果等级。
- 直接把失败包装成认知提升。
- 直接压缩、改写或重排 cognition worker 的实质建议。
- 在没有 review gate 的情况下构造下一轮 request。

### 5.4 Agent Context Pack 必须标准化

每个 worker 调用前必须形成 `agent_context_pack`。

它至少包含：

- mission
- role boundary
- task refs
- prior artifacts
- allowed changes
- blocked paths
- evaluator/baseline refs
- review history
- current hypothesis
- required output schema
- stop conditions
- token / context budget
- artifact provenance digest
- redaction and secret policy
- expected failure modes
- previous repair attempts

Context pack 必须是落盘对象，而不是临时 prompt 字符串。Agent prompt 只能由 context pack 渲染出来，不能在执行脚本中散落拼接。

### 5.5 计划更新必须成为协议的一部分

像 `$plan-execute` 更新 checklist 一样，科研执行协议也必须更新：

- research plan checklist
- review log
- object registry
- cognition memory
- skill registry
- effectiveness/delivery summary

### 5.6 不重复造 loop engine

research-plan-execute 不是替代当前 `generic loop engine`，而是在其上增加科研执行纪律。

关系应明确为：

- `generic loop engine` 继续负责阶段调度、对象链、状态机和 adapter 接入。
- `research-plan-execute` 负责 plan/batch/context/review/repair/approval 这些执行协议。
- `generic diagnosis layer` 继续负责 problem_class、routing policy 和 diagnosis 校验。
- 新实现不得复制一套 task-specific loop runner。

如果某项功能已经存在于 generic loop engine 或 diagnosis layer，research-plan-execute 只能调用或扩展，不能重写。

### 5.7 Agent Runtime 必须可替换

本项目已经反复证明，底层 agent harness 是关键不确定性来源。

因此 research-plan-execute 不得绑定单一 runtime。

必须通过 `worker_runtime_binding` 指定：

- runtime kind: `codex_cli`、`pi_coding_agent`、`mock_fixture` 或未来扩展。
- provider/model binding。
- tool permission profile。
- session reuse policy。
- timeout and retry policy。
- raw transcript path。

任何 worker 输出都必须记录实际 runtime、provider、model、prompt/context ref、raw output ref。

### 5.8 Artifact Immutability 与 Resume

科研执行协议必须支持可恢复运行。

规则：

- 已完成并通过 verifier 的 artifact 默认 immutable。
- rerun 不得静默覆盖旧 artifact，只能生成新 iteration 或新 repair attempt。
- 每个 batch 必须有 `execution_ledger`，记录 started/completed/failed/repaired/approved。
- executor 重启后必须能从 ledger 恢复，而不是重新猜测状态。

### 5.9 因果 Claim 必须经过 Ablation Gate

任何关于“认知提升导致技能提升”的 claim 都必须经过 ablation gate。

若只有性能改善，但没有 ablation，则只能声明：

- `skill performance improved under current evaluator`

不能声明：

- `cognition caused skill improvement`
- `research taste improved the method`
- `agent autonomously discovered a superior principle`

最低 ablation 要求：

1. 同一 evaluator 下比较 old skill、new skill。
2. 比较 cognition-guided request 与 metric-only/request baseline。
3. 固定 search budget。
4. 明确哪些变化来自 search space 扩展，哪些来自 cognition constraints。

### 5.10 Rule Baseline 必须保留

每个 agentic 判断至少应保留一个 deterministic baseline 对照。

用途：

- 判断 LLM agent 是否真的超过规则模板。
- 暴露 agent hallucination 或 overclaim。
- 避免把结构化规则输出误称为自主认知。

若没有 baseline，只能标注为：

- `agentic_trial_without_baseline`

不得标注为：

- `agentic_improvement_verified`

## 6. 标准对象链

一次 research-plan-execute batch 至少应产生以下对象。

### 6.1 输入侧对象

1. `research_plan`
2. `research_batch`
3. `agent_context_pack`
4. `worker_assignment`
5. `worker_runtime_binding`
6. `execution_ledger`

### 6.2 技能侧对象

1. `skill_change_request`
2. `skill_change_result`
3. `skill_asset`
4. `skill_self_report`

### 6.3 成效侧对象

1. `evaluation_run`
2. `effectiveness_assessment`
3. `baseline_comparison`
4. `metric_boundary_note`

### 6.4 认知侧对象

1. `cognition_diagnosis`
2. `cognition_to_skill_update`
3. `uncertainty_note`
4. `claim_boundary`

### 6.5 审查侧对象

1. `research_review`
2. `review_verdict`
3. `repair_request`
4. `repair_result`
5. `approval_record`

### 6.6 成果侧对象

1. `delivery_assessment`
2. `claim_routing`
3. `deliverable_package`
4. `taste_assessment`

### 6.7 对照与因果对象

1. `deterministic_baseline_assessment`
2. `ablation_plan`
3. `ablation_result`
4. `causal_claim_review`

## 7. Verdict 体系

标准 verdict 应至少包括：

1. `approved`
   - 可进入下一阶段或下一轮。
2. `real_progress`
   - 有真实进展，但仍需边界约束；只能进入 bounded next iteration。
3. `needs_fix`
   - 存在明确缺陷，必须修复后再继续。
4. `stagnation`
   - 产物存在，但没有实质推进。
5. `cheating_suspected`
   - 存在 controller overreach、伪多轮、伪认知或伪技能提升。
6. `insufficient_evidence`
   - 证据不足，不能支持当前结论。
7. `pause_for_human_review`
   - 高风险或高歧义，需要人工判断。
8. `approved_with_ablation_required`
   - 可以继续，但所有因果 claim 必须冻结，直到 ablation 完成。

## 8. Repair Routing 规则

### 8.1 skill 问题

触发条件：

- candidate 没有实质代码变化。
- 技能退回被禁止路径。
- 技能语义不符合 task。
- 技能性能失败但 evaluator/adapter 可信。

路由：

- `repair_skill`

### 8.2 evaluator 问题

触发条件：

- 指标与任务价值不一致。
- baseline/candidate 比较不公平。
- evaluator 无法区分重要失败模式。
- metric win 与 task semantic win 严重冲突且没有解释机制。

路由：

- `repair_evaluator`
- 必要时 `human_review`

### 8.3 adapter 问题

触发条件：

- task binding 不完整。
- baseline/evaluator/candidate 绑定不一致。
- search envelope 失真。
- task-specific blind spot 没有传给 cognition worker。

路由：

- `repair_adapter`

### 8.4 cognition prompt 问题

触发条件：

- cognition 输出泛泛而谈。
- 没有形成下一轮 skill constraints。
- 没有区分事实、解释和建议。
- confidence、claim、boundary 不符合 schema。

路由：

- `repair_cognition_prompt`
- `repair_context_pack`

### 8.5 schema/context 问题

触发条件：

- LLM 输出字段不合法。
- 输出对象缺少 required refs。
- confidence、status、problem_class 等枚举漂移。

路由：

- `repair_schema`
- `repair_context_pack`

### 8.6 runtime/harness 问题

触发条件：

- Agent runtime 无响应、超时或没有 raw transcript。
- provider/model 与 context pack 声明不一致。
- worker 产物无法证明来自指定 runtime。
- session reuse 导致上下文污染或跨任务泄漏。

路由：

- `repair_runtime_binding`
- `repair_context_pack`
- 必要时 `human_review`

### 8.7 causality/ablation 问题

触发条件：

- 性能改善被解释为认知导致，但没有 ablation。
- search space、evaluator、baseline 同时变化，无法归因。
- metric improvement 与 task-semantic claim 被混同。

路由：

- `repair_evaluator`
- `repair_cognition_prompt`
- `human_review`

## 9. 对 task003 iter02 的复盘吸收

task003 iter02 是当前最重要的真实案例。

它证明了：

1. skill agent 能生成新的 candidate skill。
2. candidate skill 能在真实 evaluator 下运行。
3. run_0021 的关键指标显著优于 baseline：
   - `loss`: 139.67 -> 88.53
   - `voltage_deviation`: 0.01857 -> 0.01485
   - `constraint_violation`: 8 -> 5
4. cognition workflow 能生成下一轮约束。
5. verifier 能发现 schema 枚举漂移。

它也暴露了：

1. `confidence: medium_high` 说明 LLM 输出需要 schema-aware prompt 和 normalization。
2. 当前 review gate 不是主流程硬门。
3. `compress_for_skill_agent` 仍是 controller 对 cognition 输出的加工。
4. skill improvement 的因果仍不清楚，可能来自扩大搜索空间，而不一定来自认知提升。
5. 还缺少 ablation 来证明“认知 -> 技能 -> 成效”的因果链。
6. 当前执行脚本会直接生成下一轮 request，review gate 尚未真正控制流程。
7. 当前 agent runtime/transcript 记录还没有统一进入 worker_runtime_binding。

因此，task003 iter02 不应被包装成“系统已经成熟”，而应作为 research-plan-execute 第一阶段的基准案例。

## 10. 分阶段实施计划

---

## Phase 1: 协议与对象契约固化

### 目标

将 research-plan-execute 的最小协议写清楚，避免继续在脚本中隐式推进。

### 工作内容

- [x] 编写 `docs/research-plan-execute-protocol.md`
- [x] 定义 `research_batch`
- [x] 定义 `agent_context_pack`
- [x] 定义 `research_review`
- [x] 定义 `repair_request`
- [x] 定义 `approval_record`
- [x] 定义 `worker_runtime_binding`
- [x] 定义 `execution_ledger`
- [x] 定义 `ablation_plan` / `ablation_result`
- [x] 明确 verdict enum
- [x] 明确 repair routing enum

### 验收标准

- [x] 文档能直接指导实现。
- [x] 所有 worker 的输入输出边界清楚。
- [x] review gate 与 repair loop 不再含糊。
- [x] 与 generic loop engine / diagnosis layer 的分工不重复。

---

## Phase 2: Context Pack Builder

### 目标

把散落在 prompt 构造脚本里的上下文组织逻辑收敛为通用 context pack。

### 工作内容

- [x] 实现 `scripts/build_agent_context_pack.py`
- [x] 支持 skill worker context pack
- [x] 支持 cognition worker context pack
- [x] 支持 effectiveness worker context pack
- [x] 支持 delivery/review worker context pack
- [x] 将 task003 iter02 的 prompt 输入重构为 context pack 生成

### 验收标准

- [x] 每次 agent 调用前都有可落盘 context pack。
- [x] context pack 中明确 allowed/blocked scope。
- [x] context pack 中包含上轮 review verdict。
- [x] context pack 可被 verifier 检查。
- [x] context pack 能渲染为 prompt，脚本中不再散落手写 prompt 拼接。
- [x] context pack 记录 runtime/model/provider/tool 权限要求。

---

## Phase 3: Review Gate Engine

### 目标

让 review artifact 成为控制下一轮是否继续的硬门。

### 工作内容

- [x] 实现 `scripts/run_research_review_gate.py`
- [x] 读取 skill result、effectiveness assessment、cognition update、schema validation result
- [x] 输出 `research_review`
- [x] 输出 verdict
- [x] 若 verdict 非通过，生成 `repair_request`
- [x] 禁止 loop 在未通过 review gate 时进入下一轮

### 验收标准

- [x] `approved` 才能无条件进入下一轮。
- [x] `real_progress` 只能进入 bounded next iteration，不能无条件放行。
- [x] `approved_with_ablation_required` 可以继续执行，但因果 claim 必须冻结。
- [x] `needs_fix/stagnation/cheating_suspected/insufficient_evidence` 必须进入 repair。
- [x] verifier 能发现绕过 review gate 的 loop。
- [x] review gate 能阻断未完成 ablation 的因果 claim。

---

## Phase 4: Repair Worker Protocol

### 目标

将失败回流制度化，不再由 controller 人工修补。

### 工作内容

- [ ] 定义 `repair_request` schema
- [ ] 定义 `repair_result` schema
- [ ] 实现 repair routing：
  - `repair_skill`
  - `repair_evaluator`
  - `repair_adapter`
  - `repair_cognition_prompt`
  - `repair_context_pack`
  - `repair_schema`
  - `repair_runtime_binding`
- [ ] 以 `confidence: medium_high` 问题作为 `repair_schema` 案例重放
- [ ] 以 task003 iter02 因果不清问题作为 `repair_evaluator/repair_cognition_prompt` 案例重放

### 验收标准

- [ ] 至少一个 schema failure 能自动生成 repair request。
- [ ] 至少一个 cognition-output defect 能自动生成 repair request。
- [ ] repair result 能回链到原 failure。
- [ ] 同一 repair request 超过自动重试上限后会进入 human_review。

---

## Phase 5: Research Plan Executor MVP

### 目标

形成最小可运行的科研版 plan-execute。

### 工作内容

- [ ] 实现 `scripts/run_research_plan_execute.py`
- [ ] 输入 plan file
- [ ] 拆分 checklist batches
- [ ] 为每个 batch 生成 context pack
- [ ] 调用对应 worker
- [ ] 运行 evaluator/verifier
- [ ] 运行 review gate
- [ ] 根据 verdict approve/repair/stop
- [ ] 更新 plan checklist
- [ ] 写 review log
- [ ] 写 execution ledger
- [ ] 不复制 generic loop engine 已有阶段调度逻辑

### 验收标准

- [ ] 能以 task003 multi-iteration plan 为输入跑一轮。
- [ ] 能生成 review log。
- [ ] 能在失败时进入 repair path。
- [ ] 能在通过时更新 plan checklist。
- [ ] 中断后可从 execution ledger 恢复。

---

## Phase 6: task003 基准重放

### 目标

用 research-plan-execute 重新组织 task003 iter01/iter02，验证新协议是否比当前脚本更成熟。

### 工作内容

- [ ] 将 task003 iter01/iter02 当前 artifacts 映射到新对象链
- [ ] 生成 context pack
- [ ] 生成 research review
- [ ] 生成 repair request 或 approval record
- [ ] 明确 task003 iter02 的因果边界
- [ ] 生成 task003 iter02 的 ablation plan
- [ ] 比较 cognition-guided request 与 deterministic baseline request
- [ ] 形成 protocol comparison report

### 验收标准

- [ ] 能证明新协议复现当前结果。
- [ ] 能更清楚地区分 skill improvement 与 cognition improvement。
- [ ] 能指出哪些判断需要 ablation。
- [ ] 没有 ablation 时不得声称 cognition caused improvement。
- [ ] 能比当前 `run_real_agentic_loop.py` 更少依赖 controller 临场加工。

---

## Phase 7: 迁移到 task004/task005

### 目标

验证 research-plan-execute 不只是 task003 专用脚本。

### 工作内容

- [ ] 为 task004 生成 research plan execute adapter
- [ ] 为 task005 生成 research plan execute adapter
- [ ] 对 task004 测试 boundary/overclaim review gate
- [ ] 对 task005 测试 restoration semantic/performance review gate

### 验收标准

- [ ] task004/task005 不需要重写 executor 主流程。
- [ ] 只需调整 task adapter 和 context pack。
- [ ] review gate 能识别不同 task 的核心风险。

## 11. 当前不做的事情

下一阶段暂不优先做：

1. task006。
2. 大规模多 agent 并行。
3. 自动论文生成。
4. 重型知识图谱。
5. 开放式自主选题。

原因：

- 当前真正短板是执行纪律，不是任务数量。
- 没有 review/repair 硬门，扩展任务只会放大混乱。
- 先把 task003 的真实闭环升级为成熟协议，再扩展更稳。

## 12. 成功标准

本计划完成后，应能达到以下状态：

1. 系统不只是“能跑”，而是能被审查和返工。
2. 每个 agent 调用都有 context pack。
3. 每个 batch 都有 review gate。
4. 每个 failure 都能路由到 repair worker。
5. 每个 approve 都有 evidence-backed approval record。
6. task003 的真实多轮闭环可以用新协议重放。
7. task004/task005 可以通过同一协议接入。

更重要的是：

> 项目应从“脚本驱动的 agentic experiment”升级为“协议驱动的自主科研 workflow”。

这才是向最初“模拟优秀研究生科研行为”的目标继续靠近。
