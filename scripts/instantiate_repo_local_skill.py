#!/usr/bin/env python3
"""Deterministic instantiator for repo-local skill canonical packages.

Usage:
    python3 scripts/instantiate_repo_local_skill.py --repo <repo-path>
    python3 scripts/instantiate_repo_local_skill.py --repo <repo-path> --repo-name <exact-name>
"""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_LOCAL_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "repo-local-skill" / "skills"

CANONICAL_FILES = [
    "SKILL.md",
    "code-review/SKILL.md",
    "code-review/scripts/precheck.sh",
    "references/source-of-truth.md",
    "references/architecture-map.md",
    "references/test-entrypoints.md",
    "references/runtime-and-testability.md",
    "references/history-replay-loop.md",
    "self-skills-improve/SKILL.md",
]

# SHA-256 of the removed v1 eval-loop template.  Upgrades normalize only the
# four known repository-name slots before comparing this digest; a global
# replacement would corrupt ordinary prose when a repo is named "skill",
# "repo", "eval", or another common word.
LEGACY_EVAL_LOOP_TEMPLATE_SHA256 = (
    "23566012819c825c94416f3c341cb1520bca3b32adda80db55cb08269d452b85"
)


def _normalize_legacy_eval_loop(content: str, repo_name: str) -> str | None:
    """Restore only the known v1 placeholder slots, or fail closed."""
    replacements = (
        (
            f"name: eval-loop-{repo_name}\n",
            "name: eval-loop-{{REPO_NAME}}\n",
        ),
        (
            f"  Eval-loop methodology for the {repo_name} repository. Defines how to\n",
            "  Eval-loop methodology for the {{REPO_NAME}} repository. Defines how to\n",
        ),
        (
            f"# {repo_name} — Eval Loop Methodology\n",
            "# {{REPO_NAME}} — Eval Loop Methodology\n",
        ),
        (
            f'  repo: "{repo_name}"\n',
            '  repo: "{{REPO_NAME}}"\n',
        ),
    )
    normalized = content
    for rendered, placeholder in replacements:
        if normalized.count(rendered) != 1:
            return None
        normalized = normalized.replace(rendered, placeholder, 1)
    return normalized


def _legacy_eval_loop_status(path: Path, repo_name: str) -> tuple[str, str]:
    """Classify the removed v1 eval-loop file without mutating it."""
    if path.is_symlink():
        return "error", "legacy skills/eval-loop.md must not be a symlink"
    if not path.exists():
        return "absent", ""
    if not path.is_file():
        return "error", "legacy skills/eval-loop.md exists but is not a regular file"
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return "error", f"legacy skills/eval-loop.md is not readable UTF-8: {exc}"
    normalized = _normalize_legacy_eval_loop(content, repo_name)
    if normalized is None:
        return (
            "customized",
            "legacy skills/eval-loop.md contains non-template content or does "
            "not match the generated v1 slots; "
            "review it, move reusable rules into the actual SKILL.md/focused "
            "reference/script, then remove the legacy file before continuing",
        )
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if digest == LEGACY_EVAL_LOOP_TEMPLATE_SHA256:
        return "generated", ""
    return (
        "customized",
        "legacy skills/eval-loop.md contains non-template content; review it, "
        "move reusable rules into the actual SKILL.md/focused reference/script, "
        "then remove the legacy file before continuing",
    )


def _validate_name(name: str, label: str) -> str:
    """Validate repo name as a safe POSIX path component.

    Explicit names are preserved byte-for-byte — no normalization.
    Rejects: empty, surrounding whitespace, exact '.' or '..', '/', NUL, CR/LF.
    Ordinary internal dots are valid (e.g. 'my.repo.v2').
    """
    if not name:
        print(f"ERROR: {label} is empty", file=sys.stderr)
        sys.exit(1)
    if name != name.strip():
        print(
            f"ERROR: {label} has leading or trailing whitespace — "
            f"pass the exact name without surrounding spaces",
            file=sys.stderr,
        )
        sys.exit(1)
    if name == "." or name == "..":
        print(f"ERROR: {label} must not be '.' or '..'", file=sys.stderr)
        sys.exit(1)
    if "/" in name or "\x00" in name or "\n" in name or "\r" in name:
        print(f"ERROR: {label} contains forbidden characters", file=sys.stderr)
        sys.exit(1)
    return name


def _parse_git_url(url: str) -> str | None:
    """Extract repo name from a Git remote URL. Returns None if unparseable.

    Uses stdlib urlparse for scheme-bearing URLs; retains a small explicit
    parser for scp-like Git remotes. Supports https, ssh, file, scp-like,
    and plain local-path remotes. Returns the final path component without
    .git suffix.
    """
    url = url.strip()
    if not url:
        return None

    clean = url.rstrip("/")
    if clean.endswith(".git"):
        clean = clean[:-4]

    # ── scheme-bearing URLs (https, ssh, file, git, …) ──────────
    if "://" in clean:
        parsed = urlparse(clean)
        path = parsed.path.rstrip("/")
        if path:
            parts = path.split("/")
            for p in reversed(parts):
                if p:
                    return p
        return None

    # ── scp-like remotes: user@host:path or host:path/to/repo ──
    if ":" in clean:
        before_colon, after_colon = clean.split(":", 1)
        # ponytail: require either user@ prefix OR a path-like segment
        # after colon.  Bare "host:word" is not an scp remote.
        if "@" in before_colon or "/" in after_colon:
            path_part = after_colon.lstrip("/")
            parts = path_part.split("/")
            for p in reversed(parts):
                if p:
                    return p
            return None
        # bare 'host:word' — not a recognised scp-like remote
        return None

    # ── plain local-path remote: /path/to/repo or relative/path ─
    # ponytail: only match paths that look like real filesystem paths,
    # not bare single-component names
    if "/" in clean or clean.startswith("."):
        path = Path(clean)
        name = path.name
        if name and name not in (".", ".."):
            return name

    return None


def _infer_repo_name(repo_path: Path) -> str:
    """Infer repo name from Git origin URL, falling back to directory basename."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            name = _parse_git_url(result.stdout.strip())
            if name:
                return _validate_name(name, "inferred repo-name")
    except (subprocess.TimeoutExpired, OSError):
        pass
    # Fall back to directory basename
    basename = repo_path.resolve().name
    return _validate_name(basename, "inferred repo-name (basename)")


def _validate_target(target: Path) -> Path:
    resolved = target.resolve()
    repo_local = Path(__file__).resolve().parent.parent
    # ponytail: basic traversal guard — target must be outside this repo
    try:
        resolved.relative_to(repo_local)
        print(f"ERROR: target {target} is inside the template repo itself", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        pass
    return resolved


def _preflight(
    template_dir: Path, repo_root: Path, repo_name: str
) -> tuple[list[str], dict[str, str]]:
    """Preflight: verify sources, render content, inspect destinations, check symlinks.

    Returns (errors, rendered_plan).  rendered_plan maps rel_path_str → rendered
    content.  On any error rendered_plan is empty and the caller must not write
    any target files or directories.
    """
    errors: list[str] = []
    rendered_plan: dict[str, str] = {}

    if not template_dir.is_dir():
        errors.append(f"template source not found: {template_dir}")
        return errors, {}

    repo_root_resolved = repo_root.resolve()
    target_skills = repo_root / "skills"
    target_skills_resolved = target_skills.resolve()

    # Guard: target skills/ must resolve inside the repository
    try:
        target_skills_resolved.relative_to(repo_root_resolved)
    except ValueError:
        errors.append(
            f"target skills/ resolves outside repository: {target_skills_resolved}"
        )
        return errors, {}

    legacy_status, legacy_detail = _legacy_eval_loop_status(
        target_skills / "eval-loop.md", repo_name
    )
    if legacy_status in {"customized", "error"}:
        errors.append(legacy_detail)
        return errors, {}

    for rel_path_str in CANONICAL_FILES:
        rel_path = Path(rel_path_str)
        src = template_dir / rel_path
        dst = target_skills / rel_path
        dst_resolved = dst.resolve()

        # ── source checks ────────────────────────────────────────
        if not src.is_file():
            errors.append(f"template missing: {rel_path_str}")
            continue

        try:
            raw = src.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            errors.append(f"template not readable UTF-8: {rel_path_str}: {e}")
            continue

        # ── render now (don't re-read later) ─────────────────────
        rendered = raw.replace("{{REPO_NAME}}", repo_name)
        if "{{" in rendered and "}}" in rendered:
            unresolved = []
            for part in rendered.split("{{")[1:]:
                if "}}" in part:
                    token = part.split("}}")[0].strip()
                    unresolved.append(token)
            if unresolved:
                errors.append(f"unresolved tokens in {rel_path_str}: {unresolved}")

        # ── destination symlink-escape guard ─────────────────────
        try:
            dst_resolved.relative_to(target_skills_resolved)
        except ValueError:
            errors.append(
                f"destination escapes repo/skills via symlinks: "
                f"{rel_path_str} -> {dst_resolved}"
            )
            continue

        # ── existing-destination checks ──────────────────────────
        if dst_resolved.exists():
            if not dst_resolved.is_file():
                errors.append(
                    f"destination exists but is not a regular file: {rel_path_str}"
                )
                continue
            try:
                dst_resolved.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError) as e:
                errors.append(
                    f"destination exists but is not readable UTF-8: "
                    f"{rel_path_str}: {e}"
                )
                continue

        rendered_plan[rel_path_str] = rendered

    return errors, rendered_plan


def instantiate(repo_root: Path, repo_name: str) -> dict:
    """Copy canonical files and render tokens. Idempotent: preserves user edits.

    Runs preflight before writing any target file.  On preflight failure
    no files or directories are created.  Uses the pre-rendered plan so
    source files are not re-read after preflight.
    """
    target_skills = repo_root / "skills"
    result: dict = {
        "created": [],
        "preserved": [],
        "skipped": [],
        "removed_legacy": [],
        "errors": [],
    }

    preflight_errors, rendered_plan = _preflight(REPO_LOCAL_TEMPLATE, repo_root, repo_name)
    if preflight_errors:
        result["errors"].extend(preflight_errors)
        return result

    for rel_path_str, rendered in rendered_plan.items():
        dst = target_skills / rel_path_str

        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            existing = dst.read_text(encoding="utf-8")
            if existing == rendered:
                result["skipped"].append(rel_path_str)
            else:
                result["preserved"].append(rel_path_str)
        else:
            dst.write_text(rendered, encoding="utf-8")
            result["created"].append(rel_path_str)

    legacy_path = target_skills / "eval-loop.md"
    legacy_status, legacy_detail = _legacy_eval_loop_status(legacy_path, repo_name)
    if legacy_status == "generated":
        try:
            legacy_path.unlink()
            result["removed_legacy"].append("eval-loop.md")
        except OSError as exc:
            result["errors"].append(f"could not remove generated legacy skills/eval-loop.md: {exc}")
    elif legacy_status in {"customized", "error"}:
        result["errors"].append(legacy_detail)

    # Ensure precheck is executable
    precheck = target_skills / "code-review" / "scripts" / "precheck.sh"
    if precheck.is_file():
        precheck.chmod(precheck.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        if not os.access(precheck, os.X_OK):
            result["errors"].append("precheck.sh not executable after chmod")

    # Post-write token safety net (already checked in preflight)
    for rel_path_str in result["created"]:
        dst = target_skills / rel_path_str
        try:
            text = dst.read_text(encoding="utf-8")
        except OSError:
            continue
        if "{{" in text and "}}" in text:
            unresolved = [t for t in text.split("{{")[1:] if "}}" in t]
            unresolved_tokens = [u.split("}}")[0].strip() for u in unresolved]
            result["errors"].append(
                f"unresolved tokens in {rel_path_str}: {unresolved_tokens}"
            )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic instantiator for repo-local skill canonical packages."
    )
    parser.add_argument(
        "--repo", required=True, type=Path,
        help="Target repo path (must contain .git directory)."
    )
    parser.add_argument(
        "--repo-name", type=str,
        help="Optional override for repo name. Inferred from Git origin URL or directory basename if omitted."
    )
    args = parser.parse_args()

    repo_path = _validate_target(args.repo)

    if not repo_path.is_dir():
        print(f"ERROR: repo path does not exist: {repo_path}", file=sys.stderr)
        return 1
    if not (repo_path / ".git").exists():
        print(f"ERROR: repo path is not a git repository: {repo_path}", file=sys.stderr)
        return 1

    if args.repo_name is not None:
        repo_name = _validate_name(args.repo_name, "repo-name")
    else:
        repo_name = _infer_repo_name(repo_path)

    result = instantiate(repo_path, repo_name)

    print(f"repo: {repo_name}")
    print(f"root: {repo_path}")
    print(f"created: {len(result['created'])}")
    for f in result["created"]:
        print(f"  + {f}")
    print(f"preserved (user edited): {len(result['preserved'])}")
    for f in result["preserved"]:
        print(f"  ~ {f}")
    print(f"skipped (identical): {len(result['skipped'])}")
    for f in result["skipped"]:
        print(f"  = {f}")
    print(f"removed legacy generated files: {len(result['removed_legacy'])}")
    for f in result["removed_legacy"]:
        print(f"  - {f}")
    if result["errors"]:
        print(f"errors: {len(result['errors'])}")
        for e in result["errors"]:
            print(f"  ! {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
