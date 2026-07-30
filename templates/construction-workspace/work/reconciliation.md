# Work card: Reconciliation Gate

- Objective: reconcile delivered Jarvis and repo-local knowledge and prove a route-scoped workflow verified
- Completion gate: exact delivered refs resolve, routing probes pass and at least one customer-specific workflow passes a controlled or real case
- Authorized inputs: Jarvis and repository delivery refs, build context, work-card evidence
- Allowed writes: Jarvis target/approved remote, this card, task-local evidence
- Target repository: `unresolved`
- Target workspace: `unresolved`
- Target branch: `unresolved`
- Writer: `unassigned`
- Provider/session handle: `none`
- Status: `waiting-for-construction`
- Last verified checkpoint: `none`
- Delivered artifacts: `none`
- Evidence: `none`
- Blocker: `waiting for route-scoped Parts 2 and 3 deliveries`
- Next: `Select the smallest customer-approved route scope`
- Last verified: `{{CREATED_AT}}`

Method: `playbooks/prompts/reconciliation.md` from the pinned create-jarvis commit.

## Checkpoints

- [ ] Required Jarvis and repo-local remote refs resolve
- [ ] Pending handoffs are replaced only where real entries exist
- [ ] Jarvis-to-repo routing probes pass
- [ ] Incomplete fleet/history boundaries remain explicit
- [ ] One workflow has customer-specific START, WORK, VERIFY and END
- [ ] One controlled or real case passes at pinned revisions
