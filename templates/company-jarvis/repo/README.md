# {{COMPANY_NAME}} JARVIS

{{COMPANY_SLUG}}-jarvis 是 {{COMPANY_NAME}} agent 的统一入口——知识索引、路由、综合与写回中枢。它不是源代码副本，不是会话日志库，不是只按 repo 猜入口的 router。

**核心职责**：帮 agent 先理解公司、进入正确工作闭环、并在任务完成后把可复用知识写回正确位置。

## 身份

- **公司**: {{COMPANY_NAME}}（`{{COMPANY_SLUG}}`）
- **产品 / 业务范围**: {{PRODUCT_IDENTITY}}
- **Owner**: {{COMPANY_OWNER}}

## 职责面

JARVIS 提供四个可验证的职责面：

| 面 | 说明 | 入口 |
|---|---|---|
| **capability** | 模块能力路由与边界 | `modules/<module>/overview.md` |
| **delivery** | 用户可感知的交付面映射 | `references/capability-delivery-surfaces.md` |
| **knowledge** | 公司知识路由与 source 路由 | `modules/`、`sources/` |
| **verification** | 验证证据矩阵 | `references/verify-evidence-matrix.md` |

## 核心原则

**workflow-first when active，不要先按仓库。** 有已验证 workflow 时根据 task 类型选择闭环；尚未激活 workflow 时，仍可通过 module/source/first proof 做 construction/onboarding routing，但不能冒充生产闭环。

**artifact-first。** 输入是 issue / MR / error / screenshot / URL / failing test 时，从 artifact 路由，不做无上下文全局搜索。

**repo-local truth。** repo 内部工程执行方法留在 repo-local skills。JARVIS 只维护跨 repo 路由、模式和工作流综合。

**source-of-truth。** 每个事实只有一个权威归属。source 内容留在 source，不复制到 JARVIS；模块知识通过 evidence pointer 引用原始来源。

**knowledge layering。** `modules` 回答 what，`cross-cutting` 回答 why inspect next，repo-local 回答 where/how，task artifact 回答本次证明了什么。完整合同见 `references/knowledge-layer-contract.md`。

## 已确认范围（scope，不代表语义已确认）

### 模块

{{MODULE_INDEX}}

### 数据源

{{SOURCE_INDEX}}

### 工作流

{{WORKFLOW_INDEX}}

上述预装 workflow 初始都只是 `draft-template`，不属于已验证生产范围。

### 仓库

{{REPO_INDEX}}

以上名单由客户/operator 确认，代表当前 scope。各条目的语义、角色、路由规则需在对应合约文件中逐步确认，名单本身不等于语义已落定。

## 仓库结构

```text
{{COMPANY_SLUG}}-jarvis/
├── README.md
├── MAINTENANCE.md
├── AGENTS.md
├── CLAUDE.md
├── SKILL.md
├── .github/copilot-instructions.md
├── modules/           ← 模块合约（overview + known-issues + decisions + rejected-features + test-coverage）
├── sources/           ← source route contract（每个 source 一份 README.md）
├── cross-cutting/     ← 跨模块交互、版本变更、peer product 合约
├── references/        ← 路由规则、质量门、写回治理等持久引用
├── skills/            ← entry skill + workflow skills + source-helper skills
├── tools/             ← 可复用工具和手动任务
└── evals/             ← company workflow 的行为验证案例
```

## 技能分类

| 类别 | 位置 | 用途 |
|---|---|---|
| entry skill | `skills/{{COMPANY_SLUG}}-jarvis/SKILL.md` | 统一入口、闭环路由、收束 |
| 通用方法 | runtime agent discovery 中的 `skill-creator`、`ponytail`、`writing-durable-docs`、`jarvis-self-improve-skill`、`stop-slop` | container 安装一次，不复制到本 repo |
| source/tool | `skills/{{COMPANY_SLUG}}-<name>/SKILL.md` | 帮助 agent 使用客户特定 source/tool |
| workflow | `skills/{{COMPANY_SLUG}}-workflow-<name>/SKILL.md` | 跨 repo / 跨角色的客户闭环 |
| repo-local skill | 各 repo 根 `skills/` canonical package | 单 repo 内工程执行方法 |

预装 workflow 草稿：

- `skills/{{COMPANY_SLUG}}-workflow-issue-post-check/SKILL.md`
- `skills/{{COMPANY_SLUG}}-workflow-bugfix-loop/SKILL.md`
- `skills/{{COMPANY_SLUG}}-workflow-feature-delivery/SKILL.md`

它们初始都必须保持 `draft-template`，用于 Agent 向客户讲解和共同改造，不能因为文件已存在
就承接生产任务。结合 company routing 与 repo-local skills 完成客户定制，并通过真实 case
后，才逐个改为 `active`。

## 强制预读

任何 {{COMPANY_NAME}} 工作流开始前，必须先读：
- `references/runtime-governance-quick.md`（触发升级条件时再读 `references/runtime-governance.md`）

## 二级路由条件

从 JARVIS 进入具体工作面后，触发以下条件时才返回 JARVIS 做 second-hop：
- 当前工作面无法独立完成，需要跨 repo / 跨 source / 跨模块协作
- 发现了需要更新 routing rule 的模式
- END 阶段需要写回跨模块知识
- 工作结果需要在 JARVIS 侧更新 capability status

## 工作闭环：START → WORK → VERIFY → END

### START
先读最相关的稳定入口（模块 overview、source route、或 workflow skill），检查是否已有类似故障、决策或被拒绝路径。

### WORK
在正确的 repo、source system 或 workflow surface 中执行。当工作变为 repo-specific 时，遵循 repo-local instructions。不随意扩大 rollout 范围。

### VERIFY
对照原始 trigger 验证工作结果。收集可观测证据，运行回归检查。不能仅靠静态阅读判断运行时行为。

### END
把可复用知识写回正确文件：
- **writeback primary home**：issue 结论写回 issue；repo 执行知识写回 repo-local skill；跨模块路由规则按 primary home 选择：task-local → repo-local → source → workflow → company → upstream
- 现有 guidance 足够时记录 `no_skill_gap`，不增长 skill
- 不让学习结果困在会话记录里

## 写回规则

写回遵循 `references/writeback-governance.md`。核心约束：
- 不把源代码复制进 JARVIS
- 不把私密信息（token、密钥、PII）写入 JARVIS
- 不把单次偶发事件提升为持久规则
- 每条事实只有一个 primary home；跨 repo 的事实按 promotion ladder 选择归属

## 真实仓库拓扑

公司实际的 repo 拓扑记录在 `references/canonical-repo-fleet.md`。JARVIS 只引用、不镜像。

## 维护

修改 JARVIS 本身时，遵循 `MAINTENANCE.md`。
