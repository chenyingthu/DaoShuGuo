# 认知 Agent 重设计计划：从通用 reviewer 到研究认知工作者

## 1. 计划目标

当前项目已经完成了 LLM cognition layer 的第一步：

- 有 prompt
- 有 job spec
- 有 dry-run
- 有至少一轮真实 Codex cognition jobs
- 有 guardrail verifier

但当前这些 cognition agents 仍然存在明显局限：

- 更像“结构化 reviewer”
- 不是强约束的研究认知工作者
- 角色区分不够锋利
- workflow 仍偏单轮、单 agent
- 尚未明确在何处真正优于规则基线

因此，本计划的目标是：

> 重新设计 cognition agents，使它们从“通用审稿式评述”升级为“分工明确、带有反驳和裁决机制的研究认知 agent”。

## 2. 为什么必须重设计

前一轮真实 LLM job 已经证明：

- LLM 能发现规则层盲点
- LLM 能更敏感地发现 overclaim
- LLM 能更好地区分局部改善与广义 claim

但也暴露出问题：

### 2.1 角色仍太泛

`result_interpreter`、`semantic_critic`、`literature_reviewer`、`effectiveness_reviewer`
虽然名字不同，但行为仍有较大重叠。

### 2.2 workflow 太单轮

当前更像：

- 读取 artifacts
- 一次性输出评价

而真正高质量认知通常需要：

1. 初步解释
2. 反解释 / 反例
3. 批判
4. 裁决
5. 压缩为最终认知

### 2.3 没有显式要求“比规则更强”

如果不把“相对规则基线的增益”写进 agent 设计，它们很容易变成：

- 更漂亮的规则总结器

而不是：

- 真正能指出规则漏掉之处的认知工作者

## 3. 新设计的核心原则

### 3.1 从“一次性评论”改为“多步认知流程”

认知输出不应由单一 agent 一步完成。

第一版建议最少拆成三步：

1. `interpretation_proposer`
2. `counter_interpreter`
3. `adjudicator`

### 3.2 明确角色之间的职责差异

#### interpretation_proposer

职责：

- 给出“当前证据支持的最强可成立解释”

#### counter_interpreter

职责：

- 给出“当前解释的最强替代解释或最强反驳”

#### adjudicator

职责：

- 在 proposal 与 counter-proposal 之间做裁决
- 形成 bounded cognition

### 3.3 认知必须包含可反驳性

每个 cognition agent 输出都必须包含：

- strongest_supported_claim
- strongest_unsupported_claim
- alternative_interpretation
- discriminating_missing_evidence

### 3.4 仍由确定性系统把关

无论 agent 多强，都不能跳过：

- evidence grounding
- schema validation
- reference checking
- taste / claim guard

## 4. 推荐新角色体系

### 4.1 Result Interpretation Lane

#### A. interpretation_proposer

输入：

- run
- metrics
- evidence
- report

输出：

- strongest supported interpretation

#### B. counter_interpreter

输入：

- 同上
- proposer output

输出：

- strongest alternative interpretation
- strongest overclaim risk

#### C. adjudicator

输入：

- proposer output
- counter output
- rule baseline

输出：

- final bounded interpretation

### 4.2 Semantic Critique Lane

#### A. semantic_proposer

职责：

- 给出当前 task 本体的最佳语义解释

#### B. semantic_counter

职责：

- 给出指标上可能更好但问题本体上更差的替代解释

#### C. semantic_adjudicator

职责：

- 输出最终 failure taxonomy 或 success semantics

### 4.3 Literature Critique Lane

#### A. literature_proposer

职责：

- 给出最合理的方法家族映射

#### B. literature_counter

职责：

- 专门寻找 superficial similarity / false novelty / false equivalence

#### C. literature_adjudicator

职责：

- 给出最终 novelty positioning

### 4.4 Effectiveness Critique Lane

#### A. delivery_proposer

职责：

- 给出最乐观但仍有证据支持的 deliverable readiness 判断

#### B. delivery_counter

职责：

- 找出最强阻断项、最强缺失验证、最强 overclaim 风险

#### C. delivery_adjudicator

职责：

- 输出最终 claim routing / deliverable readiness

## 5. 推荐输出字段

建议统一增强为：

- `job_id`
- `agent_role`
- `input_refs`
- `strongest_supported_claim`
- `strongest_unsupported_claim`
- `alternative_interpretation`
- `discriminating_missing_evidence`
- `agreement_with_rule_baseline`
- `new_insights`
- `overclaim_warnings`
- `recommended_action`
- `confidence`

## 6. 与当前系统的关系

本计划不是推翻已有第一版 cognition layer，而是：

- 保留现有四类角色作为第一版 baseline
- 新增多角色 workflow 作为第二版
- 用同一批 artifacts 对照比较两版表现

也就是说：

- 旧层 = `single-pass baseline`
- 新层 = `multi-role cognition workflow`

## 7. 第一轮测试对象

建议继续用已有最成熟切片：

### task003

用于测试：

- 指标成功但任务语义失配

### task004

用于测试：

- 边界判断 vs 单点结果
- overclaim 风险

### task005

用于测试：

- 恢复问题本体
- 局部恢复 vs 系统韧性

## 8. 测试方式

### 8.1 single-pass vs multi-role

比较：

- 旧 single-pass cognition job
- 新 multi-role cognition workflow

### 8.2 rule vs agent

比较：

- deterministic baseline
- redesigned cognition agents

### 8.3 gain criteria

只有满足以下至少一项，才算真正增益：

1. 发现规则漏掉的合理语义维度
2. 找到规则未识别的 overclaim
3. 更准确地区分 failure 类型
4. 更清楚指出真正缺的证据

## 9. 实施步骤

## Phase 1: Prompt Redesign

目标：

重写 cognition prompts，使其从 generic review 变成 domain-shaped cognition workflow。

执行内容：

- [x] 重写 result interpretation prompts
- [x] 重写 semantic critique prompts
- [x] 重写 literature critique prompts
- [x] 重写 effectiveness critique prompts

完成判据：

- [x] 每个角色有清晰、互补而非重叠的职责

## Phase 2: Multi-role Job Spec

目标：

让一个 cognition task 不再是单一 job，而是一个小型 workflow。

执行内容：

- [x] 定义 proposer / counter / adjudicator job spec
- [x] 定义中间产物格式
- [x] 定义 final adjudicated output 格式

完成判据：

- [x] 至少一条 workflow 可被离线构造

## Phase 3: Offline Workflow Bundles

目标：

先离线生成可审查的多角色 cognition bundles。

执行内容：

- [x] 为 task003 构造一条 semantic workflow
- [x] 为 task004 构造一条 literature workflow
- [x] 为 task005 构造一条 result/effectiveness workflow

完成判据：

- [x] 多角色 cognition bundle 可人工审阅

## Phase 4: Real LLM Workflow Tests

目标：

使用真实 Codex 执行至少一条多角色 workflow。

执行内容：

- [x] 至少运行一个 proposer
- [x] 至少运行一个 counter
- [x] 至少运行一个 adjudicator
- [x] 保存 raw / parsed / reviewed artifacts

完成判据：

- [x] 至少一条真实多角色 cognition workflow 完整跑通

## Phase 5: Comparative Evaluation

目标：

系统比较：

- 规则基线
- 旧 single-pass LLM cognition
- 新 multi-role cognition workflow

执行内容：

- [ ] 设计 comparison rubric
- [x] 记录 gain / regression / hallucination risk
- [x] 判断新设计是否真正优于旧设计

完成判据：

- [x] 至少在一个 slice 上证明 redesigned workflow 明显优于旧 baseline

## Phase 6: Guardrail & Integration

目标：

让新 cognition workflow 进入正式验证体系。

执行内容：

- [x] 扩展 verifier
- [x] 增加 multi-role output checks
- [x] 接入 integration checks
- [x] 更新实验记录和设计文档

完成判据：

- [x] redesigned cognition agents 不绕过证据和 claim guard

## 10. 成功标准

本计划成功的标准不是“提示词更长”，而是：

1. cognition roles 真正分工清晰
2. 至少一条真实多角色 workflow 跑通
3. 新 workflow 能识别旧设计或规则基线未识别的问题
4. verifier 能继续限制 hallucination 和 overclaim
5. 有证据表明新设计优于旧单轮 reviewer 设计

## 11. 风险

### 风险 1：角色太多但信息增益很少

缓解：

- 强制做 old vs new 对照评估

### 风险 2：多角色只是在重复同一种观点

缓解：

- counter role 必须强制提出 alternative interpretation

### 风险 3：adjudicator 只是总结而不裁决

缓解：

- 输出必须包含 accepted / rejected interpretations

## 12. 当前结论

本计划是对当前 cognition layer 的真正升级。

它的目标不是让 agent“更会写”，而是让 agent：

- 更会反驳
- 更会裁决
- 更会在证据约束下形成研究认知

如果这一步成立，当前框架才会真正开始接近：

> 由 LLM agents 参与认知工作、而不是只由规则和模板维持表面结构的自主科研系统。 
