---
name: {{SKILL_NAME}}
description: 从真实 issue artifact 提炼最小回归 fixture——可选、任意客户/issue source/repo/test stack 通用。只应在 bugfix 已有真实复现或等价性证据、root cause 与 fix boundary 已明确、post-fix 验证已完成，且授权 artifact 中存在值得固化的真实结构时使用。
version: 1.0.0
---

# issue attachment → 最小回归 fixture

把 bugfix 闭环末尾的真实 issue 附件提炼成可长期留在仓库里的回归测试 fixture。不是 intake，不是首轮定位，不是 live 复现的替代品。

## Trigger

满足以下全部条件时进入本 workflow：

- bugfix 已完成真实复现或持有等价性证据
- root cause 和 fix boundary 已明确
- post-fix 验证已通过
- 授权 artifact 中存在值得固化的真实结构——即附件中有因果相关、可脱敏、可独立存留的数据

以下情况路由回 bugfix/blocked：

- 尚未证明 bug 存在
- 想仅凭附件猜测 root cause
- 目标 repo 没有明确的测试 contract

## START

先读 `{{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md`、`{{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md` 和 `{{COMPANY_SLUG}}-jarvis/references/redaction-rules.md`，再进入目标 repo 的 canonical repo-local skill 上下文并完成以下登记：

1. **artifact pointer**：附件来源引用、获取路径、关联 issue 或 MR
2. **授权 source route**：确认获取附件的方式已授权；附件只通过已确认的 source route 获取
3. **访问与保留边界**：声明哪些数据可访问、哪些可保留到 fixture、哪些不得进入仓库
4. **当前 bug shape**：症状描述、复现路径、影响范围
5. **pre-fix evidence**：修复前问题表现的实际证据
6. **fix scope**：修复涉及的模块、函数、边界
7. **目标测试 contract**：目标 repo 的测试框架、文件位置惯例、断言风格、fixture 目录结构

## WORK

### 1. 验证 artifact 身份、完整性与 provenance

确认拿到的文件与 issue 中声明的来源一致——未被截断、未转换格式、内容可解析。记录 provenance：谁提供、何时、从哪个系统导出、有无二次加工。

### 2. 把 bug shape 压成因果三元组

- **input / precondition**：触发所需的最小前置状态
- **observed failure**：实际发生的错误行为
- **expected contract**：正确的行为契约

不要求固定格式，因果链路清楚即可。这句压缩后的 bug shape 决定后续保留哪些字段、删除哪些字段。

### 3. 选取维持 root cause 判断所需的最小因果结构

从真实 artifact 中只保留与 root cause 有因果关联的结构。判断标准：删掉这个字段或这条记录后，还能不能打中同一个 root cause？能删就删。保留项逐条有因果理由。

### 4. 删除无关数据并脱敏

- 删除与 bug 无关的业务文案、样式、配置噪音、可推断的冗余字段
- 脱敏或去除 PII、secret、私有绝对路径、无关客户数据
- 不把 raw dump 整体复制进仓库

### 5. 按 repo-local 测试惯例构造 fixture 与 provenance note

fixture 命名反映问题本质，不退化到占位名。附带的 provenance note 说明数据来源、精简依据、等价性边界。

### 6. 设计断言

断言覆盖两件事：

- **实际失败契约**：fix 前会 break 的那个行为
- **修复边界**：fix 的确切作用范围

断言集合由 repo contract 和风险评估决定，只保留证明失败契约与修复边界所需的最小集合。

## VERIFY

### 安全且可行时：完整 red-green 验证

1. 在受控的 pre-fix snapshot 上执行 fixture，证明回归测试能暴露原始症状
2. 在 post-fix 目标上执行并通过

### 无法执行 pre-fix 时

记录已有 oracle 和限制条件，不伪称完成了 red-green。

### 质量确认

- 精简后的 fixture 仍然保持了原始 failure signature 和等价性
- 目标测试和适用的 repo checks 已实际执行通过
- fixture 不含 secret、PII、私有绝对路径、无关客户数据
- diff 未带入大块噪音

## END

### 记录

- 净化后的 provenance
- 保留与删除理由：每条保留结构的因果理由，每条删除的判定依据
- 实际验证状态：pre-fix 是否执行及结果、post-fix 是否通过
- target repo artifact：测试文件路径、关联 issue/MR
- 未解决风险：覆盖盲区、未验证的等价性假设、仅部分验证的边界条件

### 收尾

- VCS 提交和 writeback 按 repo policy 执行
- 稳定的 fixture 规则留在 repo-local skill 中
- 跨 repo 方法缺口才考虑提交到 {{COMPANY_NAME}} Jarvis
- 普通任务不制造 no_skill_gap
- fixture 暴露新 bug 或 route 假设失效时，重开 bugfix

## 参考

- {{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md
- {{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md
- {{COMPANY_SLUG}}-jarvis/references/redaction-rules.md
- {{COMPANY_SLUG}}-jarvis/references/verify-evidence-matrix.md
- {{COMPANY_SLUG}}-jarvis/references/writeback-governance.md
- 合同记录模板参考：`references/example-contract.md`
