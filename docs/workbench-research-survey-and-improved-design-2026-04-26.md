# Collaborative Research Workbench Survey And Improved Design - 2026-04-26

## 1. 调研目的

本调研服务于 DaoShuGuo 下一阶段开发：在实现协同科研工作台 UI/API 前，先理解已有类似方案、科研成果和可借鉴的设计原则。

当前项目目标不是复刻一个“全自动 AI Scientist”，而是建设：

> 面向电力科研人员的人-Agent 协同科研工作台。

核心问题是：

1. 如何让科研人员快速理解 Agent 中间过程。
2. 如何让人类判断成为结构化、可审计、可回链的研究对象。
3. 如何让人类反馈真实改变下一轮 Agent 路由。
4. 如何避免把流程完成、文档生成或 UI 展示误判为科研进展。

## 2. 调研对象

### 2.1 全自动科研 Agent：The AI Scientist

The AI Scientist 的目标是端到端自动化科学研究：生成研究想法、写代码、跑实验、画图、写论文、自动评审。其 arXiv 摘要称其能够让前沿模型“independently”执行研究并沟通发现；Nature 版本进一步说明其覆盖 ideation、literature search、experiment planning、implementation、analysis、manuscript writing、peer review 等阶段。

可借鉴点：

- 研究过程应被分解为可执行阶段。
- 实验日志和 notes 是后续写作/评审的重要中间资产。
- 自动 reviewer 可以作为初筛，但不能替代真实科研 judgment。

警示点：

- Nature 论文明确指出它仍存在 naive ideas、实现错误、实验严谨性不足、幻觉引用等失败模式。
- 它适合计算机内闭环较强的 ML 研究；电力科研中 scenario、evaluator、baseline 和工程边界更容易成为决定性瓶颈。
- DaoShuGuo 不能把“自动写出论文”作为主目标，否则会偏离技能、认知、成效三要素。

设计吸收：

- 保留 experiment journal / iteration digest。
- 引入 claim reviewer，但只作为护栏，不作为最终授权。
- UI 中必须暴露 failure modes、claim ceiling、evidence gaps，而不是只展示生成结果。

### 2.2 AI Co-Scientist：Google AI co-scientist

Google AI co-scientist 是 Gemini 2.0 驱动的多 Agent 科研协作系统，用于生成新假设和研究 proposal。其设计包括 Generation、Reflection、Ranking、Evolution、Proximity、Meta-review 等专门 Agent，并允许科学家提供 seed ideas 和自然语言反馈。

可借鉴点：

- 科学发现不是单 Agent 顺序流程，而是生成、反思、排序、演化和 meta-review 的组合。
- 系统明确接受 scientist-provided objectives and guidance。
- 专家反馈不是旁路，而是系统交互范式的一部分。

警示点：

- 其主要对象是 hypothesis/proposal generation，不直接解决本项目已有的 task/evaluator/skill/cognition artifact 可视化问题。
- 公开材料也承认需要更强 factuality checking、外部工具交叉检查、更多专家参与的大规模评价。

设计吸收：

- DaoShuGuo 的 Agent 不应只有 executor；应拆出 brief worker、claim reviewer、cognition critic、routing compiler。
- 工作台应支持 human seed idea、direction override、expert annotation。
- 下一步 UI 必须显示“人类反馈如何改变路由”，而不只是收集反馈。

### 2.3 自驱实验室 / 工具型科研 Agent：Coscientist

Coscientist 展示了 LLM 结合 web search、documentation search、code execution 和实验自动化 API 后，能规划并执行复杂化学实验。Nature 论文列出六类能力：化学合成规划、硬件文档搜索、云实验室高层指令、液体处理仪低层控制、多模块任务集成、历史实验数据优化。

可借鉴点：

- Agent 的行动空间必须被工具命令清楚限定。
- 文档搜索、代码执行、实验执行应作为不同模块，有明确输入输出。
- Tool outputs 是证据，不只是对话上下文。

警示点：

- 工具成功不等于科研 judgment 成立。
- 物理/工程实验系统尤其需要安全边界、操作审计和失败记录。

设计吸收：

- DaoShuGuo 的 loop controller 只负责调度、校验和证据绑定；不能直接伪装成 cognition worker。
- UI 需要显示“Agent 调用了什么工具、得到什么证据、为什么这支持/不支持当前 claim”。
- 对电力系统场景，scenario/evaluator/runtime 应被视为工具边界的一部分。

### 2.4 可复现科研平台：Renku、DVC、Galaxy、OSF

Renku 关注数据、代码、计算环境和 workflow 的可复现协作。其知识图谱用 PROV-O 等开放标准连接项目、数据集、代码和结果，并强调 metadata 不是目的，平台应帮助人们 discover、learn、get things done。

DVC 把 pipeline stage 的 command、dependencies、parameters、outputs 写入 `dvc.yaml` / `dvc.lock`，使实验可复现、可重跑、可共享。

Galaxy 通过图形化 workflow、histories、pages 降低科研工作流门槛。其 Pages 能把 histories、workflows、datasets 组织成解释“how and why”的 virtual paper。

OSF 则更像科研生命周期管理和长期归档平台，支持项目协作、存储、预注册、第三方工具集成和长期保存。

可借鉴点：

- provenance graph 是科研平台底座。
- 研究者需要从 workflow/result 下钻到 data/code/environment。
- 界面要照顾非工程用户，但不能剥夺高级用户访问底层对象的能力。
- “页面/brief”应该解释 how and why，而不是展示文件清单。

警示点：

- 这些平台多数不解决 LLM Agent 的 claim 过度、认知幻觉、导师式汇报问题。
- 纯 provenance 平台容易变成元数据系统，而不是科研判断系统。

设计吸收：

- DaoShuGuo 需要 evidence graph，但第一屏不能是图数据库浏览器。
- 每个 brief 必须有 evidence refs、source paths、object ids。
- 工作台应该提供 executive / research / audit 三层信息。

### 2.5 Human-AI Interaction / Collaborative Intelligence

Microsoft 的 Human-AI Interaction Guidelines 将 AI 交互分为初始交互、常规交互、出错时、长期使用四类，并强调 AI 系统应在不同阶段表现出合适的不确定性、可控性、反馈吸收和错误恢复。

关于 human-AI collaborative discovery 的研究强调：系统不应追求 AI 替代人，而应扩展人类创造力；有效协作需要 shared state、shared communication、calibrated trust、transparent intentions、joint decision making，并且要把有限的人类注意力路由到最有价值的位置。

可借鉴点：

- 人类注意力是稀缺资源，系统必须主动管理。
- 用户反馈必须是 explicit、intentional、informed，而不是含糊聊天。
- 系统应显示 AI 的不确定性、能力边界和错误恢复路径。

警示点：

- 简单“human in the loop”容易沦为形式审批。
- 如果系统只让人批准/拒绝，而不说明影响路径，人类反馈不会形成有效科研资产。

设计吸收：

- Human Attention Queue 是一等对象。
- Human decision 写入后必须显示 impact preview。
- 每个 Agent 建议都要说明 confidence、evidence、uncertainty、possible next route。

## 3. 综合判断

现有方案可以分为五类：

| 类型 | 代表 | 强项 | 不足 | DaoShuGuo 应吸收 |
| --- | --- | --- | --- | --- |
| 全自动科研 Agent | The AI Scientist | 端到端研究自动化、自动实验/写作/评审 | 易产生弱想法、实现错误、幻觉引用、过度 claim | 实验日志、自动初审、失败模式暴露 |
| AI co-scientist | Google AI co-scientist | 多 Agent 假设生成、反思、排序、演化，科学家可反馈 | 偏 hypothesis/proposal，不直接管理本地科研 artifact | 专家反馈、生成-反思-排序-演化机制 |
| 自驱实验室 | Coscientist | 工具调用、文档检索、实验执行边界清楚 | 工具执行不等于科研判断 | 工具输出证据化、action space 明确 |
| 可复现科研平台 | Renku / DVC / Galaxy / OSF | provenance、workflow、data/code/env 可复现协作 | 不处理 LLM 认知质量和 claim 审核 | evidence graph、history、pages、dependency/output contract |
| Human-AI 协作框架 | HAI guidelines / collaborative intelligence | shared state、calibrated trust、attention management | 原则较泛，需要领域落地 | Human Attention Queue、impact preview、explicit feedback |

结论：

> DaoShuGuo 不应做“全自动 AI Scientist”，也不应只做“科研 artifact 管理平台”。它应做一个以科研 judgment 为中心的 human-Agent collaborative workbench。

也就是：

```text
Agent 高吞吐执行 + deterministic evidence substrate + human taste/judgment node
```

## 4. 改进后的系统设计

### 4.1 系统定位

系统目标：

> 让电力科研人员能够在一个 topic 上快速理解 Agent 工作状态、审查证据、判断 claim 上限、写入专家反馈，并让反馈约束下一轮 Agent 行动。

第一阶段不追求：

- 自动写论文。
- 自动生成复杂多 Agent 组织。
- 大而全科研管理平台。
- 漂亮但不可审计的 dashboard。

第一阶段追求：

- 研究状态可读。
- 证据链可查。
- claim 上限清楚。
- 人类介入点明确。
- 人类判断可写回。
- 路由变化可预览。

### 4.2 架构

建议采用五层架构：

```text
1. Research Artifact Layer
   tasks / adapters / evaluators / runs / analysis / skills / cognition / literature

2. Workbench Object Layer
   workbench_topic / timeline_event / researcher_lens / mentor_brief
   human_attention_item / evidence_graph / claim_brief

3. Human Decision Layer
   human_review / research_decision / direction_override
   expert_annotation / claim_approval / iteration_steering

4. Constraint Compiler Layer
   human objects -> routing_constraint -> loop_context.json

5. Agent Loop Integration Layer
   loop_context.json -> context pack / worker prompt / next CLI loop
```

关键边界：

- Workbench 不重写 evaluator。
- Workbench 不重写 generic loop engine。
- Workbench 不直接判断科学 claim 是否成立。
- Workbench 负责组织信息、收集判断、编译约束、暴露证据。

### 4.3 Agent 逻辑

建议把 Agent 角色拆为：

1. `artifact summarizer`
   - 从 run/analysis/schema 中提取当前状态。
   - 不做最终科研判断。

2. `mentor brief worker`
   - 生成导师可读汇报。
   - 必须引用 evidence refs。
   - 必须说明 claim ceiling 和 uncertainty。

3. `claim reviewer`
   - 检查 claim 是否超过 evidence。
   - 输出 claim approval / rejection suggestion。

4. `cognition critic`
   - 判断本轮结果属于 skill-use improvement、skill-structure improvement、evaluator problem 还是 task problem。

5. `human attention router`
   - 把最需要专家判断的问题放入 attention queue。
   - 不把所有信息都推给人。

6. `routing compiler`
   - 将 human objects 编译为下一轮 loop constraints。
   - 输出可预览、可审计的 `loop_context.json`。

### 4.4 接口设计

第一阶段建议 file-backed API，不直接引入数据库。

只做最小接口：

```text
GET  /topics
GET  /topics/{topic}/cockpit
GET  /topics/{topic}/briefs
GET  /topics/{topic}/evidence-graph
GET  /topics/{topic}/human-attention-queue
GET  /topics/{topic}/loop-context

POST /topics/{topic}/direction-override
POST /topics/{topic}/expert-annotation
POST /topics/{topic}/claim-approval
POST /topics/{topic}/compile-constraints
```

每个 POST 必须返回：

```yaml
written_object_ref: ...
affected_topic_ref: ...
compiled_constraint_refs: [...]
loop_context_path: ...
impact_summary: ...
verification_status: ...
```

### 4.5 交互设计

工作台第一屏必须回答：

1. 当前研究主题是什么。
2. 当前阶段是什么。
3. 当前最强 claim ceiling 是什么。
4. 当前 taste grade 是什么。
5. 当前 blocking issue 是什么。
6. 当前证据是否足够。
7. 哪些问题需要导师/专家判断。
8. 如果写入判断，下一轮 Agent 会怎么变。

页面结构：

```text
Topic Header
  topic / stage / status / last updated

Research Cockpit
  claim ceiling / taste grade / blocking issue / recommended action

Mentor Brief
  conclusion first / evidence / uncertainty / next question

Human Attention Queue
  item / why human needed / expected decision type / consequence

Evidence Graph
  brief nodes first, expandable to raw objects

Timeline
  iteration digest, decisions, route changes

Decision Panel
  direction override / expert annotation / claim approval

Routing Preview
  generated constraints / loop_context diff
```

### 4.6 数据设计

需要强化现有对象的几个字段：

1. `source_refs`
   - 指向原始 artifact path / object id。

2. `claim_scope`
   - 声明该对象能支持什么 claim，不能支持什么 claim。

3. `uncertainty`
   - 不确定性来源、影响程度、需要什么证据降低不确定性。

4. `human_decision_impact`
   - 人类判断影响哪些 routing constraints。

5. `attention_reason`
   - 为什么这个问题需要人类判断，而不是 Agent 自己继续跑。

6. `route_diff`
   - 编译前后的 loop context 差异。

### 4.7 文档设计

后续文档应分为四类：

1. `architecture`
   - 说明工作台边界、对象层、路由层、Agent 职责。

2. `interaction`
   - 说明导师/专家如何阅读、追问、批注、授权、纠偏。

3. `object-contract`
   - 说明每类 workbench/human/constraint 对象字段和生命周期。

4. `verification`
   - 说明如何证明工作台没有只做展示，而是真的改变下一轮 loop。

## 5. 对当前计划的改进建议

原计划是：

1. 最小 UI。
2. file-backed API。
3. loop context 消费。
4. mentor brief 优化。

调研后建议调整为：

### Phase 1: Evidence-Centered Cockpit

先做只读 cockpit，但必须包含：

- mentor brief
- claim ceiling
- taste grade
- blocking issue
- evidence refs
- timeline
- human attention queue

验收标准：

- 研究人员 1 分钟内知道当前状态。
- 10 分钟内能追溯主要 claim 的证据。

### Phase 2: Decision Writeback And Impact Preview

加入 human decision 写入：

- direction override
- expert annotation
- claim approval

同时显示：

- written object
- compiled constraints
- loop_context diff

验收标准：

- 人类判断不是备注，而能改变 routing constraints。

### Phase 3: LLM Mentor Brief With Grounding Gate

在 deterministic brief 之后增加 LLM brief worker。

必须包含：

- evidence refs completeness check
- overclaim gate
- uncertainty section
- comparison with deterministic baseline

验收标准：

- brief 质量提高，但 claim ceiling 不被写作能力抬高。

### Phase 4: Loop Consumption Proof

让 generic loop / context pack / worker prompt 消费 `loop_context.json`。

验收标准：

- 同一 topic 写入不同 human decision 后，下一轮 Agent prompt 或 route 有可验证差异。

## 6. 第一版实现建议

第一版不要做复杂后端。

推荐顺序：

1. 读取现有 `workbench_data/`。
2. 实现本地 file-backed API。
3. 做 cockpit UI。
4. 支持 direction override 写入。
5. 调用 constraint compiler。
6. 显示 `loop_context` diff。
7. 跑现有验证命令。

第一版 UI 不追求产品化，但必须让科研人员直观看到：

- Agent 汇报是否像合格研究生。
- 证据链是否可信。
- 人类反馈是否真正改变系统。

## 7. Sources

- The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery, arXiv: https://arxiv.org/abs/2408.06292
- Towards end-to-end automation of AI research, Nature: https://www.nature.com/articles/s41586-026-10265-5
- Towards an AI co-scientist, arXiv: https://arxiv.org/abs/2502.18864
- Google Research AI co-scientist blog: https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
- Autonomous chemical research with large language models, Nature: https://www.nature.com/articles/s41586-023-06792-0
- Renku platform overview: https://blog.renkulab.io/introducing-renku/
- Renku NeurIPS Datasets and Benchmarks paper: https://proceedings.neurips.cc/paper_files/paper/2023/file/838694e9ab6b0a193b84daaafcac0eed-Paper-Datasets_and_Benchmarks.pdf
- DVC data pipelines documentation: https://doc.dvc.org/start/data-pipelines/data-pipelines
- Galaxy computational biology platform overview: https://en.wikipedia.org/wiki/Galaxy_%28computational_biology%29
- Open Science Framework product overview: https://www.cos.io/products/osf
- Microsoft Guidelines for Human-AI Interaction: https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/
- Collaborative Intelligence in Sequential Experiments, Information Systems Research: https://pubsonline.informs.org/doi/10.1287/isre.2024.1154
