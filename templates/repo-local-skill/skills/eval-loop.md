---
name: eval-loop-{{REPO_NAME}}
description: |
  Eval-loop methodology for the {{REPO_NAME}} repository. Defines how to
  turn evidence from real tasks, pilot observations, and history replay into
  bounded skill decisions with recorded skill refs, oracle comparison, and
  same-case rerun.
---

# {{REPO_NAME}} — Eval Loop Methodology

## Cycle

```
  REAL TASK / PILOT / HISTORY REPLAY
    │
    ▼
  BASELINE SKILL REFS — 记录本次执行实际加载的技能版本
    │
    ▼
  EXECUTE — agent 使用此 snapshot 执行任务
    │
    ▼
  ORACLE COMPARISON — 技能输出 vs 实际正确结果（先于 failure classification）
    │
    ▼
  FAILURE CLASSIFICATION — Phase 12 统一分类
    │
    ▼
  DECISION
    ├── no_skill_gap → 记录，不写回
    ├── repo-local update → 更新此 repo skill
    ├── workflow update → 更新 workflow skill
    ├── company jarvis update → 提交 company Jarvis
    └── eval-case-gap / defer → gap 不足以推导 skill 变更
    │
    ▼
  SAME-CASE RERUN — 用同一 case 和修复后的 snapshot 重新执行，验证改善
```

## Step 1: Capture Task Signal

```yaml
trigger:
  type: real_task | pilot_observation | history_replay
  description: "<用户或系统要求什么>"
  repo: "{{REPO_NAME}}"
```

## Step 2: Record Baseline Skill Refs

执行前记录本次实际加载的 skill 文件和可解析的 commit/tree ref。首次回放必须使用 proposed writeback 之前的 baseline；同 case rerun 记录更新后的 refs。不要把 case 创建时间当作永久 snapshot。

## Step 3: Execute

使用已记录的 baseline skills 实际执行任务，保留非空 trace/result、读取过的 evidence 和运行过的验证。signal、文件存在或静态阅读本身不算 skill 执行。

## Step 4: Oracle Comparison（先于 failure classification）

必须读取与结果等价的完整受控 oracle artifact。代码变更 case 要读取完整 final diff 并解释每个 changed surface；没有代码 diff 的分析/评审/决策任务则读取其实际结论和验证证据，不得虚构 diff。

| 任务类型 | Oracle 来源 |
|----------|------------|
| real task | 用户实际需求、人类专家做法、测试输出 |
| pilot observation | pilot 反馈中指出的正确行为 |
| history replay | hidden oracle（修复 commit / 正确 review 结论）|

比较技能输出与 oracle：

| Dimension | Skill Output | Oracle | Finding |
|-----------|-------------|--------|---------|
| Routing | ... | ... | pass / fail / partial |
| Truth boundary | ... | ... | pass / fail / partial |
| Repo-local boundary | ... | ... | pass / fail / partial |
| Verification | ... | ... | pass / fail / partial |
| END writeback | ... | ... | pass / fail / partial |

## Step 5: Failure Classification

使用 Phase 12 统一分类。`replay-not-executed` 是执行状态，不能映射成 `no_skill_gap`；未执行时 primary classification 写 `not-evaluated`。

| Class | Meaning |
|-------|---------|
| `routing_failure` | 技能未能将 agent 路由到正确子 skill 或 reference |
| `truth_failure` | 技能中事实错误或缺失导致判断错误 |
| `boundary_failure` | repo-local 与 company Jarvis 边界不清导致越界或遗漏 |
| `writeback_failure` | 结果未能写回正确位置 |
| `duplication_failure` | 多个技能或文件重复覆盖同一关注点 |
| `bloat_failure` | 技能包含不必要的通用内容 |
| `promotion_failure` | repo-local 事实被错误提升到 company Jarvis |
| `verification_failure` | 验证步骤无法检测实际错误 |
| `no_skill_gap` | 现有技能充分，偏差来自外部因素 |
| `eval-case-gap` | gap 只来自 under-specified / ineligible case，不足以推导 skill 变更 |

## Step 6: Decision

| Decision | When |
|----------|------|
| **no_skill_gap** | 有效执行和完整 oracle comparison 没有证明 durable skill gap——记录，不写回 |
| **repo-local update** | 可复用、可验证、归属明确的 repo-local gap |
| **workflow update** | 偏差涉及跨仓库或团队工作流 |
| **company jarvis update** | 偏差涉及公司级策略、路由或方法论 |
| **eval-case-gap / defer** | gap 只来自 under-specified / ineligible case，不足以推导 skill 变更 |

- 选择唯一 primary writeback home（task-local / repo-local / workflow / company Jarvis / upstream）；mirror 仅在确有必要时。
- 不将 repo-local 事实提升为 company Jarvis update 而不经过 self-improvement 决策门。
- 单个高影响 case 只要证据完整，也可以证明 durable gap。

## Step 7: Same-Case Rerun

修复后用同一 case 和新的 skill snapshot 重新 replay，验证改善：

1. 使用同一 replay case 和 visible START。
2. 使用修复后的技能 snapshot。
3. 与同一 hidden oracle 比较。
4. 失败维度改善、原有正确维度未退化且验证证据成立 → 更新可标 verified。
5. 未改善或引入新退化 → 撤销“已验证”结论，重新分类和修改。

## Durable Record

History replay 使用 company Jarvis 的固定 registry、case、failure analysis 和 skill update decision 文件，不在 repo-local skill 内再发明一份 eval log。真实 task/pilot 只有在证据足以形成可复验 case 时才进入同一闭环；否则保留 task-local observation，不改 skill。
