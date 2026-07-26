# Phase 5 - 就绪检查

目标：用 live evidence 判断当前 runtime agent 是否能安全执行业务发现和本地生成，并把安装/runtime 缺口归还给正确 owner。

## 检查项

- 如果当前安装提供 `jarvis-box-doctor` / `jarvis-box-init`，按其权限合同诊断和修复；未安装这些 skill 时使用当前版本可观察的 CLI/help/status 和直接 filesystem probe，不编造能力。
- selected runtime agent 已通过最小 prompt probe。
- 记录有效 UID/GID；bootstrap workspace、company Jarvis target 和需要写 repo-local package 的 checkout 可由该 UID/GID 写入。
- service-private config/state 与 agent-owned workspace 分离；没有让 agent 直接写 service-only 路径。
- container bind mount 使用 host UID/GID mapping 或等价权限合同；Linux host workspace 有明确 owner/group/ACL。
- target home 存在或可由 selected agent 创建；`JARVIS_HOME` 与 `JARVIS_TARGET_HOME` 不冲突。
- method repo URL/ref/commit 可记录。
- first workflow 所需 repo/source 有最小 read access；其他 source 可标 `deferred-needs-access`。
- Git/provider/isolation 能力分别记录 `observed-ready`、`missing` 或 `not-required-yet`。
- secret 只记录状态，不读取值。
- remote writeback 没有批准时强制 local-only；需要远端发布的 phase 再以 exact approval blocker 停止。

## 权限故障记录

每个失败路径至少记录：path、访问类型、effective UID/GID、owner/group/mode、probe 结果、期望 owner 和负责修复的 install/image 能力。不要建议客户在未知目标上执行递归 `chmod`/`chown`，也不要用 world-writable 目录作为完成条件。

## 输出

- 就绪判断：`proceed`、`needs-input`、`blocked` 或 `failed`；
- runtime capability + filesystem ownership matrix；
- blockers、warnings、missing approval 和 exact next action；
- 更新 `bootstrap-state.json` / `bootstrap-result.json`。

## 停止条件

- target/workspace 不安全或 selected agent 不可写。
- first workflow 必需 source/repo 不可读。
- selected agent 不可用，或继续会暴露 secret。
- 缺口只能靠未经授权的提权/所有权修改绕过。
- 用户要求立即远端写回，但 project/approval policy 无法安全确定。

缺少非 first-workflow access、尚未批准远端发布或尚未安装可选 isolation transport，不阻塞 Phase 6 的 local-only discovery；按最早真正需要该能力的 phase 记录 gate。
