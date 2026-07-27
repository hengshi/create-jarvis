# Create Jarvis 验收标准

验收分为 Preparation、Company Jarvis construction 和 Repository learning 三个角色。一个角色的完成不能用来冒充另一个角色完成。

## Preparation 完成

- 在 agent-owned workspace 中生成 `BUILD-CONTEXT.md`、两个 `RUN-*.md` 和 `START-HERE.md`。
- inventory 覆盖所有已授权 repo、文档和工作系统，并记录准确 pointer、live access、revision、dirty state 和 write policy。
- `BUILD-CONTEXT.md` 记录客户确认的 GitHub/GitLab provider、host、owner/namespace、`<company-slug>-jarvis` repo、visibility、default branch、远端存在状态、访问/创建权限与发布方式；不因 CLI 存在或当前登录账号而猜测。
- 两个任务文件包含实际绝对路径，不包含凭据、源码/文档 dump 或未解析占位符。
- `START-HERE.md` 有两条适配现场已登录 agent 的可执行命令；它们分别启动新的 Company construction 与 Repository learning agent。
- Preparation agent 写完后停止，没有偷偷开始任一长任务。

## Company Jarvis construction 完成

- 产物是客户自己的独立 company Jarvis repo，而不是知识 dump 或 repo-local skill 集合。
- 验证后的产物已发布到 `BUILD-CONTEXT.md` 确认的客户 GitHub/GitLab repo；只有本地目录不能标记完成。
- `BUILD-CONTEXT.md` 声明的每个 artifact root、source 和 repo 都有 coverage 状态；每个 candidate capability 都有 include/merge/defer/reject disposition。
- 有明确的 company entry、公司/产品身份边界和 module/source/repo routing。
- 每个 included software module 都有产品锚点、实际读取过的实现锚点和 first proof/verification contract；repo/path 或 commit message 本身不能冒充业务证据。
- known issues、decisions、rejected features 和 test coverage 只写有 authority 的可复用事实；没有证据时允许保持明确空状态。
- repo fleet 区分 capability authority、execution owner、delivery、docs/operational 和 verification surfaces，不使用“主仓/次仓”代替关系。
- cross-cutting 只保存稳定因果边、false owner、first proof 与 repo-local next hop，不复制仓库 implementation truth。
- 至少用真实产品问题、defect 线索和跨 capability 变更线索验证 company entry routing；失败 route 修正后已重跑。
- 三套预装 workflow 明确保持 `draft-template`；Company construction 不把母版冒充客户已验证 workflow。
- 所有客户事实都能回指 `BUILD-CONTEXT.md` 中的授权构件；不知道的事实保持 unresolved。
- 客户代码仓库未被该 Agent 修改。
- 全新或确认无历史的远端有可达的初始默认分支和 commit；已有历史的远端没有被覆盖或 force-push，而是在基于默认分支的独立 branch 上提交并创建 PR/MR。
- 若客户 policy 要求 review，PR/MR 未合并前状态是 `ready-for-review`，不能声称 canonical default branch 已交付；Agent 不自动合并。
- company repo 不包含 `jarvis.toml`、construction state files 或 runtime-owned 通用 skills 的副本。
- `COMPANY-JARVIS-PROGRESS.md` 足以让另一个 Agent 验证最后证据并继续，并记录 provider、remote URL、branch、commit、PR/MR（如有）和远端验证结果，但不记录凭据。

不能用固定运行时长、固定 Agent 数、几个示例 module、所有模板文件非空或结构 verifier PASS 代替上述语义覆盖。

## Repository learning 完成

- `BUILD-CONTEXT.md` 中每个 repo 都在同一份进度表中有明确状态；没有 per-repo JSON 状态机。
- 声明为 `completed` 的 repo 已扫描到声明历史范围边界；阻塞 repo 写明已搜索范围和恢复动作。
- 历史范围可以是一年、两年、全部可达历史或自定义日期/ref；范围内 commit 有实际 code-change 检查证据，不能只用 message/stat 分类冒充 learning。
- 每个执行过的 case 都是从原始问题到真实 outcome 的完整 episode，START 没有泄漏事后答案。
- baseline replay 实际执行，外层 comparison 在 skill decision 之前完成。
- 每个保留的 skill delta 都有 same-case 改善证据；无可复用缺口时正确记录 `no_skill_gap`。
- 默认按 oldest-to-newest 累积学习，并在范围结束后用当前 revision 重新核对架构、路径、命令、构建和测试，未把过时历史规则留进最终 skill。
- repo-local delta 只写入所属代码仓库，不复制到 company Jarvis，不生成 `eval-loop` skill。
- 未经批准不覆盖 dirty worktree、不 push、不建 branch/MR。

## Workflow onboarding 完成

- 1+2 reconciliation 已把 company routing 中的 pending repo handoff 替换为真实可解析的 repo-local entry，或明确保留 blocked；company → repo-local probes 已重跑。
- Agent 已用预装草稿向客户讲清 issue post-check、bugfix、feature-delivery 的 START → WORK → VERIFY → END。
- 每个激活的 workflow 已替换通用假设，使用客户真实 source、角色、company route、repo-local skill、branch/review/test/release policy。
- 至少用一个客户真实或等价受控 case 验证 route、handoff、执行和 closure；未验证的 workflow 继续保持 `draft-template`。
- 只有满足上述条件的 skill 才改为 `active`。workflow 文件存在或 `1+2` 完成都不能单独宣称数字员工已上岗。

## Shadow delivery 完成

- 已激活候选 workflow 在多个代表性客户任务中完成 route、execution、verification 和 END closure。
- 客户不再需要口头补充关键隐藏步骤；若仍需补充，事实已写回正确 primary home 并重跑。
- Agent 完成声明与客户验收证据一致；未验证范围保持明确。
- 通过数量不按固定天数或固定 task count 判断，而由客户任务类型覆盖与剩余风险决定。

## 整体边界

- jarvis-box/container 负责 agent、Git、`gh`、`glab`、权限、进程、session、heartbeat 和日志；method pack 不复制这些能力。
- 三个角色只写各自允许的目录。
- 客户只需要看到任务目录、两条启动命令、结果和真正的 blocker，不需要学习内部方法名。
- 不使用 `jarvis.toml`、`bootstrap-state.json` 或 `bootstrap-result.json` 作为当前生态的必备合同。
