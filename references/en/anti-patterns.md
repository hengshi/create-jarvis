# Anti-Patterns

## 1. The pretty shell
Generating a polished JARVIS repo without clarifying the business intent, first loop, or next owners.

**Better:** define the first valuable loop, then generate only what supports it.

## 2. The content dump
Copying source documents, issue bodies, or meeting notes into JARVIS.

**Better:** extract patterns, routing clues, and durable summaries.

## 3. Centralizing everything
Stuffing repo-local truth into the central JARVIS repo.

**Better:** keep repo-local execution guidance with the repo and let JARVIS route to it.

## 4. Placeholder theater
Leaving placeholders that look like validated company truth.

**Better:** mark placeholders explicitly and name the expected owner for replacement.

## 5. Exhaustiveness before value
Trying to map every source, repo, and workflow before proving the first useful loop.

**Better:** start with the smallest scope that can demonstrate compounding value.

## 6. Single-hero design
Assuming one person or one agent can build and maintain JARVIS alone.

**Better:** define ownership and handoff early.

## 7. Static mindset
Treating the first scaffold as a finished JARVIS.

**Better:** ship the first pass as a rollout stage with backlog and next steps.

## 8. Skill inflation
Creating a new skill for every failure or idea.

**Better:** check `no_skill_gap`, merge with existing skills by default, and require evidence before skill growth.

## 9. Premature upstreaming
Moving company-specific facts, examples, repo names, or issue IDs into generic create-jarvis-skill methodology.

**Better:** promote only redacted, company-neutral method after the pattern proves reusable.

## 10. Template contamination
Putting private examples into templates because they made one internal pilot clearer.

**Better:** keep templates abstract and move private examples to the company instance or repo-local skill.

## 11. Runtime takeover
Asking create-jarvis-skill to manage install, credentials, webhooks, task queues, or service lifecycle.

**Better:** keep runtime mechanics in jarvis-box or the caller runtime; keep this repo focused on methodology, scaffold, pilot, and calibration.
