# Part 1: Company Jarvis repository initialization

You are the single writer for the Company Jarvis target during initialization. Follow `work/company-repo-initialization.md`; do not perform Part 2 semantic construction in this task.

## Read first

Read:

1. the pinned create-jarvis method checkout;
2. `BUILD-CONTEXT.md`;
3. `work/company-repo-initialization.md`;
4. `templates/company-jarvis/README.md`;
5. the instantiation and verification scripts referenced there.

Use only the Company identity and publication facts in `BUILD-CONTEXT.md`. Unresolved customer facts stay unresolved.

## Initialize locally

Instantiate the Company Jarvis template into the exact target workspace recorded by the card. Resolve the company name/slug and publication fields required to create the repo. Product identity may remain explicit `UNRESOLVED` for Part 2; do not invent modules, products, repo roles, runtime paths, tool availability or customer policies.

The initialized repository must retain all construction surfaces, including:

- Company entry and routing references;
- modules, sources and cross-cutting structure;
- starter workflow templates;
- canonical repo fleet;
- `references/runtime-governance.md` and its quick reference;
- company `tools/` surface.

`runtime-governance.md` is a required constitutional scaffold. Its unresolved questions are Part 2 work; it is not evidence that a runtime foundation already exists.

## Validate the scaffold

Run the deterministic Company output verifier. Also inspect for unresolved rendering tokens, accidental HENGSHI customer facts, credentials, source dumps and links to Host-only construction paths.

Record the local commit and verification evidence in the work card before publication.

## Publish

Honor the publication contract exactly:

- `new-initial-push` or `empty-initial-push`: create/use the approved customer remote and establish the approved default branch;
- `existing-branch-review`: preserve existing history, use a dedicated branch and deliver a PR/MR;
- `blocked`: stop with the precise missing customer authorization or provider capability.

Never force-push or replace existing history. Verify the remote commit and PR/MR head after delivery. A local directory or dirty worktree is not completion.

## Finish

Update the card with status, last verified checkpoint, local/remote commit, branch, PR/MR, evidence, blocker and `Next`. If you are the Coordinator, update `CONSTRUCTION-JOURNAL.md`; otherwise report the verified card pointer so the Coordinator can update it.

Part 1 completes only when the scaffold is both locally valid and consumable under the customer Git policy. On completion, Part 2 and each Part 3 repository card may become `ready`.
