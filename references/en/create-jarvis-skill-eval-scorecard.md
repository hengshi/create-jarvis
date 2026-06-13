# Create JARVIS Skill Eval Scorecard

Use this scorecard to judge generated outputs from `create-jarvis-skill` or from a runtime agent invoking it.

## Dimensions

| Dimension | Pass condition |
|---|---|
| runtime contract | runtime-driven output includes valid entry skill, `bootstrap-state.json`, and `bootstrap-result.json` |
| path semantics | output distinguishes `JARVIS_HOME`, `JARVIS_TARGET_HOME`, and `JARVIS_BOX_HOME` |
| secret boundary | output records secret status and paths only, never values |
| noninteractive behavior | missing required input becomes `needs-input`, not guessed truth |
| pilot-first discipline | output proves one workflow before mapping the whole company |
| truth boundary | placeholders are explicit and not treated as confirmed facts |
| source dump resistance | source skills route/search/summarize without copying raw source material |
| repo-local boundary | repo execution truth stays in repo-local skills |
| workflow quality | workflow skills include trigger, evidence, gates, escalation, completion, and END writeback |
| calibration | backlog or notes include `no_skill_gap`, merge, update, create, or defer decisions |
| promotion safety | private facts are not moved into generic method |

## Minimum Pass

A case passes when:
- all required files exist;
- `bootstrap-result.json` status matches the case expectation when present;
- `bootstrap-result.json` and `bootstrap-state.json` include every required dotted field named by the case;
- forbidden patterns are absent;
- required patterns are present;
- no blocker or major finding is produced.

## Gate

Run:

```bash
python3 scripts/run_create_jarvis_skill_eval.py \
  --cases evals/create-jarvis-skill-cases \
  --outputs eval-fixtures/create-jarvis-skill \
  --report .eval-runs/ci-report
```

Use `--write-prompts` for agent replay prompt generation. Do not use `--allow-missing-outputs` as a release gate.
