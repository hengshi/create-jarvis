# Skill Update Decision

> 先在 calibration snapshot 形成 candidate 并完成 same-case rerun，再把 verified candidate 应用到 authoritative repo-local home。未执行/invalid → Decision: `defer`，Status: `deferred`，不能写 `no_skill_gap` 或 `closed`。

## Decision Summary

- **Case ID**: `<case-id>`
- **Execution gate**: `executed` / `replay-not-executed` / `invalid`
- **Case validity**: `valid` / `invalid`
- **Outcome verification sufficient for skill judgment**: `yes` / `no`
- **Primary failure classification**: `<skill_gap / instance_fact_gap / source_access_environment / execution_deviation / case_construction_leak / oracle_limitation / not-evaluated>`
- **Learning type**: `stable-fact` / `method-gap` / `not-evaluated`
- **no_skill_gap**: `yes` / `no` / `not-evaluated`
- **Primary home**: `task-local` / `repo-local` / `upstream-method` / `no-writeback`
- **Mirror**: `none` 或 `<target + reason>`
- **Conflict**: `none` 或 `writeback-conflict`
- **Owner**: `<owner or unresolved>`
- **Decision**: `no_skill_gap` / `task-local` / `repo-local` / `upstream-method` / `defer`
- **Status**: `proposed` / `approved` / `patched` / `verified` / `deferred` / `closed`

## Rationale

> 说明 replay evidence 为什么支持这个决定。未执行、invalid、执行后发现泄漏或 outcome verification 不足 → Decision: `defer`，`no_skill_gap: not-evaluated`。

`<rationale>`

## Proposed Minimal Update

| Target File / Skill | Change | Why Reusable & Verifiable | Excluded (case-specific facts) |
|---|---|---|---|
| `<target>` | `<minimal change>` | `<why this is a repeatable method gap, not a one-off>` | `<private fact or one-off detail excluded from the update>` |

- **Evidence**: `<pilot-id / replay-case-id / run-id>`

## Candidate Update

- **Calibration snapshot**: `<writable snapshot pointer>`
- **Calibration skill ref before**: `<snapshot ref/digest>`
- **Candidate type**: `method/skill` / `stable-fact` / `none`
- **skill-creator invocation / trace**: `<pointer / not-applicable-stable-fact / not-applicable-no-update>`
- **Candidate patch**: `<diff pointer>`
- **Candidate primary home**: `<actual SKILL.md / focused reference / validation script / fact owner>`
- **Stable-fact authority and verification**: `<current authoritative source pointer + check / not-applicable>`
- **Case-specific facts excluded**: `<what was intentionally not written>`

## Same-Case Rerun

保持同一 visible START、cutoff、allowed sources 和 hidden oracle，只替换 skill snapshot。

- **Rerun ID**: `<run-id>`
- **Candidate skill refs**: `<refs>`
- **Result**: `improved` / `no-improvement` / `partial` / `blocked` / `not-required-no-skill-gap`
- **Regression check**: `<previously correct dimensions preserved?>`
- **Evidence**: `<pointer>`
- **Candidate verification**: `verified` / `rejected` / `not-applicable`
- **Promoted to cumulative baseline**: `yes` / `no` / `not-applicable`
- **Calibration skill ref after**: `<new cumulative ref, or unchanged ref for no-update>`
- **Ordered candidate set after promotion**: `<ordered decision/candidate ids>`

同一个 case 证明 candidate 修复了该回归，不单独证明跨 episode 泛化。

## Writeback Approval

- **Owner approval**: `approved` / `needs-owner-confirmation` / `blocked`
- **Approval evidence**: `<pointer>`

## Writeback Evidence

- **Writeback ID**: `<wb-id>`（对应 `controlled-writeback-log.md`）
- **Patch evidence**: `<pointer or summary>`
- **Target**: `<path or skill>`
- **Ordered candidate position**: `<n/total>`
- **Final authoritative ref matches cumulative calibration ref**: `yes` / `no` / `blocked`

## Delivery Revalidation

ordered candidate set 全部应用后，用最终累计 authoritative snapshot 对同一 visible START 做交付复验，确认应用过程或后续 candidate 没有改变已验证行为。

- **Rerun ID**: `<run-id>`
- **Result**: `preserved` / `regressed` / `partial` / `blocked`
- **Evidence**: `<pointer>`
- **同一个 case 不单独证明泛化**

## Upstream Safety

- [ ] Upstream promotion 前已移除 private names、hosts、issue IDs、commit hashes、raw comments 和 paths
- [ ] Update 是 method-level，不是 fact-level
- [ ] Owning layer 明确
- [ ] 已记录 repeated value 或 high blast radius
