# task001 收敛与 task002 准入计划

## 1. 计划目标

本计划用于将当前 `task001` 的实验性纵向切片收敛为稳定基线，使系统具备进入 `task002` 测试状态的条件。

当前 `task001` 已经完成：

- 真实电力任务接入
- baseline/candidate 技能运行
- evaluator 独立评估
- run/evidence/report/taste/cognition 写回
- weak-shunt 候选技能
- strategy comparison
- semantic comparison
- literature alignment
- explanation alignment
- cognition upgrade
- evidence-strength driven cognition control
- 集成测试脚本

本计划的目标不是继续扩展新能力，而是：

> 稳定 task001，固定测试基线，整理产物边界，确保系统可以安全进入 task002。

## 2. 核心原则

1. 基本闭环优先
2. 不再扩展文献能力
3. 不引入新任务前，先稳定 task001
4. 测试必须能证明当前纵向切片完整
5. task002 必须复用 task001 的框架能力，而不是重新造一套

## 3. 当前判断

当前系统已经证明：

- 能真实执行 task001
- 能发展 candidate skill
- 能独立评估
- 能结构化记录
- 能最小认知提炼
- 能做 taste 约束
- 能做写回积累
- 能做文献对齐和认知升级

但仍存在进入 task002 前必须处理的问题：

1. `runs/` 与 `analysis/` 下存在大量历史中间产物，缺少清晰标注
2. 集成测试仍依赖部分固定 artifact 编号
3. `orchestrator/main.py` 承载过多能力，边界逐渐变重
4. task002 的准入标准尚未正式定义
5. 当前测试仍偏脚本化，缺少更正式的测试分层

## 4. 成功标准

本计划完成后，必须满足：

1. `task001` 的核心纵向链路可一键验证
2. 集成测试不依赖脆弱编号
3. 关键产物有清晰说明，历史产物不再干扰判断
4. `orchestrator/main.py` 至少完成第一轮应用边界梳理或拆分计划
5. task002 准入标准明确
6. 所有当前验证命令通过

## 5. 验收标准

### 5.1 功能验收

- [x] `python scripts/run_integration_checks.py` 通过
- [x] `python orchestrator/main.py verify-task001-pipeline` 通过
- [x] `python scripts/validate_schemas.py` 通过
- [x] `python scripts/validate_schemas.py --artifacts literature-alignment-plan` 通过
- [x] `python -m py_compile orchestrator/main.py` 通过

### 5.2 稳定性验收

- [x] 集成测试不依赖过多固定 artifact 编号
- [x] 最新有效产物可被自动发现
- [x] `runs/task001` 与 `analysis/task001` 有说明文件或索引
- [x] 明确哪些产物是历史中间产物，哪些是当前推荐参考产物

### 5.3 解耦验收

- [x] 梳理 `orchestrator/main.py` 中的功能区域
- [x] 明确哪些能力应拆成独立应用模块
- [x] 至少完成一个低风险拆分，或形成可执行拆分计划
- [x] 保持 CLI 行为不变

### 5.4 task002 准入验收

- [x] 明确 task002 必须复用的对象和流程
- [x] 明确 task002 不允许重新发明的部分
- [x] 明确 task002 的最小任务包结构
- [x] 明确 task002 的最低成功标准和失败也算成功的条件

## 6. 实施步骤

## Phase 1: task001 产物整理

目标：

让后续开发者能看懂当前 task001 的有效产物和历史产物。

涉及目录：

- [runs/task001](/home/chenying/root-research/DaoShuGuo-v1/runs/task001)
- [analysis/task001](/home/chenying/root-research/DaoShuGuo-v1/analysis/task001)
- [cognition](/home/chenying/root-research/DaoShuGuo-v1/cognition)

执行内容：

- [x] 为 `runs/task001` 补充当前有效 run 索引
- [x] 为 `analysis/task001` 补充当前有效 analysis 索引
- [x] 标注推荐参考产物
- [x] 标注历史中间产物保留原因

完成判据：

- [x] 新进入仓库的人能知道应该看哪些产物

## Phase 2: 集成测试稳健化

目标：

让当前集成测试不依赖过多固定编号。

涉及文件：

- [run_integration_checks.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/run_integration_checks.py)
- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)

执行内容：

- [x] 改造集成测试为“发现最新有效产物”
- [x] 保留对 medium/high evidence path 的明确验证
- [x] 保留对 task001 纵向闭环的验证
- [x] 保证所有验证命令通过

完成判据：

- [x] 删除或新增若干中间运行产物不应轻易破坏测试

## Phase 3: orchestrator 边界梳理

目标：

避免 `orchestrator/main.py` 继续变成所有能力的宿主。

涉及文件：

- [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py)
- 可能新增：
  - `orchestrator/literature_app.py`
  - `orchestrator/comparison_app.py`
  - `orchestrator/cognition_app.py`

执行内容：

- [x] 划分当前 orchestrator 中的能力区域
- [x] 识别低风险拆分边界
- [ ] 优先拆出文献对象生成或比较分析中的一个模块
- [x] 保持 CLI 行为不变

完成判据：

- [x] 至少一个能力从 main.py 中低风险拆出，或形成明确拆分计划

## Phase 4: task002 准入规范

目标：

定义 task002 进入测试前必须满足的条件。

建议新增文件：

- `plans/task002-admission-plan.md`
- 或 `docs/task002准入规范.md`

执行内容：

- [x] 定义 task002 最小任务包结构
- [x] 定义 task002 必须复用的 schema 与 registry
- [x] 定义 task002 允许不同的部分
- [x] 定义 task002 的最低成功标准
- [x] 定义 task002 失败也算成功的条件

完成判据：

- [x] task002 不会重新发明 task001 已有机制

## Phase 5: 最终验证与提交

目标：

固定 task001 稳定基线。

执行内容：

- [x] 跑完整验证命令
- [x] 更新 review 记录
- [x] 更新实验过程记录
- [x] Git 提交

完成判据：

- [x] 工作区干净
- [x] Git 中有稳定基线提交

## 7. 风险

### 风险 1：过度整理导致打断现有产物链

缓解：

- 不删除历史产物
- 只补索引和说明

### 风险 2：过早重构 orchestrator

缓解：

- 只做低风险拆分
- 或先形成拆分计划，不强行大改

### 风险 3：task002 目标过大

缓解：

- task002 准入规范必须强调最小任务包
- 不允许直接跳到复杂系统任务

## 8. 验证命令

必须通过：

- [x] `python scripts/run_integration_checks.py`
- [x] `python orchestrator/main.py verify-task001-pipeline`
- [x] `python scripts/validate_schemas.py`
- [x] `python scripts/validate_schemas.py --artifacts literature-alignment-plan`
- [x] `python -m py_compile orchestrator/main.py`

## 9. 结论

本计划完成后，项目可以正式进入：

> task002 测试准备状态

但前提是：

- task001 不再只是实验堆积
- 而是成为一个稳定、可复现、可交接的纵向样板。
