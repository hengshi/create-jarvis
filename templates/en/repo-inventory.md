# Repo Inventory

| Repo | Role in the first workflow | Owners | Default branch | Runtime / entrypoints | Validation / test entrypoints | Repo-local skill path or gap | Truth that must stay repo-local | Central JARVIS routing summary | Priority | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `<repo>` | `<role>` | `<owners>` | `<branch>` | `<dev/run/build>` | `<test/lint/check>` | `<skill/path/gap>` | `<commands/paths/local rules>` | `<routing summary>` | `<high/medium/low>` | `<notes>` |

## Notes

- Record the repo’s role, not just its name.
- If the real source of truth lives in the repo, route toward a repo-local skill.
- Keep low-level repo details out of central JARVIS unless there is a strong reason.
- Central JARVIS should keep the routing summary; the repo skill should keep execution truth.
