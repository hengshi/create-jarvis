# Phase 10 - 交付确认检查点

目标：给服务负责人、客户 owner 和后续 phase 一份共同事实表，并在同一次 runtime-agent invocation 中立即进入 Phase 11。Phase 10 不是 bootstrap 终点。

Phase 10 的核心职责是审计 Phase 6-9 的语义就绪状态，不是重复文件数量。以下任一情况发现时，必须将工作发回所属 phase：

- 可访问的 source route 仍为泛化状态
- repo-local package 为泛化模板
- 模块身份未解决
- reference 链接断开
- 仅靠间接证据标为 `included` 的模块

Phase 10 完成时：

- `bootstrap-result.json.status` 和 `bootstrap-state.json.status` 保持 `in-progress`；
- Phase 3-10 为 `completed`，Phase 11-14 仍为 `pending`；
- `bootstrap-state.json.phase` 切到 `phase-11-shadow-pilot`；
- `next_action` 是立即执行 Phase 11，不是让用户以后提供 artifact；
- 不输出最终 Bootstrap Complete 总结，不返回 jarvis-box。

只有进入 Phase 11 并实际执行其 artifact 搜索后，Phase 11 才可能根据自己的停止条件写 `needs-input` / `blocked`。

## 内容

- 完成了什么。
- 没完成什么。
- 哪些是 confirmed facts。
- 哪些需要 owner confirmation。
- identity reconciliation：company identity、confirmed product identity、source-detected identities、conflicts 和 owner confirmation 状态。
- 哪些进入 backlog。
- blockers、warnings、missing inputs。
- first workflow 和影子试跑计划。
- writeback policy。
- runtime link paths。
- 第二天运营 owner/action。
- `bootstrap-result.json` 的 runtime contract 字段：
  - 顶层必须包含 `schema_version`、`status`、`summary`、`paths`、`created_files`、`updated_files`、`preserved_files`、`missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions`、`next_action`、`phase_summary`、`generated_at`。
  - `paths` 至少包含 `jarvis_home`、`jarvis_target_home`、`entry_skill` 三个字符串字段；`jarvis_target_home` 不能因为等于 `jarvis_home` 而省略。
  - `paths` 只能是 string map；每个 value 必须是字符串路径或字符串值，不能放数组、对象或表格。
  - `created_files`、`updated_files`、`preserved_files` 只能是字符串数组；repo-local skill 目录如果有多个路径，也写成多个字符串条目。
  - `missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions` 必须是字符串数组。
  - 只要 `missing_inputs`、`blockers` 或 `conflicting_inputs` 非空，`status` 就不能是 `completed`。
  - 只要 `identity_reconciliation.status` 不是 `confirmed`，`status` 就不能是 `completed`。
  - 详细结构化解释放在 onboarding report、rollout checklist 或 phase report，不放进 runtime contract。
- `bootstrap-state.json` 的 resume contract 字段：
  - 顶层必须包含 `schema_version`、`phase`、`status`、`paths`、`inputs`、`confirmed_answers`、`identity_reconciliation`、`method_repo`、`phase_status`。
  - `paths` 至少包含 `jarvis_home`、`jarvis_target_home`、`jarvis_box_home`、`entry_skill`。
  - `inputs.company_slug` 必须逐字等于 `JARVIS_COMPANY_SLUG`。
  - `phase_status` 使用 `phase-03-bootstrap-invocation` 到 `phase-14-day2-operation` 的完整 phase key；不要只写 `phase_3` 这种简写。
  - 可以额外写 `bootstrap`、`env`、`normalized` 等嵌套字段，但不能用这些嵌套字段替代上述顶层字段。

## 输出

- onboarding report。
- 更新后的 `rollout-confirmation-checklist.md`。
- `bootstrap-result.json` checkpoint status（`in-progress`）。
- 更新后的 `bootstrap-state.json` resume state。

## 禁止

- 不把机器防呆通过写成 bootstrap 完成。
- 不把 Phase 10 onboarding report 写成 Bootstrap Complete，也不预判 Phase 11-14 为 `needs-input`。
- 不在 Phase 10 返回 runtime-agent 最终回答；完成检查点后立即进入 Phase 11。
- 不把目录和占位符写成真实 company Jarvis。
- 不隐藏 unresolved fields。
- 不把 source-detected identity 写成已确认的客户 company identity。
- 不把服务负责人自己的判断写成客户确认事实。
- 不把对象、表格或嵌套结构塞进 `bootstrap-result.json.blockers` 等 runtime list 字段。
- 不在 `bootstrap-result.json.paths` 里放数组或对象；`paths.repo_local_skills: [...]` 是错误写法，应改为 `created_files` 中的多条字符串或 report 文件中的表格。
- 不省略 `bootstrap-result.json.summary` 或 `paths.jarvis_target_home`。
- 不把 `bootstrap-state.json.method_repo`、`phase`、`paths`、`confirmed_answers` 只写在嵌套对象里。
