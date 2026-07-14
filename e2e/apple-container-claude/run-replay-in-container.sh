#!/usr/bin/env bash
set -euo pipefail

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[create-jarvis-replay] %s\n' "$*"
}

# ── mount contract ──────────────────────────────────────────────
for mount in /replay/visible /replay/worktree /replay/company-runtime /replay/output; do
  [ -d "$mount" ] || die "required mount missing: $mount"
done

[ -f /replay/visible/replay-prompt.md ] || die "/replay/visible/replay-prompt.md not found"

# ── writable HOME (tmpfs, required for non-root Claude CLI) ─────
mkdir -p "$HOME"
chmod 700 "$HOME"
export HOME

# ── isolation manifest ──────────────────────────────────────────
cat > /replay/output/replay-isolation-manifest.json <<'MANIFEST'
{
  "mechanism": "secondary-apple-container",
  "allowed_mounts": [
    "/replay/visible",
    "/replay/worktree",
    "/replay/company-runtime",
    "/replay/output"
  ],
  "forbidden_inputs": [
    "hidden oracle",
    "bootstrap output root",
    "eval case",
    "bootstrap transcript",
    "/host-e2e",
    "/create-jarvis-skill"
  ]
}
MANIFEST

# ── run Claude in the worktree ──────────────────────────────────
cd /replay/worktree

prompt="$(cat /replay/visible/replay-prompt.md)"

# ponytail: append deterministic guard to the prompt
guard='
---
Deterministic replay constraints:
- Start from the company runtime entry skill in /replay/company-runtime.
- You may only read files under: /replay/visible, /replay/company-runtime, /replay/worktree, /replay/output.
- Complete the WORK and VERIFY phases.
- Write a summary of results to /replay/output/replay-result.md.
- Do not search for or read any hidden oracle, bootstrap-output, eval-case, or bootstrap-transcript files.
- Do not assume any file exists outside the four allowed mounts.'
full_prompt="${prompt}${guard}"

log "running isolated replay agent"
replay_rc=0
printf '%s\n' "$full_prompt" \
  | claude -p \
      --input-format text \
      --output-format stream-json \
      --verbose \
      --permission-mode bypassPermissions \
      --add-dir /replay/visible \
      --add-dir /replay/company-runtime \
      --add-dir /replay/worktree \
      --add-dir /replay/output \
    > /replay/output/replay-agent.jsonl \
    2> /replay/output/replay-agent.stderr.log \
  || replay_rc=$?

# ponytail: claude rc=0 with no result is still a failure
if [ "$replay_rc" -eq 0 ]; then
  if [ ! -f /replay/output/replay-result.md ] || [ ! -s /replay/output/replay-result.md ]; then
    replay_rc=1
    printf 'ERROR: claude exited 0 but /replay/output/replay-result.md is missing or empty\n' >> /replay/output/replay-agent.stderr.log
    log "replay agent exited 0 but replay-result.md missing/empty; rc overridden to 1"
  fi
fi

# ── write exit code ─────────────────────────────────────────────
echo "$replay_rc" > /replay/output/exit-code

if [ "$replay_rc" -ne 0 ]; then
  log "replay agent exited non-zero: $replay_rc (output preserved)"
fi

log "replay done"
exit "$replay_rc"
