---
name: {{SKILL_NAME}}
description: >
  通过 Outline API 访问内部知识库。从对应 source route 读取 base URL、认证入口和允许操作后执行文档检索与导出。仅在 Phase 6 已确认 Outline source/API 时创建。
---

# Outline API 访问

此 package 仅在 Phase 6 已确认 Outline source/API 时创建。

它适用于：
- 已知 Outline 文档 URL，需要拿正文
- 需要搜索内部文档标题/正文
- 需要从 share URL 反查 `documentId`
- 需要导出 Markdown 再继续抽取环境信息、服务信息、运维说明

它不负责：
- 管理 Outline 内容结构本身的长期治理
- 代替跨 repo 路由

## 强制预读

- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`

## 前置条件

- Outline base URL 和认证入口从 `{{COMPANY_SLUG}}-jarvis/sources/<outline-source>/README.md` 获取，不硬编码。
- API credential 的存储位置和获取方式以 source route 为准；不在本 skill 规定机器本地保存路径。
- 不要打印 token 明文；只读取、使用，必要时只显示长度或前缀掩码。
- 如 token 缺失，按 source route 中的指引获取；不要猜测 API 是否可用。

## START → WORK → VERIFY → END

### START

1. 读取 `{{COMPANY_SLUG}}-jarvis/sources/<outline-source>/README.md`，获取：
   - base URL
   - 认证入口（token 获取方式、环境变量名等）
   - 允许的操作
   - first proof 方法
2. 验证 token 可用：执行 auth.info 或等价的认证验证（具体命令以 source route 为准）。
3. 如认证失败，停止执行，不继续猜测搜索/导出问题。

### WORK

1. 标准 API 方法（执行前以 route/当前 API 文档为准）：
   - `auth.info`：验证 credential 和当前调用身份
   - `documents.list`：列文档，获取 `id`、`title`、`url`、`urlId`、`collectionId`
   - `documents.search` / `documents.search_titles`：按关键词搜索
   - `documents.info`：读取文档详情（`title`、`url`、`updatedAt`、`text`）
   - `documents.export`：导出 Markdown 正文（返回 JSON，正文在 `data` 字段）
2. Share URL 解析：从 URL 提取 `urlId`，用 `documents.list` / `documents.search` 匹配，获取 `documentId`，再读详情或导出。不执行全量 dump。
3. Base URL、token、document id 是 task-time 环境变量或参数，不由 skill 硬编码。
4. first proof 只证明鉴权/API 可用，不证明文档内容正确。
5. 命中文档中的 secret（数据库密码、access key 等）时只说明已发现受限信息，按 `{{COMPANY_SLUG}}-jarvis/references/redaction-rules.md` 处理。不提取、展示或写回敏感信息。

### VERIFY

1. API 响应状态正确。
2. 检索结果与查询目标匹配。
3. 敏感信息已脱敏。

### END

1. 输出查询结果摘要和证据指针（document id、title、version/updatedAt），不复制整篇正文。
2. 如提取的环境信息需后续复用，优先保存到 session artifact / temp file，不默认写回仓库。
3. 只有用户明确要求时，才把 durable knowledge 按 `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md` 回填。
4. 只有出现 self-improvement signal 时才做 `no_skill_gap` / skill update 判断；普通文档检索不需要制造 skill 决策。
