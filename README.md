# Create JARVIS Skill

`create-jarvis-skill` 是客户直接交给已登录 Codex、Claude 或其他 runtime agent 使用的说明书和模板库。

jarvis-box install 或受支持的 Docker / Apple container 的目标合同，是把环境准备成可运行 agent 的 runtime：agent CLI、Git/VCS 工具、方法入口、明确且可写的 workspace，以及正确的 UID/GID 或 volume mapping。客户只完成 agent 的一次性登录。当前 image 缺少任一项时，Phase 3/5 报告 exact capability blocker，不能假装已经预装。本仓库不负责服务、凭证、webhook、日志或任务队列，但会验证这些前置能力，避免把安装权限缺陷留给客户处理。

本仓库只负责一件事：让当前 runtime agent 直接按 `playbooks/phase-checklist.md` 从 Phase 3 到 Phase 14 执行，生成客户自己的 `<slot>-jarvis` repo、repo-local skills、skill packages、试点计划、历史回放校准和受控写回路径。它不依赖一份 bootstrap CLI 表单，也不要求客户在多个 agent session 之间搬运 prompt。

## 直接开始

在已登录且能访问客户授权材料的 runtime agent 中，粘贴 `playbooks/prompts/agent-native-bootstrap.md` 的短 prompt；可选地追加公司名和 repo/docs URL。agent 应先自行发现可观测事实，只就授权、身份冲突、凭据和不可逆写入审批向人提问。

针对已有 repo-local skills 的历史压实，使用 `playbooks/prompts/history-calibration.md`。该 prompt 明确把 eval loop 定义为逐 commit 组的控制循环，长期产物是实际 skill delta，不是一个新建的 eval-loop skill。

## Runtime Agent 读取顺序

1. `GOAL.md`
2. `SKILL.md`
3. `acceptance.md`
4. `playbooks/phase-checklist.md`
5. 当前 phase 详情：`playbooks/phases/phase-*.md`
6. 需要执行专门任务时读取 `playbooks/prompts/`
7. 需要生成文件时读取 `templates/`

## 目录职责

```text
create-jarvis-skill/
├── GOAL.md                 # 长期目标：生成客户自己的 company Jarvis 生态
├── SKILL.md                # runtime agent 入口
├── acceptance.md           # 唯一验收标准
├── playbooks/
│   ├── phase-checklist.md  # 主说明书，Phase 3-14
│   ├── phases/             # 每个 phase 的细节
│   └── prompts/            # agent-native 入口与历史校准 prompt
├── templates/              # 模板素材
│   ├── company-jarvis/     # company JARVIS 仓库母版（repo/module/source/artifacts）
│   ├── repo-local-skill/   # repo-local skill canonical package 母版
│   ├── skill-packages/     # 默认方法/workflow 母版与通用扩展母版
│   └── replay/             # history replay 产物模板
├── scripts/                # 确定性实例化与验证脚本（Phase 7/8/9）
│   ├── instantiate_company_jarvis.py   # Phase 7/9: base/module/source/package 子命令
│   ├── instantiate_repo_local_skill.py # Phase 8: repo-local skill 渲染
│   └── verify_bootstrap_output.py      # Phase 7/8/9: 输出验证
├── evals/                  # eval case，不是 runtime agent 主路径
└── e2e/                    # e2e runbook，不是 runtime agent 主路径
```

## Phase 7/8/9 确定性脚本

Phase 7（company JARVIS repo）使用 `instantiate_company_jarvis.py`：

```bash
python3 scripts/instantiate_company_jarvis.py base --state <bootstrap-state.json>
python3 scripts/instantiate_company_jarvis.py module --state <...> --name <模块名>
python3 scripts/instantiate_company_jarvis.py source --state <...> --name <source名>
python3 scripts/instantiate_company_jarvis.py package --state <...> \
  --kind <generic-source|generic-workflow> --name <slot前缀技能名>
```

`base` 同时创建根目录 `bootstrap-state.json`、`bootstrap-result.json`、
`_bootstrap/jarvis-build-brief.md`，并安装以下默认 skills：

```text
ponytail
writing-durable-docs
jarvis-self-improve-skill
stop-slop
<slot>-workflow-issue-post-check
<slot>-workflow-bugfix-loop
<slot>-workflow-feature-delivery
```

运行状态保持为当前 state 的状态；未进入的后续 phase 初始化为 `pending`。重复运行会
保留 runtime agent 或操作员已经修改过的文件。

Phase 8（repo-local skills）使用 `instantiate_repo_local_skill.py`：

```bash
python3 scripts/instantiate_repo_local_skill.py --repo <repo路径>
```

Phase 9 结合客户证据定制三个默认 workflow。额外的 company source/tool skill 必须命名为
`<slot>-<name>`，额外 workflow 必须命名为 `<slot>-workflow-<name>`，并通过 `package`
子命令从 `generic-source` 或 `generic-workflow` 母版创建。

所有输出通过 `verify_bootstrap_output.py` 做确定性机器检查：

```bash
python3 scripts/verify_bootstrap_output.py --jarvis-home <目标目录> --repo <repo路径>
```

## 唯一成功标准

产物必须是客户自己的 company Jarvis repo，角色和生态形态等价于 `hengshi-jarvis`：

- 有公司级入口 skill；
- Git 仓库和公司入口 skill 均命名为 `<slot>-jarvis`；
- 默认四个通用方法 skill 和三个 `<slot>-workflow-*` 母版存在；
- 有 company identity、confirmed product identity、source-detected identity 的清楚边界；
- 有从客户证据中提炼出的产品/业务 module 拓扑；
- 有 `sources/`、`references/jarvis-first-routing.md`、workflow skills 和 repo-local handoff 路由；
- 有 first workflow 的 START → WORK → VERIFY → END；
- 有 pilot repo-local skills 或明确 blocker；
- 有 owner、缺口、writeback policy；
- Phase 11-14 有可执行产物路径：shadow pilot、history replay、controlled writeback、day-2 operation。

机器检查通过不等于 bootstrap 完成。如果输出不像客户自己的 company Jarvis 生态，就继续补 `playbooks/phase-checklist.md` 和对应 phase 文件。

## 验证

开发本仓库时可以运行：

```bash
python3 scripts/run_create_jarvis_skill_eval.py \
  --cases evals/cases \
  --outputs eval-fixtures/create-jarvis-skill \
  --report .eval-runs/ci-report
```

这只做机器防呆，不替代 `acceptance.md`。
