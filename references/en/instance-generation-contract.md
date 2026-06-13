# Instance Generation Contract

Use this contract to decide what a JARVIS-building agent may generate directly, what must be confirmed by humans, and what can only become real through continued use and writeback.

## The core principle

Do not present scaffolding as truth.

Every generated artifact should fall into one of three classes:
1. **safe to scaffold automatically**
2. **requires human confirmation before being treated as truth**
3. **cannot be honestly generated up front and must emerge from real work**

## Runtime caller contract

Some callers, such as jarvis-box, invoke this repository through a runtime agent instead of copying templates into the caller repo. In that mode, this repository remains the methodology source of truth and the caller only supplies inputs, target paths, and runtime constraints.

The runtime owns install, setup, credentials, webhooks, service lifecycle, task state, logs, and agent process execution. create-jarvis-skill must not generate or take ownership of runtime scripts, system services, schedulers, PATH setup, workspace clone logic, or secret storage.

### Required normalized inputs

- target home: `JARVIS_TARGET_HOME` or `JARVIS_HOME`
- entry skill: `JARVIS_ENTRY_SKILL`, default `SKILL.md`
- company name: `JARVIS_COMPANY_NAME`
- first loop: `JARVIS_FIRST_LOOP`
- GitLab scope: `GITLAB_HOST`, `GITLAB_PROJECTS`
- source-of-truth notes: `JARVIS_SOURCE_OF_TRUTH`
- owners: `JARVIS_OWNERS`
- writeback policy: `JARVIS_WRITEBACK_STRATEGY`
- neutral runtime root: `JARVIS_BOX_HOME` when supplied
- method repo URL: `CREATE_JARVIS_SKILL_REPO_URL`, defaulting to `https://github.com/hengshi/create-jarvis-skill.git`
- method repo commit/ref when known

### Minimum runtime output

A runtime-generated instance must include a valid entry skill at `JARVIS_HOME/SKILL.md` unless a different `JARVIS_ENTRY_SKILL` is explicitly supplied. It must also include enough bootstrap artifacts for a future agent to continue the pilot without rediscovery:

- `README.md`
- `MAINTENANCE.md`
- build brief
- source inventory
- repo inventory
- workflow inventory
- ownership map
- rollout plan
- confirmation checklist
- `bootstrap-state.json`
- `bootstrap-result.json`

### Resume and overwrite policy

`bootstrap-state.json` is the resume anchor. It should record:

- confirmed answers
- generated files
- files intentionally preserved because they appear user-authored
- unresolved questions
- methodology repo URL or commit when known
- runtime input summary without secret values
- last completed phase
- conflicts between previous confirmed answers and new runtime input

On resume, do not overwrite user-authored files unless the human explicitly confirms it. Generated files may be refreshed only when they are clearly marked as scaffold-owned.

### Runtime result policy

`bootstrap-result.json` is for the runtime. It should include:

- `schema_version`
- `status`: `completed`, `needs-input`, `blocked`, or `failed`
- `result_code`
- `retryable`
- `summary`
- `paths.jarvis_home`, `paths.jarvis_target_home`, and `paths.entry_skill`
- method repo URL and commit/ref
- created, updated, and preserved files
- unresolved questions, missing inputs, conflicting inputs, and blockers
- writeback policy
- next action
- generated timestamp

If required inputs are missing in noninteractive mode, write a blocked result instead of guessing.

### Secrets boundary

Generated artifacts may record secret names, configured/unconfigured status, and safe secret paths or provider names. They must not record secret values.

### Naming policy

Generated customer output must not assume Hengshi-specific runtime names, paths, or owners. Use customer-specific names for the JARVIS instance and use neutral runtime variables such as `JARVIS_HOME`, `JARVIS_TARGET_HOME`, and `JARVIS_BOX_HOME`.

---

## 1. Safe to scaffold automatically

These artifacts are usually safe to generate as first-pass structure:

- JARVIS root README skeleton
- MAINTENANCE guide skeleton
- source inventory skeleton
- repo inventory skeleton
- workflow inventory skeleton
- skill backlog
- ownership map structure
- rollout plan skeleton
- company JARVIS entry skill stub
- source skill stubs
- repo skill stubs
- workflow skill stubs
- module overview skeletons
- source README skeletons
- cross-cutting skeletons such as module interactions and version changelog indexes
- tools index skeleton
- raw export boundary notes

These are structure and method artifacts. They should be generated with visible placeholders and explicit adaptation notes.

Skill backlog entries may be scaffolded, but each entry should include outcome, owner or unresolved owner, evidence source, overlap/merge candidate, and whether `no_skill_gap` is currently plausible.

---

## 2. Requires human confirmation

These items should not be treated as settled truth until a human owner confirms them:

- the business intent for JARVIS
- the first valuable workflow to prove
- module boundaries
- source names and source owners
- repo roles and maintainers
- source-of-truth locations
- workflow boundaries and handoffs
- security or compliance-sensitive access paths
- ownership assignments
- writeback destinations
- what is explicitly out of scope for the current rollout
- whether a proposed skill is truly needed or an existing skill/reference is enough
- promotion target for calibration outcomes: repo-local, central JARVIS, or upstream methodology

Agents may propose these items. Humans should ratify them.

---

## 3. Must emerge from real use

These items cannot be honestly generated from zero and should grow through START → WORK → END loops:

- real known-issue patterns
- real decisions with rationale
- real rejected-feature memory
- meaningful test coverage summaries
- trustworthy cross-module interaction knowledge
- durable version-change understanding
- useful operational tools born from repeated need
- mature repo-local operating guidance
- mature workflow evidence and handoff rules
- failure taxonomy and calibration evidence after real pilot or replay
- upstream methodology changes derived from multiple redacted real cases

The agent can create placeholders for these files, but not credible final content.

---

## 4. Skill creation and calibration boundary

Before creating or expanding a skill, evaluate `no_skill_gap`.

Use `no_skill_gap` when:
- existing source, repo, workflow, or governance skills already cover the method;
- the failure was caused by missing task evidence, runtime behavior, source data, or code, not missing skill guidance;
- the case is a one-off exception;
- the fix belongs in the owning repo/source rather than in JARVIS methodology.

Create or expand a skill only when:
- a repeatable closed loop needs stable procedural guidance;
- there is an owner;
- the trigger is clear;
- overlap with existing skills was checked;
- expected value is observable;
- replay or pilot evidence shows the update helps.

Promotion rule:
- repo execution details stay repo-local;
- company routing, ownership, and workflow orchestration stay in central JARVIS;
- only company-neutral method moves upstream into create-jarvis-skill.

---

## 5. Generation sequence

### Step 1 — Define the first loop
Choose one real business loop and name its success signal.

### Step 2 — Classify outputs by generation boundary
For each intended artifact, decide whether it is:
- scaffoldable now,
- requires human confirmation,
- or must emerge later.

### Step 3 — Generate only the scaffoldable layer
Create the initial structure with clear placeholders and contracts.

### Step 4 — Get humans to confirm truth-bearing fields
Do not silently lock in business truth, ownership, or operating boundaries.

### Step 5 — Run a real shadow pilot
Use the generated structure to support real work.

### Step 6 — Calibrate and write back only durable learnings
Promote repeated truths, not one-off chatter.

---

## 6. Failure modes

### Bad
- auto-generating detailed known issues with no evidence
- inventing owners or maintainers
- guessing workflow stages from generic software lore
- presenting placeholder histories as if they were real institutional memory
- creating a new skill before checking `no_skill_gap`
- promoting private company examples into generic methodology

### Better
- generating the container
- marking unknowns explicitly
- routing truth to humans or future writeback
- growing the memory layer only from actual work
- treating `no_skill_gap` as a valid calibration result

---

## 7. Acceptance criteria for a responsible generator

A responsible JARVIS generator:
- [ ] separates structure from truth
- [ ] labels placeholders clearly
- [ ] requests confirmation for truth-bearing fields
- [ ] does not fake historical knowledge
- [ ] makes writeback the path to maturity rather than pretending maturity exists at setup time
- [ ] records runtime bootstrap state and result when runtime-driven
- [ ] checks `no_skill_gap` before skill growth
- [ ] keeps private instance facts out of generic methodology
