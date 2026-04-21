# task002: IEEE69 配电网无功补偿优化迁移验证

`task002` 的目标不是重新发明 `task001` 的框架，而是验证当前闭环在第二个相邻任务上是否还能成立。

本任务聚焦以下问题：

1. `task001` 的 task / baseline / evaluator / run 对象能否迁移到 `IEEE69`。
2. `weak_bus_shunt_optimizer` 这一类候选技能能否在新网络上继续真实运行。
3. evaluator / taste / evidence / report 写回机制是否仍然成立。

当前最小边界：

- 仅覆盖 IEEE69 径向配电网单工况。
- 仅覆盖基线 ext-grid 电压设定与 weak-shunt 迁移 candidate。
- 不追求论文级最优结果，只验证真实迁移闭环是否成立。
