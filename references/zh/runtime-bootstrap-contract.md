# Runtime Bootstrap 契约

当 jarvis-box 或其他 runtime 通过 agent 调用 create-jarvis-skill 时，使用这份契约。

## 边界

create-jarvis-skill 不是 runtime operating system。

它不负责 runtime install scripts、system services、credentials、webhooks、task queues、PATH setup、scheduler setup、workspace clone logic 或 process lifecycle。这些属于 jarvis-box 或调用方 runtime。

create-jarvis-skill 负责：
- 企业 JARVIS 方法论；
- scaffold generation；
- pilot workflow shaping；
- source/repo/workflow skill boundaries；
- confirmation gates；
- writeback 与 calibration contracts。

## 输入与路径语义

- `JARVIS_TARGET_HOME`：本次 bootstrap 写入目标。
- `JARVIS_HOME`：生成实例引用的 canonical root。
- 如果两者都存在，realpath 后必须一致，否则停止并返回 `path-conflict`。
- `JARVIS_BOX_HOME` 只是 runtime host root，不能当作客户实例 root。
- `CREATE_JARVIS_SKILL_REPO_URL` 默认是 `https://github.com/hengshi/create-jarvis-skill.git`。
- `CREATE_JARVIS_SKILL_REPO_REF` 是请求的 method repo ref。
- `JARVIS_NONINTERACTIVE=1` 时禁止追问，缺必填输入必须写入机器可读结果。

## Secret 边界

不要读取、打印、持久化 secret value。只能记录 secret name / purpose、configured 状态、safe path/provider、unresolved access blocker。

## 最小输出

目标 home 应包含：
- `SKILL.md` 或配置的 entry skill；
- `README.md`；
- `MAINTENANCE.md`；
- build brief；
- source/repo/workflow inventories；
- ownership map；
- rollout plan；
- confirmation checklist；
- `bootstrap-state.json`；
- `bootstrap-result.json`。

## `bootstrap-state.json`

它是 resume anchor，至少包含：
- `schema_version`、`phase`、`status`；
- `paths.jarvis_home`、`paths.jarvis_target_home`、`paths.jarvis_box_home`、`paths.entry_skill`；
- 不含 secret 的 normalized inputs；
- confirmed answers / unresolved questions；
- generated files / scaffold-owned files / preserved user files；
- method repo url / requested ref / resolved commit；
- writeback policy、noninteractive、secrets boundary、updated_at。

resume 时保留 confirmed answers 和 user-authored files。只有 scaffold-owned 或被明确批准的文件可以刷新。

## `bootstrap-result.json`

它是 runtime terminal verdict，至少包含：
- `schema_version`
- `status`: `completed | needs-input | blocked | failed`
- `result_code`
- `summary`
- paths
- method repo
- created / updated / preserved files
- unresolved questions
- blockers
- writeback policy
- next action
- generated_at

即使被 block，只要有安全目标或 runtime 提供的结果路径，也应尽量产出这个文件。

## 错误码

常用 `result_code`：
- `ok`
- `missing-target-home`
- `target-not-writable`
- `path-conflict`
- `missing-company-name`
- `missing-first-loop`
- `missing-owners`
- `missing-source-scope`
- `noninteractive-missing-input`
- `secret-boundary-violation`
- `invalid-entry-skill`
- `resume-state-corrupt`

每个失败都应包含 retryable、missing inputs、conflicting inputs、blockers 和 next action。
