# Generic Loop Engine Spec

## 1. 文档目的

本规范定义 `generic loop engine` 的职责边界、最小状态机、输入输出契约和对象链要求。

它服务的是可跨 task 复用的闭环运行骨架，而不是某个单任务的专用脚本。

本规范必须同时满足：

- 不把 task-specific 逻辑塞回 loop engine
- 不让 controller 代替 worker 下场
- 为后续 `task004 / task005 / task006` 适配提供统一入口

## 2. 定位

`generic loop engine` 是闭环编排层，不是技能层、成效层或认知层。

它只负责：

- 读取任务 adapter
- 按固定阶段调度 worker
- 绑定阶段输入输出
- 记录运行状态
- 持久化对象引用与证据索引
- 触发 verifier

它不负责：

- 直接生成 skill change 内容
- 直接判定 candidate 是否优于 baseline
- 直接给出 cognition diagnosis
- 直接解释 task-specific 失败机理
- 直接决定某个算法、prompt、参数应该怎么改

## 3. 设计约束

### 3.1 controller 非 authoring

loop engine 作为 controller 必须是 `non-authoring controller`。

允许：

- 生成 run id
- 选择下一阶段
- 组装 worker 输入包
- 写入状态流转记录
- 持久化 worker 产物引用
- 在缺少必需对象时停止流程

禁止：

- 写 `skill_change_request` 的实质变更方案
- 写 `effectiveness_assessment` 的结论正文
- 写 `cognition_diagnosis` 的归因正文
- 用内置 if/else 代替 worker judgment
- 未引用 worker 对象就直接生成 `loop_routing_decision`

### 3.2 task 无关性

loop engine 内不得硬编码：

- `task004`、`task005`、`task006` 等 task 名称
- task-specific evaluator 路径
- task-specific baseline 选择逻辑
- task-specific diagnosis 规则

所有 task-specific 信息都必须经由 adapter 提供。

### 3.3 证据优先

loop engine 对下游的唯一合法控制方式是：

1. 调用 worker
2. 接收 worker 对象
3. 校验对象完整性
4. 基于对象引用路由下一阶段

若对象缺失或证据不足，engine 必须中止或回退，不能自行补写。

## 4. 层间边界

### 4.1 loop engine

负责：

- orchestration
- state machine
- run workspace binding
- artifact registry binding
- verifier hook

不负责：

- task meaning
- evaluator semantics
- diagnosis semantics

### 4.2 task adapter

负责：

- 提供 task definition
- 提供 baseline / candidate / evaluator binding
- 提供 search envelope
- 提供 task-specific diagnosis hook 输入

不负责：

- 重写 loop 状态机
- 直接执行 worker judgment
- 直接替代 diagnosis layer

### 4.3 diagnosis layer

负责：

- 读取已有 worker 证据
- 做结构化归因
- 生成下一轮 worker routing 建议
- 在必要时拒绝继续 loop

不负责：

- 亲自改 skill
- 亲自跑 evaluator
- 亲自定义 task

## 5. 最小输入契约

一次标准运行启动时，loop engine 至少接收以下输入：

- `task_adapter_ref`
- `run_intent`
- `workspace_root`
- `loop_config`
- `verifier_config`

其中：

- `task_adapter_ref` 指向唯一 task adapter 对象
- `run_intent` 表示本轮是 baseline run、candidate run、repair run 还是 review run
- `workspace_root` 表示本轮对象与日志的根目录
- `loop_config` 包含最大轮数、阶段开关、失败上限等运行控制
- `verifier_config` 指定何时执行边界校验和对象链校验

## 6. 最小输出契约

一次标准运行结束后，loop engine 至少输出：

- `run record`
- `phase transition log`
- `artifact index`
- `loop_routing_decision`
- `loop review`

其中：

- `run record` 说明本轮运行处于 `completed`、`blocked`、`failed_experiment` 或 `insufficient_evidence`
- `artifact index` 仅记录对象引用，不替代对象本体
- `loop_routing_decision` 必须引用 diagnosis 与前序 worker 对象
- `loop review` 用于总结本轮是否完整、缺了什么、是否可进入下一轮

## 7. 标准阶段

Phase 1 固定以下最小阶段顺序：

1. `skill_change_request`
2. `skill_execution`
3. `effectiveness_assessment`
4. `cognition_diagnosis`
5. `loop_routing_decision`

可选辅助阶段：

- `preflight_validation`
- `artifact_verification`
- `loop_review`

### 7.1 skill_change_request

输入：

- task adapter 提供的 task package
- 上一轮 diagnosis 或初始化策略
- search envelope

输出：

- `skill_change_request`

要求：

- 由 `skill worker` 产出
- engine 只能传递上下文，不能写变更内容

### 7.2 skill_execution

输入：

- `skill_change_request`
- adapter 提供的 candidate binding
- task execution context

输出：

- `skill_change_result`

要求：

- 记录本轮具体执行了什么
- 若执行失败，也必须形成结构化失败对象

### 7.3 effectiveness_assessment

输入：

- `skill_change_result`
- baseline binding
- evaluator binding

输出：

- `effectiveness_assessment`

要求：

- 由 `effectiveness worker` 产出
- assessment 必须显式说明比较对象、指标结果和证据边界

### 7.4 cognition_diagnosis

输入：

- `skill_change_request`
- `skill_change_result`
- `effectiveness_assessment`
- task-specific diagnosis hook inputs

输出：

- `cognition_diagnosis`

要求：

- 由 `cognition worker` 或 diagnosis layer 产出
- 必须给出问题归属、边界、不确定性和建议交接 worker

### 7.5 loop_routing_decision

输入：

- `cognition_diagnosis`
- 对象链完整性校验结果
- loop policy

输出：

- `loop_routing_decision`

要求：

- 由 controller 产出，但只能基于已有 worker 对象和 policy
- 必须引用上游对象，不能凭 controller 自己判断写结论

## 8. 最小 required artifact chain

一个可声称为“合格 loop round”的轮次，至少要有以下对象：

1. `skill_change_request`
2. `skill_change_result`
3. `effectiveness_assessment`
4. `cognition_diagnosis`
5. `loop_routing_decision`

建议同步要求：

6. `run record`
7. `loop review`

### 8.1 对象链引用要求

- `skill_change_result` 必须引用 `skill_change_request`
- `effectiveness_assessment` 必须引用 `skill_change_result` 和 evaluator/baseline
- `cognition_diagnosis` 必须引用前面三个 worker 对象
- `loop_routing_decision` 必须引用 `cognition_diagnosis`
- `loop review` 必须引用整条对象链

### 8.2 缺失处理

若缺少上述五项中的任一项：

- 不得声称完成完整自主 loop
- engine 应标记 `incomplete_worker_chain`
- engine 应停止写高层结论，只允许写阻塞或失败说明

## 9. 运行状态

loop engine 至少支持以下运行状态：

- `queued`
- `running`
- `blocked`
- `failed_experiment`
- `insufficient_evidence`
- `completed`
- `cancelled`

注意：

- `completed` 只表示本轮运行结束并留下了规定对象，不表示一定得到创新结果
- `insufficient_evidence` 表示对象可能存在，但不足以支持后续 diagnosis 或 claim

## 10. verifier 接口

loop engine 必须预留 verifier hook，用于检查：

1. required artifact chain 是否完整
2. controller 是否跳过 worker 直接写判断
3. `loop_routing_decision` 是否引用合法对象
4. task-specific 信息是否仅来自 adapter
5. 证据链是否能回链到 evaluator 与 baseline

若 verifier 失败，engine 必须：

- 阻止本轮进入“可沉淀”状态
- 输出结构化失败原因
- 不得用报告摘要掩盖对象缺失

## 11. 工作目录建议

一个最小 run workspace 建议至少包含：

```text
<run_root>/
├── run.yaml
├── phase_transitions/
├── artifacts/
│   ├── skill_change_request/
│   ├── skill_change_result/
│   ├── effectiveness_assessment/
│   ├── cognition_diagnosis/
│   └── loop_routing_decision/
├── logs/
└── review/
```

说明：

- engine 只规定目录职责，不规定 task-specific 文件内容
- artifacts 目录按对象类型分层，避免 task-specific 命名侵入框架层

## 12. 对后续实现的约束

后续任何 `generic loop runner` 实现都必须满足：

1. 只通过 adapter 获取 task-specific 信息
2. controller 不生成 worker judgment
3. routing decision 必须引用 diagnosis
4. 缺对象时停止，而不是脑补
5. 不把报告层文本当作事实层对象替代品

若某实现不满足以上要求，它只能被视为：

- `framework debugging experiment`

不能被称为：

- 通用 loop engine
- 合格 skill-cognition-effectiveness 闭环
