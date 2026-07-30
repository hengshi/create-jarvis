# Real, scoreable customer-journey evals

`evals.json` contains three complete episodes, not a list of policy questions:

1. new journey → preparation → verified Part 1 stop;
2. interrupted Part 2 → customer Host runtime foundation → published runtime constitution;
3. interrupted Part 3 → historical replay → repo-local delivery → Reconciliation Gate.

Each executor starts in a fresh directory and runs the attached
`fixtures/build_customer_journey_fixture.py`. The builder creates disposable customer inputs with real
Git repositories, commits, bare remotes, dirty-worktree boundaries and, for resume cases, a valid
Construction Workspace plus Jarvis scaffold. It refuses to overwrite an existing fixture root.

The fixture is visible input, not a checked-in expected output. Case 3's executor must discover the
episode by reading real patch/code/test history; commit messages are deliberately non-authoritative.
An isolated replay worker should see the issue, replay and selected parent snapshot, not the later fix.

## Scoring

Every eval has explicit `expectations`. Grade transcript behavior and actual artifacts. In addition,
run the deterministic artifact scorer from the method checkout:

```bash
python3 evals/verify_eval_artifacts.py \
  --case <new-journey|runtime-governance|repository-reconciliation> \
  --fixture-root <run-directory>/customer-fixture \
  --method-repository <evaluated-create-jarvis-checkout>
```

The scorer composes `scripts/verify_construction_workspace.py`,
`scripts/verify_jarvis_output.py` and case-specific filesystem/Git checks. Its pass is necessary but
not sufficient: a grader still verifies scope discipline, real replay behavior, evidence quality,
single-writer ownership and lifecycle claims from the transcript.

For a comparative `skill-creator` run, use the same freshly generated case, runtime Agent and
permissions for the current branch and the read-only baseline snapshot. Do not reuse a mutated fixture
between configurations. Save transcripts, output trees, grading JSON, timing and token metrics under
the skill-creator iteration workspace, then generate the standard eval viewer before interpreting the
results.
