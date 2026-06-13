# Skill Calibration Loop

Use this after real work, pilot runs, or historical replay exposes a failure.

## Loop

```text
real task or historical artifact
-> eval case
-> agent replay
-> failure mode
-> no_skill_gap or scoped update
-> verification
-> repo-local, central, or upstream promotion decision
```

## Eval Case Sources

Good eval cases come from:
- real START -> WORK -> END runs;
- historical issue/MR/commit/task outcomes summarized without copying private text;
- owner corrections;
- routing mistakes;
- access or source interpretation failures;
- writeback misses;
- counterexamples where scaffolding would have been dishonest.

Single-use surprises usually stay as task notes. Repeated failures or high-blast-radius failures may justify skill changes.

## Failure Taxonomy

| Failure | Meaning |
|---|---|
| `routing_failure` | wrong module, source, repo, workflow, or next hop |
| `truth_failure` | unconfirmed data treated as fact |
| `boundary_failure` | repo-local truth centralized, or central routing scattered |
| `route_invalidation` | later evidence invalidated an earlier reasonable route |
| `writeback_failure` | durable learning missed or written to the wrong home |
| `duplication_failure` | new skill created instead of improving an existing one |
| `bloat_failure` | skill/template growth without repeated value |
| `promotion_failure` | private company material promoted to generic method |
| `verification_failure` | conclusion lacked evidence or replay |
| `no_skill_gap` | existing skills were sufficient; the failure was task-local, data-local, or execution-local |

## Calibration discipline

Before changing a skill, separate:
- prompt/task evidence missing from the run;
- source data or runtime behavior outside the skill's control;
- a route that was reasonable with old evidence but invalidated later;
- a repeatable method gap that belongs in a stable skill or reference.

Only the last category should normally change the skill. `route_invalidation` may change route-confidence checks, but it does not automatically mean the old skill was wrong.

## `no_skill_gap` Gate

Check `no_skill_gap` before creating or expanding a skill. Choose it when:
- existing source/repo/workflow skills already cover the needed method;
- the failure came from missing task evidence, not missing skill guidance;
- the case is a one-off exception;
- the fix belongs in source data, code, tests, or runtime behavior.

Only update a skill when the failure is repeatable, transferable, and best solved by stable procedural guidance.

## Skill Bloat Protection

A new or expanded skill needs:
- trigger condition;
- owner;
- workflow or source/repo target;
- evidence source;
- overlap check against existing skills;
- expected observable benefit;
- verification through replay or later pilot.

If it overlaps an existing skill, merge by default. If it serves only one exception, defer or record `no_skill_gap`.

## Calibration Record

Each calibration entry should capture:
- eval case pointer;
- failure taxonomy;
- selected action: no skill gap, edit existing skill, create new skill, update reference, update source/repo/workflow inventory;
- owner;
- verification evidence;
- promotion target: repo-local, central JARVIS, or upstream create-jarvis-skill.
