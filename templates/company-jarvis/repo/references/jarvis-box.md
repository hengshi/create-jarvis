# Jarvis Box integration boundary

**Status**: reference scaffold | **Maturity**: `unresolved`

Jarvis Box is the formal execution runtime used after a customer workflow becomes `construction-ready`. It does not construct, clone, mount or interpret the customer Jarvis repo.

## Ownership boundary

Jarvis Box owns Runtime Agent execution, Task/Run, workspaces, provider/IM ingress and writeback, state/logs, cleanup and its public operator contract.

Company Jarvis owns customer knowledge, routing, workflows and cross-runtime governance. The customer Runtime Foundation owns bootstrap, sync, native Agent discovery, doctor, maintenance and Scheduler Adapter behavior.

This file records customer-visible facts and evidence only. It does not reproduce Jarvis Box commands, environment variables, Compose shape, container paths or internal lifecycle rules.

## Deployment choice

| Mode | Runtime owner | Credential behavior |
| --- | --- | --- |
| Native | existing installing OS user | reuse that user's authorized native CLI identities |
| Docker | persistent runtime inside the container boundary | import only approved portable identities from the current Host user |

A dedicated machine account is optional policy, not an installation prerequisite. Never copy Host HOME, SSH agent, Keychain, complete credential stores or token values into this repo.

## Observed customer integration

Fill this table during onboarding from the installed public release and live probes.

| Fact | Observed value/pointer | Evidence | State |
| --- | --- | --- | --- |
| public release and operator entry | UNRESOLVED | UNRESOLVED | unresolved |
| deployment mode: Native or Docker | UNRESOLVED | UNRESOLVED | unresolved |
| runtime owner | UNRESOLVED | UNRESOLVED | unresolved |
| actual runtime root/deployment home | UNRESOLVED | UNRESOLVED | unresolved |
| release version | UNRESOLVED | UNRESOLVED | unresolved |
| Docker image digest when applicable | UNRESOLVED | UNRESOLVED | unresolved |
| credential discovery/import boundary | UNRESOLVED | UNRESOLVED | unresolved |
| Runtime Foundation doctor | UNRESOLVED | UNRESOLVED | unresolved |
| real Agent discovery | UNRESOLVED | UNRESOLVED | unresolved |
| provider or IM writeback | UNRESOLVED | UNRESOLVED | unresolved |
| workspace/external-resource cleanup | UNRESOLVED | UNRESOLVED | unresolved |
| optional connector boundary | UNRESOLVED | UNRESOLVED | unresolved |
| current workflow maturity | UNRESOLVED | UNRESOLVED | unresolved |

Use the installed release's public help and customer operations manual. If this reference conflicts with live released behavior, stop and use the runtime-owned source for operations; update only observed customer facts here.

## Governance

- Read [runtime-governance-quick.md](runtime-governance-quick.md) for cross-runtime preflight.
- Read [runtime-governance.md](runtime-governance.md) for customer paths, sync, tools, authority, handoff and cleanup.
- Read [canonical-repo-fleet.md](canonical-repo-fleet.md) for canonical repository identities.
