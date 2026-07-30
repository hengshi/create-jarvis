# jarvis-box integration boundary

jarvis-box owns Task/Run, Agent execution, control plane, persistent runtime state/workspaces/logs, generic tooling and operator mechanics. It does not clone, pull, sync, mount, validate or inject this Jarvis repo and does not read `runtime-governance.md`.

## Formal Docker runtime

The public image contains jarvis-box, selected Agent CLIs/toolchain, generic runtime skills and connector binary. It must not contain an upstream method pack, this Jarvis or this Jarvis's Runtime Foundation.

This Jarvis's Runtime Foundation is bootstrapped into the formal container's persistent Agent HOME before business ingress. Runtime Agent then discovers the installed Jarvis entry through its native discovery roots.

## Scheduler boundary

The Jarvis-owned Scheduler Adapter uses the release's `runtime-job` helper to enter the formal container and invoke an environment-native inner job. jarvis-box supplies only this generic transport helper. Inner sync, maintenance and self-improve commands remain Docker-unaware.

## Observed integration facts

Fill during first formal runtime setup from live release/runtime behavior.

| Fact | Observed value/pointer | Evidence | State |
|---|---|---|---|
| public release/version/image digest | UNRESOLVED | UNRESOLVED | unresolved |
| public operator documentation | UNRESOLVED | UNRESOLVED | unresolved |
| deployment home | UNRESOLVED | UNRESOLVED | unresolved |
| persistent Agent HOME volume | UNRESOLVED | UNRESOLVED | unresolved |
| Runtime Foundation revision/doctor | UNRESOLVED | UNRESOLVED | unresolved |
| Runtime Agent discovery probe | UNRESOLVED | UNRESOLVED | unresolved |
| host Scheduler Adapter | UNRESOLVED | UNRESOLVED | unresolved |
| formal identity/authority boundary | UNRESOLVED | UNRESOLVED | unresolved |
| provider/connector boundary | UNRESOLVED | UNRESOLVED | unresolved |
| first supervised task | UNRESOLVED | UNRESOLVED | unresolved |

Use the installed release's operator documentation for jarvis-box operations. Keep Jarvis bootstrap/sync/maintenance behavior in [runtime-governance.md](runtime-governance.md).
