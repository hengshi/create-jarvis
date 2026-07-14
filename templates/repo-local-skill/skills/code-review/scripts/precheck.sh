#!/usr/bin/env bash
# Bootstrap-safe package contract and environment-signal check for {{REPO_NAME}}.
# It does not run product build/test commands and does not prove repo health.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd -P)"

echo "repo: {{REPO_NAME}}"
echo "precheck: root=$REPO_ROOT"

if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: script-derived root is not inside a git worktree"
  exit 1
fi

GIT_ROOT="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null)"
GIT_ROOT="$(cd "$GIT_ROOT" && pwd -P)"
if [ "$GIT_ROOT" != "$REPO_ROOT" ]; then
  echo "ERROR: script-derived root does not equal git root: $GIT_ROOT"
  exit 1
fi

cd "$REPO_ROOT"

branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' 'detached')"
echo "INFO: checkout-branch=$branch (not default-branch evidence)"
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo "WARN: working tree has uncommitted changes"
fi

CANONICAL_FILES=(
  "skills/SKILL.md"
  "skills/eval-loop.md"
  "skills/code-review/SKILL.md"
  "skills/code-review/scripts/precheck.sh"
  "skills/references/source-of-truth.md"
  "skills/references/architecture-map.md"
  "skills/references/test-entrypoints.md"
  "skills/references/runtime-and-testability.md"
  "skills/references/history-replay-loop.md"
  "skills/self-skills-improve/SKILL.md"
)

CONTENT_FILES=(
  "skills/SKILL.md"
  "skills/eval-loop.md"
  "skills/code-review/SKILL.md"
  "skills/references/source-of-truth.md"
  "skills/references/architecture-map.md"
  "skills/references/test-entrypoints.md"
  "skills/references/runtime-and-testability.md"
  "skills/references/history-replay-loop.md"
  "skills/self-skills-improve/SKILL.md"
)

blockers=0

echo "=== Canonical Package ==="
for file in "${CANONICAL_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "INFO: present $file"
  else
    echo "ERROR: missing $file"
    blockers=$((blockers + 1))
  fi
done

echo "=== Fill Contract ==="
sentinel="BOOTSTRAP_""REQUIRED"
left_brace='{'
right_brace='}'
token_prefix="${left_brace}${left_brace}"
token_suffix="${right_brace}${right_brace}"
token_re="${token_prefix}[A-Z_][A-Z_]*${token_suffix}"

for file in "${CANONICAL_FILES[@]}"; do
  [ -f "$file" ] || continue
  if grep -Fq "$sentinel" "$file"; then
    echo "ERROR: unfilled bootstrap value in $file"
    blockers=$((blockers + 1))
  fi
  if grep -Eq "$token_re" "$file"; then
    echo "ERROR: unrendered template token in $file"
    blockers=$((blockers + 1))
  fi
done

echo "=== Machine-Local Dependency Check ==="
absolute_home_re='(/Users/[^/[:space:]]+|/home/[^/[:space:]]+)'
hidden_runtime_re='~\/\.[^/[:space:]]+\/(repos|repo-cache|bin)\/'
for file in "${CONTENT_FILES[@]}"; do
  [ -f "$file" ] || continue
  if grep -Eq "$absolute_home_re|$hidden_runtime_re" "$file"; then
    echo "ERROR: hard-coded machine-local path in $file"
    blockers=$((blockers + 1))
  fi
done

echo "=== Observed Manifests And CI ==="
BUILD_FILES=(
  "Makefile"
  "package.json"
  "Cargo.toml"
  "go.mod"
  "pom.xml"
  "build.gradle"
  "build.gradle.kts"
  "CMakeLists.txt"
  "setup.py"
  "pyproject.toml"
  "BUILD"
  "BUILD.bazel"
)

found_manifest=false
for file in "${BUILD_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "INFO: build-manifest=$file"
    found_manifest=true
  fi
done
if [ "$found_manifest" = false ]; then
  echo "INFO: no manifest from the precheck detection list"
fi

[ ! -f ".gitlab-ci.yml" ] || echo "INFO: ci=.gitlab-ci.yml"
[ ! -f "Jenkinsfile" ] || echo "INFO: ci=Jenkinsfile"
[ ! -f ".circleci/config.yml" ] || echo "INFO: ci=.circleci/config.yml"
if [ -d ".github/workflows" ]; then
  workflow_count="$(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')"
  echo "INFO: ci=.github/workflows count=$workflow_count"
fi

check_tool() {
  local tool="$1"
  if command -v "$tool" >/dev/null 2>&1; then
    echo "INFO: tool=$tool available"
  else
    echo "WARN: tool=$tool unavailable"
  fi
}

echo "=== Local Tool Signals ==="
[ ! -f "Makefile" ] || check_tool make
[ ! -f "package.json" ] || check_tool node
if [ -f "Cargo.toml" ]; then
  check_tool cargo
  check_tool rustc
fi
[ ! -f "go.mod" ] || check_tool go
[ ! -f "pom.xml" ] || check_tool mvn
[ ! -f "build.gradle" ] && [ ! -f "build.gradle.kts" ] || check_tool gradle
[ ! -f "CMakeLists.txt" ] || check_tool cmake
[ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ] || check_tool python3
check_tool git

if [ "$blockers" -gt 0 ]; then
  echo "precheck: exit=1 blockers=$blockers"
  exit 1
fi

echo "precheck: exit=0 contract checks passed; product build/test not executed"
