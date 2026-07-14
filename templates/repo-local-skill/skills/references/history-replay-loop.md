---
name: history-replay-loop-{{REPO_NAME}}
description: |
  History replay loop methodology for the {{REPO_NAME}} repository. Defines
  how replay cases from past commits calibrate skills — aligned with Phase 12.
  Replay case storage and execution artifacts live in company Jarvis, not in
  this repo-local skill.
---

# {{REPO_NAME}} — History Replay Loop

## Purpose

从仓库自身历史中挖掘 case 来校准技能。每个 replay case 严格遵循 Phase 12：visible START 与 hidden oracle 隔离；先执行、再完整 oracle comparison、再 failure classification；未执行是 `not-evaluated`。

**固定产物位置**：replay case 注册表、case 文件和 replay run 产物在 company Jarvis 的 `evals/history-replay/` 与 `_bootstrap/history-replay-runs/`，不在此 repo skill 下创建 `replay-cases` 目录。

## Hidden Oracle 模式

以下内容**默认全部是 hidden oracle，不向 replay agent 暴露**：

- 最终 commit message（完整 subject + body）
- 最终 changed-file list 和 diff
- 最终测试名、测试内容、测试结果
- 修复原因（root cause analysis）和修复策略
- reviewer/owner 的修正意见

### Visible START（仅来自 pre-outcome artifact）

回放开始时 agent 只能看到：

- **直接 pre-fix artifact**：issue、ticket、log、failing test output、alert、用户描述——这些在修复前就存在且独立于修复。
- **Parent state 可独立复现的信号**：从 parent commit 的代码、测试、日志中可以直接观测到的症状。
- **eligible-reconstructed**：只从纯外部症状的最终 commit subject 归一化投影出的外部症状，不含 cause/fix/实现标识。outer case 必须如实记录 outcome provenance；visible packet 只获得投影文本。

**绝对不能**在 visible START 中暴露：修复 commit 的 diff、root cause、changed paths、commit hash、author，或只从 outcome 才得知的实现标识符和修复方向。直接 pre-outcome artifact 中本来就出现的标识符可以保留，但必须有逐条 provenance。

## Provenance Awareness

每个 visible fact 必须记录：

- **provenance**：来自哪个 pre-fix artifact、哪条 parent-state 信号，或 `reconstructed-from-outcome-subject`
- **source timing**：`pre-outcome-direct`、`parent-observed` 或 `outcome-metadata-reconstructed`
- **visible projection**：实际交给 replay agent 的归一化文本

`outcome-metadata-reconstructed` 只允许投影纯外部症状；完整 provenance 和重建过程留在 outer case，不进入 visible packet。

## Replay Discipline

### Step 1: Construct Case（仅用 visible START）

- 扫描 pilot repo Git 历史（自适应窗口 80→200→500）
- 处理每个候选 commit：分离可见症状和隐藏结果
- 含 cause、修复方向、具体实现标识或 changed paths 的 case 标 `ineligible-leaky`，不得启动 replay
- 只有 `eligible-direct` 或 `eligible-reconstructed` case 可进入 replay

### Step 2: Isolated Replay

- 隔离必须是 container/VM 等真实文件系统边界；同机 fresh process 或 `--add-dir` 不构成隔离
- replay agent 只能访问 visible packet（replay prompt、allowed sources、skill entrypoints）、parent commit source（只读挂载或内部可写 worktree）、裁剪后的 company Jarvis runtime 副本
- 每次 run 记录该次实际使用的 baseline skill refs/snapshot；首次 replay 使用写回前的技能，rerun 使用更新后的技能。case 本身不永久绑定创建时的技能版本
- 在可写 parent snapshot 中完成真实 WORK（诊断后实施候选修复/文档变更并运行可用验证），不是只提出方案

### Step 3: Oracle Comparison（先于 failure classification）

- 读取完整 final diff 或等价受控 oracle artifact
- 逐个解释每个 changed surface 为什么存在
- 分维度对比：routing、truth boundary、repo-local boundary、verification、END writeback

### Step 4: Failure Classification

使用 Phase 12 统一分类（仅当 replay 实际执行后）：

| Class | Definition |
|-------|------------|
| `routing_failure` | 技能未能将 agent 路由到正确子 skill 或 reference |
| `truth_failure` | 技能中事实错误或缺失导致判断错误 |
| `boundary_failure` | repo-local 与 company Jarvis 边界不清导致越界或遗漏 |
| `writeback_failure` | 结果未能写回正确位置 |
| `duplication_failure` | 多个技能或文件重复覆盖同一关注点 |
| `bloat_failure` | 技能包含不必要的通用内容 |
| `promotion_failure` | repo-local 事实被错误提升到 company Jarvis |
| `verification_failure` | 验证步骤无法检测实际错误 |
| `no_skill_gap` | 本次有效 replay 和完整 oracle comparison 没有证明 durable skill gap |
| `eval-case-gap` | gap 只来自 under-specified / ineligible case，不足以推导 skill 变更 |

`replay-not-executed` 是执行状态，不属于 skill failure，不能映射成 `no_skill_gap`。未执行时 primary classification 写 `not-evaluated`。

### Step 5: Decision（no_skill_gap 优先）

| Condition | Decision |
|-----------|----------|
| 技能输出与 oracle 一致 | `no_skill_gap` — 记录并归档，不写回 |
| 可复用、可验证、归属明确的 repo-local gap | `repo-local update` — 修复对应文件 |
| 跨仓库工作流 gap | `workflow update` — 更新 workflow skill |
| 公司级方法或策略 gap | `company jarvis update` — 提交 company Jarvis MR |
| Gap 只来自 under-specified / ineligible case | `eval-case-gap` / `defer` — 不写 skill |

选择唯一 primary writeback home（task-local / repo-local / workflow / company Jarvis / upstream）；mirror 仅在确有必要时。

### Step 6: Same-Case Rerun

修复后保持同一 visible START、allowed sources、隔离边界和 hidden oracle，改用更新后的 skill refs 重新 replay。只有失败维度得到改善、原有正确维度未退化且验证证据仍成立，才能把更新记为 verified。

## When NOT to Start Replay

- `ineligible-leaky`：含 outcome-derived cause / 修复方向 / 实现标识 / changed paths——登记排除理由，不得启动 replay，继续搜索其他候选
- `low-confidence` / `needs-better-start`：START 不足——扩大搜索窗口或查询授权 source
- 只证明网络、权限或本机配置故障，且没有任何可复用 skill 行为可评估的 episode

拒绝一个泄漏 case 只是正确的中间结果，不代表 Phase 12 完成。必须继续扫描所有 pilot repo 的 80→200→500 窗口；只有授权历史全部耗尽后，才可记录 `needs-input`。
