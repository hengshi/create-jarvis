# Phase 9 - 实例化完整 workflow/source-helper skill packages

目标：按 Phase 6 generation plan 实例化完整的 workflow/source-helper skill packages。Phase 9 是这些 skills 的唯一创建者——Phase 7 建立了容器骨架，Phase 9 填充 workflow 和 source 能力。

## 核心原则

必须使用确定性母版实例化器：

```
python scripts/instantiate_company_jarvis.py package --state <...> --kind <template kind> --name <confirmed exact output name>
```

这会从 `templates/skill-packages/<kind>/` 复制完整 package（SKILL.md + references/jobs/scripts 如适用）并渲染全局 token。

完整 package 包括：
- 母版 `SKILL.md`（包含 START -> WORK -> VERIFY -> END 闭环）；
- `references/`（如适用：routing reference、quality gate、boundary rules）；
- `jobs/`（如适用：scheduled 或 trigger-based jobs）；
- `scripts/`（如适用：可执行 helper scripts）。

不能只生成统一 35 行 scaffold。每个 package 必须消费 Phase 6 evidence inventory 和 generation plan 中的事实。generation plan 必须明确 template kind；package 内 companion files 是 mandatory。

### 两类变量必须分开

- **Bootstrap-time value**：source route、project path、owner 状态、已选工具、reference 路径、first workflow handoff 等客户事实。Phase 9 必须从已收集证据填实，或写成带已检查证据和恢复条件的 `unresolved`；产物不得保留 `BOOTSTRAP_REQUIRED`、`[needs-evidence: ...]`、`REFERENCES_PATH`、`PROJECT_NAME` 等模板标记。
- **Task-time parameter**：每次运行 workflow 时才知道的 issue iid、project path、branch、artifact path、版本号等。可以在命令/输出合同中写成 `<issue-iid>` 这类明确参数，但必须说明从 START artifact 或 route 中获取，不能伪装成已经确认的客户事实。

`create-scaffold-needs-pilot` 只表示方法尚需真实 pilot 校准，不允许保留模板 token。它必须写清已经可执行的部分、缺哪个真实 artifact、如何恢复和什么证据才能升级。

## Package 选择性

- 只实例化 Phase 6 generation plan 中标记为 `create-now` 或 `create-scaffold-needs-pilot` 的 skills。
- 未适用的 package（generation plan 中没有的）不复制。
- install-owned runtime skills（jarvis-box-doctor、jarvis-box-init、jarvis-box-monitor）不复制到 company repo；Phase 14 只检查/登记它们。
- `jarvis-self-improve-skill` 是可由客户确认的 company-owned 方法论 workflow，不等同于 jarvis-box 的 session self-improvement runtime。确认出现在 workflow scope 时，使用 `self-improve-skill` package 生成它；该 package 只能描述证据读取、归因、决策和写回边界，不得复制 collector、scheduler 或其他 runtime 实现。
- external reference skills 不复制到 company repo。

## Source Skill

source skill 负责访问、路由、边界和安全提示。它不复制 source 内容。

source-helper 也不承载 repo-local execution truth。Git repo 的目录布局、build/test 命令、runtime 前提和代码审查规则仍在该 repo 的 `skills/`；source-helper 只指向 `sources/<source>/README.md` 和对应 repo-local entry。

完整 source skill package 必须说明：

- source 类型和访问方式；
- allowed operations；
- forbidden operations；
- secret boundary；
- evidence pointer 写法（引用 evidence inventory 中的具体 retrieval/check）；
- unresolved 权限或 owner。

不得为填满 source-helper 而发明 clone URL、默认分支、build/test 命令、环境变量、危险操作或技术栈。不可访问时只保留真实访问状态、缺失输入和恢复条件，不生成伪命令。

每个 source skill 位于 `skills/<source-skill>/SKILL.md`。如果 generation plan 对其有 `references/` 或 `scripts/` 要求，一并创建。

## Workflow Skill

workflow skill 负责 START -> WORK -> VERIFY -> END 的跨 source/repo/team 闭环。

完整 workflow skill package 必须说明：

- trigger；
- owner；
- gates（包括 claim normalization、disposition routing）；
- repo/source handoff（指向具体 repo-local skill 和 source route）；
- verification（具体可运行的检查，不是概念性描述）；
- escalation；
- END writeback judgment。

模板中的方法语义可以直接复用，但工具、project、branch、label、version、endpoint 和验证命令必须由客户证据支持。需要特定系统或 CLI 的 package（例如文档 API、CI job builder）只有在 Phase 6 已确认该 source/tool 可用时才能 `create-now`；否则应为 `create-scaffold-needs-pilot` 或不创建，不能把 reference company 的命令改个前缀后当客户能力。

每个 workflow skill 位于 `skills/<workflow-skill>/SKILL.md`。如果 generation plan 对其有 `references/`、`jobs/` 或 `scripts/` 要求，一并创建。

## 多个 confirmed workflows 的处理规则

- issue intake / post-check / bugfix loop 不能合并成一个含糊的 issue workflow；它们的 START artifact、claim gate、verification 和 END writeback 不同。
- feature delivery / PRD review / release notes / branch-neutral docs 等确认 workflow，可以在首日只创建 scaffold，但每个都要有独立 skill 和完整 package 形状。
- 如果缺真实 artifact、缺 source 或缺 owner，把缺口写进 skill 的 status / unresolved / verification sections；不要把它变成 backlog 后不落文件。
- workflow scope 中的值默认就是目录名，例如 `skills/<workflow>/SKILL.md`；不要把客户确认的 workflow 名翻译、缩写或合并。

## 多个 confirmed sources 的处理规则

- source scope 中的值默认就是目录名，例如 `sources/<source>/README.md`。
- 如果暂时不能访问，仍然创建 route scaffold，并标记 `needs-access` / `raw-export-boundary` / `needs-owner-confirmation`。
- 不要把 `api-docs`、`customer-success`、`official-website` 等客户确认来源改写成 `gitlab` 或 `local-repos`。
- Phase 7 已创建 `sources/<source>/README.md`；Phase 9 为需要 source skill 的 source 创建 `skills/<source-skill>/SKILL.md` 完整 package。

## 步骤

1. 读取 Phase 6 的 `_bootstrap/discovery/generation-plan.md`。
2. 对 generation plan 中每个 `create-now` skill：
   - 运行 `python scripts/instantiate_company_jarvis.py package --state <...> --kind <template kind> --name <output name>`
   - 消费 evidence inventory 中的具体事实填充 trigger、gates、handoff、verification；
   - 没有证据的精确值先穷尽 route/repo/source evidence；仍未知时写 `unresolved`、已检查内容和恢复条件，不能留下模板标记或伪可执行命令。
3. 对 generation plan 中每个 `create-scaffold-needs-pilot` skill：
   - 创建完整 package 骨架，标 `status: scaffold-needs-pilot`；
   - 写清缺什么 artifact、source 或 owner 才能从 scaffold 升级到完整 skill。
   - 删除所有 bootstrap-time 模板标记；只允许 task-time 参数占位。
4. 确认没有创建 generation plan 之外的 skills。
5. 确认没有复制 install-owned runtime skills 或 external reference skills；确认的 company-owned `jarvis-self-improve-skill` 必须使用专用 package，且不含 runtime 实现副本。
6. 对每个 package 逐文件检查：所有 company reference 链接可解析；所有 companion files 存在并被入口引用；没有 reference-company 名称/路径；没有未经证据支持的产品 CLI、技术栈、endpoint 或默认值。

## Phase 9 Gate

进入 Phase 10 前运行：

```bash
python3 scripts/verify_bootstrap_output.py \
  --stage phase-09 \
  --jarvis-home <company-jarvis-home> \
  --customer-repos-dir <authorized-repo-checkouts>
```

这个 gate 只验 Phase 3-9 已经应该完成的内容，不要求 shadow pilot、history replay 或 day-2 产物。任何 module/routing/source/workflow/repo-local blocker 必须先修复，不能把 verifier 留到昂贵的 replay 之后。

## 停止条件

- workflow 不是 generation plan 中的 `create-now` 或 `create-scaffold-needs-pilot`。
- source 权限未知但仍要写访问步骤。
- skill 只是"以后可能有用"且不在 generation plan 中。
- confirmed workflow/source 被改名、合并或省略。
- skill package 只有统一 scaffold 没有消费 evidence inventory。
- install-owned runtime skills 或 external reference skills 被复制到 company repo；或 company-owned `jarvis-self-improve-skill` 变成了 runtime 实现副本。
- package 仍有 `BOOTSTRAP_REQUIRED`、`[needs-evidence: ...]`、未渲染 token 或模板字段名。
- source-helper 复制了 repo-local build/test/runtime/目录真相，或 workflow package 写入 evidence inventory 无法支持的命令、project、branch、label、version、endpoint、工具默认值。
- 工具专用 package 没有可访问 source、已确认 CLI/API 和最小 first proof，却被标成可执行。
