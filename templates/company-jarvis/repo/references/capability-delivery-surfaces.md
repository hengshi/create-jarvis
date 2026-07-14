---
title: 能力归属与交付面
description: 确定每个 capability 的 authority、交付面、验证面和文档 fallout。
---

# 能力归属与交付面

## 定义

- **Capability**：客户证据确认的产品能力、业务能力或运营能力。不是技术模块、代码包或 repo 边界。
- **Authority**：对 capability 的 contract 或决策拥有裁定权的角色、团队或治理机制。可以集中也可以分布，分别记录：
  - Contract / decision authority
  - Execution owners（可多个）
- **Delivery surface**：能力被消费或执行的真实入口，按客户证据中实际存在的形态记录。
- **Verification surface**：证明 delivery surface 满足其 contract 的验证入口。
- **Docs / operational fallout**：能力的 contract 或 acceptance 文档。仅在实际存在时记录。

## Capability Matrix

每个字段需带 evidence pointer 和状态。

| Capability | Contract authority | Execution owners | Delivery surfaces | Verification surfaces | Docs / operational fallout | 状态 |
|-----------|-------------------|------------------|------------------|---------------------|--------------------------|------|
| BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED | BOOTSTRAP_REQUIRED |

状态反映 evidence 是否足以支撑当前 contract；未解决项同时记录已查范围和恢复条件。

## First Execution / First Proof

First proof 的选择依据：

- 离原始 claim 最近的 evidence
- 能最快区分关键假设
- 有对应 authority 或 contract 能裁定结果

## Fallout

Fallout 仅覆盖 contract 或 acceptance 真正受影响的 surface。

- 记录受影响 surface、影响关系、验证入口和更新路径。
- 只有排除某个相邻 surface 会影响 closure 判断时，才记录其不受影响依据。

## Authority 未解决

Authority unresolved 且该 unresolved 影响当前执行 → `blocked`。记录恢复所需的 evidence 类型和来源。
