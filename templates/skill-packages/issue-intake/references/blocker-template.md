# Blocker 模板

证据不足时使用。`blocked-needs-evidence` 是正常的 intake 结果，不是失败。

## 模板

```md
<!-- {{COMPANY_SLUG}}-issue-intake:v1 -->
## Intake summary
- final outcome: blocked-needs-evidence
- should create new issue: no
- candidate module:
- source:

## 为什么不 ready
-

## 已查内容
-

## 缺失事实及为何影响 disposition
-

## 手头已有证据
-

## 恢复问题
（按当前缺口动态生成，只列关键缺失项，不机械填充固定数量）

## Decision
blocked-needs-evidence
```

## 使用规则

- 按当前缺口动态生成恢复问题，不机械套用固定问卷或固定数量问题槽。
- 已有信息填入"手头已有证据"，避免 reporter 重复提供。
- Blocker 目标是让下一轮输入变成可判定的 intake 结论，非推责任。
- 已知 workaround 或疑似方向写入"已查内容"。
