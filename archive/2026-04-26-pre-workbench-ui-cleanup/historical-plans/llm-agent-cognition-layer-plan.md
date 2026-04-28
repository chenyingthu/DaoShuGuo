# LLM Agent 认知层实施与测试计划

## 1. 背景与问题

当前框架已经形成了较完整的确定性底座：

- task / run / evidence / taste / report
- evaluator
- schema validation
- failure taxonomy
- literature alignment
- cognition upgrade
- effectiveness / delivery readiness

但必须承认：

> 当前大多数 cognition / semantic / literature / effectiveness 判断仍然主要由规则、模板和人工设计逻辑生成。

这说明当前系统更准确地说是：

- 研究对象管理系统
- 证据与验证底座
- 规则化认知基线

而还不是完整的：

- LLM-based autonomous research agent

因此，本计划的目标是：

> 将 LLM-based agents 正式作为认知工作者接入当前框架，并通过对照测试证明它们是否真正提升认知质量，而不是制造更漂亮的幻觉。

## 2. 核心原则

### 2.1 规则不是认知

规则能做：

- 格式检查
- 引用检查
- 关键词分类
- 证据强度粗分
- claim 上限约束

规则不能真正完成：

- 方法语义理解
- 文献解释
- 失败机理判断
- 成果交付判断
- 研究价值判断

### 2.2 LLM Agent 是认知工作者

真正需要 LLM agent 参与的环节包括：

- task framing
- result interpretation
- semantic comparison
- literature interpretation
- cognition critique
- effectiveness / delivery review

### 2.3 确定性系统是护栏

LLM agent 的输出不能直接进入稳定认知层。

必须经过：

- schema validation
- evidence grounding
- reference checking
- overclaim gate
- deterministic baseline comparison

## 3. 本计划目标

建立一个最小 LLM Agent 认知层，使系统能完成：

1. 对 task003/task004/task005 结果进行 LLM-based result interpretation
2. 对 rule-based semantic comparison 进行 LLM critique
3. 对 literature alignment 进行 LLM explanation review
4. 对 effectiveness / delivery routing 进行 LLM review
5. 与当前 deterministic baseline 对照，评估 LLM 是否带来真实增益

## 4. 不做的事情

本阶段不做：

- 完全自治科研循环
- 多智能体大规模协作
- 自动论文/专利全文生成
- 任意开放式联网检索
- 替代当前 evaluator

LLM agent 只进入认知判断层，不进入硬成效计算层。

## 5. 推荐新增目录与对象

建议新增：

```text
agents/
  cognition/
    prompts/
      result_interpreter.md
      semantic_critic.md
      literature_reviewer.md
      effectiveness_reviewer.md
    jobs/
    outputs/
```

建议新增对象：

- `llm_cognition_job`
- `llm_cognition_output`
- `llm_cognition_review`

第一版可以先不写正式 schema，而用 YAML/JSON 对象约定。

## 6. Agent 角色设计

### 6.1 Result Interpretation Agent

输入：

- run
- metrics
- evidence bundle
- report
- taste assessment

输出：

- result interpretation
- mechanism hypothesis
- failure mode interpretation
- claim boundary

核心问题：

- 这个结果到底说明了什么？
- 它没有说明什么？
- 当前 failure 是方法问题、任务问题、参数问题，还是证据不足？

### 6.2 Semantic Critic Agent

输入：

- strategy comparison
- rule-based semantic comparison
- run artifacts

输出：

- agreement / disagreement with rule baseline
- missed semantic dimensions
- overclaim warnings

核心问题：

- rule-based semantic comparison 是否漏掉关键语义？
- rule 判断是否把指标成功误认为研究成功？

### 6.3 Literature Reviewer Agent

输入：

- literature alignment
- explanation alignment
- method cards
- target cognition

输出：

- literature fit assessment
- superficial similarity warning
- novelty calibration
- missing literature signals

核心问题：

- 当前文献对齐是真相关，还是只是关键词相似？
- 当前认知在文献空间中应该被升级、保留还是降级？

### 6.4 Effectiveness Reviewer Agent

输入：

- validation plan
- experiment matrix
- application assessment
- deliverable package
- claim routing

输出：

- readiness critique
- missing validation
- delivery route critique
- paper/patent/report suitability judgment

核心问题：

- 当前 deliverable routing 是否过于乐观？
- 是否缺少关键验证？
- 哪些 claim 仍然不能对外说？

## 7. 第一阶段测试对象

建议第一版只选三个固定测试切片：

### Slice A: task003

目标：

- 测试 LLM 是否能区分：
  - inverter-aware candidate
  - weak-shunt mismatch
  - performance failure

### Slice B: task004

目标：

- 测试 LLM 是否能理解：
  - hosting capacity 是条件化边界
  - single-point result 不是 boundary assessment
  - boundary overclaim 风险

### Slice C: task005

目标：

- 测试 LLM 是否能理解：
  - event-driven restoration
  - critical load recovery
  - resilience overclaim

## 8. 测试方式

### 8.1 与 deterministic baseline 对照

每个 LLM 输出必须与当前 rule-based 输出对照。

比较项：

- 是否识别同一 failure type
- 是否指出新维度
- 是否发生过度 claim
- 是否引用了正确 evidence
- 是否更适合 human researcher 阅读

### 8.2 幻觉与越界测试

必须测试：

- LLM 是否引用不存在的 artifact
- LLM 是否夸大单工况结论
- LLM 是否把 failure 包装成 success
- LLM 是否把文献关键词相似误认为方法一致

### 8.3 增益测试

LLM 输出只有在以下情况下才算有增益：

- 发现规则漏掉的合理认知维度
- 更准确解释 failure 机理
- 更清楚指出缺失验证
- 更好地约束成果 claim

## 9. 输出要求

LLM agent 输出必须结构化。

建议字段：

- `job_id`
- `agent_role`
- `input_refs`
- `interpretation_summary`
- `evidence_used`
- `agreement_with_rule_baseline`
- `new_insights`
- `overclaim_warnings`
- `missing_evidence`
- `recommended_action`
- `confidence`

## 10. 最小实现路线

## Phase 1: Agent Prompt 与 Job Spec

目标：

建立 LLM cognition worker 的输入输出契约。

执行内容：

- [x] 编写 result interpreter prompt
- [x] 编写 semantic critic prompt
- [x] 编写 literature reviewer prompt
- [x] 编写 effectiveness reviewer prompt
- [x] 定义 job spec 与 output spec

完成判据：

- [x] 每个 agent 角色都有明确输入、输出和禁止事项

## Phase 2: 离线样本驱动测试

目标：

先不接 API，使用当前 artifacts 构造 prompt/job 样本。

执行内容：

- [x] 为 task003 构造 cognition job
- [x] 为 task004 构造 cognition job
- [x] 为 task005 构造 cognition job
- [x] 生成可人工审阅的 prompt bundles

完成判据：

- [x] LLM agent cognition stage 可以被离线审查

## Phase 3: 最小 LLM 调用层

目标：

接入实际 LLM 调用，但保持可控。

执行内容：

- [x] 实现 `run_llm_cognition_job.py`
- [x] 支持手动指定模型/命令
- [x] 支持 dry-run 输出 prompt
- [x] 支持保存 raw response 与 parsed output

完成判据：

- [x] 至少一个 LLM cognition job 可真实执行

## Phase 4: LLM vs Rule 对照评估

目标：

验证 LLM 是否真的比规则基线更有认知价值。

执行内容：

- [x] 设计 comparison rubric
- [x] 对 task003/004/005 各跑至少一个 LLM job
- [x] 对照 rule-based cognition output
- [x] 记录增益与风险

完成判据：

- [x] 能明确判断 LLM agent 在哪些认知任务上有增益，哪些没有

## Phase 5: Guardrail 与 Integration

目标：

把 LLM cognition 层纳入现有验证体系。

执行内容：

- [x] 增加 artifact validation
- [x] 增加 overclaim / hallucination checks
- [x] 接入 integration checks
- [x] 更新实验记录

完成判据：

- [x] LLM cognition 层不会绕过证据系统和 taste gate

## 11. 成功标准

本计划成功的标准不是“LLM 输出看起来聪明”，而是：

1. LLM cognition job 有明确输入输出契约
2. LLM 输出可回链 evidence
3. LLM 输出能与 deterministic baseline 对照
4. LLM 能至少在一个任务中发现规则漏掉的合理认知维度
5. LLM 输出没有绕过 claim guard
6. verifier 能捕获至少一种 LLM 过度 claim 或引用错误

## 12. 风险

### 风险 1：LLM 只是写得更漂亮

缓解：

- 必须与 rule baseline 对照
- 必须记录 new_insights 与 missing_evidence

### 风险 2：LLM 引入幻觉

缓解：

- 禁止引用不存在 artifact
- 输出必须列出 evidence_used
- verifier 检查 evidence_refs

### 风险 3：LLM 过度拔高结论

缓解：

- 专门测试 overclaim warnings
- 必须经过 taste / claim gate

### 风险 4：LLM 调用导致系统不可复现

缓解：

- 保存 prompt bundle
- 保存 raw response
- 保存 parsed output
- 保留 deterministic baseline

## 13. 当前结论

这是一个纠偏计划。

当前框架已经有强大的确定性底座，但还没有真正把 LLM agent 作为认知工作者接入。

本计划完成后，系统才真正开始接近最初目标：

> 用 Agent 模拟受过训练的研究生，在证据约束下进行问题理解、结果解释、文献比较、认知升级和成果判断。
