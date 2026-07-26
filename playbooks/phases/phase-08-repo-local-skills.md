# Phase 8 - 创建仓库本地技能包

目标：为 first workflow 涉及的 pilot repos 创建 repo-local skill 目录包或 backlog。

## 核心原则

必须先运行确定性母版实例化器，再以真实 repo evidence 填充：

```
python scripts/instantiate_repo_local_skill.py --repo <path>
```

这会从 `templates/repo-local-skill/skills/` 复制 canonical 9-file package 并渲染 `{{REPO_NAME}}` token。precheck 自动设为 executable。

升级已有 package 时，instantiator 只会自动移除内容仍与旧版生成模板完全一致的 `skills/eval-loop.md`。该文件若有客户编辑会 fail closed：先由 owner 审查，把仍可复用的规则迁入实际 primary `SKILL.md`、focused reference 或验证脚本，再删除 legacy 文件。不得盲删或静默保留。

Phase 8 完成后，specialised skills 进入 Phase 12 演进（从真实 history replay 生长）。canonical 9 文件是起点，不是成熟度上限；eval loop 是 Phase 12 的控制流，不生成独立的 eval-loop skill/file。

## 判断顺序

1. 该 repo 是否已有执行入口或 repo-local skill 目录。
2. first workflow 是否真的需要 agent 在该 repo 中执行。
3. build/test/lint/CI 命令是否能从 repo 证据或 owner 确认。
4. 缺口是否是 `no_skill_gap`、文档缺口、repo-local skill 缺口，还是 runtime/source 权限问题。

已有 repo-local skill 不是自动合格。runtime agent 必须检查它是否满足本 phase 的 canonical package contract；缺任何核心文件时要补齐，不能用“已有更多 reference 文件”替代固定核心文件。`AGENTS.md`、`CLAUDE.md`、`.claude/skills`、`.agents/skills`、`.codex/skills` 都不能替代 repo root 的 canonical `skills/` package；如果 root `skills/` 缺失，必须创建。

## 输出

- 每个 pilot repo 的 status：reuse existing、create package、backlog、blocked、no_skill_gap。
- repo-local skill 目录包，或明确 backlog。
- company Jarvis 只在 `references/jarvis-first-routing.md` 或对应 workflow skill 中登记 pilot repo 的角色、路由和边界，不复制 repo execution truth，不创建顶层 `repos/`。

## 最小目录包

```text
skills/
├── SKILL.md
├── code-review/SKILL.md
├── code-review/scripts/precheck.sh
├── references/source-of-truth.md
├── references/architecture-map.md
├── references/test-entrypoints.md
├── references/runtime-and-testability.md
├── references/history-replay-loop.md
└── self-skills-improve/SKILL.md
```

引导生成阶段不只是创建骨架。repo-local skill package 的确定性九文件创建完成后，必须立即检查每个可读 repo 并填入所有可直接观察的事实：

- 实际 default branch 和可由证据支持的分支策略；default branch 必须来自 remote HEAD 或 VCS project metadata，当前 checkout 分支只能作为补充观察，不能单独充当 default branch
- repo 角色和边界
- 语言/构建文件
- 重要路径
- package/module 布局
- 精确的 build/test/lint/CI 命令及其证据（来自 CI 配置、Makefile、package.json scripts 等）
- 测试/fixture 位置
- runtime 前提条件
- source-of-truth 指针
- 可观察的生成区域
- 公司 handoff

`skills/code-review/SKILL.md` 的“仓库特有检查”表也必须在 Phase 8 收尾时完成。不得因为没有立刻找到额外 review trigger 就保留 `BOOTSTRAP_REQUIRED`。如果在已记录的代码、配置、CI、测试和历史扫描范围内确实没有观察到额外 trigger，写一条明确的 `not-observed` 记录，包含实际扫描范围和 pointer；这表示当前没有额外证据，不是凭通用常识补造检查，也不是把 sentinel 当作完成。

**区分 `observed-not-executed` 和 `executed-pass`**：命令可以从构建/CI 证据中记录下来而不假装执行过。不要在未实际运行时标 `executed-pass`。

语言生态惯例本身不是 repo evidence。不能因为看到 `go.mod` 就补出 `go build ./...` / `go test -race ./...`，也不能因为看到 `pom.xml` / `package.json` 就补出未在 manifest、wrapper、CI、repo 文档、owner confirmation 或执行记录中出现的命令。

Owner 确认和历史回放用于模糊策略和成熟的失败模式，不用于 checked-in 文件中可直接看到的事实。

**禁止**：repo 可读时，任何核心 repo-local 文件保留 `<>` 占位符、泛化示例命令、伪造的 default branch 或全面 `needs-owner-confirmation`。

模板复制进客户 repo 后必须成为长期可用的 repo-local skill。`Phase 8 填充`、`用真实内容替换下表` 等生成期旁白不得留在最终 package；其中仍有长期价值的规则必须改写成不依赖 bootstrap phase 的 evidence contract。

**差异化要求**：八个 package 必须根据各自 repo 证据有所不同。三个或以上归一化相同的 repo truth section 证明 Phase 8 被跳过。

专业的历史衍生 reference 可以后续生长，但基础 skill 必须已经能让一个新 agent 路由、构建、测试和找到 source truth。

## 首个工作流的语义执行 trace

canonical 九文件包只是文件形状，不代表 repo-local skill 已经具备执行能力。对 first workflow 需要在 `skills/SKILL.md` 中再填一张可审查的语义执行 trace；如果该 repo 不承担 first workflow，必须明确写 `not-applicable` 并记录判断依据。

当 first workflow 包含 issue/bugfix、回归或代码修改时，trace 至少必须包含：

- visible initial signal 的形状和精确 repo-relative / artifact pointer；
- 需要保持不变或可能出错的 semantic value，例如 request field、response field、HE/HQL expression、generated SQL fragment、resource identity 或 error code；
- 该值经过的每个实际 rewrite/normalize/serialize/query/response boundary，以及每个 boundary 的 source pointer；
- 最窄的 owning sink 和为什么不是更外层 controller/helper；
- 对应的最小 repro、regression test 或等价行为断言 pointer；
- 每条验证命令的来源、是否实际执行，以及 `executed-pass` / `observed-not-executed` / `blocked` 状态。

如果症状涉及请求/响应字段、过滤、聚合、表达式、生成 SQL 或外部 provider，必须显式检查 predicate placement（如 `where`/`having`）、表达式 rewrite 和 response assembly 三者是否位于同一条证据链中。只能观察到 response field 缺失时，不得直接把 response collector 当作 root cause。

Phase 12 history replay 必须能从 repo-local skill 读到这张 trace，并用实际 replay trace 验证每个字段；否则该 package 只能标 `needs-improvement`，不能因 precheck 通过而标成熟。

即使 repo 已有更丰富的 reference 文件，也必须保留上述固定文件名。特别是 `references/runtime-and-testability.md` 不能被 `runtime-and-forensics.md`、`local-dev-runtime.md` 等近似文件替代；可以在固定文件里链接这些更细 reference。

`skills/code-review/scripts/precheck.sh` 必须是客户 repo 自包含脚本。它可以读取当前 repo 内的文件，但不能依赖 reference company、bootstrap 操作员或其他机器的绝对路径、私有脚本和维护命令。如果发现已有 precheck 存在这类依赖，必须改写为自包含 scaffold，并把迁移事实写入 repo-local reference。

bootstrap 阶段的 `precheck.sh` 是 bootstrap-safe scaffold check，不是完整语言栈环境验收。它必须：

- 从 repo root 可执行；未填充的初始骨架应因 canonical 核心文件缺失、临时占位、未渲染 token 或硬编码的机器私有路径而退出非 0，Phase 8 填充完成且不存在这些 contract blocker 后才退出 0；
- 输出明确 repo marker，例如 `repo: <repo-name>`；
- 检查 repo 内稳定文件、目录、配置和 fixed contract；
- 对 JDK、Node、pnpm、Go、Docker、kubectl、shellcheck 等技术栈工具只能输出 `WARN` / `INFO` 和后续安装建议，不能在 bootstrap 阶段作为 hard fail；
- 把缺失工具写成实际 `blocked` 原因；把从 manifest / Makefile / CI 读到但未运行的命令写成 `observed-not-executed`。不要把可直接读取的命令写成 `needs-owner-confirmation`，也不要让缺失开发工具本身成为 precheck 的 hard fail。

## 必做收尾

每个创建出来的 repo-local skill package 都必须完成：

1. `chmod +x skills/code-review/scripts/precheck.sh`。
2. 从 repo root 执行 `skills/code-review/scripts/precheck.sh`。
3. 确认输出中包含 `repo: <repo-name>` 或等价 repo root marker。
4. 确认 precheck 不引用 reference company 私有路径或维护命令；如果引用，先改成自包含脚本再执行。
5. 如果 precheck 报告 `BOOTSTRAP_REQUIRED` 或未渲染 token，必须回到对应文件逐项填充后重新执行 precheck；不得把失败记录成“工具缺失”、跳过该 repo，或直接进入 Phase 9。
6. 在 `references/jarvis-first-routing.md` 或 `skills/<slot>-workflow-<name>/SKILL.md` 中写明：
   - repo-local skill path；
   - first workflow 中该 repo 的角色；
   - 哪些事实必须留在 repo-local；
   - 哪些命令或 owner 信息仍待确认。
7. 对 first workflow repo，读取并确认 `skills/SKILL.md` 的语义执行 trace 已填实；缺 semantic value、rewrite boundary、owner sink、regression proof 或验证状态任一项时，写入 backlog/blocker，不得标 completed。

如果 precheck 不能执行，不能把该 repo 的 repo-local skill status 标成 completed；应写入 blocker、backlog 或 unresolved question。缺少客户 repo 技术栈工具不是 precheck 不能执行的理由；此时应让 precheck 通过并把缺失工具记录为待确认/待安装。

## 写入客户仓库

创建并验证本地 package 不等于已经把 repo-local skills 交付给客户仓库。对每个 pilot repo，必须执行 Phase 4 已确认的 repo writeback plan：

1. 读取实际 remote/default branch、保护规则和当前 worktree 状态；不得从当前 checkout branch 猜 default branch。
2. 如果 repo 有与 bootstrap 无关的未提交改动，保留现场并改用独立 worktree/branch；不得清理、覆盖或混入提交。
3. `disabled`：不写文件，记录 blocker 或 backlog，不把该 repo 标为 delivered。
4. `local-only`：保留已验证 diff，记录本地 branch/路径、owner 和后续发布条件，不声称远端已交付。
5. `branch + MR/PR` 或 `human-approved`：从实际 default branch 创建专用 bootstrap branch，只提交该 repo 的 repo-local skill 变更，推送并创建 MR/PR；不自动合并。
6. 只有客户明确允许直接提交且分支保护允许时，才能直接 push；记录批准人、依据、commit SHA 和 remote branch。
7. push 前运行 `git diff --cached --check`、repo-local precheck 和本 repo 已确认的必要检查；未执行的 product test 必须标 `observed-not-executed`，不得写 PASS。
8. 在 `bootstrap-state.json` 为每个 pilot repo 记录 project path、default branch、publication policy、local branch、commit SHA、MR/PR URL、checks 和 delivery status。不得记录 token。

这些是初始 repo-local package 的交付步骤，不是 Phase 13 的受控学习写回。Phase 13 只处理 Phase 11/12 已验证的新 learning。

## 禁止

- 不为非 pilot repo 创建 skill package。
- 不从中心 Jarvis 猜 repo 命令。
- 不把 repo-local truth 写成 company-wide rule。
- 不保留依赖 reference company 环境的 precheck、脚本或路径。
- 不覆盖客户未提交改动，不 force-push，不绕过保护分支，不自动合并 MR/PR。
- writeback policy 要求远端交付但 push/MR/PR 失败或无权限时，不标 delivered/completed。
