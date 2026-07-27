---
name: {{SKILL_NAME}}
description: >
  {{COMPANY_NAME}} 额外 workflow 的客户定制草稿。仅用于讲解、校准和验证客户真实流程；
  正文状态改为 active 前不得承接生产任务。
---

# {{COMPANY_NAME}} 通用兜底工作流

## 模板状态

**当前状态：`draft-template`**

这是客户额外 workflow 的改造起点。必须用客户真实 trigger、角色、source、repo-local skill、
policy 和 closure evidence 替换通用 fallback 假设，并通过至少一个真实或等价受控 case。
完成后才改为 `active` 并重写 frontmatter description；在此之前只能用于 workflow onboarding。

此 skill 仅在 generation plan 明确选择 fallback 时存在。它不是 specialized workflow 的替代品——一旦识别任务类型，立即路由到匹配的 workflow skill。

## 第一步：重路由

任何任务进入此 fallback 前，必须先通过当前已加载的 `{{COMPANY_SLUG}}-jarvis` company entry 重做 specialized workflow 路由。如果找到匹配的 workflow，退出此 fallback 并进入对应 skill。

## 强制预读

进入此工作流前必须读：
- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`
- `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`

涉及路由/所有权时加读：
- `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md`

END 阶段写回时加读：
- `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md`
- `{{COMPANY_SLUG}}-jarvis/references/minimal-closure-card.md`

## START → WORK → VERIFY → END

### START

1. 识别输入 artifact（issue、MR、diff、commit、文件路径、API 路径、error、stacktrace、failing test、screenshot、URL、reproduction entry）。
2. 从 artifact 提取症状和可观测差异，确定当前闭环。
3. 执行重路由检查——如已匹配到 specialized workflow，退出并进入对应 skill。
4. 如确实无匹配，写一行任务摘要：做什么、为什么、成功标准。
5. 记录已知假设和未知项。

### WORK

1. 收集最小必要上下文：artifact 本身 → 相关 source route → 相关 reference。
2. 在正确的 repo、source system 或 workflow surface 中执行。
3. 遵循 repo-local instructions，使用现有 helpers 和共享路径。
4. 记录检查了什么、发现了什么、做了什么、仍未知什么。
5. 跨 repo 边界时标明 handoff 点和 next owner。
6. 不随意扩大 rollout 范围。

### VERIFY

按任务风险选择验证方式，不预设每项任务都必须有测试、reproduction、rollback、截图或 MR：
- 对照原始 trigger 验证结果
- 收集可观测证据
- 如有代码变更，按目标 repo 的 `skills/SKILL.md` 选择与风险匹配的实际验证，并诚实记录未执行项
- 静态阅读不能作为运行时行为声明的唯一证据

### END

1. 输出结论、关键发现、验证证据、下一步。
2. 判断 `no_skill_gap`：
   - 现有 guidance 是否已足够？
   - 失败是否因缺失证据、源访问、运行时状态或一次性任务问题？
   - 此变更是否有助于未来任务？
   - 若否 → 记录 `no_skill_gap`，不增长 skill。
3. 如需写回，按 `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md` 选择唯一 primary home。
4. 闭合卡至少回答：当前闭环、首跳执行面、是否升级到 second hop、用什么证据判断、是否需要 durable knowledge writeback。

## 硬规则

- 第一步必须是重路由；能路由就退出 fallback。
- 所有 gate 通过后才能进入下一阶段。
- 无验证不持久写回。
- 不把 repo-local 执行真相提升到公司 Jarvis。
- 不把源代码、密钥、PII 写入 Jarvis。
- 不把一次性任务细节写成 durable skill；单个高影响 case 只有在证据完整、可复验时才可能成立。
