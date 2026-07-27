# Create JARVIS Skill

`create-jarvis-skill` 是客户 runtime agent 使用的 Jarvis 构建方法包。它不再让一个 Agent 从环境检查一直跑到所有仓库学习完毕，而是准备两个可独立运行、可过夜、可重新启动的任务；Company construction 的正式交付物会发布到客户选择的 GitHub 或 GitLab。

这两个任务只是完整成长路径的并发构建段。客户 Jarvis 的完整方法是：运行环境就绪 → Preparation → Company construction + Repository learning → 1+2 reconciliation → Workflow construction → Shadow delivery → Active Jarvis → 证据驱动的持续进化。详见 `playbooks/customer-jarvis-growth-loop.md`。

## 运行模型

```text
客户当前已登录的 Agent（Preparation）
  ├─ 盘点已授权 repo、文档和工作系统
  ├─ 写 Company Jarvis construction task
  ├─ 写 Repository learning task
  └─ 给客户两条启动命令

新 Agent 1                         新 Agent 2
Company Jarvis construction      Repository learning
构建并发布 company Jarvis repo     写各客户 repo 的 local skills
```

Preparation 完成后即停止。两个新 Agent 不共享可变状态，也不要求客户搬运中间结果。

## 客户入口

jarvis-box/container 准备好 runtime、权限和 agent 登录后，客户只需说：

> 请为我们准备 Jarvis 构建。检查当前已授权的代码仓库、文档和工作系统，确认我们选择的 GitHub 或 GitLab 上的 company Jarvis 发布目标，写好 Company Jarvis construction 与 Repository learning 两个任务文件，并给我两条可以直接启动它们的命令。

完整入口见 `playbooks/prompts/customer-start.md`。

## Preparation 的交付物

```text
jarvis-build/
├── BUILD-CONTEXT.md
├── RUN-COMPANY-JARVIS-CONSTRUCTION.md
├── RUN-REPOSITORY-LEARNING.md
└── START-HERE.md
```

- `BUILD-CONTEXT.md` 只保存构件路径、访问状态、revision、角色候选、write policy，以及客户确认的 GitHub/GitLab 发布目标；不复制正文或凭据。
- 两个 `RUN-*.md` 是自包含的长任务指令。
- `START-HERE.md` 包含适配现场 Codex、Claude 或其他受支持 agent 的两条真实命令。

没有 `jarvis.toml`，也没有全局 `bootstrap-state.json` / `bootstrap-result.json` 状态机。

## 两个执行任务

### Company Jarvis construction

输入是共同构件清单，输出是客户独立拥有、发布在其 GitHub 或 GitLab 命名空间中的 `<company-slug>-jarvis` repo。它负责公司级入口、语义和路由，并预装 issue post-check、bugfix、feature-delivery 三套 `draft-template` workflow；客户代码仓库对它是只读证据。只有本地目录不算正式交付。

它对声明授权范围与记录的扫描深度做 coverage-complete、evidence-backed 构建：从客户产品证据建立 capability taxonomy，逐 capability 闭合产品/实现/验证证据，建立 source routes、repo fleet、capability surfaces 与跨模块因果边，再用真实 artifact 验证 company entry routing。它不以固定 module 数或固定运行时间提前结束，也不把“coverage”冒充逐字读完所有内容。

### Repository learning

输入是构件清单中的全部代码仓库，输出写回每个仓库自己的 repo-local skills。

它按客户指定的一年、两年、全部或自定义历史范围遍历 commits，默认从旧到新，从真实历史中还原完整 episode。Agent 必须读取实际 code changes 和相关测试/上下文，在 pre-change snapshot 上隐藏 outcome 做 baseline replay，比较真实结果，判断 `no_skill_gap` 或最小 skill delta，再用同一 case 重跑。走到边界后还要用当前 revision 淘汰过时规则。commit message 只是导航信息；不会生成 `eval-loop` skill。

无论有多少 repo，只维护一份 `REPOSITORY-LEARNING-PROGRESS.md`：一张 repo 队列表加当前 episode pointer。重新运行同一条命令即可恢复。

## 1+2 之后：让数字员工上岗

`1+2` 交付 company Jarvis 与 repo-local skills 后，Agent 先把实际 repo-local entries 接回 company routing 并重跑 handoff probes，再使用三套预装草稿向客户讲解 workflow，并结合客户真实的 issue/source、团队角色、repo 路由、review/test/release policy 共同定制。草稿通过客户真实 bugfix/feature case 验证并改为 `active` 后，进入 shadow delivery；只有现场任务证明其稳定闭环后，才是可上岗的 Jarvis workflow。

## Runtime 与方法包边界

- jarvis-box/container：安装 agent、method skills、Git、GitHub CLI (`gh`)、GitLab CLI (`glab`)、权限与 volume，管理进程、session、日志、heartbeat 和 retry。
- Preparation agent：收集 observed artifact pointers，写任务包和启动命令。
- Company construction agent：只写 company Jarvis target，并按确认的发布策略写入客户的远端 company Jarvis repo。
- Repository learning agent：只按 policy 写客户代码仓库。
- create-jarvis-skill：维护三种角色的指令、模板和方法，不实现任务调度器。

稳定合同见 `playbooks/runtime-method-contract.md`，完整角色边界见 `playbooks/one-plus-two-runtime-model.md`。

## 目录

```text
create-jarvis-skill/
├── SKILL.md
├── GOAL.md
├── acceptance.md
├── playbooks/
│   ├── one-plus-two-runtime-model.md
│   ├── customer-jarvis-growth-loop.md
│   ├── runtime-method-contract.md
│   └── prompts/
│       ├── preparation.md
│       ├── company-jarvis-construction.md
│       └── repository-learning.md
├── templates/
│   ├── company-jarvis/
│   ├── skill-packages/
│   └── replay/
├── evals/
└── e2e/
```

## 验证原则

确定性脚本只检查它真正能判断的文件安全、路径和可执行边界。方法是否正确必须通过真实 Agent 行为验证：Preparation 是否真的产出两个可启动任务，Company construction 是否完成声明范围的语义/routing coverage，以及 Repository learning 是否在真实 episode 上产生可证明的行为改善。不要用 Markdown 关键词或 `assertIn` 冒充方法论测试。
