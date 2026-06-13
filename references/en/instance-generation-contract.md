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

### Resume and overwrite policy

`bootstrap-state.json` is the resume anchor. It should record:

- confirmed answers
- generated files
- files intentionally preserved because they appear user-authored
- unresolved questions
- methodology repo URL or commit when known

On resume, do not overwrite user-authored files unless the human explicitly confirms it. Generated files may be refreshed only when they are clearly marked as scaffold-owned.

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

The agent can create placeholders for these files, but not credible final content.

---

## 4. Generation sequence

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

### Step 5 — Run a real pilot
Use the generated structure to support real work.

### Step 6 — Write back only durable learnings
Promote repeated truths, not one-off chatter.

---

## 5. Failure modes

### Bad
- auto-generating detailed known issues with no evidence
- inventing owners or maintainers
- guessing workflow stages from generic software lore
- presenting placeholder histories as if they were real institutional memory

### Better
- generating the container
- marking unknowns explicitly
- routing truth to humans or future writeback
- growing the memory layer only from actual work

---

## 6. Acceptance criteria for a responsible generator

A responsible JARVIS generator:
- [ ] separates structure from truth
- [ ] labels placeholders clearly
- [ ] requests confirmation for truth-bearing fields
- [ ] does not fake historical knowledge
- [ ] makes writeback the path to maturity rather than pretending maturity exists at setup time
