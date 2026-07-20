# Phase 5 - 就绪检查

目标：判断当前上下文是否足以继续生成 company Jarvis repo。

## 检查项

- 加载 install 已提供的 `jarvis-box-doctor`，按当前安装版本和 slot 运行就绪诊断；读取人类可读结果，不要求额外 JSON schema。
- doctor 发现可修复的 install/runtime 缺口时加载 `jarvis-box-init`，按其权限规则修复后重新运行 doctor；不能修复时记录 exact blocker。
- target home 存在或可创建。
- `JARVIS_HOME` 与 `JARVIS_TARGET_HOME` 没有冲突。
- `JARVIS_RUNTIME_ROOT` 存在或可创建；它承载 workspace、repo-cache、task state 等运行期目录。
- method repo URL/ref/commit 可记录。
- runtime agent 可执行。
- pilot repo/source 有最小 read access。
- company Jarvis repo 有 create/link/write 策略。
- secret 只记录状态，不读取值。
- writeback policy 有 owner 和 approval model。
- 非交互模式没有未解决必填项。

## 输出

- 就绪判断：`proceed`、`needs-input`、`blocked` 或 `failed`。
- blockers、warnings、missing inputs、next action。
- 更新 `bootstrap-result.json`。

## 停止条件

- target path 不安全或不可写。
- `jarvis-box-doctor` 证明当前 runtime/agent 不可用，且 `jarvis-box-init` 无法修复或需要尚未获得的授权。
- `JARVIS_RUNTIME_ROOT` 缺失且无法创建。
- source/repo access 不足以验证 first workflow。
- writeback requested 但 approval model 缺失。
- 需要暴露 secret value 才能继续。
