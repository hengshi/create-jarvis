# Phase 4 - Bootstrap 信息接收

目标：runtime agent 读取 Phase 3 的交接上下文，补齐最小安全输入，并生成或校验 adaptation manifest。

Phase 4 只做信息接收、归一化和 manifest。它不做业务扫描，不生成 modules，不创建 company Jarvis repo。

## Owner

- runtime agent 使用 create-jarvis-skill。
- 客户 operator 提供缺失操作信息。
- 客户 owner 确认 truth-bearing 字段。

## 必填输入

- company name。
- company slug 或 slug 推导规则。
- 客户确认的 company identity 和 product/scope identity；如果客户尚未确认产品身份，必须记录为 unresolved。
- `JARVIS_TARGET_HOME` / `JARVIS_HOME`。
- first workflow。
- pilot repo/source scope。
- owner 或 escalation path。
- writeback policy。
- company Jarvis 远端仓库归属：VCS host、namespace/group、目标项目路径 `<namespace>/<slot>-jarvis`、可见性、default branch、建仓权限和首次发布审批方式。

## 步骤

1. 读取 Phase 3 handoff context。
2. 立即读取 runtime allowlist env，只读取这些非 secret 字段，不 dump 全量 env：
   ```bash
   printf 'JARVIS_COMPANY_SLUG=%s\n' "${JARVIS_COMPANY_SLUG:-}"
   printf 'JARVIS_COMPANY_NAME=%s\n' "${JARVIS_COMPANY_NAME:-}"
   printf 'JARVIS_CONFIRMED_PRODUCT_IDENTITY=%s\n' "${JARVIS_CONFIRMED_PRODUCT_IDENTITY:-}"
   printf 'JARVIS_TARGET_HOME=%s\n' "${JARVIS_TARGET_HOME:-}"
   printf 'JARVIS_HOME=%s\n' "${JARVIS_HOME:-}"
   printf 'JARVIS_ENTRY_SKILL=%s\n' "${JARVIS_ENTRY_SKILL:-}"
   printf 'JARVIS_BOX_HOME=%s\n' "${JARVIS_BOX_HOME:-}"
   printf 'JARVIS_RUNTIME_ROOT=%s\n' "${JARVIS_RUNTIME_ROOT:-}"
   printf 'JARVIS_SOURCE_OF_TRUTH=%s\n' "${JARVIS_SOURCE_OF_TRUTH:-}"
   printf 'JARVIS_FIRST_LOOP=%s\n' "${JARVIS_FIRST_LOOP:-}"
   printf 'JARVIS_SOURCE_SCOPE=%s\n' "${JARVIS_SOURCE_SCOPE:-}"
   printf 'JARVIS_WORKFLOW_SCOPE=%s\n' "${JARVIS_WORKFLOW_SCOPE:-}"
   printf 'JARVIS_MODULE_HINTS=%s\n' "${JARVIS_MODULE_HINTS:-}"
   printf 'JARVIS_GITLAB_HOST=%s\n' "${JARVIS_GITLAB_HOST:-}"
   printf 'JARVIS_GITLAB_PROJECTS=%s\n' "${JARVIS_GITLAB_PROJECTS:-}"
   printf 'JARVIS_RAW_SOURCE_POLICY=%s\n' "${JARVIS_RAW_SOURCE_POLICY:-}"
   ```
   这些 env 是 runtime confirmed inputs，优先级高于从 company name 或 repo 内容推导的值。
3. 标准化路径：`JARVIS_TARGET_HOME`、`JARVIS_HOME`、`JARVIS_ENTRY_SKILL`、`JARVIS_BOX_HOME`、`JARVIS_RUNTIME_ROOT`。
4. 标准化公司身份：company name、slug、primary language、timezone、deployment environment。
   - 如果 Phase 3 / runtime env / jarvis-box handoff 已提供 `company_slug` 或 `JARVIS_COMPANY_SLUG`，它就是 confirmed slug；必须逐字使用，不能从 company name 重新推导，不能缩短成第一个词，不能把 `acme-claude-e2e` 改成 `acme`。
   - company entry skill 必须使用 confirmed slug：`skills/<company_slug>-jarvis/SKILL.md`。
   - `jarvis.toml`、`bootstrap-state.json`、`bootstrap-result.json.paths.entry_skill` 中的 slug 必须一致。
5. 标准化客户确认的 product/scope identity：产品名、业务线、当前 rollout 覆盖范围。如果 `JARVIS_CONFIRMED_PRODUCT_IDENTITY` 存在，它就是客户确认事实；不能把同名 source-detected identity 再写成 unresolved。如果客户只给了 company name，不要从 repo 名或源码命名空间猜 product identity。
6. 标准化 first workflow：trigger、business outcome、success signal、pilot scope、explicit non-scope。
7. 标准化 owners：bootstrap owner、workflow owner、pilot repo owner、source owner、approval/security owner。
8. 标准化 sources/repos：VCS、issues/tickets、docs/wiki、support/customer sources、pilot repos、excluded sources/repos。
   - 如果 `JARVIS_SOURCE_SCOPE` 存在，逐项记录为 confirmed source scope facts；这些值默认就是目标 `sources/<source>/README.md` 路由名，Phase 6 只能补证据和访问状态，不能无声省略或泛化改名。
   - 如果 `JARVIS_MODULE_HINTS` 存在，逐项记录为 confirmed module facts；这些值默认就是目标 `modules/<module>/` 目录名，Phase 6 必须给每项一个 coverage decision，不能无声省略、泛化改名或改大小写。
   - 如果 `JARVIS_WORKFLOW_SCOPE` 存在，逐项记录为 confirmed workflow 的 `<name>`；Phase 9 必须逐字节保留并映射到 `skills/<slot>-workflow-<name>/SKILL.md`。三个 starter workflows 无条件存在，额外 workflow 不能无声省略、合并或泛化改名。
9. 标准化 writeback policy：disabled、local-only、human-approved、repo/docs writeback 或 custom approval。
10. 标准化 company Jarvis 远端仓库策略：
    - 仓库名固定为 `<confirmed-company-slug>-jarvis`，不得使用泛化的 `company-jarvis`；
    - 记录 VCS host、namespace/group、完整 project path、remote URL、可见性和 default branch；
    - 记录远端是由 runtime agent 创建、由客户预先创建，还是需要 owner 执行；
    - 记录空仓库首次 seed 是否允许直接推送 default branch；不允许时记录 bootstrap branch 和 MR/PR 审批方式；
    - 记录 repo-local skills 对每个 pilot repo 的写入方式：disabled、local-only、直接提交、branch + MR/PR 或 custom approval。
11. 生成或校验 adaptation manifest，记录 confirmed、unresolved、missing、conflicting fields。
12. 初始化 identity reconciliation：company identity、confirmed product identity、source-detected identity candidates、conflicts。
13. 将仓库归属和发布策略写入 `bootstrap-state.json` 的 `company_repository` 与 pilot repo writeback 记录，再更新 `bootstrap-result.json`。secret 只记录 available/missing，不记录值。

## 输出

- normalized context；
- adaptation manifest draft 或 validated manifest；
- missing input list；
- conflict list；
- identity reconciliation draft；
- company repository publication plan；
- pilot repo writeback plan；
- initial status。

## 状态规则

- 所有必填输入存在且不冲突：`completed`。
- 交互模式缺输入：`needs-input`，列出要问谁、问什么、为什么需要。
- 非交互模式缺输入：`needs-input` + `result_code: noninteractive-missing-input`。
- 路径冲突或 state 损坏：`failed` 或 `blocked`，在 `bootstrap-result.json` 写明。

## 禁止

- 不从公司名猜业务 modules。
- 不覆盖 runtime 已确认的 company slug。
- 不在 `JARVIS_COMPANY_SLUG` 存在时自行派生 slug。
- 不把源码、包名、README 中出现的 product/brand 直接当作客户 company identity。
- 不从 repo 名猜 owner。
- 不因为客户暂时不知道所有 source 就扩大 scope。
- 不把“缺字段”当作失败；它是正常信息接收结果。
- 不从 GitLab 登录用户或本地 checkout 猜 namespace、可见性、default branch 或发布权限。
- 不因本地目录名已经是 `<slot>-jarvis` 就声称客户远端仓库已建立。
