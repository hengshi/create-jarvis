---
name: runtime-and-testability-{{REPO_NAME}}
description: |
  Runtime and testability guidance for the {{REPO_NAME}} repository. Covers
  runtime environment, startup entry points, environment variables, external
  dependencies, logs and diagnostics, and forbidden operations.
---

# {{REPO_NAME}} — Runtime and Testability

## Runtime Environment

从仓库内 package manifest 和构建文件中观察到的运行时需求：

| 需求 | 版本/约束 | Evidence |
|------|-----------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Service Startup Entry Points

| Service / Process | Exact Start Command | Working Dir | Evidence | Status |
|-------------------|---------------------|-------------|----------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Environment Variables

仅列出变量名，不记录值：

| 变量名 | 用途 | Required / Optional | Evidence |
|--------|------|---------------------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## External Dependencies

| Dependency | Type | Local Requirement | Substitute / Mock | Evidence |
|------------|------|-------------------|-------------------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Logs and Diagnostics

| Source | Location / Command | Format | Evidence |
|--------|--------------------|--------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Safe / Dry-Run Options

| Operation | Exact Safe / Dry-Run Command | Evidence |
|-----------|------------------------------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Forbidden / Unsafe Operations

*以下内容仅记录从此仓库实际代码、配置和文档中观察到的禁止操作。每条必须有 evidence pointer，不编造通用臆造规则。未观察到此类操作时写 `not-observed` 并记录扫描范围。*

| Operation | Risk | Evidence |
|-----------|------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Run Verification

| Check | Exact Command | Working Dir | Evidence | Status |
|-------|---------------|-------------|----------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## 证据约束

1. 只能记录仓库证据支持的 runtime、环境变量名、依赖、日志、安全/dry-run/禁止操作。每条必须有 evidence pointer。
2. 未观察到某类 runtime、safe mode 或禁止操作时写 `not-observed` / `not-applicable` 并记录扫描范围，不用通用安全常识填空。
3. 环境变量只记录名字，不记录值。
4. 外部依赖根据实际代码引用、配置和启动链记录，不预设通用依赖。
5. 命令沿用 `test-entrypoints.md` 的状态：未运行写 `observed-not-executed`，只有实际成功运行才能写 `executed-pass`。
