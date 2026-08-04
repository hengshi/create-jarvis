#!/usr/bin/env python3
"""Materialize isolated customer-journey eval inputs with real Git history.

The generated directories are disposable customer fixtures, not expected
outputs. Each case refuses to overwrite an existing directory so repeated eval
runs cannot accidentally inherit state.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Acme Eval Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@acme.example",
    "GIT_COMMITTER_NAME": "Acme Eval Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@acme.example",
}


class FixtureError(Exception):
    pass


def run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=GIT_ENV,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise FixtureError(f"command failed ({' '.join(command)}): {detail}")
    return completed.stdout.strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git_init(repo: Path) -> None:
    repo.mkdir(parents=True)
    run(["git", "init", "--initial-branch=main"], cwd=repo)


def git_commit(repo: Path, message: str) -> str:
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo)
    return run(["git", "rev-parse", "HEAD"], cwd=repo)


def attach_bare_remote(repo: Path, remote: Path) -> None:
    remote.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "--bare", "--initial-branch=main", str(remote)])
    run(["git", "remote", "add", "origin", str(remote)], cwd=repo)
    run(["git", "push", "-u", "origin", "main"], cwd=repo)


def create_order_repo(root: Path, name: str, noun: str) -> tuple[Path, str]:
    repo = root / "customer-repos" / name
    git_init(repo)
    write(
        repo / "README.md",
        f"# {name}\n\nSmall fixture service for Acme {noun}.\n",
    )
    write(repo / "src" / "service.py", "def health():\n    return {'status': 'ok'}\n")
    write(
        repo / "tests" / "test_service.py",
        "import unittest\nfrom src.service import health\n\n"
        "class ServiceTest(unittest.TestCase):\n"
        "    def test_health(self):\n"
        "        self.assertEqual(health()['status'], 'ok')\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    git_commit(repo, "initialize service")
    write(
        repo / "src" / "service.py",
        "def health():\n    return {'status': 'ok'}\n\n"
        f"def describe():\n    return '{noun}'\n",
    )
    head = git_commit(repo, "record service capability")
    attach_bare_remote(repo, root / "remotes" / f"{name}.git")
    return repo, head


def create_invoice_history(root: Path) -> tuple[Path, dict[str, str]]:
    repo = root / "customer-repos" / "invoice-service"
    git_init(repo)
    write(
        repo / "AGENTS.md",
        "# Repository guidance\n\nKeep `skills/invoice-service/SKILL.md` as the "
        "repo router. Before finalizing topology, record every current task family in "
        "`skills/invoice-service/references/capability-coverage.md`. Stable independently triggered "
        "capabilities may become skills after current-state validation; risky behavior loops require "
        "historical replay. Do not split skills merely by file or module, and do not flatten validated "
        "capabilities into the router. Preserve customer changes and run "
        "`python3 -m unittest discover -s tests`.\n",
    )
    write(repo / "invoice_service" / "__init__.py", "")
    write(
        repo / "invoice_service" / "webhooks.py",
        "class InvoiceLedger:\n"
        "    def __init__(self):\n"
        "        self.paid_count = 0\n\n"
        "    def apply_paid(self, event_id):\n"
        "        self.paid_count += 1\n"
        "        return self.paid_count\n",
    )
    write(
        repo / "tests" / "test_webhooks.py",
        "import unittest\nfrom invoice_service.webhooks import InvoiceLedger\n\n"
        "class InvoiceLedgerTest(unittest.TestCase):\n"
        "    def test_paid_event(self):\n"
        "        ledger = InvoiceLedger()\n"
        "        self.assertEqual(ledger.apply_paid('evt-1'), 1)\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    baseline = git_commit(repo, "initial invoice webhook")
    write(
        repo / "invoice_service" / "consumer.py",
        "def consume(handler, event):\n"
        "    # The queue may deliver the same event more than once.\n"
        "    return handler.apply_paid(event['id'])\n",
    )
    webhook_vulnerable = git_commit(repo, "wire queue consumer")
    write(
        repo / "invoice_service" / "webhooks.py",
        "class InvoiceLedger:\n"
        "    def __init__(self):\n"
        "        self.paid_count = 0\n"
        "        self.processed_event_ids = set()\n\n"
        "    def apply_paid(self, event_id):\n"
        "        if event_id in self.processed_event_ids:\n"
        "            return self.paid_count\n"
        "        self.processed_event_ids.add(event_id)\n"
        "        self.paid_count += 1\n"
        "        return self.paid_count\n",
    )
    write(
        repo / "tests" / "test_webhooks.py",
        "import unittest\nfrom invoice_service.webhooks import InvoiceLedger\n\n"
        "class InvoiceLedgerTest(unittest.TestCase):\n"
        "    def test_paid_event(self):\n"
        "        ledger = InvoiceLedger()\n"
        "        self.assertEqual(ledger.apply_paid('evt-1'), 1)\n\n"
        "    def test_duplicate_event_is_idempotent(self):\n"
        "        ledger = InvoiceLedger()\n"
        "        ledger.apply_paid('evt-duplicate')\n"
        "        self.assertEqual(ledger.apply_paid('evt-duplicate'), 1)\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    webhook_fixed = git_commit(repo, "follow up on retry report")
    write(
        repo / "invoice_service" / "lifecycle.py",
        "class Invoice:\n"
        "    def __init__(self):\n"
        "        self.state = 'draft'\n\n"
        "    def issue(self):\n"
        "        self.state = 'issued'\n"
        "        return self.state\n\n"
        "    def mark_paid(self):\n"
        "        self.state = 'paid'\n"
        "        return self.state\n\n"
        "    def refund(self):\n"
        "        self.state = 'refunded'\n"
        "        return self.state\n",
    )
    write(
        repo / "tests" / "test_lifecycle.py",
        "import unittest\nfrom invoice_service.lifecycle import Invoice\n\n"
        "class InvoiceLifecycleTest(unittest.TestCase):\n"
        "    def test_paid_invoice_can_be_refunded(self):\n"
        "        invoice = Invoice()\n"
        "        invoice.issue()\n"
        "        invoice.mark_paid()\n"
        "        self.assertEqual(invoice.refund(), 'refunded')\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    lifecycle_vulnerable = git_commit(repo, "support invoice refunds")
    write(
        repo / "invoice_service" / "lifecycle.py",
        "class Invoice:\n"
        "    def __init__(self):\n"
        "        self.state = 'draft'\n\n"
        "    def issue(self):\n"
        "        if self.state != 'draft':\n"
        "            raise ValueError('invoice must be draft before issue')\n"
        "        self.state = 'issued'\n"
        "        return self.state\n\n"
        "    def mark_paid(self):\n"
        "        if self.state != 'issued':\n"
        "            raise ValueError('invoice must be issued before payment')\n"
        "        self.state = 'paid'\n"
        "        return self.state\n\n"
        "    def refund(self):\n"
        "        if self.state != 'paid':\n"
        "            raise ValueError('only a paid invoice can be refunded')\n"
        "        self.state = 'refunded'\n"
        "        return self.state\n",
    )
    write(
        repo / "tests" / "test_lifecycle.py",
        "import unittest\nfrom invoice_service.lifecycle import Invoice\n\n"
        "class InvoiceLifecycleTest(unittest.TestCase):\n"
        "    def test_paid_invoice_can_be_refunded(self):\n"
        "        invoice = Invoice()\n"
        "        invoice.issue()\n"
        "        invoice.mark_paid()\n"
        "        self.assertEqual(invoice.refund(), 'refunded')\n\n"
        "    def test_draft_invoice_cannot_be_refunded(self):\n"
        "        with self.assertRaises(ValueError):\n"
        "            Invoice().refund()\n\n"
        "    def test_refund_is_terminal(self):\n"
        "        invoice = Invoice()\n"
        "        invoice.issue()\n"
        "        invoice.mark_paid()\n"
        "        invoice.refund()\n"
        "        with self.assertRaises(ValueError):\n"
        "            invoice.refund()\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    lifecycle_fixed = git_commit(repo, "follow up on account report")
    write(
        repo / "invoice_service" / "audit.py",
        "def export_audit_record(invoice_id, state, total_cents):\n"
        "    if not invoice_id:\n"
        "        raise ValueError('invoice id is required')\n"
        "    if total_cents < 0:\n"
        "        raise ValueError('invoice total cannot be negative')\n"
        "    return {\n"
        "        'invoice_id': invoice_id,\n"
        "        'state': state,\n"
        "        'total_cents': total_cents,\n"
        "    }\n",
    )
    write(
        repo / "tests" / "test_audit.py",
        "import unittest\nfrom invoice_service.audit import export_audit_record\n\n"
        "class InvoiceAuditTest(unittest.TestCase):\n"
        "    def test_exports_stable_record(self):\n"
        "        self.assertEqual(\n"
        "            export_audit_record('inv-7', 'paid', 1250),\n"
        "            {'invoice_id': 'inv-7', 'state': 'paid', 'total_cents': 1250},\n"
        "        )\n\n"
        "    def test_rejects_negative_total(self):\n"
        "        with self.assertRaises(ValueError):\n"
        "            export_audit_record('inv-7', 'paid', -1)\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n",
    )
    audit_export = git_commit(repo, "add invoice audit export")
    write(
        repo / "README.md",
        "# invoice-service\n\nConsumes invoice events. Queue delivery is at least once.\n",
    )
    head = git_commit(repo, "document delivery semantics")
    attach_bare_remote(repo, root / "remotes" / "invoice-service.git")
    write(repo / "CUSTOMER-NOTE.md", "keep this uncommitted customer investigation note\n")
    return repo, {
        "baseline": baseline,
        "webhook_vulnerable": webhook_vulnerable,
        "webhook_fixed": webhook_fixed,
        "lifecycle_vulnerable": lifecycle_vulnerable,
        "lifecycle_fixed": lifecycle_fixed,
        "audit_export": audit_export,
        "head": head,
    }


def method_commit(method: Path) -> str:
    value = run(["git", "rev-parse", "HEAD"], cwd=method)
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise FixtureError("method checkout does not resolve to a full commit")
    return value


def replace_field(path: Path, label: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(?m)^- {re.escape(label)}:.*$")
    if len(pattern.findall(text)) != 1:
        raise FixtureError(f"expected one {label!r} field in {path}")
    path.write_text(pattern.sub(f"- {label}: `{value}`", text), encoding="utf-8")


def set_checked(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")


def init_workspace(root: Path, method: Path, commit: str) -> Path:
    workspace = root / "jarvis-build"
    run(
        [
            sys.executable,
            str(method / "scripts" / "instantiate_construction_workspace.py"),
            "init",
            "--workspace",
            str(workspace),
            "--method-repository",
            str(method),
            "--method-commit",
            commit,
            "--coordinator",
            "fixture Host Agent",
            "--created-at",
            "2026-07-30T00:00:00+00:00",
        ]
    )
    return workspace


def add_repo_card(
    workspace: Path,
    method: Path,
    repo: Path,
    name: str,
    branch: str,
) -> None:
    run(
        [
            sys.executable,
            str(method / "scripts" / "instantiate_construction_workspace.py"),
            "add-repository",
            "--workspace",
            str(workspace),
            "--name",
            name,
            "--repository",
            str(repo),
            "--history-range",
            "all reachable history",
            "--delivery-policy",
            "branch-push to fixture origin; no provider PR API",
            "--target-workspace",
            str(root_for(workspace) / "worktrees" / name),
            "--target-branch",
            branch,
            "--added-at",
            "2026-07-30T00:00:00+00:00",
        ]
    )


def root_for(workspace: Path) -> Path:
    return workspace.parent


def instantiate_company(root: Path, method: Path, repositories: list[str]) -> tuple[Path, Path, str]:
    company = root / "workspaces" / "acme-labs-jarvis"
    company.parent.mkdir(parents=True, exist_ok=True)
    render_input = root / "customer-input" / "company-render-input.json"
    write(
        render_input,
        json.dumps(
            {
                "schema_version": 1,
                "company": {
                    "name": "Acme Labs",
                    "slug": "acme-labs",
                    "product_identity": "Acme Commerce",
                    "owner": "platform-engineering",
                },
                "paths": {
                    "target": str(company),
                    "workspace_root": str(company.parent),
                },
                "scope": {
                    "modules": ["billing"],
                    "sources": ["customer-docs", "issue-tracker"],
                    "repositories": repositories,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    run(
        [
            sys.executable,
            str(method / "scripts" / "instantiate_company_jarvis.py"),
            "base",
            "--input",
            str(render_input),
        ]
    )
    run(
        [
            sys.executable,
            str(method / "scripts" / "instantiate_company_jarvis.py"),
            "module",
            "--input",
            str(render_input),
            "--name",
            "billing",
        ]
    )
    git_init_existing(company)
    company_commit = git_commit(company, "initialize Acme Labs Jarvis")
    remote = root / "remotes" / "acme-labs-jarvis.git"
    attach_bare_remote(company, remote)
    return company, remote, company_commit


def git_init_existing(repo: Path) -> None:
    run(["git", "init", "--initial-branch=main"], cwd=repo)


def fill_common_context(
    workspace: Path,
    company: Path,
    company_remote: Path,
    company_commit: str,
) -> None:
    context = workspace / "BUILD-CONTEXT.md"
    for label, value in (
        ("Company legal/display name", "Acme Labs"),
        ("Company slug", "acme-labs"),
        ("Provider/host", "local Git fixture"),
        ("Owner/namespace", "acme-eval"),
        ("Repository", "acme-labs-jarvis"),
        ("Canonical remote", str(company_remote)),
        ("Existing history/default branch", "initial commit on main"),
        ("Publication mode", "new-initial-push"),
        ("Write/review capability probe", f"main pushed at {company_commit}"),
    ):
        replace_field(context, label, value)

    initialization = workspace / "work" / "company-repo-initialization.md"
    for label, value in (
        ("Target repository", str(company_remote)),
        ("Target workspace", str(company)),
        ("Target branch", "main"),
        ("Writer", "fixture Part 1 writer (ended)"),
        ("Status", "complete"),
        ("Last verified checkpoint", f"remote main resolves {company_commit}"),
        ("Delivered artifacts", f"{company_remote} main {company_commit}"),
        ("Evidence", f"git ls-remote {company_remote} refs/heads/main"),
        ("Blocker", "none"),
        ("Next", "Start Company construction and independent repository cards"),
    ):
        replace_field(initialization, label, value)
    set_checked(initialization)

    construction = workspace / "work" / "company-construction.md"
    for label, value in (
        ("Target repository", str(company_remote)),
        ("Target workspace", str(company)),
        ("Target branch", "create-jarvis/company-construction"),
        ("Status", "ready"),
        ("Blocker", "none"),
        ("Next", "Assign the single Company integrator"),
    ):
        replace_field(construction, label, value)

    journal = workspace / "CONSTRUCTION-JOURNAL.md"
    for label, value in (
        ("Current work card", "work/company-construction.md"),
        ("Company delivery", f"main {company_commit}"),
        ("Blocker", "none"),
        ("Next", "Execute work/company-construction.md"),
    ):
        replace_field(journal, label, value)
    text = journal.read_text(encoding="utf-8")
    text = text.replace(
        "| `work/company-repo-initialization.md` | ready | unassigned | workspace created | assign Company writer |",
        f"| `work/company-repo-initialization.md` | complete | fixture writer ended | remote main {company_commit} | start Part 2/3 |",
    ).replace(
        "| `work/company-construction.md` | waiting-for-part-1 | unassigned | none | wait for Part 1 delivery |",
        "| `work/company-construction.md` | ready | unassigned | Part 1 remote verified | assign Company integrator |",
    )
    journal.write_text(text, encoding="utf-8")


def build_new_journey(root: Path) -> dict[str, object]:
    storefront, storefront_head = create_order_repo(root, "storefront", "ordering")
    fulfillment, fulfillment_head = create_order_repo(root, "fulfillment", "shipping")
    write(fulfillment / "CUSTOMER-NOTE.md", "preserve this uncommitted note\n")
    company_remote = root / "remotes" / "acme-labs-jarvis.git"
    company_remote.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "--bare", "--initial-branch=main", str(company_remote)])
    write(
        root / "customer-docs" / "product-overview.md",
        "# Acme Commerce\n\nStorefront accepts orders; fulfillment owns shipment state. "
        "The pilot workflow is investigate-and-fix an order that never enters shipment.\n",
    )
    write(
        root / "customer-input" / "customer-brief.md",
        f"# Customer brief\n\n"
        f"Company: Acme Labs (`acme-labs`). Owner: platform-engineering.\n\n"
        f"Authorized document: `{root / 'customer-docs' / 'product-overview.md'}`.\n\n"
        f"Authorized repositories:\n\n"
        f"- storefront: `{storefront}` at `{storefront_head}`; all reachable history; branch-push to fixture origin.\n"
        f"- fulfillment: `{fulfillment}` at `{fulfillment_head}`; all reachable history; preserve its dirty customer note; branch-push to fixture origin.\n\n"
        f"Company target: local Git remote `{company_remote}`, private-equivalent, new initial push to `main`; target workspace `{root / 'workspaces' / 'acme-labs-jarvis'}`.\n\n"
        "No Host runtime discovery pointers are supplied yet. Record that boundary; do not scan outside these paths. "
        "Prepare the journey, execute Part 1 only, then stop at a recoverable verified checkpoint.\n",
    )
    return {
        "case": "new-journey",
        "customer_brief": str(root / "customer-input" / "customer-brief.md"),
        "repositories": [str(storefront), str(fulfillment)],
        "company_remote": str(company_remote),
    }


def build_runtime_governance(root: Path, method: Path, commit: str) -> dict[str, object]:
    repo, repo_head = create_order_repo(root, "commerce-api", "commerce API")
    company, company_remote, company_commit = instantiate_company(
        root, method, [str(repo)]
    )
    workspace = init_workspace(root, method, commit)
    add_repo_card(
        workspace,
        method,
        repo,
        "commerce-api",
        "create-jarvis/repo-learning-commerce-api",
    )
    fill_common_context(workspace, company, company_remote, company_commit)
    host_runtime = root / "host-runtime"
    (host_runtime / "bin").mkdir(parents=True)
    (host_runtime / "cache").mkdir()
    write(
        host_runtime / "README.md",
        "# Authorized Host runtime root\n\nThe customer authorizes create/read/write under this directory only. "
        "A stable customer-owned sync entry is required under `bin/`. It must materialize the Company Jarvis "
        "and commerce-api canonical remotes into `cache/`, preserve non-fast-forward safety, and print the exact resolved commits.\n",
    )
    context = workspace / "BUILD-CONTEXT.md"
    for label, value in (
        ("Discovery pointers explicitly supplied by customer", str(host_runtime)),
        ("Approved stable runtime root/resolver", str(host_runtime)),
        ("Approved install/write targets", f"{host_runtime / 'bin'}; {host_runtime / 'cache'}"),
        ("Existing sync/workspace/tool entry pointers", "none observed"),
        ("Authority probe/evidence", f"create/read/write/rename verified under {host_runtime}"),
    ):
        replace_field(context, label, value)
    write(
        root / "customer-docs" / "runtime-requirements.md",
        f"# Acme Host runtime requirements\n\n"
        f"Canonical Company remote: `{company_remote}`. Canonical commerce-api remote: `{root / 'remotes' / 'commerce-api.git'}`.\n\n"
        "Every Host task must sync both sources before durable work, refuse to overwrite a dirty cache, "
        "and report exact commits. Credentials stay outside Company Jarvis and the Construction Workspace. "
        "No jarvis-box installation is authorized in this case.\n",
    )
    write(
        root / "customer-input" / "customer-brief.md",
        f"# Resume instruction\n\nContinue the journey at `{workspace}` using its pinned method commit. "
        f"Execute Part 2 only. The authorized customer docs are `{root / 'customer-docs' / 'runtime-requirements.md'}` "
        f"and `{host_runtime / 'README.md'}`. You may write only the Company target, its approved remote, the active card/evidence, "
        f"and `{host_runtime}`. Build and behaviorally verify the missing Host runtime foundation, publish the Company result, "
        "then stop with a recoverable checkpoint. Do not install or imitate jarvis-box.\n",
    )
    return {
        "case": "runtime-governance",
        "workspace": str(workspace),
        "company": str(company),
        "company_remote": str(company_remote),
        "company_initial_commit": company_commit,
        "repository": str(repo),
        "repository_head": repo_head,
        "host_runtime": str(host_runtime),
    }


def build_repository_reconciliation(root: Path, method: Path, commit: str) -> dict[str, object]:
    repo, history = create_invoice_history(root)
    company, company_remote, company_commit = instantiate_company(
        root, method, [str(repo)]
    )
    route = company / "modules" / "billing" / "overview.md"
    route.write_text(
        route.read_text(encoding="utf-8")
        + "\n## Invoice webhook execution\n\n- repo: invoice-service\n"
        "- repo-local entry: pending repo-local entry\n"
        "- first proofs: customer issues ACME-17 and ACME-18 plus current repository history\n",
        encoding="utf-8",
    )
    company_commit = git_commit(company, "record pending invoice-service handoff")
    run(["git", "push", "origin", "main"], cwd=company)

    workspace = init_workspace(root, method, commit)
    add_repo_card(
        workspace,
        method,
        repo,
        "invoice-service",
        "create-jarvis/repo-learning-invoice-service",
    )
    fill_common_context(workspace, company, company_remote, company_commit)

    construction = workspace / "work" / "company-construction.md"
    for label, value in (
        ("Writer", "fixture Company integrator (ended)"),
        ("Status", "complete"),
        ("Last verified checkpoint", f"Company main resolves {company_commit}"),
        ("Delivered artifacts", f"Company main {company_commit}"),
        ("Evidence", f"git ls-remote {company_remote} refs/heads/main"),
        ("Blocker", "none"),
        ("Next", "Run invoice-service card, then reconciliation"),
    ):
        replace_field(construction, label, value)
    set_checked(construction)

    repo_card = workspace / "work" / "repositories" / "invoice-service.md"
    for label, value in (
        ("Status", "ready"),
        ("Blocker", "none"),
        ("Next", "Build full capability coverage, replay ACME-17 and ACME-18, and deliver repo-local guidance"),
    ):
        replace_field(repo_card, label, value)

    journal = workspace / "CONSTRUCTION-JOURNAL.md"
    for label, value in (
        ("Current work card", "work/repositories/invoice-service.md"),
        ("Company delivery", f"main {company_commit}"),
        ("Repository deliveries", "none; invoice-service ready"),
        ("Reconciliation", "waiting-for-construction"),
        ("Blocker", "none"),
        ("Next", "Execute work/repositories/invoice-service.md"),
    ):
        replace_field(journal, label, value)
    journal.write_text(
        journal.read_text(encoding="utf-8")
        .replace(
            "| `work/company-construction.md` | ready | unassigned | Part 1 remote verified | assign Company integrator |",
            f"| `work/company-construction.md` | complete | fixture integrator ended | Company main {company_commit} | run repository card |",
        )
        .replace(
            "| `work/repositories/invoice-service.md` | waiting-for-part-1 | unassigned | none | wait for Part 1 delivery |",
            "| `work/repositories/invoice-service.md` | ready | unassigned | Part 1 and Part 2 verified | inventory capabilities and replay ACME-17/18 |",
        ),
        encoding="utf-8",
    )
    write(
        root / "customer-input" / "issue-ACME-17.md",
        "# ACME-17: duplicate paid webhook increments invoice twice\n\n"
        "Queue delivery is at least once. Replaying the same event id must leave the paid count at one. "
        "The incident was resolved somewhere in the supplied repository history; commit messages are not authoritative.\n",
    )
    write(
        root / "customer-input" / "replay_duplicate_webhook.py",
        "from invoice_service.webhooks import InvoiceLedger\n"
        "ledger = InvoiceLedger()\n"
        "ledger.apply_paid('evt-retry')\n"
        "assert ledger.apply_paid('evt-retry') == 1\n"
        "print('duplicate webhook replay: pass')\n",
    )
    write(
        root / "customer-input" / "issue-ACME-18.md",
        "# ACME-18: unpaid invoice accepted a refund\n\n"
        "Refund is a terminal transition and is valid only after issue and payment. Draft invoices and already-refunded "
        "invoices must reject refund. The incident was resolved somewhere in the supplied repository history; commit "
        "messages are not authoritative.\n",
    )
    write(
        root / "customer-input" / "replay_invoice_lifecycle.py",
        "from invoice_service.lifecycle import Invoice\n"
        "draft = Invoice()\n"
        "try:\n"
        "    draft.refund()\n"
        "except ValueError:\n"
        "    pass\n"
        "else:\n"
        "    raise AssertionError('draft refund must fail')\n"
        "paid = Invoice()\n"
        "paid.issue()\n"
        "paid.mark_paid()\n"
        "assert paid.refund() == 'refunded'\n"
        "try:\n"
        "    paid.refund()\n"
        "except ValueError:\n"
        "    pass\n"
        "else:\n"
        "    raise AssertionError('refund must be terminal')\n"
        "print('invoice lifecycle replay: pass')\n",
    )
    write(
        root / "customer-input" / "customer-brief.md",
        f"# Resume instruction\n\nContinue at `{workspace}`. Execute the invoice-service repository card using "
        f"`{root / 'customer-input' / 'issue-ACME-17.md'}` with `{root / 'customer-input' / 'replay_duplicate_webhook.py'}`, "
        f"and `{root / 'customer-input' / 'issue-ACME-18.md'}` with `{root / 'customer-input' / 'replay_invoice_lifecycle.py'}`. "
        "Inspect real patches and code across all reachable history; preserve the uncommitted CUSTOMER-NOTE.md. Before selecting replay cases, "
        "inventory every current task family and give each an evidence-backed topology disposition. Derive skills from independently triggerable "
        "capabilities and logic loops, not from repo/module/directory count or a fixed skill quota. Use current-state validation for stable capability "
        "workflows and same-case plus cross-loop route evidence for risky historical loops. Deliver a lightweight repo router and the complete validated "
        "repo-local topology through the recorded branch policy. "
        "Then run Reconciliation Gate: replace the pending Company handoff with the delivered router entry, prove both controlled cases route "
        "to their distinct focused skills, customize the bugfix workflow enough to move it to construction-ready if evidence supports it, "
        "publish the Company ref, and stop. "
        "Do not mark the workflow active and do not install jarvis-box.\n",
    )
    return {
        "case": "repository-reconciliation",
        "workspace": str(workspace),
        "company": str(company),
        "company_remote": str(company_remote),
        "repository": str(repo),
        "repository_remote": str(root / "remotes" / "invoice-service.git"),
        "history": history,
        "dirty_file": str(repo / "CUSTOMER-NOTE.md"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        required=True,
        choices=("new-journey", "runtime-governance", "repository-reconciliation"),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--method-repository", required=True, type=Path)
    args = parser.parse_args()

    root = args.output.expanduser().resolve()
    method = args.method_repository.expanduser().resolve()
    if root.exists():
        print(f"ERROR: output already exists: {root}", file=sys.stderr)
        return 1
    if not (method / "SKILL.md").is_file():
        print(f"ERROR: invalid create-jarvis checkout: {method}", file=sys.stderr)
        return 1
    root.mkdir(parents=True)
    try:
        commit = method_commit(method)
        if args.case == "new-journey":
            manifest = build_new_journey(root)
        elif args.case == "runtime-governance":
            manifest = build_runtime_governance(root, method, commit)
        else:
            manifest = build_repository_reconciliation(root, method, commit)
    except (FixtureError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    manifest["method_repository"] = str(method)
    manifest["method_commit"] = commit
    write(root / "fixture-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
