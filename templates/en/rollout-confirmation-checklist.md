# Rollout Confirmation Checklist

Use this checklist before calling a generated JARVIS pilot-ready.

## Human-confirmed truths

- [ ] the business intent is confirmed
- [ ] the first valuable loop is confirmed
- [ ] shadow-pilot success criteria are confirmed
- [ ] included sources are confirmed
- [ ] included repos are confirmed
- [ ] included workflows are confirmed
- [ ] ownership assignments are confirmed
- [ ] source-of-truth locations are confirmed
- [ ] writeback policy is confirmed

## Runtime boundary

- [ ] runtime owner is jarvis-box or another named runtime, not create-jarvis-skill
- [ ] `JARVIS_HOME` / generated instance root is confirmed
- [ ] `JARVIS_TARGET_HOME` is writable or unresolved in `bootstrap-result.json`
- [ ] `JARVIS_BOX_HOME`, if present, is treated only as runtime host root
- [ ] runtime install/setup/service/webhook responsibilities are outside this instance scaffold
- [ ] secret values are not written to generated artifacts
- [ ] noninteractive missing inputs are recorded as unresolved rather than guessed

## Generated structure quality

- [ ] placeholders are explicit
- [ ] stable entrypoints exist
- [ ] source / repo / workflow layers are represented where needed
- [ ] central JARVIS behaves as router, not content mirror
- [ ] repo-local truth remains with repos
- [ ] source skills route and interpret sources without dumping source content
- [ ] maintenance guidance exists
- [ ] writeback expectations exist
- [ ] calibration and `no_skill_gap` expectations exist

## Maturity honesty

- [ ] no fake history is presented as real knowledge
- [ ] no placeholder owner is presented as a real owner
- [ ] no guessed workflow is presented as a validated company flow
- [ ] the pilot scope is smaller than the company-wide dream
- [ ] the result is described as pilot-ready, not pilot-proven, until a real loop has run
