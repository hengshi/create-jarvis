# Part 4: jarvis-box installation and onboarding

Use this card after reconciliation has verified one usable Jarvis → source/module → repo-local route. Read `work/jarvis-box-onboarding.md` first and record every material checkpoint and `Next` before pausing.

## 1. Reverify inputs

Resolve from remote facts, without guessing:

- the approved Jarvis remote and ref containing a verified Runtime Foundation;
- required repo-local delivery refs for the first supervised workflow;
- the public jarvis-box release, checksums and OCI image digest;
- the formal Agent identity and provider/source authorization scope;
- the target Agent's native discovery roots;
- the host scheduler type and approved installation location.

Do not deploy dirty Host paths or floating image tags. Missing inputs block only the affected step; record the exact recovery action in the work card.

## 2. Prepare the formal runtime

Use the extracted public release rather than cloning jarvis-box source. Prepare a private deployment home containing only jarvis-box/operator configuration:

```text
<deployment-home>/
├── deployment.env          # pinned JARVIS_IMAGE and deployment settings
├── runtime.env             # jarvis-box/provider configuration
└── connector.env           # only when the connector profile is enabled
```

The Compose deployment creates persistent Agent HOME, Task/Run state, workspace, log and connector volumes. Do not create or mount a Jarvis directory, `jarvis-context.json`, `deployment-lock.json` or replacement manifest. Do not bind the Host user's home or SSH agent. Docker socket remains an explicit host-root-equivalent authorization.

Set `JARVIS_SERVE_MODE=read-only` for initial onboarding, start the formal service, then activate the independent formal identity in the persistent Agent HOME:

```bash
<release-dir>/scripts/deploy-production.sh <deployment-home> start
<release-dir>/scripts/deploy-production.sh <deployment-home> shell
```

Record account/host/capability facts, never credential values.

## 3. Bootstrap the Jarvis Runtime Foundation

Before enabling business ingress, run the bootstrap entry published by the approved Jarvis ref inside the formal Docker Runtime Environment. Use a task-scoped checkout or streamed release artifact only for bootstrap; it must install stable commands/cache/state/log into the persistent Agent HOME and then remove temporary material.

Use the jarvis-box release helper to enter the formal environment. The inner command and arguments come from the Jarvis repo's runtime governance; jarvis-box does not define or inspect them:

```bash
<release-dir>/scripts/deploy-production.sh <deployment-home> runtime-job \
  <jarvis-bootstrap-command> <approved-remote> <approved-ref>
```

Then call the installed Jarvis-owned entries through the same helper:

```bash
<release-dir>/scripts/deploy-production.sh <deployment-home> runtime-job <quick-sync-command>
<release-dir>/scripts/deploy-production.sh <deployment-home> runtime-job <runtime-foundation-doctor>
```

Verify inside the container that:

1. the canonical cache resolves the approved Jarvis revision;
2. stable commands work without the temporary checkout;
3. state/log are under persistent Agent HOME;
4. Jarvis skills/references exist in the actual Codex/Claude discovery roots;
5. a real Runtime Agent invocation discovers and follows the Jarvis entry;
6. create-jarvis itself was not installed as a runtime skill.

If the Runtime Foundation is incomplete, return to Part 2. Do not teach jarvis-box to clone, mount or inject the Jarvis repo as a workaround.

## 4. Bind the host scheduler

Use the Scheduler Adapter delivered by the Jarvis repo. Configure it with the release helper path, deployment home and inner Runtime Job command. The adapter may install launchd, systemd, cron or a customer scheduler entry, but the inner job stays Docker-unaware.

Run one trigger manually and verify both layers:

- host layer: helper successfully entered the formal container, or recorded a launch failure;
- runtime layer: the inner job wrote its own result/state/log in persistent Agent HOME.

For a full sync under host scheduling, pass the Jarvis-defined equivalent of `--skip-scheduler-update` to prevent an in-container scheduler installation. Do not modify `pullall`, runtime sync, maintenance or self-improve to call Docker.

## 5. Verify jarvis-box mechanics

Run the release's generic verification:

```bash
<release-dir>/scripts/deploy-production.sh <deployment-home> verify
```

It verifies the image/toolchain, container authority, Agent health, Task/Run and Agent HOME persistence, configured providers, optional connector and explicitly authorized Docker socket. It does not verify a Jarvis repo, parse runtime governance or create readiness state.

After those checks pass and the customer approves business ingress, set `JARVIS_SERVE_MODE=worker`, enable only business lanes whose applicable Jarvis workflows are present in native discovery, and restart through the release helper. Run one supervised end-to-end business task. Confirm Runtime Agent discovery, routing to the delivered repo-local skill, work/verify/writeback behavior and operator visibility. Record evidence and any exact gap in the onboarding card.

## 6. Handoff and recovery

The onboarding card records release path/digest, deployment home, identity facts, Runtime Foundation revision/probes, scheduler entry, service probes, supervised task result and `Next`. It is construction recovery evidence, not runtime configuration.

After onboarding:

- Jarvis changes flow through its remote → cache → sync → discovery roots;
- jarvis-box upgrades flow through the release image process;
- Runtime Foundation jobs recover from their own state/log;
- jarvis-box Task/Run recovers from jarvis-box state/control plane;
- host scheduler launch failures recover from host operator logs.
