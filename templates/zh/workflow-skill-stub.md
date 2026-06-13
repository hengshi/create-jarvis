---
name: <workflow-skill-name>
description: 帮助 agents 为 <company/product> 执行 <workflow-name> workflow。当工作横跨多个 sources、repos、roles 或 产物，并需要一条具有明确阶段、证据和 回写 的可重复闭环时使用。
---

# <Workflow Skill Title>

## Purpose

说明：
- 这个 workflow 覆盖哪条闭环，
- 它为什么重要，
- 它旨在解锁什么业务结果。

## Trigger 与 Preconditions

- **Trigger**: `<start condition>`
- **Preconditions**: `<required context>`
- **Input evidence required**: `<artifact / issue / request / source record>`
- **In-scope repos**: `<repos>`
- **In-scope sources**: `<sources>`

## Workflow Stages

1. **START precheck** — `<what must be true before work starts>`
2. **WORK routing** — `<which source/repo/work surface is first>`
3. **Escalation** — `<when to move to another source/repo/owner>`
4. **Verify** — `<证据 or checks>`
5. **END writeback judgment** — `<what gets written back, where, or why no writeback is needed>`

## Handoffs

| Stage | Main owner / role | Artifact | Next handoff |
|---|---|---|---|
| `<stage>` | `<owner>` | `<artifact>` | `<next>` |

## Routing Rules

在以下情况使用这个 workflow skill：
- `<trigger>`
- `<trigger>`

不要把它用于：
- `<out of scope>`
- `<out of scope>`

## Verification

- [ ] start condition 已明确
- [ ] input evidence 和 START precheck 明确
- [ ] 交接点 与 产物 已明确
- [ ] escalation conditions 明确
- [ ] success 证据 已明确
- [ ] 回写 真正闭合了闭环，而不是在交付处停止
- [ ] 当现有 skills 足够时允许 `no_skill_gap`
