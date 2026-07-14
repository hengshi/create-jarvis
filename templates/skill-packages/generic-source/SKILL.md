---
name: {{SKILL_NAME}}
description: >
  {{SOURCE_NAME}} 源访问助手。负责路由、访问状态、精确检索、证据指针、脱敏、允许的写回和阻塞恢复。不承载 repo-local 执行真相。
---

# {{SOURCE_NAME}} 源访问

此 skill 是 source-helper，不是 repo-local skill。唯一事实入口为 `{{COMPANY_SLUG}}-jarvis/sources/{{SOURCE_NAME}}/README.md`。

只负责：
- 路由与访问状态
- 精确检索与证据指针
- 脱敏边界
- 允许的写回操作
- 阻塞恢复条件

不负责：
- Git repo 的目录布局、build/test/run 命令、runtime 前提——这些由该 repo 的 `skills/SKILL.md` 承载
- 复制源内容到 Jarvis

## START

1. 读取 `{{COMPANY_SLUG}}-jarvis/sources/{{SOURCE_NAME}}/README.md`，确认源类型、访问方式、认证入口和当前访问状态。
2. 从 README 获取本次查询的具体检索入口（clone URL、API endpoint、文档路径等）。
   如 README 中未填实，记录阻塞状态和恢复条件，停止执行。
3. 如源尚不可访问（`needs-access` / `needs-credentials` / `request-pending`），记录阻塞状态和恢复条件，停止执行。

## WORK

1. 逐字执行 route 中记录的检索方法；不要擅自替换工具、host、认证方式或 endpoint。
2. 认证失败时记录实际错误和 route 中的恢复条件，不要假设凭据类型，也不要猜测内容。
3. 记录检索证据：

```
source: {{SOURCE_NAME}}
pointer: <repo-relative path / document ID / URL path>
retrieval: <执行的命令 / API 调用 / 浏览器导航>
observed: <日期 / commit hash / 文档版本>
```

4. 输出前执行脱敏：不复制源原文、凭据、PII、内部地址。命中文档中的 secret 时只说明已发现受限信息，按 redaction 处理。
5. 如需写回，按 `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md` 判断目标位置和权限。

## VERIFY

验证按任务风险选择，不预设各项都必须执行：
- 检索结果与查询目标是否匹配
- 证据指针是否可复现
- 敏感信息是否已脱敏
- 如写回已执行，确认写入内容正确

## END

1. 输出查询结果摘要和证据指针，不复制源原文。
2. 如出现 self-improvement signal，先判断现有 guidance 是否已经足够；足够时记录 `no_skill_gap`，不扩张 skill。
3. 如有可复用、可验证的持久知识需写回，按 `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md` 选择唯一 primary home：
   - 源访问/查询/脱敏规则 → 本 source skill
   - repo 命令/路径/架构 → repo-local skill

## 边界规则

1. 此 source skill 是路由，不是缓存。所有原始内容保留在源处。
2. 证据记录检索方式和观察结果，不复制源内容。
3. 访问被阻塞时记录 `needs-access`，不猜测内容。
4. Source-detected 身份不等于公司身份——记录在身份核实清单中。
