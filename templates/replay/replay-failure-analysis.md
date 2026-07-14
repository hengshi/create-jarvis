# Replay Failure Analysis

## Execution Gate

- **Case ID**: `<case-id>`
- **Replay run ID**: `<run-id>`
- **Execution gate**: `executed` / `replay-not-executed` / `invalid`
- **Case readiness pointer**: `<history-replay-case.md#case-readiness-gate>`
- **Case validity**: `valid` / `invalid`
- **Leak discovered after execution**: `yes` / `no`
- **Agent invocation pointer**: `<exact command，脱敏>`
- **Agent exit code**: `<code>`
- **First valid agent action evidence**: `<pointer or none>`

> CLI/权限/container 在首个有效 agent action 前失败 = `replay-not-executed`。case invalid 或执行后发现泄漏同样只能 `not-evaluated`，不得得出 `no_skill_gap` 或 skill gap 结论。

## Replay Trace / Output

| Step | Replay Action | Evidence Used | Comment |
|---|---|---|---|
| `<step>` | `<action>` | `<evidence>` | |

## Final Output Evidence

> 记录 replay 最终产出证据。适用于代码（final diff / commit）和非代码 episode（oracle artifact / final output / 等价 outcome evidence pointer）。

- **Evidence type**: `<git-diff / oracle-artifact / final-output / log-excerpt / api-response / 其他>`
- **Exact command or artifact pointer**: `<exact diff 命令，或等价 artifact 路径/指针，脱敏>`
- **获取方式**: `<如何获取 replay 最终产出证据>`
- **确认已完整读取**: `yes` / `no`

## Historical Outcome Evidence

- **Evidence type**: `<final-diff / final-artifact / review-decision / api-response / 其他>`
- **Exact command or artifact pointer**: `<读取完整历史 outcome 的 exact command/pointer，脱敏>`
- **确认已完整读取**: `yes` / `no`
- **Documented root cause**: `<历史材料明确记录的 root cause；未记录写 unknown>`
- **Historical verification status**: `verified` / `partial` / `unknown`
- **Complete changed surfaces / outcome artifacts**: `<完整列表或 pointer>`

## Oracle Comparison

> Oracle comparison 必须由外层 bootstrap agent 读取完整 hidden oracle 后执行。replay agent 不自评 oracle。

**读取完整 hidden oracle 确认**: `yes` / `no`

### Changed-surface purpose（每个 oracle changed surface 必须逐条解释）

| Changed Surface (file) | Oracle 中的用途 | Replay 是否命中 | 说明 |
|---|---|---|---|
| `<path>` | bug-fix / test / refactor / config / doc / … | yes / no / partial | <如果 replay 未命中，为什么> |

> 不得将未读取实际 diff 内容的 changed surface 猜测为 cosmetic / supporting / 不重要。非代码 episode 支持等价 outcome artifact——记录实际 outcome artifact pointer 和比较方式。

### Dimension Comparison

| Dimension | Replay Result | Oracle Expectation | Finding |
|---|---|---|---|
| Route / owner | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |
| Evidence boundary | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |
| Repo-local boundary | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |
| Behavior / outcome | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |
| Verification | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |
| Closure / writeback | `<result>` | `<expectation>` | matched / partial / mismatched / blocked |

> 允许等价或更优解，也允许指出历史 outcome 局限。不要求逐字/逐 patch 相同。

### Alternative Solution Verification

- **Replay 与历史实现不同**: `yes` / `no`
- **Independent behavioral verification**: `verified` / `unproven` / `not-applicable`
- **Evidence**: `<独立行为验证 pointer；没有则写 none>`

> replay 方案与历史实现不同时，只有独立行为验证为 `verified` 才能称为等价或更优；否则结论必须是 `unproven`。

## Primary Classification

> 只有 `Execution gate: executed` 且存在非空 replay trace/result + 完成 oracle comparison 后才做以下分类。

### Attribution（选择所有适用项，再选一个 primary）

- [ ] `skill_gap` — 现有 skills 存在可复用、可验证的缺口
- [ ] `instance_fact_gap` — 实例事实缺失（缺 source/repo 信息）
- [ ] `source_access_environment` — source/access/environment 问题
- [ ] `execution_deviation` — 执行偏差（agent 行为偏差而非 skill 问题）
- [ ] `case_construction_leak` — case 构造/泄漏问题
- [ ] `oracle_limitation` — oracle 本身局限

- **Primary classification**: `<one>`
- **Why**: `<reason>`

## no_skill_gap Check

> `no_skill_gap` 必须由 valid + executed case 的实际 skill trace、完整 oracle comparison（含完整 final diff 或等价 outcome evidence 读取和每条 changed surface 的用途说明）以及充分 outcome verification 支持。非代码 episode 不得宣称必须有 diff，但必须提供等价的 outcome evidence。`replay-not-executed` / `invalid` / outcome verification 不足 → `not-evaluated`。

- **Existing guidance sufficient?** `yes` / `no` / `unknown`
- **Failure caused by missing evidence / source data / runtime behavior / code?** `yes` / `no` / `unknown`
- **One-off exception?** `yes` / `no` / `unknown`
- **Skill change justified?** `yes` / `no` / `defer`
- **Outcome verification sufficient for skill judgment?** `yes` / `no`
- **no_skill_gap**: `yes` / `no` / `not-evaluated`

> 只有 `executed` + valid + oracle compared 后 `no_skill_gap: yes` 可判。未执行/invalid 只能 `not-evaluated`。

## Candidate Fact Correction / Method Gap / Primary Home

给 Phase 13 的候选：

| Home | Candidate Update | Type | Pros | Risks |
|---|---|---|---|---|
| `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream` / `none` | `<update>` | stable-fact / method-gap | | |
