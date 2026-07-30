# Create Jarvis

`create-jarvis` 是客户从零建设、安装并启用自己 Jarvis 的 Agent 方法仓库。它不是安装器、construction daemon 或 jarvis-box 的内部模板集合。

## 给正在读取这个页面的 Agent

如果客户让你“阅读这个 GitHub 仓库并构建 Jarvis”，先在当前客户授权的 workspace 中执行普通 `git clone https://github.com/hengshi/create-jarvis`，记录 checkout commit，然后从本地读取 `SKILL.md` 及引用文件。不要用 GitHub HTML、raw URL 或连续 WebFetch 拼装方法。

客户第一句话只授权读取这个公共方法仓库，不授权扫描客户电脑。不要枚举 home、Agent 配置、shell 环境、已安装 skills、无关 Git 仓库或历史残留来猜公司情况。先引导客户提供公司名称、文档入口、代码仓库和工作系统指针，只检查明确提供的 URL 或本地路径。

## 客户唯一入口

客户在自己已经登录并授权的 Host Agent 中只需要说：

> 请先运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

收到请求的 Agent 是 Construction Coordinator。它主持资料 intake、建立可恢复建设工作区、协调长任务、发布客户资产、安装 jarvis-box 并引导 onboarding。客户不需要安装 create-jarvis、执行 phase、复制子 Agent 命令或开多个终端。

## 固定逻辑模型

| Owner | Owns |
|---|---|
| `create-jarvis` | 通用建设方法、模板、步骤、证据门槛和恢复协议 |
| Construction Workspace | 当前旅程的 work cards、checkpoint、journal 和 evidence |
| `<company-slug>-jarvis` | 客户知识、跨 runtime 宪法、路由、sources、workflows 和公司工具 |
| 客户代码仓库 | repo 执行真相与 repo-local skills |
| `jarvis-box` | 正式 runtime 实现、injected execution contract、control plane、state 和 operator runbook |

Company Jarvis 的 `runtime-governance.md` 是客户所有 Host Agent 与 managed runtime 共同遵守的公司宪法，不是 jarvis-box 内部 runbook。create-jarvis 负责构建和验证这份宪法；jarvis-box 自己负责实现其 runtime 内部能力。

## 四部分建设旅程

```text
customer request
  → new / resume
  → Construction Workspace
  → Part 1  Company Jarvis repo initialization
  ├→ Part 2  Company Jarvis construction
  └→ Part 3  N independent repo-local learning tasks
  → Reconciliation Gate
  → Part 4  jarvis-box install, start and onboarding
  → supervised shadow
  → active
```

Part 1 从模板创建并发布客户 Company repo 骨架。Part 2 从客户证据构建 modules、sources、cross-cutting、skills、references、tools 和 runtime governance。Part 3 为每个代码 repo 创建一个独立长任务，把经真实 episode 验证的执行知识写回该 repo。Part 2 和 Part 3 可并行。

Part 4 只在 Reconciliation Gate 通过且至少一个 route-scoped workflow 达到 `construction-ready` 后开始。它下载并校验 jarvis-box public release，固定 Company/repo/image revisions，安装并启动服务，完成独立正式身份授权和容器内 probes，再引导客户进入 shadow。

## Runtime governance 的建设

```text
template scaffold
  → customer runtime discovery
  → customer-specific constitution
  → installed and verified runtime behavior
```

模板只提供问题结构。Part 2 要确认客户自己的 canonical runtime root、repo cache/task workspace、task-start sync、稳定工具、checkout 隔离、handoff、cleanup、credential 和 write boundary。如果规则依赖尚不存在的 Host runtime 工具或同步机制，必须创建、安装并验证，或明确标记 `pending-runtime-foundation`；不能只写说明。

不得把 HENGSHI 的路径和工具名复制给其他客户。Part 4 观察到的稳定 runtime 事实可回写 Company 宪法，但 jarvis-box 的 execution contract、control plane 和 operator runbook 仍由 jarvis-box 自己拥有。

## Construction Workspace 与恢复

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

每张 work card 记录 objective、authorized inputs、allowed writes、target workspace/branch、writer、可选 session handle、status、last verified checkpoint、delivery、blocker、`Next` 和验证时间。

恢复时使用 recorded method commit，核验实际文件、Git/remote 和 runtime facts；旧 writer 活着就重连，已结束才替换，ownership 不明时禁止重复 writer。session handle 只是提示，不是真值。

客户恢复话术：

> 继续构建我们的 Jarvis。建设工作区是 `<path>/jarvis-build`。请读取 `CONTINUE-JARVIS.md` 和 `CONSTRUCTION-JOURNAL.md`，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。

## Repository learning

学习单位是完整、可重放的真实 episode，不是 commit message 分类：

```text
visible START
  → pre-change baseline replay
  → hidden real outcome comparison
  → no_skill_gap / minimal skill delta
  → same-case rerun
  → adjacent regression
```

每个 repo 只有一个 writer 和独立交付 ref。只有能改善未来行为的知识才进入 repo-local skill；dirty worktree 不是交付。

## Workflow 生命周期

```text
draft-template → construction-ready → runtime-deployed
               → ready-for-shadow → shadowing → active
```

`active` 属于一个 workflow 和一组不可变 revisions，不代表整个客户 Jarvis 的所有范围都完成。没有代表性真实任务时诚实停在 `ready-for-shadow`。

## jarvis-box 发布边界

客户使用 jarvis-box 公共 release bundle，不 clone 私有源码。正式部署固定一个 OCI image digest；镜像内包含 jarvis-box、固定版本 connector 和 Agent 工具链。可选 connector service 与 jarvis-box service 使用同一镜像，但拥有独立凭据、日志和 volume 边界。

正式 Agent 使用独立、可审计、可轮换和可撤销的高权限 identity。Docker socket 是 host-root-equivalent，必须显式授权。建设阶段的人类 Host home、SSH agent 和 credential store 不复制进正式 runtime。

完整方法见 `playbooks/customer-jarvis-growth-loop.md`、`playbooks/construction-journey-model.md`、`playbooks/construction-recovery-contract.md` 和 `playbooks/runtime-method-contract.md`。

## 验证原则

确定性脚本只验证路径、渲染、安全和可执行合同。方法质量必须通过真实 Agent 行为验证：一句话是否启动完整 journey，中断后是否从事实恢复，Company runtime governance 是否变成可执行宪法，repo learning 是否从真实 episode 改善行为，formal runtime 是否消费固定 revisions。不要用 Markdown 关键词存在冒充方法论验证。
