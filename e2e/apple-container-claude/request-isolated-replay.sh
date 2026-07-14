#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: request-isolated-replay
  --case-id ID
  --visible-packet DIR
  --parent-worktree DIR
  --company-jarvis DIR
  --destination DIR

Idempotent short-poll protocol for isolated replay:
- First call creates and submits the bridge request.
- Same case/params repeated call continues waiting/collecting (does not error).
- Each call waits up to REPLAY_BRIDGE_POLL_SECONDS (default 90) then exits 75 if still PENDING.
- Absolute timeout REPLAY_BRIDGE_TIMEOUT_SECONDS (default 1800) cancels with exit 124.
- On DONE copies output and returns the replay exit code.
- Parameter mismatch or corrupt request fails closed.

Test mode: set REQUEST_ISOLATED_REPLAY_TEST_MODE=1 and provide
  REQUEST_ISOLATED_REPLAY_E2E_ROOT  (replaces /e2e)
  REQUEST_ISOLATED_REPLAY_BRIDGE_ROOT (replaces /host-e2e/replay-bridge)
USAGE
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[request-isolated-replay] %s\n' "$*"
}

# ── test mode gating ──────────────────────────────────────────────
test_mode="${REQUEST_ISOLATED_REPLAY_TEST_MODE:-0}"
e2e_root_override="${REQUEST_ISOLATED_REPLAY_E2E_ROOT:-}"
bridge_root_override="${REQUEST_ISOLATED_REPLAY_BRIDGE_ROOT:-}"

if [ "$test_mode" = "1" ]; then
  [ -n "$e2e_root_override" ] || die "REQUEST_ISOLATED_REPLAY_TEST_MODE=1 requires REQUEST_ISOLATED_REPLAY_E2E_ROOT"
  [ -n "$bridge_root_override" ] || die "REQUEST_ISOLATED_REPLAY_TEST_MODE=1 requires REQUEST_ISOLATED_REPLAY_BRIDGE_ROOT"
  E2E_ROOT="$e2e_root_override"
  BRIDGE_ROOT="$bridge_root_override"
else
  if [ -n "$e2e_root_override" ] || [ -n "$bridge_root_override" ]; then
    die "REQUEST_ISOLATED_REPLAY_E2E_ROOT and REQUEST_ISOLATED_REPLAY_BRIDGE_ROOT are only allowed in test mode (set REQUEST_ISOLATED_REPLAY_TEST_MODE=1)"
  fi
  E2E_ROOT="/e2e"
  BRIDGE_ROOT="/host-e2e/replay-bridge"
fi

# ── parse args ──────────────────────────────────────────────────
case_id=""
visible_packet=""
parent_worktree=""
company_jarvis=""
destination=""

while [ $# -gt 0 ]; do
  case "$1" in
    --case-id)       case_id="$2";       shift 2 ;;
    --visible-packet) visible_packet="$2"; shift 2 ;;
    --parent-worktree) parent_worktree="$2"; shift 2 ;;
    --company-jarvis)  company_jarvis="$2";  shift 2 ;;
    --destination)     destination="$2";     shift 2 ;;
    -h|--help)         usage; exit 0 ;;
    *) die "unknown arg: $1" ;;
  esac
done

# ── validate ────────────────────────────────────────────────────
[ -n "$case_id" ]       || die "--case-id is required"
[ -n "$visible_packet" ] || die "--visible-packet is required"
[ -n "$parent_worktree" ] || die "--parent-worktree is required"
[ -n "$company_jarvis" ]  || die "--company-jarvis is required"
[ -n "$destination" ]     || die "--destination is required"

# case-id: safe chars only (alphanumeric, dash, underscore, dot)
case "$case_id" in
  *[!a-zA-Z0-9._-]*) die "case-id contains unsafe characters: $case_id" ;;
esac

[ -d "$visible_packet" ] || die "visible-packet dir not found: $visible_packet"
[ -d "$parent_worktree" ] || die "parent-worktree dir not found: $parent_worktree"
[ -d "$company_jarvis" ]  || die "company-jarvis dir not found: $company_jarvis"

# Fail before creating bridge state when the caller has not prepared a real
# snapshot. Otherwise a later git-init/commit failure would leave a corrupt
# request directory that blocks every retry for the same case ID.
find "$visible_packet" -mindepth 1 -print -quit | grep -q . \
  || die "visible-packet is empty: create the replay packet before submitting"
find "$parent_worktree" -mindepth 1 -print -quit | grep -q . \
  || die "parent-worktree is empty: prepare the cutoff snapshot before submitting"

# ── path contracts ──────────────────────────────────────────────
expected_visible="${E2E_ROOT}/output/company-jarvis/_bootstrap/history-replay-runs/${case_id}/visible-packet"
expected_parent="${E2E_ROOT}/work/replay-parent-worktrees/${case_id}"
expected_company="${E2E_ROOT}/output/company-jarvis"
expected_dest="${E2E_ROOT}/output/company-jarvis/_bootstrap/history-replay-runs/${case_id}"

case "$visible_packet" in
  "$expected_visible") ;;
  *) die "visible-packet must be $expected_visible" ;;
esac
case "$parent_worktree" in
  "$expected_parent") ;;
  *) die "parent-worktree must be $expected_parent" ;;
esac
[ "$company_jarvis" = "$expected_company" ] \
  || die "company-jarvis must be $expected_company"
case "$destination" in
  "$expected_dest") ;;
  *) die "destination must be $expected_dest" ;;
esac

# destination must be creatable (parent exists or we can mkdir -p)
if [ ! -d "$destination" ]; then
  mkdir -p "$destination" || die "cannot create destination: $destination"
fi

# ── timeout validation ──────────────────────────────────────────
poll_seconds="${REPLAY_BRIDGE_POLL_SECONDS:-90}"
absolute_timeout="${REPLAY_BRIDGE_TIMEOUT_SECONDS:-1800}"

case "$poll_seconds" in
  ''|*[!0-9]*) die "REPLAY_BRIDGE_POLL_SECONDS must be a non-negative integer, got: '$poll_seconds'" ;;
esac
case "$absolute_timeout" in
  ''|*[!0-9]*) die "REPLAY_BRIDGE_TIMEOUT_SECONDS must be a positive integer, got: '$absolute_timeout'" ;;
esac
if [ "$absolute_timeout" -le 0 ]; then
  die "REPLAY_BRIDGE_TIMEOUT_SECONDS must be a positive integer, got: $absolute_timeout"
fi

# ── request root ────────────────────────────────────────────────
mkdir -p "$BRIDGE_ROOT"

request_root="$BRIDGE_ROOT/$case_id"

# ── parameter manifest helper ───────────────────────────────────
write_manifest() {
  local request_dir="$1"
  cat > "$request_dir/params-manifest.json" <<MANIFEST
{
  "case_id": "$case_id",
  "visible_packet": "$visible_packet",
  "parent_worktree": "$parent_worktree",
  "company_jarvis": "$company_jarvis",
  "destination": "$destination"
}
MANIFEST
}

# ── idempotency: if request already exists, validate and poll ──
if [ -d "$request_root" ]; then
  log "request already exists, validating (case-id=$case_id)"

  # all must exist or the request is corrupt
  if [ ! -f "$request_root/request.json" ]; then
    die "existing request is corrupt: request.json missing for case-id=$case_id"
  fi
  if [ ! -f "$request_root/params-manifest.json" ]; then
    die "existing request is corrupt: params-manifest.json missing for case-id=$case_id"
  fi
  if [ ! -f "$request_root/CREATED_AT" ]; then
    die "existing request is corrupt: CREATED_AT missing for case-id=$case_id"
  fi
  if [ ! -d "$request_root/output" ]; then
    die "existing request is corrupt: output directory missing for case-id=$case_id"
  fi

  # exact parameter comparison against manifest
  expected_manifest=$(cat <<MANIFEST
{
  "case_id": "$case_id",
  "visible_packet": "$visible_packet",
  "parent_worktree": "$parent_worktree",
  "company_jarvis": "$company_jarvis",
  "destination": "$destination"
}
MANIFEST
)
  actual_manifest=$(cat "$request_root/params-manifest.json")
  if [ "$expected_manifest" != "$actual_manifest" ]; then
    die "parameter mismatch: current parameters do not match stored manifest for case-id=$case_id"
  fi

  # if already DONE, collect
  if [ -f "$request_root/DONE" ]; then
    log "replay already DONE, collecting output (case-id=$case_id)"
    mkdir -p "$destination"
    cp -a "$request_root/output"/* "$destination/" 2>/dev/null || true

    replay_exit_code=0
    if [ -f "$destination/exit-code" ]; then
      replay_exit_code="$(cat "$destination/exit-code")"
    fi
    case "$replay_exit_code" in
      ''|*[!0-9]*) die "invalid exit-code from replay: '$replay_exit_code'" ;;
    esac
    if [ "$replay_exit_code" -lt 0 ] || [ "$replay_exit_code" -gt 255 ]; then
      die "exit-code out of range 0-255: $replay_exit_code"
    fi
    log "request-isolated-replay complete (case-id=$case_id, exit=$replay_exit_code)"
    exit "$replay_exit_code"
  fi

  # still PENDING — fall through to poll loop
  log "request still PENDING, continuing to poll (case-id=$case_id)"
else
  # ── first call: create request ─────────────────────────────────
  log "creating replay bridge request (case-id=$case_id)"

  # Build the complete request in a private staging directory, then publish
  # it atomically. The host monitor only sees READY after every input and
  # contract file exists.
  request_tmp="$BRIDGE_ROOT/.${case_id}.tmp.$$"
  if ! mkdir "$request_tmp"; then
    die "cannot create temporary request directory: $request_tmp"
  fi
  cleanup_request_tmp() {
    if [ -n "${request_tmp:-}" ] && [ -d "$request_tmp" ]; then
      rm -rf -- "$request_tmp"
    fi
  }
  trap cleanup_request_tmp EXIT

  # record first creation time for absolute timeout tracking
  date +%s > "$request_tmp/CREATED_AT"

  # ── copy visible packet ─────────────────────────────────────────
  log "copying visible packet"
  cp -a "$visible_packet" "$request_tmp/visible-packet"

  # ── copy and sanitize parent worktree ───────────────────────────
  log "copying and sanitizing parent worktree"
  cp -a "$parent_worktree" "$request_tmp/parent-worktree"

  # strip all .git pointers — both worktree .git file and regular .git directory
  find "$request_tmp/parent-worktree" -name '.git' -type f -delete
  find "$request_tmp/parent-worktree" -name '.git' -type l -delete
  find "$request_tmp/parent-worktree" -name '.git' -type d -prune -exec rm -rf -- {} \;
  if find "$request_tmp/parent-worktree" -name '.git' -print -quit | grep -q .; then
    die "failed to remove Git history pointers from parent snapshot"
  fi

  # init fresh git repo with baseline commit (makes worktree editable for replay agent)
  (
    set -e
    cd "$request_tmp/parent-worktree"
    git init >/dev/null 2>&1
    git config user.email "replay-isolation@e2e.local"
    git config user.name "Replay Isolation"
    git add -A >/dev/null 2>&1
    git commit -m "baseline: parent snapshot for isolated replay" >/dev/null 2>&1
  )

  # ── copy company runtime (allowlist only) ───────────────────────
  log "copying company runtime (allowlist)"
  mkdir -p "$request_tmp/company-runtime"

  for f in SKILL.md AGENTS.md CLAUDE.md jarvis.toml; do
    if [ -f "$company_jarvis/$f" ]; then
      cp -a "$company_jarvis/$f" "$request_tmp/company-runtime/$f"
    fi
  done

  for d in modules sources cross-cutting references skills tools; do
    if [ -d "$company_jarvis/$d" ]; then
      cp -a "$company_jarvis/$d" "$request_tmp/company-runtime/$d"
    fi
  done

  # ── create output dir ───────────────────────────────────────────
  mkdir -p "$request_tmp/output"

  # ── write request.json ──────────────────────────────────────────
  cat > "$request_tmp/request.json" <<JSON
{
  "schema_version": 1,
  "case_id": "$case_id",
  "allowed_mount_logical_names": [
    "visible-packet",
    "parent-worktree",
    "company-runtime",
    "output"
  ]
}
JSON

  # ── write parameter manifest ────────────────────────────────────
  write_manifest "$request_tmp"

  # ── signal ready ────────────────────────────────────────────────
  touch "$request_tmp/READY"
  mv "$request_tmp" "$request_root"
  request_tmp=""
  trap - EXIT
  log "request ready, waiting for host replay container (case-id=$case_id)"
fi

# ── poll loop ────────────────────────────────────────────────────
elapsed=0
interval=1

while [ $elapsed -lt $poll_seconds ]; do
  if [ -f "$request_root/DONE" ]; then
    log "replay completed (case-id=$case_id, elapsed=${elapsed}s)"
    break
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done

# ── handle DONE ──────────────────────────────────────────────────
if [ -f "$request_root/DONE" ]; then
  log "copying replay output to destination: $destination"
  mkdir -p "$destination"
  cp -a "$request_root/output"/* "$destination/" 2>/dev/null || true

  replay_exit_code=0
  if [ -f "$destination/exit-code" ]; then
    replay_exit_code="$(cat "$destination/exit-code")"
  fi

  case "$replay_exit_code" in
    ''|*[!0-9]*) die "invalid exit-code from replay: '$replay_exit_code'" ;;
  esac
  if [ "$replay_exit_code" -lt 0 ] || [ "$replay_exit_code" -gt 255 ]; then
    die "exit-code out of range 0-255: $replay_exit_code"
  fi

  log "request-isolated-replay complete (case-id=$case_id, exit=$replay_exit_code)"
  exit "$replay_exit_code"
fi

# ── absolute timeout check ───────────────────────────────────────
created_at=0
if [ -f "$request_root/CREATED_AT" ]; then
  created_at="$(cat "$request_root/CREATED_AT")"
fi
if [ "$created_at" -gt 0 ]; then
  now="$(date +%s)"
  total_elapsed=$((now - created_at))
  if [ $total_elapsed -ge $absolute_timeout ]; then
    # absolute timeout — write TIMEOUT output
    echo "124" > "$request_root/output/exit-code"
    echo "TIMEOUT" > "$request_root/output/replay-result.md"
    cat > "$request_root/output/host-isolation-evidence.json" <<'TOJSON'
{"mechanism": "secondary-apple-container", "error": "host replay timed out"}
TOJSON
    touch "$request_root/CANCELLED"
    log "ABSOLUTE TIMEOUT waiting for replay (case-id=$case_id, elapsed=${total_elapsed}s, timeout=${absolute_timeout}s)"
    mkdir -p "$destination"
    cp -a "$request_root/output"/* "$destination/" 2>/dev/null || true
    exit 124
  fi
fi

# ── still PENDING after poll window ──────────────────────────────
log "PENDING: replay not complete after ${poll_seconds}s (case-id=$case_id)"
exit 75
