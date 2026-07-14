---
name: {{SKILL_NAME}}
description: >
  已建 issue 的后检母版。事件、人、bot 请求审查已存在 issue 时使用。
  先过 trigger gate：intake marker 只证明来源不证明结论正确，仅当 intake 输出契约与证据仍完整、
  live issue 无新增/冲突/stale/risk 信号且公司策略允许时才 skip。否则进入完整 START→WORK→VERIFY→END 后检。
---

# Issue 后检

面向**已建 issue** 的强制审查。所有 source/tool 从 company route 和 live issue 中按需解析。

不用此 skill 做建 issue 前 intake（用 issue-intake），也不替代 bugfix / feature-delivery 闭环。

## 强制性前置阅读

- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`
- `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`
- 进入 disposition 前：`{{COMPANY_SLUG}}-jarvis/references/issue-claim-normalization.md`

按需加读：
- `references/environment-version-evidence-gate.md`：仅当版本、环境、部署身份会改变 duplicate、fix coverage 或路由时使用
- `references/peer-product-contract-check.md`：仅当判断确实依赖行业/同类产品契约且授权 source 可访问时使用；外部产品不是权威
- `{{COMPANY_SLUG}}-jarvis/references/jarvis-first-routing.md`
- `{{COMPANY_SLUG}}-jarvis/references/verify-evidence-matrix.md`

本地 reference 从 `references/` 解析，公司级从 `{{COMPANY_SLUG}}-jarvis/references/` 解析。

## Trigger gate

每个已存在 issue 先过 trigger gate，输出两种结果之一：

| 结果 | 含义 |
|------|------|
| `run-full-post-check` | 进入完整后检 |
| `skip-intake-already-verified` | 跳过，不进入历史搜索和 disposition |

`skip-intake-already-verified` 不是完整 disposition 之一。跳过时不产出完整 post-check comment，不执行历史搜索和 claim 归一化。

### 跳过条件

同时满足以下全部条件：

1. issue 描述携带可信 intake 来源标记（如 `<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->` 或等价完整签名），依据 issue-intake 输出契约整体判断其结论与证据仍完整
2. 当前 live issue / 触发事件没有新增证据、冲突、stale 或 risk 信号
3. 当前公司策略允许跳过

不得用固定字段数或证据条数判可信。仅有关键词匹配、仅有 label、仅有 AI 语气摘要不构成可信 intake。module 可以合法 unknown，不作为 intake 可信度的必要条件。

### Stale / risk 信号

触发事件满足以下任一条件时必须 `run-full-post-check`：

- 改变了 intake 结论所依赖的事实（如描述、证据被实质更新，或 issue type 变更导致 routing 失效）
- 引入了 intake 未覆盖的新证据或冲突证据（如新评论、复现材料、日志、error string、VCS 变更链接、专家判断）
- 使 intake 确立的 routing、issue identity、freshness 或产品契约判断失效
- 客户策略明确要求重审

### Skip 输出

简短记录 trigger gate 结果和理由，写入 decision record。不输出完整 comment，不触发后续 phase。

---

## START

1. 完成 runtime preflight。
2. 用 Phase 6 已确认的 issue source route 读取 live issue：当前正文、触发事件、评论、附件 pointer、可用 metadata。
3. 登记事实、推断、未知。不得只信 webhook 摘要。

## WORK

4. 归一化 claim：用 `issue-claim-normalization.md` 产出 `reporter_labeled_type`、`normalized_claim_type`、product lens、technical lens。
5. 按 company Jarvis routing 和 evidence 映射 module；读对应 jarvis 模块的 known-issues 和 decisions。涉及多模块时读 cross-cutting。
6. 用已确认 source route 搜索历史：issue、decision、rejected record、相关变更。从 claim/source 字段自适应扩展搜索范围，至证据足以决策或授权耗尽。记录搜索范围。
7. 只在版本、环境、关联开发工作确实影响 disposition 时执行对应 evidence gate：
   - 环境/版本 gate：区分 reporter claim、observed runtime identity、historical fix identity；只比较当前 source 实际存在的 identity 维度，无法验证则 disputed/blocked。
   - 同类产品契约检查：仅当判断依赖行业/同类产品契约且授权 source 可访问时；外部产品只提供上下文，不能替代当前产品契约。
8. 如果 claim 含用户目标和具体实现方案，分离两者。Reporter 提出的实现方案是假设不是事实；先验证现有产品契约是否已覆盖同一用户目标。
9. `execution_project` / `base_branch` 只能从 company route、repo-local truth、live VCS/source relation 得出。未知就保持 unresolved，不能按症状类别或 issue 容器猜。source branch / target branch 选择服从该项目已确认工作流，不内置默认。

## VERIFY

10. 按证据判断 disposition：
    - `duplicate` / `by-design` / `rejected`：必须有正面可追溯来源。`by-design` 必须说明哪个现有契约/边界/默认行为在起作用且真正解释了当前实际结果。
    - `ready-for-bugfix`：必须有真实行为证据和可解释 execution route。不要求此阶段猜 root cause。
    - `ready-for-feature-delivery`：必须有 user goal、current contract/gap、product-scope fit 和可执行 handoff。
    - `blocked-needs-evidence`：必须说明适用且可访问的证据动作已穷尽、缺失事实为何会改变 disposition。
11. 确认 claim 归一化未被后续证据推翻。
12. 按 `agent-engineering-quality-gate.md` 验证 assumption / verification / output gate。缺失会改变 disposition 的关键证据时必须 blocked，不能继续给出确定路由。

## END

13. 产出面向 issue 读者的 `comment.md` 和结构化 decision record。
14. comment 只放影响结论与下一步的事实。审计细节进 decision record。
15. 写回、label 建议或状态动作仅在客户/project policy 与当前任务明确允许时执行；否则只保存 artifact，不伪称已写回。
16. decision record 使用 `execution_project`。feature-linked project/branch 只有 live relation 明确证明时才写。

## Disposition 路由

- `duplicate` / `by-design` / `rejected` / `blocked-needs-evidence` → post-check 结束
- `ready-for-bugfix` → 交接 bugfix 闭环
- `ready-for-feature-delivery` → 交接 feature-delivery 闭环

## Decision record

记录 outcome、支撑证据、issue identity、已确认 routing、未解决缺口和 next workflow。没有值的字段省略。trigger gate 补充跳过/重审动作记录。环境检查补充相关冲突记录。
