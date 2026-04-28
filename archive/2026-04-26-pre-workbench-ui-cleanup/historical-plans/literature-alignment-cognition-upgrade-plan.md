# 文献对齐与比较认知升级实施计划

## 1. 目标

实现一个新的框架层，使系统不仅能比较运行结果，还能：

1. 比较策略语义
2. 比较认知层次
3. 将本地认知与文献中的方法和解释对齐
4. 对认知和主张进行升级或降级

## 2. 阶段策略

采用两阶段路线：

### Phase A: 本地比较认知升级

先不引入完整文献检索，先完成：

- strategy_semantic_comparison
- novelty_assessment
- cognition_upgrade

### Phase B: 文献对齐接入

再实现：

- literature_alignment
- 文献方法映射
- 文献解释对齐

当前状态：

- 已完成种子文献驱动的方法家族级对齐
- 已将 literature_alignment 接入 novelty_assessment 与 cognition_upgrade
- 已完成解释卡片级对齐
- 已完成人工整理 `fulltext_excerpt` 驱动的片段级解释对齐
- 尚未完成自动 PDF/HTML 全文抽取

## 3. 验收标准

### 3.1 第一阶段

- [x] 新增比较认知升级相关 schema
- [x] orchestrator 新增对应入口
- [x] 能基于两次 run 生成语义比较结果
- [x] 能生成升级后的认知对象
- [x] 能对 claim 上限做重新判断

### 3.2 第二阶段

- [x] 新增 literature_alignment schema
- [x] 能记录文献方法与本地策略的关系
- [x] 能记录文献解释与本地认知的关系
- [x] 能输出新颖性判断
- [x] 能生成基础文献对象层（paper/method/explanation cards）
- [x] 能进行原文片段级解释对齐
- [ ] 能进行自动 PDF/HTML 全文抽取

## 4. 第一步实施内容

### Step 1: schema 层扩展

- [x] `strategy_semantic_comparison.schema`
- [x] `novelty_assessment.schema`
- [x] `cognition_upgrade.schema`

### Step 2: orchestrator 对接

- [x] 新增 `compare-semantics`
- [x] 新增 `upgrade-cognition`

### Step 3: task001 首次使用

- [x] 用 `run_0009` 与 `run_0011` 做第一次语义比较
- [x] 用比较结果生成更高层认知对象

## 5. 非目标

本计划当前不追求：

- 自动完整文献综述
- 自动论文写作
- 大规模外部知识图谱
- 一步到位的全文精细语义解析

## 6. 结论

本计划的意义在于：

让系统从“会比较哪个更强”，进入“会比较为什么这样更强、这意味着什么、是否真的具有研究价值”的阶段。
