---
name: repo-{{REPO_NAME}}
description: |
  Repo-local skill for the {{REPO_NAME}} repository. Provides repo-specific context,
  working rules, reference docs, and self-improvement methodology. Use when a task
  needs local source-of-truth guidance, runtime entrypoints, validation flows, or
  repo-local working rules.
---

# {{REPO_NAME}} — Repo Skill

## Repo Identity

- **Repo**: `{{REPO_NAME}}`
- **默认分支**: `BOOTSTRAP_REQUIRED`
- **Owner**: `BOOTSTRAP_REQUIRED`
- **Status**: `BOOTSTRAP_REQUIRED`

## 检测到的技术栈

从仓库内 package manifest、构建文件和 CI 配置中观察到的语言和构建系统：

- **语言 / 运行时**: `BOOTSTRAP_REQUIRED`
- **构建系统**: `BOOTSTRAP_REQUIRED`
- **包管理器**: `BOOTSTRAP_REQUIRED`
- **测试框架**: `BOOTSTRAP_REQUIRED`

## First-Workflow Role

此仓库在 first workflow 中的角色和边界：

- **角色**: `BOOTSTRAP_REQUIRED`
- **边界**: `BOOTSTRAP_REQUIRED`

## First-Workflow Semantic Execution Trace

当此 repo 承担 issue/bugfix、回归或代码修改时，先填实这张 trace，再进入 patch：

| Field | Observed value | Evidence pointer | Status |
|---|---|---|---|
| Initial signal shape | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |
| Semantic value at risk | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |
| Rewrite / normalize boundaries | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |
| Owning sink | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |
| Regression proof | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |
| Verification command and status | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` | `BOOTSTRAP_REQUIRED` |

Trace rules:

- `Semantic value at risk` 必须描述实际可能错误的 request field、response field、表达式、查询谓词、生成 SQL fragment、resource identity 或 error code，不能只写“功能异常”。
- `Rewrite / normalize boundaries` 必须列出真实调用链中的 boundary 和 repo-relative pointer；不能从 response field 缺失直接推断 collector 是 root cause。
- 涉及过滤、聚合、表达式、生成 SQL 或外部 provider 时，显式检查 `where` / `having`、表达式 rewrite、query sink 和 response assembly 的关系。
- `Owning sink` 必须是证据支持的最窄 owner；外层 controller/helper 只是入口时，要写出继续向下追踪的依据。
- 只有实际运行成功才能写 `executed-pass`；从 manifest、CI、README 或代码读到但未运行的命令写 `observed-not-executed`；缺工具或环境写 `blocked`。
- 如果该 repo 不承担 first workflow，所有字段写 `not-applicable` 并给出 repo-role evidence，不得留下模板占位符。

## Working Rules

仅保留最高信号的 repo-local 规则。其余放入子文件。

- **入口**: 先读本文件做任务路由，再查阅对应子 skill 或 reference。
- **构建 / 运行 / 测试**: 见 `skills/references/test-entrypoints.md` 和 `skills/references/runtime-and-testability.md`。
- **架构问题**: 见 `skills/references/architecture-map.md`。
- **事实权威**: 见 `skills/references/source-of-truth.md`。
- **代码审查**: 见 `skills/code-review/SKILL.md`。
- **自我改进**: 见 `skills/self-skills-improve/SKILL.md`。

### 本地反模式

- 不在此 repo skill 中重复 company Jarvis 指导——引用即可。
- 不将 repo-local 事实提升到 company Jarvis 而不经过 self-improvement 决策门（`skills/self-skills-improve/SKILL.md`）。
- 不硬编码随开发者环境变化的路径或凭据。
- 不用通用模板冒充成熟 reference；checked-in 可观察事实由 agent 直接读取，不要求 owner 确认；策略或语义歧义写清证据缺口。
- 没观察到的可选类别不得编造——写 `not-observed` 或 `not-applicable` 并记录实际扫描范围。

## 入口点

- **构建**: 见 `skills/references/test-entrypoints.md`
- **测试**: 见 `skills/references/test-entrypoints.md`
- **事实权威**: 见 `skills/references/source-of-truth.md`
- **参考**: 见 `skills/references/` 下各文件

## Boundaries

**此 repo skill 负责：**

- 完全位于 {{REPO_NAME}} 仓库内的事实。
- 此仓库特定的构建 / 运行 / 测试命令。
- 本地验证和安全变更规则。
- 此代码库特定的代码审查标准。
- 此仓库历史中可供校准的事实、验证入口和 durable repo-local 结论；case 注册表和运行产物保存在 company Jarvis。

**委托给 company Jarvis 的内容：**

- 公司级路由和身份协调。
- 跨仓库工作流协调。
- 组织级 rollout 和 ownership 策略。
- 通用 skill 创建和方法论规则（上游 `create-jarvis-skill`）。

## Task Routing

**使用此 skill 的场景：**

- 在 {{REPO_NAME}} 仓库内工作。
- 需要 repo-local 事实、命令或工作规则。
- 对 {{REPO_NAME}} 变更进行代码审查。
- 调试此仓库中的构建 / 测试 / 运行时故障。

**移交 company Jarvis 的场景：**

- 问题涉及多个仓库。
- 任务需要组织级策略决策。
- 问题是关于通用 skill 方法论，而非仓库特定内容。

## Repo-local 基线验证清单

- [ ] 所有临时占位已被可观察事实或明确的不可访问状态替换。
- [ ] 默认分支来自 remote HEAD 或 VCS project metadata；当前 checkout 分支没有被当成 default branch 证据。
- [ ] 技术栈来自实际 package manifest / 构建文件。
- [ ] First-workflow 角色来自仓库在 company source map 中的位置。
- [ ] 新 agent 进入此仓库时能发现如何验证其工作。
- [ ] Repo-local 事实与公司级指导明确分离。
- [ ] First-workflow repo 已填 semantic execution trace：signal、semantic value、rewrite boundaries、owner sink、regression proof 和 verification status 均有可解析 evidence pointer。
