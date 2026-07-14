---
name: {{SKILL_NAME}}
description: 写或修改耐久文档时使用——README、API 文档、workflow skill、source-route 文档、产品说明等，尤其在聊天、issue、review 之后，当前线程上下文容易泄漏进正文的场景。
---

# 分支中立文档

耐久文档写给脱离当前会话的长期读者，不写给刚参与对话的人。

## Trigger

写或修改长期文档。输入通常来自聊天、issue、review、临时分析等容易携带线程上下文的材料。

不适用：时间线本身即为内容的文档——run log、comment、release note、postmortem——交给对应 workflow。

## START

先读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md` 和 `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`，再确认：

- **Canonical target source**：文档的权威存储位置与格式
- **写权限**：是否有权直接写入，还是需要该 source 已确认的审批流程
- **长期读者**：未来维护者、功能 owner、外部协作者——都没看过当前对话
- **文档职责**：这份文档承担什么判断 / 指引 / 契约职能
- **Authority / source-of-truth**：文档所依据的权威来源
- **Freshness**：现有内容是否已过期、需要更新还是新建

内容分类：

- **长期事实**：不随当前线程消失的规则、契约、边界
- **具名历史事实**：版本号、issue 编号、决策记录——仅在其 provenance 对长期读者有价值时保留
- **线程上下文**：当前聊天的纠错过程、临时结论、会话指代——一律剔除
- **推断**：基于当前材料的推断，标注推断依据或删除
- **敏感内容**：secret、PII、机器私有路径——一律不写

若 target 是 repo，进入对应 repo-local 的 docs / review contract。

## WORK

1. **先抽象，后举例**：先写契约、边界、判断逻辑；例子只支撑规则，不替代规则。
2. **去掉线程依赖**：凡需要当前对话才能理解的指代、纠错过程、临时结论，全部重写或删除。
3. **具名历史仅保留有用 provenance**：明确写出真实版本、artifact 或决策标识，不用"刚才那个""这次修复的"代替来源。
4. **Truth-bearing 内容从 source 验证**：链接、命令、路径、版本号，从授权 source 确认；未知不补全。
5. **不把一个 case 自动提升为通用规则**：只有证据足以说明可复用边界、验证方式和适用范围时才泛化。

按需读取公司参考：

- `{{COMPANY_SLUG}}-jarvis/references/redaction-rules.md`
- `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md`

## VERIFY

完稿后逐项检查：

- 脱离当前会话重读，仍可理解
- 删除所有例子后，规则仍成立
- 所有 material claim 有 source / authority
- 引用可解析：链接有效，路径存在，版本号准确
- 无 secret / PII / 机器私有路径 / raw dump
- 未把 task status、branch 暂态或本次 diff 写成永恒规则
- 文档与 canonical target 的现有结构、语言、contract 一致

## END

- 按 source route 和写权限交付；实际写回后才声称完成
- 记录 target、evidence、未解决项
- 判断是否需要 repo-local 或 {{COMPANY_NAME}} Jarvis writeback
- 普通文档编辑不制造 no_skill_gap
