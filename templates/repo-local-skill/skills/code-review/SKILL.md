---
name: code-review-{{REPO_NAME}}
description: |
  Code-review guidance specific to the {{REPO_NAME}} repository. Defines review
  scope, repo-specific checks, precheck integration, and writeback policy.
  Use when performing or requesting code review on {{REPO_NAME}} changes.
---

# {{REPO_NAME}} — Code Review Guidance

## 原则

findings-first review：先读任务意图、diff、相关实现和验证证据，用仓库自身事实和 reference 做判断。本文件只增加 repo-local 检查项，不复制跨仓库工作流。

## Scope

### 在范围内

- 正确性：逻辑错误、边界情况、数据完整性。
- 架构适配：是否尊重 {{REPO_NAME}} 模块边界（见 `skills/references/architecture-map.md`）。
- 验证充分性：实际执行过哪些检查，证据是否覆盖本次变更的风险；测试文件存在本身不算通过。
- 运行时安全：资源泄漏、并发问题、禁止操作（见 `skills/references/runtime-and-testability.md`）。
- 风格一致性：是否遵循仓库已有惯例。
- 回归风险：是否命中 repo-local reference 中已沉淀的历史失败模式；需要回放时按 `skills/references/history-replay-loop.md` 路由到 company Jarvis case registry。

### 不在范围内

- 与此仓库事实无关的公司级策略。
- 与变更目的无关的通用重构。
- 跨仓库协调问题——标记后移交。

## Review 顺序

1. **目的与范围**：任务/MR/PR 描述是否与实际 diff 一致，是否混入无关变更。
2. **完整 diff**：读取变更及必要上下文，不只看摘要或文件名。
3. **事实路由**：按 touched surface 读取对应 repo-local reference 和 source-of-truth。
4. **风险判断**：列出可能的正确性、兼容性、数据、并发、运行时或回归风险，但只保留本次 diff 实际相关的项。
5. **验证证据**：从 `test-entrypoints.md` 选择与风险匹配的精确命令；明确哪些实际执行、哪些未执行、哪些阻塞。
6. **Precheck**：运行 `bash skills/code-review/scripts/precheck.sh`，只把它作为 package contract 与环境线索证据。
7. **Findings**：按严重性输出可定位、可行动的问题；没有 finding 时说明剩余验证缺口。

## 仓库特有检查

下表只记录仓库实际代码、配置、CI 和历史证据支持的检查项。不要预设该仓库一定存在某类风险；没有观察到的类别不创建通用检查项。

| Trigger / Surface | Repo-local Check | Evidence |
|---|---|---|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## 审查验证

审查必须按风险选择真实验证，不能因为测试文件存在就判通过。precheck 只是 bootstrap-safe orientation/fixed-contract check，不代表 build/test/runtime 通过。

## Precheck Integration

审查前运行：

```bash
bash skills/code-review/scripts/precheck.sh
```

Precheck 是 bootstrap-safe orientation/fixed-contract check，确认 canonical 文件已填充，并报告检测到的 manifest、CI 与本机工具线索。

**precheck 通过 ≠ build/test/runtime 通过**。实际构建和测试验证由审查者按风险选择执行。
