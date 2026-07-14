---
title: 模块边界路由
description: 确定 artifact / claim 归属的 module 边界和路由决策。
---

# 模块边界路由

## 核心规则

将 artifact 或 claim 归属到**当前证据下最合理的 primary module**，不要求在 triage 阶段已知 root cause。Module 来自客户业务/产品域，不是技术层。

## 路由依据

使用以下信息比较 claim 与 module contract：

- Module overview（`modules/<module>/overview.md`，如存在）
- Evidence inventory（当前 workflow 已收集的证据）
- Workflow / source / repo 关系（已确认的跨模块路由记录）

允许多个候选 module 保持 `unresolved`，各自记录持有证据和区分它们的下一项 proof。

## 输出

每个路由决策记录：

- **Selected module**：当前证据下最合理的 primary module
- **Candidate modules**：其他候选 module，各自附证据指针
- **First proof**：下一步需验证的关键假设
- **False-owner / alternative**：已排除的 module 及排除依据
- **Unresolved**：暂无法裁定的候选及 return condition（满足什么条件时重新裁定）
- **Evidence pointers**：支撑以上判断的证据位置

判断确定性由 evidence provenance、已验证关系和 unresolved 项表达。路由记录可随新证据更新；候选范围与层级由客户 modules 和当前 claim 决定。
