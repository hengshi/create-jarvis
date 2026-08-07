# Construction journey model

This is the stable logical model for constructing a customer Jarvis. Change it only when review finds a logical error, not to match a temporary implementation detail.

## Owners

```text
create-jarvis
  owns method, templates, gates and recovery protocol

jarvis-build/ Construction Workspace
  owns this journey's context, work cards, checkpoints and evidence

<company>-jarvis
  owns customer knowledge, cross-runtime constitution, routes and workflows

customer code repositories
  own their repo-local execution knowledge

jarvis-box
  owns the formal runtime implementation, control plane, state and runbook
```

These boundaries are complementary. In particular, Company `runtime-governance.md` is the customer's constitution across Host Agents and managed runtimes. It does not compete with or duplicate jarvis-box's injected execution contract, control plane or operator runbook.

## Journey

```text
customer request
  → select new or resume
  → Construction Workspace
  → Part 1: Company repository initialization
  ├→ Part 2: Company construction
  └→ Part 3: one customer-launched top-level Codex process per code repository
  → Reconciliation Gate
  → Part 4: jarvis-box install, start and onboarding
  → supervised shadow
  → active
```

Part 1 establishes the target and minimum versioned skeleton. Parts 2 and 3 may then proceed concurrently because their write targets are disjoint. Part 4 requires a verified reconciliation and at least one route-scoped workflow at `construction-ready`.

## Work ownership

| Work | Writer | Primary target | Read-only evidence |
|---|---|---|---|
| Coordination | Coordinator | Construction Workspace | all authorized pointers |
| Part 1 | Company repo writer | Company repo and approved remote | templates, build context |
| Part 2 | Company integrator | Company repo/remote and customer-approved Host runtime foundation targets | customer docs, repos, work systems, unapproved Host locations |
| Part 3 | one customer-launched top-level Codex writer per repo | that customer repo, its card directory and approved remote | Company routes, episode sources |
| Reconciliation | Coordinator or Company integrator | Company repo and reconciliation card | delivered Company/repo refs |
| Part 4 | Coordinator | deployment target and onboarding card; Company governance only with writer ownership | immutable delivered refs, public jarvis-box release |

A Company scanner may return an evidence packet but cannot edit the Company target. Repositories can be learned in parallel, but a single repo cannot have concurrent writers. Unknown writer ownership is a blocker, not permission to launch a duplicate.

## Runtime governance lifecycle

The Company template must contain runtime-governance scaffolding in Part 1. Part 2 turns it into an executable, customer-specific constitution:

```text
template scaffold
  → discover actual customer runtime and constraints
  → decide and publish customer-specific rules
  → install any required Host runtime foundation
  → verify the behavior and record evidence
```

The constitution covers the customer's equivalent of canonical runtime root, repository cache, disposable task workspace, environment and state storage, task-start sync, stable tools, checkout isolation, handoff and cleanup. Names and paths are discovered; HENGSHI-specific paths must not be copied into another customer.

Every governed behavior is one of:

- `unresolved`: template question not yet answered;
- `documented`: customer rule is evidence-backed but needs no installed mechanism;
- `implemented`: required mechanism exists but has not completed verification;
- `verified`: behavior was observed and evidence is linked;
- `pending-runtime-foundation`: the rule depends on a missing customer runtime mechanism.

This maturity is content evidence, not a machine phase engine.

## Dispatch

The Coordinator directly owns Parts 1, 2, reconciliation and Part 4. Repository Learning uses a clean-process handoff because one repository is one coherent, context-heavy outcome:

- prepare one repository card and deterministic launch command at a time by default;
- require the customer to start that command in a new terminal;
- disable multi-agent tools for the primary repository writer;
- never reuse one Codex chat/process for another repository;
- let the worker update only its repository and card directory;
- let the Coordinator alone update the journal and accept the remote delivery.

The customer action is intentionally small: run one command, then return to the original Coordinator and reply `继续`. Session handles remain optional recovery hints. A process that ends may be replaced from the last verified card checkpoint; an unknown live writer still blocks replacement.

## Reconciliation Gate

The gate verifies actual delivery facts rather than trusting progress prose:

1. Company repo remote, commit and publication state exist;
2. required repo-local entries resolve at delivered refs;
3. Company routes preserve `what/why/where first`, while repo-local assets preserve `how`;
4. Company → module/source → repo-local routing probes pass for the selected scope;
5. unresolved repositories and history remain explicit;
6. at least one workflow has customer-specific START, WORK, VERIFY and END behavior and passes a controlled or real case.

Passing a narrow route scope does not claim the entire company or repository fleet is complete.

## Formal runtime boundary

Part 4 consumes canonical remotes, immutable commits and the jarvis-box public release interface. jarvis-box supplies its own execution contract, control plane, runtime state and operator procedures. create-jarvis supplies the construction and onboarding method; Company Jarvis supplies customer policy and knowledge.

Installation may reveal stable facts that complete or correct Company runtime governance. Such facts can be written back with evidence. jarvis-box internals are never copied into Company Jarvis.

## Evidence maturity

Workflow maturity remains:

```text
draft-template → construction-ready → runtime-deployed
               → ready-for-shadow → shadowing → active
```

These labels describe evidence attached to versioned content. They do not require a new scheduler, daemon, heartbeat or workflow-state service.
