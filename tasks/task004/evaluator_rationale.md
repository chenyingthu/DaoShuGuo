# task004 Evaluator Rationale

## Why Task004 Needs a Different Evaluator

task004 评估的不是单点性能改进，而是边界。

因此 evaluator 的核心不再是：

- 当前一次 run 的 loss 是否更低

而是：

- 在什么接入水平第一次触碰边界
- 边界由什么触发
- 该边界在边界点上的损耗与电压裕度如何

第一版使用 `vm_min=0.91` 的 screening threshold，目的是在当前基础网络上形成可比较的边界扫描结果，而不是直接给出工程运行标准意义下的最终承载力。

同时，第一版承载力必须理解为：

- 在当前扫描包络内
- 可审计、可比较的
- 控制策略相关边界

## Minimal Metrics

1. `hosting_capacity_level`
2. `violation_trigger_type`
3. `loss_at_boundary`
4. `voltage_margin`

## Claim Discipline

即使 candidate 提高了承载力边界，当前也只能表述为：

- 在给定控制策略下
- 单代表工况下
- 静态约束驱动的

边界变化。
