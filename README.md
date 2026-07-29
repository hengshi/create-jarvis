# Create Jarvis

`create-jarvis` 是客户从零建设并启用自己 Jarvis 的 Agent 方法仓库。它不是安装器，也不要求客户先安装 jarvis-box。

## 给正在读取这个页面的 Agent

如果客户让你“阅读这个 GitHub 仓库并构建 Jarvis”，这个网页只是入口。不要继续通过 GitHub HTML、`raw.githubusercontent.com` 或一连串 WebFetch 拼装方法。先在当前客户授权的 workspace 中执行一次普通 `git clone https://github.com/hengshi/create-jarvis`，记录 checkout 的 commit，然后从本地读取 `SKILL.md` 及其引用文件。

客户的第一句话只授权读取这个公共方法仓库，不授权你扫描客户电脑。不要枚举 home、`.claude`、`.codex`、`.hengshi`、shell 配置、环境变量、已安装 skills、无关 Git 仓库或历史残留来猜公司情况。先告诉客户你不会扫描电脑，再引导客户提供公司名称、文档入口、代码仓库和工作系统指针；只检查客户明确提供的 URL 或本地路径。

## 客户唯一入口

客户在自己已经登录并授权的 Codex 中只需要说：

> 请先运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

收到这句话的 Agent 是整个建设旅程的 **Construction Coordinator**。它先 clone 并固定本仓库，再主持客户资料 intake、验证客户给出的材料、协调长任务、恢复中断、发布产物、引导 workflow 建设，并在内容达到可部署边界后安装正式 jarvis-box runtime。客户不需要 curl 脚本、安装本地 Skill、选择 create-jarvis 版本、执行 Phase，或复制两条启动命令。

## 一条旅程，两类建设产物

```text
客户的 Host Codex（Construction Coordinator）
  → Preparation
  → Company Jarvis construction ─┐
                                  ├→ reconciliation
  → Repository learning ──────────┘
  → workflow construction
  → formal runtime deployment
  → supervised shadow delivery
  → active workflows
```

Construction Coordinator 使用客户当前 Host Agent 的真实文件、网络、Git 和 source 权限。它不依赖 jarvis-box，也不把建设阶段的人类凭据复制给正式数字员工。

## Jarvis 生态中的身份与边界

| 身份 / 产物 | 所有者与位置 | 负责什么 | 不是什么 |
|---|---|---|---|
| Jarvis 交付方 / 顾问 | 为客户讲解和陪跑的人 | 讲方法、帮助客户校准证据门槛和首个 workflow | 不替客户长期持有代码、账号或生产服务 |
| 客户 | 自己拥有公司材料、Git 平台和运行环境 | 决定授权范围、发布目标、正式身份与生产运维策略 | 不是内部 jarvis-box 源码仓库的使用者 |
| 客户 Host Agent | 客户已登录的 Codex / Claude | clone `create-jarvis`，主持建设、发布客户产物并完成部署交接 | 不是 jarvis-box server，也不是客户事实的来源 |
| `create-jarvis` | 公共 GitHub 方法仓库 | 指导 Company construction、Repository learning、workflow construction、部署和 shadow | 不是安装器、daemon、镜像或客户知识库 |
| `<company-slug>-jarvis` | 客户自己的 GitHub / GitLab repo | 保存公司身份、产品能力、source/repo 路由、跨模块关系和客户 workflow | 不是衡石内部 Jarvis 的副本，也不保存 repo 实现细节 |
| repo-local skills | 客户各代码仓库 | 保存该仓库可验证、可复用的实现与回归知识 | 不是 Company Jarvis，也不是 commit message 汇总 |
| customer workflow skills | 客户 Company Jarvis | 把客户真实角色、权限、review/test/release/acceptance 串成 bugfix/feature 等闭环 | 通用 starter 只是模板，不能直接冒充已上岗 workflow |
| Hengshi Jarvis | 衡石自己的成熟 Company Jarvis | 是衡石业务和研发工作流的运行实例，可用于理解最终形态 | 不是客户模板、客户事实或需要复制的仓库 |
| jarvis-box 内部源码 | 交付方私有 GitLab | 开发、测试和发布 jarvis-box | 客户部署不需要、也不应取得该源码 |
| jarvis-box 公共发布面 | GitHub Releases / 公共下载地址 | 向客户交付 release bundle、校验文件、镜像 digest 和版本说明 | 不要求客户 clone GitHub 源码来运维 |
| jarvis-box release bundle | 客户下载并解压的只读版本目录 | 提供 `compose.yaml`、部署脚本、模板和 `CUSTOMER-OPERATIONS.md` | 不是客户私有 deployment home |
| jarvis-box OCI image | 公共 registry 中固定 digest 的镜像 | 内置 jarvis-box、固定版本 uv-im-connector、Agent CLI 和工具链 | 不是两个由客户自行搭配的产品镜像 |
| jarvis-box service | 正式 Compose 中的主服务 | Task/Run、Agent 执行、Company context、日志与诊断 | 不是 construction 工作台 |
| uv-im-connector service | 正式 Compose 中可选的 IM 边界 | 使用独立凭据、配置、日志和 volume 连接飞书/企微等 IM | 二进制虽独立演进，但不要求客户选择第二个 image |

因此，正式部署是“一个 release bundle + 一个固定 image digest + 一个或两个 Compose service”。启用 IM 时，两个 service 运行同一个 image 中的不同 binary；客户只维护一个镜像版本。

### Company Jarvis construction

输出是客户拥有并发布在其 GitHub 或 GitLab 上的 `<company-slug>-jarvis` repo。它保存公司级身份、产品能力、source、repo fleet、跨模块关系、路由和客户 workflow，不复制代码仓库中的实现真相。

### Repository learning

输出写回各代码仓库自己的 repo-local skills。Agent 按客户选择的一年、两年、全部或自定义历史范围读取 commits 的真实 code changes，从完整历史 episode 中执行 baseline replay、真实 outcome comparison、最小 skill delta 和 same-case rerun。commit message 只用于导航；不会生成 `eval-loop` skill。

## Coordinator 的最小工作文件

```text
jarvis-build/
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── RUN-COMPANY-JARVIS-CONSTRUCTION.md
├── RUN-REPOSITORY-LEARNING.md
├── COMPANY-JARVIS-PROGRESS.md
└── REPOSITORY-LEARNING-PROGRESS.md
```

- `CONSTRUCTION-JOURNAL.md` 只是恢复索引：固定的 method commit、两份 progress pointer、远端交付 pointer、当前 blocker 和下一动作。它不复制 lane progress，也不是机器状态机。
- `BUILD-CONTEXT.md` 记录授权构件、精确 revision、write/delivery policy 和正式发布目标，不保存正文或凭据。
- 两个 `RUN-*.md` 是 Coordinator 派发给独立工作 lane 的自包含合同，不是客户操作手册。
- 只有当前 Agent 确实需要 provider-native 子进程命令时，才按需生成 `START-HERE.md` 作为恢复兜底。

Agent 或机器中断后，客户再次发送同一句话即可。Coordinator 先寻找既有 journal；找到后使用其中固定的 method commit，验证 pointers，再从 `Next` 继续。找不到 journal 时才开始新的建设。

## 产物必须可消费

Company Jarvis 与 repo-local skills 都必须遵守客户 Git policy，并记录真实 branch、commit、PR/MR、review/merge 状态和验证结果。只有本地 dirty delta 不算交付。

大客户可以先达到某个 workflow 所需的 route-scoped usable boundary，但必须明确尚未学习的仓库和历史范围。后续 learning 写入新 branch/ref，不得让正在 shadow 或 active 的 runtime snapshot 漂移。

## Workflow 生命周期

```text
draft-template
  → construction-ready
  → runtime-deployed
  → ready-for-shadow
  → shadowing
  → active
```

- `construction-ready`：客户路由、角色、source、repo、review/test/release policy 已写入，并通过至少一个受控或真实 case。
- `ready-for-shadow`：正式 runtime 已加载固定的 Company/repo/image revisions，并通过容器内 routing、source、Agent 和 capability probes。
- `active`：代表性真实任务在 supervised shadow 中稳定闭环，并得到客户批准。

`active` 属于某个 workflow 和一组不可变 revisions，不代表整个客户 Jarvis 的所有范围都已完成。

## create-jarvis 与 jarvis-box 的边界

- `create-jarvis` 负责建设旅程、知识分层、历史学习、workflow construction、正式部署 handoff 和 shadow promotion。
- `jarvis-box` 是后续正式高权限数字员工 runtime，不是客户建设工作台。
- 客户从 jarvis-box 公共 release bundle 获得部署脚本和完整运维文档，不 clone 私有源码。`scripts/deploy-production.sh` 位于解压后的 release 目录；客户私有的 deployment home 只保存配置、不可变 Company snapshot、凭据引用、持久化数据和 deployment lock。
- 正式镜像同时内置 jarvis-box 与固定版本的 uv-im-connector。Compose 可启动两个独立服务，但两者使用同一个 `JARVIS_IMAGE` digest，不存在客户选择的 `UVIM_IMAGE`。
- 正式 runtime 使用独立、可审计、可轮换、可撤销的高权限身份。身份可以按客户授权拥有超级管理员能力；独立身份的目的不是降权，而是与建设阶段的人类身份分开治理。
- `jarvis-box server` 与它启动的 Agent 属于同一个高权限信任域；IM provider 原生凭据属于独立的 connector。

完整内容路径见 `playbooks/customer-jarvis-growth-loop.md`，角色与恢复边界见 `playbooks/one-plus-two-runtime-model.md`，construction/runtime 边界见 `playbooks/runtime-method-contract.md`。

## 验证原则

确定性脚本只验证路径、渲染、安全和可执行合同。方法质量必须通过真实 Agent 行为验证：一句话是否启动完整 journey、中断后是否恢复、Company construction 是否形成证据支持的路由、Repository learning 是否从真实 episode 改善行为、正式 runtime 是否消费固定 revisions。不要用 Markdown 关键词或 `assertIn` 冒充方法论测试。
