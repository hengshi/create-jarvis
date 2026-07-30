---
name: {{JARVIS_REPO_NAME}}
description: "{{JARVIS_NAME}} Agent 统一入口。对属于本 Jarvis 已确认范围的任务执行闭环识别、知识路由、source/repo handoff、验证与受控写回。"
---

# {{JARVIS_NAME}} JARVIS

> {{JARVIS_SLUG}}-jarvis 是 {{JARVIS_NAME}} 闭环统一入口——知识索引、路由、综合与写回中枢，不是内容镜像仓库。

## 1. 定位与身份

- **Jarvis**：{{JARVIS_NAME}}
- **已确认Jarvis 用途**：{{JARVIS_PURPOSE}}
- **Owner**：{{JARVIS_OWNER}}

Source-detected identity 不能覆盖 Jarvis 身份。JARVIS 首先回答：当前任务属于哪个已验证闭环、应最先加载哪种 skill、第一跳去哪能最快拿到 first proof、什么证据阈值触发升级、任务结束后是否需要 durable knowledge writeback。

## 2. 执行上下文

每次任务先读 `references/runtime-governance-quick.md`，运行当前 Runtime Environment 的 quick sync，
并确认本入口来自 Agent 的原生 discovery roots。普通授权 checkout 与 managed Task 都服从当前授权
target；不要发明不存在的 Task identity，也不要假设 Jarvis mount、`JARVIS_HOME` 或 root-skill 注入。
涉及路径、同步、工具、权限、handoff、cleanup 或 runtime integration 时按 quick 升级到完整版。

涉及 workflow disposition、执行、代码/文档修改、delegation、或声称完成时，必须读 `references/agent-engineering-quality-gate.md`。

Session compact、handoff 后，后续 agent 重新执行本节 preflight 即可。

## 3. 客户索引

### Workflows

{{WORKFLOW_INDEX}}

初始列出的 bundled workflows 均是 `unverified`；只有内容来自真实客户事实并通过真实或等价 case 的 workflow 才属于可执行范围。

### 模块

{{MODULE_INDEX}}

### 数据源

{{SOURCE_INDEX}}

### Repo-local 入口

{{REPO_INDEX}}

各索引职责：
- **workflow**：已确认的跨 source、流程或 repo 闭环，定义起点、执行面和关闭标准
- **module**：从客户证据形成的稳定能力边界，聚合真实入口、已知问题模式和设计决策
- **source**：已授权事实源的路由契约入口，统一为 `sources/<source>/README.md`
- **repo**：工程执行入口，只在证据路由到具体 repo 时进入

Capability owner 可以是已确认的 product、source、process 或 repo owner，不预设必须是 repo。

预装但尚未验证的 workflows：

- 已建 issue/ticket 需要判断、去重或路由：`{{JARVIS_SLUG}}-workflow-issue-post-check`
- 已确认 bug 需要修复：`{{JARVIS_SLUG}}-workflow-bugfix-loop`
- 已确认需求需要交付：`{{JARVIS_SLUG}}-workflow-feature-delivery`
- 进入代码或耐久文档实现前：按任务加载 `ponytail`、`writing-durable-docs` 或 `stop-slop`
- 发现重复 agent failure 或 review pattern：`jarvis-self-improve-skill`

前三个 bundled workflow 初始状态是 `unverified`。路由前读取目标 skill 的 evidence：`unverified`
不得执行；`verified` 只表示列出的适用范围和验证证据成立。新的运行环境仍需通过 Runtime Foundation
doctor 与 Agent discovery probe，但不产生另一套 workflow deployment 状态。

## 4. 路由算法

本入口坚持 **workflow-first when verified**：先检查是否有 evidence-backed workflow；命中时再选择 module、source 和 repo-local 执行面。没有已验证 workflow 时，仍可找到 module/source/first proof，但必须明确缺失的执行合同。不要先按仓库猜入口。

同时坚持 **artifact-first**：从 issue、MR、error、screenshot、failing test 或其他实际 artifact 提取事实后再路由，不做无上下文的全局搜索。

```text
读 artifact / source pointer
→ 提取显式事实、claim、可观测差异、unknown
→ 有匹配的 verified workflow：进入 workflow，再映射到 module / source
→ 没有 verified workflow：映射到 module / source / first proof，并报告 workflow 缺口
→ 只有 evidence 路由到 repo 时才进入 repo-local
→ 关键 module/source/first-proof route 无法证明 → blocked，不发明
```

artifact 所在容器或标题不等于 execution owner；首跳必须由内容与 route evidence 决定。
未验证 workflow 不能承接任务。

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
| `runtime-governance-quick.md` | 每次任务 preflight |
| `runtime-governance.md` | quick 指定的路径、同步、工具、权限、handoff、cleanup 或 integration 场景 |
| `canonical-repo-fleet.md` | 查询已确认的 canonical repo fleet |
| `jarvis-box.md` | 正式 runtime 的客户 integration facts 与公开 operator pointer |

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
- repo execution truth 留在 repo-local；Jarvis 保存跨边界长期路由
- 当前动作所需的 identity、route、authority 或 acceptance 关键证据缺失 → blocked
- 机器/文件存在不等于语义完成
- 不把源代码、密钥、私密信息写入 Jarvis
- 只有证据足以说明可复用边界和验证方式时才写回，不要求固定 task 次数
