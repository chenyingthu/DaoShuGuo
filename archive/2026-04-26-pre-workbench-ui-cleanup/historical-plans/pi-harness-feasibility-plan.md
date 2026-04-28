# Pi Harness 可行性验证计划

## 1. 背景

DaoShuGuo 当前已经验证了数据契约、技能层、认知层、成效层和若干真实 task slice。

但在尝试用 Codex 实现真实 `skill agent <-> cognition agent` 多轮闭环时，暴露出一个底层问题：

> 成熟 agentic coding 产品很强，但并不一定适合作为可被科研框架精确 harness 的底层 agent runtime。

Codex / Claude Code / opencode 这类环境拥有自己的 session、sandbox、approval、tool policy、状态恢复与执行模型。我们要控制它们时，经常是在和既有产品架构搏斗。

因此，本计划转向验证 Pi：

- https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent
- https://github.com/davebcn87/pi-autoresearch

目标是判断 Pi 是否能成为 DaoShuGuo 的底层 agent harness。

## 2. 验证目标

本阶段只验证底座，不迁移完整系统。

要回答：

1. Pi 是否能在本机构建和运行
2. Pi 是否支持可控的非交互/JSON/RPC/SDK 使用方式
3. Pi package 是否能把 extension + skill 组合成可安装能力包
4. pi-autoresearch 是否提供了可借鉴的 autonomous experiment loop
5. DaoShuGuo 是否可以用同样方式实现 research-loop harness

## 3. 验证步骤

- [x] Clone `badlogic/pi-mono`
- [x] Clone `davebcn87/pi-autoresearch`
- [x] 安装 Pi monorepo dependencies
- [x] 构建 Pi monorepo
- [x] 运行 Pi CLI `--help` / `--version`
- [x] 安装 `pi-autoresearch` 到隔离 HOME
- [x] 验证 Pi package discovery
- [x] 创建最小 `daoshuguo-pi-research-loop` package 原型
- [x] 安装最小 DaoShuGuo Pi package
- [x] 验证 Pi JSON mode 事件输出

## 4. 当前验证结果

### 4.1 本机环境

- Node: `v22.22.0`
- npm: `11.7.0`
- pnpm: `10.31.0`

满足 Pi package 的 Node 要求。

### 4.2 Pi 源码构建

Pi monorepo 在 `/tmp/daoshuguo-pi-feasibility/pi-mono` 中成功 clone。

依赖安装：

```bash
npm install
```

结果：

- installed 537 packages
- audited 550 packages
- found 0 vulnerabilities

构建：

```bash
npm run build
```

注意：

- 普通沙箱中 `tsx` 创建 IPC pipe 被拒绝
- 提权运行后构建成功
- 构建阶段成功生成 865 个 tool-capable model entries

### 4.3 Pi CLI 验证

隔离 HOME：

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home
```

CLI:

```bash
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js --help
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js --version
```

结果：

- `--version` 输出 `0.68.1`
- `--help` 成功展示：
  - `--mode text/json/rpc`
  - `--print`
  - `--extension`
  - `--skill`
  - `--tools`
  - `--no-tools`
  - `--session-dir`
  - `PI_CODING_AGENT_DIR`

### 4.4 pi-autoresearch 验证

`pi-autoresearch` 结构：

- `package.json`
  - `pi.extensions`
  - `pi.skills`
- `extensions/pi-autoresearch/index.ts`
- `skills/autoresearch-create/SKILL.md`
- `skills/autoresearch-finalize/SKILL.md`

安装命令：

```bash
pi install /tmp/daoshuguo-pi-feasibility/pi-autoresearch
```

结果：

```text
Installed /tmp/daoshuguo-pi-feasibility/pi-autoresearch
```

`pi list` 可见该 package。

### 4.5 DaoShuGuo Pi package 原型

创建了隔离原型：

```text
/tmp/daoshuguo-pi-feasibility/daoshuguo-pi-package
```

内容：

- `package.json`
- `extensions/daoshuguo-research-loop/index.ts`
- `skills/daoshuguo-research-create/SKILL.md`

最小 extension 提供：

- `init_research_task`
- `log_research_iteration`
- `/daoshuguo` command
- `before_agent_start` 注入 `research_loop.md`

安装命令：

```bash
pi install /tmp/daoshuguo-pi-feasibility/daoshuguo-pi-package
```

结果：

```text
Installed /tmp/daoshuguo-pi-feasibility/daoshuguo-pi-package
```

`pi list` 可见：

- `pi-autoresearch`
- `daoshuguo-pi-package`

### 4.6 JSON mode 验证

命令：

```bash
pi --no-session --no-tools --no-context-files --mode json -p --provider openai --model gpt-4o-mini --api-key dummy "Say ok"
```

结果：

- JSON events 正常输出：
  - `session`
  - `agent_start`
  - `turn_start`
  - `message_start`
  - `message_end`
  - `turn_end`
  - `agent_end`
  - `auto_retry_start`
  - `auto_retry_end`
- 因 dummy key / 网络条件，模型调用报 `Connection error`
- 这不影响 harness 验证，反而证明 JSON event stream 可被外部 orchestrator 捕获

## 5. 关键发现

### 5.1 Pi 的核心优势

Pi 不是一个重产品式 coding agent，而是一个 minimal terminal coding harness。

它提供：

- TypeScript extension
- skills
- prompt templates
- package
- print/json/rpc/sdk modes
- lifecycle event hooks
- tool call/result interception
- system prompt injection
- command registration

这非常适合 DaoShuGuo。

### 5.2 pi-autoresearch 的关键启发

pi-autoresearch 的真正价值是架构分离：

> Extension 提供通用实验循环基础设施；Skill 提供领域知识。

这正是 DaoShuGuo 需要的：

- extension 管 run/log/keep/revert/dashboard
- skill 管 task/evaluator/cognition/claim boundary

### 5.3 DaoShuGuo 可以迁移为 Pi package

最小原型已经证明：

- DaoShuGuo 可以以 Pi package 形式存在
- 可以注册工具
- 可以注册 skill
- 可以注入 durable memory
- 可以写 `research_loop.md` 与 `research_loop.jsonl`

## 6. 当前限制

本轮还没有验证：

- 真实模型 API 下完整跑一轮 Pi agent
- DaoShuGuo extension 工具被 LLM 主动调用
- Pi RPC / SDK 的完整外部控制
- 与现有 task003 evaluator 的真实连接

这些应放到下一阶段。

## 7. 建议结论

Pi 可作为 DaoShuGuo 下一阶段 agent harness 的主要候选。

建议停止继续在 Codex 上硬做多轮 agentic loop，把下一阶段改为：

> DaoShuGuo-on-Pi 最小垂直切片。

第一目标不是“做强科研”，而是证明：

1. Pi agent 能在 `research_loop.md/jsonl` 约束下运行
2. extension 能稳定记录 loop 事件
3. skill agent 的行为可以被 package/extension harness
4. cognition constraints 可以进入下一轮 skill work，而不是散成聊天文本

