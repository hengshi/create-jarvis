# Construction and runtime boundary

This file expands the runtime portion of `GOAL.md`; it cannot override that ownership model.

## Actors and owners

The Host Runtime Agent acts as Construction Coordinator. It pins the create-jarvis method, explains and requests customer inputs, maintains the Construction Workspace, coordinates writers and invokes onboarding. It is not the durable owner of sync or scheduler execution.

The Jarvis repo owns customer knowledge, `runtime-governance.md` and its Runtime Foundation. Each customer code repo owns its repo-local execution skills. jarvis-box owns Task/Run, Agent execution, control plane, runtime state/workspaces/logs and operator mechanics.

## Runtime Foundation contract

For every supported Runtime Environment, the Jarvis repo must provide or identify:

- bootstrap from an approved Jarvis remote/ref into the target Agent HOME;
- canonical cache, stable commands, state and log locations;
- quick task-start sync and periodic full sync;
- materialization into that Runtime Agent's native discovery roots;
- a doctor/probe that verifies the resolved revision and actual discovery;
- an environment-specific Scheduler Adapter;
- update, retry and rollback behavior.

The implementation may differ between customers and Agents. The contract may not assume a mounted Jarvis checkout, `JARVIS_HOME`, a jarvis-box context file or a temporary construction path.

## Scheduler boundary

Internal Runtime Jobs implement only their work. They run inside the current Runtime Environment and do not call Docker:

```text
native scheduler ───────────────→ inner job
host scheduler → release helper → same inner job in Docker
Agent already inside Docker ─────→ inner job
```

The Jarvis-owned Scheduler Adapter chooses the outer invocation. For Docker it calls the jarvis-box release helper with the deployment home and inner command. The helper enters the running formal container with the persistent Agent HOME. A full sync invoked this way must skip attempts to install another scheduler inside the container.

Runtime Jobs write their own state/log inside Agent HOME. The host scheduler records only launch/transport failures. jarvis-box does not read host scheduler logs.

## Docker image and persistence

The image contains jarvis-box, selected Agent CLIs, common toolchain, generic runtime skills and the connector binary. It contains neither create-jarvis nor customer Jarvis/Runtime Foundation content.

Persistent boundaries are:

- Agent HOME volume: Agent identity/config, discovery roots and Jarvis Runtime Foundation;
- jarvis-box state volume: Task/Run/resume state;
- workspace volume: task workspaces;
- logs volume: jarvis-box diagnostics;
- connector volume: connector-owned state.

No Jarvis repo or Host HOME is mounted. Container recreation preserves the Agent HOME. Jarvis updates and jarvis-box image updates remain independent.

## Bootstrap order

1. download and verify the jarvis-box release and image digest;
2. prepare deployment config and persistent Agent HOME;
3. start the formal container in `read-only` mode and activate the formal Agent/source identities in that HOME;
4. use the release `runtime-job` helper to run the Jarvis-owned bootstrap inside that running formal container;
5. run sync/doctor and an actual Agent discovery probe;
6. install the host Scheduler Adapter;
7. verify generic jarvis-box and provider mechanics;
8. after customer approval, switch to `worker`, enable only workflow-backed lanes and guide the first supervised task.

Bootstrap may receive the approved remote/ref and task-scoped authentication through the operator-authorized invocation. jarvis-box neither stores nor interprets those values.

## Recovery ownership

- construction interruption → Construction Workspace;
- Runtime Foundation failure → its stable command, state and log;
- host-to-container launch failure → host scheduler/operator log;
- Task/Run failure → jarvis-box control plane and state;
- provider/connector failure → the relevant operator surface.

No cross-product manifest, context, lock or readiness state aggregates these facts.
