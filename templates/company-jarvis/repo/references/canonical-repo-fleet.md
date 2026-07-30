# Canonical Repo Fleet

**Status**: binding scaffold | **Maturity**: `unresolved`

## Authority

Confirmed source routes and their current remote/VCS metadata are authoritative for repository identity, access entry, default branch and revision. Runtime caches are materialization surfaces, not alternate repository identities.

## Repository inventory

### Confirmed scope

{{REPO_INDEX}}

### Details

| Repository | Canonical remote/source route | Capability/surface role | Default branch evidence | Access state | repo-local entry | Initial routing |
|---|---|---|---|---|---|---|
| UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

Before the current declared Company knowledge scope closes, replace the placeholder with all authorized repos. A repo may be a contract authority, execution owner, delivery, docs/operational or verification surface. Do not reduce these relations to “primary/secondary repo.”

When repo-local knowledge has not delivered an entry, write `pending repo-local entry`; never invent a future path.

## Materialization surfaces

Record how each execution surface obtains the canonical fleet. Paths and commands come from observed customer/runtime contracts, not examples.

| Surface | Resolver/sync entry | Cache location and mode | Task workspace rule | Evidence | State |
|---|---|---|---|---|---|
| Host construction | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| ordinary authorized checkout | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| formal managed runtime | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |

The Company runtime constitution owns cross-surface rules. jarvis-box or another managed runtime owns its own cache/workspace implementation and exposes observable behavior through its public interface.

## Fleet rules

- Resolve default branches from live remote HEAD or VCS metadata; do not hard-code names or trust the current checkout branch.
- Perform edits only in an explicitly authorized working tree/workspace.
- Treat a declared read-only cache as read-only.
- Record exact remote and commit for delivery, reconciliation and deployment.
- The customer Host runtime foundation owner creates and verifies any required sync mechanism or marks it `pending-runtime-foundation`.
- Formal runtime onboarding records observed managed-runtime resolution without copying runtime internals.

## Completion gate

- Every authorized repo has evidence-backed identity, role, access, default branch, repo-local entry state and routing relation.
- Host and formal runtime materialization entries have evidence states consistent with `runtime-governance.md`.
- Missing mechanisms and inaccessible repos have an owner, blocker and recovery action.
