# create-jarvis-skill 目标

`create-jarvis-skill` 的真正目标不是生成一个通用目录骨架，而是指导 runtime agent 从 0 引导生成客户自己的公司 Jarvis 生态。

客户完成 jarvis-box 安装或一键启动受支持 container 后，直接在已登录 runtime agent 中使用本仓库。agent 必须依据方法论、模板、phase checklist 和客户授权材料，创建一个客户自有的 company Jarvis repo；不依赖 bootstrap 表单命令，也不让客户在多个 session 之间搬运 prompt。这个 repo 在角色和生态形态上应当等价于 `hengshi-jarvis`：它是该公司的 agent 入口、知识路由、workflow 编排、repo handoff、source 索引和持续演进中心。

`hengshi-jarvis` 的“等价形态”不是任意公司知识库目录树，而是明确的仓库拓扑：root `README.md` / `MAINTENANCE.md` / `jarvis.toml`，长期知识在 `modules/`、`sources/`、`cross-cutting/`，路由和质量规则在 `references/`，入口和 workflow/helper skills 在 `skills/`，操作工具在 `tools/`，校准用例在 `evals/`。bootstrap 过程文件只能作为 runtime artifacts 或 `_bootstrap/` 辅助材料，不能变成顶层主骨架。

`hengshi-jarvis` 是成熟形态和目录拓扑参考，不是可复制的事实来源。任何私有公司事实、内部 host、repo fleet、issue/MR 编号、owner、文档正文、代码片段和 secret 都不能进入通用模板或客户产物。

## Bootstrap 的含义

Bootstrap company Jarvis repo 指 runtime agent 在客户授权范围内完成以下工作：

1. 从客户提供或授权访问的 docs、repos、tests、issues/MRs、wiki、产品材料、支持材料、CI 配置和历史 commits 中提炼公司级事实。
2. 用这些事实建立客户自己的产品/业务/技术 module 拓扑，而不是套用 `backend-service`、`frontend-app` 这类通用工程分层。
3. 创建 `<slot>-jarvis` Git 仓库和同名 company entry skill，让 agent 能按 artifact、问题类型、workflow、source 和 repo 路由。
4. 分清 company identity、客户确认的 product identity、source-detected identity，不能把 repo/docs 里识别出的品牌或产品名直接写成客户公司身份。
5. 建立 source、repo、workflow inventories，并明确每个条目的 evidence、owner、状态和缺口。
6. 为第一条高价值 workflow 建立可执行闭环：START -> WORK -> VERIFY -> END。
7. 为 pilot repos 创建或登记 repo-local skill package，让 repo execution truth 留在 repo 本地。
8. 安装四个通用方法 skill，创建并定制三个默认 workflow 母版；再为额外 confirmed source/workflow scope 创建完整 skill package。证据不足时写明 status、unresolved 和 verification，不得只留 stub 或 backlog，也不复制 source 原文。
9. 建立影子试跑、历史回放校准、`no_skill_gap` 判断和受控 writeback 规则。
10. 写出 jarvis-box 和后续 agent 可继续执行的 `bootstrap-state.json` 与 `bootstrap-result.json`。

模板只提供结构、边界和初始文件形状。所有 truth-bearing 内容必须来自客户证据、真实试跑、历史回放，或在穷尽可访问证据后被明确标记为 `unresolved`、`grow-from-pilot`、`grow-from-history-replay`。只有策略或语义歧义才需要 owner 确认；checked-in 文件、Git 元数据和可直接执行的命令不得因为 agent 尚未读取而写成 `needs-owner-confirmation`。

## 命名和默认能力合同

- Git 仓库名：`<slot>-jarvis`
- 公司统一入口 skill：`<slot>-jarvis`
- 公司自有 workflow：`<slot>-workflow-<name>`
- 公司自有 source/tool skill：`<slot>-<name>`
- repo-local skills：留在各自代码仓库，不加 slot 前缀

每个客户无条件获得四个通用方法 skill：`ponytail`、`writing-durable-docs`、
`jarvis-self-improve-skill`、`stop-slop`。它们保留通用名称，不携带 reference company
事实。

每个客户无条件获得三个完整、可编辑的工作流母版：

- `<slot>-workflow-issue-post-check`
- `<slot>-workflow-bugfix-loop`
- `<slot>-workflow-feature-delivery`

这些 workflow 不是空 scaffold。模板提供稳定闭环语义，runtime agent 在 Phase 9 根据客户
issue/ticket 系统、repo 路由、分支与版本策略、review/CI、发布方式、owner 和 writeback
policy 完成初次定制。

`jarvis-box-doctor`、`jarvis-box-init`、`jarvis-box-monitor` 也属于所有客户的默认能力，
但由 jarvis-box install 全局提供并随产品升级，不能复制进 `<slot>-jarvis`。

## 什么不算完成

以下结果不能被称为完成 bootstrap：

- 只生成 `SKILL.md`、inventory 文件和 repo-local skill 骨架。
- 生成 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 这类顶层 bootstrap 过程目录，而不是 `hengshi-jarvis` 风格的 `modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`、`evals/`。
- company Jarvis repo 只有通用占位文本，没有客户产品/业务/模块拓扑。
- modules 主要是 `backend`、`frontend`、`api`、`database`、`infra` 之类工程层，而不是从客户材料中提炼出的产品域或业务能力。
- repo-local skills 生成了，但 company Jarvis 不知道这些 repo 在真实 workflow 中承担什么角色。
- 没有 source 证据、owner 状态、missing input、writeback policy 或 verification gate。
- 只满足脚本能解析、jarvis-box 能绑定、precheck 能运行，却没有形成公司级路由和第一条 workflow 闭环。
- 把大量 source 原文、代码、issue、聊天记录、私有路径或 secret 当成”知识库”复制进 Jarvis repo。
- 目录数量正确、模板渲染完成、verifier 通过，但客户语义不正确或实际执行证据缺失。verifier 只做确定性机器防呆，不能替代客户语义正确性或实际执行。
- `completed` 仅因 phase 的 scaffold 存在而标记，但该 phase 的客户事实和执行证据并未实际填入。

## 对”模板”的定义

模板提供的是固定方法语义（method semantics），直接复用并参数化。模板本身不含客户事实——所有 truth-bearing 内容由客户证据填充。

- 模板定义结构、边界、初始文件形状和不可协商规则。
- 四个通用方法 skill 和三个默认 workflow 的固定方法语义直接复用；客户事实只填入允许定制的位置。
- 客户事实（module 名、product identity、source route、workflow trigger、repo role、endpoint/route/label）只能来自 evidence inventory、owner 确认、真实试跑或历史回放。
- 不以文件数量要求 module 成熟度；一个只有 scaffold 的 module 如果证据不足、但 coverage matrix 和 generation plan 已正确记录缺口，仍是合格的 Phase 6/7 产物。
- 禁止用模板结构充当客户事实，禁止把”模板写了几行”当成”module 已成熟”。

## 唯一验收目标

目标只有一个：runtime agent 按 `playbooks/phase-checklist.md` 一项一项执行后，产物必须像客户自己的 company Jarvis 生态。

机器文件可解析、目录存在、precheck 可运行，只是过程检查。它们不构成另一个成功等级。如果最终 repo 形态不像客户自己的 `hengshi-jarvis`，就说明当前 phase checklist 不够细，必须继续调整 checklist 和 phase 文件。

验收细则见 `acceptance.md`。

## Runtime 所有权边界

jarvis-box install 托管以下能力：runtime sync、Jarvis maintenance launcher、Jarvis session self-improvement、Task workspace cleanup、service lifecycle、agent registry/routing/failover、Task lifecycle。company bootstrap 只检查、登记和配置 company-specific policy，不重新实现这些能力。

install/image 还必须提供 agent CLI、create-jarvis-skill 入口、Git/VCS 客户端和 selected agent 可写的 bootstrap workspace。service-private state 与 agent-owned workspace 分离；Linux owner/group/ACL 和 container host UID/GID mapping 必须能由 live probe 证明。权限合同不成立时由 install/image 修复，不能要求客户用递归提权命令兜底。

bootstrap phase state（`bootstrap-state.json`、`bootstrap-result.json`）与 jarvis-box Target/Task/Run/AgentConversation/Workspace lifecycle 是两套状态。Phase 3-14 始终写 `bootstrap-state.json` 和 `bootstrap-result.json`；不得用 Task/Run status 替代 `phase_status`。

只有 Phase 11 真正通过 jarvis-box Task 执行 shadow pilot 时才记录可选 Target/Task/Run/AgentConversation/Workspace pointer；直接受控 dry-run 不要求也不得编造 ID。Task/Run pointer 不是所有 bootstrap 的硬条件。

## 两个演进循环

history replay 与 session self-improvement 是两个证据来源不同的循环，不得互相替代：

- **history replay（Phase 12）**：从 pilot repo Git 历史构造 visible START 和 hidden oracle，用隔离 agent 重放来校准 skills。属于 bootstrap 阶段。
- **session self-improvement（day-2）**：从真实 agent sessions 发现重复操作失败，用于持续改进。属于 day-2 运营。

## 不可协商规则

- `bootstrap-result.json` 只报告 runtime 状态、产物路径、缺失输入、blocker 和下一步，不输出复杂分层字段。
- `bootstrap-result.json` 必须能被 jarvis-box 直接解析；`missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions` 只能是字符串数组，结构化细节写到 rollout 或 report 文件。
- `bootstrap-result.json.paths` 必须是纯字符串 map；不能把 repo-local skill 路径列表、文件表格或对象塞进 `paths`。
- 如果产物不符合 `acceptance.md`，最终状态必须是 `needs-input`、`blocked` 或 `failed`，并明确列出是哪一个 phase/checklist 项不够或未完成。
- 业务理解不是可选项。runtime agent 必须读取客户授权材料并提炼客户自己的 module、workflow 和 repo role。
- 不要求第一次产物达到 `hengshi-jarvis` 的文件数量、覆盖范围或成熟度，但要求角色正确、证据链清楚、第一条 workflow 可验证。
- 不允许为了“看起来完整”而编造 owner、source-of-truth、repo 命令、审批规则、产品模块或测试路径。
- 不允许把 source-detected product/brand/company identity 与客户 company identity 混写成一个已确认主体；冲突时必须进入 `needs-input` 或 `blocked`。
- 历史回放必须先尝试从 pilot repo 的真实 Git 历史自动构造 eval case；从当时可见的初始信号构造 START，再用隐藏 outcome 判断失败模式。不能跳过 Git 历史扫描直接等人提供 episode，也不能只停在 candidate registry，更不能用事后答案污染 START state。
- skill 扩展必须先判断 `no_skill_gap`，只有可复用、可验证、归属明确的缺口才写回 repo-local、company Jarvis 或 create-jarvis-skill。
- history replay 必须以轻量 cursor 逐个相关 commit 组闭合 case、comparison、skill-creator candidate 和 same-case rerun；不能先分类整个时间范围，也不能把控制循环生成为 eval-loop skill/file。

## 最终目标

一个合格的 bootstrap 完成后，客户应当能够在自己的机器上通过 agent 对话进入 company Jarvis，并让 agent 面对真实工作时知道：

- 从哪个公司入口 skill 开始；
- 当前问题属于哪个产品域、workflow、source 或 repo；
- 应该读取哪些来源、遵守哪些边界；
- 何时进入 repo-local skill；
- 如何验证结果；
- END 阶段应该不写回、写回任务局部记录、写回 repo-local skill、写回 company Jarvis，还是抽象为 create-jarvis-skill 方法论改进。
