# Reconciliation Gate and workflow construction

You own the route-scoped handoff between delivered Jarvis knowledge, repo-local execution knowledge and formal runtime onboarding. Follow `work/reconciliation.md` and keep one Jarvis repo writer.

## Verify inputs

Read the Jarvis construction card and every repository card required by the selected workflow. Re-resolve canonical remotes, exact commits, review/merge state and repo-local entry paths. A card saying `completed` is not enough when its remote ref or entry cannot be fetched.

Select the smallest customer-approved route scope that can produce a useful workflow. Record all excluded repos, modules, sources and history as explicit coverage boundaries.

## Reconcile ownership

- Jarvis modules retain capability semantics and `what`.
- Cross-cutting retains `why inspect next` and first proof.
- Jarvis source routes retain authority/access contracts.
- Repo-local entries retain repository-specific `where/how/test`.
- Workflow retains the customer-specific cross-source/repo/role closure.

Replace `pending Repository learning` only when the delivered entry exists at the pinned repo commit. Do not copy repo implementation details into Jarvis.

## Re-run routing

Using real customer artifacts, verify:

```text
Jarvis entry
  → module/source
  → first proof
  → required repo-local entry
  → repo verification surface
```

Record expected route, observed route, mismatch, correction and rerun evidence. Unresolved routes remain blockers or exclusions for this scope.

## Construct the workflow

Customize one starter workflow with the customer's actual:

- START artifact and intake rules;
- roles, identities and authorization checkpoints;
- source and Jarvis routing;
- repo-local execution handoffs;
- branch, review, test, CI, release and acceptance policy;
- VERIFY evidence and END/writeback closure.

Run at least one controlled or real case through `START → WORK → VERIFY → END` at the pinned revisions. The workflow becomes `verified` only when the required Jarvis/repo refs are delivered and that case passes.

Re-run the deterministic Jarvis verifier with `--require-runtime-foundation`. Its Jarvis-owned static verifier must resolve real implementation entries and pass all capability/boundary checks. A Part 1 structural pass or an `implemented` table row is not enough. Keep formal Docker discovery, persistence and scheduler transport as Part 4 evidence.

## Close the gate

Update `work/reconciliation.md` with pinned refs, route scope, probe/case evidence, unresolved coverage, delivered workflow commit/PR/MR, blocker and `Next`. A delegated worker reports the verified card to the Coordinator; only the Coordinator updates `CONSTRUCTION-JOURNAL.md`.

Passing the gate authorizes Part 4 for the named workflow and exact delivered refs. It does not claim that unrelated sources/repos are complete or that a future supervised business task has already succeeded.
