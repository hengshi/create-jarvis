# Pilot Registry — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> `_bootstrap/shadow-pilot/` 索引。只记录 pilot 基本信息、artifact pointer 和执行状态。不包含 participant/contact roster。

## Artifact Search Coverage

| 来源 | 实际命令/查询 | 查询边界 | 候选或零结果 | 停止理由 | 状态 |
|---|---|---|---|---|---|
| <source/repo> | <exact command or query> | <时间或提交边界> | <candidates or 无结果> | <why stopped> | scanned / eligible-found / needs-input |

## Pilot Index

| Pilot ID | Artifact Pointer | Mode | Workflow | Run/Evidence Pointer | Claim Scope | Outcome | Writeback Decision | Owner | Next Action |
|---|---|---|---|---|---|---|---|---|---|
| <pilot-id> | <pointer or redacted summary> | owner-provided / historical-shadow | <workflow> | `shadow-pilot-run.md`, `pilot-evidence.md` | <此 pilot 验证的 scope> | <outcome> | <none / task-local / repo-local / company-jarvis / source-skill / workflow-skill / upstream> | <owner> | <next action> |

## Status Definitions

| 状态 | 含义 |
|---|---|
| **ready** | START 信息足够运行 shadow pilot |
| **running** | pilot 执行中 |
| **blocked** | 缺 access、owner、artifact、source、repo 或安全审批 |
| **completed** | START → ROUTE/WORK → VERIFY → END 已记录 |
| **needs-input** | 缺 artifact，且所有授权来源无法选出可用候选 |

## Notes

- 详细证据在 `shadow-pilot-run.md` 和 `pilot-evidence.md`，不在此复制。
- Pilot 结束后及时更新状态。
- 发现 writeback need 时记录到 `_bootstrap/controlled-writeback-log.md`，Phase 13 汇总。
