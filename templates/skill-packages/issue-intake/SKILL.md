---
name: {{SKILL_NAME}}
description: >
  Issue 建单前预检：当尚未建 issue、只有零散原始材料（聊天、截图、日志等）时，
  判断是否值得建 issue。输出 ready-to-file-bug、ready-to-file-feature、duplicate、
  by-design、rejected-request/wontfix-history 或 blocked-needs-evidence。
  仅对前两种允许创建 issue。已建 issue 的 webhook 重审应使用 issue-post-check。
---

# {{COMPANY_NAME}} Issue 预检（Intake）

此 skill 执行建 issue 前的 intake 门禁。不修 bug，不评审需求，不转发截图原文。

## 适用范围

**使用**：reporter 提交的发现或反馈、零散聊天/截图/日志需整理成 issue；仍处于建单前预检阶段。

**不使用**：直接修 bug、PRD 评审、仅转发截图/录屏、关键事实缺失时强行生成看似完整的 issue、已建 issue 的 webhook 重审（用 `issue-post-check`）。

## 前置阅读

1. 先读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`
2. 再读 `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`
3. 模块归属不确定时读 `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md`
4. claim type 尚未归一化时读 `{{COMPANY_SLUG}}-jarvis/references/issue-claim-normalization.md`

本 package 内 reference 从 `references/` 解析；公司级 reference 从 `{{COMPANY_SLUG}}-jarvis/references/` 解析。

## 执行阶段

### START — 登记与授权

1. 登记原始 artifact pointer（URL、消息 ID、文件路径等）、reporter 显式陈述的事实、授权可访问的 source。
2. 完成前置阅读中的 runtime/quality gate 检查。
3. 区分事实、推断、未知。不把推断写成事实。

### WORK — 归一化与调查

4. 把输入压缩为一句话 claim：谁在什么场景下，看到什么错误行为或缺少什么能力。
5. 归一化 claim type：reporter 标的 bug/feature/enhancement/question 只是假设。用 `issue-claim-normalization.md` 建立 `normalized_claim_type`，再定 disposition。
6. 依据公司 modules、source routes、live issue-system metadata 推导候选模块和目标 issue 容器。
7. 通过已确认 source route 的读/搜操作查历史 issue、decision、known issue、rejected record。覆盖所有与 claim 有直接证据关联的候选模块。
8. 收集 agent 可自行获得的证据：把附件关键信息转为文字，搜索真实历史 issue 正文和评论（不只看标题），在授权 source 内执行可操作的 live 验证。
9. 只有关键事实不可从授权 source 获取时才问人；按 `references/guided-question-flow.md` 按缺口提问。

### VERIFY — 证据门

10. 用 `references/pre-filing-judgment-card.md` 做 disposition 证据门判断。
11. 对疑似 duplicate/by-design/rejected，按 `references/disposition-command-checklist.md` 执行证据动作，按 `references/disposition-proof-sop.md` 做实查和可追溯证据采集。
12. **ready-to-file-bug** 必须：可观察行为、期望/实际、复现或观察入口、可追溯证据、目标 issue 容器依据，并排除已有正面证据支持的 duplicate/by-design。
13. **ready-to-file-feature** 必须：user goal、场景、价值、验收标准、与 {{PRODUCT_IDENTITY}} 已确认 scope 的关系，并检查已有能力和历史决策。
14. **非 filing 结论**（duplicate/by-design/rejected）必须引用能够正面支持结论的来源。
15. **blocked-needs-evidence** 必须说明已查内容、缺失事实及其为何会改变 disposition。

### END — 输出

16. 只有 ready-to-file 才允许创建 issue。没有写权限时留下 artifact，不伪称已创建。
17. 按 `references/output-template.md` 产出：ready-to-file issue 描述或非 filing 结论。
18. blocked 按 `references/blocker-template.md` 产出 blocker 清单。
19. ready 输出保留 `<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->` 来源标记。
20. 用 `references/issue-type-matrix.md` 确认最终 disposition。

## 硬规则

- 只有截图/录屏不够——关键证据必须转为文字。
- Reporter 标的类型只是假设，先归一化再做 disposition。
- `by-design` 需要正面证据，不能是"没证明是 bug 就算 by-design"。
- 如果已能判定 duplicate/by-design/rejected，直接停止，不建 issue。
- 关键事实缺失时输出 `blocked-needs-evidence`，不输出弱 issue。
- 一个 issue 只承载一个主要问题。
- 不要把整段聊天记录贴进 issue；先提炼。
- 需求类 issue 不能只有"客户想要"；必须写出场景、现状、价值和验收标准。
- `question/usage clarification` 不是最终结果；必须解析为 by-design/blocked/feature filing 之一。
- 已知 workaround 记录下来；它可能不阻止建 issue 但影响判断。
- 区分事实、推断和未知；禁止把猜测写成结论。
- 所有搜索、读取、写回操作使用 START 阶段确认的 source route 对应工具，不假设特定平台 CLI。

## Reference 路由

按需阅读，不要一次全读：

| 场景 | 文件 |
|------|------|
| 判断真缺口/duplicate/by-design/rejected/workaround/证据底线 | `references/pre-filing-judgment-card.md` |
| 疑似 duplicate/by-design/rejected，需证据动作收集证据 | `references/disposition-command-checklist.md` |
| 下 duplicate/by-design/rejected 结论，需可追溯证据 | `references/disposition-proof-sop.md` |
| 需向 reporter 提问，或处理懒惰输入 | `references/guided-question-flow.md` |
| 确定 disposition 选项 | `references/issue-type-matrix.md` |
| 产出 ready-to-file 或非 filing 输出 | `references/output-template.md` |
| 产出 blocked-needs-evidence | `references/blocker-template.md` |
| Quality gate 检查 | `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md` |
| Claim 归一化 | `{{COMPANY_SLUG}}-jarvis/references/issue-claim-normalization.md` |
| Capability owner / delivery surface | `{{COMPANY_SLUG}}-jarvis/references/capability-delivery-surfaces.md` |
| 模块归属/next-hop 不明确 | `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md` |

## Handoff

- `ready-to-file-bug` → bugfix-loop
- `ready-to-file-feature` → feature-delivery
- 需求进入 spec 阶段 → prd-review
- 其他 outcome → intake 在此结束
