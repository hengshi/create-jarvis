# Create Jarvis 验收标准

## 一句话入口与恢复

- 在没有 jarvis-box 的 Host 上，客户只给已授权 Agent canonical GitHub URL 和建设请求即可开始。
- Agent clone canonical repo、固定 method commit 并从本地读取方法；客户不 curl、不安装 Skill、不运行 phase 或子任务命令。
- 新 journey 从模板创建完整 `jarvis-build/`：`CONTINUE-JARVIS.md`、`CONSTRUCTION-JOURNAL.md`、`BUILD-CONTEXT.md`、各部分/per-repo work cards 和 `evidence/`。
- 恢复时使用 recorded method commit，核验实际文件、Git/remote、PR/MR 和 runtime state 后从 card 的 last verified checkpoint/`Next` 继续。
- 旧 writer 存活时重连，已结束才替换；ownership 不明时阻止重复 writer。session handle 不是事实真值。
- 没有子 Agent 时 Coordinator 顺序执行 cards，不虚假承诺后台存活、heartbeat 或上下文隔离。

## Preparation

- Agent 明确不扫描电脑，再引导客户提供公司身份、repo、文档和工作系统 pointer；一个 pilot scope 即可启动。
- inventory 只覆盖明确提供的 URL/路径，记录 pointer、revision、access 和 write/delivery policy。
- Git provider、host、namespace、Company repo、visibility、default branch 和 publication mode 有现场证据；歧义只问最小问题。
- 每个代码 repo 有独立 card，绑定 history range、target workspace/branch、writer 和 delivery policy。
- Construction Workspace 不包含凭据、source dump、`jarvis.toml` 或 bootstrap JSON 状态机。

## Part 1 — Company repo initialization

- Company Jarvis 从模板初始化，不伪造 customer modules、repo roles、runtime paths 或 policies。
- 骨架包含 company entry、modules/sources/cross-cutting/skills/references/tools、starter workflows、repo fleet 和 `runtime-governance*`。
- deterministic verifier 通过，且未渲染 token、凭据、Host-only construction paths 和其他客户事实不存在。
- 新/空远端有可达 commit；已有远端保留历史并通过 branch + PR/MR 交付。
- Part 1 的本地与 remote ref 验证后，Parts 2/3 才进入 ready。

## Part 2 — Company construction

- 授权范围中的 capability/source/repo 都有 evidence-backed disposition。
- included capability 有产品锚点、实现锚点和 first proof/verification contract。
- Company entry 能从真实 artifact 路由到 module/source/repo next hop；cross-cutting 不复制实现真相。
- `runtime-governance.md` 明确是客户跨 Host/managed runtime 宪法，不是 jarvis-box runbook。
- runtime root、cache/workspace/state roles、task-start sync、stable tools、isolation、handoff、cleanup、credential/write boundaries 来自客户事实，不复制 HENGSHI 路径。
- Host runtime 的 discovery/write scope 由客户明确提供并记录；Agent 不用建设目标反向授权扫描 home 或旧 runtime residue。
- 每项 obligation 有 `unresolved/documented/implemented/verified/pending-runtime-foundation` 状态和 evidence。
- 宪法需要的 Host tools/sync mechanisms 已创建、安装、运行验证，或明确 `pending-runtime-foundation`；不能只交文档。
- starter workflows 保持 `draft-template`；Company changes 按客户 Git policy 形成可消费 ref。

## Part 3 — Repository learning

- 每个 repo 有独立 card 和一个 writer；不同 repo 可并行，同一 repo 不并发写。
- 声明完成的 history range 已检查实际 code changes；commit message/stat 分类不能冒充 learning。
- 每个执行 case 有 visible START、隔离 baseline replay、真实 outcome comparison、skill decision 和 same-case rerun。
- 只有证明行为改善且相邻回归可接受的最小 delta 被保留；`no_skill_gap` 不制造文件。
- 最终 guidance 在当前 revision 核对，过时历史规则已移除或收窄。
- 每个 repo 记录 branch、commit、PR/MR、验证和 consumability；dirty local delta 或 read-only candidate 不能声称已部署。

## Reconciliation Gate

- Company 和 workflow 所需 repo-local remote refs 都真实可解析。
- pending handoff 只在真实 entry 存在时替换；Company 保存 `what/why/where first`，repo-local 保存 `how`。
- Company → module/source → repo-local routing probes 在 pinned revisions 上通过。
- route-scoped boundary 只覆盖 workflow 所需范围，剩余 repo/history 仍明确未完成。
- workflow 使用客户真实 source、roles、branch/review/test/release/acceptance policy，并通过至少一个受控或真实 `START → WORK → VERIFY → END` case 后才是 `construction-ready`。

## Part 4 — jarvis-box installation and onboarding

- Part 4 只在 Reconciliation Gate 和至少一个 `construction-ready` workflow 可复验后开始。
- 客户只选择 Native 或 Docker；其余安装和运维步骤来自已校验 jarvis-box public release contract，不依赖私有源码。
- Native 使用安装者当前 OS 用户；Docker 从当前 Host 用户自动导入批准的可移植认证。Dedicated machine account 是可选策略，不是部署前置条件。
- work card 记录实际 deployment mode、runtime owner/root、release version、Docker image digest（适用时）和 connector boundary，不预设客户路径。
- selected environment 中的 Agent discovery、source、provider ingress、Task/Run、workspace、writeback 和 cleanup probes 实际通过。
- Host HOME、SSH agent、Keychain、完整 credential store 和 token 不进入 runtime evidence 或客户仓库。
- Docker socket 未单独授权时不挂载；若挂载，审计中明确 host-root-equivalent。
- 安装观察到的客户级稳定事实可回写 Company runtime governance；jarvis-box execution contract、control plane 和 operator runbook 不复制。
- 成功后 workflow 是 `ready-for-shadow`，不是 `active`。

## Shadow 与 active

- `ready-for-shadow` workflow 在客户监督下处理代表性真实任务，并使用不可变 snapshot。
- learning/self-improve 只写新 ref，不直接改变当前 snapshot。
- routing、execution、verification、END 和隐藏客户步骤稳定闭合且客户批准后，workflow 才进入 `active`。
- `active` 记录对应 workflow 与 exact deployment revisions，不宣称整个客户范围同时 active。

## 客户可见结果

默认只展示 Company repo/PR、repo-local PR/MR、当前可用范围、runtime-foundation 缺口、需审批或授权事项、真实 blocker、Construction Workspace recovery phrase 和下一项业务结果。内部 replay/oracle、card schema 和 provider child-process 命令不构成客户界面。
