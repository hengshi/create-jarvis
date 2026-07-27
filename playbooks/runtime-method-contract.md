# Jarvis runtime / method contract

这份合同只划分能力所有权，避免 create-jarvis-skill 变成第二套 runtime。

## Jarvis-box / container 负责

- 安装并暴露客户选择的 Codex、Claude 或其他 agent；
- 安装 create-jarvis-skill、skill-creator 和通用 runtime skills；
- Git、GitHub CLI (`gh`)、GitLab CLI (`glab`)、证书、代理和已批准的 source adapters；
- agent-owned workspace 与正确的 UID/GID、ACL、volume mapping；
- 进程、session、后台运行、日志、heartbeat、retry 和 native resume；
- 必要的隔离 replay 环境。

这些能力应在镜像中默认准备好，不让客户手工修权限、安装 provider CLI 或填写 bootstrap 表单。客户只需登录自己选择的 GitHub 或 GitLab；凭据仍由客户和 agent/source provider 管理，不能写入 method pack 或任务文件。

## Create-jarvis-skill 负责

- Preparation、Company construction、Repository learning 三种角色的指令，以及 `1+2` 后的 workflow onboarding 方法；
- 1+2 reconciliation、shadow delivery 与持续知识进化的方法；
- company Jarvis、repo-local skills 和 replay 所需的模板/方法；
- 从现场证据确认 GitHub/GitLab publication contract，以及验证后创建/发布 company Jarvis remote 的方法；
- 语义边界、写入边界和验收方法。

它不创建 runtime user、不管理 daemon、不实现 task scheduler，也不维护与 runtime 重复的 process state。

## Preparation handoff

Preparation agent 在可写 workspace 中生成四个普通 Markdown 文件：

- `BUILD-CONTEXT.md`
- `RUN-COMPANY-JARVIS-CONSTRUCTION.md`
- `RUN-REPOSITORY-LEARNING.md`
- `START-HERE.md`

它通过 live probe 确认构件可访问、目标可写，并确认客户选择的 GitHub/GitLab provider、host、namespace、repo 与权限，然后把当前 agent 的两条实际启动命令写入 `START-HERE.md`。准备完成后停止。

## 长任务进度

两个执行 Agent 各维护一份自解释 Markdown：

- `COMPANY-JARVIS-PROGRESS.md`
- `REPOSITORY-LEARNING-PROGRESS.md`

Repository learning 的一个进度表覆盖所有 repo。repo 数量不是建立更多状态机的理由。Agent 或机器中断后，重新执行原命令并读取 progress 继续。

不要求 `bootstrap-state.json`、`bootstrap-result.json` 或 `jarvis.toml`。若 jarvis-box 需要展示运行状态，应从它自己的 job/session 状态和最终 Agent 结果读取，而不是让 method pack 发明平行状态机。

## Workflow 草稿与上岗门槛

company base 可以预装 issue post-check、bugfix 和 feature-delivery workflow 草稿，便于 Agent 向客户讲解并共同改造。草稿在 discovery 和正文中必须明确标为 `draft-template`，不能承接生产任务。只有客户特定路由、角色、policy 和验收方式已经写入，并通过真实 case 后才改为 `active`。这是一条内容验收规则，不需要新的 workflow 状态服务。

两个构建任务结束后，runtime agent 还要执行一次内容层 reconciliation：读取两份 progress，把 company route 中的 pending repo-local handoff 替换为实际入口。这不是 jarvis-box 的状态同步协议，也不需要新增 daemon；它是进入 workflow construction 前的一次可验证知识接线。

## 文件系统边界

- service-private state 与 agent-owned workspace 分离；
- Preparation 只写任务目录；
- Company construction 只写 company Jarvis target 和自己的 progress；
- Company construction 只向 `BUILD-CONTEXT.md` 确认的 customer-owned GitHub/GitLab remote 发布；已有历史必须走保护性 branch + PR/MR；
- Repository learning 只按记录的 policy 写客户 repo、自己的 progress 和 replay workspace；
- 开始长任务前以 selected agent 的真实 UID/GID执行 create/read/write/rename probe；失败时报告 exact path、owner/group/mode，由 install/image 修复；
- 不以递归提权、world-writable 或把客户 repo 交给 service user 作为标准方案。

## 客户可见交付

Preparation 只展示任务目录和两条命令。执行 Agent 只展示可用结果、company Jarvis remote/PR/MR、真正 blocker 和恢复方式。Phase、cursor、oracle、baseline、eval 和 verifier 属于内部方法，不是客户操作界面。
