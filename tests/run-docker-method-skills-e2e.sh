#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
jarvis_box_root="${1:-}"
image="${2:-}"
[ -x "$jarvis_box_root/scripts/deploy-production.sh" ] || {
  printf 'Usage: %s <jarvis-box-root> <image@sha256:digest>\n' "$0" >&2
  exit 2
}
[[ "$image" =~ ^.+@sha256:[0-9a-f]{64}$ ]] || {
  printf 'image must be pinned by sha256 digest\n' >&2
  exit 2
}

deployment_home="$(mktemp -d "${TMPDIR:-/tmp}/create-jarvis-docker-method.XXXXXX")"
deployment_home="$(cd -P -- "$deployment_home" && pwd -P)"
project="create-jarvis-method-e2e-$$"
helper="$jarvis_box_root/scripts/deploy-production.sh"

cleanup() {
  if [ -f "$deployment_home/deployment.env" ]; then
    "$helper" "$deployment_home" compose down --remove-orphans >/dev/null 2>&1 || true
  fi
  rm -rf -- "$deployment_home"
}
trap cleanup EXIT HUP INT TERM

printf '%s\n' \
  "JARVIS_DEPLOYMENT_HOME=$deployment_home" \
  "JARVIS_DEPLOYMENT_NAME=$project" \
  "JARVIS_IMAGE=$image" \
  'JARVIS_BIND_ADDRESS=127.0.0.1' \
  'JARVIS_PORT=0' \
  'JARVIS_AUTH_IMPORT=auto' \
  >"$deployment_home/deployment.env"
printf '%s\n' \
  'JARVIS_SERVE_MODE=read-only' \
  'JARVIS_RUNTIME_AGENT=codex' \
  'JARVIS_CONNECTOR_PROFILE=' \
  >"$deployment_home/runtime.env"
: >"$deployment_home/connector.env"
chmod 0600 "$deployment_home"/*.env

"$helper" "$deployment_home" auth-import >/dev/null
"$helper" "$deployment_home" start >/dev/null
"$root/scripts/install_runtime_method_skills_docker.sh" install \
  --jarvis-box-helper "$helper" \
  --deployment-home "$deployment_home" \
  --agent codex >/dev/null
"$root/scripts/install_runtime_method_skills_docker.sh" doctor \
  --jarvis-box-helper "$helper" \
  --deployment-home "$deployment_home" \
  --agent codex >/dev/null
"$helper" "$deployment_home" runtime-job test -r \
  /home/jarvis/.codex/skills/jarvis-self-improve-skill/SKILL.md

"$helper" "$deployment_home" compose up -d --force-recreate jarvis-box >/dev/null
"$root/scripts/install_runtime_method_skills_docker.sh" doctor \
  --jarvis-box-helper "$helper" \
  --deployment-home "$deployment_home" \
  --agent codex >/dev/null

printf 'Docker method-skill transport and persistence passed\n'
printf 'fresh_agent_discovery=required-separately\n'
