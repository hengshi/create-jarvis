#!/usr/bin/env python3
"""Verify deterministic Construction Workspace and recovery contracts.

This verifier checks structure, cross-file pointers, work-card completeness and
filesystem safety. It does not grade customer semantics, Git delivery, runtime
behavior or whether a human-written checkpoint is true.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "README.md",
    "BUILD-CONTEXT.md",
    "CONSTRUCTION-JOURNAL.md",
    "CONTINUE-JARVIS.md",
    "evidence/README.md",
    "work/company-repo-initialization.md",
    "work/company-construction.md",
    "work/reconciliation.md",
    "work/jarvis-box-onboarding.md",
)
CORE_WORK_CARDS = (
    "work/company-repo-initialization.md",
    "work/company-construction.md",
    "work/reconciliation.md",
    "work/jarvis-box-onboarding.md",
)
REQUIRED_CARD_FIELDS = (
    "Objective",
    "Completion gate",
    "Authorized inputs",
    "Allowed writes",
    "Writer",
    "Provider/session handle",
    "Status",
    "Last verified checkpoint",
    "Delivered artifacts",
    "Evidence",
    "Blocker",
    "Next",
    "Last verified",
)
REQUIRED_REPOSITORY_CARD_FIELDS = (
    "History range",
    "Delivery policy",
    "Execution mode",
    "Scope lock",
    "Method repository",
    "Method commit",
    "Handoff entry",
    "Fixed revision",
    "Default branch",
    "Reachable commit count",
    "History cursor",
    "Code-read coverage",
    "Capability coverage",
    "Capability ledger",
    "Repository model",
    "Validation evidence",
    "Validation cursor",
    "Depth audit",
    "Delivery ref",
    "Review state",
    "Coordinator finding",
)
REPOSITORY_WORKER_CHECKPOINTS = (
    "Exact repository revision and history boundary are verified",
    "Every reachable commit has actual code-change disposition, not message/stat-only coverage",
    "Every current major business task family has trigger, owner, entrypoint, state/failure model, proof, validation level and topology disposition",
    "Every merge/split/no-skill decision is explicit; no broad router/capability row hides independent workflows",
    "Every delivered capability has an executed representative route probe; high-risk claims have the required replay/negative evidence",
    "Skill structure, links, scripts, current-ref checks and depth audit pass",
    "Worker delivered a commit/branch/PR/MR or explicit blocked result and stopped at Coordinator verification",
)
REPOSITORY_COORDINATOR_CHECKPOINT = (
    "Coordinator independently verified semantic coverage, remote ref and review state before marking this card completed"
)
OBSOLETE_CONTRACTS = (
    "bootstrap-state.json",
    "bootstrap-result.json",
    "jarvis.toml",
    "REPOSITORY-WORK-CARD.md",
)
TEXT_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".env", ".sh", ".py"}
)
TOKEN_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
ANGLE_PLACEHOLDER_RE = re.compile(
    r"<(?:absolute-path(?:-or-host|-or-remote)?|full-commit|timestamp|branch|range|policy|company-target|unresolved|repo)>"
)
SECRET_RE = re.compile(
    r"(?im)^\s*(?:api[_-]?key|access[_-]?token|password|private[_-]?key|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
)
COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
FIELD_RE_TEMPLATE = r"(?m)^- {label}:\s*(.+?)\s*$"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def field_value(text: str, label: str) -> str | None:
    matches = re.findall(FIELD_RE_TEMPLATE.format(label=re.escape(label)), text)
    if len(matches) != 1:
        return None
    return matches[0].strip().strip("`")


class Verifier:
    def __init__(self, workspace: Path, *, require_dispatch_ready: bool = False) -> None:
        self.workspace = workspace.resolve()
        self.require_dispatch_ready = require_dispatch_ready
        self.findings: list[Finding] = []

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))

    def verify(self) -> dict[str, Any]:
        if not self.workspace.is_dir() or self.workspace.is_symlink():
            self.add(
                "blocker",
                "workspace_missing",
                f"Construction Workspace does not exist or is a symlink: {self.workspace}",
            )
            return self.report()
        self.verify_required_files()
        self.verify_recovery_consistency()
        self.verify_work_cards()
        self.verify_repository_indexes()
        self.verify_filesystem_safety()
        if self.require_dispatch_ready:
            self.verify_dispatch_ready()
        return self.report()

    def repository_cards(self) -> list[Path]:
        repo_root = self.workspace / "work" / "repositories"
        return sorted(repo_root.glob("*/CARD.md")) if repo_root.is_dir() else []

    def verify_required_files(self) -> None:
        for relative in REQUIRED_FILES:
            if not (self.workspace / relative).is_file():
                self.add("blocker", "required_file_missing", f"required file missing: {relative}")
        for name in OBSOLETE_CONTRACTS:
            for path in self.workspace.rglob(name):
                self.add(
                    "blocker",
                    "obsolete_contract_present",
                    f"obsolete construction contract must not be present: {path.relative_to(self.workspace)}",
                )
        work_root = self.workspace / "work"
        if work_root.is_dir():
            for path in work_root.glob("RUN*.md"):
                self.add(
                    "blocker",
                    "legacy_run_document_present",
                    f"legacy lane RUN document must not be present: {path.relative_to(self.workspace)}",
                )

    def read(self, relative: str) -> str | None:
        path = self.workspace / relative
        if not path.is_file() or path.is_symlink():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.add("blocker", "file_unreadable", f"cannot read {relative}: {exc}")
            return None

    def require_field(self, text: str, label: str, relative: str) -> str | None:
        value = field_value(text, label)
        if value is None:
            self.add(
                "blocker",
                "work_card_field_invalid",
                f"{relative} must contain exactly one '{label}' field",
            )
        return value

    def verify_recovery_consistency(self) -> None:
        build = self.read("BUILD-CONTEXT.md")
        journal = self.read("CONSTRUCTION-JOURNAL.md")
        continuation = self.read("CONTINUE-JARVIS.md")
        if build is None or journal is None or continuation is None:
            return

        workspace_values = {
            "BUILD-CONTEXT.md": field_value(build, "Construction Workspace"),
            "CONSTRUCTION-JOURNAL.md": field_value(journal, "Construction Workspace"),
            "CONTINUE-JARVIS.md": field_value(continuation, "Construction Workspace"),
        }
        for relative, value in workspace_values.items():
            if value != str(self.workspace):
                self.add(
                    "blocker",
                    "workspace_pointer_mismatch",
                    f"{relative} records {value!r}, expected {str(self.workspace)!r}",
                )

        build_context_pointer = field_value(journal, "Build context")
        expected_build_context = str(self.workspace / "BUILD-CONTEXT.md")
        if build_context_pointer != expected_build_context:
            self.add(
                "blocker",
                "build_context_pointer_mismatch",
                f"journal records {build_context_pointer!r}, expected {expected_build_context!r}",
            )
        journal_pointer = field_value(continuation, "Journal")
        expected_journal = str(self.workspace / "CONSTRUCTION-JOURNAL.md")
        if journal_pointer != expected_journal:
            self.add(
                "blocker",
                "journal_pointer_mismatch",
                f"continuation records {journal_pointer!r}, expected {expected_journal!r}",
            )

        commits = {
            field_value(build, "Method commit"),
            field_value(journal, "Method commit"),
            field_value(continuation, "Method commit"),
        }
        commit: str | None = None
        if len(commits) != 1 or None in commits:
            self.add("blocker", "method_commit_mismatch", "method commit differs across recovery files")
        else:
            commit = next(iter(commits))
            if commit is None or not COMMIT_RE.fullmatch(commit):
                self.add("blocker", "method_commit_invalid", "method commit is not a full hex commit")

        methods = {
            field_value(build, "Method repository"),
            field_value(continuation, "Method repository"),
        }
        if len(methods) != 1 or None in methods:
            self.add(
                "blocker",
                "method_repository_mismatch",
                "method repository differs across recovery files",
            )
        else:
            method = Path(next(iter(methods))).expanduser()
            if not method.is_dir():
                self.add(
                    "major",
                    "method_repository_unavailable",
                    f"recorded method repository is unavailable: {method}",
                )
            elif commit is not None and COMMIT_RE.fullmatch(commit):
                resolved = subprocess.run(
                    ["git", "-C", str(method), "rev-parse", "--verify", f"{commit}^{{commit}}"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if resolved.returncode != 0 or resolved.stdout.strip().lower() != commit:
                    self.add(
                        "blocker",
                        "method_commit_unavailable",
                        f"recorded method commit is unavailable in {method}: {commit}",
                    )
                head = subprocess.run(
                    ["git", "-C", str(method), "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if head.returncode != 0 or head.stdout.strip().lower() != commit:
                    self.add(
                        "blocker",
                        "method_checkout_mismatch",
                        f"recorded method checkout is not materialized at {commit}",
                    )

        current = field_value(journal, "Current work card")
        if current is None:
            self.add("blocker", "current_work_card_missing", "journal has no unique current work card")
        else:
            candidate = (self.workspace / current).resolve()
            try:
                candidate.relative_to(self.workspace)
            except ValueError:
                self.add("blocker", "current_work_card_unsafe", f"current work card escapes workspace: {current}")
            else:
                if not candidate.is_file():
                    self.add("blocker", "current_work_card_missing", f"current work card does not exist: {current}")

    def verify_work_cards(self) -> None:
        cards = [self.workspace / relative for relative in CORE_WORK_CARDS]
        cards.extend(self.repository_cards())
        for card in cards:
            if not card.is_file() or card.is_symlink():
                continue
            relative = str(card.relative_to(self.workspace))
            text = self.read(relative)
            if text is None:
                continue
            for label in REQUIRED_CARD_FIELDS:
                self.require_field(text, label, relative)
            if relative == "work/jarvis-box-onboarding.md":
                for label in ("Target deployment", "Target workspace", "Target release/image"):
                    self.require_field(text, label, relative)
            else:
                for label in ("Target repository", "Target workspace", "Target branch"):
                    self.require_field(text, label, relative)
            if relative.startswith("work/repositories/"):
                for label in REQUIRED_REPOSITORY_CARD_FIELDS:
                    self.require_field(text, label, relative)
                self.verify_repository_handoff(card, text, relative)
                self.verify_repository_delivery_record(text, relative)

    def verify_repository_delivery_record(self, text: str, relative: str) -> None:
        status = field_value(text, "Status")
        if status not in {"delivered-awaiting-coordinator-verification", "completed"}:
            return
        required_values = (
            "Fixed revision",
            "Default branch",
            "Reachable commit count",
            "History cursor",
            "Code-read coverage",
            "Capability coverage",
            "Capability ledger",
            "Repository model",
            "Validation evidence",
            "Validation cursor",
            "Depth audit",
            "Delivery ref",
            "Review state",
            "Delivered artifacts",
            "Evidence",
        )
        placeholders = {"", "none", "unresolved", "not-run", "not-started", "pending"}
        for label in required_values:
            value = (field_value(text, label) or "").strip()
            if value.lower() in placeholders:
                self.add(
                    "blocker",
                    "repository_delivery_record_incomplete",
                    f"{relative} cannot be {status} while '{label}' is {value!r}",
                )
        fixed_revision = field_value(text, "Fixed revision") or ""
        if not COMMIT_RE.fullmatch(fixed_revision.lower()):
            self.add(
                "blocker",
                "repository_fixed_revision_invalid",
                f"{relative} must record one full fixed revision before delivery",
            )
        reachable_count = field_value(text, "Reachable commit count") or ""
        if not reachable_count.isdigit() or int(reachable_count) < 1:
            self.add(
                "blocker",
                "repository_history_count_invalid",
                f"{relative} must record a positive reachable commit count before delivery",
            )
        if "pass" not in (field_value(text, "Depth audit") or "").lower():
            self.add(
                "blocker",
                "repository_depth_audit_not_passed",
                f"{relative} must record an actually passed depth audit before delivery",
            )
        for checkpoint in REPOSITORY_WORKER_CHECKPOINTS:
            if not re.search(rf"(?mi)^- \[[xX]\] {re.escape(checkpoint)}$", text):
                self.add(
                    "blocker",
                    "repository_worker_checkpoint_open",
                    f"{relative} has an open worker checkpoint: {checkpoint}",
                )
        coordinator_checked = bool(
            re.search(
                rf"(?mi)^- \[[xX]\] {re.escape(REPOSITORY_COORDINATOR_CHECKPOINT)}$",
                text,
            )
        )
        if status == "completed" and not coordinator_checked:
            self.add(
                "blocker",
                "repository_coordinator_checkpoint_open",
                f"{relative} is completed without Coordinator verification",
            )
        if status == "completed" and (
            field_value(text, "Coordinator finding") or ""
        ).strip().lower() in placeholders:
            self.add(
                "blocker",
                "repository_coordinator_finding_missing",
                f"{relative} is completed without a recorded Coordinator finding",
            )
        if status == "delivered-awaiting-coordinator-verification" and coordinator_checked:
            self.add(
                "blocker",
                "repository_coordinator_checkpoint_premature",
                f"{relative} claims Coordinator verification before completed status",
            )

    def verify_repository_handoff(self, card: Path, text: str, relative: str) -> None:
        if field_value(text, "Execution mode") != "user-launched-top-level-codex":
            self.add(
                "blocker",
                "repository_execution_mode_invalid",
                f"{relative} must use a user-launched top-level Codex process",
            )
        if field_value(text, "Scope lock") != (
            "exactly one repository; primary writer multi-agent tools disabled"
        ):
            self.add(
                "blocker",
                "repository_scope_lock_invalid",
                f"{relative} does not enforce one repository with primary multi-agent disabled",
            )
        status = field_value(text, "Status")
        handoff = field_value(text, "Handoff entry")
        if status not in {
            "ready-for-user-launch",
            "in-progress",
            "paused",
            "delivered-awaiting-coordinator-verification",
            "completed",
        }:
            return
        expected = card.parent / "START-REPOSITORY-LEARNING.md"
        if handoff != str(expected):
            self.add(
                "blocker",
                "repository_handoff_pointer_invalid",
                f"{relative} records {handoff!r}, expected {str(expected)!r}",
            )
        if not expected.is_file() or expected.is_symlink():
            self.add(
                "blocker",
                "repository_handoff_missing",
                f"repository handoff is missing or unsafe: {expected.relative_to(self.workspace)}",
            )
            return
        start_text = expected.read_text(encoding="utf-8")
        for required in (
            str(card),
            field_value(text, "Method repository") or "",
            field_value(text, "Method commit") or "",
            "agents.enabled=false",
            "delivered-awaiting-coordinator-verification",
        ):
            if not required or required not in start_text:
                self.add(
                    "blocker",
                    "repository_handoff_content_invalid",
                    f"{expected.relative_to(self.workspace)} is missing required pinned scope",
                )
                break

    def verify_repository_indexes(self) -> None:
        build = self.read("BUILD-CONTEXT.md")
        journal = self.read("CONSTRUCTION-JOURNAL.md")
        if build is None or journal is None:
            return
        marker_counts = {
            "BUILD-CONTEXT.md inventory start": build.count("<!-- REPOSITORY-INVENTORY:START -->"),
            "BUILD-CONTEXT.md inventory end": build.count("<!-- REPOSITORY-INVENTORY:END -->"),
            "journal work index start": journal.count("<!-- REPOSITORY-WORK-INDEX:START -->"),
            "journal work index end": journal.count("<!-- REPOSITORY-WORK-INDEX:END -->"),
        }
        for label, count in marker_counts.items():
            if count != 1:
                self.add("blocker", "repository_index_marker_invalid", f"{label} count is {count}, expected 1")
        cards = self.repository_cards()
        card_names = [card.parent.name for card in cards]
        inventory_block = build.split("<!-- REPOSITORY-INVENTORY:START -->", 1)[-1].split(
            "<!-- REPOSITORY-INVENTORY:END -->", 1
        )[0]
        inventory_names = [
            line.split("|", 2)[1].strip()
            for line in inventory_block.splitlines()
            if line.startswith("|") and line.count("|") >= 2
        ]
        journal_names = re.findall(
            r"(?m)^\| `work/repositories/([^`/]+)/CARD\.md` \|", journal
        )
        for label, names in (
            ("BUILD-CONTEXT.md repository inventory", inventory_names),
            ("CONSTRUCTION-JOURNAL.md repository index", journal_names),
        ):
            if len(names) != len(set(names)):
                self.add(
                    "blocker",
                    "repository_index_duplicate",
                    f"{label} contains duplicate rows",
                )
            if set(names) != set(card_names):
                self.add(
                    "blocker",
                    "repository_index_mismatch",
                    f"{label} names {sorted(set(names))!r} do not match cards {card_names!r}",
                )

    def verify_filesystem_safety(self) -> None:
        for path in self.workspace.rglob("*"):
            if path.is_symlink():
                self.add(
                    "blocker",
                    "symlink_not_allowed",
                    f"workspace artifact is a symlink: {path.relative_to(self.workspace)}",
                )
                continue
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > 1_000_000:
                    continue
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            relative = path.relative_to(self.workspace)
            if SECRET_RE.search(text):
                self.add("blocker", "secret_exposure", f"possible secret in {relative}")
            if TOKEN_RE.search(text) or ANGLE_PLACEHOLDER_RE.search(text):
                self.add(
                    "blocker",
                    "template_token_unresolved",
                    f"unrendered method template token in {relative}",
                )

    def verify_dispatch_ready(self) -> None:
        build = self.read("BUILD-CONTEXT.md")
        initialization = self.read("work/company-repo-initialization.md")
        if build is None or initialization is None:
            return
        for label in (
            "Company legal/display name",
            "Company slug",
            "Provider/host",
            "Owner/namespace",
            "Repository",
            "Canonical remote",
            "Existing history/default branch",
            "Publication mode",
            "Write/review capability probe",
        ):
            value = field_value(build, label)
            if value is None or value.lower().startswith("unresolved"):
                self.add("major", "dispatch_fact_unresolved", f"BUILD-CONTEXT.md: {label} is unresolved")
        for label in ("Target repository", "Target workspace", "Target branch"):
            value = field_value(initialization, label)
            if value is None or value.lower().startswith("unresolved"):
                self.add(
                    "major",
                    "dispatch_target_unresolved",
                    f"company initialization card: {label} is unresolved",
                )
        for card in self.repository_cards():
            text = card.read_text(encoding="utf-8")
            for label in (
                "Target repository",
                "Target workspace",
                "Target branch",
                "History range",
                "Delivery policy",
            ):
                value = field_value(text, label)
                if value is None or value.lower().startswith("unresolved"):
                    self.add(
                        "major",
                        "repository_dispatch_fact_unresolved",
                        f"{card.relative_to(self.workspace)}: {label} is unresolved",
                    )

    def report(self) -> dict[str, Any]:
        counts = {
            severity: sum(1 for finding in self.findings if finding.severity == severity)
            for severity in ("blocker", "major", "minor")
        }
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "pass" if counts["blocker"] == 0 and counts["major"] == 0 else "fail",
            "scope": "deterministic Construction Workspace structure, recovery pointers and safety only",
            "workspace": str(self.workspace),
            "repository_card_count": len(self.repository_cards()),
            "finding_counts": counts,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def write_report_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Construction Workspace Verification",
        "",
        f"- status: {report['status']}",
        f"- scope: {report['scope']}",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    lines.extend(
        f"- {finding['severity']} [{finding['code']}]: {finding['message']}"
        for finding in findings
    )
    if not findings:
        lines.append("- no findings")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--require-dispatch-ready", action="store_true")
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    args = parser.parse_args()

    report = Verifier(
        args.workspace,
        require_dispatch_ready=args.require_dispatch_ready,
    ).verify()
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.report_md:
        write_report_md(args.report_md, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
