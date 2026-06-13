# Runtime Bootstrap Contract

Use this when jarvis-box or another runtime invokes create-jarvis-skill through an agent.

## Boundary

create-jarvis-skill is not the runtime operating system.

It must not generate or take ownership of runtime install scripts, system services, credentials, webhooks, task queues, PATH setup, scheduler setup, workspace clone logic, or process lifecycle. Those belong to jarvis-box or the caller runtime.

create-jarvis-skill owns:
- enterprise JARVIS methodology;
- scaffold generation;
- pilot workflow shaping;
- source/repo/workflow skill boundaries;
- confirmation gates;
- writeback and calibration contracts.

## Expected Inputs

The runtime may pass these as environment variables, JSON context, CLI flags, or a prompt. Normalize them before writing artifacts.

| Field | Meaning | Required |
|---|---|---|
| `JARVIS_TARGET_HOME` or `JARVIS_HOME` | output instance root | yes |
| `JARVIS_ENTRY_SKILL` | entry skill path, default `SKILL.md` | no |
| `JARVIS_COMPANY_NAME` | company/product/org name | yes |
| `JARVIS_FIRST_LOOP` | first workflow to prove | yes |
| `GITLAB_HOST`, `GITLAB_PROJECTS` | initial GitLab scope | when GitLab is in scope |
| `JARVIS_SOURCE_OF_TRUTH` | known docs/issues/runbooks/source systems | yes if known |
| `JARVIS_OWNERS` | owners or escalation path | yes |
| `JARVIS_WRITEBACK_STRATEGY` | local-only, repo writeback, docs writeback, approval-required, etc. | yes |
| `JARVIS_BOX_HOME` | neutral runtime root when caller is jarvis-box | no |
| `CREATE_JARVIS_SKILL_REPO_URL` | method repo URL, default `https://github.com/hengshi/create-jarvis-skill.git` | no |
| `CREATE_JARVIS_SKILL_REPO_REF` | requested method repo ref | no |
| method resolved commit | checked out commit used by the runtime agent | strongly recommended |
| `JARVIS_NONINTERACTIVE` | `1` disables prompts and requires machine-readable needs-input results | no |
| `JARVIS_BOOTSTRAP_PROMPT_FILE` | optional audit copy of the runtime prompt | no |

Do not assume `.hengshi`, Hengshi owners, GitLab hosts, or internal repo names for external customers.

## Path Semantics

- `JARVIS_TARGET_HOME` is the directory this bootstrap invocation writes.
- `JARVIS_HOME` is the canonical instance root that generated artifacts should reference.
- If both are set, resolve them to real paths. If they differ, stop with `path-conflict`.
- After first successful bootstrap, they should normally be the same path.
- `JARVIS_BOX_HOME` is only the runtime host root. Never use it as the customer instance root.
- If no target path is available, write a machine-readable failure to the runtime-provided result path if one exists; otherwise report `missing-target-home` and do not create arbitrary directories.

## Secrets Boundary

Never copy secret values into generated JARVIS artifacts. Record only:
- secret name or purpose;
- whether the runtime reports it as configured;
- secret path or provider name if safe;
- unresolved access blocker if not configured.

## Minimum Outputs

The target home should contain:
- `SKILL.md` or the configured entry skill;
- `README.md`;
- `MAINTENANCE.md`;
- build brief;
- source, repo, and workflow inventories for the pilot;
- ownership map;
- rollout plan;
- confirmation checklist;
- `bootstrap-state.json`;
- `bootstrap-result.json`.

Use `templates/en/bootstrap-state.json` and `templates/en/bootstrap-result.json` as the default schema examples when the caller runtime does not supply a stricter schema.

## `bootstrap-state.json`

State is the resume anchor. It should include:
- `schema_version`;
- `phase`;
- `status`;
- `paths.jarvis_home`;
- `paths.jarvis_target_home`;
- `paths.jarvis_box_home`;
- `paths.entry_skill`;
- `inputs` with only non-secret normalized inputs;
- `confirmed_answers`;
- `unresolved_questions`;
- `generated_files`;
- `scaffold_owned_files`;
- `preserved_user_files`;
- `method_repo.url`;
- `method_repo.requested_ref`;
- `method_repo.resolved_commit`;
- `writeback_policy`;
- `noninteractive`;
- `secrets_boundary.declared_secret_names`;
- `secrets_boundary.status`;
- `secrets_boundary.secret_paths`;
- `updated_at`;
- conflicts between new runtime input and prior confirmed answers.

On resume, preserve confirmed answers and user-authored files. Refresh generated files only when they are clearly scaffold-owned or explicitly approved.

If state exists but cannot be parsed, do not guess. Write `bootstrap-result.json` with `status: "failed"` and `result_code: "resume-state-corrupt"` when possible.

## `bootstrap-result.json`

`bootstrap-result.json` is the runtime terminal verdict. It should include:

```json
{
  "schema_version": 1,
  "status": "completed",
  "result_code": "ok",
  "summary": "<short runtime-readable summary>",
  "paths": {
    "jarvis_home": "<path>",
    "jarvis_target_home": "<path>",
    "entry_skill": "<path>"
  },
  "method_repo": {
    "url": "https://github.com/hengshi/create-jarvis-skill.git",
    "requested_ref": "<ref-or-null>",
    "resolved_commit": "<sha-or-ref>"
  },
  "created_files": [],
  "updated_files": [],
  "preserved_files": [],
  "unresolved_questions": [],
  "blockers": [],
  "writeback_policy": "<policy>",
  "next_action": "<shadow-pilot-or-human-confirmation>",
  "generated_at": "<iso8601>"
}
```

Allowed `status` values:
- `completed`
- `needs-input`
- `blocked`
- `failed`

Even when bootstrap is blocked, write this file when a safe target or runtime-provided result path exists. The runtime should not have to parse prose to decide the next action.

The committed eval harness validates this shape through dotted required fields such as `paths.jarvis_home` and `method_repo.url`.

## Error Contract

Errors must be machine-readable. Use these `result_code` values unless a caller defines a stricter list:

| Code | Retryable | Meaning |
|---|---|---|
| `ok` | no | bootstrap completed |
| `missing-target-home` | no | no writable target was supplied |
| `target-not-writable` | no | target path cannot be written |
| `path-conflict` | no | `JARVIS_HOME` and `JARVIS_TARGET_HOME` resolve differently |
| `missing-company-name` | no | company/product name is absent |
| `missing-first-loop` | no | first workflow is absent |
| `missing-owners` | no | no owner or escalation path is known |
| `missing-source-scope` | no | required source or GitLab scope is absent |
| `noninteractive-missing-input` | no | prompts are disabled and required input is missing |
| `secret-boundary-violation` | no | a secret value would be written or echoed |
| `invalid-entry-skill` | no | generated entry skill is missing or invalid |
| `resume-state-corrupt` | no | existing state cannot be parsed safely |

For each failure include:
- `result_code`;
- `retryable`;
- `missing_inputs`;
- `conflicting_inputs`;
- `blockers`;
- `next_action`.

## Writeback Policy

Default writeback policy is `local-only`.

Use external writeback only when:
- the runtime or human explicitly supplies `JARVIS_WRITEBACK_STRATEGY`;
- required approvals are available;
- the action is not a shadow-pilot write;
- and the target source/repo is the correct home for the truth.

The runtime starts and records the agent task; this methodology should not silently post to external systems.

## Noninteractive Behavior

In noninteractive mode:
- do not guess required truth-bearing inputs;
- do not ask follow-up prompts;
- write unresolved fields to state/result;
- generate only safe scaffold artifacts;
- return `status: "needs-input"` with `result_code: "noninteractive-missing-input"` when required inputs are missing.

Interactive mode may ask for missing fields, but confirmed answers still need to be recorded in state.
