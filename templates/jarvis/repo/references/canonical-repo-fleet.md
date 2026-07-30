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

Before the current declared Jarvis knowledge scope closes, replace the placeholder with all authorized repos. A repo may be a contract authority, execution owner, delivery, docs/operational or verification surface. Do not reduce these relations to “primary/secondary repo.”

When repo-local knowledge has not delivered an entry, write `pending repo-local entry`; never invent a future path.

## Checkout and execution surfaces

Record how each execution surface obtains the target repository when work actually routes there. Do not make Jarvis Runtime Foundation clone every code repository merely so the inventory looks complete.

| Surface | Repository resolver | Checkout/workspace rule | Repo-local skill discovery | Evidence | State |
|---|---|---|---|---|---|
| Authorized Host checkout | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| ordinary authorized checkout | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| formal managed runtime | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |

Jarvis Runtime Foundation syncs Jarvis knowledge into Agent discovery roots. Target code repositories remain independent: the owning runtime or operator resolves an authorized checkout/workspace, and the Runtime Agent uses that checkout's repo-local instructions/skills. For jarvis-box, Task/workspace mechanics are jarvis-box-owned and are not encoded here as Jarvis implementation details.

## Fleet rules

- Resolve default branches from live remote HEAD or VCS metadata; do not hard-code names or trust the current checkout branch.
- Perform edits only in an explicitly authorized working tree/workspace.
- Treat a declared read-only cache as read-only.
- Record exact remote and commit for delivery, reconciliation and deployment.
- Runtime Foundation must not pre-clone the whole fleet unless a separately evidenced customer rule requires it.
- First formal runtime setup records observable repository resolution and repo-local discovery without copying runtime internals.

## Completion gate

- Every authorized repo has evidence-backed identity, role, access, default branch, repo-local entry state and routing relation.
- Required execution surfaces have evidence states consistent with `runtime-governance.md`.
- Missing mechanisms and inaccessible repos have an owner, blocker and recovery action.
