---
name: {{SKILL_NAME}}
description: >
  通过 curated job catalog 选择 Jenkins job，收集参数，确认风险操作，执行并跟踪构建状态。不预设特定 CLI 工具或 Jenkins 实例参数。
---

# Jenkins Job Builder

此 skill 是 agent 操作指南，不是运行时实现。使用 source route 已确认的 Jenkins 执行面和 curated job catalog。

## 前置条件（必须检查）

执行前必须逐个检查，任一不满足即停止并返回明确 blocker：

1. **Catalog 非空**：`jobs/registry.json` 的 `jobs` 数组不能为空。空 catalog 表示 jobs 尚未填充，停止执行。
2. **Source route active**：从 `{{COMPANY_SLUG}}-jarvis/sources/<jenkins-source>/README.md` 获取 Jenkins base URL、认证入口和 CLI 工具路径。
3. **Execution command / first proof 已填实**：source route 中必须提供可用的认证验证命令。如缺失，返回 blocker，不能猜测 job 或命令。

## 文件

- `jobs/registry.json`：sanitized Jenkins job catalog。选 job 前必须读。根对象有 `jobs` 数组。

## Execution Surface

CI 工具和执行命令从 source route 获取，不在本 skill 预设实现。

在运行任何 Jenkins 操作前，按 source route 中指定的工具验证连接和认证状态。如工具不可用，告知用户并请求安装或提供批准的本地执行路径。如认证缺失，引导用户本地认证，不要将 token 贴入聊天。

不要 echo Jenkins token。不要把 token 写入此 skill 目录。

## START → WORK → VERIFY → END

### START

1. 读取 `jobs/registry.json`，确认 catalog 非空且有匹配 job。
2. 读取 `{{COMPANY_SLUG}}-jarvis/sources/<jenkins-source>/README.md`，获取 base URL、认证入口、first proof 命令。
3. 执行 first proof 验证连接可用。
4. 从用户 artifact 和 catalog 的 `scene` 识别请求类型，不另造一套固定 taxonomy。

### WORK

1. 从 `jobs/registry.json` 的 `jobs[]` 中按 `aliases`、`keywords`、`scene` 和用户措辞匹配候选 job。
2. 如多个匹配，展示足以消除歧义的最小候选集合，含 `displayName`、`jobPath`、`scene`、`riskLevel` 和匹配原因。
3. 检查选中 job 的 `params`。参数只来自：
   - catalog 中的参数定义
   - job live inspection（如 source route 支持）
   - 用户在 START 中提供的值
4. 默认值只能来自 live job 检查或 catalog evidence——不预设固定默认值。
5. catalog 或 live inspection 标为高风险、生产变更或破坏性的执行，必须展示精确 job、参数和目标并获得用户显式确认；只读查询不要求执行确认。
6. 按 catalog 中的 `commandTemplate` 组装并执行命令。

### VERIFY

1. 读取 queue/build status——触发成功不等于构建成功。
2. 如可访问，读取构建日志摘要。
3. 报告实际构建状态。

### END

1. 报告实际状态和 pointer（job path、build number/URL、status）。
2. 不持久化 token 或凭据。
3. 只有 catalog/route 的 durable gap 被实际执行证据暴露时才做 `no_skill_gap` / skill update 判断；普通 job 执行不制造 skill 决策。

## Catalog Contract

每个 `jobs[]` 条目只保存经 source evidence 验证的选择与执行元数据：

- `displayName`、`jobPath`、`aliases`、`keywords`、`scene`
- `params`：参数名、是否必填、live/catalog evidence 支持的默认值及风险
- `riskLevel`、`confirmationRequired`
- `commandTemplate`：由 source route 已确认执行面支持的 task-time 参数模板
- `sourceEvidence`：job inspect/API pointer 和观测版本/时间

缺任一执行所需字段时，该 job 不可执行；不要用相似 job 的字段补齐。

## Answer Pattern

准备执行时：

```text
我准备执行这个 Jenkins job：
- Job: <displayName>
- Path: <jobPath>
- Risk: <riskLevel>
- 参数:
  - KEY=value

风险点:
- <only if relevant>

回复 `确认` 后我再执行。
```

执行后：

```text
已触发 Jenkins:
- Job: <jobPath>
- Build/Queue: <number or URL>
- 当前状态: <status>

后续查询按 source route 中指定的 CLI 工具执行。
```

## Guardrails

- 高风险、release、deploy 或破坏性 job 未经显式确认不执行。
- 不发明 job 名称。先用 catalog，catalog 过期或不完整时才按 source route 中的方法查询 live Jenkins。
- 不隐藏默认值——展示将要使用的默认值。
- 不让用户把 Jenkins token 贴入聊天；优先本地认证。
- 不把 Jenkins 凭据持久化到 skill 目录。
- 不向 catalog 添加原始 Jenkins job 快照、webhook URL、host IP、账号名、凭据默认值或一次性备份文件名。
- 不为此流程构建自定义 JS/Python 运行时。
