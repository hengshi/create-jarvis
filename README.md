# Create JARVIS Skill

**Bootstrap an enterprise JARVIS with any agent.**

- English (this file): `README.md`
- 中文：`README.zh.md`

> Note: `SKILL.md` is the single golden path. Keep it as the only authoritative execution path. The supporting documentation under `references/en/`, `references/zh/`, `templates/en/`, and `templates/zh/` is organized as mirrored same-name files across English and Chinese.

This repo is not just a repo generator. It is a methodology and practical guide for helping agents turn a company's digital assets, repos, workflows, and runtime constraints into durable, executable organizational capability.

JARVIS starts as knowledge, but its real goal is execution:
- help agents understand the company,
- help agents enter the right repos and work surfaces,
- help agents follow real delivery workflows,
- and help the organization compound what agents learn over time.

## What This Project Is

`create-jarvis-skill` is a meta-skill for building company-specific JARVIS systems.

It helps an agent:
1. clarify why a company needs JARVIS,
2. inventory sources, repos, and workflows,
3. identify central JARVIS, source, repo-local, and workflow skill boundaries,
4. generate a runtime-linkable first pass,
5. force company-specific adaptation,
6. run a shadow pilot,
7. and evolve the system through writeback and calibration.

## What This Project Is Not

It is **not**:
- a one-shot exporter for a knowledge repo,
- a document dumping workflow,
- a promise that one agent can finish an enterprise rollout in one session,
- a replacement for repo-local source of truth,
- or a replacement for jarvis-box runtime install/setup/service/task logic.

If it only generates a pretty `<company>-jarvis` repo, it has not gone far enough.

## What a Strong Result Looks Like

A strong result is not just a generated repo. It is a usable company-specific JARVIS instance.

A useful first pass can already produce:
- a JARVIS core scaffold,
- source / repo / workflow inventories,
- skill backlog and ownership map,
- rollout plan,
- and first-pass source / repo / workflow skill stubs.

But a mature result goes further. It accumulates:
- real company history,
- real source routing,
- real repo-local operating guidance,
- real workflow closure,
- and repeated START → WORK → END writeback.

So the standard is:
- **installed scaffold** = enough structure for a runtime to link the entry skill
- **pilot-ready** = enough confirmed truth to begin a shadow pilot
- **pilot-proven** = at least one real START -> WORK -> END loop has evidence
- **controlled ops** = writeback and calibration happen under owner review
- **mature instance** = part of how the organization actually thinks and works

This project is meant to help agents move through those stages intentionally.

## The Four Ecosystem Layers

A strong JARVIS rollout needs four knowledge layers plus a separate runtime layer.

### 1. JARVIS entry skill

The central company entrypoint.

It owns:
- loop identification,
- routing,
- index and synthesis,
- next-hop selection,
- and END writeback judgment.

It does not mirror source systems, replace repo-local skills, or manage runtime services.

### 2. Source skills
Skills that help agents access and understand company digital assets.

Examples:
- docs and wiki systems
- issue trackers
- meeting notes
- analytics / BI systems
- customer feedback systems
- incident and support records

### 3. Repo-local skills
Skills that help agents execute inside specific repos.

Examples:
- frontend repo skills
- backend repo skills
- docs repo skills
- QA / automation repo skills
- infrastructure repo skills

These usually belong with the repo itself. JARVIS should route to them, index them, and help keep the company-wide map coherent.

### 4. Workflow skills
Skills that help agents complete real cross-team loops.

Examples:
- PRD → SPEC → implementation
- bug intake → triage → fix → regression → release note
- feature work across frontend, backend, QA, and docs

### Runtime layer

jarvis-box or another runtime owns install, setup, credentials, webhooks, task execution, state, logs, and service lifecycle. create-jarvis-skill owns methodology, scaffold, pilot, writeback, and calibration contracts.

## What a Good First Pass Produces

A useful first pass often includes:

- a JARVIS core repo or workspace
- a `jarvis-build-brief.md` single source of truth
- a source inventory
- a repo inventory
- a workflow inventory
- a skill backlog split by source / repo / workflow layers
- an ownership map
- a rollout plan
- first-pass templates and scaffolds
- explicit company adaptation notes
- runtime bootstrap state/result files when invoked by jarvis-box or another runtime

That is the real output — not just one repo.

## Working Principles

- **Index, don’t dump.** JARVIS should route, summarize, and extract patterns instead of copying raw source material.
- **Patterns over logs.** A known-issues file should capture recurring failure patterns, not raw ticket history.
- **Company adaptation is mandatory.** Generated output must separate reusable method from company truth.
- **Repo truth stays with repos.** JARVIS may index or point, but it should not absorb repo-local source of truth by default.
- **History matters most.** Historical bugs, decisions, and rejected ideas are often more valuable than current status snapshots.
- **Build for handoff.** JARVIS should survive changes in owner, team, or agent.
- **Unlock the first closed loop first.** Do not wait for perfect coverage before proving value.
- **Calibrate from failures.** Use eval cases, failure taxonomy, `no_skill_gap`, and scoped skill updates instead of growing skills by reflex.
- **Promote carefully.** Internal company lessons move upstream only after redaction and method-level generalization.

## How to Use

### Step 1 — Give `SKILL.md` to your agent

Ask your agent to read `SKILL.md` and use this repo as the methodology for building JARVIS.

Examples:
- "Read `SKILL.md` and help me bootstrap JARVIS for my company."
- "Use this repo to map our sources, repos, and workflows into a JARVIS rollout plan."
- "Use `create-jarvis-skill` to generate the first-pass JARVIS scaffolds and backlog for our company."

### Runtime callers such as jarvis-box

jarvis-box should call this repository through its configured runtime agent instead of bundling these templates inside jarvis-box. The runtime supplies `JARVIS_TARGET_HOME`, `JARVIS_COMPANY_NAME`, `JARVIS_FIRST_LOOP`, GitLab scope, owners, and writeback policy; this repository supplies the methodology and output contract.

In runtime mode, the agent must create a valid `$JARVIS_HOME/SKILL.md`, bootstrap artifacts, `bootstrap-state.json`, and `bootstrap-result.json` in the target home when possible. Use neutral runtime variables such as `JARVIS_HOME`, `JARVIS_TARGET_HOME`, and `JARVIS_BOX_HOME`; do not assume a customer runtime root is named after Hengshi. The default method repo URL is `https://github.com/hengshi/create-jarvis-skill.git`.

This repo carries a deterministic eval harness for the runtime/bootstrap contract:

```bash
python3 scripts/run_create_jarvis_skill_eval.py \
  --cases evals/create-jarvis-skill-cases \
  --outputs eval-fixtures/create-jarvis-skill \
  --report .eval-runs/ci-report
```

Use `--write-prompts .eval-runs/prompts` to export prompts for a runtime or agent replay. Do not use `--allow-missing-outputs` as a release gate.

### Step 2 — Clarify the first valuable loop

Do not begin with structure for structure’s sake.

First determine:
- why the company wants JARVIS,
- who needs it,
- what the first high-value workflow is,
- and how success will be recognized.

### Step 3 — Inventory the real operating surface

Use the provided templates to map:
- digital assets,
- repos,
- workflows,
- owners,
- and the current source of truth.

### Step 4 — Generate the first pass

Use the skill to create:
- JARVIS core scaffolds,
- skill backlog,
- ownership map,
- rollout plan,
- and the first high-leverage source / repo / workflow skill stubs.

Use the adoption references when you need a practical rollout shape rather than more abstraction:
- `references/en/runtime-bootstrap-contract.md`
- `references/en/jarvis-ecosystem-architecture.md`
- `references/en/pilot-workflow-methodology.md`
- `references/en/adoption-guide.md`
- `references/en/example-pilot-shape.md`
- `references/en/concrete-instance-topology.md`
- `references/en/instance-readiness.md`
- `references/en/detailed-maintenance-contracts.md`
- `references/en/instance-generation-contract.md`
- `references/en/skill-calibration-loop.md`
- `references/en/internal-to-generic-promotion.md`

Chinese mirrors with the same basenames are available under `references/zh/`.

### Step 5 — Adapt, don’t cargo-cult

Replace placeholders with company truth.

The point is not to copy this repo mechanically. The point is to adapt its method to the company’s actual systems, people, language, and workflows.

### Step 6 — Continue as a rollout

Once the first pass exists, continue through staged rollout rather than restarting from scratch.

## Repo Structure

```text
create-jarvis-skill/
├── README.md
├── README.zh.md
├── SKILL.md
├── references/
│   ├── en/
│   │   ├── positioning.md
│   │   ├── company-adaptation.md
│   │   ├── instance-generation-contract.md
│   │   └── ...
│   └── zh/
│       ├── positioning.md
│       ├── company-adaptation.md
│       ├── instance-generation-contract.md
│       └── ...
└── templates/
    ├── en/
    │   ├── jarvis-build-brief.md
    │   ├── source-inventory.md
    │   ├── repo-inventory.md
    │   └── ...
    └── zh/
        ├── jarvis-build-brief.md
        ├── source-inventory.md
        ├── repo-inventory.md
        └── ...
```

## Generation Discipline

A responsible JARVIS generator should:
- scaffold structure aggressively,
- ask humans to confirm truth-bearing fields,
- and leave real historical memory to grow through actual writeback.

That is why this repo now includes:
- runtime bootstrap contracts for jarvis-box-style callers,
- ecosystem layer boundaries,
- pilot workflow methodology,
- concrete instance topology guidance,
- instance readiness levels,
- a generation contract,
- detailed maintenance contracts,
- calibration and promotion rules,
- and a fuller set of instance templates.

## Why This Matters

Agents are no longer only code generators. In strong environments, they can participate in planning, implementation, testing, documentation, and cross-repo delivery.

That only works when the organization gives them a real operating substrate:
- structured memory,
- clear routing,
- repo-local instructions,
- cross-team workflow guidance,
- and a way to preserve what they learn.

That substrate is JARVIS.

## Background Reading

These essays explain the broader thinking behind JARVIS:

1. [Building JARVIS for Software Companies](https://chenjunhao.cn/2026/03/23/building-jarvis-for-software-companies/)
2. [Why One-Shot AI Dev Experiments Can't Reveal the Real Upper Bound](https://chenjunhao.cn/2026/03/24/why-one-shot-ai-dev-experiments-cannot-reveal-the-real-upper-bound/)
3. [From AI Writing Code to AI-Driven R&D — The Gap Is JARVIS](https://chenjunhao.cn/2026/03/24/from-ai-writing-code-to-ai-driven-r-and-d-the-gap-is-jarvis/)
4. [How to Run an AI R&D Experiment: What You Validate Is Loop Closure, Not Code Output](https://chenjunhao.cn/2026/03/24/how-to-run-an-ai-r-and-d-experiment-what-you-validate-is-loop-closure-not-code-output/)
5. [JARVIS and Harness Engineering](https://chenjunhao.cn/2026/03/31/jarvis-and-harness-engineering/)

## License

© 2026 [Hengshi](https://github.com/hengshi). All rights reserved.

JARVIS is a paid consulting product. This skill is provided for licensed users to bootstrap their JARVIS knowledge base.

For licensing and consulting inquiries:
- 🌐 [hengshi.com](https://hengshi.com)
- 📧 hi@hengshi.com
- 📞 15810120570
