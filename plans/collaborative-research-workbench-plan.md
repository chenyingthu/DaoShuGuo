# Collaborative Research Workbench Plan

## 1. 方向调整

DaoShuGuo 下一阶段不应继续以“开发一组 Python 脚本跑通自主科研闭环”为主目标。

已有工作已经证明：

1. Agent 可以执行技能、运行 evaluator、写入证据、生成候选认知。
2. 通用 task onboarding、generic loop、Pi runtime harness、learning/reframing chain 已经具备可用基础。
3. 但在真实科研中，方向选择、问题重构、价值判断、claim 上限和成果品味仍高度依赖专家介入。

因此，下一阶段目标应调整为：

> 建设一个面向科研人员的人-Agent 协同科研工作台，使专家能够围绕给定研究主题，清楚看到中间信息、理解 Agent 工作逻辑、在关键节点介入，并把人的判断沉淀为可审计的研究对象。

这不是放弃 Agent 自主性，而是把“人的高阶认知与品味”纳入系统架构。

## 2. 新系统定位

建议将下一阶段系统定位为：

> DaoShuGuo Collaborative Research Workbench

中文可称为：

> 道术果协同科研工作台

系统目标：

围绕一个研究主题，把以下链路可视化、交互化、可回溯地组织起来：

`文献调研 -> 方案设计 -> 技能开发 -> 系统验证 -> 认知提升 -> 迭代交互 -> 成果总结`

其中：

1. Agent 负责高吞吐执行、结构化整理、候选判断和工具调用。
2. 确定性系统负责 schema、evaluator、证据链、状态机和版本管理。
3. 科研人员负责方向判断、价值判断、品味控制、关键分叉和最终 claim 授权。

## 3. 核心认识

### 3.1 人不是补丁，而是系统节点

此前开发过程说明：

Agent 如果完全隔离人的参与，容易出现：

1. 局部优化。
2. 过度执行。
3. 对研究价值判断不足。
4. 将流程完成误判为科研进展。
5. 无法及时发现问题定义不对或场景不支撑。

因此，人不应被视为“Agent 失败后的人工补救”。

人的角色应被建模为：

1. 高阶认知节点。
2. 品味审查节点。
3. 方向裁决节点。
4. claim 授权节点。
5. 研究策略调整节点。

### 3.2 工作台的价值不在 UI，而在交互组织

工作台不是简单把 YAML 文件显示成网页。

它必须回答科研人员最关心的问题：

1. 现在研究进行到哪一步？
2. Agent 正在做什么？
3. 它为什么这么做？
4. 它依据了哪些证据？
5. 哪些结论可靠，哪些只是候选？
6. 哪些地方需要我判断？
7. 我的一次判断会如何改变后续路径？
8. 最终成果为什么只能写到这个程度？

更重要的是，工作台必须解决“中间过程不可读”的问题。

科研人员不应该被迫打开代码、YAML、JSON、日志逐行理解 Agent 做了什么。
这就像导师不应被迫直接阅读研究生的全部代码才能判断研究进展。

Agent 必须具备稳定的科研汇报能力：

1. 把复杂执行过程压缩成可读的研究叙述。
2. 把关键中间结果解释成“这说明了什么”。
3. 把失败、异常、负结果解释成“这暴露了什么问题”。
4. 把下一步建议讲清楚“为什么值得做”。
5. 把不确定性和证据缺口明确说出来。

因此，工作台的第一性目标不是展示更多信息，而是让专家更容易理解、追问、纠偏和决策。

### 3.3 交互必须成为证据资产

人的判断不能只停留在聊天记录里。

每次关键交互都应写成对象：

1. `human_review`
2. `research_decision`
3. `direction_override`
4. `claim_approval`
5. `expert_annotation`
6. `iteration_steering`

这些对象应进入 evidence chain，成为后续 Agent 可读取、可遵守、可复盘的约束。

## 4. 现有资产复用

下一阶段不推倒重来。

继续复用：

1. `tasks/`
2. `adapters/`
3. `evaluators/`
4. `skills/`
5. `cognition/`
6. `literature/`
7. `analysis/`
8. `runs/`
9. `schemas/`
10. `configs/agent_runtimes/registry.yaml`
11. `scripts/run_generic_loop_engine.py`
12. `scripts/build_real_task001_reframing.py`
13. `scripts/verify_real_task001_reframing.py`
14. `scripts/build_real_task001_upgrade_report.py`
15. `scripts/verify_real_task001_upgrade.py`

这些是工作台的 backend substrate。

新增的是：

1. 可视化工作台。
2. human-in-the-loop 对象契约。
3. UI-facing aggregation API。
4. Agent progress/event stream。
5. 专家交互写回机制。

### 4.1 不重造已有能力

工作台不得重复实现已有科研 backend 能力。

边界如下：

1. 不重写 task onboarding。
2. 不重写 generic loop engine。
3. 不重写 evaluator。
4. 不重写 Pi runtime harness。
5. 不重写 skill/cognition registry。
6. 不把 UI action 写成新的 task-specific pipeline。

工作台只新增三类能力：

1. 面向科研人员的 topic aggregation。
2. 人类交互对象写回。
3. 人类决策到后续 Agent 路由的约束编译。

如果某个功能需要修改已有科研 backend，应优先通过已有对象契约扩展，而不是在 workbench 内部创建平行逻辑。

## 5. 科研人员需要看到的信息

工作台首先是给科研人员使用的，不是给脚本运行日志归档的。

因此，任何信息展示都必须服务于四类研究动作：

1. `overview`：快速判断研究是否在正确方向上推进。
2. `drill_down`：追溯某个结论、指标或建议的证据来源。
3. `challenge`：质疑 Agent 的判断、要求补证据或指出研究品味问题。
4. `steer`：把专家判断写回系统，并改变后续 Agent 路由。

如果一个页面或接口不能支持上述动作之一，应推迟实现。

### 5.1 全局状态

科研人员进入工作台后，第一屏必须回答：

1. 当前研究主题是什么。
2. 当前阶段是什么。
3. 当前 loop 是第几轮。
4. 当前最强可支持 claim 是什么。
5. 当前成果等级是什么。
6. 当前最大风险是什么。
7. 当前下一步推荐是什么。
8. 哪些节点正在等待人工判断。

示例字段：

```yaml
topic: "IEEE69 renewable hosting capacity"
current_stage: "cognition_reframing"
iteration: 4
claim_ceiling: "operational_quality_only"
taste_grade: "diaomu"
blocking_issue: "scenario does not trigger boundary"
recommended_action: "design boundary-triggering scenario"
human_attention_required: true
```

### 5.2 研究者信息分层

科研人员不应该被迫直接阅读所有 YAML、JSON 或 raw log。

同一份底层证据应被组织成三层：

1. `executive_layer`
   - 面向 1 分钟判断。
   - 回答：当前是否值得继续、是否有风险、是否需要我介入。
2. `research_layer`
   - 面向 10 分钟审查。
   - 回答：问题定义、方法选择、指标、文献关系和 claim 上限是否合理。
3. `audit_layer`
   - 面向深度复盘。
   - 回答：每个对象、运行、指标、Agent 输出和人类决策如何回链。

每个页面都应提供从 `executive_layer` 到 `audit_layer` 的下钻路径。

示例：

```text
claim_ceiling: operational_quality_only
  -> supporting_evaluator_runs: [runs/task004/run_0029]
  -> supporting_metrics: [hosting_capacity_level, voltage_quality, cost]
  -> cognition_diagnosis: analysis/real_task_001_upgrade/...
  -> taste_reason: no boundary-triggering scenario, no primary improvement
  -> human_action: approve ceiling | challenge evaluator | request new scenario
```

### 5.3 中间证据

科研人员需要随时看到：

1. 文献来源。
2. 文献到方法族的映射。
3. 方法族到技能请求的映射。
4. 技能实现到 run 的映射。
5. run 到 evaluator 的映射。
6. evaluator 到 cognition diagnosis 的映射。
7. cognition 到下一轮路由的映射。
8. delivery 到 claim gate 的映射。

这应以证据链图和表格同时呈现。

### 5.4 科研阶段视角

科研人员不是按文件夹理解项目，而是按科研阶段理解工作。

工作台必须按以下阶段组织信息：

| 阶段 | 研究者要看什么 | 典型问题 | 允许操作 | 写回对象 |
| --- | --- | --- | --- | --- |
| 文献调研 | 文献覆盖、方法族、已有指标、外部 SOTA 参照 | 文献是否够？方法空间是否窄？ | 要求补文献、排除弱相关文献 | `expert_annotation`, `research_decision` |
| 方案设计 | 问题边界、假设、场景、指标、基线 | 这个问题值得做吗？场景是否能触发机制？ | 修改研究边界、要求重构 task | `direction_override`, `research_decision` |
| 技能开发 | 方法/流程/标准三要素、版本差异、适用边界 | 技能真的升级，还是只调参数？ | 要求 ablation、冻结技能、要求结构性改进 | `human_review`, `expert_annotation` |
| 系统验证 | baseline/candidate 对比、鲁棒性、代价、失败样本 | 改进是否真实？是否可泛化？ | 要求补实验、标记 evaluator gap | `human_review`, `research_decision` |
| 认知提升 | 候选认知、失败认知、文献对齐、冲突 | 学到了什么？哪些不能上升为规律？ | 接受、降级、要求补文献 | `expert_annotation`, `research_decision` |
| 成果总结 | claim ceiling、taste grade、报告候选 | 能写成什么？不能写什么？ | 批准 claim、禁止 claim、锁定成果等级 | `claim_approval` |

### 5.5 Agent 工作进展

每个 Agent/worker 的执行都应显示：

1. Worker 名称。
2. 输入对象。
3. 输出对象。
4. 当前状态。
5. 开始时间。
6. 耗时。
7. 使用 backend/model。
8. raw output 摘要。
9. 校验结果。
10. 失败原因。
11. 本次工作属于技能、认知、成效还是交付。
12. 是否需要人的判断才能继续。

科研人员不应只能看到“running”或“done”，而应看到 Agent 的工作逻辑。

### 5.6 关键判断点

工作台必须显式提示专家介入节点，例如：

1. 任务定义是否合理。
2. 文献 framing 是否接受。
3. 方法族选择是否合理。
4. evaluator 是否表达研究价值。
5. skill change 是结构性改进还是使用条件变化。
6. 负结果是否应继续投入。
7. claim ceiling 是否准确。
8. 是否进入成果写作。

每个判断点都应包含：

1. Agent 建议。
2. 支持证据。
3. 反对证据。
4. 风险。
5. 可选操作。
6. 人的批注输入框。
7. 写回对象。

### 5.7 研究者可问的问题

工作台必须支持科研人员围绕当前 topic 追问，而不是只能按按钮执行。

第一版不要求自由聊天完全智能化，但至少要支持基于 artifacts 的结构化问答模板：

1. `why_current_claim_ceiling`
   - 为什么当前成果只能支持这个 claim ceiling？
2. `what_blocks_upgrade`
   - 阻止成果升级的最关键证据是什么？
3. `what_changed_between_iterations`
   - 两轮迭代到底改变了技能、参数、场景还是评价标准？
4. `is_this_structural_skill_improvement`
   - 当前改进是否是结构性技能提升？
5. `what_should_human_decide`
   - 哪些问题必须由专家判断？
6. `what_next_if_continue`
   - 如果继续投入，最有价值的下一步是什么？
7. `what_not_to_claim`
   - 当前绝不能声称什么？

每个回答都必须包含：

1. 简短结论。
2. 支持证据引用。
3. 不确定性。
4. 可执行下一步。
5. 可写回的人类操作。

### 5.8 Human Attention Queue

工作台必须维护一个显式的 `human_attention_queue`。

每个 attention item 至少包含：

```yaml
attention_id: string
topic_id: string
severity: low | medium | high | blocking
stage: literature | framing | skill | evaluation | cognition | delivery
question: string
why_human_needed: string
agent_recommendation: string
evidence_refs: array[string]
allowed_actions:
  - approve
  - revise
  - reject
  - request_more_evidence
  - override_direction
  - pause
writeback_object_type: human_review | research_decision | direction_override | expert_annotation | claim_approval
status: open | resolved | superseded
```

`human_attention_queue` 是工作台区别于“运行日志看板”的关键。
它告诉科研人员：现在我应该在哪里花注意力。

### 5.9 Research Communication Layer

工作台必须增加独立的 `research_communication_layer`。

它的职责不是生成新事实，而是把已有 artifacts 转换为科研人员可读、可讨论、可决策的汇报材料。

核心输出包括：

1. `mentor_brief`
   - 面向导师/专家的短汇报。
   - 说明本轮做了什么、发现了什么、没解决什么、需要专家判断什么。
2. `iteration_digest`
   - 面向多轮 loop 的中间结果摘要。
   - 说明本轮相比上一轮发生了哪些实质变化。
3. `decision_brief`
   - 面向某个关键判断点的决策说明。
   - 给出选项、证据、风险、推荐和可写回动作。
4. `failure_brief`
   - 面向失败和负结果的解释。
   - 说明失败类型、暴露的问题、是否值得继续。
5. `claim_brief`
   - 面向成果输出的主张边界说明。
   - 说明能写什么、不能写什么、为什么。

每个 brief 必须满足：

1. 先给结论，再给证据。
2. 区分事实、解释、推断和建议。
3. 不要求用户打开原始文件才能理解。
4. 必须包含 evidence refs，支持下钻。
5. 必须包含“需要人判断吗”。
6. 必须包含“如果我是导师，我应该问什么”。

示例结构：

```yaml
object_type: mentor_brief
topic_id: string
iteration: integer
headline: string
one_minute_summary: string
what_changed:
  - change_type: skill | evaluation | cognition | scenario | claim | failure
    summary: string
    evidence_refs: array[string]
what_it_means: array[string]
what_is_not_proven: array[string]
human_questions_to_consider: array[string]
recommended_human_action: string
drilldown_refs: array[string]
```

## 6. 工作台信息架构

### 6.1 Research Topic Cockpit

用途：

给科研人员一个“研究驾驶舱”。

显示：

1. 研究主题。
2. 当前阶段。
3. 任务包 readiness。
4. 当前 claim ceiling。
5. 当前 taste grade。
6. 当前 blocking issue。
7. 最近一次 run。
8. 最近一次 human decision。
9. 下一步 action queue。

核心操作：

1. 启动 onboarding。
2. 启动下一轮 loop。
3. 暂停 loop。
4. 要求 Agent 解释当前状态。
5. 添加专家批注。

### 6.2 Literature & Framing Board

用途：

让科研人员审查“这个问题到底怎么被定义”。

显示：

1. `learning_need`
2. `learning_context_pack`
3. `research_framing_map`
4. `method_family_map`
5. `metric_taxonomy`
6. `claim_threshold_map`
7. `experiment_design_recommendation`

核心操作：

1. 接受 framing。
2. 要求补文献。
3. 删除不适用文献。
4. 修改问题边界。
5. 要求 Agent 比较两个方法族。

### 6.3 Plan & Iteration Board

用途：

展示科研 loop 的当前轨迹。

显示：

1. `skill_change_request`
2. `skill_change_result`
3. `effectiveness_assessment`
4. `cognition_diagnosis`
5. `loop_routing_decision`
6. `loop_review`

核心操作：

1. 批准下一轮。
2. 驳回 Agent 路由。
3. 指定下一步 worker。
4. 改写下一轮约束。
5. 标记“局部陷阱”。

### 6.4 Skill Lab

用途：

让科研人员审查技能是否真的变强。

显示：

1. 技能列表。
2. 方法/流程/标准三要素。
3. 技能版本。
4. 关联 run。
5. evaluator 结果。
6. 结构性评价。

核心操作：

1. 对技能打标签。
2. 要求 ablation。
3. 要求 equal-budget comparison。
4. 冻结低价值技能。
5. 将 candidate skill 提升为 validated skill。

### 6.5 Evaluation Dashboard

用途：

让科研人员快速判断“成效是否真实”。

显示：

1. baseline/candidate 对比。
2. primary metrics。
3. secondary metrics。
4. cost metrics。
5. boundary trigger。
6. robustness。
7. failure lane。
8. negative control。

核心操作：

1. 查看 run 详情。
2. 选择对比 run。
3. 要求补实验。
4. 标记 evaluator gap。
5. 禁止不合理 claim。

### 6.6 Cognition Board

用途：

让科研人员看到系统“学到了什么”和“不该学什么”。

显示：

1. 候选认知。
2. 稳定认知。
3. 失败认知。
4. 认知冲突。
5. evidence refs。
6. human annotations。

核心操作：

1. 接受候选认知。
2. 降级认知。
3. 添加边界。
4. 标记冲突。
5. 要求文献对齐。

### 6.7 Delivery Studio

用途：

让科研人员控制成果输出。

显示：

1. 当前 report。
2. taste assessment。
3. claim ceiling。
4. missing evidence。
5. paper/patent/report readiness。
6. forbidden claims。

核心操作：

1. 生成内部报告。
2. 请求论文候选路线。
3. 审核 claim。
4. 锁定成果等级。
5. 输出汇总材料。

## 7. 人机交互对象契约

### 7.0 通用对象要求

所有 human-in-the-loop 对象必须满足统一元数据要求：

```yaml
object_id: string
object_type: string
schema_version: string
topic_id: string
task_id: string
created_at: datetime
created_by: string
source: ui | cli | api | agent_suggestion
target_refs: array[string]
evidence_refs: array[string]
status: draft | active | superseded | resolved | rejected
supersedes: array[string]
tags: array[string]
```

对象 ID 必须稳定、可引用、不可复用。

推荐命名：

```text
human_review.{topic_id}.{yyyymmddhhmmss}.{short_slug}
research_decision.{topic_id}.{yyyymmddhhmmss}.{short_slug}
direction_override.{topic_id}.{yyyymmddhhmmss}.{short_slug}
expert_annotation.{topic_id}.{yyyymmddhhmmss}.{short_slug}
claim_approval.{topic_id}.{yyyymmddhhmmss}.{short_slug}
routing_constraint.{topic_id}.{yyyymmddhhmmss}.{short_slug}
```

每个对象必须同时进入：

1. 对象原始目录。
2. topic timeline。
3. evidence graph。
4. artifact index。

### 7.1 `human_review`

用途：

记录专家对某个对象的审查。

字段：

```yaml
object_type: human_review
review_target_ref: string
reviewer_role: string
decision: approve | revise | reject | pause
rationale: string
required_changes: array[string]
claim_boundary: array[string]
created_at: datetime
```

### 7.2 `research_decision`

用途：

记录研究方向或关键分叉。

字段：

```yaml
object_type: research_decision
decision_scope: task | literature | skill | evaluator | cognition | delivery
selected_option: string
rejected_options: array[object]
decision_drivers: array[string]
evidence_refs: array[string]
human_rationale: string
agent_recommendation_ref: string
```

### 7.3 `direction_override`

用途：

当专家认为 Agent 路由不合适时，显式改写方向。

字段：

```yaml
object_type: direction_override
source_routing_ref: string
override_action: string
why_agent_route_is_insufficient: string
new_constraints: array[string]
must_not_do: array[string]
```

### 7.4 `expert_annotation`

用途：

在任意 artifact 上添加专家批注。

字段：

```yaml
object_type: expert_annotation
target_ref: string
annotation_type: clarification | warning | insight | boundary | taste_note
content: string
severity: low | medium | high
action_required: boolean
```

### 7.5 `claim_approval`

用途：

成果输出前的专家授权。

字段：

```yaml
object_type: claim_approval
deliverable_ref: string
approved_claims: array[string]
rejected_claims: array[string]
required_qualifiers: array[string]
max_report_type: technical_note | paper_draft | patent_candidate
approval_status: approved | rejected | conditional
```

### 7.6 `iteration_steering`

用途：

记录专家对下一轮科研迭代的策略性引导。

字段：

```yaml
object_type: iteration_steering
source_loop_ref: string
target_next_iteration: integer
steering_goal: string
priority: low | medium | high | blocking
preferred_actions: array[string]
forbidden_actions: array[string]
required_evidence: array[string]
stop_condition: string
human_rationale: string
```

### 7.7 `routing_constraint`

用途：

把方向性人类判断编译为 loop controller 可读取的约束对象。

字段：

```yaml
object_type: routing_constraint
source_human_object_ref: string
applies_to_stage: literature | framing | skill | evaluation | cognition | delivery | loop
constraint_type: must_do | must_not_do | prefer | require_evidence | claim_limit | pause_condition
content: string
priority: low | medium | high | blocking
active: true
expires_after_iteration: integer | null
conflicts_with: array[string]
resolution_status: none | resolved | needs_human
```

### 7.8 `agent_response_to_human`

用途：

记录 Agent 对人类判断、质疑或改写方向的回应。

字段：

```yaml
object_type: agent_response_to_human
human_object_ref: string
response_type: accepted | partially_accepted | rejected | needs_more_evidence
rationale: string
changed_routing_constraints: array[string]
next_actions: array[string]
evidence_refs: array[string]
```

### 7.9 冲突处理

人类对象之间、人类对象与 Agent 路由之间可能冲突。

必须采用显式冲突处理规则：

1. `blocking` 级 human constraint 优先于 Agent recommendation。
2. 较新的 human object 不自动覆盖旧对象，除非 `supersedes` 显式声明。
3. 同一 topic 出现互斥 active constraints 时，loop 必须进入 `needs_human_resolution`，不得自行猜测。
4. claim approval 只能降低或限制 claim ceiling，不能越过 evaluator 和 taste gate 提升 claim。
5. Agent 可以提出拒绝人类建议，但必须生成 `agent_response_to_human` 并给出 evidence refs。

## 8. Agent 与科研人员沟通机制

### 8.1 Progress Narrative

每轮 Agent 必须生成一个短的 progress narrative：

1. 我正在做什么。
2. 为什么做。
3. 用了哪些输入。
4. 预计输出什么。
5. 当前风险是什么。
6. 什么时候需要人介入。

该 narrative 应写入：

1. UI timeline。
2. `research_loop.md`。
3. `research_loop.jsonl`。

Progress narrative 不能写成宣传稿。

必须使用固定约束：

1. 不得声称未验证的进展。
2. 不得把运行完成包装成科研进展。
3. 必须标出证据缺口。
4. 必须说明下一步是否需要人类判断。

### 8.1.1 汇报质量标准

Agent 面向科研人员的汇报必须遵守以下标准：

1. `结论先行`
   - 先说本轮最重要的结论，再说过程。
2. `层次稳定`
   - 每次汇报都包含：目标、动作、结果、解释、风险、下一步、需要人判断的问题。
3. `中间结果可读`
   - 对每个关键中间结果说明“这意味着什么”，而不是只列文件名或指标值。
4. `变化可比较`
   - 多轮迭代必须说明相比上一轮改变了什么，属于技能结构、技能使用、场景、evaluator、认知还是成果边界。
5. `证据可追溯`
   - 关键判断必须附 evidence refs，但正文不能依赖用户打开文件才能理解。
6. `不确定性显式`
   - 必须说明尚未证明什么，哪些结论只是候选。
7. `导师问题预判`
   - 必须列出 2 到 5 个专家可能追问的问题。

禁止以下汇报方式：

1. 只说“已完成”“已生成”“已通过验证”。
2. 只给文件路径，不解释其研究意义。
3. 用抽象词替代具体证据，例如“效果不错”“认知提升明显”。
4. 把失败轻描淡写成“后续可改进”。
5. 用长篇流水账掩盖关键结论。

### 8.1.2 Mentor Brief Template

每个阶段完成后必须能生成一个面向导师的 brief：

```text
本轮结论：
<一句话说明最重要的判断>

做了什么：
<3-5 条具体动作，不列无意义流水账>

关键发现：
<3-5 条，每条说明证据和含义>

没有证明什么：
<明确 claim 边界>

需要您判断：
<列出需要专家介入的问题>

如果继续：
<推荐下一步和理由>

证据入口：
<列出 3-5 个最关键 refs>
```

### 8.2 Agent Explanation Cards

每个关键建议都应有 explanation card：

1. Recommendation。
2. Evidence used。
3. Alternatives considered。
4. Why not other options。
5. Risk。
6. Human decision needed。

这样科研人员不用阅读所有 YAML，也能理解 Agent 的逻辑。

建议对象：

```yaml
object_type: agent_explanation_card
card_id: string
topic_id: string
stage: string
recommendation: string
short_answer: string
evidence_used: array[string]
alternatives_considered:
  - option: string
    rejected_reason: string
risk: array[string]
uncertainty: array[string]
human_decision_needed: boolean
suggested_human_actions: array[string]
generated_by_worker_ref: string
```

### 8.3 Human Question Channel

科研人员应能随时问：

1. 为什么推荐这个方向？
2. 这个结果为什么不能写成论文？
3. 哪些证据最关键？
4. 如果继续做，最有价值的下一步是什么？
5. 现在最大的认知不确定性是什么？

系统应基于当前 artifacts 回答，而不是依赖隐藏上下文。

### 8.4 Human Decision Impact

人的判断必须真正改变系统，而不是只写入备注。

每个关键人类对象都必须能被编译为 `routing_constraint`。
`routing_constraint` 的统一字段以第 7.7 节为准。

Loop controller 在进入下一轮前必须读取 active routing constraints。

这条规则保证：

1. 专家不是旁观者。
2. 人类批注不会丢在聊天记录里。
3. Agent 后续行为可被人的研究判断约束。
4. 每次方向变化都可审计。

### 8.5 Agent 解释义务

当科研人员改写方向或质疑结论时，Agent 必须生成一份 response：

`agent_response_to_human` 的统一字段以第 7.8 节为准。

如果 Agent 拒绝人的建议，必须给出证据理由。
如果没有足够证据拒绝，必须标记为 `needs_more_evidence`，不得用空泛解释拖延。

## 9. 后端 API 设计

第一版不必引入复杂数据库。

建议先做 file-backed API：

1. 读取 artifact index。
2. 读取 task cockpit summary。
3. 读取 worker timeline。
4. 读取 evidence graph。
5. 写入 human interaction objects。
6. 触发 backend scripts。

建议 API：

```text
GET /api/topics
GET /api/topics/{topic_id}/cockpit
GET /api/topics/{topic_id}/timeline
GET /api/topics/{topic_id}/evidence-graph
GET /api/topics/{topic_id}/researcher-lens
GET /api/topics/{topic_id}/human-attention-queue
GET /api/topics/{topic_id}/question-cards
GET /api/topics/{topic_id}/briefs
GET /api/topics/{topic_id}/artifacts/{object_id}
POST /api/topics/{topic_id}/actions/run-worker
POST /api/topics/{topic_id}/questions/answer
POST /api/topics/{topic_id}/human-review
POST /api/topics/{topic_id}/research-decision
POST /api/topics/{topic_id}/direction-override
POST /api/topics/{topic_id}/expert-annotation
POST /api/topics/{topic_id}/claim-approval
POST /api/topics/{topic_id}/iteration-steering
POST /api/topics/{topic_id}/agent-response-to-human
```

## 10. 前端 MVP

### 10.1 技术建议

如果仓库目前没有前端框架，建议新增轻量应用：

```text
workbench/
  package.json
  src/
  app/
  components/
  lib/
```

前端建议：

1. React + Vite。
2. File-backed FastAPI 或 Node API。
3. 不引入重型状态管理。
4. 第一版只读为主，少量写 human decision objects。

实现顺序必须是：

1. 先以静态 JSON fixture 跑通页面。
2. 再接 file-backed API。
3. 再开放写入 human objects。
4. 最后接 worker trigger。

不得在前端尚未有稳定数据契约时直接耦合后端脚本细节。

### 10.2 MVP 页面

第一版只做 4 个页面：

1. `Cockpit`
2. `Evidence Graph`
3. `Iteration Board`
4. `Human Review Panel`

不先做完整论文写作系统。

其中 `Cockpit` 必须优先展示 mentor brief，而不是优先展示文件列表。

### 10.3 研究者使用路径

MVP 必须覆盖一条真实的科研人员使用路径：

1. 科研人员打开 `Cockpit`，在 1 分钟内知道当前 topic 的状态、claim ceiling、taste grade、最大风险和下一步建议。
2. 科研人员先阅读 `mentor_brief`，无需打开原始文件即可理解本轮做了什么、发现了什么、没证明什么。
3. 科研人员点击 `为什么不能升级成果等级`，进入 explanation card，看到 supporting runs、metrics、cognition diagnosis 和缺失证据。
4. 科研人员进入 `Evidence Graph`，检查这个判断是否回链到 evaluator、run、literature 和 cognition。
5. 科研人员进入 `Iteration Board`，比较两轮 loop 到底改变了技能结构、使用参数、场景边界还是评价标准。
6. 科研人员在 `Human Review Panel` 写入一个 direction override，例如要求下一轮优先设计 boundary-triggering scenario，而不是继续调参。
7. 系统把 override 编译为 routing constraint。
8. 下一轮 Agent recommendation 显示该 human decision 已被读取并改变路由。

如果 MVP 不能走通这条路径，即使页面能展示数据，也不能算协同科研工作台成立。

### 10.4 MVP 样例任务

使用 `real-task-001` 作为演示案例。

必须能展示：

1. 三轮原始 task004 loop。
2. learning/reframing chain。
3. upgraded run `0029`。
4. 为什么仍是 `diaomu`。
5. 人可以写入一个 direction override：下一步优先做 boundary-triggering scenario。
6. mentor brief 能用导师可读语言解释上述结论。

### 10.5 UI 设计原则

前端设计必须遵守：

1. 先做研究驾驶舱，不做文件浏览器。
2. 每个高层结论都能一键下钻到证据。
3. 每个需要人判断的事项都必须进入 attention queue。
4. 每个 Agent 建议都必须说明证据、替代方案和风险。
5. 每个人类判断都必须写回对象，并影响后续路由。
6. 所有页面都要显示当前 claim ceiling 和 taste grade，防止表达上限被遗忘。
7. raw artifact 可以查看，但不能成为主交互入口。
8. 每个页面都应有“给导师看的摘要”，避免用户被迫读原始 artifact。

## 11. 后端最小实现计划

### Phase 0: Workbench Data Model

新增 schema：

1. `human_review`
2. `research_decision`
3. `direction_override`
4. `expert_annotation`
5. `claim_approval`
6. `workbench_topic`
7. `workbench_timeline_event`
8. `iteration_steering`
9. `routing_constraint`
10. `agent_response_to_human`
11. `agent_explanation_card`
12. `human_attention_item`
13. `researcher_lens`
14. `mentor_brief`
15. `iteration_digest`
16. `decision_brief`
17. `failure_brief`
18. `claim_brief`

新增目录：

```text
workbench_data/
  topics/
  human_reviews/
  decisions/
  annotations/
  claim_approvals/
  steering/
  routing_constraints/
  agent_responses/
  briefs/
```

建议路径：

```text
workbench_data/topics/{topic_id}/topic.yaml
workbench_data/topics/{topic_id}/cockpit.json
workbench_data/topics/{topic_id}/timeline.jsonl
workbench_data/topics/{topic_id}/evidence_graph.json
workbench_data/topics/{topic_id}/researcher_lens.json
workbench_data/topics/{topic_id}/human_attention_queue.json
workbench_data/topics/{topic_id}/question_cards.json
workbench_data/topics/{topic_id}/mentor_briefs.jsonl
workbench_data/human_reviews/{object_id}.yaml
workbench_data/decisions/{object_id}.yaml
workbench_data/annotations/{object_id}.yaml
workbench_data/claim_approvals/{object_id}.yaml
workbench_data/steering/{object_id}.yaml
workbench_data/routing_constraints/{object_id}.yaml
workbench_data/agent_responses/{object_id}.yaml
workbench_data/briefs/{object_id}.yaml
```

写入要求：

1. 原子写入，避免半写文件进入 evidence chain。
2. 写入后立即运行 schema validation。
3. 写入失败不得修改 topic timeline。
4. 写入成功后必须更新 index/timeline/evidence graph。
5. 同一 object_id 已存在时不得覆盖，只能创建新对象并使用 `supersedes`。

### Phase 1: Topic Aggregator

新增脚本：

```text
scripts/build_workbench_topic.py
scripts/verify_workbench_topic.py
```

输入：

1. task package。
2. analysis artifacts。
3. runs。
4. cognition。
5. delivery。

输出：

1. cockpit summary。
2. timeline。
3. evidence graph。
4. open questions。
5. human attention queue。

Aggregator 必须满足：

1. 支持任意 topic/task，不得写死 `real-task-001`。
2. `real-task-001` 只能作为 demo fixture。
3. 缺少 artifact 时输出 degraded summary，而不是崩溃。
4. 所有 summary 字段必须带来源 refs 或标记为 inferred。
5. 不得在 aggregator 中生成新的科研判断，只能汇总已有对象。

### Phase 1.5: Researcher Lens Aggregator

新增脚本：

```text
scripts/build_researcher_lens.py
scripts/verify_researcher_lens.py
```

输入：

1. cockpit summary。
2. timeline。
3. evidence graph。
4. worker outputs。
5. human objects。

输出：

1. `executive_layer`
2. `research_layer`
3. `audit_layer`
4. `human_attention_queue`
5. `question_answer_cards`
6. `agent_explanation_cards`

该层的职责不是生成新科研判断，而是把已有对象组织成科研人员可理解、可追问、可干预的信息结构。

### Phase 1.6: Research Communication Builder

新增脚本：

```text
scripts/build_research_communication_briefs.py
scripts/verify_research_communication_briefs.py
```

输入：

1. researcher lens。
2. timeline。
3. evidence graph。
4. loop review。
5. human attention queue。

输出：

1. `mentor_brief`
2. `iteration_digest`
3. `decision_brief`
4. `failure_brief`
5. `claim_brief`

要求：

1. brief 必须面向科研人员阅读，而不是面向机器。
2. brief 必须解释中间结果的研究意义。
3. brief 必须区分事实、解释、推断和建议。
4. brief 必须列出专家应关注的问题。
5. brief 必须提供证据入口，但不要求用户打开文件才能理解正文。

### Phase 2: Human Interaction Writer

新增脚本：

```text
scripts/write_human_review.py
scripts/write_research_decision.py
scripts/write_direction_override.py
scripts/write_expert_annotation.py
scripts/write_claim_approval.py
scripts/write_iteration_steering.py
scripts/compile_human_decision_constraints.py
scripts/write_agent_response_to_human.py
```

要求：

1. 每个写入对象必须 schema valid。
2. 每个对象必须引用目标 artifact。
3. 每个对象必须能进入 timeline。
4. 每个方向性对象必须能编译为 routing constraint。
5. 每个 human action 必须有 agent response。

### Phase 3: API Layer

新增轻量 API：

```text
workbench_api/
  app.py
```

功能：

1. 读取 cockpit。
2. 读取 timeline。
3. 读取 evidence graph。
4. 写入 human objects。
5. 触发预定义 scripts。

API 要求：

1. 第一版只允许触发白名单脚本。
2. 所有写请求必须先 dry-run validate，再实际写入。
3. API 不直接执行任意 shell 命令。
4. API 返回对象必须包含 `source_refs` 和 `validation_status`。
5. 触发 worker 时必须生成可追踪 job/event，而不是只返回同步文本。
6. 多用户并发暂不做复杂权限系统，但必须避免对象覆盖。

### Phase 3.5: Loop Integration Gate

新增脚本：

```text
scripts/apply_workbench_constraints_to_loop.py
scripts/verify_workbench_loop_integration.py
```

职责：

1. 读取 active routing constraints。
2. 检测冲突。
3. 把约束注入下一轮 loop context。
4. 生成 loop integration report。
5. 验证下一轮 Agent recommendation 是否引用了 human decision。

没有通过该 gate，不得声称“人的判断改变了下一轮 Agent 路由”。

### Phase 4: Frontend MVP

实现 4 个页面：

1. Cockpit。
2. Evidence Graph。
3. Iteration Board。
4. Human Review Panel。

### Phase 5: End-to-End Demo

用 `real-task-001` 演示：

1. 打开 topic。
2. 查看 Agent 进展。
3. 查看为什么结果不能升级。
4. 写入专家 direction override。
5. 触发下一步 planning recommendation。
6. 验证 human decision 已进入 artifact chain。

### Phase 6: Generic Topic Smoke Test

为了防止工作台退化为 `real-task-001` 专用展示页，必须增加通用 topic smoke test。

测试对象：

1. `real-task-001`。
2. 至少一个已有 task，例如 `task003` 或 `task005`。
3. 一个最小 synthetic topic fixture。

验收：

1. 三个 topic 都能生成 cockpit。
2. 三个 topic 都能生成 timeline。
3. 三个 topic 都能生成 researcher lens。
4. 缺少文献、run 或 cognition 的 topic 能明确显示 degraded status。
5. 不需要新增 framework 代码即可接入新 topic。

## 12. 验收标准

### 最低验收

1. 科研人员可以在 UI 中看到 real-task-001 的完整状态。
2. 科研人员可以看到 Agent 每一步输入、输出和验证状态。
3. 科研人员可以写入 `human_review` 或 `direction_override`。
4. 写入对象通过 schema validation。
5. Agent 下一轮推荐能读取该人类决策对象。
6. 科研人员可以看到 `human_attention_queue`。
7. 至少一个 explanation card 能回答“为什么当前不能写论文”。
8. 一个 human decision 能被编译为 active routing constraint。
9. 至少一个 mentor brief 能让科研人员不打开原始文件也理解本轮核心进展。

### 良好验收

1. UI 能展示 evidence graph。
2. UI 能区分 primary/secondary/cost metrics。
3. UI 能显示 claim ceiling 与 taste grade。
4. UI 能列出 human attention queue。
5. 系统能回答“为什么当前不能写论文”。
6. UI 能比较两轮迭代的变化类型：技能结构、技能使用、场景、evaluator 或 claim gate。
7. UI 能显示人的判断如何改变下一轮路由。
8. iteration digest 能清楚说明多轮迭代之间的实质差异。

### 高质量验收

1. 科研人员能通过工作台完成一次完整交互迭代。
2. 人的判断改变了下一轮 Agent 路由。
3. 该改变被记录为 evidence-backed research decision。
4. 后续报告能引用人类决策对象。
5. 科研人员能从 executive layer 下钻到 audit layer，完整追溯一个关键结论。
6. 系统能明确提示“继续投入可能陷入局部陷阱”的情形。
7. Agent 能对专家质疑作出证据化回应，而不是泛泛解释。
8. 研究者沟通层的 brief 能稳定达到“导师汇报”质量，而不是文件清单质量。

### 必须验证的命令

执行计划完成后，至少需要提供以下验证证据：

```bash
python scripts/verify_workbench_topic.py --topic real-task-001
python scripts/verify_researcher_lens.py --topic real-task-001
python scripts/verify_research_communication_briefs.py --topic real-task-001
python scripts/write_human_review.py --topic real-task-001 --dry-run
python scripts/write_research_decision.py --topic real-task-001 --dry-run
python scripts/write_direction_override.py --topic real-task-001 --dry-run
python scripts/write_expert_annotation.py --topic real-task-001 --dry-run
python scripts/write_claim_approval.py --topic real-task-001 --dry-run
python scripts/write_iteration_steering.py --topic real-task-001 --dry-run
python scripts/compile_human_decision_constraints.py --topic real-task-001 --dry-run
python scripts/verify_workbench_loop_integration.py --topic real-task-001 --dry-run
python scripts/verify_workbench_topic.py --topic synthetic-topic-fixture
python scripts/verify_workbench_topic.py --topic task003
python scripts/validate_schemas.py --artifacts workbench
```

如引入前端，还必须验证：

```bash
npm --prefix workbench test
npm --prefix workbench run build
```

### 不得声称完成的情况

出现以下任一情况，不得声称工作台 MVP 成立：

1. 只能展示 `real-task-001`，不能接入第二个 topic。
2. human object 写入后没有进入 timeline/evidence graph。
3. direction override 不能编译为 routing constraint。
4. 下一轮 Agent context 没有读取 routing constraint。
5. explanation card 没有 evidence refs。
6. UI 只能浏览 raw YAML，不能回答研究者关键问题。
7. claim approval 可以绕过 evaluator 或 taste gate。
8. mentor brief 只是文件清单或流水账，不能解释研究意义。

## 13. 风险

### 风险 1: UI 变成 YAML 浏览器

防护：

1. 必须提供 cockpit summary。
2. 必须提供 Agent explanation cards。
3. 必须提供 human attention queue。

### 风险 2: 人类交互只停留在聊天

防护：

1. 所有关键交互必须写 object。
2. 所有 object 必须 schema valid。
3. Agent 后续必须读取这些 objects。

### 风险 3: 过早做复杂产品

防护：

1. 第一版只做 real-task-001。
2. 第一版只做 4 个页面。
3. 第一版只做 file-backed API。

### 风险 4: 工作台削弱 Agent 自主性

防护：

1. Agent 仍然执行 worker chain。
2. 人只在关键判断点介入。
3. 人类决策也被对象化，而不是随意打断。

### 风险 5: 科研人员被信息淹没

防护：

1. 必须提供 executive/research/audit 三层信息。
2. 默认只显示需要判断的问题，不默认展开全部 artifact。
3. 所有长日志必须被压缩为 explanation card 和 evidence refs。
4. raw log 仅作为 audit drill-down。

### 风险 6: 人类判断没有系统后果

防护：

1. 每个方向性人类对象必须编译为 routing constraint。
2. 下一轮 loop 必须读取 active constraints。
3. Agent 必须生成 response_to_human。
4. 若人类判断未被采纳，必须有证据化理由。

### 风险 7: 工作台变成单任务定制系统

防护：

1. `real-task-001` 只能作为 demo，不得写入核心逻辑分支。
2. 必须通过 generic topic smoke test。
3. topic aggregator 必须允许 degraded status。
4. 所有 task-specific 内容放入 topic/task package 或 adapter，不进入 workbench framework。

### 风险 8: 人类决策绕过科研护栏

防护：

1. human approval 不能提升 claim ceiling，只能确认、限制或降级。
2. evaluator 和 taste gate 仍是 claim 上限的硬约束。
3. human override 如果要求违反证据边界，必须进入 `needs_more_evidence` 或 `rejected`。
4. 所有人类决策必须保留 rejected options 和 rationale。

### 风险 9: 敏感信息和模型输出泄漏

防护：

1. API 和 UI 默认不展示 provider token、auth、环境变量和本机绝对隐私路径。
2. raw agent output 进入 UI 前必须支持 redaction。
3. 导出的 report 不应包含隐藏 prompt、API key、模型认证配置。
4. workbench_data 可包含本地证据路径，但对外分享前必须经过 export filter。

### 风险 10: Agent explanation 变成二次幻觉

防护：

1. explanation card 必须引用已有 artifact。
2. 没有 evidence refs 的 explanation 只能标记为 `ungrounded_draft`。
3. researcher lens aggregator 不产生新科研判断。
4. 自由问答回答必须区分 grounded answer、inference 和 unknown。

### 风险 11: 汇报可读性不稳定

防护：

1. 所有阶段都使用 mentor brief template。
2. brief 必须先给结论，再给证据。
3. brief 必须解释中间结果的研究意义。
4. brief 必须列出“需要专家判断的问题”。
5. brief verifier 应检查是否只输出文件清单、流水账或空泛评价。

## 14. 下一步建议

下一步应先执行：

```text
plans/collaborative-research-workbench-plan.md
```

但执行时不要直接写前端。

建议先完成：

1. human-in-the-loop schema。
2. workbench topic aggregator。
3. researcher lens aggregator。
4. research communication brief builder。
5. real-task-001 cockpit summary。
6. human attention queue。
7. human review writer。
8. all human object writers。
9. routing constraint compiler。
10. loop integration gate。
11. generic topic smoke test。
12. verifier。

只有当这些后端交互对象稳定后，再做 UI。

原因很简单：

> 如果人类判断不能被对象化和回链，即使界面再漂亮，也只是一个科研聊天面板，不是协同科研工作台。
