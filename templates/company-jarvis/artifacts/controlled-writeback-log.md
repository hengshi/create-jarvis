# Controlled Writeback Log — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> 记录稳定事实修正和方法/skill 缺口两类写回。每条学习只有一个 primary home。主归属对齐 `references/writeback-governance.md`。Phase 13 执行写回和复跑。

## Log

| 字段 | 说明 |
|---|---|
| **ID** | `<wb-id>` |
| **Source Evidence** | `<pilot-id / replay-case-id / evidence pointer>` |
| **Source Gate** | `eligible` / `invalid` / `replay-not-executed` |
| **Evidence Contract** | `complete` / `incomplete` |
| **Type** | `stable-fact` / `method-gap` |
| **no_skill_gap** | 仅 method-gap 类型填写：`yes` / `no` / `not-evaluated`。stable-fact 填 `n/a` |
| **Primary Home** | `task-local` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream` / `no-writeback` |
| **Target** | `<目标文件或 skill 路径>` |
| **Mirror** | `none` 或 `<target + reason>`——仅当另一层必须发现/执行该规则时 |
| **Conflict** | `none` 或 `writeback-conflict`（附双方 evidence 和 authority） |
| **Approval** | `approved` / `needs-owner-confirmation` / `blocked` |
| **Patch Evidence** | `<写回 patch 的 pointer or summary>` |
| **Verification** | `<replay / precheck / dry-run / owner-review / 未验证>` |
| **Replay Rerun** | `<case-id + run-id>，仅 method-gap 写回后复跑时填写` |
| **Status** | `proposed` / `patched` / `verified` / `deferred` / `no_skill_gap` / `blocked` |
| **Next Action** | `<next action>` |

| ID | Source Evidence | Source Gate | Evidence Contract | Type | no_skill_gap | Primary Home | Target | Mirror | Conflict | Approval | Patch Evidence | Verification | Replay Rerun | Status | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <wb-id> | <pointer> | eligible | complete | stable-fact | n/a | | | | | | | | | | |
| <wb-id> | <pointer> | eligible / invalid / replay-not-executed | complete / incomplete | method-gap | | | | | | | | | | | |

## Status Definitions

| Status | Meaning |
|---|---|
| **proposed** | 写回已记录，尚未审核或批准 |
| **patched** | 变更已写入目标文件或 skill |
| **verified** | 已通过复跑或等价验证 |
| **deferred** | 原则同意但推迟实现 |
| **no_skill_gap** | 现有 guidance 已足够，无需写回 |
| **blocked** | 被 access、ownership 或 policy 阻塞 |

## Safety Checks

- [ ] 未包含 raw source dump
- [ ] 未包含 secret / PII
- [ ] 未泄露 hidden oracle
- [ ] Repo-local execution truth 未写入 company Jarvis
- [ ] Upstream 更新已脱敏、公司中立
- [ ] Primary home 规则正确——每条学习只有一个 primary home
- [ ] Mirror writeback（如有）有正当理由
- [ ] 学习是可复用的，非一次性事实伪装
- [ ] 冲突未覆盖，双方 evidence 和 authority 已保留
