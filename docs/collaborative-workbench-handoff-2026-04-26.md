# Collaborative Workbench Handoff - 2026-04-26

## 1. 当前方向

DaoShuGuo 当前阶段已经从“单纯开发 Python 脚本跑自主科研闭环”转向：

> 面向科研人员的人-Agent 协同科研工作台。

这个工作台的目标不是替代现有 CLI，也不是先做漂亮 UI，而是从当前 CLI 环境出发，把已有的任务、运行、评价、认知、证据和人类判断组织成可视化、可交互、可审计的科研过程。

当前总体链路应理解为：

```text
CLI artifacts
  -> workbench_data
  -> researcher-facing briefs / cockpit / evidence graph / timeline
  -> human decisions
  -> routing constraints
  -> next CLI / Agent loop
```

## 2. 已完成的核心能力

### 2.1 计划与设计

新增计划：

- `plans/collaborative-research-workbench-plan.md`

该计划明确了：

1. 不重造 onboarding、loop engine、evaluator、Pi runtime。
2. 先做 backend object layer，再做 API 和 UI。
3. 工作台不能只是 YAML 浏览器。
4. 人类判断必须对象化、证据化、可回链。
5. 人类判断必须能编译为下一轮 loop 可读取的 routing constraints。
6. Agent 必须能生成导师可读的阶段汇报，而不是只产出文件。

已补充讨论记录：

- `docs/实验过程与讨论记录.md`

其中记录了第十次重要转向：从自主脚本框架转向协同科研工作台。

### 2.2 新增 schema

已新增 workbench / human-in-the-loop / communication 相关 schema：

1. `workbench_topic`
2. `workbench_timeline_event`
3. `human_review`
4. `research_decision`
5. `direction_override`
6. `expert_annotation`
7. `claim_approval`
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

对应样例也已加入 `schemas/samples/`。

### 2.3 新增脚本

核心通用库：

- `scripts/workbench_common.py`

薄 CLI 入口：

1. `scripts/build_workbench_topic.py`
2. `scripts/verify_workbench_topic.py`
3. `scripts/build_researcher_lens.py`
4. `scripts/verify_researcher_lens.py`
5. `scripts/build_research_communication_briefs.py`
6. `scripts/verify_research_communication_briefs.py`
7. `scripts/write_human_review.py`
8. `scripts/write_research_decision.py`
9. `scripts/write_direction_override.py`
10. `scripts/write_expert_annotation.py`
11. `scripts/write_claim_approval.py`
12. `scripts/write_iteration_steering.py`
13. `scripts/write_agent_response_to_human.py`
14. `scripts/compile_human_decision_constraints.py`
15. `scripts/apply_workbench_constraints_to_loop.py`
16. `scripts/verify_workbench_loop_integration.py`

### 2.4 已生成的 workbench 数据

当前已生成：

- `workbench_data/topics/real-task-001/`
- `workbench_data/topics/task003/`
- `workbench_data/topics/synthetic-topic-fixture/`
- `workbench_data/briefs/`
- `workbench_data/human_reviews/`
- `workbench_data/decisions/`
- `workbench_data/annotations/`
- `workbench_data/claim_approvals/`
- `workbench_data/steering/`
- `workbench_data/routing_constraints/`
- `workbench_data/agent_responses/`

这证明当前实现不是只绑定 `real-task-001`，至少已经能做一个已有 task 和一个 synthetic fixture 的 smoke test。

## 3. 当前能力边界

### 3.1 已成立

当前已经可以：

1. 从现有 task/run/analysis/delivery artifacts 构建 workbench topic。
2. 为 topic 生成 cockpit、timeline、evidence graph、human attention queue。
3. 生成 researcher lens。
4. 生成 `mentor_brief` 等科研沟通 brief。
5. 通过 CLI 写入人类审查、方向覆盖、专家批注、claim approval、iteration steering。
6. 将 active human objects 编译为 routing constraints。
7. 将 routing constraints 汇总为下一轮 loop 可读取的 `loop_context.json`。
8. 对 workbench artifact set 做 schema validation。

### 3.2 尚未成立

当前还没有完成：

1. 前端 UI。
2. file-backed API server。
3. generic loop engine 对 `loop_context.json` 的真实消费。
4. LLM-authored high-quality mentor brief。
5. 多用户权限、并发编辑和审计 UI。
6. 真正的交互式 Agent 对话通道。

当前的 mentor brief 是 deterministic/template-based，已经比文件清单更可读，但还不是优秀研究生级别的汇报。

## 4. 已通过验证

已通过以下命令：

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

Plan execution review:

- `reviews/collaborative-research-workbench-plan-review.md`

Verdict: `APPROVED` for backend/object-layer MVP.

## 5. 当前最重要的问题

用户明确指出：交互过程是否合理，是这个方向能否成立的核心。

关键问题不是“有没有 UI”，而是：

1. Agent 汇报是否稳定可读。
2. 中间过程是否能被专家快速理解。
3. 专家是否不必打开大量代码、YAML、JSON、日志才能判断进展。
4. Agent 是否能像合格研究生一样，用清晰准确的方式向导师汇报。
5. 人类反馈是否真正改变后续工作，而不是只停留在聊天记录。

因此，后续开发不能只堆对象和脚本。

必须尽快做一个直观可体验的完整框架，让科研人员看到：

1. 当前 topic 状态。
2. 导师可读 brief。
3. 证据链。
4. 多轮迭代变化。
5. 需要人工判断的问题。
6. 写入判断后的路由变化。

## 6. 推荐下一阶段开发顺序

### Step 1: 做一个最小可体验界面

不要继续挤牙膏式完善细节。

先搭出直观体验：

1. Cockpit 页面。
2. Mentor Brief 区域。
3. Evidence Graph 简化视图。
4. Iteration / Timeline 视图。
5. Human Attention Queue。
6. Human Decision 写入表单。
7. Loop Context / Routing Constraints 结果展示。

第一版可以只读本地 `workbench_data/`，不必一开始做复杂 API。

### Step 2: 接 file-backed API

前端静态体验跑通后，再接：

1. `GET /topics`
2. `GET /topics/{topic}/cockpit`
3. `GET /topics/{topic}/briefs`
4. `GET /topics/{topic}/evidence-graph`
5. `GET /topics/{topic}/human-attention-queue`
6. `POST /topics/{topic}/direction-override`
7. `POST /topics/{topic}/compile-constraints`

### Step 3: 让 generic loop engine 消费 loop context

这是“人类判断改变下一轮 Agent 路由”的真正闭环。

需要把：

- `workbench_data/topics/{topic}/loop_context.json`

接入到：

- generic loop engine
- agent context pack
- Pi/Codex worker prompt

### Step 4: 优化 mentor brief

当前 brief 是模板化的。

下一步应支持：

1. deterministic baseline brief。
2. LLM-improved mentor brief。
3. brief quality verifier。
4. human feedback on brief quality。

目标不是写得漂亮，而是像研究生向导师汇报一样：

1. 结论先行。
2. 证据清楚。
3. 问题明确。
4. 边界诚实。
5. 下一步可讨论。

## 7. 需要避免的误区

1. 不要继续只加 schema，而没有直观体验。
2. 不要先做复杂产品架构。
3. 不要把 UI 做成 YAML 浏览器。
4. 不要让 mentor brief 退化成文件清单。
5. 不要让人类判断只停留在备注，而不影响 loop。
6. 不要为了 `real-task-001` 写 task-specific 逻辑。
7. 不要把 communication improvement 包装成 scientific improvement。

## 8. 下次会话建议起点

建议下次会话直接从以下目标开始：

> 基于现有 `workbench_data/`，实现一个最小可体验的协同科研工作台界面。

优先目标：

1. 能打开 `real-task-001`。
2. 第一屏看到 mentor brief。
3. 能看到 claim ceiling、taste grade、blocking issue。
4. 能看到 evidence refs。
5. 能看到 human attention queue。
6. 能写入一个 direction override。
7. 能看到 routing constraints / loop context 发生变化。

第一版 UI 不求好看，但必须让科研人员获得直观体验。

