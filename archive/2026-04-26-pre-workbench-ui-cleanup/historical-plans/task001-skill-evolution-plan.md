# task001 技能演化计划：weak_bus_shunt_optimizer

## 1. 目标

本计划用于将 `task001` 的 candidate 从“真实但浅层的 ext_grid 单参数搜索”推进为更符合电力系统无功优化语义的候选技能。

核心目标不是扩大工况，而是研发一个可复用、可验证、可沉淀的真实技能：

`weak_bus_shunt_optimizer`

## 2. 为什么做这个

项目最初的核心不是“流程跑完”，而是：

- 技能变强
- 成效可验证
- 认知可沉淀
- 品味约束主张

当前 `ext_grid.vm_pu` 搜索已经证明真实闭环可运行，但它不是足够好的科研技能。下一步应让系统开始研发真正的 candidate 技能。

## 3. 技能定义

### 3.1 技能名称

`skill.power.weak_bus_shunt_optimizer`

### 3.2 技能思想

1. 运行 baseline 潮流。
2. 识别电压最低的若干弱节点。
3. 在这些节点上搜索 shunt compensation 容量。
4. 用统一 evaluator 比较网损、电压偏差和约束违反。
5. 选择满足约束且综合目标最优的方案。

### 3.3 输入

- 网络模型：`pandapower case33bw`
- 约束集：
  - 电压上下限
  - 候选弱节点数量
  - shunt 容量网格
  - 最大 shunt 数量

### 3.4 输出

- 选定的 shunt 节点与容量
- 真实潮流指标
- 搜索轨迹摘要
- solver 状态

## 4. 验收标准

### 4.1 功能验收

- [x] 新增 `weak_bus_shunt_optimizer.py`
- [x] 新增 `skill.power.weak_bus_shunt_optimizer` 样例或注册记录
- [x] evaluator 能评估 shunt optimizer 输出
- [x] orchestrator 能通过 `real-run --strategy weak-shunt` 或等价入口调用该技能
- [x] 真实运行目录完整生成

### 4.2 质量验收

- [x] `run.yaml` 只记录事实
- [x] `metrics.json` 包含 baseline 与 candidate 的真实指标
- [x] `cognition` 记录弱节点补偿相关候选认知或失败认知
- [x] `taste_assessment` 不因单工况成功而拔高结论
- [x] `skills/registry.json` 记录该技能的使用或产出

### 4.3 最低科研有效性

成功不是必须优于 ext_grid 搜索，但必须至少满足：

- [x] 技能表达更接近无功优化问题
- [x] 控制对象比 ext_grid 调压更真实
- [x] 成功或失败都能提供有价值认知

## 5. 实施步骤

### Phase 1: 技能实现

- [x] 新增 `skills/active_dev/weak_bus_shunt_optimizer.py`
- [x] 在 baseline 潮流结果中识别弱节点
- [x] 搜索候选 shunt 节点与容量
- [x] 输出 evaluator 兼容结构

### Phase 2: evaluator 适配

- [x] 保持 evaluator 独立
- [x] 支持 candidate solution 中携带 shunt control settings
- [x] 保持指标计算逻辑不偏向 solver

### Phase 3: orchestrator 接入

- [x] 新增真实运行策略参数
- [x] 支持 `--strategy weak-shunt`
- [x] 继续支持原有 ext-grid 路线作为对照
- [x] 保持 writeback 逻辑

### Phase 4: schema/registry 接入

- [x] 补 skill 样例
- [x] 确保 registry 可记录该技能
- [x] 确保 `validate_schemas.py` 通过

### Phase 5: 真实运行与复盘

- [x] 跑一次真实 weak-shunt 运行
- [x] 检查指标
- [x] 检查 taste 分级是否克制
- [x] 检查 cognition 是否不是空话

## 6. 风险

### 风险 1：shunt 搜索不优于 baseline

这不是失败。若能形成“当前弱节点 shunt 策略在该设置下无效”的负向认知，仍然有效。

### 风险 2：搜索空间过大

第一版只搜索少量弱节点和少量容量，不做组合爆炸。

### 风险 3：结果好但机理薄

报告必须控制 claim，最多按 `琢石` 或 `雕木` 处理。

## 7. 验证命令

- [x] `python scripts/validate_schemas.py`
- [x] `python orchestrator/main.py validate`
- [x] `python orchestrator/main.py real-run --strategy weak-shunt`

## 8. 结论

这个计划的价值不在于一次性做出强算法，而在于让框架真正开始“研发技能”。

如果该技能成功，它应成为技能网络的新节点；如果失败，它应成为认知网络中的负向知识。
