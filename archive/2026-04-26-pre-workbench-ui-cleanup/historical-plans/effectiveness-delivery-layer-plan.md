# 成效与交付层计划：验证、应用与学术成果收口

## 1. 计划目标

本计划的目标不是再增加新的 task 或新的 solver，而是补齐最初设计中的第三个核心要素：

> `成效（Effectiveness）`

这里的“成效”不再被理解为单个指标是否提升，而是：

> 当前工作是否已经形成较为完备的验证、测试、应用说明，并进一步具备生成高质量报告、专利、论文等学术成果的条件。

因此，本计划要建设的不是单一 evaluator，而是一个：

- `验证完备性判断层`
- `应用相关性判断层`
- `成果交付 readiness 判断层`

## 2. 为什么这一层现在必须补

到当前阶段，项目已经具备：

- 技能开发与写回
- 本地认知提炼
- failure taxonomy
- 文献对齐与外部参照认知升级

但仍然缺少一个关键能力：

> 如何判断“这些技能与认知，是否已经足以形成可信、完整、可交付的研究成果”。

如果不补这一层，会出现两个问题：

### 2.1 结果存在，但交付无门

系统可能已经有：

- run
- compare
- semantic
- cognition
- literature alignment

但仍然回答不了：

- 现在能不能写论文
- 哪部分更适合专利
- 哪部分只能做内部技术报告
- 还缺哪些验证才能对外表达

### 2.2 研究进展存在，但质量边界不清

系统可能知道：

- 某个 candidate 比 baseline 好
- 某条认知得到文献支持

但不知道：

- 这是不是已经经过充分测试
- 是局部现象还是已足够稳健
- 是原型级成果、方法级成果，还是仅仅是内部线索

所以，当前阶段最需要的不是更多“结果”，而是：

> 把已有结果组织成完整的验证与交付系统。

## 3. 成效层的重新定义

本计划将“成效层”明确定义为四个组成部分：

### 3.1 validation completeness

当前工作是否已经经过足够的验证。

### 3.2 application relevance

当前结果在什么应用场景下有意义，在什么场景下还没有意义。

### 3.3 deliverable readiness

当前结果是否已经足以形成某类成果交付。

### 3.4 claim routing

当前证据最适合流向：

- 报告
- 专利
- 论文
- 还是继续内部研究

## 4. 本计划要回答的关键问题

1. 什么叫“验证充分”
2. 什么叫“应用相关”
3. 什么叫“论文 ready”
4. 什么叫“专利 ready”
5. 什么叫“只适合内部报告”
6. 如何让 skill / cognition / effectiveness 三者真正联动

## 5. 本计划的范围

本计划聚焦：

- validation matrix
- application assessment
- deliverable package
- claim routing
- readiness verifier

本计划暂不做：

- 自动论文全文写作系统
- 自动专利撰写系统
- 投稿策略自动推荐
- 法律意义上的专利可授权性分析

第一版目标是：

> 能判断“当前工作更适合哪类成果交付，以及还缺什么”。

## 6. 现有可复用基础

当前项目已经有许多可直接复用的对象：

### 6.1 结果层对象

- run
- evidence_bundle
- taste_assessment
- report

### 6.2 比较层对象

- strategy_comparison
- strategy_semantic_comparison

### 6.3 认知层对象

- cognition
- cognition_upgrade
- novelty_assessment
- literature_alignment
- explanation_alignment

### 6.4 已有实验材料

- task002：迁移 + failure probe
- task003：任务接入 + failure taxonomy + literature alignment
- task004：边界判断 + boundary discipline + literature alignment

因此，本计划不应重造上述对象，而应在其之上建设“验证与交付判断层”。

## 7. 推荐新增对象

### 7.1 validation_plan

用于表达：

- 当前研究对象需要哪些验证
- 哪些验证已完成
- 哪些验证缺失
- 哪些缺失会阻止某类交付

### 7.2 experiment_matrix

用于表达：

- baseline
- candidate
- failure probes
- application cases
- boundary cases

之间的测试覆盖关系。

### 7.3 application_assessment

用于表达：

- 当前结果适用于什么场景
- 不适用于什么场景
- 应用价值和应用边界是什么

### 7.4 deliverable_package

用于表达：

- 当前最适合的成果形态
- 支撑该成果形态的证据
- 缺失项
- readiness level

### 7.5 claim_routing

用于表达：

- 该工作现在应流向：
  - internal report
  - patent candidate
  - paper candidate
  - continue research

## 8. 推荐 readiness 级别

第一版建议采用简单分级。

### 8.1 internal_report_ready

说明：

- 结果已有局部价值
- 但验证尚不充分
- 适合内部交流和归档

### 8.2 patent_candidate

说明：

- 技术方案或结构路径有新意
- 有一定验证支持
- 但学术机理未必成熟

### 8.3 paper_candidate

说明：

- 验证较完整
- 对照和边界较充分
- 有清晰认知线和文献定位

### 8.4 not_ready

说明：

- 当前结果还不能形成稳定对外交付

## 9. 推荐 validation 维度

第一版至少覆盖以下维度：

1. baseline coverage
2. candidate coverage
3. failure coverage
4. boundary coverage
5. literature support
6. explanation support
7. application note completeness
8. reproducibility status

## 10. 推荐 application assessment 维度

第一版建议至少判断：

1. 当前工作对应什么工程场景
2. 当前场景是否只是代表性仿真
3. 结果离工程应用还有哪些差距
4. 应用假设和限制是什么

## 11. 推荐 deliverable routing 逻辑

第一版建议遵循：

### 11.1 报告优先

任何已完成的工作都应至少能进入内部报告体系。

### 11.2 专利偏“技术路径新颖”

如果：

- 技能方案有新结构
- 有初步验证
- 但学理未完全成熟

则可路由为 `patent_candidate`。

### 11.3 论文偏“验证充分 + 认知清楚”

如果：

- 对照较充分
- failure / boundary 清楚
- 有 literature / explanation support
- 结果与认知链完整

则可路由为 `paper_candidate`。

## 12. 推荐本阶段先覆盖的对象

第一版建议先在以下已有主线对象上试运行：

- task003 success / failure / literature upgrade
- task004 boundary / failure / literature upgrade

原因：

- task003 更像“方法与任务接入型成果”
- task004 更像“边界判断型成果”

二者足够体现不同交付面。

## 13. 实施步骤

## Phase 1: 成效层对象设计

目标：

把“验证、应用、交付”从口头判断变成显式对象。

执行内容：

- [x] 定义 `validation_plan`
- [x] 定义 `experiment_matrix`
- [x] 定义 `application_assessment`
- [x] 定义 `deliverable_package`
- [x] 定义 `claim_routing`

完成判据：

- [x] 至少形成一版对象定义或最小 schema 草案

## Phase 2: task003 / task004 validation matrix

目标：

把已有 task003/004 结果组织成验证矩阵。

执行内容：

- [x] 为 task003 生成 validation plan
- [x] 为 task004 生成 validation plan
- [x] 建 experiment matrix
- [x] 明确已覆盖与未覆盖项

完成判据：

- [x] 能明确说出每条主线当前缺什么验证

## Phase 3: application assessment

目标：

判断当前结果在应用层面的意义和边界。

执行内容：

- [x] 为 task003 生成 application assessment
- [x] 为 task004 生成 application assessment
- [x] 明确应用假设与限制

完成判据：

- [x] task003 / task004 都能输出“适用场景 + 不适用场景”

## Phase 4: deliverable routing

目标：

判断当前结果最适合流向哪类成果。

执行内容：

- [x] 为 task003 生成 deliverable package
- [x] 为 task004 生成 deliverable package
- [x] 输出 claim routing

完成判据：

- [x] 至少能区分：
  - internal_report_ready
  - patent_candidate
  - paper_candidate
  - not_ready

## Phase 5: verifier 与收口

目标：

让成效层也进入统一验证。

执行内容：

- [x] 增加最小 verifier
- [x] 扩展 integration checks
- [x] 更新实验记录和设计文档

完成判据：

- [x] skill / cognition / effectiveness 三层在对象层上完成闭环

## 14. 成功标准

以下条件同时满足，视为本计划成功：

1. 成效层有显式对象
2. task003 / task004 都完成 validation assessment
3. task003 / task004 都完成 application assessment
4. 至少一种 deliverable routing 成立
5. verifier 与 integration checks 覆盖新层

## 15. 风险

### 风险 1：把“成效”重新缩成指标

缓解：

- 明确区分结果指标与交付 readiness

### 风险 2：过早生成论文/专利壳子

缓解：

- 第一版只做 readiness 判断，不做全文生成

### 风险 3：对象层过重

缓解：

- 第一版保持最小对象集
- 优先做 task003 / task004 的试运行

## 16. 当前结论

本计划的意义在于：

> 把“技能 - 认知 - 成效”中的第三层真正补完整，让系统不只是会产生结果和认知，还能判断这些结果和认知是否已经足以形成可信交付。 
