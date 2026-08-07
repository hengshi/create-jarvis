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


def skill_description_has_use(text: str) -> bool:
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
    if not frontmatter:
        return False
    description = re.search(
        r"(?ms)^description:\s*(.*)\Z",
        frontmatter.group(1),
    )
    return bool(description and re.search(r"\buse\b", description.group(1), re.IGNORECASE))


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
    cards = sorted(
        (root / "jarvis-build" / "work" / "repositories").glob("*/CARD.md")
    )
    card_names = [card.parent.name for card in cards]
    checks.add(
        "Exactly two independent repository cards exist",
        card_names == ["fulfillment", "storefront"],
        repr(card_names),
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
    repo_card = (
        root
        / "jarvis-build"
        / "work"
        / "repositories"
        / "invoice-service"
        / "CARD.md"
    )
    reconciliation = root / "jarvis-build" / "work" / "reconciliation.md"
    checks.add(
        "Repository worker stops before Coordinator acceptance and reconciliation",
        field(repo_card, "Status") == "delivered-awaiting-coordinator-verification"
        and field(reconciliation, "Status") == "waiting-for-construction",
        f"repo={field(repo_card, 'Status')!r}; reconciliation={field(reconciliation, 'Status')!r}",
    )
    start = repo_card.parent / "START-REPOSITORY-LEARNING.md"
    start_text = start.read_text(encoding="utf-8") if start.is_file() else ""
    checks.add(
        "Repository card has one clean top-level Codex handoff",
        start.is_file()
        and str(repo_card) in start_text
        and manifest["method_commit"] in start_text
        and "agents.enabled=false" in start_text
        and field(repo_card, "Execution mode") == "user-launched-top-level-codex",
        str(start),
    )
    skills_root = repo / "skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    router = skills_root / "invoice-service" / "SKILL.md"
    router_text = router.read_text(encoding="utf-8") if router.is_file() else ""
    delivered = [path for path in skill_files if path != router]
    coverage_path = router.parent / "references" / "capability-coverage.json"
    try:
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        coverage = {}
    categories = coverage.get("categories", []) if isinstance(coverage, dict) else []
    surfaces = coverage.get("surface_inventory", []) if isinstance(coverage, dict) else []
    capabilities = coverage.get("capabilities", []) if isinstance(coverage, dict) else []
    category_names = {row.get("name") for row in categories if isinstance(row, dict)}
    expected_categories = {
        "build", "runtime", "lifecycle", "config", "concurrency", "security",
        "diagnostics", "compatibility", "repo-specific",
    }
    capability_by_id = {
        row.get("id"): row for row in capabilities
        if isinstance(row, dict) and row.get("id")
    }
    primary_homes = {
        row.get("primary_home") for row in capabilities
        if isinstance(row, dict)
        and row.get("disposition")
        in {"router", "capability-skill", "focused-loop", "cross-cutting-skill"}
    }
    checks.add(
        "Capability ledger covers every required repository surface",
        category_names == expected_categories
        and all(
            row.get("status") in {"covered", "not-applicable"}
            and isinstance(row.get("evidence"), list)
            and bool(row.get("evidence"))
            and isinstance(row.get("surface_ids"), list)
            and isinstance(row.get("capability_ids"), list)
            for row in categories if isinstance(row, dict)
        ),
        repr(sorted(category_names)),
    )
    surface_by_id = {
        row.get("id"): row
        for row in surfaces
        if isinstance(row, dict) and row.get("id")
    }
    required_capability_fields = {
        "task_family",
        "trigger_examples",
        "authority",
        "entrypoints",
        "state_or_resource_model",
        "proof",
        "route_eval_ids",
        "merge_split_rationale",
        "current_state",
    }
    checks.add(
        "Current and historical fixture capabilities all have explicit dispositions",
        {"webhook-idempotency", "invoice-lifecycle", "audit-export"}
        <= set(capability_by_id)
        and all(
            capability_by_id[name].get("disposition")
            in {
                "router",
                "capability-skill",
                "focused-loop",
                "cross-cutting-skill",
                "reference",
                "script-gate",
                "no-skill",
                "candidate",
            }
            and required_capability_fields <= set(capability_by_id[name])
            and bool(capability_by_id[name].get("trigger_examples"))
            and bool(capability_by_id[name].get("authority"))
            and bool(capability_by_id[name].get("entrypoints"))
            and bool(capability_by_id[name].get("proof"))
            and bool(capability_by_id[name].get("route_eval_ids"))
            for name in {"webhook-idempotency", "invoice-lifecycle", "audit-export"}
        ),
        repr(sorted(capability_by_id)),
    )
    checks.add(
        "Every present surface maps to explicit capabilities",
        bool(surface_by_id)
        and all(
            row.get("status") != "present"
            or (
                bool(row.get("capability_ids"))
                and all(capability_id in capability_by_id for capability_id in row["capability_ids"])
            )
            for row in surface_by_id.values()
        ),
        repr(sorted(surface_by_id)),
    )
    checks.add(
        "Skill topology follows capability primary homes without a fixed package count",
        router.is_file()
        and {path.parent.name for path in delivered} <= primary_homes
        and all(home in {path.parent.name for path in skill_files} for home in primary_homes),
        f"skills={sorted(path.parent.name for path in skill_files)!r}; homes={sorted(primary_homes)!r}",
    )
    checks.add(
        "Router names every delivered skill package",
        bool(delivered)
        and all(path.parent.name in router_text for path in delivered)
        and "route" in router_text.lower(),
        f"router={router}; delivered={[path.parent.name for path in delivered]}",
    )
    delivered_text = {
        path: path.read_text(encoding="utf-8") for path in delivered if path.is_file()
    }
    webhook_skills = [
        path
        for path, text in delivered_text.items()
        if "idempot" in text.lower()
        and "invoice_service/webhooks.py" in text
        and "test" in text.lower()
    ]
    lifecycle_skills = [
        path
        for path, text in delivered_text.items()
        if "invoice_service/lifecycle.py" in text
        and "refund" in text.lower()
        and ("state" in text.lower() or "transition" in text.lower())
        and "test" in text.lower()
    ]
    checks.add(
        "Webhook idempotency is an independently focused loop",
        len(webhook_skills) == 1,
        repr([str(path.relative_to(repo)) for path in webhook_skills]),
    )
    checks.add(
        "Invoice lifecycle is a distinct independently focused loop",
        len(lifecycle_skills) == 1
        and (not webhook_skills or lifecycle_skills[0] != webhook_skills[0]),
        repr([str(path.relative_to(repo)) for path in lifecycle_skills]),
    )
    audit_skills = [
        path
        for path, text in delivered_text.items()
        if "invoice_service/audit.py" in text
        and "audit" in text.lower()
        and "test" in text.lower()
        and any(marker in text.lower() for marker in ("current-state", "current state", "l1"))
    ]
    checks.add(
        "Unprompted current-state audit export capability is independently represented",
        len(audit_skills) == 1
        and (not webhook_skills or audit_skills[0] != webhook_skills[0])
        and (not lifecycle_skills or audit_skills[0] != lifecycle_skills[0]),
        repr([str(path.relative_to(repo)) for path in audit_skills]),
    )
    focused_text = {
        path: delivered_text[path]
        for path in webhook_skills + lifecycle_skills
        if path in delivered_text
    }
    checks.add(
        "Risky focused skills declare triggers, loop guardrails, and proof",
        len(focused_text) == 2
        and all(
            skill_description_has_use(text)
            and "trigger" in text.lower()
            and "guardrail" in text.lower()
            and "proof" in text.lower()
            and any(word in text.lower() for word in ("failure", "recovery", "retry"))
            for text in focused_text.values()
        ),
        repr([str(path.relative_to(repo)) for path in focused_text]),
    )
    checks.add(
        "Every delivered skill has an explicit use trigger",
        bool(delivered_text)
        and all(skill_description_has_use(text) for text in delivered_text.values()),
        repr([str(path.relative_to(repo)) for path in delivered_text]),
    )
    coverage = skills_root / "invoice-service" / "references" / "capability-coverage.md"
    coverage_text = coverage.read_text(encoding="utf-8") if coverage.is_file() else ""
    checks.add(
        "Capability ledger covers replay loops and the unprompted current capability",
        coverage.is_file()
        and all(
            marker in coverage_text
            for marker in (
                "invoice_service/webhooks.py",
                "invoice_service/lifecycle.py",
                "invoice_service/audit.py",
            )
        )
        and "focused-loop" in coverage_text
        and "capability-skill" in coverage_text
        and any(marker in coverage_text.lower() for marker in ("l1", "current-state", "current state")),
        str(coverage),
    )
    depth_assets = [
        skills_root / "invoice-service" / "references" / "skill-depth.md",
        skills_root / "invoice-service" / "references" / "skill-depth.json",
        skills_root / "invoice-service" / "evals" / "evals.json",
        skills_root / "invoice-service" / "scripts" / "audit_skill_depth.py",
    ]
    checks.add(
        "Router delivers the six-dimension depth, eval, and mechanical audit assets",
        all(path.is_file() for path in depth_assets)
        and all(str(path.relative_to(skills_root / "invoice-service")) in router_text for path in depth_assets),
        repr([str(path.relative_to(repo)) for path in depth_assets]),
    )
    audit = skills_root / "invoice-service" / "scripts" / "audit_skill_depth.py"
    if audit.is_file():
        audit_run = command(
            [
                sys.executable,
                str(audit),
                "--repo",
                str(repo),
                "--router",
                "invoice-service",
            ]
        )
        checks.add(
            "Repository depth audit actually passes",
            audit_run.returncode == 0,
            (audit_run.stdout or audit_run.stderr).strip(),
        )
    else:
        checks.add("Repository depth audit actually passes", False, str(audit))
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
        "Repository worker leaves Company handoff pending for Coordinator",
        "pending repo-local entry" in module_text
        and "skills/invoice-service/SKILL.md" not in module_text,
        str(module),
    )
    workflow = company / "skills" / "acme-labs-workflow-bugfix-loop" / "SKILL.md"
    workflow_text = workflow.read_text(encoding="utf-8") if workflow.is_file() else ""
    checks.add(
        "Repository worker does not advance Company workflow maturity",
        "draft-template" in workflow_text
        and not re.search(
            r"(?m)^\*\*当前状态：`(?:construction-ready|active)`\*\*$",
            workflow_text,
        ),
        str(workflow),
    )
    fixed = [
        manifest["history"]["webhook_fixed"],
        manifest["history"]["lifecycle_fixed"],
    ]
    evidence_text = repo_card.read_text(encoding="utf-8") if repo_card.is_file() else ""
    checks.add(
        "Work-card evidence identifies both actual historical fix revisions",
        all(revision in evidence_text for revision in fixed),
        f"expected revisions={fixed}",
    )
    checks.add(
        "Coverage evidence accounts for the current-state audit capability commit",
        manifest["history"]["audit_export"] in (coverage_text + evidence_text),
        f"expected revision={manifest['history']['audit_export']}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        required=True,
        choices=("new-journey", "runtime-governance", "repository-learning-worker"),
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
