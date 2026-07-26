# Phase 4 - 证据优先的信息接收

目标：runtime agent 合并用户直接提供的事实、runtime allowlist facts 和当前授权环境中可发现的事实，生成或校验 adaptation manifest。不要先把客户挡在一份自己也不知道如何填写的长表单前。

Phase 4 只做信息接收、发现计划和 truth/approval 边界；不生成正式 modules。

## 人必须确认的最小输入

- company identity，或对 agent 发现的冲突候选作确认；
- 允许读取的 source/repo 范围以及缺失访问所需的凭据/授权；
- 任何远端建仓、push、MR/PR、业务系统写回的批准策略；
- 当证据支持多个真实候选时，对 first workflow / rollout scope 的业务选择。

slug、本地 target、扫描顺序、repo role candidates、source routes、default branch 等可从 live evidence 得到或可逆 local-only 推导的内容，不作为首轮问题。推导值必须带 provenance/status，在不可逆写入前再确认冲突。

## Owner

- runtime agent 使用 create-jarvis-skill 主动发现和归一化。
- 客户 operator 只补不可从授权环境取得的权限、身份和审批决策。
- truth-bearing owner 确认冲突或不可逆外部写入。

## 步骤

1. 读取 Phase 3 capability/ownership 结果和已有 state。
2. 读取以下 allowlist env；只读非 secret 值，不 dump 全量 env：
   `JARVIS_COMPANY_SLUG`、`JARVIS_COMPANY_NAME`、`JARVIS_CONFIRMED_PRODUCT_IDENTITY`、`JARVIS_TARGET_HOME`、`JARVIS_HOME`、`JARVIS_ENTRY_SKILL`、`JARVIS_BOX_HOME`、`JARVIS_RUNTIME_ROOT`、`JARVIS_WORKSPACE_ROOT`、`JARVIS_SOURCE_OF_TRUTH`、`JARVIS_FIRST_LOOP`、`JARVIS_SOURCE_SCOPE`、`JARVIS_WORKFLOW_SCOPE`、`JARVIS_MODULE_HINTS`、`JARVIS_GITLAB_HOST`、`JARVIS_GITLAB_PROJECTS`、`JARVIS_RAW_SOURCE_POLICY`。
3. 归一化路径和公司身份：
   - runtime/operator 已提供 slug 时逐字使用；
   - 只有 company name 时可生成 deterministic slug candidate，标 `derived-needs-conflict-check`；
   - company identity、confirmed product identity、source-detected product/brand identity 分开记录。
4. 建立授权 source/repo inventory。先从 existing checkouts、remotes、provider metadata、docs navigation、issues/MRs、tests 和 CI 发现 repo/source scope、owner hints、default branch 与访问状态；不要从当前登录用户名猜客户 owner 或 namespace。
5. 从高信号 artifact 提出 first workflow candidates：真实 trigger、business outcome、success signal、涉及 repo/source 和 explicit non-scope。只有候选冲突或业务优先级无法由证据确定时才请 operator 选择。
6. 发现 VCS publication 能力和目标候选。默认 writeback 为 `human-approved`；没有明确批准时允许继续生成 local-only calibration output，但禁止创建远端、push 或写业务系统。
7. 对 operator/env 已确认的 scope 保留原值：
   - `JARVIS_SOURCE_SCOPE` → `sources/<source>/README.md` route names；
   - `JARVIS_MODULE_HINTS` → `modules/<module>/` names；
   - `JARVIS_WORKFLOW_SCOPE` → `<slot>-workflow-<name>` names。
   Agent 后续只能补证据和状态，不能无声改名、改大小写、合并或翻译。
8. 生成或校验 adaptation manifest，分别记录 `confirmed`、`observed`、`derived`、`unresolved`、`conflicting`、`approval-required`。
9. 初始化 identity reconciliation、company repository publication candidate 和 pilot repo writeback plan。secret 只记录 available/missing。
10. 把无法自行回答的问题压缩成最小问题集：写清已经搜索的证据、为什么仍不能推导、谁能确认，以及不回答时采用的安全停点。

## 输出

- normalized context 和 adaptation manifest；
- source/repo inventory 与 discovery plan；
- identity reconciliation draft；
- first workflow candidates 或 confirmed first workflow；
- local-only / remote publication policy；
- 最小 unresolved/approval question list。

## 状态规则

- 可以在不越权的 local-only 范围继续发现：`completed`，把不可逆写入审批留给对应 writeback gate。
- first workflow 必需访问、身份冲突或业务选择无法安全确定：`needs-input`。
- 路径冲突、state 损坏或授权边界不清：`blocked` / `failed`。

## 禁止

- 不要求客户预先填写所有 module、repo role、owner、branch、visibility 和 workflow 字段。
- 不从公司名猜业务 modules。
- 不覆盖 runtime/operator 已确认的 slug 或 scope 名称。
- 不把 source-detected brand 当作已确认 company identity。
- 不从登录用户、本地目录名或 repo 名猜 namespace、owner 或写入权限。
- 不因远端发布尚未批准而阻塞安全的 local-only discovery；也不把 local-only 产物伪装成已交付远端。
