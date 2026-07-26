---
name: create-jarvis-skill
description: Agent-native instruction set for building or continuing a customer-owned company Jarvis repo after jarvis-box or a supported container has prepared the runtime. Use when a customer asks an authenticated Codex, Claude, or other runtime agent to discover the authorized company ecosystem, create company/repo-local skills, run pilot/history calibration, or resume from bootstrap state.
---

# Create JARVIS Skill

jarvis-box install 或受支持的 container 应已经准备好 runtime、可写 workspace 和 agent CLI；客户完成所选 agent 的登录。本 skill 不负责安装，但 Phase 3/5 必须验证这些能力和 UID/GID 权限合同，不能把安装缺口当成客户操作问题。

本 skill 的任务只有一个：当前 runtime agent 直接按 `playbooks/phase-checklist.md` 从 Phase 3 到 Phase 14 逐项执行，生成客户自己的 company Jarvis 生态。入口 prompt 见 `playbooks/prompts/agent-native-bootstrap.md`；不需要 bootstrap 表单命令。

## 必读顺序

1. `GOAL.md`
2. `acceptance.md`
3. `playbooks/phase-checklist.md`
4. 当前 phase 详情：`playbooks/phases/phase-*.md`
5. 需要执行专门任务时读取 `playbooks/prompts/`
6. 需要生成文件时读取 `templates/`

## 模板分类

| 模板 | 用途 |
|---|---|
| `templates/company-jarvis/` | company JARVIS 仓库母版（repo/module/source/artifacts） |
| `templates/repo-local-skill/` | repo-local skill canonical package 母版 |
| `templates/skill-packages/` | 默认方法/workflow 母版与通用扩展母版 |
| `templates/replay/` | history replay 产物模板 |

## Phase 7/8/9 确定性脚本

- **Phase 7**：`scripts/instantiate_company_jarvis.py base/module/source --state <bootstrap-state.json>`；`base` 同时安装默认四个方法 skill 和三个 slot 化 workflow 母版
- **Phase 8**：`scripts/instantiate_repo_local_skill.py --repo <repo路径>`
- **Phase 9**：定制默认 workflow；额外能力使用 `package --kind <generic-source|generic-workflow> --name <slot前缀技能名>`
- **验证**：`scripts/verify_bootstrap_output.py --jarvis-home <目标目录>`

## 执行规则

- 从 Phase 3 开始；Phase 0-2 属于 jarvis-box/install image，不在本仓库重复实现。Phase 3 由客户已经打开的 runtime agent 直接进入，不等待另一层 CLI handoff。
- 当前 agent 是 bootstrap 协调者。需要并发时自行派发 bounded lanes；并发不可用时顺序执行并通过 state 恢复，禁止要求客户新开 session、复制 prompt 或转发 agent 结果。
- 先探测 live runtime、授权 source 和 VCS metadata，再询问无法安全推导的身份冲突、权限和不可逆写入审批。不要把所有 phase 字段变成首轮表单。
- bootstrap workspace、customer checkout 和 target 必须对 selected agent 的有效 UID/GID 可读写；service-private state 与 agent-owned workspace 分离。权限不成立时把 exact blocker 归给 jarvis-box install/image，禁止用盲目提权或 world-writable 目录掩盖。
- 每次按 checklist 推进，当前 phase 在执行/checkpoint 中写 `in-progress`，收口时写 `completed`、`needs-input`、`blocked` 或 `failed`；显式 full-range history 未到 cursor 边界时不能伪装成终态。
- 先从授权 repo/source、Git/VCS metadata、文档、issues/MRs、测试与运行证据中寻找答案；只有可访问证据已穷尽后，才为仍缺失的客户事实、权限、owner、scope 或 writeback policy 向人请求输入。
- company identity、客户确认的 product identity、source-detected product/brand identity 必须分开记录；未确认前不要混写成一个已确认主体。
- 业务 modules 必须来自客户授权的 docs、repos、tests、issues/MRs、wiki 或 owner 确认。
- 不把 `backend`、`frontend`、`api`、`database`、`infra` 这类工程层当作主要业务 module。
- repo execution truth 留在 repo-local skills；company Jarvis 只做入口、路由、workflow 编排和 writeback 判断。
- repo-local skill 复用已有内容时也必须补齐 canonical package 固定文件；`precheck.sh` 必须自包含，不能依赖 reference company 或操作员机器的私有路径、脚本和维护命令。
- source skill 只写访问、路由、引用和边界，不复制 source 原文。
- company Jarvis repo 必须采用 `hengshi-jarvis` 形态：`modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`、`evals/`；不要创建顶层 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 作为主结构。
- 已由客户/operator 确认的 module/source 名称必须逐字节保留为目录名，包括大小写；例如 `HQL` 必须是 `modules/HQL/`，不能被 agent 改成 `modules/hql/`。workflow 的 `<name>` 部分保持原样，并按公司命名合同生成 `<slot>-workflow-<name>`。
- Git 仓库名和 company entry skill 均为 `<slot>-jarvis`；entry 的 canonical 位置是 `skills/<slot>-jarvis/SKILL.md`。
- 通用方法 skill 固定为 `ponytail`、`writing-durable-docs`、`jarvis-self-improve-skill`、`stop-slop`，不加 slot 前缀。
- 默认客户工作流固定为 `<slot>-workflow-issue-post-check`、`<slot>-workflow-bugfix-loop`、`<slot>-workflow-feature-delivery`，Phase 9 必须依据客户事实完成初次定制。
- company 自有 source/tool skill 命名为 `<slot>-<name>`；repo-local skills 留在各代码仓库，不加 slot 前缀。
- skill 扩展前先判断 `no_skill_gap`。
- Phase 12 历史回放不能默认等待人工 episode；pilot repo 有 Git 历史时，必须用轻量 cursor 逐组执行 `commit group → eval case → replay → oracle comparison → skill-creator decision → same-case rerun`。不得先把整个时间范围全量分类，也不得创建 eval-loop skill。没有 isolated replay agent 只阻塞 replay 执行，不阻塞 case 文件创建。候选清单不是合格产物；有候选但没有 `evals/history-replay/cases/<case-id>/history-replay-case.md` 时，Phase 12 是执行失败，不是合格 `needs-input`。
- `bootstrap-result.json` 只报告 runtime 状态、路径、缺口和下一步，不输出复杂分层字段；其中 `missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions` 必须是字符串数组。
- `bootstrap-result.json.paths` 只能是 string map，不能包含数组或对象；多个文件路径写入 `created_files` 字符串数组或 report 文件。
- `bootstrap-result.json` 和 `bootstrap-state.json` 必须写在 company Jarvis repo 根目录，`_bootstrap/` 只能保存审计副本和过程证据。

## 完成标准

`completed` 只允许在产物满足 `acceptance.md` 时写出。最低要求：

- company Jarvis repo 有有效 company entry skill；
- company entry skill 位于 `skills/<slot>-jarvis/SKILL.md`，并且仓库骨架接近 `hengshi-jarvis`；
- 默认四个通用方法 skill 和三个 slot 化 workflow 均存在；
- company identity、confirmed product identity、source-detected identity 的边界清楚；
- company entry 能把真实 artifact 路由到 module、workflow、source 或 repo-local skill；
- 有证据驱动的客户产品/业务 module 拓扑；
- first workflow 有 START → WORK → VERIFY → END；
- pilot repos 有 repo-local skill package 或明确 blocker；
- `sources/`、`references/jarvis-first-routing.md`、workflow skills 和 repo-local handoff 有 role、owner、状态、证据和缺口；
- 影子试跑、历史回放、受控写回和第二天运营有固定产物路径，或明确写出 `needs-input` / blocker；
- 没有 secret、私有 reference company 事实、raw source dump。

如果产物不像客户自己的 company Jarvis 生态，不要写 `completed`；返回 `needs-input`、`blocked` 或 `failed`，并说明需要补哪一个 phase/checklist 项。
