# 运行时治理速查

**状态**：强制 | **版本**：1.0

---

每次新会话执行任务前必须完成以下预检。若触发升级条件，转到 [runtime-governance.md](runtime-governance.md) 完整版。

## 会话预检

每次新会话的第一项任务前：

```bash
jarvis-box version
jarvis-box status
jarvis-box agent current
```

`jarvis-box version` 失败说明当前 shell 不可用，停止并修复安装或 PATH。需要探查 agent 实际能力时按任务需要执行 `jarvis-box agent smoke` 或 `jarvis-box agent doctor`。

## 路径确认

普通业务任务从当前授权 checkout、company entry 和 live `jarvis-box status` 确认路径。仍在 construction 期间时，任务目标和构件范围以外部 `BUILD-CONTEXT.md` 为准。静态 company repo 不保存 runtime root 或 method-pack 路径。

## 执行上下文识别

每次会话必须判定当前处于哪种执行上下文：

| 上下文 | 特征 | 处理方式 |
|--------|------|---------|
| 普通 operator checkout | 人工 clone 的工作树，无 Task 身份 | 合法；记录授权工作树，不伪造 Task 状态 |
| 已授权 repo checkout | 有明确授权记录的工作树 | 在授权范围内读写 |
| 受管 Task workspace | 存在可验证的 Task identity（task_id、workspace 路径与 Task 记录一致） | 按 Task/Run 生命周期处理 |

只有存在可验证 Task identity 时才应用 Task/Run 生命周期和受管 workspace 语义。用户完成安装后直接启动 codex/claude/copilot 对话构建或继续 Jarvis 是合法的——该对话不一定是 jarvis-box Task 或 Run，不得要求 Task pointer 或受管 Task workspace 才能开始工作。

## 写入边界

- 写入**仅在**当前授权 target 或 worktree 内进行。
- jarvis-box 管理的 env、service state、Task/Run artifact 及其识别出的 cache **不直接写**。
- agent 不直接修改产品状态文件或凭据文件。
- provider-native session handle（包括 Codex JSONL 的 `thread.started` / `thread_id`）属于 jarvis-box 私有 runtime 状态，不写入 company Jarvis 或公开 handoff；Task/Run identity 只使用 jarvis-box 实际返回的值。

## 升级到完整版的条件

以下任一触发时，必须阅读 [runtime-governance.md](runtime-governance.md)：

- 路径或身份冲突
- Task 五个生命周期操作（start/continue/stop/recover/retry-writeback）
- service 或 agent 配置变更
- install-owned managed job 的配置、失败或恢复
- fleet 维护操作
- 涉及凭据边界
- 跨 target writeback

service restart 只恢复服务能力，不继续旧 Task。只有 Task 已被 live 状态标记为 `recovery-required` 时，才按证据显式执行 `tasks recover`。
