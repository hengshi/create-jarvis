---
name: jarvis-self-improve-skill
description: >
  Company Jarvis self-improvement 方法。读取 jarvis-box 支持的
  agent session、用户纠正和高信号 review trajectory，从 evidence 中修正
  decision model，并把可验证的 durable control 路由到正确 owner。
---

# Company Jarvis Self-Improvement

这是 company Jarvis 的方法论 skill，不是 collector、scheduler、数据库或运行时实现。
session 收集、agent registry、定时触发和运行目录由 jarvis-box install 提供；本 skill
只负责读取已授权证据、还原 decision trajectory、修正逻辑模型、选择 durable owner 和验证结果。

episode 不是学习单元，只是模型证据。真正要学习的是：Agent 用什么实体、所有权、权威来源、状态、转换、不变量和 fallback 做决定。不断追加具体案例规则而不修正错误模型，不算 self-improvement。

## 强制预读

进入此 skill 前，先从当前已加载的 company entry 定位 active company Jarvis root，再读取：

- `references/runtime-governance-quick.md`
- `references/agent-engineering-quality-gate.md`
- `references/minimal-closure-card.md`

涉及写回时加读：

- `references/writeback-governance.md`

涉及 repo-local skill 深度或漂移时，在目标 repo 的 router package 中按需读取：

- `references/skill-depth.md`
- `references/skill-depth.json`
- `evals/evals.json`（只允许 evaluator 在 task 完成后读取 hidden expectations）
- `scripts/audit_skill_depth.py`

如果这些产物不存在，不要假装 self-improve 已闭环。将缺失本身路由为
`upstream-method` 或该 repo 的一次 repository-learning depth upgrade；普通 task
执行期间不得为了当前答案临时生成 oracle。

## START -> WORK -> VERIFY -> END

### START

1. 通过当前 jarvis-box agent registry 发现实际支持的 agent 和可读 evidence root；不要假设固定 transcript 路径。发现命令必须有每个 Agent 的边界超时，并保留已完成的 partial result；卡住本身也是 tool/runtime evidence。
2. 明确本次窗口、仓库/项目范围、agent 范围和 review 状态过滤条件。用户要求 broad/backfill 时，建立完整 ledger，为每个目标 session 标记 `accounted`、`duplicate`、`excluded-with-reason` 或 `blocked`。
3. 区分 session trajectory、用户纠正、reviewed-MR trajectory、history replay case 和外部故障；它们可共同支持模型，但不能互相冒充执行证据。
4. 从当前 authoritative source 解析仓库、默认分支、产品/skill 名称、版本、MR/PR 和 release 状态。旧 transcript、旧 worktree、目录名和记忆不是当前事实；canonical method identity 是 `create-jarvis`。
5. open MR 可以作为未闭合 evidence，但不能当最终 outcome。已合并 MR 先查 repo-local self-improve decision，避免重复学习；没有 decision 时记录缺失的 owner handoff。

### WORK

1. 重建 trajectory：用户可见目标、当时已知事实、Agent 采用的模型、decision points、实际命令/修改、失败、用户纠正、恢复路径和最终结果。摘要只用于导航，结论回到原始 evidence。
2. 聚类的是相同错误决策，不是相似词。为每个 cluster 写出：当前模型、被 evidence 反驳的 assertion、正确模型、影响的入口和如果不修正会重复出现的 failure mode。
3. 给 evidence 标注 model effect：`confirm`、`refine`、`replace`、`remove` 或 `not-evaluated`。重复用户纠正、跨 provider/部署面的同类逃逸、以及 review 连续抓到的同源问题是高权重信号。
4. 按 broken control point 分类：runtime、routing、repo-local execution、upstream method、skill drift、tool/hook、test/review/release gate 或 external one-off。
5. 先选择 intervention，再写 prose。控制强度从高到低：产品状态机/schema、确定性 CLI/script/hook、测试/review/release gate、skill/reference、docs、`no_change`。能机械阻止的错误不得只加提醒。
6. 对每个模型缺口选择唯一 primary home 和 owner。repo execution truth 留在 repo-local；跨客户建设方法属于 `create-jarvis`；Task/Run/Workspace/Agent/Provider/runtime 行为属于 jarvis-box；客户私有事实只留在 Company Jarvis。
7. Review 意见是 evidence，不是命令。逐条判断它是否揭示合同/模型缺口，记录 `accept`、`reject-with-reason` 或 `defer-with-owner`；禁止为了消除评论扩大产品合同。
8. 同一窗口内所有安全、明确且属于当前可写 owner 的改动都应直接完成。不要把可实施修正降级成报告或空 backlog，也不要每个假设推一次分支等待 CI；先在一次性诊断/replay 环境区分根因，再做一次针对性修改。
9. 对 repo-local skill gap，先读取六维 inventory：缺实现 anchor 修 D1；能机械阻止却只有提醒修 D2；claim 超过证据修 D3；只会复述历史答案修 D4；跨仓 owner/交接丢失修 D5；路径、symbol、命令或 provider contract 漂移修 D6。不要用“扩写正文”同时宣称解决六类缺口。

### VERIFY

1. 检查模式是否有至少两个独立 trajectory，或单个足以证明高影响且包含真实 outcome 的完整证据。用户反复纠正同一决策模型可构成多个独立 decision samples。
2. 为旧模型与新模型各选至少一个会给出不同答案的 discriminating case；执行 before/after replay，并选相邻 case 检查过拟合。不能用报告或文案存在替代行为验证。
3. 对机械 control 运行它真正拥有的验证；对 runtime/user-story claim 使用外部触发到最终 owner writeback/cleanup 的完整链路，局部函数测试不能替代。
4. 检查命名、owner、状态和来源只剩一个权威模型。删除或迁移已被替代的词、路径、状态和竞争 guidance；不能让新旧模型同时有效。
5. 若已有 guidance 和 control 已足够，输出 `no_skill_gap`，不扩张 skill。若 evidence 不完整、泄漏或无法隔离，输出 `not-evaluated`，不能据此关闭缺口。
6. self-improve 执行中出现的超时、shell 可移植性、stale worktree、CLI 兼容、权限或恢复失败，重新进入 ledger；不能因它发生在复盘工具里而忽略。
7. repo-local 候选先运行 `audit_skill_depth.py`，再在隔离上下文执行 same-case、adjacent/negative 和 runtime-hidden forward case。task Agent 不得读取 expected route、forbidden route、invariants、proof 或 oracle；评分由外层 evaluator 完成。缺少隔离执行时记录 `prepared-not-executed`。
8. 检查 `skill-depth.json` 的 drift watch：authority path/symbol、生成入口、测试命令、provider boundary 或 fixed revision 发生变化时，重新核对受影响 records；不能因为 package 仍能被发现就判定模型未漂移。

### END

输出一张 decision card：

- evidence window and sources
- session accounting summary
- old model -> corrected model
- model effect and discriminating cases
- failure mode and blast radius
- decision: `no_skill_gap` / `repo-local` / `central-jarvis` / `jarvis-box-runtime` / `upstream-method`
- intervention, primary home and owner
- changed durable artifacts
- before/after, adjacent/negative and forward verification evidence（分别标明 executed 或 prepared）
- six-dimension effect: D1/D2/D3/D4/D5/D6 中实际改变了哪些，哪些保持不变
- unresolved/blocked evidence with owner
- next action

只有证据支持且 owner 明确时才写回。写回后记录路径、验证命令和结果；没有 durable
变化时明确记录 `no_skill_gap`，不要创建空 backlog。broad/backfill 只有在 ledger 全部 accounted、
所有 accepted intervention 已交付或诚实 blocked 时才算完成。

## 边界

- 不复制 jarvis-box 的 collector、scheduler、agent routing、workspace cleanup 或 service lifecycle 实现。
- 不把 raw transcript、reviewer identity、secret、PII、私有机器路径或源代码写入 company Jarvis。
- 不把一次性外部故障或单条未经验证的建议提升为 durable rule。
- 不把另一个客户的主机名、路径、测试身份或部署事实写成公共方法默认值。
- 不用新增抽象、manifest、状态文件或 service owner 掩盖本可由现有模型表达的问题。
- broad backfill / RL 请求必须分片、可恢复，并为每条 session 和候选保留 accounted status。

## Runtime Foundation ownership

Session discovery rules belong to this skill. The generated Company Jarvis owns the versioned maintenance/self-improve jobs and prompts under `runtime-foundation/`; the selected customer Runtime Foundation root owns their installed locks, logs and workspaces. Jarvis Box only supplies Agent selection/lifecycle and the Docker `runtime-job` transport. Do not assume Jarvis Box creates the customer scheduler or run directories.
