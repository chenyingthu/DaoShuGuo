# DaoShuGuo-v1

本仓库用于设计并实现一个面向电力科研的自主研究 Agent 系统。

它不是单纯的“科研流程自动化”项目，而是一个同时包含以下三重目标的研究与工程计划：

1. 构建一个可被 harness 成“合格科研研究生”的 Agent 系统。
2. 将“技能 - 认知 - 成效”三要素转化为可执行的软件架构。
3. 通过系统运行过程反向研究“AI 辅助电力科研”的规律、边界与方法论。

## 核心思想

- 科研系统的核心不是流程完备，而是资产积累。
- 需要持续积累三类资产：
  - 技能：可复用、可组合、可验证的工具与方法。
  - 认知：对研究对象、规律、边界和机理的理解。
  - 成效：可外部验证、可重复比较的结果改进。
- 系统必须显式建模“品味”，避免用强写作能力掩盖弱研究结果。

## 文档导航

- [docs/项目总设计方案.md](/home/chenying/root-research/DaoShuGuo-v1/docs/项目总设计方案.md)
- [docs/系统模块设计.md](/home/chenying/root-research/DaoShuGuo-v1/docs/系统模块设计.md)
- [docs/运行时执行与状态机规范.md](/home/chenying/root-research/DaoShuGuo-v1/docs/运行时执行与状态机规范.md)
- [docs/研究记录与证据规范.md](/home/chenying/root-research/DaoShuGuo-v1/docs/研究记录与证据规范.md)
- [docs/实验过程与讨论记录.md](/home/chenying/root-research/DaoShuGuo-v1/docs/实验过程与讨论记录.md)
- [docs/持续记录模板.md](/home/chenying/root-research/DaoShuGuo-v1/docs/持续记录模板.md)
- [docs/文献对齐与比较认知升级框架设计.md](/home/chenying/root-research/DaoShuGuo-v1/docs/文献对齐与比较认知升级框架设计.md)
- [docs/数据契约设计总纲.md](/home/chenying/root-research/DaoShuGuo-v1/docs/数据契约设计总纲.md)
- [docs/数据契约版本化与扩展策略.md](/home/chenying/root-research/DaoShuGuo-v1/docs/数据契约版本化与扩展策略.md)
- [docs/核心对象契约草案.md](/home/chenying/root-research/DaoShuGuo-v1/docs/核心对象契约草案.md)
- [docs/资产与证据对象契约草案.md](/home/chenying/root-research/DaoShuGuo-v1/docs/资产与证据对象契约草案.md)
- [docs/对象命名与引用规范.md](/home/chenying/root-research/DaoShuGuo-v1/docs/对象命名与引用规范.md)
- [docs/受控枚举与状态规范.md](/home/chenying/root-research/DaoShuGuo-v1/docs/受控枚举与状态规范.md)
- [docs/第一版Schema清单与样例规划.md](/home/chenying/root-research/DaoShuGuo-v1/docs/第一版Schema清单与样例规划.md)
- [docs/合格科研研究生Agent规范.md](/home/chenying/root-research/DaoShuGuo-v1/docs/合格科研研究生Agent规范.md)
- [docs/科研品味评估框架.md](/home/chenying/root-research/DaoShuGuo-v1/docs/科研品味评估框架.md)
- [docs/工作原则与研发方法.md](/home/chenying/root-research/DaoShuGuo-v1/docs/工作原则与研发方法.md)
- [docs/MVP实施路线图.md](/home/chenying/root-research/DaoShuGuo-v1/docs/MVP实施路线图.md)

## Schema 导航

- [schemas/README.md](/home/chenying/root-research/DaoShuGuo-v1/schemas/README.md)
- [schemas/core/task.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/core/task.schema.yaml)
- [schemas/core/baseline.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/core/baseline.schema.yaml)
- [schemas/core/evaluator.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/core/evaluator.schema.yaml)
- [schemas/core/run.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/core/run.schema.yaml)
- [schemas/assets/skill.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/assets/skill.schema.yaml)
- [schemas/assets/cognition.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/assets/cognition.schema.yaml)
- [schemas/quality/agent_trace.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/agent_trace.schema.yaml)
- [schemas/quality/prompt_observation.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/prompt_observation.schema.yaml)
- [schemas/quality/strategy_comparison.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/strategy_comparison.schema.yaml)
- [schemas/quality/strategy_semantic_comparison.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/strategy_semantic_comparison.schema.yaml)
- [schemas/quality/novelty_assessment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/novelty_assessment.schema.yaml)
- [schemas/quality/cognition_upgrade.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/cognition_upgrade.schema.yaml)
- [schemas/quality/literature_alignment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/literature_alignment.schema.yaml)
- [schemas/quality/paper_record.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/paper_record.schema.yaml)
- [schemas/quality/paper_excerpt.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/paper_excerpt.schema.yaml)
- [schemas/quality/method_card.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/method_card.schema.yaml)
- [schemas/quality/explanation_card.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/explanation_card.schema.yaml)
- [schemas/quality/explanation_alignment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/explanation_alignment.schema.yaml)
- [schemas/quality/taste_assessment.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/taste_assessment.schema.yaml)
- [schemas/quality/evidence_bundle.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/quality/evidence_bundle.schema.yaml)
- [schemas/reporting/report.schema.yaml](/home/chenying/root-research/DaoShuGuo-v1/schemas/reporting/report.schema.yaml)

## 当前定位

当前阶段以项目总纲和方法论固化为主，优先明确：

1. 什么是“合格科研研究生 Agent”。
2. 什么是“高质量、有深度”的研究成果。
3. 如何用最小可行系统验证上述判断。

## 工作原则

- 先定义评价，再做探索。
- 先做最小闭环，再扩展多智能体与复杂记忆。
- 任何认知结论都要绑定证据。
- 任何漂亮表述都不能抬高成果等级。

## 运行入口

- 校验 schema 与样例：
  `python scripts/validate_schemas.py`
- 运行 orchestrator 内置校验：
  `python orchestrator/main.py validate`
- 生成一次成功 demo 闭环：
  `python orchestrator/main.py demo-run --mode success`
- 生成一次失败 demo 闭环：
  `python orchestrator/main.py demo-run --mode failure`
- 生成一次成功真实闭环：
  `python orchestrator/main.py real-run --mode success`
- 生成一次失败真实闭环：
  `python orchestrator/main.py real-run --mode failure`
- 运行弱节点 shunt candidate 技能：
  `python orchestrator/main.py real-run --strategy weak-shunt`
- 生成两次运行的结构化对照分析：
  `python orchestrator/main.py compare-runs --left-run-id <run_id> --right-run-id <run_id>`
- 生成两次运行的语义比较：
  `python orchestrator/main.py compare-semantics --left-run-id <run_id> --right-run-id <run_id>`
- 基于比较结果升级认知：
  `python orchestrator/main.py upgrade-cognition --comparison-dir <dir> --semantic-dir <dir>`
- 生成文献对齐对象：
  `python orchestrator/main.py align-literature --comparison-dir <dir> --semantic-dir <dir>`
- 从种子文献生成文献对象卡片：
  `python orchestrator/main.py build-literature-cards`
- 生成本地认知与文献解释的对齐结果：
  `python orchestrator/main.py align-explanations --cognition-ref <cognition_ref> --literature-dir <dir>`
- 从原始片段输入生成文献 source：
  `python orchestrator/main.py ingest-seed-literature`
- 验证 task001 完整纵向闭环：
  `python orchestrator/main.py verify-task001-pipeline`
