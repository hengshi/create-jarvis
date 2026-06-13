# Internal to Generic Promotion

Use this when deciding whether a lesson from one company JARVIS instance should update create-jarvis-skill.

## Promotion Ladder

1. Task-local note: useful only for the current run.
2. Repo-local skill/reference: execution truth for one repo or project.
3. Central JARVIS instance: routing, workflow, ownership, or durable company pattern.
4. Generic create-jarvis-skill methodology: company-neutral rule that helps future JARVIS builders.

Do not skip levels just because a lesson feels important.

## What Belongs Where

Repo-local:
- commands;
- validation;
- local architecture;
- repo-specific failure patterns;
- safe mutation and writeback paths.

Central JARVIS:
- cross-repo routing;
- workflow orchestration;
- source map;
- ownership;
- durable failure patterns;
- writeback and maintenance rules for that company.

Generic create-jarvis-skill:
- company-neutral methodology;
- scaffold contracts;
- pilot design;
- layer boundaries;
- calibration and promotion rules;
- reusable anti-patterns without private examples.

## Upstream Gate

Promote to create-jarvis-skill only when:
- the lesson is not company-specific;
- private names, paths, issue IDs, customers, owners, and secrets are removed;
- it applies to multiple instances or companies;
- it changes method rather than merely adding facts;
- it has evidence from real usage or replay;
- it does not duplicate an existing rule.

## Redaction Rules

Generic methodology may describe patterns but must not carry:
- company names except in the repository owner URL itself;
- private Git hosts;
- internal repo names;
- issue/MR IDs;
- customer names;
- screenshots or raw transcripts;
- secret names that reveal sensitive infrastructure.

Use placeholders or abstract labels instead.
