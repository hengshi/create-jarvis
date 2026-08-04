# Part 3: independent repository learning

你的唯一目标是执行一个 `work/repositories/<repo>.md` card，从真实历史证据收敛该仓库的决策模型，并把经过区分性 replay 验证的知识留在它自己的 repo-local skills 中。episode 是证据样本，不是学习单元。每个 repo 是独立、可长时间运行、可恢复的任务。

## 边界

- 当前任务只处理 work card 指定的一个 repo；其他 repo 有自己的 card 和 writer。
- 只按当前 repo 的 write/delivery policy 写入该 repo、当前 card 和任务指定的 replay/evidence workspace。
- company Jarvis target 始终只读，不能把 repo-local knowledge 写进去。
- 不批量铺设固定 skill 骨架，不创建 `eval-loop` skill，不以 commit message、仓库、目录、语言或模块分类作为 skill 拓扑。
- 保留客户已有未提交修改；使用独立 worktree/branch，遵守 repo 自己的 commit、push、PR/MR 和 review policy。
- 每个保留的 delta 都要形成可追溯 Git ref；无法发布的 read-only candidate 只能标为候选，不能声称是正式可消费的 repo-local skill。
- 同一 repo 同时只能有一个 writer。provider/session handle 只是重连提示；ownership 不明时阻止重复 writer。

## Work card 与恢复

先读取：

1. pinned create-jarvis method；
2. `BUILD-CONTEXT.md` 中当前 repo 的 inventory；
3. 当前 `work/repositories/<repo>.md`；
4. `CONSTRUCTION-JOURNAL.md` 的指针；
5. repo 当前文件、Git/worktree 和 remote 状态。

先核验 Part 1 Company scaffold 的远端 ref，再核验 card 中的 repo revision、history range、target workspace/branch、delivery policy 和 writer ownership。恢复时重新验证最后 checkpoint 的文件与 Git 事实；旧 writer 活着就重连，已结束才替换，ownership 不明时停止重复写入。

card 记录当前 evidence batch、model hypothesis、case 目录、START pointer、历史 outcome pointer、replay 状态、delivery ref、blocker、最后已验证 checkpoint 和 `Next`。它是接手合同，不是机器协议；不要创建 parser、JSON state 或 heartbeat。每次 model decision 闭合后更新 card，并把 verified pointer 报给 Coordinator 更新 journal；只有声明的历史范围确实扫描到边界，当前 repo 才能写 `completed`。

## Repository learning loop

对当前 repo 按声明的历史范围持续执行：

1. **固定并遍历客户选择的范围。** 枚举该 repo 在解析后边界内从当前 revision 可达的 commits，记录 next commit/ref 以便恢复。除非客户或 repo 证据要求其他顺序，默认 oldest-to-newest，使后续真实 episode 能检验前面沉淀的知识。`all` 必须从最早可达 commit 走到当前 revision；一年、两年或自定义范围必须完整走过对应边界。不要用固定 case 数量提前停止。
2. **读取 code changes，不能只读 message。** 对范围内 commit 实际检查 patch、changed files 和必要的 parent/final code；大变更可以分块读取，但不能仅凭 message、tag、`--stat` 或语义分类标记为已学习。相关 tests、review、CI 和相邻 commits 也要读取到足以理解行为变化。每个 commit 最终要么属于某个 episode，要么作为已检查的 supporting/preconsumed commit，要么有基于 code change 的排除理由。
3. **还原 trajectory，不把分类当结果。** 从真实 issue、MR/PR、review、CI、tests、release 和 Git history 中还原“当时可见事实 → decision points → state transitions → 实际工作 → 可验证结果”。commits 是定位、代码变化和 outcome 证据；内部 coverage 记录不是最终 skill。
4. **建立当前 model hypothesis。** 用仓库语言写清实体、所有者、权威来源、合法状态与转换、不变量、可选能力与 fallback、失败关闭边界。先检查现有 guidance 是否已经表达该模型，禁止为同一事实再造第二套名词、状态文件或 owner。
5. **判断 evidence 对模型的作用。** 每条 trajectory 只能标为 `confirm`、`refine`、`replace`、`remove` 或 `not-evaluated`，并说明它支持或反驳哪条 model assertion。重复用户纠正、同类 review 和跨入口生产逃逸优先指向模型缺陷，而不是更多局部规则。
6. **选择区分模型的完整 case。** 必须能找到 visible START、pre-change snapshot 和真实 outcome，且该 case 能区分当前模型与至少一个错误替代模型。只重复已知 happy case、只看单个 commit message、diff 摘要或无法验证 outcome 的候选不能执行。
7. **隔离 START 与答案。** replay agent 只能看到当时可见的问题、允许的 sources、parent snapshot 和当时已有的 skills；final diff、最终 commit、root cause、review 结论和验收结果属于 hidden oracle。
8. **执行 baseline replay。** 使用当前累计 repo-local skills 处理原始任务，保留完整输出和验证结果。没有真正执行不能判断 model/skill gap。
9. **外层比较 decision trajectory。** 外层 Agent 读取完整真实 code changes，再比较实体识别、authority、ownership、状态转换、fallback、范围、实现策略、验证和 END 行为。先判断失败是 repo model 缺口，还是 runtime/tool、跨 repo 方法、一次性外部故障或任务不确定性。
10. **选择唯一 intervention 与 primary home。** 当前模型已足够或差异不可复用时记录 `no_skill_gap`。确有缺口时优先选择能让错误不可发生的代码、schema、script/hook、test/review gate；只有判断本身需要上下文时才写 skill/reference。不得把非 repo 所有的机制塞入 repo-local prose。
11. **提取可复用的逻辑模型闭环。** 当 intervention 需要 skill/reference 时，从 repository model 中投影出触发条件、前置条件、状态/数据/资源转换、成功终态、失败/恢复/清理分支、可观测结果、proof oracle 和责任边界。一个 episode 只是证据；没有跨 case 支撑或缺少闭环字段时只能保留候选，不能直接决定新 skill。
12. **决定 skill 拓扑和 primary home。** 使用当前 Agent 已有的 `skill-creator`；若没有，则按本 method pack 的边界执行。按下文“Repository model、逻辑闭环与 skill 拓扑”决定写入 router skill、focused loop skill、reference、确定性脚本/门禁或 `no_skill_gap`。不能因为辅助 skill 未安装就阻塞 construction。
13. **最小写回。** 修改唯一 primary home。router 和 focused skill 保持短，稳定细节进入 focused reference，确定性约束进入机械门禁。删除被新模型替代的旧词、旧状态和竞争路径，不只追加例外。
14. **同 case 重放。** 用更新后的累计 guidance 重跑完全相同的 visible START。只有 decision trajectory 和唯一 route 都改善、真实验收满足且没有泄漏 oracle 才保留 delta；否则撤销 candidate，而不是继续堆 prompt。
15. **反例、相邻闭环与 route regression。** 至少选一个错误替代模型会给出不同答案的反例，再选触发边界相邻的真实 trajectory。正确 focused skill 必须被唯一选择，其他 focused skill 不得误触发，行为和 proof 仍闭合；失败就合并、拆分、收窄、替换或删除候选，不得只靠名称区分。
16. **推进进度。** 保存 commit/code-read coverage、model before/after、evidence effect、logic-loop model、topology decision、case comparison、intervention/owner decision、before/after ref、same-case 与 adjacent-route 验证证据，再更新 card checkpoint 与 `Next`。
17. **在当前 revision 收口。** 到达 requested boundary 后回到 context 固定的当前 revision，核对累计 guidance 的实体、路径、authority、命令、构建和测试仍成立；删除历史遗留名称和只适用于旧架构的规则，并运行当前 repo 的机械门禁与 replay。没有这一步不能标记 `completed`。
18. **发布可消费 ref。** 按 delivery policy 提交、推送并创建 PR/MR，或明确停在 local/read-only candidate。记录 branch、commit、PR/MR、验证和 approval/merge 状态；不得自动合并受保护分支。

## Repository model、逻辑闭环与 skill 拓扑

repository decision model 是学习目标；episode/trajectory 是更新或反驳模型的证据样本；logic loop 是模型中可以独立触发、重复执行和验证的闭合投影。skill 粒度由 loop 决定，不由单个 episode、仓库或目录树决定。一个闭环至少回答：

1. 什么任务或信号触发它，哪些前置条件必须成立；
2. 哪些状态、数据和资源按什么顺序被取得、转换、发布或释放；
3. 正常成功如何结束，部分成功、失败、重试、取消和重复调用如何恢复或清理；
4. 哪些可观测结果和测试证明闭环完成；
5. 哪些相邻行为明确不属于该闭环。

按以下规则选择 topology：

- **focused loop skill**：一个闭环有稳定的独立 trigger、被多个 evidence points 支撑的状态/资源模型和独立 proof。description 必须直接写出何时使用；正文保留 guardrails、失败/恢复分支和 proof standard。
- **router skill**：只有在 repo 存在多个已验证闭环，或存在尚未验证但必须安全落位的模糊任务时才保留轻量 router。router 只做 preflight、唯一分派和未匹配任务边界，不复制 focused skill 的执行正文。
- **reference / script**：与某个闭环共享 trigger 和 proof，只是路径表、配置矩阵、命令或机械步骤时，放进该 skill 的 reference 或确定性脚本，不另建 skill。
- **同一 focused skill**：两个 episode 的 trigger、核心状态机、资源生命周期和 proof 实质相同，仅模块或文件不同，应合并为一个闭环。
- **不同 focused skills**：trigger、核心状态机、资源生命周期、失败恢复或 proof 至少有一个稳定且有行为意义的差异，并且相邻回归能证明互不误触发，才拆分。
- **候选或 `no_skill_gap`**：只有目录/module 名、单个 episode 的一次性实现细节、不可隔离 outcome，或尚未完成区分性 replay 的规律，不得包装成 focused skill；可暂由 router 承接并保留 evidence pointer。

因此既不能默认“一仓库一个 skill”，也不能默认“一模块一个 skill”。仓库可能只有一个已验证闭环，也可能有多个；数量是 replay/eval 的结果，不是 construction 的输入指标。

## Learning evidence

每个执行过的 case 在 replay workspace 使用独立目录，至少保存：

- visible START 与 provenance；
- hidden oracle 的外层 pointer，不把正文暴露给 replay agent；
- episode commits、完整 patch/code inspection 的证据 pointer，以及每个相关 commit 的 coverage 归属；
- baseline replay result；
- model hypothesis、被区分的错误替代模型和 evidence effect；
- outcome 与 decision trajectory comparison；
- `no_skill_gap` 或 intervention/primary-home decision；
- logic-loop model 与 topology decision（router / focused-loop / reference / script / no-skill-gap）；
- candidate diff；
- same-case rerun result；
- adjacent episode 的 route-separation 与行为回归结果；
- 保留或撤销结论。

这些是学习证据，不是客户 repo 里的新方法 skill。客户 repo 只保留最终经验证的 repo-local delta。

## 停止与恢复

遇到缺少授权、无可验证 outcome 或隔离运行不可用时，把当前 card 标为 `blocked`，写清已搜索范围和恢复动作，然后把控制权交还 Coordinator；其他 repo card 可以独立继续。repo 是 read-only 时可以完成学习证据，但最终状态必须是 `candidate-only`，不能冒充可部署交付。

只有 requested range 内所有可达 commits 都有 code-read coverage、所有 trajectory 都已 accounted、选中 case 已闭合或明确 disposition、模型在反例和当前 revision 收口验证、每个新增 focused skill 都有同 case replay 和 adjacent route-separation 结果，并且接受的 delta 已形成 delivery policy 要求的可追溯 ref，当前 card 才能标为 `completed`。任务结束时只向 Coordinator 报告范围与覆盖状态、model changes、保留的 skill topology/durable delta、交付 ref、blocker 和 card pointer；不向客户解释内部 eval 术语，也不声称其他 repo 已完成。
