# Construction and formal runtime boundary

This contract separates customer construction, the customer-owned Runtime Foundation and Jarvis Box execution.

## Host Construction Agent

The customer starts with an already authenticated and explicitly authorized Host Agent. It clones and pins create-jarvis, guides source intake, maintains the Construction Workspace, publishes customer assets, coordinates repository learning and invokes formal runtime onboarding.

The initial request authorizes the public method clone only. It does not authorize scanning HOME, Agent history/configuration, unrelated repositories or old runtime residue.

Construction through reconciliation works without Jarvis Box.

## create-jarvis

This repository owns:

- the four-part construction journey;
- templates, work cards and recovery facts;
- Company/repository reconciliation;
- the Native/Docker deployment decision and cross-boundary evidence gate;
- supervised shadow and promotion.

It does not run a construction daemon, own customer knowledge or implement Jarvis Box lifecycle behavior.

## Customer Jarvis and Runtime Foundation

The customer Jarvis repo owns company knowledge, routing, workflows and `runtime-governance.md`. Its Runtime Foundation owns bootstrap, sync, native Agent discovery materialization, doctor, maintenance and Scheduler Adapter behavior.

Jarvis Box does not clone, mount, parse or validate the customer Jarvis repo. It provides the runtime-job transport used by a Docker Host Scheduler Adapter; the environment-native inner command remains customer-owned.

## Jarvis Box

Jarvis Box owns:

- Runtime Agent execution and generic toolchain;
- Task/Run lifecycle and workspace ownership;
- provider/IM ingress and writeback;
- state, logs, diagnostics and cleanup;
- Native installer and Docker release operator contract;
- optional connector integration.

Company semantics stay in customer Jarvis. Repository execution truth stays in each code repository.

## Native and Docker identity

Both modes execute with customer-approved authority.

| Mode | Identity contract |
| --- | --- |
| Native | use the existing installing OS user and that user's native CLI authentication |
| Docker | import only approved portable identities from the current Host user into a separate persistent runtime |

A dedicated machine account may be selected for audit, rotation or reduced blast radius, but is not required to install Jarvis Box. Host HOME, SSH agent, Keychain and complete credential stores are never implicitly copied. Docker socket authorization is host-root-equivalent. IM provider-native credentials remain inside the connector boundary.

## Construction files

`jarvis-build/` contains Markdown recovery facts: continuation entry, context, journal, work cards and task-local evidence. These files contain no credentials and never become Jarvis Box runtime state.

## Deployment conversion

Part 4 turns construction evidence into observable runtime facts:

- delivered Company/repository refs;
- selected Native or Docker mode;
- runtime owner and actual runtime root;
- Jarvis Box release and Docker image digest when applicable;
- credential capability evidence without token values;
- Runtime Foundation doctor and real Agent discovery;
- provider ingress, writeback and cleanup evidence.

The selected Jarvis Box release owns concrete installation commands, files and recovery steps. create-jarvis and Company Jarvis record pointers and evidence rather than copying that runbook.

## Customer-visible contract

Show delivered repositories and PRs/MRs, usable workflow scope, selected deployment mode, approval checkpoints, blockers and the next business result. When pausing, show the Construction Workspace path and recovery phrase. Hide internal replay/oracle and child-process mechanics unless needed to recover a concrete failure.
