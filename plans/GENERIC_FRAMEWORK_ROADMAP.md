# 通用框架恢复与推进实施路线图

**目标**: 将 DaoShuGuo-v1 从 task-specific 硬编码架构迁移到 adapter 驱动的通用框架

**基准日期**: 2026-04-27
**预计周期**: 4-6 周
**风险等级**: 高（涉及核心架构变更）

---

## 现状诊断

### 已具备的基础
- ✅ `archive/legacy-scripts/run_generic_loop_engine.py` - 完整的通用引擎实现（484行）
- ✅ `adapters/*.yaml` - 10个 task adapter 已定义
- ✅ `schemas/` - 完整的数据契约定义
- ✅ 验证脚本设计文档

### 当前债务
- ❌ 489 处硬编码 task 引用在 orchestrator/main.py
- ❌ Pi Skill 使用 `run_task003_trial` 而非通用工具
- ❌ task007_fixture 验证未实现（AGENTS.md 验收标准）
- ❌ 通用引擎被归档，未在使用

---

## 实施阶段

### Phase 0: 准备工作（Week 1）

#### 0.1 恢复通用引擎
**动作**:
```bash
# 1. 恢复核心文件
mv archive/2026-04-26-pre-workbench-ui-cleanup/legacy-scripts/run_generic_loop_engine.py scripts/
mv archive/2026-04-26-pre-workbench-ui-cleanup/legacy-scripts/backend_registry.py scripts/
mv archive/2026-04-26-pre-workbench-ui-cleanup/legacy-scripts/generic_diagnosis_layer.py scripts/
mv archive/2026-04-26-pre-workbench-ui-cleanup/legacy-scripts/worker_chain_helpers.py scripts/

# 2. 创建通用 fixture workers
mv archive/2026-04-26-pre-workbench-ui-cleanup/legacy-scripts/generic_loop_engine_fixture_workers.py scripts/
```

**验收**:
- [x] `python scripts/run_generic_loop_engine.py --help` 可执行
- [x] 无导入错误
- [x] 基础单元测试通过

#### 0.2 创建 task007_fixture（AGENTS.md 验收标准）
**动作**:
```bash
# 创建最小 fixture task 目录结构
mkdir -p tasks/task007_fixture
cat > tasks/task007_fixture/task.yaml << 'EOF'
schema_version: "0.1.0"
object_type: "task"
object_id: "task.power.task007_fixture"
object_version: "0.1.0"
status: "active"
title: "Task007 Fixture for Generic Onboarding Validation"
research_object: "最小 fixture 用于验证通用任务接入"
scenario_boundary:
  grid_model: "placeholder"
success_intent:
  goal: "验证框架可在不修改代码的情况下接入新 task"
  non_goal: "不执行真实仿真"
baseline_refs: []
constraint_summary:
  research: ["fixture is intentionally incomplete"]
EOF

# 创建对应 adapter
cat > adapters/task007_fixture.yaml << 'EOF'
schema_version: "0.1.0"
object_type: "task_adapter"
object_id: "task_adapter.power.task007_fixture"
object_version: "0.1.0"
status: "active"
metadata:
  protocol: "generic-task-onboarding"
task_id: "task007_fixture"
task_ref: "task.power.task007_fixture"
task_package_path: "tasks/task007_fixture"
runtime_entry:
  type: "python_script"
  path: "scripts/generic_fixture_runner.py"
metrics_mapping: {}
candidate_skill_refs: []
fallback_skill_refs: []
claim_gates: []
known_task_risks:
  - "fixture is intentionally incomplete"
supported_downstream_stages:
  - "framing"
EOF
```

**验收**:
- [x] task007_fixture 可被通用 onboarding 入口加载
- [x] 生成 readiness report
- [x] 明确显示 "fixture is intentionally incomplete"

#### 0.3 创建通用 onboarding 验证脚本
**文件**: `scripts/verify_generic_task_onboarding.py`

**功能**:
```python
# 验证 checklist:
# 1. task package 是否完整
# 2. baseline 是否存在
# 3. evaluator 是否存在且可绑定
# 4. runtime entry 是否存在
# 5. candidate skill 或 fallback skill 是否存在
# 6. metrics mapping 是否明确
# 7. claim gate 是否可用
# 8. structural-learning / portfolio 是否可路由

# 输出:
# - readiness report (YAML)
# - 路由决策: run / repair_task_package / repair_evaluator / repair_adapter / framing_only / pause
```

**验收**:
- [x] `python scripts/verify_generic_task_onboarding.py --task task007_fixture` 通过
- [x] `python scripts/verify_generic_task_onboarding.py --task task003` 通过
- [x] `python scripts/verify_generic_task_onboarding.py --task task004` 通过
- [x] 新 task 无需修改框架代码即可被识别

---

### Phase 1: 统一 CLI 接口（Week 2）

#### 1.1 创建通用运行命令
**目标**: 替代 `real-run-task003`, `real-run-task004` 等硬编码命令

**方案 A: Adapter 驱动（推荐）**
```bash
# 新接口
python orchestrator/main.py real-run \
  --task-ref task.power.ieee69_renewable_reactive_opt \
  --adapter adapters/task003.yaml \
  --strategy inverter-support

# 或更简洁
python orchestrator/main.py real-run \
  --task task003 \
  --strategy inverter-support
```

**方案 B: 兼容层（过渡）**
```python
# orchestrator/main.py 中新增统一入口
def cmd_real_run(args):
    """Unified real-run command using adapter."""
    adapter = load_adapter(args.task)
    if adapter['metadata']['protocol'] == 'legacy-hardcoded':
        # 回退到旧实现
        return legacy_run(args)
    else:
        # 使用通用引擎
        return generic_run(adapter, args)
```

#### 1.2 重构 orchestrator 路由
**修改** `orchestrator/main.py`:
```python
# 当前（硬编码）
def cmd_real_run_task003(args): ...
def cmd_real_run_task004(args): ...

# 新（通用路由）
def cmd_real_run(args):
    """Generic task runner based on adapter."""
    task_id = args.task
    adapter_path = REPO_ROOT / "adapters" / f"{task_id}.yaml"
    
    if not adapter_path.exists():
        raise RuntimeError(f"No adapter found for task {task_id}")
    
    # 使用通用引擎
    return run_generic_loop_engine(
        task_adapter_path=adapter_path,
        strategy=args.strategy,
        ...
    )
```

**验收**:
- [ ] `python orchestrator/main.py real-run --task task003 --strategy inverter-support` 成功
- [ ] 结果与旧命令一致
- [ ] task004, task005 同样工作

#### 1.3 创建适配器转换工具
**脚本**: `scripts/migrate_task_to_adapter.py`

**功能**:
- 将现有硬编码 task 配置导出为 adapter.yaml
- 验证 adapter 完整性
- 生成迁移报告

**验收**:
- [ ] task001-task005 全部有对应 adapter
- [ ] 迁移报告通过验证

---

### Phase 2: 重构 Pi Skill（Week 3）

#### 2.1 创建通用 Pi Tool
**文件**: `pi-packages/daoshuguo-research-loop/extensions/daoshuguo-research-loop/index.ts`

**新增 Tool**:
```typescript
// 替代 run_task003_trial, run_task004_trial
pi.registerTool({
  name: "run_task_trial",
  label: "Run Task Trial",
  description: "Execute a DaoShuGuo task trial using the generic loop engine.",
  parameters: Type.Object({
    task_ref: Type.String({ description: "Task reference (e.g., task.power.ieee69_renewable_reactive_opt)" }),
    task_id: Type.String({ description: "Task ID (e.g., task003)" }),
    strategy: Type.Optional(Type.String({ default: "default" })),
    candidate_params: Type.Optional(Type.Object({})),
  }),
  async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
    const repoRoot = ctx.cwd;
    const cmd = `python orchestrator/main.py real-run --task ${params.task_id} --strategy ${params.strategy}`;
    
    const result = await runCommand(cmd, repoRoot);
    
    // 解析 run_ref, report_ref
    const runDir = result.exitCode === 0 ? parseTaskRunPath(result.stdout) : null;
    const runRef = runDir ? parseRunRefFromRunYaml(runDir) : null;
    
    // 记录到 research_loop
    appendJsonl(ctx.cwd, {
      timestamp: now(),
      event: "task_trial",
      task_ref: params.task_ref,
      data: {
        task_id: params.task_id,
        strategy: params.strategy,
        exitCode: result.exitCode,
        runDir,
        runRef,
      },
    });
    
    return {
      content: [{ type: "text", text: `Task trial completed: ${result.stdout}` }],
      details: { task_id: params.task_id, runRef, exitCode: result.exitCode },
    };
  },
});
```

#### 2.2 更新 SKILL.md
```markdown
## Steps (Updated)

1. Identify the current task reference and objective.
2. Call `init_research_task` with the task reference and objective.
3. Read `research_loop.md`.
4. Use `run_task_trial` with task_id and strategy to execute trials.
   - Example: `run_task_trial(task_ref="...", task_id="task003", strategy="inverter-support")`
5. Call `log_research_iteration` after each meaningful action.
6. Call `record_skill_trial` after a concrete skill trial.
```

#### 2.3 保留向后兼容（过渡）
```typescript
// 旧工具标记为 deprecated
pi.registerTool({
  name: "run_task003_trial",
  label: "[DEPRECATED] Run Task003 Trial",
  description: "Deprecated: Use run_task_trial instead.",
  // 内部调用 run_task_trial
  async execute(...) {
    console.warn("run_task003_trial is deprecated, use run_task_trial");
    return runTaskTrial({ task_id: "task003", ... });
  },
});
```

**验收**:
- [ ] `run_task_trial(task_id="task003")` 工作
- [ ] `run_task_trial(task_id="task004")` 工作
- [ ] 新增 task 无需修改 Pi Skill 代码
- [ ] research_loop.jsonl 记录正确

---

### Phase 3: 全面迁移（Week 4-5）

#### 3.1 Task 迁移矩阵

| Task | Adapter 状态 | 迁移动作 | 验证 |
|------|-------------|---------|------|
| task001 | ✅ 创建 | 创建 adapter, 验证 | ✅ |
| task002 | ✅ 创建 | 创建 adapter, 验证 | ✅ |
| task003 | ✅ 存在 | 验证通过 | ✅ |
| task004 | ✅ 存在 | 验证通过 | ✅ |
| task005 | ✅ 存在 | 验证通过 | ✅ |
| task007_fixture | ✅ 存在 | 创建 adapter, 验证 | ✅ |

#### 3.2 Orchestrator 清理
**删除/标记**:
```python
# 删除或标记为 @deprecated
# - cmd_real_run_task003
# - cmd_real_run_task004
# - cmd_real_run_task005
# - TASK_RUN_CONTEXTS 硬编码部分
# - 所有 task-specific solver path 硬编码

# 保留内部实现但路由统一
```

#### 3.3 统一验证
**脚本**: `scripts/verify_all_tasks_generic.py`

```bash
# 验证所有 task 可通过通用接口运行
python scripts/verify_all_tasks_generic.py \
  --tasks task001,task002,task003,task004,task005 \
  --output verification_report.yaml
```

**验收标准**:
- [x] 所有 task 通过通用接口运行
- [x] 结果与硬编码版本一致（误差 < 1%）
- [x] 性能差异 < 10%

---

### Phase 4: AGENTS.md 验收验证（Week 6）

#### 4.1 验收清单

根据 AGENTS.md 第15节要求:

| 验收项 | 验证命令 | 状态 |
|--------|---------|------|
| 1. task003/004/005 可通过同一 onboarding 命令生成 readiness report | `verify_generic_task_onboarding.py --task task003` | ✅ |
| 2. task007_fixture 在不新增框架代码的情况下被识别和诊断 | `verify_generic_task_onboarding.py --task task007_fixture` | ✅ |
| 3. 缺失字段产生明确 blocked report | 故意损坏 adapter，验证报告 | ✅ |
| 4. readiness report 给出下一步路由 | 检查 report 包含 routing decision | ✅ |

#### 4.2 集成测试
```bash
# 端到端测试
python scripts/run_integration_checks.py

# 特定测试
python scripts/verify_pi_task003_bridge.py  # 已存在
python scripts/verify_pi_task004_bridge.py  # 需创建
python scripts/verify_generic_task_bridge.py --task task007_fixture  # 需创建
```

#### 4.3 Pi Skill 验收
```bash
# 验证 Pi Skill 通用工具
pi install /path/to/daoshuguo-research-loop

# 在 Pi 中执行
/daoshuguo
run_task_trial(task_ref="...", task_id="task003")
run_task_trial(task_ref="...", task_id="task007_fixture")
```

**最终验收**:
- [ ] AGENTS.md 15.3 所有验收项通过
- [ ] 新增 task007_fixture 无需修改框架代码
- [ ] Pi Skill 使用通用 tool
- [ ] Orchestrator 无硬编码 task 引用（或仅有向后兼容层）

---

## 风险管理

### 风险 1: 迁移期间系统不稳定
**缓解**:
- 保持向后兼容层
- 使用 feature flag: `--use-generic-engine`
- 分 task 逐步迁移，非一次性切换

### 风险 2: 性能回归
**缓解**:
- 每个 task 迁移前记录基准性能
- 自动化性能对比测试
- 允许 10% 性能损失，超阈值则回滚

### 风险 3: 功能不一致
**缓解**:
- 每个 task 完整验证套件
- 对比新旧实现输出
- 差异分析工具

### 风险 4: 文档不同步
**缓解**:
- 每 Phase 更新 AGENTS.md
- 更新 README 运行命令
- 更新 Pi Skill SKILL.md

---

## 成功标准

### 技术成功
1. ✅ `run_generic_loop_engine.py` 成为主要运行入口
2. ✅ `orchestrator/main.py real-run --task <id>` 工作
3. ✅ `run_task_trial` 替代所有 `run_taskXXX_trial`
4. ✅ task007_fixture 验证通过
5. ✅ 新增 task 无需修改框架代码

### 文档成功
1. ✅ AGENTS.md 更新，移除 task-specific 警告
2. ✅ README.md 更新运行命令
3. ✅ 新增 `docs/GENERIC_FRAMEWORK_MIGRATION.md`

### 验收成功
1. ✅ AGENTS.md 15.3 所有验收标准通过
2. ✅ 集成测试全部通过
3. ✅ Pi Skill 验证通过

---

## 下一步行动

**立即执行** (今天):
1. 评审本计划
2. 创建 feature branch: `feature/generic-framework`
3. 开始 Phase 0.1: 恢复通用引擎

**本周完成**:
- Phase 0 全部完成
- task007_fixture 可用

**下周完成**:
- Phase 1 全部完成
- 统一 CLI 接口可用

---

**计划作者**: Claude
**日期**: 2026-04-27
**版本**: 1.0
