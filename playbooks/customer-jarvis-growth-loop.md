# Customer Jarvis growth loop

客户 Jarvis 不是一次性生成物，也不是先交一个骨架、然后把后续成长交给客户自己摸索。`create-jarvis-skill` 提供一条从零到上岗、再到持续进化的完整路径；每一步都有明确输入、动作、交付物和进入下一步的证据。

```text
Runtime ready
  → Preparation
  → Company construction ─┐
                           ├→ 1+2 reconciliation
  → Repository learning ──┘
  → Workflow construction
  → Shadow delivery
  → Active Jarvis
  → Evidence-driven evolution ──┐
                                └──回写 modules / routes / repo skills / workflows
```

这里的步骤是内容成熟路径，不是要求 jarvis-box 实现的 phase 状态机。

## 0. Runtime ready

### 输入

- 客户选择并登录的 runtime agent；
- 已授权的代码、文档和工作系统；
- 客户认可的 workspace 与写入策略。

### 动作

jarvis-box/container 预装 agent、Git、GitHub CLI (`gh`)、GitLab CLI (`glab`)、create-jarvis-skill、skill-creator、通用 runtime methods 和已批准 source adapters，并用客户实际 Agent UID/GID 验证 workspace 与授权 volume 可读写。客户只登录自己选择的 GitHub 或 GitLab；另一个 provider 未登录不影响执行。

### 完成证据

- Agent 无需客户手工修目录权限；
- source/repo 可以通过 live probe 访问；
- 客户选择的 GitHub/GitLab host 与账号可通过 provider CLI 访问；
- runtime 能启动、记录和恢复长任务。

## 1. Preparation

### 输入

- 当前环境和客户给出的 identity / artifact pointers。

### 动作

Preparation agent 只做浅层、可验证 inventory，确认 customer-owned GitHub/GitLab publication contract，写出 `BUILD-CONTEXT.md`、两个 `RUN-*.md` 和 `START-HERE.md`。

### 完成证据

- 两个长任务不需要客户再次解释路径、权限、revision 或历史范围；
- Company construction 不需要客户再次解释 provider、host、namespace、repo、visibility 或发布策略；
- 两条命令能分别启动 Company construction 与 Repository learning；
- Preparation 没有提前执行任何长任务。

## 2A. Company Jarvis construction

### 输入

- `BUILD-CONTEXT.md` 中全部授权 docs、source、repo、issue/MR/CI/test 入口；
- company Jarvis template 和 construction method。

### 动作

Company construction agent 对**声明的授权范围与记录的扫描深度**做 coverage-complete、evidence-backed 构建：

1. 协调 company/product/brand identity；
2. 从产品证据建立 capability taxonomy；
3. 对每个 candidate 完成 include / merge / defer / reject 判定；
4. 对 included capability 闭合产品、实现和验证证据；
5. 建 source routes、repo fleet、capability surfaces 和 cross-cutting 因果边；
6. 填充有证据的 known issues、decisions、rejected paths 与 coverage gaps；
7. 收束 company entry，并用真实 artifact 验证初始 routing。
8. 验证完整待发布 diff，再将 repo 发布到客户确认的 GitHub/GitLab；已有远端保留历史并通过 PR/MR 交付。

它持续处理到声明范围全部有 coverage/disposition，不以固定 module 数、固定 Agent 数或固定运行时长提前停止。coverage 不等于逐字读取所有内容：docs 导航、repo 入口、test/CI 入口要全覆盖；每个 included capability 的相关实现和验证证据要深读；历史统计只作候选发现，提升为 durable knowledge 的条目必须深读原始 evidence/outcome。

### 完成证据

- 当前授权范围内的 capability、source 和 repo 都有明确 disposition；
- included module 都有产品锚点、实现锚点和 first proof/verification contract；
- company entry 能从真实 artifact 路由到 module/source/first proof；
- 不确定项诚实保留，不用模板补齐；
- starter workflows 仍是 `draft-template`。
- 新/空远端的 default branch 已包含验证后的 commit；已有远端在 PR/MR 合并前明确为 `ready-for-review`，不能把本地目录冒充正式交付。

## 2B. Repository learning

### 输入

- `BUILD-CONTEXT.md` 中全部代码仓库；
- 客户指定的一年、两年、全部或自定义历史范围。

### 动作

Repository learning agent 逐 repo 遍历声明历史范围，读取实际 code changes，从完整 episode 执行 baseline → outcome comparison → minimal skill delta → same-case rerun，并在当前 revision 收口。

### 完成证据

- 每个 repo 的声明历史范围都有 code-read coverage；
- 只有产生可复用行为改善的 repo-local guidance 被保留；
- `no_skill_gap` 不制造 skill；
- repo-local truth 留在所属 repo。

2A 与 2B 可以同时运行。它们不共享可变状态，也不等待对方才开始。

## 3. 1+2 reconciliation

### 为什么必须有这一步

Company construction 运行时，Repository learning 可能还没有创建或改善 repo-local entry；Company Jarvis 因此只能把该 handoff 标为 `pending Repository learning`。两个任务都结束后，必须把实际结果接起来，否则“1+2”只是两堆互不认识的文件。

### 输入

- company Jarvis 当前 revision；
- `COMPANY-JARVIS-PROGRESS.md`；
- `REPOSITORY-LEARNING-PROGRESS.md`；
- 每个 repo 最终存在的 repo-local entry 与 skill delta。

### 动作

由后续 customer runtime agent：

1. 验证每个 repo-local entry 的真实路径；
2. 把 company fleet / first routing 中的 pending handoff 替换为真实 pointer；
3. 检查 company module/cross-cutting 只保存 `what` 与 `why inspect next`，repo-local 保存 `where/how`；
4. 用 construction routing probes 再走一次 company → repo-local handoff；
5. 将仍 blocked 的 repo 保持显式 blocked，不伪造闭合。

### 完成证据

- Company entry 到 repo-local 的所有已声明 handoff 可解析；
- 没有把 repo implementation truth 复制到 company repo；
- 进入 workflow construction 所需的核心 route 已可用，或客户明确接受剩余边界。

## 4. Workflow construction

### 输入

- 预装的 issue post-check、bugfix 和 feature-delivery `draft-template`；
- company routing 与 repo-local skills；
- 客户真实 issue/source、角色、review/test/release/acceptance 方式；
- 至少一个真实或受控的 customer case。

### 动作

Runtime agent 先用通用草稿向客户讲解 START → WORK → VERIFY → END，再逐项替换模板假设：

- START 的真实 artifact/source 和准入条件；
- 各角色与 authority；
- module/source/repo-local 路由；
- branch、review、CI、测试、发布和验收 policy；
- blocked、handoff、writeback 与 END closure；
- 哪些步骤可由 Agent 自动执行，哪些必须由客户确认。

每个 workflow 独立定制、独立验证、独立激活，不要求三套同时完成。

### 完成证据

- 通用占位和错误假设已经移除；
- 真实 case 能走通 route、execution、verification 和 closure；
- 失败 case 已反馈到正确 primary home 并重跑；
- 只有通过验证的 workflow 从 `draft-template` 改为 `active`。

## 5. Shadow delivery

### 输入

- 已定制但尚需现场观察的 workflow；
- 客户接下来真实发生的 bugfix/feature 工作。

### 动作

Agent 执行真实任务，客户在关键 gate 审阅。每次任务都检查：

- routing 是否选中正确 module/source/repo；
- repo-local guidance 是否足以执行；
- workflow 是否遗漏角色、policy、验证或结束动作；
- 新知识的 primary home 在哪里；
- 是 `no_skill_gap`，还是需要最小 durable delta。

### 完成证据

- workflow 在多于一个代表性任务中稳定工作；
- 客户不再需要口头补充关键隐藏步骤；
- Agent 的完成声明与客户验收证据一致；
- 未验证范围仍明确，不以陪跑天数代替证据。

## 6. Active Jarvis 与持续进化

Jarvis 上岗后，每次真实任务都同时是一次受控知识维护机会：

```text
真实 artifact
  → workflow route
  → company module / source / cross-cutting
  → repo-local execution
  → verification + END
  → no_skill_gap 或最小 writeback
```

写回归属遵循：

- module：产品能力和稳定语义；
- cross-cutting：跨 module 因果边与 false owner；
- source route：访问、authority、freshness 与 writeback boundary；
- repo-local：仓库内架构、命令、实现和测试方法；
- workflow：客户跨 source/repo/角色的闭环；
- task artifact：本次才成立的证据。

定期维护不是重跑一次全量 bootstrap。以新 source、新版本、新 module、失败的 route、重复的人工补充或真实 workflow regression 为触发器，更新唯一正确的 primary home，并用原任务或相邻任务验证。

### 成熟资产怎样一步步长出来

后续真实工作出现以下信号时，按最小正确归属扩展，而不是在 construction 时预生成：

| 重复信号 | 应增长的资产 | 验证门槛 |
|---|---|---|
| 新产品 capability 已有产品与实现双锚点 | 新 module 或现有 module 边界修订 | 代表性 artifact 能稳定路由，旧 route 无回归 |
| 两个以上 modules 反复出现同一因果链或 false owner | cross-cutting interaction | first proof 能决定是否沿边展开 |
| 新的跨 source/repo/角色闭环无法由现有 workflow 表达 | 新 customer workflow | 多个真实/受控 case 走通 START → END |
| 多个 workflows 反复使用同一个 reasoning gate、verification contract 或 stop rule | focused company reference；公司无关则上游 runtime method | 调用点清楚，移除重复正文后 route 仍可用 |
| Agent 反复执行同一客户特有检索、转换或验证操作 | source helper skill 或 company tool | 实际执行、错误边界和 secret boundary 已验证 |
| repo 内反复出现同一 architecture/test failure | repo-local skill/reference | Repository learning 或真实 delivery replay 证明改善 |
| 一次性 issue、日志、diff 或客户环境事实 | 不增长 durable asset，留 task/source owner | `no_skill_gap` |

每次只增加能消除已观察到重复成本或错误的最小资产。这样客户 Jarvis 会从首轮 construction 的 modules/sources/routes，逐步长出适合自己公司的 workflows、references 和 tools，而不是复制另一家公司的目录清单。

## 客户现场节奏

典型但不硬编码的交付节奏：

- 第一天上午：讲清生态、知识分层和上岗路径；
- 第一天下午：runtime ready + Preparation，启动 2A/2B；小范围可当天完成并发布，大范围可过夜；
- 第二天：完成 1+2 reconciliation，开始客户 workflow construction；
- 第三至第五天：用真实任务 shadow delivery，逐个激活 workflow；
- 之后：由 active workflow 的 END/writeback 持续进化。

时间表服务于客户沟通，完成与否只看上述 evidence gate，不看“到了第几天”。
