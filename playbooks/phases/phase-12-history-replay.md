# Phase 12 — 历史回放

目标：从每个 pilot repo 及相关已授权历史来源的真实历史 episode 中，以“当时可见初始信号”构造 eval case，使用当前 skills 隔离重放，找到失败模式，只把可复用、可验证的缺口交给 Phase 13。

## A. Episode 搜索

### 搜索范围

runtime agent 主动扫描每个 pilot repo 和已授权 issue/MR/ticket/incident/delivery history。不是只扫 Git，也不等用户整理。

每个 repo 记录：

- 实际命令/查询；
- 时间或提交边界；
- 候选和排除理由；
- 为什么停止继续扩大搜索。

**无固定数量或固定扫描窗口**。记录实际做了什么、为什么停止。

### Episode 准入

episode 必须同时满足：

1. 有当时明确的工作目标；
2. cutoff 前有足够开工的 initial signal；
3. cutoff 后有可验证的 outcome；
4. 有授权访问。

以下候选不进入 replay（可留 backlog）：

- 没有明确任务目标，无法评价 skills 的路由、执行、验证或闭合；
- 无可验证 outcome；
- START/oracle 无法分离（commit message 披露了全部答案且无法还原独立症状）。

## B. 时间切片与当前 skills

### Visible START（可见初始信号）

visible START 只含 cutoff 时已可见或按当时权限可合理取得的事实。每条 fact 记录：

- provenance（来源：哪个 pre-fix artifact、parent-state 信号，或 `reconstructed-from-outcome-subject`）；
- 为什么 cutoff 前可见。

合法来源：

1. **直接 pre-fix artifact**：issue、ticket、log、failing test output、alert、用户描述——在修复前已存在且独立于修复。
2. **Parent state 可独立复现的信号**：从 parent commit 的代码、测试、日志中可直接观测到的症状，不依赖对最终 diff 的了解。
3. **从 commit subject 重建**：最终 commit subject 主要用于找候选；只有其中可独立成立的外部症状/请求可谨慎投影到 START。原因、修复方向、changed paths、方法/字段等未来答案不能投影。无法安全分离的候选标 `needs-better-start` / `rejected-leaky`。

### Hidden Oracle（隐藏答案）

hidden oracle 必须陈述从完整 final diff/artifact 中观察到的真实 outcome。禁止用 `likely`、`probably` 或经验猜测替代。若历史 root cause 或 verification 未记录，写 `unknown`。历史 outcome 是"发生了什么"的证据，不自动是最优解。

hidden oracle 含 cutoff 后发生的事实：

- 最终 commits / diff / changed files；
- MR/PR 评论、review correction；
- root cause analysis；
- verification evidence；
- final outcome。

这些内容**默认全部是 hidden oracle**，不能在构造 visible START 时作为"已知事实"使用。

### Visible-Packet 事实闭环

`visible-packet/` 中的 `replay-prompt.md`、`allowed-sources.md` 和 `skill-entrypoints.md` 中的每条事实声明和每条 narrowing instruction 必须逐条写入 outer case 的 Visible Packet Fact Closure 表，并对应到 Visible Fact Provenance 的一个或多个 Fact ID。仅允许某个 repo/source 不等于授权命名某个未来的 file/class/method/fix target。

### reconstructed-from-outcome-subject 规则

`reconstructed-from-outcome-subject` 只能投影可独立成立的外部症状。任何新增行为声明需要 `direct-pre-fix` 或 `parent-observed` 证据。任何 file、directory、module、class、method、field、constant、root cause 或 fix direction 需要其自己的 pre-outcome provenance。

### 当前 Skills

- 历史 repo/source snapshot 冻结在 cutoff；被测对象是运行时“当前版本”的 company/repo-local/source/workflow skills，不回退成历史 skill。
- 记录当前 skill pointers，并检查该 episode 是否曾直接写入当前 skill。若 skill 已包含 case-specific hidden outcome，此 case 只能做回归，不能独立证明发现新 gap 或泛化。

## C. 隔离与执行

### 物理分离

- outer case（含 oracle）与 visible packet 物理/权限分离。replay agent 只能读：visible packet、cutoff snapshot、裁剪后的当前 company Jarvis runtime、必要 repo-local skills、独立输出目录。
- 有效隔离要求独立 container/VM/等价文件系统边界。同一主机 fresh process、Task Workspace、`--add-dir` 不能单独证明隔离。
- 透传 selected agent 必需的最小凭据环境，不把值写进 artifact。
- runtime/handoff 已提供 executable isolation bridge helper 时，该 helper 就是当前可用的隔离 transport。必须按其调用合同执行；不得因为当前容器内看不到 Docker/Podman，或因为尚未调用 helper，就写 bridge/container/VM/isolated replay transport unavailable。

### Case Readiness Gate（调用 replay bridge 前）

在启动 replay 前，外层 agent 必须在 outer case 中完成以下门禁：

- visible fact 表完整；
- Visible Packet Fact Closure 表完成（每条 visible-packet 事实均可回指 Fact ID）；
- Hidden Facts Excluded From Visible Packet 表完成，且每项检查结果均为 `absent`；
- hidden oracle 已从真实 final artifact 完整提取；
- 精确 evidence command/pointer 已记录；
- 外层 agent 标记 `ready` 或 `invalid` 并解释原因。

`invalid` / `not-ready` case 不得执行。若执行后发现泄漏，分类为 `invalid` / `not-evaluated`；Phase 12 完成前必须另选一个有效 case。

### Preflight

replay 前运行 preflight 确认：

- START/provenance 完整性；
- mount allowlist 正确；
- future refs/oracle 不可见；
- agent CLI 可用。

preflight 做明显的泄漏/结构检查。runtime agent 对语义负责；不写复杂的 identifier 黑名单算法。

### 执行

- replay 重放原任务，不猜 patch。适用时在 cutoff 可写副本真实修改并运行验证；分析/评审任务按原合同交付。
- 记录 exact invocation（脱敏）、exit code、非空执行轨迹、diff/输出、验证结果。
- CLI 在首个有效 action 前失败 = `replay-not-executed`，不产生 skill gap / `no_skill_gap` 结论。

## D. Oracle Comparison 与归因

### Comparison

- replay 结束后由外层 bootstrap agent 读取完整真实 outcome/oracle；replay agent 不自评 oracle。
- 必须首先读取 exact replay final output 和 exact 历史 final outcome。记录 command/pointer 和完整 changed surfaces 或等价非代码 artifact。
- 不要求逐字/逐 patch 相同。比较：route/owner、关键证据、边界、行为结果、验证、越权/幻觉、闭合。
- 替代 replay 方案只有经独立行为验证后才能称为等价/更优；否则标 `unproven`。
- 允许指出历史 outcome 局限。
- 结果可用：`matched`、`partial`、`mismatched`、`blocked`、`invalid`。

### 归因

非通过先归因：

- `skill_gap`：现有 skills 存在可复用、可验证的缺口；
- `instance_fact_gap`：实例事实缺失（缺 source/repo 信息）；
- `source_access_environment`：source/access/environment 问题；
- `execution_deviation`：执行偏差（agent 行为偏差而非 skill 问题）；
- `case_construction_leak`：case 构造/泄漏问题；
- `oracle_limitation`：oracle 本身局限。

未执行/invalid 不能判断 skill。

### no_skill_gap → Phase 13

`no_skill_gap` 需要：已执行（`executed`）+ 有效 case + 完整 comparison + 充分 outcome 验证。泄漏/invalid/未验证 case 均为 `not-evaluated`。

按 `references/writeback-governance.md` 做 `no_skill_gap` 决策。skill gap 需要可复用、有证据、可验证、归属明确。重复 episode 或高影响单例都可，但必须解释复用性。

Phase 13 执行 skill 更新后，用同一 case 复跑证明该回归改善；同一 case 不单独证明泛化。

## E. 产物和状态

### 目录结构

```text
evals/history-replay/
├── replay-case-registry.md
└── cases/
    └── <case-id>/
        ├── history-replay-case.md
        ├── replay-failure-analysis.md
        └── skill-update-decision.md

_bootstrap/history-replay-runs/
└── <case-id>/
    ├── visible-packet/
    │   ├── replay-prompt.md
    │   ├── allowed-sources.md
    │   └── skill-entrypoints.md
    ├── replay-agent-cli-checks.md
    ├── replay-agent.jsonl
    ├── replay-agent.stderr.log
    └── replay-result.md
```

三个规范模板为强制可执行合同：

- `templates/replay/history-replay-case.md`
- `templates/replay/replay-failure-analysis.md`
- `templates/replay/skill-update-decision.md`

runtime agent 必须实例化并完整填写模板的现有 sections/fields，不得用缩减自由格式替代。额外参考：

- `templates/replay/replay-case-registry.md`

### 状态判定

- `completed`：至少一个真实 ready case 在有效隔离中实际执行，外层完成 oracle comparison、归因和 writeback decision。更多候选可进 backlog，不作为缺输入。Phase 12 不修改 skills；写回和复跑由 Phase 13 执行。
- `needs-input`：没有合格 episode、缺授权/真实 outcome/隔离 runtime/可用 agent 等。必须写已完成的搜索和下一步。已识别候选但没有创建 case 文件时不是合格 `needs-input`，而是执行不完整。
- `blocked`：source/repo/history 权限不可用，或 visible/hidden 无法安全分离。
- `failed`：泄漏 oracle 后仍执行并据此下 skill 结论、secret 泄漏、越权写入等。

## 执行步骤

1. 创建或更新 `evals/history-replay/replay-case-registry.md`。
2. 扫描每个 pilot repo 和已授权 issue/MR/ticket/incident 历史，记录命令/查询、时间或提交边界、候选和排除理由、停止原因。无固定数量或窗口。
3. 为 episode 分配稳定 id，例如 `replay-YYYYMMDD-001`。
4. 选择 START/oracle 可分离且能覆盖真实风险的 episode，为每个选中的 episode 创建完整 `evals/history-replay/cases/<case-id>/history-replay-case.md`。其余候选留在 registry backlog；不能只留候选而不创建任何可执行 case。
5. 填写 visible START：initial signal、provenance（每个 fact 的来源和 pre-outcome 状态）、allowed sources/repos、available skills、known unknowns、replay prompt。把每条 visible-packet 事实和 narrowing instruction 逐条写入 Visible Packet Fact Closure 表，并回指 Visible Fact Provenance 的 Fact ID。
6. 填写 hidden outcome oracle：必须用已记录的 exact command/pointer 读取完整真实 final diff/artifact，提取实际观察到的 outcome，禁止 `likely`/`probably`/猜测。记录 final commit/MR/decision pointer、actual owner/repo/source、actual changed surfaces、actual verification evidence、expected durable writeback。若历史 root cause 或 verification 未记录，写 `unknown`。填写 Hidden Facts Excluded From Visible Packet 表。
7. 创建 `_bootstrap/history-replay-runs/<case-id>/visible-packet/`。visible-packet 只放 replay prompt、allowed sources/repos、skill entrypoints、parent commit / worktree pointer。不放 hidden oracle、final diff、最终 commit message、failure analysis。
8. 运行 Case Readiness Gate：visible fact 表、Visible Packet Fact Closure 表和 Hidden Facts Excluded 表完整，排除项均为 `absent`，hidden oracle 已从真实 artifact 完整提取，exact evidence command/pointer 已记录。外层 agent 标记 case validity 和 `ready` / `invalid`。`invalid`/`not-ready` 不得执行。
9. 创建 `_bootstrap/history-replay-runs/<case-id>/replay-agent-cli-checks.md`，记录 agent CLI 可用性、filesystem isolation mechanism、挂载 allowlist。
10. 运行 preflight：
   ```bash
   python3 scripts/verify_bootstrap_output.py \
     --stage phase-12-preflight \
     --jarvis-home <company-jarvis-home> \
     --case-id <case-id>
   ```
   它只辅助检查结构和明显泄漏；runtime agent 仍负责判断每条 visible fact 的语义 provenance。preflight 不通过时修 case 或继续搜索。
11. 在独立 container/VM 中执行 replay：只挂载 visible-packet、cutoff snapshot、裁剪后的当前 company Jarvis runtime、必要 repo-local skills、独立输出目录。透传最小凭据环境。
12. replay 完成后，bootstrap agent 先读取 exact replay final output 和 exact 历史 final outcome，记录 command/pointer 和完整 changed surfaces 或等价非代码 artifact。
13. 创建 `replay-failure-analysis.md`：必须使用规范模板并完整填写所有 sections/fields，不得用缩减自由格式替代。对比 replay result 和 hidden oracle，分维度判断（routing、truth boundary、repo-local boundary、verification、END writeback），分类 failure mode，先做 `no_skill_gap` check。
14. 创建 `skill-update-decision.md`：必须使用规范模板并完整填写所有 sections/fields，不得用缩减自由格式替代。按 `references/writeback-governance.md` 决定 no_skill_gap / primary home / mirror / verification plan。
15. 将候选写回和复跑交给 Phase 13；Phase 12 不直接修改被测 skills。
16. 更新 registry status 和相关 state 文件。

## Oracle Comparison 必须在决策之前

replay 完成后**必须先做 oracle comparison**，再写 failure analysis、skill decision、`no_skill_gap` 判断和 Phase 12 状态更新。无效 case 或 replay 未被 bootstrap agent 收集、比较，不得完成 Phase 12。

## 禁止

- 不用事后答案污染 START。
- 不把 hidden oracle 放进 replay prompt。
- 不把 final commit message、changed-file list、final diff、最终测试或修复原因放进 visible packet。
- 不把从最终 diff 得出的 changed path 放 visible packet。
- 不因为一次性误差扩展 skill。
- replay agent 未执行时不判断 `no_skill_gap`，不把 shadow pilot 当 history replay 证据。
- 不在 oracle comparison 之前写 failure analysis、skill decision、`no_skill_gap` 或 Phase 12 状态。
- 不把 repo-local execution truth 写进 company Jarvis。
- 不把 private company facts upstream 到 create-jarvis-skill。
- 不从未执行、泄漏或 outcome 不可验证的 case 推导 skill gap。
- 不在有效隔离 replay 完成前进入 Phase 13/14 的 completed 状态。
- 不在 executable isolation bridge helper 已提供时声称 bridge、container/VM runtime 或 isolated replay transport unavailable。

## 读物

- `GOAL.md`
- `acceptance.md`
- `playbooks/phase-checklist.md`
- `templates/replay/history-replay-case.md`
- `templates/replay/replay-failure-analysis.md`
- `templates/replay/skill-update-decision.md`
- `evals/scorecard.md`
