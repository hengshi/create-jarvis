# Shadow Pilot Run — {{COMPANY_NAME}} ({{COMPANY_SLUG}})

> 单次真实 artifact 的端到端 shadow pilot 记录。精确对应 Phase 11。一个文件对应一个 pilot run。

## Run Identity

- **Pilot ID**: `<pilot-id>`
- **Workflow**: `<workflow-name>`
- **Source artifact**: `<issue / ticket / MR / commit / alert / doc task / support case>`
- **Artifact mode**: `owner-provided` / `historical-shadow`
- **Run owner**: `<owner or unresolved>`
- **Company JARVIS ref**: `skills/{{COMPANY_SLUG}}-jarvis/SKILL.md`
- **Status**: `draft` / `running` / `blocked` / `completed`
- **Mode**: `shadow`（不生产写回、不修改真实业务数据、不代表 owner 做最终决策）

<!-- 可选：只有实际通过 jarvis-box Task 执行时才记录 -->
<!-- **Task pointer**: <target/task/run> -->

## PILOT INPUT / START

artifact 按本次 pilot 实际拿到的形态呈现。若 artifact 是完整 commit/MR，其 diff 可作为可见输入。

- **Artifact 当前形态**: <本次 pilot 实际看到的 artifact 内容，summary 或 pointer>
- **Allowed sources / repos**: <scope>
- **Excluded sources / repos**: <non-scope>
- **Success signal**: <什么算 useful>
- **Known unknowns**:
  - <unknown>
- **若为 historical-shadow**: 记录实际搜索范围（命令、时间或提交边界）、选中理由、停止理由。

> 若 artifact 的完整 commit/MR 内容作为输入已可见，本 pilot 验证的是 routing/readability/handoff/VERIFY/END，不验证 agent 能否重新发现修复。若要隐藏 outcome 做盲测，转入 Phase 12。

## ROUTE / WORK / VERIFICATION PLAN

- **Route 选择**: <从 company entry skill 读取了什么 entrypoint，选择了哪个 module/workflow/source/repo-local skill>
- **未选候选**: <为什么没有选择其他明显的候选>
- **Work 计划**: <source 查证策略（只记录 pointer/summary）、repo-local handoff 计划、修改只在受控 copy/draft 中操作>
- **Verification 方法**: <precheck / test / lint / dry-run / owner review；记录 reviewer role 和实际审查内容>

## OBSERVED EXECUTION

- **实际执行的命令与 exit code**:
  - `<command>` → exit `<code>`, 输出摘要: `<summary>`
- **未执行**: `<not-run 项与原因>`
- **受控副本/draft 操作**: <在工作副本中做了什么修改>
- **生产写入边界**: <无 / 停止于 draft / 需要 owner approval>

> 只记录实际执行并捕获输出的验证结果。`PASS` 或 `FAIL` 只能来自真实运行命令后的输出。未执行验证必须记为 `not-run`。不得从文件存在声称 `PASS`。

## END / PILOT EVALUATION

- **Outcome**: `useful` / `partial` / `blocked` / `missed`
- **Routing 评价**: <route 是否正确，与期望 route 的对照（如有），偏差原因>
- **Work 评价**: <source 查证、repo-local handoff 是否完成>
- **VERIFY 评价**: <哪些验证 pass / fail / not-run / blocked>
- **Closure 评价**: <END 是否正确闭合，为什么写回或不写回>
- **Failure attribution**: <routing_failure / truth_failure / boundary_failure / writeback_failure / verification_failure / no_skill_gap / none>
- **no_skill_gap**: `yes` / `no` / `not-evaluated`
- **Writeback decision**: `none` / `task-local` / `repo-local` / `company-jarvis` / `source-skill` / `workflow-skill` / `upstream`
- **Next action**: <next action>

> 若 artifact 为 historical-shadow 且为 dry-run 或 route-only，必须明确它只能证明 routing/readability，不能证明产品行为或所有 skills 无 gap。

## Safety Checks

- [ ] 未发生未经授权的生产写入。
- [ ] 未泄露 secret / PII / 未经授权材料。
- [ ] 单次 pilot 结果未直接提升为 durable skill rule。
- [ ] Repo-local execution truth 留在 repo-local 层。
