# Company Jarvis construction agent task

你的唯一目标，是依据 `BUILD-CONTEXT.md` 中已授权的客户证据，构建或继续构建客户自己的 company Jarvis repo，并在验证后把它发布到客户确认的 GitHub 或 GitLab。

你不是在“把模板文件填满”，也不是要机械复制另一个公司已经运行数月后才形成的文件数量。你的交付物应是一个对**本次声明授权范围与记录深度 coverage-complete、且所有结论 evidence-backed** 的公司语义与路由中枢：新的 Agent 能据此理解客户是谁、有哪些产品能力、事实去哪里找、任务先查什么、何时进入哪个 repo，以及哪些结论仍未被证明。

## 本轮 construction 完成后应该具备什么

Company Jarvis 至少能回答：

1. 这家公司和产品的 confirmed identity 是什么，哪些品牌名、产品名或历史名称仍有冲突；
2. 客户有哪些稳定的业务/产品 capability，它们的边界和常用语言是什么；
3. 每个 capability 的产品证据、实现证据与验证入口在哪里；
4. 文档、issue tracker、代码、测试、CI 等 source 如何访问，分别拥有什么事实；
5. 各 repo 在 capability owner、delivery surface、docs surface 和 verification surface 中扮演什么角色；
6. 一个真实任务从哪个 module/source 开始，什么 first proof 决定是否进入哪个 repo；
7. 哪些跨 module / repo 关系有真实证据，哪些仍是 unresolved；
8. 一条新知识应留在 company module、cross-cutting、source route、repo-local skill 还是当前任务中。

当前客户证据足以形成的 module knowledge、source route、跨模块关系和公司级决策，应在本轮完成，不能以“以后会成熟”为由跳过。成熟客户 workflow、额外 references 和专用 tools 则必须按各自证据形成；不能为了模仿另一个成熟 Jarvis 而按数量制造。完整成长路径见 `playbooks/customer-jarvis-growth-loop.md`。

## 写入边界

- 主要写入目标只有任务文件指定的 company Jarvis target，以及 `BUILD-CONTEXT.md` 明确确认的同一个 customer-owned GitHub/GitLab remote。
- 任务目录中只维护 `COMPANY-JARVIS-PROGRESS.md`，以及确有并行扫描需要时的临时 evidence packet；不要建立 construction 状态机。
- 客户代码仓库、文档和工作系统都是只读证据；不要在其中创建 repo-local skills、branch、commit 或 MR/PR。
- 不运行 Repository learning 的 history eval loop。Company construction 可以定向读取 issue、MR/PR、commit diff 和测试来证明公司级事实，但不遍历历史来训练 repo-local skill。
- 不创建 `jarvis.toml`、`bootstrap-state.json` 或 `bootstrap-result.json`。
- 当前是 Host Agent 的 construction context，不要求 jarvis-box 已安装，也不执行 `jarvis-box version/status/agent current`。生成的 company 指针必须允许 construction/onboarding 在普通授权 checkout 中继续；正式 runtime 诊断只在后续 managed-production context 中触发。
- runtime-owned 通用方法不复制进 company repo；当前 Host Agent 已有对应方法时可以使用，没有时按本 method pack 的自包含合同完成。
- base 中的 issue post-check、bugfix 和 feature-delivery workflow 必须保持 `draft-template`。本任务不能把通用母版冒充客户已经验证的 workflow。
- 发布不是可选的额外动作。只能严格按 `BUILD-CONTEXT.md` 中已经确认的 provider、host、owner/namespace、repo、visibility、default branch 和 publication mode 执行；缺少或冲突时先标 blocker，不能猜测或降级为只交本地目录。

## 先锁定本地 target 与远端身份

开始写入前，读取 publication contract 并用所选 provider 的已登录 CLI/API 做 live probe：

- provider 必须是客户选择的 GitHub 或 GitLab，host 与 owner/namespace 必须完全匹配；
- remote URL 必须对应 canonical `<company-slug>-jarvis`，不能因为当前账号有权限就改发到个人 namespace；
- 若远端已有历史，先 fetch/clone 并从真实 default branch 建独立工作分支；不得把另一个本地 Git history 强推到它上面；
- 若远端不存在或确认为空，可以先在本地 target 构建，但发布前必须再次探测，防止长任务期间目标状态发生变化；
- 若本地已有 `origin` 且与确认目标不一致，停止远端写入并记录 blocker，不得替换后继续；
- 若 CLI 登录、repo 权限或 branch/review policy 与 `BUILD-CONTEXT.md` 不一致，保留已完成的本地工作并标 blocked，不得尝试绕过保护。

只记录身份与 probe 结果，不读取、打印或写入 credential value。

## 从中断处继续

先读取：

1. 当前 `RUN-COMPANY-JARVIS-CONSTRUCTION.md`；
2. `BUILD-CONTEXT.md`；
3. 已存在的 `COMPANY-JARVIS-PROGRESS.md`；
4. company target 当前内容和 Git 状态；
5. 本 method pack 中本任务明确引用的模板、脚本与 reference。

若 progress 不存在，创建一个普通 Markdown 工作日志，至少包含：

- target、固定的输入 revision 和写入策略；
- artifact/source 覆盖表；
- candidate module 表；
- repo 与 source 覆盖表；
- 已通过和未通过的 routing probe；
- unresolved conflict / missing authorization；
- publication target、probe、local branch、remote branch、commit、PR/MR 和下一发布动作；
- 最后验证过的 evidence pointer；
- 下一动作。

每闭合一个 module 或 source 的证据单元就更新 progress。恢复时先验证最后一个完成项的 pointer 和 revision 仍然成立，再从 `Next` 继续；不要因为新开了 session 就重扫已经闭合的范围。

`COMPANY-JARVIS-PROGRESS.md` 是给后续 Agent 阅读的工作日志，不是机器协议。不要为它写 parser、cursor schema 或状态迁移代码。

## 核心工作单位：capability，不是 repo，也不是扫描 Agent

初始 taxonomy 必须来自客户的产品语言和实际行为。repo、package、目录、技术栈和组织结构只能提供实现证据，不能直接成为业务 module。

以下名称通常不能直接作为主要 module：

- `backend`、`frontend`、`api`、`database`、`infra`；
- 单个 repo 名、service 名或 package 名；
- 没有客户行为含义的工程分层；
- 仅从模板预置、却没有客户证据的通用能力。

一个好的 module 应稳定表达客户能力，使常见任务能先收敛到少量候选 module；它不应随着 repo 拆分或目录重构立即失效。

对软件产品 capability，纳入 `modules/` 前至少需要两类独立锚点：

1. **产品锚点**：产品文档、UI、API contract、验收材料或行为测试证明这项客户能力真实存在；
2. **实现锚点**：实际读取过的代码证明该能力在 `<repo-name>:<repo-relative-path>` 有实现落点。

测试/CI、issue、MR/PR 和运行观测可以补强行为、历史与因果证据，但“路径存在”“依赖声明存在”或“commit message 提到了名字”都不能单独证明业务含义。

没有代码实现的业务流程或外部系统，不要为了满足双锚点强塞进产品 module；优先把它建模为 source、未来 workflow 或 unresolved boundary。

## 证据发现：四个视角，数量自适应

完整构建需要同时覆盖四个证据视角，但这不等于必须固定启动四个 Agent。

### 产品与领域视角

从产品文档、导航、UI、API 文档、词汇表和验收材料提取：

- 公司、品牌、产品和历史名称；
- 客户使用的 module/capability 名称；
- 用户角色、业务目标、输入输出和边界；
- 产品 workflow 中的 gate、审批、发布或验收节点；
- 中文名、英文名、缩写和代码 namespace 变体。

### 代码与 repo 视角

实际读取 repo 结构、build files、关键实现、已有 `AGENTS.md` / `CLAUDE.md` / skills 和 CI 配置，提取：

- repo 做什么、不做什么；
- capability contract 在哪里定义；
- 哪些 repo 是 delivery、docs 或 verification surface；
- 每个 module 的真实实现锚点；
- 当前真实存在的 repo-local entry。尚未存在时写 `pending Repository learning`，不能预写一个想象中的 `skills/SKILL.md`；
- 可执行的 build/test/verification 入口。

目录名只用于导航。要读取足够的代码、配置或测试来证明它与 capability 的关系。

### 行为与验证视角

从单元测试、集成测试、E2E、CI、验收用例和运行观测中提取：

- capability 的可观察行为；
- 最接近原始 claim 的 first proof；
- 验证入口和当前覆盖盲区；
- 跨 repo contract 在哪里被实际检查。

不要把“测试文件存在”写成“行为已覆盖”。需要读取测试意图、运行入口和必要的断言/fixture，区分可执行证据与静态线索。

### 协作与历史视角

从 issue、MR/PR、review、设计记录、release 记录和相关 commits 中定向提取：

- 可复用的故障模式；
- 已接受且仍有效的产品/设计决策；
- 明确评估后被拒绝的路径；
- false owner、跨 module 因果边和实际交付链；
- 客户真实工作流的候选证据，供后续 workflow onboarding 使用。

统计、label 或 commit message 只用于发现候选。任何要写入 company Jarvis 的 durable 结论，都要继续读取必要的正文、讨论、代码变化、测试或最终结果来证明；不能把一批 message 的语义分类直接当成知识。

### 如何并行

当 artifact 数量足够大且当前 runtime 支持 delegation 时，按互不重叠的 source、repo 或 module batch 并发扫描。每个 worker 只交付带 pointer 的 evidence packet，不直接同时修改同一个 company target。主 Agent 负责 identity reconciliation、taxonomy、冲突判断和最终写入。

小客户或单 repo 可以顺序完成。并发是缩短时间的执行策略，不是方法正确性的来源；不要为了凑固定 Agent 数量切碎上下文。

## Construction loop

这个 loop 按 capability/source/repo coverage 持续运行：声明范围中的每个 artifact root 都必须被扫描，每个 candidate capability 都必须得到 `include / merge / defer / reject`，每个 included capability 都必须完成 evidence closure。不要用固定运行时长、固定 case 数或“已经有几个好看的 module”提前结束。

“coverage”不是声称逐字读完所有源码、文档和历史。必须把实际深度写清：

| Evidence family | 最低 coverage 合同 |
|---|---|
| Docs / wiki / API docs | 枚举全部导航/root collections；读取定义 identity、capability、用户行为和 acceptance 的相关内容；记录不可访问或排除范围 |
| Code repos | 覆盖清单中全部 repo 的 root guidance、build/CI/test 入口和职责边界；对每个 included capability 深读足以证明语义的实现路径 |
| Tests / CI | 覆盖全部已发现测试/CI 入口；对每个 included capability 读取相应测试意图、运行方式和已知盲区 |
| Issue / MR / decision / release history | 记录精确 query、时间/ref 范围和结果量；统计/分类只发现候选，任何提升为 durable knowledge 的条目必须深读原始证据与 outcome |
| Other sources | 枚举 source 提供的 collection/namespace 和权限边界；按 capability/route 深读相关条目 |

若 source 太大，允许分 batch 和恢复，但不能把尚未覆盖的 batch 默认为完成。范围外内容、负向搜索和 source retention limit 都要可见。

### 1. 固定输入与身份

- 对 `BUILD-CONTEXT.md` 中每个授权构件执行 live read probe，并记录实际 revision/观测时间。
- 区分 company identity、product identity、brand identity 和 source 中出现的历史名称。
- source 检测到的名称不能覆盖客户确认的公司身份；冲突写 `needs-owner-confirmation`，并保留双方 pointer。
- 若 product identity 尚未确认，可以先做只读发现；在关键 identity 无法可靠渲染前不要伪造 base。

### 2. 建立 capability 候选图

先从产品侧证据形成候选 capability，再用代码和测试寻找实现/行为锚点。对每个候选记录：

| Candidate | Product anchor | Implementation anchor | Behavior/verification anchor | Relationships | Decision |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | include / merge / defer / reject |

判断规则：

- 同一个客户能力因 docs、UI 和代码使用不同名字时，保留客户确认名称，并把其他名称记作检索 alias；
- 多个候选实际是一个稳定能力的不同 delivery surface 时合并，不按 repo 分裂；
- 一个候选过大、导致多数任务仍无法确定 first proof 时再拆分；
- 没有双锚点的候选保持 `defer`，不生成一个装满 `UNRESOLVED` 的 module 目录；
- confirmed module/source 名称原样保留，不擅自翻译、缩写或改大小写。

### 3. 渲染最小 base

当 company name、slug 和 product identity 足以确认后，使用本 method pack 的 `scripts/instantiate_company_jarvis.py base` 创建或补齐骨架。为脚本准备的 render input 只是一次普通调用输入，不是 construction state；其事实仍以 `BUILD-CONTEXT.md`、progress 和客户证据为准。

`base` 只负责安全、一致地生成：

- company entry 与通用目录；
- company knowledge-layer / routing references；
- 三个 `draft-template` workflow；
- 空的 tools/evals/cross-cutting 容器。

它没有证明任何客户语义。重复运行时必须保留客户已经编辑的内容。

### 4. 逐 capability 做 evidence closure

对每个 `include` 的 capability，使用 `instantiate_company_jarvis.py module` 生成容器，然后完成最小 module contract：

- **业务定位**：用客户语言写目的、用户/角色、能力边界和明确 non-scope；
- **产品锚点**：指向实际 docs/UI/API/test evidence；
- **实现锚点**：至少一个实际读取并存在的 `<repo-name>:<repo-relative-path>`；
- **行为/验证锚点**：first proof、验证入口或明确的验证缺口；
- **首跳路由**：哪些 artifact signal 会进入此 module，先查什么；
- **false owner**：只有证据显示容易误路由时才写；
- **关系**：只写已证明的相邻 module/capability 关系。

五文件不是五项填空任务：

- `overview.md` 是每个 included module 必须完成的稳定语义与路由入口；
- `known-issues.md` 只保存可复用失败模式，不保存 issue 清单；
- `decisions.md` 只保存仍有意义的 accepted/superseded 决策和理由，不保存 MR 日志；
- `rejected-features.md` 只保存明确评估并拒绝、很可能再次被提出的路径；
- `test-coverage.md` 保存行为覆盖、验证入口和盲区，不保存测试运行流水。

后四个文件没有可靠证据时保持明确的空状态。不要为了“看起来完整”制造内容。

### 5. 建 source routes

对每个已授权 source 使用 `instantiate_company_jarvis.py source` 建立一份 route contract，记录：

- source identity、authority/owner、访问状态与精确 pointer；
- Agent 到达和检索它的实际方式；
- revision、freshness 或观测时间；
- 它能证明哪些事实、关联哪些 modules；
- writeback 与 redaction 边界；
- blocked source 已搜索的范围和恢复条件。

`sources/` 是 source 的索引和访问合同，不是 source 内容镜像。不要复制文档正文、issue dump、代码或凭据。只有客户特有 source 确实需要一套可复用且已验证的操作方法时，才创建 source helper skill；一份 README route 足够时不要生成 skill。

### 6. 建 repo fleet 与 capability surfaces

更新：

- `references/canonical-repo-fleet.md`；
- `references/capability-delivery-surfaces.md`；
- `references/jarvis-first-routing.md`。

对每个 repo 记录 canonical identity、source route、default branch evidence、访问状态和实际角色。不要使用笼统的“主仓/次仓”代替以下关系：

- capability / contract authority；
- execution owner；
- delivery surface；
- docs / operational surface；
- verification surface。

一个 repo 可以承担多个 surface；capability authority 也可能不是 repo。Company construction 与 Repository learning 可以并行，因此 repo-local skill 尚未生成不是 company construction 的失败。记录当前真实入口；不存在时明确写 `pending Repository learning`，后续 1+2 reconciliation 再替换。

### 7. 建 cross-cutting 因果边

从已验证的产品、代码、测试和历史证据中更新 `cross-cutting/module-interactions.md`。这里回答“为什么从 A 必须继续检查 B”，应包含：

- trigger；
- shared invariant 或交付关系；
- producer → handoff/transform → consumer 的因果边；
- 常见 false owner；
- first proof；
- repo-local next-hop pointer 或 `pending Repository learning`；
- evidence anchors。

不要把完整调用栈、symbol map、逐文件修改清单或 repo 测试命令复制到 cross-cutting；这些属于 repo-local。没有真实跨模块证据时，保持空状态，不根据目录依赖图发明业务关系。

### 8. 收束 company entry

最后更新 canonical company entry skill 和 README，使它们只声明已经证明的范围：

- identity 与 scope；
- modules 与 source routes；
- repo fleet / repo-local handoff 当前状态；
- artifact → module/source → first proof → optional repo handoff 的初始路由；
- knowledge primary-home 规则；
- 三套 workflow 的 `draft-template` 状态和 onboarding next step。

初始 entry 在 workflow 尚未激活时，仍应能把知识查询、问题 artifact 和变更线索路由到正确 module/source/first proof；它不能假装已拥有客户 bugfix/feature 闭环。

不要为了模仿成熟 Jarvis 而自动生成额外 workflow、reference 或 tool。只有当前客户证据证明它是跨任务、可复用且 primary home 确实在 company 层时才创建。

### 9. 用真实 artifact 做 routing probes

从已读取的客户材料中选择少量、彼此不同的真实 artifact 或任务线索，至少覆盖：

- 一个产品/能力问题；
- 一个 defect 或异常线索；
- 一个可能跨 capability/repo 的变更线索。

对每个 probe，从 company entry 开始，检查能否得到：

1. 正确的候选 module/source；
2. 最接近 claim 的 first proof；
3. evidence 足够时的 repo handoff，或诚实的 unresolved/pending；
4. 不应进入的 false owner；
5. 可验证的 pointer。

把期望、实际 route、差异和修正记录在 progress；适合长期回归且不暴露敏感内容的 case 再写入 company `evals/`。修正 routing 后重跑失败 probe。不要用关键词存在、文件数量或 Python `assertIn` 代替这项行为验证。

### 10. 验证语义与待发布内容

运行本 method pack 的 `scripts/verify_company_output.py` 检查它能确定判断的结构、安全、secret、模板 token 和写入边界。它通过只表示结构边界通过，不表示 company 语义正确。

随后人工/Agent 检查：

- 每个 included module 的产品与实现双锚点仍可解析；
- source routes 的访问方法可执行或有明确 blocked/recovery；
- repo role 和 capability surface 不来自猜测；
- entry 与 cross-cutting 没有复制 repo-local implementation truth；
- routing probes 已通过或把真实缺口写为 unresolved；
- 三套 starter workflow 仍为 `draft-template`；
- 客户 repo 未被修改；
- company repo 中没有 raw source dump、凭据或 construction state。

发布前再检查本地 Git 状态和准备提交的完整 diff，确认只包含 company Jarvis 目标文件，没有临时 evidence packet、客户 raw source dump、credential、未渲染 token 或无关 worktree 变化。结构 verifier 通过不能替代这项 diff 与语义审查。

### 11. 发布到客户选择的 GitHub 或 GitLab

语义与待发布内容验证完成后，再按 publication mode 执行：

#### 新建或确认空的远端

1. 在 company target 中建立正常、可追溯的 Git history；仅提交已验证的 company Jarvis 文件。
2. 发布前重新确认远端仍不存在或仍无 refs，且 provider/host/namespace/repo 完全匹配。
3. 使用所选 provider 的 CLI/API 创建 repo；采用确认的 visibility/default branch，不让 provider 自动初始化 README、license 或 `.gitignore` 与本地 history 竞争。
4. 设置并核对 `origin`，推送初始 default branch；禁止 force-push。
5. 从远端重新读取 repo URL、default branch 和 commit，证明交付可达。

#### 已有历史的远端

1. fetch 远端并从真实 default branch 创建专用 branch；若当前本地工作不是基于该 history，重新应用/提交到正确分支，不得用 force 解决 ancestry 冲突。
2. 推送专用 branch，GitHub 创建 PR、GitLab 创建 MR，并遵守客户的 review/CI/branch-protection policy。
3. 不自动合并。PR/MR 未合并时把 construction 标为 `ready-for-review`，向客户给出唯一 review URL；不能宣称 canonical default branch 已经包含交付。
4. 客户合并后再次验证 default branch commit，再标记 `completed`。

把 provider、remote URL、visibility、default branch、publication mode、本地/远端 branch、commit SHA、PR/MR URL 与状态、最后验证命令及结果写入 `COMPANY-JARVIS-PROGRESS.md`。不得记录 token 或其他凭据。

## 完成标准

满足以下条件时，Company construction 可以在当前授权边界内标记完成：

- company/product identity 已确认，或冲突被明确标注且不妨碍已交付路由；
- 所有已授权 source/repo 都已读取并在 coverage 表中有状态，不可访问项有恢复条件；
- 每个 included software module 都完成产品锚点 + 实现锚点 + first proof/verification contract；
- repo fleet、capability surfaces 和已有跨模块因果边都有 evidence pointer；
- canonical entry 能通过代表性 routing probes；
- 结构 verifier 通过，语义检查已记录；
- workflow 全部保持 `draft-template`；
- customer-owned GitHub/GitLab remote 可达，且已验证的 commit 已进入新/空 repo 的 default branch；已有 repo 则在合并前明确保持 `ready-for-review`，合并并复验后才是 `completed`；
- progress 写明当前构建边界、未解决项，以及 Repository learning / workflow onboarding 的下一步。

“所有模板文件都有文字”“扫描过所有 commit message”“生成了很多 skills/tools”都不是完成标准。

## Blocked 与降级

- 一个 source/repo 不可访问：记录 probe、范围和恢复条件，继续其他独立范围；
- candidate module 缺产品或实现锚点：defer，不生成虚假 module；
- identity/authority 冲突：保留双方证据并标 `needs-owner-confirmation`；
- 核心产品 taxonomy 完全无法从任何授权证据建立：这是 construction blocker；
- provider/host/namespace、repo create/push 权限或现有远端保护策略无法确认：允许继续独立的本地语义构建，但 publication 保持 blocked，整体不能标记完成；
- 只有当 blocker 使最小 company entry 无法形成时，才阻塞整体任务。

结束时只向客户说明：company Jarvis 当前可用到什么边界、正式 remote URL（或唯一 publication blocker）、需要 review 的 PR/MR URL（如有）、Repository learning 的独立状态不可由本任务声称，以及 1+2 完成后需要进行 workflow onboarding。不得声称数字员工已经正式上岗。
