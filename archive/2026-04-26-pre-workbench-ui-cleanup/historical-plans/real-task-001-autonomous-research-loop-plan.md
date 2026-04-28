# real-task-001 计划：真实科研任务多轮自主研究闭环验证

## 1. 计划定位

本计划把当前工作重心从“fixture-level 框架验证”切换到“真实科研任务多轮闭环验证”。

前一阶段已经证明：

- 通用 onboarding/readiness 可以运行。
- 通用 `skill -> effectiveness -> cognition -> routing` 闭环可以运行。
- 多 task × 多 Pi runtime fixture 矩阵可以通过。
- runtime 切换已回到 registry/config 驱动，而不是 task/model 特化补丁。

但这还不足以证明 DaoShuGuo 能支撑真实自主科研。

本计划要验证的是：

> 在一个真实电力科研任务上，系统是否能经过多轮 agentic skill-effectiveness-cognition-delivery 闭环，产生可证据支持的技能提升、认知提升和成效改进。

## 2. 任务选择

### 2.1 选择对象

`real-task-001` 选择基于现有 `task004`：

> 新能源接入下的 IEEE69 静态承载力评估。

任务引用：

- `task.power.ieee69_hosting_capacity`
- task package: `tasks/task004/`
- adapter: `adapters/task004.yaml`
- evaluator: `evaluators/task004_evaluator.yaml`
- runtime/evaluator implementation: `orchestrator/main.py real-run-task004`

### 2.2 为什么选择 task004

选择 task004 的原因：

1. 它不是纯 fixture，已有真实运行、真实 evaluator、真实报告和真实边界风险。
2. 它涉及承载力边界判断，比单点优化更接近科研问题。
3. 它天然要求 claim control，能测试“成效”和“品味”层。
4. 它已经暴露过 `boundary overclaim`、`skill mismatch`、`task mismatch` 等科研真实失败形态。
5. 它已有多轮运行基础，适合观察迭代是否真正改进。

已有基础包括：

- `runs/task004/run_0001` 到后续 run。
- `analysis/task004/boundary_overclaim_*`
- `analysis/task004/mismatch_*`
- `analysis/task004/semantic_*`
- `analysis/task004/literature_*`
- `analysis/task004/upgrade_*`
- `effectiveness/task004/*`

## 3. 核心问题

本计划不再问：

> 框架是否能跑通？

而要问：

1. Agent 是否能基于上一轮结果提出更好的技能改变。
2. evaluator 是否能诚实识别改进、无效、退化和伪进步。
3. cognition worker 是否能把结果解释为 skill-use、skill-structure、evaluator 或 task 问题。
4. 下一轮技能变化是否真的来自 cognition，而不是 controller 下场或随机调参。
5. 多轮后是否出现可证据支持的成效改进。
6. 多轮后是否形成更清晰、更可复用、更有边界意识的科研认知。
7. 最终成果是否能进入 internal report、paper candidate 或 stop/pause 的合理路由。

## 4. 非目标

本计划暂不追求：

1. 多模型语义差异大规模研究。
2. 完整时序 hosting capacity。
3. 概率承载力或大规模场景集。
4. 复杂 OPF 或多目标经济优化。
5. 自动生成论文或专利。
6. 通过扩大搜索空间制造局部指标提升。
7. 为 task004 写一套不可复用的专用框架。

## 5. 成功判据

### 5.1 最低成功

满足以下条件，视为真实任务闭环最低成功：

1. 至少完成 3 轮闭环。
2. 每轮都有完整 artifact chain：
   - `skill_change_request`
   - `skill_change_result`
   - `effectiveness_assessment`
   - `cognition_diagnosis`
   - `cognition_to_skill_update`
   - `loop_routing_decision`
   - `loop_review`
   - `run_record`
3. 每轮都绑定真实 task004 run 或明确说明没有运行的阻断原因。
4. 每轮都区分 skill-use improvement 与 skill-structure improvement。
5. 最终形成一个 `real_task_research_report`，说明技能、认知、成效和成果路由。

### 5.2 较好成功

在最低成功基础上，还满足：

1. 至少一轮出现真实成效改进。
2. 至少一轮认知明确阻止伪进步或过度 claim。
3. 至少一个技能变化从参数/边界使用改善上升到方法、流程或标准层面的结构问题。
4. 最终 claim 比初始 claim 更准确、更窄、更可信。

### 5.3 高质量成功

在较好成功基础上，还满足：

1. 形成可复用的 hosting-capacity skill card。
2. 形成稳定 cognition card，明确承载力边界、控制策略条件和 overclaim 风险。
3. 形成可复用 evaluator 改进建议或 evaluator 结构升级。
4. 能说明这条研究线下一步如何从 internal report 走向 paper candidate。

## 6. 禁止事项

后续执行不得出现以下行为：

1. controller 直接写 cognition diagnosis。
2. controller 直接决定 skill 怎么改。
3. 只调参数就声称技能结构提升。
4. 只提高指标但不记录代价、边界和 evaluator 条件。
5. 因为结果不好而降低 evaluator 标准。
6. 为 task004 加不可迁移的 framework special-case。
7. 用漂亮报告掩盖研究质量不足。
8. 把 artifact-chain passed 当成真实科研成功。

## 7. 运行架构

### 7.1 入口原则

优先使用既有统一入口：

```bash
python scripts/run_generic_loop_engine.py \
  --task-adapter adapters/task004.yaml \
  --backend pi_gpt55 \
  --run-intent real_task_001
```

若现有 generic loop 对真实多轮 task004 支持不足，应修复通用 loop/protocol，而不是写 task004-only runner。

允许薄 task adapter 描述：

- task binding
- evaluator binding
- baseline binding
- runtime binding
- metrics mapping
- known risks
- claim boundary

不允许 adapter 重写 loop engine、review gate、learning chain 或 portfolio 逻辑。

### 7.2 Runtime 策略

主 runtime：

- `pi_gpt55`

备选 runtime：

- `pi_baidu_glm5`

确定性基线：

- `deterministic`

本计划不扩大多 runtime 矩阵。备选 runtime 只用于主 runtime 异常或关键判断复核。

### 7.3 Worker 边界

`skill_worker` 负责：

- 读取上一轮 cognition_to_skill_update。
- 生成 skill_change_request。
- 明确改变属于 method/process/standard 哪一类。
- 明确是否只是 skill-use 尝试。

`effectiveness_worker` 负责：

- 运行或读取 task004 evaluator。
- 比较 baseline/candidate。
- 记录 hosting capacity、violation trigger、loss、voltage margin 等指标。
- 识别指标改进是否来自参数、边界、代价或标准变化。

`cognition_worker` 负责：

- 判断问题类型。
- 解释 skill-use 与 skill-structure。
- 控制 boundary overclaim。
- 给下一轮提出可验证问题。

`delivery_worker` 负责：

- 形成成果等级判断。
- 审核 claim。
- 路由 internal report / paper candidate / pause。

`controller` 只负责：

- 调度。
- 写对象。
- 校验契约。
- 绑定证据。
- 根据 worker 输出路由。

## 8. 三轮闭环设计

### Round 0: Readiness And Baseline Freeze

目标：

- 冻结 task004 当前状态。
- 明确 baseline、candidate、evaluator、claim boundary。
- 不做技能改动。

输入：

- `tasks/task004/task.yaml`
- `adapters/task004.yaml`
- `evaluators/task004_evaluator.yaml`
- 最新 `runs/task004/run_*`
- `effectiveness/task004/*`

输出：

- `analysis/real_task_001/readiness/task_readiness_report.yaml`
- `analysis/real_task_001/baseline_state.yaml`
- `analysis/real_task_001/claim_boundary.yaml`

检查点：

- 如果 evaluator 不足，先进入 evaluator repair，不进入 skill evolution。
- 如果 task adapter 不完整，先 repair adapter。

### Round 1: Reproduce Existing Boundary Skill

目标：

- 用 agentic worker 复现当前 task004 hosting capacity run。
- 确认系统能把真实运行纳入 artifact chain。

建议 skill change：

- 不改算法结构，只做受控调用。
- 明确这是 `skill-use baseline reproduction`。

输出：

- Round 1 worker chain。
- 真实 task004 run ref。
- effectiveness assessment。
- cognition diagnosis。

预期认知：

- 如果 candidate 与 baseline 持平，不能声称技能提升。
- 若改进只来自参数/包络，标记为 skill-use improvement。
- 必须记录 boundary condition。

### Round 2: Cognition-Guided Skill Change

目标：

- 让 cognition_to_skill_update 驱动下一轮 skill change。
- 尝试把 Round 1 的观察转化为结构性问题。

候选方向：

1. Method：从单一策略扫描变成策略族比较。
2. Process：增加边界扫描停止条件、违反触发分类、边界邻域复查。
3. Standard：增加 overclaim gate、boundary stability check 或 scan envelope sufficiency check。

优先级：

1. 先改 process/standard。
2. 再考虑 method。
3. 不优先扩大搜索空间。

输出：

- Round 2 worker chain。
- 新 run。
- 新 evaluator result。
- skill-use vs skill-structure 判断。

检查点：

- 如果指标改善但 claim 更弱，这是可能合理的科研进步。
- 如果指标不改善但 overclaim 控制更强，也可能是认知/标准进步。

### Round 3: Effectiveness And Delivery Upgrade

目标：

- 判断多轮后是否形成可交付成果。
- 不只看 hosting_capacity_level，也看 claim quality 和 boundary confidence。

输出：

- `effectiveness_summary.yaml`
- `cognition_upgrade.yaml`
- `delivery_readiness.yaml`
- `real_task_research_report.md`

必须回答：

1. 技能是否真的进步。
2. 认知是否真的进步。
3. 成效是否真的进步。
4. 结果属于拓玉、琢石、雕木还是绘墨。
5. 当前适合 internal report、paper candidate、patent candidate 还是 pause。

## 9. 可选 Round 4: Ablation

触发条件：

- Round 2 或 Round 3 声称 cognition-guided skill change 带来改进。

最低 ablation：

1. 同 evaluator 下比较旧 skill 和新 skill。
2. 比较 cognition-guided request 与 metric-only request。
3. 固定搜索预算。
4. 分离搜索空间扩张与认知约束效果。

没有 ablation，不得声称：

- cognition caused skill improvement
- agent autonomously discovered superior principle
- research taste improved the method

## 10. 产物目录

建议目录：

```text
analysis/real_task_001/
  readiness/
  rounds/
    round_000/
    round_001/
    round_002/
    round_003/
  reports/
  delivery/
  reviews/
```

每轮至少包含：

```text
skill_change_request.yaml
skill_change_result.yaml
effectiveness_assessment.yaml
cognition_diagnosis.yaml
cognition_to_skill_update.yaml
loop_routing_decision.yaml
loop_review.yaml
run_record.yaml
artifact_index.json
```

## 11. 验证命令

计划执行后至少运行：

```bash
python -m py_compile \
  scripts/run_generic_loop_engine.py \
  scripts/llm_full_loop_workers.py \
  scripts/verify_generic_full_loop.py \
  scripts/validate_schemas.py

python scripts/run_task_onboarding_check.py --task task004

python scripts/validate_schemas.py --artifacts generic-task-onboarding

python scripts/validate_schemas.py --artifacts generic-full-loop-validation
```

若新增 real-task artifact set，则增加：

```bash
python scripts/validate_schemas.py --artifacts real-task-001
```

若执行真实 task004 run，则至少运行：

```bash
python orchestrator/main.py real-run-task004 --strategy inverter-support
python orchestrator/main.py real-run-task004 --strategy single-point-mismatch
```

## 12. Review Gate

每轮 review 必须给出以下 verdict 之一：

- `approved`
- `real_progress`
- `needs_fix`
- `stagnation`
- `cheating_suspected`
- `insufficient_evidence`
- `pause_for_human_review`

`real_progress` 只允许进入 bounded next iteration。

如果出现以下情况，必须停下而不是继续循环：

1. evaluator 无法支持 claim。
2. 连续两轮只做参数变化且无结构问题沉淀。
3. 成效改善来自降低标准。
4. artifact chain 不完整。
5. worker 输出和 evidence 明显不一致。

## 13. 最终报告结构

最终 `real_task_research_report.md` 必须包含：

1. 任务定义和边界。
2. Baseline 与 evaluator。
3. 每轮 skill change。
4. 每轮 effectiveness result。
5. 每轮 cognition diagnosis。
6. skill-use vs skill-structure 汇总。
7. 成效是否改进。
8. 认知是否升级。
9. 成果等级和 claim 上限。
10. 失败、边界和下一步。

## 14. 执行顺序

1. 建立 `analysis/real_task_001/` artifact set 和验证入口。
2. 运行 Round 0 readiness/baseline freeze。
3. 运行 Round 1 reproduction。
4. 运行 Round 2 cognition-guided change。
5. 运行 Round 3 delivery/readiness。
6. 如出现强改进 claim，运行 Round 4 ablation。
7. 更新实验记录。
8. 运行验证。
9. 形成最终综合判断。

## 15. 当前计划结论

本计划是 DaoShuGuo 从“框架工程验证”进入“真实科研闭环验证”的第一步。

若该计划成功，项目可以合理声称：

> DaoShuGuo 已经能在一个真实电力科研小任务上运行多轮自主研究闭环，并形成证据约束下的技能、认知和成效资产。

若该计划失败，失败也必须被记录为有效认知：

- 是 skill worker 不会提出有价值改变。
- 是 evaluator 不足以支持研究判断。
- 是 cognition worker 无法形成有效诊断。
- 是 delivery gate 无法区分成果等级。
- 还是真实任务本身不适合当前框架。
