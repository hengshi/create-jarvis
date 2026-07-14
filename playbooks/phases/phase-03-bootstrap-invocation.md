# Phase 3 - Bootstrap 启动交接

目标：让 jarvis-box 正确进入 company Jarvis bootstrap，并把上下文交给 selected runtime agent。

Phase 3 只处理 bootstrap CLI handoff。也就是 jarvis-box 调起 agent、准备上下文、交出输出契约。它不做业务信息接收，不扫描客户业务，不生成 adaptation manifest，不创建 company Jarvis 文件。

Phase 3 是独立同步 bootstrap CLI 的交接点，不是 jarvis-box Target/Task/Run 创建。不在此阶段创建 Target、不分配 task_id/run_id。

## Owner

- jarvis-box：发起 bootstrap、确定调用模式、准备 prompt/env、调起 selected runtime agent、等待 result。
- runtime agent：接收上下文，确认可读，然后进入 Phase 4。

## 输入

- selected bootstrap agent（本次 bootstrap 固定选择；jarvis-box Task runtime failover 不会自动接管 bootstrap agent）。
- `jarvis-box bootstrap jarvis` 的 CLI 参数、env 或配置。
- existing `JARVIS_HOME`、`JARVIS_REPO_URL`、`JARVIS_ENTRY_SKILL`，如果存在。
- target home / result path / working directory。
- method repo URL/ref。

## 步骤

1. 确认 selected bootstrap agent 可执行。
2. 判断调用模式：
   - `existing-jarvis-link`
   - `explicit-repo-clone`
   - `interactive-operator-generation`
   - `noninteractive-runtime-generation`
   - `resume-generation`（只读取已保存 answers/state 后重新发起 bootstrap agent；不继续旧 Run、不调用 native resume、不是 jarvis-box Continue With Agent 或 Recover Lost Run）
3. 准备 handoff context：
   - runtime env；
   - prompt file 或 prompt body；
   - target/result paths；
   - known answers；
   - noninteractive/resume 标志；
   - method repo URL/ref；
   - output contract。
4. 调起 runtime agent。
5. 等待 agent 写出 `bootstrap-result.json`，或收集调用失败。
6. 如果已有或显式 clone company Jarvis repo，校验 entry skill 是否存在并可读。
7. 说明 jarvis-box 只在 `bootstrap-result.json` `status=completed` 时才 link `JARVIS_HOME`；`needs-input`/`blocked`/`failed` 作为未完成返回，根目录 `bootstrap-state.json` 和 `bootstrap-result.json` 仍用于下一次 `bootstrap --resume` 继续。
8. `resume-generation` 还要做现有产物完整性审计：
   - 读取根目录 `bootstrap-state.json`、`bootstrap-result.json` 和当前文件状态；
   - 识别 bootstrap 后发生的用户编辑，保留并在冲突时进入 Phase 4 处理；
   - 对已经声称完成的产物运行当前适用的 `--stage phase-09` 和 final verifier；
   - 把 blocker/acceptance failure 映射到最早所属 phase；旧 `completed` 只是一条历史声明，不能覆盖当前证据；
   - 将最早未通过 phase 作为恢复起点，更晚 phase 恢复为 `pending`。Phase 3 只确定恢复起点，实际业务扫描和修复回到对应 phase 执行。

## 输出

- 启动交接模式；
- selected agent command；
- prompt/context path；
- target/result paths；
- handoff succeeded/failed；
- resume 时的完整性审计结果和最早恢复 phase；
- 如果已有 Jarvis 被绑定，记录 `JARVIS_HOME` 和 entry skill。
- 输出中不包含 `task_id`/`run_id`。

## 停止条件

- selected bootstrap agent 不可执行或未认证。
- target path 明显不安全。
- 非交互模式没有 result path 或 target home。
- existing Jarvis entry skill 不存在。
- resume 会覆盖用户已编辑文件，但没有进入 Phase 4 的 conflict 处理。
- 把 bootstrap resume 误当 Task recovery（Continue With Agent / Recover Lost Run）。
- 把非 `completed` 的 bootstrap 当已绑定成功。

## 进入 Phase 4 的条件

runtime agent 已拿到交接上下文。缺 company name、first workflow、owner、repo/source scope、writeback policy 等业务输入不在 Phase 3 解决，进入 Phase 4 后由 agent 做信息接收。
