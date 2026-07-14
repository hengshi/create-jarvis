# Rollout Confirmation Checklist — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> Phase 10 完成、进入 Phase 11 前的交付确认清单。逐项检查 Phase 3–10 的产出是否满足进入 shadow pilot 的门槛。不需要每项签字——owner 确认只在事实/权限/策略确实需要时记录。

## Phase 3–5: Identity / Scope / Readiness

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| 3.1 | {{COMPANY_NAME}} 身份已获 {{COMPANY_OWNER}} 确认 | [ ] | | |
| 3.2 | {{PRODUCT_IDENTITY}} 已确认或标记 unresolved | [ ] | | |
| 3.3 | Source-detected identities 已登记，未混入 confirmed identity | [ ] | | |
| 3.4 | First workflow 已识别 | [ ] | | |
| 3.5 | Success signal 已定义 | [ ] | | |
| 3.6 | Included sources 已确认 | [ ] | | |
| 3.7 | Included repos 已确认 | [ ] | | |
| 3.8 | Out-of-scope 已显式记录 | [ ] | | |
| 3.9 | Target / runtime / method pointers 已配置 | [ ] | | |
| 3.10 | Writeback policy 已确认 | [ ] | | |

## Phase 6: Real Scan

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| 6.1 | 已执行真实 source 扫描（非占位 inventory） | [ ] | | |
| 6.2 | 已执行真实 repo 扫描 | [ ] | | |
| 6.3 | 每个 module 有实际 discovery 证据，非纯模板 | [ ] | | |
| 6.4 | 每个 source 有实际 access/query 证据，非纯模板 | [ ] | | |

## Phase 7: Topology + Customer Modules / Source Routes

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| 7.1 | Customer module overviews 已从 Phase 6 discovery 生成 | [ ] | | |
| 7.2 | Source routes 已从 Phase 6 discovery 生成 | [ ] | | |
| 7.3 | Module 边界与 source routes 对齐真实发现，未编造映射 | [ ] | | |

## Phase 8: Repo-local Truth

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| 8.1 | Repo-local skills/references 已生成，内容来自真实 repo 扫描 | [ ] | | |
| 8.2 | Repo-local truth 留在 repo-local 层，未复制到 company Jarvis | [ ] | | |
| 8.3 | 每个 pilot repo 的 entrypoint / test / precheck 已记录 | [ ] | | |

## Phase 9: Workflow / Source Packages

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| 9.1 | Workflow skills 已从 Phase 6–8 生成，覆盖 START→ROUTE→WORK→VERIFY→END | [ ] | | |
| 9.2 | Source skills 已从 Phase 6–7 生成，包含 access/query/redaction/freshness | [ ] | | |
| 9.3 | Company entry skill 可路由至正确的 module/workflow/source/repo-local skill | [ ] | | |

## Runtime Contracts

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| R.1 | Runtime owner 已明确（jarvis-box 或其他显式 runtime） | [ ] | | |
| R.2 | 未将 secret / token / PII 写入 artifact | [ ] | | |
| R.3 | Non-interactive missing inputs 记为 unresolved，未猜测 | [ ] | | |
| R.4 | `bootstrap-state.json` 与 `bootstrap-result.json` 位于 company root，路径和 phase 状态一致 | [ ] | | |
| R.5 | Canonical entry、runtime bridge files 和 17 个核心 references 均存在且链接可达 | [ ] | | |

## Links / Redaction / Acceptance

| # | 检查项 | 通过 | Owner 确认 | 备注 |
|---|---|---|---|---|
| L.1 | 所有 artifact 间的链接使用 company repo 相对路径 | [ ] | | |
| L.2 | 无 raw source dump、secret、未经授权材料或 hidden oracle 泄露 | [ ] | | |
| L.3 | Acceptance standard 可检查且与当前 scope 一致 | [ ] | | |

## Unresolved / Blockers

| 项目 | 类型 | 影响 Phase | Owner | 状态 |
|---|---|---|---|---|
| <description> | unresolved / blocker | <phase> | <owner> | open |

## Next Action

- <next action>
