# task003 第三阶段计划：文献对齐与外部参照认知升级

## 1. 计划目标

`task003` 第二阶段已经证明：

- 本地比较认知成立
- success / skill mismatch / performance failure / task mismatch 已被区分
- 至少两条 task003 升级认知已形成

但当前这些认知仍主要来自：

- 本地 run
- 本地 comparison
- 本地 semantic comparison

因此，`task003` 第三阶段的目标是：

> 将 task003 已有本地认知与外部文献方法空间建立联系，使认知不只来自“自我感悟”，而能被已有工作校准、比较和定位。

## 2. 第三阶段核心问题

本阶段要回答的问题不是“再多找几篇论文”，而是：

1. task003 的 success path 对应哪个方法家族
2. skill mismatch 在文献空间中应被视为“不同问题语义”，还是“旧方法迁移失败”
3. performance failure 在文献空间中应被理解为：
   - 方法家族本身不成立
   - 还是当前实现/参数还不够好
4. task003 当前两条升级认知，与已有研究是：
   - 重复
   - 补充
   - 变体
   - 还是潜在 extension
5. 哪些认知值得继续投入，哪些应在文献参照下被降级或收窄

## 3. 第三阶段范围

本阶段聚焦四件事：

- task003 新能源相关文献种子建立
- task003 方法家族级 literature alignment
- task003 explanation alignment
- 文献参照下的 cognition upgrade / novelty assessment

本阶段暂不做：

- 自动联网检索最新论文
- 大规模文献综述生成
- PDF 自动全文解析系统
- 复杂 citation ranking

第一版仍然采用：

- 人工 curated seed papers
- 轻量 method/explanation card
- excerpt 级支持/补充/冲突判断

## 4. 为什么这一阶段是必要的

到目前为止，task003 已经能形成很好的本地认知。

但如果没有外部文献参照，系统仍然可能陷入三类风险：

### 4.1 封闭认知风险

只在自己的 run 和 semantic comparison 中循环，难以知道：

- 认知是否只是已知规律的局部再现
- 当前“新发现”是否只是别人早已总结过的方法家族差异

### 4.2 新颖性误判风险

没有文献参照，很难判断：

- 当前 success cognition 是不是已知 inverter Volt/Var 控制的自然表现
- 当前 performance failure 是否只是文献中常见的参数敏感性问题

### 4.3 failure 解释不足风险

本地能看到 failure，但没有文献参照时，很难进一步判断：

- 这类失败是方法家族固有边界
- 还是当前实现太粗糙

因此，本阶段的作用不是“让报告更像论文”，而是：

> 用外部方法空间校准 task003 的认知边界和新颖性判断。

## 5. 当前可复用基础

项目已有以下基础设施可直接复用：

### 5.1 文献对象层

- `literature_source`
- `paper_record`
- `paper_excerpt`
- `method_card`
- `explanation_card`

### 5.2 文献流程能力

- `build-literature-cards`
- `align-literature`
- `align-explanations`
- `upgrade-cognition`

### 5.3 task003 本地认知材料

- success run: `run_0001`
- skill mismatch run: `run_0003`
- performance failure run: `run_0004`
- task mismatch freeze artifacts
- compare objects
- semantic comparison objects
- task003 cognition upgrades

这意味着 task003 第三阶段不应重造文献框架，而应主要做：

- task003 语义映射扩展
- task003 新能源种子设计
- task003 特有的 literature / explanation 对齐规则

## 6. task003 推荐最小文献种子

第三阶段建议先建立一组非常克制的 task003 种子，不求多，只求能覆盖关键方法语义。

### 6.1 success path 对应种子

用于对齐 `inverter-support`：

- inverter-based Volt/Var control
- DER reactive support
- distributed / local Volt/Var optimization

建议最少 2-3 篇。

### 6.2 skill mismatch 对应种子

用于说明：

- 传统 capacitor placement / weak-bus compensation 与 inverter-based reactive support 属于不同方法语义

这部分可直接复用 task001/task002 中已有的：

- capacitor placement
- weak bus / shunt family 文献

### 6.3 performance failure 对应种子

用于说明：

- inverter reactive support 路线在文献中通常存在参数敏感性、目标冲突或控制边界问题

建议最少 1-2 篇能体现：

- reactive support capability limits
- local control vs system-level objective tension

## 7. 推荐方法家族映射

task003 本阶段建议至少显式定义以下 method family。

### 7.1 renewable_inverter_reactive_support

对应：

- inverter-based Volt/Var control
- DER reactive support
- local inverter Q control

### 7.2 coordinated_volt_var_control

对应：

- inverter + capacitor / regulator / OLTC 的协同控制

虽然 task003 当前还没实现完整协同 candidate，但该家族应先在文献层预留。

### 7.3 weak_bus_shunt_search

对应：

- capacitor placement
- reactive compensation placement

此家族可部分复用现有映射规则。

## 8. 本阶段要处理的三类对齐问题

### 8.1 success path 的文献定位

问题：

- `inverter-support` 当前是一个本地 candidate
- 它在文献空间中应被定位为哪类已知方法家族

目标：

- 不拔高其新颖性
- 但明确其问题语义是合理的

### 8.2 skill mismatch 的文献解释

问题：

- 为什么 weak-shunt 在数值上可以更强，却仍然不应被视为新能源-aware candidate

目标：

- 用文献方法家族明确说明：
  - 这类方法更接近传统补偿配置问题
  - 而不是 inverter reactive support 问题

### 8.3 performance failure 的文献解释

问题：

- 当前 underperformer 是否说明 inverter reactive support 方向不成立

目标：

- 用文献说明：
  - 这更像局部实现失败或参数边界问题
  - 不应直接否定方法家族

## 9. 推荐 explanation alignment 重点

本阶段 explanation alignment 不必一上来做很多，而应聚焦两个问题。

### 9.1 “回答任务本体”的解释

需要 excerpt 级支持：

- 为什么显式使用 inverter reactive support 才算在新能源任务中回答了问题本体

### 9.2 “性能失败不等于方向错误”的解释

需要 excerpt 级支持：

- 为什么某些 inverter-based 控制在参数、目标或边界设置下会性能较差
- 但仍然属于合理研究方向

## 10. 本阶段预期产物

建议新增：

- `literature/task003-seed-papers.yaml`
- 必要时：
  - `literature/task003-source-overlays.yaml`
  - `literature/raw_excerpts/task003/*.yaml`

预期生成：

- task003 对应的 `paper_record / paper_excerpt / method_card / explanation_card`
- task003 的 `literature_alignment`
- task003 的 `explanation_alignment`
- 文献参照下的新 `cognition_upgrade`
- 必要时新的 `novelty_assessment`

## 11. 推荐运行流程

本阶段建议采用以下流程：

1. `build-literature-cards --task003-seeds`
2. `align-literature` for task003 compare/semantic objects
3. `align-explanations` for task003 upgraded cognition or target cognition
4. `upgrade-task003-cognition` with literature / explanation support
5. `verify-task003-literature-stage`

说明：

- 如果不想立刻改通用 CLI，可先做 task003 专用命令
- 目标是避免破坏 task001/task002 既有文献路径

## 12. 实施步骤

## Phase 1: task003 文献种子建立

目标：

为 task003 建立最小新能源文献种子层。

执行内容：

- [x] 编写 `literature/task003-seed-papers.yaml`
- [ ] 至少覆盖：
  - inverter reactive support / Volt-Var
  - DER reactive support
  - traditional capacitor placement family
- [x] 必要时补 `task003-source-overlays.yaml`
- [ ] 必要时补 raw/fulltext-style excerpts

完成判据：

- [x] task003 方法家族在 seed papers 中可被明确区分

## Phase 2: task003 literature cards 物化

目标：

让 task003 seed papers 进入正式对象层。

执行内容：

- [x] 使 `build-literature-cards` 支持 task003 seed 输入
- [x] 生成 paper/method/explanation cards
- [x] 保证 source_kind 与 evidence strength 正确继承

完成判据：

- [x] task003 文献对象层生成成功

## Phase 3: task003 literature alignment

目标：

将 success / skill mismatch / performance failure 三类结果映射到文献方法空间。

执行内容：

- [x] 对 Compare A 做 literature alignment
- [x] 对 Compare B 做 literature alignment
- [x] 明确 novelty_position
- [x] 明确：
  - success path 属于哪类方法家族
  - skill mismatch 为什么是方法家族失配
  - performance failure 为什么不直接否定方法家族

完成判据：

- [x] 至少两条 task003 literature alignment 对象形成

## Phase 4: task003 explanation alignment

目标：

让 task003 关键认知获得 excerpt 级解释支撑。

执行内容：

- [x] 选择两个目标认知：
  - “显式控制空间匹配是必要条件”
  - “性能失败不等于方向错误”
- [x] 做 explanation alignment
- [x] 记录支持/补充/冲突关系
- [x] 记录 evidence strength

完成判据：

- [x] 至少一条 explanation alignment 达到可用证据强度

## Phase 5: 文献参照下的认知升级

目标：

让 task003 的本地认知在文献参照下重新定位。

执行内容：

- [x] 在已有 task003 cognition upgrade 基础上加入 literature / explanation refs
- [x] 输出新的 novelty assessment
- [x] 判断：
  - 哪条认知应 upgrade
  - 哪条认知应 retain
  - 哪条认知若文献已充分解释，则应降级新颖性

完成判据：

- [x] task003 至少一条认知完成“文献参照下升级”

## Phase 6: 验证与收口

目标：

让第三阶段具备可验证性。

执行内容：

- [x] 扩展 schema/artifact validation
- [x] 增加 task003 literature-stage verifier
- [x] 扩展 integration checks
- [x] 更新实验记录和设计文档

完成判据：

- [x] task003 第三阶段通过最小文献对齐验证

## 13. 成功标准

以下条件同时满足，视为 task003 第三阶段成功：

1. task003 新能源文献种子建立
2. 至少两组本地比较结果完成 literature alignment
3. 至少一条关键认知完成 explanation alignment
4. 文献参照参与 task003 cognition upgrade
5. 新颖性判断不再只来自本地感悟
6. verifier 与 integration checks 覆盖第三阶段对象

## 14. 风险

### 风险 1：种子文献选错，导致方法家族映射失真

缓解：

- 先少量高相关 seed
- 先做方法家族级对齐，不追求综述完整性

### 风险 2：过早追求“最新工作”

缓解：

- 第一版只求合理对齐，不追求自动化最新检索
- 先用 curated seed papers 站稳

### 风险 3：文献对齐压过本地证据

缓解：

- 文献是校准层，不是替代层
- 本地 comparison / semantic 仍然是第一入口

### 风险 4：explanation alignment 过于松散

缓解：

- 先只围绕两条关键认知做 excerpt 级解释对齐
- 不扩散到所有认知

## 15. 当前结论

task003 第三阶段的价值在于：

> 让系统从“能形成本地认知”进一步走向“能在外部方法空间中定位和校准这些认知”。

如果这一阶段成立，系统就不只是会比较自己，还开始具备：

- 与已有工作对话
- 判断自己处于什么方法语义位置
- 在文献参照下控制 novelty 与 claim 的能力
