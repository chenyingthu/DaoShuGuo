# Real Research Loop Convergence Plan

## 1. 计划定位

本计划汇总近期围绕 DaoShuGuo 后续推进的几个关键讨论，并把它们收敛为一次可以连续执行的工作方案。

当前项目已经完成两类证明：

1. 通用框架 fixture 级验证已经达到 `level_3_cross_task_agentic_full_loop`。
2. `real-task-001` 已经在 task004 上完成三轮真实任务闭环，并诚实得出 `diaomu / internal_report_ready` 结论。

但这还不是项目最初追求的“自主科研 Agent”。

当前最核心的问题是：

> 系统已经能守门、限界和记录失败，但还没有充分证明它能通过外部学习与认知重构，主动推动研究问题、技能结构和成果质量升级。

因此，本计划的目标不是继续堆 task，也不是继续调 task004 参数，而是把真实科研闭环推进到下一层：

> `真实任务证据 -> 学习/文献 worker -> 认知重构 worker -> 结构性技能/评价/场景升级 -> 成效复测 -> 成果等级再判断 -> 通用框架回归验证`

## 2. 前面讨论的统一判断

### 2.1 关于 task004 当前结果

`real-task-001` 的 task004 结果不是失败，也不是成功。

它证明了：

1. task004 可以进入真实电力科研闭环。
2. 系统能区分 primary hosting-capacity 指标和 secondary operational-quality 指标。
3. 系统没有把 loss、voltage margin 改善包装成 hosting-capacity 提升。
4. 负面对照验证了单点/失配证据不能替代边界扫描证据。

它没有证明：

1. 技能本身已经结构性变强。
2. 认知层已经能主动提出高质量研究框架。
3. 当前结果已经具备论文候选质量。
4. 多轮 loop 自然会产生更高层认知。

### 2.2 关于认知层的问题

当前 cognition layer 更像 `claim gate`，主要作用是：

1. 阻止过度 claim。
2. 标记证据不足。
3. 区分 skill-use improvement 和 skill-structure improvement。
4. 给出下一步粗略方向。

但它还不像一个优秀研究生的认知活动，因为它缺少：

1. 外部文献和方法谱系输入。
2. 对问题定义的主动重构。
3. 对 evaluator 是否表达研究价值的反思。
4. 对 skill family 边界的系统比较。
5. 对“什么证据足以从雕木走向琢石”的明确判断。

### 2.3 关于学习/文献 worker 的定位

学习/文献 worker 仍然必要，但不能做成“补引用”和“润色报告”的 worker。

它的职责是为 cognition worker 提供外部方法空间：

1. 研究问题如何被文献定义。
2. 方法族有哪些。
3. 指标体系有哪些。
4. 实验矩阵如何设计。
5. claim threshold 应如何设置。
6. 当前 task 与已有方法的关系是什么。

学习 worker 不做最终科研判断。最终判断由 cognition worker 基于 evidence pack 和 learning context 完成。

### 2.4 关于技能升级的判断

技能不是一个算法文件，而是：

1. 方法。
2. 流程。
3. 标准。

因此，下一阶段不能把 `q_step` 调大、搜索范围扩大、参数换一换就称为技能提升。

允许观察 skill-use improvement，但必须追问：

1. 它是否揭示了方法问题。
2. 它是否揭示了流程问题。
3. 它是否揭示了标准问题。
4. 它是否能转化成可复用的结构性 skill change request。

### 2.5 关于通用框架的判断

task004 可以作为真实任务锚点，但不能把框架改成 task004 专用。

下一阶段所有新增能力必须满足：

1. worker 协议通用。
2. artifact schema 通用。
3. runtime/backend 选择走 registry。
4. task-specific 信息只存在于 task package、adapter、evaluator、skill candidate 或 evidence seed。
5. 不新增 `if task004` 式 framework logic。

## 3. 本计划要证明的主张

本计划结束时，项目应能给出比当前更强、但仍诚实的主张：

> 对满足 DaoShuGuo task package contract 的真实电力科研小任务，系统可以在不修改框架核心逻辑的情况下，引入学习资料和外部方法空间，驱动 cognition worker 形成研究重构，生成结构性 skill/evaluator/scenario change request，并通过真实任务复测判断是否产生更高质量成效。

如果 task004 仍然不能从 `diaomu` 升到 `zhuoshi`，也必须说明原因：

1. 研究方向本身不够强。
2. 当前技能族还不够强。
3. evaluator 仍不能表达关键价值。
4. scenario 没有触发关键边界。
5. 文献参照表明该路线只是已知工程常识。

## 4. 非目标

本计划不做以下事情：

1. 不做大规模自动论文生成。
2. 不做重型知识图谱或向量数据库。
3. 不做多模型语义差异研究。
4. 不为了好看强行把 task004 升为论文候选。
5. 不用 controller 下场写认知结论。
6. 不用 task-specific runner 伪装通用能力。
7. 不把参数调优包装成结构性技能升级。

## 5. 执行总路线

### Phase 0: 冻结现状与建立执行基线

目标：

1. 确认当前 `real-task-001` 已有证据完整。
2. 确认 generic full-loop fixture matrix 的现状。
3. 建立下一步执行前的回归基线。

必须检查：

1. `analysis/real_task_001/reports/real_task_research_report.md`
2. `analysis/real_task_001/reports/cognition_upgrade.yaml`
3. `analysis/real_task_001/delivery/taste_assessment.yaml`
4. `analysis/real_task_001/delivery/delivery_readiness.yaml`
5. `analysis/runtime_matrix/agent_runtime_matrix_report.yaml`
6. `docs/generic-full-loop-validation-report.md`

输出：

1. `analysis/real_task_001/reframing/input_evidence_pack.yaml`
2. `analysis/real_task_001/reframing/current_gap_summary.yaml`

验收：

1. evidence pack 能回链到三轮 run、effectiveness、cognition、delivery 和 taste artifacts。
2. current gap summary 明确列出 `claim gate 已成立` 与 `research framing 未成立` 的区别。

### Phase 1: 建立通用 learning / literature worker 协议

目标：

把已有 structural-learning chain 升级为真实任务可用的 learning worker 协议，而不是 task003 的 curated seed replay。

需要固化的对象链：

1. `learning_need`
2. `learning_context_pack`
3. `research_framing_map`
4. `method_family_map`
5. `metric_taxonomy`
6. `claim_threshold_map`
7. `experiment_design_recommendation`

实现原则：

1. learning worker 负责整理外部方法空间。
2. cognition worker 负责解释学习资料对当前任务的意义。
3. controller 只负责编排和校验，不写判断。
4. 初期允许 curated seed，但必须标注 `curated_seed`，不能伪装成完整文献综述。
5. 后续可扩展到 abstract/fulltext excerpt，但本轮先保证 worker 协议和 artifact 质量。

输出：

1. `docs/research-framing-learning-worker-protocol.md`
2. `schemas/quality/research_framing_map.schema.yaml`
3. `schemas/quality/method_family_map.schema.yaml`
4. `schemas/quality/metric_taxonomy.schema.yaml`
5. `schemas/quality/claim_threshold_map.schema.yaml`
6. `schemas/quality/experiment_design_recommendation.schema.yaml`
7. 对应 sample artifacts。

验收：

1. schema 能被 `scripts/validate_schemas.py` 识别。
2. artifacts 必须有 source refs、applicability boundaries、confidence 和 gaps。
3. 不允许把 learning worker 输出直接当最终 cognition diagnosis。

### Phase 2: 为 task004 生成 research framing learning pack

目标：

让 learning worker 针对 task004 的 hosting-capacity 问题生成外部方法空间，而不是继续围绕 `q_step` 调参。

必须覆盖的问题定义：

1. static hosting capacity。
2. time-series hosting capacity。
3. probabilistic hosting capacity。
4. OPF/search-based hosting capacity。
5. control-strategy-conditioned hosting capacity。

必须覆盖的方法族：

1. scale scan。
2. deterministic power-flow scan。
3. sensitivity-based method。
4. OPF/search method。
5. Volt/VAR control assisted HC。
6. curtailment / inverter capability assisted HC。

必须覆盖的评价指标：

1. `hosting_capacity_level`
2. `boundary_trigger_scale`
3. `first_violation_type`
4. `boundary_stability_margin`
5. `control_effort`
6. `loss_at_boundary`
7. `voltage_margin`
8. `scenario_robustness`
9. `claim_support_level`

输出：

1. `analysis/real_task_001/literature/learning_need.yaml`
2. `analysis/real_task_001/literature/learning_context_pack.yaml`
3. `analysis/real_task_001/literature/problem_framing_map.yaml`
4. `analysis/real_task_001/literature/method_family_map.yaml`
5. `analysis/real_task_001/literature/metric_taxonomy.yaml`
6. `analysis/real_task_001/literature/experiment_design_recommendation.yaml`
7. `analysis/real_task_001/literature/claim_thresholds.yaml`
8. `analysis/real_task_001/literature/next_skill_family_candidates.yaml`

验收：

1. 每个方法族必须说明与 task004 的关系、适用边界和最低验证条件。
2. 每个指标必须说明支持哪些 claim，不能支持哪些 claim。
3. 必须明确当前 task004 为什么只能是 `diaomu`。

### Phase 3: cognition reframing worker 形成研究重构

目标：

让 cognition worker 基于 Phase 0 evidence pack 和 Phase 2 learning pack，形成真正的研究框架升级，而不是泛泛建议。

必须回答：

1. 当前 task004 问题定义是否过窄。
2. 当前 evaluator 是否足以表达研究价值。
3. 当前 scenario 是否没有触发关键边界。
4. 当前 skill family 是否只是在做 skill-use tuning。
5. 下一轮应先升级 scenario、evaluator、skill，还是三者协同。
6. 从 `diaomu` 到 `zhuoshi` 的最低证据门槛是什么。

输出：

1. `analysis/real_task_001/reframing/research_framing_upgrade.yaml`
2. `analysis/real_task_001/reframing/evaluator_upgrade_request.yaml`
3. `analysis/real_task_001/reframing/skill_family_upgrade_request.yaml`
4. `analysis/real_task_001/reframing/scenario_upgrade_request.yaml`
5. `analysis/real_task_001/reframing/zhuoshi_threshold.yaml`
6. `analysis/real_task_001/reframing/skill_structure_diagnosis.yaml`
7. `analysis/real_task_001/reframing/structural_skill_change_request.yaml`

验收：

1. cognition worker 输出必须引用 learning pack 和 real-task evidence。
2. 必须显式区分 skill-use improvement、structural skill attempt、verified structural improvement。
3. 不得声称已产生 structural improvement，除非后续复测验证。

### Phase 4: 实施一个最小但真实的结构性升级

目标：

不做大而全，只实现一个足以检验认知重构是否有用的 bounded upgrade。

优先级：

1. Scenario upgrade：扩展扫描包络，确保有机会触发 boundary。
2. Evaluator upgrade：记录 first violation point、violation type、boundary margin、control effort。
3. Skill upgrade：新增一个与 uniform support 结构不同的简单 skill family。

推荐最小方案：

1. 保留原始 `hosting_capacity_level` 主指标。
2. 增加 boundary-neighborhood scan。
3. 增加 `voltage_sensitivity_q_allocation` candidate。
4. 在同一 evaluator 下比较 uniform support 与 sensitivity allocation。
5. 增加 `control_effort`，防止用不可接受代价换指标。

输出：

1. 更新或新增 task004 scenario/constraint object。
2. 更新 evaluator 输出字段。
3. 新增 candidate skill 文件和 skill card。
4. 新增或更新 adapter 配置，但不得改 loop engine。

验收：

1. 结构性变化必须落在方法、流程或标准至少一类上。
2. 不能只增加 `q_step`。
3. 不能通过降低标准制造提升。
4. 所有新增字段必须被 verifier 或 schema 检查。

### Phase 5: 运行升级后的真实任务闭环

目标：

在 `analysis/real_task_001_upgrade/` 下运行至少一轮升级后真实闭环，并与 `real-task-001` 三轮结果对比。

必须产出：

1. `task_readiness_report`
2. `skill_change_request`
3. `skill_change_result`
4. `effectiveness_assessment`
5. `cognition_diagnosis`
6. `loop_routing_decision`
7. `research_review`
8. `delivery_readiness`
9. `taste_assessment`

必须判断：

1. primary hosting-capacity 是否提升。
2. boundary 是否被真实触发。
3. secondary operational-quality 是否改善。
4. control effort 是否合理。
5. 改善是否来自结构性 skill change，而不是 task-specific 参数调优。
6. 是否满足 `zhuoshi_threshold`。

输出：

1. `analysis/real_task_001_upgrade/reports/upgrade_effectiveness_assessment.yaml`
2. `analysis/real_task_001_upgrade/reports/upgrade_cognition_diagnosis.yaml`
3. `analysis/real_task_001_upgrade/reports/real_task_upgrade_report.md`
4. `analysis/real_task_001_upgrade/delivery/taste_assessment.yaml`
5. `analysis/real_task_001_upgrade/delivery/delivery_readiness.yaml`

验收：

1. 如果主指标仍不提升，必须说明原因，而不是继续泛化叙述。
2. 如果只改善 secondary metrics，成果等级最多到 bounded internal report，不能直接升到 paper candidate。
3. 如果形成 `zhuoshi`，必须有 boundary、metric、claim、literature 四类证据支撑。

### Phase 6: 通用性回归与多任务防局部陷阱验证

目标：

防止新增能力变成 task004 专用补丁。

必须回归：

1. generic onboarding。
2. generic full-loop engine。
3. fixture runtime matrix 的关键子集。
4. structural-learning chain。
5. research review gate。

至少验证：

1. task004 upgrade 不破坏 `task006_near_neighbor`。
2. task004 upgrade 不破坏 `task008_bad_candidate`。
3. task004 upgrade 不破坏 `task010_literature_required`。
4. 新 learning/reframing artifacts 可以被 generic schema 层识别。

推荐命令：

```bash
python scripts/verify_real_task001_loop.py
python scripts/validate_schemas.py --artifacts real-task-001
python scripts/validate_schemas.py --artifacts real-task-001-reframing
python scripts/verify_real_task001_upgrade.py
python scripts/run_light_probe.py
python scripts/run_generic_loop_engine.py --task-adapter adapters/task010_literature_required.yaml --backend pi_gpt55
```

若时间允许，运行缩小版矩阵：

```bash
python scripts/run_agent_runtime_matrix.py \
  --tasks task006_near_neighbor task008_bad_candidate task010_literature_required \
  --runtimes pi_gpt55 pi_baidu_kimi_k25
```

验收：

1. task004 新能力不能要求修改 generic loop engine 的 task-specific 分支。
2. fixture 任务仍能跑通或给出明确 blocked report。
3. 若 runtime matrix 出现语义差异，只记录为后续研究对象，不在本阶段展开多模型对齐研究。

### Phase 7: 总结、记录与提交

目标：

把这轮工作变成项目资产，而不是临时实验痕迹。

必须更新：

1. `docs/实验过程与讨论记录.md`
2. `docs/generic-full-loop-validation-report.md`
3. `docs/structural-learning-worker-protocol.md` 或新增 learning worker protocol。
4. `AGENTS.md` 中必要的长期原则，若本轮暴露新的禁止事项。
5. 相关 reviews。

最终报告必须回答：

1. skill 阶段是否产生结构性变化。
2. cognition 阶段是否从 claim gate 升级为 research framing upgrader。
3. effectiveness 阶段是否产生更强证据。
4. delivery 阶段是否从 `diaomu` 推进到 `zhuoshi`。
5. 框架是否仍保持 generic。
6. 哪些部分仍是假设、占位或 curated seed。

提交要求：

1. 提交前必须 review 当前 diff。
2. 只 stage 本轮相关文件。
3. commit message 遵守 Lore Commit Protocol。

## 6. 必要步骤与扩展步骤

### 6.1 必要步骤

这些必须完成，否则不能声称下一阶段成立：

1. Phase 0 evidence pack。
2. Phase 1 learning worker protocol 和 schema/sample。
3. Phase 2 task004 learning pack。
4. Phase 3 cognition reframing outputs。
5. Phase 4 至少一个 bounded structural upgrade。
6. Phase 5 至少一轮升级后真实任务闭环。
7. Phase 6 最小通用性回归。
8. Phase 7 记录和 review。

### 6.2 扩展步骤

这些有价值，但不应阻塞主线：

1. 大规模文献自动检索。
2. fulltext excerpt 自动抽取。
3. 多模型语义差异统计。
4. 多 task 大矩阵。
5. 复杂 OPF skill family。
6. GraphRAG 或长期知识图谱。
7. paper draft 自动生成。

## 7. 风险与防护

### 风险 1: 文献 worker 退化为报告润色器

防护：

1. 输出必须是 method/metric/claim/experiment maps。
2. 不接受只有 narrative summary 的结果。

### 风险 2: cognition worker 继续只做 claim gate

防护：

1. 必须产出 evaluator、skill、scenario upgrade request。
2. 必须给出 `zhuoshi_threshold`。

### 风险 3: 技能升级仍是参数调优

防护：

1. structural skill assessment 必须执行。
2. 只改参数的结果标记为 `skill_use_tuning`。

### 风险 4: task004 特化污染框架

防护：

1. framework script 不允许新增 task004 特化分支。
2. task-specific 信息只在 adapter/task/evaluator/skill/evidence seed 中出现。

### 风险 5: 结果仍然很弱

防护：

1. 接受 `diaomu` 结论。
2. 记录为什么不能升级。
3. 将失败转化为下一轮研究设计，而不是包装成果。

## 8. 一口气推进的执行顺序

建议 `$plan-execute` 执行时按以下顺序连续推进，不在小细节上停顿：

1. 先补齐 Phase 0-1 的通用协议和契约。
2. 再生成 Phase 2-3 的 task004 learning/reframing artifacts。
3. 随后只选择一个最小结构性 upgrade，不扩展成大系统。
4. 立即跑 Phase 5 升级后闭环。
5. 跑 Phase 6 最小回归。
6. 最后完成 Phase 7 记录、review、提交建议。

执行中允许降级：

1. 若外部检索不稳定，使用 curated seed，但必须标注。
2. 若 upgraded skill 未提升主指标，仍完成 effectiveness/cognition/delivery 判断。
3. 若 runtime backend 出错，先使用 `pi_gpt55` 主路径，其他 runtime 作为回归而非主线阻塞项。

执行中不允许降级：

1. 不允许 controller 写 cognition。
2. 不允许无 evidence claim。
3. 不允许 task-specific framework patch。
4. 不允许把参数调优称为结构性技能提升。

## 9. 最终验收标准

最低合格：

1. learning worker 和 cognition reframing worker 的 artifact chain 成立。
2. task004 完成至少一轮升级后真实任务闭环。
3. 系统明确判断是否仍为 `diaomu`。
4. 通用回归不被破坏。

良好：

1. evaluator 能记录 boundary trigger、control effort 和 claim support。
2. 新 skill family 与 uniform support 形成清晰对照。
3. cognition worker 形成可执行的下一轮研究设计。

优秀：

1. 新 skill family 在真实 boundary scenario 下产生 primary 或 boundary-stability 改善。
2. 改善不是降低标准或增加不合理代价换来的。
3. 成果等级有证据从 `diaomu` 推进到 `zhuoshi`。

## 10. 本计划的核心结论

下一步不要再问“多跑几轮会不会自然变好”。

应该验证的是：

> 当真实任务暴露出局部参数优化无法提高研究质量时，DaoShuGuo 能否引入外部学习，重构问题定义和方法空间，再让技能、评价和成效进入下一轮更高质量闭环。

这才是本项目从“能跑的框架”走向“自主科研 Agent 实验平台”的关键一步。

## Execution Status — 2026-04-26

Status: executed.

Completed phases:

1. Phase 0 evidence baseline was materialized as `analysis/real_task_001/reframing/input_evidence_pack.yaml` and `analysis/real_task_001/reframing/current_gap_summary.yaml`.
2. Phase 1 protocol and contracts were added through `docs/research-framing-learning-worker-protocol.md`, five research-framing schemas, and five schema samples.
3. Phase 2 task004 learning pack was generated under `analysis/real_task_001/literature/`.
4. Phase 3 cognition reframing was produced by Pi GPT-5.5 and stored under `analysis/real_task_001/reframing/`.
5. Phase 4 implemented the bounded structural attempt `skill.power.voltage_sensitivity_capacity_optimizer_task004` plus evaluator boundary/control-effort metrics.
6. Phase 5 ran upgraded task004 as `run.power.ieee69_hosting_capacity.0029` and produced `analysis/real_task_001_upgrade/`.
7. Phase 6 regression verification passed for real-task-001, reframing, upgrade, light probe, and representative generic full-loop task once the final generic command completed.
8. Phase 7 review and experiment records were updated in `reviews/real-research-loop-convergence-plan-review.md` and `docs/实验过程与讨论记录.md`.

Key result:

The learning/reframing chain successfully moved cognition from claim gate toward research-framing upgrade. The structural skill attempt was real but did not improve primary hosting capacity or trigger a boundary, so the result remains `diaomu / internal_report_ready` rather than `zhuoshi`.
