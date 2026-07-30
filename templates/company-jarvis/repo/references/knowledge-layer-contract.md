---
id: reference.knowledge-layer-contract
status: binding
version: 1.0
---

# Company / cross-cutting / repo-local knowledge 分层合同

## Core rule

知识按它回答的问题分层，不按文件格式或扫描来源分层：

```text
artifact / task evidence
  → modules：这个产品 capability 的稳定语义是什么
  → cross-cutting：为什么必须从 A 继续检查 B
  → repo-local：在 B 的仓库里去哪里、怎样实现和验证
  → source / runtime / tests：本次事实是否成立
```

多个层可以指向同一条真实链路，但不能各自维护一份实现说明。

## Authority matrix

| Layer | 它回答的问题 | 适合保存 | 不应保存 |
|---|---|---|---|
| shared method/reference | Agent 应怎样发现、证明和停止 | gate、evidence type、stop condition | 客户 repo 的 symbol map、单个 issue 结论 |
| `modules/<module>/` | 这个 capability 的边界与稳定语义是什么 | current contract、decision、known pattern、coverage gap、source pointer | 跨模块完整因果图、repo 操作 SOP |
| `cross-cutting/` | 改 A 为什么会影响 B、下一跳是什么 | shared invariant、causal edge、false owner、first proof、next-hop pointer | 完整调用栈、逐文件清单、测试命令 |
| repo-local skill/reference | 在一个 repo 中去哪里、怎样实现和验证 | architecture/layer owner、concrete source role、repo command、test home | 公司级 workflow、跨 repo 产品矩阵 |
| source route | 如何到达事实以及它拥有什么 authority | access、retrieval、freshness、redaction、writeback boundary | source 正文镜像 |
| task-local artifact | 这次实际读了什么、证明了什么 | log、diff、coverage ledger、unknown、stop rationale | 未经归纳的长期规则 |

最短记忆法：

- `modules` 回答 **what**；
- `cross-cutting` 回答 **why inspect next**；
- repo-local 回答 **where and how**；
- source/runtime/tests 回答 **is it true now**；
- task artifact 回答 **what was proved this time**。

## Repo-local handoff

当 company route 命中 execution repo：

1. 读取该 repo 当前真实存在的 `AGENTS.md`、root skill 或其他入口；
2. 不存在 repo-local skill 时明确记录 `pending repo-local entry`，不能发明路径；
3. 由 repo-local guidance 选择具体 layer、symbol、command 和 test home；
4. 回到当前源码/测试验证 guidance 是否仍成立；
5. task-specific 结论留在当前 artifact，稳定 repo pattern 才写回 repo-local。

Company knowledge 与当前 route scope 所需的 repo-local knowledge 交付后，必须把 pending handoff 替换为实际入口并重新验证路由。

## Overlap test

一段内容看起来可以写到多个地方时，依次问：

1. 只解释本次任务证据？留 task-local。
2. 描述一个 capability 内的稳定产品/语义 contract？写 module。
3. 解释两个以上 capability 之间的稳定因果边？写 cross-cutting。
4. 依赖具体 repo 的 layer、symbol、framework、command 或 test？写 repo-local。
5. 只描述如何访问一个事实源？写 source route。
6. 是公司无关的通用推理方法？留在 runtime method，不复制进 company repo。

若同时包含跨模块 contract 和仓库实现，拆成两层：company 保存 contract 与 pointer，repo-local 保存实现与 proof。

## Conflict and freshness

- 当前 source/runtime 证明 durable knowledge 过期：按当前证据处理，并修正或标记 stale owner。
- observed behavior 与 accepted decision 冲突：前者证明 current behavior，后者证明 expected contract；两者共同构成后续判断。
- company capability owner 与代码 semantic owner 可以不同；必须写清 handoff，不能互相覆盖。
- broken pointer 会让 routing 在边界处停止，必须作为 maintenance 缺口处理。

## Writeback rule

一条结论只有一个正文 owner：

- 新的 module invariant / semantic family → module `decisions.md`；
- 可复用 failure pattern → module `known-issues.md`；
- 跨模块 causal edge / false owner → `cross-cutting/module-interactions.md`；
- repo layer rule / symbol map / test recipe → repo-local skill/reference；
- source access / authority / freshness → source route；
- 客户跨 source/repo/角色闭环 → customer workflow；
- 公司无关的 agent reasoning gate → upstream runtime method。

其他层只保留 pointer 和一句路由理由，不复制正文。
