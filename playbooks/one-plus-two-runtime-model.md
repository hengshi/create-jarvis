# Construction Coordinator + two work lanes

Customer Jarvis construction may read many repositories, documents and years of history. The method therefore separates continuity ownership from work ownership without inventing a scheduler.

```text
Construction Coordinator
  ├─ BUILD-CONTEXT.md
  ├─ CONSTRUCTION-JOURNAL.md
  ├─ RUN-COMPANY-JARVIS-CONSTRUCTION.md → Company construction lane
  └─ RUN-REPOSITORY-LEARNING.md         → Repository learning lane
```

The Coordinator is the Agent that received the customer's journey request. It remains responsible after Preparation: dispatch, recovery, reconciliation, workflow construction, formal deployment handoff and shadow promotion all have an owner.

## Preparation

Preparation records what artifacts exist, where they are, what is currently accessible, which revisions were observed and how each target may be written or delivered. It does not infer company taxonomy or learn repository history.

The Coordinator writes two self-contained RUN contracts so each lane can work without asking the customer to repeat paths, scope or policy.

## Dispatch

- If the current Agent supports native subagents, dispatch the two lanes concurrently.
- If it does not, execute the two RUN contracts sequentially. Preserve role and write boundaries; do not claim the same conversation became an isolated context.
- A Company scanning worker may return evidence packets, but only the Company integrator writes the Company target.
- A Repository learning coordinator may shard different repos, but one repo has only one writer at a time.

The customer never has to start two terminals. `START-HERE.md` exists only when a concrete provider-native child invocation is required for recovery.

## Progress and recovery

The Company lane maintains `COMPANY-JARVIS-PROGRESS.md`. The Repository lane maintains one `REPOSITORY-LEARNING-PROGRESS.md` for every repo:

```markdown
| Repository | History range | Status | Last episode | Delivery ref | Next |
|---|---|---|---|---|---|
```

`CONSTRUCTION-JOURNAL.md` is written only by the Coordinator and contains:

- method commit;
- construction workspace;
- the two progress pointers;
- delivered remote/commit/PR/MR pointers;
- deployment pointer if one exists;
- last verified time;
- current blocker and next action.

The journal is an index, not the truth it points to. Resume always revalidates remote refs, files and access. It has no parser, transition service, heartbeat or per-repo state files.

Before yielding, changing lane or ending a session, update the current lane progress and journal pointer. A new Agent resumes from those files. Process survival is not promised.

## Write and delivery boundaries

| Role | May write | Read only |
|---|---|---|
| Coordinator/Preparation | construction task directory | authorized artifacts |
| Company lane | Company target, confirmed remote, Company progress, evidence packets | customer repos/docs/work systems |
| Repository lane | repo targets permitted by per-repo policy, Repository progress, replay evidence | Company target, docs/work systems |

Each lane must turn accepted changes into consumable Git facts. A result may be merged/approved, candidate PR/MR, read-only evidence or blocked; it may not hide behind an unexplained dirty worktree.

## After 1+2

The Coordinator verifies delivered refs, reconciles Company routes with repo-local entries, builds customer workflows, and decides the smallest route-scoped boundary that is ready for deployment. Remaining repository history may continue on new refs without mutating a deployed snapshot.

Workflow maturity is:

```text
draft-template → construction-ready → runtime-deployed
               → ready-for-shadow → shadowing → active
```

No daemon or new workflow-state service is required; these labels describe evidence attached to versioned content.
