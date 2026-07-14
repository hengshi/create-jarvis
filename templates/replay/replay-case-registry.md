# Replay Case Registry

> `evals/history-replay/` 的索引。两表：每个 pilot repo / 已授权历史来源的 search coverage；selected cases。不设固定 case 数量或扫描窗口。不放置 hidden oracle 细节。

## Search Coverage

每个 pilot repo 和已授权 issue/ticket/incident/delivery 历史来源，记录实际做了什么、为什么停止。

| 来源 | 实际命令/查询 | 查询边界 | 候选 | 排除理由 | 停止理由 | 状态 |
|---|---|---|---|---|---|---|
| `<repo/source>` | `<exact command>` | `<时间或提交边界>` | `<candidates>` | `<why excluded>` | `<why stopped>` | scanned / eligible-found / needs-input / blocked |

## Selected Cases

| Case ID | Episode Pointer | Cutoff | START Construction | Eligibility | Current Skills | Contamination | Last Run | Result | Decision | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| `<case-id>` | `<commit/MR/issue/incident/ticket pointer>` | `<cutoff ref>` | direct-pre-fix / parent-observed / reconstructed-from-outcome-subject | eligible-direct / eligible-reconstructed / ineligible-leaky / needs-better-start / ready-for-replay | `<current skill pointers>` | yes / no / regression-only | `<date/run-id or 未执行>` | `<matched / partial / mismatched / blocked / invalid>` | `<no_skill_gap / task-local / repo-local / company-jarvis / source-skill / workflow-skill / upstream / defer>` | `<next action>` |

## Queue Rules

- 只有代表独立 failure mode、重复模式或高影响 miss 的 episode 才进入 registry。
- Search coverage 记录实际扫描工作；存在 START/oracle 可分离的候选时，必须至少创建一个 `cases/<case-id>/history-replay-case.md`。
- Visible START 必须和 hidden outcome oracle 分离。
- 有 Git 历史时先自动扫描，不默认等客户手工提供 episode。
- 只有 `eligible-direct` 或 `eligible-reconstructed` case 在 visible/hidden 分离并完成 CLI/isolation checks 后才能写 `ready-for-replay`。
- 兼容状态词：`eligible-direct`、`eligible-reconstructed`、`ineligible-leaky`、`needs-better-start`、`ready-for-replay`。
- 优先写回 repo-local 或 company-local，除非 lesson 是 company-neutral methodology。
- 现有 guidance 已足够时记录 `no_skill_gap`，不扩展 skill。
