---
name: create-jarvis
description: Build, publish, install, resume, and evolve a customer-owned Jarvis from an authenticated Host Runtime Agent. Use for Jarvis repo initialization, knowledge and Runtime Foundation construction, repository learning, reconciliation, jarvis-box Docker onboarding, or interrupted journey recovery.
---

# Create Jarvis

`create-jarvis` is the reusable construction method. Read `GOAL.md` once before taking ownership of a journey; it is the sole cross-repository ownership model.

The customer-facing entry is:

> 请运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建一套 Jarvis。

The authenticated Host Runtime Agent receiving the request acts as **Construction Coordinator**. It coordinates the work; it does not become the durable runtime sync service.

## Materialize and pin the method

Clone this repository into a customer-authorized workspace, record `git rev-parse HEAD`, and read referenced files locally. The initial request authorizes this public clone only. Do not inspect customer home contents, Agent history/configuration, shell state, unrelated repositories or old runtime residue without explaining the purpose and receiving authorization.

## Route from durable facts

- No named workspace and no `jarvis-build/CONTINUE-JARVIS.md`: run guided intake and preparation.
- Existing Construction Workspace: resume it before creating anything.
- Named work card: execute only that card within its read/write boundary.
- Completed Part 1: Part 2 and independent Part 3 cards may proceed.
- Delivered Jarvis and repo-local refs: run reconciliation.
- Reconciliation proves one usable end-to-end route: run Part 4.
- Existing runtime: diagnose from the owning layer's state/log before retrying.

## Progressive loading

Read `playbooks/construction-journey-model.md` once when taking ownership. Then load only the current route:

| Route | Read |
|---|---|
| New journey | `playbooks/prompts/preparation.md` |
| Resume | `playbooks/construction-recovery-contract.md`, current card, then its prompt |
| Part 1 | `playbooks/prompts/jarvis-repo-initialization.md`, `templates/jarvis/README.md` |
| Part 2 | `playbooks/prompts/jarvis-construction.md`; only referenced templates needed now |
| Part 3 | `playbooks/prompts/repository-learning.md`; only replay templates needed by the current episode |
| Reconciliation | `playbooks/prompts/reconciliation.md` and delivered refs in the selected route |
| Part 4 | `playbooks/runtime-method-contract.md`, `playbooks/prompts/formal-runtime-deployment.md`, current onboarding card |
| Later evolution | relevant route in `playbooks/customer-jarvis-growth-loop.md` |

Do not preload every playbook or copy this method into the generated Jarvis repo.

## Resume before starting over

Check only a workspace explicitly named by the customer or `./jarvis-build/CONTINUE-JARVIS.md`:

1. read the recovery entry and pinned method commit;
2. read the journal, build context and current card;
3. verify files, Git state, remote refs and external runtime facts;
4. determine whether the prior writer is live, ended or unknown;
5. reattach when live, replace only when ended, and block duplicate writers when ownership is unknown;
6. continue from the last verified checkpoint and `Next`;
7. update the card and journal before yielding.

Session handles are hints, not truth. Do not silently migrate an in-progress journey to a newer method commit.

## Preparation and writer ownership

Ask in free-form text for the Jarvis name/purpose and the documentation, code repositories and work-system sources it should learn. Explain that these pointers let Jarvis recover original intent, routing and operating rules; customers may start with one pilot source or repository and add the rest later.

Use `scripts/instantiate_construction_workspace.py init`, then `add-repository` for each authorized code repo. Cards record objective, authorized inputs, allowed writes, target, writer, status, last verified checkpoint, delivery, blocker, `Next` and verification time. They never contain credentials.

- Part 1 has one Jarvis repo writer.
- Part 2 has one Jarvis integrator; scanners return evidence packets only.
- Part 3 has one independent card and at most one writer per code repo.
- Part 2 and Part 3 may run concurrently when the Host supports long-running Agents.
- Part 4 begins only after reconciliation proves at least one usable route.

## Part 1 — Jarvis repo initialization

Follow `playbooks/prompts/jarvis-repo-initialization.md`.

Use `scripts/instantiate_jarvis.py` and `templates/jarvis/` to build the minimum repo, verify it with `scripts/verify_jarvis_output.py`, then publish through the customer's Git policy. The scaffold includes unresolved `runtime-governance.md`; it is a required constitutional template, not proof that Runtime Foundation exists.

## Part 2 — Jarvis construction and Runtime Foundation

Follow `playbooks/prompts/jarvis-construction.md`.

Build Jarvis identity/purpose, modules, source routes, repo fleet, cross-cutting relations, workflows, references and tools from explicitly authorized evidence. Do not force its boundary from an organization label, one product or one technical integration pattern.

Part 2 must also turn runtime governance into executable behavior for each intended Runtime Environment:

1. identify Agent HOME and native skill discovery roots;
2. define the approved Jarvis remote/ref and bootstrap authentication boundary;
3. implement stable bootstrap, quick/full sync, state/log and verification entries owned by the Jarvis repo;
4. materialize Jarvis skills/references into native discovery roots safely;
5. keep internal Runtime Jobs Docker-unaware;
6. implement a Scheduler Adapter for native direct execution or Docker outer execution;
7. run behavioral verification or record a precise `pending-runtime-foundation` gap.

Do not copy HENGSHI paths or tool names into another Jarvis. Documentation alone is not a verified Runtime Foundation.

## Part 3 — Repository learning

Follow `playbooks/prompts/repository-learning.md` once per repository card.

Commit messages and issue links are navigation hints. Prefer a real issue/ticket/discussion and request access only after explaining why it improves replay. If original intent is missing or inaccessible, a scanner produces an evidence packet and an isolated reconstruction Agent derives the smallest plausible visible START from pre-change code, diff, tests and adjacent history, recording provenance and uncertainty. A separate Replay Agent receives no final diff, root cause or outcome.

Only a minimal repo-local change that improves same-case replay and survives adjacent regression is delivered. Never edit the Jarvis repo from a repository card.

## Reconciliation

Follow `playbooks/prompts/reconciliation.md`. Verify remote Jarvis and repo-local refs, replace pending pointers only with real entries, and demonstrate at least one Jarvis → source/module → repo-local route. Incomplete coverage remains explicit; there is no deployment lifecycle state machine.

## Part 4 — jarvis-box Docker onboarding

Follow `playbooks/prompts/formal-runtime-deployment.md`.

Use the public jarvis-box release. Pin its OCI image digest, prepare a persistent formal Agent HOME, and activate an independent auditable identity. Before business ingress:

1. run the Jarvis repo's Runtime Foundation bootstrap inside the formal Docker Runtime Environment using the persistent Agent HOME;
2. run the Jarvis-owned sync/doctor and prove the Runtime Agent discovers the Jarvis entry natively;
3. install the Jarvis-owned host Scheduler Adapter, configured to call the jarvis-box release runtime-job helper;
4. start and verify jarvis-box health, Agent, Task/Run persistence, providers and optional connector;
5. guide the customer through a supervised real task.

There is no `jarvis-context.json`, `deployment-lock.json`, Jarvis directory mount, `JARVIS_HOME`, root-skill injection or jarvis-box readiness/onboarding state machine. Construction checkpoints stay in the onboarding work card.

## Non-negotiable boundaries

- Jarvis repo is the source of Jarvis knowledge and Runtime Foundation.
- Runtime Agent discovery roots are the runtime consumption surface.
- jarvis-box does not clone, pull, sync, mount, validate or inject Jarvis.
- Docker awareness belongs only in the outer Scheduler Adapter/release helper, never inside Runtime Jobs.
- Docker image contains generic runtime mechanics only, never customer Jarvis content.
- Repo execution truth remains repo-local.
- Replay is a learning method, not the delivered skill.
