# Create Jarvis

`create-jarvis` 帮已购买 HENGSHI JARVIS 的客户从零建设自己的 Jarvis，并把它交付到 Jarvis Box。客户不需要学习 construction phase、模板命令或容器内部结构。

开始前只需确认当前 GitHub 账号已被邀请加入 `hengshi-jarvis` 组织，并且 `gh auth status` 显示该账号可用。产品方法和运行时仓库均为私有仓库；授权随客户服务有效期管理。

## 客户只需要说一句话

在已经登录并获得授权的 Codex 或 Claude 中发送。Host Agent 直接获取 GitHub 最新代码，记录其 commit 和提交日期时间和提交人：

```text
请用 gh 获取 hengshi/create-jarvis 的最新代码，检出其 commit 和提交日期时间和提交人，读取 SKILL.md，然后帮我构建属于我们公司的 Jarvis。
```

收到请求的 Host Agent 会成为 Construction Coordinator。它只读取客户明确提供的文档、代码仓库和工作系统，不扫描 HOME、历史会话、无关仓库或旧 runtime 猜测客户情况。

## 接下来会发生什么

```text
一句话开始
  → 建立可恢复的 jarvis-build/
  → 建设并发布客户 Company Jarvis
  → 从真实代码变更学习 repo-local skills
  → 对齐 workflow 与交付证据
  → 选择 Native 或 Docker
  → 部署 Jarvis Box
  → 用真实任务进入 shadow
```

客户只在权限、发布目标、部署模式和生产启用前做决定。Coordinator 负责其余步骤和恢复记录。

## 只需要选择一次：Native 还是 Docker

| | Native | Docker |
| --- | --- | --- |
| 适合 | 单机、最少配置、直接使用当前机器 | 隔离、独立持久化、标准化迁移 |
| runtime owner | 发起安装的现有 OS 用户 | 同一现有 OS 用户的数字 UID/GID |
| 认证 | 直接复用当前用户已有认证 | 自动导入当前 Host 用户的必要认证 |
| 客户路径 | 使用现场实际 runtime root | 使用与 `jarvis-build/`、Company Jarvis 源码物理分离的 deployment home；数据在其 `data/` 绑定目录中 |

Dedicated machine account 可以作为客户自己的安全策略，但 create-jarvis 和 Jarvis Box 都不会代建系统用户。两种模式都使用客户选择的现有 OS 用户，也不复制整个 Host HOME、SSH agent、Keychain 或 credential store。

## 中断后怎么继续

客户只需要提供建设工作区：

```text
继续构建我们的 Jarvis。建设工作区是 <path>/jarvis-build。请读取 CONTINUE-JARVIS.md 和 CONSTRUCTION-JOURNAL.md，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。
```

Coordinator 会先核验文件、Git ref、PR/MR 和 runtime 事实，再决定重连还是继续，不会因为换了一次 Agent 会话就重做全部工作。

## 什么算完成

建设完成不等于所有 workflow 自动进入生产。至少需要：

1. Company Jarvis 与所需 repo-local refs 已发布并可解析；
2. 一个客户 workflow 达到 `construction-ready`；
3. 所选 Native/Docker 环境中的 Runtime Foundation doctor 和真实 Agent discovery 通过；
4. 一条真实任务完成 ingress、Task/Run、workspace、Agent、writeback 和 cleanup；
5. pinned method skills 经显式 installer/doctor 进入所选 Agent discovery root，`jarvis-self-improve-skill` 由 fresh Agent 实际发现；
6. 客户批准后才从 `ready-for-shadow` 进入 `shadowing`，稳定后再进入 `active`。

## 给 Coordinator

从本地 `SKILL.md` 开始。只读取当前 route 指定的 playbook，不一次加载整个仓库。`create-jarvis` 拥有建设方法和恢复合同；客户 Jarvis 拥有知识、workflow 和 Runtime Foundation；客户代码仓库拥有 repo-local 执行真相；jarvis-box 拥有 Task/Run、workspace、provider loop、writeback 和 operator contract。

直接使用 GitHub 最新代码；Construction Workspace 必须记录 checkout commit、提交日期时间和提交人，不能依赖浮动分支。

`create-jarvis` 与 Jarvis Box 使用独立版本。完整关系和发布步骤见 [RELEASE.md](RELEASE.md)。
