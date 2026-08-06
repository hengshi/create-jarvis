# Create Jarvis 的目标

客户从一句自然语言请求开始，由自己已经授权的 Host Agent 持续建设并最终得到：

1. 从模板初始化、由客户拥有并发布在其 GitHub 或 GitLab 上的 `<company-slug>-jarvis`；
2. 基于客户文档、代码和工作系统证据构建的公司级 modules、cross-cutting、skills、references、tools 以及跨 runtime 宪法；
3. 在每个客户代码仓库内，经真实历史 episode 验证并按该仓库 Git policy 交付的 repo-local skills；
4. 下载、安装并启动的 jarvis-box 正式数字员工，以及完成客户授权和上岗引导的首个 workflow。

## 不变的所有权模型

除非 review 发现逻辑错误，建设始终遵循以下边界：

| Owner | Owns |
|---|---|
| `create-jarvis` | 通用建设方法、模板、步骤、证据门槛和恢复协议 |
| Construction Workspace | 当前客户建设旅程的 task cards、checkpoint、journal、evidence 和恢复入口 |
| `<company-slug>-jarvis` | 客户公司知识、跨 runtime 宪法、路由、sources、workflows 和公司级工具 |
| 客户代码仓库 | 该仓库的执行真相与 repo-local skills |
| `jarvis-box` | 正式 runtime 的二进制实现、injected execution contract、control plane、运行状态和 operator runbook |

`create-jarvis` 不复制或重新定义 jarvis-box 内部实现。Company Jarvis 中的
`runtime-governance.md` 也不是 jarvis-box runbook；它是客户所有 runtime 和 Agent 都必须遵守的
公司级执行宪法。

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

- Part 1 从模板建立并发布 Company Jarvis 的最小骨架；
- Part 2 从客户明确提供的材料构建公司级知识和 runtime governance；
- Part 3 为每个客户代码仓库分配独立、可长时间运行、可恢复的学习任务；
- Part 4 通过 jarvis-box 的公开 release/runtime 接口完成下载、安装、启动和 onboarding。

Part 2 与 Part 3 可以并行。Part 4 必须等待 Reconciliation Gate，并且至少有一个 route-scoped
workflow 达到 `construction-ready`。并发只是效率手段，不要求客户开多个终端。

## Runtime governance 的成熟过程

`runtime-governance.md` 是 Part 1 和 Part 2 的重要产物：

```text
template scaffold
  → customer runtime discovery
  → customer-specific constitution
  → installed and verified runtime behavior
```

模板提供必须回答的结构，不伪造客户事实。Part 2 要从客户真实 Host runtime 和组织约束中确认
canonical runtime root、repo cache/workspace、同步入口、稳定工具、checkout 隔离、handoff、清理、
凭据与写入边界。若这些规则依赖尚不存在的客户 runtime 工具，Part 2 还要创建、安装并验证它们；
做不到时明确标记 `pending-runtime-foundation`，不能只写一篇看起来完整的说明。

Part 4 只消费 jarvis-box 的公开能力。安装后观察到的稳定 runtime 事实可以回写 Company Jarvis
宪法，但不得把 jarvis-box 的 injected contract、control plane 或 operator runbook 复制进去。

## 两种使用模式

Company Jarvis 构建完成后支持两种模式，由 `env.sh` 自动检测 `jarvis-box` 是否存在来切换：

### Mode B：jarvis-box 协同（构建目标）

这是 create-jarvis 的构建产出。jarvis-box 接管 workspace 和 repo-cache（`~/.jarvis-box/`），
hengshi-jarvis runtime foundation 负责 scheduler 定义、稳定工具和知识层（`~/.hengshi-jarvis/`）。
维护和自改进任务通过 `jarvis-box tasks create` 注册为正式 Task，在 `jarvis-box tasks list` 中可见。

### Mode A：独立使用（可选）

构建完成后，客户可以在任意无 jarvis-box 的机器上单独安装 hengshi-jarvis runtime foundation。
此时 `env.sh` 检测不到 `jarvis-box`，自动将所有路径（workspace、repo-cache）保留在
`~/.hengshi-jarvis/` 下自行管理。个人电脑上的 agent 可直接使用 Company Jarvis 的 skills、
references 和 tools，无需 jarvis-box。

客户切换方式：在已构建完成的 Company Jarvis 机器上运行 `~/.hengshi-jarvis/bin/pullall`，
然后将整个 `~/.hengshi-jarvis/` 目录复制到目标机器，source `env.sh` 即可。

## 中断与恢复

每个客户旅程都有独立 `jarvis-build/` Construction Workspace。它保存一个恢复入口、一个协调
journal、共享建设上下文、每个部分或代码仓库的独立 work card，以及可复核 evidence。

恢复不依赖原对话或某个 Agent 进程仍然存活：

1. 读取 `CONTINUE-JARVIS.md` 和固定的 method commit；
2. 读取 journal 与当前 work card；
3. 核验文件、Git remote/ref、外部交付和 jarvis-box 实际状态；
4. 确认旧 writer 是否仍然存活；
5. 活着则重新连接，已结束才替换，writer ownership 不明时禁止启动重复 writer；
6. 从最后一个已验证 checkpoint 的 `Next` 继续；
7. 在暂停、换人或完成前更新 card 和 journal。

这些都是供 Agent 和客户阅读的普通 Markdown 事实，不是 parser、daemon、heartbeat 或 phase 状态机。

## Repository learning 的本质

学习单位是完整、可重放的真实工作 episode，不是单个 commit 或 commit message 分类：

```text
visible START
  → pre-change baseline replay
  → hidden real outcome comparison
  → no_skill_gap / minimal skill delta
  → same-case rerun
  → adjacent regression
```

每个代码仓库有自己的 work card、writer、workspace、branch、delivery ref 和恢复点。扫描 worker 只返回
evidence packet，不能写共享目标。只有证明行为改善的 repo-local delta 才保留。

## 从 construction 到上岗

四部分建设不是一次性生成结束。Workflow 按证据成熟：

```text
draft-template → construction-ready → runtime-deployed
               → ready-for-shadow → shadowing → active
```

没有后续真实任务时，诚实停在 `ready-for-shadow`。不能凭初始请求制造生产证据，也不能替客户完成
最终业务批准。

## 权限模型

Host Construction Agent 与正式 Jarvis Agent 都是高权限执行主体。正式 jarvis-box 容器以 root 运行，
独立 identity 用于审计、轮换和撤销，不是业务降权机制。

- Host Agent 使用客户当前明确授权的身份建设资产；
- 正式 runtime 使用独立、可审计、可轮换、可撤销的高权限身份；
- 人类 Host home、SSH Agent 和凭据不会被整体复制进正式 runtime；
- Docker socket 等价于宿主机 root 能力，只有客户明确授权才启用；
- IM provider 原生凭据只属于 connector。

## 最终客户体验

客户只参与无法从证据判断的业务选择、授权 checkpoint、Git review/approval 和真实 shadow 验收。
中断后，客户只需要告诉新的 Host Agent Construction Workspace 路径并要求继续；客户不需要理解
phase、cursor、oracle、baseline、eval 或内部进程命令。
