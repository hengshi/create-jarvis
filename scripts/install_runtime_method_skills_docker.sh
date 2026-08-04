#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  scripts/install_runtime_method_skills_docker.sh install|doctor \
    --jarvis-box-helper <deploy-production.sh> \
    --deployment-home <absolute-path> \
    --agent codex|claude
EOF
}

[ "$#" -gt 0 ] || { usage >&2; exit 2; }
command_name="$1"
shift
helper=""
deployment_home=""
agent=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --jarvis-box-helper) helper="${2:-}"; shift 2 ;;
    --deployment-home) deployment_home="${2:-}"; shift 2 ;;
    --agent) agent="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
case "$command_name" in install|doctor) ;; *) usage >&2; exit 2 ;; esac
[ -x "$helper" ] || { printf 'Jarvis Box helper is not executable: %s\n' "$helper" >&2; exit 2; }
case "$deployment_home" in /*) ;; *) printf 'deployment home must be absolute\n' >&2; exit 2 ;; esac
case "$agent" in
  codex) skills_root=/home/jarvis/.codex/skills ;;
  claude) skills_root=/home/jarvis/.claude/skills ;;
  *) printf 'agent must be codex or claude\n' >&2; exit 2 ;;
esac

method_commit="$(git -C "$root" rev-parse HEAD)"
printf '%s' "$method_commit" | grep -Eq '^[0-9a-f]{40}$'
[ -z "$(git -C "$root" status --porcelain --untracked-files=all)" ] || {
  printf 'refusing Docker installation from a dirty create-jarvis checkout\n' >&2
  exit 1
}

git -C "$root" archive --format=tar "$method_commit" -- \
  scripts/install_runtime_method_skills.py templates/skill-packages \
| "$helper" "$deployment_home" runtime-job sh -ceu '
    mkdir -p "$HOME/.cache"
    scratch="$(mktemp -d "$HOME/.cache/create-jarvis-method.XXXXXX")"
    trap '\''rm -rf -- "$scratch"'\'' EXIT HUP INT TERM
    tar -xf - -C "$scratch"
    python3 "$scratch/scripts/install_runtime_method_skills.py" "$1" \
      --skills-root "$2" --method-commit "$3"
  ' -- "$command_name" "$skills_root" "$method_commit"
