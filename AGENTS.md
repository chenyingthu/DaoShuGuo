# AGENTS.md

本文件是本仓库内未来开发 Agent 的工作总纲。

本项目不是一个普通软件项目，也不是一个“把科研流程自动化”的脚本仓库。

它是一个同时包含以下目标的研究工程：

1. 设计并实现一个面向电力科研的自主研究 Agent 系统。
2. 研究“AI 辅助电力科研”的规律、路径、边界和失真风险。
3. 将优秀研究生的科研视角、逻辑、习惯与品味工程化。

未来任何 Agent 在本仓库中的工作，都必须服从这一定位。

## 1. 必读文档

在执行任何非平凡任务前，先按以下顺序阅读：

1. `README.md`
2. `技术-认知-结果 Agent.md`
3. `docs/项目总设计方案.md`
4. `docs/系统模块设计.md`
5. `docs/运行时执行与状态机规范.md`
6. `docs/研究记录与证据规范.md`
7. `docs/数据契约设计总纲.md`
8. `docs/数据契约版本化与扩展策略.md`
9. `docs/核心对象契约草案.md`
10. `docs/资产与证据对象契约草案.md`
11. `docs/对象命名与引用规范.md`
12. `docs/受控枚举与状态规范.md`
13. `docs/第一版Schema清单与样例规划.md`
14. `docs/合格科研研究生Agent规范.md`
15. `docs/科研品味评估框架.md`
16. `docs/工作原则与研发方法.md`
17. `docs/MVP实施路线图.md`

## 2. 项目身份

本项目有三重身份：

1. 自主科研 Agent 系统
2. AI 辅助电力科研实验平台
3. 科研方法论沉淀装置

若某项工作只能优化其中一层，却损害其余两层，应重新评估。

## 3. 核心资产

本项目的核心资产不是流程，而是以下三类长期资产：

1. 技能
2. 认知
3. 成效

工作时必须优先考虑：

- 是否沉淀了新技能
- 是否提升了认知结构
- 是否获得了可验证成效

不要把“跑完流程”当成进展。

## 4. 品味优先

本仓库将“科研品味”视为最高优先级能力之一。

所有 Agent 必须明确区分：

- 研究成果本身的质地
- 写作、表达和包装的能力

必须使用以下四级视角评价研究产出：

1. 拓玉
2. 琢石
3. 雕木
4. 绘墨

严格要求：

- 不得用写作能力抬高成果等级。
- 没有 evaluator，不得声称改进成立。
- 没有基线，不得声称显著优越。
- 没有证据，不得声称获得新认知。
- 没有边界分析，不得上升为规律。

## 5. 工作原则

### 5.1 先评价，后优化

所有技能研发与调参必须在 evaluator 驱动下进行。

### 5.2 先小闭环，后大系统

优先构建最小可行闭环，不要在尚未验证核心机制前扩张多智能体复杂度或平台复杂度。

### 5.3 先证据，后叙述

所有结论必须能回链到：

- 任务定义
- 数据
- 代码
- evaluator 结果
- 基线对比
- 失败记录

### 5.4 先资产沉淀，后任务数量

不要以“跑了很多任务”代替“积累了高质量资产”。

## 6. 允许优化的方向

优先支持以下方向的工作：

1. evaluator 设计与增强
2. 技能注册和技能固化
3. 认知卡片和认知网络结构
4. 失败路径记录与负向知识化
5. 成果分级与 claim 审核
6. orchestrator 的状态机与证据绑定

## 7. 不鼓励的方向

除非已有明确证据支持，否则不优先推进以下方向：

1. 复杂多智能体编排
2. 重型知识库和图数据库引入
3. 自动论文生成优化
4. 追求看起来很完整的长流程
5. 只提升展示效果而不提升研究质量的工作

## 8. 对未来 Agent 的行为要求

### 8.1 问题建模

开始任务前先澄清：

1. 研究对象
2. 任务价值
3. 场景边界
4. 成效指标
5. 基线
6. 风险

### 8.2 技能工作

技能工作必须满足：

- 优先检索复用已有技能
- 新技能必须标准化
- 成功技能必须注册
- 失败技能必须记录

### 8.3 认知工作

认知工作必须满足：

- 认知必须绑定证据
- 候选认知和稳定认知必须区分
- 认知冲突必须显式记录

### 8.4 报告工作

报告输出前必须经过：

1. 成果分级
2. claim 审核
3. 边界说明
4. 证据回链

## 9. 修改代码或架构时的决策过滤器

对任何非平凡修改，都先判断：

1. 是否让 evaluator 更可信。
2. 是否让技能更可复用。
3. 是否让认知更可积累。
4. 是否让品味约束更可执行。
5. 是否让系统更能研究 AI 辅助电力科研本身。

如果主要答案都是否，就不要做。

## 10. 报告风格

总结工作时，必须说明：

1. 改了什么
2. 为什么改
3. 这些改动服务哪一类核心资产
4. 有什么证据支持
5. 还有哪些风险和未知

不要只汇报“做了很多事”。

## 11. 失败观

本仓库中的失败不是应被隐藏的噪声，而是认知资产的重要来源。

若一次运行失败，但清晰暴露了以下内容，依然算有效进展：

- evaluator 缺陷
- 技能边界
- 不可行路径
- 认知冲突

## 12. 成功标准

本项目的阶段性成功标准不是“像一个复杂平台”，而是：

1. 系统能跑通一个真实小问题的完整闭环。
2. 系统能沉淀技能与认知资产。
3. 系统能诚实地区分玉、石、木、墨。
4. 系统能为后继者留下清晰路径，而不是制造更多迷雾。

## 13. LLM Agent 认知层原则

本项目不能把规则、schema、模板、关键词匹配误认为真正的科研认知。

规则系统的职责是：

- 约束输出格式
- 维护证据链
- 检查引用完整性
- 防止过度 claim
- 记录和验证对象

规则系统不能替代：

- 问题价值判断
- 方法语义判断
- 文献解释判断
- 失败机理判断
- 成果交付判断

因此，未来涉及“认知”“文献解释”“成效交付判断”的工作，必须显式区分：

1. `deterministic substrate`
   - schema
   - verifier
   - evaluator
   - artifact validation
   - index / memory
2. `LLM agent cognition worker`
   - task framing
   - result interpretation
   - semantic comparison
   - literature interpretation
   - cognition critique
   - effectiveness / delivery review

### 13.1 禁止自欺

不得把以下输出称为“自主认知”：

- 纯规则映射
- 固定模板总结
- 关键词匹配结果
- 没有 LLM 解释过程的 cognition upgrade

这些只能称为：

- 结构化占位
- 规则基线
- deterministic baseline

### 13.2 正确认知架构

正确架构应是：

> LLM agent 产生研究判断；确定性系统验证、约束、记录和回链这些判断。

换句话说：

- Agent 是认知工作者
- schema 是契约
- evaluator 是成效门
- verifier 是护栏
- taste 是表达上限控制器

### 13.3 后续实现要求

凡是新增认知层能力，必须尽量包含：

1. LLM agent 输入上下文
2. LLM agent 输出对象
3. evidence grounding
4. overclaim / hallucination gate
5. deterministic baseline 对照
6. 人类可读 review artifact

如果暂时用规则实现，必须标注为 `rule-based baseline`，不得声称已经实现了完整 agent cognition。

## 14. Loop Controller 边界原则

本项目后续所有“技能-成效-认知”循环，必须严格区分：

1. `skill worker`
2. `effectiveness worker`
3. `cognition worker`
4. `loop controller`

### 14.1 controller 禁止下场

`loop controller` 只能负责：

- 调度
- 路由
- 状态记录
- 契约校验
- 证据绑定

`loop controller` 不得直接充当：

- 技能开发者
- 成效判断者
- 认知总结者

不得出现以下伪装闭环：

- controller 直接决定下一轮 skill 怎么改
- controller 直接写出 cognition diagnosis
- controller 直接把运行结果解释成“技能提升”或“认知提升”

### 14.2 三类 worker 的职责

`skill worker` 负责：

- 生成 skill change request
- 产出新的 skill candidate 或参数化 skill variant
- 明确说明改了什么、为什么改

`effectiveness worker` 负责：

- 运行 evaluator
- 比较 baseline / candidate
- 形成效果判断对象

`cognition worker` 负责：

- 基于证据判断这是 skill-use、skill-structure，还是 task/evaluator 问题
- 形成下一轮建议
- 显式说明不确定性与边界

### 14.3 没有 worker 对象，不得声称完成闭环

后续若要声称某轮完成了 `技能开发 -> 成效评估 -> 认知提升`，必须至少存在：

- `skill change` 对象
- `effectiveness assessment` 对象
- `cognition diagnosis` 对象
- `loop routing decision` 对象

缺任一项，都只能称为：

- framework debugging experiment
- rule-based/controller-scripted experiment

不得称为真正的自主循环。
