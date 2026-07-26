# Repo history calibration prompt

这份 prompt 用于对一个已经有 repo-local skills 的目标仓库做持续历史校准。它抽取的是执行方法，不是要求 agent 创建一个名为 eval loop 的 skill。

```text
请对 <TARGET_REPO> 的 <TIME_RANGE> 历史执行 repo-local skills 校准。目标是让现有 skills 在真实 bugfix/feature episode 上更可靠；history replay 是执行控制循环，不是交付物，也不要创建 “eval-loop skill”。

范围边界：只处理 <TARGET_REPO>，使用 <COMPANY_JARVIS> 和该 repo 当前真实的 repo-local skills。状态和中间 eval artifact 写入 <CALIBRATION_WORKSPACE>；只有经过证据和同 case 复跑验证的 skill delta 才进入目标 skill 的受控写回。

不要先把整个时间范围的 commits 全量语义分类。只建立轻量 cursor，然后重复下面的小循环：

1. 从 cursor 选择下一个未处理 commit 作为 `cursor_before`/seed，立即向前后扩展成最小相关 commit 组。分组证据依次使用：同一 issue/MR key、连续同主题提交、重叠的高信号文件、紧随其后的 cleanup，以及补充测试/验证。记录 `cursor_after`（按遍历顺序从 seed 推进后的下一枚）、group_commits 和非 seed 的 preconsumed_commits；跨非连续提交扩组不能直接跳过中间历史，preconsumed 成员只在以后 encounter 时跳过。遇到 refactor/tests/docs/release/noise 时随 cursor 记录 skip；不要先做全年分类阶段。
2. 从该组最早 parent 和独立 pre-fix artifact 重建当时可见的 START。完整 final commit message、changed files、diff、root cause、修复方向和最终测试属于 hidden oracle。若没有直接 pre-fix artifact，final subject 只能把可独立成立的纯外部症状归一化投影为 `reconstructed-from-outcome-subject`；cause、fix、path 和实现 identifier 一律不能投影。START 与 oracle 无法安全分离时，记录排除理由并继续下一个候选。
3. 冻结 cutoff snapshot，记录本次实际加载的当前 company/repo-local/workflow/source skill refs，在隔离环境里只给 replay agent visible packet、cutoff snapshot 和这些 current skills，让它真实执行原任务及可用验证。
4. 外层协调 agent 再读取 replay 结果和完整 hidden oracle，比较 route/owner、关键证据、fix boundary、行为结果、verification 和 END closure。先用精确枚举归因：`skill_gap`、`instance_fact_gap`、`source_access_environment`、`execution_deviation`、`case_construction_leak` 或 `oracle_limitation`。
5. 只有证据证明存在可复用、可验证且归属明确的 `skill_gap` 时，才调用 skill-creator 修改实际的 primary skill home（通常是 repo-local SKILL.md、一个 focused reference 或验证脚本）的候选副本。若 primary attribution 是 `instance_fact_gap`，只有当前权威来源能独立证明它是稳定事实时，才在同一 calibration snapshot 形成最小 fact correction；不调用 skill-creator，不写入单次历史答案。其他 attribution 不形成 candidate。不要创建 history/eval-loop 方法 skill；没有 durable gap 时明确记录 no_skill_gap 或 defer。
6. 保持同一 visible START、cutoff、allowed sources 和 hidden oracle，用更新后的 skill snapshot 复跑同一 case。只有失败维度改善、原有正确维度无回归且验证成立，才把 candidate 标为 verified。verified candidate 先晋升为 writable calibration snapshot 的累计 baseline，生成新的 `calibration_skill_ref`；下一组必须加载这个累计 ref，而不是重新加载旧 authoritative skills。`no_skill_gap` 保持 baseline 不变。
7. 关闭当前组：保存可回放 case、comparison、decision、candidate diff/rerun 结果，以及 baseline before/after 和 ordered verified candidate set。先持久化新的 `calibration_skill_ref`，再推进 cursor。一个组只有在“verified skill delta / stable-fact correction 已进入累计 baseline”或有证据的 “no update / defer”结论成立后才算闭合。
8. 到达当前 scope 的 completion boundary 后执行交付：如果这是 bootstrap Phase 12，把 ordered verified candidate set 交给 Phase 13；如果这是独立历史校准任务，按每个 primary home 的 owner/审批政策做等价的受控应用。应用后核对 authoritative ref 与累计 baseline 等价，并用最终累计 authoritative snapshot 复跑所有受影响 case，防止后续 candidate 让早期 case 回归。缺审批时返回 needs-approval，不得把只留在 calibration workspace 的 candidate 称为已交付。

如果目标是完整处理 <TIME_RANGE>，cursor 越过时间边界前都继续；上下文或执行预算到达 checkpoint 时持久化 cursor 并返回 in-progress，下一次从该 cursor 继续，不能把暂停写成完成。bootstrap 首次校准可以在至少一个有效组闭合后把剩余范围列入 day-2 continuation，但不能声称整个时间范围已经处理完。

长期产物是被压实的真实 repo-local skills/references/scripts 以及可追溯的校准证据。cursor、`calibration_skill_ref`、ordered candidate set 和大体量 replay trace 可以留在运行期状态；除非目标仓库治理明确要求，不要为了展示 loop 而把它们包装成新 skill 或把所有历史事实提交进 repo。
```
