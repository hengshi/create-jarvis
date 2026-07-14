# Skill Update Decision

> **Phase 12 只提决定，Phase 13 才执行写回和复跑。** 未执行/invalid → Decision: `defer`，Status: `deferred`，不能写 `no_skill_gap` 或 `closed`。

## Decision Summary

- **Case ID**: `<case-id>`
- **Execution gate**: `executed` / `replay-not-executed` / `invalid`
- **Case validity**: `valid` / `invalid`
- **Outcome verification sufficient for skill judgment**: `yes` / `no`
- **Primary failure classification**: `<skill_gap / instance_fact_gap / source_access_environment / execution_deviation / case_construction_leak / oracle_limitation / not-evaluated>`
- **Learning type**: `stable-fact` / `method-gap` / `not-evaluated`
- **no_skill_gap**: `yes` / `no` / `not-evaluated`
- **Primary home**: `task-local` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream` / `no-writeback`
- **Mirror**: `none` 或 `<target + reason>`
- **Conflict**: `none` 或 `writeback-conflict`
- **Owner**: `<owner or unresolved>`
- **Decision**: `no_skill_gap` / `task-local` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream` / `defer`
- **Status**: `proposed` / `approved` / `patched` / `verified` / `deferred` / `closed`

## Rationale

> 说明 replay evidence 为什么支持这个决定。未执行、invalid、执行后发现泄漏或 outcome verification 不足 → Decision: `defer`，`no_skill_gap: not-evaluated`。

`<rationale>`

## Proposed Minimal Update

| Target File / Skill | Change | Why Reusable & Verifiable | Excluded (case-specific facts) |
|---|---|---|---|
| `<target>` | `<minimal change>` | `<why this is a repeatable method gap, not a one-off>` | `<private fact or one-off detail excluded from the update>` |

- **Evidence**: `<pilot-id / replay-case-id / run-id>`

## Phase 13 Approval

- **Owner approval**: `approved` / `needs-owner-confirmation` / `blocked`
- **Approval evidence**: `<pointer>`

## Phase 13 Writeback Evidence

- **Writeback ID**: `<wb-id>`（对应 `controlled-writeback-log.md`）
- **Patch evidence**: `<pointer or summary>`
- **Target**: `<path or skill>`

## Phase 13 Rerun

用 Phase 12 同一 visible START 隔离复跑，证明该回归改善。

- **Rerun ID**: `<run-id>`
- **Result**: `improved` / `no-improvement` / `partial` / `blocked`
- **Evidence**: `<pointer>`
- **同一个 case 不单独证明泛化**

## Upstream Safety

- [ ] Upstream promotion 前已移除 private names、hosts、issue IDs、commit hashes、raw comments 和 paths
- [ ] Update 是 method-level，不是 fact-level
- [ ] Owning layer 明确
- [ ] 已记录 repeated value 或 high blast radius
