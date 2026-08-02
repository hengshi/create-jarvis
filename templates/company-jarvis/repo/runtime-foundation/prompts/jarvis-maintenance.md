# Company Jarvis Maintenance

维护当前 Company Jarvis，不要临时发明新的运维脚本或规则。

1. 先阅读仓库根目录的 `AGENTS.md`、`MAINTENANCE.md`、`README.md` 和它们引用的正式 skills。
2. 只读取 `MAINTENANCE.md` 授权的数据源，只修改其授权的产物。
3. 发现需要持久化的改进时，按仓库既有 GitHub/GitLab 交付规则创建或更新 PR/MR；不要强制合并，不要绕过 review gate。
4. 已有维护 PR/MR 时优先继续闭环，不要重复创建。
5. 没有可靠证据时不修改；记录 `NO_CHANGES` 是有效结果。
6. 不得修改 Jarvis Box 的 Task/Run/Workspace state，不得把客户 Runtime Foundation 伪装成 Jarvis Box 内建能力。
