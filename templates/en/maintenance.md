# [Company / Product] JARVIS Maintenance Guide

> JARVIS is the routing, indexing, and synthesis layer for [Company / Product].
> It is not a raw content mirror. It is the operating substrate that helps agents understand the company, enter the right repos and work surfaces, and preserve what they learn.

---

## 1. Mission and Scope

### Mission

State in 2-4 sentences:
- why this JARVIS exists,
- who it serves,
- what the first high-value closed loop is,
- and what kind of organizational capability it should unlock.

### Scope for the current rollout

- **Current phase**: `<phase>`
- **Primary loop**: `<workflow or problem area>`
- **Included sources**: `<list>`
- **Included repos**: `<list>`
- **Included workflows**: `<list>`
- **Explicitly out of scope for now**: `<list>`

---

## 2. Data Sources and Access Paths

| Source | Type | Owner | Access Path | Auth / Tooling | Notes |
|---|---|---|---|---|---|
| `<source>` | `<docs/wiki/issues/repo/meetings/...>` | `<team/person>` | `<url/cli/path>` | `<tool/token/login>` | `<constraints>` |

Keep this table pragmatic. It should help a future agent or owner know where truth lives and how to reach it.

---

## 3. Skill Layers

### JARVIS entry skill

Describe the central entry skill and its boundary.

| Skill | Instance root | Runtime owner | Status | Notes |
|---|---|---|---|---|
| `<company-jarvis>` | `<JARVIS_HOME>` | `<jarvis-box/other>` | `<planned/in-progress/ready>` | `<notes>` |

The entry skill routes and closes loops. It does not mirror sources, replace repo-local skills, or manage runtime service behavior.

### Source skills

List the skills that help agents read company digital assets.

| Skill | Target source | Owner | Status | Notes |
|---|---|---|---|---|
| `<skill>` | `<source>` | `<owner>` | `<planned/in-progress/ready>` | `<notes>` |

### Repo skills

List the skills that help agents operate inside specific repos.

| Skill | Repo | Owner | Status | Notes |
|---|---|---|---|---|
| `<skill>` | `<repo>` | `<owner>` | `<planned/in-progress/ready>` | `<notes>` |

### Workflow skills

List the skills that help agents complete cross-repo or cross-role loops.

| Skill | Workflow | Owner | Status | Notes |
|---|---|---|---|---|
| `<skill>` | `<workflow>` | `<owner>` | `<planned/in-progress/ready>` | `<notes>` |

---

## 4. Write Contracts

### Global rules

1. **Index, don’t dump.** Summarize and route; do not copy raw source material unless there is a compelling reason.
2. **Patterns over logs.** Capture recurring lessons, constraints, and routing clues rather than raw chronological history.
3. **One home per truth.** If knowledge belongs to a repo-local source of truth, route to that repo instead of centralizing it here.
4. **Mark placeholders explicitly.** Separate reusable method from company truth.
5. **Read before writing.** Match the existing structure before appending or rewriting files.

### File responsibilities

| File | Should contain | Should not contain |
|---|---|---|
| `known-issues.md` | recurring failure patterns, likely root causes, repair clues | raw ticket dumps |
| `decisions.md` | durable design decisions, tradeoffs, why | incidental bugfix notes |
| `rejected-features.md` | ideas declined, rationale, decision context | active proposals still under discussion |
| `overview.md` | role, boundaries, key paths, mental model | full implementation detail |
| source skill docs | how to reach and interpret a source | a mirror of the source content |
| repo skill docs | repo-local execution guidance | company-wide policy that belongs in JARVIS |
| workflow skill docs | handoffs, artifacts, evidence, writeback | repo-local low-level detail better kept with repos |

---

## 5. Update Triggers

| Event | Update expected |
|---|---|
| a recurring bug is diagnosed or fixed | update `known-issues.md` or related source/repo skill |
| a durable product or engineering decision is made | update `decisions.md` |
| a proposal is explicitly rejected | update `rejected-features.md` |
| a workflow changes materially | update the workflow inventory or workflow skill |
| a repo changes its operating guidance | update the repo-local skill and refresh JARVIS routing |
| a new data source becomes strategically important | add or revise a source skill |
| rollout ownership changes | update ownership map and rollout plan |
| a pilot or eval case fails | classify failure and decide no-skill-gap / merge / update / create |
| an internal method proves reusable beyond this instance | consider upstream create-jarvis-skill promotion after redaction |

---

## 6. Ownership and Handoff

| Area | Primary owner | Supporting owner(s) | Notes |
|---|---|---|---|
| source layer | `<owner>` | `<owners>` | |
| repo layer | `<owner>` | `<owners>` | |
| workflow layer | `<owner>` | `<owners>` | |
| maintenance / governance | `<owner>` | `<owners>` | |

A healthy JARVIS should be continue-able by another owner without full rediscovery.

---

## 7. The Closed Loop: START → WORK → END

### START
- read the relevant JARVIS routing and history first
- identify the best source skills, repo skills, and workflow skills for the task
- check whether a similar failure, decision, or rejected path already exists

### WORK
- execute in the right source, repo, or workflow context
- follow repo-local instructions when work becomes repo-specific
- keep the current rollout scope in mind; do not widen it casually

### END
- write back durable learnings
- update the correct layer rather than dumping notes into a random file
- record whether the work should change a source skill, repo skill, workflow skill, or governance artifact
- record `no_skill_gap` when existing guidance was sufficient

---

## 8. Calibration and Promotion

### Calibration cadence

- **Review cadence**: `<weekly / per pilot / per release / other>`
- **Eval case sources**: `<real tasks / historical artifacts / owner corrections / replay cases>`
- **Owner**: `<owner>`

### Failure taxonomy

Use the shared taxonomy:
- `routing_failure`
- `truth_failure`
- `boundary_failure`
- `writeback_failure`
- `duplication_failure`
- `bloat_failure`
- `promotion_failure`
- `verification_failure`
- `no_skill_gap`

### Promotion ladder

1. Keep task-local notes task-local.
2. Move repo execution truth to repo-local skills.
3. Move cross-repo routing and workflow rules to this central JARVIS instance.
4. Move only redacted, company-neutral method upstream to create-jarvis-skill.

Do not create or expand skills unless evidence shows a repeatable method gap.

---

## 9. Rollout Status

- **Current maturity**: `<installed / pilot-ready / pilot-proven / controlled-ops / mature>`
- **Next highest-leverage additions**:
  1. `<item>`
  2. `<item>`
  3. `<item>`
- **Known gaps**: `<list>`
- **Last review date**: `<date>`
- **Next review trigger**: `<event/date>`
