# 输出模板

先写 intake 结论，再决定是否建 issue。所有 outcome 共享以下头部字段。

## 共享头部

```md
<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->
## Intake summary
- reporter-labeled type:
- normalized claim type:
- final outcome:
- should create new issue: yes / no
- candidate issue project:
- candidate module:
- source:
```

`ready-to-file-*` 描述必须保留首行来源标记。

## A. ready-to-file-bug

建议标题：`[Bug] <一句话症状> - <affected surface>`

```md
<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->
## Intake summary
- reporter-labeled type:
- normalized claim type: supported-contract defect hypothesis
- final outcome: ready-to-file-bug
- should create new issue: yes
- candidate issue project:
- candidate module:
- source:

## Observed
-

## Expected
-

## Reproduction or observation
-

## Evidence pointers
-

## Impact
- affected users / roles:
- blocked workflow / business impact:
- frequency:
- regression signal:
- workaround:

## Historical check
- related existing issue(s):
- overlap vs delta:
- why this is not duplicate / by-design:

## Decision
ready-to-file-bug
```

## B. ready-to-file-feature

建议标题：`[Feature] <期望能力> - <适用场景>` 或 `[Enhancement] <已有能力> - <优化点>`

```md
<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->
## Intake summary
- reporter-labeled type:
- normalized claim type: product-scope capability gap
- final outcome: ready-to-file-feature
- should create new issue: yes
- candidate issue project:
- candidate module:
- source:

## User goal
-

## Context / current gap
-

## Value
-

## Acceptance criteria
-

## Product fit
-

## Historical check
- related existing issue(s) / rejected history:
- overlap vs delta:
- why this is not duplicate / historical wontfix:

## Evidence / references
- reporter wording summary:
- attachment summary:

## Decision
ready-to-file-feature
```

## C. 非 Filing 结果

适用于 `duplicate`、`by-design`、`rejected-request / wontfix-history`。

```md
<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->
## Intake summary
- reporter-labeled type:
- normalized claim type:
- final outcome:
- should create new issue: no
- candidate issue project:
- candidate module:
- source:

## 为什么不建新 issue
-

## Supporting source
- known issue / existing issue:
- design decision / boundary:
- rejected request / wontfix history:

## Overlap vs delta
- 与历史条目的重叠：
- 当前 case 的差异：
- delta 是否改变 root cause / 产品边界 / 验收边界：是 / 否
- 对 disposition 的影响：

## Recovery
- 应对 reporter 说什么：
- workaround / 替代路径：
- 什么变化后值得重新 intake：

## Evidence pointers
- live behavior / current evidence:
- issue / comment / decision source:
- fix scope / version check if relevant:

## Decision
duplicate / by-design / rejected-request / wontfix-history
```

## 写作规则

- 标题只含一个主要问题，不写叙事文章。
- 证据先列文本证据再列附件。
- 写回 issue 时使用受众合适的语言；需保真时保留原文标识符和错误文本。
- 当 claim 涉及"之前修过/被拒过/旧工单重复"时纳入真实来源，非二手判断。
- 模块判断不确定写候选，不假装确认。
- 无实际值的 section/field 直接省略，不填 unknown/n-a 等占位符。
- 非 filing 结果必须用人话写，让 reporter 理解为什么这次不应建新 issue。
