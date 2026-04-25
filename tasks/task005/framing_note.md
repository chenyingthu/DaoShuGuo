# task005 Framing Note

## Core Decision

task005 第一版把“韧性恢复”限定为：

> 单故障、单工况、最小恢复动作集下的局部恢复能力判断。

## Why This Scope

- 先验证事件驱动任务能否进入框架
- 避免一开始进入复杂保护与时序恢复
- 保证 failure taxonomy 与 claim boundary 可被清晰判断

## Overclaim Guard

不得将当前结果写成：

- 系统普适韧性
- 任意故障下恢复能力
- 工程级恢复调度结论
