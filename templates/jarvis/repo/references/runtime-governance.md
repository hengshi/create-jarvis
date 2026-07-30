# Runtime governance

**Status**: binding scaffold | **Maturity**: `unresolved`

This is the constitution for every Agent that uses this Jarvis. It is owned by this Jarvis repo and must be replaced with observed, customer-approved facts. It is not a jarvis-box execution contract or operator runbook; jarvis-box does not read this file.

## Evidence states

| State | Meaning |
|---|---|
| `unresolved` | the question has not been answered |
| `documented` | an evidence-backed rule requires no installed mechanism |
| `implemented` | the required mechanism exists but behavioral verification is incomplete |
| `verified` | behavior ran in the intended Runtime Environment and evidence is revisitable |
| `pending-runtime-foundation` | a required mechanism is still missing |

Prose alone is never `verified`.

## Runtime Environments

| Environment | Agent/runtime | Agent HOME | Discovery roots | Authority/identity | Evidence | State |
|---|---|---|---|---|---|---|
| Authorized Host runtime | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| Formal Docker runtime | UNRESOLVED | persistent `/root` or observed equivalent | UNRESOLVED | separate formal identity | UNRESOLVED | unresolved |

An ordinary authorized checkout is valid without a managed Task. Do not invent Task/Run identity when none exists.

## Runtime Foundation

Record the implementation owned by this Jarvis repo. Do not copy another Jarvis's paths or tool names.

| Obligation | Stable entry/location | Failure behavior | Evidence | State |
|---|---|---|---|---|
| approved Jarvis remote/ref | UNRESOLVED | reject ambiguous or unapproved source | UNRESOLVED | unresolved |
| one-time bootstrap | UNRESOLVED | leave prior working foundation intact | UNRESOLVED | unresolved |
| canonical repo cache | UNRESOLVED | report last verified revision; do not edit cache | UNRESOLVED | unresolved |
| stable command directory | UNRESOLVED | report unavailable entry | UNRESOLVED | unresolved |
| quick task-start sync | UNRESOLVED | expose stale/unavailable result | UNRESOLVED | unresolved |
| periodic full sync | UNRESOLVED | preserve previous discovery material | UNRESOLVED | unresolved |
| state directory | UNRESOLVED | fail without fabricating success | UNRESOLVED | unresolved |
| log directory | UNRESOLVED | report unwritable log boundary | UNRESOLVED | unresolved |
| doctor/discovery probe | UNRESOLVED | identify the failed layer | UNRESOLVED | unresolved |

Bootstrap and sync materialize Jarvis skills/references into Agent-native discovery roots. They do not require a permanent Jarvis mount or `JARVIS_HOME`. Stable entries must work after temporary bootstrap material is removed.

## Materialization contract

- Resolve the approved remote/ref to an exact revision and record it in Runtime Foundation state.
- Update cache and discovery material safely; a failed update leaves the prior verified material usable.
- Preserve Agent-owned files outside Jarvis-owned destinations.
- Install the Jarvis entry and required workflow/source skills for each supported Agent.
- Verify with an actual Agent discovery invocation, not only filesystem existence.
- Keep credentials, tokens and private Agent state out of the Jarvis repo and logs.

| Agent | Source paths | Discovery destinations | Update method | Verification | State |
|---|---|---|---|---|---|
| Codex | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| Claude | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |

## Runtime Jobs

Internal jobs execute inside their current Runtime Environment and are Docker-unaware.

| Job | Stable inner command | Frequency/trigger | State/log | Owner | Evidence | State |
|---|---|---|---|---|---|---|
| quick sync | UNRESOLVED | task start | UNRESOLVED | Jarvis Runtime Foundation | UNRESOLVED | unresolved |
| full sync | UNRESOLVED | periodic/manual | UNRESOLVED | Jarvis Runtime Foundation | UNRESOLVED | unresolved |
| maintenance | UNRESOLVED | customer decision | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| self-improve | UNRESOLVED | customer decision | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |

Do not put `docker compose exec/run` in these commands.

## Scheduler Adapter

| Runtime Environment | Scheduler | Outer invocation | Inner job | Launch log owner | Evidence | State |
|---|---|---|---|---|---|---|
| native | UNRESOLVED | direct stable command | UNRESOLVED | native scheduler/operator | UNRESOLVED | unresolved |
| Docker | host scheduler | jarvis-box release `runtime-job` helper | UNRESOLVED | host scheduler/operator | UNRESOLVED | unresolved |

Docker scheduling enters the formal container through the outer helper and then calls the same inner job. Full sync must use the Jarvis-defined skip-scheduler-update option so the container does not install a second scheduler. Runtime Jobs own their state/log in persistent Agent HOME; jarvis-box does not read host scheduler logs.

## Workspaces, writers and Git

- Cache establishes identity/revision truth; edits occur only in an explicitly authorized workspace.
- One writer owns a target at a time. Scanners return evidence packets.
- Resolve default branches and remotes from live VCS facts.
- Preserve customer changes and remote history.
- Publish durable changes through the target repo's Git policy.

| Rule | Decision | Evidence | State |
|---|---|---|---|
| workspace/worktree creation | UNRESOLVED | UNRESOLVED | unresolved |
| branch/review policy | UNRESOLVED | UNRESOLVED | unresolved |
| writer ownership detection | UNRESOLVED | UNRESOLVED | unresolved |
| cleanup/retention | UNRESOLVED | UNRESOLVED | unresolved |

## Credentials and authority

- Authorized Host runtime uses the customer's explicitly authorized identity.
- Formal runtime uses a separately activated, auditable, rotatable and revocable identity in persistent Agent HOME.
- Host HOME, SSH agent and credential store are not copied or mounted wholesale.
- Docker socket is host-root-equivalent and requires explicit authorization.
- Provider-native connector credentials remain in the connector boundary.
- Credentials and private resume handles never enter Jarvis/repo artifacts or external work cards.

## Handoff, cleanup and recovery

A handoff records task/card identity, authorized target, exact revisions, last verified checkpoint, evidence, delivery, blocker and `Next`. Reattach a live writer; replace only a writer known to have ended.

| Failure | Recovery owner/source | Entry | Evidence | State |
|---|---|---|---|---|
| external evolution journey interruption | external work card | customer-approved recovery entry | UNRESOLVED | unresolved |
| bootstrap/sync/job failure | Runtime Foundation state/log | UNRESOLVED | UNRESOLVED | unresolved |
| host cannot enter Docker runtime | host scheduler/operator log | UNRESOLVED | UNRESOLVED | unresolved |
| Task/Run failure | jarvis-box control plane/state | runtime-owned operator entry | UNRESOLVED | unresolved |
| provider/connector failure | owning operator surface | UNRESOLVED | UNRESOLVED | unresolved |

Do not create a cross-product context, deployment lock or readiness state to aggregate these facts.

## Completion gate

This constitution is usable only when every required Runtime Environment has evidence-backed decisions, required mechanisms are behaviorally verified or have a precise `pending-runtime-foundation` owner/action, and no credentials, foreign-customer paths or jarvis-box internals were copied into this repo.
