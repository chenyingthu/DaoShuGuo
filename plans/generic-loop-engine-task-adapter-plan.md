# 通用 Loop Engine + Task Adapter + Diagnosis Layer 结构性推进计划

## 1. 计划定位

本计划不是为了继续把 `task004` 做得更好看，也不是为了围绕某个单任务继续修补脚本。

本计划的核心目标是：

> 将当前项目中已经暴露出的 loop、worker、task/evaluator 适配与认知归因问题，抽象为一套可跨 `task004 / task005 / task006` 复用的通用框架层。

换句话说，本计划针对的是：

- 通用 loop engine
- task adapter contract
- generic diagnosis layer

而不是单一 task 的局部优化。

## 2. 背景与问题

### 2.1 当前项目已经证明的部分

当前仓库已经证明：

1. Pi 可以作为可 harness 的底层 agent runtime
2. skill / cognition / effectiveness 可以形成最小闭环
3. worker 边界与 controller overreach 已经被明确识别
4. task004 的 skill-evolution 结果已经能产出最小 worker 对象链

### 2.2 当前暴露出的结构性问题

但当前也已经暴露出几个不能再回避的问题：

1. loop 逻辑仍然严重 task-specific
2. controller 仍容易偷偷下场，替 worker 做判断
3. task/evaluator 盲区会被误判成 skill 问题
4. 同一种问题到 task005/task006 时可能被重复返工

### 2.3 这一步为何必须做

如果现在不抽象通用框架，而继续在 task004 上临时修补，那么：

- task005 会再来一轮
- task006 会再来一轮
- 框架会不断积累 task-specific 脚本
- 最后既不能说是“自主科研架构”，也不能说是“可延续的研究工程”

因此，现在必须进行结构性推进。

## 3. 总体目标

本计划分三大目标。

### 3.1 通用 Loop Engine

提供一个不依赖 task004 的 loop engine，负责：

- worker 调度
- 输入输出绑定
- 状态机
- 对象落盘
- verifier 接口

它不负责：

- task-specific 评价逻辑
- 具体技能实现
- 具体认知结论

### 3.2 Task Adapter Contract

为每个 task 提供一个薄而明确的 adapter 层，负责：

- task definition
- baseline / candidate binding
- evaluator binding
- search envelope
- task-specific diagnosis hooks

目标是：

> 新 task 的接入只改 adapter，而不是重写 loop。

### 3.3 Generic Diagnosis Layer

建立一个统一的 diagnosis 归因层，明确区分：

1. framework problem
2. task-adapter problem
3. skill-use problem
4. skill-structure problem
5. evaluator-design problem

它要做的不是简单“总结结果”，而是：

- 给出问题归属
- 给出下一轮应该交给哪个 worker
- 给出是否应该继续 skill evolution、还是先修 task/evaluator

## 4. 设计原则

### 4.1 通用性优先于局部完美

本阶段不追求所有 task 都立刻达到最好效果。

优先追求：

- 同一个 loop engine 能服务不同 task
- 不同 task 能共享相同对象链和 verifier 逻辑

### 4.2 controller 不得下场

这是硬原则。

通用 loop engine 只能：

- 调度
- 路由
- 状态管理
- 对象绑定

不能：

- 直接生成 skill 变更
- 直接做效果判断
- 直接做 cognition diagnosis

### 4.3 task adapter 必须薄

adapter 层只允许包含：

- task binding
- evaluator binding
- search envelope
- task-specific interpretation hook

不允许把 loop 逻辑重新塞回 adapter。

### 4.4 diagnosis 必须能拒绝继续 loop

diagnosis layer 不只是说“下一轮做什么”，还必须能说：

- 暂停 skill evolution
- 先修 evaluator
- 先扩 search envelope
- 当前 task 不适合继续迭代

否则框架会在错误问题上无限空转。

## 5. 目标产物

本计划完成后，至少应交付以下产物。

### 5.1 文档产物

1. `docs/generic-loop-engine-spec.md`
2. `docs/task-adapter-contract.md`
3. `docs/generic-diagnosis-layer-spec.md`

### 5.2 代码产物

1. 通用 loop engine 最小运行骨架
2. task adapter 基类/契约解析器
3. diagnosis layer 最小实现
4. 对应 verifier

### 5.3 适配产物

1. `task004` 作为第一个 adapter 实现
2. 用 `task004` 跑通通用 loop engine
3. 证明 task004 只通过 adapter 接入，而不是重写 loop

## 6. 分阶段推进

---

## Phase 1: 文档与契约固定

### 目标

先把三层抽象固定下来，防止后续实现再次退化成 task-specific patch。

### 工作内容

- [x] 写 `generic-loop-engine-spec.md`
- [x] 写 `task-adapter-contract.md`
- [x] 写 `generic-diagnosis-layer-spec.md`
- [x] 明确 loop engine / adapter / diagnosis 的输入输出边界
- [x] 明确 worker object chain 的最小 required artifacts

### 验收标准

- [x] 三份 spec 可指导后续编码
- [x] controller / worker / adapter 边界不再含糊
- [x] 任何新增 loop 脚本都能被归类到三层之一

---

## Phase 2: 通用对象链最小实现

### 目标

将已有 task004 worker chain 从“事后 materialize”推进到“框架原生对象链”。

### 工作内容

- [x] 抽象 `skill change request/result` 的通用写入函数
- [x] 抽象 `effectiveness assessment` 对象的通用写入函数
- [x] 抽象 `cognition diagnosis` / `cognition_to_skill_update` 对象写入函数
- [x] 抽象 `loop routing decision` / `loop review` 写入函数
- [x] 将 `verify_loop_worker_boundaries.py` 升级为对象链校验器

### 验收标准

- [x] 通用对象链不依赖 task004 命名硬编码
- [x] verifier 能检查对象链是否完整
- [x] 能检测 controller overreach / missing worker objects

---

## Phase 3: 通用 Loop Engine 最小骨架

### 目标

提供一个不依赖 task004 的运行骨架。

### 工作内容

- [x] 实现 `generic loop runner`
- [x] 支持以下标准阶段：
  - `skill_change_request`
  - `skill_execution`
  - `effectiveness_assessment`
  - `cognition_diagnosis`
  - `loop_routing_decision`
- [x] 将当前 state machine 中与 task-specific 无关的逻辑抽出去
- [x] 定义统一 workdir 结构

### 验收标准

- [x] loop runner 不直接引用 `task004` 字符串
- [x] loop runner 只通过 adapter 访问 task-specific 信息
- [x] 运行结束后能得到完整对象链和 review

---

## Phase 4: Task Adapter Contract 实现与 task004 首次接入

### 目标

将 task004 从一堆专用脚本，收敛为第一个 adapter 实例。

### 工作内容

- [x] 定义 task adapter 所需字段
- [x] 实现 task004 adapter
- [x] 将 task004 的 baseline/candidate/evaluator/search envelope 绑定收敛进 adapter
- [x] 让通用 loop engine 通过 adapter 跑通 task004

### 验收标准

- [x] task004 接入不需要重写 loop engine
- [x] task004 的特殊性只体现在 adapter
- [x] task004 原有 task-specific loop 脚本可逐步降级为历史实验脚本

---

## Phase 5: Generic Diagnosis Layer

### 目标

把当前 scattered 的“解释问题归属”收敛成通用 diagnosis 组件。

### 工作内容

- [x] 定义 diagnosis 输入对象
- [x] 定义 diagnosis 输出类别：
  - `framework_problem`
  - `task_adapter_problem`
  - `skill_use_problem`
  - `skill_structure_problem`
  - `evaluator_design_problem`
- [x] 给出 next-action routing
- [x] 用 task004 当前已有证据做 first diagnosis run

### 验收标准

- [x] diagnosis 不再只是 narrative，总能落到下一步路由
- [x] 能明确说“先修 task/evaluator，不要继续 skill evolution”
- [x] task004 的当前问题能被 diagnosis 正确归类

---

## Phase 6: 集成测试与对照验证

### 目标

证明这不是“换了名字的 task004 patch”，而是可迁移框架。

### 工作内容

- [x] 跑 task004 通用 loop engine 集成测试
- [x] 跑对象链完整性测试
- [x] 跑 controller overreach 检测
- [x] 选一个非 task004 的轻量任务做 adapter feasibility smoke test

### 验收标准

- [x] task004 跑通
- [x] worker object chain 完整
- [x] controller 不下场
- [x] 另一个 task 能以 adapter 形式接入 smoke path

## 7. 当前优先级建议

当前建议优先顺序：

1. `Phase 1`
2. `Phase 2`
3. `Phase 3`
4. `Phase 4`
5. `Phase 5`
6. `Phase 6`

原因：

- 先固定抽象，再固化对象链
- 先把 controller 从认知判断中剥离出来
- 再把 task004 迁到通用引擎上
- 最后才谈跨 task 验证

## 8. 风险提示

### 8.1 风险一：抽象过早过重

若把 adapter / engine / diagnosis 一次抽得太复杂，可能重新落入“流程很完整，但没跑通”的陷阱。

控制原则：

- 每层都先做 MVP
- 只服务当前已暴露的问题

### 8.2 风险二：task004 特殊性泄漏回引擎

如果实现时把 task004 的边界扫描逻辑硬编码进 generic engine，那么这次结构性推进就失败了。

控制原则：

- 引擎不碰 task-specific 语义
- task-specific 信息必须来自 adapter

### 8.3 风险三：diagnosis 又被 controller 偷取

如果 diagnosis layer 还是脚本里 if/else 写死，那只是换了名字，没有解决问题。

控制原则：

- diagnosis 输出必须落对象
- controller 只能引用 diagnosis 对象，不直接生成 diagnosis

## 9. 阶段成功标准

本计划的成功，不是“task004 表现更好”，而是：

1. loop engine 成为通用层
2. task adapter 成为 task-specific 薄层
3. diagnosis 能决定 loop 的下一步方向
4. controller 不再下场
5. 后续 task005/006 接入时，改的是 adapter，不是重写框架
