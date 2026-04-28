# task004-on-Pi 计划：承载力边界任务的 Pi 迁移与三层验证

## 1. 计划定位

`task004` 不只是下一个要迁移到 Pi 的任务，它还是当前最适合检验 DaoShuGuo 三层目标的任务：

- `技能`
- `认知`
- `成果`

原因很明确：

- `task003` 更偏向方法路径比较
- `task004` 更偏向边界判断
- 边界判断天然更接近：
  - claim discipline
  - paper readiness
  - internal report vs paper candidate 的区分

因此，本计划的目标不是简单把 `task004` 搬到 Pi 上，而是：

> 用 `task004` 检验 Pi-based DaoShuGuo 是否更适合支撑“认知”和“成果”层的真实达成。

## 2. 当前基础

当前仓库中，`task004` 已有基础明显好于很多其它任务。

### 2.1 真实运行基础

已有真实运行：

- `runs/task004/run_0001`
- `runs/task004/run_0002`

其中已经覆盖：

- success path
- skill mismatch path

### 2.2 边界与认知基础

已有对象：

- `analysis/task004/boundary_overclaim_*`
- `analysis/task004/compare_*`
- `analysis/task004/semantic_*`
- `analysis/task004/upgrade_*`
- `analysis/task004/literature_*`
- `analysis/task004/explanations_*`

### 2.3 成效基础

已有：

- `effectiveness/task004/validation_plan.yaml`
- `effectiveness/task004/experiment_matrix.yaml`
- `effectiveness/task004/application_assessment.yaml`
- `effectiveness/task004/deliverable_package.yaml`
- `effectiveness/task004/claim_routing.yaml`

这意味着 `task004` 已经不仅有 run 和 compare，还有：

- readiness judgment
- application boundary
- deliverable routing

## 3. task004 为什么更适合检验认知与成果层

`task004` 当前最有价值的地方，在于它能逼出真正的“研究判断”，而不只是“结果对比”。

它天然回答这些问题：

1. `hosting capacity` 是不是边界问题
2. 单点运行结果能不能替代边界扫描
3. 控制策略影响的是“系统固有承载力”，还是“条件化边界”
4. 什么时候会发生 `boundary overclaim`
5. 为什么有些工作现在只配 internal report，不配 paper candidate

这些问题正好对应 DaoShuGuo 最初设计里最难的两层：

- 认知是否深刻
- 成果是否成熟

## 4. 计划目标

本计划分三层目标。

### 4.1 技能层目标

让 Pi 能稳定驱动 `task004` 的真实 trial：

- success path
- skill mismatch path

并能结构化记录：

- boundary result
- mismatch evidence

### 4.2 认知层目标

让 Pi loop 能把已有的 task004 关键认知重新带入 runtime：

- 单点运行结果不能替代边界扫描
- 承载力结论必须绑定当前扫描包络和控制策略
- boundary overclaim 必须进入 loop 约束

### 4.3 成果层目标

让 Pi loop 能支撑一条更清楚的成效判断链：

- 为什么现在只是 `internal_report_ready`
- 哪些缺失使其还不是 `paper_candidate`
- 哪些验证补齐后才可能升级

## 5. 核心原则

### 5.1 task004 不追求更复杂 solver，先追求更真实的边界治理

本阶段不优先做：

- 更复杂 hosting capacity algorithm
- 多年时序承载力评估
- 大规模概率承载力

本阶段优先做：

- 边界类结果的稳定执行
- 边界类认知的稳定记录
- 成果 readiness 的稳定表达

### 5.2 Pi 继续做 harness，Python 继续做 domain runtime

Pi 负责：

- task init
- trial trigger
- skill trial record
- cognition constraint record
- iteration review
- deliverable/claim boundary record

Python 继续负责：

- `run_real_task004`
- evaluator
- existing report/taste/evidence generation

### 5.3 task004 loop 必须把 boundary overclaim 纳入主线，而不是附属检查

这和 task003 不同。

在 `task004` 中，`boundary overclaim` 不是附带问题，而是任务本体的一部分。

## 6. 建议新增 Pi 工具

在已有 package 基础上，建议新增以下工具。

### 6.1 `run_task004_trial`

作用：

- 触发 `orchestrator/main.py real-run-task004`

参数：

- `strategy`
  - `inverter-support`
  - `single-point-mismatch`
- `repo_root`
- `task_ref`

返回：

- `runDir`
- `runRef`
- `reportRef`
- `exitCode`
- `stdout/stderr`

### 6.2 `record_boundary_judgment`

作用：

- 将边界结论写入 `research_loop.jsonl` 和 `research_loop.md`

参数：

- `task_ref`
- `run_ref`
- `boundary_statement`
- `claim_ceiling`
- `boundary_type`

### 6.3 `record_effectiveness_status`

作用：

- 将 task004 的 readiness 结论写入 loop runtime

参数：

- `task_ref`
- `readiness_level`
- `supported_output`
- `missing_for_next_level`

## 7. task004 Pi loop 的最小链条

建议最小完整链条如下：

1. `init_research_task`
2. `run_task004_trial (success path)`
3. `record_skill_trial`
4. `record_boundary_judgment`
5. `record_cognition_constraint`
6. `record_effectiveness_status`
7. `record_iteration_review`

然后再补：

8. `run_task004_trial (single-point-mismatch)`
9. `record_skill_trial`
10. `record_boundary_judgment`
11. `record_iteration_review`

## 8. 阶段划分

---

## Phase 1: task004 Pi Bridge

### 目标

把 `task004` 接到 Pi package。

### 工作内容

- [x] 在 Pi package 中新增 `run_task004_trial`
- [x] 解析 `runDir/runRef/reportRef`
- [x] 新增 `verify_pi_task004_bridge.py`
- [x] 做一次 success path 真实桥接

### 验收标准

- [x] Pi tool 可真实触发 `task004` 运行
- [x] 可得到结构化返回

---

## Phase 2: task004 Stable Vertical Slice

### 目标

完成 `task004` 的第一条 Pi step-based stable loop。

### 工作内容

- [x] 新建 `run_pi_task004_loop.py`
- [x] 采用和 task003 相同的 step-based runner 思路
- [x] 新增 `scripts/verify_pi_task004_state_loop.py`
- [x] 在全新 workdir 上以 `baidu-anthropic/glm-5` 跑通最小真实链路

### 当前验收结论

- [x] `init_step -> task_trial_step -> boundary_judgment_step -> effectiveness_status_step -> iteration_review_step` 已在 `analysis/pi_harness/pi_json_loop_task004_baidu_glm5` 真实完成
- [x] 真实 task 运行已触发并生成 `runs/task004/run_0005`
- [x] 状态环校验通过：`python scripts/verify_pi_task004_state_loop.py`

### 当前事实说明

当前 task004-on-Pi 不再只是 `openai/gpt-5.4` 路线上的实验。

已经确认：

- `baidu-anthropic` provider 可被 Pi 正确加载
- `glm-5` 可稳定完成 task004 的最小 step-based loop
- 这条链路能真实触发 domain runtime，并把边界判断与成效判断写回 durable loop

本轮关键产物：

- `analysis/pi_harness/pi_json_loop_task004_baidu_glm5/state/research_state.json`
- `analysis/pi_harness/pi_json_loop_task004_baidu_glm5/research_loop.jsonl`
- `runs/task004/run_0005/run.yaml`

本轮 task004 的研究含义不是“得到更优 candidate”，而是：

- 获得一个真实 failure-boundary 样本
- 证明 Pi + LLM provider 可以驱动 task004 的边界与成效记录
- 证明 task004 适合作为 `认知 + 成果` 层的测试任务
- [ ] 先跑 success path
- [ ] 写出：
  - `research_loop.md`
  - `research_loop.jsonl`
  - `research_state.json`
  - `state/requests/*.json`
  - `state/results/*.json`

### 验收标准

- [ ] task004 一条完整 step-based stable loop 成立

---

## Phase 3: Boundary Cognition Integration

### 目标

把 task004 已有边界认知真正写进 Pi loop 主线。

### 工作内容

- [ ] 新增 `record_boundary_judgment`
- [ ] 将 `boundary_overclaim` 结论写入 loop
- [ ] 将 `claim_adjustment` 写入 loop
- [ ] 让 loop 明确记录：
  - single-point 不能替代 boundary scan
  - 当前结论只绑定扫描包络与控制策略

### 验收标准

- [ ] task004 Pi loop 已显式吸收 boundary cognition

---

## Phase 4: Effectiveness Layer Integration

### 目标

把 task004 的成果层显式引入 Pi loop。

### 工作内容

- [ ] 新增 `record_effectiveness_status`
- [ ] 读取并记录：
  - `deliverable_package`
  - `claim_routing`
  - `validation_plan`
- [ ] 在 loop 中显式写出：
  - 当前只到 `internal_report_ready`
  - 为什么不是 `paper_candidate`

### 验收标准

- [ ] Pi loop 中已真实出现成果 readiness 判断

---

## Phase 5: task004 对照路径

### 目标

让 `task004` 形成一条更像研究判断的对照链。

### 工作内容

- [ ] 跑 success path: `inverter-support`
- [ ] 跑 mismatch path: `single-point-mismatch`
- [ ] 输出 comparison review
- [ ] 判断：
  - success path 是边界提升还是局部条件化边界
  - mismatch path 为什么不构成有效承载力结论

### 验收标准

- [ ] task004 形成 success vs mismatch 的 Pi-based comparison

---

## Phase 6: 三层评估

### 目标

专门回答 `task004` 是否比 `task003` 更能支撑：

- 技能
- 认知
- 成果

### 工作内容

- [ ] 评估 skill layer 是否更成熟
- [ ] 评估 cognition layer 是否更深刻
- [ ] 评估 effectiveness layer 是否更接近实际科研交付
- [ ] 与 task003 做对照

### 验收标准

- [ ] 形成一份明确结论：task004 是否更能支撑高层科研目标

## 9. 风险

### 风险 1：task004 仍然只是“多跑几次边界”

缓解：

- 必须引入 `boundary_judgment`
- 必须引入 `effectiveness_status`

### 风险 2：成果层仍然停留在 YAML，不进入 loop

缓解：

- 必须把 readiness judgment 写入 loop files

### 风险 3：task004 过早追求复杂承载力算法

缓解：

- 当前只做边界判断与交付判断，不做算法扩张

## 10. 成功标准

本计划成功意味着：

1. task004 在 Pi 上拥有稳定 step-based loop
2. boundary cognition 被真实纳入 loop
3. effectiveness 判断被真实纳入 loop
4. 能够更清楚回答：
   - task004 为什么比 task003 更能支撑认知与成果层
