# Preparation agent task

你是客户已经登录的 runtime agent。你的任务不是构建 Jarvis，而是为两个独立的长任务准备可靠、可直接执行的 handoff。

## 1. 确定任务目录

在 runtime 声明的 agent-owned workspace 下选择一个普通目录，例如 `jarvis-build/`。先实际验证当前 agent 能在其中 create、read、write、rename。不要使用 service-private runtime root，也不要通过提权或 world-writable 权限绕过问题。

同时确认 Git、GitHub CLI (`gh`) 和 GitLab CLI (`glab`) 的可用状态。客户只需要登录自己选择的平台；另一个平台未登录不是 blocker。只记录命令、host、账号/namespace 和 probe 结果，不记录 token、cookie、SSH private key 或其他 credential value。

## 2. 收集构件信息

优先从当前环境、Git metadata、已授权 connector 和客户给出的路径自动发现。这里只做 inventory，不深入提炼公司 Jarvis 内容，也不执行历史 eval loop。

为每个代码仓库记录：

- 准确名称、绝对本地路径和 remote URL（如有）；
- 当前 revision、default branch 和 working tree 是否已有改动；
- 它目前可读还是可写；
- 客户允许的写入方式：read-only、local-only、branch、branch + MR/PR；
- 可访问的 issue、MR/PR、review、CI 和测试历史入口；
- 当前已知的 repo 角色；不知道就写 `unresolved`，不要编造。

为文档和其他工作系统记录：

- 类型、准确路径或稳定 URL/connector pointer；
- 当前访问状态和范围；
- 它可能提供哪类事实；不知道就写 `unresolved`。

记录已经确认的公司名称、slot/slug、company Jarvis 目标目录和 Repository learning 范围。客户可以指定最近一年、最近两年、全部可达历史，或自定义日期/ref；允许全局范围，也允许某个 repo 单独覆盖。把相对范围解析为当前日期下的精确时间边界，并记录执行时的 HEAD/ref；`all` 记录为“从当前 revision 可达的最早 commit 到当前 revision”。若客户没有指定，采用最近 12 个月作为明确、可修改的默认值，不必为此阻塞 preparation。

### 确认 company Jarvis 的远端发布目标

Company Jarvis 的正式交付必须进入客户选择的 GitHub 或 GitLab，而不是只留在 container 本地。按以下优先级确认：

1. 客户明确指定的平台、host 和 owner/namespace；
2. 已授权客户 repo 的 canonical remote 与当前已登录 provider 能唯一指向同一个客户命名空间；
3. 仍有多个平台、host 或 namespace 候选时，只问客户一个最小确认问题。

不能因为安装了 `gh` 或 `glab`、当前登录了某个个人账号，或多数代码仓库恰好位于某个 owner 下，就擅自替客户选择。GitHub Enterprise 或 self-managed GitLab 使用客户实际 host，不强制 `github.com` / `gitlab.com`。

确认并 live probe 以下合同：

- provider：`github` 或 `gitlab`；
- host 与 customer-owned owner/organization/namespace；
- canonical repo name：`<company-slug>-jarvis`；
- canonical remote URL 和首选 transport（沿用客户已配置的 SSH/HTTPS）；
- visibility：新 repo 默认 `private`，除非客户明确选择其他值；
- default branch：新 repo 默认 `main`，已有 repo 服从远端事实与客户 policy；
- 远端是否不存在、为空、或已有历史；
- 当前身份是否有 read、create、push 和 create PR/MR 所需权限；
- publication mode：`new-initial-push`、`empty-initial-push`、`existing-branch-review` 或 `blocked`。

通过 provider CLI/API 做只读探测。若目标已存在，记录真实 default branch、visibility 和 history 状态；若不存在，只验证目标明确且当前身份具备创建权限，不要在 Preparation 阶段提前建仓。远端目标或授权无法确认时，不得降级为“先只交本地 repo”；把它作为 Company construction blocker 明确交给客户。

不要把 token、cookie、password、private key、源代码、文档正文或大量 issue 内容写入任务目录。

## 3. 写四个文件

### `BUILD-CONTEXT.md`

它是两个执行 Agent 的共同输入，至少包含：

- observed runtime 与 workspace；
- confirmed company identity 与仍未解决的 identity conflict；
- company Jarvis target；
- company Jarvis publication contract：provider、host、owner/namespace、repo name/URL、visibility、default branch、existence/history 状态、权限 probe 和 publication mode；
- repository inventory 表；
- docs/work-system inventory 表；
- 全局及 per-repo Repository learning 范围（原始选择、解析后的时间/ref 边界和当前 revision）；
- 每个写入目标的 write policy；
- preparation 时实际执行过的 access probe 及结果；
- unresolved facts，但不包含凭据值。

每条事实都要有可复查 pointer。不要把“路径存在”写成“内容已经理解”。

### `RUN-COMPANY-JARVIS-CONSTRUCTION.md`

先要求执行 Agent 读取 `playbooks/customer-jarvis-growth-loop.md` 的 Company construction 步骤，再以 `playbooks/prompts/company-jarvis-construction.md` 为方法正文，补入以下绝对路径：

- `BUILD-CONTEXT.md`；
- company Jarvis target；
- `COMPANY-JARVIS-PROGRESS.md`；
- 当前 method pack。

同时写入已经确认的 company Jarvis publication contract。明确客户代码仓库对该 Agent 是只读证据，唯一主要写入目标是 company Jarvis target 及其对应的 customer-owned GitHub/GitLab remote。

### `RUN-REPOSITORY-LEARNING.md`

先要求执行 Agent 读取 `playbooks/customer-jarvis-growth-loop.md` 的 Repository learning 步骤，再以 `playbooks/prompts/repository-learning.md` 为方法正文，补入以下绝对路径：

- `BUILD-CONTEXT.md`；
- `REPOSITORY-LEARNING-PROGRESS.md`；
- replay 工作目录；
- 当前 method pack。

把 inventory 中的 repo 全部列为学习范围，并逐个带上 write policy。明确它不能修改 company Jarvis target。

### `START-HERE.md`

根据当前已登录 agent 写出两条真实命令。命令必须：

- 分别启动一个新 runtime agent；
- 从对应 `RUN-*.md` 的标准输入读取完整任务；
- 使用任务目录作为工作目录，并授予构件清单中必要的准确路径；
- 不在命令行展开凭据；
- 不保留 `<path>`、`$TODO` 等占位符。

Codex 的命令形态可以是：

```bash
codex exec -C /absolute/jarvis-build --skip-git-repo-check --add-dir /absolute/authorized-root - < /absolute/jarvis-build/RUN-COMPANY-JARVIS-CONSTRUCTION.md
```

Claude 的命令形态可以是：

```bash
cd /absolute/jarvis-build && claude --print --add-dir /absolute/authorized-root < /absolute/jarvis-build/RUN-COMPANY-JARVIS-CONSTRUCTION.md
```

根据现场实际 agent 只生成适用的命令，并为 Repository learning 生成对应的第二条。路径必须做 shell-safe quoting。不要擅自加入跳过权限或 sandbox 的危险参数。

## 4. 停止并交付

检查四个文件中的路径均存在或是明确的新建 target，两条命令没有占位符，并且 company Jarvis publication contract 已确认或被明确标为 blocker。然后停止，不要在当前 session 中开始执行任一长任务。

最终只告诉客户：

1. 任务目录；
2. 两条可复制执行的命令；
3. 如果确有 blocker，只说当前唯一 blocker。
