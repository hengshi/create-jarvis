---
name: {{SKILL_NAME}}
description: >
  {{PRODUCT_IDENTITY}} 版本发布说明生成。从已授权的 release source route 确认 release identity、
  变更边界、目标受众和发布状态，收集证据并生成可追溯的发布说明。
---

# {{PRODUCT_IDENTITY}} 发布说明

为 {{PRODUCT_IDENTITY}} 生成版本发布说明。所有路由信息、状态语义和分类约定在 START 阶段从已授权的 release source route 获取。

## 强制预读

- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`
- `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`
- `{{COMPANY_SLUG}}-jarvis/references/redaction-rules.md`
- END 写回时：`{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md`

## START → WORK → VERIFY → END

### START

1. 从已授权的 release source route 确认本次发布的完整身份：
   - release identity（版本号、发布名称或等效标识）
   - 纳入的变更边界（已确认进入本次发布的具体 change 范围）
   - 目标受众
   - release source 定义的发布状态
   - canonical target 及其写入入口
   - 既有语言、分类体系和格式约定（从 canonical target 或已有发布说明提取）
   - 允许的写回与发布动作
2. 任一关键信息缺失时，先在已授权的 source route、release 记录和既有发布规范中穷尽搜索；仍无法确认的项再向对应 authority 请求，不猜测。
3. 发布范围、authority 或发布状态尚未确认时，标记为 blocked，向对应的 release workflow 取证。

### WORK

1. 从所有已授权的 release source 收集实际纳入的 change records 和证据指针；具体记录类型和查询入口从 source route 获取。
2. 按稳定的 change identity 对收集到的变更去重。
3. 对每条候选条目读取足以确认用户或运维影响的内容——不只依赖标题、标签或分类标记。
4. 只使用 canonical target 已确认的分类体系和措辞风格组织条目；change 类型从实际证据和该分类 contract 推导。
5. 每条条目标注确认状态：confirmed included、not included、unverified。
6. 只为有证据支撑的条目生成对应 section；不生成空 section。
7. 被 canonical taxonomy 识别为高影响的 claim，必须包含直接证据指针和受众需要的行动说明。
8. 按 redaction-rules 处理敏感信息。

### VERIFY

1. 每条 claim 可追溯到具体证据指针。
2. 整体 coverage 与 release source 声明的变更 scope 对齐。
3. 无重复条目、无越界内容、无未发布内容被标记为已发布。
4. 目标受众能从每条条目理解影响与必要行动。
5. 所有引用可解析。
6. 按 canonical target 的契约检查 target diff 或 preview。
7. 未实际执行写回或发布时不声称完成。

### END

1. 按 source route 将发布说明写回或发布到 canonical target。
2. 若 target 为 repo，进入其 repo-local 的 docs/review contract。
3. 记录交付物：release identity、target 位置、证据集、publication status、unverified 或 blocked 项、下一步动作。
4. 稳定且可复用的 release routing 或 taxonomy 变化按 writeback-governance 回填；普通发布说明生成不触发 no_skill_gap。
