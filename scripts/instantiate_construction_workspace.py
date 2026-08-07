#!/usr/bin/env python3
"""Create and extend a durable Construction Workspace.

The workspace uses Markdown as its only state surface. ``init`` creates one
new workspace from the pinned method checkout. ``add-repository`` adds one
independent repository work card. ``prepare-repository-learning`` creates the
single customer command that starts a clean top-level Codex writer.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_METHOD_FILES = (
    "SKILL.md",
    "playbooks/prompts/repository-learning.md",
    "templates/construction-workspace/BUILD-CONTEXT.md",
    "templates/construction-workspace/CONSTRUCTION-JOURNAL.md",
    "templates/construction-workspace/CONTINUE-JARVIS.md",
    "templates/repository-learning/START-REPOSITORY-LEARNING.md",
)
REPOSITORY_TEMPLATE = Path(
    "templates/construction-workspace/work/repositories/REPOSITORY-WORK-CARD.md"
)
REPOSITORY_START_TEMPLATE = Path(
    "templates/repository-learning/START-REPOSITORY-LEARNING.md"
)
GENERIC_REPOSITORY_CARD = Path("work/repositories/REPOSITORY-WORK-CARD.md")
TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
COMMIT_RE = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})\Z")
CARD_NAME_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?\Z")
FIELD_RE_TEMPLATE = r"(?m)^- {label}:\s*(.+?)\s*$"


class UserError(Exception):
    """A stable, user-actionable invocation error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def require_single_line(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise UserError(f"{label} is empty")
    if "\n" in value or "\r" in value or "\x00" in value:
        raise UserError(f"{label} must be one line and contain no NUL byte")
    return value


def validate_card_name(value: str) -> str:
    name = require_single_line(value, "repository name")
    if not CARD_NAME_RE.fullmatch(name) or name in {".", ".."}:
        raise UserError(
            "repository name must be a safe work-card name using letters, "
            "numbers, '.', '_' or '-'"
        )
    if name == "REPOSITORY-WORK-CARD":
        raise UserError("repository name is reserved for the method template")
    return name


def resolve_method_repository(value: str) -> Path:
    method = Path(value).expanduser().resolve()
    if not method.is_dir():
        raise UserError(f"method repository is not a directory: {method}")
    missing = [relative for relative in REQUIRED_METHOD_FILES if not (method / relative).is_file()]
    if missing:
        raise UserError(
            "method repository is missing required files: " + ", ".join(missing)
        )
    return method


def verify_method_checkout(method: Path, commit: str) -> None:
    resolved = subprocess.run(
        ["git", "-C", str(method), "rev-parse", "--verify", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if resolved.returncode != 0 or resolved.stdout.strip().lower() != commit:
        raise UserError(f"method commit is not available in the recorded checkout: {commit}")
    head = subprocess.run(
        ["git", "-C", str(method), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if head.returncode != 0 or head.stdout.strip().lower() != commit:
        observed = head.stdout.strip() or "unavailable"
        raise UserError(
            f"method checkout HEAD is {observed}; materialize the recorded commit {commit} first"
        )


def resolve_new_workspace(value: str) -> Path:
    raw = Path(value).expanduser()
    workspace = raw.resolve()
    if workspace in {Path(workspace.anchor), Path.home().resolve()}:
        raise UserError("workspace must not be a filesystem root or the user home")
    if workspace.exists() or workspace.is_symlink():
        raise UserError(
            f"workspace already exists; resume it instead of reinitializing: {workspace}"
        )
    return workspace


def resolve_existing_workspace(value: str) -> Path:
    workspace = Path(value).expanduser().resolve()
    if not workspace.is_dir() or workspace.is_symlink():
        raise UserError(f"Construction Workspace is missing or unsafe: {workspace}")
    return workspace


def render(content: str, values: dict[str, str], label: str) -> str:
    for key, value in values.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    unresolved = sorted(set(TOKEN_RE.findall(content)))
    if unresolved:
        raise UserError(
            f"unresolved template tokens in {label}: " + ", ".join(unresolved)
        )
    return content


def write_rendered_tree(template_root: Path, target: Path, values: dict[str, str]) -> None:
    for source in sorted(template_root.rglob("*")):
        relative = source.relative_to(template_root)
        if relative == GENERIC_REPOSITORY_CARD:
            continue
        if source.is_symlink():
            raise UserError(f"method template contains a symlink: {relative}")
        destination = target / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if not source.is_file():
            raise UserError(f"unsupported method template entry: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text(encoding="utf-8")
        destination.write_text(render(content, values, str(relative)), encoding="utf-8")


def init_workspace(args: argparse.Namespace) -> dict[str, object]:
    method = resolve_method_repository(args.method_repository)
    method_commit = require_single_line(args.method_commit, "method commit").lower()
    if not COMMIT_RE.fullmatch(method_commit):
        raise UserError("method commit must be a full 40- or 64-character hexadecimal commit")
    verify_method_checkout(method, method_commit)
    workspace = resolve_new_workspace(args.workspace)
    coordinator = require_single_line(args.coordinator, "coordinator")
    created_at = require_single_line(args.created_at or utc_now(), "creation time")
    template_root = method / "templates" / "construction-workspace"

    values = {
        "CONSTRUCTION_WORKSPACE": str(workspace),
        "METHOD_REPOSITORY": str(method),
        "METHOD_COMMIT": method_commit,
        "COORDINATOR": coordinator,
        "CREATED_AT": created_at,
    }

    workspace.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{workspace.name}.staging-", dir=workspace.parent)
    )
    try:
        write_rendered_tree(template_root, staging, values)
        staging.rename(workspace)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return {
        "status": "created",
        "workspace": str(workspace),
        "method_repository": str(method),
        "method_commit": method_commit,
        "next": "Execute the intake in playbooks/prompts/preparation.md and fill BUILD-CONTEXT.md",
    }


def read_recorded_method(workspace: Path) -> tuple[Path, str]:
    continuation = workspace / "CONTINUE-JARVIS.md"
    if not continuation.is_file():
        raise UserError(f"required recovery file is missing: {continuation}")
    prefix = "- Method repository: `"
    values = [
        line[len(prefix) : -1]
        for line in continuation.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix) and line.endswith("`")
    ]
    if len(values) != 1:
        raise UserError("CONTINUE-JARVIS.md must record exactly one method repository")
    commit_prefix = "- Method commit: `"
    commits = [
        line[len(commit_prefix) : -1].lower()
        for line in continuation.read_text(encoding="utf-8").splitlines()
        if line.startswith(commit_prefix) and line.endswith("`")
    ]
    if len(commits) != 1 or not COMMIT_RE.fullmatch(commits[0]):
        raise UserError("CONTINUE-JARVIS.md must record exactly one full method commit")
    method = resolve_method_repository(values[0])
    verify_method_checkout(method, commits[0])
    return method, commits[0]


def insert_before_marker(content: str, marker: str, row: str, label: str) -> str:
    if content.count(marker) != 1:
        raise UserError(f"{label} must contain exactly one {marker} marker")
    return content.replace(marker, f"{row}\n{marker}")


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|")


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise UserError(f"refusing to replace unexpected temporary file: {temporary}")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists() or temporary.is_symlink():
            temporary.unlink()


def field_value(content: str, label: str) -> str:
    matches = re.findall(FIELD_RE_TEMPLATE.format(label=re.escape(label)), content)
    if len(matches) != 1:
        raise UserError(f"work card must contain exactly one '{label}' field")
    return matches[0].strip().strip("`")


def replace_field(content: str, label: str, value: str) -> str:
    pattern = FIELD_RE_TEMPLATE.format(label=re.escape(label))
    if len(re.findall(pattern, content)) != 1:
        raise UserError(f"work card must contain exactly one '{label}' field")
    return re.sub(pattern, f"- {label}: `{value}`", content)


def add_repository(args: argparse.Namespace) -> dict[str, object]:
    workspace = resolve_existing_workspace(args.workspace)
    name = validate_card_name(args.name)
    pointer = require_single_line(args.repository, "repository pointer")
    history_range = require_single_line(args.history_range, "history range")
    delivery_policy = require_single_line(args.delivery_policy, "delivery policy")
    target_workspace = require_single_line(args.target_workspace, "target workspace")
    target_branch = require_single_line(args.target_branch, "target branch")
    added_at = require_single_line(args.added_at or utc_now(), "addition time")

    method, method_commit = read_recorded_method(workspace)
    template = method / REPOSITORY_TEMPLATE
    card_root = workspace / "work" / "repositories" / name
    card = card_root / "CARD.md"
    if card_root.exists() or card_root.is_symlink():
        raise UserError(f"repository work card directory already exists: {card_root}")

    values = {
        "REPOSITORY_NAME": name,
        "REPOSITORY_POINTER": pointer,
        "TARGET_WORKSPACE": target_workspace,
        "TARGET_BRANCH": target_branch,
        "HISTORY_RANGE": history_range,
        "DELIVERY_POLICY": delivery_policy,
        "METHOD_REPOSITORY": str(method),
        "METHOD_COMMIT": method_commit,
        "ADDED_AT": added_at,
    }
    card_content = render(template.read_text(encoding="utf-8"), values, str(template))

    build_context = workspace / "BUILD-CONTEXT.md"
    journal = workspace / "CONSTRUCTION-JOURNAL.md"
    if not build_context.is_file() or not journal.is_file():
        raise UserError("workspace is missing BUILD-CONTEXT.md or CONSTRUCTION-JOURNAL.md")
    build_original = build_context.read_text(encoding="utf-8")
    journal_original = journal.read_text(encoding="utf-8")
    inventory_row = "| " + " | ".join(
        markdown_cell(value)
        for value in (
            name,
            pointer,
            "unresolved",
            history_range,
            delivery_policy,
            "unresolved",
            "unresolved",
        )
    ) + " |"
    journal_row = (
        f"| `work/repositories/{name}/CARD.md` | waiting-for-part-1 | unassigned | "
        "none | wait for Part 1 delivery |"
    )
    build_updated = insert_before_marker(
        build_original,
        "<!-- REPOSITORY-INVENTORY:END -->",
        inventory_row,
        "BUILD-CONTEXT.md",
    )
    journal_updated = insert_before_marker(
        journal_original,
        "<!-- REPOSITORY-WORK-INDEX:END -->",
        journal_row,
        "CONSTRUCTION-JOURNAL.md",
    )

    card_root.mkdir(parents=True, exist_ok=False)
    try:
        atomic_write(build_context, build_updated)
        atomic_write(journal, journal_updated)
        atomic_write(card, card_content)
    except Exception:
        atomic_write(build_context, build_original)
        atomic_write(journal, journal_original)
        if card_root.exists():
            shutil.rmtree(card_root)
        raise

    return {
        "status": "repository-card-added",
        "workspace": str(workspace),
        "repository": name,
        "card": str(card),
    }


def replace_repository_journal_row(
    content: str,
    name: str,
    *,
    status: str,
    writer: str,
    checkpoint: str,
    next_action: str,
) -> str:
    prefix = f"| `work/repositories/{name}/CARD.md` |"
    rows = [line for line in content.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise UserError(f"journal must contain exactly one repository row for {name}")
    replacement = (
        f"{prefix} {status} | {writer} | {checkpoint} | {next_action} |"
    )
    return content.replace(rows[0], replacement)


def prepare_repository_learning(args: argparse.Namespace) -> dict[str, object]:
    workspace = resolve_existing_workspace(args.workspace)
    name = validate_card_name(args.name)
    method, method_commit = read_recorded_method(workspace)
    card_root = workspace / "work" / "repositories" / name
    card = card_root / "CARD.md"
    if not card.is_file() or card.is_symlink():
        raise UserError(f"repository work card is missing or unsafe: {card}")

    original = card.read_text(encoding="utf-8")
    if field_value(original, "Execution mode") != "user-launched-top-level-codex":
        raise UserError("repository card does not require a user-launched top-level Codex")
    if field_value(original, "Scope lock") != (
        "exactly one repository; primary writer multi-agent tools disabled"
    ):
        raise UserError("repository card scope lock is missing or changed")
    if field_value(original, "Method repository") != str(method):
        raise UserError("repository card method repository differs from CONTINUE-JARVIS.md")
    if field_value(original, "Method commit").lower() != method_commit:
        raise UserError("repository card method commit differs from CONTINUE-JARVIS.md")

    status = field_value(original, "Status")
    writer = field_value(original, "Writer")
    blocker = field_value(original, "Blocker")
    if status not in {"ready", "ready-for-user-launch"}:
        raise UserError(
            "repository card must be ready before handoff; verify Part 1 and set Status to ready"
        )
    if writer != "unassigned":
        raise UserError(f"repository card already has a writer: {writer}")
    if blocker.lower() != "none":
        raise UserError(f"repository card still has a blocker: {blocker}")

    target_repository = field_value(original, "Target repository")
    target_branch = field_value(original, "Target branch")
    history_range = field_value(original, "History range")
    delivery_policy = field_value(original, "Delivery policy")
    for label, value in (
        ("Target repository", target_repository),
        ("Target branch", target_branch),
        ("History range", history_range),
        ("Delivery policy", delivery_policy),
    ):
        if value.lower() in {"none", "unresolved"}:
            raise UserError(f"repository card field '{label}' must be resolved before handoff")

    target_workspace = Path(field_value(original, "Target workspace")).expanduser().resolve()
    if not target_workspace.is_dir() or target_workspace.is_symlink():
        raise UserError(f"target repository workspace is missing or unsafe: {target_workspace}")
    repository_root = subprocess.run(
        ["git", "-C", str(target_workspace), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if (
        repository_root.returncode != 0
        or Path(repository_root.stdout.strip()).resolve() != target_workspace
    ):
        raise UserError(
            f"target workspace must be the root of a Git worktree: {target_workspace}"
        )
    start = card_root / "START-REPOSITORY-LEARNING.md"

    launch_prompt = (
        f"读取 {start}，只执行其中指定的 {name} Repository Learning；"
        "完成后按启动文件的返回指引停止。"
    )
    launch_command = shlex.join(
        [
            require_single_line(args.codex_command, "Codex command"),
            "-C",
            str(target_workspace),
            "--add-dir",
            str(card_root),
            "--sandbox",
            "workspace-write",
            "--ask-for-approval",
            "on-request",
            "-c",
            "agents.enabled=false",
            launch_prompt,
        ]
    )

    if start.is_symlink():
        raise UserError(f"refusing unsafe handoff entry: {start}")
    if start.is_file() and status == "ready-for-user-launch":
        if field_value(original, "Handoff entry") != str(start):
            raise UserError("existing repository handoff pointer does not match its start file")
        return {
            "status": "ready-for-user-launch",
            "repository": name,
            "card": str(card),
            "start": str(start),
            "launch_command": launch_command,
            "return_instruction": "完成后回到原 create-jarvis 会话回复：继续",
        }
    if start.exists():
        raise UserError(f"refusing to overwrite unexpected handoff entry: {start}")

    template = method / REPOSITORY_START_TEMPLATE
    if not template.is_file() or template.is_symlink():
        raise UserError(f"method repository is missing the handoff template: {template}")
    prepared_at = require_single_line(args.prepared_at or utc_now(), "preparation time")
    start_content = render(
        template.read_text(encoding="utf-8"),
        {
            "REPOSITORY_NAME": name,
            "CONSTRUCTION_WORKSPACE": str(workspace),
            "BUILD_CONTEXT": str(workspace / "BUILD-CONTEXT.md"),
            "CARD_PATH": str(card),
            "METHOD_REPOSITORY": str(method),
            "METHOD_COMMIT": method_commit,
            "TARGET_REPOSITORY": target_repository,
            "TARGET_WORKSPACE": str(target_workspace),
            "TARGET_BRANCH": target_branch,
            "HISTORY_RANGE": history_range,
            "DELIVERY_POLICY": delivery_policy,
            "PREPARED_AT": prepared_at,
        },
        str(template),
    )
    updated = replace_field(original, "Handoff entry", str(start))
    updated = replace_field(updated, "Status", "ready-for-user-launch")
    updated = replace_field(updated, "Last verified checkpoint", "clean-process handoff generated")
    updated = replace_field(updated, "Next", "customer runs the generated Codex command")
    updated = replace_field(updated, "Last verified", prepared_at)

    journal = workspace / "CONSTRUCTION-JOURNAL.md"
    if not journal.is_file() or journal.is_symlink():
        raise UserError(f"construction journal is missing or unsafe: {journal}")
    journal_original = journal.read_text(encoding="utf-8")
    journal_updated = replace_repository_journal_row(
        journal_original,
        name,
        status="ready-for-user-launch",
        writer="unassigned",
        checkpoint="clean-process handoff generated",
        next_action="customer runs printed Codex command",
    )
    try:
        atomic_write(start, start_content)
        atomic_write(card, updated)
        atomic_write(journal, journal_updated)
    except Exception:
        atomic_write(card, original)
        atomic_write(journal, journal_original)
        if start.exists():
            start.unlink()
        raise

    return {
        "status": "ready-for-user-launch",
        "repository": name,
        "card": str(card),
        "start": str(start),
        "launch_command": launch_command,
        "return_instruction": "完成后回到原 create-jarvis 会话回复：继续",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create a new Construction Workspace")
    init.add_argument("--workspace", required=True)
    init.add_argument("--method-repository", required=True)
    init.add_argument("--method-commit", required=True)
    init.add_argument("--coordinator", default="customer-authorized Host Agent")
    init.add_argument("--created-at", help=argparse.SUPPRESS)
    init.set_defaults(handler=init_workspace)

    add_repo = subparsers.add_parser(
        "add-repository", help="add one independent repository work card"
    )
    add_repo.add_argument("--workspace", required=True)
    add_repo.add_argument("--name", required=True)
    add_repo.add_argument("--repository", required=True)
    add_repo.add_argument("--history-range", default="preceding 12 months")
    add_repo.add_argument("--delivery-policy", default="unresolved")
    add_repo.add_argument("--target-workspace", default="unresolved")
    add_repo.add_argument("--target-branch", default="unresolved")
    add_repo.add_argument("--added-at", help=argparse.SUPPRESS)
    add_repo.set_defaults(handler=add_repository)

    prepare_repo = subparsers.add_parser(
        "prepare-repository-learning",
        help="prepare one customer-launched top-level Codex repository writer",
    )
    prepare_repo.add_argument("--workspace", required=True)
    prepare_repo.add_argument("--name", required=True)
    prepare_repo.add_argument("--codex-command", default="codex")
    prepare_repo.add_argument("--prepared-at", help=argparse.SUPPRESS)
    prepare_repo.set_defaults(handler=prepare_repository_learning)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = args.handler(args)
    except (OSError, UnicodeError, UserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
