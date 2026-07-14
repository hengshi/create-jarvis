# 真实 fixture 合同记录参考

此文件是记录模板和检查参考，不是虚构示例。每个实际 case 按以下方面记录，不固定字段条数或断言层数，空项直接省略。用自然语言描述应填内容，不出现占位 token。

## 应记录的内容

### source pointer

附件从哪里来——issue 链接、MR 链接、原始消息引用、文件在系统中的位置。包括获取方式与授权路径，确保后续可溯源。

### artifact identity

附件的身份信息：经脱敏的文件标识、格式、完整性摘要、freshness 和 source identity。信息应足以判断附件是否被替换或截断，但不记录提供者个人身份或无关私密元数据。

### bug shape

用自然语言说清三件事：触发条件是什么、实际发生了什么错误、正确的行为应该是什么。不套模板句式，因果链路清晰、能直接指导 fixture 保留哪些因果结构即可。

### preserved structure and causal reasoning

从真实 artifact 中保留了哪些结构，每项的因果理由——为什么它对 root cause 判断是必要的。逐条写清，不做笼统的"精简到 N 条"式总结。保留项应当尽量少，但每一项都有无法进一步删除的原因。

### deletions and redactions

删除了什么、脱敏了什么、各自的理由。同样逐条写清判定依据。例如删除某个字段是因为它在该 bug 路径上恒为默认值，脱敏某个标识符是因为它在 fixture 中只需保证唯一性而不需要暴露原始值。

### equivalence

精简后的 fixture 在什么意义上等价于原始 artifact 的 bug 触发路径。明确等价的范围（哪些因果结构完整保留）和不等价的范围（哪些数据被有意缩减，以及为什么缩减后仍能触发同一 root cause）。

### assertion contract

断言覆盖了什么行为、每个断言的目的是什么。关键是说明"这个断言失败意味着什么"——它对应的是失败契约的哪一部分、还是修复边界的哪一侧。不拘泥于断言层数或命名模式。

### pre-fix execution evidence

是否在修复前的版本上执行过、执行结果、是否确实暴露了原始症状。如果无法执行 pre-fix——例如历史版本不可构建或依赖环境已消失——记录原因和已有的替代 oracle。

### post-fix execution evidence

在修复后的版本上是否通过、执行命令、结果。如果依赖 CI 或其他验证方式而非本地执行，说明替代方式和结果。

### limitations

已知的覆盖盲区、未验证的等价性假设、仅部分验证的边界条件。也记录 fixture 依赖的外部条件。标识符参与 bug 语义时，优先使用保持格式与关联关系的脱敏 surrogate；只有无法替代且经 policy 明确允许时才保留受控 pointer，不把真实私密值复制进 fixture。

## 检查参考

完成 fixture 后逐项确认：

- 每条保留的结构都有因果理由，不是"看起来重要"
- 每条删除的数据都有删除理由，不是"看起来不重要"
- 断言直接命中 bug shape 的失败契约和修复边界，而非仅覆盖相关函数
- provenance 可追溯到原始 issue 和 artifact
- 无 secret、无 PII、无私有路径、无无关客户数据
- pre-fix 和 post-fix 的验证状态如实记录，区分"已执行通过"与"未执行但有替代证据"
- limitations 明确写出覆盖盲区和等价性假设，不暗示全面覆盖
- fixture 命名反映问题本质，非占位名

## 公司参考

- {{COMPANY_SLUG}}-jarvis/references/runtime-governance-quick.md
- {{COMPANY_SLUG}}-jarvis/references/agent-engineering-quality-gate.md
- {{COMPANY_SLUG}}-jarvis/references/redaction-rules.md
- {{COMPANY_SLUG}}-jarvis/references/verify-evidence-matrix.md
- {{COMPANY_SLUG}}-jarvis/references/writeback-governance.md
