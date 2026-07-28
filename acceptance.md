# Create Jarvis 验收标准

## 一句话入口与恢复

- 在没有 jarvis-box 的 Host 上，客户只给已授权 Codex canonical GitHub URL 和建设请求，Agent 即可开始。
- Agent 先 clone canonical repo，固定 method commit，再从本地读取完整方法；它不通过 GitHub HTML/raw URL/WebFetch 逐文件拼装方法。客户不 curl、不安装 Skill、不选择版本、不运行 phase 或两条子任务命令。
- 全新 journey 创建 `BUILD-CONTEXT.md`、两个 `RUN-*.md` 和 pointer-only `CONSTRUCTION-JOURNAL.md`。
- 再次发送同一句话时，Agent 先找到 journal，切回记录的 method commit，验证 pointers 后继续，不重建或自动升级方法。
- 没有子 Agent 时，由 Coordinator 顺序执行两个 lane；它不虚假承诺上下文隔离、后台进程或 heartbeat。

## Preparation

- Agent 先明确告诉客户不会扫描电脑，再引导客户提供公司身份、repo、文档和工作系统指针；一个 pilot product/repo 即可启动。
- 客户提供 pointers 前，Agent 不创建 phase/task 列表、`jarvis-build`、Company modules 或猜测的 repo scope。
- inventory 只覆盖客户明确提供的 URL 或路径，记录准确 pointer、live access、revision、dirty state 和 write/delivery policy。
- Agent 不枚举 home、Agent 配置/历史、shell profile、环境变量、installed skills、无关 repo 或旧 runtime 残留来推断公司身份与 source scope。
- GitHub/GitLab、host、owner/namespace、Company Jarvis repo、visibility、default branch和 publication mode 有现场证据；有歧义时只问一个最小问题。
- 每个代码 repo 的交付方式明确为 read-only、local commit、branch push 或 branch + PR/MR。
- 文件不包含凭据、source dump、未解析占位符、`jarvis.toml` 或 bootstrap JSON 状态机。

## Company Jarvis construction

- 输出是 customer-owned Company Jarvis repo，而不是知识 dump 或 repo-local skill 集合。
- 授权范围中的 capability/source/repo 都有 evidence-backed disposition。
- included capability 有产品锚点、实现锚点和 first proof/verification contract。
- Company entry 能从真实 artifact 路由到 module/source/repo next hop；cross-cutting 不复制实现真相。
- starter workflows 保持 `draft-template`。
- 新/空远端拥有可达 commit；已有远端保留历史并通过 branch + PR/MR 交付。
- progress 记录 remote、branch、commit、PR/MR、review/merge 状态和验证结果；只有本地目录不算完成。
- construction/onboarding 可在 Host Agent 中执行，不要求 `jarvis-box version/status/agent current`。

## Repository learning

- 所有 repo 共用一份进度表，没有 per-repo JSON 状态机。
- 声明完成的历史范围已检查实际 code changes；commit message/stat 分类不能冒充 learning。
- 每个执行 case 都有 visible START、隔离 baseline replay、真实 outcome comparison、skill decision 和 same-case rerun。
- 只有证明行为改善且相邻回归可接受的最小 delta 被保留；`no_skill_gap` 不制造文件。
- 最终 guidance 在当前 revision 上重新核对，过时历史规则已移除或收窄。
- 每个 repo 记录 branch、commit、PR/MR、验证和 consumability；dirty local delta 或 read-only candidate 不能声称已部署。

## Reconciliation 与 workflow construction

- Company routes 只连接真实存在、可读的 pinned repo-local entries。
- route-scoped boundary 只覆盖该 workflow 需要的 modules、sources 和 repos；剩余范围仍明确 in-progress/deferred。
- starter workflow 已替换客户 source、角色、路由、branch/review/test/release policy，并通过至少一个受控或真实 case后，才从 `draft-template` 改为 `construction-ready`。
- `construction-ready` 不能承接无监督生产任务。

## Formal runtime deployment

- Deployment 只使用 canonical remotes 和 resolved commits，不使用 Host 绝对路径或复制 Host credential home。
- 正式高权限身份的 Git host user/id、Git author、Agent account、credential/rotation owner 可审计。
- Company clone、pilot repo clone、受控 writeback 和 Agent probe 以正式身份通过。
- runtime snapshot 固定 Company commit、workflow 所需 repo commits、repo-local entries、image digests 和 probe 结果。
- container 内 company → repo entry、source access 和必要 build/test command 均实际验证。
- Docker socket未获单独授权时不挂载；若挂载，审计中明确标为 host-root-equivalent。
- 成功后 workflow 进入 `ready-for-shadow`，不是 `active`。

## Shadow 与 active

- `ready-for-shadow` workflow 在客户监督下处理代表性真实任务，并在执行期间使用不可变 snapshot。
- 后台 learning 或 self-improve 只能写新 ref，不直接修改当前 snapshot。
- routing、execution、verification、END 和客户隐藏步骤在代表性任务中闭合后，客户明确批准，workflow 才进入 `active`。
- `active` 记录对应 workflow 和 exact deployment revisions；不宣称整个客户 Jarvis 的全部范围同时 active。

## 客户可见结果

默认只展示 Company repo/PR、repo-local PR/MR 状态、当前可用范围、需审批或授权的事项、真实 blocker 和下一项业务结果。Phase、eval、oracle、cursor、内部 progress 文件和子进程命令不构成客户操作界面。
