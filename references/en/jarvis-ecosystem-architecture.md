# JARVIS Ecosystem Architecture

Use this reference when deciding where a rule, skill, or artifact belongs.

## Layer Contract

| Layer | Owns | Does not own |
|---|---|---|
| Runtime | install, service lifecycle, webhooks, credentials, agent execution, task state, logs, bootstrap invocation | company methodology, repo-local execution truth, durable business knowledge |
| JARVIS entry skill | company-wide routing, loop identification, source/repo/workflow selection, END writeback decision | raw source copies, full repo procedures, runtime operations |
| Workflow skills | cross-source or cross-repo loops, gates, artifacts, handoffs, completion evidence | low-level repo commands, source exports, runtime state |
| Project/repo-local skills | build/test/run commands, repo structure, local conventions, validation, safe mutation rules | company-wide routing, unrelated workflow policy |
| Source/tool skills | access, search, freshness, redaction, query/export boundaries for a source | mirroring source content into JARVIS |
| Governance references | stable rules for writeback, redaction, promotion, completion, maintenance | task-local notes or one-off examples |
| Calibration loop | eval cases, failure modes, no-skill-gap decisions, scoped skill updates | automatic skill growth for every failure |

## Central JARVIS Entry Skill

The entry skill should behave like a router and closure gate:

```text
task
-> identify the loop
-> select workflow/source/repo-local skill
-> choose the shortest evidence path
-> execute in the owning surface
-> decide whether durable writeback is needed
```

It should not become a giant content warehouse. Keep raw artifacts in their source systems and repo-local execution truth in the repo that owns it.

## Workflow-First Pilot Rule

The pilot unit is one closed workflow, not a pile of repos or documents. Source and repo inventories exist only to support that workflow until the pilot is proven.

## Source and Repo Boundaries

For every pilot repo, record:
- role in the workflow;
- owner or maintainer;
- repo-local skill path or missing-skill gap;
- what must remain repo-local;
- what central JARVIS may keep as a routing summary.

For every pilot source, record:
- owner;
- access path and tool;
- query/search strategy;
- freshness and redaction constraints;
- what should never be copied into JARVIS.

## Workflow Skill Quality Bar

A workflow skill must define:
- trigger;
- required input evidence;
- START precheck;
- WORK routing and execution surfaces;
- escalation conditions;
- completion evidence;
- END writeback decision;
- handoff card.

If it only narrates a process, it is not yet a useful workflow skill.
