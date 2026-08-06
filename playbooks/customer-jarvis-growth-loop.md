# Customer Jarvis growth loop

客户从已经授权的 Host Agent 开始，不需要先安装 `jarvis-box`。`create-jarvis` 把一句目标变成一条可中断、可核验、可恢复的连续建设旅程。

```text
Customer request
  → New / resume from Construction Workspace
  → Part 1: Company repository initialization
  ├→ Part 2: Company Jarvis construction ───────┐
  └→ Part 3: N repo-local learning tasks ───────┤
                                                ├→ Reconciliation Gate
                                                └→ Workflow construction
  → Part 4: jarvis-box install, start and onboarding
  → Supervised shadow
  → Active workflow
  → Evidence-driven evolution
```

这些是内容与交付门槛，不是 phase 状态机。持续事实存在普通 Markdown、Git revisions、外部交付引用和 runtime probes 中。

## 0. New or resume

客户只需对当前 Host Agent 说：

> 请用 `gh` 获取 `hengshi/create-jarvis` 的最新代码，检出其 commit 和提交日期时间和提交人，读取 `SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

Host Agent 固定 create-jarvis commit 后成为 Construction Coordinator。若 Construction Workspace 已存在，必须先恢复，不能重新初始化。若是新旅程，它引导客户提供 company identity、docs、code repos 和 work-system pointers，只探测这些明确授权的材料。

## Construction Workspace

Coordinator 建立 `jarvis-build/`：

```text
jarvis-build/
├── CONTINUE-JARVIS.md
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── work/
│   ├── company-repo-initialization.md
│   ├── company-construction.md
│   ├── repositories/<repo>.md
│   ├── reconciliation.md
│   └── jarvis-box-onboarding.md
└── evidence/
```

每张 work card 都能由一个新 Agent 独立恢复：它记录目标、授权输入、允许写入、目标 workspace/branch、writer ownership、可选 session handle、最后已验证 checkpoint、交付、blocker 和 `Next`。Coordinator journal 只做索引和汇总，实际文件、remote refs 和 runtime 状态仍需重新核验。

## Part 1. Company repository initialization

Coordinator 用 Company Jarvis 模板建立 `<company-slug>-jarvis` 最小骨架，并按客户 Git policy 发布。

骨架必须包含：

- company entry、modules、sources、cross-cutting、skills、references 和 tools 的稳定结构；
- starter workflows 和 repo fleet 表面；
- `runtime-governance.md` 与 quick reference；
- 所有尚未从客户证据确认的字段和建设状态。

模板是建设起点，不是客户事实。此时 runtime governance 只提供宪法结构和待回答问题。

## Part 2. Company Jarvis construction

Company integrator 从客户 docs、work systems 和只读代码证据构建：

- company/product/brand identity；
- 以产品能力为中心的 modules；
- source routes、canonical repo fleet、first proof 和 repo handoff；
- 产品、实现、验证双向可追溯的 capability coverage；
- cross-cutting interactions、known issues、decisions 和 rejected paths；
- 客户级 skills、references、tools 与 runtime governance。

Runtime governance 按以下路径成熟：

```text
template scaffold
  → customer runtime discovery
  → customer-specific constitution
  → installed and verified runtime behavior
```

如果宪法要求新的 Host runtime sync、稳定工具或 workspace 管理机制，Part 2 要创建、安装、运行并保留验证 evidence；暂时做不到则标记 `pending-runtime-foundation`。不能用文字完成度代替运行基础。

每个 capability candidate 都有 include/merge/defer/reject disposition。starter workflows 在适配并验证前保持 `draft-template`。

## Part 3. Independent repository learning

每个代码仓库有独立 work card、writer、workspace、branch、progress 和 delivery ref。不同 repo 可并行；同一 repo 同时只有一个 writer。

学习按客户选择的历史范围检查实际 diff，并把 issue/MR、patch、相关代码、测试和最终 outcome 还原为完整 episode：

```text
current guidance baseline
  → replay real failure or decision
  → compare with historical outcome
  → minimal durable skill/reference/script delta or no_skill_gap
  → rerun the same case
  → adjacent regression check
```

只有能改善未来行为的知识进入 repo-local skill。每个 repo 必须留下可消费的 remote commit/branch/PR/MR，或明确的 read-only/blocked 结果。dirty worktree 不是交付。

Parts 2 and 3 写入边界独立，可以并行。Company repo 可暂时记录 `pending Repository learning` pointer，但不能假装 repo-local entry 已交付。

## Reconciliation Gate and workflow construction

Coordinator 在当前 route-scoped 范围内：

1. 核验 Company repo 与 repo-local remote refs；
2. 将已完成 handoff 解析到真实 repo-local entry；
3. 保持 Company 侧存 `what/why/where first`，repo 侧存 `how`；
4. 重跑 Company → module/source → repo-local routing probes；
5. 保留未完成 repo 和历史 coverage boundary；
6. 用真实 source、role、branch/review/test/release/acceptance policy 构建首个 workflow；
7. 用至少一个受控或真实 case 验证 `START → WORK → VERIFY → END`。

满足这些条件的 workflow 才是 `construction-ready`。局部通过不代表整个客户知识或所有 repo 已完成。

## Part 4. jarvis-box install, start and onboarding

达到 Reconciliation Gate 后，Coordinator 才使用公开的 `hengshi/jarvis-box` Release/runtime 接口：

- 固定 Company Jarvis 和 workflow 必需 repo-local commits；
- 下载并校验 release bundle 与 OCI image digest；
- 创建独立、可审计、可轮换、可撤销的正式 Agent identity；
- 安装、启动服务并完成 Git/source/Agent provider 授权；
- 在容器内执行 Agent、source、routing、read/write 和 capability probes；
- 引导客户完成首个 workflow onboarding。

jarvis-box 自己提供 injected execution contract、control plane、runtime state 和 operator runbook。create-jarvis 不重新实现这些能力。安装中观察到的稳定事实可以回写 Company runtime governance，以完成客户跨 runtime 宪法的验证。

探针通过后 workflow 依次进入 `runtime-deployed`、`ready-for-shadow`。deployment lock 记录准确 commits、image digest、identity 和 probe evidence。

## Supervised shadow and activation

`ready-for-shadow` workflow 在客户监督下处理代表性真实任务，开始时进入 `shadowing`。每次任务验证 routing、repo-local execution、VERIFY、END、权限和隐藏人工步骤，并将耐久缺口写回唯一正确 owner。

只有代表性任务稳定闭合、遗留边界明确、deployment lock 准确且客户批准后，workflow 才进入 `active`。没有真实任务时诚实停在 `ready-for-shadow`。

## Recovery loop

客户中断后可对任意已授权 Host Agent 说：

> 继续构建我们的 Jarvis。建设工作区是 `<path>/jarvis-build`。请读取 `CONTINUE-JARVIS.md` 和 `CONSTRUCTION-JOURNAL.md`，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。

恢复者先固定 recorded method commit，再核验当前 card 的文件、Git、remote 和 runtime 事实。旧 writer 存活就重连，已结束才替换，ownership 不明时先阻止重复写入。恢复从最后已验证 checkpoint 开始，而不是相信最后一句进度描述。

## Evidence-driven evolution

上岗后的真实任务继续产生受控学习：

```text
real artifact
  → active workflow
  → Company route
  → repo-local execution
  → verification + END
  → no_skill_gap or minimal writeback
```

新增能力进入 module；跨 module 因果进入 cross-cutting；仓库命令与测试进入 repo-local；客户跨 source/repo/角色闭环进入 workflow；一次性 issue、日志和 diff 留在任务/source owner。每次只增加能消除已观察重复成本或错误的最小资产，并用原 case 或相邻 case 回归。
