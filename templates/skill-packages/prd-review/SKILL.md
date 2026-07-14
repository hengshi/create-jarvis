---
name: {{SKILL_NAME}}
description: >-
  {{COMPANY_NAME}} feature-delivery 闭环中的 PRD / spec review 阶段。将人类 PRD 转为 agent-ready implementation brief 和 reviewed spec，补齐跨 source 的实现约束与决策记录。NOT for：已可直接执行的 repo-local task、纯 bug 修复、单纯格式润色。
company: {{COMPANY_SLUG}}
product: {{PRODUCT_IDENTITY}}
version: "1.0.0"
---

# {{COMPANY_NAME}} PRD / Spec Review

此 skill 是 `feature-delivery` 内的规划评审阶段，不替代 repo-local 实现 skill，也不独立启动完整交付闭环。

## Trigger

进入此 skill 的条件：
- `feature-delivery` 判断输入尚未达到 implementation-ready，或用户明确请求评审 PRD/spec。
- 不触发的情况：目标是调查或修复 supported behavior 的纯 bug、已确认且可直接执行的 repo-local task、单纯的格式或措辞润色（不改变 scope/acceptance）。

## START：预检与登记

进入后首先完成：

1. **加载 company runtime 与质量预检**：
   - `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`
   - quick reference 触发升级时，再读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`
   - `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`

2. **登记 artifact 元信息**：
   - 原始 PRD/spec/artifact 的 pointer（来源、位置、格式）。
   - 版本或 freshness 标记（如有）。
   - 决策 authority：谁能对 scope、acceptance、tradeoff 做最终裁决。
   - 授权 source 及访问边界；另行记录此次评审的触发者或触发事件。

3. **标注输入内容**：为每个 material claim 标注所有适用状态：
   - **user goal**：用户或业务要达成的目标。
   - **problem evidence**：支撑问题存在的证据或数据。
   - **proposed solution**：提议的解决方案（不等于唯一方案）。
   - **confirmed decision**：已有 authority 确认的决策。
   - **assumption**：尚未验证的假设。
   - **unknown**：当前信息无法判定的内容。

## WORK：补事实、验证、形成评审

按以下流程执行，评审可在阻塞项关闭前反复进行，不设轮数上限：

1. **补充事实**：agent 必须先从已授权的 docs/repos/tests/issues/decisions/source routes 中自行查找事实。凡可通过已有 source 回答的问题，不得推回给人。
   - 路由方法参考 `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md`。
   - 证据矩阵参考 `{{COMPANY_SLUG}}-jarvis/references/verify-evidence-matrix.md`。

2. **验证现有契约与能力**：确认 PRD 所依赖的现有能力、契约、接口是否真实存在且版本匹配。发现矛盾或缺失时记录为证据，不猜测。

3. **形成结构化评审**：
   - scope / non-scope。
   - actors / scenarios。
   - acceptance criteria（可观察、可验证）。
   - 关键边界条件与失败条件。
   - 依赖 / fallout / rollout（仅在适用时记录，不强制虚构）。

4. **识别 capability owner 与 delivery surface**：按 company routing 确定谁拥有此能力、通过哪些 surface 交付和验证、可能的 execution source。不得按工程层猜测。
   - 参考 `{{COMPANY_SLUG}}-jarvis/references/capability-delivery-surfaces.md`。

5. **阻塞问题**：两类情况形成 blocking question：
   - 需要人做 product tradeoff 决策的问题。
   - 所有可查 source 均已穷尽但仍无法获得的事实。
   - 阻塞问题格式参考 `references/blocking-questions-template.md`。

## VERIFY：评审自检

在声明评审完成前，逐条自检：

- 每个 material requirement 都能回指原始证据或明确的 authority decision。
- 每项 acceptance 都是可观察、可验证的——而非主观描述。
- proposed solution 没有被当成唯一方案；若只覆盖了一种实现方式，标注是否故意限定。
- source / repo / branch / tool / command 若未经证据确认，不出现在输出中。
- 所有会改变 scope / route / acceptance 的 unknown 均已标记为显式阻塞。
- 仅在实际完成 gate 检查后才标注 implementation-ready。

## END：产出与写回

产出以下产物，空字段省略：

- **reviewed spec**：经评审的需求规格。
- **agent-ready implementation brief**：供后续 agent 执行使用的简报。
- **decision / assumption / evidence log**：所有关键决策、假设及其证据的追溯记录。
- **blocking questions**：如有未解决的阻塞问题。
- **feature-delivery handoff**：交回 feature-delivery 的上下文摘要。

最终状态为以下三者之一：
- **implementation-ready**：具备足够信息进入 repo-local 实现。
- **blocked-needs-decision/evidence**：存在未解决的阻塞项。
- **redirected**：经判断不属于此 skill 范围，已路由到正确的闭环。

此 skill 不实施代码、不创建虚构的 delivery artifact。若评审过程中识别出应固化的产品边界或跨 surface 规则，按 `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md` 的 writeback policy 回填到对应 source。

## Companion 引用

- `references/source-routing.md` — 如何在 company sources 中提取 PRD 事实、产品契约、执行/验证 route。
- `references/spec-checklist.md` — implementation readiness gate，围绕 goal / scope / non-scope / acceptance / evidence / owner / surface / unknown。
- `references/blocking-questions-template.md` — 阻塞问题记录格式。
- `references/output-template.md` — 紧凑输出形状参考。

## Company 引用（完整路径）

- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`
- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`
- `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`
- `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md`
- `{{COMPANY_SLUG}}-jarvis/references/capability-delivery-surfaces.md`
- `{{COMPANY_SLUG}}-jarvis/references/verify-evidence-matrix.md`
- `{{COMPANY_SLUG}}-jarvis/references/writeback-governance.md`
