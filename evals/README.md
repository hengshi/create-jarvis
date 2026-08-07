# Real, scoreable customer-journey evals

`evals.json` contains three complete episodes, not a list of policy questions:

1. new journey → preparation → verified Part 1 stop;
2. interrupted Part 2 → customer Host runtime foundation → published runtime constitution;
3. Coordinator prepares one clean-process handoff → customer launches one top-level Codex for one repo → full current capability inventory + historical logic-loop replay → coverage-complete repo-local delivery awaiting Coordinator verification.

Each executor starts in a fresh directory and runs the attached
`fixtures/build_customer_journey_fixture.py`. The builder creates disposable customer inputs with real
Git repositories, commits, bare remotes, dirty-worktree boundaries and, for resume cases, a valid
Construction Workspace plus Company scaffold. It refuses to overwrite an existing fixture root.

The fixture is visible input, not a checked-in expected output. Case 3's executor must discover two
independently triggerable risky loops by reading real patch/code/test history, while also inventorying
the complete current task-family surface. A stable current-state capability is intentionally absent
from the customer brief, so an issue-only learner under-generates and fails. Commit messages remain
non-authoritative. Each isolated replay worker sees its issue, replay and selected parent snapshot,
not the later fix. The scorer requires a lightweight router, distinct focused loop skills, a capability
coverage ledger and independently triggerable guidance for the unprompted current capability. It does
not require an exact total skill count. A one-repo-one-skill result, issue-only topology, directory
quota, or risky loops without cross-route separation fails.

## Scoring

Every eval has explicit `expectations`. Grade transcript behavior and actual artifacts. In addition,
run the deterministic artifact scorer from the method checkout:

```bash
python3 evals/verify_eval_artifacts.py \
  --case <new-journey|runtime-governance|repository-learning-worker> \
  --fixture-root <run-directory>/customer-fixture \
  --method-repository <evaluated-create-jarvis-checkout>
```

The scorer composes `scripts/verify_construction_workspace.py`,
`scripts/verify_company_output.py` and case-specific filesystem/Git checks. Its pass is necessary but
not sufficient: a grader still verifies scope discipline, real replay behavior, evidence quality,
single-writer ownership and lifecycle claims from the transcript.

For a comparative `skill-creator` run, use the same freshly generated case, runtime Agent and
permissions for the current branch and the read-only baseline snapshot. Do not reuse a mutated fixture
between configurations. Save transcripts, output trees, grading JSON, timing and token metrics under
the skill-creator iteration workspace, then generate the standard eval viewer before interpreting the
results.
