# task001 真实任务接入计划

## 1. 计划目标

本计划用于将当前 `task001` 从 demo 骨架升级为真实可执行的电力科研最小闭环。

当前仓库已经具备：

- 项目总纲与方法论文档
- 完整的 schema/spec
- 最小校验器
- demo evaluator
- demo orchestrator
- skills/cognition registry 写回

本计划的目标不是立刻产出高水平科研成果，而是完成 **第一轮真实 task 接入**，使系统在真实电力问题上形成可信、可复盘、可积累的闭环。

## 2. 任务定义

### 2.1 研究对象

IEEE 33 节点配电网无功优化问题。

### 2.2 当前假设

本计划默认采用以下路线：

- 仿真环境：`pandapower`
- 问题范围：单网络、单工况
- 比较方式：一个 baseline、一个 candidate
- 评价指标：
  - 网损 `loss`
  - 电压偏差 `voltage_deviation`
  - 约束违反数 `constraint_violation`

### 2.3 非目标

本阶段不追求：

- 多工况大规模实验
- 复杂多智能体协同求解
- 论文级算法创新
- 大规模知识图谱推理
- 全任务泛化平台化

## 3. 成功标准

以下条件同时满足，视为本计划执行成功：

1. `task001` 可在真实仿真环境中运行，不再依赖 demo 指标硬编码。
2. baseline 与 candidate 都能通过统一 evaluator 输出结构化指标。
3. orchestrator 能产出真实 `run / taste_assessment / evidence_bundle / report`。
4. orchestrator 能继续写回 `skills/registry.json` 与 `cognition/registry.json`。
5. 至少完成一次真实成功运行或一次高质量真实失败运行。
6. 失败情况下仍能形成负向认知与诚实分级，而不是空报告。

## 4. 验收标准

### 4.1 最低功能验收

- [x] `task001_evaluator.py` 不再使用 demo 指标返回，而是真实运行仿真并计算指标
- [x] `baseline_solver.py` 能输出真实 baseline 解
- [x] `reactive_optimizer.py` 能输出真实 candidate 解
- [x] `orchestrator/main.py demo-run` 被真实运行入口替代或包裹
- [x] 运行目录内的 `metrics.json` 来自真实计算
- [ ] 运行目录仍包含：
  - [x] `run.yaml`
  - [x] `taste_assessment.yaml`
  - [x] `evidence_bundle.yaml`
  - [x] `report.yaml`
  - [x] `agent_trace.yaml`
  - [x] `prompt_observation.yaml`
  - [x] `writeback.json`

### 4.2 最低质量验收

- [x] 报告仍然受 `taste_assessment` 约束
- [x] `run.yaml` 只记录事实，不写高层认知
- [x] `cognition` 必须带证据和边界
- [x] 真实运行后 registry 写回仍可追踪最近使用和最近产出
- [x] `python scripts/validate_schemas.py` 通过
- [x] 至少一个真实 run 能完整生成结构化产物

### 4.3 失败也算通过的条件

若 candidate 未优于 baseline，只要满足以下条件，仍算本计划成功完成：

- [x] evaluator 真正运行了真实仿真
- [x] 失败原因被记录
- [x] 失败认知被写回
- [x] 成果等级被诚实压到 `huimo` 或其他合理等级
- [x] 未发生“把失败包装成成果”的情况

## 5. 关键设计原则

### 5.1 不换架构，先换执行内容

优先保留当前对象层、registry、taste gate、evidence bundle 和 orchestrator 骨架。

本计划主要替换：

- evaluator 的执行内容
- baseline/candidate skill 的执行内容
- metrics 的来源

### 5.2 先单工况，再扩展

第一轮只做：

- 单网络
- 单工况
- 单 baseline
- 单 candidate

### 5.3 evaluator 必须独立

不允许 solver 自己证明自己好。

真实 task 接入后，所有 skill 输出必须经过统一 evaluator 验证。

### 5.4 报告必须继续服从品味约束

接入真实数据后，必须继续防止：

- 证据不足却拔高结论
- 局部现象被包装成规律
- 失败结果被写成“阶段性成功”

## 6. 实施步骤

## Phase 1: 真实任务包收束

目标：把 `task001` 从 demo 描述收束为真实仿真任务定义。

涉及文件：

- [task.md](/home/chenying/root-research/DaoShuGuo-v1/tasks/task001/task.md)
- [task.yaml](/home/chenying/root-research/DaoShuGuo-v1/tasks/task001/task.yaml)
- [constraints.yaml](/home/chenying/root-research/DaoShuGuo-v1/tasks/task001/constraints.yaml)
- [baseline.yaml](/home/chenying/root-research/DaoShuGuo-v1/tasks/task001/baseline.yaml)
- [targets.yaml](/home/chenying/root-research/DaoShuGuo-v1/tasks/task001/targets.yaml)

执行内容：

- [x] 明确真实网络模型来源与加载方式
- [x] 明确单工况的输入参数
- [x] 明确 baseline 的真实定义
- [x] 将 `metric_expectations` 从 demo 常量改为可运行比较对象说明
- [x] 明确 candidate skill 的可操作范围

完成判据：

- [x] 任务包可独立说明真实运行所需输入
- [x] 不再依赖“只是 demo”作为主要语义

## Phase 2: baseline 接入真实执行

目标：让 baseline 从占位返回值变成真实可运行求解。

涉及文件：

- [baseline_solver.py](/home/chenying/root-research/DaoShuGuo-v1/skills/validated/baseline_solver.py)
- [baseline.sample.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/samples/baseline.sample.yaml)
- [skill.baseline.sample.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/samples/skill.baseline.sample.yaml)

执行内容：

- [x] 接入 `pandapower` 网络加载
- [x] 实现 baseline 解法
- [x] 输出真实 baseline 指标所需结构
- [x] 对 baseline 技能的输入输出契约进行必要修正

完成判据：

- [x] baseline solver 可在本地运行
- [x] baseline 结果可被 evaluator 读取

## Phase 3: candidate skill 接入真实执行

目标：让 candidate 从 demo 假值返回变成真实候选方法。

涉及文件：

- [reactive_optimizer.py](/home/chenying/root-research/DaoShuGuo-v1/skills/validated/reactive_optimizer.py)
- [reactive_optimizer_candidate.py](/home/chenying/root-research/DaoShuGuo-v1/skills/active_dev/reactive_optimizer_candidate.py)
- [skill.sample.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/samples/skill.sample.yaml)
- [skill.candidate.sample.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/samples/skill.candidate.sample.yaml)

执行内容：

- [x] 选择第一版 candidate 方案
- [x] 接入真实求解逻辑
- [x] 输出与 evaluator 兼容的候选结果格式
- [x] 保留 candidate 与 validated skill 的边界

完成判据：

- [x] candidate 可真实运行
- [x] candidate 输出可与 baseline 对比

## Phase 4: evaluator 真实化

目标：用统一 evaluator 替换 demo 指标函数。

涉及文件：

- [task001_evaluator.py](/home/chenying/root-research/DaoShuGuo-v1/evaluators/task001_evaluator.py)
- [task001_evaluator.yaml](/home/chenying/root-research/DaoShuGuo-v1/evaluators/task001_evaluator.yaml)

执行内容：

- [x] 加载网络和工况
- [x] 应用 baseline/candidate 解
- [x] 运行真实潮流或等价仿真
- [x] 计算 `loss / voltage_deviation / constraint_violation`
- [x] 输出统一结构化比较结果

完成判据：

- [x] evaluator 不再依赖 `demo_candidate_metrics`
- [x] evaluator 可单独运行并输出结构化结果

## Phase 5: orchestrator 接入真实 task

目标：保持现有闭环结构不变，把 demo execution 换成真实 execution。

涉及文件：

- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)
- [README.md](/home/chenying/root-research/DaoShuGuo-v1/README.md)

执行内容：

- [x] 新增真实运行入口，例如 `real-run`
- [x] 保留现有 schema 校验步骤
- [x] 让 orchestrator 调 baseline 和 candidate skill
- [x] 让 orchestrator 读取 evaluator 输出生成运行产物
- [x] 保持 writeback 逻辑不回退

完成判据：

- [x] 能生成一次真实 `run_XXXX`
- [x] writeback 仍然生效

## Phase 6: 真实运行验证

目标：完成第一轮真实 task 验证。

涉及文件：

- [runs/task001](/home/chenying/root-research/DaoShuGuo-v1/runs/task001)
- [skills/registry.json](/home/chenying/root-research/DaoShuGuo-v1/skills/registry.json)
- [cognition/registry.json](/home/chenying/root-research/DaoShuGuo-v1/cognition/registry.json)

执行内容：

- [x] 跑至少一次 baseline vs candidate 真实比较
- [x] 检查 `run.yaml` 是否只保留事实
- [x] 检查 `taste_assessment` 是否合理
- [x] 检查 `report` 是否越权拔高
- [x] 检查 registry 是否真实写回

完成判据：

- [x] 至少一个真实运行目录完整生成
- [x] 若失败，也能形成失败认知与诚实报告

## 7. 风险与缓解

### 风险 1：pandapower 环境或数据模型接入复杂

缓解：

- 第一轮只做一个最小网络载入和单工况
- 不同时做多时段和复杂控制变量

### 风险 2：candidate 方案一开始就跑不通

缓解：

- 先保证 baseline 跑通
- candidate 先用最简单的真实可运行方案

### 风险 3：真实运行后报告开始拔高

缓解：

- 强制保留 `taste_assessment -> report` 约束链
- 明确失败也算有效结果

### 风险 4：写回逻辑因真实对象变复杂而退化

缓解：

- 本轮不改 schema 边界
- 继续使用现有 registry 与 cognition asset 写回模式

## 8. 验证步骤

在本计划实施过程中，至少要运行以下验证：

1. `python scripts/validate_schemas.py`
2. `python orchestrator/main.py validate`
3. baseline solver 单独运行验证
4. candidate solver 单独运行验证
5. evaluator 单独运行验证
6. orchestrator 真实运行验证

## 9. 预期产物

计划完成后，预期应新增或更新：

- 真实化后的 `task001` 任务包
- 真实化后的 baseline/candidate skill
- 真实化后的 evaluator
- 至少一个真实运行目录
- 写回后的 skills/cognition registry
- 一份受品味约束的真实 report

## 10. 计划清单

- [x] 收束真实任务包
- [x] 接入真实 baseline
- [x] 接入真实 candidate
- [x] evaluator 真实化
- [x] orchestrator 增加真实运行入口
- [x] 跑第一次真实闭环
- [x] 检查 writeback 与 report 质量

## 11. 结论

这个计划的核心不是追求“做大”，而是把当前已经搭好的方法论和对象架构，第一次稳定地压到真实电力任务上。

只要完成第一轮真实闭环，不论结果是正是负，项目都会从“高质量设计阶段”进入“真实研究系统阶段”。
