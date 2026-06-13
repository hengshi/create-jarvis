# 实例成熟度

用这份 checklist 判断生成的 JARVIS 只是 installed、pilot-ready、pilot-proven、operational，还是 mature。

## Level 0 - Installed Scaffold

满足：
- root structure 存在；
- maintenance guidance 存在；
- 部分 templates / inventories 存在；
- runtime-driven 时 runtime 能 link entry skill。

Installed scaffold 还不是 operational。

## Level 1 - Pilot-Ready

满足：
- 定义了一条真实 business loop；
- 该 loop 需要的 sources / repos / workflows 已 inventory；
- source / repo / workflow skill 至少有 draft；
- truth-bearing fields 已确认或明确 unresolved；
- owner / escalation path 已知；
- 另一个 agent 或 owner 能开始 pilot，不必从零发现。

Pilot-ready 只表示可以开始跑，不表示方法已经被证明。

## Level 2 - Pilot-Proven

满足：
- 至少跑过一条真实 START -> WORK -> END；
- 有证据显示 JARVIS 帮到了哪里、失败在哪里；
- failures 已分类；
- skill backlog 包含 `no_skill_gap` / merge / update / create 决策；
- controlled writeback 已提出或在 owner review 下完成。

Pilot-proven 证明方向，不证明完整。

## Level 3 - Controlled Operations

满足：
- modules 中有真实知识，不是 placeholders；
- source routing 真实可用；
- repo-local truth 正确 linked；
- workflow closure 明确；
- START -> WORK -> END writeback 正在实践；
- calibration 能防止 skill bloat。

## Level 4 - Mature Instance

满足：
- 历史知识深且结构化；
- repeated failures 被沉淀为 patterns；
- decisions / rejected ideas 有 rationale；
- cross-cutting knowledge 持续维护；
- ownership 稳定；
- eval cases 和 calibration loops 定期运行；
- 系统通过真实使用持续进化。

## Readiness checks

- [ ] business modules 有真实 overview / issue / decision content
- [ ] sources 有真实 routing docs
- [ ] cross-cutting knowledge 在需要处存在
- [ ] company-specific JARVIS skill entry 存在
- [ ] main loops 需要的 repo skills / workflow skills 存在
- [ ] writeback 来自真实工作，而不是只在 setup 时发生
- [ ] claim pilot success 前已有 pilot evidence
- [ ] calibration decisions 在适当时候包含 `no_skill_gap`
- [ ] 另一个 owner 或 agent 能接手而不重新发现基础事实
