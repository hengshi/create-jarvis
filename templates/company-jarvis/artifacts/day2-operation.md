# Day-2 Operations — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> 对应 Phase 14。接管并验证 day-2 运营状态，不重复实现 install-owned runtime。记录 install-owned 能力的真实状态、观测入口和恢复动作。前提 phase（11/12/13）未完成时只能写交接和待办，不能标 `completed`。

## Observed Runtime

- **jarvis-box version**: `<version from jarvis-box version>`
- **Runtime root**: `<path>`
- **Company Jarvis root**: <`bootstrap-state.paths.jarvis_target_home`>
- **Canonical entry**: `skills/{{COMPANY_SLUG}}-jarvis/SKILL.md`
- **Pilot repo fleet**: <pointers>

## Public CLI Evidence

以下命令已实际执行并记录输出（不含 secret）：

| 命令 | Exit | 输出摘要 | 观察时间 | 对应 capability |
|---|---|---|---|---|
| `jarvis-box version` | `<code>` | `<summary>` | | |
| `jarvis-box --help` | `<code>` | `<summary>` | | |
| `jarvis-box status` | `<code>` | `<summary>` | | |
| `jarvis-box doctor` | `<code>` | `<summary>` | | |
| `jarvis-box agent list --check` | `<code>` | `<summary>` | | |

> 公共 CLI help 只证明 command shape，不是能力清单。`jarvis-box doctor` 总体非零时按具体 finding 归属，不一律判所有能力失败。

## Install-owned Capability Status

逐项检查，每项分别记录五列维度。不得用单个模糊词（如 `configured`、`installed`）合并所有维度。

| 能力 | Install/Authority 证据 | 观测当前状态 | 最近执行证据 | Readiness | Owner & Recovery |
|---|---|---|---|---|---|
| service lifecycle | | | | | |
| agent registry / routing / failover | | | | | |
| Task lifecycle | | | | | |
| runtime sync | | | | | |
| Jarvis maintenance launcher | | | | | |
| session self-improvement | | | | | |
| workspace cleanup | | | | | |

**Readiness 取值**：

- `ready`：当前可用性已被直接观测。若某项实例相关操作尚未真实发生，最近执行证据可写 `unexercised`，但必须同时记录成功的非破坏性 readiness probe 和未执行原因；仅有 artifact/help 仍不够。
- `ready-with-explicit-alternative`：有明确替代机制（exact mechanism + owner + executability evidence）
- `unverified`：install 产物或 CLI help 存在但未观测到实际工作
- `blocked`：有已知问题，需写明恢复动作

**关键边界**：

- 产物存在、public help、version 输出或零活跃 Task 不单独证明能力已配置/工作。
- 零 Task 意为 `unexercised`，不是 `not-applicable`。
- 容器缺少 systemd 不使 service/jobs 变为 `not-applicable`：实际探测可用替代方案或标记 `unverified`/`blocked`。
- 真正的外部/人工替代需要 exact mechanism、owner 和 executability evidence。
- `bootstrap --resume` 只是 bootstrap state/form 恢复，绝不是 Jarvis maintenance authority。

## Managed Jobs

从当前 release docs / 安装产物、host scheduler 视图、job log / activity 确认实际存在的 managed jobs。

| Job | Product Owner | 触发机制 | 观测入口 | 最近状态 | 失败信号 | 恢复动作 |
|---|---|---|---|---|---|---|
| <job identity> | jarvis-box | <scheduler / external> | <log / status command> | | | |

> 公开 CLI help 不单独证明 host job 是否已安装或运行。不复制 install-owned 脚本到 company repo，不把内部脚本入口伪装成公共 CLI。

## Runtime Agent Prompt Probe

- **Agent check 方法**: `<jarvis-box agent list --check 或其他实际命令>`
- **真实 prompt probe invocation**: `<受控短 prompt 的 exact command，脱敏>`
- **真实 prompt probe evidence**: `<exit code + 非空响应 pointer/摘要；--help 和 agent list --check 不能替代>`
- **Probe 结果**: <agent 实际收到了 prompt 并正常响应，或 blocked reason>
- **Fallback agents**: `<optional backlog>`

## Company Owner / Escalation

| 职责 | Owner | Escalation | 状态 |
|---|---|---|---|
| Company Jarvis instance | | | confirmed / needs-owner-confirmation |
| Repo / source / workflow | | | confirmed / needs-owner-confirmation |
| 知识维护 | | | confirmed / needs-owner-confirmation |
| History replay | | | confirmed / needs-owner-confirmation |

> 允许同一角色承担多个责任，但每项必须可找到 owner 或 escalation。不强制 backup owner。

## Event / Cadence Triggers

| 活动 | 触发机制 | Owner | 输入 | 输出 | 失败信号 |
|---|---|---|---|---|---|
| 知识维护触发 | <event-driven / human-run / scheduler> | | | | |
| History replay 触发 | <event-driven / human-run / scheduler> | | | | |
| Source/repo inventory refresh | <event-driven / human-run / scheduler> | | | | |
| Writeback policy review | <event-driven / human-run / scheduler> | | | | |
| Acceptance drift 检查 | <event-driven / human-run / scheduler> | | | | |

> 允许 event-driven、human-run、host scheduler、external scheduler 等有 owner 的机制。不强制固定 cadence 或某种 OS scheduler。只有既无 install-owned 机制又无替代 owner/机制时才标 `blocked`。

## History Replay vs Session Self-Improvement 边界

- **History replay**：从已授权的 repo/issue/incident/delivery 历史构造 visible START/hidden oracle 校准 skills（Phase 12）。
- **Session self-improvement**：从真实 agent sessions 发现重复操作失败，用于持续改进。证据来源：agent session logs。
- 两者证据来源不同、执行阶段不同，不得互相替代。

## Company-owned Tools

- **Tools pointer**: `tools/README.md`（按字段登记 company-owned tools）
- 不生成 install-owned 工具的客户版副本。

## Failure / Recovery

| 故障类型 | 症状 | 恢复动作 | Owner |
|---|---|---|---|
| <type> | <symptom> | <recovery action> | |

## Day-2 Backlog

| 项目 | Layer | Owner | 证据 | 状态 | Next Action |
|---|---|---|---|---|---|
| <item> | runtime / source / repo / workflow / company / upstream | <owner> | <pointer> | planned / in-progress / blocked / done | |

## Cross-Artifact Consistency Review

> 在更新 Phase 14 状态前完成。检查以下文件之间无矛盾（如 `MAINTENANCE.md` 不能将 Phase 11-14 标为 pending 而根 state 标为 completed）：

| 产物 | 状态摘要 | 与根 state 一致？ | 备注 |
|---|---|---|---|
| `MAINTENANCE.md` | | yes / no | |
| `references/runtime-governance.md` | | yes / no | |
| `tools/README.md` | | yes / no | |
| `_bootstrap/day2-operation.md` | | yes / no | |
| `bootstrap-state.json` | | yes / no | |
| `bootstrap-result.json` | | yes / no | |

- **一致性审查通过**: `yes` / `no`
- **若 `no`**: <矛盾说明和修复动作>

## Final Status

- **Phase 14 status**: `completed` / `needs-input` / `blocked` / `failed`
- **Prerequisite phases status**: <Phase 11/12/13 的状态>
- **必要运营能力 readiness**: <每个必要能力为 `ready` 或 `ready-with-explicit-alternative`？若任何必要能力为 `unverified`，不得 completed>

## Next Action

- <next action>
