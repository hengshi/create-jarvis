---
name: create-jarvis
description: Build, publish, deploy, and evolve a customer-owned Jarvis from the customer's authenticated Host Agent. Use whenever a customer asks to build their company Jarvis, collect and verify customer-supplied company sources, learn repo-local skills from real Git history, reconcile company and repository knowledge, customize delivery workflows, deploy the formal jarvis-box runtime, resume an interrupted construction journey, or improve Jarvis from real delivery evidence. The default entry coordinates the whole journey; it does not stop after preparing commands for the customer.
---

# Create Jarvis

`create-jarvis` is the Agent-native construction journey. The customer-facing interface is one request, not an installer or phase CLI:

> 请先运行 `git clone https://github.com/hengshi/create-jarvis create-jarvis`，读取本地 `create-jarvis/SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

The Agent receiving that request becomes the **Construction Coordinator**. It owns continuity from discovery through deployment and shadow promotion. `jarvis-box` appears only when the constructed knowledge and workflows are ready for the formal runtime.

### Materialize the method before reading it

The GitHub URL is a boot pointer, not a collection of pages to fetch. If this repository is not already the current local checkout, first clone it into a dedicated directory in the current customer-authorized workspace. Then record `git rev-parse HEAD` and read `SKILL.md` and referenced files from that checkout. Do not reconstruct the method through GitHub HTML, `raw.githubusercontent.com`, repeated WebFetch calls, or copied snippets.

The initial one-line request authorizes this public clone. It does **not** authorize searching the customer's home directory, configuration, shell profiles, environment, Agent histories, installed skills, unrelated repositories or previous runtime remnants. Customer evidence begins with pointers the customer explicitly provides.

## Route the current invocation

Determine the role from durable artifacts, not from an assumed phase number:

- Journey request with no existing journal: start a new **Construction Coordinator** journey.
- Journey request with an existing `CONSTRUCTION-JOURNAL.md`: resume the recorded journey using its pinned method commit.
- `RUN-COMPANY-JARVIS-CONSTRUCTION.md`: execute only the **Company construction lane**.
- `RUN-REPOSITORY-LEARNING.md`: execute only the **Repository learning lane**.
- Constructed company/repo assets with workflow work remaining: continue **reconciliation / workflow construction**.
- `construction-ready` workflow and a deployable runtime release: continue **formal runtime deployment**.
- Deployed candidate handling real work: continue **shadow delivery / promotion / evolution**.

## Construction Coordinator

Read, in order:

1. `playbooks/customer-jarvis-growth-loop.md`
2. `playbooks/one-plus-two-runtime-model.md`
3. `playbooks/runtime-method-contract.md`
4. `playbooks/prompts/preparation.md`

### Resume before starting over

Before selecting the current repository HEAD as the method version, check only the construction workspace explicitly named by the customer or the current directory's `jarvis-build/CONSTRUCTION-JOURNAL.md`. If found:

1. read the journal;
2. use the method commit recorded there;
3. verify the referenced progress, remotes and revisions still exist;
4. continue its `Next` action.

Do not search the customer's home or unrelated directories for a journal. If no workspace was named and the current directory has no journal, ask whether this is a new journey or request the existing construction workspace path. Do not silently migrate an in-progress journey to a newer method revision.

### Ask before discovering

For a new journey, begin with a short guided intake. Ask the customer in free-form text for the company identity and the documentation, code repositories and work-system sources they want Jarvis to learn from. Accept remote URLs or explicit local paths, and explain that one pilot product/repository is enough to start if the complete fleet is not ready. Do not offer guessed company/product choices derived from the machine. After those sources are provided, probe only them, summarize what is accessible, and ask one compact follow-up for unresolved history range, publication target or write policy.

Do not infer the company, product fleet or authorization boundary from artifacts found on the Host computer. The Host is an execution surface, not a customer evidence source.

### Preparation

Preparation turns customer-provided pointers into a shallow, verified inventory. It creates:

```text
jarvis-build/
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── RUN-COMPANY-JARVIS-CONSTRUCTION.md
└── RUN-REPOSITORY-LEARNING.md
```

`BUILD-CONTEXT.md` records exact pointers, revisions, access probes and write/delivery policy. For the Company Jarvis remote it records provider, host, owner/namespace, canonical repo, visibility, default branch, current history and publication mode. For every code repo it records whether an accepted result must remain read-only, be committed locally, be pushed to a branch, or be delivered through PR/MR.

Do not store source dumps or credentials. Do not create `bootstrap-state.json`, `bootstrap-result.json` or `jarvis.toml`.

### Dispatch the two lanes

After writing the task contracts, the Coordinator starts both lanes itself:

- use native subagents when available;
- otherwise execute the two RUN contracts sequentially in the same Agent, preserving role and write boundaries;
- never require the customer to open two terminals or understand the commands.

Only generate `START-HERE.md` when a provider-native child invocation is genuinely needed as a recovery fallback. It is not a normal customer deliverable.

The Company integrator is the only writer to the Company Jarvis target. Each customer code repo has at most one Repository learning writer at a time. Scanning workers may return evidence packets but do not concurrently edit a shared target.

Before yielding or changing lane, update that lane's progress and the journal pointer. Do not promise daemon, heartbeat, process survival or native resume that the current Host Agent does not actually provide.

## Company Jarvis construction lane

Read only the shared context, this lane's RUN contract, the Company construction section of the growth loop, `playbooks/prompts/company-jarvis-construction.md`, and explicitly referenced templates.

Write only:

- the Company Jarvis target;
- its customer-confirmed GitHub/GitLab remote according to publication policy;
- `COMPANY-JARVIS-PROGRESS.md`;
- task-local evidence packets.

Customer code repos are read-only evidence in this lane. Establish capability taxonomy from product evidence; disposition every candidate; close product, implementation and verification anchors for included capabilities; then construct source routes, repo fleet, capability surfaces, cross-cutting relations and company entry. Repository learning's eval loop cannot substitute for company semantic construction.

Validate content before publication. New/empty remotes may receive an initial default branch; existing remotes must preserve history and use a branch plus PR/MR. Record remote, branch, commit, PR/MR and remote verification. A local directory alone is not delivery.

Starter workflows remain `draft-template`.

## Repository learning lane

Read only the shared context, this lane's RUN contract, the Repository learning section of the growth loop, `playbooks/prompts/repository-learning.md`, and the replay templates needed by the current episode.

Write only repo-local skill deltas permitted by each repo's delivery policy, `REPOSITORY-LEARNING-PROGRESS.md`, and task-local replay evidence. Never modify the Company Jarvis repo from this lane.

One progress table covers all repos. The customer may select one year, two years, all reachable history, or a custom date/ref. Inspect actual code changes throughout the selected range; commit messages are navigation only. Preserve a delta only after same-case replay proves an improvement and adjacent regression remains acceptable.

For every repo, record the delivered branch/commit/PR/MR and whether the result is approved/merged, candidate-only, read-only, or blocked. A dirty local delta is not a consumable repo skill.

## Reconciliation and workflow construction

When both lanes finish or reach a customer-approved route-scoped boundary, the Coordinator:

1. reads both progress files and remote delivery facts;
2. resolves each usable repo-local entry at a real pinned ref;
3. replaces `pending Repository learning` routes only when the target is actually readable;
4. reruns Company → repo-local routing probes;
5. retains unresolved repos and history honestly;
6. customizes starter workflows with the customer's real sources, roles, routing, branch/review/test/release policy and closure evidence.

A workflow becomes `construction-ready` only when its required modules, sources and repositories have current-revision validation and at least one controlled or real case passes. This does not make it production-active.

## Formal deployment and immutable snapshot

After at least one workflow is `construction-ready`, follow `playbooks/prompts/formal-runtime-deployment.md`.

Deployment uses canonical remotes and commits, never Host construction paths. It binds an immutable validation set:

- Company Jarvis commit;
- workflow-required repo commits and repo-local entries;
- the released jarvis-box OCI image digest, which also contains the pinned
  uv-im-connector binary;
- the bundled uv-im-connector version/commit reported by the same release;
- routing, source, Agent and capability probe results.

The formal Agent uses an independently activated, auditable, rotatable and revocable high-authority identity. It may be an organization super-admin if the customer authorizes that power. Never copy the entire Host home, SSH agent or human credential store. Treat Docker socket access as host-root-equivalent and require explicit authorization.

After successful container-side probes, change the workflow to `ready-for-shadow`. Later learning writes new refs and cannot mutate the deployed snapshot in place.

## Shadow delivery and promotion

`ready-for-shadow` workflows process representative real tasks under customer supervision. Mark a workflow `shadowing` while this evidence is accumulating. Promote it to `active` only when:

- routing, repo-local execution, verification and END closure are stable across representative tasks;
- hidden customer steps have been written to the correct durable owner and replayed;
- the customer approves production use;
- the active deployment lock identifies the exact revisions that passed.

No initial prompt can manufacture future production evidence. When no representative task exists yet, stop honestly at `ready-for-shadow` and explain the next business event needed.

## Non-negotiable boundaries

- Construction does not require jarvis-box.
- Company knowledge stores company semantics and routes; repository execution truth stays repo-local.
- Eval loop is an internal learning method, never the delivered skill.
- Publication and deployment use real remote revisions, not uncommitted Host paths.
- Runtime-owned generic methods are not copied into Company Jarvis.
- The customer sees delivered repos/PRs, usable scope, approval/blockers and the next business result—not phases, oracle, cursor, replay internals or child-process commands.
