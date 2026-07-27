---
name: {{SKILL_NAME}}
description: >
  {{COMPANY_NAME}} Bugfix workflow 的客户定制草稿。仅在向客户讲解、校准和验证其真实
  bugfix 流程时使用；正文状态改为 active 前不得承接真实 bugfix。
---

# {{COMPANY_NAME}} Bugfix Loop

## 模板状态

**当前状态：`draft-template`**

这是 `1+2` 阶段预装的教学与改造起点，不是已经确认的客户流程。Agent 应逐项向客户解释
本草稿的 START → WORK → VERIFY → END、handoff 和 gate，再用 company Jarvis、repo-local
skills 以及客户真实 issue、分支、review、test、release policy 替换其中的通用假设。

只有至少一个客户真实或等价受控 bugfix case 已验证 route、patch、verification 和 closure，
并由客户确认流程可用后，才把本节改为 `active`，同时把 frontmatter description 改成真实
触发条件。`draft-template` 期间只能用于 workflow onboarding，不能执行生产 bugfix。

## 执行规则

- `{{COMPANY_SLUG}}-jarvis/references/` 解析到共享公司 Jarvis references 目录。本 skill 本地文件从当前 skill package 的 `references/` 目录解析。
- 先读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md` 做 runtime preflight。
- Runtime preflight 后必读 `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`。
- 进入 patch 前必须通过 assumption gate、scope gate 和 surgical-change gate；声称 fixed / verified / done 前必须通过 verification gate 和 output gate。

## 触发条件

- 输入是已验证的 post-check handoff（ready-for-bugfix）。
- 用户明确提供 issue / error / artifact / failing check 并要求调查修复。
- 用户报告上一次修复无效或症状仍然存在。
- 如果输入尚不足以做可执行路由判断，先退回 issue post-check / triage。

## 输出契约

- 可审查的修复。
- 原始症状的 before/after 证据。
- 按风险和 repo contract 选择的验证结果。
- 相邻路径影响评估。
- bugfix-result 记录：bug target、evidence、execution route、root cause、change scope、实际验证、未解决风险、交付 artifact、writeback 判断。

## START

### Runtime preflight
读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`，再读 `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`。完成后立即回到 artifact-first 主线。

### 消费输入 artifact
从 post-check handoff 或用户提供的材料中提取：
- 原始症状描述、error 文本、日志、截图、入口点。
- 可用讨论和附件的 source route pointer。附件通过已确认的 source 工具获取。

写出 bug target：observed behavior、expected behavior、入口点、影响范围。

### 消费 decision record
如存在 decision record，读取其中已有的执行路由和分支依据。用 live source 检查是否 stale；只消费当前仍有证据支持的字段。

### 确定执行上下文
从以下来源推导 `execution_project`、`base_branch`、worktree：
- company routing 规则
- source relation 证据
- repo-local truth

禁止用 issue 所在容器猜测执行位置。

进入执行 repo 后：
- 读取该 repo 的 canonical repo-local skill 和相关 truth。
- 只比较当前产品真实存在且有证据的运行时 identity、config、version、data、dependency 差异。

### 跨环境差异
同一输入在不同环境产生不同行为时，只比较当前产品真实存在且能由证据验证的差异维度。调查顺序由最能区分当前假设的证据决定，不把任何配置差异或代码差异预设为首因。

### 路由假设失效
后续新证据使当前路由假设失效时，停止 patch flow，重新路由或退回 post-check。

## WORK

### 获取第一手行为证据
优先获取最接近原始入口、能回答当前假设的证据。可选形态：
- 原始 artifact 的直接观察
- 运行时捕获
- 最小构造 repro

构造 repro 必须证明与原始 artifact 的关键语义等价后才能支持 patch。详见 `references/reproduction-evidence.md`。

### 追踪 owner / root cause
沿症状实际经过的边界追踪。不预设执行面划分、固定状态链或技术栈。首跳从证据推导。

到达主执行 repo 后，切换到 repo-local skill。仅在首跳证据不足时扩展到 second hop。

### 最小修复
进入 patch 前加载 `ponytail`。在证据确认的最窄 owner boundary 做最小 root-cause fix；命令、工具、目录、测试全部来自 repo-local truth / source route。新证据推翻当前 route 时停止 patch 并重新路由。

## VERIFY

### 重放原始症状
必须重放原始症状或已证明等价的入口。按 repo contract 和变更风险选择验证组合：
- targeted checks
- repo checks
- 运行时 proof
- adjacent impact checks

只把实际执行成功写入 executed-pass。未执行的写入 observed-not-executed。静态解释、clean apply 或机器 PASS 不能声称修好。

### 多分支验证
backport / cherry-pick 仅在当前任务需要时执行。每个目标分支按其 repo contract 独立验证。clean cherry-pick 不等于该分支验证通过。

## END

### 产出 bugfix-result
记录：bug target、evidence、execution route、root cause、change scope、实际验证结果、未解决风险、交付 artifact、writeback 判断。

### 协作动作
VCS 变更、review、reviewer 分配、CI、label、comment 等操作仅在客户公司规则、repo policy、project policy 或任务明确要求时执行。使用已确认的 source 工具。

### Still not fixed
用户报告症状持续时：
1. 从原始入口重新复现。
2. 记录新事实，废弃被推翻假设。
3. 重开 WORK。

### 知识写回
只有稳定、可复用、可验证的知识缺口才写回 repo-local 或 company Jarvis。普通任务不制造 no_skill_gap。

## Resources

- `{{COMPANY_SLUG}}-jarvis/references/runtime-governance.md`：runtime preflight
- `{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md`：quality gate
- `references/reproduction-evidence.md`：复现证据选择与等价性验证
- `ponytail`：进入 patch 前选择最小正确实现
- `{{COMPANY_SLUG}}-jarvis`：company Jarvis 闭环选择
- 执行 repo 的 canonical repo-local skill：执行面明确后加载
