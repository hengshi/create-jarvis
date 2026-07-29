# Customer Jarvis growth loop

客户 Jarvis 的建设入口是客户已经在使用的 Host Agent，不是一个需要先安装和配置的
`jarvis-box`。`create-jarvis` 负责把一句目标变成一条连续旅程：构建客户知识、学习代码
仓库、定制工作流，最后才部署正式运行时并让数字员工上岗。

```text
Customer request
  → Preparation + dispatch
  → Company Jarvis construction ─┐
                                  ├→ reconciliation
  → Repository learning ─────────┘
  → Workflow construction
  → Formal runtime deployment
  → Supervised shadow
  → Active workflow
  → Evidence-driven evolution
```

这些是内容和交付门槛，不是要求产品实现的 phase 状态机。唯一持久的协调事实是普通文件、
Git revision 和外部交付引用；Agent 可以从这些证据恢复。

## 0. Customer Agent ready

客户只需把授权材料交给自己的 Codex、Claude 或其他可执行 Agent，并说：

> 请先运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

Host Agent 先把 create-jarvis clone 到本地并固定 commit，然后成为全程 Construction Coordinator。它先引导客户提供 docs、repo 和 work-system 指针，再检查这些指定材料的可用能力、写入边界和访问授权，
但不要求客户先安装 jarvis-box，不要求填写 phase 表，也不把内部 eval-loop 方法讲给客户。

## 1. Preparation and dispatch

Coordinator 先主持一次简短资料 intake，再浅查客户明确提供的 docs、repo、issue/MR、CI/test 指针。它不扫描 Host home、Agent 配置或无关仓库来猜客户环境。随后确定：

- 公司身份以及 `<company-slug>-jarvis` 的 GitHub/GitLab 发布目标；
- 每个代码仓库的授权 checkout、写入方式、目标分支和交付策略；
- Repository learning 的历史范围：一年、两年、全部或自定义 ref/time range；
- 可并行工作的边界、单一 writer 和恢复证据。

它写入 `BUILD-CONTEXT.md`、两个自包含的 `RUN-*.md`、两份 progress 和
`CONSTRUCTION-JOURNAL.md`，随后自动派发 2A/2B。provider 支持子 Agent 时可并行；否则由
同一个 Agent 顺序执行。客户不需要复制命令、开两个终端或理解内部角色。

`START-HERE.md` 只是在 provider 必须通过外部命令恢复子任务时才生成的技术兜底，不是标准
客户交付物。

## 2A. Company Jarvis construction

Company construction 在模板骨架上用客户证据建立：

- company/product/brand identity；
- 以产品能力为中心的 modules，而不是 backend/frontend/database 等工程分层；
- source routes、canonical repo fleet、first proof 和 repo handoff；
- 产品、实现、验证双向可追溯的 capability coverage；
- 有证据的 cross-cutting interactions、known issues、decisions 和 rejected paths。

每个 candidate 都要有 include/merge/defer/reject disposition。找不到证据时记录搜索范围和
`needs-verification`，不把模板、路径存在或 commit message 当成客户事实。构建结果必须提交到
客户选择的 GitHub/GitLab；已有远端通过 branch + PR/MR 交付，未合并时只叫
`ready-for-review`。

starter workflows 保持 `draft-template`，不能在这一阶段冒充已经适配客户的生产闭环。

## 2B. Repository learning

每个代码仓库独立学习、独立写入、独立发布。Agent 按客户选择的历史范围遍历 commit，并把
issue/MR、patch、相关代码、测试和最终 outcome 还原为真实 episode，而不是只对 message 做
语义分类。

对每个有潜在复用价值的 episode 执行：

```text
current guidance baseline
  → replay real failure/decision
  → compare with historical outcome
  → minimal durable skill/reference/script delta (or no_skill_gap)
  → rerun the same case
  → adjacent regression check
```

只有能改善未来行为的知识才进入 repo-local skill；一次性事实留在 episode/progress。完成一个
repo 必须留下可消费的 commit、branch 和 PR/MR（按客户 policy），不能把 dirty worktree 当作
交付。

2A 和 2B 不共享可变状态，不互相等待。Company construction 可把尚未发布的 repo-local entry
标为 `pending Repository learning`。

## 3. Reconciliation

Coordinator 等两条 lane 到达当前声明范围的证据门槛后：

1. 验证 Company Jarvis 和各 repo-local 交付 ref；
2. 把 pending handoff 替换为真实、可解析的 repo-local pointer；
3. 保持 company 侧保存 `what/why/where first`，repo 侧保存 `how`；
4. 用真实 artifact 重跑 company → module/source → repo-local 路由；
5. 对尚未完成的大仓库保留明确 coverage boundary。

客户可以先使用某个 workflow 所需的 route-scoped boundary；这不等于宣称所有仓库和全部历史
都已完成。后续 learning 产生新 ref，不会偷偷改变 shadow/active runtime 的快照。

## 4. Workflow construction

通用 issue post-check、bugfix 和 feature-delivery skills 是讲解和共同改造的模板，不应删除。
Agent 用客户真实 source、角色、权限、branch/review/test/release/acceptance policy 和至少一个
受控或真实 case，把每个 workflow 独立改到 `construction-ready`：

```text
START → WORK → VERIFY → END
```

`construction-ready` 只说明闭环在建设环境中通过，不允许直接处理无人监督的生产任务。

## 5. Formal runtime deployment

只有目标 workflow 已达到 `construction-ready` 后，Coordinator 才部署正式运行时：

- 选择已发布的 Company Jarvis commit 和每个必需 repo-local commit；
- 下载并校验 jarvis-box 公共 release bundle，选择一个固定 digest 的正式 image；
- 从同一 release metadata 固定内置 uv-im-connector 的 version/commit；
- 创建独立、可审计、可轮换和可撤销的正式 Agent identity；
- 为该 identity 完成所选 GitHub/GitLab、Agent provider 和 source 的授权；
- 部署持久化 agent home、runtime state 和 connector state；
- 将 Company context 和允许的 repo fleet 作为不可变 snapshot 注入；
- 在容器内执行 Agent、Git provider、source、读写和路由 capability probes。

Host Agent 与正式 Jarvis Agent 都是高权限执行主体。正式 jarvis-box 容器按 root 运行，
这不是低权限沙箱；独立 identity 只用于审计、轮换和撤销。Docker socket 等
host-root-equivalent 能力仍必须显式选择。

正式 Compose 用同一个 `JARVIS_IMAGE` digest 启动 jarvis-box 服务和可选的 uv-im-connector
服务；二者进程、凭据、日志和 volume 边界独立，但客户不选择第二个 connector image。探针通过后
workflow 依次进入 `runtime-deployed`、`ready-for-shadow`。部署锁记录准确 commits、单一 image
digest、内置组件版本、identity 和 probe evidence。

## 6. Shadow and activation

`ready-for-shadow` workflow 在客户监督下处理代表性真实任务，开始时改为 `shadowing`。每次任务
检查 routing、repo-local execution、verification、END、权限和隐藏人工步骤，并把耐久缺口写回
唯一正确的 primary home。

只有多个代表性任务稳定闭合、完成声明与客户证据一致、遗留边界明确，且客户批准后，该
workflow 才变为 `active`。`active` 总是绑定该 workflow 的 deployment lock，不代表整个客户
Jarvis 所有能力同时成熟。

## 7. Evidence-driven evolution

上岗后的每个任务继续产生受控学习：

```text
real artifact
  → active workflow
  → Company route
  → repo-local execution
  → verification + END
  → no_skill_gap or minimal writeback
```

新增能力进入 module；跨 module 因果进入 cross-cutting；仓库架构、命令和测试进入 repo-local；
客户跨 source/repo/角色闭环进入 workflow；一次性 issue、日志和 diff 留在任务/source owner。
每次只增加能消除已观察重复成本或错误的最小资产，并用原 case 或相邻 case 回归。

## 客户现场节奏

- 第一天上午：讲清 Jarvis 生态、知识分层和上岗路径；
- 第一天下午：客户把一句目标交给 Host Agent，自动启动 Company construction 与 Repository learning；
- 第二天：完成当前 route-scoped reconciliation，构建首个客户 workflow；
- 第三至第五天：部署正式 runtime，用真实任务 shadow，逐个激活 workflow；
- 之后：由 active workflow 的 END/writeback 持续进化。

时间表只服务于客户沟通。是否完成始终由 evidence gate、Git 交付和固定 deployment snapshot
决定，不由“跑了一晚”或“到了第几天”决定。
