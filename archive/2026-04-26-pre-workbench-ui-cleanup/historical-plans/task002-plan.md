# task002 计划：框架迁移验证任务

## 1. 计划目标

`task002` 的主要目的不是继续把 `task001` 中某个单一技能调到更强，而是验证：

> 当前自主科研框架在第二个相邻任务上是否仍然成立，且能复用已经沉淀的技能、认知、评价和文献对齐能力。

换句话说，`task002` 的核心问题是：

- 框架能不能迁移
- 技能能不能迁移
- 认知能不能迁移
- 评价与品味约束能不能迁移

## 2. 任务定位

### 2.1 主目标

验证自主科研框架的可迁移性。

### 2.2 副目标

观察 `task001` 中沉淀出的 candidate skill 和认知，在相邻任务中的适用边界。

### 2.3 非目标

本任务当前不追求：

- 直接做出论文级新方法
- 在 task002 上把某个 candidate 调到最强
- 大规模多工况复杂实验
- 大规模文献自动检索

## 3. 建议任务选择

推荐 `task002` 选择：

> `IEEE69 配电网无功补偿优化迁移验证`

原因：

- 与 `task001` 保持同类问题
- 可以最大化复用：
  - task schema
  - evaluator 逻辑
  - weak-shunt 类技能思路
  - 文献种子与对齐框架
- 可以测试：
  - 技能边界
  - 认知边界
  - framework 迁移能力

## 4. task002 的关键问题

task002 要回答的，不是“某个技能能不能在另一个网络上再赢一次”，而是：

1. task001 的对象体系是否足够通用
2. evaluator 是否可参数化迁移
3. weak-shunt 技能是否依赖 IEEE33 的特殊结构
4. task001 的认知能否保留，还是必须收窄边界
5. 文献对齐层是否仍然有效
6. 品味约束在迁移任务上是否依然能抑制拔高

## 5. 复用要求

task002 必须显式复用：

- schema envelope
- task / baseline / evaluator / run
- skill registry
- cognition registry
- evidence bundle
- taste assessment
- strategy comparison
- semantic comparison
- literature alignment
- explanation alignment
- cognition upgrade

## 6. 允许变化

task002 允许变化的部分：

- 网络模型
- baseline solver 的参数化
- candidate skill 的适配层
- evaluator 中网络相关参数
- literature seed 的任务适配

## 7. 最小任务定义

### 7.1 研究对象

IEEE69 配电网中的无功补偿优化问题。

### 7.2 最小输入

- 一个可加载的网络模型
- 单工况约束
- baseline 定义
- 一个迁移 candidate 技能

### 7.3 最小输出

- 至少一个 baseline run
- 至少一个 candidate run
- 结构化比较结果
- 至少一条迁移相关认知
- 受 taste 限制的报告

## 8. 成功标准

以下条件同时满足，视为 `task002` 阶段成功：

1. 能在 `task002` 上跑通完整纵向闭环
2. 不需要重造 task001 已有框架对象
3. 至少一次成功或失败运行能形成有价值的迁移认知
4. 文献对齐与认知升级仍然成立
5. 集成测试可被扩展到 task002

## 9. 失败也算成功的条件

如果 `weak-shunt` 或其他迁移 candidate 在 task002 上失效，只要满足以下条件，仍然算 task002 有价值：

- evaluator 真正运行
- 失败被记录
- 负向认知形成
- 认知边界被收窄
- 报告没有把失败包装成成果

## 10. 实施步骤

## Phase 1: task002 任务包建立

目标：

建立 task002 的最小任务对象。

建议文件：

- `tasks/task002/task.md`
- `tasks/task002/task.yaml`
- `tasks/task002/constraints.yaml`
- `tasks/task002/baseline.yaml`
- `tasks/task002/targets.yaml`

执行内容：

- [x] 定义 research object
- [x] 定义 scenario boundary
- [x] 定义 baseline
- [x] 定义 targets

完成判据：

- [x] task002 任务包可独立说明其目标和边界

## Phase 2: baseline 迁移

目标：

在 task002 上建立一个真实 baseline。

执行内容：

- [x] 复用 task001 baseline 结构
- [x] 参数化到 task002 网络
- [x] 输出与 evaluator 兼容的 baseline 结果

完成判据：

- [x] baseline 在 task002 上可真实运行

## Phase 3: candidate skill 迁移

目标：

将 `weak_bus_shunt_optimizer` 或相近技能迁移到 task002。

执行内容：

- [x] 评估当前 skill 是否可直接复用
- [x] 必要时只加最小适配层
- [x] 不得重写成全新体系

完成判据：

- [x] 至少一个 candidate 在 task002 上真实运行

## Phase 4: evaluator 迁移

目标：

让 evaluator 在 task002 上继续独立工作。

执行内容：

- [x] 参数化 evaluator
- [x] 保持指标定义结构
- [x] 保持 pass criteria 逻辑

完成判据：

- [x] task002 evaluator 可独立比较 baseline 与 candidate

## Phase 5: 迁移认知与文献对齐

目标：

观察 task001 认知和文献对齐在 task002 上的保留或失效。

执行内容：

- [x] 做至少一次 strategy comparison
- [x] 做 semantic comparison
- [x] 做 literature alignment
- [x] 做 explanation alignment
- [x] 做 cognition upgrade

完成判据：

- [x] 至少形成一条迁移相关认知

## Phase 6: task002 验证

目标：

证明 task002 不是重新造系统，而是复用框架。

执行内容：

- [x] 跑 task002 integration checks
- [x] 验证 artifact 结构
- [x] 验证 writeback

完成判据：

- [x] task002 通过最小纵向验证

## 11. 验收标准

### 11.1 功能验收

- [x] task002 最小任务包建立
- [x] baseline 迁移成功
- [x] candidate 迁移成功
- [x] evaluator 迁移成功
- [x] 迁移认知对象形成
- [x] task002 报告生成

### 11.2 质量验收

- [x] task002 复用 task001 的对象层
- [x] task002 没有重新发明 evaluator/taste/writeback 机制
- [x] task002 失败时仍能形成负向认知

## 12. 风险

### 风险 1：task002 过于接近 task001，验证价值不够

缓解：

- 至少换网络模型或任务边界

### 风险 2：task002 过于复杂，混淆框架问题和任务问题

缓解：

- 保持问题类型相近
- 不直接换到完全不同领域

### 风险 3：为 task002 重新造系统

缓解：

- 明确复用边界
- 把“不允许重造”写进验收标准

## 13. 结论

`task002` 的真正价值，不在于再做一个新算例，而在于证明：

> 我们做出来的不是一套只能服务 task001 的实验脚手架，而是一个能够跨任务迁移的自主科研框架。
