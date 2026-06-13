---
name: <company-jarvis>
description: The unified entry skill for the <company/product> JARVIS instance. Use when an agent needs to query company knowledge, route into the right module or source, follow cross-cutting guidance, or maintain the JARVIS instance itself.
---

# <Company / Product> JARVIS

## Runtime context

This file may be installed directly as `$JARVIS_HOME/SKILL.md` by jarvis-box or another runtime. Treat `JARVIS_HOME` as the instance root and do not assume the runtime root is named after any vendor or company.

The runtime owns service lifecycle, credentials, task state, webhooks, and agent execution. This entry skill owns routing, loop selection, and END writeback judgment.

## Core boundary

JARVIS is the company-wide router and closure gate. It should:
- identify the current loop;
- select the right workflow, source, or repo-local skill;
- choose the shortest evidence path;
- route execution to the owning source or repo;
- decide whether durable writeback is needed at END.

It should not:
- mirror source systems;
- replace repo-local execution truth;
- manage runtime install/setup/service behavior;
- turn task logs into permanent knowledge.

## Use the right entrypoint first

- business domain questions → `modules/<module>/overview.md`
- source-specific questions → `sources/<source>/README.md`
- cross-domain effects → `cross-cutting/*.md`
- operational helpers → `tools/*`
- workflow execution → `skills/<workflow-skill>/SKILL.md` or the workflow inventory
- repo-specific execution → the repo-local skill or repo-owned instructions

Do not guess randomly when a stable entrypoint exists.

## Default query path

```text
user task
→ identify workflow / module / source / cross-cutting topic
→ read the stable entrypoint
→ route to workflow/source/repo-local skill when needed
→ read issue / decision / rejection patterns if needed
→ execute in the owning source, repo, or workflow surface
→ decide whether END writeback is needed
```

## Work loop

### START
- read the relevant JARVIS entrypoint first
- identify source-of-truth locations

### WORK
- do the work in the real source, repo, or workflow surface

### END
- write back durable knowledge to the correct JARVIS file
- record `no_skill_gap` when the skill set was sufficient
- follow the maintenance guide instead of inventing writeback rules ad hoc

## Maintenance

When maintaining the JARVIS instance itself, use the root `MAINTENANCE.md` as the source of truth.
