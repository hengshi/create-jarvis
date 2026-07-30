#!/usr/bin/env python3
"""Programmatic artifact checks for the three customer-journey evals.

The checks are intentionally narrower than the expectations in evals.json.
They make filesystem/Git claims reproducible; a grader still reviews the
transcript and evidence quality for semantic expectations.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def command(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)


def field(path: Path, label: str) -> str | None:
    if not path.is_file():
        return None
    matches = re.findall(
        rf"(?m)^- {re.escape(label)}:\s*(.+?)\s*$",
        path.read_text(encoding="utf-8"),
    )
    return matches[0].strip().strip("`") if len(matches) == 1 else None


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, object]] = []

    def add(self, name: str, passed: bool, evidence: str) -> None:
        self.items.append({"name": name, "passed": bool(passed), "evidence": evidence})

    def run_json(self, name: str, args: list[str]) -> None:
        completed = command(args)
        evidence = (completed.stdout or completed.stderr).strip()
        self.add(name, completed.returncode == 0, evidence[-4000:])

    def report(self, case: str, root: Path) -> dict[str, object]:
        passed = sum(1 for item in self.items if item["passed"])
        total = len(self.items)
        return {
            "case": case,
            "fixture_root": str(root),
            "status": "pass" if passed == total else "fail",
            "summary": {"passed": passed, "failed": total - passed, "total": total},
            "checks": self.items,
        }


def common_checks(checks: Checks, root: Path, method: Path, *, dispatch: bool = False) -> None:
    workspace_args = [
        sys.executable,
        str(method / "scripts" / "verify_construction_workspace.py"),
        "--workspace",
        str(root / "jarvis-build"),
    ]
    if dispatch:
        workspace_args.append("--require-dispatch-ready")
    checks.run_json("Construction Workspace verifier passes", workspace_args)
    checks.run_json(
        "Company Jarvis verifier passes",
        [
            sys.executable,
            str(method / "scripts" / "verify_company_output.py"),
            "--jarvis-home",
            str(root / "workspaces" / "acme-labs-jarvis"),
            "--expected-company-slug",
            "acme-labs",
            "--skip-precheck",
        ],
    )


def remote_commit_count(remote: Path) -> int:
    completed = command(["git", "--git-dir", str(remote), "rev-list", "--all", "--count"])
    if completed.returncode != 0:
        return 0
    try:
        return int(completed.stdout.strip())
    except ValueError:
        return 0


def check_new(checks: Checks, root: Path, method: Path) -> None:
    common_checks(checks, root, method, dispatch=True)
    cards = sorted((root / "jarvis-build" / "work" / "repositories").glob("*.md"))
    checks.add(
        "Exactly two independent repository cards exist",
        [card.stem for card in cards] == ["fulfillment", "storefront"],
        repr([card.stem for card in cards]),
    )
    init_card = root / "jarvis-build" / "work" / "company-repo-initialization.md"
    checks.add(
        "Part 1 has a verified completed card",
        field(init_card, "Status") == "complete"
        and field(init_card, "Last verified checkpoint") not in {None, "none"}
        and field(init_card, "Delivered artifacts") not in {None, "none"},
        f"status={field(init_card, 'Status')!r}; checkpoint={field(init_card, 'Last verified checkpoint')!r}",
    )
    remote = root / "remotes" / "acme-labs-jarvis.git"
    checks.add(
        "Company remote contains a delivered commit",
        remote_commit_count(remote) >= 1,
        f"remote commit count={remote_commit_count(remote)}",
    )
    note = root / "customer-repos" / "fulfillment" / "CUSTOMER-NOTE.md"
    checks.add(
        "Pre-existing customer change is preserved",
        note.is_file() and "preserve this uncommitted note" in note.read_text(encoding="utf-8"),
        str(note),
    )


def check_runtime(checks: Checks, root: Path, method: Path, manifest: dict) -> None:
    common_checks(checks, root, method)
    card = root / "jarvis-build" / "work" / "company-construction.md"
    checks.add(
        "Part 2 card is completed with behavioral evidence",
        field(card, "Status") == "complete"
        and field(card, "Evidence") not in {None, "none"}
        and field(card, "Delivered artifacts") not in {None, "none"},
        f"status={field(card, 'Status')!r}; evidence={field(card, 'Evidence')!r}",
    )
    remote = Path(manifest["company_remote"])
    checks.add(
        "Company runtime-governance result is published after the scaffold commit",
        remote_commit_count(remote) >= 2,
        f"remote commit count={remote_commit_count(remote)}; initial={manifest['company_initial_commit']}",
    )
    runtime_root = Path(manifest["host_runtime"])
    entries = [path for path in (runtime_root / "bin").iterdir() if path.is_file()]
    executable = [path for path in entries if os.access(path, os.X_OK)]
    checks.add(
        "Authorized Host runtime foundation contains a stable executable sync entry",
        bool(executable),
        repr([str(path) for path in executable]),
    )
    git_caches = [path for path in (runtime_root / "cache").rglob(".git") if path.is_dir()]
    checks.add(
        "Behavioral sync materialized both canonical Git sources",
        len(git_caches) >= 2,
        repr([str(path.parent) for path in git_caches]),
    )
    governance = root / "workspaces" / "acme-labs-jarvis" / "references" / "runtime-governance.md"
    governance_text = governance.read_text(encoding="utf-8") if governance.is_file() else ""
    checks.add(
        "Runtime constitution records the authorized root and verified maturity",
        str(runtime_root) in governance_text and "verified" in governance_text,
        f"runtime root mentioned={str(runtime_root) in governance_text}; verified mentioned={'verified' in governance_text}",
    )
    jarvis_payload = [path for path in runtime_root.rglob("*") if "jarvis-box" in path.name.lower()]
    checks.add(
        "No jarvis-box payload was installed",
        not jarvis_payload,
        repr([str(path) for path in jarvis_payload]),
    )


def check_repository(checks: Checks, root: Path, method: Path, manifest: dict) -> None:
    common_checks(checks, root, method)
    repo = Path(manifest["repository"])
    repo_card = root / "jarvis-build" / "work" / "repositories" / "invoice-service.md"
    reconciliation = root / "jarvis-build" / "work" / "reconciliation.md"
    checks.add(
        "Repository learning and reconciliation cards are complete",
        field(repo_card, "Status") == "complete" and field(reconciliation, "Status") == "complete",
        f"repo={field(repo_card, 'Status')!r}; reconciliation={field(reconciliation, 'Status')!r}",
    )
    skill = repo / "skills" / "invoice-service" / "SKILL.md"
    skill_text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
    checks.add(
        "Repo-local skill captures concrete idempotency and proof routes",
        skill.is_file()
        and "idempot" in skill_text.lower()
        and "invoice_service/webhooks.py" in skill_text
        and "test" in skill_text.lower(),
        str(skill),
    )
    checks.add(
        "No legacy eval-loop skill was created",
        not (repo / "skills" / "eval-loop.md").exists(),
        str(repo / "skills" / "eval-loop.md"),
    )
    note = Path(manifest["dirty_file"])
    checks.add(
        "Uncommitted customer note is preserved",
        note.is_file() and "keep this uncommitted" in note.read_text(encoding="utf-8"),
        str(note),
    )
    remote = Path(manifest["repository_remote"])
    branch_probe = command(
        [
            "git",
            "--git-dir",
            str(remote),
            "show-ref",
            "--verify",
            "refs/heads/create-jarvis/repo-learning-invoice-service",
        ]
    )
    checks.add(
        "Repo-local delivery branch resolves at the customer remote",
        branch_probe.returncode == 0,
        (branch_probe.stdout or branch_probe.stderr).strip(),
    )
    company = Path(manifest["company"])
    module = company / "modules" / "billing" / "overview.md"
    module_text = module.read_text(encoding="utf-8") if module.is_file() else ""
    checks.add(
        "Company pending handoff resolves to the delivered repo-local entry",
        "pending repo-local entry" not in module_text
        and "skills/invoice-service/SKILL.md" in module_text,
        str(module),
    )
    workflow = company / "skills" / "acme-labs-workflow-bugfix-loop" / "SKILL.md"
    workflow_text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""
    checks.add(
        "Workflow advances only to construction-ready",
        bool(
            re.search(
                r"(?m)^\*\*当前状态：`construction-ready`\*\*$",
                workflow_text,
            )
        )
        and not re.search(r"(?m)^\*\*当前状态：`active`\*\*$", workflow_text),
        str(workflow),
    )
    fixed = manifest["history"]["fixed"]
    evidence_text = repo_card.read_text(encoding="utf-8") if repo_card.is_file() else ""
    checks.add(
        "Work-card evidence identifies the actual historical fix revision",
        fixed in evidence_text,
        f"expected revision={fixed}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        required=True,
        choices=("new-journey", "runtime-governance", "repository-reconciliation"),
    )
    parser.add_argument("--fixture-root", required=True, type=Path)
    parser.add_argument("--method-repository", required=True, type=Path)
    args = parser.parse_args()
    root = args.fixture_root.expanduser().resolve()
    method = args.method_repository.expanduser().resolve()
    manifest_path = root / "fixture-manifest.json"
    if not manifest_path.is_file():
        print(f"ERROR: fixture manifest is missing: {manifest_path}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = Checks()
    if args.case == "new-journey":
        check_new(checks, root, method)
    elif args.case == "runtime-governance":
        check_runtime(checks, root, method, manifest)
    else:
        check_repository(checks, root, method, manifest)
    report = checks.report(args.case, root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
