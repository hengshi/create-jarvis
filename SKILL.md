---
name: create-jarvis
description: Build, publish, deploy, resume, and evolve a customer-owned Jarvis from the customer's authenticated Host Agent. Use for Company Jarvis repository initialization, company knowledge and cross-runtime governance construction, independent repo-local skill learning, reconciliation, jarvis-box installation and onboarding, interrupted journey recovery, or later evidence-driven evolution.
---

# Create Jarvis

`create-jarvis` is the reusable construction method. The customer-facing entry is one request:

Its canonical product and skill identity is exactly `create-jarvis`. Resolve the current identity from this checked-out root skill and release metadata, never from an old transcript, branch, directory name or remembered alias. A renamed predecessor is obsolete vocabulary, not a second supported method.

> 请用 `gh` 获取 `hengshi/create-jarvis` 的最新代码，检出其 commit 和提交日期时间和提交人，读取 `SKILL.md`，然后帮我构建属于我们公司的 Jarvis。

The authenticated Host Agent receiving that request is the **Construction Coordinator**. It owns continuity across repository initialization, long-running construction tasks, reconciliation, formal runtime onboarding, interruption recovery and shadow promotion.

## Materialize and pin the method

The public GitHub repository is a boot pointer, not a set of pages to fetch. Clone `hengshi/create-jarvis` into a dedicated directory in the customer-authorized workspace, check out its latest commit, record the commit hash, author date, and committer, and read all referenced method files locally. Do not reconstruct the method from GitHub HTML, raw URLs, repeated WebFetch calls or copied fragments.

The initial request authorizes access to this public method repository only. It does not authorize searching the customer home, shell profiles, Agent histories, installed skills, unrelated repositories or old runtime remnants. Customer evidence starts with explicit URLs or paths supplied by the customer.

## Fixed ownership model

| Owner | Responsibility |
|---|---|
| create-jarvis | reusable method, templates, construction steps, evidence gates and recovery protocol |
| Construction Workspace | the current journey's context, work cards, checkpoints, journal and evidence |
| Company Jarvis repo | customer knowledge, cross-runtime constitution, routes, sources, workflows and company tools |
| Customer code repo | repo execution truth and repo-local skills |
| jarvis-box | formal runtime implementation, injected execution contract, control plane, state and operator runbook |

Do not move jarvis-box implementation material into create-jarvis or the Company Jarvis repo. Do not remove `runtime-governance.md` from Company Jarvis: it is the customer's cross-runtime constitution, not a jarvis-box internal template.

## Route the current invocation

Route from durable artifacts, not an assumed phase number:

- No named workspace and no `jarvis-build/CONTINUE-JARVIS.md`: start guided intake for a new journey.
- Existing Construction Workspace: resume it before creating anything.
- A named work card: execute only that card within its read/write boundary.
- Completed Part 1 with open company construction: continue Part 2.
- Open `work/repositories/*/CARD.md` cards: prepare or verify the independent Part 3 handoffs.
- Parts 2 and 3 at a route-scoped boundary: run reconciliation and workflow construction.
- Reconciliation passed and at least one workflow is `construction-ready`: continue Part 4.
- Deployed candidate processing real work: continue shadow, promotion or evidence-driven evolution.

## Load only the current route

Read `playbooks/construction-journey-model.md` once when taking ownership of a journey. Then load only the material required by the durable route:

| Route | Read now |
|---|---|
| New journey | `playbooks/prompts/preparation.md` |
| Existing Construction Workspace | `playbooks/construction-recovery-contract.md`, then the current work card and its prompt |
| Part 1 card | `playbooks/prompts/company-repo-initialization.md` and the Company template README it names |
| Part 2 card | `playbooks/prompts/company-jarvis-construction.md`; load only its explicitly needed templates/references |
| Part 3 repository card | `playbooks/prompts/repository-learning.md` and the replay material needed to discriminate the current repository model |
| Reconciliation card | `playbooks/prompts/reconciliation.md` and the delivered cards/refs in its selected route scope |
| Part 4 card | `playbooks/runtime-method-contract.md` and `playbooks/prompts/formal-runtime-deployment.md` |
| Shadow/promotion/evolution | the relevant section of `playbooks/customer-jarvis-growth-loop.md` plus the active workflow/deployment lock |

Do not preload every playbook. Load `playbooks/customer-jarvis-growth-loop.md` only when the current decision crosses parts, selects a maturity transition or needs the customer-visible lifecycle. Load `playbooks/runtime-method-contract.md` only for runtime ownership/integration questions or Part 4.

## Resume before starting over

Check only the Construction Workspace explicitly named by the customer or `./jarvis-build/CONTINUE-JARVIS.md`. If it exists:

1. read `CONTINUE-JARVIS.md`;
2. use the method commit recorded there;
3. read `CONSTRUCTION-JOURNAL.md`, `BUILD-CONTEXT.md` and the current work card;
4. verify actual files, Git state, remote refs, external deliveries and jarvis-box state;
5. determine whether the prior writer is live, ended or unknown;
6. reattach when live, replace only when ended, and block duplicate writers when ownership is unknown;
7. continue the card's last verified checkpoint and `Next` action;
8. update the card and journal before yielding.

Provider process or session handles are hints, never proof. Do not search unrelated directories for a workspace. Do not silently migrate an in-progress journey to a newer create-jarvis commit.

If the customer needs a recovery instruction, use:

> 继续构建我们的 Jarvis。建设工作区是 `<path>/jarvis-build`。请读取 `CONTINUE-JARVIS.md` 和 `CONSTRUCTION-JOURNAL.md`，核验现有交付事实后从记录的 Next 继续，不要重新初始化已存在的工作。

## Guided intake and preparation

For a new journey, ask in free-form text for company identity and the documentation, code repositories and work-system sources Jarvis should learn. One pilot product or repository is enough. Probe only supplied pointers, summarize access, and ask one compact follow-up for unresolved history range, publication target or write policy.

Preparation runs `scripts/instantiate_construction_workspace.py init` against the pinned
`templates/construction-workspace/` and uses `add-repository` for each authorized code repo:

```text
jarvis-build/
├── CONTINUE-JARVIS.md
├── CONSTRUCTION-JOURNAL.md
├── BUILD-CONTEXT.md
├── work/
│   ├── company-repo-initialization.md
│   ├── company-construction.md
│   ├── repositories/<repo>/
│   │   ├── CARD.md
│   │   └── START-REPOSITORY-LEARNING.md
│   ├── reconciliation.md
│   └── jarvis-box-onboarding.md
└── evidence/
```

`BUILD-CONTEXT.md` records exact pointers, observed revisions, access probes and delivery policy without credentials or source dumps. Each work card records objective, authorized inputs, allowed writes, target repo/workspace/branch, optional provider/session handle, status, last verified checkpoint, delivered artifacts, blocker, `Next` and verification time. Repository cards additionally keep code-read, capability, model, validation, audit and delivery accounts separate.

Do not create `bootstrap-state.json`, `bootstrap-result.json` or `jarvis.toml`. These Markdown files are recovery facts, not a parser contract or runtime state service.

## Dispatch and writer ownership

The Coordinator starts or resumes Company construction and runtime work. Part 3 is the deliberate exception: the Coordinator prepares one exact command for a customer-launched top-level Codex process, shows that command with one short return instruction, and stops. Do not use a subagent as the primary repository-learning writer.

- Part 1 has one Company repo writer.
- Part 2 keeps one integrator as the only Company repo writer; scanners return evidence packets only.
- Part 3 has one independent card, one clean top-level Codex process and at most one writer per customer code repo. Never batch multiple repositories into one Codex chat or process. Disable multi-agent tools for the primary writer; isolated replay/eval processes may still receive only their bounded visible case.
- Parts 2 and 3 may overlap after the customer launches a repository process; default to one repository command at a time.
- Part 4 starts only after its reconciliation prerequisite is verified.

Default to one repository handoff at a time so the customer sees one action:

1. verify Part 1 and set the selected repository card to `ready` with no blocker;
2. run `scripts/instantiate_construction_workspace.py prepare-repository-learning --workspace <jarvis-build> --name <repo>`;
3. show only the returned `launch_command` under “请在新终端运行”，then say “完成后回到这里回复：继续”;
4. when the customer returns, verify the card, evidence, Git ref and PR/MR before marking it `completed` or starting reconciliation.

Prepare several distinct commands only when the customer explicitly asks to run repositories in parallel. A customer-launched process owns only its repository, card directory and task-local evidence; it never writes the Company Jarvis repo or `CONSTRUCTION-JOURNAL.md`.

Before pausing, changing writer or ending a session, update the current work card and journal. Never promise daemon, heartbeat, process survival or native reattachment the Host provider does not actually support.

## Part 1 — Company repository initialization

Follow `playbooks/prompts/company-repo-initialization.md`.

Instantiate the Company Jarvis template, resolve identity and publication placeholders, validate the scaffold, and deliver it according to the customer's Git policy. A new or empty remote may receive its initial default branch; an existing remote must preserve history and use a branch plus PR/MR.

The scaffold includes `runtime-governance.md` and its quick reference. At this point they define required questions and unresolved fields; they are not yet evidence that the customer's runtime foundation exists.

## Part 2 — Company Jarvis construction

Follow `playbooks/prompts/company-jarvis-construction.md`.

Build company identity, product capability modules, source routes, canonical repo fleet, cross-cutting relations, workflows, references, company tools and runtime governance from customer evidence. Customer code repos are read-only evidence in this part.

Runtime governance must mature through:

```text
template scaffold
  → customer runtime discovery
  → customer-specific constitution
  → installed and verified runtime behavior
```

Discover the customer's real Host runtime root, storage roles, repo cache/workspace rules, task-start sync, stable tools, checkout isolation, handoff, cleanup, credentials and write boundaries. If the constitution requires customer-specific Host tools or sync mechanisms, create, install and verify them within authorization. Otherwise mark the affected rule `pending-runtime-foundation`; prose alone is not completion.

Disposition every capability candidate and close product, implementation and verification anchors. Starter workflows remain `draft-template` until customized and exercised.

## Part 3 — Customer-launched repository learning

Prepare one clean top-level Codex handoff for each `work/repositories/<repo>/CARD.md`. The new process must read `playbooks/prompts/repository-learning.md` in full from the pinned method checkout; do not copy fragments of that prompt into a child-agent message.

Inspect actual code changes across the customer-selected history range. Commit messages are navigation only. Episodes are evidence samples, not the learning unit: infer the repository's current entities, ownership, state transitions, authorities, invariants and fallback rules. Project that decision model into independently triggerable trigger-to-proof logic loops. Deliver complete business task-family coverage with minimal duplication; “minimal” applies to repeated text and competing homes, never to the number of business workflows retained.

Each repository worker delivers its own commit, branch and PR/MR or an explicit read-only/blocked result, then sets its card to `delivered-awaiting-coordinator-verification`. Only the Coordinator may verify the remote facts and mark the card `completed`. Never edit the Company Jarvis repo from a repository card. A dirty local worktree or worker completion claim is not a consumable skill delivery.

## Reconciliation and workflow construction

Follow `work/reconciliation.md` and `playbooks/prompts/reconciliation.md`. Read the reconciliation section of the growth loop only when selecting or explaining the route-scoped lifecycle boundary.

Verify the Company Jarvis delivery and every repo-local ref before consuming them. Resolve usable repo pointers, retain incomplete coverage honestly, rerun Company → module/source → repo-local routing probes, and customize a route-scoped workflow with the customer's real roles, sources, branch/review/test/release policy and closure evidence.

A workflow is `construction-ready` only when its required Company and repo-local revisions are delivered and at least one controlled or real case passes. This is the gate for Part 4, not production activation.

## Part 4 — jarvis-box install, start and onboarding

Follow `playbooks/prompts/formal-runtime-deployment.md` and `work/jarvis-box-onboarding.md`.

Ask the customer one deployment question: Native or Docker. Use only the selected public `hengshi/jarvis-box` Release's installation and operations contract. Native uses the existing installing OS user and that user's authorized CLI identities. Docker runs with the same user's numeric UID/GID, persists data below a dedicated deployment home, and imports only approved portable identities from the current Host user. Before Docker installation, resolve and validate three pairwise-disjoint absolute paths: Construction Workspace, canonical Company Jarvis checkout and deployment home. A dedicated machine account is optional customer policy, not an installation prerequisite. Never copy Host HOME, SSH agent, Keychain or a complete credential store.

Before scheduled jobs can be accepted, install the pinned method packages with `scripts/install_runtime_method_skills.py` into the selected Agent's explicit discovery root, run its doctor, and prove fresh discovery of `jarvis-self-improve-skill`. Company repos do not vendor these generic packages; a template in create-jarvis or a prompt that names the skill is not runtime installation evidence.

Record the selected mode, actual runtime owner/root, release version, Docker image digest when applicable, exact create-jarvis method-skill manifest, credential capability evidence, optional connector boundary and real Agent/provider/writeback/cleanup evidence. Do not copy Compose files, environment-variable catalogs, container paths or the jarvis-box runbook into Company Jarvis. After the selected environment's real probes pass, advance the selected workflow to `ready-for-shadow`.

## Shadow delivery and evolution

Representative customer-supervised tasks advance `ready-for-shadow → shadowing → active`. Promotion requires stable routing, repo-local execution, verification and END closure, durable writeback of hidden customer steps, an exact deployment lock and customer approval.

No initial construction request can manufacture future production evidence. Without a representative task, stop honestly at `ready-for-shadow` and name the next business event.

## Non-negotiable boundaries

- Construction works without jarvis-box until Part 4.
- Company Jarvis stores company semantics, routes and cross-runtime governance; repository execution truth stays repo-local.
- jarvis-box internals stay in jarvis-box.
- After Part 4, the Company Jarvis operates in Mode B (jarvis-box协同). The customer can optionally use Mode A (standalone, no jarvis-box) on other machines: copy the Company Jarvis runtime root (`~/.&lt;slug&gt;-jarvis/`) to the target machine, source `env.sh` — it auto-detects the absence of jarvis-box and uses standalone paths.
- Eval/replay is an internal learning method, not the delivered skill.
- Publication and deployment use verified remote revisions, not uncommitted Host paths.
- The customer sees one launch command when a fresh Repository Learning process is required, then delivered repos/PRs, usable scope, approvals, blockers and the next business result—not internal phase mechanics or copied prompt fragments.
