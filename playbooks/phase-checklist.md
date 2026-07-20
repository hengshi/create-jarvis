# Company Jarvis Bootstrap Phase Checklist

这份文件是 runtime agent 的主说明书。

前提：jarvis-box install 已完成，客户机器已经可以通过所选 agent 发起命令行对话。Phase 0-2 属于 jarvis-box install，不在本仓库执行。

目标：从 Phase 3 到 Phase 14 按顺序执行，生成客户自己的 company Jarvis repo。最终产物必须满足 `acceptance.md`。

## 读取顺序

1. `GOAL.md`
2. `SKILL.md`
3. `acceptance.md`
4. 本文件
5. 当前 phase 详情：`playbooks/phases/phase-*.md`
6. 需要生成文件时读取 `templates/`

## 通用规则

- 已进入的当前 phase 必须得到一个状态：`completed`、`needs-input`、`blocked` 或 `failed`。尚未进入的未来 phase 一律保持 `pending`，不得根据预测提前写成 `needs-input` / `blocked` / `failed`。
- 当前 phase 未完成时，不跳到后续 phase。
- `needs-input` / `blocked` 只能来自当前 phase 已实际执行的 checklist 和停止条件。不能在 Phase 10 预判 Phase 11-14 缺什么，也不能把一个当前 phase 的状态复制给尚未进入的后续 phase。
- 当前 phase 为 `completed` 时，在同一次 runtime-agent invocation 中立即进入下一 phase；Phase 10 onboarding report 只是检查点，不是 bootstrap 终点。除非当前 phase 的真实停止条件成立，否则 runtime agent 不得总结返回。
- bootstrap phase state（`bootstrap-state.json`、`bootstrap-result.json`）和 jarvis-box Task lifecycle（Target、Task、Run、AgentConversation、Workspace）是两套不同状态。Phase 3-14 始终写 `bootstrap-state.json` 和 `bootstrap-result.json`；不得用 Task/Run 状态替代 `phase_status`。
- `bootstrap --resume` 只恢复 bootstrap answers 和 `bootstrap-state.json`，不继续旧 Run、不是 jarvis-box 的 Continue With Agent，也不是 Recover Lost Run。不得把 resume 写成 task continue/recover。
- resume 时，旧 `phase_status=completed` 只是上次 runtime agent 的声明，不是当前方法论下的验收证明。新 agent 必须先读取现有 state/result、当前产物和用户改动，再运行当前适用的确定性 gates，找到最早不满足 checklist/acceptance 的 phase；从该 phase 修复，所有更晚 phase 恢复为 `pending`。不得因为旧 state 指向 Phase 10/11 就跳过已经失效的 Phase 6/8 证据。
- 只有 Phase 11 确实通过 jarvis-box provider loop 或手动 Task 执行 shadow pilot 时，Target/Task/Run/Workspace pointer 才是可选运行证据；没有走 Task 时不得编造 ID。
- Task Workspace、同一主机 fresh CLI、`--add-dir` 都不能单独证明 Phase 12 隔离。有效 replay 必须运行在独立文件系统边界中（独立 container 或 VM），且 replay 环境只能挂载或复制 visible packet、parent commit checkout/worktree、经过裁剪的 company Jarvis runtime 副本。
- install-owned 边界：runtime sync、maintenance launcher、session self-improve scheduler、workspace cleanup、service lifecycle、agent registry/routing/failover、Task lifecycle 由 jarvis-box install 托管。company bootstrap 只检查和登记状态、owner、观测入口和恢复动作，不重新实现这些能力。
- history replay 和 session self-improvement 是两个证据来源不同的循环：history replay 从 repo Git 历史构造 visible START 和 hidden oracle，用于 bootstrap 校准；session self-improvement 从真实 agent sessions 发现重复操作失败，用于持续改进。不得合并或互相替代。
- 只要本地授权 source / repo 已存在，能由 runtime agent 自己执行的检查、扫描、生成、pilot 或 replay 不能写成“等待客户输入”；`needs-input` 只用于外部 owner 确认、凭证、权限、人工审批或本地无法取得的 artifact。
- 如果为了便于恢复而预先创建了后续 phase 的交接文件，也不能认为已经进入该 phase。当前 phase 停在 `needs-input`、`blocked` 或 `failed` 时，尚未进入的后续 phase 保持 `pending`，并在 `next_action` 写清从当前 phase 哪里恢复。
- 非交互模式缺必填输入时，返回 `needs-input`，不要编造。
- 任何 truth-bearing 字段都必须有来源：客户证据、owner 确认、pilot、history replay，或标记为 unresolved。
- company identity、客户确认的 product identity、source-detected product/brand identity 必须分开记录；未确认前不能混写成一个事实。
- `bootstrap-result.json` 是 jarvis-box runtime contract；`paths` 必须是 value 全部为字符串的 object，`missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions` 必须是字符串数组，结构化说明写进 report/rollout 文件。
- 不在 `bootstrap-result.json.paths` 中放数组、对象或文件清单；多个路径写进 `created_files` 字符串数组，或写进 onboarding report。
- `bootstrap-result.json` 必须保留稳定顶层字段：`schema_version`、`status`、`summary`、`paths`、`created_files`、`updated_files`、`preserved_files`、`missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions`、`next_action`、`phase_summary`、`generated_at`。
- `bootstrap-result.json.paths` 至少包含字符串字段：`jarvis_home`、`jarvis_target_home`、`entry_skill`。即使 `jarvis_home` 和 `jarvis_target_home` 相同，也必须同时写出。
- `bootstrap-state.json` 必须保留稳定顶层字段：`schema_version`、`phase`、`status`、`paths`、`inputs`、`confirmed_answers`、`identity_reconciliation`、`method_repo`、`phase_status`。可以额外写嵌套结构，但不能用嵌套结构替代这些顶层字段。
- `bootstrap-result.json` 和 `bootstrap-state.json` 是 company Jarvis repo 根目录下的 runtime contract 文件；不能只放在 `_bootstrap/`。`_bootstrap/` 只能保存审计副本、pilot/replay 过程证据和交接说明。
- runtime agent 尚在 Phase 3-13 或 Phase 14 未完成时，checkpoint 的 `bootstrap-result.json.status` 和 `bootstrap-state.json.status` 使用 `in-progress`；只有 runtime agent 准备返回 jarvis-box 时才写最终 `completed` / `needs-input` / `blocked` / `failed`。最终 verifier 必须拒绝遗留的 `in-progress`。
- 客户/operator 确认的 module/source 名称和 workflow 的 `<name>` 部分必须逐字节保留，包括大小写、连字符和缩写；例如 `HQL` 必须生成 `modules/HQL/`，workflow `deploy-loop` 必须生成 `skills/<slot>-workflow-deploy-loop/`。
- 只要 `missing_inputs`、`blockers`、`conflicting_inputs` 非空，或 `identity_reconciliation.status` 不是 `confirmed`，`bootstrap-result.json.status` 不能是 `completed`。
- Phase 12 没有隔离 replay agent 的 `replay-result.md` 时，`bootstrap-state.json.phase_status.phase-12-history-replay` 和 `bootstrap-result.json.phase_summary.phase-12-history-replay` 必须是 `needs-input`，不能是 `completed`。Phase 12 completed 必须至少有一次运行在独立文件系统边界（独立 container 或 VM）的有效隔离 replay；case construction 可以先完成，但不能替代 replay。
- 如果 `phase-12-history-replay` 不是 `completed`，`phase-13-controlled-writeback` 和 `phase-14-day2-operation` 不能写 `completed`。
- 只有实际进入 Phase 14 后，才能给 `phase-14-day2-operation` 写 `completed`、`needs-input`、`blocked` 或 `failed`。如果 bootstrap 停在更早 phase，Phase 14 必须保持 `pending`，不得用 day-2 交接文件替代进入和执行 Phase 14。
- 不复制 source 原文、代码大段、issue 全文、聊天记录或 secret。
- 不把通用工程层当作客户业务 module。
- 不把机器防呆通过当作 bootstrap 完成。
- 每条 durable evidence pointer 必须是完整 `<repo>:<repo-relative-path>`，不能含 `...`、Unicode 省略号、glob 或说明性后缀；指向文件或目录均可，但必须在授权 checkout 中存在。不能因为同一 module 有一条合法 pointer，就放过其他伪 pointer。
- 多个 module 批量复用同一首跳路由段落必须失败。路由目标必须能由该 module 自己的 evidence/repo role 支持；不要要求所有 module 长成同一种文体。
- `bootstrap-result` 与 `bootstrap-state` 的同名 phase 状态必须一致；顶层 status 必须一致；任一前置 phase 未 completed 时，summary 不得宣称 "complete through Phase N"。任一当前 phase 未完成时，尚未进入的后续 phase 必须保持 `pending`。
- Phase 12 中，缺 isolated replay agent 或 container/VM isolation runtime 只阻塞 replay 执行，不阻塞从 Git 历史创建 case 文件。只留下 candidate registry、没有 `cases/<case-id>/history-replay-case.md`，必须视为执行失败。Phase 12 completed 必须至少有一次运行在独立 container/VM 中的有效隔离 replay。
- Phase 7 创建 root、canonical entry、baseline references、cross-cutting、modules、sources README、tools inventory、root runtime contracts，并由 `base` 确定性安装四个通用方法 skill 和三个 starter workflow 母版。不得自由生成其他 workflow/source-helper skills。
- Phase 9 负责结合客户事实定制三个 starter workflow，并按 Phase 6 generation plan 实例化额外 workflow/source-helper package。额外 package 只能使用 `generic-workflow` / `generic-source` 母版，不能只生成统一 35 行 scaffold。
- `ponytail`、`writing-durable-docs`、`jarvis-self-improve-skill`、`stop-slop` 无条件存在。install-owned runtime skills（jarvis-box-doctor/init/monitor）不复制到 company repo；Phase 5/14 只调用、检查和登记其结果。
- 模板提供固定方法语义直接复用并参数化，客户事实由证据填充；不以文件数量要求 module 成熟度。
- evidence-inventory 中每条精确 endpoint/route/label/方法/字段/版本/数量/命令必须记录 observed fact + repo-relative pointer + retrieval/check。正式文件只能引用这些事实。无证据就省略精确值或标 `needs-verification`，禁止"按常见 REST 习惯补全"。
- repo 证据指针统一写成可解析的 `<repo-name>:<repo-relative-path>`，例如 `everest:service/src/main/java/.../DatasetProxyImpl.java`。只写 `service/`、`model/ + service/`、绝对 checkout 路径或最终 diff 才知道的 changed path 都不算合格证据。
- 非 first-workflow 的已确认 source 暂不可访问时可标 `deferred-needs-access`，不阻断 bootstrap；只有 first workflow 必需 access 才在 Phase 5/6 阻断。
- [ ] `deferred-needs-access` 的非 first-workflow source 不得同时出现在 `bootstrap-result.json.missing_inputs` 或 `blockers`；把它留在 source route/report 的状态和后续 action 中。

## Phase 3 - 启动交接

详情：`playbooks/phases/phase-03-bootstrap-invocation.md`

- [ ] 确认 jarvis-box 已调起 runtime agent。
- [ ] 确认这是 bootstrap CLI handoff，不是 Target/Task/Run 创建。
- [ ] 读取 target path、result path、working directory、prompt/context。
- [ ] 确认 selected bootstrap agent、noninteractive/resume 标志。selected bootstrap agent 是本次 bootstrap 固定选择；不声称 jarvis-box Task runtime failover 会自动接管 bootstrap。
- [ ] resume-generation 只读取已保存 answers/state 后重新发起 bootstrap agent，不继续旧 Run、不调用 native resume。
- [ ] 读取已有 `bootstrap-state.json`，如存在。
- [ ] resume 时执行完整性审计：读取已有 result/state 和用户改动，运行当前 `--stage phase-09` / final verifier（按已存在产物适用），把 blocker 映射到最早所属 phase；旧 `completed` 不覆盖当前证据。
- [ ] resume 起点是最早未通过 phase；所有更晚 phase 设回 `pending`。修复仍由对应 phase 执行，不在 Phase 3 偷做业务扫描或文件生成。
- [ ] 只交接已知信息和缺口，不做业务发现。
- [ ] 写入或更新 state/result。输出中不要求 `task_id`/`run_id`。
- [ ] 说明 jarvis-box 只在 `bootstrap-result.json` `status=completed` 时才 link `JARVIS_HOME`；`needs-input`/`blocked`/`failed` 作为未完成返回，根目录 state/result 仍用于下一次继续。

停止条件：

- [ ] target path 不安全或不可写。
- [ ] runtime agent 没有输出路径。
- [ ] resume 会覆盖用户已编辑文件。
- [ ] 把 bootstrap resume 误当 Task recovery（Continue With Agent / Recover Lost Run）。
- [ ] 把非 `completed` 的 bootstrap 当已绑定成功。

## Phase 4 - 信息接收

详情：`playbooks/phases/phase-04-bootstrap-intake.md`

- [ ] 先读取 runtime allowlist env：`JARVIS_COMPANY_SLUG`、`JARVIS_COMPANY_NAME`、`JARVIS_CONFIRMED_PRODUCT_IDENTITY`、`JARVIS_TARGET_HOME`、`JARVIS_HOME`、`JARVIS_ENTRY_SKILL`、`JARVIS_BOX_HOME`、`JARVIS_RUNTIME_ROOT`、`JARVIS_SOURCE_OF_TRUTH`、`JARVIS_FIRST_LOOP`、`JARVIS_SOURCE_SCOPE`、`JARVIS_WORKFLOW_SCOPE`、`JARVIS_MODULE_HINTS`、`JARVIS_GITLAB_HOST`、`JARVIS_GITLAB_PROJECTS`、`JARVIS_RAW_SOURCE_POLICY`；不要 dump 全量 env 或 secret。
- [ ] 收敛 company name / slug / company identity。
- [ ] 如果 jarvis-box / runtime 已传入 `company_slug` / `JARVIS_COMPANY_SLUG`，把它作为 confirmed slug；必须逐字使用，不要缩短或重新 slugify，例如不能把 `acme-claude-e2e` 改成 `acme`。
- [ ] 收敛客户确认的 product/scope identity，如客户尚未确认则标记 unresolved。
- [ ] 如果 `JARVIS_CONFIRMED_PRODUCT_IDENTITY` 存在，把它作为客户确认的 product identity；不能再把 repo/docs 中同名 product 写成 `needs-owner-confirmation`。
- [ ] 收敛 first workflow。
- [ ] 收敛 pilot repos。
- [ ] 收敛 source scope。
- [ ] 如果 `JARVIS_SOURCE_SCOPE`、`JARVIS_WORKFLOW_SCOPE` 或 `JARVIS_MODULE_HINTS` 存在，它们是客户/operator 给 agent 的 confirmed scope facts；Phase 6 必须逐项覆盖到 generation plan，不能丢弃、重命名、改大小写、合并成泛化名称，除非同一个客户/operator 明确要求改名。
- [ ] 收敛 owners / escalation path。
- [ ] 收敛 writeback policy。
- [ ] 记录 missing inputs、unresolved questions、blockers。
- [ ] 记录 identity conflicts：客户声明身份、repo/docs 中识别出的产品/品牌名、两者是否已由 owner 确认。
- [ ] 不扫描业务，不生成 module。

停止条件：

- [ ] 缺 company name。
- [ ] 缺 first workflow。
- [ ] 缺 pilot repo 或 source scope。
- [ ] `JARVIS_COMPANY_SLUG` 存在但输出 slug / entry skill / `jarvis.toml` / result paths 与它不一致。
- [ ] 缺 owner / writeback policy 且无法继续。

## Phase 5 - 就绪检查

详情：`playbooks/phases/phase-05-readiness-gate.md`

- [ ] 加载 install 提供的 `jarvis-box-doctor`，按当前安装版本和 slot 运行诊断；直接读取其人类可读结果，不增加 JSON schema。
- [ ] doctor 发现可修复缺口时加载 `jarvis-box-init`，按权限规则修复并复诊；无法修复时记录 exact blocker。
- [ ] 检查 `JARVIS_HOME` / target path。
- [ ] 检查 `JARVIS_RUNTIME_ROOT` 存在或可创建；缺失但无法创建时不能进入 Phase 6。
- [ ] 检查 source/repo 访问权限。
- [ ] 检查 secret 边界，只记录 configured/unconfigured，不记录值。
- [ ] 检查 writeback 是否允许。
- [ ] 判断是否能进入 Phase 6。

停止条件：

- [ ] 缺少 first workflow 所需 source/repo access。
- [ ] 继续会暴露 secret。
- [ ] writeback 被要求但审批模型缺失。

## Phase 6 - 业务发现和生成策略

详情：`playbooks/phases/phase-06-business-discovery.md`

Phase 6 是同一 Phase 内的两层扫描：(1) 全生态拓扑扫描——覆盖所有已授权 repos/docs/tests/issues-or-history/CI/客户材料，识别 product surfaces、完整 module candidates、repo roles、sources、workflow scope；(2) 第一条 workflow 深挖——对 first workflow 的 modules/repos/sources 做足够深的 evidence extraction。

- [ ] 第一层：全生态拓扑扫描——覆盖所有已授权材料，不要求把每个模块写成熟。
- [ ] 第二层：对 first workflow 的 modules/repos/sources 做深挖，保证 Phase 7/8/9 和 Phase 11 可执行。
- [ ] 提炼 domain vocabulary、product surfaces、user roles、workflow gates。
- [ ] 提炼 identity signals：source/repo/docs 中出现的 product、brand、company、package namespace、artifact name。
- [ ] 对照 Phase 4 的 company/product identity，形成 identity reconciliation：confirmed、needs-owner-confirmation、conflict、unresolved。
- [ ] 形成 product/domain module candidates。
- [ ] 如果 Phase 4 给了 `JARVIS_MODULE_HINTS`，这些值默认就是目标 `modules/<module>/` 目录名，必须逐字节保留；逐项建立 module coverage matrix：`included`、`deferred-needs-evidence` 或 `rejected-by-owner`，并写明证据；不能只挑 8-10 个最容易总结的模块，也不能把客户给出的模块名改写成通用 taxonomy。
- [ ] 每个 module candidate 必须有 evidence pointer、confidence、confirmation status。
- [ ] 建立 source map：source 的用途、访问、owner、禁止复制边界。非 first-workflow 的已确认 source 暂不可访问时标 `deferred-needs-access`，不阻断 bootstrap。
- [ ] 如果 Phase 4 给了 `JARVIS_SOURCE_SCOPE`，这些值默认就是目标 `sources/<source>/README.md` 路由名；每个 source 都必须出现在 source map。
- [ ] 建立 repo role map：每个 pilot repo 在 first workflow 中做什么。
- [ ] 建立 workflow map：START -> WORK -> VERIFY -> END。
- [ ] 如果 Phase 4 给了 `JARVIS_WORKFLOW_SCOPE`，每个值是 workflow 的 `<name>` 部分；逐字节保留并映射到 `skills/<slot>-workflow-<name>/SKILL.md`。三个 starter workflow 无条件存在，额外 workflow 必须写入 generation plan。
- [ ] 建立 skill map：company entry、repo-local、source、workflow skills 的创建或 backlog 决策。
- [ ] 建立 unresolved map：缺 owner、权限、证据或确认的事项。
- [ ] 在 `_bootstrap/discovery/` 写入非空 `evidence-inventory.md`、`module-coverage-matrix.md`、`repo-role-map.md`、`workflow-map.md`、`generation-plan.md`。
- [ ] evidence-inventory 每条精确 endpoint/route/label/方法/字段/版本/数量/命令必须记录 observed fact + repo-relative pointer + retrieval/check。
- [ ] 对当前环境中可访问的 repo/source 执行真实扫描；evidence inventory 记录命令、具体 pointer、正向发现和负向检索结果。
- [ ] 每个 `included` module 至少有一个具体客户 evidence pointer 和明确产品/first-workflow role；`JARVIS_MODULE_HINTS` 只能确认名称，不能单独充当业务证据。
- [ ] 没有正向证据的 confirmed module 必须记录实际搜索范围和负向结果，并标 `deferred-needs-evidence`；不能用同一段通用占位文本标成 `included`。
- [ ] generation plan 明确引用 coverage matrix、repo role map 和 workflow map。
- [ ] 精确 endpoint/route/issue label/方法字段/版本/数量/命令都能回指 evidence inventory；否则写 `needs-verification`。禁止”按常见 REST 习惯补全”。
- [ ] `_bootstrap/discovery/` 可记录扫描机器路径；durable modules/sources/skills/references 只写 repo 名和 repo-relative path，不保留 `/e2e/customer-repos` 测试路径。
- [ ] 通过 Phase 7 入口门后再创建 module/source/workflow 正式文件。
- [ ] 在搜索原始代码之前，先读取已有高信号客户地图（如果存在）：产品文档/导航、UI 标签/路由、测试/规约名称、CLI help、README/AGENTS/CLAUDE、issue/历史词汇、已有知识地图。
- [ ] `JARVIS_MODULE_HINTS` 确认的模块名称只确认输出命名空间/名称，不证明模块的业务含义、owner、实现或 `included` 状态。名称确认后仍需完整语义证据链。
- [ ] 每个 `included` module 必须同时满足双锚点：(1) 产品身份锚点——产品文档、UI 标签/路由、验收/E2E 测试、CLI 表面、issue 分类法或 owner 已确认的 artifact；(2) 实现/验证锚点——`<repo-name>:<repo-relative-path>` 指向真实存在的代码/测试/构建配置。路径存在或依赖声明本身不能单独证明业务含义；必须读取匹配内容。
- [ ] 对每个 hinted/discovered module，从客户词汇构造别名并在所有相关 repo/source 中递归搜索。仅靠精确英文 token 搜索不够。
- [ ] 显式拒绝/消歧同名异义和近似匹配。记录为什么一个看似合理的代码匹配不是目标业务概念。
- [ ] 仅存在间接证据时使用 `deferred-needs-evidence`；不为了满足预期目录列表而强行标 `included`。
- [ ] 负向搜索有效性要求：别名已覆盖、所有 repo role map 中的 repo 已递归搜索产品文档/UI/测试/历史、搜索范围已记录。未满足时负向结果不能作为"该模块不存在"的结论。
- [ ] evidence inventory 中每条检索命令必须精确且在当前 checkout 上下文中可直接执行：禁止 `...`、Unicode 省略号、虚构伪路径、未测量的 `N+` 计数。精确数量/版本/命令必须有产生该结果的命令输出或指针。
- [ ] 每个可访问的 source route 必须在发现阶段映射：source 类型、具体 repo/doc 指针、访问方式、搜索方法、新鲜度/分支证据、状态。只有真正不可访问的 source 才能保持 deferred。
- [ ] Phase 7 入口门：当一个模块只有同名异义匹配/间接锚点时，发回 Phase 6 继续扫描。当一个可访问 source 仍为泛化状态时，发回 Phase 6 补全 source route 映射。

停止条件：

- [ ] 没有授权 source 却要生成客户业务 module。
- [ ] module candidates 主要是通用工程层。
- [ ] module candidate 没有 evidence pointer。
- [ ] `_bootstrap/discovery/` 五个证据文件缺失、为空，或没有记录实际扫描。
- [ ] 本地 repo/source 可读，却把所有 module 写成”待 Phase 6 扫描/补充”。
- [ ] source-detected identity 与客户声明身份冲突，且无法以”source-detected / needs-owner-confirmation”方式安全表达。
- [ ] fallback 会变成空白拓扑设计。
- [ ] 正式文件中出现 evidence inventory 无法支持的精确 endpoint/route/label 且未标 `needs-verification`。
- [ ] 每个 `included` 且客户 repo 可读的 module，在进入 Phase 10 前必须已经有 evidence-backed、module-specific 的首跳路由、first proof、false owner 和搜索/验证入口。shadow pilot/history replay 用来校准，不是用来填基本路由。不得用"本模块相关问题""首次 pilot 后填充""本模块尚未通过 pilot"等批量通用段落。

## Phase 7

详情：`playbooks/phases/phase-07-company-jarvis-repo.md`

Phase 7 创建 root、canonical company entry、完整 baseline references、cross-cutting、modules、sources README、tools inventory、root runtime contracts，以及固定默认 skill 集合。不得在 Phase 7 自由生成其他客户 workflow/source-helper skills。

- [ ] 先读取 `templates/company-jarvis/README.md`。
- [ ] 运行 `python3 scripts/instantiate_company_jarvis.py base --state <bootstrap-state.json>` 创建完整 root files、17 references、canonical entry、cross-cutting、tools、evals、四个通用方法 skill 和三个 starter workflow。
- [ ] Git 仓库名和 company entry skill 均使用 `<slot>-jarvis`；entry 位于 `skills/<slot>-jarvis/SKILL.md`，root `SKILL.md` 只能作为 runtime 兼容入口或转发副本。
- [ ] 确认 `skills/ponytail/`、`skills/writing-durable-docs/`、`skills/jarvis-self-improve-skill/`、`skills/stop-slop/` 已完整创建。
- [ ] 确认 `skills/<slot>-workflow-issue-post-check/`、`skills/<slot>-workflow-bugfix-loop/`、`skills/<slot>-workflow-feature-delivery/` 及其 companion files 已完整创建。
- [ ] company entry skill 必须使用 confirmed slug，并与 `jarvis.toml`、`bootstrap-state.json`、`bootstrap-result.json.paths.entry_skill` 一致。
- [ ] 创建根目录 runtime contract files：`bootstrap-state.json`、`bootstrap-result.json`；不能只放在 `_bootstrap/`。
- [ ] 创建 `_bootstrap/jarvis-build-brief.md`。
- [ ] 创建完整 baseline references（17 个跨公司核心 reference files，包括 `history-replay.md`）。客户/产品/工具链/流程特有的 reference 不得从母版预装，只能在 Phase 6/9/11/12/13 中按 evidence 生长。
- [ ] company entry skill 必须声明 mandatory runtime pre-read：先读 `references/runtime-governance-quick.md`。
- [ ] 按 Phase 6 coverage matrix 运行 `python scripts/instantiate_company_jarvis.py module --state <...> --name <name>` 创建完整 module contract（5 files）。
- [ ] 确定性 module 母版只是安全的五文件容器，不等于 module 已完成。每个 `overview.md` 必须填入客户业务目的、first-hop routing、first proof，并消费 `_bootstrap/discovery/module-coverage-matrix.md` 中至少一个可解析且真实存在的 `<repo-name>:<repo-relative-path>` 证据。
- [ ] `known-issues.md`、`decisions.md`、`rejected-features.md`、`test-coverage.md` 可以诚实记录“bootstrap 尚未提升任何条目 / 尚未评估”，但不能预装虚构故障、决策、版本、数量、技术栈或稳定接口。
- [ ] module/source/workflow 中的精确 endpoint、route、label、command 和数量只来自 evidence inventory；未验证时明确标 `needs-verification`。
- [ ] module identity 必须来自 Phase 6 的客户证据；禁止默认复制 Hengshi Sense module names。
- [ ] 创建 source entrypoints：运行 `python scripts/instantiate_company_jarvis.py source --state <...> --name <name>`。
- [ ] 在 `references/jarvis-first-routing.md` 记录 pilot repo 角色并指向 repo-local skill；不要创建顶层 `repos/`。
- [ ] 创建 `cross-cutting/module-interactions.md` 和 `tools/README.md`。module interactions 至少覆盖 first workflow 的真实模块关系；peer product、版本索引、company-specific tool 尚无证据时写明确未登记状态，不生成示例产品、版本、命令或工具。
- [ ] 标记所有 truth-bearing 字段状态。
- [ ] 所有页面都遵守 identity reconciliation。
- [ ] 对照 `acceptance.md` 自检。
- [ ] 除四个通用方法 skill 和三个 starter workflow 外，不得在 Phase 7 创建其他 workflow/source-helper skill；额外能力由 Phase 9 负责。
- [ ] 不得复制 install-owned runtime skills（jarvis-box-doctor/init/monitor）到 company repo；默认 `jarvis-self-improve-skill` 只包含方法语义，不复制 runtime collector/scheduler。
- [ ] 公司入口从已确认的 product identity、实际 repo-role map、实际 source route 和已有 reference 文件名填充；不用 reference-company 示例或泛化别名。entry skill 所有链接必须可解析。
- [ ] repo-local handoff 名称必须是实际授权的 repo 名称/路径，不是 reference-company 示例或泛化别名。
- [ ] 离开 Phase 7 前重新读取 root `README.md` 的模块、数据源、工作流、仓库四个 scope 索引：实际已创建目录必须列出，尚无证据只能写 `none-yet`/下一步；不得保留 `BOOTSTRAP_REQUIRED`。Phase 9 新增 package 后再次同步。
- [ ] 正式 durable 文件使用 runtime 变量/contract（如 bootstrap state 确认的 runtime root 或 `JARVIS_RUNTIME_ROOT`），不保留 E2E 测试机绝对路径。Runtime 命令从已安装 `jarvis-box --help`/`version`/`doctor`/`status` 观察，不发明脚本或命令。
- [ ] 已确认产品身份的任何正式 module/root/entry 文件不得保留未解决的身份或对该身份的 `needs-owner-confirmation`。
- [ ] 对每个可访问 source，将 source scaffold 替换为具体 route。`needs-evidence`、`REFERENCES_PATH` 和示例占位符在可访问 route 中是 phase blocker。

停止条件：

- [ ] entry skill 不存在或不可读。
- [ ] 四个通用方法 skill 或三个 slot 化 starter workflow 任一缺失。
- [ ] 输出只有 root files / inventories / generic scaffold。
- [ ] module 主要是工程层或没有 evidence/confidence/confirmation status。
- [ ] module 只有 `overview.md`，缺少 durable contract files。
- [ ] entry skill 没有 mandatory runtime quick-ref。
- [ ] baseline references 缺少 `runtime-governance-quick.md`、`runtime-governance.md`、`capability-delivery-surfaces.md` 或 `next-hop-compression.md`。
- [ ] company identity 与 source-detected identity 混写成已确认事实。
- [ ] company Jarvis 不知道 pilot repos 如何支撑 first workflow。
- [ ] first workflow 缺 START -> WORK -> VERIFY -> END。
- [ ] 输出出现顶层 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 作为 company Jarvis 主结构。
- [ ] Phase 7 自由生成了 workflow/source-helper skill 文件。
- [ ] 生成内容包含 secret、raw source dump 或 reference company 私有事实。
- [ ] durable customer-fact files 仍有 `BOOTSTRAP_REQUIRED`、`<repo>`、`<endpoint>`、`module-a`、`product-a` 等模板占位，或保留母版中的虚构示例事实。

## Phase 8 - 创建 repo-local skills

详情：`playbooks/phases/phase-08-repo-local-skills.md`

- [ ] 识别 first workflow 触达的 pilot repos。
- [ ] 先运行 `python scripts/instantiate_repo_local_skill.py --repo <path>` 创建 canonical package。
- [ ] 检查每个 repo 是否已有 repo-local guidance。
- [ ] 没有时用 instantiator 创建 repo-local skill package。
- [ ] 已有 repo-local guidance 时也要按 canonical package contract 补齐固定文件，不能用近似文件名替代。
- [ ] 每个 repo-local package 包含 `skills/SKILL.md`、`skills/code-review/SKILL.md`、`skills/code-review/scripts/precheck.sh`、`skills/references/source-of-truth.md`、`skills/references/architecture-map.md`、`skills/references/test-entrypoints.md`、`skills/references/runtime-and-testability.md`、`skills/references/history-replay-loop.md`、`skills/eval-loop.md`、`skills/self-skills-improve/SKILL.md`。
- [ ] `precheck.sh` 必须可执行，并从 repo root 跑一次。
- [ ] `precheck.sh` 必须自包含，不能依赖 reference company 私有路径或维护命令，例如 `~/.hengshi/repos/hengshi-jarvis/*`、`pullall`、`hengshi-jarvis/tools/precheck-diff.sh`。
- [ ] `precheck.sh` 本身也不能包含 reference-company 私有名称，不能通过在脚本里 grep 这些禁用字符串来“检查自己”；这类跨文件检查由 verifier 执行。
- [ ] company Jarvis 只在 `references/jarvis-first-routing.md` 或对应 workflow skill 中指向 repo-local skill；不要创建顶层 `repos/<repo-name>.md`。
- [ ] 真实 build/test/lint 命令只来自 repo 证据、CI、owner、pilot 或 replay。
- [ ] 语言生态惯例（例如“标准 Go/Maven/npm 命令”）本身不是 repo 证据；命令必须指向实际 manifest、wrapper、CI、repo 文档、owner confirmation 或执行记录。
- [ ] 确定性十文件 package 创建后，立即检查每个可读 repo 并填入所有可直接观察的事实：实际 default branch/分支策略、repo 角色和边界、语言/构建文件、重要路径、package/module 布局、精确 build/test/lint/CI 命令及其证据、测试/fixture 位置、runtime 前提条件、source-of-truth 指针、生成区域、公司 handoff。
- [ ] 区分 `observed-not-executed` 和 `executed-pass`：命令可以从构建/CI 证据记录而不假装执行过。未实际运行时不得标 `executed-pass`。
- [ ] repo 可读时，核心 repo-local 文件不得保留 `<>` 占位符、泛化示例命令、伪造 default branch 或全面 `needs-owner-confirmation`。
- [ ] copied template 中的“Phase 8 填充/替换”生成期旁白必须消失；保留的规则要改写成新 agent 可长期执行的 repo evidence contract。
- [ ] 八个 package 必须根据各自 repo 证据有所不同。三个或以上归一化相同的 repo truth section 证明 Phase 8 被跳过。
- [ ] 基础 skill 必须让新 agent 能路由、构建、测试和找到 source truth。专业历史衍生 reference 可后续生长。

停止条件：

- [ ] repo path 不可访问。
- [ ] repo-local package 无法写入。
- [ ] precheck 不可执行且无法记录 blocker。

## Phase 9 - 定制默认 workflow 并实例化额外 skills

详情：`playbooks/phases/phase-09-source-workflow-skills.md`

Phase 7 已经确定性创建三个 starter workflow。Phase 9 负责用 Phase 6 客户证据完成初次定制，并按 generation plan 创建额外 workflow/source-helper package。

- [ ] 逐一读取并定制 `<slot>-workflow-issue-post-check`、`<slot>-workflow-bugfix-loop`、`<slot>-workflow-feature-delivery`：填入客户 issue/ticket source、repo 路由、branch/version policy、review/CI、发布、owner 和 writeback policy；没有证据的字段保持明确 unresolved，不能编造。
- [ ] 默认 workflow 的固定方法语义和 companion files 必须保留；客户差异不能把 START → WORK → VERIFY → END 闭环删成薄壳。
- [ ] generation plan 中额外 `create-now` workflow 使用 `package --kind generic-workflow --name <slot>-workflow-<name>`；额外 source/tool skill 使用 `package --kind generic-source --name <slot>-<name>`。
- [ ] generation plan 中额外 `create-scaffold-needs-pilot` 也只能使用对应 generic 母版，并标 `status: scaffold-needs-pilot`。
- [ ] 每个 package 消费 evidence inventory 中的具体事实填充 trigger、gates、handoff、verification。
- [ ] generation plan 中没有的额外 package 不创建；不复制 reference company 的 release、文档 API、CI job 或附件处理 skill。
- [ ] install-owned runtime skills 不复制到 company repo；默认 `jarvis-self-improve-skill` 已存在，Phase 9 只接入客户允许的 evidence source、owner 和 writeback policy。
- [ ] source skill 只写访问、检索、引用、边界和 writeback 限制。
- [ ] workflow skill 写 trigger、non-trigger、evidence、routing gates、completion、END writeback。
- [ ] 不创建 generation plan 之外的”以后可能用”的泛化 skills。
- [ ] 运行 `python3 scripts/verify_bootstrap_output.py --stage phase-09 --jarvis-home <目标目录> --customer-repos-dir <repo副本根目录>`；Phase 3-9 blocker 清零后才能进入 Phase 10。
- [ ] Phase 9 gate 前确认 root README scope 索引与 `modules/`、`sources/`、`skills/` 实际目录一致；可访问 source 不得残留 `BOOTSTRAP_REQUIRED` 或泛化 route。

停止条件：

- [ ] source access 未确认却声称可用。
- [ ] workflow 没有跨 source/repo/team 的闭环。
- [ ] skill package 只有统一 scaffold 没有消费 evidence inventory。
- [ ] install-owned runtime skills 被复制到 company repo；或 `jarvis-self-improve-skill` 被错误替换成 runtime collector/scheduler 实现。
- [ ] confirmed workflow 的 `<name>` 或 source 名称被改名、合并或省略，或输出不符合 slot 命名合同。

## Phase 10 - 交付确认报告

详情：`playbooks/phases/phase-10-onboarding-report.md`

- [ ] 汇总 created / updated / preserved files。
- [ ] 汇总 confirmed facts、unresolved fields、missing inputs、blockers。
- [ ] 汇总 identity reconciliation：company identity、confirmed product identity、source-detected identities、conflicts 和 owner confirmation 状态。
- [ ] 汇总 first workflow、pilot repos、sources、owners、writeback policy。
- [ ] 汇总 acceptance 自检结果。
- [ ] 审计 Phase 6-9 语义就绪状态，不只重复文件数量。发现以下任一情况时发回所属 phase：可访问的 source route 仍为泛化状态、repo-local package 为泛化模板、模块身份未解决、reference 链接断开、仅靠间接证据 `included` 的模块。
- [ ] 写 confirmation checklist。
- [ ] 确认 `bootstrap-result.json` runtime contract 可解析：list 字段只能放字符串。
- [ ] 如果不满足 `acceptance.md`，不要写 `completed`。
- [ ] 把 Phase 10 记录为 checkpoint：Phase 11-14 保持 `pending`，顶层 status 保持 `in-progress`，`next_action` 明确为立即进入 Phase 11。
- [ ] 在同一次 runtime-agent invocation 中进入 Phase 11；不得在 Phase 10 输出最终总结或返回 jarvis-box。

停止条件：

- [ ] owner 无法判断下一步。
- [ ] required owner/source/writeback 仍 unresolved，却准备写 completed。

## Phase 11 — 影子试跑

详情：`playbooks/phases/phase-11-shadow-pilot.md`

目标：用真实 artifact 验证 company entry → module/workflow/source → repo-local handoff 路由可用性，以及 VERIFY/END 诚实闭合。不是 history replay。

- [ ] 确认 Phase 10 的 unresolved/blockers 中没有阻止试跑的问题。
- [ ] 主动从已授权来源寻找真实 artifact（当前 issue/request/alert/doc task），不等整理、不编造。
- [ ] 没有当前 artifact 时，从 pilot repo Git 历史选取 `historical-shadow` artifact，记录实际搜索范围、选中理由、停止理由。historical fallback 可做 route-only/draft pilot，明确其只能证明 routing/readability。
- [ ] 不用固定的最近 3/5/N 条 commit 作为“无候选”结论。跳过无效候选后继续扩大历史范围和其他 pilot repos，直到选中一个 artifact，或所有授权 pilot repos 都有实际搜索命令、边界、排除理由和停止理由。
- [ ] 创建或更新 `_bootstrap/shadow-pilot/pilot-registry.md`。
- [ ] 为每个 artifact 创建 `shadow-pilot-run.md` 和 `pilot-evidence.md`，使用固定产物目录结构。
- [ ] PILOT INPUT / START：artifact 按本次 pilot 实际拿到的形态呈现。完整 commit/MR 的 diff 可以是可见输入；若要隐藏 outcome、重放 cutoff 前任务，转 Phase 12。
- [ ] ROUTE：从 company entry skill 进入，记录读取的 entrypoint、选择的 module/workflow/source/repo-local skill 和理由。
- [ ] WORK：受控副本/read-only/draft，不做未授权生产写入。实际运行什么就记录什么。
- [ ] VERIFY：运行可用检查、owner review、precheck 或 dry-run；未运行不写 PASS，记录为 `not-run`。owner review 只证明其实际审查内容。
- [ ] END：分类 outcome（useful/partial/blocked/missed）、failure mode、`no_skill_gap`、writeback decision。
- [ ] jarvis-box Task 可选：只有实际走 Task 时才记录 pointer，遵守五个 lifecycle operations；普通 agent 对话不编造。
- [ ] `no_skill_gap`/writeback decision 写进 pilot evidence。只有治理规则本身变化时才更新 `references/writeback-governance.md`。
- [ ] 更新 `bootstrap-state.json`。
- [ ] 禁止事项：不得从文件存在声称 PASS；dry-run 只能证明路由/可读性；pilot 暴露 Phase 6-9 基础产物为空/错误时，回到对应 phase 修正后重跑。

停止条件：

- [ ] 客户未提供 artifact，且 pilot repo Git 历史也无法选出可用 `historical-shadow` artifact。
- [ ] artifact 需要的 source/repo 权限不可用。
- [ ] owner 未批准 shadow mode 操作范围。
- [ ] workflow 只能靠 invented example 演示。
- [ ] 因缺 Task ID 而把有真实 artifact、完整 START-WORK-VERIFY-END 的受控 shadow pilot 判失败。

## Phase 12 — 历史回放

详情：`playbooks/phases/phase-12-history-replay.md`

目标：从每个 pilot repo 及已授权历史来源的真实 episode 构造 eval case，用当前 skills 隔离重放，找失败模式，只把可复用、可验证的缺口交给 Phase 13。

### Episode 搜索

- [ ] 主动扫描每个 pilot repo 和已授权 issue/MR/ticket/incident/delivery history。不只扫 Git，不等用户整理。
- [ ] 在 `replay-case-registry.md` 的 Search Coverage 表中为每个 pilot repo 写一条真实 canonical 行：exact search command/query、时间或提交边界、候选、排除理由、停止理由和状态；不能用段落或“后续扫描”替代表格行。
- [ ] 每个 repo 记录实际命令/查询、时间或提交边界、候选和排除理由、停止原因。无固定数量或窗口。
- [ ] episode 准入：当时明确工作目标、cutoff 前足够 initial signal、cutoff 后可验证 outcome、授权访问。纯 housekeeping / 无可验证 outcome / START-oracle 无法分离的候选不进 replay，可留 backlog。

### 时间切片与当前 skills

- [ ] visible START 只含 cutoff 时已可见或按当时权限可合理取得的事实。每条 fact 记录 provenance 和为什么 cutoff 前可见。
- [ ] `reconstructed-from-outcome-subject` 只能投影独立外部症状。文件、目录、module、class、method、field、constant、root cause、fix direction 需要独立 pre-outcome provenance。
- [ ] visible-packet 中的 `replay-prompt.md`、`allowed-sources.md`、`skill-entrypoints.md` 每条事实声明和 narrowing instruction 必须逐条写进 outer case 的 Visible Packet Fact Closure 表，并回指 Visible Fact Provenance 的 Fact ID。
- [ ] hidden oracle 必须从完整真实 final diff/artifact 提取实际观察到的 outcome，禁止 `likely`/`probably`/猜测。若历史 root cause/verification 未记录写 `unknown`。
- [ ] 历史 repo/source snapshot 冻结在 cutoff；被测对象是运行时当前版本的 skills。记录当前 skill pointers，检查是否曾直接写入当前 skill。
- [ ] 不写复杂的 identifier 黑名单算法。语义 provenance 审查属于 runtime agent；确定性检查只抓 exact/structural 矛盾。

### 隔离与执行

- [ ] 创建 `evals/history-replay/cases/<case-id>/history-replay-case.md`（含 visible START 和 hidden oracle），必须使用规范模板并完整填写所有 sections/fields。
- [ ] 创建 `_bootstrap/history-replay-runs/<case-id>/visible-packet/`：只放 replay prompt、allowed sources/repos、skill entrypoints。不放 hidden oracle。
- [ ] outer case（含 oracle）与 visible packet 物理/权限分离。
- [ ] 有效隔离：独立 container/VM/等价文件系统边界。同机 fresh process、Task Workspace、`--add-dir` 不能单独证明隔离。
- [ ] 透传 selected agent 必需的最小凭据环境，不把值写进 artifact。
- [ ] **Case Readiness Gate**（调用 replay bridge 前）：visible fact 表和 Packet Fact Closure 表完整；Hidden Facts Excluded 表中的每项检查结果均为 `absent`；hidden oracle 已用 exact command/pointer 从真实 artifact 完整提取。外层 agent 标记 case validity 和 `ready` / `invalid`。`invalid`/`not-ready` 不得执行。
- [ ] Preflight：确认 START/provenance、mount allowlist、future refs/oracle 不可见、agent CLI 可用。
- [ ] bridge 调用前先准备并确认 cutoff snapshot 非空、visible packet 非空、company Jarvis runtime 与 destination 使用 bridge 合同要求的 canonical paths；不得用临时 runtime 副本路径或空目录试探性调用。
- [ ] bridge 返回非零时先读取 exact stderr、request state 和 output；如果失败发生在 request `READY` 之前，不得写成 isolation runtime unavailable，也不得继续 oracle comparison。修复输入后使用同一 case 重试；若 request 已损坏则换新 case id，并把 bridge protocol failure 记录为 `replay-not-executed`。
- [ ] 记录 exact invocation（脱敏）、exit code、非空执行轨迹、diff/输出、验证结果。
- [ ] CLI 在首个有效 action 前失败 = `replay-not-executed`，不产生 skill gap / `no_skill_gap` 结论。

### Oracle Comparison 与归因

- [ ] replay 结束后由外层 bootstrap agent 做 oracle comparison；replay agent 不自评 oracle。
- [ ] 首先读取 exact replay final output 和 exact 历史 final outcome。记录 command/pointer 和完整 changed surfaces 或等价非代码 artifact。
- [ ] 比较 route/owner、关键证据、边界、行为结果、验证、越权/幻觉、闭合。替代 replay 方案只有经独立行为验证后才能称为等价/更优；否则标 `unproven`。
- [ ] 非通过先归因：skill gap / instance fact gap / source-access-environment / execution deviation / case construction leak / oracle limitation。未执行/invalid 不能判断 skill。
- [ ] 创建 `replay-failure-analysis.md` 和 `skill-update-decision.md`，必须使用规范模板并完整填写所有 sections/fields，不得用缩减自由格式替代。
- [ ] `no_skill_gap` 需要：执行（`executed`）+ 有效 case + 完整 comparison + 充分 outcome 验证。泄漏/invalid/未验证 case 均为 `not-evaluated`。
- [ ] skill gap 需可复用、有证据、可验证、归属明确。skill 更新后用同一 case 复跑证明改善。
- [ ] Oracle comparison 必须在 failure analysis / skill decision / `no_skill_gap` / Phase 12 状态更新之前完成。

### 状态

- [ ] `completed`：至少一个真实 ready case 在有效隔离中实际执行，外层完成 oracle comparison/归因/writeback decision。Phase 12 不修改 skills；更多候选进 backlog，不作为缺输入。
- [ ] `needs-input`：没有合格 episode、缺授权/真实 outcome/隔离 runtime/可用 agent。必须写已完成的搜索和下一步。
- [ ] 已识别候选但没有 case 文件不是合格 `needs-input`。只留 candidate registry 没有 case 文件视为执行不完整。
- [ ] 若执行后发现泄漏，分类为 `invalid`/`not-evaluated`；Phase 12 完成前必须另选有效 case。

停止条件：

- [ ] 所有 pilot repo 和客户提供材料扫描后仍没有真实历史 episode。
- [ ] visible START 无法和 hidden outcome 分离。
- [ ] replay agent 会看到事后答案。
- [ ] Phase 12 未 `completed` 时，Phase 13/14 保持 `pending`；不得只创建交接文件就给未来 phase 判状态。

## Phase 13 — 受控写回

详情：`playbooks/phases/phase-13-controlled-writeback.md`

目标：把 Phase 11/12 已验证的 learning 写回正确位置。只处理可复用、可验证、归属明确的学习。

- [ ] 进入前确认 Phase 11 和 Phase 12 均为 `completed`；否则不进入 Phase 13，Phase 13/14 保持 `pending`，bootstrap 从未完成的前置 phase 返回。

- [ ] 明确 controlled skill/file writeback 不是 jarvis-box Retry Writeback。Retry Writeback 只重试已有 provider delivery。
- [ ] 只消费 source gate 有效且 evidence contract 完整的 eligible learning signals。
- [ ] invalid / `replay-not-executed` / 泄漏 / oracle 未验证 signal 可记录为 `deferred`/`not-evaluated`，不得计为 `no_skill_gap`、`skill_gap`、`closed` 或 completed candidate。
- [ ] 汇总 Phase 11/12 已验证 learning signals，先区分稳定事实修正和方法/skill 缺口。稳定事实修正可直接写其事实 owner；skill 扩展必须先 `no_skill_gap`。
- [ ] 稳定事实修正写其事实 owner；只有方法/skill candidate 先判断 `no_skill_gap`。
- [ ] 为每条 candidate 选择唯一 primary home，严格按 `references/writeback-governance.md`：task-local / repo-local / company module/reference / source skill / workflow skill / upstream create-jarvis-skill / none。
- [ ] 只有另一层必须发现/执行该规则时才 mirror。mirror 只写 pointer，不复制细节。冲突不覆盖，owner 确认。upstream 必须 company-neutral。
- [ ] 做 redaction：去除 secret、个人隐私、未经授权材料、raw source dump、长篇原文和 hidden oracle；客户实例保留必要真实身份与稳定 pointer，upstream 再公司中立化。
- [ ] 按目标 owner 的实际写入/审批政策执行，不预设 branch/MR/PR/CI。
- [ ] 写入最小可验证规则，不写长篇复盘。保留 evidence pointer。
- [ ] 用原 pilot/replay 或等价真实任务验证写回；skill 更新后用同一 Phase 12 case 隔离复跑，并更新 decision/registry。
- [ ] 更新 `_bootstrap/controlled-writeback-log.md`（模板：`templates/company-jarvis/artifacts/controlled-writeback-log.md`）。
- [ ] 只有治理规则本身变化时才更新 `references/writeback-governance.md`。
- [ ] 无有效 Phase 12 replay 时不得写入由该 replay 推导出的规则。`replay-not-executed` 对应 decision 只能是 `defer`。
- [ ] 不用 Phase 11 shadow pilot 替代 Phase 12 replay 关闭 writeback candidate。
- [ ] Phase 13 完成只计 eligible candidates。

停止条件：

- [ ] candidate 没有 replay/pilot/owner evidence。
- [ ] primary home 不明确。
- [ ] 需要 owner approval 但未批准。
- [ ] 写回会泄露 private facts 或 hidden oracle。
- [ ] 规则来自未完成有效隔离 replay 的 Phase 12，却当作已验证学习写入。

## Phase 14 — 第二天运营

详情：`playbooks/phases/phase-14-day2-operation.md`

目标：检查 install-owned 能力的真实状态、记录观测入口和恢复动作，明确 company-specific 的 owner、维护机制和 writeback policy。不重复实现 install-owned runtime。

- [ ] 进入前确认 Phase 11、Phase 12 和 Phase 13 均为 `completed`；否则不进入 Phase 14，Phase 14 保持 `pending`，bootstrap 从未完成的前置 phase 返回。

- [ ] 先读取当前安装：`jarvis-box version`、顶层及相关 `--help`。CLI help 只证明公共命令 shape。
- [ ] 加载 install 提供的 `jarvis-box-monitor` 生成当前 slot 的运行快照；用 live CLI、state 和日志证据核对，不把模板文本当作当前事实。
- [ ] 逐项检查 install-owned 能力，每项分别记录五列维度：install/authority evidence、observed current state、last execution proof（或 unexercised）、readiness、owner & recovery。不得用单个模糊词合并。
- [ ] 产物存在、public help、version 输出或零活跃 Task 不单独证明能力已配置/工作。零 Task 意为 `unexercised`，不是 `not-applicable`。容器缺少 systemd 不使 service/jobs 变为 `not-applicable`：实际探测可用替代方案或标记 `unverified`/`blocked`。
- [ ] install-owned managed jobs 的事实来自当前 release docs/安装产物、host scheduler 或 `/server` crons、job logs/activity。不能因为不在顶层 `--help` 就判不存在。
- [ ] 先按当前安装版本复核合同。当前已确认的 Task 合同是五个 lifecycle operations（start/continue/stop/recover/retry-writeback）；`reap`/`clean` 是维护；`reconcile` 是 dry-run；service restart 不自动恢复 Task；`recover` 仅 recovery-required；`bootstrap --resume` 只恢复表单/已确认状态，绝不是 Jarvis maintenance authority。此处不把某个版本号当作永久基线：若当前安装版本的 `--help` 或 release contract 有差异，以当前机器的 live 输出为准并记录差异。
- [ ] 至少一个 runtime agent 需要真实 prompt probe（受控短 prompt 确认实际响应）。`--help` 和 `agent list --check` 不能替代。
- [ ] doctor 总体非零时按具体 finding 归属，不把所有能力一律判失败。
- [ ] 指定 Jarvis owner；替代责任人按客户政策登记。
- [ ] 明确 company-specific 内容：owner/escalation、维护触发或 cadence、source/repo inventory refresh、history replay 触发、writeback policy、acceptance drift、company-owned tools。
- [ ] 允许 event-driven/human-run/host scheduler/external scheduler 等有 owner 的机制，不强制固定 cadence 或某种 OS scheduler。只有既无 install-owned 机制又无明确替代 owner/机制时标 `blocked`。
- [ ] 更新 `references/runtime-governance.md` 的 managed jobs section、`MAINTENANCE.md`、`tools/README.md`。
- [ ] 创建或更新 `_bootstrap/day2-operation.md`（使用规范模板）。所有 Phase 14 证据统一写入此文件，不再创建单独 `_bootstrap/day2-runtime-checks.md`。
- [ ] 在更新 Phase 14 状态前，执行跨产物一致性审查：`MAINTENANCE.md`、`references/runtime-governance.md`、`tools/README.md`、`_bootstrap/day2-operation.md`、`bootstrap-state.json`、`bootstrap-result.json`。
- [ ] 不复制 install-owned 脚本到 company repo。
- [ ] 记录 day-2 backlog。更新 `bootstrap-state.json` 和 `bootstrap-result.json`（引用通用规则中的 phase 状态传递规则，不复制大段 JSON state 字段逐项规则）。
- [ ] Phase 14 完成需要每个必要运营能力 readiness 为 `ready` 或 `ready-with-explicit-alternative`。`unverified` 必要能力导致不能 completed。

停止条件：

- [ ] 没有客户 Jarvis owner。
- [ ] 无法确认 runtime root 或运行机器边界。
- [ ] install-owned capability 既无 install 托管也无明确替代 owner/机制，却写 `completed`。
- [ ] 重新生成 install-owned runtime 产品能力。
- [ ] 跨产物一致性审查未通过（如 `MAINTENANCE.md` 与根 state 矛盾）。
- [ ] 必要运营能力 readiness 为 `unverified` 或 `blocked`。

## 完成判定

只有满足 `acceptance.md` 时，`bootstrap-result.json.status` 才能是 `completed`。

不满足时：

- 缺人可补的信息：`needs-input`。
- 缺权限、路径、安全条件或 owner 决策：`blocked`。
- 发生不安全写入、secret 泄露、state 损坏：`failed`。

不要发明中间成功标签。输出不像客户自己的 company Jarvis 生态，就继续细化本 checklist 和对应 phase 文件。
