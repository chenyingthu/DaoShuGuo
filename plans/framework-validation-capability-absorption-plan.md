# 框架验证能力吸收计划：吸收 ResearchGraphBuilder 的验证基础设施

## 1. 计划目标

本计划的目标不是把 `ResearchGraphBuilder` 整体迁移到当前项目，而是：

> 有选择地吸收其中最适合当前 `DaoShuGuo` 的验证与测试基础设施，增强本项目的框架有效性验证能力。

当前优先吸收三类能力：

1. `preflight / light probe`
2. `experiment index`
3. `diagnosis memory`

这些能力的共同目标是：

- 提高新任务接入前的稳定性
- 让实验资产可回看、可比较、可检索
- 让 failure 经验不仅停留在认知对象，还能进入可检索诊断记忆

## 2. 为什么现在做这件事

到当前阶段，`DaoShuGuo` 已经完成：

- task002：迁移验证与负向认知
- task003：新能源任务接入、failure taxonomy、本地认知、外部参照
- task004：边界研究任务、failure taxonomy、本地认知、外部参照

这意味着框架主线已经成立。

当前最缺的，不再是“是否能跑通”，而是：

- 如何在正式执行前更早发现问题
- 如何把已有实验资产整理成可检索结构
- 如何把失败经验沉淀成长期可复用的诊断记忆

## 3. 吸收范围

本计划明确只吸收以下三类能力：

### 3.1 preflight / light probe

参考来源：

- `provider_preflight.py`
- `run_light_probe.py`

目标：

- 在正式执行 task 前，先做环境、对象、关键路径的轻量探测

### 3.2 experiment index

参考来源：

- `build_experiment_index.py`

目标：

- 为 task002/003/004 建立统一的实验索引
- 让 success / failure / compare / upgrade / literature artifact 可导航

### 3.3 diagnosis memory

参考来源：

- `diagnosis_memory.py`
- `diagnosis_memory.jsonl`

目标：

- 让失败经验进入可检索、可追加、可复用的诊断记忆层

## 4. 不在本计划范围内

本计划不吸收以下部分：

- idea scaffolding
- novelty probe 主链
- proposal generation
- blueprint / module scaffold 推荐
- topic sampling 主流程

原因：

- 这些能力更偏研究内容生成
- 当前项目优先级在框架验证，不在选题自动化

## 5. 计划的关键问题

本计划要回答的不是“能不能把脚本拷过来”，而是：

1. 哪些能力可以最小代价接入 `DaoShuGuo`
2. 哪些能力不会破坏现有 schema / orchestrator 路径
3. 哪些能力能直接提升 task005 前的可验证性
4. 如何保证吸收后的能力也进入现有 verifier / integration checks

## 6. 推荐实现原则

### 6.1 只吸收验证基础设施，不吸收内容生成主链

目标是增强框架，而不是让项目突然切换到另一套研究生成范式。

### 6.2 保持当前对象层优先

新的能力必须优先复用：

- task / run / evidence / taste / cognition
- 现有 schema
- 现有 integration checks

### 6.3 新能力应作为辅层，不替代主层

例如：

- `preflight` 是执行前的检查层
- `experiment index` 是实验资产索引层
- `diagnosis memory` 是失败记忆层

它们都不应取代现有 orchestrator 的主执行逻辑。

## 7. 推荐新增对象或文件

### 7.1 preflight / probe

建议文件：

- `scripts/run_preflight_checks.py`
- `scripts/run_light_probe.py`

建议输出：

- `analysis/preflight/*.json`
- `analysis/preflight/*.md`

### 7.2 experiment index

建议文件：

- `scripts/build_experiment_index.py`

建议输出：

- `analysis/experiment_index.json`
- `analysis/experiment_index.md`

### 7.3 diagnosis memory

建议文件：

- `memory/diagnosis_memory.jsonl`
- `scripts/update_diagnosis_memory.py`

建议输出：

- 附加型 JSONL 记录
- 可选摘要报告

## 8. 推荐最小 preflight 范围

第一版 preflight 不做复杂环境探测，只做最直接对当前项目有价值的检查。

### 8.1 必查项

- 关键 task 包是否存在
- 关键 evaluator 是否存在
- schema validator 是否可运行
- orchestrator 关键命令是否可执行
- 文献对象层是否存在关键文件

### 8.2 可选项

- pandapower 是否可导入
- 关键 scripts 是否可被 `py_compile`

### 8.3 输出要求

至少输出：

- `status`
- `checked_items`
- `blocking_issues`
- `recommended_next_step`

## 9. 推荐最小 light probe 范围

目标不是跑完整流程，而是快速回答：

> 当前项目状态是否值得进入正式执行。

第一版建议：

- 运行最小 schema check
- 运行一个最小 verifier
- 运行一个最小 task probe

输出：

- `ready`
- `degraded`
- `blocked`

## 10. 推荐 experiment index 范围

第一版 experiment index 只覆盖：

- task002
- task003
- task004

并组织以下对象：

- success run
- failure run
- compare
- semantic
- upgrade
- literature
- explanation

索引字段建议：

- task
- object_type
- object_id
- path
- status
- tags
- stage
- recommended

## 11. 推荐 diagnosis memory 范围

第一版 diagnosis memory 只记录高价值 failure：

- skill mismatch
- task mismatch
- performance failure
- boundary overclaim

建议字段：

- timestamp
- task_ref
- failure_type
- summary
- evidence_ref
- recommended_action

目标：

- 后续 task 能显式检索已有失败类型
- 避免反复踩同样的坑

## 12. 实施步骤

## Phase 1: 计划与接口对齐

目标：

把吸收范围缩到最小可执行集。

执行内容：

- [x] 明确三类吸收能力的最小接口
- [x] 明确输出文件位置
- [x] 明确哪些现有对象可复用

完成判据：

- [x] 新能力不会重造现有 schema 主线

## Phase 2: preflight / light probe

目标：

在正式执行前增加一层快速稳定性检查。

执行内容：

- [x] 实现 `run_preflight_checks.py`
- [x] 实现 `run_light_probe.py`
- [x] 输出结构化 preflight / probe 结果

完成判据：

- [x] 能区分 `ready / degraded / blocked`

## Phase 3: experiment index

目标：

让已有 task 实验资产形成统一索引。

执行内容：

- [x] 实现 `build_experiment_index.py`
- [x] 聚合 task002/003/004 关键 artifacts
- [x] 生成 `json + md` 双输出

完成判据：

- [x] 可快速查看每个 task 的 success/failure/upgrade 主线

## Phase 4: diagnosis memory

目标：

让 failure 经验进入可检索记忆层。

执行内容：

- [x] 实现 `update_diagnosis_memory.py`
- [x] 初始化 `memory/diagnosis_memory.jsonl`
- [x] 从 task002/003/004 failure artifacts 回填首批记录

完成判据：

- [x] 至少四类 failure 被结构化记忆

## Phase 5: 验证与收口

目标：

让这些新增能力进入当前框架的统一验证体系。

执行内容：

- [x] 为 preflight / probe / experiment index / diagnosis memory 增加测试
- [x] 扩展 integration checks
- [x] 更新实验记录和设计文档

完成判据：

- [x] 新能力不破坏现有 task002/003/004 主线验证

## 13. 成功标准

以下条件同时满足，视为本计划成功：

1. preflight / light probe 可运行
2. experiment index 可生成
3. diagnosis memory 可回填并追加
4. 至少一个后续任务可直接使用这些能力
5. integration checks 覆盖这些新增能力

## 14. 风险

### 风险 1：把外部项目脚本直接搬过来，导致风格失配

缓解：

- 只吸收思想和最小接口
- 不做整体复制

### 风险 2：新增层与现有 schema 主线脱节

缓解：

- 输出应尽量复用现有对象引用
- 新文件只做辅层

### 风险 3：experiment index 变成又一个“报表”

缓解：

- 索引必须服务于后续 task 检索和验证
- 不只做漂亮展示

## 15. 当前结论

本计划的价值，不在于增加更多“研究内容生成能力”，而在于：

> 让 `DaoShuGuo` 从“能做任务的科研框架”，进一步升级为“可预检、可回看、可诊断、可泛化评估的科研框架”。
