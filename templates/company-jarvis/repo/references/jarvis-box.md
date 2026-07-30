# jarvis-box integration boundary

**Status**: reference scaffold | **Maturity**: `unresolved`

jarvis-box is the formal managed runtime used after a customer workflow becomes `construction-ready`. It does not perform initial Company/repository construction.

## Ownership boundary

jarvis-box owns:

- runtime binaries and packaged toolchain;
- injected execution contract;
- Task/Run control plane, workspaces, logs and state;
- Company snapshot and repo materialization mechanics;
- diagnostics, update/rollback and operator runbook;
- selected connector integration.

Company Jarvis owns customer knowledge, routing, workflows and the cross-runtime constitution. This file records only customer-visible integration facts and pointers; it does not reproduce jarvis-box commands, internal lifecycle rules, environment variables or runbook content.

## Construction and deployment boundary

Company/repository construction and reconciliation run from the customer-authorized Host Agent without jarvis-box. Formal runtime onboarding uses a verified public release bundle and public runtime interface to:

1. pin the Company and required repo-local commits;
2. pin a released OCI image digest and bundled component versions;
3. activate a separate formal high-authority identity;
4. install and start the service;
5. run container-side Agent, source, routing and read/write probes;
6. create an immutable deployment lock and enter `ready-for-shadow`.

## Observed customer integration

Fill this table during formal runtime onboarding from the installed release and live probes.

| Fact | Observed value/pointer | Evidence | State |
|---|---|---|---|
| public release source and version | UNRESOLVED | UNRESOLVED | unresolved |
| public operator documentation | UNRESOLVED | UNRESOLVED | unresolved |
| deployment owner/home | UNRESOLVED | UNRESOLVED | unresolved |
| pinned image digest | UNRESOLVED | UNRESOLVED | unresolved |
| Company snapshot commit/digest | UNRESOLVED | UNRESOLVED | unresolved |
| required repo refs | UNRESOLVED | UNRESOLVED | unresolved |
| formal identity/authority boundary | UNRESOLVED | UNRESOLVED | unresolved |
| connector boundary | UNRESOLVED | UNRESOLVED | unresolved |
| deployment lock | UNRESOLVED | UNRESOLVED | unresolved |
| current workflow maturity | UNRESOLVED | UNRESOLVED | unresolved |

Use the installed release's own public help and operator documentation for commands and recovery. If this file conflicts with live installed behavior, stop, use the runtime-owned source for operations, and update only the customer integration facts here with evidence.

## Governance

- Read [runtime-governance-quick.md](runtime-governance-quick.md) for the cross-runtime preflight.
- Read [runtime-governance.md](runtime-governance.md) for customer paths, sync, tools, authority, handoff and cleanup.
- Read [canonical-repo-fleet.md](canonical-repo-fleet.md) for canonical repository identities and materialization boundaries.
