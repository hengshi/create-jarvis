# Pilot Evidence — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> 汇总本 pilot 的 claims 与证据。一个 pilot 一份 evidence。不要求每次更新 writeback-governance；只记录 decision，Phase 13 汇总。

## Evidence Summary

- **Pilot ID**: `<pilot-id>`
- **Artifact**: `<pointer or redacted summary>`
- **Artifact mode**: `owner-provided` / `historical-shadow`
- **Outcome**: `useful` / `partial` / `blocked` / `missed`
- **Primary owner**: `<owner or unresolved>`

## Route / Handoff

| 维度 | 实际 | 证据 |
|---|---|---|
| Entrypoint 读取 | <entrypoint skill / reference 读取记录> | <pointer> |
| Module 选择 | <选择的 module> | <pointer> |
| Workflow 选择 | <选择的 workflow> | <pointer> |
| Source route | <选择的 source route> | <pointer> |
| Repo-local skill | <handoff 到的 repo-local skill> | <pointer> |
| 未选候选 | <明显候选及排除理由> | |

## Work Output

| 维度 | 实际 | 证据 |
|---|---|---|
| Source 查证 | <查证了哪些 source，结论> | <pointer> |
| Repo 操作 | <在受控副本中做了什么> | <pointer> |
| 产出 | <交付了什么> | <pointer> |

## Verification

| 验证项 | 结果 | 证据 |
|---|---|---|
| <check> | `executed-pass` / `executed-fail` / `observed-not-executed` / `blocked` | <pointer or summary> |

> 只记录实际执行并捕获输出的验证。`executed-pass` / `executed-fail` 来自真实运行命令后的输出。未执行 = `observed-not-executed`。不得从文件存在声称 pass。

## Scope Limitation

- <本次 pilot 的范围限制，如 dry-run / route-only / 未运行 product-level verification>
- <若为 historical-shadow dry-run：明确只能证明 routing/readability>

## Failure Attribution

- **Primary classification**: `routing_failure` / `truth_failure` / `boundary_failure` / `writeback_failure` / `verification_failure` / `no_skill_gap` / `none`
- **Why**: <原因>

## Learning Type — Stable Fact vs Method Gap

- **稳定事实修正**: <事实缺失或错误的修正，如 source route、repo path、owner 映射>
- **方法/skill 缺口**: <skill guidance 缺口——必须先完成 no_skill_gap 判断>

## no_skill_gap

- **现有 guidance 是否已足够？** `yes` / `no` / `unknown`
- **失败来自缺证据/权限/环境/一次性情况？** `yes` / `no` / `unknown`
- **是否需要 skill 变更？** `yes` / `no` / `defer`

## Candidate Primary Home

- **Primary home**: `task-local` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream` / `no writeback`
- **Mirror**（仅当另一层必须发现/执行该规则时）: `none` or `<target + reason>`

## Next Action

- <next action>
