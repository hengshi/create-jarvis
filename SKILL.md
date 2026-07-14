---
name: create-jarvis-skill
description: Runtime agent instruction set for bootstrapping a customer-owned company Jarvis repo after jarvis-box install is complete. Use when `jarvis-box bootstrap jarvis` asks an agent to create or update company Jarvis, repo-local skills, skill packages, pilot/replay/writeback plans, or related bootstrap state.
---

# Create JARVIS Skill

jarvis-box install 已经完成机器安装和 agent 登录准备。本 skill 不负责安装。

本 skill 的任务只有一个：runtime agent 按 `playbooks/phase-checklist.md` 从 Phase 3 到 Phase 14 逐项执行，生成客户自己的 company Jarvis 生态。

## 必读顺序

1. `GOAL.md`
2. `acceptance.md`
3. `playbooks/phase-checklist.md`
4. 当前 phase 详情：`playbooks/phases/phase-*.md`
5. 需要生成文件时读取 `templates/`

## 模板分类

| 模板 | 用途 |
|---|---|
| `templates/company-jarvis/` | company JARVIS 仓库母版（repo/module/source/artifacts） |
| `templates/repo-local-skill/` | repo-local skill canonical package 母版 |
| `templates/skill-packages/` | 12 种 skill package 母版 |
| `templates/replay/` | history replay 产物模板 |

## Phase 7/8/9 确定性脚本

- **Phase 7**：`scripts/instantiate_company_jarvis.py base/module/source --state <bootstrap-state.json>`
- **Phase 8**：`scripts/instantiate_repo_local_skill.py --repo <repo路径>`
- **Phase 9**：`scripts/instantiate_company_jarvis.py package --kind <包类型> --name <技能名>`
- **验证**：`scripts/verify_bootstrap_output.py --jarvis-home <目标目录>`

## 执行规则

- 从 Phase 3 开始；Phase 0-2 属于 jarvis-box install，不在本仓库重复描述。
- 每次按 checklist 推进，当前 phase 必须写出 `completed`、`needs-input`、`blocked` 或 `failed`。
- 先从授权 repo/source、Git/VCS metadata、文档、issues/MRs、测试与运行证据中寻找答案；只有可访问证据已穷尽后，才为仍缺失的客户事实、权限、owner、scope 或 writeback policy 向人请求输入。
- company identity、客户确认的 product identity、source-detected product/brand identity 必须分开记录；未确认前不要混写成一个已确认主体。
- 业务 modules 必须来自客户授权的 docs、repos、tests、issues/MRs、wiki 或 owner 确认。
- 不把 `backend`、`frontend`、`api`、`database`、`infra` 这类工程层当作主要业务 module。
- repo execution truth 留在 repo-local skills；company Jarvis 只做入口、路由、workflow 编排和 writeback 判断。
- repo-local skill 复用已有内容时也必须补齐 canonical package 固定文件；`precheck.sh` 必须自包含，不能依赖 reference company 或操作员机器的私有路径、脚本和维护命令。
- source skill 只写访问、路由、引用和边界，不复制 source 原文。
- company Jarvis repo 必须采用 `hengshi-jarvis` 形态：`modules/`、`sources/`、`cross-cutting/`、`references/`、`skills/`、`tools/`、`evals/`；不要创建顶层 `repos/`、`workflows/`、`pilot/`、`writeback/`、`rollout/`、`scheduled-jobs/` 作为主结构。
- 已由客户/operator 确认的 module/source/workflow 名称必须逐字节保留为目录名，包括大小写；例如 `HQL` 必须是 `modules/HQL/`，不能被 agent 改成 `modules/hql/`。
- company entry skill 的 canonical 位置是 `skills/<company>-jarvis/SKILL.md`。
- skill 扩展前先判断 `no_skill_gap`。
- Phase 12 历史回放不能默认等待人工 episode；pilot repo 有 Git 历史时，必须先自动扫描 commits、读取候选 diff，并构造 visible START / hidden oracle 分离的 replay case。没有 isolated replay agent 只阻塞 replay 执行，不阻塞 case 文件创建。候选清单不是合格产物；有候选但没有 `evals/history-replay/cases/<case-id>/history-replay-case.md` 时，Phase 12 是执行失败，不是合格 `needs-input`。
- `bootstrap-result.json` 只报告 runtime 状态、路径、缺口和下一步，不输出复杂分层字段；其中 `missing_inputs`、`blockers`、`conflicting_inputs`、`unresolved_questions` 必须是字符串数组。
- `bootstrap-result.json.paths` 只能是 string map，不能包含数组或对象；多个文件路径写入 `created_files` 字符串数组或 report 文件。
- `bootstrap-result.json` 和 `bootstrap-state.json` 必须写在 company Jarvis repo 根目录，`_bootstrap/` 只能保存审计副本和过程证据。

## 完成标准

`completed` 只允许在产物满足 `acceptance.md` 时写出。最低要求：

- company Jarvis repo 有有效 company entry skill；
- company entry skill 位于 `skills/<company>-jarvis/SKILL.md`，并且仓库骨架接近 `hengshi-jarvis`；
- company identity、confirmed product identity、source-detected identity 的边界清楚；
- company entry 能把真实 artifact 路由到 module、workflow、source 或 repo-local skill；
- 有证据驱动的客户产品/业务 module 拓扑；
- first workflow 有 START → WORK → VERIFY → END；
- pilot repos 有 repo-local skill package 或明确 blocker；
- `sources/`、`references/jarvis-first-routing.md`、workflow skills 和 repo-local handoff 有 role、owner、状态、证据和缺口；
- 影子试跑、历史回放、受控写回和第二天运营有固定产物路径，或明确写出 `needs-input` / blocker；
- 没有 secret、私有 reference company 事实、raw source dump。

如果产物不像客户自己的 company Jarvis 生态，不要写 `completed`；返回 `needs-input`、`blocked` 或 `failed`，并说明需要补哪一个 phase/checklist 项。
