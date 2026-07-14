#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  E2E_REPO_SPECS="frontend=/repo-cache/frontend.git,backend=/repo-cache/backend.git" \
  JARVIS_BOX_SRC_DIR=/path/to/jarvis-box \
  JARVIS_BOX_DIST_DIR=/path/to/dist \
  scripts/run_customer_bootstrap_e2e.sh

Required:
  E2E_REPO_SPECS       comma-separated repo specs: name=container-visible-git-source
  JARVIS_BOX_SRC_DIR   jarvis-box source checkout containing install.sh

Optional:
  JARVIS_BOX_DIST_DIR  directory with jarvis-box linux artifacts and SHA256SUMS
                       default: /tmp/jarvis-box-install-e2e/dist
  E2E_REPO_CACHE_DIR   host repo cache mounted read-only at /repo-cache
  E2E_RUN_DIR          host directory for outputs
  E2E_CONTAINER_NAME   default: create-jarvis-skill-customer-e2e
  E2E_CONTAINER_IMAGE  default: jarvis-box-install-e2e:ubuntu-24.04-systemd
  E2E_KEEP_CONTAINER   default: 1
  JARVIS_VERSION       inferred from dist when omitted
  JARVIS_COMPANY_SLUG  default: acme-e2e
  JARVIS_COMPANY_NAME  default: Acme Analytics
  JARVIS_FIRST_LOOP    default: issue intake -> triage -> repo fix -> regression
  JARVIS_OWNERS        default: platform-owner
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[customer-bootstrap-e2e] %s\n' "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
jarvis_box_src="${JARVIS_BOX_SRC_DIR:-}"
dist_dir="${JARVIS_BOX_DIST_DIR:-/tmp/jarvis-box-install-e2e/dist}"
repo_cache="${E2E_REPO_CACHE_DIR:-}"
repo_specs="${E2E_REPO_SPECS:-}"
container_name="${E2E_CONTAINER_NAME:-create-jarvis-skill-customer-e2e}"
container_image="${E2E_CONTAINER_IMAGE:-jarvis-box-install-e2e:ubuntu-24.04-systemd}"
company_slug="${JARVIS_COMPANY_SLUG:-acme-e2e}"
company_name="${JARVIS_COMPANY_NAME:-Acme Analytics}"
first_loop="${JARVIS_FIRST_LOOP:-issue intake -> triage -> repo fix -> regression}"
owners="${JARVIS_OWNERS:-platform-owner}"
writeback_strategy="${JARVIS_WRITEBACK_STRATEGY:-local-only}"
keep_container="${E2E_KEEP_CONTAINER:-1}"

[ -n "$repo_specs" ] || die "E2E_REPO_SPECS is required"
[ -n "$jarvis_box_src" ] || die "JARVIS_BOX_SRC_DIR is required"
[ -d "$jarvis_box_src" ] || die "JARVIS_BOX_SRC_DIR not found: $jarvis_box_src"
[ -f "$jarvis_box_src/install.sh" ] || die "install.sh not found in JARVIS_BOX_SRC_DIR: $jarvis_box_src"
[ -d "$dist_dir" ] || die "JARVIS_BOX_DIST_DIR not found: $dist_dir"
[ -f "$dist_dir/SHA256SUMS" ] || die "SHA256SUMS not found in JARVIS_BOX_DIST_DIR: $dist_dir"

require_cmd docker

if [ -z "${E2E_RUN_DIR:-}" ]; then
  run_id="$(date -u +%Y%m%dT%H%M%SZ)"
  run_dir="$repo_root/.eval-runs/customer-bootstrap-e2e/$run_id"
else
  run_dir="$E2E_RUN_DIR"
fi
mkdir -p "$run_dir"

cleanup() {
  if [ "$keep_container" != "1" ]; then
    docker rm -f "$container_name" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

log "run dir: $run_dir"
log "starting container: $container_name"
docker rm -f "$container_name" >/dev/null 2>&1 || true

docker_args=(
  run -d
  --name "$container_name"
  --privileged
  --cgroupns=host
  --tmpfs /run
  --tmpfs /run/lock
  -v /sys/fs/cgroup:/sys/fs/cgroup:rw
  -v "$dist_dir":/dist:ro
  -v "$jarvis_box_src":/jarvis-box-src:ro
  -v "$repo_root":/create-jarvis-skill:ro
  -v "$run_dir":/e2e
)
if [ -n "$repo_cache" ]; then
  [ -d "$repo_cache" ] || die "E2E_REPO_CACHE_DIR not found: $repo_cache"
  docker_args+=(-v "$repo_cache":/repo-cache:ro)
fi
docker_args+=("$container_image" /sbin/init)

docker "${docker_args[@]}" >/dev/null
sleep 2

container_arch="$(docker exec "$container_name" uname -m)"
case "$container_arch" in
  x86_64|amd64) release_arch="amd64" ;;
  aarch64|arm64) release_arch="arm64" ;;
  *) die "unsupported container arch: $container_arch" ;;
esac

version="${JARVIS_VERSION:-}"
if [ -z "$version" ]; then
  first_artifact="$(find "$dist_dir" -maxdepth 1 -name "jarvis-box_*_linux_${release_arch}.tar.gz" | sort | head -1)"
  [ -n "$first_artifact" ] || die "no linux_${release_arch} artifact found in $dist_dir"
  base="$(basename "$first_artifact")"
  version="${base#jarvis-box_}"
  version="${version%_linux_${release_arch}.tar.gz}"
fi

artifact="/dist/jarvis-box_${version}_linux_${release_arch}.tar.gz"
log "installing jarvis-box version=$version arch=$release_arch"
docker exec "$container_name" bash -lc "
  set -euo pipefail
  export JARVIS_VERSION='$version'
  export JARVIS_COMPANY_SLUG='$company_slug'
  export JARVIS_ARTIFACT_FILE='$artifact'
  export JARVIS_SHA256SUMS_FILE=/dist/SHA256SUMS
  export JARVIS_INSTALL_AGENT_READINESS=defer
  bash /jarvis-box-src/install.sh
"

log "preparing customer repo copies"
docker exec "$container_name" bash -lc "
  set -euo pipefail
  rm -rf /e2e/customer-repos /e2e/output /e2e/work
  mkdir -p /e2e/customer-repos /e2e/output /e2e/work
  IFS=',' read -r -a specs <<< '$repo_specs'
  for spec in \"\${specs[@]}\"; do
    name=\"\${spec%%=*}\"
    source=\"\${spec#*=}\"
    [ -n \"\$name\" ] && [ -n \"\$source\" ] && [ \"\$name\" != \"\$source\" ] || {
      echo \"invalid repo spec: \$spec\" >&2
      exit 2
    }
    case \"\$name\" in
      *[!a-zA-Z0-9._-]*)
        echo \"invalid repo name: \$name\" >&2
        exit 2
        ;;
    esac
    git clone \"\$source\" \"/e2e/customer-repos/\$name\" >/tmp/clone-\"\$name\".log 2>&1
    rm -rf \"/e2e/customer-repos/\$name/skills\" \"/e2e/customer-repos/\$name/.agents/skills\" \"/e2e/customer-repos/\$name/.codex/skills\"
  done
  chmod -R a+rwx /e2e
"

log "installing controlled bootstrap agent"
docker exec "$container_name" bash -lc "cat > /e2e/bootstrap-agent <<'AGENT'
#!/usr/bin/env bash
set -euo pipefail

target=\"\${JARVIS_TARGET_HOME:?JARVIS_TARGET_HOME required}\"
repo_root=\"\${E2E_CUSTOMER_REPOS:-/e2e/customer-repos}\"
method_root=\"\${E2E_METHOD_REPO:-/create-jarvis-skill}\"
prompt_file=\"\${JARVIS_BOOTSTRAP_PROMPT_FILE:-}\"
generated_at=\"\$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
company=\"\${JARVIS_COMPANY_NAME:-Acme Analytics}\"
first_loop=\"\${JARVIS_FIRST_LOOP:-issue intake -> triage -> repo fix -> regression}\"
owner=\"\${JARVIS_OWNERS:-platform-owner}\"
company_slug=\"\${JARVIS_COMPANY_SLUG:-acme-e2e}\"
entry_skill=\"skills/\${company_slug}-jarvis/SKILL.md\"
workflow_skill_slug=\"issue-to-fix\"
module_slug=\"issue-to-regression\"
source_slug=\"customer-repos\"

mkdir -p \
  \"\$target\" \
  \"\$target/modules/\$module_slug\" \
  \"\$target/sources/\$source_slug\" \
  \"\$target/cross-cutting\" \
  \"\$target/references\" \
  \"\$target/tools\" \
  \"\$target/skills/\$company_slug-jarvis\" \
  \"\$target/skills/\$workflow_skill_slug\" \
  \"\$target/evals/history-replay/cases\" \
  \"\$target/_bootstrap/shadow-pilot\"
if [ -n \"\$prompt_file\" ] && [ -f \"\$prompt_file\" ]; then
  cp \"\$prompt_file\" \"\$target/_bootstrap/bootstrap-agent-prompt.md\"
else
  cat > \"\$target/_bootstrap/bootstrap-agent-prompt.md\"
fi

method_commit=\"mounted-worktree\"
if [ -d \"\$method_root/.git\" ]; then
  method_commit=\"\$(git -C \"\$method_root\" rev-parse --short HEAD 2>/dev/null || printf mounted-worktree)\"
fi

cat > \"\$target/README.md\" <<EOF
# \$company Jarvis

Status: controlled e2e sample.

This controlled e2e output proves the machine chain only. It is not bootstrap completion unless acceptance.md passes against customer evidence.

First workflow: \$first_loop

Entry skill: \$entry_skill
EOF

cat > \"\$target/jarvis.toml\" <<EOF
schema_version = 1
company_slug = \"\$company_slug\"
entry_skill = \"\$entry_skill\"
EOF

cat > \"\$target/\$entry_skill\" <<EOF
# \$company Jarvis

Use this as the company entry skill for the pilot workflow: \$first_loop.

Route repository execution to repo-local skills under each generated test repository. Start routing from references/jarvis-first-routing.md.

Do not copy raw source, issues, or repository history into this Jarvis repo. Keep repository execution truth in repo-local skills.
EOF

cat > \"\$target/MAINTENANCE.md\" <<EOF
# Maintenance

- Treat this controlled e2e output as a machine-chain sample until real customer evidence, module topology, and shadow-pilot evidence satisfy the acceptance standard.
- Use history replay before expanding repo-local skills.
- Treat no_skill_gap as a valid result.
- Write repo execution facts back to the owning repo-local skill.
EOF

cat > \"\$target/_bootstrap/jarvis-build-brief.md\" <<EOF
# Jarvis Build Brief

- company identity: \$company
- company slug: \$company_slug
- confirmed product identity: unresolved
- source-detected identities: customer repo specs, needs-owner-confirmation
- identity status: needs-owner-confirmation
- first workflow: \$first_loop
- owner: \$owner
- writeback strategy: \${JARVIS_WRITEBACK_STRATEGY:-local-only}
- method repo: \${CREATE_JARVIS_SKILL_REPO_URL:-unset}
- method commit: \$method_commit
EOF

cat > \"\$target/sources/\$source_slug/README.md\" <<EOF
# Customer Repositories Source

- repos: \${GITLAB_PROJECTS:-customer repo specs}
- source of truth: \${JARVIS_SOURCE_OF_TRUTH:-/e2e/customer-repos}
- detected identity: needs-owner-confirmation
- confirmation status: needs-owner-confirmation

## Repo-local skill handoff

Repo execution truth stays in each customer repo under skills/.
EOF

cat > \"\$target/modules/\$module_slug/overview.md\" <<EOF
# Issue To Regression Module

Status: generated-needs-owner-confirmation.

This module represents the first customer workflow selected for bootstrap:

\$first_loop

Evidence source:
- customer repository copies under \${JARVIS_SOURCE_OF_TRUTH:-/e2e/customer-repos}

Unknowns remain unresolved until owner review and shadow pilot evidence confirm the workflow.
EOF

cat > \"\$target/references/jarvis-first-routing.md\" <<EOF
# Jarvis First Routing

Company identity: \$company
Identity status: needs-owner-confirmation
First workflow: \$first_loop

## Workflow first

| Trigger | Workflow skill | First proof | Repo-local handoff | Verification | END |
|---|---|---|---|---|---|
| customer issue / change request | skills/\$workflow_skill_slug/SKILL.md | owner-confirmed artifact | repo-local skills/SKILL.md | repo precheck + owner review | writeback decision |

## Pilot repo roles

| Repo | Role in workflow | Repo-local skill | First-proof condition | Escalation condition |
|---|---|---|---|---|
EOF

cat > \"\$target/cross-cutting/ownership-map.md\" <<EOF
# Ownership Map

| area | owner | status |
| --- | --- | --- |
| bootstrap | \$owner | confirmed-if-supplied-by-owner |
EOF

cat > \"\$target/cross-cutting/module-interactions.md\" <<EOF
# Module Interactions

Status: generated-needs-owner-confirmation.

The first workflow crosses the company Jarvis entry skill, the workflow skill, and repo-local skills.

| From | To | Contract | Evidence |
|---|---|---|---|
| skills/\$company_slug-jarvis/SKILL.md | references/jarvis-first-routing.md | choose workflow before repo | generated bootstrap state |
| references/jarvis-first-routing.md | skills/\$workflow_skill_slug/SKILL.md | run workflow guardrails | generated bootstrap state |
| skills/\$workflow_skill_slug/SKILL.md | repo-local skills/SKILL.md | keep repo execution truth repo-local | customer repo copies |
EOF

cat > \"\$target/references/agent-engineering-quality-gate.md\" <<EOF
# Agent Engineering Quality Gate

- Do not declare completion from scaffold creation alone.
- Use owner-confirmed evidence for business claims.
- Keep repo-specific commands in repo-local skills.
- Verify durable updates with a shadow pilot or history replay before promotion.
EOF

cat > \"\$target/references/minimal-closure-card.md\" <<EOF
# Minimal Closure Card

- START signal:
- Work performed:
- Verification:
- Owner or evidence confirmation:
- Writeback decision:
- Remaining unresolved questions:
EOF

cat > \"\$target/references/redaction-rules.md\" <<EOF
# Redaction Rules

- Do not copy secrets, tokens, private keys, or credentials.
- Do not copy long raw source, raw issue dumps, or large private documents into company Jarvis.
- Keep evidence pointers and concise summaries.
- Keep repo execution truth in repo-local skills.
EOF

cat > \"\$target/references/history-replay.md\" <<EOF
# History Replay

Build replay cases from real historical repo work:

1. Preserve only the visible START signal for the replay agent.
2. Keep final commits, owner corrections, and real outcomes as hidden oracle.
3. Run existing skills against the START signal.
4. Classify failures.
5. Update the smallest durable skill or reference.
6. Re-run the replay.
EOF

cat > \"\$target/references/writeback-governance.md\" <<EOF
# Writeback Governance

Policy: \${JARVIS_WRITEBACK_STRATEGY:-local-only}

Write durable learning to the narrowest correct home:

| Learning type | Home |
|---|---|
| repo command / architecture / test entrypoint | repo-local skills/ |
| workflow guardrail | skills/\$workflow_skill_slug/SKILL.md |
| routing or company-wide boundary | references/ |
| bootstrap process evidence | _bootstrap/ |
EOF

cat > \"\$target/references/runtime-governance.md\" <<EOF
# Runtime Governance

Status: generated-needs-owner-confirmation.

Managed jobs, pullall/runtime-sync behavior, owner rotation, and scheduler choices must be confirmed during day-2 operation. Do not install cron jobs from this bootstrap sample.
EOF

cat > \"\$target/skills/\$workflow_skill_slug/SKILL.md\" <<EOF
# Issue To Fix Workflow

Use this workflow for: \$first_loop.

## START

Read references/jarvis-first-routing.md and identify the owner-confirmed artifact.

## WORK

Route repository execution to the matching repo-local skill package. Do not invent build or test commands that the repo owner has not confirmed.

## VERIFY

Run or inspect the repo-local precheck and record unresolved commands.

## END

Decide whether the durable learning belongs in repo-local skills, this workflow skill, company Jarvis references, upstream create-jarvis-skill, or no_skill_gap.
EOF

cat > \"\$target/_bootstrap/rollout-confirmation-checklist.md\" <<EOF
# Rollout Confirmation Checklist

- [ ] customer owner confirms first workflow
- [ ] customer owner confirms repo scope
- [ ] customer owner confirms company/product/source identity reconciliation
- [ ] customer owner confirms repo-local skill commands
- [ ] shadow pilot artifact selected
EOF

cat > \"\$target/tools/README.md\" <<EOF
# Tools

Status: backlog.

Customer-owned runtime-sync / pullall should be generated in Phase 14 from customer repo fleet and scheduler policy, not during jarvis-box install.
EOF

detect_stack() {
  local repo_path=\"\$1\"
  local stack=\"\"
  [ -f \"\$repo_path/package.json\" ] && stack=\"\${stack}node \"
  [ -f \"\$repo_path/pom.xml\" ] && stack=\"\${stack}maven \"
  [ -f \"\$repo_path/gradlew\" ] && stack=\"\${stack}gradle \"
  [ -f \"\$repo_path/Makefile\" ] && stack=\"\${stack}make \"
  [ -n \"\$stack\" ] || stack=\"unknown \"
  printf '%s' \"\$stack\"
}

created_files='\"README.md\", \"MAINTENANCE.md\", \"jarvis.toml\", \"references/jarvis-first-routing.md\", \"references/agent-engineering-quality-gate.md\", \"references/minimal-closure-card.md\", \"references/redaction-rules.md\", \"references/history-replay.md\", \"references/writeback-governance.md\", \"references/runtime-governance.md\", \"cross-cutting/module-interactions.md\", \"sources/customer-repos/README.md\", \"modules/issue-to-regression/overview.md\", \"tools/README.md\"'
for repo_path in \"\$repo_root\"/*; do
  [ -d \"\$repo_path/.git\" ] || continue
  repo=\"\$(basename \"\$repo_path\")\"
  [ ! -e \"\$repo_path/skills/SKILL.md\" ] || {
    echo \"repo skill was not deleted before bootstrap: \$repo\" >&2
    exit 2
  }
  stack=\"\$(detect_stack \"\$repo_path\")\"
  head_sha=\"\$(git -C \"\$repo_path\" rev-parse --short HEAD)\"
  mkdir -p \
    \"\$repo_path/skills/code-review/scripts\" \
    \"\$repo_path/skills/references\" \
    \"\$repo_path/skills/self-skills-improve\"
  cat > \"\$repo_path/skills/SKILL.md\" <<EOF
# \$repo Repo-Local Skill

Generated by create-jarvis-skill customer bootstrap e2e.

## Scope

This skill owns execution guidance for the \$repo repository only.

## Evidence

- repo path: \$repo_path
- head: \$head_sha
- detected stack: \$stack

## First Workflow

\$first_loop

## Initial Commands To Confirm

- Inspect package/build files before running commands.
- Confirm test and lint commands with the repo owner before using this in production.

## Skill Package

- skills/code-review/SKILL.md: repository-local review gate.
- skills/code-review/scripts/precheck.sh: executable precheck scaffold.
- skills/references/source-of-truth.md: owner-confirmed source boundaries.
- skills/references/architecture-map.md: architecture entrypoints.
- skills/references/test-entrypoints.md: verification entrypoints.
- skills/references/runtime-and-testability.md: runtime and observability notes.
- skills/references/history-replay-loop.md: replay discipline for skill growth.
- skills/eval-loop.md: repo-local replay update loop.
- skills/self-skills-improve/SKILL.md: repo-local skill improvement route.

## Boundaries

- Keep repo execution truth here.
- Do not move repository-specific commands into the company Jarvis entry skill.
- Use history replay before treating this scaffold as mature.
EOF
  cat > \"\$repo_path/skills/code-review/SKILL.md\" <<EOF
# \$repo Code Review

Review repository-local changes in \$repo.

## Review Order

1. Confirm changed files belong to the stated task.
2. Read skills/references/source-of-truth.md and skills/references/architecture-map.md.
3. Run or inspect skills/code-review/scripts/precheck.sh.
4. Identify missing tests, unsafe mutations, and unconfirmed commands.
5. Decide whether any durable learning belongs in repo-local references.

## Output

- Findings first, ordered by severity.
- File and line references when available.
- Test gaps and residual risk.
- Writeback decision: none, repo-local, workflow, company-jarvis, or no_skill_gap.
EOF
  cat > \"\$repo_path/skills/code-review/scripts/precheck.sh\" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

repo_root=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")/../../..\" && pwd)\"
cd \"\$repo_root\"

echo \"repo-local precheck scaffold\"
echo \"repo: \$(basename \"\$repo_root\")\"

if [ -f package.json ]; then
  echo \"detected package.json; confirm npm/yarn/pnpm commands with repo owner before production use\"
fi

if [ -f pom.xml ]; then
  echo \"detected pom.xml; confirm Maven commands with repo owner before production use\"
fi

if [ -f gradlew ]; then
  echo \"detected gradlew; confirm Gradle commands with repo owner before production use\"
fi

if [ -f Makefile ]; then
  echo \"detected Makefile; inspect targets before production use\"
fi

echo \"precheck scaffold completed\"
EOF
  chmod +x \"\$repo_path/skills/code-review/scripts/precheck.sh\"
  cat > \"\$repo_path/skills/references/source-of-truth.md\" <<EOF
# Source Of Truth

Status: generated-needs-owner-confirmation

Record authoritative repo-local locations for:

- product behavior implemented in this repo;
- API, UI, configuration, or data contracts;
- tests that prove the first workflow;
- files that need owner confirmation before edits.

Detected evidence:

- repo path: \$repo_path
- head: \$head_sha
- detected stack: \$stack

Do not copy secrets, raw issue text, long source snippets, or company-wide policy here.
EOF
  cat > \"\$repo_path/skills/references/architecture-map.md\" <<EOF
# Architecture Map

Status: generated-needs-owner-confirmation

Use this file to point agents to high-value architecture entrypoints.

- main modules:
- important paths:
- extension points:
- generated code:
- risky areas:
- owner-confirmed notes:

Leave unknowns blank or mark them unresolved.
EOF
  cat > \"\$repo_path/skills/references/test-entrypoints.md\" <<EOF
# Test Entrypoints

Status: generated-needs-owner-confirmation

Record confirmed verification commands only.

- smoke checks:
- unit tests:
- integration tests:
- lint/type checks:
- CI jobs:
- fixtures and golden files:
- known gaps:

Detected build files are evidence to inspect, not permission to invent commands.
EOF
  cat > \"\$repo_path/skills/references/runtime-and-testability.md\" <<EOF
# Runtime And Testability

Status: generated-needs-owner-confirmation

Record how agents can safely run, observe, and verify this repo.

- local runtime prerequisites;
- service startup or app entrypoints;
- logs and diagnostics;
- test data requirements;
- external dependencies;
- safe sandbox or dry-run options;
- forbidden operations.

Do not record secret values.
EOF
  cat > \"\$repo_path/skills/references/history-replay-loop.md\" <<EOF
# History Replay Loop

Status: generated-needs-owner-confirmation

Use this reference to turn historical repo work into replay cases.

1. Capture the visible START signal only.
2. Keep the final commit, owner corrections, and real outcome as hidden oracle.
3. Run current repo-local and company skills against the START state.
4. Classify the failure.
5. Decide no_skill_gap, repo-local update, workflow update, company Jarvis update, or upstream method change.
6. Verify the update against the replay.

Do not expose hidden outcome facts to the replay agent.
EOF
  cat > \"\$repo_path/skills/eval-loop.md\" <<EOF
# Eval Loop

Use this loop for repo-local skill changes:

visible START signal -> current skill run -> hidden oracle comparison -> failure analysis -> no_skill_gap or minimal repo-local update -> replay verification

A change is not complete until the replay that justified it is improved or the decision is explicitly no_skill_gap.
EOF
  cat > \"\$repo_path/skills/self-skills-improve/SKILL.md\" <<EOF
# \$repo Skill Improvement

Improve this repository's local skills from owner-confirmed failures, shadow pilot evidence, and history replay cases.

## Decision Order

1. Check no_skill_gap.
2. Identify the correct writeback home.
3. Keep repo-local truth in this repo.
4. Update the smallest reference or sub skill that fixes the replay.
5. Re-run the replay or precheck.

## Forbidden

- Do not grow skills from one-off confusion.
- Do not copy raw private artifacts into references.
- Do not promote repo-local execution truth into company Jarvis.
EOF
  printf '| %s | implementation repo | %s/skills/SKILL.md | owner confirms commands | workflow needs code change |\n' \"\$repo\" \"\$repo_path\" >> \"\$target/references/jarvis-first-routing.md\"
  {
    printf '\n### %s\n\n' \"\$repo\"
    printf -- '- repo-local skill: `%s/skills/SKILL.md`\n' \"\$repo_path\"
    printf -- '- detected stack: `%s`\n' \"\$stack\"
    printf -- '- head: `%s`\n' \"\$head_sha\"
    printf -- '- status: generated-needs-owner-confirmation\n'
  } >> \"\$target/sources/\$source_slug/README.md\"
  {
    printf '\n## Repo evidence: %s\n\n' \"\$repo\"
    printf -- '- repo-local skill: `%s/skills/SKILL.md`\n' \"\$repo_path\"
    printf -- '- detected stack: `%s`\n' \"\$stack\"
    printf -- '- head: `%s`\n' \"\$head_sha\"
  } >> \"\$target/modules/\$module_slug/overview.md\"
  created_files=\"\$created_files, \\\"\$repo_path/skills/SKILL.md\\\", \\\"\$repo_path/skills/code-review/SKILL.md\\\", \\\"\$repo_path/skills/code-review/scripts/precheck.sh\\\", \\\"\$repo_path/skills/references/source-of-truth.md\\\", \\\"\$repo_path/skills/references/architecture-map.md\\\", \\\"\$repo_path/skills/references/test-entrypoints.md\\\", \\\"\$repo_path/skills/references/runtime-and-testability.md\\\", \\\"\$repo_path/skills/references/history-replay-loop.md\\\", \\\"\$repo_path/skills/eval-loop.md\\\", \\\"\$repo_path/skills/self-skills-improve/SKILL.md\\\"\"
done

cat > \"\$target/bootstrap-state.json\" <<EOF
{
  \"schema_version\": 1,
  \"phase\": \"phase-10-onboarding-report\",
  \"status\": \"needs-input\",
  \"paths\": {
    \"jarvis_home\": \"\$target\",
    \"jarvis_target_home\": \"\$target\",
    \"entry_skill\": \"\$entry_skill\"
  },
  \"inputs\": {
    \"company_name\": \"\$company\",
    \"company_slug\": \"\$company_slug\",
    \"product_identity\": \"unresolved\",
    \"first_workflow\": \"\$first_loop\",
    \"source_scope\": \"\${JARVIS_SOURCE_OF_TRUTH:-/e2e/customer-repos}\",
    \"repo_scope\": \"\${GITLAB_PROJECTS:-customer repo specs}\",
    \"owners\": \"\$owner\",
    \"writeback_strategy\": \"\${JARVIS_WRITEBACK_STRATEGY:-local-only}\"
  },
  \"identity_reconciliation\": {
    \"company_identity\": {
      \"name\": \"\$company\",
      \"slug\": \"\$company_slug\",
      \"status\": \"needs-owner-confirmation\"
    },
    \"confirmed_product_identity\": \"unresolved\",
    \"source_detected_identities\": [
      {
        \"identity\": \"customer repo specs\",
        \"evidence\": \"E2E_REPO_SPECS\",
        \"status\": \"needs-owner-confirmation\"
      }
    ],
    \"conflicts\": [],
    \"status\": \"needs-owner-confirmation\"
  },
  \"confirmed_answers\": {
    \"company_name\": \"\$company\",
    \"first_workflow\": \"\$first_loop\",
    \"owners\": \"\$owner\"
  },
  \"unresolved_questions\": [
    \"customer owner must confirm company/product/source identity reconciliation\",
    \"repo owners must confirm generated repo-local commands before production use\",
    \"shadow pilot artifact is not selected\"
  ],
  \"generated_files\": [
    \"README.md\",
    \"MAINTENANCE.md\",
    \"jarvis.toml\",
    \"\$entry_skill\",
    \"references/jarvis-first-routing.md\",
    \"references/agent-engineering-quality-gate.md\",
    \"references/minimal-closure-card.md\",
    \"references/redaction-rules.md\",
    \"references/history-replay.md\",
    \"references/writeback-governance.md\",
    \"cross-cutting/module-interactions.md\",
    \"modules/\$module_slug/overview.md\",
    \"sources/\$source_slug/README.md\",
    \"tools/README.md\"
  ],
  \"scaffold_owned_files\": [
    \"README.md\",
    \"MAINTENANCE.md\",
    \"jarvis.toml\",
    \"\$entry_skill\",
    \"_bootstrap/jarvis-build-brief.md\",
    \"_bootstrap/rollout-confirmation-checklist.md\",
    \"sources/\$source_slug/README.md\",
    \"modules/\$module_slug/overview.md\",
    \"cross-cutting/ownership-map.md\",
    \"cross-cutting/module-interactions.md\",
    \"references/jarvis-first-routing.md\",
    \"references/agent-engineering-quality-gate.md\",
    \"references/minimal-closure-card.md\",
    \"references/redaction-rules.md\",
    \"references/history-replay.md\",
    \"references/writeback-governance.md\",
    \"references/runtime-governance.md\",
    \"tools/README.md\"
  ],
  \"method_repo\": {
    \"url\": \"\${CREATE_JARVIS_SKILL_REPO_URL:-file:///create-jarvis-skill}\",
    \"requested_ref\": null,
    \"resolved_commit\": \"\$method_commit\"
  },
  \"writeback_policy\": \"\${JARVIS_WRITEBACK_STRATEGY:-local-only}\",
  \"noninteractive\": true,
  \"updated_at\": \"\$generated_at\"
}
EOF

cat > \"\$target/bootstrap-result.json\" <<EOF
{
  \"schema_version\": 1,
  \"status\": \"needs-input\",
  \"result_code\": \"ok\",
  \"retryable\": false,
  \"summary\": \"Generated company Jarvis machine-chain sample and repo-local skill packages for customer repo copies. Status is needs-input until owner confirms identity reconciliation, repo-local commands, and shadow pilot artifact.\",
  \"paths\": {
    \"jarvis_home\": \"\$target\",
    \"jarvis_target_home\": \"\$target\",
    \"entry_skill\": \"\$entry_skill\"
  },
  \"method_repo\": {
    \"url\": \"\${CREATE_JARVIS_SKILL_REPO_URL:-file:///create-jarvis-skill}\",
    \"requested_ref\": null,
    \"resolved_commit\": \"\$method_commit\"
  },
  \"created_files\": [
    \$created_files
  ],
  \"updated_files\": [],
  \"preserved_files\": [],
  \"unresolved_questions\": [
    \"customer owner must confirm company/product/source identity reconciliation\",
    \"repo owners must confirm generated repo-local commands before production use\",
    \"shadow pilot artifact is not selected\"
  ],
  \"missing_inputs\": [
    \"identity reconciliation confirmation\",
    \"repo command confirmation\",
    \"shadow pilot artifact\"
  ],
  \"conflicting_inputs\": [],
  \"blockers\": [],
  \"writeback_policy\": \"\${JARVIS_WRITEBACK_STRATEGY:-local-only}\",
  \"next_action\": \"human-confirmation\",
  \"generated_at\": \"\$generated_at\"
}
EOF
AGENT
chmod +x /e2e/bootstrap-agent"

log "running jarvis-box bootstrap jarvis"
docker exec "$container_name" bash -lc "
  set -uo pipefail
  set +e
  runuser -u jarvis-box -- env \
    HOME=/var/lib/jarvis-box \
    PATH=/usr/local/bin:/usr/bin:/bin \
    JARVIS_COMPANY_SLUG='$company_slug' \
    JARVIS_BOOTSTRAP_AGENT_CMD=/e2e/bootstrap-agent \
    JARVIS_BOOTSTRAP_WORKDIR=/e2e/work/bootstrap \
    CREATE_JARVIS_SKILL_REPO_URL=file:///create-jarvis-skill \
    E2E_METHOD_REPO=/create-jarvis-skill \
    E2E_CUSTOMER_REPOS=/e2e/customer-repos \
    JARVIS_COMPANY_NAME='$company_name' \
    JARVIS_FIRST_LOOP='$first_loop' \
    GITLAB_HOST=gitlab.example.com \
    GITLAB_PROJECTS='customer-repo-specs' \
    JARVIS_SOURCE_OF_TRUTH=/e2e/customer-repos \
    JARVIS_OWNERS='$owners' \
    JARVIS_WRITEBACK_STRATEGY='$writeback_strategy' \
    JARVIS_TARGET_HOME=/e2e/output/company-jarvis \
    jarvis-box bootstrap jarvis --non-interactive
  bootstrap_rc=\$?
  set -e
  if [ \"\$bootstrap_rc\" -ne 0 ]; then
    bootstrap_status=\$(python3 - <<'PY'
import json
from pathlib import Path

path = Path('/e2e/output/company-jarvis/bootstrap-result.json')
if not path.exists():
    print('')
else:
    try:
        print(json.loads(path.read_text(encoding='utf-8')).get('status', ''))
    except Exception:
        print('')
PY
)
    case \"\$bootstrap_status\" in
      needs-input|blocked)
        printf '[customer-bootstrap-e2e] jarvis-box returned rc=%s with bootstrap status=%s; continuing to verifier\n' \"\$bootstrap_rc\" \"\$bootstrap_status\"
        ;;
      *)
        exit \"\$bootstrap_rc\"
        ;;
    esac
  fi
"

log "verifying generated artifacts"
docker exec "$container_name" bash -lc "
  set -euo pipefail
  python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py \
    --jarvis-home /e2e/output/company-jarvis \
    --customer-repos-dir /e2e/customer-repos \
    --report-json /e2e/bootstrap-verify-report.json \
    --report-md /e2e/bootstrap-verify-findings.md \
    >/e2e/bootstrap-verify-stdout.json
  runuser -u jarvis-box -- env HOME=/var/lib/jarvis-box PATH=/usr/local/bin:/usr/bin:/bin jarvis-box doctor >/e2e/jarvis-box-doctor.txt
"

log "outputs:"
printf '  run_dir=%s\n' "$run_dir"
printf '  company_jarvis=%s\n' "$run_dir/output/company-jarvis"
printf '  customer_repos=%s\n' "$run_dir/customer-repos"
printf '  verification=%s\n' "$run_dir/bootstrap-verify-report.json"
printf '  doctor=%s\n' "$run_dir/jarvis-box-doctor.txt"
