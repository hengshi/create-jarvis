---
name: architecture-map-{{REPO_NAME}}
description: |
  Architecture overview for the {{REPO_NAME}} repository. Maps main modules,
  important paths, extension points, generated code areas, and risk areas.
  Updated as part of the eval loop.
---

# {{REPO_NAME}} — Architecture Map

## Repo Role & Boundary

- **角色**: `BOOTSTRAP_REQUIRED`
- **边界**: `BOOTSTRAP_REQUIRED`

## Top-Level Layout

从仓库根目录观察到的顶层结构：

| 路径 | 用途 | Evidence |
|------|------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Main Modules

| Module | Path | Purpose | Evidence |
|--------|------|---------|----------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

*路径使用 repo-relative resolvable path。目录用途必须来自对其入口文件、manifest、文档或调用关系的直接读取，不能只根据目录名推断。*

## Extension Points

| Extension Point | Mechanism | Location | Status |
|-----------------|-----------|----------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Generated Code Areas

| Path | Generator | Rerun Command |
|------|-----------|---------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Risk Surface

仅记录从此仓库实际代码和配置中观察到的风险：

| Area | Observed Risk | Existing Guard / Evidence |
|------|---------------|---------------------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Related References

- `source-of-truth.md` — 产品行为事实和 API 合约。
- `test-entrypoints.md` — 各模块的测试覆盖。
- `runtime-and-testability.md` — 本地开发环境。

## 证据约束

1. 所有条目必须来自实际文件内容、目录结构、manifest、调用关系或历史证据的读取，不得只凭名称猜测用途。
2. 没观察到的类别（如无生成代码、无扩展点）写 `not-observed` 或 `not-applicable`，并记录实际扫描范围。
3. 路径使用 repo-relative resolvable path。
