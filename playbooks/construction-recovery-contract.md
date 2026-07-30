# Construction recovery contract

Customer Jarvis construction is expected to pause between conversations, machines, Agents and customer approvals. Recovery is therefore part of the normal method, not an exceptional failure path.

## Durable recovery surface

The named Construction Workspace is the only journey state location:

```text
jarvis-build/
├── CONTINUE-JARVIS.md
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── work/
│   ├── jarvis-repo-initialization.md
│   ├── jarvis-construction.md
│   ├── repositories/<repo>.md
│   ├── reconciliation.md
│   └── jarvis-box-onboarding.md
└── evidence/
```

The files are human- and Agent-readable evidence. They do not define a JSON schema, state machine, scheduler, daemon or heartbeat.

The Coordinator is the single writer for `CONSTRUCTION-JOURNAL.md`. A delegated worker updates only its own card and evidence, then reports the verified pointer to the Coordinator. This prevents parallel repository tasks from racing on the journal.

## Required work-card fields

Every work card records:

- objective and completion gate;
- authorized inputs;
- allowed writes;
- target repository, workspace and branch;
- writer identity or role;
- optional provider/session handle;
- status;
- last verified checkpoint and evidence pointer;
- delivered artifacts and remote refs;
- blocker;
- `Next` action;
- last verified time.

The provider/session handle is a reattachment hint only. A process identifier or stale session record does not prove that the writer is alive or still owns the target.

## Checkpoint rule

A checkpoint is valid only when its material fact can be reverified. Examples include:

- a file exists and its content/revision matches the card;
- a Git branch or commit exists locally and at the recorded remote;
- a PR/MR URL resolves to the recorded head;
- a customer approval is linked;
- a jarvis-box release checksum or image digest was verified;
- a service status or capability probe was observed and evidence saved.

“Agent said it finished” is not a checkpoint. Record the last verified fact before the next action, not an aspirational percentage.

## Recovery algorithm

1. Read `CONTINUE-JARVIS.md` from the customer-named workspace.
2. Materialize create-jarvis at the recorded method commit. Do not silently upgrade it.
3. Read `CONSTRUCTION-JOURNAL.md`, `BUILD-CONTEXT.md` and the current work card.
4. Run the pinned method's `scripts/verify_construction_workspace.py --workspace <path>` structural check, then verify current files, Git worktrees, remote refs, PR/MR state, customer approvals and jarvis-box state referenced by the card.
5. Determine the prior writer state using provider-native inspection when available.
6. Reattach if the writer is live. Replace it only when it is known to have ended.
7. If ownership is unknown, block a duplicate writer and ask only for the information or authority needed to resolve ownership.
8. Resume from the last verified checkpoint's `Next`, not from the beginning and not from unverified prose.
9. Update the work card before pausing, handing off or completing; the Coordinator then updates the journal from the verified card.

## Writer invariants

- One writer owns the Jarvis target at a time across Parts 1, 2 and reconciliation.
- Each customer code repo has at most one learning writer at a time.
- Evidence scanners may run concurrently, but they write only task-local packets under `evidence/`.
- Part 4 has one deployment/onboarding writer for a deployment target.

When a writer changes, the outgoing or recovering Coordinator records the new owner and a verified checkpoint first. Do not infer permission to replace a writer from silence.

## Customer recovery phrase

Provide this sentence when a journey may pause:

> 继续构建我们的 Jarvis。建设工作区是 `<path>/jarvis-build`。请读取 `CONTINUE-JARVIS.md` 和 `CONSTRUCTION-JOURNAL.md`，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。

The workspace path is required. The Agent must not search the customer's home or unrelated directories to guess it.

## Honest stopping states

A pause is safe when the current card contains a verified checkpoint and a concrete `Next`. A blocked card names the missing approval, access, material or runtime foundation. A completed card links the delivered and verified facts that satisfy its gate.

No method instruction may claim background survival, automatic retry or native session resume unless the current Host provider actually supplies and verifies that behavior.
