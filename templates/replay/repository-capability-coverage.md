# Repository Capability Coverage

> 本 ledger 与 commit/code-read coverage 分开维护。commit 被读取不代表其中仍有效的任务知识已经获得 skill/reference/no-skill disposition。长任务每完成一个 history batch 就增量更新，最终在 fixed revision 收口。

## Repository Identity

- **Repository**: `<name / canonical remote>`
- **Fixed revision**: `<exact commit>`
- **Requested history range**: `<all / dates / refs>`
- **Code-read coverage pointer**: `<ledger/evidence>`
- **Repository model pointer**: `<model/version>`
- **Existing repo-local skills ref**: `<commit/path or none>`
- **Last reconciled at**: `<timestamp + ref>`

## Current Surface Inventory

每一类都必须写 `present`、`not-present` 或 `not-authorized`，并给出实际路径/命令/搜索证据。

| Surface category | Status | Current entrypoints / authority | Evidence |
|---|---|---|---|
| build / dependency / toolchain | `<status>` | `<paths/commands>` | `<pointer>` |
| code generation / schema / ABI | `<status>` | `<paths/commands>` | `<pointer>` |
| format / lint / test / quality | `<status>` | `<paths/commands>` | `<pointer>` |
| package / release / deployment | `<status>` | `<paths/commands>` | `<pointer>` |
| public API / runtime entrypoints | `<status>` | `<paths/symbols>` | `<pointer>` |
| domain state machines / data flows | `<status>` | `<paths/symbols>` | `<pointer>` |
| resource / provider / plugin lifecycles | `<status>` | `<paths/symbols>` | `<pointer>` |
| config / persistence / migration / variants | `<status>` | `<paths/symbols>` | `<pointer>` |
| concurrency / retry / cancellation / shutdown | `<status>` | `<paths/symbols>` | `<pointer>` |
| security / identity / sensitive data | `<status>` | `<paths/symbols>` | `<pointer>` |
| observability / logs / metrics / diagnostics | `<status>` | `<paths/symbols>` | `<pointer>` |
| compatibility / cross-repo contracts | `<status>` | `<paths/symbols>` | `<pointer>` |

## Task-Family Ledger

The delivered machine ledger uses schema version 2. Every `present` surface maps to explicit capability IDs. Every capability records `task_family`, `trigger_examples`, `authority`, `entrypoints`, `state_or_resource_model`, `proof`, `route_eval_ids`, `merge_split_rationale` and `current_state`. A category-level path or generic router row cannot substitute for these fields.

Validation levels:

- `L0`: discovered only;
- `L1`: current-state authority, paths, workflow and proof verified;
- `L2`: historical outcome plus isolated same-case replay verified;
- `L3`: adjacent/negative route or forward behavior also verified.

Topology dispositions:

- `router`
- `capability-skill`
- `focused-loop`
- `cross-cutting-skill`
- `reference`
- `script-gate`
- `no-skill`
- `candidate`

| ID / verb-led task family | Trigger examples | Owner / authority | Current entrypoints | Historical evidence | State/data/resource and failure model | Validation level + evidence | Topology disposition / primary home | Merge/split/no-skill rationale | Current-ref status | Executed representative route eval |
|---|---|---|---|---|---|---|---|---|---|---|
| `<id>` | `<user/task/CI signals>` | `<owner>` | `<paths/symbols/commands/tests>` | `<patch/episode pointers>` | `<loop/risk summary>` | `<L0-L3 + pointer>` | `<type + path>` | `<reason>` | `valid / stale / blocked` | `<eval ID + executed result>` |

## Route Matrix

| Representative request / signal | Primary skill | Conditional co-load | Must not route to | Proof |
|---|---|---|---|---|
| `<request>` | `<skill>` | `<reference/skill or none>` | `<adjacent skills>` | `<route/behavior evidence>` |

## Coverage Closure Review

- **Major current task families with disposition**: `<count>/<count>`
- **High-impact surfaces left at L0/candidate**: `<list + reason>`
- **Current public/build/release/security surfaces represented only by one router line**: `<none or explain>`
- **Potential under-generation found and resolved**: `<details>`
- **Potential over-generation / trigger overlap found and resolved**: `<details>`
- **Retired historical patterns removed or narrowed**: `<details>`
- **All delivered paths/commands reconciled at fixed ref**: `yes / no + evidence`
- **Coverage status**: `complete / incomplete / blocked`

## Delivery

- **Branch**: `<branch>`
- **Commit**: `<exact commit>`
- **PR/MR**: `<url>`
- **Validator results**: `<pointer>`
- **Executed verification**: `<pointer>`
- **Observed but not executed**: `<pointer>`
