# Part 3: independent repository learning

你的唯一目标是执行一个 `work/repositories/<repo>.md` card：完整学习该客户代码仓库在客户授权范围内的当前实现和真实历史，把足以改善未来工程行为的仓库知识写入可消费的 repo-local skills，并按 delivery policy 交付。每个 repo 是独立、可长时间运行、可恢复的任务。

这里的“完整学习”包含两个同等重要、不能互相替代的结果：

1. **coverage completeness**：仓库当前仍有效的主要任务族、能力面、构建/测试/生成/发布入口和高风险横切约束都有明确 disposition，不能因为没有挑中 replay case 就静默丢失；
2. **behavioral correctness**：写入 skill 的工作流、状态转换、失败恢复、责任边界和 proof 与当前代码及历史 outcome 一致，高风险规则经过足够强的 replay/回归验证。

不要把“读完所有 commits”误当成“知识已经覆盖”，也不要把“只有少量 replay 通过”误当成“仓库只有少量值得保留的 skills”。history coverage、knowledge coverage 和 behavioral validation 是三张不同的账，必须分别闭合。

## 核心术语与不可混淆的学习对象

- **repository decision model**：仓库当前有效的实体、所有者、权威来源、合法状态和转换、不变量、可选能力/fallback、构建与验证方法、失败关闭边界及跨 repo 责任边界。它是学习目标。
- **task family / capability surface**：用户或工程 Agent 会独立提出的一类稳定任务，例如“修改产品配置并保持迁移兼容”“新增设备变体”“生成插件接口”“排查显示管线”“导出审计记录”。它必须能用真实 trigger、owner、入口和 proof 描述，不能只是目录名。
- **trajectory / episode**：从当时可见问题到真实 outcome 的历史证据样本。它用于确认、修正或反驳 repository model，不等于一个 skill。
- **logic loop**：task family 中可重复执行和验证的闭合行为投影，覆盖 trigger、前置条件、状态/数据/资源转换、成功终态、失败/恢复/清理、可观测结果和责任边界。
- **skill topology**：router、capability skill、focused loop skill、cross-cutting skill、reference、script/gate 与 `no-skill` disposition 的组合。拓扑由知识覆盖和独立触发边界共同决定，不由预设数量决定。
- **primary home**：一条知识的唯一权威写入位置。唯一 primary home 用于防止重复和冲突，不表示整个仓库只能有一个或很少的 skills。

## 边界与安全约束

- 当前任务只处理 work card 指定的一个 repo；其他 repo 有自己的 card 和 writer。
- 只按当前 repo 的 write/delivery policy 写入该 repo、当前 card 和任务指定的 replay/evidence workspace。
- Company Jarvis target 在 Repository learning 阶段始终只读；repo-local execution truth 不写入 Company repo，等 Reconciliation Gate 再接线。
- 保留客户已有未提交修改；使用独立 worktree/branch，遵守 repo 自己的 commit、push、PR/MR 和 review policy。
- 同一 repo 同时只能有一个 writer。provider/session handle 只是重连提示；ownership 不明时阻止重复 writer。
- 每个保留的 delta 都要形成可追溯 Git ref；无法发布的 read-only candidate 只能标为候选，不能声称为正式可消费的 repo-local skill。
- 不创建 `eval-loop`、`history-scan`、`commit-category` 等只描述学习过程的客户 skill。学习证据留在 evidence workspace，客户 repo 只保留未来执行任务需要的知识。
- 不按固定数量批量铺设空 skill，也不允许用“一仓库一个 skill”压扁多个独立任务族。
- commit message、目录、语言、模块和文件扩展名都只能是发现线索，不能单独决定 skill。但模块/子系统如果同时拥有稳定任务 trigger、authority、工作流和 proof，可以成为合理的 capability boundary。

## Work card、恢复与开始前核验

开始或恢复时依次读取并核验：

1. pinned create-jarvis method 的 exact commit；
2. `BUILD-CONTEXT.md` 中当前 repo 的 canonical remote、revision、history range、write/delivery policy 和授权边界；
3. 当前 `work/repositories/<repo>.md`；
4. `CONSTRUCTION-JOURNAL.md` 的当前 pointer、前序 Company delivery ref 和 writer 状态；
5. repo 的 `AGENTS.md`、`CLAUDE.md`、已有 skills、Git/worktree、remote/default branch、dirty state；
6. 已存在的 coverage ledger、repository model、case/evidence 和最后 delivery ref。

先确认 Part 1 Company scaffold 的远端 ref 仍可解析，再确认 card 记录的 repo revision 和 history boundary 没有漂移。恢复时重新验证最后 checkpoint 的文件与 Git 事实：旧 writer 活着就重连；已结束才能替换；无法判断 ownership 时停止重复写入。

card 至少记录：固定 revision、history range、history cursor、coverage ledger pointer、repository model pointer、当前 validation batch/case、target worktree/branch、delivery ref、blocker、最后已验证 checkpoint 和 `Next`。card 是给接手 Agent 的恢复合同，不要创建额外 parser、JSON 状态机或 heartbeat。

## 总体执行顺序

严格按以下阶段推进。可以在长任务中交替增量更新 ledger 和 model，但不能跳过 Phase B 的全仓能力覆盖盘点，直接从少量 replay cases 决定最终 skill 拓扑。

### Phase A：固定范围并完整读取历史与当前状态

1. 解析并记录 fixed current revision、default branch 和 requested history boundary。
2. 枚举从 fixed revision 可达且位于授权范围内的全部 commits。默认 oldest-to-newest；`all` 必须从最早可达 commit 到 fixed revision，不能用固定 case 数量提前停止。
3. 对每个 commit 实际读取 patch、changed files 和理解变化所需的 parent/final code。大 patch 可以分块，但不能只读 message、tag、`--stat` 或文件名。
4. 读取关联 tests、issue、MR/PR、review、CI、release notes 和相邻 commits，直到能判断变化的行为、owner、验证状态和当前有效性。
5. 每个 commit 必须落入以下一种 coverage disposition：
   - 某个 task family / capability 的 evidence；
   - 某个 trajectory/episode 的 seed 或 supporting evidence；
   - 已被其他 evidence batch 预消费；
   - 基于实际 code change 的明确排除理由。
6. 回到 fixed current revision，读取当前目录结构、公开 API、构建入口、生成器、配置、测试、发布/打包入口、运行时入口、观测/诊断和安全相关 surface。历史已经删除或更名的路径不能直接写入当前 skill。

Phase A 的完成只说明 history/code-read coverage 闭合，不说明 knowledge coverage 或 skills 已完成。

### Phase B：先建立 capability coverage ledger，再选择 cases

在任何最终 topology 决定前，创建或更新一个可恢复的 capability coverage ledger。推荐使用 `templates/replay/repository-capability-coverage.md`。至少盘点以下类别；不存在时写 `not-present + evidence`，不能默默跳过：

- build、dependency、toolchain、code generation、format/lint/test、package/release；
- 主要 runtime/service/library entrypoints 与公开 API；
- 主要 domain state machines、data flows、resource lifecycles 和 provider/plugin boundaries；
- configuration、persistence、migration、product/platform/device variants；
- concurrency、callback、timer、queue、retry、cancellation、startup/shutdown；
- security、identity、permissions、sensitive data；
- observability、logging、metrics、crash/support diagnostics；
- compatibility、generated ABI/schema、cross-repo consumer/provider contracts；
- 仓库特有且在历史中反复出现的用户任务族。

ledger 中每个 task family 至少记录：

| 字段 | 必须回答的问题 |
|---|---|
| ID / verb-led name | Agent 将执行什么稳定动作，而不是目录叫什么？ |
| trigger examples | 用户、issue、CI 或代码信号在什么情况下应命中它？ |
| owner / authority | 哪个模型、配置、schema、controller、provider 或 build file 是权威？ |
| current entrypoints | fixed revision 上应先读哪些路径、symbol、command、test？ |
| historical evidence | 哪些实际 patches/episodes 支撑这个模型？ |
| loop/risk model | 有哪些状态、资源、失败恢复或横切不变量？ |
| validation level | 当前达到 L0/L1/L2/L3 中哪一级？证据 pointer 是什么？ |
| topology disposition | router / capability-skill / focused-loop / cross-cutting / reference / script-gate / no-skill / candidate？ |
| rationale | 为什么独立、合并、降级或不写 skill？ |
| current-state reconciliation | 路径、命令、行为在 fixed revision 是否仍成立？ |

发现 candidate task family 的充分线索包括但不限于：

- 当前公开 API、用户可见功能、构建/发布入口或运维任务有独立请求方式；
- 多个历史 changes 指向同一 owner、状态机、数据流或验证方法；
- 一个小模块虽 commit 少，但承担安全、兼容、身份、持久化或生成 ABI 等高 blast-radius 责任；
- 多个目录共同完成同一个端到端任务，应合并为一个 task family；
- 同一目录承载多个 trigger、状态机或 proof，应拆成多个 task families；
- 当前测试或脚本定义了稳定、可重复的操作，即使没有适合隔离的历史 issue，也可能形成 capability skill。

禁止以下 shortcut：

- 只把选中的 replay cases 写进 ledger；
- 只统计 commit 数量或目录大小；
- 因为某能力没有 issue 链接就直接丢弃；
- 用 router 中的一行模糊描述替代本应独立可发现的稳定 task family；
- 为凑数量把每个目录都变成 skill；
- 把所有横切约束都做成会与每个 capability 同时触发的泛化 skill。

Phase B 必须让每个主要当前 task family 都有 disposition。`candidate` 可以存在，但必须说明缺失证据和下一步；高影响能力不能在没有理由的情况下全部停留为 candidate。

### Phase C：收敛 repository decision model

1. 用仓库自己的语言记录实体、owner、authority、合法状态/转换、不变量、optional capability/fallback、失败关闭边界、build/test/release 方法和跨 repo 边界。
2. 从真实 issue、MR/PR、review、CI、tests、release 和 Git history 还原 trajectory：当时可见事实 → decision points → state/data/resource transitions → actual work → observable outcome。
3. 每条 evidence 对 model assertion 标记为 `confirm`、`refine`、`replace`、`remove` 或 `not-evaluated`。
4. 重复用户纠正、同类 review、跨入口生产逃逸和反复回滚优先指向模型缺陷；不要不断追加互相竞争的局部例外。
5. repository model 是跨 cases 累积的。一个 case 可以证明某个 assertion，但不能独占整个 task family 的定义。

### Phase D：按风险选择验证等级

不要再把“完整历史 replay”设为所有有用 skill 的唯一准入条件。采用以下分级，并诚实记录证据：

- **L0 discovered**：只发现 candidate，尚未验证当前路径、命令或行为。只能留在 ledger/router unmatched boundary，不能写成正式执行结论。
- **L1 current-state verified**：在 fixed revision 核对 authority、路径、symbols、命令、测试/生成器和可观测结果；运行可用的静态/结构/单测/build probe。适合稳定 build/config/API/task-family guidance。L1 不是高风险生命周期规则的充分证明。
- **L2 historical outcome/replay verified**：找到完整 visible START、pre-change snapshot 和真实 outcome，读取实际 diff/code/test，隔离 hidden oracle，执行 baseline 与 same-case rerun，证明 guidance 改善行为。适合状态机、并发、重试、迁移、资源生命周期和历史高频陷阱。
- **L3 route/negative/forward verified**：增加相邻 trigger route separation、错误替代模型反例、负例或当前 revision forward test，证明不误触发且没有只记住一个历史答案。对高风险且与相邻 skill 重叠的规则、拆分新 focused skill、或可能泄漏 oracle 的规则必须达到 L3。

晋升规则：

- 一个稳定、独立触发、有当前 authority/entrypoint/workflow/proof 的 capability task family，可以在 L1 后形成 capability skill；不要求凭空制造历史 incident。
- 涉及并发、身份/密钥、持久化迁移、幂等、状态机、startup/shutdown、跨进程资源或失败恢复的核心行为，通常至少需要 L2；若与相邻 route 易混淆则需要 L3。
- 历史 evidence 丰富但当前实现已删除的规律不能晋升；可记录为 retired/no-skill。
- 只有单个一次性实现细节、没有独立 trigger、没有当前 proof 或通用模型已经足够时，放入现有 reference、任务本地证据或 `no-skill`。
- validation level 决定 claim 强度，不决定是否强行把所有内容合并进 router。

#### L2/L3 replay 的完整要求

1. 选择能区分当前模型与至少一个错误替代模型的完整 case；只重复 happy case 不够。
2. replay agent 只能看到 cutoff 当时可见问题、允许 sources、pre-change snapshot 和当时已有 skills；final diff、root cause、review 结论和验收结果属于 hidden oracle。
3. 先执行 baseline；没有真正执行就不能判断 skill/model gap。
4. 外层 Agent 完整读取真实 code changes，比较 owner、authority、状态转换、fallback、scope、implementation、verification 和 END behavior。
5. 先判断失败属于 repo model/skill gap，还是 runtime/tool、一次性外部事实、跨 repo 方法或 case construction 泄漏。
6. candidate 更新后重放相同 visible START。只有行为改善、真实验收满足且没有泄漏 oracle 才保留。
7. 需要 L3 时，使用相邻真实 trajectory 或独立负例验证 route separation 和行为泛化；失败时合并、拆分、收窄、替换或删除候选。

### Phase E：决定 skill topology

先看完整 capability ledger，再逐项选择 primary home。允许的 topology 类型如下：

#### Router skill

- 当 repo 有多个独立 task families，或用户任务经常先以模糊症状到达时保留一个轻量 router。
- router 负责 repo preflight、task-family 路由、跨 repo owner 边界和 unmatched/candidate 处理。
- router 必须列出所有已交付 repo-local skill，并给出互斥或有优先级的 trigger；不能只列两个 replay cases 而遗漏其他已验证能力。
- router 不能复制所有 focused skill 正文，也不能成为“其余知识垃圾桶”。

#### Capability skill

- 用于稳定、可独立请求的工程任务族，至少达到 L1。
- description 写清实际用户任务、artifact/symbol/command 信号和何时使用。
- 正文包含 owner/authority、入口选择、核心 workflow、重要边界和 proof；详细路径矩阵、历史模式和命令放 references。
- capability skill 可以覆盖多个目录，也可以对应一个有明确责任的模块；判断依据是 trigger-to-proof 闭环，不是目录配额。

#### Focused loop skill

- 用于有独立 trigger、状态/资源生命周期、失败恢复和独立 proof 的高风险闭环，通常达到 L2/L3。
- 正文必须明确 trigger、preconditions、ordered transitions、success state、failure/recovery/retry/idempotence、guardrails、proof 和 excluded adjacent behavior。
- 一个 historical episode 只是 evidence，不能把 issue 号、commit 答案或一次性 patch 写成通用 skill。

#### Cross-cutting skill 或 reference

- concurrency、device variants、security、compatibility 等横切知识只有在用户会独立请求它、且有独立 proof 时才做 skill。
- 如果它主要约束若干 capability workflows，就作为这些 skills 直接链接的 reference/checklist，或由 router 明确要求在相应条件下共同加载。
- 不要创建 description 宽到几乎所有任务都会触发的横切 skill。

#### Reference / script / mechanical gate

- 与某个 skill 共享 trigger，只是路径表、schema、配置矩阵、历史模式、命令或详细例子时放 reference。
- 重复且确定性的生成、校验、迁移、格式化或安全检查优先写 script/hook/test/gate，并实际运行验证。
- reference 必须由 SKILL.md 直接链接并写明何时读取；不要深层嵌套或复制同一事实。

#### `no-skill` / candidate

- `no-skill` 必须有具体理由：当前通用模型已覆盖、一次性事实、已删除能力、缺少独立 trigger、应由代码/schema/gate 所有，或不属于当前 repo。
- `candidate` 必须写缺失的 validation、影响范围和下一 proof；不能成为永久忽略主要能力的借口。

#### 合并与拆分判断

两个 candidate 在以下维度实质相同时优先合并：用户 trigger、owner/authority、核心 state/data/resource model、工作顺序、failure recovery 和 proof。仅文件或产品变体不同通常不足以拆分。

以下任一维度存在稳定且有行为意义的差异时可以拆分：

- 用户会用不同语言独立请求；
- authority/owner 和第一执行入口不同；
- 状态机或资源生命周期不同；
- 失败恢复、兼容/安全边界不同；
- 验证命令和 success oracle 不同；
- 同时加载会带来明显无关上下文或误路由。

不要预设“一模块一个 skill”“一仓库一个 skill”或“每仓固定 N 个 skills”。最终数量是完整 coverage ledger、trigger independence、proof 和 context cost 共同作用的结果。

### Phase F：按 progressive disclosure 写入

使用当前 Agent 已有的 `skill-creator`；若不可用，则遵循本 method pack 的 skill 边界。每个 skill：

1. folder/name 使用简短、verb-led、仓库命名空间明确的 kebab-case；
2. frontmatter 只保留 `name` 和 `description`；description 是主要触发器，必须同时说明“做什么”和“何时使用”，包含用户语言与关键 artifact/signal；
3. SKILL.md 保留执行所需的 owner、workflow、guardrails、失败行为和 proof，不写学习过程报告；
4. detailed path maps、configuration/product matrices、historical pitfalls、search patterns 和长命令进入一层 `references/`；
5. 机械、易错、重复操作进入 `scripts/`，并实际运行；
6. 生成或更新 `agents/openai.yaml`，确保 UI metadata 与 SKILL.md 一致；
7. router 直接链接所有交付 skills/references，并说明相邻 route 如何区分；
8. 删除过时路径、竞争性旧规则和重复内容，不只追加新段落。

**“最小写回”的唯一正确解释**：每条知识只写到最合适的 primary home，skill body 只保留执行所需内容，细节按需加载，避免重复和无关上下文。它绝不意味着减少 task-family 覆盖、把多个独立 trigger 强塞进一个 router、或只为少数 replay cases 建 skill。

### Phase G：验证、覆盖收口与交付

对最终累计 topology 执行：

1. 对每个 skill 运行 `skill-creator` `quick_validate.py` 或等价 validator；检查 metadata、links、scripts 和 references。
2. 对每个 L1 skill 在 fixed revision 重跑记录的 path/symbol/command/test/build/generator checks。
3. 对每个 L2/L3 skill保存 same-case、oracle comparison、negative/adjacent route 和当前 revision reconciliation evidence。
4. 做 route matrix：使用代表性用户请求验证唯一主 skill、必要共同加载的横切 reference、以及不应触发的相邻 skills。
5. 回看 capability coverage ledger，确认每个主要当前 task family 都有 disposition；不得用“history fully read”替代这一步。
6. 检查欠生成：是否有当前公开 API、构建/发布入口、高 blast-radius surface 或反复历史模式只剩 router 一行而无解释？
7. 检查过生成：是否有 skills 仅按目录命名、trigger 重叠、没有独立 workflow/proof，或只是已有 skill 的 reference？
8. 回到 fixed revision 核对所有路径、symbols、命令、构建和测试仍成立；区分 `executed-pass`、`executed-fail` 与 `observed-not-executed`。
9. 按 delivery policy commit、push、创建或更新 PR/MR。记录 branch、exact commit、PR/MR、验证、approval/merge 状态；不得自动合并受保护分支。

## 必须保存的证据

### Repository-level evidence

- 完整 commit/code-read coverage 与 cursor；
- capability coverage ledger；
- repository model before/after；
- topology/route matrix；
- 每个 delivered skill 的 validation level 与证据 pointer；
- current-revision reconciliation；
- exact delivery ref 和 review state。

### 每个执行过的 replay case

- visible START 与 provenance；
- hidden oracle pointer，正文不暴露给 replay agent；
- episode commits、完整 patch/code inspection pointer 和 coverage 归属；
- model assertion / wrong alternative model；
- baseline replay result；
- outcome/decision trajectory comparison；
- intervention/primary-home decision；
- logic-loop model 与 topology decision；
- candidate diff；
- same-case rerun；
- 需要时的 adjacent/negative route regression；
- 保留、降级或撤销结论。

这些是学习证据，不是客户 repo 里的新方法 skill。客户 repo 只保留未来任务需要的最终 repo-local delta。

## 完成门槛

只有同时满足以下条件，当前 repo card 才能标为 `completed`：

- requested history range 内所有可达 commits 都有实际 code-read coverage disposition；
- fixed revision 的主要 task families/capability surfaces 全部进入 ledger 且有明确 disposition；
- 没有未解释的高影响能力遗漏，也没有用 router 一行替代应独立触发的已验证 workflow；
- repository model 已根据历史和当前状态收口；
- 所有交付 skills 通过结构校验，L1/L2/L3 claim 与证据强度匹配；
- 高风险或易重叠 skills 已完成要求的 replay/negative/route 验证；
- 最终 topology 通过 coverage、trigger precision、behavioral closure、duplication/context cost 和 current-state reconciliation 检查；
- 客户 dirty state 被保留；
- 接受的 delta 已形成 delivery policy 要求的可追溯 ref。

遇到授权缺失、无法读取必要 outcome 或隔离 replay 不可用时，把受影响 case/capability 标为 `blocked` 或 `candidate`，写清已搜索范围、当前仍可完成的 L1 evidence 和恢复动作。只有当阻塞使 repository-level 完成门槛无法满足时，repo card 才标为 `blocked`；其他 repo cards 可以独立继续。

任务结束时向 Coordinator 报告：history coverage、capability coverage、最终 skill topology、各 validation levels、精确 delivery ref、未验证/blocked 项和 card pointer。不要只报告 skill 数量或 eval 总分。

## 解释性示例：防止再次欠生成

假设一个 service 的全历史和当前代码呈现三类稳定任务：

1. webhook 至少一次投递，需要幂等处理；有历史 incident、fix 和 replay；
2. invoice payment/refund 状态机；有历史 incident、fix 和 replay；
3. audit export；当前有公开函数、格式 contract、测试和独立用户请求方式，但没有合适的 incident replay。

正确结果可以是：一个轻量 router、两个达到 L2/L3 的 focused loop skills，以及一个达到 L1 的 audit-export capability skill。不能因为第三类没有历史 issue replay 就把它丢进 router 一行；也不能因为 `export.py` 是单独目录/文件就无证据地建 skill。决定性证据是独立 trigger、当前 authority/workflow 和 proof。

反过来，如果多个小目录共同完成同一个 media session，且共享 trigger、resource lifecycle、failure cleanup 和 integration test，就应形成一个 capability/focused skill，并把目录表放 reference，而不是为每个目录各建一个 skill。
