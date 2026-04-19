# 第一版 Schema 清单与样例规划

## 1. 文档目的

本文件用于把前面几层 spec 收束成第一版正式 schema 工作清单。

它回答的问题是：

- 第一版到底先落哪些 schema
- 哪些是核心
- 哪些暂时只写样例，不急于正式化

## 2. 第一版目标

第一版 schema 的目标不是覆盖全部未来对象，而是支撑 MVP 闭环：

1. 定义任务
2. 定义 evaluator
3. 记录运行
4. 沉淀技能
5. 沉淀认知
6. 做成果分级
7. 组织证据
8. 输出报告

## 3. 第一版核心 schema 清单

### 3.1 必须正式化

1. `task.schema`
2. `evaluator.schema`
3. `run.schema`
4. `skill.schema`
5. `cognition.schema`
6. `taste_assessment.schema`
7. `evidence_bundle.schema`
8. `report.schema`

### 3.2 建议同步定义的子结构

1. `metric_definition`
2. `baseline_strategy`
3. `input_snapshot`
4. `artifact_ref`
5. `object_ref`
6. `claim_scope`

### 3.3 当前仍可延后正式化

1. `cognition_relation` 独立对象
2. `skill_path` 独立对象

### 3.4 已追加正式化的扩展对象

1. `baseline.schema`
2. `agent_trace.schema`
3. `prompt_observation.schema`

## 4. 第一版推荐落地顺序

### Phase A: 事实闭环

先落：

1. `task.schema`
2. `evaluator.schema`
3. `run.schema`

原因：

- 先把事实层稳住
- 先让一次运行能被清楚记录

### Phase B: 资产沉淀

再落：

1. `skill.schema`
2. `cognition.schema`

原因：

- 系统的长期价值来自技能和认知沉淀

### Phase C: 质量门控

再落：

1. `taste_assessment.schema`
2. `evidence_bundle.schema`

原因：

- 没有这两层，很容易重新退化成“有结果就开始写”

### Phase D: 表达输出

最后落：

1. `report.schema`

原因：

- 报告不应领先于事实、资产和质量门控

## 5. 每个 schema 的最低内容要求

### 5.1 Task

最低支持：

- 研究对象
- 问题定义
- 场景边界
- 基线引用
- 约束摘要

### 5.2 Evaluator

最低支持：

- 指标定义
- 基线策略
- 成功判据
- 执行入口

### 5.3 Run

最低支持：

- 任务引用
- evaluator 引用
- 运行状态
- 输入快照
- 结果摘要

### 5.4 Skill

最低支持：

- 能力描述
- 输入输出契约
- 实现引用
- 验证引用

### 5.5 Cognition

最低支持：

- 认知类型
- 认知表达
- 证据引用
- 适用边界

### 5.6 Taste Assessment

最低支持：

- 分级结果
- 分级理由
- claim 上限

### 5.7 Evidence Bundle

最低支持：

- run 引用
- artifact 引用
- claim_scope

### 5.8 Report

最低支持：

- 报告类型
- 摘要
- 证据包引用
- 分级引用

## 6. 样例对象规划

第一版建议每个核心 schema 至少写 2 类样例对象：

### 6.1 正常样例

用于说明该对象在理想情况下应长什么样。

### 6.2 边界样例

用于说明对象在“证据不足、状态受限、部分字段缺失”时应如何表达。

例如：

- `run.completed.sample`
- `run.failed_experiment.sample`
- `cognition.candidate.sample`
- `cognition.failure.sample`
- `taste.zhuoshi.sample`
- `taste.huimo.sample`

## 7. 第一版推荐样例组合

建议至少准备以下样例：

1. 一个 `Task` 样例
2. 一个 `Evaluator` 样例
3. 两个 `Run` 样例
4. 一个 `Skill` 样例
5. 两个 `Cognition` 样例
6. 两个 `Taste Assessment` 样例
7. 一个 `Evidence Bundle` 样例
8. 两个 `Report` 样例

## 8. Schema 目录建议

当后续开始落正式 schema 文件时，建议目录形态为：

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

## 9. 校验策略建议

第一版不必一开始就追求复杂校验器，但至少应支持：

1. 必填字段检查
2. 引用字段格式检查
3. 受控枚举检查
4. 关键对象间引用存在性检查

## 10. 交付顺序建议

当开始写正式 schema 时，建议严格按以下顺序交付：

1. 先写 schema 文档头和对象说明
2. 再写字段定义
3. 再写样例对象
4. 再写校验规则
5. 最后再引入程序化校验器

## 11. 第一版完成标准

第一版 schema 工作不以“字段写得多”为完成，而以以下条件为完成：

1. 一次 MVP 任务可以全程使用这组 schema 表达。
2. 核心对象之间没有循环污染。
3. 报告不能反向污染事实层。
4. 技能、认知和成果等级都可独立存在。
5. 后继者只读 schema 和样例，也能理解系统如何组织研究资产。
