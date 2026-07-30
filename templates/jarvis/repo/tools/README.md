# Tools and Runtime Foundation index

This directory owns reusable Jarvis-specific tools, including the Runtime Foundation needed to make this Jarvis discoverable and maintainable in each supported Runtime Environment.

## Required Runtime Foundation entries

Jarvis Runtime Foundation work must implement or point to stable entries and record them here:

| Environment | bootstrap | quick sync | full sync | doctor | scheduler adapter | state/log | Evidence | State |
|---|---|---|---|---|---|---|---|---|
| Host/native | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| Formal Docker | UNRESOLVED | same inner job | same inner job | same inner doctor | host adapter → release `runtime-job` helper | persistent Agent HOME | UNRESOLVED | unresolved |

The stable inner commands are Docker-unaware. The Scheduler Adapter owns native-direct versus host-to-container invocation. A temporary bootstrap checkout is never the long-term invocation path.

For each entry document source owner, install/update/rollback behavior, permissions, secret boundary and behavioral verification. Use `pending-runtime-foundation` when required implementation is missing; prose cannot be `verified`.

Before this Jarvis claims its Foundation is implemented, add an executable `tools/verify-runtime-foundation`. It must support the read-only invocation:

```text
tools/verify-runtime-foundation --static --json
```

The result uses `schema_version: 1`, `status: pass|fail`, and names these capabilities with a Jarvis-relative source `entry`, `verified: true|false`, and non-empty `evidence`: `bootstrap`, `quick_sync`, `full_sync`, `discovery_sync`, `maintenance`, `self_improve`, `doctor`, `recovery`, `scheduler_adapter`. It also verifies the boolean boundaries `runtime_jobs_docker_unaware`, `box_workspace_owned_separately`, and `box_task_state_untouched`.

This is a source-level gate, not runtime state. Formal runtime onboarding must still run the installed doctor, actual Agent discovery and host-to-container scheduler probes in the target environment.

## Other Jarvis tools

| identity | owner | source | purpose | stable entry | permissions/secret boundary | verification | State |
|---|---|---|---|---|---|---|---|
| none yet | — | — | — | — | — | — | — |

## Boundaries

- Keep repo-local execution tools in their code repositories.
- Do not copy jarvis-box implementation or its operator runbook here.
- Do not store credentials, tokens or private Agent state.
- Prefer small, single-purpose, dependency-light tools.
- Preserve the prior verified Runtime Foundation when an update fails.
