#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[apple-container-claude-e2e] %s\n' "$*"
}

# ── sync outputs (bind-mount aware) ──────────────────────────────
# /e2e/output is a host bind mount — already persisted, never copied.
# Control-plane files first, customer-repos last (largest).
# Returns 0 on success, 1 if any mkdir/cp fails or required dirs missing.
sync_outputs() {
  [ -d /host-e2e ] || return 1
  [ -d /e2e ] || return 1
  mkdir -p /host-e2e || return 1
  local _sync_failed=0

  # Phase 1: small control-plane files/dirs — exclude output, home, customer-repos
  for path in /e2e/* /e2e/.[!.]* /e2e/..?*; do
    [ -e "$path" ] || continue
    case "$(basename "$path")" in
      home|customer-repos|output) continue ;;
    esac
    cp -a "$path" /host-e2e/ 2>/dev/null || _sync_failed=1
  done

  # Phase 2: customer-repos last (can be 10+ GB)
  if [ -d /e2e/customer-repos ]; then
    cp -a /e2e/customer-repos /host-e2e/ 2>/dev/null || _sync_failed=1
  fi

  return "$_sync_failed"
}

# ── signal handling ──────────────────────────────────────────────
_eb_exit_signal=""
_eb_last_rc=""
_eb_finalizing=0

_eb_handle_signal() {
  local sig="$1" code="$2"
  log "received $sig, propagating exit $code"
  _eb_exit_signal="$sig"
  _eb_last_rc="$code"
  exit "$code"
}

_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then
    # prevent recursive trap invocation
    exit "$rc"
  fi
  _eb_finalizing=1

  # Clear traps to avoid depending on Bash EXIT trap recursion behavior.
  trap - EXIT INT TERM

  local final_rc="$rc"

  # Sync outputs to host.
  # On sync failure: if original was 0, promote to 1; else preserve original.
  sync_outputs || {
    if [ "$final_rc" -eq 0 ]; then
      final_rc=1
    fi
  }

  # Write outer-exit-code atomically: temp file on same filesystem, then mv.
  # If process is SIGKILL'd mid-sync, this never runs → host fails closed.
  local _marker_tmp
  _marker_tmp="/host-e2e/.outer-exit-code.$$"
  echo "$final_rc" > "$_marker_tmp" 2>/dev/null || true
  mv "$_marker_tmp" /host-e2e/outer-exit-code 2>/dev/null || true

  exit "$final_rc"
}

trap '_eb_handle_signal INT 130' INT
trap '_eb_handle_signal TERM 143' TERM
trap 'rc=$?; [ -n "${_eb_last_rc:-}" ] && rc="$_eb_last_rc"; _eb_finalize "$rc"' EXIT

# ── env ─────────────────────────────────────────────────────────
repo_specs="${E2E_REPO_SPECS:-}"
dist_dir="${JARVIS_BOX_DIST_DIR:-/dist}"
version="${JARVIS_VERSION:-}"
company_slug="${JARVIS_COMPANY_SLUG:-acme-claude-e2e}"
company_name="${JARVIS_COMPANY_NAME:-Acme Claude E2E}"
confirmed_product_identity="${JARVIS_CONFIRMED_PRODUCT_IDENTITY:-}"
first_loop="${JARVIS_FIRST_LOOP:-issue intake -> triage -> repo fix -> regression}"
source_scope="${JARVIS_SOURCE_SCOPE:-}"
workflow_scope="${JARVIS_WORKFLOW_SCOPE:-}"
module_hints="${JARVIS_MODULE_HINTS:-}"
gitlab_host="${JARVIS_GITLAB_HOST:-gitlab.example.com}"
# Keep jarvis-box environment detection separate from the simulated customer's
# GitLab facts. In particular, HENGSHI customer E2E must generate a fresh repo
# instead of triggering jarvis-box's managed hengshi-jarvis auto-detection.
box_gitlab_host="${JARVIS_BOX_GITLAB_HOST:-gitlab.example.com}"
gitlab_projects="${JARVIS_GITLAB_PROJECTS:-customer-repo-specs}"
raw_source_policy="${JARVIS_RAW_SOURCE_POLICY:-no-raw-copy}"
owners="${JARVIS_OWNERS:-platform-owner}"
writeback_strategy="${JARVIS_WRITEBACK_STRATEGY:-local-only}"
e2e_host_uid="${E2E_HOST_UID:-}"
continuation="${E2E_CONTINUATION:-0}"

[ -n "$repo_specs" ] || die "E2E_REPO_SPECS is required"
[ -d "$dist_dir" ] || die "JARVIS_BOX_DIST_DIR not found in container: $dist_dir"
[ -f "$dist_dir/SHA256SUMS" ] || die "SHA256SUMS not found in container: $dist_dir"
[ -d /create-jarvis-skill ] || die "/create-jarvis-skill mount missing"
[ -f /create-jarvis-skill/scripts/verify_bootstrap_output.py ] || die "verify_bootstrap_output.py missing"
case "$continuation" in
  0) ;;
  1)
    [ -d /continue-from ] || die "/continue-from mount missing for continuation"
    [ -f /continue-from/output/company-jarvis/bootstrap-state.json ] \
      || die "continuation bootstrap-state.json missing"
    [ -f /continue-from/output/company-jarvis/bootstrap-result.json ] \
      || die "continuation bootstrap-result.json missing"
    [ -d /continue-from/customer-repos ] || die "continuation customer-repos missing"
    ;;
  *) die "E2E_CONTINUATION must be 0 or 1: $continuation" ;;
esac

mkdir -p \
  /e2e/bin \
  /e2e/config \
  /e2e/customer-repos \
  /e2e/logs \
  /e2e/output \
  /e2e/work/bootstrap

# runtime/state root from install.sh — use the actual paths created by install.sh
runtime_state_root=/e2e/install-root/var/lib/jarvis-box
runtime_env_file="$runtime_state_root/envs/.env.jarvis-box"
# ensure runtime directories exist (install.sh creates them under install-root)
mkdir -p "$runtime_state_root/runs" "$(dirname "$runtime_env_file")"

# ── identify release artifact ───────────────────────────────────
container_arch="$(uname -m)"
case "$container_arch" in
  x86_64|amd64) release_arch="amd64" ;;
  aarch64|arm64) release_arch="arm64" ;;
  *) die "unsupported container arch: $container_arch" ;;
esac

if [ -z "$version" ]; then
  first_artifact="$(find "$dist_dir" -maxdepth 1 -name "jarvis-box_*_linux_${release_arch}.tar.gz" | sort -V | tail -1)"
  [ -n "$first_artifact" ] || die "no linux_${release_arch} artifact found in $dist_dir"
  base="$(basename "$first_artifact")"
  version="${base#jarvis-box_}"
  version="${version%_linux_${release_arch}.tar.gz}"
fi

artifact="$dist_dir/jarvis-box_${version}_linux_${release_arch}.tar.gz"
[ -f "$artifact" ] || die "jarvis-box artifact missing: $artifact"

# ── install jarvis-box via artifact install.sh ──────────────────
log "installing jarvis-box via artifact install.sh version=$version arch=$release_arch"
rm -rf /tmp/jarvis-box-artifact
mkdir -p /tmp/jarvis-box-artifact
tar -xzf "$artifact" -C /tmp/jarvis-box-artifact

install_sh="$(find /tmp/jarvis-box-artifact -type f -name install.sh | head -1)"
[ -n "$install_sh" ] || die "install.sh not found in artifact"

install_root=/e2e/install-root
mkdir -p "$install_root"

systemd_runtime_dir=/tmp/jarvis-systemd-runtime
mkdir -p "$systemd_runtime_dir"

log "executing install.sh (log: /e2e/install.log)"
install_rc=0
JARVIS_VERSION="$version" \
JARVIS_ARTIFACT_FILE="$artifact" \
JARVIS_SHA256SUMS_FILE="$dist_dir/SHA256SUMS" \
JARVIS_TEST_ROOT="$install_root" \
JARVIS_INSTALL_OS=linux \
JARVIS_SYSTEMD_RUNTIME_DIR="$systemd_runtime_dir" \
JARVIS_AUTO_BOOTSTRAP_JARVIS=0 \
JARVIS_AUTO_SETUP_GITLAB=0 \
  bash "$install_sh" > /e2e/install.log 2>&1 || install_rc=$?

if [ "$install_rc" -ne 0 ]; then
  log "install.sh exited non-zero: $install_rc (see /e2e/install.log)"
  tail -n 60 /e2e/install.log >&2 || true
  die "install.sh failed"
fi

jarvis_box_bin="$install_root/usr/local/bin/jarvis-box"
[ -x "$jarvis_box_bin" ] || die "jarvis-box binary not found after install: $jarvis_box_bin"

# ── install evidence ────────────────────────────────────────────
log "collecting install evidence"

# hard-verify canonical install paths exposed by the supplied release artifact
_check_install_artifact() {
  local label="$1" path="$2"
  if [ ! -f "$path" ] && [ ! -x "$path" ]; then
    die "required install artifact missing: $label ($path)"
  fi
}

_check_install_artifact "jarvis-box binary"          "$install_root/usr/local/bin/jarvis-box"
_check_install_artifact "install state"              "$install_root/var/lib/jarvis-box/install-state.json"
_check_install_artifact "env sample"                 "$install_root/etc/jarvis-box/env.jarvis-box.sample"
_check_install_artifact "systemd service"            "$install_root/etc/systemd/system/jarvis-box.service"
_check_install_artifact "jarvis-self-improve script"  "$install_root/usr/local/bin/jarvis-self-improve"
_check_install_artifact "jarvis-self-improve prompt"  "$install_root/var/lib/jarvis-box/config/prompts/jarvis-self-improve.md"

# all present — verify the installed release before writing evidence
if ! jarvis_ver="$("$jarvis_box_bin" version 2>&1)"; then
  die "jarvis-box version command failed: $jarvis_ver"
fi
case "$jarvis_ver" in
  "jarvis-box $version ("*")") ;;
  *) die "jarvis-box version mismatch: expected $version, got: $jarvis_ver" ;;
esac
{
  echo "# Install Evidence"
  echo ""
  echo "## Install State"
  echo "- install.sh exit code: $install_rc"
  echo "- JARVIS_VERSION: $version"
  echo "- install root: $install_root"
  echo "- systemd runtime dir: $systemd_runtime_dir"
  echo "- JARVIS_TEST_ROOT: $install_root"
  echo "- JARVIS_INSTALL_OS: linux"
  echo ""
  echo "## Key Artifacts"
  echo "- jarvis-box binary: present ($install_root/usr/local/bin/jarvis-box)"
  echo "  - version output: $jarvis_ver"
  echo "- install state: present ($install_root/var/lib/jarvis-box/install-state.json)"
  echo "- env sample: present ($install_root/etc/jarvis-box/env.jarvis-box.sample)"
  echo "- systemd service: present ($install_root/etc/systemd/system/jarvis-box.service)"
  echo "- jarvis-self-improve script: present ($install_root/usr/local/bin/jarvis-self-improve)"
  echo "- jarvis-self-improve prompt: present ($install_root/var/lib/jarvis-box/config/prompts/jarvis-self-improve.md)"
  echo ""
  echo "## Container Day-2 Policy"
  echo "- systemd is NOT active in this test-root (expected behavior in E2E container)"
  echo "- Container day-2 operations use external scheduler / human operator fallback"
  echo "- owner: $owners"
  echo "- This is an operator-confirmed E2E policy; do not attempt to activate systemd."
} > /e2e/install-evidence.md

log "install evidence written to /e2e/install-evidence.md"

# ── verify runtime env file exists after install ──────────────────
if [ ! -f "$runtime_env_file" ]; then
  die "runtime env file missing after install: $runtime_env_file (expected at envs/.env.jarvis-box under runtime state root)"
fi
log "runtime env file confirmed: $runtime_env_file"

# ── save jarvis-box --help for Phase 14 command validation ─────────
"$jarvis_box_bin" --help > /e2e/jarvis-box-help.txt 2>&1 || true
log "jarvis-box --help saved to /e2e/jarvis-box-help.txt"

if [ "${E2E_STOP_AFTER_INSTALL:-0}" = "1" ]; then
  log "E2E_STOP_AFTER_INSTALL=1; install smoke completed"
  exit 0
fi

# ── copy request-isolated-replay helper ─────────────────────────
if [ -f /create-jarvis-skill/e2e/apple-container-claude/request-isolated-replay.sh ]; then
  install -m 0755 /create-jarvis-skill/e2e/apple-container-claude/request-isolated-replay.sh /e2e/bin/request-isolated-replay
  log "request-isolated-replay installed to /e2e/bin/"
else
  die "request-isolated-replay.sh not found in create-jarvis-skill mount"
fi

# ── prepare customer repos ──────────────────────────────────────
log "preparing customer repo copies"
rm -rf /e2e/customer-repos/* /e2e/output/* /e2e/work/bootstrap/*
if [ "$continuation" = "1" ]; then
  log "copying prior E2E artifacts into a new continuation run"
  cp -a /continue-from/customer-repos/. /e2e/customer-repos/
  cp -a /continue-from/output/company-jarvis /e2e/output/company-jarvis
  if [ -f /continue-from/semantic-acceptance.md ]; then
    cp -a /continue-from/semantic-acceptance.md /e2e/continuation-semantic-acceptance.md
  fi
else
  IFS=',' read -r -a specs <<< "$repo_specs"
  for spec in "${specs[@]}"; do
    name="${spec%%=*}"
    source="${spec#*=}"
    [ -n "$name" ] && [ -n "$source" ] && [ "$name" != "$source" ] || die "invalid repo spec: $spec"
    case "$name" in
      *[!a-zA-Z0-9._-]*)
        die "invalid repo name: $name"
        ;;
    esac
    git clone "$source" "/e2e/customer-repos/$name" >"/e2e/logs/clone-$name.log" 2>&1
    (
      cd "/e2e/customer-repos/$name" || exit 1
      rm -rf skills .agents/skills .codex/skills .claude/skills
      git add -A
      git -c user.name="e2e-fixture" -c user.email="e2e-fixture@jarvis-box.local" \
        commit --quiet --allow-empty --no-gpg-sign \
        -m "chore(e2e-fixture): remove pre-existing agent skills"
      if [ -n "$(git status --porcelain)" ]; then
        printf 'ERROR: %s\n' "fixture repo $name: git status not clean after fixture commit" >&2
        exit 1
      fi
      forbidden_paths="$(git ls-tree -r --name-only HEAD -- skills .agents/skills .codex/skills .claude/skills)"
      if [ -n "$forbidden_paths" ]; then
        printf 'ERROR: %s\n' "fixture repo $name: HEAD tree still contains pre-existing agent skill paths" >&2
        exit 1
      fi
    ) || die "fixture commit failed for repo $name"
  done
fi

# ── bootstrap agent wrapper ─────────────────────────────────────
log "installing claude bootstrap wrapper"
cat > /e2e/claude-bootstrap-agent <<'AGENT'
#!/usr/bin/env bash
set -euo pipefail
set -o pipefail

prompt="$(cat)"
{
  printf '%s\n' "$prompt"
  printf '\n%s\n' 'Runtime allowlist facts for create-jarvis-skill Phase 4:'
  printf '%s\n' 'These values are customer/operator confirmed bootstrap facts. If they conflict with the generic jarvis-box prompt fields, use these JARVIS_* values for create-jarvis-skill discovery and output contracts.'
  printf 'JARVIS_CONFIRMED_PRODUCT_IDENTITY=%s\n' "${JARVIS_CONFIRMED_PRODUCT_IDENTITY:-}"
  printf 'JARVIS_SOURCE_SCOPE=%s\n' "${JARVIS_SOURCE_SCOPE:-}"
  printf 'JARVIS_WORKFLOW_SCOPE=%s\n' "${JARVIS_WORKFLOW_SCOPE:-}"
  printf 'JARVIS_MODULE_HINTS=%s\n' "${JARVIS_MODULE_HINTS:-}"
  printf 'JARVIS_GITLAB_HOST=%s\n' "${JARVIS_GITLAB_HOST:-}"
  printf 'JARVIS_GITLAB_PROJECTS=%s\n' "${JARVIS_GITLAB_PROJECTS:-}"
  printf 'JARVIS_RAW_SOURCE_POLICY=%s\n' "${JARVIS_RAW_SOURCE_POLICY:-}"
  printf '\n%s\n' 'Execution contract for this bootstrap run:'
  printf '%s\n' '- Sole methodology authority: GOAL.md → SKILL.md → acceptance.md → playbooks/phase-checklist.md → current phase detail file. This prompt supplements with E2E path facts, operator facts, and isolated-replay transport mechanics only. It is NOT a second source of Phase rules, quality gates, or checklists.'
  printf '%s\n' '- Execute Phases 3–14 in order. Follow each phase'\''s state-transition and status-recording rules exactly as defined in playbooks/phase-checklist.md.'
  printf '%s\n' '- E2E path facts:'
  printf '%s\n' '    /create-jarvis-skill          — mounted skill template repo'
  printf '%s\n' '    /e2e/customer-repos           — customer repos'
  printf '%s\n' '    /e2e/output/company-jarvis    — company Jarvis output root'
  printf '%s\n' '    /e2e/work                     — work directory'
  printf '%s\n' '    /e2e/jarvis-box-help.txt      — jarvis-box --help output'
  printf '%s\n' '    /e2e/install-evidence.md      — install evidence'
  printf '%s\n' '- Phase 7 deterministic scripts — invoke each form separately:'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/instantiate_company_jarvis.py base --state <bootstrap-state.json>'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/instantiate_company_jarvis.py module --state <bootstrap-state.json>'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/instantiate_company_jarvis.py source --state <bootstrap-state.json>'
  printf '%s\n' '- Phase 8 deterministic script:'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/instantiate_repo_local_skill.py --repo <path>'
  printf '%s\n' '- Phase 9 deterministic scripts and verifier gate:'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/instantiate_company_jarvis.py package --state <...> --kind <kind> --name <name>'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py --stage phase-09 --jarvis-home /e2e/output/company-jarvis --customer-repos-dir /e2e/customer-repos'
  printf '%s\n' '  Do not proceed to Phase 10 while phase-09 verifier reports blockers.'
  printf '%s\n' '- Final verifier:'
  printf '%s\n' '    python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py --jarvis-home /e2e/output/company-jarvis --customer-repos-dir /e2e/customer-repos'
  printf '%s\n' '- Operator fact: all checkouts under /e2e/customer-repos are authorized, confirmed pilot repo scope. The current local tree is available for Phase 6, Phase 8, Phase 11, and Phase 12. No additional human artifact is provided; pre-fixture product history is an authorized candidate source.'
  printf '%s\n' '- Write bootstrap-result.json and bootstrap-state.json at the company Jarvis repo root (/e2e/output/company-jarvis/), not only under _bootstrap/.'
  printf '%s\n' '- Apple Container E2E isolated replay transport mechanics:'
  printf '%s\n' '  1. Parent worktree path: /e2e/work/replay-parent-worktrees/<id> (bridge rejects any other parent path).'
  printf '%s\n' '  2. Mount facts:'
  printf '%s\n' '     - visible packet directory containing only files authorized by the Phase 12 checklist'
  printf '%s\n' '     - trimmed current company runtime copy (SKILL.md, AGENTS.md, CLAUDE.md, jarvis.toml, modules/, sources/, cross-cutting/, references/, skills/, tools/ — exclude _bootstrap/, evals/, bootstrap-state.json, bootstrap-result.json)'
  printf '%s\n' '     - current repo-local skills/ overlay on parent snapshot'
  printf '%s\n' '  3. Preflight (must exit 0 before calling bridge):'
  printf '%s\n' '     python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py --stage phase-12-preflight --jarvis-home /e2e/output/company-jarvis --case-id <id>'
  printf '%s\n' '     If exit != 0, fix the case or continue scanning; do NOT call the bridge.'
  printf '%s\n' '  4. Bridge invocation:'
  printf '%s\n' '     /e2e/bin/request-isolated-replay --case-id <id> --visible-packet <packet-dir> --parent-worktree <worktree-dir> --company-jarvis <jarvis-dir> --destination <dest-dir>'
  printf '%s\n' '     /e2e/bin/request-isolated-replay being executable proves host bridge is available. Do NOT inspect Docker/Podman inside this container to override that fact.'
  printf '%s\n' '  5. Polling exit-code contract:'
  printf '%s\n' '     75 = pending — repeat the exact same invocation, do not advance'
  printf '%s\n' '     124 = cancelled (timeout) — replay-not-executed, do NOT advance to oracle comparison'
  printf '%s\n' '     0 = terminal success — collect result from destination dir, proceed to oracle comparison'
  printf '%s\n' '     other nonzero = terminal failure — collect DONE/output if present, classify honestly, do NOT advance blindly'
  printf '%s\n' '  6. Replay container visibility restrictions: NO access to /host-e2e, /create-jarvis-skill, hidden oracle, bootstrap output root, eval case files, or outer bootstrap transcript artifacts.'
  printf '\n%s\n' 'Container E2E policy facts:'
  printf '%s\n' '- /e2e/install-evidence.md is the authoritative Phase 14 install-owned capability evidence.'
  printf '%s\n' '- The JARVIS_OWNERS value in this handoff is operator-confirmed for this E2E. Use it as the owner for the declared scope; do not request a second owner confirmation or call it a placeholder.'
  printf '%s\n' '- A confirmed source that is not required by the first workflow may be marked deferred-needs-access when no local access exists. That deferred route is not a missing input or bootstrap blocker; only missing access required by the first workflow blocks.'
  printf '%s\n' '- The test-root systemd is intentionally NOT active (container environment). Container day-2 operations use external scheduler / human operator fallback. owner=platform-owner. This is operator-confirmed E2E policy — do not report systemd inactive as a defect.'
  printf '%s\n' '- Fixture commit boundary: each customer repo under /e2e/customer-repos contains a harness commit with subject "chore(e2e-fixture): remove pre-existing agent skills". This commit is NOT a real product commit — it must never be selected as a Phase 11 shadow pilot candidate or Phase 12 history-replay candidate. Phase 6 and Phase 8 must not read deleted skill content from commits before this fixture commit as bootstrap facts, templates, or evidence. The create-jarvis-skill template is the sole authority for repo-local skill generation. Product code, docs, and tests in the current HEAD tree are readable and usable for discovery. Pre-fixture product commit history (before this fixture commit) is available for Phase 11 and Phase 12. When traversing pre-fixture history, skip any content under skills/, .agents/skills/, .codex/skills/, or .claude/skills/. The fixture commit itself must never be selected as a candidate.'
} > /e2e/claude-bootstrap-prompt.md

if [ "${E2E_CONTINUATION:-0}" = "1" ]; then
  {
    printf '\n%s\n' 'Continuation E2E facts:'
    printf '%s\n' '- Existing bootstrap-state.json and bootstrap-result.json are claims made by a prior runtime agent, not current proof that those phases still pass.'
    printf '%s\n' '- Follow the current playbook resume-integrity audit. Read /e2e/continuation-semantic-acceptance.md when present, inspect preserved user files, and run the applicable Phase 9 and final verifier gates.'
    printf '%s\n' '- Preserve existing user-authored files. Map every current failure to its earliest owning phase, repair from that earliest failed phase, reset later phases to pending as required, and then proceed sequentially through Phase 14.'
    printf '%s\n' '- The old state.phase is not a forced starting point. Do not jump directly to Phase 11-14 merely because the prior state named a later phase.'
    printf '%s\n' '- For every history-replay case, cross-check replay-agent-cli-checks.md against host-isolation-evidence.json, exit-code, and actual replay-agent.jsonl/replay-result.md. A stale, contradictory, or missing CLI report is a Phase 12 failure: regenerate the report or re-execute the case before accepting completion.'
  } >> /e2e/claude-bootstrap-prompt.md
fi

claude_args=(
  -p
  --input-format text
  --output-format stream-json
  --verbose
  --permission-mode bypassPermissions
  --add-dir /create-jarvis-skill
  --add-dir /e2e/customer-repos
  --add-dir /e2e/output
  --add-dir /e2e/work
)

printf '%s\n' "claude ${claude_args[*]//${ANTHROPIC_AUTH_TOKEN:-__NO_TOKEN__}/[redacted]}" > /e2e/claude-command.txt
cat /e2e/claude-bootstrap-prompt.md \
  | claude "${claude_args[@]}" \
    > >(tee /e2e/claude-stdout.jsonl) \
    2> >(tee /e2e/claude-stderr.log >&2)
AGENT
chmod +x /e2e/claude-bootstrap-agent

# ── bootstrap user setup ────────────────────────────────────────
if ! id -u e2e >/dev/null 2>&1; then
  if [ -n "$e2e_host_uid" ]; then
    useradd -u "$e2e_host_uid" -m -d /e2e/home -s /bin/bash e2e
  else
    useradd -m -d /e2e/home -s /bin/bash e2e
  fi
fi

# Non-recursive chown on /e2e itself so the e2e user can create files
# directly under /e2e (e.g. /e2e/claude-bootstrap-prompt.md).
# The e2e user's UID matches the host UID, but /e2e is root:root 755
# until this point.
chown e2e:e2e /e2e

# Adjust ownership of /e2e internal directories.
# Explicitly skip /e2e/output — it is a host bind mount; chown on
# bind mounts fails with "Operation not permitted" on Apple container.
# The e2e user (created with host UID) already owns /e2e/output natively.
for d in /e2e/* /e2e/.[!.]* /e2e/..?*; do
  [ -e "$d" ] || continue
  [ "$(basename "$d")" = "output" ] && continue
  chown -R e2e:e2e "$d" 2>/dev/null || true
done

agent_env=()
while IFS='=' read -r name value; do
  case "$name" in
    ANTHROPIC_*|HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|NO_PROXY|http_proxy|https_proxy|all_proxy|no_proxy)
      agent_env+=("$name=$value")
      ;;
  esac
done < <(env)

log "running jarvis-box bootstrap jarvis with real Claude"
bootstrap_args=(bootstrap jarvis --non-interactive)
if [ "$continuation" = "1" ]; then
  bootstrap_args+=(--resume)
fi
set +e
runuser -u e2e -- env \
  "${agent_env[@]}" \
  PATH="/e2e/install-root/usr/local/bin:/e2e/bin:/usr/local/bin:/usr/bin:/bin" \
  HOME=/e2e/home \
  JARVIS_CONFIG_DIR=/e2e/install-root/etc/jarvis-box \
  JARVIS_STATE_DIR="$runtime_state_root" \
  JARVIS_LOG_DIR=/e2e/logs \
  JARVIS_RUNTIME_ROOT="$runtime_state_root" \
  JARVIS_RUNTIME_AGENT=claude \
  CLAUDE_CMD=claude \
  JARVIS_COMPANY_SLUG="$company_slug" \
  JARVIS_CONFIRMED_PRODUCT_IDENTITY="$confirmed_product_identity" \
  JARVIS_BOOTSTRAP_AGENT_CMD=/e2e/claude-bootstrap-agent \
  JARVIS_BOOTSTRAP_WORKDIR=/e2e/work/bootstrap \
  CREATE_JARVIS_SKILL_REPO_URL=file:///create-jarvis-skill \
  JARVIS_COMPANY_NAME="$company_name" \
  JARVIS_FIRST_LOOP="$first_loop" \
  JARVIS_SOURCE_SCOPE="$source_scope" \
  JARVIS_WORKFLOW_SCOPE="$workflow_scope" \
  JARVIS_MODULE_HINTS="$module_hints" \
  JARVIS_GITLAB_HOST="$gitlab_host" \
  JARVIS_GITLAB_PROJECTS="$gitlab_projects" \
  JARVIS_RAW_SOURCE_POLICY="$raw_source_policy" \
  GITLAB_HOST="$box_gitlab_host" \
  GITLAB_PROJECTS="$gitlab_projects" \
  JARVIS_SOURCE_OF_TRUTH=/e2e/customer-repos \
  JARVIS_OWNERS="$owners" \
  JARVIS_WRITEBACK_STRATEGY="$writeback_strategy" \
  JARVIS_TARGET_HOME=/e2e/output/company-jarvis \
  JARVIS_ENV_FILE="$runtime_env_file" \
  E2E_CONTINUATION="$continuation" \
  "$jarvis_box_bin" "${bootstrap_args[@]}" \
  >/e2e/bootstrap-jarvis.log 2>&1
bootstrap_rc=$?
set -e

if [ "$bootstrap_rc" -ne 0 ]; then
  if grep -Fq "ERROR: create-jarvis-skill runtime agent failed:" /e2e/bootstrap-jarvis.log; then
    log "runtime agent execution failed; preserving evidence and skipping semantic verifier"
    tail -n 80 /e2e/bootstrap-jarvis.log >&2 || true
    exit "$bootstrap_rc"
  fi
  bootstrap_status="$(python3 - <<'PY'
import json
from pathlib import Path

path = Path("/e2e/output/company-jarvis/bootstrap-result.json")
if not path.exists():
    print("")
else:
    try:
        print(json.loads(path.read_text(encoding="utf-8")).get("status", ""))
    except Exception:
        print("")
PY
)"
  case "$bootstrap_status" in
    needs-input|blocked)
      log "jarvis-box returned rc=$bootstrap_rc with bootstrap status=$bootstrap_status; continuing to verifier"
      ;;
    *)
      if [ -d /e2e/output/company-jarvis ]; then
        log "jarvis-box returned rc=$bootstrap_rc with partial output; continuing to verifier"
      else
        log "jarvis-box returned rc=$bootstrap_rc; see /e2e/bootstrap-jarvis.log"
        tail -n 80 /e2e/bootstrap-jarvis.log >&2 || true
        exit "$bootstrap_rc"
      fi
      ;;
  esac
fi

# ── verify ──────────────────────────────────────────────────────
log "verifying generated artifacts"
verify_args=(
  --jarvis-home /e2e/output/company-jarvis
  --customer-repos-dir /e2e/customer-repos
  --expected-company-slug "$company_slug"
  --jarvis-box-help-file /e2e/jarvis-box-help.txt
  --replay-bridge-helper /e2e/bin/request-isolated-replay
  --report-json /e2e/bootstrap-verify-report.json
  --report-md /e2e/bootstrap-verify-findings.md
)
expected_product="${JARVIS_EXPECTED_PRODUCT_IDENTITY:-$confirmed_product_identity}"
if [ -n "$expected_product" ]; then
  verify_args+=(--expected-product-identity "$expected_product")
fi
if [ -n "${JARVIS_EXPECTED_MODULES:-}" ]; then
  IFS=',' read -r -a expected_modules <<< "${JARVIS_EXPECTED_MODULES:-}"
  for module in "${expected_modules[@]}"; do
    [ -n "$module" ] && verify_args+=(--expected-module "$module")
  done
fi
if [ -n "${JARVIS_EXPECTED_SOURCES:-}" ]; then
  IFS=',' read -r -a expected_sources <<< "${JARVIS_EXPECTED_SOURCES:-}"
  for source in "${expected_sources[@]}"; do
    [ -n "$source" ] && verify_args+=(--expected-source "$source")
  done
fi
if [ -n "${JARVIS_EXPECTED_SKILLS:-}" ]; then
  IFS=',' read -r -a expected_skills <<< "${JARVIS_EXPECTED_SKILLS:-}"
  for skill in "${expected_skills[@]}"; do
    [ -n "$skill" ] && verify_args+=(--expected-skill "$skill")
  done
fi
# Run final verifier as the e2e user (same HOME/PATH context used for bootstrap)
# so Git safe.directory does not reject e2e-owned repos.
# Report files still land at the existing /e2e paths.
runuser -u e2e -- env \
  PATH="/e2e/install-root/usr/local/bin:/e2e/bin:/usr/local/bin:/usr/bin:/bin" \
  HOME=/e2e/home \
  python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py \
    "${verify_args[@]}" \
    >/e2e/bootstrap-verify-stdout.json

log "done"
