# Formal jarvis-box deployment

Use this lane only after the Company Jarvis remote, the required repo-local
skill refs and at least one customer workflow are `construction-ready`.
Construction itself must not depend on jarvis-box. The result of this lane is
an immutable deployment set and a `ready-for-shadow` runtime; it is not a
promise that a future business task has already been completed.

## 1. Freeze the handoff

Read `CONSTRUCTION-JOURNAL.md`, both lane progress files and the actual remote
delivery facts. Resolve, without guessing:

- the Company Jarvis provider, remote and approved commit;
- every required code repository's canonical remote, fetchable ref, exact
  commit and repo-local entry skill;
- the workflow skill paths, their source commits and the workflow being
  deployed;
- the released jarvis-box image digest and, if selected, the uv-im-connector
  image digest;
- the formal Agent identity and credential profile.

Do not deploy a Host dirty checkout, an unreviewed branch, a floating image
tag, or a local skill that has not been published to a real GitHub/GitLab
ref. A deployment lock must point to real revisions that another operator can
fetch.

The `workflows` entries in `company-context.json` use `ready-for-shadow` as the
deployment target. This does not rewrite the Company workflow skill's
construction evidence or claim that shadowing already happened; the separate
deployment lock records whether the runtime probes actually passed.

## 2. One authorization checkpoint

Explain the exact capability scope before starting the formal runtime. Activate
an independent, auditable, rotatable and revocable high-authority identity for:

- Codex or Claude;
- GitHub/GitLab and Git author identity;
- required documentation/source systems;
- the selected IM provider application, if any;
- the OCI registry when images are private;
- Docker socket access only when the workflow explicitly needs a host-root-
  equivalent executor.

The formal Agent may be an organization super-admin if the customer chooses
that authority. Identity separation is for audit, rotation and revocation, not
for pretending the digital employee is low privilege. Do not copy the Host
user's whole home, SSH agent or credential store into the runtime.

## 3. Prepare the private deployment home

Use the released bundle's `compose.yaml` and `scripts/` from the same release.
Do not clone jarvis-box source or run the legacy native installer. The private
deployment home must contain:

```text
<deployment-home>/
├── deployment.env
├── company-context.json
├── company/                 # clean Company commit export, read-only in runtime
├── runtime.env
├── connector.env            # only needed when JARVIS_CONNECTOR_PROFILE=uvim
└── lock/                    # created by deploy-production.sh
```

Materialize `company/` from the approved Company commit with `git archive` or
an equivalent clean export. Compute its tree digest with the released image's
`jarvis-box jarvis digest`; do not use a dirty checkout or copy `.git` as
runtime evidence. Write `company-context.json` with strict schema v1, including
the Company commit/tree digest, required repository refs/commits/entries,
workflow paths, `authority: "high"`, and OCI references pinned by digest.

`deployment.env` pins `JARVIS_IMAGE` (and `UVIM_IMAGE` when selected) and the
absolute deployment home. `runtime.env` contains the runtime agent, provider
allowlists, webhook/connector references and any provider configuration. Keep
provider-native IM secrets in `connector.env`; they are not copied into
jarvis-box. Enable the Docker socket only through the explicit deployment
switch after the authorization checkpoint.

If a native-v1 installation is detected, do not treat it as a fresh install or
overwrite it. Use the release's explicit migration/recovery path if one exists;
otherwise stop and report the blocker.

## 4. Start the locked runtime and authenticate

Run the released deployment script from the bundle:

```bash
scripts/deploy-production.sh <deployment-home> start
scripts/deploy-production.sh <deployment-home> shell
```

`start` is intentionally usable before Agent login. It removes stale
`lock/deployment-lock.json`, starts the high-authority root container and keeps
health/status/shell available, but every business write is rejected with
`deployment_not_ready`. Inside the persistent container home, complete the
provider-native Codex/Claude, `gh`/`glab`, source and registry logins. Do not
run routine `jarvis-box version/status/agent current`; the injected Company
context is the business routing input. Use doctor/status only to diagnose a
concrete failure.

## 5. Verify the real runtime

After authorization, run:

```bash
scripts/deploy-production.sh <deployment-home> verify
```

The probe must execute in the actual image and verify all of the following:

1. Company context schema, clean tree digest, entry and workflow files;
2. container-root/high-authority execution and the complete batteries-included
   toolchain;
3. Codex/Claude doctor plus a real minimal Agent smoke response;
4. every required repository ref resolving to its exact commit and repo-local
   entry, including `git push --dry-run` where `write_required` is true;
5. Company → workflow → repository routing and source access;
6. optional connector health, protocol metadata and authenticated capability;
7. optional Docker socket access, only when explicitly enabled;
8. container recreation preserving Agent home and Task/Run state.

If any capability is missing, report the exact gap. Do not install packages
interactively inside a running container and then call the deployment
reproducible.

Only after every probe passes does the script atomically write
`lock/deployment-lock.json` and restart jarvis-box. The server then reports
`deployment_ready: true` and accepts business work in `ready-for-shadow` mode.
If verification fails, no new lock is written and the server remains locked.

## 6. Shadow and later promotion

Record the resulting lock path, exact revisions, identity and probe output in
the construction journal. Keep the workflow at `ready-for-shadow` until the
customer supervises representative real tasks. Mark it `shadowing` while
evidence accumulates; promote to `active` only after routing, repo-local
execution, verification and END closure are stable and the customer approves.

Repository learning or self-improve work creates a new published ref and a new
deployment set. It never mutates the active snapshot in place.
