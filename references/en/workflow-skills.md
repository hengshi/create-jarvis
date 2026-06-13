# Workflow Skills

Workflow skills help agents complete real delivery loops that span sources, repos, teams, or roles.

## When to create a workflow skill

Create or propose a workflow skill when the task:
- touches multiple repos,
- crosses role boundaries,
- requires handoffs or staged artifacts,
- or repeatedly follows the same closed loop.

Typical examples:
- PRD → SPEC → implementation → QA → docs
- bug intake → triage → fix → regression → release note
- incident → diagnosis → patch → postmortem → hardening

## What a workflow skill should define

A workflow skill should make these things explicit:
- trigger or start condition
- input evidence required
- claim normalization: observation, expectation, requested change, and scope
- START precheck
- preconditions
- main stages
- required artifacts
- which sources and repos to use at each stage
- escalation conditions
- evidence needed to advance
- route-confidence checks before high-confidence routing
- END writeback expectations
- known stop conditions or escalation paths

## Keep it high-leverage

A workflow skill should orchestrate. It should not become a copy of repo-local instructions.

Reference repo skills for repo-specific execution.
Reference source skills for source-specific retrieval.
Keep the workflow skill focused on the loop itself.

## Claim normalization and route confidence

For ambiguous inputs, normalize before routing:
- observation: what was actually seen;
- expectation: what behavior or outcome was expected;
- requested change: what the requester wants changed, if any;
- scope: source, repo, workflow, user group, version, or environment.

When claiming that two surfaces are equivalent or that a route is correct, name the evidence class:
- identity: are these the same object, project, customer, or artifact?
- scope: does the claim apply to this source/repo/workflow boundary?
- freshness: is the evidence current enough?
- contract: which API, prompt, workflow, or human rule defines the expected behavior?

If later evidence invalidates the earlier route, record the invalidation as calibration evidence. Do not treat that as proof that the earlier route was unreasonable at the time.

## Resumability, dedupe, and event hygiene

Event-driven workflows should define:
- a stable fingerprint or dedupe key for repeated triggers;
- one in-flight unit of work when duplicate processing is harmful;
- a resume point or terminal artifact so reruns do not restart blindly;
- noise filters for bot/system events and low-signal follow-ups;
- retryable vs terminal failure classes when automation is involved.

This is method guidance, not a requirement to copy any runtime's queue implementation.

## Useful output pattern

A workflow skill is strong when another owner or agent can immediately see:
- what the loop is,
- why it exists,
- what order things happen in,
- where handoffs occur,
- and what counts as success.

## Workflow-first pilot rule

The pilot unit is the workflow. Source and repo inventories exist to support that workflow, not to become a general enterprise map before value is proven.

## Calibration hook

After a workflow run, record whether failures came from routing, truth, boundary, writeback, duplication, bloat, promotion, verification, or `no_skill_gap`. Use that result to update the workflow skill only when the failure is repeatable and the skill is the right home.
