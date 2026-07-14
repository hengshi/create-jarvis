---
name: test-entrypoints-{{REPO_NAME}}
description: |
  Test entry points for the {{REPO_NAME}} repository. Documents build, test,
  lint, and type-check commands observed from package manifests, Makefiles,
  and CI configuration. All entries must be traceable to an evidence file.
  Updated as part of the eval loop.
---

# {{REPO_NAME}} — Test Entry Points

## 状态定义

| 状态 | 含义 |
|------|------|
| `observed-not-executed` | 从 manifest/CI 配置中提取，未实际运行 |
| `executed-pass` | 已运行并通过（必须实际执行过，不可仅因测试文件存在而标记） |
| `executed-fail` | 已运行但失败 |
| `blocked` | 缺少依赖或环境，无法执行 |

## Build Commands

*每行必须记录精确命令、工作目录、证据文件和状态。未观察到构建命令时写 `not-observed` 并记录扫描范围。*

| Command | Working Dir | Evidence File | Scope | Status |
|---------|-------------|---------------|-------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

*Evidence file 使用 repo-relative path + target/script/job。读取 wrapper 实现后再记录最终入口，不要只抄 script 名称。*

## Test Commands

*每行必须记录精确命令、工作目录、证据文件和状态。严格区分 observed-not-executed、executed-pass、executed-fail、blocked；测试文件存在不等于测试通过。*

| Command | Working Dir | Evidence File | Scope | Status |
|---------|-------------|---------------|-------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Lint / Type Check Commands

| Command | Working Dir | Evidence File | Scope | Status |
|---------|-------------|---------------|-------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## CI Job References

| Job Name | CI Provider | Trigger | Config Location |
|----------|-------------|---------|-----------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Fixture / Golden File Locations

| Path | Purpose | Regenerate Command |
|------|---------|---------------------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## Known Gaps

| Gap | Impact | Status |
|-----|--------|--------|
| `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

## 证据约束

1. 命令必须来自实际文件（package manifest / Makefile / CI 配置），不得猜测。
2. 每条命令必须记录精确命令文本、工作目录、证据文件和状态。
3. 严格区分 `observed-not-executed`（从 manifest 提取但未运行）和 `executed-pass`（实际运行并通过）。测试文件存在不等于通过——只有实际执行才能写 `executed-pass`。
4. 未观察到的命令类别标记 `not-observed` 或 `not-applicable`，必须记录实际扫描范围或证据；不保留通用示例事实。
5. CI 配置是命令证据之一。必须读取 job、include、wrapper 和工作目录，不能把 job 名或配置文件存在性冒充完整可执行命令。
