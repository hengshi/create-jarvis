# Create Jarvis 的目标与逻辑闭环

本文件是 `create-jarvis`、客户 Jarvis repo 与 `jarvis-box` 之间的唯一总纲。其他文件只能展开各自负责的步骤，不能重新定义所有权。

客户从一句自然语言请求开始，由自己已授权的 Host Runtime Agent 持续建设并得到一套可运行、可维护、可恢复的 Jarvis：

1. 一个从模板初始化、由客户拥有并发布到其 Git 服务的 Jarvis repo；
2. Jarvis repo 中基于真实证据构建的 modules、cross-cutting、skills、references、`runtime-governance.md` 与 Runtime Foundation；
3. 每个客户代码仓库内经真实历史 episode 验证并按该仓库 Git policy 交付的 repo-local skills；
4. 一个使用独立正式身份、持久 Agent HOME 和客户 Jarvis 能力的 jarvis-box Docker 服务，以及完成监督式 onboarding 的首个 workflow。

## 不变的所有权

| Owner | Owns | Does not own |
|---|---|---|
| `create-jarvis` | 通用建设方法、模板、Construction Workspace、证据门槛、恢复协议和 jarvis-box onboarding 方法 | 客户长期知识、客户 Runtime Foundation 的日常运行、jarvis-box 内部实现 |
| Construction Workspace | 本次建设的 work cards、checkpoint、journal、evidence 和恢复入口 | Runtime Agent 的配置、调度状态或业务运行状态 |
| Jarvis repo | 该套 Jarvis 的知识、路由、sources、workflows、跨 runtime 宪法和客户特有 Runtime Foundation | jarvis-box 的 Task/Run、control plane、execution contract 或 operator runbook |
| 客户代码仓库 | 该仓库的执行真相与 repo-local skills | 跨仓库知识和 Jarvis runtime 机制 |
| `jarvis-box` | Task/Run、Agent 执行、control plane、持久 runtime state/workspaces/logs、通用运行工具和 operator surface | Jarvis repo 的 clone/pull/sync/install/mount/校验、Jarvis 路由注入、客户 onboarding 状态机 |
| jarvis-box Docker image | jarvis-box、选定 Agent CLI、通用工具链、通用 runtime skills 和 connector binary | `create-jarvis`、任一客户 Jarvis repo、任一客户 Runtime Foundation |

Jarvis repo 的 `runtime-governance.md` 是所有使用这套 Jarvis 的 Agent 共同遵守的宪法。它不是 jarvis-box runbook。jarvis-box 不读取或解释它；Runtime Agent 通过自己的 skill discovery 机制发现已安装的 Jarvis entry 与 references。

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
  → supervised real work
  → evidence-driven evolution
```

- Part 1 从模板建立并发布 Jarvis repo 的最小骨架，其中包含待客户化的 `runtime-governance.md`；
- Part 2 从客户明确授权的文档、代码、工作系统与运行环境证据构建 Jarvis 知识和 Runtime Foundation；
- Part 3 为每个代码仓库分配独立、可长时间运行、可恢复的学习任务；
- Part 4 使用 jarvis-box 的公开 release 启动正式 Docker runtime，在该 runtime 的持久 Agent HOME 中 bootstrap Jarvis Runtime Foundation，然后引导客户完成授权、验证和首个监督任务。

Part 2 与 Part 3 可以并行。并发只是效率手段，不要求客户开多个终端。Part 4 只依赖可核验的交付事实，不引入 deployment manifest、context、lock 或 onboarding 状态机。

## Runtime Foundation 闭环

Runtime Foundation 是 Jarvis repo 针对一种 Runtime Environment 提供的最小维护机制。它负责：

- 从已批准的 Jarvis remote/ref 完成一次性 bootstrap；
- 在该环境的 Agent HOME 下维护 canonical repo cache、稳定入口、state 与 logs；
- 在 task start 执行快速同步，并由周期任务执行完整同步；
- 将 Jarvis skills/references 物化到 Runtime Agent 原生 discovery roots；
- 为维护任务提供可重复、可诊断、可重试的内部命令；
- 安装或生成该环境的 Scheduler Adapter。

它不要求把 Jarvis repo 挂载给 jarvis-box，也不要求 `JARVIS_HOME`。Git remote/ref 与认证只在 Runtime Foundation bootstrap/sync 边界使用。

```text
approved Jarvis remote/ref
  → one-time bootstrap in target Runtime Environment
  → canonical cache in persistent Agent HOME
  → stable inner jobs
  → Agent-native discovery roots
  → Runtime Agent discovers Jarvis entry
```

### 内部任务与外层调度适配

`pullall`、runtime sync、maintenance、self-improve 等内部 Runtime Job 只实现任务本身，对 Docker 无感：

```text
native scheduler ───────────────→ inner Runtime Job
host scheduler → Compose helper → same inner Runtime Job inside Docker
Runtime Agent already in Docker ─→ inner Runtime Job
```

- native 环境的 scheduler 直接调用内部任务；
- Docker 环境由宿主 scheduler 调用 jarvis-box release 提供的 Compose helper，在正式容器环境中执行同一个内部任务；
- 容器内 Runtime Agent 直接调用内部任务，禁止再次递归调用 Docker；
- 使用宿主调度时，完整 sync 以 `--skip-scheduler-update` 或等价参数运行，避免容器内安装第二套 scheduler；
- Runtime Job 把自己的 state/log 写进持久 Agent HOME；宿主 scheduler 只负责启动结果及“容器未能启动任务”这类外层错误；
- jarvis-box 二进制不读取宿主 scheduler 的日志。

Scheduler Adapter 属于 Jarvis Runtime Foundation；通用 Compose helper 属于 jarvis-box release。两者都不改变内部任务实现。

## Docker runtime 闭环

正式 Docker runtime 的关键持久边界是 Agent HOME，而不是 Jarvis 目录挂载：

```text
jarvis-agent-home volume (/root)
  ├── Agent identity/config
  ├── Agent discovery roots
  └── Jarvis Runtime Foundation cache/bin/state/logs

jarvis-box volumes
  ├── Task/Run state
  ├── workspaces
  ├── logs
  └── connector state
```

Part 4 的顺序是：

1. 下载并校验 jarvis-box public release，固定 OCI image digest；
2. 准备 deployment/runtime 配置和独立持久 Agent HOME，不绑定 Host HOME；
3. 先以 `read-only` 启动正式 jarvis-box 容器，在该持久 Agent HOME 中激活独立身份；
4. 通过 release helper 进入这个正式容器，运行 Jarvis repo 提供的 bootstrap；
5. 在容器内验证 stable sync、Runtime Foundation state/log 和 Runtime Agent 原生 skill discovery；
6. 在宿主安装 Scheduler Adapter，使其通过同一 release helper 进入同一正式 Runtime Environment；
7. 验证 jarvis-box 的 health、Agent、provider、Task/Run、persistence 和可选 connector；
8. 客户批准后把运行模式切为 `worker`、只启用已具备 Jarvis workflow 的业务 lane，并由 Host Runtime Agent 引导首个监督任务；checkpoint 写回 Construction Workspace。

jarvis-box 不知道 Jarvis repo URL、path 或 ref，不执行 Git checkout，不校验 Jarvis 内容，也不把 root skill 注入每次 Run。容器重建后，持久 Agent HOME 保留 Runtime Foundation 与 discovery roots；Jarvis 更新沿 `remote → cache → sync → discovery roots` 独立流动，jarvis-box image 更新沿 release 流程独立流动。

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

存在真实 issue、工单或讨论时，优先恢复当时可见的问题。链接失效、权限不足或根本不存在原始问题时，扫描 Agent 只能提交 evidence packet；另一个上下文隔离的 reconstruction Agent 根据 pre-change state、change diff、tests 与相邻历史反推最小问题陈述，并明确来源与不确定性。Replay Agent 只能看到该 reconstructed START 和截止时点允许的证据，不能看到真实改动结果。

每个代码仓库有自己的 work card、writer、workspace、branch、delivery ref 和恢复点。只有证明能改善未来行为的 repo-local delta 才保留。

## 中断、恢复与故障归属

建设恢复不依赖原对话或某个 Agent 进程仍然存活。Construction Workspace 记录最后核验事实、writer ownership、delivery、blocker 与 `Next`；恢复时重新核验实际文件、remote/ref 和外部运行事实后继续。

运行故障按 owner 恢复：

- construction 中断：Construction Workspace；
- bootstrap/sync/maintenance/self-improve 失败：Runtime Foundation state/log 与稳定入口；
- jarvis-box Task/Run 失败：jarvis-box state/control plane；
- Docker scheduler 无法进入容器：宿主 scheduler/operator log；
- provider/connector 失败：jarvis-box 或 connector 的 operator surface。

不创建一个跨产品 JSON 文件来重复、汇总或门禁这些事实。

## 尚需现场回答、但不破坏模型的问题

以下是每次部署的输入，不是逻辑漏洞：

- Jarvis remote/ref 与 bootstrap 凭据如何提供给一次性容器；
- 当前 Runtime Agent 的 discovery roots 是哪些；
- scheduler 使用 launchd、systemd、cron 还是客户已有系统；
- 哪些 provider/source 需要正式身份授权；
- 哪些 Runtime Job 存在、频率与 owner 是什么。

这些答案进入 Jarvis repo 的 runtime governance、Runtime Foundation 配置或 Construction Workspace evidence；不会进入 jarvis-box 的 Jarvis context。
