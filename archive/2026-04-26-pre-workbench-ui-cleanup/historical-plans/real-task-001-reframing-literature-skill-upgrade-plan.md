# real-task-001 下一阶段计划：文献参照驱动的研究重构与技能升级

## 1. 计划定位

本计划承接 `real-task-001` 三轮真实任务闭环结果。

上一阶段已经证明：

- task004 可以作为真实电力科研小任务进入闭环。
- 三轮 evidence-bound loop 已完成。
- 主指标 `hosting_capacity_level` 没有提升。
- 次级指标 loss、voltage margin 有改善。
- 系统正确阻止了“次级指标改善 = 承载力提升”的过度 claim。
- 最终成果路由为 `internal_report_ready`，成果等级为 `diaomu`。

但上一阶段也暴露出一个关键问题：

> 当前 cognition layer 主要在守门、限界、纠错，还没有充分起到“重构研究框架、引入外部参照、驱动技能结构升级”的作用。

因此，本计划的目标不是继续简单多跑几轮，而是：

> 让文献调研与认知重构进入 real-task-001 主循环，推动 task004 从 `diaomu` 级内部技术记录，向 `zhuoshi` 级可打磨研究问题推进。

## 2. 核心判断

当前 `diaomu` 评价不是对研究方向的否定，而是对当前证据质量的评价。

方向本身仍有潜力：

- 新能源接入承载力评估是有明确科研价值的问题。
- 控制策略对承载力边界的影响是合理研究对象。
- 当前 task004 已经暴露出边界定义、控制策略、指标体系和 claim discipline 的重要性。

当前证据偏弱的原因主要是：

1. 当前扫描包络没有充分触发真实边界。
2. 控制策略空间太窄，只测试了 uniform inverter support。
3. evaluator 过度依赖单一 `hosting_capacity_level` 主指标。
4. 次级指标改善没有被纳入更完整的研究价值框架。
5. 文献方法谱系没有进入下一轮技能设计。
6. cognition worker 还没有主动提出更高层研究框架。

## 3. 总目标

本计划要一口气推进四件事：

1. 建立 `research-framing literature worker`。
2. 建立 `cognition_reframing_worker`。
3. 基于文献和认知重构，设计 task004 的下一版技能/评价框架。
4. 执行至少一轮升级后的真实任务闭环，判断是否能从 `diaomu` 向 `zhuoshi` 推进。

## 4. 非目标

本计划暂不做：

1. 大规模自动文献综述。
2. 多 Agent 语义差异研究。
3. 自动论文写作。
4. 全量 PDF/HTML 自动抽取。
5. 复杂时序/概率 hosting capacity 全系统实现。
6. 为了制造指标提升而降低 evaluator 标准。

## 5. 新增 Worker 设计

### 5.1 research-framing literature worker

职责：

不是“补引用”，而是为 cognition layer 提供外部方法空间。

输入：

- `tasks/task004/task.yaml`
- `analysis/real_task_001/reports/real_task_research_report.md`
- `analysis/real_task_001/reports/cognition_upgrade.yaml`
- `analysis/real_task_001/delivery/taste_assessment.yaml`
- task004 已有 `literature_alignment`、`method_card`、`explanation_card`
- 必要时新增人工 curated seed papers

必须回答：

1. Hosting capacity 文献中有哪些典型问题定义：
   - static HC
   - time-series HC
   - probabilistic HC
   - OPF-based HC
   - control-strategy-conditioned HC
2. 常见算法策略有哪些：
   - simple scale scan
   - deterministic power-flow scan
   - sensitivity-based method
   - OPF/search method
   - Volt/VAR control assisted HC
   - curtailment / inverter capability assisted HC
3. 常见评价指标有哪些：
   - hosting capacity level
   - voltage violation trigger
   - thermal violation trigger
   - control effort
   - loss
   - voltage margin
   - boundary stability
   - scenario robustness
4. 当前 task004 为什么只能支持 internal report。
5. 如果要成为 paper candidate，最低实验矩阵是什么。
6. 下一轮 skill family 应该优先探索什么。

输出：

- `analysis/real_task_001/literature/problem_framing_map.yaml`
- `analysis/real_task_001/literature/method_family_map.yaml`
- `analysis/real_task_001/literature/metric_taxonomy.yaml`
- `analysis/real_task_001/literature/experiment_design_recommendation.yaml`
- `analysis/real_task_001/literature/claim_thresholds.yaml`
- `analysis/real_task_001/literature/next_skill_family_candidates.yaml`

### 5.2 cognition_reframing_worker

职责：

把 real-task-001 的失败和文献参照转化为下一版研究框架。

输入：

- real-task-001 三轮结果。
- literature worker 输出。
- existing task004 task/evaluator/skill objects。

必须回答：

1. 当前问题定义是否过窄。
2. 当前 evaluator 是否足以表达研究价值。
3. 当前技能空间是否太弱。
4. 当前场景是否没有触发真实边界。
5. 下一版任务边界如何重写。
6. 下一版 evaluator 应增加哪些指标或 gate。
7. 下一版 skill worker 应探索哪些方法、流程、标准变化。
8. 从 `diaomu` 升到 `zhuoshi` 的最低证据门槛是什么。

输出：

- `analysis/real_task_001/reframing/research_framing_upgrade.yaml`
- `analysis/real_task_001/reframing/evaluator_upgrade_request.yaml`
- `analysis/real_task_001/reframing/skill_family_upgrade_request.yaml`
- `analysis/real_task_001/reframing/scenario_upgrade_request.yaml`
- `analysis/real_task_001/reframing/zhuoshi_threshold.yaml`

## 6. 下一版研究框架建议

基于目前结果，下一版 task004 不应继续只问：

> uniform inverter support 是否提高 hosting_capacity_level？

而应升级为：

> 在边界可触发的静态承载力扫描包络下，比较不同控制策略对承载力边界、运行质量、控制代价和边界稳定性的影响。

### 6.1 Scenario upgrade

当前问题：

- baseline 和 candidate 都能扫到 scale=3.0。
- 没有充分触发真实边界。

建议：

1. 扩展 `renewable_scale_values` 到更高上限，例如 4.0、5.0 或直到触发 violation。
2. 增加更紧电压下限 sensitivity case，例如 `vm_min=0.93` 或 `0.95`，但必须记录这是 scenario stress，不得当作降低/改变标准来制造进步。
3. 增加至少两个 load level：
   - normal load
   - stressed load
4. 记录 first violation point，而不仅是 last feasible point。

### 6.2 Skill family upgrade

当前技能：

- uniform inverter Q support。

建议新增技能族：

1. `uniform_q_support`
   - 当前基线 candidate。
2. `voltage_sensitivity_q_allocation`
   - 按节点电压/灵敏度分配无功。
3. `boundary_neighborhood_refinement`
   - 在边界邻域进行细粒度复查。
4. `control_effort_limited_q_support`
   - 在给定 control effort budget 下比较效果。
5. 可选：`simple_search_q_allocation`
   - 简化优化式无功分配，不做复杂 OPF。

### 6.3 Evaluator upgrade

当前 evaluator 主指标合理，但维度不足。

建议保留：

- `hosting_capacity_level` as primary.

新增或强化：

- `boundary_trigger_scale`
- `first_violation_type`
- `boundary_stability_margin`
- `control_effort`
- `loss_at_boundary`
- `voltage_margin`
- `scenario_robustness`
- `claim_support_level`

关键原则：

1. 不能降低 `hosting_capacity_level` 的主指标地位。
2. 次级指标改善只能支持 bounded operational-quality claim。
3. 若要支持 paper candidate，必须有跨场景稳定改善或明确机制解释。

## 7. 执行阶段

### Phase 0: Consolidate real-task-001 evidence

目标：

- 冻结已完成三轮结果。
- 建立输入 evidence pack。

输出：

- `analysis/real_task_001/reframing/input_evidence_pack.yaml`

### Phase 1: Literature framing worker

目标：

- 用已有文献对象和必要新增 seed，形成 hosting capacity 方法/指标/claim 地图。

输出：

- `problem_framing_map.yaml`
- `method_family_map.yaml`
- `metric_taxonomy.yaml`
- `experiment_design_recommendation.yaml`
- `claim_thresholds.yaml`
- `next_skill_family_candidates.yaml`

验收：

- 每个方法族必须说明控制变量、适用边界和与 task004 的关系。
- 每个 claim threshold 必须说明需要哪些证据。

### Phase 2: Cognition reframing worker

目标：

- 解释为什么当前 `diaomu`。
- 明确如何升级到 `zhuoshi`。
- 生成下一版 task/evaluator/skill/scenario 改造请求。

输出：

- `research_framing_upgrade.yaml`
- `evaluator_upgrade_request.yaml`
- `skill_family_upgrade_request.yaml`
- `scenario_upgrade_request.yaml`
- `zhuoshi_threshold.yaml`

验收：

- 必须明确指出当前失败是技能、场景、evaluator、还是研究定义问题。
- 必须给出可执行下一轮改变，不得只写泛泛建议。

### Phase 3: Implement one bounded upgrade

本阶段只实现一个最小升级，不追求全系统完成。

优先级：

1. Scenario upgrade：扩展 scan envelope，使边界更可能被触发。
2. Evaluator upgrade：记录 first violation point / boundary trigger scale。
3. Skill upgrade：新增一个简单但结构不同的 skill family，例如 `voltage_sensitivity_q_allocation`。

输出：

- 新/更新 task004 scenario 或 constraint object。
- 新/更新 evaluator 字段。
- 新 candidate skill 或 strategy。
- 对应 run artifacts。

### Phase 4: Run upgraded real-task loop

目标：

- 至少执行一轮升级后的真实任务闭环。
- 与 real-task-001 三轮结果对比。

必须判断：

1. 主指标是否改善。
2. 次级指标是否改善。
3. 控制代价是否可接受。
4. 边界是否真正被触发。
5. claim 是否可以从 internal report 向 zhuoshi 迈进。

输出：

- `analysis/real_task_001_upgrade/`
- `real_task_001_upgrade_report.md`
- `upgrade_effectiveness_assessment.yaml`
- `upgrade_cognition_reframing_result.yaml`

## 8. 验收标准

最低成功：

1. 文献 worker 输出六类 framing artifacts。
2. cognition_reframing_worker 输出五类 reframing artifacts。
3. 至少完成一个 scenario/evaluator/skill 的结构性升级。
4. 至少运行一轮升级后真实任务。
5. 最终报告明确说明是否脱离 `diaomu`。

较好成功：

1. 新场景真实触发 boundary。
2. 新 evaluator 能区分 primary boundary gain、secondary quality gain、control effort。
3. 新 skill family 至少形成与 uniform support 的清晰对照。
4. 即使主指标仍不提升，也能形成更清晰的 `zhuoshi_threshold` 和下一步研究设计。

高质量成功：

1. 新 skill family 在至少一个 stress scenario 下提高 primary hosting capacity 或 boundary stability。
2. 改进不是通过降低标准获得。
3. 文献参照能说明该结果是已知方法复现、合理变体，还是潜在 extension。
4. 成果等级从 `diaomu` 升级为 `zhuoshi`，但仍受 claim boundary 控制。

## 9. 必须避免的错误

1. 把文献 worker 做成报告润色器。
2. 把更多文献数量当作认知提升。
3. 把 scenario stress 当作公平提升证据。
4. 把次级指标改善包装成承载力提升。
5. 把结构性建议停留在文字，不进入下一轮 skill/evaluator/scenario 改造。
6. 把新 runner 写成 task004-only 死脚本，而不沉淀可复用 worker 协议。

## 10. 推荐验证命令

计划执行后至少运行：

```bash
python -m py_compile \
  scripts/run_real_task001_loop.py \
  scripts/verify_real_task001_loop.py \
  scripts/validate_schemas.py

python scripts/verify_real_task001_loop.py
python scripts/validate_schemas.py --artifacts real-task-001
python scripts/run_light_probe.py
```

若新增 artifact set：

```bash
python scripts/validate_schemas.py --artifacts real-task-001-reframing
```

若实现升级后真实任务：

```bash
python scripts/verify_real_task001_upgrade.py
```

## 11. 最终判断逻辑

本计划结束时必须给出四类判断：

1. `research framing`
   - 当前 task004 研究框架是否更清晰。
2. `skill`
   - 是否出现方法、流程或标准层面的结构性技能升级。
3. `effectiveness`
   - 主指标、次级指标、控制代价和边界稳定性是否改善。
4. `delivery`
   - 是否仍是 `diaomu/internal_report_ready`，还是可以推进到 `zhuoshi/paper_candidate_preparation`。

如果最终仍是 `diaomu`，也必须说明：

- 是方向不够强。
- 是当前技能不够强。
- 是 evaluator 还不够。
- 是场景仍不足以触发关键差异。
- 还是文献参照表明该路线缺乏新颖性。

## 12. 计划结论

下一步不应该继续盲目迭代 task004 参数，也不应该过早研究多 Agent 语义差异。

真正应该做的是：

> 让文献调研和认知重构进入真实科研闭环，用外部方法空间重新设计 task004 的问题定义、技能空间、评价指标和成果门槛。

这一步如果成功，DaoShuGuo 的认知层将从 `claim gate` 升级为 `research framing upgrader`。
