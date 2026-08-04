# Repository skill depth contract

This artifact is delivered with the repository router skill. It is not a
history report. It tells a future task Agent where the implementation model is
anchored, what proof is strong enough, and how the skill set notices that its
model has drifted.

Companion artifacts:

- `skill-depth.json`: machine-readable inventory for every delivered skill;
- `../evals/evals.json`: runtime-hidden route, negative, forward and handoff
  cases; normal task execution must not load expected answers;
- `../scripts/audit_skill_depth.py`: deterministic structure, path, coverage
  and eval-integrity gate.

## Six required depth dimensions

### D1 — Implementation anchors

For every skill, identify the current authority plus the first executable
entry, key state/data/resource transition and closest proof surface. Use exact
repo-relative paths and symbols. A directory name or historical commit alone
is not an implementation model. Detailed matrices belong in this reference;
the skill body keeps only the workflow and direct links.

### D2 — Mechanical controls

Identify what can be checked by code rather than prose: generator, parser,
schema check, focused test, build target, sanitizer, ABI diff, lifecycle
harness, or this depth auditor. Record the real command and whether it was
executed. If no deterministic control exists, say what observable result and
owner close the gap; do not invent a passing command.

### D3 — Risk-based evidence promotion

Record both risk and evidence level per skill. L1 is sufficient only for a
stable current-state capability whose claims are bounded by the checks that
actually ran. Concurrency, security, persistence, migration, state machines,
resource lifecycles, startup/shutdown and failure recovery normally require
L2. Route overlap, an easy wrong alternative model, or a hidden-oracle risk
requires L3. Missing proof narrows claims; it does not disappear from the
inventory.

### D4 — Runtime-hidden forward eval

At least one case per high-risk or overlapping route must start from a current
revision task not used to write that skill. The task Agent sees only the prompt
and repository; expected route, forbidden route, behavioral invariants and
proof are kept outside its context until scoring. Include should-trigger,
must-not-trigger and adjacent-route cases. Rewording a historical answer is not
a forward eval.

### D5 — Cross-repository closure

For every boundary-crossing skill, record the local last authority, downstream
first authority, handoff payload and end-to-end proof owner. The current repo
must not claim downstream execution from a provider call or compile. A
cross-repo case passes only when routing selects the correct primary owner and
preserves the boundary payload.

### D6 — Drift and self-improve writeback

Record the files/symbols/commands whose change can invalidate each skill. On a
real-task failure, review correction, path drift or eval regression, run the
audit and route evidence through `jarvis-self-improve-skill`. Self-improve
compares the old model and candidate on same, adjacent and forward cases, then
writes one durable primary home. It never edits a skill during the task merely
to rationalize the current answer.

## Required per-skill record

Each `skill-depth.json` entry answers:

| Field | Required meaning |
|---|---|
| `name` | exact delivered package name |
| `risk` | `normal`, `high`, or `critical`, with a short reason |
| `level` | honest L1/L2/L3 claim |
| `authority` | exact current paths/symbols that own the model |
| `entrypoints` | first code/command/test surfaces for the task |
| `transitions` | state/data/resource loop and failure close |
| `mechanical_controls` | commands/gates and actual execution status |
| `forward_eval_ids` | runtime-hidden cases covering this skill |
| `cross_repo` | boundary owner/payload/proof, or explicit `none` |
| `drift_watch` | paths, symbols, commands or contracts that invalidate it |

The auditor proves structural completeness and path freshness. It does not
upgrade behavioral evidence: L2/L3 still require isolated replay/eval results.
