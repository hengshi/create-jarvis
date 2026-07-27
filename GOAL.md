# create-jarvis-skill 目标

目标是在客户自己的 runtime agent、授权材料和代码仓库上，交付两个不同但能协作的长期资产：

1. 客户独立拥有、发布在其选择的 GitHub 或 GitLab 上的 company Jarvis repo；
2. 与各代码仓库共同演进的 repo-local skills。

## 为什么是 1 + 2

客户的文档、代码仓库和历史可能很大，一个交互 Agent 不应同时承担准备、公司级构建和全部仓库学习。

- Preparation agent 只确认构件、权限、写入边界和远端发布目标，写出两个任务文件与两条命令。
- Company Jarvis construction agent 构建公司级入口、语义和路由，预装待客户定制的 workflow 草稿，并把验证后的 repo 发布到客户确认的 GitHub/GitLab 命名空间。
- Repository learning agent 从各 repo 的真实历史 episode 中学习可复用的本地执行知识。

三个角色通过普通 Markdown 文件交接。runtime 负责 session 和进程；create-jarvis-skill 不实现另一套调度或 JSON phase 状态机。

`1 + 2` 之后不是把成长责任丢给客户。method pack 继续引导 1+2 reconciliation、客户 workflow construction、真实任务 shadow delivery 和 evidence-driven evolution。完整步骤见 `playbooks/customer-jarvis-growth-loop.md`。

## 两种产物的所有权

Company Jarvis 保存：

- 公司和产品语义；
- module、source、repo role 与入口路由；
- 从通用草稿出发、经客户定制和真实案例验证的跨 repo、跨角色 workflow；
- repo-local skill 的位置和使用条件。

客户代码 repo 保存：

- 本仓库的架构、边界、构建和测试真相；
- 从真实失败中验证过的 repo-specific 约束；
- 必要的 focused references 和确定性脚本。

Company Jarvis 不复制 repo execution truth，repo-local skills 不承担公司级路由。

## Repository learning 的本质

学习单位是完整、可重放的真实工作 episode，不是单个 commit，也不是 commit message 分类。

对每个 episode 执行：visible START → isolated baseline replay → hidden outcome comparison → `no_skill_gap` / minimal skill update → same-case rerun → adjacent regression。

只有证明 Agent 行为改善的 delta 才保留。eval loop 是构建方法，不是最终 skill。

客户可以指定 Repository learning 覆盖最近一年、两年、全部可达历史或自定义日期/ref。所谓覆盖不是读取 commit message：Agent 必须检查实际 code changes，并把相关 commits 还原到完整 bugfix/feature episode 中。

## 数字员工上岗

`1+2` 结束只代表 company 语义/路由和 repo execution knowledge 已经具备。随后 Agent 先把真实 repo-local entries 接回 company routing，再用预装的 issue post-check、bugfix、feature-delivery 草稿向客户讲解和共同定制 workflow。只有这些 workflow 使用客户真实 source、角色、repo skills 和交付规则，并在 shadow delivery 中通过真实 case 验证后，Jarvis 数字员工才算正式上岗。

## 客户体验

第一天客户只需要完成 runtime agent、所选 GitHub/GitLab 的登录和必要授权。Preparation agent 写好任务包后，客户启动两个长任务；小项目可以当天完成，大项目可以运行过夜。客户不需要理解 Phase、cursor、oracle、eval 或内部 verifier。
