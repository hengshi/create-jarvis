---
name: create-jarvis-skill
description: Bootstrap, redesign, or scale an enterprise JARVIS ecosystem from company sources, repos, workflows, and runtime constraints. Use when an agent or runtime such as jarvis-box needs to create a company-specific JARVIS substrate, define source/repo/workflow skill boundaries, prepare a pilot workflow, or evolve skills through eval failures and writeback. This is methodology and scaffold generation, not a replacement for jarvis-box runtime logic or repo-local source of truth.
---

# Create JARVIS Skill

Build a company-specific JARVIS substrate that can participate in real company work.

This repository is the methodology source of truth. A runtime such as jarvis-box may clone or read this repo through a runtime agent, but it should not bundle stale copies of these templates. The runtime owns install, setup, service lifecycle, credentials, task execution, and artifact persistence. This skill owns enterprise JARVIS structure, pilot method, skill boundaries, and calibration discipline.

Use `references/en/` only when a phase needs that detail. Use `templates/en/` only to produce artifacts required by the selected phase. Chinese materials under `references/zh/` and `templates/zh/` are human-facing mirrors and helpers; the English route remains the canonical execution path.

## Runtime Bootstrap Mode

When jarvis-box or another runtime invokes this methodology:

1. Treat the runtime prompt and normalized context as input, not as company truth.
2. Read `references/en/runtime-bootstrap-contract.md`.
3. Write the generated instance to `JARVIS_TARGET_HOME` or `JARVIS_HOME`.
4. Produce a valid entry skill at `JARVIS_ENTRY_SKILL` or `SKILL.md`.
5. Record `bootstrap-state.json` for resume and `bootstrap-result.json` for the runtime.
6. Use neutral paths such as `JARVIS_BOX_HOME`, `JARVIS_HOME`, and `JARVIS_TARGET_HOME`. Never hard-code company-specific runtime roots such as `.hengshi` into customer output.
7. Record the methodology source repo URL and commit/ref when known. The expected default repo URL is `https://github.com/hengshi/create-jarvis-skill.git`.
8. Do not read, print, or persist secret values. Only record secret names, status, and paths supplied by the runtime.

Stop instead of fabricating output when a required runtime input is absent, target paths are not writable, owners are guessed, or generated placeholders could be mistaken for confirmed company truth.

## Success Standard

A successful first pass does not mean the whole company is mapped.

It means:
- one valuable workflow is selected for a pilot;
- the sources, repos, owners, and handoffs for that workflow are mapped;
- a JARVIS entry skill and minimum source/repo/workflow skill stubs exist;
- truth-bearing fields are confirmed or explicitly marked unresolved;
- the runtime can link `JARVIS_HOME/SKILL.md`;
- and the result is ready for a shadow pilot, not declared mature.

Maturity comes later from real work: task outcomes, eval cases, failure analysis, and controlled writeback.

## Ecosystem Model

Keep these layers separate:

- Runtime layer: jarvis-box or another runtime. Owns install, service, webhooks, task state, credentials, agent execution, logs, and bootstrap invocation.
- JARVIS entry skill: the company-wide routing and closure entrypoint.
- Workflow skills: reusable loops such as intake, bugfix, PRD review, release notes, or customer operations.
- Project/repo-local skills: source-of-truth execution guidance inside each repo or project.
- Source/tool skills: integrations for docs, issue trackers, BI, CRM, calendars, support systems, and other digital assets.
- Governance references: durable routing, writeback, redaction, completion, and maintenance rules.
- Calibration loop: eval failures and real task outcomes that decide whether a skill update is needed.

Read `references/en/jarvis-ecosystem-architecture.md` when boundaries between these layers are unclear.

## The Golden Path

Do the phases in order. Do not skip stop conditions. Do not present scaffolding as mature knowledge.

```text
0. RUNTIME CONTRACT
1. FIRST WORKFLOW
2. PILOT INVENTORY
3. TRUTH BOUNDARIES
4. SCAFFOLD JARVIS SUBSTRATE
5. BOOTSTRAP MINIMUM SKILLS
6. CONFIRMATION GATE
7. SHADOW PILOT
8. CONTROLLED WRITEBACK
9. SKILL CALIBRATION LOOP
```

## Phase 0 - RUNTIME CONTRACT

Goal: establish whether this is human-driven bootstrap, runtime-driven bootstrap, or maintenance of an existing instance.

Output:
- normalized runtime context if called by jarvis-box;
- target path and entry skill path;
- writeback policy and confirmation policy;
- method repo URL/ref;
- explicit blockers for missing inputs.

Must confirm:
- `JARVIS_HOME` or `JARVIS_TARGET_HOME`;
- company or product name;
- first workflow candidate;
- allowed source/repo scope;
- human owner or escalation path.

Stop if:
- the runtime asks this repo to manage service lifecycle, credentials, task queues, or webhooks;
- target paths are missing or unsafe;
- noninteractive mode lacks required inputs.

Read:
- `references/en/runtime-bootstrap-contract.md`
- `references/en/instance-generation-contract.md`

## Phase 1 - FIRST WORKFLOW

Goal: choose the first valuable loop to prove, not a company-wide map.

Output:
- `templates/en/jarvis-build-brief.md`

The build brief must state business intent, target users, first workflow, success signal, rollout scope, non-scope, confirmation policy, and shadow-pilot criteria.

Stop if:
- success is described only as "better knowledge";
- the scope expands to the whole company before a pilot exists;
- no owner can judge whether the first loop worked.

Read only if needed:
- `references/en/pilot-workflow-methodology.md`
- `references/en/positioning.md`
- `references/en/example-pilot-shape.md`

## Phase 2 - PILOT INVENTORY

Goal: map only the operating surface needed for the first workflow.

Output:
- `templates/en/source-inventory.md`
- `templates/en/repo-inventory.md`
- `templates/en/workflow-inventory.md`

Capture source systems, repos/projects, workflow triggers, owners, access constraints, existing repo-local skills, and missing skills for the pilot.

Stop if:
- owners are guessed;
- source-of-truth locations are inferred but unconfirmed;
- the inventory becomes a full enterprise catalog before the pilot loop works.

Read only if needed:
- `references/en/company-adaptation.md`
- `references/en/source-skills.md`
- `references/en/repo-skills.md`
- `references/en/workflow-skills.md`

## Phase 3 - TRUTH BOUNDARIES

Goal: classify what may be generated now, what needs human confirmation, and what must grow from real work.

Output:
- artifact classification: scaffold now / confirm before use / grow through writeback.

Stop if:
- you are about to generate fake history;
- you are freezing ownership, workflow, or source truth without confirmation;
- you are creating detailed known issues, decisions, or rejected features from speculation.

Read:
- `references/en/instance-generation-contract.md`
- `references/en/instance-readiness.md`

## Phase 4 - SCAFFOLD JARVIS SUBSTRATE

Goal: generate the smallest company-specific JARVIS structure that can support the pilot and be linked by the runtime.

Output:
- root `README.md`;
- root `MAINTENANCE.md`;
- company JARVIS entry skill;
- source/repo/workflow inventories;
- source and module entrypoints as needed;
- ownership map;
- rollout plan;
- confirmation checklist;
- runtime bootstrap state/result files when runtime-driven.

Typical templates:
- `templates/en/root-readme.md`
- `templates/en/maintenance.md`
- `templates/en/company-jarvis-skill-stub.md`
- `templates/en/source-readme.md`
- `templates/en/module-overview.md`
- `templates/en/ownership-map.md`
- `templates/en/rollout-plan.md`
- `templates/en/rollout-confirmation-checklist.md`

Stop if:
- the scaffold becomes a content dump;
- module boundaries are invented without confirmation;
- generated placeholders could be read as mature company memory.

Read only if needed:
- `references/en/concrete-instance-topology.md`
- `references/en/detailed-maintenance-contracts.md`
- `references/en/write-contracts.md`

## Phase 5 - BOOTSTRAP MINIMUM SKILLS

Goal: create only the skills needed for the pilot workflow.

Output:
- source skill stubs when a source requires repeated access/routing;
- project/repo-local skill stubs when a repo lacks an execution entrypoint;
- workflow skill stubs when the first loop spans sources/repos/teams;
- `templates/en/skill-backlog.md`.

Every proposed repo skill must name what stays repo-local. Every proposed source skill must name what must not be copied into JARVIS. Every proposed workflow skill must include gates, evidence, escalation, and END writeback judgment.

Stop if:
- you are creating skills "just in case";
- central JARVIS is absorbing repo-local truth;
- backlog entries have no owner, outcome, or validation path.

Read only if needed:
- `references/en/jarvis-ecosystem-architecture.md`
- `references/en/source-skills.md`
- `references/en/repo-skills.md`
- `references/en/workflow-skills.md`
- `references/en/rollout-and-ownership.md`

## Phase 6 - CONFIRMATION GATE

Goal: force a human confirmation pass before pilot use.

Output:
- completed `templates/en/rollout-confirmation-checklist.md`;
- unresolved-question list;
- explicit "pilot-ready, not mature" status.

Confirm:
- first workflow and success signal;
- included sources, repos, and workflows;
- source-of-truth locations;
- owners and escalation;
- writeback destinations;
- security and redaction constraints;
- runtime linkability of `JARVIS_HOME/SKILL.md`.

Stop if:
- any truth-bearing field is still guessed;
- noninteractive bootstrap lacks a way to report unresolved fields;
- the pilot scope is company-wide in disguise.

## Phase 7 - SHADOW PILOT

Goal: run the first workflow against real artifacts while humans retain control.

Output:
- 3 to 5 real pilot artifacts or eval cases;
- task notes showing where JARVIS helped and where it failed;
- skill backlog updates;
- no uncontrolled production writeback.

Shadow mode means agents may read, route, draft, and recommend, but humans approve writeback and operational changes.

Stop if:
- the pilot has no real artifacts;
- the workflow can only be demonstrated with invented examples;
- runtime failures are being patched into create-jarvis-skill instead of jarvis-box or the owning runtime.

Read:
- `references/en/pilot-workflow-methodology.md`

## Phase 8 - CONTROLLED WRITEBACK

Goal: let real work grow durable memory without turning JARVIS into a log pile.

Output:
- updates to known issues, decisions, rejected features, test coverage, source routes, workflow rules, or repo-local skills only when evidence justifies them.
- updates to `bootstrap-state.json` or rollout artifacts when pilot assumptions are confirmed, disproved, or still unresolved;
- skill backlog changes with `no_skill_gap`, merge, update, create, or defer decisions;
- readiness level changes only when supported by pilot evidence.

Writeback rules:
- promote repeated or high-value truths, not raw chat residue;
- keep repo-local truth with the repo when appropriate;
- preserve one home per truth;
- record evidence pointers without copying private source material;
- use human approval when writeback changes operating behavior.

Stop if:
- you are copying raw issue/MR/docs text;
- a one-off artifact is being promoted as a durable rule;
- private company specifics are leaking into generic create-jarvis-skill methodology.

Read:
- `references/en/write-contracts.md`
- `references/en/detailed-maintenance-contracts.md`
- `references/en/internal-to-generic-promotion.md`

## Phase 9 - SKILL CALIBRATION LOOP

Goal: improve JARVIS from failures without bloating skills.

Use this loop:

```text
real task or historical artifact
-> eval case
-> agent replay
-> failure mode
-> no_skill_gap or skill/reference update
-> verification
-> local writeback or upstream methodology proposal
```

`no_skill_gap` is a first-class outcome. Not every failure means a skill should grow.

Output:
- eval case record;
- failure classification;
- skill update or explicit no-skill-gap decision;
- evidence that the updated skill improves the replay;
- promotion decision: repo-local, company JARVIS, or generic create-jarvis-skill.

Read:
- `references/en/skill-calibration-loop.md`
- `references/en/internal-to-generic-promotion.md`
- `references/en/anti-patterns.md`

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Let's just generate the JARVIS repo first." | A repo without a confirmed first workflow is a shell. |
| "We should inventory the whole company now." | Pilot scope beats fake completeness. |
| "We can fill in owners later." | Ownership is a truth-bearing field. |
| "The runtime can handle method details." | Runtime executes tasks; this repo defines the JARVIS method. |
| "The method repo should handle credentials and webhooks." | That belongs to jarvis-box or the runtime. |
| "Every eval failure should update a skill." | `no_skill_gap` prevents skill bloat. |
| "Internal examples can be copied into the generic method." | Promote patterns, not private artifacts. |

## Red Flags

- the runtime repository bundles stale copies of this repo's templates;
- `.hengshi` or any other company-specific runtime root appears in generated customer output;
- references drive the process instead of supporting a phase;
- inventories are broader than the pilot scope;
- owners, boundaries, or source-of-truth locations are guessed;
- history files contain generated content with no real evidence;
- repo-local truth is centralized for convenience;
- the output is described as mature before real writeback and calibration exist.

## Verification

Before finishing, confirm:

- [ ] Runtime inputs, target paths, and method repo source are recorded when runtime-driven.
- [ ] A first valuable workflow and success signal are explicitly named.
- [ ] Pilot-scope sources, repos, workflows, and owners are inventoried.
- [ ] Intended artifacts are classified into scaffold / confirm / grow-later.
- [ ] `JARVIS_HOME/SKILL.md` is valid and runtime-linkable.
- [ ] Only the minimum high-leverage skills are bootstrapped.
- [ ] A human confirmation pass or unresolved-field report exists.
- [ ] Shadow pilot and controlled writeback paths are explicit.
- [ ] Calibration can produce either `no_skill_gap` or a scoped skill/reference update.
- [ ] Private company lessons are promoted to generic methodology only through redacted patterns.
