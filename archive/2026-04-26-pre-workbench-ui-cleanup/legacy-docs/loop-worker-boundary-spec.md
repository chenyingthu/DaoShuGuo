# Loop Worker Boundary Spec

## 1. 文档目的

本规范用于防止项目在“技能-成效-认知”闭环中发生 `controller overreach`。

所谓 `controller overreach`，是指：

> loop controller 自己直接下场，代替 skill worker、effectiveness worker 或 cognition worker 完成实质判断和生成工作。

这是本项目必须重点防止的一类自欺风险。

## 2. 四类角色

本项目中的闭环角色固定为四类：

1. `skill worker`
2. `effectiveness worker`
3. `cognition worker`
4. `loop controller`

## 3. 允许的职责

### 3.1 skill worker

允许：

- 基于上一轮 diagnosis 生成新的 skill 变体
- 修改 skill 文件、参数或搜索结构
- 产出 `skill_change_request` / `skill_change_result`

### 3.2 effectiveness worker

允许：

- 运行 evaluator
- 比较 baseline 与 candidate
- 产出 `effectiveness_assessment`

### 3.3 cognition worker

允许：

- 读取 skill change 与 evaluator 结果
- 判断是 `skill-use`、`skill-structure`、`task-design` 还是 `evaluator-design` 问题
- 产出 `cognition_diagnosis`

### 3.4 loop controller

允许：

- 调度 worker
- 绑定输入输出
- 写状态机
- 汇总引用
- 形成 `loop_routing_decision`

不允许：

- 直接写 skill 变体内容
- 直接给出 effectiveness 结论
- 直接给出 cognition diagnosis

## 4. 最小对象要求

一个合格的闭环轮次至少应有以下对象：

1. `skill_change_request`
2. `skill_change_result`
3. `effectiveness_assessment`
4. `cognition_diagnosis`
5. `loop_routing_decision`

若缺任一项，则该轮不能声称为完整自主循环。

## 5. 典型违规模式

以下情况属于 `controller overreach`：

1. controller 直接在脚本里写死“下一轮把参数从 0.1 改到 0.2”
2. controller 直接在脚本里判定“这一轮是 cognition deepened”
3. controller 不经过 cognition worker，直接把失败归因为 `skill-structure`
4. controller 没有引用 worker 产物，只凭内置 if/else 决定下一轮方向

## 6. 当前项目中的应用

在 task003/task004 的早期 Pi loop 中，曾经出现过：

- 用脚本写死下一轮策略
- 用脚本直接解释每轮结果

这些工作可作为：

- `framework debugging experiments`

但不能再被称为：

- 自主 skill-cognition-effectiveness loop

## 7. 后续 verifier 要求

后续应提供 verifier 检查：

1. 是否存在所需 worker 对象
2. controller 的 routing decision 是否引用这些对象
3. 是否存在 controller 直接生成 diagnosis / effectiveness / skill change 的痕迹

一旦发现，应标记：

- `controller_overreach`
- `framework_cheating`
