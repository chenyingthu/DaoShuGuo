# task004: 新能源接入承载力评估任务

`task004` 的目标是验证系统能否从“优化一个控制量”上升到“判断系统边界”。

第一版将“承载力”限定为：

> 在单代表工况下、给定控制策略、约束条件和当前扫描包络内，系统能够容纳的最大新能源接入水平。

本任务不追求完整 hosting capacity 研究，而只验证：

- 承载力定义能否被清晰形式化
- baseline 与 candidate 是否能输出结构化边界
- failure 是否能区分：
  - skill mismatch
  - task mismatch
  - boundary overclaim

本任务不支持系统普适承载力或长期时序承载力结论。

第一版的承载力边界使用 `screening threshold`，其作用是得到可比较的边界扫描结果，而不是替代正式工程标准。
