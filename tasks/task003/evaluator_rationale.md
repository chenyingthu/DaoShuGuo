# task003 Evaluator Rationale

## Metric Choice

task003 沿用 task001/task002 的三个硬指标：

- loss
- voltage_deviation
- constraint_violation

并新增：

- reactive_support_effort

## Why Add Reactive Support Effort

新能源 inverter 无功支撑不是免费变量。即使第一版不做经济调度，也必须记录无功支撑使用程度，避免 candidate 只靠过度使用 inverter Q 获得表面改善。

## Pass Criteria

candidate 必须：

- 改善 loss
- 改善 voltage_deviation
- 不新增 constraint violation
- reactive_support_effort 被明确记录且处于边界内

## Blind Spots

- 不评价调节次数。
- 不评价经济成本。
- 不评价时序稳定性。
