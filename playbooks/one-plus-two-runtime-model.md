# One preparation agent + two execution agents

Jarvis 初次构建可能读取大量 repo、文档和历史，不能假设一个交互 session 可以连续完成。运行模型只保留三个角色，不增加调度系统。

这份文件只定义初次构建的并发与写入边界。客户从零到 Jarvis 上岗、再到持续进化的完整内容方法见 `customer-jarvis-growth-loop.md`。

```text
Preparation agent
  ├─ BUILD-CONTEXT.md
  ├─ RUN-COMPANY-JARVIS-CONSTRUCTION.md  ──> Company construction agent
  ├─ RUN-REPOSITORY-LEARNING.md          ──> Repository learning agent
  └─ START-HERE.md
```

## Preparation agent

它负责确认“有哪些构件、在哪里、能否访问、允许怎样写”，以及 company Jarvis 应发布到客户选择的哪个 GitHub/GitLab host 与 namespace，并把这些 observed facts 固化为文件。它不负责回答“这家公司应该有哪些 modules/workflows”，也不负责从历史里学习 repo-local knowledge。

它的成功标准是两个新 Agent 不需要客户重新解释环境，就能从各自任务文件开始工作。

## Company construction agent

它构建一个独立的 customer-owned company Jarvis repo，并在内容验证后发布到 `BUILD-CONTEXT.md` 确认的 GitHub 或 GitLab。它可以读取客户 repo 来理解公司和产品，但不能修改这些 repo，也不能承担 Repository learning。base 中预装的 issue post-check、bugfix 和 feature-delivery skills 只是后续教学与定制草稿，不代表客户 workflow 已完成。

它维护一份普通的 `COMPANY-JARVIS-PROGRESS.md`。文件记录已完成内容、证据 pointer、当前未解决问题和下一动作，不实现通用状态机。

## Repository learning agent

它遍历 `BUILD-CONTEXT.md` 中的全部代码仓库，通过真实历史 episode 改进各 repo 自己的 local skills。它不能修改 company Jarvis repo。

它只维护一份 `REPOSITORY-LEARNING-PROGRESS.md`：

```markdown
| Repository | History range | Status | Last completed episode | Next |
|---|---|---|---|---|
| repo-a | 2025-07-27..2026-07-27 | in-progress | issue-123 | inspect issue-124 |
| repo-b | 2025-07-27..2026-07-27 | pending | - | start discovery |
```

这只是给后续 Agent 阅读的工作日志，不是机器协议：没有 parser、状态迁移规则或 per-repo
状态文件。Agent 可以按现场需要补充文字，只要能看出每个 repo 已做到哪里、证据在哪、下一步
是什么。

当前 episode 的 visible START、hidden oracle pointer、replay result、skill decision 和 rerun 证据写在任务目录的 replay 子目录。表里只放恢复所需的最小 pointer。

repo 再多也不增加状态机；它们只是同一个长任务的工作队列。需要并发时，Repository learning agent 可以自行派发 bounded work，但必须把结果收束回同一份进度文档。

## 恢复

执行 Agent 或机器中断后，客户重新运行同一条命令。新 Agent：

1. 读取自己的 `RUN-*.md`；
2. 读取已有 progress；
3. 验证 progress 中最后一个完成证据仍然存在；
4. 从 `Next` 继续。

runtime/jarvis-box 负责进程、session、日志和 heartbeat；create-jarvis-skill 不复制这些能力。

## 写入边界

| Role | 可写 | 只读 |
|---|---|---|
| Preparation | task directory | authorized artifacts |
| Company construction | company Jarvis target、确认的 customer-owned GitHub/GitLab remote、自己的 progress | customer repos/docs/work systems |
| Repository learning | 经 write policy 允许的 customer repos、自己的 progress/replay workspace | company Jarvis target、docs/work systems |

两个执行 Agent 不共享可变状态，也不互相写对方的产物。company Jarvis 可以按约定路径路由到 repo-local skills，但不复制其内容。

## 1+2 之后

`1+2` 完成时，客户在自己选择的 GitHub/GitLab 上拥有 company Jarvis repo，并在各代码仓库中拥有 repo-local skills。只有 container 本地 company 目录时，1 还没有完成。下一步由 runtime agent 先执行 1+2 reconciliation，把实际 repo-local entry 接回 company routing 并重跑 handoff probes；然后用预装 workflow 草稿向客户讲解闭环，并把它们改造成客户自己的 issue post-check、bugfix、feature-delivery workflow。

workflow 定制必须使用客户真实的角色、事实源、repo 路由、branch/review/test/release policy 和闭合证据。草稿只有在真实 case 上验证后才从 `draft-template` 改为 `active`，再进入 shadow delivery；到现场任务证明其稳定闭环时，Jarvis 数字员工才真正具备上岗条件。这里不增加调度器或 workflow 状态服务。
