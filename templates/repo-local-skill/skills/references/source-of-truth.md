---
name: source-of-truth-{{REPO_NAME}}
description: |
  Source-of-truth declarations for the {{REPO_NAME}} repository. Maps where
  authoritative facts live — product behaviour, API contracts, configuration
  assumptions, and test proof. Each entry must have a repo-relative pointer
  to a file, test, CI config, or doc. Updated as part of the eval loop.
---

# {{REPO_NAME}} — Source of Truth

## 原则

- **文件内容可观察**：checked-in 可观察事实由 agent 直接读取，不要求 owner 确认——文件路径、测试存在性、CI 配置、package manifest 内容、代码中的变量名和函数签名都属于此类。但仅看到路径或文件存在不足以断言语义或测试通过；必须真正读取文件内容。
- **语义解释**：代码行为的含义、API 契约的预期行为、配置值的业务影响，应先交叉读取产品文档、契约、实现、测试和历史，再用实际执行验证；只有证据仍冲突或缺失时才请求 owner 澄清。
- **实际执行证明**：测试文件必须被读过，只有实际执行才能写 `executed-pass`。测试存在不等于通过。
- 每条记录必须有 repo-relative pointer。优先 path + symbol/section（如 `src/auth/login.ts#LoginHandler`），不要要求稳定事实使用易漂移行号。

## Product Behaviour

| Behaviour | Authority | Type |
|-----------|-----------|------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

*Authority 使用 repo-relative path + symbol/section；行号只作为辅助定位。*

## API / UI Contract Locations

| Contract | Location | Type |
|----------|----------|------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Configuration Assumptions

| Key/File | Observed Value Source | Where Used |
|----------|----------------------|------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Test Evidence

*读取测试内容只能说明它声明/断言了什么；只有实际执行才能写 `executed-pass`，未执行时标记 `observed-not-executed`。*

| Behaviour | Test File / Case | Assertion Read From Test | Execution Status |
|-----------|------------------|--------------------------|------------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Resolved Semantic Notes

*本节只记录经文档、契约、运行证据、历史或 owner correction 解决过的语义歧义，并保留来源。checked-in 可观察事实不重复放在本节。*

| Note | Resolution | Source |
|------|------------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## 证据约束

1. checked-in 可观察事实直接记录，不要求 owner 确认。必须真正读取文件内容，不能仅靠路径或存在性断言。
2. 没观察到的可选类别标记 `not-observed` 或 `not-applicable`，必须记录实际扫描范围或证据；不保留通用示例事实。
3. 区分"文件内容可观察""语义解释""实际执行证明"三层；测试文件须被读过，只有实际执行才能写 `executed-pass`。
4. 优先 path + symbol/section 定位，不依赖易漂移行号。

## Forbidden Content

以下内容不得出现在本文件：

- 凭据、secret、token 或任何敏感材料。
- 属于 company Jarvis 的通用方法论。
- 无 repo-relative pointer 的断言。
- 未读取内容就从文件名、路径、依赖名或测试存在性推导出的结论。
