# Jarvis Box — 使用者视图

**状态**：参考 | **版本**：1.0

---

## 是什么

jarvis-box 是 Company Jarvis 建设完成后的正式 agent 运行环境。它不负责首次 construction。
产品负责：

- **service 管理**：启停、健康检查、日志。
- **agent 路由**：当前 agent 的选择、启用、排序和诊断。
- **Task/Run 管理**（仅受管任务）：Task 生命周期、Run 证据、事件审计。
- **Company context 注入**：把 deployment lock 固定的 Company/repo snapshot 注入业务任务。
- **day-2 诊断**：`doctor`、`monitor`、`logs`、`tasks verify/diagnose/reconcile`。
- **install-owned maintenance**：由当前 release 和 host scheduler 托管的 runtime sync、Jarvis maintenance、session self-improvement、Task workspace cleanup。

## 与 construction 的边界

客户最初用自己的 Host Agent 阅读 `create-jarvis` 并完成 Company construction、Repository
learning 和 workflow construction；该阶段不安装、不启动也不依赖 jarvis-box。

workflow 达到 `construction-ready` 后，Coordinator 才使用公开 release bundle 部署 jarvis-box、
正式 Agent identity 和 connector，固定 Company/repo commits、单一 jarvis-box image digest 与
内置 connector version/commit，并通过容器内 capability probes。connector 是独立服务和凭据
边界，但使用同一 image 中的内置 binary，不要求客户选择第二个 image。

## 两种正式使用方式

### 直接正式 Agent 对话

用户可直接启动已注入 Company context 的正式 agent 对话执行授权工作。这不一定是 jarvis-box
Task，不经过 Task/Run 生命周期。Agent 在授权工作树内正常读写。

### 受管 Task

由 jarvis-box Task 启动的会话，有明确的 task_id、workspace 和 Run 记录。此时应用 Task/Run 生命周期：Task 状态可查询、Run 证据可追溯、writeback 由产品管理。

**关键区别**：不要对普通 agent 对话要求 Task pointer 或 workspace——那是受管 Task 才有的概念。

## 稳定入口

以下入口用途稳定，具体参数以当前 `--help` 输出为准：

| 入口 | 用途 |
|------|------|
| `jarvis-box --help` | 命令可用性的权威入口 |
| `jarvis-box version` | 确认安装版本 |
| `jarvis-box init` | 打印 setup readiness snapshot 和已确认路径 |
| `jarvis-box status` | 运行时状态快照 |
| `jarvis-box doctor` | 健康检查（只报告，不修改） |
| `jarvis-box monitor` | 近期活动摘要 |
| `jarvis-box agent` | agent 配置（current/list/set/enable/disable/order/unset/doctor/smoke） |
| `jarvis-box tasks` | Task 管理（list/show/events/logs/verify/diagnose/reconcile/start/continue/stop/recover/retry-writeback/reap/clean） |
| `jarvis-box logs` | 服务日志查看 |
| `jarvis-box start/stop/restart` | 服务生命周期 |

Task 只有 `start`、`continue`、`stop`、`recover`、`retry-writeback` 五个生命周期操作。`reap`、`clean` 是维护操作；`reconcile` 只生成 dry-run 计划。service restart 不自动继续 Task。

当前 CLI 和 `--help` 是 command shape 的权威。install-owned managed jobs 的权威来自当前 release 文档/安装产物、host scheduler、`/server` crons 和 job logs。company Jarvis 不重新实现这些能力。

jarvis-box production image 提供 runtime agent CLI、Git/provider/source 工具、可写 workspace 和
持久化 agent home/state。正式容器按 root 运行；这不是低权限沙箱，正式 identity 应具备目标 workflow
所需的高权限，但凭据通过 provider/secret boundary 管理，不写入 Company repo。

## 环境变量

以下变量由 jarvis-box 管理，不从静态 Company repo 猜测：

- `JARVIS_RUNTIME_ROOT`
- `JARVIS_ENV_FILE`
- `JARVIS_STATE_DIR`
- `JARVIS_WORKSPACE_ROOT`
- `JARVIS_LOG_DIR`

## 治理文档

按需阅读：

1. **[runtime-governance-quick.md](runtime-governance-quick.md)** — 上下文与诊断边界速查。
2. **[runtime-governance.md](runtime-governance.md)** — 完整治理规范。
3. **[canonical-repo-fleet.md](canonical-repo-fleet.md)** — fleet 操作规范。
