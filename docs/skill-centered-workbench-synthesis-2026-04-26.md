# Skill-Centered Workbench Synthesis - 2026-04-26

## 1. 为什么补充这份文档

前一版协同工作台设计强调了 human judgment、evidence、claim gate 和 routing constraint。

这个方向是必要的，但还不够准确。

DaoShuGuo 的研究推进主轴应是：

> 围绕技能开展研究工作推进。

因此，工作台不能只是 `topic cockpit`，而应首先是：

> skill-centered research cockpit。

Topic 是研究容器；skill 是推进对象；effectiveness 是评价门；cognition 是结构化解释；human decision 是下一轮 skill iteration 的路由约束。

## 2. 既有研究已经给出的答案

### 2.1 研究推进对象是什么

当前 `real-task-001` 的技能推进对象不是泛泛的“工作台 topic”，而是：

```yaml
target_skill_ref: skill.power.renewable_capacity_optimizer_task004
```

来源：

- `analysis/real_task_001/reframing/structural_skill_change_request.yaml`

该技能服务的研究对象是 IEEE69 hosting capacity 静态承载力评估。

### 2.2 当前技能家族如何划分

既有 `method_family_map` 已把技能相关路线拆成五类：

| family | dimension | 当前判断 |
| --- | --- | --- |
| `scale_scan` | process | existing baseline process |
| `uniform_q_support` | use_condition | existing candidate，但不能直接叫结构提升 |
| `voltage_sensitivity_q_allocation` | method | recommended minimal structural candidate |
| `boundary_neighborhood_refinement` | process | recommended evaluator/process upgrade |
| `control_effort_limited_search` | standard | future extension |

来源：

- `analysis/real_task_001/literature/method_family_map.yaml`

这已经回答了工作台第一屏应显示什么：

1. 当前 active skill family。
2. 它属于方法、流程、标准，还是使用条件。
3. 为什么它算或不算结构性技能提升。
4. 最低验证要求是什么。

### 2.3 当前 skill-use vs skill-structure 判断是什么

既有 `skill_structure_diagnosis` 给出的判断是：

> Observed gains so far are bounded skill-use observations and claim-gate success, not verified structural skill improvement.

它明确指出：

- uniform inverter-Q support 更像 use condition。
- 真正的结构候选应转向 voltage-sensitivity-based non-uniform reactive allocation。
- 结构提升不能来自 q_step 增大或 scan envelope 变宽。
- 必须有 changed allocation logic、comparable baseline evidence、cost-aware evaluation。

来源：

- `analysis/real_task_001/reframing/skill_structure_diagnosis.yaml`

这直接定义了工作台里的关键判定卡：

```text
当前是否是结构性技能提升？
答案：不是已验证提升，只是结构性尝试 / 技能使用观察。
```

### 2.4 方法、流程、标准分别要怎么改

既有 `structural_skill_change_request` 已给出三类改动：

#### 方法

- 引入 `voltage_sensitivity_q_allocation` 作为最小非均匀分配方法。
- 与 fixed baseline 和 uniform support 在同一 scan envelope、可比 control effort 下比较。
- 把 `uniform_q_support` 明确标成 use-condition baseline。
- 每个 candidate skill 必须说明 method / process / standard。
- 排除 q_step-only escalation。

#### 流程

- 运行 `extended_until_violation`，确保电压边界真的被触发。
- 保留 original scan 作为连续性 baseline，但不能在没有 violation bracket 时用于 boundary movement claim。
- 加入 first violation 周边的 boundary-neighborhood scenario。
- 保持 static single-snapshot 范围，不扩展到 time-series/probabilistic。
- 保留 mismatch negative-control lane，仅用于诊断对照。

#### 标准

- baseline 和 candidate 都必须报告 last-feasible / first-violation。
- 增加 boundary-neighborhood refinement。
- primary metrics 与 secondary operational-quality metrics 分离。
- 增加 control-effort metric 和 claim gate。
- negative control 与 candidate-improvement scoring 分离。

来源：

- `analysis/real_task_001/reframing/structural_skill_change_request.yaml`

这说明 UI 不能只显示“下一步建议”，而要显示：

```text
本轮技能结构请求：
- method changes
- process changes
- standard changes
- forbidden shortcuts
- required validation
```

### 2.5 evaluator 已经回答了哪些 claim 边界

既有 `metric_taxonomy` 已明确：

- `hosting_capacity_level` 是 primary metric，支持 hosting-capacity boundary movement。
- `boundary_trigger_scale` 是 primary_support，证明 boundary 是否真的 bracketed。
- `loss_at_boundary` 是 secondary，只支持 operational-quality improvement。
- `control_effort` 是 cost gate，防止高代价伪改进。

已明确 claim boundary：

- secondary metric gains 不能支持 primary hosting-capacity claims。
- boundary-trigger evidence 是 boundary movement claim 的前提。

来源：

- `analysis/real_task_001/literature/metric_taxonomy.yaml`

### 2.6 当前成效判断是什么

升级后的 effectiveness assessment 结论是：

```yaml
primary_delta: 0.0
loss_delta: -26.463893510266843
voltage_margin_delta: 0.004372542949686031
boundary_trigger_delta: 0.0
control_effort_delta: 0.35
boundary_triggered: false
claim_support_level: operational_quality_only
```

判断：

> This is a structural method attempt with operational-quality gains, not verified hosting-capacity improvement.

来源：

- `analysis/real_task_001_upgrade/reports/upgrade_effectiveness_assessment.yaml`

这说明当前技能推进状态是：

1. 有真实结构性方法尝试。
2. 产生了 secondary operational-quality gain。
3. primary hosting-capacity 没有提升。
4. boundary 没触发。
5. control effort 增加。
6. 不能声称已形成结构性技能提升。

### 2.7 当前认知诊断是什么

升级后的 cognition diagnosis 判断：

> Voltage-sensitivity allocation is a real structural attempt, but current evidence still supports only bounded operational-quality improvement, not zhuoshi-grade hosting-capacity advancement.

边界问题：

- hosting_capacity_level delta is zero
- boundary_triggered is false
- control_effort increased by 0.35

下一步：

```yaml
recommended_next_worker: skill_worker
recommended_action: redesign_skill_structure
continue_loop: true
```

来源：

- `analysis/real_task_001_upgrade/reports/upgrade_cognition_diagnosis.yaml`

### 2.8 当前品味/成果等级是什么

当前 taste assessment：

```yaml
grade: diaomu
claim_ceiling: Internal technical note on structural attempt and bounded operational-quality improvement.
forbidden_claims:
  - verified structural skill improvement
  - hosting-capacity boundary improvement
  - paper-candidate result
```

来源：

- `analysis/real_task_001_upgrade/delivery/taste_assessment.yaml`

这说明工作台应把成果等级绑定到技能证据，而不是绑定到 brief 写作质量。

## 3. 对工作台设计的修正

### 3.1 第一屏从 Topic Cockpit 改为 Skill-Centered Cockpit

第一屏应优先回答：

1. 当前 active skill 是什么。
2. 当前 skill family 是什么。
3. 本轮尝试属于 method / process / standard / use_condition 哪一类。
4. baseline skill 是什么。
5. candidate skill 是什么。
6. evaluator 证明了什么。
7. 本轮是 skill-use observation、structural attempt，还是 verified structural improvement。
8. 下一轮 skill worker 应改方法、流程还是标准。
9. 哪些 shortcut 被禁止。
10. 人类需要判断什么技能问题。

Topic 状态、claim ceiling、taste grade 仍然显示，但作为 skill evidence 的结果，而不是第一主轴。

### 3.2 新增 Skill Progression Strip

每个 topic 下应显示一条技能推进链：

```text
method_family_map
-> structural_skill_change_request
-> skill_change_result
-> effectiveness_assessment
-> cognition_diagnosis
-> taste / claim gate
-> next_skill_request
```

用户可以看到当前卡在哪个节点。

### 3.3 新增 Skill Judgment Card

卡片字段：

```yaml
active_skill_ref: skill.power.renewable_capacity_optimizer_task004
candidate_family: voltage_sensitivity_q_allocation
dimension: method
status: structural_attempt_not_verified
baseline: fixed_q_baseline / uniform_q_support
primary_metric_delta: 0.0
secondary_gain: loss and voltage margin improved
cost_delta: +0.35 control effort
boundary_triggered: false
judgment: operational_quality_only
forbidden_claims:
  - verified structural skill improvement
  - hosting-capacity boundary improvement
next_worker: skill_worker
next_action: redesign_skill_structure
```

### 3.4 Human Attention Queue 应围绕技能问题

当前最重要的人类判断不应只是：

> claim ceiling 是否接受？

而应包括：

1. 是否接受 `voltage_sensitivity_q_allocation` 作为下一轮主技能方向？
2. 是先修 scenario/boundary trigger，还是继续改 allocation method？
3. `uniform_q_support` 是否应冻结为 use-condition baseline？
4. control-effort gate 应设为硬门槛还是软解释项？
5. 这轮 negative/diagnostic result 是否值得继续投入？

### 3.5 Routing Constraint 应直接约束下一轮 skill worker

人类反馈应编译成类似：

```yaml
target_worker: skill_worker
must_do:
  - implement or refine voltage_sensitivity_q_allocation
  - compare against uniform_q_support under equal control effort
  - run extended_until_violation scan
must_not_do:
  - q_step-only escalation
  - claim boundary improvement without boundary_triggered=true
  - treat secondary metric gain as primary skill improvement
required_outputs:
  - skill_change_request
  - skill_change_result
  - effectiveness_assessment
  - cognition_diagnosis
```

## 4. 工作台要直接回答的问题

基于既有研究，第一版 UI 至少要回答这些问题：

1. 当前研究推进的技能是什么？
   - `skill.power.renewable_capacity_optimizer_task004`

2. 当前推荐结构候选是什么？
   - `voltage_sensitivity_q_allocation`

3. 当前已有 candidate 的性质是什么？
   - `uniform_q_support` 是 use-condition，不是结构提升。

4. 本轮有没有结构性技能提升？
   - 没有 verified structural improvement；只有 real structural attempt。

5. 为什么不能 claim hosting-capacity improvement？
   - primary delta 为 0，boundary 未触发。

6. 有什么正向信号？
   - loss 与 voltage margin 改善，说明有 operational-quality gain。

7. 代价是什么？
   - control effort 增加 0.35。

8. 下一轮该做什么？
   - redesign skill structure；优先处理 boundary-triggering scenario 和 equal-effort comparison。

9. 禁止什么捷径？
   - q_step-only escalation、single-point boundary evidence、secondary metric overclaim。

10. 成果等级是什么？
    - `diaomu`，内部 technical note 级。

## 5. 对后续实现的要求

后续 UI/API 开发必须以这些对象为输入，而不是重新硬编码判断：

- `analysis/real_task_001/literature/method_family_map.yaml`
- `analysis/real_task_001/literature/metric_taxonomy.yaml`
- `analysis/real_task_001/literature/claim_thresholds.yaml`
- `analysis/real_task_001/literature/experiment_design_recommendation.yaml`
- `analysis/real_task_001/reframing/skill_structure_diagnosis.yaml`
- `analysis/real_task_001/reframing/structural_skill_change_request.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_effectiveness_assessment.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_cognition_diagnosis.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_loop_review.yaml`
- `analysis/real_task_001_upgrade/delivery/taste_assessment.yaml`

第一版可以先把这些对象聚合进 workbench topic / cockpit / researcher lens。

验收标准：

1. UI 不打开原始 YAML，也能讲清 active skill、candidate family、method/process/standard、skill-use vs structure。
2. UI 能显示本轮技能推进为什么只是 structural attempt，不是 verified structural improvement。
3. UI 能把 human decision 编译成下一轮 skill worker 的 routing constraints。
4. UI 不允许把 secondary metric improvement 展示成 primary skill improvement。
5. UI 能显示 forbidden shortcuts 和 required validation。
