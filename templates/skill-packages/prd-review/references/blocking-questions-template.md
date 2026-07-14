# Blocking Questions Template

此模板用于记录 PRD/spec 评审中发现的阻塞问题。只记录会改变 scope / route / acceptance 的未决事项；不记录不改变决策的细节澄清。

## 每条阻塞问题必须包含

### 问题本身
用一句话描述什么尚未决定或未知，及其对 scope / route / acceptance 的潜在影响。

### 已查 Source
列出 agent 已查询的所有 source，包含：
- 查了什么（source 类型和位置，不是虚构路径）。
- 找到了什么（如果有部分信息）。
- 为什么这些 source 不足以回答此问题。

### 为何 Agent 无法自行回答
具体说明：
- 这是一个需要 authority 做 product tradeoff 的决策（agent 无权决定产品取舍）。
- 还是所有已知 source 都已穷尽但事实仍不存在（需要人提供新事实）。
- 不能是 agent 能力不足或懒得查更广——必须声明已穷尽的范围。

### Decision Owner
谁能关闭此问题——具体角色或 authority，不是泛指的「产品」或「开发」。

### 恢复证据
当此问题被回答后，用什么样的证据可以确认它已关闭——例如：更新后的 spec 章节、authority 的书面确认、新的 source doc。

## 数量与格式

- 阻塞问题数量不固定——有多少列多少，不为凑数虚构问题，也不为看起来干净而合并不同性质的问题。
- 如果评审没有发现任何阻塞问题，此部分省略（不输出空清单）。

## 非阻塞问题

以下情况不应列在此模板中：
- agent 可以通过已有 source 自行回答的问题。
- 不影响 scope / route / acceptance 的细节疑问——可以附带在输出中作为备注，但不算阻塞。
- 纯实现细节（用哪种具体技术手段）——除非该选择会改变 scope 或 acceptance。
