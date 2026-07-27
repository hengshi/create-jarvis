# 历史重放 Case

> **Outer case**——包含 hidden oracle，不能提供给 replay agent。本文件与被测 skills、replay agent 之间必须有独立的可读边界。本文件只能由外层 Repository learning agent 读。

## Case Identity

- **Case ID**: `<case-id>`
- **Episode type**: `issue-to-outcome` / `feature-request-to-delivery` / `incident-to-resolution` / `support-case-to-resolution` / `review-to-disposition` / `task-to-outcome` / `reconstructed-problem-to-outcome`
- **Original problem pointer**: `<issue / request / incident / support / review / task；Git-only 时为 reconstructed START provenance>`
- **Original work goal / problem**: `<cutoff 前存在的原始任务、需求或问题 pointer>`
- **Outcome pointer**: `<cutoff 后可验证的 final disposition / MR / commit / delivery pointer>`
- **Episode evidence**: `<issue / ticket / MR / review / CI / test / delivery pointers>`
- **Group commits**: `<Git episode 的 ordered commit evidence；非 Git episode 写 not-applicable>`
- **Code-change inspection**: `<逐 commit patch/changed-code 读取证据 pointer；不能只填 message 或 stat>`
- **Range coverage disposition**: `<这些 commits 是 episode seed / supporting / preconsumed / code-read exclusion>`
- **Cursor seed**: `<source artifact/commit selected for discovery>`
- **Cursor after episode**: `<next pointer in the requested traversal; non-contiguous evidence does not move this implicitly>`
- **Preconsumed commits**: `<non-seed Git evidence skipped if encountered later；非 Git episode 写 not-applicable>`
- **Calibration skill ref before**: `<authoritative-derived or cumulative snapshot ref>`
- **Calibration skill ref after**: `<same ref for no-update, or promoted cumulative ref>`
- **Repo**: `<repo name or source>`
- **Cutoff ref**: `<parent commit / pre-fix timestamp>`
- **START construction**: `direct-pre-fix` / `parent-observed` / `reconstructed-from-outcome-subject`
- **Replay eligibility**: `eligible-direct` / `eligible-reconstructed` / `ineligible-leaky` / `needs-better-start`
- **Status**: `draft` / `ready-for-replay` / `replayed` / `closed` / `needs-better-start`

## Source Search & Selection

- **Selection source**: `git-history` / `pilot` / `issue` / `MR` / `incident` / `ticket` / `task`
- **实际搜索命令**: `<exact command, e.g. git log / git show>`
- **实际 code-read 命令/证据**: `<读取 patch、parent/final code、tests 的命令和输出 pointer>`
- **选中理由**: <为什么这是与当前 workflow/repo skill 相关的完整真实工作 episode>
- **为什么可执行**: <目标明确、初始信号足够、outcome 可验证、START/oracle 可分离>
- **搜索边界**: <时间或提交范围>
- **候选排除理由**: <why other candidates were excluded>
- **Episode 边界证据**: <原始任务如何关联到 MR/commits/review/CI/test/final disposition>

`commit`、`commit-group` 和 `MR` 不能作为 episode type。它们是发现 seed、过程容器或 outcome
evidence；即使 episode 最终只有一个 fix commit，也必须写清“原始问题 → 可验证 outcome”的
边界，Git-only 重建使用 `reconstructed-problem-to-outcome`。

## Visible START State

只包含 cutoff 时执行者已可见或按当时权限可合理取得的事实。每条 fact 记录 provenance、timing 和 projection。

### Visible Fact Provenance

| Fact ID | Outer Provenance | Source Timing | Visible Projection | Allowed in Packet |
|---|---|---|---|---|
| `<fact-id>` | pre-fix-artifact / parent-observed / reconstructed-from-outcome-subject | pre-outcome-direct / parent-observed / outcome-metadata-reconstructed | `<replay agent 看到的归一化文本>` | yes / no + reason |

### Allowed Sources & Snapshot

| Surface | Scope | Access Status | Notes |
|---|---|---|---|
| `<repo/source>` | `<allowed paths or systems>` | available / blocked / unknown | |

### Current Skills

被测对象是当前 repo 的 repo-local skills；runtime 方法 skill 只作为执行工具，不是本 case 的写回目标。第一个 episode 从 authoritative snapshot 派生，后续 episode 使用已验证的累计 ref。历史 repo snapshot 冻结在 cutoff。

| Skill | Version / Pointer | Expected Role |
|---|---|---|
| `<skill>` | `<ref>` | routing / execution / source / workflow |

### Contamination Check

episode 是否曾直接影响当前 skill 的内容：

- **Episode 相关事实已写入当前 skill？** `yes` / `no`
- **若 yes**: <哪些内容已被包含，此 case 只能做回归验证，不能独立证明发现新 gap 或泛化>

### Known Unknowns at START

- `<unknown>`

## Replay Prompt

给 replay agent 的 prompt。不含 hidden outcome 信息。

```text
<prompt>
```

### Visible Packet Fact Closure

逐条登记 visible packet 中的事实声明和收窄执行范围的指令。仅把某个 repo/source 列为可访问范围，不等于允许指定其中的未来实现位置。

| Packet File | 事实声明或 narrowing instruction | Supporting Fact ID(s) | Closure Result |
|---|---|---|---|
| `replay-prompt.md` / `allowed-sources.md` / `skill-entrypoints.md` | `<packet 中的完整声明或指令>` | `<fact-id(s)>` | supported / remove-from-packet |

## Isolation Mount Allowlist

- **Visible packet dir**: `<replay-workspace>/<case-id>/visible-packet/`
- **Replay agent CLI checks**: `<replay-workspace>/<case-id>/replay-agent-cli-checks.md`
- **Replay worktree / snapshot**: `<parent commit worktree or allowed read-only repo pointer>`
- **Mount allowlist**:
  - `visible-packet/`（只含 replay prompt、allowed sources/repos、skill entrypoints、cutoff snapshot pointer）
  - cutoff snapshot
  - 当前 repo-local skills
  - 独立输出目录
- **禁止挂载**:
  - 本 outer case 文件
  - `replay-failure-analysis.md`
  - `skill-update-decision.md`
  - Hidden oracle artifacts
  - Repository learning transcript / 已有 failure analysis
  - 未来 Git refs

## Hidden Outcome Oracle

> 本节禁止提供给 replay agent。

- **Actual outcome**: `<final disposition or fix summary>`
- **Actual owner / repo / source**: `<owner and surface>`
- **Actual changed surfaces**: `<files, modules, docs, workflows——完整列表>`
- **Final artifact extraction command / pointer**: `<读取完整 final diff 或等价 outcome artifact 的 exact command/pointer>`
- **Final artifact fully read**: `yes` / `no`
- **Relevant code changes fully understood**: `yes` / `no`（必须读实际 patch 与必要上下文，message/stat 不足）
- **Documented root cause**: `<历史材料明确记录的 root cause；未记录写 unknown>`
- **Actual verification evidence**: `<checks, review, CI, manual proof>`
- **Historical verification status**: `verified` / `partial` / `unknown`
- **Final diff / commit pointer**: `<commit hash, MR pointer, or controlled artifact pointer>`
- **Expected durable writeback**: `none` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream`
- **Expected dimensions for oracle comparison**:
  - Route: `<expectation>`
  - Evidence boundary: `<expectation>`
  - Repo-local boundary: `<expectation>`
  - Verification: `<expectation>`
  - Closure / writeback: `<expectation>`

### Hidden Facts Excluded From Visible Packet

| Hidden Fact | Outcome Evidence | Exact Packet Review | Result |
|---|---|---|---|
| `<changed path / implementation target / root cause / fix direction / outcome>` | `<final artifact pointer>` | `<检查了哪些 packet 文件>` | absent / leaked |

## Case Readiness Gate

> 在调用隔离 replay runtime 前由外层 Repository learning agent 完成。

- **Visible fact 表完整**: `yes` / `no`
- **Packet Fact Closure 表完整**（每条 visible-packet 事实可回指 Fact ID）: `yes` / `no`
- **Hidden Facts Excluded 表完整且结果全部为 absent**: `yes` / `no`；若 `no`，列明：<leaked items>
- **Hidden oracle 已从真实 final artifact 完整提取**: `yes` / `no`
- **Exact evidence command/pointer 已记录**: `yes` / `no`
- **Case validity**: `valid` / `invalid`
- **Readiness**: `ready` / `invalid`
- **Invalid reason**（若 `invalid`）: <explanation>

`invalid` / `not-ready` case 不得执行。

## Redaction / Leak Review

- <去除了什么或做了什么泛化>
- <私有证据是否仅在受控 company instance 内保留>
- <commit metadata 是否泄露了 cause/fix/implementation；若是，为什么本 case 是 ineligible-leaky 或 needs-better-start>
- <每条 visible fact 的 provenance 检查结果——是否能独立于 hidden outcome 成立>
