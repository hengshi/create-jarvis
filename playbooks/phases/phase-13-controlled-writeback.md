# Phase 13 — 受控写回

目标：把 Phase 11 的 eligible learning 和 Phase 12 已进入累计 calibration baseline 的 ordered verified candidate set 写回正确 authoritative home。受控写回不是"把发现都写进 JARVIS"——它只处理可复用、可验证、归属明确的学习。

## 受控写回 vs jarvis-box Retry Writeback

明确区分两个概念：

- **受控写回（本 phase）**：把 Phase 11/12 验证过的 learning 写入它的事实或方法 owner，执行路径服从目标位置的实际写入和审批政策。
- **Retry Writeback（jarvis-box lifecycle operation）**：只重试已经生成的 provider delivery。不用于 skill 写回、pilot evidence 生成或 bootstrap resume。

如果 writeback 在某个真实 Task 中继续，可使用 jarvis-box Continue With Agent 创建后续 Run；否则在当前授权上下文中按目标 owner 的政策执行。

## 前置条件

- Phase 11 和 Phase 12 已完成。
- 如果任一前置 phase 是 `needs-input`、`blocked` 或 `failed`，不进入 Phase 13；Phase 13 保持 `pending`，当前 bootstrap 从前置 phase 恢复。
- 无有效 Phase 12 replay（未在独立 container/VM 中完成隔离 replay）时，不得写入由该 replay 推导出的规则。这些规则必须留在 backlog，等待有效 replay 后再写回。
- `replay-not-executed` 不能产生 `no_skill_gap` candidate。对应 decision 只能是 `defer`。

## Learning Signal 准入

只消费 source gate 有效且 evidence contract 完整的 eligible learning signals：

- Phase 11 pilot：END decision 有完整 START-WORK-VERIFY-END evidence；
- Phase 12 replay：case validity 为 `valid`、Replay eligibility 为 `eligible-direct` / `eligible-reconstructed`、case Status 为 `replayed` / `closed`、execution gate 为 `executed`、oracle comparison 完整、changed-surface 逐项说明完整、outcome verification 足以支持判断。

invalid / `replay-not-executed` / 泄漏 / oracle 未验证的 signal 可记录为 `deferred` / `not-evaluated`，但不得计为 `no_skill_gap`、`skill_gap`、`closed` 或 completed candidate。Phase 13 完成只计 eligible candidates。

## 汇总 Learning Signals

汇总 Phase 11/12 已验证的 learning signals，先区分两类：

1. **稳定事实修正**：事实缺失或错误（如 source route、repo path、owner 映射）——可直接写入其事实 owner。
2. **方法/skill 缺口**：需要扩展 skill guidance——必须先完成 `no_skill_gap` 判断。

## Primary Home

每条学习只选一个 primary home，严格按 `references/writeback-governance.md`：

- task-local note；
- repo-local skill/reference；
- company module/reference；
- source skill；
- workflow skill；
- upstream create-jarvis-skill；
- no writeback。

只有当另一层必须发现/执行该规则时，才做 mirror writeback。mirror 只写 pointer/summary，不复制细节。

## 固定产物

`_bootstrap/controlled-writeback-log.md`

使用模板：`templates/company-jarvis/artifacts/controlled-writeback-log.md`

## 执行步骤

1. 收集 candidates（只收集 eligible signals——source gate 有效且 evidence contract 完整）：
   - Phase 11 pilot END decisions（完整 START-WORK-VERIFY-END evidence）；
   - Phase 12 ordered verified candidate set（仅限 Replay eligibility `eligible-direct`/`eligible-reconstructed` + Status `replayed`/`closed` + `executed` + 完整 oracle comparison；`skill_gap` 还必须有 candidate diff、same-case rerun 和 cumulative-baseline promotion；stable-fact 还必须有当前权威来源验证）；
   - owner review 指出的 durable gap；
   - verifier/e2e 发现的 generic contract gap。
   
   invalid / `replay-not-executed` / 泄漏 / oracle 未验证 signal 记录为 `deferred` / `not-evaluated`，不进入 candidate pool。
2. 为每条 candidate 填写 writeback record：source evidence pointer、source gate、evidence contract、proposed learning、affected layer、owner、verification evidence。
3. 对方法/skill candidate 判断 `no_skill_gap`；稳定事实修正不以扩展 skill 为前提：
   - existing guidance 是否已经足够；
   - 失败是否由缺数据、缺权限、runtime、一次性误解或代码 bug 引起；
   - 是否需要 skill/doc 改动。
4. 判断 primary home：
   - repo 命令、路径、架构、测试、local pitfall → repo-local；
   - company routing、workflow、source map、owner map → company module/reference；
   - source access/query/redaction/freshness → source skill；
   - START/WORK/VERIFY/END 编排 → workflow skill；
   - company-neutral bootstrap/checklist/eval contract → upstream create-jarvis-skill；
   - 没有 durable gap → no writeback。
5. 判断 mirror writeback：只有当另一层必须发现/执行该规则时才 mirror。
6. 做 redaction：去除 secret、个人隐私、未经授权材料、raw source dump、长篇聊天/issue/MR 原文和 hidden oracle；客户实例保留必要的真实身份与稳定 repo-relative pointer，upstream 再做 company-neutral 化。
7. 执行写回：
   - 按 Phase 12 ordered candidate set 的顺序应用，先核对每个 diff 只修改 decision 指定的 primary home，且与 calibration snapshot 的 verified diff 一致；
   - 按目标 owner 的实际写入/审批政策执行，不预设 branch/MR/PR/CI；
   - 使用最小 patch，不重写无关文档；
   - 保留 evidence pointer；
   - 标注 owner approval 或 needs-owner-confirmation；
   - 冲突不覆盖，owner 确认。
8. 验证写回：
   - 用原 pilot/replay 或等价真实任务验证；
   - repo-local：运行 precheck 或相关 replay；
   - company：重跑 routing/pilot trace；
   - workflow/source skill：重跑对应 START/route；
   - upstream create-jarvis-skill：跑 eval 或记录为什么暂不加 eval。
9. 全部 candidate 应用后，核对最终 authoritative diff/ref 与 Phase 12 累计 `calibration_skill_ref` 等价；再用最终累计 authoritative snapshot 对 ordered set 中每个受影响 case 做交付复验，确认后续 candidate 没有让较早 case 回归。这不是替代 Phase 12 的 candidate rerun，也不单独证明跨 episode 泛化。更新对应 replay result、decision 和 registry。
10. 更新 `_bootstrap/controlled-writeback-log.md`。
11. 只有治理规则本身变化时才更新 `references/writeback-governance.md`；不要每次写回都修改它。

## 状态判定

- `completed`：所有 eligible candidates（影响 first workflow/bootstrap 验收）已完成 writeback 或明确 `no_skill_gap`，且 verification 记录完整；可选候选进入有 owner/触发条件的 backlog。只计 eligible candidates；`deferred`/`not-evaluated` signal 不计入完成判定。
- `needs-input`：进入 Phase 13 后，缺 owner approval、eligible candidate 所需 evidence、primary home 判断或 verification command。
- `blocked`：写回目标不可写、权限缺失、policy 禁止或 redaction 无法完成。
- `failed`：写回泄露 private facts、写错 primary home、破坏 existing guidance、未验证就标 completed，或规则来自未完成有效隔离 replay 的 Phase 12 却当作已验证学习写入。

## 禁止

- 不把 raw issue/MR/docs/chat 当作长期记忆。
- 不把公司私有事实写进 generic methodology。
- 不把 repo-local execution truth 提升到中心层。
- 不为了让 backlog 变少而合并不相关 learning。
- 不从无有效隔离 replay 的 Phase 12 推导规则后写入。
- 不用 Phase 11 shadow pilot 替 Phase 12 replay 关闭 writeback candidate。
- 不把 controlled writeback 写成 jarvis-box Retry Writeback。

## 读物

- `GOAL.md`
- `acceptance.md`
- `playbooks/phase-checklist.md`
- `references/writeback-governance.md`
- `templates/company-jarvis/artifacts/controlled-writeback-log.md`
