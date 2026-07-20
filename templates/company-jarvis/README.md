# company-jarvis 母版模板

> 本目录是 company JARVIS 模板的**母版**。它不会被整体复制到客户或公司仓库中。运行时 agent 从 bootstrap-state.json 读取已确认的参数，调用实例化脚本将模板渲染到目标目录。

## 目录结构

```text
templates/company-jarvis/
├── README.md          ← 本文件：母版说明
├── repo/              ← company JARVIS 仓库母版（base 子命令渲染）
├── module/            ← 单模块合约模板（module 子命令渲染）
├── source/            ← source route contract 模板（source 子命令渲染，仅含 README.md）
├── artifact/          ← 引导期产物模板
```

### repo/ — company Jarvis 母版

`repo/` 是 {{COMPANY_NAME}} JARVIS 仓库的母版。它包含：
- 根文件：README.md、MAINTENANCE.md、jarvis.toml、AGENTS.md、CLAUDE.md、SKILL.md
- 入口技能模板：`skills/__COMPANY_SLUG__-jarvis/SKILL.md`
- 17 个跨公司核心持久引用文件（`references/`）。客户/产品/工具链/流程特有的 reference 不由母版预装，只能在 bootstrap 各 phase 中按 evidence 生长。
- 跨模块合约（`cross-cutting/`）
- 工具索引（`tools/README.md`）
- 评估入口（`evals/evals.json`）

通过 `base --state <bootstrap-state.json>` 渲染到 `paths.jarvis_target_home`。

**重要区分**：
- `runtime_root`：jarvis-box 运行时的根目录（如 `/opt/jarvis/acme`），由 jarvis-box 管理
- `jarvis_target_home`：JARVIS 仓库的渲染目标目录，是 runtime_root 下的 JARVIS 实例位置
- 两者是不同的概念，不能混用

**注意**：`repo/` 是 company JARVIS 母版，不是 repo-local skill 模板。repo-local skill 的模板在 `templates/repo-local-skill/` 中。

### module/ — 模块合约模板

通过 `module --state <...> --name <模块名>` 渲染单模块五文件合约（overview、known-issues、decisions、rejected-features、test-coverage）到 `modules/<name>/`。

### source/ — source route contract 模板

通过 `source --state <...> --name <source名>` 渲染 source route contract（仅 README.md）到 `sources/<name>/README.md`。

**source route 与 source-helper skill 的分工**：
- **source route**（`sources/<name>/README.md`）：最小路由信息——identity、access、owner、query、retrieval evidence、redaction、freshness、writeback、status。帮助 agent 到达和初步理解 source，不做深度操作。
- **source-helper skill**（`skills/<slot>-<name>/SKILL.md`）：当 agent 需要对特定 source 做精确检索、证据引用、允许的写回或安全边界处理时，通过 `package --kind generic-source --name <slot>-<name>` 生成。技能名带公司命名空间，仍路由到 `sources/<name>/README.md`；repo 的构建、测试和目录真相留在 repo-local skill。

简单说：source route 是路标，source-helper skill 是操作手册。Phase 9 如需要 source-helper，应使用 `package --kind generic-source`。

### artifacts/ — 引导期产物模板

引导和运营过程中生成的产物模板（pilot registry、writeback log、day2 operation 等），供各 phase 参考。

## 实例化方式

用户**不需要**手动提供六个参数。运行时流程为：

1. jarvis-box runtime 在 readiness gate 阶段收集确认信息
2. 确认信息写入 `bootstrap-state.json`
3. runtime agent 读取 bootstrap-state.json
4. 调用 `instantiate_company_jarvis.py base --state <bootstrap-state.json>` 渲染母版；base 同时从 `templates/skill-packages/` 安装四个通用方法 skill 和三个 slot 化 starter workflow
5. 后续按需调用 `module`、`source`、`package` 子命令

## 渲染 Token

以下 token 由实例化脚本从 bootstrap-state.json 自动提取并替换：

| Token | 来源 | 缺失行为 |
|---|---|---|
| `{{COMPANY_NAME}}` | `identity_reconciliation.company_identity.name` | fail |
| `{{COMPANY_SLUG}}` | `identity_reconciliation.company_identity.slug` | fail |
| `{{PRODUCT_IDENTITY}}` | `identity_reconciliation.confirmed_product_identity` | 渲染为 `unresolved-product-identity` |
| `{{RUNTIME_ROOT}}` | `confirmed_answers.runtime_root` 或 `paths.runtime_root` | fail |
| `{{ENTRY_SKILL_PATH}}` | `paths.entry_skill` | fail |
| `{{VCS_HOST}}` | `confirmed_answers.vcs_host` 或 `confirmed_answers.gitlab_host` | 渲染为 `needs-evidence` |
| `{{COMPANY_OWNER}}` | `confirmed_answers.company_owner` 或 `confirmed_answers.owners` | 渲染为 `needs-owner-confirmation` |
| `{{SOURCE_NAME}}` | source 子命令的 `--name`；generic-source package 使用去掉 `<slot>-` 前缀后的名称 | — |
| `{{SKILL_NAME}}` | package 子命令的 `--name` | — |
| `{{MODULE_NAME}}` | module 子命令的 `--name` | — |

## 母版与渲染实例

- 本目录是**母版**。母版修改会影响未来的实例化。
- 客户或公司的 JARVIS 实例是已渲染的副本，token 已替换为公司实际值。
- 不要把客户专有内容放进母版。
- 不要把 secret、凭据、专有逻辑放进母版。
- 脱敏规则和访问控制属于实例，不属于母版。

## 母版演进

母版随 create-jarvis-skill 方法论演进而更新：
- 新产物类型在引导过程需要时添加
- 现有模板在方法论通过 pilot 检测到缺口时更新
- 新的 token 在跨实例需要新变量内容时添加
- 公司中立的改进贡献回 create-jarvis-skill 上游
- 公司特定的定制**不**回馈——它们留在实例中

## repo-local skill 模板

repo-local skill 模板位于 `templates/repo-local-skill/`。详见该目录的 README。repo-local skill 的实例化使用 Phase 8（repo-local skills）流程，与 company JARVIS 母版的渲染是独立的。
