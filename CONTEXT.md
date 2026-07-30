# Ubiquitous Language

| Term | Meaning |
|---|---|
| Jarvis | 一套由客户自行拥有、具有明确知识与运行边界的数字员工能力；边界由客户选择的共同使用范围决定。 |
| Jarvis repo | 某套 Jarvis 的 Git source of truth，保存入口、知识、workflows、runtime governance 与客户特有 Runtime Foundation。 |
| Construction Coordinator | 客户已授权的 Host Runtime Agent 在本次建设旅程中的角色。 |
| Construction Workspace | 保存本次建设 work cards、checkpoint、journal、evidence 与恢复入口的普通文件工作区。 |
| Runtime Environment | Runtime Agent 实际运行和发现 skills 的环境；可以是 native host，也可以是 jarvis-box Docker 容器。 |
| Agent HOME | Runtime Agent 的持久 home；保存身份配置、原生 skill discovery roots 与 Runtime Foundation 数据。 |
| Runtime Foundation | Jarvis repo 为目标 Runtime Environment 提供的 bootstrap、sync、稳定入口、state/log 和调度适配机制。 |
| Runtime Job | `pullall`、sync、maintenance、self-improve 等在当前 Runtime Environment 内直接执行、对 Docker 无感的内部任务。 |
| Scheduler Adapter | 把外部 scheduler 的触发绑定到目标 Runtime Environment 内 Runtime Job 的薄适配层。 |
| Standard Workflow Pack | `create-jarvis` 提供的建设期 workflow starter；经客户事实替换和行为验证后复制进客户 Jarvis，运行时不依赖 `create-jarvis`。 |
| Customer Workflow | 客户 Jarvis 中已经客户化并通过行为证据验证的 workflow 实现。 |
| Workflow Runtime Contract | `jarvis-box` 与 Runtime Agent/Customer Workflow 之间的版本化输入、结果和受控 action 协议；不解释客户业务 outcome。 |
| jarvis-box | 提供 Workflow Runtime Contract、injected Agent execution contract、Task/Run、control plane、持久 runtime mechanics 与 operator runbook/surface 的产品。 |
