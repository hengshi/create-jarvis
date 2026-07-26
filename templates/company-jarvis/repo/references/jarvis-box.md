# Jarvis Box — 使用者视图

**状态**：参考 | **版本**：1.0

---

## 是什么

jarvis-box 是 agent 任务的运行时环境。产品负责：

- **service 管理**：启停、健康检查、日志。
- **agent 路由**：当前 agent 的选择、启用、排序和诊断。
- **Task/Run 管理**（仅受管任务）：Task 生命周期、Run 证据、事件审计。
- **bootstrap handoff**：安装后的初始化信息传递。
- **day-2 诊断**：`doctor`、`monitor`、`logs`、`tasks verify/diagnose/reconcile`。
- **install-owned maintenance**：由当前 release 和 host scheduler 托管的 runtime sync、Jarvis maintenance、session self-improvement、Task workspace cleanup。

## 两种使用方式

### 直接 agent 对话（最常见）

用户安装完成后直接启动 codex/claude/copilot 对话执行工作。这不是 jarvis-box Task，不经过 Task/Run 生命周期。agent 在工作树内正常读写，jarvis-box 提供环境变量、agent 配置和观测命令。

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

Company Jarvis bootstrap 由用户在已登录 runtime agent 中直接启动；agent 使用 create-jarvis-skill 和根目录 `bootstrap-state.json` 开始或继续。它不是 Task continue/recover，也不复用旧 Run。

jarvis-box/install image 应提供 runtime agent CLI、可写 agent workspace 和正确 UID/GID/volume mapping，但不保存 agent vendor 登录凭据。Phase 3 继续之前，至少一个 agent CLI 必须已由用户完成认证并通过受控 prompt probe。

## 环境变量

以下变量由 jarvis-box 管理，值从当前环境、`bootstrap-state`、`init` 或 `status` 的 live 输出获取，不猜公司名或路径：

- `JARVIS_RUNTIME_ROOT`
- `JARVIS_ENV_FILE`
- `JARVIS_STATE_DIR`
- `JARVIS_WORKSPACE_ROOT`
- `JARVIS_LOG_DIR`

## 治理文档

按需阅读：

1. **[runtime-governance-quick.md](runtime-governance-quick.md)** — 会话预检速查。
2. **[runtime-governance.md](runtime-governance.md)** — 完整治理规范。
3. **[canonical-repo-fleet.md](canonical-repo-fleet.md)** — fleet 操作规范。
