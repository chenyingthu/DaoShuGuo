# Ralph Context Snapshot: Evidence-Stratified Cognition Upgrade

## Task Statement

推进以下三步，并收敛成可验证状态：

1. `abstract_excerpt` 参与证据强度控制
2. 引入少量 `fulltext_excerpt`
3. 让不同证据等级真正影响 `cognition_upgrade`

## Desired Outcome

当前框架必须证明：

- 文献输入源可区分 `seed_curated`、`manual_summary`、`abstract_excerpt`、`fulltext_excerpt`
- 文献卡片生成优先使用更高质量 source
- explanation alignment 输出 `evidence_strength`
- cognition upgrade 和 novelty assessment 吸收 `evidence_strength`
- 完整 task001 纵向链路可验证

## Known Facts / Evidence

- Git 已初始化，初始 commit 为 `9339b29`
- 已有 `task001` 真实 pandapower 闭环
- 已有 `weak_bus_shunt_optimizer`
- 已有 `strategy_comparison`、`strategy_semantic_comparison`
- 已有 `literature_alignment`、`explanation_alignment`
- 已有 `literature_source`、`paper_excerpt`、`method_card`、`explanation_card`
- 已有 `validate_schemas.py --artifacts literature-alignment-plan`

## Constraints

- 基本闭环优先，不继续无限扩展
- 不破坏现有 run / analysis / cognition 研究资产
- 文献层不得替代 evaluator 和本地 run 证据
- 扩展能力必须可验证

## Unknowns / Open Questions

- 当前 `fulltext_excerpt` 仍是人工整理的全文片段输入，不是自动 PDF/HTML 抽取
- 后续是否需要真正自动化全文抽取，当前不作为本轮目标

## Likely Codebase Touchpoints

- `orchestrator/main.py`
- `scripts/validate_schemas.py`
- `literature/task001-source-overlays.yaml`
- `literature/raw_excerpts/task001/*.yaml`
- `schemas/quality/*.yaml`
- `plans/literature-alignment-cognition-upgrade-plan.md`
- `plans/literature-excerpt-alignment-plan.md`
- `README.md`
