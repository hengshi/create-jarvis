---
name: <workflow-skill-name>
description: Help agents execute the <workflow-name> workflow for <company/product>. Use when work spans multiple sources, repos, roles, or artifacts and requires a repeatable closed loop with clear stages, evidence, and writeback.
---

# <Workflow Skill Title>

## Purpose

State:
- what loop this workflow covers,
- why it matters,
- and what business outcome it is meant to unlock.

## Trigger and Preconditions

- **Trigger**: `<start condition>`
- **Preconditions**: `<required context>`
- **Input evidence required**: `<artifact / issue / request / source record>`
- **In-scope repos**: `<repos>`
- **In-scope sources**: `<sources>`

## Workflow Stages

1. **START precheck** — `<what must be true before work starts>`
2. **WORK routing** — `<which source/repo/work surface is first>`
3. **Escalation** — `<when to move to another source/repo/owner>`
4. **Verify** — `<evidence or checks>`
5. **END writeback judgment** — `<what gets written back, where, or why no writeback is needed>`

## Handoffs

| Stage | Main owner / role | Artifact | Next handoff |
|---|---|---|---|
| `<stage>` | `<owner>` | `<artifact>` | `<next>` |

## Routing Rules

Use this workflow skill when:
- `<trigger>`
- `<trigger>`

Do not use it for:
- `<out of scope>`
- `<out of scope>`

## Verification

- [ ] the start condition is explicit
- [ ] input evidence and START precheck are explicit
- [ ] handoffs and artifacts are explicit
- [ ] escalation conditions are explicit
- [ ] evidence of success is explicit
- [ ] writeback closes the loop rather than ending at delivery
- [ ] `no_skill_gap` is allowed when existing skills are sufficient
