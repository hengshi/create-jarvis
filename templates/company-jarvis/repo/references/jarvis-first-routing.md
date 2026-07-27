---
id: reference.jarvis-first-routing-v1
status: binding
version: 1.0
---

# Jarvis 首跳路由

任务首次进入 Jarvis、所有权不明或可能涉及多 repo fallout 时读取。路由目标是找到当前证据下最合理的第一工作面和第一项 proof，而非在 triage 阶段就确定全部归属。

---

## 身份

- **公司身份**：{{COMPANY_NAME}}（slug: {{COMPANY_SLUG}}）
- **客户确认的产品身份**：{{PRODUCT_IDENTITY}}
- **Source 检测到的身份**：UNRESOLVED — 根据 source/repo/docs 证据填写，标记 `needs-owner-confirmation`；不得覆盖公司身份和客户确认的产品身份
- **身份协调状态**：UNRESOLVED — `confirmed` / `needs-owner-confirmation` / `conflict` / `unresolved`

---

## 优先级

按企业闭环 skill 优先，不按仓库优先。

### 已确认工作流范围

{{WORKFLOW_INDEX}}

### 初始任务路由表

| 触发证据 | Candidate module / source | First proof | Repo-local handoff（如有） | 验证 | 当前状态 |
|---------|---------------------------|-------------|--------------------------|------|--------|
| UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

每条已填实规则必须能回指触发证据，并包含 module/source、first proof、适用的 repo-local handoff、验证和 unresolved/pending 状态。workflow 未激活时仍可完成这条初始路由。

---

## Repo 角色

### 已确认仓库范围

{{REPO_INDEX}}

### Repo 角色表

| Repo | 证据支撑的角色 | Repo-local entry | First proof | 升级 / 返回条件 |
|------|--------------|-----------------|-------------|----------------|
| UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

repo 名来自实际 checkout identity。repo-local entry 必须是当前可解析路径；尚未生成时明确写 `pending Repository learning`。角色与 first proof 均能回指 source/repo evidence。

---

## 路由算法

1. 从 artifact / source 提取事实集合
2. 匹配已确认且 `active` 的 workflow —— 命中则进入对应 workflow skill
3. 没有 active workflow 时进入 construction/onboarding mode，只做 semantic routing，不声称已形成 delivery closure
4. 从客户业务/产品域确定 module 边界
5. 选择最接近原始 claim、足以区分关键路由假设且在授权范围内可执行的 first proof
6. 仅在证据指向特定 repo 时路由到当前真实 repo-local handoff
7. module/source/first-proof route 不存在或证据冲突 → `blocked`，记录需要解除阻塞的 evidence 类型

---

## Second Hop

仅当以下任一条件成立时触发 second hop：

- First proof 证据不足以闭合当前路由
- First proof 结果与 workflow contract 矛盾
- 证据已证明跨边界（跨 module / 跨 repo / 跨 source）

新发现的路由规则只有在证据足以说明可复用边界和验证方式时，才按 writeback governance 判断是否写回。

---

## 约束

- Source-detected identity 不等于公司身份。路由到公司特有 workflow 前必须完成身份协调。
- Repo-local execution truth 留在 repo-local skills。没有跨 repo 适用性证据时，不把 repo 级路由规则提升到公司 Jarvis。
- 所有路由行和 repo 角色行必须来自实际 evidence。
