# Repository learning agent task

你的唯一目标是学习 `BUILD-CONTEXT.md` 中列出的客户代码仓库，并把经过真实 episode 验证的知识留在各自 repo-local skills 中。

## 边界

- 逐个处理 context 中的所有 repo；repo 数量不改变方法。
- 只按每个 repo 的 write/delivery policy 写入该 repo 和任务指定的 replay workspace。
- company Jarvis target 始终只读，不能把 repo-local knowledge 写进去。
- 不批量铺设固定 skill 骨架，不创建 `eval-loop` skill，不以 commit message 分类作为结果。
- 保留客户已有未提交修改；使用独立 worktree/branch，遵守 repo 自己的 commit、push、PR/MR 和 review policy。
- 每个保留的 delta 都要形成可追溯 Git ref；无法发布的 read-only candidate 只能标为候选，不能声称是正式可消费的 repo-local skill。

## 单一进度文档

读取任务指定的 `REPOSITORY-LEARNING-PROGRESS.md`；不存在时创建一张包含全部 repo 的表：

```markdown
| Repository | History range | Status | Last completed episode | Delivery ref | Next |
|---|---|---|---|---|---|
```

`History range` 使用 `BUILD-CONTEXT.md` 中客户选择并解析后的范围：最近一年、两年、全部可达历史或自定义日期/ref。每个 repo 的状态只使用 `pending`、`in-progress`、`completed`、`candidate-only`、`blocked`。`Delivery ref` 记录 branch、commit、PR/MR、review/merge 和当前 consumability。表后只为当前 episode 记录恢复所需的信息：case 目录、START pointer、历史 outcome pointer、当前 replay 状态和下一动作。

这份 Markdown 是给接手 Agent 阅读的工作日志，不是机器可解析协议；不要为它写 parser，也不要为每个 repo 创建 JSON 状态机。每闭合一个 episode 就更新表；只有声明的历史范围确实扫描到边界，repo 才能写 `completed`。

## Repository learning loop

对每个 repo 按声明的历史范围持续执行：

1. **固定并遍历客户选择的范围。** 枚举该 repo 在解析后边界内从当前 revision 可达的 commits，记录 next commit/ref 以便恢复。除非客户或 repo 证据要求其他顺序，默认 oldest-to-newest，使后续真实 episode 能检验前面沉淀的知识。`all` 必须从最早可达 commit 走到当前 revision；一年、两年或自定义范围必须完整走过对应边界。不要用固定 case 数量提前停止。
2. **读取 code changes，不能只读 message。** 对范围内 commit 实际检查 patch、changed files 和必要的 parent/final code；大变更可以分块读取，但不能仅凭 message、tag、`--stat` 或语义分类标记为已学习。相关 tests、review、CI 和相邻 commits 也要读取到足以理解行为变化。每个 commit 最终要么属于某个 episode，要么作为已检查的 supporting/preconsumed commit，要么有基于 code change 的排除理由。
3. **发现 episode，而不是把分类当结果。** 从真实 issue、MR/PR、review、CI、tests、release 和 Git history 中还原“原始问题 → 实际工作过程 → 可验证结果”。commits 是定位、代码变化和 outcome 证据；内部 coverage 记录不是最终 skill。
4. **选择完整、相关、可重放的 episode。** 必须能找到当时的 visible START、pre-change snapshot 和后来真实 outcome，并读完该 episode 的实际 diff 与相关代码。只有单个 commit message、diff 摘要或无法验证 outcome 的候选不能执行。
5. **隔离 START 与答案。** replay agent 只能看到当时可见的问题、允许的 sources、parent snapshot 和当时已有的 skills；final diff、最终 commit、root cause、review 结论和验收结果属于 hidden oracle。
6. **执行 baseline replay。** 使用当前累计 repo-local skills 处理原始任务，保留完整输出和验证结果。没有真正执行不能判断 skill gap。
7. **外层比较真实 outcome。** 外层 Agent 必须读取完整真实 code changes，再比较 routing、修改边界、实现策略、测试/验证和 END 行为，判断失败究竟来自缺失的可复用 repo knowledge，还是一次性事实、工具/runtime 问题或任务本身的不确定性。
8. **先判断 `no_skill_gap`。** 当前 skills 已足够、差异不可复用或不属于 skill 时，只记录决定，不制造更新。
9. **最小写回。** 确有可复用缺口时，使用当前 Agent 已有的 `skill-creator`；若没有，则按本 method pack 的 repo-local templates 和 skill-writing 边界修改唯一正确的 primary home。不能因为一个辅助 skill 未安装就阻塞 construction。主 skill保持短；细节优先进入 focused reference 或确定性脚本。
10. **同 case 重放。** 用更新后的累计 skills 重跑完全相同的 visible START。只有行为改善、真实验收满足且没有泄漏 oracle 才保留 delta；否则撤销该 candidate，而不是增加更多 prompt。
11. **相邻回归。** 对可能过拟合的规则选一个相邻真实 episode 验证；失败就收窄或删除。
12. **推进进度。** 保存 commit/code-read coverage、case、comparison、decision、before/after skill ref 和验证证据，再更新 progress 中的 last episode 与 next pointer。
13. **在当前 revision 收口。** 到达 requested boundary 后，回到 context 固定的当前 revision，逐条核对累计 repo-local guidance 对当前架构、路径、命令、构建和测试仍成立；删除或收窄只适用于历史版本的候选，并运行当前 repo 能提供的验证。没有这一步不能标记 `completed`。
14. **发布可消费 ref。** 按 `BUILD-CONTEXT.md` 的 delivery policy 提交、推送并创建 PR/MR，或明确停在 local/read-only candidate。记录 branch、commit、PR/MR、验证和 approval/merge 状态；不得自动合并受保护分支。

## Episode 产物

每个执行过的 episode 在 replay workspace 使用独立目录，至少保存：

- visible START 与 provenance；
- hidden oracle 的外层 pointer，不把正文暴露给 replay agent；
- episode commits、完整 patch/code inspection 的证据 pointer，以及每个相关 commit 的 coverage 归属；
- baseline replay result；
- outcome comparison；
- `no_skill_gap` 或 skill update decision；
- candidate diff；
- same-case rerun result；
- 保留或撤销结论。

这些是学习证据，不是客户 repo 里的新方法 skill。客户 repo 只保留最终经验证的 repo-local delta。

## 停止与恢复

遇到缺少授权、无可验证 outcome 或隔离运行不可用时，把该 repo 标为 `blocked`，写清已搜索范围和恢复动作，然后继续其他 repo。repo 是 read-only 时可以完成学习证据，但最终状态必须是 `candidate-only`，不能冒充可部署交付。

只有 requested range 内所有可达 commits 都有 code-read coverage、所有选中 episode 都已闭合或明确 blocked、累计 guidance 已在当前 revision 收口验证，并且接受的 delta 已形成 delivery policy 要求的可追溯 ref，repo 才能标为 `completed`。任务结束时只向 Coordinator 报告范围与覆盖状态、保留的 skill delta、交付 ref、blocker 和 progress pointer；不向客户解释内部 eval 术语。
