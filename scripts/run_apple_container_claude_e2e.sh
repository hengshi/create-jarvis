#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  E2E_REPO_SPECS="lhotse=/repo-cache/lhotse.git,everest=/repo-cache/everest.git" \
  E2E_REPO_CACHE_DIR=/path/to/repo-cache \
  JARVIS_BOX_DIST_DIR=/path/to/jarvis-box/dist \
  scripts/run_apple_container_claude_e2e.sh

E2E flow: release install.sh -> jarvis-box bootstrap -> host-isolated replay -> verify.

1. Builds the Apple container image with Claude CLI and replay entrypoint.
2. Starts an outer bootstrap container (detached) that runs the real jarvis-box
   install.sh from the release artifact and then bootstraps a company Jarvis repo.
3. The outer container may create replay bridge requests under
   <run_dir>/replay-bridge/<case-id>/READY.
4. The host monitor picks up each READY, launches an independent replay container
   with minimal mounts (no bootstrap output, no create-jarvis-skill, no hidden
   oracle), and signals DONE when complete.
5. After the outer container exits and all replays finish, outer logs and exit
   code are collected. The script exits with the outer container's exit code.

Credentials:
  ANTHROPIC_* values are loaded from ~/.zshrc into a temporary env-file.
  Values are not printed and the env-file is deleted on exit.

Required:
  E2E_REPO_SPECS       comma-separated repo specs using container-visible paths

Optional:
  E2E_REPO_CACHE_DIR   host repo cache mounted read-only at /repo-cache
  JARVIS_BOX_DIST_DIR  jarvis-box release artifact dir, default /tmp/jarvis-box-install-e2e/dist
  E2E_RUN_DIR          host output dir
  E2E_CONTINUE_FROM_DIR existing E2E run dir to audit and resume (absolute path)
  E2E_CONTAINER_NAME   default create-jarvis-skill-claude-e2e
  E2E_CONTAINER_IMAGE  default create-jarvis-skill/claude-e2e:latest
  E2E_REBUILD_IMAGE    set 1 to rebuild image
  E2E_CONTAINER_MEMORY default 8G
  E2E_CONTAINER_CPUS   optional CPU limit
  E2E_STOP_AFTER_INSTALL set 1 to run release install smoke without invoking Claude
  E2E_REPLAY_USER      replay container --user, default $(id -u):$(id -g) (non-root required by Claude CLI bypassPermissions)
  E2E_REPLAY_BRIDGE_POLL_SECONDS single replay request wait window, default 600
  REPLAY_BRIDGE_TIMEOUT_SECONDS default 1800 (propagated to request-isolated-replay)
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
  printf '[apple-container-claude-e2e] %s\n' "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

# ── config ──────────────────────────────────────────────────────
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
containerfile="$repo_root/e2e/apple-container-claude/Containerfile"
dist_dir="${JARVIS_BOX_DIST_DIR:-/tmp/jarvis-box-install-e2e/dist}"
repo_cache="${E2E_REPO_CACHE_DIR:-}"
repo_specs="${E2E_REPO_SPECS:-}"
container_name="${E2E_CONTAINER_NAME:-create-jarvis-skill-claude-e2e}"
container_image="${E2E_CONTAINER_IMAGE:-create-jarvis-skill/claude-e2e:latest}"
rebuild_image="${E2E_REBUILD_IMAGE:-0}"
container_memory="${E2E_CONTAINER_MEMORY:-8G}"
container_cpus="${E2E_CONTAINER_CPUS:-}"
replay_user="${E2E_REPLAY_USER:-$(id -u):$(id -g)}"
continue_from="${E2E_CONTINUE_FROM_DIR:-}"

case "$container_name" in
  ''|*[!a-zA-Z0-9._-]*) die "unsafe E2E_CONTAINER_NAME: $container_name" ;;
esac

[ -n "$repo_specs" ] || die "E2E_REPO_SPECS is required"
[ -f "$containerfile" ] || die "Containerfile not found: $containerfile"
[ -d "$dist_dir" ] || die "JARVIS_BOX_DIST_DIR not found: $dist_dir"
[ -f "$dist_dir/SHA256SUMS" ] || die "SHA256SUMS not found in JARVIS_BOX_DIST_DIR: $dist_dir"
if [ -n "$repo_cache" ]; then
  [ -d "$repo_cache" ] || die "E2E_REPO_CACHE_DIR not found: $repo_cache"
fi

require_cmd container
require_cmd zsh
require_cmd python3

if [ -n "$continue_from" ]; then
  case "$continue_from" in
    /*) ;;
    *) die "E2E_CONTINUE_FROM_DIR must be an absolute path: $continue_from" ;;
  esac
  [ -d "$continue_from" ] || die "E2E_CONTINUE_FROM_DIR not found: $continue_from"
  [ -f "$continue_from/output/company-jarvis/bootstrap-state.json" ] \
    || die "continuation bootstrap-state.json not found: $continue_from/output/company-jarvis/bootstrap-state.json"
  [ -f "$continue_from/output/company-jarvis/bootstrap-result.json" ] \
    || die "continuation bootstrap-result.json not found: $continue_from/output/company-jarvis/bootstrap-result.json"
  [ -d "$continue_from/customer-repos" ] \
    || die "continuation customer-repos not found: $continue_from/customer-repos"
fi

# ── run dir ─────────────────────────────────────────────────────
if [ -z "${E2E_RUN_DIR:-}" ]; then
  run_id="$(date -u +%Y%m%dT%H%M%SZ)"
  run_dir="$repo_root/.eval-runs/apple-container-claude-e2e/$run_id"
else
  run_dir="$E2E_RUN_DIR"
fi
if [ -n "$continue_from" ]; then
  continue_from_canonical="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$continue_from")"
  run_dir_canonical="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$run_dir")"
  [ "$continue_from_canonical" != "$run_dir_canonical" ] \
    || die "E2E_CONTINUE_FROM_DIR must differ from E2E_RUN_DIR"
fi
mkdir -p "$run_dir"
mkdir -p "$run_dir/output"

# ── credential env file ─────────────────────────────────────────
anthropic_env_file="$(mktemp /tmp/anthropic-env.XXXXXX)"
replay_containers=()

cleanup() {
  # stop and remove outer container if it still exists
  container stop "$container_name" 2>/dev/null || true
  container rm "$container_name" 2>/dev/null || true
  # replay containers use --rm, but clean up any stragglers
  for rn in "${replay_containers[@]-}"; do
    [ -n "$rn" ] || continue
    container stop "$rn" 2>/dev/null || true
    container rm "$rn" 2>/dev/null || true
  done
  rm -f "$anthropic_env_file"
}
trap cleanup EXIT

log "run dir: $run_dir"
log "collecting ANTHROPIC_* env names from ~/.zshrc without printing values"
umask 077
zsh -lc '
  set -a
  [ -f ~/.zshrc ] && source ~/.zshrc >/dev/null 2>&1 || true
  set +a
  env
' | python3 -c '
import os
import re
import sys

allowed = re.compile(r"^(ANTHROPIC_|HTTP_PROXY=|HTTPS_PROXY=|ALL_PROXY=|NO_PROXY=|http_proxy=|https_proxy=|all_proxy=|no_proxy=)")
for line in sys.stdin:
    line = line.rstrip("\n")
    if "=" not in line:
        continue
    if allowed.match(line):
        print(line)
' > "$anthropic_env_file"
chmod 0600 "$anthropic_env_file"

if ! grep -Eq '^(ANTHROPIC_API_KEY|ANTHROPIC_AUTH_TOKEN)=' "$anthropic_env_file"; then
  die "no ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN found after sourcing ~/.zshrc"
fi
log "ANTHROPIC env file prepared: $(awk -F= '/^ANTHROPIC_/ {print $1}' "$anthropic_env_file" | sort | paste -sd ',' -)"

# ── image build ─────────────────────────────────────────────────
if [ "$rebuild_image" = "1" ] || ! container image inspect "$container_image" >/dev/null 2>&1; then
  log "building Apple container image: $container_image"
  container build -f "$containerfile" -t "$container_image" "$repo_root/e2e/apple-container-claude"
else
  log "using existing Apple container image: $container_image"
fi

# ── start outer bootstrap container (detached) ──────────────────
outer_args=(
  run
  -d
  --name "$container_name"
  --memory "$container_memory"
  --env-file "$anthropic_env_file"
  -e "E2E_REPO_SPECS=$repo_specs"
  -e "JARVIS_BOX_DIST_DIR=/dist"
  -e "JARVIS_COMPANY_SLUG=${JARVIS_COMPANY_SLUG:-acme-claude-e2e}"
  -e "JARVIS_COMPANY_NAME=${JARVIS_COMPANY_NAME:-Acme Claude E2E}"
  -e "JARVIS_CONFIRMED_PRODUCT_IDENTITY=${JARVIS_CONFIRMED_PRODUCT_IDENTITY:-}"
  -e "JARVIS_FIRST_LOOP=${JARVIS_FIRST_LOOP:-issue intake -> triage -> repo fix -> regression}"
  -e "JARVIS_SOURCE_SCOPE=${JARVIS_SOURCE_SCOPE:-}"
  -e "JARVIS_WORKFLOW_SCOPE=${JARVIS_WORKFLOW_SCOPE:-}"
  -e "JARVIS_MODULE_HINTS=${JARVIS_MODULE_HINTS:-}"
  -e "JARVIS_GITLAB_HOST=${JARVIS_GITLAB_HOST:-gitlab.example.com}"
  -e "JARVIS_BOX_GITLAB_HOST=${JARVIS_BOX_GITLAB_HOST:-gitlab.example.com}"
  -e "JARVIS_GITLAB_PROJECTS=${JARVIS_GITLAB_PROJECTS:-customer-repo-specs}"
  -e "JARVIS_RAW_SOURCE_POLICY=${JARVIS_RAW_SOURCE_POLICY:-no-raw-copy}"
  -e "JARVIS_EXPECTED_PRODUCT_IDENTITY=${JARVIS_EXPECTED_PRODUCT_IDENTITY:-${JARVIS_CONFIRMED_PRODUCT_IDENTITY:-}}"
  -e "JARVIS_EXPECTED_MODULES=${JARVIS_EXPECTED_MODULES:-}"
  -e "JARVIS_EXPECTED_SOURCES=${JARVIS_EXPECTED_SOURCES:-}"
  -e "JARVIS_EXPECTED_SKILLS=${JARVIS_EXPECTED_SKILLS:-}"
  -e "JARVIS_OWNERS=${JARVIS_OWNERS:-platform-owner}"
  -e "JARVIS_WRITEBACK_STRATEGY=${JARVIS_WRITEBACK_STRATEGY:-local-only}"
  -e "E2E_STOP_AFTER_INSTALL=${E2E_STOP_AFTER_INSTALL:-0}"
  -e "E2E_REPLAY_BRIDGE_POLL_SECONDS=${E2E_REPLAY_BRIDGE_POLL_SECONDS:-600}"
  -e "REPLAY_BRIDGE_TIMEOUT_SECONDS=${REPLAY_BRIDGE_TIMEOUT_SECONDS:-1800}"
  -e "E2E_HOST_UID=$(id -u)"
  -v "$repo_root":/create-jarvis-skill:ro
  -v "$dist_dir":/dist:ro
  -v "$run_dir":/host-e2e
  -v "$run_dir/output":/e2e/output
)
if [ -n "$continue_from" ]; then
  outer_args+=(
    -e "E2E_CONTINUATION=1"
    -v "$continue_from":/continue-from:ro
  )
fi
if [ -n "$container_cpus" ]; then
  outer_args+=(--cpus "$container_cpus")
fi
if [ -n "${JARVIS_VERSION:-}" ]; then
  outer_args+=(-e "JARVIS_VERSION=$JARVIS_VERSION")
fi
if [ -n "$repo_cache" ]; then
  outer_args+=(-v "$repo_cache":/repo-cache:ro)
fi
outer_args+=("$container_image" bash /create-jarvis-skill/e2e/apple-container-claude/run-in-container.sh)

# ── pre-launch: resolve stale containers ─────────────────────────
existing_state="$(container list --all --format json 2>/dev/null \
  | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(1)
for c in (data if isinstance(data, list) else []):
    if c.get('id', '') == '$container_name':
        status = c.get('status', {})
        if isinstance(status, dict):
            print(status.get('state', ''))
        else:
            print(status)
        break
" 2>/dev/null || echo "")"

case "$existing_state" in
  stopped)
    log "removing stopped container with same name: $container_name"
    container rm "$container_name" 2>/dev/null || true
    ;;
  running)
    die "container with same name is already running: $container_name"
    ;;
esac

# ── pre-launch: clean stale markers from previous runs ─────────────
rm -f "$run_dir/outer-exit-code"
for _f in "$run_dir"/.outer-exit-code.*; do
  [ -e "$_f" ] && rm -f "$_f"
done

log "starting outer bootstrap container (detached): $container_name"
container "${outer_args[@]}"

# ── replay bridge monitor loop ──────────────────────────────────
replay_index=0
log "entering replay bridge monitor loop"

while true; do
  # --- process any unhandled READY files ---
  for ready_file in "$run_dir"/replay-bridge/*/READY; do
    [ -f "$ready_file" ] || continue
    request_dir="$(dirname "$ready_file")"

    # The requester owns the absolute timeout. Convert its cancellation marker
    # into the host monitor's terminal DONE state without launching a replay.
    if [ -f "$request_dir/CANCELLED" ]; then
      log "replay request cancelled before host launch: $(basename "$request_dir")"
      touch "$request_dir/HOST_SKIPPED"
      touch "$request_dir/DONE"
      continue
    fi

    # skip if host already started this one
    if [ -f "$request_dir/HOST_STARTED" ]; then
      continue
    fi

    touch "$request_dir/HOST_STARTED"
    case_id="$(basename "$request_dir")"

    # validate request.json exists
    if [ ! -f "$request_dir/request.json" ]; then
      log "ERROR: replay request $case_id missing request.json"
      mkdir -p "$request_dir/output"
      echo "1" > "$request_dir/output/exit-code"
      cat > "$request_dir/output/replay-result.md" <<'ERR'
# Replay Error
The replay request was malformed: request.json missing.
ERR
      cat > "$request_dir/output/host-isolation-evidence.json" <<'ERRJSON'
{"mechanism": "secondary-apple-container", "error": "malformed request: request.json missing"}
ERRJSON
      touch "$request_dir/DONE"
      continue
    fi

    # verify required directories
    malformed=0
    for sub in visible-packet parent-worktree company-runtime output; do
      if [ ! -d "$request_dir/$sub" ]; then
        log "ERROR: replay request $case_id missing required directory: $sub"
        malformed=1
      fi
    done
    if [ "$malformed" -eq 1 ]; then
      mkdir -p "$request_dir/output"
      echo "1" > "$request_dir/output/exit-code"
      cat > "$request_dir/output/replay-result.md" <<'ERR'
# Replay Error
The replay request was malformed: required directory missing.
ERR
      cat > "$request_dir/output/host-isolation-evidence.json" <<'ERRJSON'
{"mechanism": "secondary-apple-container", "error": "malformed request: required directory missing"}
ERRJSON
      touch "$request_dir/DONE"
      continue
    fi

    replay_index=$((replay_index + 1))
    # Apple Container limits IDs to 64 characters. Keep the name short while
    # retaining per-run uniqueness across different outer container names.
    replay_token="$(printf '%s' "$container_name/$case_id" | cksum | awk '{print $1}')"
    replay_name="jv-replay-${replay_index}-${replay_token}"
    replay_containers+=("$replay_name")

    log "launching replay container: $replay_name (case-id=$case_id)"

    replay_memory="${E2E_REPLAY_MEMORY:-4G}"
    replay_args=(--rm --name "$replay_name" --memory "$replay_memory")
    if [ -n "$container_cpus" ]; then
      replay_args+=(--cpus "$container_cpus")
    fi

    replay_rc=0
    container run "${replay_args[@]}" \
      --user "$replay_user" \
      --tmpfs /tmp/create-jarvis-replay \
      -e "HOME=/tmp/create-jarvis-replay/home" \
      --env-file "$anthropic_env_file" \
      -v "$request_dir/visible-packet:/replay/visible:ro" \
      -v "$request_dir/parent-worktree:/replay/worktree" \
      -v "$request_dir/company-runtime:/replay/company-runtime:ro" \
      -v "$request_dir/output:/replay/output" \
      "$container_image" /usr/local/bin/create-jarvis-replay \
      || replay_rc=$?

    # write exit-code if replay script did not
    if [ ! -f "$request_dir/output/exit-code" ]; then
      echo "$replay_rc" > "$request_dir/output/exit-code"
    fi

    # write host isolation evidence (no credential values)
    cat > "$request_dir/output/host-isolation-evidence.json" <<HOSTEV
{
  "mechanism": "secondary-apple-container",
  "replay_container_name": "$replay_name",
  "allowed_mounts": [
    {"host": "request/visible-packet",    "container": "/replay/visible",        "mode": "ro"},
    {"host": "request/parent-worktree",   "container": "/replay/worktree",       "mode": "rw"},
    {"host": "request/company-runtime",   "container": "/replay/company-runtime","mode": "ro"},
    {"host": "request/output",            "container": "/replay/output",         "mode": "rw"}
  ],
  "forbidden_mounts": [
    "create-jarvis-skill repo",
    "bootstrap output root",
    "dist artifacts",
    "repo-cache",
    "host-e2e root",
    "hidden oracle"
  ]
}
HOSTEV

    touch "$request_dir/DONE"
    log "replay complete: $replay_name (exit=$(cat "$request_dir/output/exit-code"))"
  done

  # --- check outer container state ---
  outer_state="$(container list --all --format json 2>/dev/null \
    | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(1)
# Apple container 1.0: top-level objects with field 'id', state at 'status.state'
for c in (data if isinstance(data, list) else []):
    if c.get('id', '') == '$container_name':
        status = c.get('status', {})
        if isinstance(status, dict):
            print(status.get('state', ''))
        else:
            print(status)
        break
" 2>/dev/null || echo "")"

  case "$outer_state" in
    running)
      ;;
    stopped)
      log "outer container state: stopped"
      ;;
    "")
      log "outer container state unknown (empty), continuing to wait"
      ;;
    *)
      log "outer container state: $outer_state, continuing to wait"
      ;;
  esac

  if [ "$outer_state" = "stopped" ]; then
    # check if all READY have been processed (have DONE)
    pending=0
    for ready_file in "$run_dir"/replay-bridge/*/READY; do
      [ -f "$ready_file" ] || continue
      req_dir="$(dirname "$ready_file")"
      if [ ! -f "$req_dir/DONE" ]; then
        pending=1
        break
      fi
    done
    if [ "$pending" -eq 0 ]; then
      log "outer container stopped, all replays complete"
      break
    fi
  fi

  sleep 2
done

# ── collect outer container logs ────────────────────────────────
log "collecting outer container logs"
container logs "$container_name" > "$run_dir/outer-container.log" 2>&1 || true
container rm "$container_name" 2>/dev/null || true

# ── validate and exit with outer exit code ───────────────────────
if [ ! -f "$run_dir/outer-exit-code" ]; then
  die "outer-exit-code not found at $run_dir/outer-exit-code — outer container may have been terminated before finalizing sync"
fi

outer_exit_code="$(cat "$run_dir/outer-exit-code")"
case "$outer_exit_code" in
  ''|*[!0-9]*)
    die "outer-exit-code is not an integer: '$outer_exit_code'"
    ;;
esac

if [ "$outer_exit_code" -lt 0 ] || [ "$outer_exit_code" -gt 255 ]; then
  die "outer-exit-code out of range [0,255]: $outer_exit_code"
fi

log "outer exit code: $outer_exit_code"
log "outputs:"
printf '  run_dir=%s\n' "$run_dir"
printf '  company_jarvis=%s\n' "$run_dir/output/company-jarvis"
printf '  customer_repos=%s\n' "$run_dir/customer-repos"
printf '  verification=%s\n' "$run_dir/bootstrap-verify-report.json"
printf '  claude_stdout=%s\n' "$run_dir/claude-stdout.jsonl"
printf '  claude_stderr=%s\n' "$run_dir/claude-stderr.log"
printf '  outer_container_log=%s\n' "$run_dir/outer-container.log"
printf '  install_log=%s\n' "$run_dir/install.log"
printf '  install_evidence=%s\n' "$run_dir/install-evidence.md"
if [ -d "$run_dir/replay-bridge" ] && [ "$(ls -A "$run_dir/replay-bridge" 2>/dev/null)" ]; then
  printf '  replay_bridge=%s\n' "$run_dir/replay-bridge"
fi

exit "$outer_exit_code"
