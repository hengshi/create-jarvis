# Output Template

PRD/spec review 的紧凑输出形状参考。各章节仅在内容非空时出现；不固定章节数量、字数或 review 轮数。

## Reviewed Spec

经评审确认的需求规格。包含：
- 从 PRD 中提取并验证过的功能描述。
- scope 与 non-scope。
- actors 与 scenarios。
- acceptance criteria（可验证形式）。

## Agent-Ready Implementation Brief

供 feature-delivery 后续 agent 使用的执行简报。包含：
- 需要实现的本质（不是怎么实现）。
- capability owner 和 delivery surface。
- 关键约束与边界条件。
- 依赖 / fallout / rollout（仅在确认存在时记录）。

## Decision / Assumption / Evidence Log

评审过程中产生的决策与假设追溯：
- 每条 decision：谁做的、基于什么 evidence、时间/版本。
- 每条 assumption：为什么是 assumption 而非 confirmed fact、验证方式。
- 每条 evidence：来源、内容摘要、provenance 与 freshness 状态。

## Blocking Questions

仅当存在未解决的阻塞问题时输出。每条问题按 `references/blocking-questions-template.md` 格式记录。

如无阻塞问题，此章节省略。

## Feature-Delivery Handoff

交回 feature-delivery 的上下文：
- 最终状态：implementation-ready / blocked-needs-decision/evidence / redirected。
- 若 blocked：具体阻塞项和 recovery path。
- 若 redirected：路由目标和原因。
- 建议的下一步（若有）。

## 格式规则

- 空章节直接省略，不留占位。
- 不设字数下限或上限。
- 不预设 review 轮数——可以一轮通过也可以多轮迭代直到阻塞项关闭。
