# Company Jarvis 验收标准

本文只定义一个验收目标：runtime agent 按 `playbooks/phase-checklist.md` 执行完后，产物必须是客户自己的 company Jarvis repo，角色和生态形态等价于 `hengshi-jarvis`。

没有中间成功等级。机器文件能解析、目录能创建、repo-local skill 能生成，都只是过程检查；如果最终产物不像客户自己的 company Jarvis 生态，就不能称为 bootstrap 完成。

## 对"模板"的定义

模板提供固定方法语义（method semantics），直接复用并参数化。模板本身不含客户事实——所有 truth-bearing 内容由客户证据填充。不以文件数量要求 module 成熟度。

## 唯一成功标准

目标只有一个：runtime agent 按 Phase 3-14 执行后，产物必须是客户自己的 company Jarvis 生态，在角色和拓扑上操作等价于真实的 reference 生态（`hengshi-jarvis`）。

目录数量、模板渲染完成、verifier 通过都不能替代客户语义正确性或实际执行证据。`completed` 意味着该 phase 的客户事实和执行证据已实际存在，不仅仅 scaffold 存在。

bootstrap 完成时，客户应当获得一个可以被 agent 直接使用的 company Jarvis repo。它必须具备：

- 公司级入口 skill：能识别真实 artifact，并路由到 module、workflow、source 或 repo-local skill。
- 仓库形态：必须接近 `hengshi-jarvis` 的真实拓扑：`README.md`、`MAINTENANCE.md`、`jarvis.toml`、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`、`modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`、`evals/`；company entry skill 位于 `skills/<company>-jarvis/SKILL.md`。
- 身份边界：客户 company identity、客户确认的 product identity、source 中识别出的 product/brand identity 必须分开记录。source 里出现的品牌或产品名只能作为 evidence-backed detected identity，不能在 owner 确认前并入 company identity。
- 产品/业务 module 拓扑：modules 来自客户授权材料，不是 `backend`、`frontend`、`api`、`database`、`infra` 这类通用工程层；每个 module 必须落完整 durable contract：`overview.md`、`known-issues.md`、`decisions.md`、`rejected-features.md`、`test-coverage.md`，没有证据时用 `needs-evidence` / `none-yet` / `needs-owner-confirmation` 明确留空，不能只生成 `overview.md`。
- source 入口：列出客户授权 sources 的访问方式、权限状态、owner、禁止复制边界和证据引用方式。
- routing references：`references/runtime-governance-quick.md`、`runtime-governance.md`、`jarvis-first-routing.md`、`agent-engineering-quality-gate.md`、`minimal-closure-card.md`、`redaction-rules.md`、`capability-delivery-surfaces.md`、`next-hop-compression.md`、`repo-pre-push-review-loop.md` 等文件说明 runtime 前置、routing、质量门、first-proof、repo-local handoff 和 END writeback，并指向 repo-local skill。
- workflow skill：至少一条 first workflow 以 `skills/<workflow-skill>/SKILL.md` 的形式存在，并有 START -> WORK -> VERIFY -> END 的闭环定义。
- repo-local skills：pilot repos 中有 repo-local skill package 或明确 blocker；repo execution truth 留在 repo 本地。
- 交付确认：所有未确认事实、owner 问题、权限缺口、写回策略和下一步都明确记录。
- 演进机制：影子试跑、历史回放、`no_skill_gap` 判断和受控写回路径已经进入 checklist，并有固定产物路径或明确 `needs-input` / blocker。

## 必须失败的情况

出现以下任一情况，说明 phase checklist 没有被正确执行，或者 checklist 本身还不够细，不能把结果称为完成：

- company Jarvis repo 只有模板文件、通用段落或目录说明。
- company Jarvis repo 长成 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 这些 bootstrap 过程目录，而不是 `hengshi-jarvis` 风格的 `modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`。
- company entry skill 不在 `skills/<company>-jarvis/SKILL.md`。
- company entry skill 没有强制 runtime pre-read `references/runtime-governance-quick.md`。
- `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` 缺失，或没有指向 canonical entry skill。
- baseline references 缺失，例如 `runtime-governance-quick.md`、`runtime-governance.md`、`capability-delivery-surfaces.md`、`next-hop-compression.md`。
- modules 主要是通用工程层，而不是客户产品域、业务能力、核心流程或关键概念。
- modules 只有 `overview.md`，缺少 `known-issues.md`、`decisions.md`、`rejected-features.md`、`test-coverage.md`。
- module/cross-cutting/routing/tools 文件仍有 `BOOTSTRAP_REQUIRED`、`<repo>`、`<endpoint>`、`module-a`、`product-a` 等母版占位，或包含未经客户证据支持的 cache/Kafka/GraphQL/Kubernetes/版本/日期/数量/stable endpoint 示例事实。
- module overview 没有业务目的、first-hop routing、first proof，或没有至少一个可在授权 checkout 中解析的 `<repo-name>:<repo-relative-path>` 证据。
- `_bootstrap/discovery/` 缺少 evidence inventory、module coverage matrix、repo role map、workflow map 或 generation plan，却把 Phase 6 标成 completed。
- `_bootstrap/discovery/` 的 truth-bearing 文件保留 `<module>` / `<repo>` 等未解析占位，或使用 `repo:path/.../File`、glob、不可解析路径作为 evidence pointer。
- 客户 repo/source 在当前环境可读，module 仍批量重复“待 Phase 6 扫描”“needs-evidence”等通用文本，没有具体 repo/path/test/doc evidence pointer。
- durable `modules/`、`sources/`、`references/` 或 company `skills/` 保留 `/e2e/customer-repos` 等 bootstrap 测试机绝对路径，而不是 repo 名 + repo-relative pointer。
- module/source/workflow 写出 evidence inventory 无法支持的精确 endpoint、route、issue label、版本、测试数量或命令，并把模型补全当成 confirmed fact。
- 把客户提供的 company name 和 source 中识别出的另一个 company/product/brand 直接拼成一个已确认主体，或者用 source-detected identity 替代客户 company identity。
- repo-local skills 生成了，但 company Jarvis 的 `references/jarvis-first-routing.md` 或 workflow skill 不知道这些 repo 如何支撑 first workflow。
- pilot repo 缺 root `skills/` canonical package，却把 `AGENTS.md`、`CLAUDE.md`、`.claude/skills`、`.agents/skills` 或 `.codex/skills` 当作替代。
- repo-local 核心 skill/reference 仍保留“Phase 8 填充/替换”一类生成期旁白，而不是可长期使用的 repo evidence contract。
- repo-local build/test/lint/runtime 命令只由“语言生态惯例”推导，未指向实际 manifest、wrapper、CI、文档、owner confirmation 或执行证据。
- repo-local `skills/code-review/scripts/precheck.sh` 依赖 reference company 私有路径或工具，例如 `hengshi-jarvis`、`pullall`、`~/.hengshi`。
- repo-local `precheck.sh` 为了检测 reference-company 依赖而把这些禁用名称写进脚本自身，导致产物本身仍携带 reference-company 事实。
- repo-local `precheck.sh` 在 bootstrap 阶段因为缺 JDK、Node、Go、Docker、kubectl 等目标技术栈工具而 hard fail，而不是输出 WARN/INFO 并把缺口写入 repo-local references。
- 没有 first workflow，或 workflow 没有 START -> WORK -> VERIFY -> END。
- 没有 source route、routing reference、workflow skill、owner 状态或 writeback policy。
- 客户/operator 已提供 confirmed product identity、source scope、workflow scope 或 module hints，但输出仍把这些事实写成 unresolved，或无声省略其中一部分。
- 客户/operator 已提供 confirmed module/source/workflow 名称，但输出把它们改名、改大小写、翻译、合并或泛化成 agent 自己的 taxonomy；除非同一个客户/operator 明确要求改名，否则 confirmed 名称就是目标目录名。
- confirmed workflow scope 中有多个 workflow，却被折叠成一个泛化 workflow skill，导致 START/VERIFY/END gate 不可区分。
- confirmed workflow scope 中的 workflow 没有生成同名 `skills/<workflow>/SKILL.md` scaffold，而是只写入 backlog。
- company `skills/` package 保留 `BOOTSTRAP_REQUIRED`、`[needs-evidence: ...]`、`REFERENCES_PATH`、`PROJECT_NAME` 等 bootstrap-time 模板标记，或把模板标记藏进看似可执行的命令。
- source-helper 复制 repo-local 目录/build/test/runtime 真相，或用假 clone URL、假默认分支和通用危险操作填满模板，而不是只保存 source route、边界和 evidence pointer。
- workflow/tool package 写出 evidence inventory 无法支持的产品 CLI、project、branch、label、version、endpoint、job 参数或默认值；工具专用 package 没有实际 source/tool first proof 却宣称可执行。
- confirmed source scope 中的 source 没有生成同名 `sources/<source>/README.md` route scaffold，而是只保留 `gitlab` / `local-repos` 之类泛化来源。
- confirmed module hints 没有 coverage matrix，最终只生成少量 agent 随手归纳的模块，或把客户模块改写成通用 BI / 工程分类。
- 把 Task/Run pointer 当作所有 bootstrap 的硬条件，而非只在 Phase 11 实际使用 jarvis-box Task 执行 shadow pilot 时才要求。
- 同机 fresh CLI 或 `--add-dir` 被当作 Phase 12 合格隔离。
- Task Workspace 被当作 Phase 12 oracle isolation。
- Phase 14 重新生成 install-owned runtime 产品能力（runtime sync、maintenance launcher、session self-improve scheduler、workspace cleanup、service lifecycle、agent routing/failover），而不是接管并验证 day-2 运营。
- history replay 与 session self-improvement 两个演进循环互相替代。
- Phase 11-14 只写成概念性计划，没有 artifact 选择、replay case、writeback log、day-2 operation 的可执行路径。
- Phase 10 被写成 Bootstrap Complete / 最终交付，runtime agent 在没有实际进入 Phase 11 的情况下返回。
- `bootstrap-state.json.phase` 仍停在 Phase 10，却把 Phase 11-14 预判为 `needs-input` / `blocked` / `failed`；尚未进入的未来 phase 必须保持 `pending`。
- Phase 10 checkpoint 把顶层 status 写成最终 `needs-input` / `completed`，而不是保持 `in-progress` 并在同一次 invocation 立即进入 Phase 11。
- `bootstrap --resume` 盲信旧 state 的 `completed`，没有按当前 checklist/verifier 找到最早失效 phase，因而跳过已不合格的 Phase 6/8/9 产物。
- Phase 12 在 pilot repo 有 Git 历史时，没有先自动扫描真实 commits 并尝试构造 replay case，就直接写”等待客户提供历史 episode”。
- Phase 11 只运行固定浅窗口（如 `git log -3/-5/-N`）或只检查一个 pilot repo，就声称没有 `historical-shadow` artifact。
- Phase 12 已经识别 replay candidates，但没有创建任何 `evals/history-replay/cases/<case-id>/history-replay-case.md`。
- `history-replay-case.md`、`replay-failure-analysis.md` 或 `skill-update-decision.md` 未使用规范模板，或模板 sections/fields 未完整填写，或以缩减自由格式替代。
- visible-packet 中的 `replay-prompt.md`、`allowed-sources.md`、`skill-entrypoints.md` 存在未逐条写入 Visible Packet Fact Closure 表，或无法对应 Visible Fact Provenance 中 Fact ID 的事实声明或 narrowing instruction。
- `reconstructed-from-outcome-subject` 投影了 file、directory、module、class、method、field、constant、root cause 或 fix direction，且无独立 pre-outcome provenance。
- replay bridge 调用前未完成 Case Readiness Gate（visible fact 表不完整、packet fact-closure 未审查、声称排除的事实出现在 packet 中、hidden oracle 非从真实 artifact 完整提取、缺 exact evidence command/pointer）。
- `invalid`/`not-ready` case 实际启动了 replay。
- replay case 明确承认 commit title `partially leaks` / 提供 fix directional hint，却仍标 high-confidence 或 `ready-for-replay`。
- `ineligible-leaky` / `low-confidence` / `needs-better-start` case 实际启动了 replay。
- `ineligible-leaky` / `low-confidence` / `needs-better-start` case 被用来得出 `no_skill_gap`、关闭 skill decision 或证明现有 skill 已充分。
- visible packet 中出现最终 commit message、changed-file list、final diff、修复原因、fix 动作描述或从 outcome 推导的实现标识符。
- replay prompt 没有要求 replay agent 在可写 parent snapshot 中完成真实 WORK（诊断后实施候选修复/文档变更并运行可用验证），而是只要求提出方案或分析报告；除非原任务本身就是分析/评审/调研类。
- hidden oracle 使用 `likely`、`probably` 或经验猜测替代从完整真实 final diff/artifact 提取的实际观察 outcome。
- oracle comparison 未先读取 exact replay final output 和 exact 历史 final outcome，或未记录 command/pointer 和完整 changed surfaces。
- 替代 replay 方案在无独立行为验证时被称为等价/更优。
- Phase 12 completed 但没有 eligible case、隔离 evidence、非空 trace/result、oracle comparison、failure analysis、skill decision 中的任一项。
- 某个 skill gap 只来自一个 under-specified / ineligible case，却被写成了 skill 而不是 eval-case-gap / defer。
- replay 完成后先写了 failure analysis 或 skill decision，再做 oracle comparison。
- oracle comparison 没有读取完整 final diff / 等价受控 oracle artifact，却把 replay 漏掉的 changed surface 猜成 cosmetic、supporting 或不重要。
- 泄漏/invalid/未验证 case 产生 `no_skill_gap` 或 skill gap 结论（只能为 `not-evaluated`）。
- 执行后发现泄漏，case 未被分类为 `invalid`/`not-evaluated`，或 Phase 12 未另选有效 case 即标 completed。
- Phase 7 自由生成了 workflow/source-helper skills（这些应由 Phase 9 按 generation plan 实例化）。
- install-owned runtime skills（jarvis-box-doctor/init/monitor）或 external reference skills 被复制到 company repo；或者 company-owned `jarvis-self-improve-skill` 被错误实现成 jarvis-box runtime 副本。
- Phase 14 用单个模糊词（如 `configured`、`installed`）替代五列维度（install/authority evidence、observed current state、last execution proof、readiness、owner & recovery）。
- Phase 14 仅凭 artifact presence、public help、version output 或零活跃 Task 宣称能力已配置/工作。
- Phase 14 把零 Task 写为 `not-applicable` 而非 `unexercised`，或把容器缺少 systemd 当作 service/jobs 的 `not-applicable`。
- Phase 14 声称 `ready-with-explicit-alternative` 但未提供 exact mechanism、owner 和 executability evidence。
- Phase 14 未对至少一个 runtime agent 做真实 prompt probe。
- Phase 14 把 `bootstrap --resume` 当作 Jarvis maintenance authority。
- Phase 14 创建了单独的 `_bootstrap/day2-runtime-checks.md`，而非将所有证据统一写入 `_bootstrap/day2-operation.md`。
- Phase 14 未在更新状态前执行跨产物一致性审查（`MAINTENANCE.md`、`references/runtime-governance.md`、`tools/README.md`、`_bootstrap/day2-operation.md`、`bootstrap-state.json`、`bootstrap-result.json`）。
- Phase 14 在 `unverified` 必要运营能力存在时标 `completed`。
- CLI checks 已证明 `codex`、`claude` 或 `copilot` 可用，却在 `missing_inputs` 里写"缺 isolated replay agent"，而不是写真实原因。
- CLI checks 已证明 isolated replay 可执行，case 也是 `ready-for-replay`，但没有非空 `replay-agent.jsonl`、非空 stderr 或 `replay-result.md` 证明真的执行过。
- E2E/runtime 已提供可执行的 isolation bridge helper，却因为当前 bootstrap 容器里没有 Docker/Podman 再次声称 `isolation runtime unavailable`，并跳过 helper 调用。
- E2E/runtime 已提供可执行的 isolation bridge helper，却把 `request-isolated-replay` bridge、container/VM transport 或 isolated replay transport 写成 missing input。
- 已经存在 `_bootstrap/history-replay-runs/<case-id>/replay-result.md`，但对应 case 目录没有 `replay-failure-analysis.md` 或 `skill-update-decision.md`。
- replay CLI 在首个有效 agent action 前非零退出，skills 根本未被执行，却把结果分类为 `no_skill_gap`、`closed` 或“skills 已验证”。
- 用 Phase 11 shadow pilot 的成功替代 Phase 12 history replay 的执行证据或 oracle comparison。
- Phase 12 没完成时，`phase-13-controlled-writeback` 或 `phase-14-day2-operation` 仍被标成 `completed`。
- Phase 13 消费了 invalid / `replay-not-executed` / 泄漏 / oracle 未验证的 learning signal，并将其计为 `no_skill_gap`、`skill_gap`、`closed` 或 completed candidate。
- Phase 13 将 `deferred`/`not-evaluated` signal 计入完成判定。
- Phase 14 没运行真实 doctor/status/agent checks 就把 install-owned capability 标成 `configured`，或写入 `jarvis-box --help` 中不存在的观测/恢复命令。
- 没有记录哪些事实来自证据、哪些需要 owner 确认、哪些需要 pilot/history replay 生长。
- 把 source 原文、代码、issue、聊天记录、私有路径或 secret 搬进 Jarvis repo。
- `bootstrap-result.json` 只报告文件数量或脚本 pass，却没有说明 checklist 哪些 phase 真的完成、哪些还缺输入。
- `bootstrap-result.json` 或 `bootstrap-state.json` 只存在于 `_bootstrap/`，根目录没有 runtime contract 文件，导致 jarvis-box / 后续 agent 不能稳定读取。
- `bootstrap-result.json` 缺少 `summary`、`paths.jarvis_home`、`paths.jarvis_target_home` 或 `paths.entry_skill`。
- `bootstrap-result.json` 的 runtime 契约字段不可被 jarvis-box 解析，例如把 `blockers` 写成对象数组而不是字符串数组。
- `bootstrap-result.json.paths` 中包含数组或对象，例如把 repo-local skill 路径列表写成 `paths.repo_local_skills: [...]`，导致 jarvis-box 解析失败。
- `bootstrap-state.json` 缺少顶层 `phase`、`paths`、`confirmed_answers`、`method_repo` 或 `phase_status`，导致 runtime / 后续 agent 不能 resume。
- `references/history-replay.md` 缺失，却用 `evals/history-replay/` 或 `_bootstrap/history-replay-runs/` 充当替代。
- repo 可读时，module overview 仍批量使用"本模块相关问题""首次 pilot 后填充""本模块尚未通过 pilot"等通用文本，而不是 module-specific、evidence-backed 的首跳路由、first proof、false owner 和搜索/验证入口。
- evidence pointer 使用 `...`、Unicode 省略号、glob 或说明性后缀，或指向不存在的文件/目录；同一 module 有一条合法 pointer 不能放过其他伪 pointer。
- 3 个及以上 module 拥有相同的归一化首跳路由 section，路由目标不能由各 module 自己的 evidence/repo role 支持时仍批量复用。
- 首跳路由中显式出现的客户 repo 没有被该 module 的 evidence pointer 覆盖。
- Phase 11 dry-run/precheck 没有运行 product-level verification，但仍宣称 module/repo/workflow skills 全部无 gap 或 routing 已充分。
- pilot/shadow artifact 中作者/提交者邮箱未脱敏。
- Phase 12 case 的 provenance 写 "inferred from fix/outcome/final diff/commit context" 等 outcome-derived 来源。
- Phase 12 preflight 未把 hidden changed surfaces 中出现的 exact file/class/interface/method/field/constant 标识符与完整 visible START + visible packet 做交叉检查。语义 provenance 审查属于 runtime agent；确定性检查只抓 exact/structural 矛盾。
- 泄漏 case（ineligible-leaky/low-confidence/needs-better-start）实际启动了 replay bridge；或 replay 结果得出 no_skill_gap、durable skill gap、repo-local/company/upstream writeback 或 closed 等非法 decision。
- Phase 12 已有至少一个有效 eligible replay 闭环，仍把"再补更多 case"写成 missing input。
- `bootstrap-result` 与 `bootstrap-state` 的同名 phase 状态不一致；顶层 status 不一致；任一前置 phase 未 completed 时 summary 宣称 "complete through Phase N"。
- Phase 14 的 doctor/init 输出引用另一套 runtime root 而不是 `bootstrap-state.paths.runtime_root` / `jarvis_box_home` 的已确认值，或把另一套 root 的缺 env/runs 写成 missing input。
- owner 已确认的 human-run/external scheduler 是有效替代机制，仍被写成 missing input。

## 失败时怎么处理

失败不是增加一个“低等级成功”标签。失败只有两个处理方式：

1. 缺客户事实、权限、owner 或确认时，停在 `needs-input` 或 `blocked`，把缺口写清楚。
2. runtime agent 按现有 checklist 执行后仍生成不出符合目标的 repo 时，改 `playbooks/phase-checklist.md` 和相关 phase 文件，让步骤更细、更可执行。

## 对 verifier 的边界

`scripts/verify_bootstrap_output.py` 只做机器防呆：文件是否存在、JSON 是否合法、repo-local package 是否完整、precheck 是否可运行、是否有明显 source dump 或 secret 泄露。确定性检查能捕捉明显的矛盾（占位符残留、JSON 解析错误、文件缺失、precheck 损坏），但不能替代语义审查。

verifier pass 不等于 bootstrap 完成。真正完成只看本文标准和 phase checklist 的执行结果。语义审查——业务含义、source 真源、workflow 可用性、模块身份正确性——必须由 smart-agent 级别的语义审查来判定，机器防呆只是 guardrail。
