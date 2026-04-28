# DaoShuGuo-v1 目录结构说明

本文档说明项目目录结构，帮助理解哪些是**核心框架代码**，哪些是**运行时配置**，哪些是**生成内容**。

## 核心框架代码（Core Framework）

这些目录包含框架的核心实现，应该提交到 git：

```
scripts/                    # 核心脚本（通用引擎、验证工具等）
├── run_generic_loop_engine.py      # 通用循环引擎
├── generic_diagnosis_layer.py      # 诊断层
├── backend_registry.py             # 后端注册表
├── verify_generic_loop_engine.py   # 验证工具
└── ...

orchestrator/               # 编排器
├── main.py                         # 主入口（统一 CLI）
└── ...

schemas/                    # 数据契约定义（JSON Schema）
├── run.schema.json
├── task.schema.json
├── adapter.schema.json
└── ...

configs/                    # 运行时配置
└── agent_runtimes/
    └── registry.yaml             # Agent 运行时注册表

tests/                      # 测试框架
├── test_*.py                     # 单元测试
└── fixtures/                     # 测试 fixtures（示例配置）
    ├── adapters/                 # 示例 adapter 配置
    └── tasks/                    # 示例 task 定义

pi-packages/                # Pi Skill 扩展
└── daoshuguo-research-loop/
    └── extensions/
        └── daoshuguo-research-loop/
            └── index.ts          # Pi Skill 实现
```

## 运行时配置（Runtime Configuration）

这些目录包含任务和 adapter 的定义，是框架的输入配置：

```
adapters/                   # Task adapter 配置文件
├── task003.yaml                  # Task003 配置（IEEE 69 可再生能源无功优化）
├── task004.yaml                  # Task004 配置（承载能力分析）
├── task005.yaml                  # Task005 配置
├── task007_fixture.yaml          # Fixture 用于框架验证
└── ...

tasks/                      # Task 定义和数据
├── task003/                      # Task003 数据和 baseline
├── task004/                      # Task004 数据和 baseline
├── task007_fixture/              # Fixture task 定义
└── ...

evaluators/                 # Evaluator 配置和证据
literature/                 # 文献库
skills/                     # Skill 定义
cognition/                  # Cognition agent 定义
effectiveness/              # Effectiveness 评估定义
```

**注意**：虽然这些是配置而非核心代码，但它们描述了框架要执行的任务，应该随框架一起版本控制。

## 运行时生成内容（Runtime Generated）

这些目录包含框架运行时生成的内容，**不应该提交到 git**（已在 .gitignore 中排除）：

```
runs/                       # 任务执行结果（每次运行生成的 run.yaml, report.yaml 等）
├── task003/
│   ├── run_0001/
│   ├── run_0002/
│   └── ...
└── ...

analysis/                   # 分析报告
├── onboarding/             # Task onboarding 报告
└── ...

workbench_data/             # 工作台运行时数据
memory/                     # 会话记忆（session-specific）
research_loop.jsonl         # Pi Skill 运行时日志
research_loop.md            # Pi Skill 运行时笔记
```

## 规划和文档

```
plans/                      # 实施计划
├── GENERIC_FRAMEWORK_ROADMAP.md   # 通用框架迁移路线图
└── ...

docs/                       # 设计文档
├── DIRECTORY_STRUCTURE.md         # 本文件
├── AGENTS.md                      # Agent 设计文档
└── ...

reviews/                    # 代码审查记录
```

## 归档和历史

```
archive/                    # 历史归档（旧实现、备份等）
```

## 快速判断指南

| 内容类型 | 示例 | 是否提交 git |
|---------|------|-------------|
| 核心代码 | `scripts/*.py`, `orchestrator/*.py` | ✅ 是 |
| 数据契约 | `schemas/*.json` | ✅ 是 |
| Task 配置 | `adapters/*.yaml`, `tasks/task*/` | ✅ 是（配置即代码） |
| 运行结果 | `runs/*/`, `analysis/*/` | ❌ 否（运行时生成） |
| 测试代码 | `tests/*.py` | ✅ 是 |
| 缓存 | `__pycache__/`, `.pytest_cache/` | ❌ 否 |
| 日志 | `research_loop.jsonl` | ❌ 否 |

## 新增 Task 的正确位置

如果要新增一个 task（例如 task006）：

1. **配置**：创建 `adapters/task006.yaml`
2. **定义**：创建 `tasks/task006/` 目录，包含 `task.yaml` 和数据文件
3. **测试**：添加 `tests/test_task006.py`（如果需要）

不要修改框架代码，只需添加配置即可。
