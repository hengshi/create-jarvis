---
name: <company-jarvis>
description: 面向 <company/product> JARVIS instance 的统一入口 skill。当 agent 需要查询公司知识、路由到正确的 module 或 source、遵循 cross-cutting guidance，或维护 JARVIS instance 本身时使用。
---

# <Company / Product> JARVIS

## Runtime context

这个文件可以由 jarvis-box 或其他 runtime 直接安装为 `$JARVIS_HOME/SKILL.md`。把 `JARVIS_HOME` 当作 instance root，不要假设 runtime root 使用任何厂商或公司的名称。

runtime 负责 service lifecycle、credentials、task state、webhooks 和 agent execution。这个 entry skill 负责 routing、loop selection 和 END writeback 判断。

## 核心边界

JARVIS 是公司级 router 和 closure gate。它应该：
- 识别当前闭环；
- 选择正确的 workflow、source 或 repo-local skill；
- 选择最短证据路径；
- 把执行路由到拥有事实的 source 或 repo；
- 判断 END 时是否需要 durable writeback。

它不应该：
- mirror source systems；
- 替代 repo-local execution truth；
- 管理 runtime install/setup/service behavior；
- 把 task logs 变成 permanent knowledge。

## 先使用正确的入口

- 业务领域问题 → `modules/<module>/overview.md`
- source-specific 问题 → `sources/<source>/README.md`
- 跨领域影响 → `cross-cutting/*.md`
- 操作辅助工具 → `tools/*`
- workflow execution → `skills/<workflow-skill>/SKILL.md` 或 workflow inventory
- repo-specific execution → repo-local skill 或 repo-owned instructions

当稳定入口存在时，不要随机猜。

## 默认查询路径

```text
user task
→ 识别 workflow / module / source / cross-cutting topic
→ 阅读稳定入口
→ 需要时路由到 workflow/source/repo-local skill
→ 如有需要，阅读 issue / decision / rejection patterns
→ 在拥有事实的 source、repo 或 workflow surface 执行
→ 判断 END 是否需要 writeback
```

## 工作闭环

### START
- 先阅读相关的 JARVIS 入口
- 识别 权威来源 locations

### WORK
- 在真实的 source、repo 或 workflow surface 中完成工作

### END
- 把可持续复用的知识写回正确的 JARVIS 文件
- 当现有 guidance 已足够时，记录 `no_skill_gap`
- 遵循 maintenance guide，不要临时发明 回写 规则

## 维护

当维护 JARVIS instance 本身时，以根目录的 `MAINTENANCE.md` 作为 权威来源。
