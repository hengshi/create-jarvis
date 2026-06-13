# JARVIS 生态架构

当你需要判断某条规则、skill 或 artifact 应该放在哪一层时，使用这份参考。

## 分层契约

| 层级 | 负责 | 不负责 |
|---|---|---|
| Runtime | install、service lifecycle、webhooks、credentials、agent execution、task state、logs、bootstrap invocation | 企业方法论、repo-local 执行真相、长期业务知识 |
| JARVIS entry skill | 公司级 routing、闭环识别、source/repo/workflow 选择、END writeback 判断 | raw source 复制、完整 repo 操作手册、runtime 运维 |
| Workflow skills | 跨 source / repo / team 的闭环、gate、artifact、handoff、完成证据 | repo 低层命令、source export、runtime state |
| Project/repo-local skills | build/test/run 命令、repo 结构、本地约定、验证、安全修改规则 | 公司级 routing、无关 workflow policy |
| Source/tool skills | source 的访问、搜索、新鲜度、脱敏、query/export 边界 | 把 source 内容搬进 JARVIS |
| Governance references | writeback、redaction、promotion、completion、maintenance 等稳定规则 | task-local notes 或一次性例子 |
| Calibration loop | eval cases、failure modes、no-skill-gap、scoped skill updates | 每次失败都自动扩张 skill |

## 中心 JARVIS entry skill

中心 entry skill 应像 router 和 closure gate：

```text
task
-> 识别闭环
-> 选择 workflow/source/repo-local skill
-> 选择最短证据路径
-> 在拥有事实的 surface 执行
-> 判断是否需要长期 writeback
```

它不应该变成内容仓库。raw artifacts 留在 source system，repo-local execution truth 留在所属 repo。

## Workflow-first 试点规则

试点单位是一条闭环 workflow，不是一堆 repo 或文档。source 和 repo inventory 在 pilot 证明前只服务这条 workflow。

## Source / Repo 边界

每个 pilot repo 至少记录：
- workflow 中的角色；
- owner / maintainer；
- repo-local skill path 或缺口；
- 必须留在 repo-local 的事实；
- central JARVIS 只保留的 routing summary。

每个 pilot source 至少记录：
- owner；
- access path / tool；
- query/search strategy；
- freshness / redaction constraints；
- 绝不能复制进 JARVIS 的内容。
