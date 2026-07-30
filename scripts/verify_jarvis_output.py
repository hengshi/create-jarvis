#!/usr/bin/env python3
"""Check deterministic Jarvis output boundaries.

This verifier intentionally does not judge jarvis semantics, runtime-
governance maturity, Repository learning quality, work-card progress or
workflow maturity. Those require real evidence. It only catches structural
and filesystem mistakes a program can decide reliably.
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


REQUIRED_JARVIS_FILES = (
    "README.md",
    "MAINTENANCE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SKILL.md",
    "references/jarvis-first-routing.md",
    "references/knowledge-layer-contract.md",
    "references/canonical-repo-fleet.md",
    "references/runtime-governance.md",
    "references/runtime-governance-quick.md",
    "tools/README.md",
)

OBSOLETE_ROOT_CONTRACTS = (
    "jarvis.toml",
    "bootstrap-state.json",
    "bootstrap-result.json",
)

RUNTIME_OWNED_SKILLS = frozenset(
    {
        "create-jarvis",
        "create-jarvis-skill",
        "skill-creator",
        "ponytail",
        "writing-durable-docs",
        "jarvis-self-improve-skill",
        "stop-slop",
        "jarvis-box-doctor",
        "jarvis-box-init",
        "jarvis-box-monitor",
    }
)

TEXT_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".env", ".sh", ".py"}
)
UNRESOLVED_TEMPLATE_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
UNRESOLVED_PATH_TOKENS = ("__JARVIS_", "{{", "}}")
SECRET_RE = re.compile(
    r"(?im)^\s*(?:api[_-]?key|access[_-]?token|password|private[_-]?key|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
)
REQUIRED_RUNTIME_FOUNDATION_CAPABILITIES = (
    "bootstrap",
    "quick_sync",
    "full_sync",
    "discovery_sync",
    "maintenance",
    "self_improve",
    "doctor",
    "recovery",
    "scheduler_adapter",
)
REQUIRED_RUNTIME_FOUNDATION_BOUNDARIES = (
    "runtime_jobs_docker_unaware",
    "box_workspace_owned_separately",
    "box_task_state_untouched",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class Verifier:
    def __init__(
        self,
        jarvis_home: Path,
        repos: list[Path],
        *,
        run_precheck: bool = True,
        expected_jarvis_slug: str | None = None,
        expected_modules: list[str] | None = None,
        expected_sources: list[str] | None = None,
        expected_skills: list[str] | None = None,
        require_runtime_foundation: bool = False,
        runtime_foundation_verifier: Path | None = None,
    ) -> None:
        self.jarvis_home = jarvis_home
        self.repos = repos
        self.run_precheck = run_precheck
        self.expected_jarvis_slug = expected_jarvis_slug
        self.expected_modules = expected_modules or []
        self.expected_sources = expected_sources or []
        self.expected_skills = expected_skills or []
        self.require_runtime_foundation = require_runtime_foundation
        self.runtime_foundation_verifier = runtime_foundation_verifier
        self.findings: list[Finding] = []

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))

    def verify(self) -> dict[str, Any]:
        if not self.jarvis_home.is_dir():
            self.add(
                "blocker",
                "jarvis_home_missing",
                f"Jarvis directory does not exist: {self.jarvis_home}",
            )
            return self.report()

        self.verify_jarvis_structure()
        self.verify_expected_outputs()
        if self.require_runtime_foundation:
            self.verify_runtime_foundation()
        self.verify_repo_boundaries()
        self.verify_filesystem_safety()
        return self.report()

    def verify_jarvis_structure(self) -> None:
        for relative in REQUIRED_JARVIS_FILES:
            self.require_file(
                self.jarvis_home / relative,
                "jarvis_file_missing",
                relative,
            )

        for relative in OBSOLETE_ROOT_CONTRACTS:
            path = self.jarvis_home / relative
            if path.exists():
                self.add(
                    "blocker",
                    "obsolete_contract_present",
                    f"obsolete root contract must not be generated: {relative}",
                )

        skills_root = self.jarvis_home / "skills"
        for name in sorted(RUNTIME_OWNED_SKILLS):
            if (skills_root / name).exists():
                self.add(
                    "blocker",
                    "runtime_skill_copied",
                    f"runtime-owned skill must not be copied into Jarvis repo: {name}",
                )

        if self.expected_jarvis_slug:
            entry = skills_root / f"{self.expected_jarvis_slug}-jarvis" / "SKILL.md"
            self.require_file(
                entry,
                "jarvis_entry_missing",
                str(entry.relative_to(self.jarvis_home)),
            )
            return

        entries = []
        if skills_root.is_dir():
            entries = [
                path
                for path in skills_root.glob("*-jarvis/SKILL.md")
                if path.is_file()
            ]
        if len(entries) != 1:
            self.add(
                "blocker",
                "jarvis_entry_ambiguous",
                "Jarvis repo must contain exactly one skills/<slot>-jarvis/SKILL.md entry",
            )

    def verify_expected_outputs(self) -> None:
        for module in self.expected_modules:
            if not (self.jarvis_home / "modules" / module).is_dir():
                self.add(
                    "blocker",
                    "expected_module_missing",
                    f"expected module missing: {module}",
                )
        for source in self.expected_sources:
            self.require_file(
                self.jarvis_home / "sources" / source / "README.md",
                "expected_source_missing",
                f"sources/{source}/README.md",
            )
        for skill in self.expected_skills:
            self.require_file(
                self.jarvis_home / "skills" / skill / "SKILL.md",
                "expected_skill_missing",
                f"skills/{skill}/SKILL.md",
            )

    def verify_repo_boundaries(self) -> None:
        for repo in self.repos:
            if not repo.is_dir():
                self.add("blocker", "repo_missing", f"repo does not exist: {repo}")
                continue
            if (repo / "skills" / "eval-loop.md").exists():
                self.add(
                    "blocker",
                    "legacy_eval_loop_skill_present",
                    f"Repository learning must not create an eval-loop skill: {repo}",
                )
            if not self.run_precheck:
                continue
            for precheck in sorted((repo / "skills").glob("**/precheck.sh")):
                if not precheck.is_file() or precheck.is_symlink():
                    continue
                try:
                    completed = subprocess.run(
                        ["bash", str(precheck)],
                        cwd=repo,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                except subprocess.TimeoutExpired:
                    self.add(
                        "blocker",
                        "repo_precheck_timeout",
                        f"repo-local precheck timed out: {precheck}",
                    )
                    continue
                if completed.returncode != 0:
                    detail = (completed.stderr or completed.stdout).strip()
                    self.add(
                        "blocker",
                        "repo_precheck_failed",
                        f"repo-local precheck exited {completed.returncode}: {precheck}: {detail}",
                    )

    def verify_runtime_foundation(self) -> None:
        verifier = self.runtime_foundation_verifier or (
            self.jarvis_home / "tools" / "verify-runtime-foundation"
        )
        if not verifier.is_file() or verifier.is_symlink():
            self.add(
                "blocker",
                "runtime_foundation_verifier_missing",
                f"Part 2 requires a regular tools/verify-runtime-foundation implementation: {verifier}",
            )
            return
        if not verifier.stat().st_mode & 0o111:
            self.add(
                "blocker",
                "runtime_foundation_verifier_not_executable",
                f"Runtime Foundation verifier is not executable: {verifier}",
            )
            return
        try:
            completed = subprocess.run(
                [str(verifier), "--static", "--json"],
                cwd=self.jarvis_home,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.add(
                "blocker",
                "runtime_foundation_verifier_failed",
                f"Runtime Foundation verifier could not complete: {exc}",
            )
            return
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            self.add(
                "blocker",
                "runtime_foundation_verifier_failed",
                f"Runtime Foundation verifier exited {completed.returncode}: {detail}",
            )
            return
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.add(
                "blocker",
                "runtime_foundation_verifier_invalid",
                f"Runtime Foundation verifier did not return JSON: {exc}",
            )
            return
        if result.get("schema_version") != 1 or result.get("status") != "pass":
            self.add(
                "blocker",
                "runtime_foundation_verifier_invalid",
                "Runtime Foundation verifier must return schema_version=1 and status=pass",
            )

        capabilities = result.get("capabilities")
        if not isinstance(capabilities, dict):
            self.add(
                "blocker",
                "runtime_foundation_verifier_invalid",
                "Runtime Foundation verifier capabilities must be an object",
            )
            capabilities = {}
        for name in REQUIRED_RUNTIME_FOUNDATION_CAPABILITIES:
            capability = capabilities.get(name)
            if not isinstance(capability, dict) or capability.get("verified") is not True:
                self.add(
                    "blocker",
                    "runtime_foundation_capability_unverified",
                    f"Runtime Foundation capability is not statically verified: {name}",
                )
                continue
            raw_entry = capability.get("entry")
            evidence = capability.get("evidence")
            if not isinstance(raw_entry, str) or not raw_entry.strip():
                self.add(
                    "blocker",
                    "runtime_foundation_entry_invalid",
                    f"Runtime Foundation capability has no source entry: {name}",
                )
                continue
            entry = Path(raw_entry)
            if entry.is_absolute() or ".." in entry.parts:
                self.add(
                    "blocker",
                    "runtime_foundation_entry_invalid",
                    f"Runtime Foundation source entry must be a safe Jarvis-relative path: {name}: {raw_entry}",
                )
                continue
            implementation = self.jarvis_home / entry
            if not implementation.is_file() or implementation.is_symlink():
                self.add(
                    "blocker",
                    "runtime_foundation_entry_missing",
                    f"Runtime Foundation source entry is missing: {name}: {raw_entry}",
                )
            if not isinstance(evidence, list) or not any(
                isinstance(item, str) and item.strip() for item in evidence
            ):
                self.add(
                    "blocker",
                    "runtime_foundation_evidence_missing",
                    f"Runtime Foundation capability has no static evidence: {name}",
                )

        boundaries = result.get("boundaries")
        if not isinstance(boundaries, dict):
            boundaries = {}
        for name in REQUIRED_RUNTIME_FOUNDATION_BOUNDARIES:
            if boundaries.get(name) is not True:
                self.add(
                    "blocker",
                    "runtime_foundation_boundary_unverified",
                    f"Runtime Foundation ownership boundary is not verified: {name}",
                )

    def verify_filesystem_safety(self) -> None:
        roots = [self.jarvis_home, *(repo / "skills" for repo in self.repos)]
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if ".git" in path.parts:
                    continue
                relative_parts = path.relative_to(root).parts
                if any(
                    token in part
                    for part in relative_parts
                    for token in UNRESOLVED_PATH_TOKENS
                ):
                    self.add(
                        "blocker",
                        "template_path_unresolved",
                        f"unresolved template token in generated path: {path}",
                    )
                if path.is_symlink():
                    self.add(
                        "blocker",
                        "symlink_not_allowed",
                        f"generated artifact is a symlink: {path}",
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
                if SECRET_RE.search(text):
                    self.add("blocker", "secret_exposure", f"possible secret in {path}")
                if UNRESOLVED_TEMPLATE_RE.search(text):
                    self.add(
                        "blocker",
                        "template_token_unresolved",
                        f"unresolved template token in {path}",
                    )

    def require_file(self, path: Path, code: str, label: str) -> None:
        if not path.is_file():
            self.add("blocker", code, f"required file missing: {label}")

    def report(self) -> dict[str, Any]:
        counts = {
            severity: sum(1 for finding in self.findings if finding.severity == severity)
            for severity in ("blocker", "major", "minor")
        }
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "pass" if counts["blocker"] == 0 and counts["major"] == 0 else "fail",
            "scope": "deterministic jarvis structure and filesystem safety only",
            "jarvis_home": str(self.jarvis_home),
            "repo_count": len(self.repos),
            "finding_counts": counts,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def discover_repos(customer_repos_dir: Path | None, explicit_repos: list[Path]) -> list[Path]:
    candidates = list(explicit_repos)
    if customer_repos_dir and customer_repos_dir.is_dir():
        candidates.extend(customer_repos_dir.iterdir())
    repos: list[Path] = []
    for repo in candidates:
        resolved = repo.resolve()
        if resolved.is_dir() and (resolved / ".git").exists() and resolved not in repos:
            repos.append(resolved)
    return repos


def write_report_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Jarvis Verification",
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
    parser = argparse.ArgumentParser(
        description="Verify deterministic Jarvis output boundaries."
    )
    parser.add_argument("--jarvis-home", required=True, type=Path)
    parser.add_argument("--customer-repos-dir", type=Path)
    parser.add_argument("--repo", action="append", default=[], type=Path)
    parser.add_argument("--expected-jarvis-slug")
    parser.add_argument("--expected-module", action="append", default=[])
    parser.add_argument("--expected-source", action="append", default=[])
    parser.add_argument("--expected-skill", action="append", default=[])
    parser.add_argument("--skip-precheck", action="store_true")
    parser.add_argument(
        "--require-runtime-foundation",
        action="store_true",
        help="run the Jarvis-owned static Runtime Foundation verifier for Part 2/Reconciliation",
    )
    parser.add_argument("--runtime-foundation-verifier", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    args = parser.parse_args()

    verifier = Verifier(
        args.jarvis_home.resolve(),
        discover_repos(args.customer_repos_dir, args.repo),
        run_precheck=not args.skip_precheck,
        expected_jarvis_slug=args.expected_jarvis_slug,
        expected_modules=args.expected_module,
        expected_sources=args.expected_source,
        expected_skills=args.expected_skill,
        require_runtime_foundation=args.require_runtime_foundation,
        runtime_foundation_verifier=(
            args.runtime_foundation_verifier.resolve()
            if args.runtime_foundation_verifier
            else None
        ),
    )
    report = verifier.verify()
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.report_md:
        write_report_md(args.report_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
