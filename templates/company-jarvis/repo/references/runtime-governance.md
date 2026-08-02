# Runtime governance — customer cross-runtime constitution

**Status**: binding scaffold | **Maturity**: `unresolved`

This document defines how this company's Host Agents and formal managed runtimes find canonical assets, create isolated work, synchronize durable knowledge, hand off execution and close safely. It is owned by the Company Jarvis repo.

It is not a copy of any runtime's internal execution contract, control plane or operator runbook. A runtime such as jarvis-box implements its own mechanics and must comply with the customer-level boundaries recorded here through its public behavior.

## 1. Maturity and evidence

This scaffold begins unresolved. The Company knowledge owner must replace unresolved rows from observed customer facts and establish any required Host runtime foundation. Formal runtime onboarding may add stable managed-runtime facts observed through the public runtime interface.

Use only these evidence states:

| State | Meaning |
|---|---|
| `unresolved` | the constitutional question has not been answered |
| `documented` | an evidence-backed rule needs no installed mechanism |
| `implemented` | the required mechanism exists but verification is incomplete |
| `verified` | behavior was observed and a revisitable evidence pointer is recorded |
| `pending-runtime-foundation` | the rule depends on a missing customer runtime mechanism |

Do not mark prose `verified`. A command, tool or sync behavior is verified only after it runs in the intended context and its result is recorded.

## 2. Runtime surfaces

| Surface | Purpose | Canonical entry | Owner | Evidence | State |
|---|---|---|---|---|---|
| Host construction runtime | build and evolve customer assets before formal deployment | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| Ordinary authorized checkout | customer-directed work outside a managed Task | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |
| Formal managed runtime | operate deployed Company/repo snapshots | UNRESOLVED | UNRESOLVED | UNRESOLVED | unresolved |

An ordinary Agent conversation is legal when the customer authorized its checkout and scope. Do not invent managed Task/Run identity when no runtime injected it.

## 3. Canonical runtime root and storage roles

Record the customer's real equivalents. Do not copy paths from another company.

| Role | Canonical location or resolver | Mutability | Owner | Evidence | State |
|---|---|---|---|---|---|
| runtime root | UNRESOLVED | policy-defined | UNRESOLVED | UNRESOLVED | unresolved |
| Company Jarvis checkout/snapshot | UNRESOLVED | policy-defined | UNRESOLVED | UNRESOLVED | unresolved |
| repository cache | UNRESOLVED | cache only | UNRESOLVED | UNRESOLVED | unresolved |
| disposable task workspace/worktree | UNRESOLVED | task-scoped | UNRESOLVED | UNRESOLVED | unresolved |
| environment/config | UNRESOLVED | operator-managed | UNRESOLVED | UNRESOLVED | unresolved |
| runtime state/logs | UNRESOLVED | runtime-managed | UNRESOLVED | UNRESOLVED | unresolved |
| construction/replay evidence | UNRESOLVED | journey/task-scoped | UNRESOLVED | UNRESOLVED | unresolved |

Repository cache is not an editing target unless a customer-specific contract explicitly says otherwise. Runtime-managed state, environment and credential locations are never edited as ordinary source files.

## 4. Task-start synchronization

Before durable work starts, the active surface must resolve current Company knowledge, repository identities and stable tools through a customer-owned synchronization contract.

| Obligation | Entry/tool | Failure behavior | Evidence | State |
|---|---|---|---|---|
| materialize/synchronize Company Jarvis | UNRESOLVED | stop or use explicitly pinned snapshot | UNRESOLVED | unresolved |
| materialize/synchronize canonical repo fleet | UNRESOLVED | report unavailable repos; do not guess paths | UNRESOLVED | unresolved |
| resolve stable company tools | UNRESOLVED | mark required tool unavailable | UNRESOLVED | unresolved |
| report resolved revisions | UNRESOLVED | block writes when truth is ambiguous | UNRESOLVED | unresolved |

If a required sync entry or stable tool does not exist, the customer runtime foundation owner creates, installs and verifies the smallest customer-owned mechanism or marks it `pending-runtime-foundation`. Company Jarvis records the contract and source; it does not copy a runtime-owned implementation.

## 5. Checkout and workspace isolation

- Canonical checkouts and caches establish identity and revision truth; task edits occur only in an explicitly authorized working tree/workspace.
- A target has one writer at a time. Scanners return evidence packets and do not concurrently edit a shared target.
- Default branches come from the current remote/VCS source, not a hard-coded branch or the current checkout name.
- Existing customer changes are preserved. New work uses the customer's branch/worktree policy and never force-overwrites history.
- Host construction paths are not production snapshot identifiers. Formal deployment consumes canonical remotes and exact commits.

| Rule | Customer-specific decision | Evidence | State |
|---|---|---|---|
| canonical checkout/cache use | UNRESOLVED | UNRESOLVED | unresolved |
| task workspace/worktree creation | UNRESOLVED | UNRESOLVED | unresolved |
| branch and review policy | UNRESOLVED | UNRESOLVED | unresolved |
| concurrent writer detection | UNRESOLVED | UNRESOLVED | unresolved |
| cleanup/retention | UNRESOLVED | UNRESOLVED | unresolved |

## 6. Stable tools and ownership

Company-specific tools are indexed in `tools/README.md`. For every required tool record:

- stable invocation path or resolver;
- source owner and installation owner;
- install, sync, upgrade and rollback boundary;
- required identity/permissions and secret boundary;
- verification command or behavior;
- evidence state.

Do not depend on a temporary construction checkout as the long-term invocation path. Do not copy tools already owned by jarvis-box or another runtime; record their public entry and responsibility boundary instead.

## 7. Credentials and authority

- Credentials, Agent login state, private resume handles and runtime state never enter Company/repo artifacts or Construction Workspace files.
- Host construction uses the customer's explicitly authorized identity.
- Native formal runtime uses the existing installing OS user. Docker imports only approved portable credentials from the current Host user into a separate persistent runtime.
- A dedicated machine account is an optional customer authority decision, not an installation prerequisite. Every selected identity remains auditable, rotatable and revocable.
- Docker socket, Host home and Host SSH agent access are never implicit. Docker socket access is host-root-equivalent.
- Provider-native IM credentials remain inside the connector boundary.

| Authority decision | Customer rule | Evidence | State |
|---|---|---|---|
| Host Agent scope | UNRESOLVED | UNRESOLVED | unresolved |
| formal Agent scope | UNRESOLVED | UNRESOLVED | unresolved |
| cross-target writeback | UNRESOLVED | UNRESOLVED | unresolved |
| host-root-equivalent capability | UNRESOLVED | UNRESOLVED | unresolved |

## 8. Handoff and recovery

A durable handoff records only revisitable facts needed to continue:

- task or work-card identity;
- authorized target and current working tree/workspace;
- exact source/repository revisions;
- last verified checkpoint and evidence;
- delivered branch/commit/PR/MR or deployment lock;
- blocker and concrete `Next`.

Provider/session handles are private hints, not durable truth. Reattach a live writer; replace only a writer known to have ended. Unknown ownership blocks a duplicate writer.

| Handoff behavior | Customer entry | Evidence | State |
|---|---|---|---|
| construction journey recovery | external `jarvis-build/CONTINUE-JARVIS.md` | UNRESOLVED | unresolved |
| ordinary checkout handoff | UNRESOLVED | UNRESOLVED | unresolved |
| formal managed-runtime handoff | UNRESOLVED | UNRESOLVED | unresolved |

## 9. Cleanup and closure

Before closure:

1. verify the exact target and write boundary;
2. record commands/actions actually executed and their results;
3. publish or explicitly disposition local changes;
4. retain required evidence and remove only task-owned disposable work according to policy;
5. record unexecuted items, blockers and `Next`;
6. never edit runtime state or fabricate events to hide an error.

| Cleanup obligation | Customer mechanism | Evidence | State |
|---|---|---|---|
| disposable workspace cleanup | UNRESOLVED | UNRESOLVED | unresolved |
| stale branch/worktree handling | UNRESOLVED | UNRESOLVED | unresolved |
| evidence retention/redaction | UNRESOLVED | UNRESOLVED | unresolved |
| runtime state/log retention | UNRESOLVED | UNRESOLVED | unresolved |

## 10. Formal managed-runtime integration

The formal runtime owns its binaries, injected execution contract, control plane, Task/Run state, diagnostics and operator runbook. This constitution records only customer-level integration facts observed through the public interface:

| Fact | Observed value | Evidence | State |
|---|---|---|---|
| public release/operations entry | UNRESOLVED | UNRESOLVED | unresolved |
| deployment mode: Native or Docker | UNRESOLVED | UNRESOLVED | unresolved |
| runtime owner and actual runtime root | UNRESOLVED | UNRESOLVED | unresolved |
| release version and Docker image digest when applicable | UNRESOLVED | UNRESOLVED | unresolved |
| credential discovery/import boundary and capability evidence | UNRESOLVED | UNRESOLVED | unresolved |
| Runtime Foundation doctor and real Agent discovery | UNRESOLVED | UNRESOLVED | unresolved |
| provider writeback and Task workspace cleanup | UNRESOLVED | UNRESOLVED | unresolved |
| optional connector boundary | UNRESOLVED | UNRESOLVED | unresolved |

Use the installed runtime's own public help and operator documentation for operations. Do not reproduce internal command catalogs here. A service restart does not imply continuation of old work; recovery follows observed runtime state and the runtime-owned runbook.

## Completion gate

This constitution is customer-specific only when:

- every applicable obligation has a customer decision and revisitable evidence;
- required Host runtime mechanisms are installed and verified, or explicitly `pending-runtime-foundation` with an owner and recovery action;
- paths and tool names belong to this customer rather than another company's example;
- Host, ordinary checkout and formal managed-runtime boundaries are consistent;
- no credentials, private runtime state or jarvis-box internals were copied into Company Jarvis.
