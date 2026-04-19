# MVP 实施路线图

## 1. 目标

构建一个足以验证项目核心假设的最小系统：

“在 evaluator 驱动和品味约束下，一个 Agent 能否围绕技能、认知和成效形成可积累的科研闭环。”

## 2. MVP 范围

### 2.1 纳入范围

- 一个电力系统小任务
- 一个 evaluator
- 一个 orchestrator
- 一个技能注册表
- 一个认知卡片系统
- 一个成果分级器
- 一套运行日志格式

### 2.2 不纳入范围

- 大规模多任务平台
- 多智能体群体竞赛
- 重型 GraphDB
- 自动论文成稿
- 全领域通用化

## 3. 推荐目录结构

```text
.
├── AGENTS.md
├── README.md
├── 技术-认知-结果 Agent.md
├── docs/
│   ├── 项目总设计方案.md
│   ├── 合格科研研究生Agent规范.md
│   ├── 科研品味评估框架.md
│   ├── 工作原则与研发方法.md
│   └── MVP实施路线图.md
├── tasks/
│   └── task001/
│       ├── task.md
│       ├── constraints.yaml
│       ├── baseline.yaml
│       └── targets.yaml
├── evaluators/
│   └── task001_evaluator.py
├── skills/
│   ├── registry.json
│   ├── active_dev/
│   └── validated/
├── cognition/
│   ├── registry.json
│   ├── cards/
│   └── failed/
├── runs/
│   └── task001/
└── orchestrator/
    └── main.py
```

## 4. 最小模块说明

### 4.1 Task Package

内容：

- 问题描述
- 约束条件
- 基线
- 目标指标

### 4.2 Evaluator

职责：

- 接收技能输出
- 运行实验
- 输出指标
- 与基线比较
- 生成结构化结果

### 4.3 Skill Registry

至少包含：

- 技能名称
- 版本
- 输入
- 输出
- 适用场景
- 历史效果
- 依赖关系

### 4.4 Cognition Card

至少包含：

- 标题
- 类型
- 内容
- 证据引用
- 适用边界
- 状态
- 关联任务

### 4.5 Taste Grader

职责：

- 基于 evaluator 和认知解释对成果分级
- 输出拓玉、琢石、雕木、绘墨之一

## 5. 第一阶段开发顺序

1. 固化文档和 AGENTS.md
2. 选择 task001
3. 实现 evaluator
4. 定义运行日志格式
5. 定义 skill registry 和 cognition card
6. 实现最小 orchestrator
7. 接入成果分级器
8. 跑通一次完整闭环

## 6. MVP 成功判据

一次 MVP 演示至少应证明：

1. Agent 能正确理解任务和指标。
2. Agent 能调用或构建技能并在 evaluator 中运行。
3. Agent 能输出结构化结果和与基线的对比。
4. Agent 能沉淀至少一个技能资产。
5. Agent 能沉淀至少一个认知资产。
6. Agent 能对成果做诚实分级。

## 7. 失败也算成功的条件

如果系统未能得到强结果，但能稳定产出以下内容，仍算 MVP 有价值：

1. 明确失败路径
2. 负向认知总结
3. evaluator 缺陷暴露
4. 后续改进方向

这比“写出一个看上去成功的空报告”更有研究价值。
