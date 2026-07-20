---
name: {{SKILL_NAME}}
description: 写或修改 README、API 文档、workflow skill、source route、产品说明等耐久文档时使用，确保正文脱离当前聊天、issue、review 和分支上下文后仍然成立。
---

# Writing Durable Docs

耐久文档写给未来读者，不写给刚参与当前对话的人。

## Trigger

写或修改长期文档。输入通常来自聊天、issue、review、临时分析等容易携带线程上下文的材料。

不适用于时间线本身就是内容的 run log、comment、release note、postmortem；这些内容交给对应 workflow。

## START

先读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md` 和 `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`，再确认：

- canonical target source 和写权限
- 没看过当前会话的长期读者
- 文档承担的判断、指引或契约职责
- authority / source-of-truth
- 现有内容的 freshness

把输入分为长期事实、具名历史事实、线程上下文、推断和敏感内容。线程上下文必须重写或删除；推断要标注依据；secret、PII 和机器私有路径不得进入耐久文档。

目标位于代码仓库时，进入对应 repo-local docs / review contract。

## WORK

1. 先写契约、边界和判断逻辑，再用例子支撑规则。
2. 删除需要当前对话才能理解的指代、纠错过程和临时结论。
3. 历史事实使用真实版本、artifact 或决策标识，不使用“刚才”“这次”“前面”等线程指代。
4. 链接、命令、路径和版本从授权 source 验证；未知内容不补全。
5. 单个 case 只有在可复用边界、验证方式和适用范围均有证据时才提升为规则。

按需读取：

- `{{COMPANY_SLUG}}-jarvis/references/redaction-rules.md`
- `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md`

## VERIFY

- 脱离当前会话后仍能直接理解。
- 删除例子后，规则仍成立。
- material claim 有 source / authority。
- 链接可解析，路径存在，版本准确。
- 不含 secret、PII、机器私有路径或 raw dump。
- 没把 task status、branch 暂态或当前 diff 写成长期规则。
- 内容符合 canonical target 的结构、语言和 contract。

## END

- 按 source route 和权限交付，实际写回后才声称完成。
- 记录 target、evidence 和未解决项。
- 判断是否需要 repo-local 或 {{COMPANY_NAME}} Jarvis writeback。
- 普通文档编辑不制造 `no_skill_gap`。
