# Schemas

本目录存放项目第一版正式 schema 规格和样例对象。

当前阶段已经覆盖 MVP 所需的核心对象：

1. `task.schema.yaml`
2. `evaluator.schema.yaml`
3. `run.schema.yaml`
4. `skill.schema.yaml`
5. `cognition.schema.yaml`
6. `taste_assessment.schema.yaml`
7. `evidence_bundle.schema.yaml`
8. `report.schema.yaml`

## 目录结构

```text
schemas/
├── core/
│   ├── baseline.schema.yaml
│   ├── task.schema.yaml
│   ├── evaluator.schema.yaml
│   └── run.schema.yaml
├── assets/
│   ├── skill.schema.yaml
│   └── cognition.schema.yaml
├── quality/
│   ├── agent_trace.schema.yaml
│   ├── prompt_observation.schema.yaml
│   ├── strategy_comparison.schema.yaml
│   ├── strategy_semantic_comparison.schema.yaml
│   ├── novelty_assessment.schema.yaml
│   ├── cognition_upgrade.schema.yaml
│   ├── literature_alignment.schema.yaml
│   ├── paper_record.schema.yaml
│   ├── paper_excerpt.schema.yaml
│   ├── method_card.schema.yaml
│   ├── explanation_card.schema.yaml
│   ├── explanation_alignment.schema.yaml
│   ├── taste_assessment.schema.yaml
│   └── evidence_bundle.schema.yaml
├── reporting/
│   └── report.schema.yaml
└── samples/
    ├── task.sample.yaml
    ├── baseline.sample.yaml
    ├── evaluator.sample.yaml
    ├── run.completed.sample.yaml
    ├── run.failed_experiment.sample.yaml
    ├── skill.baseline.sample.yaml
    ├── skill.sample.yaml
    ├── skill.candidate.sample.yaml
    ├── skill.weak_shunt.sample.yaml
    ├── cognition.candidate.sample.yaml
    ├── cognition.failure.sample.yaml
    ├── taste.zhuoshi.sample.yaml
    ├── taste.huimo.sample.yaml
    ├── agent_trace.sample.yaml
    ├── prompt_observation.sample.yaml
    ├── evidence.sample.yaml
    ├── report.note.sample.yaml
    └── report.memo.sample.yaml
```

## 说明

- 这里的 schema 目前采用项目内自定义 YAML 规格格式。
- 目标是先稳定对象边界、必填字段、引用形式和校验规则。
- 后续如有必要，再转成程序可校验的 JSON Schema 或其他格式。
- 当前提供了一个最小校验器：`python scripts/validate_schemas.py`

## 当前约束

- `object_id` 与文件路径分离。
- `object_version` 与 `schema_version` 分离。
- 样例对象必须符合既有文档中的命名、状态、引用和边界规则。
- `run` 只记录事实摘要，不记录高层研究结论。
- `report` 不得反向定义事实层对象。
- `taste_assessment` 必须独立存在，不能藏在报告正文里。
