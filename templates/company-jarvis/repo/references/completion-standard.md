---
title: 完成标准
description: 当前 workflow 的完成判定规则。
---

# 完成标准

## 完成的定义

当前 workflow 的**实质 scope**、**验收条件**、**必须执行的动作**、**验证**、**写入授权**全部闭合，且无未处理的阻断项时，任务标记为 completed。

不适用项直接标注不适用并说明原因，不因不适用而判定未完成。

## 阻断 / 重定向

阻断（blocked）或重定向（redirected）是诚实的闭合结论，不等于 completed。记录时应说明：

- 阻断或重定向原因
- 恢复路径或下一步路由

## 完成证据

- 用 `agent-engineering-quality-gate.md` 判断 material gate 是否仍有阻断条件。
- 用 `verify-evidence-matrix.md` 为当前 claim 选择验证；检查范围来自 workflow、source/repo contract 和风险。
- 用 `minimal-closure-card.md` 记录实际结果、证据、未解决项和下一步。
- 持久写入必须处于 `runtime-governance.md` 的授权边界；受影响 delivery surface 以 `capability-delivery-surfaces.md` 的客户事实为准。
