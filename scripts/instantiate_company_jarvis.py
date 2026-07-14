#!/usr/bin/env python3
"""Deterministic instantiator for company Jarvis templates.

Subcommands:
    base    --state <bootstrap-state.json>
    module  --state <...> --name <confirmed exact name>
    source  --state <...> --name <confirmed exact name>  (creates sources/<name>/README.md only)
    package --state <...> --kind <skill-packages kind> --name <confirmed exact output name>
             Valid Phase 9 kinds include generic-source (source-helper skill package).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path
from urllib.parse import urlparse


TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "templates"
COMPANY_JARVIS_REPO = TEMPLATES_ROOT / "company-jarvis" / "repo"
COMPANY_JARVIS_MODULE = TEMPLATES_ROOT / "company-jarvis" / "module"
COMPANY_JARVIS_ARTIFACTS = TEMPLATES_ROOT / "company-jarvis" / "artifacts"
COMPANY_JARVIS_SOURCE = TEMPLATES_ROOT / "company-jarvis" / "source"
SKILL_PACKAGES = TEMPLATES_ROOT / "skill-packages"
def load_state(state_path: str) -> dict:
    path = Path(state_path)
    if not path.is_file():
        print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in state file: {exc}", file=sys.stderr)
        sys.exit(1)


def validate_name(name: str, label: str) -> str:
    if not name or not name.strip():
        print(f"ERROR: {label} is empty", file=sys.stderr)
        sys.exit(1)
    if name == "." or name == "..":
        print(f"ERROR: {label} must not be '.' or '..'", file=sys.stderr)
        sys.exit(1)
    if "/" in name or "\x00" in name:
        print(f"ERROR: {label} contains forbidden characters", file=sys.stderr)
        sys.exit(1)
    return name


def extract_globals(state: dict) -> dict:
    """Extract global render values from bootstrap state. Fail closed on missing required fields."""
    identity = state.get("identity_reconciliation")
    if not isinstance(identity, dict):
        print("ERROR: identity_reconciliation is missing or not an object", file=sys.stderr)
        sys.exit(1)

    company_identity = identity.get("company_identity")
    if not isinstance(company_identity, dict):
        print("ERROR: identity_reconciliation.company_identity is missing or not an object", file=sys.stderr)
        sys.exit(1)

    company_name = company_identity.get("name", "")
    company_slug = company_identity.get("slug", "")

    if not company_name or not company_name.strip():
        print("ERROR: COMPANY_NAME is empty — identity_reconciliation.company_identity.name is required", file=sys.stderr)
        sys.exit(1)
    if not company_slug or not company_slug.strip():
        print("ERROR: COMPANY_SLUG is empty — identity_reconciliation.company_identity.slug is required", file=sys.stderr)
        sys.exit(1)

    paths = state.get("paths")
    if not isinstance(paths, dict):
        print("ERROR: paths is missing or not an object", file=sys.stderr)
        sys.exit(1)

    confirmed = state.get("confirmed_answers")
    if not isinstance(confirmed, dict):
        confirmed = {}

    # PRODUCT_IDENTITY: must come from identity_reconciliation.confirmed_product_identity; fail closed if missing
    product_identity = identity.get("confirmed_product_identity", "")
    if not product_identity or not product_identity.strip():
        print("ERROR: PRODUCT_IDENTITY is empty — identity_reconciliation.confirmed_product_identity is required", file=sys.stderr)
        sys.exit(1)

    # RUNTIME_ROOT: validate state has runtime_root (fail if missing), but always render fixed literal
    runtime_root = confirmed.get("runtime_root") or paths.get("runtime_root", "")
    if not runtime_root or not runtime_root.strip():
        print("ERROR: RUNTIME_ROOT is empty — confirmed_answers.runtime_root and paths.runtime_root are both missing", file=sys.stderr)
        sys.exit(1)
    # Actual observed path stays in bootstrap-state/result, not durable templates.
    runtime_root = "$JARVIS_RUNTIME_ROOT"

    # VCS_HOST: priority vcs_host_confirmed > gitlab_host_confirmed > vcs_host > gitlab_host; missing -> BOOTSTRAP_REQUIRED
    vcs_host = (
        confirmed.get("vcs_host_confirmed")
        or confirmed.get("gitlab_host_confirmed")
        or confirmed.get("vcs_host")
        or confirmed.get("gitlab_host", "")
    )
    if not vcs_host or not vcs_host.strip():
        vcs_host = "BOOTSTRAP_REQUIRED"

    # Parse CSV/list confirmed_answers into clean deduplicated lists
    def _parse_csv(value):
        """Parse CSV string or list, strip whitespace, drop empties, stable dedup, preserve case/punctuation."""
        if isinstance(value, list):
            items = [str(v) for v in value]
        elif isinstance(value, str):
            items = [v.strip() for v in value.split(",") if v.strip()]
        else:
            return []
        seen = set()
        result = []
        for item in items:
            s = item.strip()
            if s and s not in seen:
                seen.add(s)
                result.append(s)
        return result

    module_hints = _parse_csv(confirmed.get("module_hints", ""))
    source_scope = _parse_csv(confirmed.get("source_scope", ""))
    workflow_scope = _parse_csv(confirmed.get("workflow_scope", ""))
    repo_scope = _parse_csv(confirmed.get("gitlab_projects_confirmed",
                                           confirmed.get("gitlab_projects", "")))

    def _bullet_index(items: list[str], fmt: str) -> str:
        """Generate Markdown bullet list; return BOOTSTRAP_REQUIRED if empty."""
        if not items:
            return "BOOTSTRAP_REQUIRED"
        return "\n".join(f"- {fmt.format(item)}" for item in items)

    def _repo_basename(project: str) -> str:
        """Derive checkout basename while preserving the full VCS project identity."""
        value = project.strip().rstrip("/")
        if "://" in value:
            path = urlparse(value).path
        elif ":" in value and "@" in value.split(":", 1)[0]:
            path = value.split(":", 1)[1]
        else:
            path = value
        basename = path.rstrip("/").rsplit("/", 1)[-1]
        if basename.endswith(".git"):
            basename = basename[:-4]
        if not basename or basename in {".", ".."}:
            print(f"ERROR: cannot derive repo basename from VCS project: {project!r}", file=sys.stderr)
            sys.exit(1)
        return basename

    def _repo_index(items: list[str]) -> str:
        if not items:
            return "BOOTSTRAP_REQUIRED"
        return "\n".join(
            f"- `{_repo_basename(project)}` — VCS project `{project}`; "
            "repo-local entry `skills/SKILL.md` inside that repo"
            for project in items
        )

    # COMPANY_OWNER: accept string or list; missing -> BOOTSTRAP_REQUIRED
    company_owner = confirmed.get("company_owner") or confirmed.get("owners", "")
    if isinstance(company_owner, list):
        company_owner = ", ".join(company_owner)
    if not company_owner or not company_owner.strip():
        company_owner = "BOOTSTRAP_REQUIRED"

    # ENTRY_SKILL_PATH: must come from paths.entry_skill; missing fail
    entry_skill_path = paths.get("entry_skill", "")
    if not entry_skill_path or not entry_skill_path.strip():
        print("ERROR: ENTRY_SKILL_PATH is empty — paths.entry_skill is required", file=sys.stderr)
        sys.exit(1)

    globals_ = {
        "COMPANY_NAME": company_name,
        "COMPANY_SLUG": company_slug,
        "COMPANY_JARVIS_NAME": f"{company_slug}-jarvis",
        "PRODUCT_IDENTITY": product_identity,
        "RUNTIME_ROOT": runtime_root,
        "ENTRY_SKILL_PATH": entry_skill_path,
        "VCS_HOST": vcs_host,
        "COMPANY_OWNER": company_owner,
        "MODULE_INDEX": _bullet_index(module_hints, "modules/{}/overview.md"),
        "SOURCE_INDEX": _bullet_index(source_scope, "sources/{}/README.md"),
        "WORKFLOW_INDEX": _bullet_index(workflow_scope, "skills/{}/SKILL.md"),
        "REPO_INDEX": _repo_index(repo_scope),
    }

    return globals_


def render_content(content: str, globals_: dict) -> str:
    for key, value in globals_.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def check_unresolved(content: str, rel_path: str) -> list[str]:
    """Return list of unresolved tokens, if any."""
    if "{{" not in content:
        return []
    tokens = []
    for part in content.split("{{")[1:]:
        if "}}" in part:
            token = part.split("}}")[0].strip()
            tokens.append(token)
    return tokens


def copy_and_render(src_dir: Path, dst_dir: Path, globals_: dict) -> dict:
    """Copy tree, render tokens, rename __COMPANY_SLUG__ dirs."""
    result: dict = {"created": [], "preserved": [], "skipped": [], "errors": []}

    if not src_dir.is_dir():
        result["errors"].append(f"source directory not found: {src_dir}")
        return result

    # Preflight: scan all text files for unresolved tokens before creating anything.
    for src_path in sorted(src_dir.rglob("*")):
        if src_path.is_dir():
            continue
        rel_path = src_path.relative_to(src_dir)
        if rel_path.parts and rel_path.parts[0] in ("bootstrap-state.json", "bootstrap-result.json"):
            continue
        try:
            raw = src_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rendered = render_content(raw, globals_)
        unresolved = check_unresolved(rendered, str(rel_path))
        if unresolved:
            result["errors"].append(
                f"preflight: unresolved tokens in template {rel_path}: {unresolved}"
            )
    if result["errors"]:
        return result

    for src_path in sorted(src_dir.rglob("*")):
        rel_path = src_path.relative_to(src_dir)

        # Skip bootstrap-state/result in repo template
        if rel_path.parts and rel_path.parts[0] in ("bootstrap-state.json", "bootstrap-result.json"):
            continue

        # Apply company slug rename
        parts = list(rel_path.parts)
        new_parts = []
        for p in parts:
            if "__COMPANY_SLUG__" in p:
                slug = globals_.get("COMPANY_SLUG", "")
                if not slug:
                    result["errors"].append(f"cannot rename __COMPANY_SLUG__ in {rel_path}: COMPANY_SLUG is empty")
                    continue
                new_parts.append(p.replace("__COMPANY_SLUG__", slug))
            else:
                new_parts.append(p)
        dst_rel = Path(*new_parts)
        dst_path = dst_dir / dst_rel

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            continue

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            raw = src_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Binary — copy as-is
            if not dst_path.exists():
                shutil.copy2(src_path, dst_path)
                result["created"].append(str(dst_rel))
            else:
                result["preserved"].append(str(dst_rel))
            continue

        rendered = render_content(raw, globals_)

        if dst_path.exists():
            existing = dst_path.read_text(encoding="utf-8")
            if existing == rendered:
                result["skipped"].append(str(dst_rel))
            else:
                result["preserved"].append(str(dst_rel))
        else:
            dst_path.write_text(rendered, encoding="utf-8")
            result["created"].append(str(dst_rel))

    # Ensure precheck executable if present
    for precheck in dst_dir.rglob("precheck.sh"):
        precheck.chmod(precheck.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # Check unresolved tokens in created files
    for rel in result["created"]:
        dst_path = dst_dir / rel
        try:
            content = dst_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        unresolved = check_unresolved(content, str(rel))
        if unresolved:
            result["errors"].append(f"unresolved tokens in {rel}: {unresolved}")

    return result


def cmd_base(state: dict) -> int:
    """Instantiate company Jarvis repo from templates/company-jarvis/repo/."""
    globals_ = extract_globals(state)
    paths = state.get("paths", {})
    target = Path(paths.get("jarvis_target_home", ""))
    if not target or str(target) == ".":
        print("ERROR: paths.jarvis_target_home is missing or invalid", file=sys.stderr)
        return 1

    if not globals_.get("COMPANY_SLUG"):
        print("ERROR: COMPANY_SLUG is empty — cannot render company-jarvis templates", file=sys.stderr)
        return 1

    print(f"base: target={target}, slug={globals_['COMPANY_SLUG']}")
    result = copy_and_render(COMPANY_JARVIS_REPO, target, globals_)

    print(f"created: {len(result['created'])}")
    for f in sorted(result["created"]):
        print(f"  + {f}")
    print(f"preserved (user edited): {len(result['preserved'])}")
    for f in sorted(result["preserved"]):
        print(f"  ~ {f}")
    print(f"skipped (identical): {len(result['skipped'])}")
    for f in sorted(result["skipped"]):
        print(f"  = {f}")

    if result["errors"]:
        print(f"ERRORS:")
        for e in result["errors"]:
            print(f"  ! {e}")
        return 1
    return 0


def cmd_module(state: dict, name: str) -> int:
    """Instantiate a single module contract from templates/company-jarvis/module/."""
    globals_ = extract_globals(state)
    paths = state.get("paths", {})
    target = Path(paths.get("jarvis_target_home", ""))
    if not target or str(target) == ".":
        print("ERROR: paths.jarvis_target_home is missing", file=sys.stderr)
        return 1

    name = validate_name(name, "module name")
    module_dir = target / "modules" / name

    globals_["MODULE_NAME"] = name

    if not COMPANY_JARVIS_MODULE.is_dir():
        print(f"ERROR: module template directory not found: {COMPANY_JARVIS_MODULE}", file=sys.stderr)
        return 1

    result = copy_and_render(COMPANY_JARVIS_MODULE, module_dir, globals_)

    print(f"module: {name}")
    print(f"created: {len(result['created'])}")
    for f in sorted(result["created"]):
        print(f"  + {f}")
    print(f"preserved: {len(result['preserved'])}")
    for f in sorted(result["preserved"]):
        print(f"  ~ {f}")
    print(f"skipped: {len(result['skipped'])}")

    if result["errors"]:
        for e in result["errors"]:
            print(f"  ! {e}")
        return 1
    return 0


def cmd_source(state: dict, name: str) -> int:
    """Instantiate a source route entry from templates/company-jarvis/source/ (README.md only, no SKILL.md)."""
    globals_ = extract_globals(state)
    paths = state.get("paths", {})
    target = Path(paths.get("jarvis_target_home", ""))
    if not target or str(target) == ".":
        print("ERROR: paths.jarvis_target_home is missing", file=sys.stderr)
        return 1

    name = validate_name(name, "source name")
    src_template = COMPANY_JARVIS_SOURCE

    if not src_template.is_dir():
        print(f"ERROR: source route template not found: {src_template}", file=sys.stderr)
        return 1

    globals_["SOURCE_NAME"] = name
    source_dir = target / "sources" / name

    result = copy_and_render(src_template, source_dir, globals_)

    print(f"source: {name}")
    print(f"created: {len(result['created'])}")
    for f in sorted(result["created"]):
        print(f"  + {f}")
    print(f"preserved: {len(result['preserved'])}")
    for f in sorted(result["preserved"]):
        print(f"  ~ {f}")
    print(f"skipped: {len(result['skipped'])}")

    if result["errors"]:
        for e in result["errors"]:
            print(f"  ! {e}")
        return 1
    return 0


def cmd_package(state: dict, kind: str, name: str) -> int:
    """Instantiate a skill package from templates/skill-packages/<kind>/."""
    globals_ = extract_globals(state)
    paths = state.get("paths", {})
    target = Path(paths.get("jarvis_target_home", ""))
    if not target or str(target) == ".":
        print("ERROR: paths.jarvis_target_home is missing", file=sys.stderr)
        return 1

    kind = validate_name(kind, "package kind")
    name = validate_name(name, "package name")

    valid_kinds = set()
    if SKILL_PACKAGES.is_dir():
        valid_kinds = {d.name for d in SKILL_PACKAGES.iterdir() if d.is_dir()}

    # generic-source is a valid Phase 9 source-helper skill package kind
    pkg_template = SKILL_PACKAGES / kind
    if not pkg_template.is_dir():
        print(f"ERROR: unknown package kind: {kind}", file=sys.stderr)
        if valid_kinds:
            print(f"valid kinds: {', '.join(sorted(valid_kinds))}", file=sys.stderr)
        return 1

    globals_["SKILL_NAME"] = name
    if kind == "generic-source":
        globals_["SOURCE_NAME"] = name
    pkg_dir = target / "skills" / name

    result = copy_and_render(pkg_template, pkg_dir, globals_)

    print(f"package: kind={kind}, name={name}")
    print(f"created: {len(result['created'])}")
    for f in sorted(result["created"]):
        print(f"  + {f}")
    print(f"preserved: {len(result['preserved'])}")
    for f in sorted(result["preserved"]):
        print(f"  ~ {f}")
    print(f"skipped: {len(result['skipped'])}")

    if result["errors"]:
        for e in result["errors"]:
            print(f"  ! {e}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic company Jarvis template instantiator."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_base = sub.add_parser("base", help="Instantiate company Jarvis repo base")
    p_base.add_argument("--state", required=True, help="Path to bootstrap-state.json")

    p_module = sub.add_parser("module", help="Instantiate a single module contract")
    p_module.add_argument("--state", required=True)
    p_module.add_argument("--name", required=True, help="Exact confirmed module name")

    p_source = sub.add_parser("source", help="Instantiate a source entry")
    p_source.add_argument("--state", required=True)
    p_source.add_argument("--name", required=True, help="Exact confirmed source name")

    p_package = sub.add_parser("package", help="Instantiate a skill package")
    p_package.add_argument("--state", required=True)
    p_package.add_argument("--kind", required=True, help="Skill package kind (directory name under skill-packages/)")
    p_package.add_argument("--name", required=True, help="Exact confirmed output skill name")

    args = parser.parse_args()
    state = load_state(args.state)

    if args.command == "base":
        return cmd_base(state)
    elif args.command == "module":
        return cmd_module(state, args.name)
    elif args.command == "source":
        return cmd_source(state, args.name)
    elif args.command == "package":
        return cmd_package(state, args.kind, args.name)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
