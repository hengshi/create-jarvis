#!/usr/bin/env python3
"""Deterministic instantiator for company Jarvis templates.

Subcommands:
    base    --input <company render input JSON>
    module  --input <...> --name <confirmed exact name>
    source  --input <...> --name <confirmed exact name>  (creates sources/<name>/README.md only)
    package --input <...> --kind <generic-source|generic-workflow>
            --name <slot-prefixed output name>

The base command installs only company-owned entry/workflow skills and the
cross-runtime governance scaffold. Generic method skills and jarvis-box
internals must not be copied into a customer repo. Construction work cards
stay outside the generated repo in ordinary Markdown.
"""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
from pathlib import Path
from urllib.parse import urlparse


TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "templates"
COMPANY_JARVIS_REPO = TEMPLATES_ROOT / "company-jarvis" / "repo"
COMPANY_JARVIS_MODULE = TEMPLATES_ROOT / "company-jarvis" / "module"
COMPANY_JARVIS_SOURCE = TEMPLATES_ROOT / "company-jarvis" / "source"
SKILL_PACKAGES = TEMPLATES_ROOT / "skill-packages"

STARTER_WORKFLOW_PACKAGES = (
    ("issue-post-check", "issue-post-check"),
    ("bugfix-loop", "bugfix-loop"),
    ("feature-delivery", "feature-delivery"),
)
EXTENSION_PACKAGE_KINDS = frozenset({"generic-source", "generic-workflow"})

def company_workflow_name(company_slug: str, workflow_name: str) -> str:
    """Return the canonical company-owned workflow skill name."""
    prefix = f"{company_slug}-workflow-"
    if workflow_name.startswith(prefix):
        return workflow_name
    return f"{prefix}{workflow_name}"


def load_input(input_path: str) -> dict:
    path = Path(input_path)
    if not path.is_file():
        print(f"ERROR: render input not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in render input: {exc}", file=sys.stderr)
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


def require_string(value: object, label: str, *, allow_empty: bool = False) -> str:
    """Return a string field or fail with a stable diagnostic instead of a traceback."""
    if not isinstance(value, str):
        print(f"ERROR: {label} must be a string", file=sys.stderr)
        sys.exit(1)
    if not allow_empty and not value.strip():
        print(f"ERROR: {label} is empty", file=sys.stderr)
        sys.exit(1)
    return value


def extract_globals(input_data: dict) -> dict:
    """Extract confirmed template values from a small render input."""
    company = input_data.get("company")
    if not isinstance(company, dict):
        print("ERROR: company is missing or not an object", file=sys.stderr)
        sys.exit(1)

    company_name = require_string(
        company.get("name", ""),
        "COMPANY_NAME — company.name",
    )
    company_slug = require_string(
        company.get("slug", ""),
        "COMPANY_SLUG — company.slug",
    )
    company_slug = validate_name(company_slug, "company slug")

    product_identity_value = company.get("product_identity", "")
    if not isinstance(product_identity_value, str):
        print(
            "ERROR: PRODUCT_IDENTITY — company.product_identity must be a string",
            file=sys.stderr,
        )
        sys.exit(1)
    product_identity = product_identity_value.strip() or (
        "UNRESOLVED — establish from customer evidence"
    )

    scope = input_data.get("scope")
    if not isinstance(scope, dict):
        scope = {}

    # Normalize optional scope hints into clean deduplicated lists.
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

    module_hints = _parse_csv(scope.get("modules", []))
    source_scope = _parse_csv(scope.get("sources", []))
    repo_scope = _parse_csv(scope.get("repositories", []))

    def _bullet_index(items: list[str], fmt: str) -> str:
        """Generate a durable scope list without leaving a construction sentinel."""
        if not items:
            return "- none-yet (populate from observed evidence)"
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
            return "- none-yet (populate from observed repository evidence)"
        return "\n".join(
            f"- `{_repo_basename(project)}` — VCS project `{project}`; "
            "repo-local entry unresolved until observed; use `pending repo-local entry` when absent"
            for project in items
        )

    # COMPANY_OWNER: accept string or list; missing -> UNRESOLVED
    company_owner = company.get("owner", "")
    if isinstance(company_owner, list):
        company_owner = ", ".join(company_owner)
    if not isinstance(company_owner, str) or not company_owner.strip():
        company_owner = "UNRESOLVED"

    starter_workflows = [
        company_workflow_name(company_slug, suffix)
        for _, suffix in STARTER_WORKFLOW_PACKAGES
    ]
    workflow_index = []
    seen_workflows = set()
    for workflow in starter_workflows:
        if workflow not in seen_workflows:
            seen_workflows.add(workflow)
            workflow_index.append(workflow)

    globals_ = {
        "COMPANY_NAME": company_name,
        "COMPANY_SLUG": company_slug,
        "COMPANY_JARVIS_NAME": f"{company_slug}-jarvis",
        "PRODUCT_IDENTITY": product_identity,
        "COMPANY_OWNER": company_owner,
        "MODULE_INDEX": _bullet_index(module_hints, "modules/{}/overview.md"),
        "SOURCE_INDEX": _bullet_index(source_scope, "sources/{}/README.md"),
        "WORKFLOW_INDEX": _bullet_index(workflow_index, "skills/{}/SKILL.md"),
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


def refresh_readme_scope_indexes(
    target: Path,
    *,
    include_workflows: bool = False,
    company_slug: str = "",
) -> None:
    """Fill the initial README scope placeholders from rendered directories.

    ``base`` can run before deep discovery, so the render input may have no
    module/source/workflow hints. Later deterministic instantiation commands
    must still keep the durable company entry synchronized without overwriting
    an agent or owner edit.
    """
    readme = target / "README.md"
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8")

    sections = [
        ("模块", "数据源", target / "modules", "modules/{}/overview.md"),
        ("数据源", "工作流", target / "sources", "sources/{}/README.md"),
    ]
    if include_workflows:
        sections.append(("工作流", "仓库", target / "skills", "skills/{}/SKILL.md"))
    for heading, next_heading, directory, item_format in sections:
        start_marker = f"### {heading}"
        end_marker = f"### {next_heading}"
        start = text.find(start_marker)
        if start < 0:
            continue
        content_start = start + len(start_marker)
        end = text.find(end_marker, content_start)
        if end < 0:
            continue
        current = text[content_start:end]
        names = sorted(p.name for p in directory.iterdir() if p.is_dir()) if directory.is_dir() else []
        if heading == "工作流":
            prefix = f"{company_slug}-workflow-"
            names = [name for name in names if company_slug and name.startswith(prefix)]
            if "UNRESOLVED" not in current and not current.strip().startswith("- none-yet"):
                missing = [
                    name for name in names
                    if item_format.format(name) not in current
                ]
                if missing:
                    addition = "".join(
                        f"- {item_format.format(name)}\n" for name in missing
                    )
                    replacement = current.rstrip() + "\n" + addition + "\n"
                    text = text[:content_start] + replacement + text[end:]
                continue
        elif "UNRESOLVED" not in current and not current.strip().startswith("- none-yet"):
            continue
        replacement = "\n\n" + (
            "- none-yet (populate from observed evidence)"
            if not names
            else "\n".join(f"- {item_format.format(name)}" for name in names)
        ) + "\n\n"
        text = text[:content_start] + replacement + text[end:]

    readme.write_text(text, encoding="utf-8")


def merge_copy_results(target: dict, source: dict) -> None:
    """Merge a copy_and_render result into an aggregate result."""
    for key in ("created", "preserved", "skipped", "errors"):
        target[key].extend(source.get(key, []))


def copy_skill_package(
    target: Path,
    globals_: dict,
    *,
    kind: str,
    name: str,
) -> dict:
    """Render one known skill package into the company Jarvis repo."""
    package_globals = dict(globals_)
    package_globals["SKILL_NAME"] = name
    if kind == "generic-source":
        company_prefix = f"{globals_['COMPANY_SLUG']}-"
        package_globals["SOURCE_NAME"] = name.removeprefix(company_prefix)
    result = copy_and_render(
        SKILL_PACKAGES / kind,
        target / "skills" / name,
        package_globals,
    )
    prefix = Path("skills") / name
    for key in ("created", "preserved", "skipped"):
        result[key] = [str(prefix / rel) for rel in result[key]]
    return result


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

    # Runtime Foundation jobs are generated source artifacts, not prose-only
    # examples. Keep their executable contract after rendering and re-renders.
    runtime_bin = dst_dir / "runtime-foundation" / "bin"
    if runtime_bin.is_dir():
        for executable in runtime_bin.iterdir():
            if executable.is_file():
                executable.chmod(
                    executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
    runtime_manager = dst_dir / "runtime-foundation" / "manage.py"
    if runtime_manager.is_file():
        runtime_manager.chmod(
            runtime_manager.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

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


def _resolve_agent_target(target_path: str, workspace_root: str) -> tuple[Path, Path]:
    """Resolve a strict child target inside the runtime-declared agent workspace."""
    workspace = Path(workspace_root).expanduser().resolve(strict=True)
    if not workspace.is_dir():
        print(f"ERROR: workspace root is not a directory: {workspace}", file=sys.stderr)
        sys.exit(1)
    target = Path(target_path).expanduser().resolve(strict=False)
    try:
        relative = target.relative_to(workspace)
    except ValueError:
        print(
            f"ERROR: company target must be inside the agent workspace: {target} not under {workspace}",
            file=sys.stderr,
        )
        sys.exit(1)
    if relative == Path("."):
        print("ERROR: company target must be a child of the workspace root", file=sys.stderr)
        sys.exit(1)
    return target, workspace


def _resolve_input_target(input_data: dict) -> tuple[Path, Path]:
    """Resolve and revalidate the write target for every render command."""
    paths = input_data.get("paths")
    if not isinstance(paths, dict):
        print("ERROR: paths is missing or not an object", file=sys.stderr)
        sys.exit(1)

    target_value = require_string(paths.get("target", ""), "paths.target")
    workspace_value = require_string(
        paths.get("workspace_root", ""),
        "paths.workspace_root",
    )
    target, workspace = _resolve_agent_target(target_value, workspace_value)

    return target, workspace


def cmd_base(input_data: dict) -> int:
    """Instantiate company Jarvis repo from templates/company-jarvis/repo/."""
    globals_ = extract_globals(input_data)
    target, _ = _resolve_input_target(input_data)

    if not globals_.get("COMPANY_SLUG"):
        print("ERROR: COMPANY_SLUG is empty — cannot render company-jarvis templates", file=sys.stderr)
        return 1

    print(f"base: target={target}, slug={globals_['COMPANY_SLUG']}")
    result = copy_and_render(COMPANY_JARVIS_REPO, target, globals_)
    for kind, suffix in STARTER_WORKFLOW_PACKAGES:
        name = company_workflow_name(globals_["COMPANY_SLUG"], suffix)
        merge_copy_results(
            result,
            copy_skill_package(target, globals_, kind=kind, name=name),
        )
    refresh_readme_scope_indexes(
        target,
        include_workflows=True,
        company_slug=globals_["COMPANY_SLUG"],
    )

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


def cmd_module(input_data: dict, name: str) -> int:
    """Instantiate a single module contract from templates/company-jarvis/module/."""
    globals_ = extract_globals(input_data)
    target, _ = _resolve_input_target(input_data)

    name = validate_name(name, "module name")
    module_dir = target / "modules" / name

    globals_["MODULE_NAME"] = name

    if not COMPANY_JARVIS_MODULE.is_dir():
        print(f"ERROR: module template directory not found: {COMPANY_JARVIS_MODULE}", file=sys.stderr)
        return 1

    result = copy_and_render(COMPANY_JARVIS_MODULE, module_dir, globals_)
    refresh_readme_scope_indexes(target)

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


def cmd_source(input_data: dict, name: str) -> int:
    """Instantiate a source route entry from templates/company-jarvis/source/ (README.md only, no SKILL.md)."""
    globals_ = extract_globals(input_data)
    target, _ = _resolve_input_target(input_data)

    name = validate_name(name, "source name")
    src_template = COMPANY_JARVIS_SOURCE

    if not src_template.is_dir():
        print(f"ERROR: source route template not found: {src_template}", file=sys.stderr)
        return 1

    globals_["SOURCE_NAME"] = name
    source_dir = target / "sources" / name

    result = copy_and_render(src_template, source_dir, globals_)
    refresh_readme_scope_indexes(target)

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


def cmd_package(input_data: dict, kind: str, name: str) -> int:
    """Instantiate a skill package from templates/skill-packages/<kind>/."""
    globals_ = extract_globals(input_data)
    target, _ = _resolve_input_target(input_data)

    kind = validate_name(kind, "package kind")
    name = validate_name(name, "package name")

    valid_kinds = EXTENSION_PACKAGE_KINDS
    if kind not in valid_kinds:
        print(f"ERROR: package kind is not an extension kind: {kind}", file=sys.stderr)
        print(f"valid kinds: {', '.join(sorted(valid_kinds))}", file=sys.stderr)
        return 1

    pkg_template = SKILL_PACKAGES / kind
    if not pkg_template.is_dir():
        print(f"ERROR: unknown package kind: {kind}", file=sys.stderr)
        return 1

    company_slug = globals_["COMPANY_SLUG"]
    if kind == "generic-workflow":
        expected_prefix = f"{company_slug}-workflow-"
    else:
        expected_prefix = f"{company_slug}-"
    if not name.startswith(expected_prefix) or name == expected_prefix:
        print(
            f"ERROR: {kind} output name must start with {expected_prefix!r} "
            f"and include a name: {name!r}",
            file=sys.stderr,
        )
        return 1
    if kind == "generic-source" and (
        name == f"{company_slug}-jarvis"
        or name.startswith(f"{company_slug}-workflow-")
    ):
        print(
            f"ERROR: generic-source output name collides with a reserved company skill: {name!r}",
            file=sys.stderr,
        )
        return 1

    result = copy_skill_package(target, globals_, kind=kind, name=name)
    refresh_readme_scope_indexes(
        target,
        include_workflows=kind == "generic-workflow",
        company_slug=company_slug,
    )

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
    p_base.add_argument("--input", required=True, help="Path to company render input JSON")

    p_module = sub.add_parser("module", help="Instantiate a single module contract")
    p_module.add_argument("--input", required=True)
    p_module.add_argument("--name", required=True, help="Exact confirmed module name")

    p_source = sub.add_parser("source", help="Instantiate a source entry")
    p_source.add_argument("--input", required=True)
    p_source.add_argument("--name", required=True, help="Exact confirmed source name")

    p_package = sub.add_parser("package", help="Instantiate a skill package")
    p_package.add_argument("--input", required=True)
    p_package.add_argument(
        "--kind",
        required=True,
        choices=sorted(EXTENSION_PACKAGE_KINDS),
        help="Additional customer-derived package kind",
    )
    p_package.add_argument(
        "--name",
        required=True,
        help="Canonical slot-prefixed output skill name",
    )

    args = parser.parse_args()
    input_data = load_input(args.input)

    if args.command == "base":
        return cmd_base(input_data)
    elif args.command == "module":
        return cmd_module(input_data, args.name)
    elif args.command == "source":
        return cmd_source(input_data, args.name)
    elif args.command == "package":
        return cmd_package(input_data, args.kind, args.name)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
