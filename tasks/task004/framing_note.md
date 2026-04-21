# task004 Framing Note

## Core Framing Decision

task004 将“承载力评估”限定为：

> 在单代表工况、给定控制策略和当前扫描包络内的最大允许新能源接入水平。

## Why This Scope

- 避免一开始就进入长期时序 hosting capacity 的复杂问题。
- 保持与 task003 的新能源接入 runtime 连续。
- 让控制策略在边界判断中显式可比较。

## Boundary Overclaim Guard

task004 必须防止以下错误：

- 把策略相关承载力写成系统固有承载力
- 把单工况边界写成普适边界
- 把扫描包络内边界写成系统真实极限承载力

## Failure Types

- `skill mismatch`: 用局部优化 skill 直接替代边界评估
- `task mismatch`: 承载力定义、边界约束或控制策略条件未说清
- `boundary overclaim`: 边界结果被过度表述
