# Create Jarvis 的完整目标与逻辑闭环

本文件是 `create-jarvis`、一套客户 Jarvis、客户代码仓库、Jarvis Runtime Foundation 与 `jarvis-box` 之间的唯一总纲。其他文件只能展开自己负责的合同、步骤和实现，不能另造一套所有权模型。

这里不使用 `company Jarvis`、`team Jarvis` 或 `domain Jarvis` 定义边界。一套 Jarvis 服务谁、覆盖哪些知识和代码仓库，由客户实际共同使用和维护的范围决定。`hengshi-jarvis` 是按本模型建设出的第一个真实客户 Jarvis，不是 `jarvis-box` 的内建依赖。

## 最终目标

客户从一句自然语言请求开始，由自己已授权的 Host Runtime Agent 作为 Construction Coordinator 持续建设并得到一套可运行、可维护、可恢复的 Jarvis：

1. 一个从模板初始化、由客户拥有并发布到其 Git 服务的 Jarvis repo；
2. Jarvis repo 中基于真实证据构建的 modules、cross-cutting、skills、references、`runtime-governance.md`、客户 workflows 与 Runtime Foundation；
3. 每个客户代码仓库内经真实历史 episode 验证，并按该仓库 Git policy 交付的 repo-local skills；
4. 一个使用独立正式身份、持久 Agent HOME 和该套 Jarvis 能力的 `jarvis-box` Docker 服务，以及完成监督式 onboarding 的首个真实 workflow。

最终交付的运行关系是：

```text
一套客户 Jarvis
  ├── Jarvis repo：知识、路由、workflows、运行时宪法与 Runtime Foundation
  ├── N 个代码仓库：各自的 repo-local execution truth
  └── 一套正式 Runtime Environment
       ├── 持久 Agent HOME
       └── jarvis-box：Task/Run、Agent 执行、control plane 与 operator surface
```

## 核心术语

- **Jarvis repo**：一套 Jarvis 的 Git source of truth。
- **Runtime Environment**：Runtime Agent 实际运行并发现 skills 的环境，可以是 native host，也可以是 `jarvis-box` Docker 容器。
- **Runtime Foundation**：Jarvis repo 针对一种 Runtime Environment 交付的 bootstrap、sync、稳定入口、state/log、doctor、恢复与调度适配机制。
- **Standard Workflow Pack**：`create-jarvis` 提供的建设期方法模板。它必须在 Construction 阶段被客户事实替换、验证并复制进客户 Jarvis；运行时不依赖 `create-jarvis`。
- **Customer Workflow**：客户 Jarvis 中已经客户化并通过行为证据验证的 workflow 实现。
- **Workflow Runtime Contract**：`jarvis-box` 与 Runtime Agent/Customer Workflow 之间的版本化输入、结果与受控 action 协议。
- **Runtime Job**：sync、maintenance、Jarvis self-improve 等在目标 Runtime Environment 内直接执行、对 Docker 无感的内部任务。
- **Scheduler Adapter**：把外部 scheduler 的触发绑定到目标 Runtime Environment 内 Runtime Job 的薄适配层。

Workflow Runtime Contract 是运行协议，不是业务方法；Runtime Foundation 是 Jarvis 的运行维护机制，不是 `jarvis-box` 的控制面；二者不能互相代替。

## 不变的所有权

| Owner | Owns | Does not own |
|---|---|---|
| `create-jarvis` | 通用建设方法、模板、Standard Workflow Packs、Construction Workspace、证据门槛、恢复协议与 Part 4 onboarding 方法 | 客户长期知识、客户 workflow 的运行时解释、客户 Runtime Foundation 的日常运行、`jarvis-box` 内部实现 |
| Construction Coordinator | 向客户解释每一步、渐进收集授权和事实、分配可恢复的长任务、核验证据并引导 onboarding | 成为客户知识、Git 真相、scheduler 状态或 Task/Run 状态的 source of truth |
| Construction Workspace | 本次建设的 work cards、checkpoint、journal、evidence、writer ownership、delivery refs、blockers 与恢复入口 | Runtime Agent 配置、调度状态、业务运行状态或部署真相 |
| Jarvis repo | 该套 Jarvis 的知识、路由、sources、Customer Workflows、跨 runtime 宪法与客户特有 Runtime Foundation | `jarvis-box` 的 Task/Run、control plane、execution mechanics 或 operator runbook |
| 客户代码仓库 | 该仓库的架构与执行真相、repo-local tools/skills、依赖初始化和验证方法 | 跨仓库知识、Jarvis runtime 机制或 `jarvis-box` 控制面 |
| `jarvis-box` | Workflow Runtime Contract、injected Agent execution contract、Task/Run、通用 workspace 生命周期、control plane、持久 runtime state/log、provider 安全写回、重试/去重/审计与 operator runbook/surface | Jarvis repo 的 clone/pull/sync/install/mount/校验、客户 workflow 语义、客户工具调用、客户 onboarding 状态机 |
| jarvis-box release | 启停/升级/诊断正式服务，以及从宿主进入正式容器执行 Runtime Job 的通用 transport helper | 客户 Scheduler Adapter、客户 cron 表、客户 Runtime Job 的内容 |
| jarvis-box Docker image | `jarvis-box`、选定 Agent CLI、通用工具链、通用 runtime skills 与 connector binary | `create-jarvis`、任一客户 Jarvis repo、任一客户 Runtime Foundation、任一客户 cron 脚本 |

Jarvis repo 的 `runtime-governance.md` 是所有使用这套 Jarvis 的 Agent 共同遵守的宪法，也是 Part 1 和 Part 2 的重要产物。它不是 `jarvis-box` runbook。`jarvis-box` 不读取或解释它；Runtime Agent 通过自己的原生 skill discovery 发现已安装的 Jarvis entry、workflows 与 references。

`jarvis-box` 二进制自己完成 injected Agent execution contract、control plane 与 operator runbook；`create-jarvis` 和客户 Jarvis 都不重复实现这些能力。客户 Jarvis 的宪法和 workflow 只通过 Runtime Agent 执行，并在边界上使用 Workflow Runtime Contract 与 `jarvis-box` 交换结果和受控 actions。

## 四部分建设旅程

```text
customer request
  → new / resume
  → Construction Workspace
  → Part 1  Jarvis repo initialization
  ├→ Part 2  Jarvis construction + Runtime Foundation
  └→ Part 3  N independent repo-local learning tasks
  → Reconciliation Gate
  → Part 4  jarvis-box install, Runtime Foundation bootstrap and onboarding
  → supervised real workflow
  → evidence-driven evolution
```

### Part 1：初始化 Jarvis repo

- 从模板建立最小骨架并发布到客户 Git 服务；
- 生成待客户化的 `runtime-governance.md`，明确 runtime root、workspace、凭据、state/log、故障与恢复边界；
- 建立 modules、cross-cutting、skills、references、sources、evals 与 Runtime Foundation 的建设入口；
- 记录未解决项和下一步，不把模板占位符伪装成客户知识。

### Part 2：建设 Jarvis 与 Runtime Foundation

- 从客户明确授权的文档、代码、工作系统、运行环境和历史证据构建知识、路由与 sources；
- 把 Standard Workflow Packs 变成 Customer Workflows：替换客户状态、标签、项目、审批、provider 和工具语义，并用真实或等价 case 验证；
- 实现该客户的 Runtime Foundation：bootstrap、quick/full sync、stable jobs、state/log、doctor/recovery、discovery-root sync 与 Scheduler Adapter；
- 把定期维护 Jarvis 本身的 maintenance/self-improve 与“针对某个代码仓库改进 repo-local skill”的业务 workflow 分开。

### Part 3：建设每个代码仓库的 repo-local skills

- 每个代码仓库分配独立、可长时间运行、可恢复的学习任务；
- 每个任务拥有自己的 work card、writer、workspace、branch、delivery ref 与恢复点；
- 以真实 episode 做 replay，只有证明能改善未来行为的 repo-local delta 才保留；
- 按目标代码仓库自己的 Git policy 评审并交付，不由 Jarvis repo 代存仓库内部执行细节。

Part 2 与 Part 3 可以并行。并发只是效率手段，不要求客户开多个终端。

### Reconciliation Gate

进入 Part 4 前必须核验：

- Jarvis repo 与所有 repo-local delivery refs 都可解析；
- Jarvis 路由与 repo-local handoff 没有互相矛盾；
- 至少一个 Customer Workflow 已通过 route-scoped 的真实或等价行为验证；
- Runtime Foundation 的实际稳定入口、state/log、doctor 和 Scheduler Adapter 已实现，不是文档占位符；
- 所有 `unresolved`、跳过项、访问限制和 owner 都已明确记录。

### Part 4：安装 jarvis-box 并完成 onboarding

- 使用 `jarvis-box` 公开 release 启动正式 Docker Runtime Environment；
- 在正式容器的持久 Agent HOME 中 bootstrap 客户 Jarvis Runtime Foundation；
- 在宿主安装客户 Jarvis 提供的 Scheduler Adapter；
- 完成正式身份、provider、Task/Run、persistence、workflow contract 和首个监督任务验证；
- 只有客户批准且 workflow 已验证时才启用对应业务入口。

Part 4 只依赖可核验的交付事实，不引入 deployment manifest、Jarvis context、deployment lock 或另一套 onboarding 状态机。

## 渐进式信息收集

Construction Coordinator 不要求客户在初次安装时一次性解释清楚所有仓库、历史项目管理工具、链接格式和访问方式。每次收集都必须先说明“为什么现在需要、会改善哪个结果、不提供会怎样”，然后允许客户：

- 现在授权并提供访问方式；
- 只提供最小事实；
- 暂时跳过并记录影响；
- 表示自己不知道，由建设 Agent 从证据中发现候选后再确认。

遇到 Jira、飞书项目或其他私有服务链接时，先识别链接族和证据价值，再向客户询问当前是否仍可访问、如何授权以及可否读取。结果写入相应 source route 或 Construction evidence：`available`、`access-pending`、`unavailable` 或 `unknown`。它不是要求客户预先完成的全公司系统清单。

跳过不等于验证通过。后续 workflow 或 replay 真正需要该信息时，应带着具体链接、用途和影响重新询问；拿不到原始问题时进入隔离重建路径。

## Standard Workflow、Customer Workflow 与 Runtime Contract

有价值的 HENGSHI 工作流方法可以产品化，但不能把 HENGSHI 语义写死在 `jarvis-box` 中：

```text
create-jarvis Standard Workflow Pack
  → construction-time customization and evidence
  → Customer Workflow in Jarvis repo
  → Runtime Agent native discovery
  → Workflow Runtime Contract owned by jarvis-box
```

`create-jarvis` 可以提供 issue post-check、bugfix、feature delivery、code review/followup、repo-skill improvement、command/chat 等 starter。`jarvis-box` 也可以把稳定 workflow type 作为公开产品能力标识，但 Customer Workflow 中使用什么 status、label、project、工具、审批规则和下一步含义，只属于客户 Jarvis。

### Workflow Runtime Contract

每个 Run 的版本化输入至少表达：

- workflow type；
- provider event、subject identity 与允许使用的 provider snapshot；
- Task、Run 与已准备 Workspace 的通用句柄；
- 当前 Run 被授权的 provider actions、资源操作与安全边界。

Customer Workflow 的版本化结果至少表达：

- 运行状态：`completed`、`blocked` 或 `needs-input`；
- 给人看的结论与证据摘要；
- 显式、结构化、受控的 provider actions；
- 可选的下一个受支持 workflow 请求。

客户业务 outcome 对 `jarvis-box` 不透明。HENGSHI workflow 可以得出 `ready-for-bugfix`，另一个客户可以使用完全不同的业务词；`jarvis-box` 不根据 outcome 猜测 `Doing`、`A::*`、标签或下一条 lane，只验证并执行结果中明确请求的受控 action。

Workflow result/action 是当前 Run 的协议产物，不是 `jarvis-context.json`、deployment manifest 或跨产品长期状态。`jarvis-box` 必须验证 subject/project identity、action allowlist、provider 权限和下一 workflow 的合法性；协议不能成为任意 shell、任意项目或任意 provider mutation 的通道。

### 运行闭环

```text
provider event / command
  → jarvis-box creates Task/Run and generic Workspace handles
  → jarvis-box launches Runtime Agent with Workflow Contract input
  → Runtime Agent natively discovers Customer Jarvis
  → Customer Workflow routes to sources and repo-local skills/tools
  → Customer Workflow returns explicit result/actions
  → jarvis-box validates, persists, writes back and optionally creates next Task
```

`jarvis-box` 不注入某个客户 skill path，不知道客户 Jarvis path/ref，也不在代码中解释客户 workflow outcome。找不到适用且 verified 的 Customer Workflow 时，应把它暴露为知识/能力缺口，而不是退回到 HENGSHI skill 注入或硬编码业务规则。

## Workspace、依赖初始化与外部资源

`jarvis-box` 只拥有通用 Workspace 生命周期：为 Task/Run 准备、登记、隔离、持久化和安全回收 workspace。它不能直接调用 `hengshi-workspace-init`，也不应要求所有客户提供一个同名的通用工具。

当客户 workflow 已经确定实际执行仓库和 base branch 后，可以调用本客户 Jarvis 或目标 repo 提供的依赖初始化工具，对现有 workspace 做客户特有配置。对 HENGSHI 来说，这可以继续叫：

```text
hengshi-workspace-init <repo> --configure-existing <workspace> --base-branch <branch>
```

这个名字和行为属于 `hengshi-jarvis`。issue/note 没有 source/target branch 时，`jarvis-box` 仍应正常启动 Runtime Agent；Customer Workflow 完成路由且拿到真实 base branch 之前，不调用 dependency configuration，也不猜 branch。

额外仓库或外部资源通过 `jarvis-box` 的通用、类型化、受控 resource/workspace registration 能力取得；由 Customer Workflow 或 repo-local tool 发出明确请求。`jarvis-box` 不通过 Everest、`.dev-data`、marker、目录名或其他客户特征猜资源。

Runtime Foundation 只清理自己拥有的 runtime root、cache、temp、state/log 和原生 workspace。它不读取 `jarvis-box` 的 `task-state`，不解释 `workspaces[]`，不调用 `jarvis-box tasks clean`，也不回收 `jarvis-box` 管理的 Task Workspace。

## Runtime Foundation 闭环

Runtime Foundation 是 Jarvis repo 针对一种 Runtime Environment 提供的最小维护机制。它负责：

- 从已批准的 Jarvis remote/ref 完成一次性 bootstrap；
- 在该环境的持久 Agent HOME 下维护 canonical repo cache、stable bin、state、locks 与 logs；
- 在 task start 执行快速同步，并由周期任务执行完整同步；
- 将 Jarvis entry、skills 与 references 物化到 Runtime Agent 原生 discovery roots；
- 为 sync、maintenance 和 Jarvis self-improve 提供可重复、可诊断、可重试的 Runtime Jobs；
- 保留上一个已验证版本，在更新失败时可恢复；
- 实现并安装该环境的 Scheduler Adapter。

它不要求把 Jarvis repo 挂载给 `jarvis-box`，不要求 `JARVIS_HOME`，也不需要 `jarvis-box` 了解 Git。Git remote/ref 与认证只在 Runtime Foundation bootstrap/sync 边界使用。

```text
approved Jarvis remote/ref
  → one-time bootstrap in target Runtime Environment
  → canonical cache in persistent Agent HOME
  → stable Runtime Jobs
  → Agent-native discovery roots
  → Runtime Agent discovers Customer Jarvis
```

Runtime Foundation 自己的 exact revision、sync state、lock 和 job logs 是单一 owner 内的操作状态；它们不是跨产品 `deployment-lock.json`，也不被 `jarvis-box` 用作启动门禁。

## 定时任务与 cron 的完整闭环

“定时任务”必须分成三类，不能再混称为 jarvis-box cron：

### 1. jarvis-box 驻留循环

provider polling、followup/writeback retry、Task/Run recovery、workspace cleanup retry、connector 等属于 `jarvis-box` 服务内部循环。它们随服务/容器运行，由 `jarvis-box` 配置、状态和日志诊断，不安装为客户 Jarvis cron。

### 2. 客户 Jarvis Runtime Jobs

full sync、Runtime Foundation cleanup、Jarvis maintenance、Jarvis self-improve 等属于客户 Jarvis Runtime Foundation。内部命令只实现任务本身，对 Docker 无感，不包含 `docker compose exec/run`。

### 3. Scheduler Adapter

Scheduler Adapter 属于客户 Jarvis Runtime Foundation，负责把 native cron/launchd/systemd 或 Docker host scheduler 绑定到同一个 Runtime Job：

```text
native scheduler ─────────────────────────→ inner Runtime Job

Docker host scheduler
  → customer Scheduler Adapter
  → jarvis-box release runtime-job helper
  → docker compose exec -T formal jarvis-box container
  → same inner Runtime Job in persistent Agent HOME

Runtime Agent already inside container ───→ inner Runtime Job
```

- native 环境的 scheduler 直接调用 Runtime Job；
- Docker 环境由宿主 scheduler 调用客户 Scheduler Adapter，再通过 release 的通用 helper 进入正式容器；
- 容器内 Runtime Agent 直接调用 Runtime Job，禁止再次递归调用 Docker；
- 使用宿主 scheduler 时，full sync 以 `--skip-scheduler-update` 或等价参数运行，避免容器内安装第二套 scheduler；
- 当宿主 scheduler 是权威调度者时，不再在容器内另装 cron；
- jarvis-box image 不烘焙 `hengshi-*`、客户 maintenance/self-improve 或客户 cron 脚本；
- scheduler 类型、频率和是否启用由客户批准，但必需的 adapter 未实现时不能标记 Part 2/Part 4 verified。

Part 4 必须验证完整三层证据：

```text
host scheduler entry exists
  → runtime-job helper enters the formal container
  → inner job writes expected state/log in persistent Agent HOME
```

仅证明 crontab 文本存在、仅在容器里手工跑过命令，或仅有 Adapter 文档，都不算闭环。

定时故障按 owner 诊断：

| Failure | Source of truth |
|---|---|
| host scheduler 没有触发 | host scheduler status/log |
| Adapter/Compose 未能进入容器 | host adapter/operator log |
| inner Runtime Job 进入容器后失败 | Runtime Foundation state/log in persistent Agent HOME |
| jarvis-box 驻留循环失败 | jarvis-box service status/log |
| Task/Run 失败 | jarvis-box state/control plane |

`jarvis-box` 不读取宿主 cron 日志，也不吞并 Runtime Foundation job log。

## Docker Runtime Environment 闭环

正式 Docker runtime 的关键持久边界是 Agent HOME，而不是 Jarvis 目录挂载：

```text
jarvis-agent-home volume (/root)
  ├── Agent identity/config
  ├── Agent discovery roots
  └── Jarvis Runtime Foundation cache/bin/state/locks/logs

jarvis-box-owned volumes
  ├── Task/Run state
  ├── managed workspaces
  ├── service logs
  └── connector state
```

Part 4 的顺序是：

1. 下载并校验 `jarvis-box` public release，固定 OCI image digest；
2. 准备 deployment/runtime 配置和独立持久 Agent HOME，不绑定 Host HOME；
3. 先以 `read-only` 启动正式容器，在该持久 Agent HOME 中激活独立正式身份；
4. 通过 release helper 进入这个正式容器，运行客户 Jarvis 提供的 Runtime Foundation bootstrap；
5. 在容器内验证 stable sync、state/log、doctor 与 Runtime Agent 原生 skill discovery；
6. 在宿主安装 Scheduler Adapter，并验证它通过同一 release helper 进入同一正式 Runtime Environment；
7. 验证 `jarvis-box` health、Agent、provider、Workflow Runtime Contract、Task/Run、persistence 和可选 connector；
8. 客户批准后切为 `worker`，只启用已具备 verified Customer Workflow 的业务能力，并由 Host Runtime Agent 引导首个监督任务；checkpoint 写回 Construction Workspace。

`jarvis-box` 不知道 Jarvis repo URL、path 或 ref，不执行其 Git checkout，不校验其内容，也不把 root skill 注入每次 Run。容器重建后，持久 Agent HOME 保留 Runtime Foundation 与 discovery roots；Jarvis 更新沿 `remote → cache → sync → discovery roots` 独立流动，`jarvis-box` image 更新沿 release 流程独立流动。

## Repository learning

学习单位是完整、可重放的真实工作 episode，不是 commit 或 commit message 分类：

```text
visible START
  → pre-change baseline replay
  → hidden real outcome comparison
  → no_skill_gap / minimal skill delta
  → same-case rerun
  → adjacent regression
```

存在真实 issue、工单或讨论时，优先恢复当时可见的问题。链接失效、权限不足或根本不存在原始问题时，扫描 Agent 只能提交 evidence packet；另一个上下文隔离的 Reconstruction Agent 根据 pre-change state、change diff、tests 与相邻历史反推最小问题陈述，并明确来源和不确定性。Replay Agent 只能看到 reconstructed START 和截止时点允许的证据，不能看到真实改动结果。

重建不是伪造原始 issue。episode 必须标记 START provenance：`direct`、`partially-recovered` 或 `reconstructed-from-outcome`；无法把结果信息与 Replay Agent 隔离的 case 不可评分。commit message 和项目管理链接只是线索，不是 ground truth。

每个代码仓库有自己的 work card、writer、workspace、branch、delivery ref 和恢复点。只有 same-case 与至少一个相邻 case 的证据证明能改善未来行为，才保留 repo-local skill delta。

## 中断、恢复与故障归属

客户可以在四个 Part 的任何步骤只完成一半。建设恢复不依赖原对话、某个 Agent 进程或原终端仍然存活。Construction Workspace 必须记录：

- 最后一个已核验事实和证据位置；
- 当前 work card 状态与唯一 writer；
- 已交付 remote/ref 和未交付本地修改；
- 授权、访问、客户确认和实际 blocker；
- 明确、可执行的 `Next`。

恢复时重新核验实际文件、Git remote/ref、Runtime Foundation state 和外部运行事实后继续，不能因 journal 写了 completed 就跳过实物检查。

运行故障按 owner 恢复：

- construction 中断：Construction Workspace；
- bootstrap/sync/maintenance/Jarvis self-improve 失败：Runtime Foundation state/log 与稳定入口；
- repo-skill improvement workflow 失败：对应 `jarvis-box` Task/Run、Customer Workflow 与目标 repo evidence；
- Workflow Contract result 无效：`jarvis-box` 拒绝 action 并保留 Task/Run 诊断，Customer Workflow 修复语义输出；
- `jarvis-box` Task/Run 或 provider writeback 失败：`jarvis-box` state/control plane/operator surface；
- Docker scheduler 无法进入容器：宿主 scheduler/Adapter operator log。

不创建一个跨产品 JSON 文件来重复、汇总或门禁这些事实。明确禁止把 `jarvis-context.json`、`deployment-lock.json` 或 deployment manifest 重新引入为 Jarvis repo 与 `jarvis-box` 的连接条件。

## 各仓库必须由此模型导出的改动

### create-jarvis

- 模板和 construction instructions 使用“一套 Jarvis / Jarvis repo”，不假定一个公司只能有一套；
- Standard Workflow Packs 保留有价值的方法，但明确是 starter，必须客户化并以真实 evidence 激活；
- Construction 渐进收集 provider、status、label、project、审批、历史链接和访问方式，并说明用途、允许跳过；
- Part 2 verifier 检查 Runtime Foundation 的真实 stable jobs、state/log、doctor 与 Scheduler Adapter 实现；
- Part 4 verifier 检查 Runtime Agent 原生 discovery、Workflow Runtime Contract 和 scheduler 三层证据；
- 不把 `create-jarvis` 安装进生产 runtime，不新增跨产品 context/manifest/lock。

### customer Jarvis（`hengshi-jarvis` 是首个真实实例）

- 保存客户 status/label/project/provider/tool/workflow 语义；HENGSHI 名称继续留在 `hengshi-jarvis`，不为假通用而改名；
- Runtime Agent/Customer Workflow 调用客户工具，`jarvis-box` 不反向依赖这些工具；
- 实现 Runtime Foundation stable jobs、maintenance、Jarvis self-improve、doctor/recovery 与 native/Docker-host Scheduler Adapter；
- 删除 Runtime Foundation 对 `jarvis-box` Task state、Task Workspace cleanup 和 `tasks clean` 的依赖；
- customer workflow 通过通用 result/actions 请求 provider writeback，不要求 `jarvis-box` 按客户状态机解释 outcome；
- 明确区分周期性 Jarvis self-improve 与每个代码仓库的 repo-skill improvement workflow。

### jarvis-box

- 把 issue/MR/followup/self-improve 等 launcher 收缩为通用 trigger、Task/Run、Workspace、Workflow Contract、result validation 与安全 writeback；
- 删除 HENGSHI status/label/project/bot/default path、HENGSHI skill fallback 和 outcome-to-next-lane 推断；
- 删除 `DependencyConfigurer` 及所有对 `hengshi-workspace-init` 的直接调用；
- 删除 Everest/`.dev-data`/marker/name 等客户资源启发式，保留通用类型化资源登记能力；
- 保留 provider/auth、Task/Run、workspace、安全 writeback、retry/dedupe/audit、operator mechanics 与通用 release `runtime-job` helper；
- 服务内部驻留循环继续在容器内运行，不把客户 Runtime Jobs 或 cron 烘焙进 image。

这些是同一逻辑闭环的必然结果，不授权顺手重构其他产品能力。

## 首个真实生产验收：chenjunhao-bot

`chenjunhao-bot` 是本模型的第一个生产 proving ground，不是通用产品中的特殊分支。最终目标不是“文档说明 Docker 可部署”，而是把该主机当前原生运行的 `jarvis-box` 安全替换为公开 release 的正式 Docker Runtime Environment，并用真实 HENGSHI workflow 证明整条闭环。

当前基线必须在切换时重新核验：该主机是 macOS/arm64，`local.jarvis-box` 由 launchd 原生运行，另有 Runtime Foundation maintenance/self-improve/cleanup 定时任务；正式切换前可能存在 active Task/Run。机器、版本、进程和调度事实属于部署 evidence，不得写死进 `jarvis-box` 产品代码。

切换门按以下顺序执行：

1. 选定并安装受支持的 Docker/Compose runtime，证明目标 OCI image 支持 arm64；
2. 固定 release 与 image digest，保存原生 binary、launchd definitions、runtime config 和 `jarvis-box` state 的可恢复快照；
3. 等待或明确处理 active Task/Run，在不接收业务 ingress 的条件下，用独立持久 Agent HOME 启动 Docker `read-only` runtime；
4. 在正式容器内 bootstrap `hengshi-jarvis` Runtime Foundation，验证原生 discovery、stable jobs、doctor 与 state/log；
5. 在宿主安装 HENGSHI Scheduler Adapter，并验证它经 release `runtime-job` helper 进入同一容器；原生 maintenance/self-improve/cleanup entries 此时仍保留但不得与新 adapter 重复触发；
6. 在隔离入口验证 health、provider、Task/Run persistence、Workflow Runtime Contract 和容器重建；
7. 排空原生服务，停止但不删除旧 launchd 服务，把正式 ingress 切到 Docker `worker`；
8. 完成一个真实监督 workflow 及安全 writeback，再禁用旧客户 Runtime Job launchd entries；
9. 观察期内发生阻断故障时，停止 Docker ingress、恢复切换前 state/config 快照并重新加载原生 launchd 服务。

生产验收必须同时证明：

- Docker 服务接管原端口和 provider ingress，原生 `local.jarvis-box` 不再运行；
- `hengshi-jarvis` 来自容器持久 Agent HOME 的 Runtime Foundation/discovery，不来自目录 mount 或 box 注入；
- 宿主只运行 Scheduler Adapter，inner Runtime Jobs 在容器内执行且日志落在持久 Agent HOME；
- Task/Run、workspace、connector 和 Agent identity 在容器重建后保持；
- rollback 在删除任何旧 launchd、binary 或 state 之前已经实际演练或至少完成机械可执行验证。

只有这些事实成立，首个生产验收才算完成。仅构建 image、仅运行 `docker compose up` 或仅返回 health 200 都不算完成。

## 完成标准

完整模型只有在以下事实同时成立时才闭环：

1. 使用同一个 `jarvis-box` binary/image，可以替换为另一套客户 Jarvis，而不重编译、不修改客户硬编码；
2. `jarvis-box` 中没有 HENGSHI status、label、project、tool、skill path、workspace heuristic 或 outcome 解释；产品名、provider adapter、公开 workflow type、通用 test fixture 不算客户绑定；
3. Runtime Agent 只靠持久 Agent HOME 的原生 discovery 找到 Customer Jarvis；`jarvis-box` 不知道 Jarvis remote/path/ref；
4. Standard Workflow Pack 经客户化和行为验证后才成为可用 Customer Workflow；未验证 workflow 不启用业务入口；
5. Workflow Runtime Contract 的 action 有版本、allowlist、identity 和权限校验，业务 outcome 对 box 不透明；
6. branchless issue/note 可以启动 Runtime Agent，不会因客户 dependency tool 需要 base branch 而在 workflow 路由前失败；
7. Runtime Foundation 不读取或清理 `jarvis-box` 的 Task/Workspace state；`jarvis-box` 也不读取 Foundation 或 host cron state；
8. Docker scheduler 通过“宿主 entry → release helper → 正式容器 → inner job state/log”得到端到端证据；容器重建后正式身份、Jarvis discovery 与 Foundation state 仍在；
9. 一个真实监督任务完成 `provider event → Task/Run → Customer Workflow → repo-local execution → explicit actions → safe writeback`；
10. 任一步中断后，新 Host Runtime Agent 能仅凭 Construction Workspace 和各 owner 的真实状态恢复继续。

## 尚需现场回答、但不破坏模型的问题

以下是每次建设/部署的输入，不是逻辑漏洞：

- Jarvis remote/ref 与 bootstrap 凭据如何一次性提供给目标 Runtime Environment；
- 当前 Runtime Agent 的 discovery roots 是哪些；
- scheduler 使用 launchd、systemd、cron 还是客户已有系统，运行哪些 Job、频率如何；
- 哪些 provider/source 需要正式身份授权，允许哪些 actions；
- 哪些 Customer Workflows 要启用，分别有哪些客户 status/label/project/approval 语义；
- 每个目标代码仓库如何取得 checkout、配置依赖和按自身 Git policy 交付。

这些答案进入 Jarvis repo 的 runtime governance、Customer Workflows、Runtime Foundation 配置、repo-local skills 或 Construction Workspace evidence；不会进入 `jarvis-box` 的“Jarvis context”。
