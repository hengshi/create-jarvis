# Phase 11 — 影子试跑

目标：用真实 artifact 验证第一条 workflow 的端到端可用性——company entry → module/workflow/source → repo-local handoff 是否能正确路由，VERIFY 和 END 是否能诚实闭合。它不是 history replay，不负责隐藏未来 patch 或让 agent 重现历史修复。

产物必须让下一个 agent 能复盘：开始时看到了什么、JARVIS 如何路由、实际做了什么、怎么验证、END 时为什么写回或不写回。

## 前置条件

- Phase 10 已完成 onboarding report。
- identity reconciliation 不阻止试跑；如果仍有冲突，owner 明确允许以 shadow mode 继续。
- 至少一个真实 artifact 可用（当前 issue/request/alert/doc task，或历史 artifact fallback）。artifact 的 source/repo access 已确认，或 blocker 已写清楚。
- shadow mode 边界已确认：不做生产写回、不修改真实业务数据、不代表 owner 作最终决策。

## Artifact 获取

runtime agent 应主动从已授权来源寻找真实 artifact，不能只等人整理，也不能编造。

### 当前 artifact 优先

优先使用当前存在的真实任务：issue、ticket、support case、MR、commit、告警、产品请求或文档请求。artifact 必须真实，属于 first workflow，并为本次 pilot 定义可检查的路由、查证或交付成功信号。

### 历史 artifact fallback

如果当前没有可直接使用的 artifact，runtime agent 必须从 pilot repo 的真实 Git 历史中选取可解释的 commit / MR pointer 作为 `historical-shadow` artifact，至少完成一次 company Jarvis routing dry-run。记录实际搜索范围（命令、时间或提交边界）、选中理由和停止理由。

`historical-shadow` 不等于 Phase 12 history replay：

- Phase 11 只验证 company entry skill 是否能面对真实 artifact 做出合理路由、repo-local handoff、VERIFY 选择和 END 判断。
- Phase 11 不隐藏最终 diff，不评估 agent 是否能重新发现修复；这些属于 Phase 12。
- historical-shadow 按本次 pilot 实际取得的 artifact 形态执行；完整 commit/MR 的 metadata 和 diff 可以作为可见输入。需要切回修复前状态并隐藏这些内容时，停止 Phase 11 路径，转入 Phase 12 构造 replay case。
- historical fallback 可以做 route-only/draft pilot，并明确它只能证明 routing/readability，不能证明重新发现修复或产品行为。

只有客户未提供 artifact、pilot repo 也没有可用 Git 历史或 commit 无法安全摘要时，Phase 11 才能写 `needs-input`。

“没有可用 Git 历史”必须有搜索证据：不能只运行一次 `git log -3/-5/-N`。跳过 fixture、housekeeping 或无法解释的候选后，继续扩大同一 repo 的范围并检查其他 pilot repos。只有所有授权 pilot repos 都记录了实际命令、搜索边界、候选排除理由和停止理由，才允许得出无 artifact 结论。

## 固定产物

每个 artifact 使用稳定 id，例如 `pilot-YYYYMMDD-001`：

```text
_bootstrap/shadow-pilot/
├── pilot-registry.md
└── <pilot-id>/
    ├── shadow-pilot-run.md
    └── pilot-evidence.md
```

使用模板：

- `templates/company-jarvis/artifacts/pilot-registry.md`
- `templates/company-jarvis/artifacts/shadow-pilot-run.md`
- `templates/company-jarvis/artifacts/pilot-evidence.md`

## 执行步骤

### 1. 创建 registry

创建或更新 `_bootstrap/shadow-pilot/pilot-registry.md`，记录每个 pilot 的基本信息：artifact 来源、选中理由、状态。

### 2. 获取 artifact

读取客户提供的 artifact；如果没有，扫描 pilot repo Git 历史并选择 `historical-shadow` artifact。记录实际搜索范围、选中理由和排除理由。

如果当前是从 Phase 10 进入，不能先把 Phase 11 写成 `needs-input` 再建议未来运行 `git log`；这些搜索命令就是本 phase 当前必须执行的工作。

### 3. 创建 run 文件

为 artifact 创建 `_bootstrap/shadow-pilot/<pilot-id>/shadow-pilot-run.md`。shadow pilot 分离四个 section：

- **PILOT INPUT / START**：artifact 按本次 pilot 实际拿到的形态呈现，同时记录允许 sources/repos、禁止范围和成功标准。若给的是完整 commit/MR，其 diff 就是输入的一部分；若要隐藏 outcome、重放 cutoff 前任务，应转 Phase 12。
- **ROUTE/WORK/VERIFICATION Plan**：当前 skill 路由选择、work 计划、verification 方法。
- **Observed Execution**：实际执行中观察到的行为、输出、结果。**不得从文件存在声称 PASS**——只有实际运行命令并捕获输出后才能记录 `PASS` 或 `FAIL`。未实际执行的验证必须记录为 `not-run`。
- **END / Pilot Evaluation**：按本次 success signal 判断 routing、handoff、验证和闭合。若 owner 或历史 outcome 提供了期望 route，可在这里对照；Phase 11 不构造 hidden oracle。

### 4. 填写 START

按上述 START 约束填写，artifact 按"本次 pilot 实际拿到的形态"呈现。

### 5. 路由（ROUTE）

从 company entry skill 开始：

- 记录读取了哪些 entrypoint；
- 记录选择的 module、workflow、source、repo-local skill；
- 记录为什么没有选择其他明显候选。

### 6. 执行 WORK

- source 查证只记录 pointer / summary，不复制原文；
- repo 工作进入 repo-local skill；
- 需要修改时，只在受控工作副本或 draft artifact 中操作；
- 需要生产写回时停下，等待 owner approval。

### 7. 执行 VERIFY

- 优先运行 repo-local `precheck.sh`；
- 运行 artifact 所需的最小 test/lint/dry-run；
- 无法运行时记录 blocked reason 和 owner/action；
- owner review 作为有效 verification，但必须记录 reviewer role 和其实际审查内容。

### 8. 闭合（END）

- 分类 outcome：`useful`、`partial`、`blocked`、`missed`；
- 分类 failure mode；
- 判断 `no_skill_gap`；
- 判断 writeback home；
- 更新 `_bootstrap/shadow-pilot/<pilot-id>/pilot-evidence.md`。

### 9. jarvis-box Task 记录（可选）

只有实际通过 jarvis-box Task 执行 shadow pilot 时才记录 pointer，并遵守五个 lifecycle operations：Start Task、Continue With Agent、Stop Run、Recover Lost Run、Retry Writeback。普通 agent 对话不编造 Task/Run ID。

如果 shadow pilot 由 bootstrap agent 直接在受控副本 dry-run（不走 jarvis-box Task），不要求记录上述操作。

### 10. 治理更新

`no_skill_gap` / writeback decision 写进 pilot evidence。只有治理规则本身变化时才更新 `references/writeback-governance.md`，不要每次 pilot 都修改它。

### 11. 状态同步

更新 `_bootstrap/rollout-confirmation-checklist.md` 和 `bootstrap-state.json`。

## 输出

- `_bootstrap/shadow-pilot/pilot-registry.md`
- `_bootstrap/shadow-pilot/<pilot-id>/shadow-pilot-run.md`
- `_bootstrap/shadow-pilot/<pilot-id>/pilot-evidence.md`
- 如通过 Task 执行，pilot evidence 中包含 Target/Task/Run/Workspace pointer（可选）。
- `bootstrap-result.json` 或 onboarding report 中的 next action。

## 状态判定

- `completed`：至少一个真实 artifact 完成 START → ROUTE/WORK → VERIFY → END，并有 pilot evidence、failure/no_skill_gap/writeback decision。dry-run/precheck 没有运行 product-level verification 时，结果必须明确为 partial/not-verified；只能陈述实际观察到的 routing 维度，不能宣称 module/repo/workflow skills 全部无 gap。
  - dry-run 只能证明路由/可读性，不能证明产品行为或所有 skills 无 gap。
  - 如果 pilot 暴露了空的 repo-local/source/module 指导（来自 Phase 6-9），必须先修复所属 phase 的产出并重新运行 pilot，再完成 Phase 11。
- `needs-input`：缺本次 pilot 必须由 owner 提供的 success signal 或允许范围；或已授权来源中找不到可用真实 artifact。
- `blocked`：缺 source/repo 权限、生产审批、安全边界或 runtime capability。
- `failed`：执行中发生不安全写入、secret 泄露、artifact/source 损坏，或把 invented example 写成真实 pilot。

## 停止条件

- 客户未提供 artifact，且 pilot repo Git 历史也无法选出可用 `historical-shadow` artifact。
- workflow 只能靠 invented example 演示。
- 试跑需要生产 mutation，但 owner 未批准。
- access 缺失导致无法完成 START 或 VERIFY。
- runtime 问题被错误写进 create-jarvis-skill 方法论。
- 因缺 Task ID 而把一个有真实 artifact、完整 START-WORK-VERIFY-END 的受控 shadow pilot 判失败。

## 读物

- `GOAL.md`
- `acceptance.md`
- `playbooks/phase-checklist.md`
- `templates/company-jarvis/artifacts/pilot-registry.md`
- `templates/company-jarvis/artifacts/shadow-pilot-run.md`
- `templates/company-jarvis/artifacts/pilot-evidence.md`
