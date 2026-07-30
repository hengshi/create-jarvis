---
name: {{SKILL_NAME}}
description: "{{JARVIS_NAME}} Feature-delivery workflow starter。只有内容已由真实客户事实替换并具有可复核行为证据时使用。"
version: "2.0.0"
---

# {{JARVIS_NAME}} 功能交付

## Applicability

**Status: `unverified`**

本文件中的通用假设不构成客户流程。用真实需求入口、决策角色、repo-local skills、
branch/review/test/release policy 与交付凭证替换后，至少用一个真实或等价 case 验证完整闭环，
记录 evidence pointer，再改为 `verified`。`unverified` 时不得执行。

以下内容是供客户校准的初始假设：从需求输入到交付闭环，定义本次动态闭环，判断就绪，路由执行，逐项验证，记录收尾。

## 触发条件

以下输入触发本闭环：

- issue-post-check 结果为 `ready-for-feature-delivery` 的 handoff；
- 已获得授权的 feature request、spec、product decision。

以下输入路由到对应闭环，不由本 skill 处理：

- 纯 bug 修复 → bugfix 闭环；
- 已建 issue 仍需判断真实类型和路由 → `{{JARVIS_SLUG}}-workflow-issue-post-check`；
- 已可直接按 repo-local 规则执行的小改动 → 对应 repo-local skill。

## 闭环结构

每次功能交付按 START → WORK → VERIFY → END 执行。这是一个动态闭环：后续证据改变范围、surface、版本或 fallout 时，更新闭环定义后继续。

---

## START — 准备与闭环定义

### 预检

先识别 construction、普通授权 checkout 或 managed production。上下文缺失、冲突或需要 runtime
诊断时才读 `{{JARVIS_SLUG}}-jarvis/references/runtime-governance-quick.md`；quick 触发升级条件时
再读完整版。不要在 construction 中要求 jarvis-box，也不要把静态 Jarvis repo 当作运行时状态。

随后读取 `{{JARVIS_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`，将该文件中的 scope gate、verification gate、output gate 作为后续各阶段的停止条件。

### 读取输入

从原始 artifact 中提取以下信息并区分状态：

- **用户目标**：真实业务需求和目标用户；
- **方案建议**：输入中提出的解决方案；
- **已确认范围**：已获授权的 scope；
- **未知项**：尚待澄清的部分。

同时读取已有的 decision record、产品契约和授权 source。

### 确定决策权限与策略

识别本轮交付的决策 authority 和客户 policy。task-time 等执行参数从本阶段识别出的 source route 和客户 policy 中获取。

### 定义本次动态闭环

闭环定义至少包含：

- 成功条件与 non-scope；
- capability owner；
- delivery surfaces 和 verification surfaces；
- 可能的 repo / source fallout；
- 需要的批准和 END artifact 形态。

闭环定义在 START 阶段形成，后续证据改变范围时更新。

---

## WORK — 判断与执行

### 就绪判断

先判断输入是否 implementation-ready。以下任一缺失时，在当前 workflow 中向 owner 收敛，或标记为 `needs-input` / `blocked`，不直接进入编码：

- 用户目标；
- scope 和 non-scope；
- acceptance 条件；
- 关键 contract；
- owner 决策。

### 路由

就绪后，按 `{{JARVIS_SLUG}}-jarvis/references/jarvis-first-routing.md` 和 `{{JARVIS_SLUG}}-jarvis/references/capability-delivery-surfaces.md` 确定 execution source。路由确实落到代码仓库时，再确定 target repo 并加载其 canonical repo-local skill。

路由信息不明确时，读取 `{{JARVIS_SLUG}}-jarvis/references/next-hop-compression.md`。

### 执行

进入代码或耐久文档修改前加载 `ponytail`。计划并实施满足已确认 scope 的最小正确改动。以下决策全部来自 source route、repo-local skill 或客户 policy：

- 命令、分支命名、工具选择；
- 目录结构；
- review policy；
- 提交和 MR 规则。

docs、test、release、operations fallout 仅在证据表明需要时纳入。同一能力可跨多个 delivery surface，但不自行发明 repo 数量、版本线数量或 MR 数量。

---

## VERIFY — 逐项验证

### 验证范围

逐条对照已确认的 acceptance 条件和原始用户目标进行验证。

### 验证方式

按每个 execution surface 的 contract 和风险，执行实际检查。检查结果分为三类：

- **executed-pass**：已执行且通过；
- **executed-fail**：已执行但未通过；
- **observed-not-executed**：观察到但未实际执行。

用户可见或运行时 proof 仅在当前能力需要时制作。机器/CI PASS、clean apply、静态解释不能替代 acceptance evidence。

### 多 surface / 多版本

多分支或多版本验证仅在 scope 实际需要时进行。每个 target 按自己的 contract 独立验证，source-branch evidence 不替代 target-branch evidence。

---

## END — 记录与收尾

### 记录

记录以下内容：

- 最终 scope；
- 交付 artifact；
- 验证 evidence（含 executed-pass / executed-fail / observed-not-executed）；
- 未解决风险；
- 批准和写回状态；
- next action。

### 发布动作

VCS change、MR 创建、reviewer 指定、CI 触发、label、publish 等动作仅按客户/repo/project policy 与当前授权执行。

### 完成声明

未实际执行的动作不声称完成。

### 写回

- 稳定且跨 repo / source / workflow 可复用的新知识，按 `{{JARVIS_SLUG}}-jarvis/references/writeback-governance.md` 写回 Jarvis。
- repo execution truth 留在 repo-local skill 中。
- 普通任务不制造 `no_skill_gap`。

### 闭环

闭环完成前读取 `{{JARVIS_SLUG}}-jarvis/references/completion-standard.md` 和 `{{JARVIS_SLUG}}-jarvis/references/minimal-closure-card.md`，确认所有必要 surface 和 evidence 已覆盖。

---

## 可依赖的参考文件

本 skill 在运行时可引用以下 jarvis refs，不应超出此范围：

| 参考文件 | 使用时机 |
|---|---|
| `{{JARVIS_SLUG}}-jarvis/references/runtime-governance-quick.md` | START 预检 |
| `{{JARVIS_SLUG}}-jarvis/references/runtime-governance.md` | START 预检升级时 |
| `{{JARVIS_SLUG}}-jarvis/references/agent-engineering-quality-gate.md` | START 预检后，scope/verification/output gate |
| `{{JARVIS_SLUG}}-jarvis/references/jarvis-first-routing.md` | WORK 路由阶段 |
| `{{JARVIS_SLUG}}-jarvis/references/capability-delivery-surfaces.md` | WORK 路由与 surface 选择 |
| `{{JARVIS_SLUG}}-jarvis/references/next-hop-compression.md` | WORK 路由信息不明确时 |
| `{{JARVIS_SLUG}}-jarvis/references/verify-evidence-matrix.md` | VERIFY 阶段定义验证证据 |
| `{{JARVIS_SLUG}}-jarvis/references/completion-standard.md` | END 闭环前 |
| `{{JARVIS_SLUG}}-jarvis/references/minimal-closure-card.md` | END 闭环前 |
| `{{JARVIS_SLUG}}-jarvis/references/writeback-governance.md` | END 写回判断 |

## 交接规则

- 需求是否属于 feature 尚不明确时，交给 `{{JARVIS_SLUG}}-workflow-issue-post-check`。
- repo 执行交接给对应 repo 的 canonical repo-local skill。
- 进入实现前加载 `ponytail`。
