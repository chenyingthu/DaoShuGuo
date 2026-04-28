# DaoShuGuo-on-Pi 最小垂直切片计划

## 1. 目标

本计划目标是在仓库内建立一个最小 Pi package，使 DaoShuGuo 能以 Pi extension + skill 的方式运行一个受控 research-loop。

本阶段不追求完整科研 agent，只验证：

1. DaoShuGuo 可以作为 Pi package 存在
2. package 可以被 Pi 安装和发现
3. extension 可以定义 durable research-loop 工具
4. skill 可以约束 agent 的科研行为
5. 不依赖真实 LLM 时，也能本地模拟 `research_loop.md/jsonl` 的行为

## 2. 实施内容

- [x] 创建 repo-local Pi package
- [x] 添加 `daoshuguo-research-loop` extension
- [x] 添加 `daoshuguo-research-create` skill
- [x] 添加 `run_task003_trial` tool bridge
- [x] 添加本地 simulation script
- [x] 生成 `research_loop.md`
- [x] 生成 `research_loop.jsonl`
- [x] 用 Pi CLI 安装并发现仓库内 package
- [x] 验证 Pi-style task003 bridge 可触发真实 run

## 3. 文件

Pi package:

- `pi-packages/daoshuguo-research-loop/package.json`
- `pi-packages/daoshuguo-research-loop/extensions/daoshuguo-research-loop/index.ts`
- `pi-packages/daoshuguo-research-loop/skills/daoshuguo-research-create/SKILL.md`

本地模拟:

- `scripts/simulate_pi_research_loop.py`

模拟输出:

- `analysis/pi_harness/task003_sim/research_loop.md`
- `analysis/pi_harness/task003_sim/research_loop.jsonl`
- `analysis/pi_harness/task003_bridge_demo/research_loop.md`
- `analysis/pi_harness/task003_bridge_demo/research_loop.jsonl`

## 4. 已验证结果

### 4.1 Pi package 安装发现

命令：

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home \
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js \
install /home/chenying/root-research/DaoShuGuo-v1/pi-packages/daoshuguo-research-loop
```

结果：

```text
Installed /home/chenying/root-research/DaoShuGuo-v1/pi-packages/daoshuguo-research-loop
```

`pi list` 可见该 package。

### 4.2 本地 research-loop simulation

命令：

```bash
python scripts/simulate_pi_research_loop.py
```

结果：

```json
{
  "workdir": ".../analysis/pi_harness/task003_sim",
  "markdown": ".../analysis/pi_harness/task003_sim/research_loop.md",
  "jsonl": ".../analysis/pi_harness/task003_sim/research_loop.jsonl",
  "entries": 2
}
```

说明：

- durable markdown memory 可生成
- append-only JSONL event log 可生成
- skill trial 事件可记录

### 4.3 task003 bridge

命令：

```bash
python scripts/verify_pi_task003_bridge.py
```

结果：

```json
{
  "exit_code": 0,
  "stdout": "Task003 real run written to .../runs/task003/run_0011",
  "stderr": ""
}
```

这说明：

- Pi-style extension tool 完全可以桥接到现有 DaoShuGuo Python orchestrator
- 不需要先重写 evaluator / task runner
- 可以先把 Pi 当作上层 harness，把现有 Python 体系当作 domain runtime

## 5. 当前能力

当前已经具备：

- repo-local Pi package
- research loop 初始化工具
- iteration log 工具
- skill trial 记录工具
- cognition constraint 记录工具
- iteration review 记录工具
- task003 real-run bridge 工具
- `/daoshuguo` command
- `before_agent_start` research_loop 注入
- 离线本地 simulation
- 本地 task003 bridge 验证

## 6. 尚未完成

还没有验证：

- 真实 LLM provider 下 Pi agent 是否主动调用这些工具
- Pi RPC/SDK 由外部 orchestrator 控制
- keep/revert/commit 的完整实验循环
- cognition constraints 如何通过 Pi package 进入下一轮 skill work

## 7. 下一步

下一阶段应做：

1. 用 Pi JSON/RPC mode 触发一次真实 task003 trial
2. 将 run result 写入 `research_loop.jsonl`
3. 在真实流程中调用 `record_cognition_constraint`
4. 在真实流程中调用 `record_iteration_review`
5. 验证 cognition constraints 能以字段形式进入下一轮
