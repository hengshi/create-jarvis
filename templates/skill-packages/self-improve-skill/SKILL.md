---
name: jarvis-self-improve-skill
description: >
  Jarvis self-improvement 方法。读取 jarvis-box 支持的
  agent session 和高信号 review trajectory，判断是否存在可复用、可验证的缺口，
  并把结果路由到正确的 durable owner。
---

# Jarvis Self-Improvement

这是 Jarvis 的方法论 skill，不是 collector、scheduler、数据库或运行时实现。
session 收集、agent registry、定时触发和运行目录由 jarvis-box install 提供；本 skill
只负责读取已授权证据、归因失败、选择写回归属和验证结果。

## 强制预读

进入此 skill 前，先从当前已加载的 Jarvis entry 定位当前 Jarvis root，再读取：

- `references/runtime-governance-quick.md`
- `references/agent-engineering-quality-gate.md`
- `references/minimal-closure-card.md`

涉及写回时加读：

- `references/writeback-governance.md`

## START -> WORK -> VERIFY -> END

### START

1. 通过当前 jarvis-box agent registry 发现实际支持的 agent 和可读 evidence root；不要假设固定 transcript 路径。
2. 明确本次窗口、仓库/项目范围、agent 范围和 review 状态过滤条件。
3. 区分 session trajectory、reviewed-MR trajectory、history replay case；三者不能互相冒充。
4. 先排除 open MR、重复 loop、没有执行证据的摘要和未经验证的用户转述。

### WORK

1. 重建每条候选 trajectory：用户意图、agent 选择、实际命令、失败、恢复路径和最终结果。
2. 按 broken control point 分类：runtime、routing、repo-local execution、skill drift、tool/hook、test/review gate 或 external one-off。
3. 在写 prose 前选择 intervention：`skill_rule`、`repo_tool`、`runtime_launcher`、`script_or_hook`、`test_fixture`、`review_gate`、`docs` 或 `no_change`。
4. 对重复或高影响模式选择唯一 primary home：repo-local、Jarvis、jarvis-box runtime、脚本/工具、测试或文档。
5. 保持 repo execution truth 在 repo-local；不要把单仓库命令或客户私有事实写入 Jarvis。

### VERIFY

1. 检查模式是否有至少两个独立 trajectory，或单个足以证明高影响的完整证据。
2. 对 proposed writeback 运行最小相关验证；不能用报告存在替代行为验证。
3. 若已有 guidance 足够，输出 `no_skill_gap`，不扩张 skill。
4. 若 evidence 不完整、泄漏或无法隔离，输出 `not-evaluated`，不能据此关闭缺口。

### END

输出一张 decision card：

- evidence window and sources
- failure mode
- decision: `no_skill_gap` / `repo-local` / `central-jarvis` / `jarvis-box-runtime` / `upstream-method`
- primary home and owner
- verification evidence
- next action

只有证据支持且 owner 明确时才写回。写回后记录路径、验证命令和结果；没有 durable
变化时明确记录 `no_skill_gap`，不要创建空 backlog。

## 边界

- 不复制 jarvis-box 的 collector、scheduler、agent routing、workspace cleanup 或 service lifecycle 实现。
- 不把 raw transcript、reviewer identity、secret、PII、私有机器路径或源代码写入 Jarvis。
- 不把一次性外部故障或单条未经验证的建议提升为 durable rule。
- broad backfill / RL 请求必须分片、可恢复，并为每条候选保留 accounted status。
