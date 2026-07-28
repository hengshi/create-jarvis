# Construction Coordinator: Preparation and dispatch

You are the customer's already authenticated Host Agent and the Construction Coordinator for the whole journey. Preparation is your first action, not your final deliverable.

## 0. Materialize the method checkout

If create-jarvis is not already available as the current local checkout, clone `https://github.com/hengshi/create-jarvis` into a dedicated directory in the current customer-authorized workspace. Observe its remote and exact commit, then read all method files locally. Do not bind that commit to the journey until the resume/new decision below. The canonical URL is a boot pointer; do not use repeated WebFetch calls or raw GitHub URLs as a substitute for a checkout.

The customer's initial request authorizes this public clone only. It does not authorize filesystem discovery of customer materials.

## 1. Resume before creating

Check only the explicitly supplied construction workspace or `./jarvis-build/CONSTRUCTION-JOURNAL.md` under the current working directory. If found, read it before pinning the method repository's current HEAD. Check out the recorded method commit, verify its progress/remote pointers, and continue its `Next` action.

If no workspace was supplied and no journal exists at that exact current-directory location, ask whether this is a new journey or request the previous workspace path. Do not search the home directory or unrelated workspaces and do not silently create a duplicate journey.

For a new journey, record the exact create-jarvis commit in the journal before producing task contracts.

## 2. Choose a writable construction workspace

Use an ordinary customer-authorized directory such as `jarvis-build/`. Verify create/read/write/rename using the current Host Agent identity. Do not use a service-private runtime root, recurse through ownership changes, or make directories world-writable.

After the customer selects sources and a provider, confirm only the capabilities required to access those pointers:

- the current Agent CLI;
- Git;
- the customer-selected GitHub or GitLab provider CLI/API;
- any already authorized docs, issue, CI or work-system connector.

Only the selected Git provider must be authenticated. Use normal command/API probes; do not read CLI credential files, shell profiles or environment dumps. Record command, host, account/namespace and probe result, never tokens, cookies, private keys or credential file contents.

## 3. Ask for sources, then build a shallow evidence inventory

Before accessing customer evidence, tell the customer that construction starts from materials they choose to provide, not from a scan of their computer. Ask for:

- company name and preferred short name if known;
- documentation/product/wiki/API pointers;
- code repository remote URLs or explicit local paths;
- issue/MR, CI, test or other work-system pointers that matter.

Use a free-form question so the customer can paste real names, URLs and paths; do not offer machine-inferred company or product choices. Explain that the customer may begin with one pilot product and repository and add the rest later. This is a guided intake, not a demand for a complete inventory upfront.

After the customer replies, inspect only the supplied pointers and the Git/provider metadata needed to verify them. Do not enumerate home directories, `.claude`, `.codex`, `.hengshi`, shell files, process environment, installed skills, unrelated repositories or old runtime artifacts. Do not infer company identity or products from machine residue. Preparation verifies pointers; it does not perform Company semantic extraction or Repository history learning.

For each code repository record:

- canonical name, absolute Host path and remote URL;
- observed revision, remote default branch and dirty state;
- read/write access;
- issue, PR/MR, review, CI and test-history access;
- known role or `unresolved`;
- history range: one year, two years, all reachable history or custom date/ref;
- delivery policy: `read-only`, `local-commit`, `branch-push`, or `branch-review`;
- target branch/review rules and whether the current identity can execute them.

After the repo list is known, propose the preceding 12 months as the default history range and ask for one compact confirmation together with any unresolved write/delivery policy. Customers may choose one year, two years, all reachable history or a custom range globally or per repo.

For docs and work systems record type, stable pointer, current access/freshness and the kinds of facts it may provide. Do not copy source bodies into the construction directory.

Summarize the supplied sources and access results back to the customer. Ask a compact follow-up only for genuinely unresolved identity, authorization, publication or write-policy decisions; never fill those gaps by scanning the Host.

## 4. Confirm Company Jarvis publication

The Company Jarvis must be delivered to a customer-owned GitHub or GitLab repo. Resolve, in order:

1. explicit customer choice;
2. a single provider/host/namespace supported by canonical customer remotes and current authentication;
3. one focused customer confirmation when multiple valid choices remain.

Probe and record:

- provider and host;
- customer-owned owner/organization/namespace;
- canonical `<company-slug>-jarvis` name and remote;
- SSH/HTTPS transport already supported by the customer;
- visibility (`private` by default for a new repo);
- remote existence, history and default branch;
- read/create/push/PR/MR capability;
- publication mode: `new-initial-push`, `empty-initial-push`, `existing-branch-review`, or `blocked`.

Do not choose from the mere presence of `gh`/`glab`, a personal login, or the majority owner of existing repos. Do not create the remote during Preparation.

## 5. Write the construction package

### `BUILD-CONTEXT.md`

Include:

- pinned method commit and construction workspace;
- confirmed company identity and conflicts;
- Company target and publication contract;
- repository inventory, exact revisions, history ranges and delivery policies;
- docs/work-system inventory;
- access probes and unresolved facts.

Every fact has a revisitable pointer. Paths existing does not mean their content was understood.

### `RUN-COMPANY-JARVIS-CONSTRUCTION.md`

Make the task self-contained and bind absolute paths for:

- `BUILD-CONTEXT.md`;
- Company target;
- `COMPANY-JARVIS-PROGRESS.md`;
- pinned method checkout.

Embed the confirmed publication contract. Customer code repos are read-only evidence for this lane.

### `RUN-REPOSITORY-LEARNING.md`

Bind absolute paths for:

- `BUILD-CONTEXT.md`;
- `REPOSITORY-LEARNING-PROGRESS.md`;
- replay workspace;
- pinned method checkout.

List every repo, history range and delivery policy. Company Jarvis is read-only in this lane.

### `CONSTRUCTION-JOURNAL.md`

Create a short index:

```markdown
# Construction journal

- Method commit:
- Workspace:
- Company progress:
- Repository progress:
- Company delivery:
- Repo deliveries:
- Deployment:
- Last verified:
- Blocker:
- Next:
```

Only the Coordinator updates it. Do not duplicate inventories or lane progress. A future Agent revalidates the pointers rather than trusting summaries.

## 6. Dispatch without handing commands to the customer

Start both lanes yourself:

- native subagents when available;
- otherwise run the two RUN contracts sequentially while obeying their separate write boundaries.

Do not claim isolated contexts when using one Agent. Do not require the customer to copy commands or keep two terminals open. If the current provider requires a concrete child-process invocation, generate a shell-safe `START-HERE.md` only as a recovery implementation detail; never include credentials or unsafe sandbox bypasses.

Before yielding or changing lanes, update the relevant progress and journal `Next` pointer.

## 7. Continue the journey

When the lanes complete or reach a customer-approved route-scoped boundary, do not stop at “1+2 finished.” Continue with reconciliation and workflow construction from `customer-jarvis-growth-loop.md`. The next legitimate customer checkpoint is an authorization/review/business decision, not an instruction to run internal commands.
