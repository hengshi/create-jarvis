---
name: create-jarvis-skill
description: Prepare, construct, publish, activate, and evolve a customer-owned Jarvis with the customer's authenticated runtime agent. Use when a customer wants to inventory authorized company artifacts, build and publish a company Jarvis repo to customer-selected GitHub or GitLab, learn repo-local skills from real repository history, reconcile company and repo knowledge, customize workflows, or improve Jarvis from real delivery evidence. The default entry prepares two independent long-running construction tasks; it does not run the whole build in one session.
---

# Create JARVIS Skill

本 skill 使用一个极简的 `1 + 2` 运行模型：

1. 当前客户 runtime agent 只负责准备：检查环境、收集已授权构件的路径与访问状态，并写出两个自包含任务文件。
2. Company Jarvis construction agent 读取其中一份任务，构建并发布客户自己的 company Jarvis repo，并安装三套待客户定制的 workflow 草稿。
3. Repository learning agent 读取另一份任务，逐个进入客户代码仓库，通过真实历史 episode 的 eval loop 生成或改进 repo-local skills。

这三个角色不能混成一个长会话。准备 Agent 写完任务包和两条启动命令后就停止；两个执行 Agent 可以分别运行数小时或过夜。

`1 + 2` 是初次构建的并发方式，不是完整成熟路径。完整路径是：Preparation → Company construction + Repository learning → 1+2 reconciliation → Workflow construction → Shadow delivery → Active Jarvis → 持续进化。进入任一角色前先读 `playbooks/customer-jarvis-growth-loop.md` 中对应步骤。

## 先判断当前角色

- 客户说“为我们构建 Jarvis”，且当前目录没有专门的 `RUN-*.md` 任务：进入 **Preparation**。
- 当前请求明确要求读取 `RUN-COMPANY-JARVIS-CONSTRUCTION.md`：只执行 **Company Jarvis construction**。
- 当前请求明确要求读取 `RUN-REPOSITORY-LEARNING.md`：只执行 **Repository learning**。
- 客户要求讲解、定制或启用 bugfix/feature workflow，且 company Jarvis 与 repo-local skills 已存在：进入 **Workflow onboarding**。
- 客户正在用已定制 workflow 处理真实任务，或要求继续提升已上岗 Jarvis：进入 **Shadow delivery / Evidence-driven evolution**。

不要因为看到了两个任务文件就在同一个 Agent 中顺序执行它们。

## Preparation

按以下顺序读取：

1. `playbooks/customer-jarvis-growth-loop.md`
2. `playbooks/one-plus-two-runtime-model.md`
3. `playbooks/runtime-method-contract.md`
4. `playbooks/prompts/preparation.md`

Preparation 只做浅层、可验证的构件盘点，不做深度业务提炼或历史学习。它在 agent-owned workspace 中创建：

```text
jarvis-build/
├── BUILD-CONTEXT.md
├── RUN-COMPANY-JARVIS-CONSTRUCTION.md
├── RUN-REPOSITORY-LEARNING.md
└── START-HERE.md
```

`BUILD-CONTEXT.md` 必须同时记录客户选择的 GitHub/GitLab、host、owner/namespace、`<company-slug>-jarvis` repo、visibility、default branch、远端是否已存在、当前授权与发布方式。客户未明确说出平台时，只能在现场证据唯一时自动确定；GitHub/GitLab 或 namespace 有歧义就问一个最小问题，不能凭当前登录账号猜。

`START-HERE.md` 必须包含适配当前已登录 agent 的两条可直接执行命令，不能保留路径占位符。最终只把这两个命令、任务目录和确有必要的发布 blocker 告诉客户。

不创建 `bootstrap-state.json`、`bootstrap-result.json` 或 `jarvis.toml`。进程、session、heartbeat 和 retry 由 runtime/jarvis-box 负责。

## Company Jarvis construction

只读取：

1. `BUILD-CONTEXT.md`
2. `RUN-COMPANY-JARVIS-CONSTRUCTION.md`
3. `playbooks/customer-jarvis-growth-loop.md`
4. `playbooks/prompts/company-jarvis-construction.md`
5. Company construction 明确引用的模板与 playbook

它只写 company Jarvis target、客户确认的 GitHub/GitLab company repo、任务目录中的 `COMPANY-JARVIS-PROGRESS.md` 和确有并发扫描需要的 task-local evidence packet，把客户代码仓库视为只读证据。它不能顺手创建或修改 repo-local skills。

Company construction 对 `BUILD-CONTEXT.md` 声明的授权范围持续做 capability/source/repo coverage：从产品证据建立 taxonomy，对每个 candidate 做 include/merge/defer/reject，对 included capability 闭合产品、实现与验证证据，再建立 source routes、repo fleet、capability surfaces、cross-cutting 和 company entry。它不能用固定运行时长或几个示例 module 提前结束，也不能用 Repository learning 的 eval loop 替代公司级语义构建。

完成结构与语义验证后才发布。全新或确认为空的远端可以建立初始历史并推送默认分支；已有历史的远端必须保留历史，在独立分支提交并创建 GitHub PR 或 GitLab MR，不能 force-push、覆盖或自动合并。只有本地目录不算 Company construction 完成；等待客户 review 时应明确标为 `ready-for-review`，不能冒充已经进入默认分支。

预装的 issue post-check、bugfix 和 feature-delivery workflow 是 `draft-template`，只用于后续向客户讲解和共同改造。它们没有经过客户真实流程验证前，不能作为已经可上岗的 workflow。

## Repository learning

只读取：

1. `BUILD-CONTEXT.md`
2. `RUN-REPOSITORY-LEARNING.md`
3. `playbooks/customer-jarvis-growth-loop.md`
4. `playbooks/prompts/repository-learning.md`
5. 当前 episode 需要的 `templates/replay/`

它只写客户代码仓库中经 eval loop 验证的 repo-local skill delta，以及任务目录里的 `REPOSITORY-LEARNING-PROGRESS.md` 和 replay 证据。它不能修改 company Jarvis repo。

一个 Repository learning agent 可以处理任意数量的 repo。所有 repo 共用一个进度文档；每个 repo 只是其中一行和必要的当前 episode 记录，不建立 per-repo 状态机。

历史范围由客户选择，可以是最近一年、最近两年、全部可达历史或自定义日期/ref。Agent 必须遍历该范围并读取 commit 的实际 code changes；commit message 只能用于导航，不能代表已经理解 bugfix/feature。

## 1+2 完成后：Workflow onboarding

当 company Jarvis 与 Repository learning 都完成或达到客户同意的可用边界后，先执行 **1+2 reconciliation**：读取两份 progress 和每个 repo 的真实 repo-local entry，把 company routing 中的 `pending Repository learning` 替换为可解析 pointer，并重跑 company → repo-local routing probes。然后使用预装 workflow 草稿向客户讲解闭环，并结合客户真实的 issue/source、角色分工、repo-local skills、测试、review、发布与验收方式逐项改造。

只有 workflow 已替换模板假设、能路由到真实 company/repo 入口，并在客户真实 bugfix/feature case 上通过验证后，才能把正文状态从 `draft-template` 改为 `active`。这是 Jarvis 数字员工正式上岗的门槛，不是 `1+2` 的隐藏子步骤。

开始 onboarding 时先读 company Jarvis、`COMPANY-JARVIS-PROGRESS.md`、`REPOSITORY-LEARNING-PROGRESS.md` 和各 repo 最终 skill delta。若任一必要 route/repo skill 仍 blocked，可以继续讲解和记录客户事实，但不能激活依赖它的 workflow。通过对话引导客户确认，不生成第三套状态机或固定问卷。

## Shadow delivery 与持续进化

workflow 通过首个客户 case 后进入 shadow delivery，不因状态改成 `active` 就停止方法指导。按 `playbooks/customer-jarvis-growth-loop.md` 使用后续真实任务持续检查 routing、repo-local execution、verification、END 和客户口头补充；缺口写回唯一正确的 primary home 后重跑原 case 或相邻 case。

稳定运行后，每次任务只在出现可复用且可验证的增量时更新 Jarvis。company capability/route、cross-cutting、source、repo-local skill 和 workflow 各自维护自己的事实；当前任务证据不直接升级成 durable rule。现有资产已足够时记录 `no_skill_gap`，不为了“持续进化”制造文件。

## 不可协商边界

- `BUILD-CONTEXT.md` 保存构件指针、访问状态、当前 revision 和写入策略，不复制代码、文档正文或凭据。
- repo execution truth 留在对应代码仓库；company Jarvis 只保存公司级入口、语义、路由，以及从草稿定制并验证过的跨 repo workflow。
- 预装 workflow 必须保持 `draft-template`，直到客户定制和真实案例验证完成；文件存在不等于可投入生产。
- eval loop 是 Repository learning 的内部方法，不生成 `eval-loop` skill，也不向客户讲解。
- commits 用于发现和还原 episode；commit message 分类不是 eval loop。
- 只有 same-case replay 证明改善后才保留 skill delta；没有可复用缺口时记录 `no_skill_gap`。
- 不覆盖客户未提交改动，不越过 `BUILD-CONTEXT.md` 记录的 write policy。
- Company Jarvis 的正式交付必须发布到客户确认的 GitHub 或 GitLab；不能根据安装了哪个 CLI、当前登录账号或现有代码仓库 owner 擅自选择平台与 namespace。
- 新 company repo 默认 private，除非客户明确选择其他 visibility；已有远端必须保留历史并遵守 branch/review policy。
- 需要恢复时，重新执行同一条命令；Agent 先读对应 progress 文件再继续。
