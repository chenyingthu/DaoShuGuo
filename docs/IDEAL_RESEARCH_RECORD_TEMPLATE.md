# 理想研究记录模板

> 基于 AutoResearchFlow/Claw 最佳实践 + AGENTS.md 15.3 验收标准

---

## 设计原则

1. **文件存在 ≠ 完成** - 必须包含可审查的实质内容
2. **状态标记 ≠ 证据** - 必须有数据支持的结论
3. **完成 ≠ 成功** - 必须记录失败、局限性和下一步

---

## 模板结构

### 1. Work Brief (工作简报)

```yaml
schema_version: "0.1.0"
object_type: work_brief
phase: skill_execution
sequence: 3

# === 核心假设 ===
hypothesis:
  statement: "在IEEE69网络的高电压偏差节点添加无功补偿，可以降低网损并改善电压分布"
  rationale: "基于无功功率-电压耦合关系，Q注入可减少线路无功传输，从而降低I²R损耗"
  testable_prediction: "补偿后网损降低>5%，电压偏差改善>10%"

# === 方法设计 ===
method:
  name: "weak_node_reactive_compensation"
  description: "识别电压最低的三个节点，添加并联电容器进行无功补偿"
  algorithm:
    type: "greedy_local_search"
    steps:
      - "计算所有节点的电压幅值"
      - "识别V < 0.95 p.u.的节点"
      - "在这些节点添加1.5 MVar并联电容"
      - "运行潮流计算"
      - "比较网损和电压指标"
  code_location: "tasks/task003/candidate_solver.py:45-89"
  baseline_comparison: "与无补偿基线对比"

# === 技能实现细节 ===
skill_implementation:
  # 技能元数据
  metadata:
    skill_name: "renewable_inverter_reactive_optimizer"
    skill_version: "0.3.1"
    skill_family: "power_system_reactive_power_optimization"
    author: "agent.skill_coder.v2"
    created_at: "2026-04-27T09:15:00Z"
    
  # 技能代码实现
  code:
    # 核心算法文件位置
    main_file: "tasks/task003/candidate_solver.py"
    git_commit: "a1b2c3d4"
    lines_range: "45-89"
    
    # 代码结构说明
    structure:
      - function: "identify_weak_nodes"
        lines: "45-58"
        purpose: "识别电压幅值最低的N个节点"
        algorithm: "排序 + 阈值筛选"
        complexity: "O(n log n)"
        
      - function: "calculate_compensation"
        lines: "60-72"
        purpose: "根据电压偏差计算所需无功补偿量"
        formula: "Q_comp = k * (V_target - V_actual) * S_base"
        k_value: 1.2
        
      - function: "apply_and_run_powerflow"
        lines: "74-89"
        purpose: "应用补偿并运行潮流计算"
        simulator_api: "pandapower.runpp"
        convergence_criteria: "1e-6"
        
    # 关键参数配置
    parameters:
      weak_node_count:
        value: 3
        rationale: "基于IEEE69网络规模的经验选择"
        tuned: false
        
      compensation_factor_k:
        value: 1.2
        rationale: "补偿系数，考虑一定的过补偿以抵消线路损耗"
        tuned: true
        tuning_history:
          - attempt: 1
            value: 1.0
            result: "补偿不足，电压改善不明显"
          - attempt: 2
            value: 1.5
            result: "过补偿，部分节点电压越上限"
          - attempt: 3
            value: 1.2
            result: "平衡，网损和电压均改善"
            
      voltage_threshold_pu:
        value: 0.95
        rationale: "IEEE标准规定的正常运行电压下限"
        source: "IEEE Std 1547"
        
  # 设计决策记录
  design_decisions:
    - decision: "使用贪心算法而非全局优化"
      context: "需要在实时控制场景下快速响应"
      alternatives_considered:
        - "OPF (Optimal Power Flow)"
        - "遗传算法"
        - "粒子群优化"
      trade_offs:
        - "速度 vs 最优性：选择速度"
        - "简单性 vs 精确性：选择简单性"
      validated: true
      validation_evidence: "贪心算法在100次随机工况中，90%情况下达到OPF 95%以上的性能"
      
    - decision: "固定补偿系数k而非自适应"
      context: "简化初始实现，后续可升级为自适应"
      limitation_acknowledged: "无法应对极端负荷变化"
      future_work: "实现基于负荷预测的自适应k值调整"
      
  # 代码质量指标
  quality_metrics:
    test_coverage_percent: 78
    lint_score: 8.5
    cyclomatic_complexity:
      overall: 12
      max_per_function: 5
    documentation:
      docstring_coverage: "100%"
      type_hints: "完整"
      
  # 依赖关系
  dependencies:
    external:
      - package: "pandapower"
        version: "2.14.0"
        purpose: "潮流计算引擎"
      - package: "numpy"
        version: "1.24.0"
        purpose: "数值计算"
    internal:
      - module: "tasks.task003.grid_context"
        purpose: "获取网络拓扑数据"
      - module: "tasks.task003.baseline"
        purpose: "基线对比数据"
        
  # 技能演化历史
  evolution:
    previous_version: "0.2.0"
    changes_from_previous:
      - "添加了电压越限检查"
      - "修复了多补偿节点冲突问题"
      - "优化了补偿量计算逻辑"
    lessons_learned:
      - "经验：必须检查补偿后的电压上限，避免过补偿"
      - "教训：早期版本未考虑节点间的电气距离，导致相邻节点补偿冲突"
    
  # 可复用性评估
  reusability:
    applicable_networks:
      - "ieee33"
      - "ieee69"
      - "ieee118"
    constraints:
      - "适用于辐射状配电网"
      - "要求有连续可调节的无功补偿设备"
    adaptation_required:
      - name: "ieee118"
        changes: "增加补偿节点数至5-7个"
        reason: "网络规模更大，需要更多补偿点"

# === 执行证据 ===
execution:
  status: completed
  timestamp: "2026-04-27T10:30:00Z"
  duration_seconds: 45
  
  inputs:
    grid_model: "ieee69"
    base_load_mw: 3.8
    compensation_nodes: [12, 23, 45]
    compensation_mvar_per_node: 1.5
    simulator: "pandapower 2.14.0"
    
  outputs:
    raw_result_path: "runs/task003/run_0021/artifacts/loadflow_result.json"
    metrics_path: "runs/task003/run_0021/artifacts/metrics.json"
    log_path: "runs/task003/run_0021/artifacts/simulation.log"

# === 量化结果 ===
results:
  primary_metrics:
    loss_before_mw: 
      value: 0.224
      unit: "MW"
      context: "基线网损"
    loss_after_mw:
      value: 0.198
      unit: "MW"
      context: "补偿后网损"
    improvement_percent:
      value: 11.6
      unit: "%"
      is_significant: true
      threshold_used: 5.0
      
  secondary_metrics:
    voltage_deviation_before:
      value: 0.08
      unit: "p.u."
    voltage_deviation_after:
      value: 0.073
      unit: "p.u."
      note: "改善不明显，可能补偿量不足"
      
  constraint_violations:
    before: 3
    after: 1
    details: "节点45在补偿后仍存在电压越限"

# === 结果解释 ===
interpretation:
  summary: "网损降低11.6%验证了无功补偿的有效性，但电压改善低于预期"
  
  supports_hypothesis: partially
  support_evidence:
    - "网损降低显著(11.6% > 5%阈值)"
  contradicts_hypothesis:
    - "电压改善仅8.7%，远低于10%预期"
    
  unexpected_findings:
    - finding: "节点45电压改善不明显"
      possible_reason: "该节点距离电源较远，局部补偿效果有限"
      follow_up: "需要测试级联补偿或调整补偿位置"

# === 失败胶囊 (必须记录) ===
failure_capsule:
  # 即使整体"成功"，也要记录局限性和失败点
  
  known_limitations:
    - limitation: "仅测试单工况(peak load)"
      impact: "无法评估负荷波动下的性能稳定性"
      severity: medium
      
    - limitation: "补偿位置固定为电压最低节点"
      impact: "可能不是全局最优配置"
      severity: medium
      
    - limitation: "未与文献方法对比"
      impact: "无法判断方法先进性"
      severity: high
      
  local_failures:
    - failure: "节点45电压仍低于0.95 p.u."
      cause_hypothesis: "补偿量不足或位置不当"
      mitigation_attempted: "增加补偿量至2.0 MVar"
      mitigation_result: "仍无效，怀疑需要级联补偿"
      
  generalizability_gaps:
    - "仅在IEEE69上测试"
    - "仅测试单一网络拓扑"
    - "未考虑可再生能源不确定性"

# === 证据引用 ===
evidence_refs:
  - type: "simulation_output"
    path: "runs/task003/run_0021/artifacts/loadflow_result.json"
    checksum: "sha256:abc123..."
    
  - type: "code_snapshot"
    path: "tasks/task003/candidate_solver.py"
    git_commit: "a1b2c3d"
    lines: "45-89"
    
  - type: "baseline_comparison"
    path: "tasks/task003/baseline.yaml"
    compared_field: "loss_mw"

# === 下一步行动 ===
next_actions:
  immediate:
    - action: "测试不同补偿位置组合"
      rationale: "当前固定位置可能非最优"
      expected_output: "位置敏感性分析"
      
    - action: "增加补偿量至2.5 MVar"
      rationale: "电压改善不足可能是补偿量不够"
      constraint: "检查无功设备投资成本约束"
      
  short_term:
    - action: "引入文献[1]的方法进行对比"
      rationale: "需要基准判断方法先进性"
      paper_ref: "Zhang et al., 2023, Reactive Power Optimization..."
      
    - action: "测试多负荷工况"
      rationale: "验证方法鲁棒性"
      scenarios: ["light_load", "peak_load", "evening_ramp"]
      
  blocked_pending:
    - action: "IEEE33网络验证"
      blocked_by: "需要构建IEEE33 pandapower模型"
      
    - action: "多目标优化(成本+网损)"
      blocked_by: "缺少成本模型数据"

# === 审查检查清单 ===
review_checklist:
  # 导师/审查者可以逐项检查
  
  hypothesis_clear: true
  method_reproducible: true
  data_available: true
  results_quantified: true
  limitations_acknowledged: true
  next_actions_concrete: true
  
  reviewer_notes: []

---

## 对比：差 vs 好

### ❌ 差的记录（当前 DaoShuGuo）
```yaml
phase: skill_execution
sequence: 3
status: completed
timestamp: "2026-04-27T10:30:00Z"
task_ref: task.power.ieee69_renewable_reactive_opt
# ... 没了
```

**问题**:
- 做了什么？不知道
- 成功了吗？不知道
- 有什么数据？不知道
- 局限在哪？不知道
- 下一步干什么？不知道
- **技能怎么实现的？不知道** ← 最严重的问题
- 用的是贪心算法还是全局优化？不知道
- 参数怎么选的？不知道
- 代码质量如何？不知道
- 能否复用到其他网络？不知道

### ✅ 好的记录（基于本模板）
```yaml
# 上面完整的模板内容（包含假设、方法、结果、技能实现细节）
```

**价值**:
- ✅ 3个月后回看，能理解当时的决策
- ✅ 导师审查，能判断研究质量
- ✅ 同行复现，有具体方法可循
- ✅ 写论文时，有完整数据可用
- ✅ **技能可迭代改进** ← 关键：知道上版本改了什么，为什么改
- ✅ **参数可调优** ← 关键：知道每个参数的历史和理由
- ✅ **设计可审查** ← 关键：知道考虑过哪些替代方案，为什么没选
- ✅ **代码可维护** ← 关键：知道复杂度和质量指标

---

## 强制字段验证规则

框架应该拒绝任何不满足以下条件的记录：

| 字段 | 强制 | 验证规则 |
|------|------|---------|
| hypothesis.statement | ✅ | 不能为空字符串 |
| hypothesis.testable_prediction | ✅ | 必须包含可量化指标 |
| method.description | ✅ | 长度>100字符 |
| results.primary_metrics | ✅ | 至少包含2个指标 |
| failure_capsule.known_limitations | ✅ | 至少记录1个局限性 |
| next_actions.immediate | ✅ | 至少1个具体行动 |
| skill_implementation.code.main_file | ✅ | 不能为空 |
| skill_implementation.code.structure | ✅ | 至少1个函数描述 |
| skill_implementation.design_decisions | ✅ | 至少1个设计决策 |
| skill_implementation.quality_metrics | ✅ | 代码质量指标 |

---

## 技能实现部分详解

### 为什么需要技能实现细节？

**问题**: 只看结果数据，不知道**技能本身是如何工作的**。

**例子**:
- ❌ "技能执行了，结果是网损降低11.6%"
- ✅ "技能使用贪心算法，在电压最低的3个节点添加1.5MVar补偿。参数k=1.2经过3次调优..."

### 技能实现应该记录什么？

#### 1. 代码结构 (code.structure)
每个核心函数必须说明：
- **purpose**: 这个函数做什么？
- **algorithm**: 使用什么算法？
- **complexity**: 时间/空间复杂度
- **lines**: 代码位置（便于审查）

#### 2. 设计决策 (design_decisions)
每个重大决策必须记录：
- **alternatives_considered**: 考虑过哪些替代方案？
- **trade_offs**: 权衡了什么？
- **validated**: 是否验证过？

**目的**：防止"想当然"的设计，强制反思。

#### 3. 参数调优历史 (parameters.tuning_history)
每个关键参数必须记录：
- **尝试过的值**
- **对应的结果**
- **最终选择的理由**

**目的**：防止"拍脑袋"参数，形成调优知识。

#### 4. 演化历史 (evolution)
- **从哪个版本演化而来**
- **改了什么**
- **学到了什么教训**

**目的**：技能可迭代改进，而非每次都从零开始。

---

## 实施建议

### Phase 1: 创建模板文档（已完成）
- ✅ 本文件定义了理想记录的标准

### Phase 2: 更新 Schema
- 创建 `schemas/work_brief.schema.json`
- 定义强制字段和验证规则

### Phase 3: 修改引擎
- `run_generic_loop_engine.py` 强制收集上述字段
- 缺失字段时，拒绝进入下一阶段

### Phase 4: 验证工具
- 添加 `verify_research_quality.py`
- 检查记录是否满足模板要求

---

## 参考来源

- AutoResearchFlow `AGENT_EXECUTION_PROTOCOL.md`: 阶段定义和成功标准
- AutoResearchFlow `RESEARCH_HARNESS_PROTOCOL.md`: 观察-解释-干预模型
- AutoResearchClaw 反伪造系统: 证据引用和验证
- DaoShuGuo AGENTS.md 15.3: 验收标准
