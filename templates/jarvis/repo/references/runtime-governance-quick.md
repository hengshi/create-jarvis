# Runtime governance quick reference

**Status**: binding summary | **Maturity**: `unresolved`

Keep this aligned with [runtime-governance.md](runtime-governance.md).

## Resolve the current Runtime Environment

- Agent HOME: `UNRESOLVED`
- Agent discovery roots: `UNRESOLVED`
- Runtime Foundation root/cache/bin/state/log: `UNRESOLVED`
- quick sync entry: `UNRESOLVED`
- full sync entry: `UNRESOLVED`
- doctor entry: `UNRESOLVED`
- current resolved Jarvis revision: `UNRESOLVED`

## Before durable work

1. run the environment-native quick sync;
2. verify the Jarvis entry is discoverable through the Agent's native discovery mechanism;
3. use an authorized workspace with one writer;
4. resolve remotes/default branches from live source truth;
5. publish or explicitly disposition changes before handoff.

## Scheduler rule

- Native scheduler calls the inner Runtime Job directly.
- Docker host scheduler calls the jarvis-box release `runtime-job` helper, which calls that same inner job in the container.
- An Agent already inside Docker calls the inner job directly.
- Inner Runtime Jobs never call Docker.
- Runtime Job results live in persistent Agent HOME; host launch failures live in host scheduler/operator logs.

## Never

- require a mounted Jarvis directory or `JARVIS_HOME`;
- store credentials or private runtime state in Git;
- copy an upstream method pack into runtime discovery roots;
- treat jarvis-box as Jarvis clone/pull/sync/install owner;
- create `jarvis-context.json`, `deployment-lock.json` or a replacement readiness manifest.

Read the full constitution for bootstrap, sync, materialization, authority, writeback, cleanup or recovery decisions.
