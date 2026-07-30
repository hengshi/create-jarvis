# Replay Case Registry

> `evals/history-replay/` 的索引。三表：history cursor、每个声明 repo / 已授权历史来源的 search coverage、selected cases。不设固定 case 数量或扫描窗口。不放置 hidden oracle 细节。

## History Cursor

cursor 只负责导航、断点恢复和去重，不承担先分类整个历史范围的工作。

| Repo / Source | Mode | Requested Boundary | Direction | Next Pointer | Last Closed Episode | Preconsumed Commits | Calibration Skill Ref | Ordered Candidate Set | Owner | Resume Entry | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `<repo>` | seed / full-range | `<time/ref boundary>` | newest-to-oldest / oldest-to-newest | `<commit>` | `<case/group id>` | `<commit list or pointer>` | `<snapshot ref/digest>` | `<ordered decision/candidate ids>` | `<owner>` | `<exact prompt/state/command pointer>` | in-progress / seed-closed-with-continuation / boundary-reached / blocked |

## Search Coverage

每个声明 repo 和已授权 issue/ticket/incident/delivery 历史来源，记录实际做了什么、为什么停止。

| 来源 | 实际命令/查询 | 查询边界 | Code-read coverage | 候选 | 排除理由 | 停止理由 | 状态 |
|---|---|---|---|---|---|---|---|
| `<repo/source>` | `<exact command>` | `<时间或提交边界>` | `<patch/code evidence pointer + next uncovered ref>` | `<candidates>` | `<why excluded after inspecting changes>` | `<why stopped>` | scanned / eligible-found / needs-input / blocked |

## Selected Cases

| Case ID | Episode Pointer | Cutoff | START Construction | Eligibility | Current Skills | Contamination | Last Run | Result | Decision | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| `<case-id>` | `<commit/MR/issue/incident/ticket pointer>` | `<cutoff ref>` | direct-pre-fix / parent-observed / reconstructed-from-outcome-subject | eligible-direct / eligible-reconstructed / ineligible-leaky / needs-better-start | `<current skill pointers>` | yes / no / regression-only | `<date/run-id or 未执行>` | `<matched / partial / mismatched / blocked / invalid>` | `<no_skill_gap / task-local / repo-local / jarvis / source-skill / workflow-skill / upstream / defer>` | `<next action>` |

## Queue Rules

- 独立 bugfix/feature execution unit、重复模式或高影响 miss 都可进入 registry；不能要求先知道 failure mode 才登记 feature case。
- Search coverage 记录实际扫描工作；存在 START/oracle 可分离的候选时，必须至少创建一个 `cases/<case-id>/history-replay-case.md`。
- Visible START 必须和 hidden outcome oracle 分离。
- 有 Git 历史时先自动扫描，不默认等客户手工提供 episode。
- 客户指定的一年、两年、全部或自定义范围必须解析为精确边界。范围内 commit 只有在实际 patch/code changes 被读取并登记归属后才算 covered；message、tag 或 `--stat` 不构成 learning coverage。
- 默认 oldest-to-newest，使后续 episode 检验累计 guidance；采用其他方向时记录客户要求或 repo-specific 理由。到达边界后必须在当前 revision 做最终 truth reconciliation。
- 从 source cursor 取下一个未处理 artifact 后，寻找它所属的完整 work episode 并闭环；不得先把整个时间范围分类。Git commit 只是 discovery seed。
- `group_commits` 是 Git episode 的 evidence；`preconsumed_commits` 防止 follow-up/cleanup/test commit 被后续 episode 重复消费。两者都不是 eval 单位。
- 每个 case 固化 cursor seed/after；registry 在推进 `Next Pointer` 前先写入累计 `Calibration Skill Ref` 和 ordered candidate set。后续 episode 不得退回旧 authoritative baseline。
- seed 未到请求边界时必须记录 owner 和可执行 resume entry；full-range 到 boundary 前保持 `in-progress`。
- 只有 Replay eligibility 为 `eligible-direct` / `eligible-reconstructed` 的 case，在 visible/hidden 分离并完成 CLI/isolation checks 后，Status 才能写 `ready-for-replay`。
- canonical eligibility：`eligible-direct`、`eligible-reconstructed`、`ineligible-leaky`、`needs-better-start`；readiness/execution 使用独立 Status 字段。
- 优先写回 repo-local 或 jarvis-local，除非 lesson 是 customer-neutral methodology。
- 现有 guidance 已足够时记录 `no_skill_gap`，不扩展 skill。
