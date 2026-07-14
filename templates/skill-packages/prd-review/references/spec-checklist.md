# SPEC Checklist：Implementation Readiness Gate

此 checklist 用于判断一个 PRD/spec 是否已达到 implementation-ready——即后续 agent 或开发者可以安全地开始执行。每个检查项仅在 PRD 实际涉及该方面时才适用；不要求所有字段都出现，不适用则跳过。

## Gate 维度

### Goal
- [ ] PRD 中有明确的 user goal 或 business goal，不是仅描述了实现方式。
- [ ] goal 与 proposed solution 的边界清晰：goal 是「要达成什么」，solution 是「怎么达成」。

### Scope
- [ ] 功能范围有显式边界——做了什么、不做什么都清楚。
- [ ] 如果存在多个可能的 scope 理解，已明确选择了哪一个（或标注待决定）。

### Non-Scope
- [ ] 明确了不在本次范围内的内容，避免执行时的范围蔓延。
- [ ] 如果某些内容在当前 PRD 中看似相关但实际不在此范围，已显式排除。

### Acceptance
- [ ] 每个 acceptance criterion 是可观察、可验证的——不是「体验好」「性能优」等主观描述。
- [ ] acceptance 覆盖了关键路径和主要边界情况。
- [ ] 如果有多个 actor 或场景，各自的 acceptance 已区分。

### Evidence
- [ ] 每个 material requirement 能追溯到原始证据（source doc、data、issue、decision record）或 authority decision。
- [ ] 声称的现有能力或契约有 source 支撑，不是凭空假设。

### Owner
- [ ] 明确了 capability owner——谁拥有此能力的定义权；执行 owner 如不同也已按 surface 分开记录。
- [ ] 明确了 delivery surface——此能力通过什么 surface 对外暴露和交付。
- [ ] 如果涉及多个 capability owner，各自的边界和责任已划分。

### Surface
- [ ] 受影响的交付 surface 已识别（不限于某种特定技术形态）。
- [ ] 各 surface 的验证方式已明确（如何确认变更生效）。
- [ ] 如果变更影响多个 surface，彼此之间的一致性要求已说明。

### Unknown
- [ ] 所有会改变 scope / route / acceptance 的 unknown 均已显式标出，并形成 blocking question。
- [ ] 每一个 blocking question 都记录了已查 source、为何 agent 无法自行回答、decision owner。
- [ ] 不改变 scope / route / acceptance 的 unknown 可以标记为非阻塞并附带说明。

## 使用规则

1. 按需检查：只检查 PRD 实际涉及的维度，不强制填满所有条目。
2. 阻塞判定：任何 material 维度的缺失（即缺失会影响后续执行正确性）都应导致 `blocked` 而非 `ready`。
3. 显式标注：跳过某维度的原因（如「本次变更不涉及跨 surface」）应简要标注，避免读 checklist 的人猜测到底是真的不适用还是被遗漏。
