# Phase 7 - 确定性实例化 company Jarvis 母版 + 填 customer modules/source routes

目标：确定性实例化客户 `<slot>-jarvis` repo 的结构骨架、默认方法内核和 starter workflows。

Phase 7 的职责是建立容器和路由骨架，安装固定默认 skills，并把 Phase 6 已确认的客户事实写入 module overview、source route 和 first routing。除默认三个 workflow 外，它不自由生成客户 workflow/source-helper skills。

## 核心原则

必须运行确定性母版实例化器（deterministic master template instantiator），不能让 agent 按描述性 stub 重写 README、MAINTENANCE、entry 或 references。

Phase 7 的容器骨架本身不是完成态。以下规则保证容器内填入的是有用的客户事实而非模板残留：

### 从已确认身份填充

- 公司入口从已确认的 product identity、实际 repo-role map、实际 source route 和已有 reference 文件名填充。不得使用 reference-company 示例或泛化别名。
- 公司入口 skill 中的所有链接必须可解析。repo-local handoff 名称必须是实际授权的 repo 名称/路径，不是 reference-company 示例或泛化别名。

### Runtime 路径与命令

- 正式 durable 文件必须使用 runtime 变量/contract（例如 bootstrap state 中确认的 runtime root 或 `JARVIS_RUNTIME_ROOT`），不得保留 E2E 测试机绝对路径。
- Runtime 行为和命令必须从已安装的 `jarvis-box version`、`--help`、`doctor`/`init`/`status` 和已安装文件中观察。不得发明脚本、runtime 命令或路径。

### 已确认产品身份

- 对于已确认的产品身份，任何正式 module/root/entry 文件中不得保留未解决的身份或对该身份的 `needs-owner-confirmation`。

### Source Scaffold 替换

- 对每个可访问的 source，将 source scaffold 替换为具体 route。`needs-evidence`、`REFERENCES_PATH` 和示例占位符在可访问 route 中是 phase blocker。
- Module overview 完成仍需 Phase 6 的语义锚点，不仅仅是已有指针。空洞的 module overview（只有名称和指针但没有业务含义）不能通过 Phase 7。

开始 Phase 7 前必须读取：

- `templates/company-jarvis/README.md`
- `scripts/instantiate_company_jarvis.py`（了解 subcommand 结构）

`hengshi-jarvis` 的成熟形态是：

- root repo 是公司级 Jarvis 仓库；
- `skills/<slot>-jarvis/SKILL.md` 是统一入口；
- 四个通用方法 skill 与三个 `<slot>-workflow-*` starter workflow 由 base 创建；Phase 9 定制 starter workflows 并创建额外能力；
- 长期 routing / quality / writeback / runtime 规则在 `references/*.md`；
- 产品/业务知识在 `modules/*`、`sources/*`、`cross-cutting/*`；
- repo-local execution truth 留在各业务 repo 的 `skills/`，不复制进 company Jarvis；
- pilot / replay / controlled writeback 的执行证据可以进 `evals/` 或 `_bootstrap/`，不能变成顶层主骨架。

## 必须产物

### Root files
- `README.md`
- `MAINTENANCE.md`
- `jarvis.toml`
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

### Canonical company entry
- `skills/<slot>-jarvis/SKILL.md`

### Mandatory method skills
- `skills/ponytail/SKILL.md`
- `skills/writing-durable-docs/SKILL.md`
- `skills/jarvis-self-improve-skill/SKILL.md`
- `skills/stop-slop/SKILL.md`

### Editable starter workflows
- `skills/<slot>-workflow-issue-post-check/SKILL.md`
- `skills/<slot>-workflow-bugfix-loop/SKILL.md`
- `skills/<slot>-workflow-feature-delivery/SKILL.md`

### Root runtime contracts
- `bootstrap-state.json`
- `bootstrap-result.json`

### Complete baseline references (17 files)

The template `templates/company-jarvis/repo/references/` contains the full neutral master set:

- `agent-engineering-quality-gate.md`
- `canonical-repo-fleet.md`
- `capability-delivery-surfaces.md`
- `completion-standard.md`
- `history-replay.md`
- `issue-claim-normalization.md`
- `jarvis-box.md`
- `jarvis-first-routing.md`
- `minimal-closure-card.md`
- `module-boundary-routing.md`
- `next-hop-compression.md`
- `redaction-rules.md`
- `repo-pre-push-review-loop.md`
- `runtime-governance-quick.md`
- `runtime-governance.md`
- `verify-evidence-matrix.md`
- `writeback-governance.md`

这 17 个 reference 是所有公司 bootstrap 时都需要的跨公司核心规则。客户特有、产品特有、工具链特有或流程特有的 reference 不能从 HENGSHI 母版预装，也不能为了凑数量而创建；只能按需从以下来源生长：

- Phase 6 客户 evidence 中发现的客户特有知识
- Phase 9 package 实例化时带入的工具链/平台配套规则
- Phase 11 shadow pilot 暴露的客户流程专属约束
- Phase 12 history replay 揭示的方法缺口
- Phase 13 controlled writeback 确认后写回的规则

### Modules (per Phase 6 coverage matrix)
- `modules/<module>/overview.md`
- `modules/<module>/known-issues.md`
- `modules/<module>/decisions.md`
- `modules/<module>/rejected-features.md`
- `modules/<module>/test-coverage.md`

### Source routes (per Phase 6 source map)
- `sources/<source>/README.md`

### Cross-cutting and tools
- `cross-cutting/module-interactions.md`
- `tools/README.md`

可选过程产物：

- `_bootstrap/jarvis-build-brief.md`
- `_bootstrap/rollout-confirmation-checklist.md`
- `_bootstrap/shadow-pilot/...`
- `evals/history-replay/...`
- `_bootstrap/controlled-writeback-log.md`

## Phase 7 禁止生成的内容

以下内容不得在 Phase 7 自由生成，必须由 Phase 9 按 generation plan 实例化：

- 三个 starter workflow 之外的 workflow skills
- source-helper skills（`skills/<source-skill>/SKILL.md`）
- 任何未在 Phase 6 generation plan 中列为 `create-now` 或 `create-scaffold-needs-pilot` 的通用 skills

以下 install-owned skills 不得复制到 company repo：
- `jarvis-box-doctor`
- `jarvis-box-init`
- `jarvis-box-monitor`

以下 external reference skills 不得复制到 company repo：
- 来自 jarvis-box install 的外部 reference skills（如 create-jarvis-skill 本身）

Phase 14 只检查/登记这些 install-owned runtime 和 external skills 的状态，不复制它们。
`jarvis-self-improve-skill` 是无条件安装的 company 方法论 package；它只能路由 runtime 提供的证据和写回边界，不复制 runtime collector/scheduler。

## 步骤

1. 运行确定性母版实例化器 base 子命令：
   ```
   python scripts/instantiate_company_jarvis.py base --state <bootstrap-state.json>
   ```
   这会将 repo 母版和默认 skill packages 渲染到 `paths.jarvis_target_home`，包括 root files、17 references、canonical entry、四个方法 skills、三个 starter workflows、cross-cutting、tools inventory、evals skeleton。

2. 按 Phase 6 module coverage matrix 为每个 `included` module 运行：
   ```
   python scripts/instantiate_company_jarvis.py module --state <...> --name <confirmed exact name>
   ```

   这一步只生成安全的五文件容器。随后必须至少完成 `overview.md`：

   - 用客户语言说明业务目的、用户/角色和能力边界；
   - 写 first-hop routing、first proof、常见 false owner；
   - 至少写一个 `<repo-name>:<repo-relative-path>` 证据，且路径在授权 checkout 中真实存在；
   - 记录 observed fact 与实际 retrieval/check；
   - 删除 `BOOTSTRAP_REQUIRED` 标记。

   另外四个历史文件在 bootstrap 尚无可提升证据时可以保持“尚未提升条目”的安全空状态。这不代表客户历史中不存在 issue、decision、rejected feature 或 test，只代表当前 bootstrap 没有冒充事实。

3. 按 Phase 6 source map 为每个 source 运行：
   ```
   python scripts/instantiate_company_jarvis.py source --state <...> --name <confirmed exact name>
   ```

4. 检查默认七个 skills 的文件和 frontmatter 名称。不要在此 phase 创建其他 workflow 或 source-helper skill（Phase 9 的职责）。
5. 渲染 runtime / agent bridge files（`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`），它们随 base 子命令自动渲染，指向 canonical entry skill 和 runtime pre-read 规则。
6. 用 Phase 6 repo-role/workflow/module evidence 填写 `references/jarvis-first-routing.md`、`references/canonical-repo-fleet.md` 和 `cross-cutting/module-interactions.md`。没有 peer product、版本索引或 company-specific tool 证据时，相关文件写明确未登记状态，不填示例数据。
7. 在离开 Phase 7 前重新读取 root `README.md` 的“模块 / 数据源 / 工作流 / 仓库”四个 scope 索引：已创建的 durable 目录必须列出实际名称；暂时没有证据时只能写 `none-yet` 和下一步，不得保留 `BOOTSTRAP_REQUIRED`。后续 `module` / `source` / Phase 9 package 实例化后要再次同步这些索引。

## Phase 7 完成 = Phase 9 可进入的门

Phase 7 `completed` 的含义：容器骨架和默认 skill 集合已就位，Phase 9 可以定制 starter workflows 并按 generation plan 实例化额外 packages。

## 停止条件

- entry skill 不存在或不可读。
- 四个通用方法 skill 或三个 slot 化 starter workflow 任一缺失。
- placeholders 看起来像 confirmed facts。
- company identity、confirmed product identity、source-detected product/brand identity 被混写成一个已确认事实。
- module 缺 evidence/confidence/confirmation status。
- module 只有 `overview.md`，缺少 `known-issues.md`、`decisions.md`、`rejected-features.md`、`test-coverage.md` contract files。
- entry skill 没有强制读取 `references/runtime-governance-quick.md`。
- entry skill 没有 `Capability / Delivery Surface / Fallout`，或没有明确 `capability owner`、`delivery surface`、docs/test fallout。
- baseline references 缺 17 个文件中的任一个。
- 任何 rendered file 仍有 `{{` 未渲染 token。
- durable customer-fact files 仍有 `BOOTSTRAP_REQUIRED`、`<repo>`、`<endpoint>`、`module-a`、`product-a` 等母版标记。
- module/cross-cutting 文件保留母版虚构的 cache、Kafka、GraphQL、Kubernetes、版本、日期、数量、stable endpoint 或其他未经客户证据支持的示例事实。
- module overview 没有至少一个可解析且真实存在的 `<repo-name>:<repo-relative-path>` evidence pointer。
- module 主要是通用工程层，或客户确认的 module 名被改写成通用 taxonomy。
- 客户确认的 module 名被改大小写，例如把 `HQL` 写成 `hql`。
- company Jarvis 不知道 pilot repos 如何支撑 first workflow。
- 输出出现顶层 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 作为主结构。
- Phase 7 在默认七个 skills 之外自由生成了 workflow/source-helper skill。
- company entry skill 没有落在 `skills/<slot>-jarvis/SKILL.md`。
- 生成内容包含私有 reference-company material。
- 把 install-owned 或 external reference skills 复制到了 company repo。
