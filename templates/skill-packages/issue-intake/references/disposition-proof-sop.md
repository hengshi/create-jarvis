# Disposition 证明 SOP

面向执行调查的 agent。目标：每个结论都携带可追溯证据，不凭"看起来像"下结论。

## Agent 角色边界

Agent 先执行自己力所能及的所有动作：附件关键信息转文字、搜索历史 issue、读模块知识文件、能在授权 source 内执行 live 验证时先收集证据。只有 agent 确实拿不到的事才问人。

不要把 agent 该做的动作推回给 reporter（搜索历史 issue、把截图转文字等）。

## 先拿第一手行为证据

**Bug/Regression**：获取足以支持或推翻当前 disposition 的真实证据——可观察的错误行为、从 claim 原文和 source 可检索字段推导的关键文本。没有这层证据不要急于讨论 duplicate。

**Feature/Enhancement**：获取谁会用它、什么场景、目标能力、为什么当前不够、最低验收标准。只有"想要"或"参考其他产品有"还不够讨论 duplicate 或 rejected。

## 搜索证据

按需搜索，不以固定层数限制：

- 模块知识：`{{COMPANY_SLUG}}-jarvis/modules/<module>/known-issues.md`、`decisions.md`、`rejected-features.md`（仅在 evidence 能映射到 module 时读取）。
- 真实 issue/comment：通过 source route 工具搜索和读取，不只看标题。搜索表达式从 claim 原文与 source 可检索字段推导。
- 如果候选 issue 声称已修复：在授权 source 仓库中检查 fix scope——哪个路径/调用链被修复、当前症状是否落在同一路径上、当前版本是否包含该修复。

## 逐 Outcome 证明

### Duplicate（Bug）

证明链：当前行为证据 + 历史 issue + fix scope 验证（如涉及已修复）。

1. 收集当前样本最小证据包。
2. 搜索并阅读历史 issue 正文和评论。
3. 创建比对卡片：当前主要行为差异 vs 历史 issue、入口路径/触发条件/受影响对象是否同类别。
4. 如历史 issue 说已修复，验证 fix scope。
5. 写 overlap/delta。
6. 只有以下全部为真才能下 duplicate：主要问题一致、触发条件/范围大体一致、delta 只是新 case/截图/对象/时间戳。

如果 delta 可能改变 root cause 或 fix scope，不直接判 duplicate，输出"高度相关 issue + 当前差异"继续 ready-to-file-bug。

### Duplicate（Feature）

1. 写出当前需求卡片。
2. 搜索历史 issue/comment/rejected-features。
3. 做 overlap/delta 比对。
4. 判断 delta 是否值得新需求：只是不同客户名/措辞 → 不足以开新工单；新增了旧 issue 不覆盖的明确边界条件 → 不机械标 duplicate。
5. 真 duplicate → 追加到历史 issue；部分重叠但有新边界 → 建新 issue 但引用旧 issue 并写 overlap/delta。

### By-design

证明链：**设计来源 + 当前场景落在边界内的论证**。

1. 找明确证据：`decisions.md`、历史 issue/comment 中的产品结论、已知权限/角色边界。
2. 如能访问真实环境，确认当前行为确实符合该边界。
3. 说明哪条边界、如何适用于当前场景、为什么解释实际结果。
4. 如果 reporter 实际在提新需求非报 bug，转为 feature 判断。

**不能下 by-design**：只有模糊印象无来源、当前行为在 supported 范围内但确实坏了。

### Rejected-request / Wontfix-history

证明链：**历史结论 + 拒绝原因今天仍成立的论证**。

1. 找真实历史结论来源。
2. 读拒绝原因本身，不只看 label。
3. 写 overlap/delta：今天的需求与历史上重叠在哪、差异在哪。
4. 只有两者均为真才能用历史拒绝阻塞：核心需求相同 + 拒绝核心原因今天仍成立。
5. 如当前事实已使历史拒绝依赖的前提或产品边界失效，返回 ready-to-file-feature 判断，正文纳入历史拒绝背景。

### Blocked-needs-evidence

只有 agent 完成了所有自己该做的动作、关键事实仍缺失时才进入此类。不是"懒得查"的后门。

进入前确认：适用于当前 claim、且 agent 能在授权 source 中完成的证据动作已经执行；未适用或不可访问的动作及原因已经记录。

输出必须说明：已查过什么、仍缺哪些关键事实、下一轮最需收集哪项、为什么没有这项证据 disposition 无法继续。

## Overlap vs Delta 格式

```
- 与历史条目的重叠：
- 当前 case 的差异：
- delta 是否改变 root cause / 产品边界 / 验收边界：是 / 否
- 对 disposition 的影响：
```

## 转发话术

非 filing 结论需提供一段可直接转给 reporter 或负责方的话。应包含：为什么这次不建新 issue、命中了哪个历史 issue/decision、当前输入与历史条目重叠在哪、当前可用 workaround/替代路径、什么变化才值得重开。

不要写"我们不做这个""Duplicate of existing""By design"。应写为具体解释。

## 关闭前自检

- 是否真的搜索了真实 issue，不只是 skill 文档？
- 是否补充了自己能收集的证据，而非推回给人？
- duplicate/by-design/rejected 结论是否有可追溯来源？
- 如果涉及真实行为异常，是否获取了 live 行为证据？
- 如果声称"之前修过/之前被拒过"，是否提供了具体 issue/comment/decision 来源？
- 结论是否能让 reporter 或负责方直接用于解释，无需二次解读？
