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
