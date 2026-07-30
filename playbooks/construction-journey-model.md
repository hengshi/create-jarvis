# Construction journey model

`GOAL.md` is the sole ownership model. This playbook describes how the Construction Coordinator advances and resumes one customer journey.

## Start and preparation

The first request authorizes only the public create-jarvis clone. Explain why Jarvis needs documentation/code/work-system pointers: they recover intent, routing, evidence and operating rules. Let the customer start with one pilot and add sources later. Probe only supplied pointers and request additional filesystem/runtime access explicitly.

Create `jarvis-build/` and pin the method commit. Its Markdown cards and journal are recovery facts, not runtime state or a parser contract.

## Four parts

```text
Part 1  Jarvis repo initialization
  ├→ Part 2  knowledge + Runtime Foundation
  └→ Part 3  one independent learning task per code repo
      → reconciliation of one usable route
      → Part 4 formal Docker bootstrap, jarvis-box and onboarding
```

Part 1 establishes the Git target and unresolved scaffold. Parts 2 and 3 may proceed concurrently because they have different write targets. Reconciliation verifies remote refs and behavior. Part 4 begins when one end-to-end route and the Jarvis Runtime Foundation implementation are verifiable; it does not require a lifecycle label.

## Work ownership

- one writer for Jarvis initialization;
- one Jarvis integrator in Part 2; scanners submit evidence packets;
- one writer per code repo in Part 3;
- one Part 4 operator/coordinator;
- no duplicate writer when the previous writer's liveness is unknown.

Every card records objective, authorization, write target, writer, last verified checkpoint, delivery, blocker and `Next`. Before pause, replacement or completion, update the card and journal.

## Part 1 result

The Jarvis repo is created from `templates/jarvis/`, verified and published. `runtime-governance.md` exists as unresolved constitutional structure. Starter workflows are `unverified`; file existence proves no customer behavior.

## Part 2 result

Evidence-backed modules, sources, repo fleet, cross-cutting relations, workflows and references are published. Runtime governance names each Runtime Environment's Agent HOME/discovery roots and the Jarvis repo supplies verified or precisely pending Runtime Foundation entries: bootstrap, sync, doctor, state/log and Scheduler Adapter.

Part 2 never solves a missing foundation by making jarvis-box clone/mount/inject Jarvis.

## Part 3 result

Each code repo independently mines complete historical episodes. Missing original problems are reconstructed by a context-isolated Agent with provenance/uncertainty; Replay Agent sees only the visible START and cutoff evidence. Only behavior-improving repo-local deltas are published.

## Reconciliation result

One selected route proves:

```text
Jarvis entry → module/source first proof → real repo-local entry → verified workflow behavior
```

Pending pointers are replaced only with delivered refs. Incomplete routes remain explicit and do not block unrelated usable routes.

## Part 4 result

- pinned public jarvis-box release/image;
- persistent formal Agent HOME and independent identity;
- Jarvis Runtime Foundation bootstrapped inside the Docker Runtime Environment;
- actual Runtime Agent discovery probe passes;
- host Scheduler Adapter invokes Docker-unaware inner jobs through the release helper;
- jarvis-box mechanics/providers/persistence pass generic probes;
- first supervised task is completed or has an exact blocker/Next.

These facts live in their owning state/log and the construction work card. No context/lock/readiness manifest is created.

## Recovery routing

- unfinished construction → current Construction Workspace card;
- sync/maintenance/self-improve failure → Runtime Foundation state/log;
- host cannot enter container → host scheduler/operator log;
- Task/Run failure → jarvis-box control plane/state;
- connector/provider failure → owning operator surface.

Always reverify external facts before resuming. A session handle is never proof that work or ownership still exists.
