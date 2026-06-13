# Repo Inventory

| Repo | Role in the first workflow | Owners | Default branch | Runtime / 入口点 | Validation / test 入口点 | Repo-local skill path or gap | Truth that must stay repo-local | Central JARVIS routing summary | Priority | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `<repo>` | `<role>` | `<owners>` | `<branch>` | `<dev/run/build>` | `<test/lint/check>` | `<skill/path/gap>` | `<commands/paths/local rules>` | `<routing summary>` | `<high/medium/low>` | `<notes>` |

## Notes

- 记录 repo 的业务角色，而不只是名字。
- 如果真实 权威来源 在 repo 中，就把人路由到 repo-local skill。
- 除非有充分理由，否则不要把低层 repo 细节放进中心 JARVIS。
- central JARVIS 保留 routing summary；repo skill 保留 execution truth。
