# Disposition 操作清单

给执行 intake 的 agent 用的可执行清单。何时读：有原始材料需决定是否建 issue；怀疑可能是 duplicate/by-design/rejected；需要一组具体动作拉取证据。

此清单不替代 `pre-filing-judgment-card.md`（细粒度判断标准）和 `disposition-proof-sop.md`（证明方法）。

## 准备动作

### 1. 压缩 claim
把输入压缩为一句话：谁在什么场景下，看到什么错误行为或缺少什么能力。后续所有搜索围绕这句话展开。

### 2. 附件转文字
从附件中提取可搜索词：从 claim 原文和 source 可检索字段推导搜索表达式，如错误文本、标识符、环境身份标识等。

### 3. 查阅候选模块知识
查阅与 claim 有直接证据关联的模块对应文件：
- `{{COMPANY_SLUG}}-jarvis/modules/<module>/known-issues.md`
- `{{COMPANY_SLUG}}-jarvis/modules/<module>/decisions.md`
- `{{COMPANY_SLUG}}-jarvis/modules/<module>/rejected-features.md`

仅在 evidence 能映射到具体 module 时读取相应文件；映射不明时模块保持 unknown，按 company routing 继续查。目标不是命中关键词就下结论，而是理解候选边界、已知模式和历史上被拒绝的原因。覆盖所有有证据关联的候选模块。

## 历史搜索

### Issue 搜索
通过 START 阶段确认的 source route 工具搜索历史 issue。搜索表达式从 claim 原文与 source 可检索字段推导，不套用固定关键词公式。如果输入中已有精确文本（如错误信息、标识符），优先使用原文或稳定片段搜索，不要先改写成解释性词。

### 阅读候选 issue
通过 source route 工具读取候选 issue 正文和评论，不只看标题。需了解：主要问题是什么、是否有产品结论/wontfix/not-a-bug 判定、是否有"已修复""已支持""不会做"声明、是否提到具体修复路径或版本。

### 验证历史修复
如果历史条目声称"已修复"，在授权 source 对应的仓库中验证：
- 修复了哪个路径/组件/调用链
- 当前症状是否落在同一路径上
- 当前环境/版本是否真正包含该修复

验证的是 fix scope 是否覆盖当前症状，不是 commit 是否存在。

## Bug/Regression 分支

1. 收集当前样本的最小证据包：affected surface、环境身份、复现步骤或观察路径、期望 vs 实际、足以支持或推翻当前 disposition 的文本证据。
2. 搜索历史 issue（优先从 claim 原文推导的搜索表达式，如精确错误文本）。
3. 做"同一主要问题"比对：当前行为差异 vs 历史 issue 行为差异、入口路径/触发条件/受影响对象是否同类别。
4. 如历史 issue 说已修复，验证 fix scope 是否覆盖当前症状和版本。
5. 判 duplicate：主要问题一致 + 触发条件/范围大体一致 + delta 只是新 case/截图/时间戳。不匹配时不强制 duplicate。

## Feature/Enhancement 分支

1. 写出当前需求卡片：谁会用它、什么场景、目标能力、为什么当前不够、最低验收标准。
2. 搜索历史需求/增强/拒绝。
3. 读"为什么没做/为什么已存在"：当时的目标能力、没做的原因、是资源决策还是产品边界、是否已有替代路径。
4. 执行 overlap/delta 分析：角色/场景/能力/动机对齐部分 vs 差异部分；delta 是否改变了产品边界或验收标准。
5. 判 duplicate：当前和历史是同一件事 + delta 不改变产品边界/交付前提/验收标准。
6. 不强制 duplicate：新增了角色/权限/部署边界、新增了交付/合规约束、历史条目只共享大致方向但不覆盖当前验收标准。

## By-design 分支

1. 找明确证据：`decisions.md`、历史 issue/comment 中的产品结论、已知权限/角色边界。
2. 如能访问真实环境，确认当前行为确实符合该边界，不是在 supported flow 内的异常断裂。
3. 结论必须说明：哪个边界在起作用、为什么当前场景落在该边界内、如果要改变边界下一步应做什么。
4. 不能下 by-design：只有模糊印象无来源、当前行为在 supported 范围内但确实坏了、reporter 实际在提新需求非抱怨当前行为。

## Rejected/Wontfix 分支

1. 找真实历史结论：`rejected-features.md` 条目、历史 issue、issue comment 中明确的 wontfix/"不会做"声明。
2. 读拒绝原因本身，不只看 label。
3. 检查当前环境是否已实质性改变：新法规/合规/合同、从单点变普遍痛点、产品/架构边界已变、从低优先级变关键阻塞。
4. 用历史拒绝阻塞：今天的核心需求和历史上是同一件事 + 历史拒绝核心原因今天仍成立。任一不为真 → 回到 ready-to-file-feature 判断。

## 何时输出 blocked-needs-evidence

只有完成所有适用于当前 claim、且能在授权 source 中执行的证据动作后仍证据不足才停。未适用或不可访问的动作要记录原因，不能伪称已执行。

Blocked 输出必须说明：已查过哪些历史线索、已执行过哪些检查、仍缺哪些关键事实、下一轮最需收集哪项。

## 写回前自检

- 最终 outcome 明确
- should-create-new-issue 明确
- overlap/delta 已写（如涉及历史条目）
- 真实 issue/comment/decision 来源已引用
- 如涉及"之前已修复"，fix scope 和版本状态已记录
- 当前证据和仍未知的内容已分开
