# Construction and formal runtime boundary

This contract separates the customer construction journey, the customer's cross-runtime constitution and the production digital-employee implementation.

## Host Construction Agent

The customer starts with an already authenticated, explicitly authorized Host Agent. It may have administrator-level access. The Host Agent owns:

- reading and pinning the create-jarvis method;
- guiding customer source intake and probing supplied pointers;
- maintaining the Construction Workspace and recovery facts;
- initializing and publishing the Company Jarvis repo;
- coordinating Company construction and independent repository learning;
- creating and verifying customer-specific Host runtime foundations required by Company governance;
- reconciliation and workflow construction;
- invoking formal runtime onboarding when its gate is satisfied.

Construction through reconciliation must work when `jarvis-box` is absent. Host paths, home directories and credentials are not production artifacts.

The Host computer is not an evidence catalog. The initial request authorizes cloning the public method, not inspecting home contents, Agent history/configuration, shell state, unrelated repositories or previous runtime residue.

## create-jarvis method

This repository owns reusable instructions, templates and evidence gates for:

- the four-part construction journey;
- Construction Workspace creation and interruption recovery;
- historical episode replay and minimal repo-local writeback;
- Company/repo reconciliation and workflow maturity;
- formal jarvis-box download, installation, startup and onboarding;
- supervised shadow and promotion.

It does not own a customer's durable knowledge, run a construction daemon, promise process survival, or implement jarvis-box's control plane.

## Company runtime governance

The Company Jarvis repo owns `runtime-governance.md`: the customer-specific constitution shared by Host Agents and formal managed runtimes. It governs the customer's canonical runtime root, cache/workspace/state roles, task-start synchronization, stable tools, checkout isolation, handoff, cleanup, credentials and write boundaries.

Part 1 creates its template scaffold. Part 2 discovers customer facts, decides the constitution, installs any required Host mechanisms and verifies behavior. Missing mechanisms are marked `pending-runtime-foundation`; documentation alone cannot claim an installed runtime foundation.

The constitution may refer to jarvis-box through its public behavior. It does not copy jarvis-box's injected execution contract, control plane or operator runbook.

## Formal jarvis-box runtime

jarvis-box is installed only after reconciliation passes and at least one workflow is `construction-ready`. It owns the production execution surface:

- batteries-included Agent and operational toolchain;
- injected execution contract;
- Task/Run lifecycle and control plane;
- workspaces, logs, diagnostics and runtime state;
- immutable Company Jarvis materialization and Agent discovery;
- repo checkout/cache and repo-local skill discovery;
- operator runbook and selected IM connector integration;
- runtime update and rollback through the deployment owner.

Runtime implementation details stay in jarvis-box. Company-specific knowledge and policies stay in Company Jarvis. Repo execution truth stays in each customer code repo.

## High-authority identity model

Both construction and production Agents are high-authority execution subjects. The formal jarvis-box container runs as root; this is not a low-privilege sandbox. Identity separation exists for audit, rotation and revocation.

- The formal Agent identity is activated separately from the Host user.
- It may have organization super-admin authority when the customer explicitly chooses that model.
- jarvis-box server and its Agent share one trusted authority boundary unless another executor is introduced.
- IM provider-native credentials remain in the connector boundary.
- Docker socket, Host SSH agent and Host home access are never implicit. Docker socket authorization is host-root-equivalent.

## Construction files

The method uses ordinary Markdown in `jarvis-build/`:

- `CONTINUE-JARVIS.md` for the recovery entry;
- `BUILD-CONTEXT.md` for authorized pointers and delivery policy;
- `CONSTRUCTION-JOURNAL.md` for coordinated pointers and current work;
- one work card per construction unit;
- task-local evidence packets.

These files contain no credentials and never become jarvis-box runtime state.

## Deployment conversion

Part 4 converts construction evidence into runtime facts:

- Host path → canonical remote plus resolved commit;
- local skill delta → delivered and resolvable Git ref;
- Company entry → immutable runtime snapshot and discovery links;
- Host access → separately activated formal identity and source adapters;
- construction validation → container-side routing/source/Agent/capability probes.

The deployment lock records exact revisions, the jarvis-box image digest, bundled component versions, identity and probe evidence. Stable runtime behavior observed during onboarding may be written back into Company governance with evidence. It does not move jarvis-box internals into Company Jarvis.

## Customer-visible contract

Show delivered repositories and PRs/MRs, usable scope, approval checkpoints, blockers and the next business result. When pausing, show the Construction Workspace path and recovery phrase. Do not expose internal replay/oracle terminology or provider child-process mechanics unless required to recover a concrete failure.
