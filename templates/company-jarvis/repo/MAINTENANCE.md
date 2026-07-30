# {{COMPANY_NAME}} JARVIS 维护指南

JARVIS 是 {{COMPANY_NAME}} 的公司级语义、路由与工作流层。它帮助 Agent 理解公司并进入
正确的事实源或代码仓库，但不镜像原始内容，也不保存 repo 内部的工程执行真相。

## 目录职责

| 目录 | 保存 | 不保存 |
|---|---|---|
| `modules/` | 业务/产品模块的目的、边界、依赖和证据入口 | 源代码实现细节 |
| `sources/` | 文档、工单、数据系统等事实源的访问与检索路由 | source 正文镜像和凭据 |
| `skills/` | company entry 与跨 repo/source 的 workflow | repo-local 命令、测试和架构细节 |
| `references/` | 跨任务稳定的公司级路由与治理规则 | 临时任务笔记和会话日志 |
| `cross-cutting/` | 跨模块关系和版本/产品契约 | 单模块内部实现 |
| `evals/` | company workflow 自身的行为验证案例 | repo-local 学习的历史 episode |

repo execution truth 留在相应代码仓库的 repo-local skills。repo-local 学习的进度和
replay 证据留在它自己的任务目录，不进入 company Jarvis。

内容归属冲突时先读取 `references/knowledge-layer-contract.md`。

## 每次维护

### START

- 明确触发任务、允许修改的范围和事实 authority。
- 先读取目标文件与原始 evidence pointer，确认内容仍然有效。
- 判断信息的 primary home；repo-specific 内容只建立入口 pointer，不复制正文。

### WORK

- 只更新闭合当前事实或路由缺口所需的最小内容。
- 新旧事实冲突时保留双方 evidence，标记 `needs-owner-confirmation`，不猜测覆盖。
- 未确认内容写 `UNRESOLVED` 并说明所缺证据。

### VERIFY

- 检查新增事实能回到仍可访问的 authority pointer。
- 检查入口和跨文件链接可用。
- workflow 变化用一个真实任务或等价行为 case 验证；不能只因文件存在就声称有效。

### END

- 记录本次修改、验证证据、未解决冲突和下一动作。
- 若发现的是 repo 内执行知识，把信号交给相应 repo，而不是写入 company Jarvis。
- 若现有内容已经足够，不为了留下痕迹而扩展文件。

## Primary home

| 内容 | Primary home |
|---|---|
| 当前任务的一次性观察 | task-local 记录 |
| repo 内命令、架构、测试、实现陷阱 | 对应 repo-local skill |
| 公司/产品语义、module 边界、跨 repo 路由 | company Jarvis module/reference |
| source 的访问、检索、freshness、redaction | `sources/<name>/README.md` 或公司专属 source skill |
| 跨 source/repo/角色的闭环 | company workflow skill |
| 公司无关的通用方法 | 上游 method skill |

只有另一层必须发现该内容时才建立简短 pointer；不要复制同一事实形成多个权威版本。

## 常见更新触发器

| 事件 | 预期动作 |
|---|---|
| 公司、产品或 owner 边界变化 | 更新 identity/routing，并保留 authority pointer |
| 新 module 或 source 纳入授权范围 | 新增对应 route contract |
| repo 角色或入口变化 | 更新 canonical repo fleet 与 company entry route |
| 跨 repo workflow 变化 | 更新对应 workflow skill 并验证真实闭环 |
| repo 内部执行方法变化 | 不在这里维护；路由到 repo-local owner |
| 来源无法访问或事实冲突 | 标记 unresolved/blocker 和恢复条件 |

## Construction 与日常维护

活跃构建或演进旅程的范围、证据扫描和下一动作记录在其外部工作卡中，不在本 repo 建立另一套 construction state。旅程结束后，本文件就是
日常维护入口。外部工作卡负责旅程恢复；正式 managed runtime 的进程、session、
retry 和运维恢复遵循该 runtime 自己的公开 contract 与 operator runbook。
