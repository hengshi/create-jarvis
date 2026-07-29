# Construction and formal runtime boundary

This contract prevents the customer construction journey and the production digital-employee runtime from becoming one product surface.

## Host Construction Agent

The customer starts with an already authenticated and explicitly authorized Host Codex or equivalent Agent. It may have broad or administrator-level access. That is an intentional construction authority, not a jarvis-box service identity.

The Host Agent owns:

- reading and pinning the create-jarvis method;
- guiding customer source intake, then inventorying and probing only supplied pointers;
- Company construction and Repository learning coordination;
- customer Git publication;
- reconciliation and workflow construction;
- preparing the immutable deployment set;
- invoking formal runtime deployment when ready.

Construction must work when `jarvis-box` is absent. Host paths, home directories and credentials are not production artifacts.

The Host computer is not an evidence catalog. The initial customer request authorizes cloning the public method, not inspecting home contents, Agent history/configuration, shell state, unrelated repositories or previous runtime residue. Additional evidence access starts from customer-provided URLs or explicit paths.

## Create Jarvis method

This repository owns instructions, templates and evidence gates for:

- Coordinator, Company construction and Repository learning;
- historical episode replay and minimal repo-local skill writeback;
- Company/repo reconciliation;
- customer workflow construction and maturity;
- formal deployment handoff, supervised shadow and promotion.

It does not create an OS service user, run a daemon, promise process survival, manage container lifecycle after handoff, or maintain a parallel Task/Run state service.

## Formal jarvis-box runtime

jarvis-box is installed only after at least one workflow is `construction-ready`. It owns the production execution surface:

- batteries-included Agent and operational toolchain;
- Task/Run lifecycle, workspaces, logs, diagnostics and writeback;
- immutable Company Jarvis materialization and Agent discovery;
- repo checkout/cache and repo-local skill discovery;
- selected IM connector integration;
- runtime update/rollback through the external deployment owner.

Runtime-owned generic methods do not belong in the customer Company repo. Company-specific workflows and policies do not belong in the public runtime image.

## High-authority identity model

Both construction and production Agents are high-authority execution subjects. The formal jarvis-box container runs as root; this is not a low-privilege sandbox. Identity separation exists for audit, rotation and revocation.

- The formal Agent identity is activated separately so it can be audited, rotated and revoked independently of the Host user.
- It may have organization super-admin authority when the customer explicitly chooses that model.
- jarvis-box server and its Agent share one trusted authority boundary unless a separate executor is introduced later.
- IM provider-native credentials remain in the connector boundary. Jarvis owns only the connector capability needed to communicate.
- Docker socket, host SSH agent or host home access is never implicit. Docker socket authorization is recorded as host-root-equivalent.

## Construction files

The method uses ordinary Markdown:

- `BUILD-CONTEXT.md`
- `RUN-COMPANY-JARVIS-CONSTRUCTION.md`
- `RUN-REPOSITORY-LEARNING.md`
- `CONSTRUCTION-JOURNAL.md`
- one progress document per lane

They do not contain credentials and do not become runtime state. `START-HERE.md` is optional recovery material, not a default customer handoff.

## Deployment conversion

Deployment converts construction evidence into runtime facts:

- Host path → canonical remote plus resolved commit;
- local skill delta → approved/candidate Git ref;
- Company entry → immutable runtime snapshot and discovery links;
- Host access → separately activated formal identity and source adapters;
- construction validation → container-side routing/source/Agent/capability probes.

The resulting deployment lock records exact revisions, one jarvis-box image
digest, the bundled connector version and probe evidence. It is production
configuration, not a bootstrap phase state machine.

## Customer-visible contract

Show the customer delivered repositories/PRs, usable scope, authorization or review checkpoints, blockers and the next business result. Do not expose internal Phase names, eval/oracle terminology, progress schemas or child-process commands unless they are required to recover a concrete failure.
