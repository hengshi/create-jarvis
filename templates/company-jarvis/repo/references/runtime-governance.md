# 运行时治理 — 完整规范

**状态**：强制 | **版本**：1.0

---

## 1. 真值来源

agent 按事实域选择真值来源，不用一个来源覆盖另一个来源负责的事实：

1. **当前 CLI 输出与 `--help`** — 命令是否存在及其 command shape。
2. **bootstrap-state.json** — 当前 bootstrap 已确认的 company/method/target 路径与 phase 状态。
3. **live `jarvis-box init` / `jarvis-box status` / `jarvis-box agent current`** — readiness、服务和 agent 实时状态。
4. **source / repo contract** — source 访问与具体 repo 执行规则。

同一事实在这些来源间冲突时停止并记录冲突，不擅自选一个覆盖。静态本文不覆盖 live product 输出。

## 2. 执行上下文与写入边界

### 2.1 上下文判定

每次会话判定执行上下文（详见 [runtime-governance-quick.md](runtime-governance-quick.md)）：

- **普通 operator checkout**：人工 clone 的工作树，无 Task 身份。合法，记录授权工作树，不伪造 Task 状态。
- **已授权 repo checkout**：有明确授权记录的工作树，在授权范围内读写。
- **受管 Task workspace**：存在可验证 Task identity 时，按 Task/Run 生命周期处理。

用户安装后直接启动 agent 对话执行工作是**合法且预期**的使用方式。该对话不一定是 jarvis-box Task 或 Run。只有实际由 jarvis-box Task 启动的会话才应用 Task/Run 生命周期和受管 workspace 语义。

### 2.2 写入边界

| 区域 | 权限 | 说明 |
|------|------|------|
| 当前授权 target / worktree | 读写 | 代码编辑、构建产出 |
| jarvis-box 管理的 state/env/cache | 不直接写 | 由产品命令管理 |
| 凭据文件 | 不写 | 密钥和配置由运维管理 |
| 其他 target 或 worktree | 禁止 | 除非跨 target writeback 已明确授权 |

## 3. 命令分类

### 3.1 观测类命令（始终可用）

`version`、`status`、`init`、`doctor`、`monitor`、`logs`、`latest`、`agent current/list/doctor/smoke`、`tasks list/json/index/verify/diagnose/show/events/logs`。

### 3.2 Task 的五个生命周期操作

`tasks start/continue/stop/recover/retry-writeback` 是会改变 Task、Run 或 provider delivery 的五个产品操作。仅在 Task identity、授权、目标和恢复方式明确时执行。

- `continue` 在同一 Task 中创建后续 Run；它不是 bootstrap resume。
- `recover` 只用于 live 状态已确认的 `recovery-required` 进程观察链丢失。
- `retry-writeback` 只重试已有 provider delivery，不运行 agent，也不做 skill/file 写回。
- service restart 不推断旧 Task 应继续；需要恢复时由 operator 读取证据后显式选择生命周期操作。

### 3.3 配置与维护操作

`agent set/enable/disable/order/unset`、`tasks reap/clean`、`bootstrap jarvis`、`setup gitlab`、`start/stop/restart` 会改变配置、保留期或服务状态，但不增加 Task 生命周期操作。执行前确认授权范围、操作目标和失败恢复方式。

`tasks reconcile` 只生成 dry-run 计划，不执行计划中的 mutation。`bootstrap jarvis --resume` 只恢复 bootstrap 表单和已确认状态，不恢复 Task/Run。

## 4. 密钥与凭据

- 密钥、agent credentials、runtime state **不写入** company 或 repo artifact。
- jarvis-box 自身的 runtime 配置属于 `JARVIS_ENV_FILE` 或外部密钥管理器；agent vendor 的登录凭据由对应 CLI/keychain/外部凭据系统管理，jarvis-box 不安装或复制这些凭据。
- 不在 task-state、event、prompt、result、日志或 workspace 文件中暴露密钥。
- Private resume handle 不进入公共 artifact。

## 5. 分支真值

- repo 默认分支从当前 source route 对应的 remote HEAD 或 VCS metadata 获取，不假定 remote 名称，也不写死分支名。
- 工作修改在授权 working tree 内进行。
- cache 仅在 live product 确认时按其只读合同使用。

## 6. 会话交接

会话结束时只保留当前任务需要且有证据的 context。不设固定字段 schema——交接内容取决于任务实际需要和已确认状态。

交接只保留继续任务所需的信息，例如当前执行上下文、已确认路径、关键命令结果、未执行项和阻塞原因。

## 7. Install-owned Managed Jobs

jarvis-box release 可以通过主机或外部 scheduler 托管 runtime sync、company Jarvis maintenance、session self-improvement 和 Task workspace cleanup。它们是维护入口，不是隐藏的用户 Task 队列。

Phase 14 从以下证据确认当前版本和当前机器实际拥有的 jobs：

1. 当前安装版本及其 release 文档/安装产物；
2. host scheduler 或 `/server` crons 视图；
3. 对应 job log、最近 activity、退出状态和 artifact pointer。

每个实际 job 记录 identity、产品 owner、触发机制、观测入口、最近状态、失败信号和恢复动作。公开 `jarvis-box --help` 只证明 CLI command shape；它不单独证明 host job 是否已安装或运行。company Jarvis 不复制 install-owned 脚本，也不把内部脚本入口伪装成公共 CLI。

## 8. 会话关闭

结束时诚实记录：

- 实际执行的命令和状态
- 未执行项及阻塞原因
- 若有错误涉及 runtime root、Task identity 或 credential，标记为 blocked 并说明原因

不得伪造 Task event 或直接编辑状态文件来掩盖错误。发现越界写入或凭据暴露风险时，停止后续变更，保留可审计事实。
