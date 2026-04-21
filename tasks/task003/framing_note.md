# task003 Framing Note

## Framing Decision

本任务将“考虑新能源接入的无功补偿与优化调控”收敛为一个单代表工况下的 IEEE69 + PV inverter 无功支撑任务。

## Why This Scope

- 保持与 task002 网络连续，减少非核心变量。
- 引入 inverter Q 控制，体现新能源接入带来的控制对象变化。
- 保留传统 shunt 作为 skill-mismatch probe 的参照。

## What Is Not Claimed

- 不声称覆盖新能源波动。
- 不声称经济最优。
- 不声称多设备协调控制已完整解决。

## Mismatch Definitions

- `skill mismatch`: evaluator/task 成立，但旧 skill 不适配 inverter 控制空间。
- `task mismatch`: task/evaluator 必填定义项缺失，不能进入真实执行。
