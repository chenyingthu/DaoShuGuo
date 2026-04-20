# 原文片段抽取与片段级解释对齐实施计划

## 1. 计划目标

本计划用于将当前的文献调研能力从：

- `seed-driven excerpt`
- `method family alignment`
- `explanation card alignment`

推进到：

- 更真实的文献片段来源
- 可维护的片段对象层
- 片段级支持/补充/冲突判断
- 片段证据参与认知升级

当前系统已经具备：

1. `paper_record`
2. `paper_excerpt`
3. `method_card`
4. `explanation_card`
5. `literature_alignment`
6. `explanation_alignment`
7. `novelty_assessment`
8. `cognition_upgrade`

但当前的 `paper_excerpt` 仍然主要来自手工 seed 摘录，而非更真实的文献材料抽取。

本计划的目标是：

> 让系统具备“更真实的片段对象输入 + 片段级解释对齐”的能力，同时不破坏已经成立的基本闭环。

## 2. 范围

### 2.1 纳入范围

- `literature_source` 的进一步使用
- 文献片段对象层增强
- explanation alignment 粒度提升
- cognition upgrade 对片段证据的吸收
- task001 上的最小验证

### 2.2 不纳入范围

- 全自动 PDF 全文解析
- 大规模外部学术数据库同步
- 自动综述生成
- 多任务统一文献知识图谱

## 3. 核心原则

1. 不破坏基本闭环
2. 先做可验证的轻量真实化
3. 片段必须对象化
4. 对齐必须可回链
5. 文献输入能力增强不能替代本地证据

## 4. 当前起点

当前已有基础：

- [literature_source.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/literature_source.schema.yaml)
- [paper_record.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/paper_record.schema.yaml)
- [paper_excerpt.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/paper_excerpt.schema.yaml)
- [method_card.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/method_card.schema.yaml)
- [explanation_card.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/explanation_card.schema.yaml)
- [explanation_alignment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/explanation_alignment.schema.yaml)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)

当前已有运行入口：

- `ingest-seed-literature`
- `build-literature-cards`
- `align-literature`
- `align-explanations`
- `upgrade-cognition`

## 5. 目标能力拆解

本计划要实现的能力分成四块：

### 5.1 文献源层增强

目标：

- 区分 `seed_curated`、`manual_summary`、`abstract_excerpt`
- 允许文献源对象表达更真实的材料类型

### 5.2 片段对象层增强

目标：

- 让 `paper_excerpt` 不只是单条摘要
- 支持片段分类与片段来源追踪

### 5.3 解释对齐增强

目标：

- 对 explanation excerpt 做更细粒度支持/补充/冲突判断
- 在对齐对象中保留片段级证据

### 5.4 认知升级增强

目标：

- 让 `cognition_upgrade` 显式吸收片段级解释对齐结果
- 用片段证据约束认知晋升与 claim 调整

## 6. 实施步骤

### Phase 1: 文献源对象增强

涉及文件：

- [literature_source.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/literature_source.schema.yaml)
- [task001-seed-papers.yaml](/home/chenying/root-research/DaoShuGuo-v1/literature/task001-seed-papers.yaml)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)

执行内容：

- [x] 明确 `source_kind` 的使用规则
- [x] 让 source 层支持更真实的输入类型
- [x] 让卡片生成优先从 source 层而不是 seed 原始列表读取

完成判据：

- [x] `literature/sources/` 下对象足够作为后续唯一输入层

### Phase 2: 片段对象增强

涉及文件：

- [paper_excerpt.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/paper_excerpt.schema.yaml)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)
- `literature/excerpts/*`

执行内容：

- [x] 为 excerpt 增加更明确的来源和粒度表达
- [x] 区分 summary excerpt 与 point excerpt
- [x] 保证 excerpt 可以被 explanation alignment 显式引用

完成判据：

- [x] 每张 explanation card 都至少能映射到多个 excerpt

### Phase 3: 片段级解释对齐增强

涉及文件：

- [explanation_alignment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/explanation_alignment.schema.yaml)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)

执行内容：

- [x] 将当前 `supports/supplements/unclear` 判断继续细化
- [x] 增加对片段粒度的证据引用
- [x] 让 relation 判断更明确地区分“支持”和“仅相似”

完成判据：

- [x] `explanation_alignment` 显式保留片段证据与判断理由

### Phase 4: 认知升级吸收片段证据

涉及文件：

- [cognition_upgrade.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/cognition_upgrade.schema.yaml)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)

执行内容：

- [x] 将片段级解释对齐结果纳入 upgrade 决策
- [x] 提高 upgrade rationale 的证据密度
- [x] 保持 claim_adjustment 的克制

完成判据：

- [x] `cognition_upgrade` 可追溯到 explanation excerpt 级别

### Phase 5: task001 验证

涉及对象：

- `compare_0002`
- `semantic_0001`
- `literature_0001`
- 新生成的 `explanations_*`
- 新生成的 `upgrade_*`

执行内容：

- [x] 重跑文献卡片生成
- [x] 重跑 explanation alignment
- [x] 重跑 cognition upgrade
- [x] 检查 registry 写回

完成判据：

- [x] 生成的新对象链条完整可回溯

## 7. 验收标准

### 7.1 功能验收

- [x] `build-literature-cards` 能生成增强后的 excerpt
- [x] `align-explanations` 能基于片段对象输出结构化判断
- [x] `upgrade-cognition` 能吸收片段对齐结果

### 7.2 质量验收

- [x] 所有新增对象符合 schema
- [x] `python scripts/validate_schemas.py` 通过
- [x] 不引入新的强耦合
- [x] 不破坏既有基本闭环

## 8. 风险

### 风险 1：过度细化 excerpt 导致复杂度膨胀

缓解：

- 只做最小必要粒度
- 不追求全文解析

### 风险 2：片段判断仍然带有主观规则

缓解：

- 先显式化规则
- 后续再引入更细的判别逻辑

### 风险 3：文献层压过本地证据

缓解：

- 文献始终作为参照系，而不是直接替代 evaluator 和 run 证据

## 9. 验证命令

- [x] `python orchestrator/main.py ingest-seed-literature`
- [x] `python orchestrator/main.py build-literature-cards`
- [x] `python orchestrator/main.py align-explanations --cognition-ref <cognition_ref> --literature-dir <dir>`
- [x] `python orchestrator/main.py upgrade-cognition --comparison-dir <dir> --semantic-dir <dir> --literature-dir <dir> --explanation-dir <dir>`
- [x] `python scripts/validate_schemas.py`

## 10. 结论

本计划是当前“文献对齐 + 比较认知升级”子路线的下一步关键推进。

它不是项目最后一步，但很可能是这条子路线从“轻量可运行原型”走向“稳定认知工具层”的阶段性门槛。

## 11. 当前完成说明

本计划当前已经完成：

- `abstract_excerpt` 进入 source 层
- 少量人工整理的 `fulltext_excerpt` 进入 source 层
- source 等级影响 `explanation_alignment.evidence_strength`
- evidence strength 进入 `novelty_assessment`
- `continue_investment` 会因 `high` 证据强度升级为 `prioritize`
- `cognition_upgrade` 和 `upgraded_cognition` 可回链到 excerpt 级证据

尚未纳入本计划范围的是：

- 自动 PDF/HTML 全文解析
- 大规模外部数据库检索
