# Phase 5 - 就绪检查

目标：判断当前上下文是否足以继续生成 company Jarvis repo。

## 检查项

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
- `JARVIS_RUNTIME_ROOT` 缺失且无法创建。
- source/repo access 不足以验证 first workflow。
- writeback requested 但 approval model 缺失。
- 需要暴露 secret value 才能继续。
