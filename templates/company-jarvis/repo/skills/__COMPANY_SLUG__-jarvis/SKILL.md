---
name: {{COMPANY_JARVIS_NAME}}
description: "{{COMPANY_NAME}} 企业 agent 统一入口。对属于公司已确认范围的任务执行闭环识别、知识路由、source/repo handoff、验证与受控写回。"
---

# {{COMPANY_NAME}} JARVIS

> {{COMPANY_SLUG}}-jarvis 是 {{COMPANY_NAME}} 企业闭环统一入口——知识索引、路由、综合与写回中枢，不是内容镜像仓库。

## 1. 定位与身份

- **公司**：{{COMPANY_NAME}}
- **已确认产品身份**：{{PRODUCT_IDENTITY}}
- **Owner**：{{COMPANY_OWNER}}

Source-detected identity 不能覆盖公司身份。JARVIS 首先回答：当前任务属于哪个企业闭环、应最先加载哪种 skill、第一跳去哪能最快拿到 first proof、什么证据阈值触发升级、任务结束后是否需要 durable knowledge writeback。

## 2. 执行上下文

先判断当前是 construction/onboarding、普通授权 checkout，还是 managed production。construction
以外部 `BUILD-CONTEXT.md` 和当前 Git/source facts 为准，不要求 jarvis-box；managed production
使用 runtime 已注入的 Company snapshot、Task identity 和授权 target。上下文缺失、冲突或需要
诊断时才读 `references/runtime-governance-quick.md`，并按其条件升级到完整版。

涉及 workflow disposition、执行、代码/文档修改、delegation、或声称完成时，必须读 `references/agent-engineering-quality-gate.md`。

Session compact、handoff 后，后续 agent 重新执行本节 preflight 即可。

## 3. 客户索引

### Workflow 状态

{{WORKFLOW_INDEX}}

初始列出的 company workflows 均是 `draft-template`；只有后续客户定制并通过真实 case 的 workflow 才属于已确认可执行范围。

### 模块

{{MODULE_INDEX}}

### 数据源

{{SOURCE_INDEX}}

### Repo-local 入口

{{REPO_INDEX}}

各索引职责：
- **workflow**：已确认的跨 source、流程或 repo 闭环，定义起点、执行面和关闭标准
- **module**：从客户证据形成的业务/产品域，聚合真实入口、已知问题模式和设计决策
- **source**：已授权事实源的路由契约入口，统一为 `sources/<source>/README.md`
- **repo**：工程执行入口，只在证据路由到具体 repo 时进入

Capability owner 可以是已确认的 product、source、process 或 repo owner，不预设必须是 repo。

预装 workflow 草稿：

- 已建 issue/ticket 需要判断、去重或路由：`{{COMPANY_SLUG}}-workflow-issue-post-check`
- 已确认 bug 需要修复：`{{COMPANY_SLUG}}-workflow-bugfix-loop`
- 已确认需求需要交付：`{{COMPANY_SLUG}}-workflow-feature-delivery`
- 进入代码或耐久文档实现前：按任务加载 `ponytail`、`writing-durable-docs` 或 `stop-slop`
- 发现重复 agent failure 或 review pattern：`jarvis-self-improve-skill`

前三个 company workflow 初始状态是 `draft-template`。路由前必须读取目标 skill 的状态：

- `draft-template`：只做客户 workflow onboarding；
- `construction-ready`：只做建设环境中的受控验证；
- `runtime-deployed` / `ready-for-shadow`：已固定运行时快照，等待 supervised shadow；
- `shadowing`：在客户监督下处理代表性真实任务；
- `active`：只在 deployment lock 所绑定的范围内承接生产任务。

## 4. 路由算法

本入口坚持 **workflow-first when active**：先检查是否有已经验证并激活的 workflow；命中时再选择 module、source 和 repo-local 执行面。尚无 active workflow 时，仍可在 construction/onboarding mode 中完成 company semantic routing，找到 module/source/first proof，但不能把它冒充可执行的交付闭环。不要先按仓库猜入口。

同时坚持 **artifact-first**：从 issue、MR、error、screenshot、failing test 或其他实际 artifact 提取事实后再路由，不做无上下文的全局搜索。

```text
读 artifact / source pointer
→ 提取显式事实、claim、可观测差异、unknown
→ 有匹配的 active workflow：进入 workflow，再映射到 customer module / source
→ 没有 active workflow：以 construction/onboarding mode 映射到 module / source / first proof
→ 只有 evidence 路由到 repo 时才进入 repo-local
→ 关键 module/source/first-proof route 无法证明 → blocked，不发明
```

artifact 所在容器或标题不等于 execution owner；首跳必须由内容与 route evidence 决定。
construction/onboarding mode 可以用于理解、验证路由和收集客户 workflow 事实，不能承接未激活的生产 delivery。

## 5. START → WORK → VERIFY → END

**START**：选闭环与首跳，确定 success/stop 条件。读最相关入口（module overview、source route、或 workflow skill），检查已有故障、决策或被拒绝路径。

**WORK**：在正确的 source、process 或 repo 中执行。不随意扩大范围。

**VERIFY**：对照原始 trigger 和 acceptance criteria，用真实 evidence 验证。状态区分：
- `executed-pass`：实际执行且通过
- `executed-fail`：实际执行但未通过
- `observed-not-executed`：观察到但未实际执行

不靠静态阅读或机器 PASS 判断完成。

**END**：记录结果、阻塞或 next action。只有出现可复用、可验证的 self-improvement signal 时才判断 `no_skill_gap` 或触发 writeback。学习结果不困在会话记录里。

## 6. Reference 路由表

不默认读全部 reference，按触发条件按需加载。

### Runtime / workspace

| Reference | 触发条件 |
|---|---|
| `runtime-governance-quick.md` | 执行上下文或边界不清、冲突、诊断时 |
| `runtime-governance.md` | quick 明确触发升级时 |
| `canonical-repo-fleet.md` | 查询已确认的 canonical repo fleet |
| `jarvis-box.md` | jarvis-box 概念、服务模式 |

### 路由 / 所有权

| Reference | 触发条件 |
|---|---|
| `jarvis-first-routing.md` | 任务首次进入 JARVIS、所有权不明确 |
| `next-hop-compression.md` | 执行路由时选首跳 |
| `capability-delivery-surfaces.md` | 多 repo 任务中选 capability owner、delivery surfaces |
| `module-boundary-routing.md` | 症状跨模块 |

### 证据 / 关闭

| Reference | 触发条件 |
|---|---|
| `agent-engineering-quality-gate.md` | 涉及 disposition、执行、修改、delegation、完成声明时 |
| `verify-evidence-matrix.md` | 准备或评判验证证据 |
| `completion-standard.md` | 声称 done/fixed/verified 前 |
| `minimal-closure-card.md` | 多 repo 工作流结束前、handoff 前 |
| `issue-claim-normalization.md` | 仅 issue workflow 使用 |
| `repo-pre-push-review-loop.md` | 仅已确认 repo policy 要求时 |

### 治理

| Reference | 触发条件 |
|---|---|
| `redaction-rules.md` | 迁移原始内容到共享 skill/reference 前 |
| `writeback-governance.md` | END 阶段写回时 |
| `knowledge-layer-contract.md` | 判断 module/cross-cutting/repo-local/source/task 的 primary home 时 |

## 7. 边界与停止

- source 原文和 raw dump 不搬入 Jarvis；只保留脱敏后的提炼事实与可追溯 pointer
- repo execution truth 留在 repo-local；company Jarvis 保存跨边界长期路由
- 当前动作所需的 identity、route、authority 或 acceptance 关键证据缺失 → blocked
- 机器/文件存在不等于语义完成
- 不把源代码、密钥、私密信息写入 Jarvis
- 只有证据足以说明可复用边界和验证方式时才写回，不要求固定 task 次数
