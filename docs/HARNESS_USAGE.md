# Generic Loop Engine Harness 使用指南

> 强制研究记录质量的验证框架

---

## 概述

**Generic Loop Engine with Harness** 是对原有循环引擎的增强版本，添加了**强制输出验证**机制，确保每个 Phase 的输出都是可审查、可追溯、有价值的。

### 核心改进

| 特性 | 原有引擎 | Harness 引擎 |
|------|---------|--------------|
| 输出要求 | 无强制要求 | 强制字段检查 |
| 内容深度 | 不检查 | 检查内容是否过于简略 |
| 验证失败 | 静默通过 | 自动重试或记录失败 |
| 失败胶囊 | 无 | 必须记录局限性 |
| 质量报告 | 无 | 自动生成质量评分 |

---

## 快速开始

### 1. 验证现有运行

检查已完成的运行是否符合质量标准：

```bash
# 验证整个运行目录
python3 scripts/verify_research_quality.py \
  --run-dir runs/task003/run_001 \
  --output report.yaml

# 验证单个文件
python3 scripts/verify_research_quality.py \
  --input runs/task003/run_001/execution_record.yaml \
  --phase skill_execution
```

### 2. 使用 Harness 引擎运行

```bash
# 基本用法（启用验证）
python3 scripts/run_generic_loop_engine_with_harness.py \
  --task-adapter adapters/task003.yaml \
  --workspace-root runs/task003/harness_001 \
  --run-intent "验证 harness 功能"

# 严格模式（验证失败时停止）
python3 scripts/run_generic_loop_engine_with_harness.py \
  --task-adapter adapters/task003.yaml \
  --workspace-root runs/task003/harness_001 \
  --strict

# 禁用验证（向后兼容）
python3 scripts/run_generic_loop_engine_with_harness.py \
  --task-adapter adapters/task003.yaml \
  --workspace-root runs/task003/harness_001 \
  --no-validation
```

---

## 配置 Phase 要求

编辑 `configs/phase_requirements.yaml` 自定义验证规则：

```yaml
phases:
  skill_execution:
    description: "执行技能代码"

    # 强制字段
    must_include:
      - "hypothesis.statement"
      - "skill_implementation.code.structure"
      - "results.primary_metrics"
      - "failure_capsule.known_limitations"
      - "next_actions.immediate"

    # 内容最小长度
    min_content_length: 1000

    # 验证配置
    validation:
      enabled: true
      strict: true        # true = 验证失败必须重试
      max_retries: 3      # 最大重试次数

    # 字段特定要求
    field_requirements:
      hypothesis.statement:
        min_length: 50
        check_vague_words: true

      results.primary_metrics:
        min_properties: 2
```

---

## 质量检查清单

### 必备字段（skill_execution）

- [ ] **hypothesis.statement** - 研究假设陈述（>50字符）
- [ ] **hypothesis.testable_prediction** - 可量化预测（包含数值）
- [ ] **method.description** - 方法描述（>100字符）
- [ ] **skill_implementation.code.structure** - 代码结构（至少1个函数）
- [ ] **results.primary_metrics** - 主要指标（至少2个）
- [ ] **failure_capsule.known_limitations** - 已知局限性（至少1个）
- [ ] **next_actions.immediate** - 下一步行动（至少1个）

### 内容质量标准

- [ ] 不使用 "completed", "done", "ok" 等空泛词汇
- [ ] 提供具体数值（如 11.6%，而不是"降低了一些"）
- [ ] 说明算法名称（如 "贪心算法"，而不是"某种算法"）
- [ ] 记录设计决策和替代方案
- [ ] 承认局限性和失败点

---

## 常见问题

### Q: 验证失败怎么办？

**A:** Harness 会自动重试（最多3次）。如果仍然失败：

1. 查看错误信息，了解缺少哪些字段
2. 根据反馈补充内容
3. 如果反复失败，检查 `configs/phase_requirements.yaml` 是否要求过高

```bash
# 查看详细反馈
python3 scripts/verify_research_quality.py \
  --run-dir runs/task003/run_001 \
  --format markdown
```

### Q: 可以跳过验证吗？

**A:** 可以，但不推荐：

```bash
# 临时禁用
python3 scripts/run_generic_loop_engine_with_harness.py ... --no-validation

# 或在配置中禁用特定 phase
validation:
  enabled: false
```

### Q: 如何降低验证要求？

**A:** 修改 `configs/phase_requirements.yaml`：

```yaml
# 减少必填字段
must_include:
  - "hypothesis.statement"
  # - "skill_implementation.code.structure"  # 注释掉可选字段

# 降低内容长度要求
min_content_length: 500  # 从 1000 降到 500

# 减少重试次数
validation:
  max_retries: 1
```

### Q: 质量报告中的分数怎么算的？

**A:** 基于以下因素：
- 基础分: 100
- 缺失字段: -10/个
- 简略字段: -5/个
- 内容错误: -15/个
- 警告: -2/个
- 超长内容: +0-20（鼓励详细记录）

---

## 故障排除

### 错误: "No requirements found for phase"

检查 `configs/phase_requirements.yaml` 是否包含该 phase 的配置。

### 错误: "Schema validation failed"

检查输出文件是否符合 JSON Schema，可使用：

```bash
# 查看 schema
cat schemas/work_brief.schema.json | grep -A 5 "required"
```

### 错误: "Content too shallow"

提供更多细节：
- ❌ "使用算法优化"
- ✅ "使用贪心算法（Greedy Search）逐步添加无功补偿"

---

## 集成到工作流

### CI/CD 集成

```yaml
# .github/workflows/quality-check.yml
- name: Verify Research Quality
  run: |
    python3 scripts/verify_research_quality.py \
      --run-dir runs/task003/$(ls runs/task003 | tail -1) \
      --score-threshold 70
```

### Makefile 集成

```makefile
verify-quality:
	@python3 scripts/verify_research_quality.py \
		--run-dir $(RUN_DIR) \
		--format markdown \
		--output quality-report.md

run-with-harness:
	@python3 scripts/run_generic_loop_engine_with_harness.py \
		--task-adapter $(ADAPTER) \
		--workspace-root $(WORKSPACE) \
		--strict
```

---

## 参考文档

- [理想研究记录模板](IDEAL_RESEARCH_RECORD_TEMPLATE.md)
- [Harness 实施计划](../plans/GENERIC_LOOP_ENGINE_HARNESS_IMPLEMENTATION_PLAN.md)
- [Phase 配置](../configs/phase_requirements.yaml)
- [JSON Schemas](../schemas/)

---

## 示例

### 高质量输出示例

```yaml
phase: skill_execution
hypothesis:
  statement: "在IEEE69网络的高电压偏差节点添加无功补偿，可以降低网损并改善电压分布"
  rationale: "基于无功功率-电压耦合关系，Q注入可减少线路无功传输"
  testable_prediction: "补偿后网损降低>5%，电压偏差改善>10%"

skill_implementation:
  code:
    main_file: "tasks/task003/candidate_solver.py"
    structure:
      - function: "identify_weak_nodes"
        purpose: "识别电压幅值最低的N个节点，用于后续补偿"
        algorithm: "排序 + 阈值筛选"
        complexity: "O(n log n)"

results:
  primary_metrics:
    loss_before_mw:
      value: 0.224
      unit: "MW"
    loss_after_mw:
      value: 0.198
      unit: "MW"
    improvement_percent:
      value: 11.6
      unit: "%"

failure_capsule:
  known_limitations:
    - limitation: "仅测试单工况(peak load)，无法评估负荷波动下的性能稳定性"
      impact: "无法保证方法鲁棒性"
      severity: "medium"

next_actions:
  immediate:
    - action: "测试多负荷工况（light, peak, evening）"
      rationale: "验证方法鲁棒性"
```

### 低质量输出示例（会被拒绝）

```yaml
phase: skill_execution
hypothesis:
  statement: "补偿可以降低损耗"  # ❌ 太短
  testable_prediction: "变好"     # ❌ 无量化指标

method:
  description: "使用算法优化"      # ❌ 太简略

results:
  primary_metrics: {}             # ❌ 无指标

failure_capsule:                  # ❌ 完全缺失

next_actions:
  immediate: []                   # ❌ 为空
```

---

**版本**: 1.0  
**更新日期**: 2026-04-28
