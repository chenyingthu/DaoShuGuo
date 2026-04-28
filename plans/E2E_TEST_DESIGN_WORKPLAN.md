# Generic Loop Engine Harness E2E 测试设计工作计划

> 通过苏格拉底式提问深入分析，制定真实有效的端到端测试策略

**版本**: 1.0  
**日期**: 2026-04-28  
**状态**: 已实施并通过验证

---

## 第一部分：苏格拉底式问题分析

### 1.1 核心问题：什么是真正的 E2E 测试？

**Q1: 单元测试和 E2E 测试的本质区别是什么？**

| 维度 | 单元测试 | E2E 测试 |
|------|---------|---------|
| 测试目标 | 验证单个组件行为 | 验证整个系统流程 |
| 依赖关系 | Mock 外部依赖 | 使用真实依赖 |
| 验证内容 | 函数输入输出 | 用户场景/业务流程 |
| 环境要求 | 隔离环境 | 接近生产环境 |
| 价值体现 | 开发者信心 | 用户价值验证 |

**当前问题识别**:  
现有的 `test_harness_integration.py` 是**单元测试**，它：
- Mock 了 Validation Agent 的行为
- 使用 `unittest.mock.patch` 替换真实组件
- 只验证引擎调用逻辑，不验证真实数据流

这不是 E2E 测试，因为它没有回答核心问题："Harness 是否真的能提升研究记录质量？"

---

**Q2: E2E 测试的目标是什么？**

E2E 测试的目标是回答：
1. **功能验证**: Harness 是否能强制要求特定字段？
2. **质量提升**: 有 Harness 的输出是否比无 Harness 的质量更高？
3. **失败处理**: 验证失败时系统如何响应？
4. **用户价值**: 最终生成的研究记录是否更完整、可追溯？

**关键洞察**:  
E2E 测试必须对比"有 Harness"和"无 Harness"的输出，才能证明 Harness 的价值。

---

**Q3: 测试数据应该从哪里来？**

分析三种选择：

**A. Mock 数据** (❌ 不适合 E2E)
- 优点：可控、快速
- 缺点：无法反映真实场景，无法验证实际改进

**B. Fixture 数据** (✅ 适合回归测试)
- 优点：可重复、稳定
- 缺点：静态，无法测试动态行为

**C. 真实 Task 运行** (✅ E2E 必需)
- 优点：验证真实工作流程
- 缺点：耗时、依赖外部环境、可能有不确定性

**决策**: E2E 测试应使用真实 Task，但选择简单的 fixture task 以降低不确定性。

---

**Q4: 如何量化验证 Harness 的价值？**

这是最关键的问题。Harness 的价值不能只是"感觉更好"，必须可量化。

**量化指标设计**：

```yaml
质量维度:
  字段完整度:
    - 必填字段覆盖率 (required fields / total required)
    - 可选字段填充率 (optional fields filled / total optional)
  
  内容深度:
    - 平均内容长度 (chars per field)
    - 具体数值出现次数 (quantitative metrics count)
    - 空洞词汇出现次数 (vague words count)
  
  结构规范:
    - Schema 验证通过率
    - 字段类型正确率
  
  可追溯性:
    - 决策记录完整度
    - 失败胶囊记录率
```

---

### 1.2 对比实验设计

**核心假设**: 有 Harness 的输出质量显著高于无 Harness 的输出。

**实验设计**: A/B 对比测试

```
对照组 (无 Harness):
  - 使用原 GenericLoopEngine
  - 不验证输出
  - 记录所有 phase 输出
  - 计算质量基线分数

实验组 (有 Harness):
  - 使用 GenericLoopEngineWithHarness
  - 启用验证
  - 记录所有 phase 输出
  - 计算质量分数

对比分析:
  - 质量分数提升幅度
  - 字段完整度变化
  - 内容深度变化
  - 失败处理效果
```

---

## 第二部分：已完成修改总结

### 2.1 修改了什么？

#### 1. Validation Agent (`agents/validation_agent.py`)
**目的**: 提供自动化的输出质量验证能力

**核心功能**:
- JSON Schema 验证（结构正确性）
- 强制字段检查（完整性）
- 内容深度检查（质量）
- 反馈生成（可行动建议）

**关键设计决策**:
```python
# 为什么要检查"空洞词汇"？
vague_words = ["done", "completed", "ok", "some", "certain"]
# 因为这些词是"研究应付"的典型标志

# 为什么要区分 missing_fields 和 shallow_fields？
# 因为修复策略不同：
# - missing: 要求 AI 补充字段
# - shallow: 要求 AI 提供具体细节
```

#### 2. Phase Requirements 配置 (`configs/phase_requirements.yaml`)
**目的**: 明确定义每个 phase 的输出要求

**设计原则**:
```yaml
# 为什么用 YAML 而不是代码？
# - 非技术人员可调整
# - 运行时可修改
# - 版本控制友好

# 为什么要有 min_content_length？
# - 防止"一句话糊弄"
# - 量化质量门槛
```

#### 3. JSON Schemas (`schemas/*.schema.json`)
**目的**: 定义数据结构规范

**覆盖范围**:
- `work_brief.schema.json` - 工作简报
- `execution_record.schema.json` - 执行记录
- `assessment_packet.schema.json` - 评估报告
- `skill_implementation.schema.json` - 技能实现

#### 4. Harness 引擎 (`scripts/run_generic_loop_engine_with_harness.py`)
**目的**: 在引擎层面集成验证 harness

**核心改进**:
```python
# 为什么要在引擎层面集成，而不是 Agent 层面？
# 1. 不依赖 Agent 自觉
# 2. 统一的验证标准
# 3. 失败时自动处理（重试/记录）

# 为什么要有重试机制？
# - LLM 不是 100% 可靠
# - 给 AI 机会修正错误
# - 避免单次失败导致整个流程停止

# 为什么要有失败胶囊？
# - 即使验证失败也要记录
# - 为后续分析提供数据
# - 体现"失败也是研究"的理念
```

#### 5. 质量验证工具 (`scripts/verify_research_quality.py`)
**目的**: 事后验证研究记录质量

**用途**:
- 手动检查已完成运行的质量
- 生成质量报告
- 识别改进点

### 2.2 为什么这样修改？

**根本原因**: 原有引擎存在"形式大于内容"的问题

**问题表现**:
```yaml
# 典型的低质量输出
phase: skill_execution
status: completed
# 没了...
```

**后果**:
- 导师无法判断研究质量
- 3 个月后无法复现决策
- 技能无法迭代改进
- 研究变成"出工不出力"

**解决方案逻辑**:
1. **强制要求** → 通过 harness 强制执行
2. **自动验证** → Validation Agent 检查
3. **反馈循环** → 失败时提供反馈并允许重试
4. **失败记录** → 即使失败也要记录原因

---

## 第三部分：E2E 测试设计方案

### 3.1 测试策略

#### 总体思路

使用**真实 fixture task**运行完整工作流，对比"有 Harness"和"无 Harness"的输出质量。

**为什么选择 fixture task？**
- 真实但可控（不像真实 task 那样不确定）
- 运行时间短（便于迭代）
- 结果可预期（便于验证）

#### 测试层次

```
Level 1: 单个 Phase 验证
  - 测试每个 phase 的验证逻辑
  - 使用预先准备好的输入数据
  - 验证输出是否符合要求

Level 2: 多 Phase 工作流验证
  - 测试 phase 间的数据传递
  - 验证状态管理
  - 测试失败传播

Level 3: 完整循环验证
  - 从 skill_change_request 到 loop_routing_decision
  - 验证完整研究流程
  - 对比有/无 harness 的输出
```

### 3.2 测试用例设计

#### Test Case 1: 字段完整性验证

**目标**: 验证 Harness 能强制要求必填字段

**步骤**:
1. 准备一个不完整的 work_brief（缺少 hypothesis.rationale）
2. 使用 Validation Agent 验证
3. 验证：
   - 返回 valid=False
   - missing_fields 包含 "hypothesis.rationale"
   - feedback 提示缺少该字段

**期望结果**: 验证失败，给出明确反馈

---

#### Test Case 2: 内容深度验证

**目标**: 验证 Harness 能检测"空洞内容"

**步骤**:
1. 准备一个 work_brief，其中 hypothesis.statement = "ok"
2. 使用 Validation Agent 验证
3. 验证：
   - 返回 valid=False
   - shallow_fields 包含 "hypothesis.statement"
   - feedback 提示内容过于简略

**期望结果**: 检测出空洞内容

---

#### Test Case 3: 重试机制验证

**目标**: 验证引擎在验证失败时能自动重试

**步骤**:
1. 配置一个会失败的 worker（故意输出不完整）
2. 运行引擎，观察重试行为
3. 验证：
   - 最多重试 max_retries 次
   - 每次重试的 prompt 包含反馈
   - 最终生成失败胶囊

**期望结果**: 正确执行重试逻辑

---

#### Test Case 4: A/B 对比测试

**目标**: 证明 Harness 能提升输出质量

**步骤**:
1. **基线组**: 运行无 Harness 的引擎
   - 记录所有 phase 输出
   - 使用 Validation Agent 计算质量分数

2. **实验组**: 运行有 Harness 的引擎
   - 记录所有 phase 输出
   - 计算质量分数

3. **对比分析**:
   - 质量分数提升 > 50%
   - 必填字段覆盖率 100% (实验组) vs < 60% (基线组)
   - 内容深度提升 > 100%

**期望结果**: 实验组质量显著高于基线组

---

#### Test Case 5: 真实任务验证

**目标**: 验证在真实场景中 Harness 依然有效

**步骤**:
1. 选择 task007_fixture（简单、快速、稳定）
2. 运行完整工作流
3. 检查每个 phase 的输出
4. 验证所有强制字段存在
5. 计算质量分数

**期望结果**: 所有 phase 通过验证，质量分数 > 80

---

### 3.3 质量评分算法

```python
def calculate_quality_score(result: ValidationResult) -> float:
    """
    计算质量分数

    评分逻辑:
    - 基础分: 100
    - 缺失字段: -10/个
    - 简略字段: -5/个
    - 内容错误: -15/个
    - 警告: -2/个
    - 超长内容: +0-20（鼓励详细记录）
    """
    score = 100.0
    score -= len(result.missing_fields) * 10
    score -= len(result.shallow_fields) * 5
    score -= len(result.content_errors) * 15
    score -= len(result.warnings) * 2

    # 内容长度加分
    if result.min_required_length > 0:
        length_ratio = min(result.content_length / result.min_required_length, 2.0)
        score += (length_ratio - 1.0) * 10

    return max(0.0, min(100.0, score))
```

---

## 第四部分：实施计划

### 4.1 Phase 1: 测试基础设施 (Day 1-2)

**任务 1.1**: 创建测试工具函数
```python
# tests/e2e_utils.py
def run_engine_with_harness(task_id: str) -> Path:
    """运行带 Harness 的引擎，返回输出目录"""
    ...

def run_engine_without_harness(task_id: str) -> Path:
    """运行无 Harness 的引擎，返回输出目录"""
    ...

def calculate_quality_metrics(run_dir: Path) -> dict:
    """计算运行质量指标"""
    ...
```

**验收标准**:
- [x] 工具函数可独立调用
- [x] 返回结构化数据
- [x] 有完整的错误处理

---

**任务 1.2**: 准备测试数据集
```yaml
# tests/fixtures/low_quality_work_brief.yaml
# 用于验证检测低质量输出
phase: skill_execution
hypothesis:
  statement: "test"  # 太短
results:
  primary_metrics: {}  # 为空

# tests/fixtures/high_quality_work_brief.yaml
# 用于验证通过高质量输出
phase: skill_execution
hypothesis:
  statement: "在IEEE69网络的高电压偏差节点添加无功补偿..."
  testable_prediction: "补偿后网损降低 > 5%"
# ... 完整字段
```

**验收标准**:
- [x] 至少 3 个低质量样本
- [x] 至少 3 个高质量样本
- [x] 覆盖所有 phase 类型

---

### 4.2 Phase 2: 核心测试用例 (Day 3-4)

**任务 2.1**: 实现单个 Phase 验证测试
```python
# tests/test_harness_phase_validation.py
class TestPhaseValidation:
    def test_missing_required_fields(self):
        """测试检测缺失必填字段"""
        ...

    def test_shallow_content(self):
        """测试检测空洞内容"""
        ...

    def test_valid_output(self):
        """测试验证通过"""
        ...
```

**验收标准**:
- [x] 所有测试用例通过
- [x] 覆盖 missing_fields 场景
- [x] 覆盖 shallow_fields 场景
- [x] 覆盖 valid 场景

---

**任务 2.2**: 实现重试机制测试
```python
# tests/test_harness_retry_mechanism.py
class TestRetryMechanism:
    def test_max_retries(self):
        """测试最多重试次数"""
        ...

    def test_retry_prompt_contains_feedback(self):
        """测试重试 prompt 包含反馈"""
        ...

    def test_failure_capsule_on_max_retries(self):
        """测试最终生成失败胶囊"""
        ...
```

**验收标准**:
- [x] 验证重试次数限制
- [x] 验证反馈传递
- [x] 验证失败胶囊生成

---

### 4.3 Phase 3: A/B 对比测试 (Day 5-6)

**任务 3.1**: 实现基线测量
```python
# tests/test_harness_ab_comparison.py
def test_baseline_quality_without_harness():
    """测量无 Harness 时的基线质量"""
    run_dir = run_engine_without_harness("task007_fixture")
    metrics = calculate_quality_metrics(run_dir)

    # 记录基线数据
    print(f"基线质量分数: {metrics['average_score']}")
    print(f"必填字段覆盖率: {metrics['required_coverage']}")

    return metrics
```

**验收标准**:
- [x] 成功运行无 Harness 引擎
- [x] 计算出基线质量分数
- [x] 记录详细指标

---

**任务 3.2**: 实现实验组测量
```python
def test_harness_quality_improvement():
    """测量有 Harness 时的质量提升"""
    run_dir = run_engine_with_harness("task007_fixture")
    metrics = calculate_quality_metrics(run_dir)

    # 记录实验组数据
    print(f"实验组质量分数: {metrics['average_score']}")
    print(f"必填字段覆盖率: {metrics['required_coverage']}")

    return metrics
```

**验收标准**:
- [x] 成功运行带 Harness 引擎
- [x] 计算出实验组质量分数
- [x] 记录详细指标

---

**任务 3.3**: 实现对比分析
```python
def test_quality_improvement_significant():
    """验证质量提升显著"""
    baseline = test_baseline_quality_without_harness()
    experiment = test_harness_quality_improvement()

    # 验证提升幅度
    score_improvement = (
        (experiment['average_score'] - baseline['average_score'])
        / baseline['average_score'] * 100
    )

    assert score_improvement > 50, f"质量提升 {score_improvement}% 不足 50%"
    assert experiment['required_coverage'] == 100, "必填字段未完全覆盖"
```

**验收标准**:
- [x] 质量提升 > 50%
- [x] 必填字段覆盖率 = 100%
- [x] 生成对比报告

---

### 4.4 Phase 4: 端到端集成测试 (Day 7)

**任务 4.1**: 实现完整工作流测试
```python
# tests/test_harness_e2e_full_workflow.py
class TestHarnessEndToEnd:
    def test_complete_workflow_with_harness(self):
        """测试带 Harness 的完整工作流"""
        test = EndToEndTest(
            task_id="task007_fixture",
            backend="deterministic",
            verbose=True
        )
        result = test.run()

        # 验证所有 phase 通过
        assert result['passed_phases'] == result['total_phases']
        # 验证质量分数达标
        assert result['average_score'] >= 80
```

**验收标准**:
- [x] 完整工作流运行成功
- [x] 所有 phase 通过验证
- [x] 质量分数 >= 80

---

**任务 4.2**: 生成测试报告
```python
def generate_e2e_report():
    """生成 E2E 测试报告"""
    report = {
        "test_summary": {
            "total_tests": N,
            "passed": N,
            "failed": N
        },
        "quality_comparison": {
            "without_harness": baseline_metrics,
            "with_harness": experiment_metrics,
            "improvement": "XX%"
        },
        "conclusion": "Harness 显著提升了研究记录质量"
    }
```

**验收标准**:
- [x] 报告包含所有关键指标
- [x] 报告格式清晰
- [x] 报告可导出为 Markdown/YAML

---

## 第五部分：验证标准

### 5.1 功能验证

| 验证项 | 验证方法 | 通过标准 |
|--------|---------|---------|
| 强制字段检查 | 提交缺少字段的输出 | 被拒绝并提示 |
| 内容深度检查 | 提交"done"/"ok"内容 | 被标记为 shallow |
| 重试机制 | 故意失败 3 次 | 重试 3 次后记录失败胶囊 |
| Schema 验证 | 提交不符合 schema 的输出 | 验证失败 |

### 5.2 质量验证

| 指标 | 基线 (无 Harness) | 目标 (有 Harness) | 验证方法 |
|------|------------------|------------------|---------|
| 平均质量分数 | ~40-60 | >= 80 | 运行后计算 |
| 必填字段覆盖率 | ~40-70% | 100% | 统计缺失字段 |
| 空洞内容比例 | ~30-50% | < 10% | 统计 shallow_fields |
| 可追溯字段比例 | ~20-40% | > 80% | 检查 failure_capsule |

### 5.3 对比验证

**核心断言**: 有 Harness 的质量分数应比无 Harness 高至少 50%。

**验证公式**:
```
improvement = (score_with - score_without) / score_without * 100%
improvement >= 50%
```

---

## 第六部分：风险与缓解

### 风险 1: 真实任务运行时间过长

**风险**: 使用真实 task 可能导致测试运行时间 > 30 分钟

**缓解**:
- 使用 fixture task（简单、快速）
- 设置超时机制（单个 phase < 5 分钟）
- 提供"快速模式"选项（跳过耗时步骤）

### 风险 2: 测试结果不稳定

**风险**: LLM 输出有随机性，可能导致测试结果不稳定

**缓解**:
- 使用 deterministic backend（固定种子）
- 多次运行取平均值
- 定义"统计显著"标准（p < 0.05）

### 风险 3: 质量评分主观性

**风险**: 质量分数可能无法完全反映实际改进

**缓解**:
- 多维度指标（完整度、深度、规范性）
- 人工抽样验证
- 定期调整评分权重

---

## 第七部分：交付物清单

### 代码文件

```
tests/
├── e2e_utils.py                      # E2E 测试工具函数
├── test_harness_phase_validation.py  # Phase 验证测试
├── test_harness_retry_mechanism.py   # 重试机制测试
├── test_harness_ab_comparison.py     # A/B 对比测试
├── test_harness_e2e_full_workflow.py # 完整工作流测试
└── fixtures/
    ├── low_quality/                  # 低质量测试数据
    │   ├── work_brief_minimal.yaml
    │   ├── work_brief_shallow.yaml
    │   └── work_brief_incomplete.yaml
    └── high_quality/                 # 高质量测试数据
        ├── work_brief_complete.yaml
        ├── execution_record_complete.yaml
        └── assessment_packet_complete.yaml
```

### 文档文件

```
plans/
├── E2E_TEST_DESIGN_WORKPLAN.md       # 本文件
└── E2E_TEST_REPORT.md                # 测试报告模板

docs/
└── HARNESS_E2E_TESTING.md            # E2E 测试指南
```

---

## 第八部分：总结

### 8.1 核心洞察

1. **E2E 测试 ≠ 单元测试**: E2E 测试必须使用真实依赖，验证真实场景
2. **质量必须可量化**: 不能仅凭感觉，必须有明确的评分标准
3. **对比实验是关键**: 只有对比"有/无 Harness"才能证明价值
4. **失败也是结果**: 测试不仅要验证成功，还要验证失败处理

### 8.2 实施建议

1. **先基础设施**: 先建测试工具函数和数据集
2. **再核心测试**: 逐个实现测试用例
3. **最后集成**: 组合成完整测试套件
4. **持续验证**: 每次修改后运行 E2E 测试

### 8.3 成功标准

- [x] 所有测试用例通过
- [x] 质量提升 > 50%
- [x] 必填字段覆盖率 = 100%
- [x] 生成详细测试报告

---

**计划制定**: Claude (基于苏格拉底式提问)  
**审核**: 待定  
**实施**: Codex plan-execute (2026-04-28)
