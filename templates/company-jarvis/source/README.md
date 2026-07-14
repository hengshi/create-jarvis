# Source Route: {{SOURCE_NAME}}

> 路由合同：供 agent 到达、访问和引用此 source 的最小路由信息。本文件不是 source skill，不复制 source 内容。

## Identity

- **名称**: `{{SOURCE_NAME}}`
- **类型**: `BOOTSTRAP_REQUIRED`
- **Owner**: `BOOTSTRAP_REQUIRED`

## Access

- **Access 状态**: `BOOTSTRAP_REQUIRED`
- **Host**: `BOOTSTRAP_REQUIRED`（没有 host 的 source 写 `not-applicable`）
- **Location**: `BOOTSTRAP_REQUIRED`
- **Project / Repo 路径**: `BOOTSTRAP_REQUIRED`
- **默认分支**: `BOOTSTRAP_REQUIRED`（非 Git source 写 `not-applicable`）
- **认证入口**: `BOOTSTRAP_REQUIRED`（只记录登录入口或凭据类型，不记录凭据值）

## Retrieval

- **精确检索命令**: `BOOTSTRAP_REQUIRED`
- **Evidence pointer**: `BOOTSTRAP_REQUIRED`
- **Evidence version**: `BOOTSTRAP_REQUIRED`（commit、文档版本或观测时间，按 source 类型选择）

## Redaction

- **Source-specific redaction**: `BOOTSTRAP_REQUIRED`（没有额外约束时写 `none-observed`；凭据值、secret 和 PII 始终不写入）

## Writeback

- **可回写范围**: `BOOTSTRAP_REQUIRED`
- **禁止回写**: `BOOTSTRAP_REQUIRED`
- **回写治理引用**: `../../references/writeback-governance.md`

## Blocking & Recovery

- **Route 状态**: `BOOTSTRAP_REQUIRED`
- **阻塞条件 / 缺失输入**: `BOOTSTRAP_REQUIRED`（active route 写 `not-applicable`）
- **恢复条件**: `BOOTSTRAP_REQUIRED`
- **是否阻塞 first workflow**: `BOOTSTRAP_REQUIRED`
- **依赖的其他 source**: `BOOTSTRAP_REQUIRED`

## Phase 7 替换规则

- **可访问 source**：Phase 7 必须读取 source 并将所有临时占位替换为实际值；检索命令必须可直接执行，不得写省略号或伪命令。
- **不可访问 source**：将状态字段写为实际 deferred/blocked 状态，注明缺失输入、恢复条件和是否阻塞 first workflow，不保留临时占位。
- 不适用的字段写 `not-applicable`，搜索后仍未知的字段写 `unresolved` 并附已检查证据；不要为填满表格而编造。
