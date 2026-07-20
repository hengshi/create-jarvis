# Phase 14 — 第二天运营

目标：接管并验证 day-2 运营状态，不重复实现 install-owned runtime。检查 install-owned 能力的真实状态、记录观测入口和恢复动作，并明确 company-specific 的 owner、维护机制、writeback policy 和维护责任。

## 前置条件

- Phase 10 已交付。
- Phase 11/12/13 均已 `completed`。任一前置 phase 未完成时不进入 Phase 14，Phase 14 保持 `pending`，当前 bootstrap 从前置 phase 恢复。
- 客户 Jarvis owner 已指定，或 Phase 14 返回 `needs-input`。
- runtime root、company slug、company Jarvis repo path、pilot repo fleet 已知。

## 读取当前安装状态

先读取当前安装的真实信息，不依赖旧 reference 拓扑：

- `jarvis-box version`：确认版本；
- `jarvis-box --help` 及顶层和相关子命令 `--help`：确认公共命令 shape。CLI help 只证明公共命令 shape，不是能力清单。
- `jarvis-box doctor`：获取健康状态；
- `jarvis-box agent doctor` / `jarvis-box agent list --check`：获取 agent 状态；
- `jarvis-box status` / `jarvis-box monitor`：获取运行时状态。
- install 提供的 `jarvis-box-monitor` skill：生成当前 slot 的人类可读运行快照，并用上述 live 输出核对。

install-owned managed jobs 的事实来自：当前 release docs/安装产物、host scheduler 或 `/server` crons、job logs/activity。不能因为不在顶层 `--help` 就判不存在。

### 当前基线需要复核的关键边界

- 当前已确认的合同是 Task 只有五个 lifecycle operations：**start**、**continue**、**stop**、**recover**、**retry-writeback**。不要把某个历史版本号当作永久基线；先以当前安装版本的 `--help`、release contract 和 live 状态复核，发现差异就记录版本与差异。
  - `reap` / `clean` 是维护操作；
  - `reconcile` 是 dry-run；
  - service restart 不自动恢复 Task；
  - `recover` 仅用于 recovery-required 状态；
  - `bootstrap --resume` 只恢复表单/已确认状态，不是 task continue。
- `continue` 可以由 jarvis-box 使用已保存的 provider-native session handle 继续同一 agent 会话；该 handle 属于 runtime 私有状态。即使 Codex 输出 JSONL `thread.started` / `thread_id`，也不能把它复制到 company Jarvis、bootstrap artifact 或公开 handoff。
- Task 的 `task_id`、`run_id`、workspace 和 session 状态只记录 jarvis-box 实际返回或公开暴露的值。UI/feed 对 lane display id 的解析是产品内部兼容行为，不允许 agent 根据目录名、lane 名或字符串拼接自行生成 Task/Run identity。
- 对更新版本先读当前 help/release contract；如果语义发生变化，记录版本和差异，使用当前安装事实。
- 至少一个已认证且 prompt probe 可用的 runtime agent 足够继续。fallback agents 可以是 backlog。jarvis-box 不安装 vendor credentials。

## Install-owned 能力检查

以下能力由 jarvis-box install 托管，company bootstrap 不重新实现。逐项检查并记录真实状态、owner、观测入口和恢复动作。

每项能力分别记录以下维度（不得用单个模糊词合并）：

| 能力 | Install/Authority 证据 | 观测当前状态 | 最近执行证据 | Readiness | Owner & Recovery |
|------|----------------------|------------|------------|-----------|-----------------|
| service lifecycle | | | | | |
| agent registry/routing/failover | | | | | |
| Task lifecycle | | | | | |
| runtime sync | | | | | |
| Jarvis maintenance launcher | | | | | |
| session self-improvement | | | | | |
| workspace cleanup | | | | | |

**Readiness 取值**：

- `ready`：当前可用性已被直接观测。若某项实例相关操作尚未真实发生（例如当前没有 Task），最近执行证据可写 `unexercised`，但必须同时记录成功的非破坏性 readiness probe 和未执行原因；仅有 artifact/help 仍不够。
- `ready-with-explicit-alternative`：有明确替代机制（exact mechanism + owner + executability evidence）
- `unverified`：install 产物或 CLI help 存在但未观测到实际工作
- `blocked`：有已知问题，需写明恢复动作

**关键边界**：

- 产物存在、public help、version 输出或零活跃 Task 不证明能力已配置/工作。
- 零 Task 意为 `unexercised`，不是 `not-applicable`。
- 容器缺少 systemd 不使 service/jobs 变为 `not-applicable`：实际探测可用替代方案或标记 `unverified`/`blocked`。
- 真正的外部/人工替代需要 exact mechanism、owner 和 executability evidence。
- `bootstrap --resume` 只是 bootstrap state/form 恢复，绝不是 Jarvis maintenance authority。

## Runtime Agent

至少一个 runtime agent 需要真实 prompt probe：使用 agent CLI 的受控短 prompt，确认 agent 实际收到 prompt 并正常响应。`--help` 只能证明 executable/command shape，不证明认证后对话可用。`jarvis-box agent list --check` 是辅助检查，不能替代真实 prompt probe。

至少一个已认证、可用的 runtime agent 足够继续 bootstrap。缺少替代 agent 可以是 optional backlog，不是 bootstrap 的 missing input 或产品缺陷。

## Company-specific 内容

Company bootstrap 负责明确以下内容：

1. Jarvis owner；需要替代责任人时按客户政策登记。
2. repo/source/workflow owner。
3. escalation path。
4. 知识维护触发或 cadence。
5. history replay 触发。
6. source/repo inventory refresh。
7. writeback policy。
8. `MAINTENANCE.md` 完整性和更新触发。
9. company Jarvis 的 acceptance drift 检查。
10. company-owned tools 的登记和 owner。

允许 event-driven、human-run、host scheduler、external scheduler 等有 owner 的机制。不强制固定 cadence 或某种 OS scheduler。

只有既无 install-owned 机制又无明确替代 owner/机制时，对应项才标 `blocked`。

## 两个循环的边界

- **history replay**：从 repo Git 历史构造 visible START/hidden oracle 校准 skills（Phase 12）。
- **session self-improvement**：从真实 agent sessions 发现重复操作失败，用于持续改进。

两者证据来源不同、执行阶段不同，不得互相替代。

## 执行步骤

1. 创建或更新 `_bootstrap/day2-operation.md`（使用规范模板 `templates/company-jarvis/artifacts/day2-operation.md`）。所有 Phase 14 证据统一写入此文件，不再单独创建 `_bootstrap/day2-runtime-checks.md`。
2. 运行 `jarvis-box --help` 和相关子命令 help，确认命令真实存在。把每个实际检查写入 `_bootstrap/day2-operation.md`：exact command（不含 secret）、exit code、输出摘要、观察时间和对应 capability。
   只有实际执行的 CLI 调用才使用反引号命令格式，例如 `jarvis-box status`。安装文件、可执行文件、安装状态和 authority 证据必须写成文件路径或普通名词（例如“已安装的 jarvis-box executable”），不要写成 `` `jarvis-box binary` ``、`` `jarvis-box install` `` 这类不存在的 root command。
3. 确认本客户实际需要的 owner：Jarvis、repo/source/workflow、知识维护、history replay；同一角色可以承担多个责任，但每项必须可找到 owner 或 escalation。
4. 逐项检查 install-owned 能力，按能力表的五列维度分别记录：install/authority evidence、observed current state、last execution proof（或 unexercised）、readiness、owner & recovery。不得用单个模糊词合并所有维度。
5. 登记 managed jobs 到 `references/runtime-governance.md` 的 managed jobs section。确认 container/无 systemd 环境的替代调度安排。
6. 创建或更新 `tools/README.md`，按其字段登记 company-owned tools；不生成 install-owned 工具的客户版副本。
7. 更新 `MAINTENANCE.md`：cadence/触发条件、update triggers、runbooks、escalation。
8. 明确 company-specific 维护机制：知识维护、history replay、inventory refresh、writeback policy review、acceptance drift check。允许 event-driven/human-run/external scheduler 等有 owner 的机制。
9. 记录 day-2 backlog。
10. 在更新 Phase 14 状态前，执行跨产物一致性审查：检查 `MAINTENANCE.md`、`references/runtime-governance.md`、`tools/README.md`、`_bootstrap/day2-operation.md`、`bootstrap-state.json` 和 `bootstrap-result.json` 之间的状态一致性。例如 `MAINTENANCE.md` 不能将 Phase 11-14 标为 pending 而根 state 标为 completed。
11. 更新 `bootstrap-state.json` 和 `bootstrap-result.json`（按通用规则中的 phase 状态传递规则）。不复制大段 JSON state 字段逐项规则，引用通用规则即可。

## 状态判定

- `completed`：Phase 11/12/13 已完成；company-specific owner、维护机制、writeback policy 已明确；`_bootstrap/day2-operation.md` 已记录真实执行证据（含能力表五列维度）；每个必要运营能力的 readiness 为 `ready` 或 `ready-with-explicit-alternative`；跨产物一致性审查通过；`references/runtime-governance.md` managed jobs section、`MAINTENANCE.md`、`tools/README.md` 已更新；day-2 backlog 已记录。`unverified` 必要能力导致不能 completed。
- `needs-input`：进入 Phase 14 后，缺 owner、runtime root、scheduler policy、repo fleet 或 tool ownership。
- `blocked`：缺 runtime access、scheduler 不可用且无替代机制、security 不允许所需 job，或 install-owned 能力既无 install 托管也无明确替代 owner/机制。
- `failed`：复制私有脚本、写入 secret、安装未经批准 job、破坏 runtime，或重新生成 install-owned runtime 产品能力。

## 禁止

- 不重新实现 install-owned runtime 能力。
- 不把 doctor 总体非零时所有能力一律判失败——按具体 finding 归属。
- 不生成 install-owned 工具的客户版副本。
- 不复制 install-owned 脚本到 company repo。
- 公共 `jarvis-box` 命令必须能由当前 help 证明；install-owned job 则从 release/install/scheduler/log 证据确认，不能把其内部脚本伪装成公共 CLI。
- 前置 phase 未完成时根本不进入 Phase 14；Phase 14 保持 `pending`。
- 不创建单独的 `_bootstrap/day2-runtime-checks.md`——所有 Phase 14 证据写入 `_bootstrap/day2-operation.md`。
- 不把 `bootstrap --resume` 当作 Jarvis maintenance authority——它只是 bootstrap state/form 恢复。
- 不用 artifact presence、public help、version output 或零活跃 Task 单独证明能力已配置/工作。
- 不在跨产物一致性审查前更新 Phase 14 状态。

## 读物

- `GOAL.md`
- `acceptance.md`
- `playbooks/phase-checklist.md`
- `templates/company-jarvis/repo/MAINTENANCE.md`
- `templates/company-jarvis/repo/tools/README.md`
- `templates/company-jarvis/artifacts/day2-operation.md`
- `templates/company-jarvis/artifacts/controlled-writeback-log.md`
