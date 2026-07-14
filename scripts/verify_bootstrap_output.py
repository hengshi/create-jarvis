#!/usr/bin/env python3
"""Verify company Jarvis bootstrap output.

This verifier is intentionally deterministic. It checks that bootstrap output
is structurally safe enough for jarvis-box and later agent work. It does not
decide whether the generated repo truly matches the company Jarvis acceptance
standard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_RESULT_STATUSES = {"in-progress", "completed", "needs-input", "blocked", "failed"}
ALLOWED_STATE_STATUSES = {"in-progress", "completed", "needs-input", "blocked", "failed"}

PHASE_KEYS = tuple(
    [
        "phase-03-bootstrap-invocation",
        "phase-04-bootstrap-intake",
        "phase-05-readiness-gate",
        "phase-06-business-discovery",
        "phase-07-company-jarvis-repo",
        "phase-08-repo-local-skills",
        "phase-09-source-workflow-skills",
        "phase-10-onboarding-report",
        "phase-11-shadow-pilot",
        "phase-12-history-replay",
        "phase-13-controlled-writeback",
        "phase-14-day2-operation",
    ]
)

REQUIRED_DISCOVERY_FILES = [
    "evidence-inventory.md",
    "module-coverage-matrix.md",
    "repo-role-map.md",
    "workflow-map.md",
    "generation-plan.md",
]

PHASE6_PLACEHOLDER_PATTERNS = [
    (r"待\s*Phase\s*6\s*扫描", "phase6_placeholder_cn_scan"),
    (r"待\s*Phase\s*6\s*补充", "phase6_placeholder_cn_supplement"),
    (r"source/repo\s*证据待", "phase6_placeholder_cn_evidence_pending"),
    (r"pending\s+Phase\s*6", "phase6_placeholder_en"),
]

E2E_ABSOLUTE_PATH_RE = re.compile(r"/e2e/")

# ── semantic gate constants ─────────────────────────────────────

# Generic module phrases that indicate no module-specific evidence was actually gathered
GENERIC_MODULE_PHRASE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"本模块相关问题", re.IGNORECASE), "generic_module_phrase_cn_issues"),
    (re.compile(r"首次\s*pilot\s*后填充", re.IGNORECASE), "generic_module_phrase_cn_pilot_fill"),
    (re.compile(r"本模块尚未通过\s*pilot", re.IGNORECASE), "generic_module_phrase_cn_no_pilot"),
    (re.compile(r"本模块尚未.*pilot", re.IGNORECASE), "generic_module_phrase_cn_no_pilot_v2"),
    (re.compile(r"待\s*(?:后续|第一次|首次)\s*(?:pilot|shadow)", re.IGNORECASE), "generic_module_phrase_cn_pending_pilot"),
    (re.compile(r"pending\s+(?:first|initial)\s+pilot", re.IGNORECASE), "generic_module_phrase_en_pending_pilot"),
    (re.compile(r"(?:questions|issues)\s+(?:related\s+to|for)\s+this\s+module", re.IGNORECASE), "generic_module_phrase_en_issues"),
    (re.compile(r"will\s+be\s+(?:filled|populated|determined)\s+(?:after|during)\s+(?:pilot|shadow)", re.IGNORECASE), "generic_module_phrase_en_will_fill"),
]

# Evidence pointer must be <repo>:<repo-relative-path>, no ellipsis/glob/suffix
EVIDENCE_POINTER_ELLIPSIS_RE = re.compile(r"\.\.\.|…")
EVIDENCE_POINTER_GLOB_RE = re.compile(r"[*?\[\]]")

# Phase 11 email pattern for redaction check
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

NONZERO_EXIT_FORBIDDEN_PATTERNS = [
    (
        re.compile(
            r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:decision|primary (?:failure )?classification)(?:\*\*)?\s*:\s*`?no_skill_gap\b|^\s*-\s*\[[xX]\]\s*`?no_skill_gap\b"
        ),
        "nonzero_replay_no_skill_gap",
    ),
    (re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*:\s*`?closed\b"), "nonzero_replay_closed"),
]

NONZERO_EXIT_REQUIRED_PATTERN = re.compile(r"\b(?:defer|deferred|not-evaluated|eval-case-gap)\b", re.IGNORECASE)

PHASE12_REQUIRED_MOUNTS = {
    "/replay/visible": "ro",
    "/replay/worktree": "rw",
    "/replay/company-runtime": "ro",
    "/replay/output": "rw",
}

PILOT_SECTION_PATTERNS = [
    (
        re.compile(
            r"(?im)^#{1,6}\s*(?:PILOT\s+INPUT\s*/\s*START|"
            r"(?:PILOT|试点)\s*输入\s*/\s*(?:START|开始|起始状态))\s*$"
        ),
        "PILOT INPUT / START",
    ),
    (
        re.compile(
            r"(?im)^#{1,6}\s*(?:ROUTE\s*/\s*WORK\s*/\s*VERIFICATION\s+PLAN|"
            r"路由\s*/\s*工作\s*/\s*验证计划)\s*$"
        ),
        "ROUTE / WORK / VERIFICATION PLAN",
    ),
    (
        re.compile(r"(?im)^#{1,6}\s*(?:OBSERVED\s+EXECUTION|观察到的执行|执行观察)\s*$"),
        "OBSERVED EXECUTION",
    ),
    (
        re.compile(
            r"(?im)^#{1,6}\s*(?:END\s*/\s*PILOT\s+EVALUATION|"
            r"结束\s*/\s*试点评估)\s*$"
        ),
        "END / PILOT EVALUATION",
    ),
]


REQUIRED_COMPANY_FILES = [
    "README.md",
    "MAINTENANCE.md",
    "jarvis.toml",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "SKILL.md",
    ".gitignore",
    "bootstrap-state.json",
    "bootstrap-result.json",
    "cross-cutting/module-interactions.md",
    "cross-cutting/peer-product-contracts.md",
    "cross-cutting/version-changelog.md",
    "tools/README.md",
    "evals/evals.json",
]

# Core baseline references: the neutral master set required for every company bootstrap.
# Additional company/product/toolchain/process-specific references must grow from
# Phase 6 evidence, Phase 9 packages, Phase 11 pilot, Phase 12 replay, or Phase 13
# writeback — never pre-installed from the master template.
REQUIRED_REFERENCES = [
    "agent-engineering-quality-gate.md",
    "canonical-repo-fleet.md",
    "capability-delivery-surfaces.md",
    "completion-standard.md",
    "history-replay.md",
    "issue-claim-normalization.md",
    "jarvis-box.md",
    "jarvis-first-routing.md",
    "minimal-closure-card.md",
    "module-boundary-routing.md",
    "next-hop-compression.md",
    "redaction-rules.md",
    "repo-pre-push-review-loop.md",
    "runtime-governance-quick.md",
    "runtime-governance.md",
    "verify-evidence-matrix.md",
    "writeback-governance.md",
]

REQUIRED_MODULE_CONTRACT_FILES = [
    "overview.md",
    "known-issues.md",
    "decisions.md",
    "rejected-features.md",
    "test-coverage.md",
]

HENGSHI_SENSE_MODULE_NAMES = {
    "HQL",
    "app-management",
    "app-market",
    "chart-calculation",
    "charts",
    "connection",
    "data-agent",
    "data-processing",
    "data-service",
    "dataset",
    "deployment",
    "display-controls",
    "embed",
    "filter",
    "indicator",
    "permission",
    "system-admin",
    "visualization",
}

FORBIDDEN_COMPANY_TOP_LEVEL_DIRS = {
    "pilot",
    "repos",
    "rollout",
    "scheduled-jobs",
    "workflows",
    "writeback",
}

REQUIRED_REPO_SKILL_FILES = [
    "skills/SKILL.md",
    "skills/code-review/SKILL.md",
    "skills/code-review/scripts/precheck.sh",
    "skills/references/source-of-truth.md",
    "skills/references/architecture-map.md",
    "skills/references/test-entrypoints.md",
    "skills/references/runtime-and-testability.md",
    "skills/references/history-replay-loop.md",
    "skills/eval-loop.md",
    "skills/self-skills-improve/SKILL.md",
]

TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".env",
    ".json",
    ".md",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}

IGNORED_REPO_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "skills",
    "target",
    "vendor",
}

RAW_SOURCE_DIR_NAMES = {
    "app",
    "cmd",
    "internal",
    "lib",
    "packages",
    "pkg",
    "server",
    "src",
}

FORBIDDEN_PRECHECK_REFERENCES = {
    "hengshi-jarvis",
    "precheck-diff.sh",
    "pullall",
}

SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:token|secret|password|api[_-]?key)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{16,}"
)
BEARER_RE = re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9_./+=:-]{16,}")


@dataclass
class Finding:
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "code": self.code, "message": self.message}


@dataclass
class LeakReason:
    code: str
    message: str


class CaseLeakAnalyzer:
    """Stateless, no-side-effect analyzer that checks a history-replay case for
    oracle leakage.  Used by both preflight gate and final verifier so the same
    rules apply everywhere.

    Only verbatim-provable checks — no natural-language inference, no identifier
    word-splitting, no action-verb blacklists, no outcome-derived provenance
    guessing."""

    # Hidden oracle section heading — only explicit names, not bare "Oracle"
    HIDDEN_ORACLE_HEADING_RE = re.compile(
        r"#+\s*(?:Hidden\s+Outcome\s+Oracle|Hidden\s+Oracle|隐藏结果)",
        re.IGNORECASE,
    )

    # Structured hidden oracle heading markers — only as markdown headings at line start
    _HIDDEN_ORACLE_HEADING_MARKER_RE = re.compile(
        r'^#{1,6}\s+(?:Hidden\s+Outcome\s+Oracle|Hidden\s+Oracle|隐藏结果)',
        re.IGNORECASE | re.MULTILINE,
    )

    # Structured hidden oracle field-label markers — only as bold/structured field labels.
    # Prose mentioning the same words (e.g. "final diff unavailable") does NOT match.
    _HIDDEN_ORACLE_FIELD_MARKER_RE = re.compile(
        r'(?im)^\s*(?:[-*]\s+)?(?:\*\*)?(?:'
        r'Actual\s+outcome|'
        r'Actual\s+[Cc]hanged\s+[Ss]urfaces|'
        r'Final\s+diff\s*/\s*commit\s+pointer|'
        r'Final\s+commit\s+pointer|'
        r'实际变更|'
        r'最终\s*diff'
        r')(?:\*\*)?\s*[:：]',
    )

    # Final commit hash: 7-40 hex chars after a structured label in hidden oracle.
    # Covers: Final commit / Final commit hash / Final diff / commit pointer / 最终 commit
    FINAL_COMMIT_RE = re.compile(
        r"(?:final|最终|actual)\s*(?:diff\s*/\s*commit\s*pointer|commit(?:\s+hash)?|hash|修复\s*commit)[:\s]*([0-9a-f]{7,40})",
        re.IGNORECASE,
    )

    # Actual Changed Surfaces subsection heading within hidden oracle
    _ACTUAL_CHANGED_SURFACES_HEADING_RE = re.compile(
        r'^#+\s*(?:Actual\s+[Cc]hanged\s+[Ss]urfaces|实际变更)',
        re.MULTILINE,
    )

    # Exact file paths inside the already-scoped changed-surfaces field/section.
    _CHANGED_PATH_RE = re.compile(
        r'(?<![A-Za-z0-9_./-])`?(?:\*\*)?'
        r'([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.[A-Za-z]{1,10})'
        r'(?:\*\*)?`?(?![A-Za-z0-9_./-])',
    )

    @classmethod
    def _parse_structured_field(cls, text: str, field_name: str) -> str | None:
        """Parse a structured field like 'Status: ready-for-replay'.
        Returns the value string or None.  Strips markdown formatting from value."""
        pattern = (
            rf'(?im)^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(field_name)}'
            rf'(?:\*\*)?\s*[:：]\s*(\S+(?:\s+\S+)*?)\s*$'
        )
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip().strip('`*_"\'')
        return None

    @classmethod
    def _parse_structured_choice(cls, text: str, field_name: str) -> str | None:
        """Return one explicit choice token, rejecting untouched option lists."""
        value = cls._parse_structured_field(text, field_name)
        if not value:
            return None
        normalized = value.strip().strip('`*_"\'').lower()
        # Strip a human explanation after the one machine-choice token. The
        # checklist commonly uses an em/en dash or a parenthetical note.
        normalized = re.split(r'\s*(?:[—–]|\()\s*', normalized, maxsplit=1)[0]
        normalized = normalized.strip().strip('`*_"\'')
        if any(separator in normalized for separator in (" / ", "|", "<", ">")):
            return None
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", normalized):
            return None
        return normalized

    @classmethod
    def _is_reconstructed_case(cls, case_text: str) -> bool:
        """Check explicit structured fields (START construction, Replay eligibility,
        Eligibility) for reconstructed markers.  No full-text fallback."""
        start_construction = cls._parse_structured_choice(case_text, "START construction")
        if start_construction == "reconstructed-from-outcome-subject":
            return True
        replay_eligibility = cls._parse_structured_choice(case_text, "Replay eligibility")
        if replay_eligibility == "eligible-reconstructed":
            return True
        eligibility = cls._parse_structured_choice(case_text, "Eligibility")
        if eligibility == "eligible-reconstructed":
            return True
        return False

    @classmethod
    def _extract_actual_changed_surfaces(cls, hidden_section: str) -> str:
        """Extract the 'Actual changed surfaces' subsection from hidden oracle section.
        Returns empty string if not found."""
        heading_match = cls._ACTUAL_CHANGED_SURFACES_HEADING_RE.search(hidden_section)
        if heading_match:
            rest = hidden_section[heading_match.end():]
            next_heading = re.search(r"^#{1,4}\s", rest, re.MULTILINE)
            return rest[:next_heading.start()] if next_heading else rest

        field_match = re.search(
            r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?"
            r"(?:Actual\s+[Cc]hanged\s+[Ss]urfaces|实际变更)"
            r"(?:\*\*)?\s*[:：]\s*(.*)$",
            hidden_section,
        )
        if not field_match:
            return ""
        inline_value = field_match.group(1)
        rest = hidden_section[field_match.end():]
        next_field_or_heading = re.search(
            r"(?m)^(?:#{1,6}\s+|\s*[-*]\s+(?:\*\*)?[^\n:：]+(?:\*\*)?\s*[:：])",
            rest,
        )
        continuation = rest[:next_field_or_heading.start()] if next_field_or_heading else rest
        return inline_value + "\n" + continuation

    @classmethod
    def analyze(cls, case_text: str, visible_text: str,
                visible_packet_text: str = "") -> list[LeakReason]:
        """Analyze a case for oracle leakage. Returns a list of LeakReason.
        visible_text should be the Visible START section text.
        visible_packet_text should be all text files under visible-packet/ (recursive).
        Empty list means no leaks found."""
        reasons: list[LeakReason] = []
        full_visible = visible_text + "\n" + visible_packet_text

        # ── 1. Structured hidden oracle heading markers in visible ──
        if cls._HIDDEN_ORACLE_HEADING_MARKER_RE.search(full_visible):
            reasons.append(LeakReason(
                "hidden_oracle_marker_in_visible",
                "hidden oracle heading appears in visible START/packet",
            ))

        # ── 2. Structured hidden oracle field-label markers in visible ──
        for m in cls._HIDDEN_ORACLE_FIELD_MARKER_RE.finditer(full_visible):
            reasons.append(LeakReason(
                "hidden_oracle_marker_in_visible",
                f"hidden oracle field label '{m.group(0).strip()}' appears in visible START/packet",
            ))

        # ── 3. Extract hidden oracle section ──
        hidden_section = ""
        hidden_m = cls.HIDDEN_ORACLE_HEADING_RE.search(case_text)
        if hidden_m:
            hidden_start = hidden_m.end()
            hidden_rest = case_text[hidden_start:]
            next_heading = re.search(r"^#{1,2}\s", hidden_rest, re.MULTILINE)
            if next_heading:
                hidden_section = hidden_rest[:next_heading.start()]
            else:
                hidden_section = hidden_rest

        if not hidden_section:
            return reasons

        # ── 4. Final commit hash verbatim in visible ──
        for commit_match in cls.FINAL_COMMIT_RE.finditer(hidden_section):
            commit_hash = commit_match.group(1)
            if commit_hash in full_visible:
                reasons.append(LeakReason(
                    "final_commit_hash_in_visible",
                    f"final commit hash '{commit_hash}' from hidden oracle appears verbatim in visible START/packet",
                ))

        # ── 5. Changed path leakage: only for reconstructed cases ──
        # eligible-direct / direct-pre-fix / parent-observed: paths may be
        # pre-outcome facts — no changed-path leakage inference.
        # Only scan the Actual Changed Surfaces subsection, not all hidden-oracle bullets.
        if cls._is_reconstructed_case(case_text):
            changed_surfaces = cls._extract_actual_changed_surfaces(hidden_section)
            for path_match in cls._CHANGED_PATH_RE.finditer(changed_surfaces):
                path = path_match.group(1).strip()
                if len(path) > 4 and path in full_visible:
                    reasons.append(LeakReason(
                        "changed_path_in_visible",
                        f"hidden oracle changed path '{path}' appears verbatim in visible START/packet (reconstructed case)",
                    ))

        return reasons


class Verifier:
    def __init__(
        self,
        jarvis_home: Path,
        repos: list[Path],
        run_precheck: bool,
        expected_company_slug: str | None = None,
        expected_product_identity: str | None = None,
        expected_modules: list[str] | None = None,
        expected_sources: list[str] | None = None,
        expected_skills: list[str] | None = None,
        jarvis_box_help_file: Path | None = None,
        replay_bridge_helper: Path | None = None,
        stage: str = "final",
        case_id: str | None = None,
    ) -> None:
        self.jarvis_home = jarvis_home
        self.repos = repos
        self.run_precheck = run_precheck
        self.expected_company_slug = expected_company_slug
        self.expected_product_identity = expected_product_identity
        self.expected_modules = expected_modules or []
        self.expected_sources = expected_sources or []
        self.expected_skills = expected_skills or []
        self.jarvis_box_help_file = jarvis_box_help_file
        self.replay_bridge_helper = replay_bridge_helper
        self.stage = stage
        self.case_id = case_id
        self.findings: list[Finding] = []

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))

    def verify(self) -> dict[str, Any]:
        if self.stage == "phase-12-preflight":
            return self._verify_phase12_preflight()
        if self.stage == "phase-09":
            self._verify_phase09()
        else:
            self.verify_company_home()
            result = self.verify_bootstrap_result()
            state = self.verify_bootstrap_state()
            self.verify_identity_reconciliation(result, state)
            self.verify_company_slug(result, state)
            self.verify_expected_customer_facts(result, state)
            self.verify_repo_skill_packages()
            self.verify_history_replay_contract(result, state)
            self.verify_replay_bridge_contract(result)
            self._check_replay_exit_code_decisions()
            self._check_replay_zero_exit_artifacts()
            if self._is_phase12_completed(result, state):
                self._check_phase12_completed_requirements()
            self.verify_source_dump_resistance()
            self.verify_secret_boundary()
            self.verify_discovery_artifacts()
            self.verify_phase6_placeholders()
            self.verify_durable_e2e_paths()
            self.verify_precise_module_claims()
            self.verify_day2_operation()
            self.verify_jarvis_box_commands()
            self._check_root_placeholders(result, state)
            # Phase 9 customer-fact checks also apply to final stage
            self._verify_customer_fact_safety()
            self._verify_module_evidence_pointers()
            self._verify_crosscutting_fact_safety()
            self._verify_routing_repo_mentions()
            self._verify_deferred_source_inputs(result, state)
            self._verify_replay_decision_contradictions(result)
            self._verify_oracle_inspection_gaps(result)
            self._verify_durable_e2e_customer_paths()
            # semantic gate checks
            self._verify_generic_module_phrases()
            self._verify_route_section_duplication()
            self._verify_routing_repo_evidence_consistency()
            self._verify_replay_leaked_start()
            self._verify_phase_status_consistency(result, state)
            self._verify_phase_progression(result, state)
            self._verify_missing_input_contradictions(result, state)
            self._verify_pilot_email_redaction()
            self._verify_day2_runtime_root_consistency(result, state)
            # deterministic guards (r9)
            self._verify_discovery_retrieval_commands()
            self._verify_discovery_evidence_pointers()
            self._verify_confirmed_product_identity_unresolved(result, state)
            self._verify_company_entry_references_and_handoffs()
            self._verify_source_route_filling(result, state)
            self._verify_repo_local_truth()
            self._verify_pilot_structure(result, state)
            self._verify_shadow_pilot_repo_scan(result, state)
            self._verify_history_replay_repo_scan(result, state)

        blocker_count = sum(1 for finding in self.findings if finding.severity == "blocker")
        major_count = sum(1 for finding in self.findings if finding.severity == "major")
        minor_count = sum(1 for finding in self.findings if finding.severity == "minor")
        status = "pass" if blocker_count == 0 and major_count == 0 else "fail"
        result = None
        try:
            result = self.load_json(self.jarvis_home / "bootstrap-result.json", "bootstrap-result.json")
        except Exception:
            pass
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "scope": "machine checks only; final acceptance is acceptance.md",
            "jarvis_home": str(self.jarvis_home),
            "repo_count": len(self.repos),
            "bootstrap_status": result.get("status") if isinstance(result, dict) else None,
            "finding_counts": {
                "blocker": blocker_count,
                "major": major_count,
                "minor": minor_count,
            },
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def verify_company_home(self) -> None:
        if not self.jarvis_home.exists():
            self.add("blocker", "jarvis_home_missing", f"JARVIS_HOME does not exist: {self.jarvis_home}")
            return
        if not self.jarvis_home.is_dir():
            self.add("blocker", "jarvis_home_not_dir", f"JARVIS_HOME is not a directory: {self.jarvis_home}")
            return
        for rel_path in REQUIRED_COMPANY_FILES:
            path = self.jarvis_home / rel_path
            if not path.exists():
                self.add("blocker", "company_file_missing", f"required company Jarvis file missing: {rel_path}")
            elif not path.is_file():
                self.add("blocker", "company_file_not_file", f"required company Jarvis path is not a file: {rel_path}")
        # Check 17 core baseline references
        refs_dir = self.jarvis_home / "references"
        if refs_dir.is_dir():
            for ref in REQUIRED_REFERENCES:
                ref_path = refs_dir / ref
                if not ref_path.is_file():
                    self.add("blocker", "reference_missing", f"required reference missing: references/{ref}")
        else:
            self.add("blocker", "references_dir_missing", "references/ directory is missing")
        for dir_name in sorted(FORBIDDEN_COMPANY_TOP_LEVEL_DIRS):
            if (self.jarvis_home / dir_name).exists():
                self.add(
                    "blocker",
                    "company_topology_not_hengshi_shaped",
                    f"top-level {dir_name}/ is not part of the hengshi-jarvis-shaped company repo core; move this material into skills/, references/, sources/, evals/, tools/, or bootstrap reports",
                )
        self.verify_company_entry_skill()
        self.verify_module_and_source_shape()
        self._verify_install_owned_skills_not_copied()
        self._verify_workflow_scaffolds_not_isomorphic()
        self._verify_root_readme_semantics()
        self._verify_maintenance_semantics()
        self._verify_jarvis_toml()

    def verify_company_entry_skill(self) -> None:
        skill_files = list((self.jarvis_home / "skills").glob("*/SKILL.md"))
        jarvis_skills = [path for path in skill_files if "jarvis" in path.parent.name.lower()]
        if not jarvis_skills:
            self.add(
                "blocker",
                "company_entry_skill_missing",
                "company Jarvis entry skill must live under skills/<company>-jarvis/SKILL.md, matching hengshi-jarvis repo shape",
            )
            return
        for path in jarvis_skills:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.add("blocker", "company_entry_skill_unreadable", f"company entry skill cannot be read: {path}")
                continue
            required_patterns = {
                "entry_skill_runtime_quick_ref_missing": r"runtime-governance-quick\.md",
                "entry_skill_workflow_first_missing": r"workflow-first|Workflow-first|优先按闭环|不要先按仓库|先按闭环",
                "entry_skill_artifact_first_missing": r"artifact-first|Artifact-first|先读 artifact|明确 artifact|issue/MR/error/screenshot|failing test",
                "entry_skill_repo_local_truth_missing": r"repo-local.*truth|repo execution truth|repo-local execution|仓库内部工程执行方法",
                "entry_skill_capability_surface_missing": r"capability owner|delivery surface|交付面|capability.*delivery",
                "entry_skill_end_writeback_missing": r"END.*writeback|writeback.*END|END.*回写|回写.*END",
            }
            for code, pattern in required_patterns.items():
                if not re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                    self.add(
                        "blocker",
                        code,
                        f"{path.relative_to(self.jarvis_home)} does not preserve required hengshi-jarvis entry behavior: {code}",
                    )

    def verify_module_and_source_shape(self) -> None:
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.exists() or not modules_dir.is_dir():
            self.add("blocker", "modules_dir_missing", "company Jarvis repo must have modules/ like hengshi-jarvis")
        elif not list(modules_dir.glob("*/overview.md")):
            self.add("blocker", "module_overview_missing", "modules/ must contain at least one evidence-backed <module>/overview.md")
        else:
            for module_dir in sorted(path for path in modules_dir.iterdir() if path.is_dir()):
                for filename in REQUIRED_MODULE_CONTRACT_FILES:
                    if not (module_dir / filename).is_file():
                        self.add(
                            "blocker",
                            "module_contract_file_missing",
                            f"{module_dir.name}: required module contract file missing: {filename}",
                        )
                overview = module_dir / "overview.md"
                if overview.is_file():
                    try:
                        overview_text = overview.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        self.add("major", "module_overview_unreadable", f"{module_dir.name}: overview.md cannot be read")
                        continue
                    if module_dir.name in HENGSHI_SENSE_MODULE_NAMES and not re.search(
                        r"evidence|证据|source-of-truth|source pointer|source-detected",
                        overview_text,
                        re.IGNORECASE,
                    ):
                        self.add(
                            "major",
                            "hengshi_module_name_without_evidence",
                            f"module name matches a Hengshi Sense default but overview.md does not show explicit customer evidence: {module_dir.name}",
                        )
                    for code, pattern in {
                        "module_evidence_missing": r"evidence|证据",
                        "module_confidence_missing": r"confidence|confirmed|likely|needs-input|置信",
                        "module_owner_status_missing": r"owner|status|确认|负责人|needs-owner-confirmation",
                    }.items():
                        if not re.search(pattern, overview_text, re.IGNORECASE):
                            self.add("blocker", code, f"{module_dir.name}: overview.md missing {code}")
        sources_dir = self.jarvis_home / "sources"
        if not sources_dir.exists() or not sources_dir.is_dir():
            self.add("blocker", "sources_dir_missing", "company Jarvis repo must have sources/ like hengshi-jarvis")
        elif not list(sources_dir.glob("*/README.md")):
            self.add("blocker", "source_readme_missing", "sources/ must contain at least one source route README.md")

    def verify_bootstrap_result(self) -> dict[str, Any] | None:
        result = self.load_json(self.jarvis_home / "bootstrap-result.json", "bootstrap-result.json")
        if result is None:
            return None
        status = result.get("status")
        if status not in ALLOWED_RESULT_STATUSES:
            self.add("blocker", "result_status_invalid", f"bootstrap-result.json has invalid status: {status!r}")
        if status == "completed" and result.get("result_code") not in {"ok", "completed", None, ""}:
            self.add("major", "result_code_unexpected", f"completed bootstrap has unexpected result_code: {result.get('result_code')!r}")
        for field in ["summary", "paths", "missing_inputs", "blockers"]:
            if field not in result:
                self.add("blocker", "result_field_missing", f"bootstrap-result.json missing required field: {field}")
        paths = result.get("paths")
        if isinstance(paths, dict):
            for field in ["jarvis_home", "jarvis_target_home", "entry_skill"]:
                if not paths.get(field):
                    self.add("blocker", "result_path_missing", f"bootstrap-result.json paths.{field} is missing")
            non_string_paths = [field for field, value in paths.items() if not isinstance(value, str)]
            if non_string_paths:
                self.add(
                    "blocker",
                    "result_path_value_invalid",
                    "bootstrap-result.json paths values must all be strings; invalid fields: "
                    + ", ".join(sorted(non_string_paths)),
                )
            entry = paths.get("entry_skill", "SKILL.md")
            if isinstance(entry, str) and not self.entry_skill_exists(entry):
                self.add("blocker", "entry_skill_missing", f"entry skill declared by bootstrap-result.json is missing: {entry}")
        else:
            self.add("blocker", "result_paths_invalid", "bootstrap-result.json paths must be an object")
        for list_field in ["missing_inputs", "blockers", "conflicting_inputs", "unresolved_questions"]:
            if list_field in result and not isinstance(result[list_field], list):
                self.add("blocker", "result_list_invalid", f"bootstrap-result.json {list_field} must be a list")
            elif list_field in result:
                invalid_items = [item for item in result[list_field] if not isinstance(item, str)]
                if invalid_items:
                    self.add(
                        "blocker",
                        "result_list_item_invalid",
                        f"bootstrap-result.json {list_field} must contain only strings",
                    )
        for file_list_field in ["created_files", "updated_files", "preserved_files"]:
            if file_list_field in result:
                if not isinstance(result[file_list_field], list):
                    self.add("blocker", "result_file_list_invalid", f"bootstrap-result.json {file_list_field} must be a list")
                elif any(not isinstance(item, str) for item in result[file_list_field]):
                    self.add(
                        "blocker",
                        "result_file_list_item_invalid",
                        f"bootstrap-result.json {file_list_field} must contain only strings",
                    )
        if status == "completed":
            for list_field in ["missing_inputs", "blockers", "conflicting_inputs"]:
                values = result.get(list_field)
                if values:
                    self.add(
                        "blocker",
                        "completed_with_open_required_inputs",
                        f"bootstrap-result.json status is completed but {list_field} is not empty",
                    )
        blockers = result.get("blockers")
        if isinstance(blockers, list) and any(
            isinstance(value, str)
            and re.search(r"runtime root|JARVIS_RUNTIME_ROOT|runtime_root", value, re.IGNORECASE)
            and re.search(r"missing|does not exist|not exist|缺失|不存在", value, re.IGNORECASE)
            for value in blockers
        ):
            self.add(
                "blocker",
                "runtime_root_missing",
                "bootstrap-result.json still reports missing runtime root; install/setup or readiness gate must create it before Phase 6",
            )
        return result

    def verify_history_replay_contract(self, result: dict[str, Any] | None, state: dict[str, Any] | None) -> None:
        registry = self.jarvis_home / "evals" / "history-replay" / "replay-case-registry.md"
        case_files = list((self.jarvis_home / "evals" / "history-replay" / "cases").glob("*/history-replay-case.md"))
        if not registry.exists():
            if case_files:
                self.add("blocker", "history_replay_registry_missing", "history replay cases exist but replay-case-registry.md is missing")
            text = ""
        else:
            try:
                text = registry.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.add("major", "history_replay_registry_unreadable", "history replay registry cannot be read")
                text = ""

        def case_ready_for_replay(text: str) -> bool:
            return (
                CaseLeakAnalyzer._parse_structured_choice(text, "Status")
                == "ready-for-replay"
            )

        def case_is_ineligible(text: str) -> bool:
            """True if the case has explicit ineligible-leaky, low-confidence,
            needs-better-start, or blocked in structured Eligibility / Replay eligibility fields.
            No full-text fallback."""
            eligibility_val = CaseLeakAnalyzer._parse_structured_choice(text, "Eligibility")
            replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(text, "Replay eligibility")
            effective = eligibility_val or replay_eligibility_val
            ineligible_markers = {"ineligible-leaky", "needs-better-start", "low-confidence", "blocked"}
            return effective in ineligible_markers

        mentions_candidates = bool(re.search(r"\b[cC]andidate\b|候选", text))
        if mentions_candidates and not case_files:
            self.add(
                "blocker",
                "history_replay_candidates_without_cases",
                "history replay registry identifies candidates but no cases/<case-id>/history-replay-case.md files exist",
            )
        for case_file in case_files:
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.add("major", "history_replay_case_unreadable", f"history replay case cannot be read: {case_file}")
                continue
            if case_ready_for_replay(case_text) and case_is_ineligible(case_text):
                self.add(
                    "blocker",
                    "history_replay_low_confidence_ready_for_replay",
                    f"{case_file.parent.name}: low-confidence/ineligible history replay case must not be marked ready-for-replay",
                )
            # blocker: ineligible case that actually started replay
            case_id = case_file.parent.name
            run_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id
            if case_is_ineligible(case_text) and (run_dir / "exit-code").is_file():
                self.add(
                    "blocker",
                    "history_replay_ineligible_case_started_replay",
                    f"{case_id}: ineligible-leaky/low-confidence/needs-better-start case must not start replay; expand search or query authorized sources first",
                )
            # blocker: visible packet checked via shared CaseLeakAnalyzer
            if (run_dir / "exit-code").is_file():
                visible_prompt = run_dir / "visible-packet" / "replay-prompt.md"
                if visible_prompt.is_file():
                    try:
                        visible_text = visible_prompt.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        visible_text = ""
                    # Use CaseLeakAnalyzer for verbatim leak detection on visible packet
                    visible_start = ""
                    visible_start_file = case_file
                    if visible_start_file.is_file():
                        try:
                            case_full = visible_start_file.read_text(encoding="utf-8", errors="replace")
                            vs = self._extract_section(
                                case_full,
                                r"#+\s*(?:visible\s*START|visible\s*start|START)",
                                r"#+\s*(?:[Hh]idden\s+[Oo]utcome\s+[Oo]racle|[Hh]idden\s+[Oo]racle|隐藏结果)",
                            )
                            visible_start = vs or ""
                        except OSError:
                            pass
                    try:
                        case_text_full = case_file.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        case_text_full = ""
                    leak_reasons = CaseLeakAnalyzer.analyze(case_text_full, visible_start, visible_text)
                    if leak_reasons:
                        self.add(
                            "blocker",
                            "history_replay_visible_packet_oracle_leak",
                            f"{case_id}: visible packet contains verbatim oracle leak — must contain only pre-outcome facts",
                        )
                        for lr in leak_reasons:
                            self.add("major", f"history_replay_leak_detail_{lr.code}", f"{case_id}: {lr.message}")
        def replay_cli_available(text: str) -> bool:
            normalized = re.sub(r"[*`]", "", text.lower())
            return bool(
                re.search(
                    r"(isolated replay possible|can execute isolated replay)\??\s*:\s*yes",
                    normalized,
                    re.IGNORECASE,
                )
            )

        cli_check_texts: list[str] = []
        cli_checks_by_case: dict[str, str] = {}
        for checks_path in (self.jarvis_home / "_bootstrap" / "history-replay-runs").glob("*/replay-agent-cli-checks.md"):
            try:
                text = checks_path.read_text(encoding="utf-8", errors="replace")
                cli_check_texts.append(text)
                cli_checks_by_case[checks_path.parent.name] = text
            except OSError:
                self.add("major", "history_replay_cli_checks_unreadable", f"CLI checks cannot be read: {checks_path}")
        isolated_agent_available = any(replay_cli_available(text) for text in cli_check_texts)
        needs_isolated_agent = False
        result_open_items = ""
        if isinstance(result, dict):
            for field in ["missing_inputs", "blockers", "unresolved_questions"]:
                values = result.get(field)
                if isinstance(values, list):
                    result_open_items += "\n".join(value for value in values if isinstance(value, str)) + "\n"
                if isinstance(values, list) and any(
                    isinstance(value, str)
                    and "isolated replay agent" in value.lower()
                    and re.search(
                        r"\bmissing\b|\bnot found\b|\bunavailable\b|\bnot available\b|\bno isolated replay agent\b|缺|没有|不可用",
                        value,
                        re.IGNORECASE,
                    )
                    for value in values
                ):
                    needs_isolated_agent = True
                    break
        if isolated_agent_available and needs_isolated_agent:
            self.add(
                "blocker",
                "isolated_replay_agent_reported_missing_but_available",
                "CLI checks report an isolated replay agent is available, but bootstrap-result.json still says an isolated replay agent is missing",
            )
        if case_files:
            case_texts = []
            for case_file in case_files:
                try:
                    case_texts.append(case_file.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    continue
            all_cases_need_better_start = bool(case_texts) and all(
                (
                    CaseLeakAnalyzer._parse_structured_choice(t, "Eligibility")
                    or CaseLeakAnalyzer._parse_structured_choice(t, "Replay eligibility")
                ) in {"needs-better-start", "low-confidence"}
                for t in case_texts
            )
            for case_file, case_text in zip(case_files, case_texts, strict=False):
                case_id = case_file.parent.name
                checks_text = cli_checks_by_case.get(case_id, "")
                if case_ready_for_replay(case_text) and not checks_text:
                    self.add(
                        "blocker",
                        "history_replay_ready_case_missing_cli_checks",
                        f"{case_id}: ready-for-replay case must have replay-agent-cli-checks.md",
                    )
                    continue
                if not checks_text or not replay_cli_available(checks_text):
                    continue
                if not case_ready_for_replay(case_text):
                    continue
                run_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id
                replay_result = run_dir / "replay-result.md"
                replay_stdout = run_dir / "replay-agent.jsonl"
                replay_stderr = run_dir / "replay-agent.stderr.log"
                has_stdout = replay_stdout.is_file() and replay_stdout.stat().st_size > 0
                has_stderr = replay_stderr.is_file() and replay_stderr.stat().st_size > 0
                has_result = replay_result.is_file() and replay_result.stat().st_size > 0
                if not has_result and not has_stdout and not has_stderr:
                    self.add(
                        "blocker",
                        "history_replay_ready_case_not_executed_with_available_cli",
                        f"{case_id}: CLI checks say isolated replay can execute, but replay-agent output, stderr, and replay-result are all missing or empty",
                    )
            replay_results = list((self.jarvis_home / "_bootstrap" / "history-replay-runs").glob("*/replay-result.md"))
            for replay_result in replay_results:
                if not replay_result.is_file() or replay_result.stat().st_size == 0:
                    continue
                case_id = replay_result.parent.name
                case_dir = self.jarvis_home / "evals" / "history-replay" / "cases" / case_id
                if not case_dir.is_dir():
                    continue
                for filename in ["replay-failure-analysis.md", "skill-update-decision.md"]:
                    if not (case_dir / filename).is_file():
                        self.add(
                            "blocker",
                            "history_replay_case_calibration_file_missing",
                            f"{case_id}: replay-result.md exists but evals/history-replay/cases/{case_id}/{filename} is missing",
                        )
            if all_cases_need_better_start and not replay_results and not re.search(
                r"better\s+START|needs-better-start|low-confidence|original issue|original MR|原始|初始信号",
                result_open_items,
                re.IGNORECASE,
            ):
                self.add(
                    "blocker",
                    "history_replay_needs_better_start_not_reported",
                    "all replay cases need a better START, but bootstrap-result.json missing_inputs does not say that",
                )
        if needs_isolated_agent and case_files:
            missing_cli_checks = []
            for case_file in case_files:
                case_id = case_file.parent.name
                checks_path = (
                    self.jarvis_home
                    / "_bootstrap"
                    / "history-replay-runs"
                    / case_id
                    / "replay-agent-cli-checks.md"
                )
                if not checks_path.is_file():
                    missing_cli_checks.append(case_id)
            if missing_cli_checks:
                self.add(
                    "blocker",
                    "isolated_replay_agent_missing_without_cli_checks",
                    "bootstrap-result.json says isolated replay agent is missing but CLI checks are missing for cases: "
                    + ", ".join(sorted(missing_cli_checks)),
                )
        phase_maps: list[tuple[str, dict[str, Any]]] = []
        result_phase_status = None
        if isinstance(result, dict):
            phase_summary = result.get("phase_summary")
            if isinstance(phase_summary, dict):
                phase_maps.append(("bootstrap-result.json phase_summary", phase_summary))
                result_phase_status = phase_summary.get("phase-12-history-replay")
        if isinstance(state, dict):
            phase_statuses = state.get("phase_status")
            if isinstance(phase_statuses, dict):
                phase_maps.append(("bootstrap-state.json phase_status", phase_statuses))
        for source, phase_map in phase_maps:
            phase12 = phase_map.get("phase-12-history-replay")
            if phase12 and phase12 != "completed":
                for downstream in ["phase-13-controlled-writeback", "phase-14-day2-operation"]:
                    if phase_map.get(downstream) == "completed":
                        self.add(
                            "blocker",
                            "downstream_phase_completed_after_incomplete_history_replay",
                            f"{source} marks {downstream} completed while phase-12-history-replay is {phase12!r}",
                        )
            if isinstance(result, dict) and result.get("status") != "completed":
                if phase_map.get("phase-14-day2-operation") == "completed":
                    self.add(
                        "blocker",
                        "day2_phase_completed_while_bootstrap_not_completed",
                        f"{source} marks phase-14-day2-operation completed while bootstrap-result.json status is {result.get('status')!r}",
                    )
        completed = bool(result and result.get("status") == "completed") or result_phase_status == "completed"
        if isinstance(state, dict):
            phase_statuses = state.get("phase_status")
            if isinstance(phase_statuses, dict):
                completed = completed or phase_statuses.get("phase-12-history-replay") == "completed"
        if completed and case_files:
            missing_run_artifacts = []
            for case_file in case_files:
                case_id = case_file.parent.name
                run_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id
                if not (run_dir / "visible-packet").is_dir() or not (run_dir / "replay-result.md").is_file():
                    missing_run_artifacts.append(case_id)
            if missing_run_artifacts:
                self.add(
                    "blocker",
                    "completed_history_replay_without_isolated_run",
                    "Phase 12 is completed but isolated replay artifacts are missing for cases: "
                    + ", ".join(sorted(missing_run_artifacts)),
                )

    def entry_skill_exists(self, entry: str) -> bool:
        entry_path = Path(entry)
        if entry_path.is_absolute():
            if entry_path.exists():
                return True
            return entry_path.name == "SKILL.md" and (self.jarvis_home / "SKILL.md").exists()
        return (self.jarvis_home / entry_path).exists()

    def verify_bootstrap_state(self) -> dict[str, Any] | None:
        state = self.load_json(self.jarvis_home / "bootstrap-state.json", "bootstrap-state.json")
        if state is None:
            return None
        status = state.get("status")
        if status and status not in ALLOWED_STATE_STATUSES:
            self.add("blocker", "state_status_invalid", f"bootstrap-state.json has invalid status: {status!r}")
        for field in ["phase", "paths", "confirmed_answers", "method_repo"]:
            if field not in state:
                self.add("major", "state_field_missing", f"bootstrap-state.json missing field useful for resume: {field}")
        if "confirmed_answers" in state and not isinstance(state["confirmed_answers"], dict):
            self.add("blocker", "state_confirmed_answers_invalid", "bootstrap-state.json confirmed_answers must be an object")
        return state

    def verify_identity_reconciliation(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        if state is None:
            return
        identity = state.get("identity_reconciliation")
        if identity is None:
            severity = "blocker" if result and result.get("status") == "completed" else "major"
            self.add(severity, "identity_reconciliation_missing", "bootstrap-state.json missing identity_reconciliation")
            return
        if not isinstance(identity, dict):
            self.add("blocker", "identity_reconciliation_invalid", "bootstrap-state.json identity_reconciliation must be an object")
            return
        identity_status = identity.get("status")
        if result and result.get("status") == "completed" and identity_status not in {"confirmed"}:
            self.add(
                "blocker",
                "completed_with_unconfirmed_identity",
                f"bootstrap-result.json is completed but identity_reconciliation.status is {identity_status!r}",
            )

    def verify_company_slug(self, result: dict[str, Any] | None, state: dict[str, Any] | None) -> None:
        if not self.expected_company_slug:
            return
        expected = self.expected_company_slug
        expected_entry = f"skills/{expected}-jarvis/SKILL.md"
        if state:
            inputs = state.get("inputs")
            if isinstance(inputs, dict) and inputs.get("company_slug") != expected:
                self.add(
                    "blocker",
                    "company_slug_mismatch",
                    f"bootstrap-state.json inputs.company_slug is {inputs.get('company_slug')!r}, expected {expected!r}",
                )
            paths = state.get("paths")
            if isinstance(paths, dict):
                entry = paths.get("entry_skill")
                if isinstance(entry, str) and entry != expected_entry:
                    self.add(
                        "blocker",
                        "company_entry_slug_mismatch",
                        f"bootstrap-state.json paths.entry_skill is {entry!r}, expected {expected_entry!r}",
                    )
        if result:
            paths = result.get("paths")
            if isinstance(paths, dict):
                entry = paths.get("entry_skill")
                if isinstance(entry, str) and entry != expected_entry:
                    self.add(
                        "blocker",
                        "company_entry_slug_mismatch",
                        f"bootstrap-result.json paths.entry_skill is {entry!r}, expected {expected_entry!r}",
                    )
        jarvis_toml = self.jarvis_home / "jarvis.toml"
        if jarvis_toml.exists():
            try:
                text = jarvis_toml.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.add("major", "jarvis_toml_unreadable", "jarvis.toml cannot be read")
                return
            slug_match = re.search(r'(?m)^\s*company_slug\s*=\s*"([^"]+)"\s*$', text)
            if slug_match and slug_match.group(1) != expected:
                self.add(
                    "blocker",
                    "company_slug_mismatch",
                    f"jarvis.toml runtime.company_slug is {slug_match.group(1)!r}, expected {expected!r}",
                )
            entry_match = re.search(r'(?m)^\s*entry_skill\s*=\s*"([^"]+)"\s*$', text)
            if entry_match and entry_match.group(1) != expected_entry:
                self.add(
                    "blocker",
                    "company_entry_slug_mismatch",
                    f"jarvis.toml entry_skill is {entry_match.group(1)!r}, expected {expected_entry!r}",
                )

    def verify_expected_customer_facts(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        if self.expected_product_identity:
            expected = self.expected_product_identity
            search_parts = []
            for obj in [result, state]:
                if isinstance(obj, dict):
                    search_parts.append(json.dumps(obj, ensure_ascii=False))
            for rel_path in ["README.md", "MAINTENANCE.md"]:
                path = self.jarvis_home / rel_path
                if path.exists():
                    try:
                        search_parts.append(path.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
            if self.expected_company_slug:
                entry_path = self.jarvis_home / "skills" / f"{self.expected_company_slug}-jarvis" / "SKILL.md"
                if entry_path.exists():
                    try:
                        search_parts.append(entry_path.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
            search_text = "\n".join(search_parts)
            if expected.lower() not in search_text.lower():
                self.add(
                    "blocker",
                    "expected_product_identity_missing",
                    f"expected confirmed product identity {expected!r} is not present in generated Jarvis output",
                )
            unresolved_text = ""
            if isinstance(result, dict):
                for field in ["missing_inputs", "conflicting_inputs", "unresolved_questions"]:
                    values = result.get(field)
                    if isinstance(values, list):
                        unresolved_text += "\n".join(value for value in values if isinstance(value, str)) + "\n"
            if expected.lower() in unresolved_text.lower():
                self.add(
                    "blocker",
                    "expected_product_identity_unresolved",
                    f"expected confirmed product identity {expected!r} still appears in missing/conflicting/unresolved result fields",
                )

        module_names = self.exact_child_dir_names(self.jarvis_home / "modules")
        for module in self.expected_modules:
            module_path = self.jarvis_home / "modules" / module / "overview.md"
            if module not in module_names or not module_path.is_file():
                self.add(
                    "blocker",
                    "expected_module_missing",
                    f"expected customer module is missing or lacks overview.md: modules/{module}",
                )

        source_names = self.exact_child_dir_names(self.jarvis_home / "sources")
        for source in self.expected_sources:
            source_path = self.jarvis_home / "sources" / source / "README.md"
            if source not in source_names or not source_path.is_file():
                self.add(
                    "blocker",
                    "expected_source_missing",
                    f"expected customer source route is missing: sources/{source}/README.md",
                )

        skill_names = self.exact_child_dir_names(self.jarvis_home / "skills")
        for skill in self.expected_skills:
            skill_path = self.jarvis_home / "skills" / skill / "SKILL.md"
            if skill not in skill_names or not skill_path.is_file():
                self.add(
                    "blocker",
                    "expected_skill_missing",
                    f"expected customer skill is missing: skills/{skill}/SKILL.md",
                )

    def exact_child_dir_names(self, path: Path) -> set[str]:
        try:
            return {child.name for child in path.iterdir() if child.is_dir()}
        except OSError:
            return set()

    def verify_repo_skill_packages(self) -> None:
        if not self.repos:
            self.add("major", "repos_missing", "no customer repos were provided for repo-local skill verification")
            return
        for repo in self.repos:
            repo_name = repo.name
            if not (repo / ".git").exists():
                self.add("major", "repo_not_git", f"customer repo is not a git checkout: {repo}")
            for rel_path in REQUIRED_REPO_SKILL_FILES:
                path = repo / rel_path
                if not path.exists():
                    self.add("blocker", "repo_skill_file_missing", f"{repo_name}: required repo-local skill file missing: {rel_path}")
                elif not path.is_file():
                    self.add("blocker", "repo_skill_file_not_file", f"{repo_name}: required repo-local skill path is not a file: {rel_path}")
            if self.run_precheck:
                self.verify_precheck(repo)

    def verify_precheck(self, repo: Path) -> None:
        precheck = repo / "skills" / "code-review" / "scripts" / "precheck.sh"
        repo_name = repo.name
        if not precheck.exists():
            return
        try:
            precheck_text = precheck.read_text(encoding="utf-8", errors="replace")
        except OSError:
            self.add("blocker", "precheck_unreadable", f"{repo_name}: precheck is not readable: {precheck.relative_to(repo)}")
            return
        forbidden_refs = [ref for ref in sorted(FORBIDDEN_PRECHECK_REFERENCES) if ref in precheck_text]
        if forbidden_refs:
            self.add(
                "blocker",
                "precheck_reference_company_dependency",
                f"{repo_name}: precheck must be self-contained for the customer repo; forbidden references: {', '.join(forbidden_refs)}",
            )
            return
        if not os.access(precheck, os.X_OK):
            self.add("blocker", "precheck_not_executable", f"{repo_name}: precheck is not executable: {precheck.relative_to(repo)}")
            return
        try:
            completed = subprocess.run(
                [str(precheck)],
                cwd=repo,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            self.add("blocker", "precheck_timeout", f"{repo_name}: precheck timed out after 60 seconds")
            return
        if completed.returncode != 0:
            self.add(
                "blocker",
                "precheck_failed",
                f"{repo_name}: precheck exited {completed.returncode}: {completed.stderr.strip() or completed.stdout.strip()}",
            )
            return
        if f"repo: {repo_name}" not in completed.stdout:
            self.add("major", "precheck_repo_marker_missing", f"{repo_name}: precheck output does not identify repo name")

    def verify_source_dump_resistance(self) -> None:
        if not self.jarvis_home.exists():
            return
        for path in self.jarvis_home.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(self.jarvis_home)
            if path.suffix.lower() in SOURCE_SUFFIXES:
                self.add("blocker", "source_file_in_jarvis_home", f"source-like file exists inside company Jarvis repo: {rel}")
            if path.stat().st_size > 500_000 and path.suffix.lower() in TEXT_SUFFIXES:
                self.add("major", "large_text_artifact", f"large text artifact may be raw source dump: {rel}")
        for child in self.jarvis_home.iterdir() if self.jarvis_home.exists() else []:
            if child.is_dir() and child.name in RAW_SOURCE_DIR_NAMES:
                self.add("blocker", "raw_source_dir_in_jarvis_home", f"raw source directory exists inside company Jarvis repo: {child.name}")

        repo_hashes = self.collect_repo_source_hashes()
        if not repo_hashes:
            return
        for path in self.jarvis_home.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES | SOURCE_SUFFIXES:
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if len(data) < 200:
                continue
            digest = hashlib.sha256(data).hexdigest()
            if digest in repo_hashes:
                rel = path.relative_to(self.jarvis_home)
                self.add("blocker", "copied_repo_file", f"company Jarvis file is an exact copy of customer repo source: {rel}")

    def collect_repo_source_hashes(self) -> set[str]:
        hashes: set[str] = set()
        for repo in self.repos:
            for path in repo.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    rel_parts = path.relative_to(repo).parts
                except ValueError:
                    continue
                if any(part in IGNORED_REPO_DIRS for part in rel_parts):
                    continue
                if path.suffix.lower() not in TEXT_SUFFIXES | SOURCE_SUFFIXES:
                    continue
                try:
                    data = path.read_bytes()
                except OSError:
                    continue
                if 200 <= len(data) <= 500_000:
                    hashes.add(hashlib.sha256(data).hexdigest())
        return hashes

    def verify_secret_boundary(self) -> None:
        if not self.jarvis_home.exists():
            return
        for path in self.jarvis_home.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            rel = path.relative_to(self.jarvis_home)
            if SECRET_ASSIGNMENT_RE.search(text):
                self.add("blocker", "secret_like_assignment", f"secret-like assignment found in company Jarvis artifact: {rel}")
            if BEARER_RE.search(text):
                self.add("blocker", "bearer_token", f"bearer token found in company Jarvis artifact: {rel}")

    # ── new deterministic checks ──────────────────────────────────────

    def verify_discovery_artifacts(self) -> None:
        discovery_dir = self.jarvis_home / "_bootstrap" / "discovery"
        if not discovery_dir.is_dir():
            self.add("blocker", "discovery_dir_missing", "required _bootstrap/discovery/ directory is missing")
            return
        for filename in REQUIRED_DISCOVERY_FILES:
            path = discovery_dir / filename
            if not path.is_file():
                self.add("blocker", "discovery_file_missing", f"_bootstrap/discovery/{filename} is missing")
            elif path.stat().st_size == 0:
                self.add("blocker", "discovery_file_empty", f"_bootstrap/discovery/{filename} is empty")

    def verify_phase6_placeholders(self) -> None:
        if not self.repos:
            return
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        for overview_path in modules_dir.glob("*/overview.md"):
            if not overview_path.is_file():
                continue
            try:
                text = overview_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            module_name = overview_path.parent.name
            for pattern, code in PHASE6_PLACEHOLDER_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    self.add("blocker", code, f"modules/{module_name}: overview.md contains Phase 6 placeholder matching {pattern!r}")

    def _check_root_placeholders(self, result: dict[str, Any] | None, state: dict[str, Any] | None) -> None:
        """Enforce Phase 7 identity/routing fill and Phase 14 rollout fill separately."""
        # Check if Phase 7 is completed
        phase7_completed = False
        if isinstance(result, dict):
            ps = result.get("phase_summary")
            if isinstance(ps, dict) and ps.get("phase-07-company-jarvis-repo") == "completed":
                phase7_completed = True
        if isinstance(state, dict):
            ps = state.get("phase_status")
            if isinstance(ps, dict) and ps.get("phase-07-company-jarvis-repo") == "completed":
                phase7_completed = True
            # Also check phase field
            if state.get("phase") == "phase-07-company-jarvis-repo" and state.get("status") == "completed":
                phase7_completed = True

        # Patterns that indicate unfilled root-level placeholders
        ROOT_PLACEHOLDER_PATTERNS = [
            (r"\bBOOTSTRAP_REQUIRED\b", "BOOTSTRAP_REQUIRED sentinel"),
            (r"\[Company\]", "[Company] literal in root file"),
            (r"<confirmed company[^>]*>", "<confirmed company ...> placeholder"),
            (r"<company>", "<company> placeholder"),
            (r"<list>", "<list> placeholder"),
            (r"\[待填[^]]*\]", "待填 placeholder"),
            (r"\[TODO[^]]*\]", "[TODO] placeholder"),
            (r"\{\{[A-Z_]+\}\}", "unresolved {{TOKEN}} in root file"),
        ]

        phase7_files: list[str] = []
        if phase7_completed:
            phase7_files = [
                "README.md",
                "jarvis.toml",
                "references/jarvis-first-routing.md",
                "references/canonical-repo-fleet.md",
            ]
            if self.expected_company_slug:
                phase7_files.append(
                    f"skills/{self.expected_company_slug}-jarvis/SKILL.md"
                )
            else:
                phase7_files.extend(
                    str(path.relative_to(self.jarvis_home))
                    for path in sorted((self.jarvis_home / "skills").glob("*jarvis*/SKILL.md"))
                )

        for rel_path in phase7_files:
            path = self.jarvis_home / rel_path
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern, desc in ROOT_PLACEHOLDER_PATTERNS:
                if re.search(pattern, text):
                    self.add(
                        "blocker",
                        "phase7_root_placeholder",
                        f"Phase 7 completed but {rel_path} contains unfilled placeholder: {desc}",
                    )
                    break  # one per file is enough

        phase14_completed = False
        if isinstance(result, dict):
            ps = result.get("phase_summary")
            if isinstance(ps, dict) and ps.get("phase-14-day2-operation") == "completed":
                phase14_completed = True
        if isinstance(state, dict):
            ps = state.get("phase_status")
            if isinstance(ps, dict) and ps.get("phase-14-day2-operation") == "completed":
                phase14_completed = True

        final_completed = phase14_completed or bool(
            isinstance(result, dict) and result.get("status") == "completed"
        )
        if not final_completed:
            return

        maintenance = self.jarvis_home / "MAINTENANCE.md"
        if not maintenance.is_file():
            return
        try:
            maintenance_text = maintenance.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        for pattern, desc in ROOT_PLACEHOLDER_PATTERNS:
            if re.search(pattern, maintenance_text):
                self.add(
                    "blocker",
                    "phase14_maintenance_placeholder",
                    f"Bootstrap is complete but MAINTENANCE.md contains unfilled placeholder: {desc}",
                )
                break

    def verify_durable_e2e_paths(self) -> None:
        for dirname in ("modules", "sources", "references", "skills", "cross-cutting", "tools"):
            root = self.jarvis_home / dirname
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if E2E_ABSOLUTE_PATH_RE.search(text):
                    self.add(
                        "blocker",
                        "durable_output_e2e_absolute_path",
                        f"{path.relative_to(self.jarvis_home)} contains bootstrap-only /e2e/ absolute path",
                    )

    def verify_precise_module_claims(self) -> None:
        discovery_dir = self.jarvis_home / "_bootstrap" / "discovery"
        evidence_parts: list[str] = []
        for path in discovery_dir.glob("*.md"):
            try:
                evidence_parts.append(path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
        evidence_text = "\n".join(evidence_parts)
        if not evidence_text:
            return
        for overview in (self.jarvis_home / "modules").glob("*/overview.md"):
            try:
                text = overview.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            module_name = overview.parent.name
            for line in text.splitlines():
                if re.search(r"needs-verification", line, re.IGNORECASE):
                    continue
                if re.search(r"issue\s+tracker\s+label", line, re.IGNORECASE) and line.strip() not in evidence_text:
                    self.add(
                        "blocker",
                        "module_issue_label_without_discovery_evidence",
                        f"modules/{module_name}: precise issue label claim is not present in discovery evidence: {line.strip()}",
                    )
                if not re.search(r"API\s*/\s*contract|UI\s*/\s*route", line, re.IGNORECASE):
                    continue
                for route in re.findall(r"(?<![A-Za-z0-9_.-])/(?:api|v\d+|app)(?:/[A-Za-z0-9_{}*.:~-]+)+", line):
                    if route not in evidence_text:
                        self.add(
                            "blocker",
                            "module_route_without_discovery_evidence",
                            f"modules/{module_name}: precise route {route!r} is not present in discovery evidence",
                        )

    def _read_run_exit_code(self, run_dir: Path) -> int | None:
        exit_code_file = run_dir / "exit-code"
        if not exit_code_file.is_file():
            return None
        try:
            return int(exit_code_file.read_text(encoding="utf-8", errors="replace").strip())
        except (ValueError, OSError):
            return None

    def _check_replay_exit_code_decisions(self) -> None:
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        if not runs_dir.is_dir():
            return
        for run_dir in sorted(runs_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            case_id = run_dir.name
            exit_code = self._read_run_exit_code(run_dir)
            if exit_code is None:
                continue
            if exit_code == 0:
                continue
            case_dir = self.jarvis_home / "evals" / "history-replay" / "cases" / case_id
            for filename in ["skill-update-decision.md", "replay-failure-analysis.md"]:
                decision_file = case_dir / filename
                if not decision_file.is_file():
                    continue
                try:
                    text = decision_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for pattern, code in NONZERO_EXIT_FORBIDDEN_PATTERNS:
                    if pattern.search(text):
                        self.add("blocker", code, f"{case_id}: replay exit non-zero but {filename} contains forbidden pattern {pattern.pattern!r}")
            skill_decision = case_dir / "skill-update-decision.md"
            if not skill_decision.is_file():
                self.add(
                    "blocker",
                    "nonzero_replay_decision_missing",
                    f"{case_id}: replay exit non-zero but skill-update-decision.md is missing",
                )
            else:
                try:
                    text = skill_decision.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
                else:
                    if not NONZERO_EXIT_REQUIRED_PATTERN.search(text):
                        self.add(
                            "blocker",
                            "nonzero_replay_no_defer",
                            f"{case_id}: replay exit non-zero but skill-update-decision.md does not contain defer/deferred/not-evaluated",
                        )

    def _check_replay_zero_exit_artifacts(self) -> None:
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        if not runs_dir.is_dir():
            return
        for run_dir in sorted(runs_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            case_id = run_dir.name
            exit_code = self._read_run_exit_code(run_dir)
            if exit_code != 0:
                continue
            replay_jsonl = run_dir / "replay-agent.jsonl"
            replay_result = run_dir / "replay-result.md"
            if not replay_jsonl.is_file() or replay_jsonl.stat().st_size == 0:
                self.add("blocker", "zero_exit_replay_missing_jsonl", f"{case_id}: replay exit=0 but replay-agent.jsonl is missing or empty")
            if not replay_result.is_file() or replay_result.stat().st_size == 0:
                self.add("blocker", "zero_exit_replay_missing_result", f"{case_id}: replay exit=0 but replay-result.md is missing or empty")

    def _check_phase12_completed_requirements(self) -> None:
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"

        # No cases at all → blocker
        if not cases_dir.is_dir():
            self.add(
                "blocker",
                "phase12_completed_no_cases",
                "Phase 12 completed but evals/history-replay/cases/ directory does not exist",
            )
            return
        case_files = list(cases_dir.glob("*/history-replay-case.md"))
        if not case_files:
            self.add(
                "blocker",
                "phase12_completed_no_cases",
                "Phase 12 completed but no history-replay-case.md files exist",
            )
            return

        # Check eligible cases exist (structured fields only)
        eligible_case_ids: set[str] = set()
        ineligible_markers = {"ineligible-leaky", "low-confidence", "needs-better-start", "blocked"}
        for case_file in case_files:
            case_id = case_file.parent.name
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Check Eligibility / Replay eligibility structured fields
            eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Eligibility")
            replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Replay eligibility")
            effective = eligibility_val or replay_eligibility_val
            if effective in {"eligible-direct", "eligible-reconstructed"}:
                eligible_case_ids.add(case_id)
            elif effective in ineligible_markers:
                self.add(
                    "blocker",
                    "phase12_completed_ineligible_case",
                    f"{case_id}: Phase 12 completed with Eligibility={effective!r}",
                )

        if not eligible_case_ids:
            self.add(
                "blocker",
                "phase12_completed_no_eligible_case",
                "Phase 12 completed but no case has explicit eligible-direct or "
                "eligible-reconstructed eligibility",
            )
            # Still check calibration artifacts for cases with runs
            for case_file in case_files:
                case_id = case_file.parent.name
                run_dir = runs_dir / case_id
                if run_dir.is_dir() and (run_dir / "exit-code").is_file():
                    for filename in ["replay-failure-analysis.md", "skill-update-decision.md"]:
                        if not (case_file.parent / filename).is_file():
                            self.add(
                                "blocker",
                                "phase12_completed_missing_calibration_artifact",
                                f"{case_id}: Phase 12 completed but case has replay run without {filename}",
                            )
            return

        valid_run = False
        valid_run_case_id: str | None = None
        for run_dir in sorted(runs_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            case_id = run_dir.name
            if case_id not in eligible_case_ids:
                continue
            exit_code = self._read_run_exit_code(run_dir)
            if exit_code != 0:
                continue
            replay_jsonl = run_dir / "replay-agent.jsonl"
            replay_result = run_dir / "replay-result.md"
            if not (replay_jsonl.is_file() and replay_jsonl.stat().st_size > 0):
                continue
            if not (replay_result.is_file() and replay_result.stat().st_size > 0):
                continue
            evidence_file = run_dir / "host-isolation-evidence.json"
            if not evidence_file.is_file():
                continue
            try:
                evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if evidence.get("mechanism") != "secondary-apple-container":
                continue
            allowed_mounts = evidence.get("allowed_mounts")
            if not isinstance(allowed_mounts, list):
                continue
            actual_mounts: dict[str, str] = {}
            valid_mount_shape = True
            for mount in allowed_mounts:
                if not isinstance(mount, dict):
                    valid_mount_shape = False
                    break
                container_path = mount.get("container")
                mode = mount.get("mode")
                if not isinstance(container_path, str) or not isinstance(mode, str):
                    valid_mount_shape = False
                    break
                actual_mounts[container_path] = mode
            if not valid_mount_shape or actual_mounts != PHASE12_REQUIRED_MOUNTS:
                continue
            valid_run = True
            valid_run_case_id = case_id
            break

        if not valid_run:
            self.add(
                "blocker",
                "phase12_no_valid_isolated_run",
                "Phase 12 completed but no eligible case has a valid isolated run (exit=0, "
                "non-empty trace/result, host-isolation-evidence.json with mechanism=secondary-apple-container "
                "and allowed mounts subset of visible/parent/company-runtime/output)",
            )
            return

        # Every case with a replay run must have non-empty failure analysis and skill decision
        for case_file in case_files:
            case_id = case_file.parent.name
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            run_dir = runs_dir / case_id
            if not run_dir.is_dir() or not (run_dir / "exit-code").is_file():
                continue
            for filename in ["replay-failure-analysis.md", "skill-update-decision.md"]:
                cal_file = case_file.parent / filename
                if not cal_file.is_file():
                    self.add(
                        "blocker",
                        "phase12_completed_missing_calibration_artifact",
                        f"{case_id}: Phase 12 completed but case has replay run without {filename}",
                    )
                elif cal_file.stat().st_size == 0:
                    self.add(
                        "blocker",
                        "phase12_completed_empty_calibration_artifact",
                        f"{case_id}: Phase 12 completed but {filename} is empty",
                    )

        # Failure analysis must contain oracle comparison (English or Chinese equivalents)
        oracle_comparison_pattern = re.compile(
            r"(?i)(?:oracle\s*comparison|oracle\s*contrast|oracle\s*compare"
            r"|compared?\s*(?:with|to|against)\s*(?:the\s*)?oracle"
            r"|对比\s*oracle|对照\s*oracle|与\s*oracle\s*(?:比较|对比|对照)"
            r"|oracle\s*(?:对比|对照|比较))"
        )
        for case_file in case_files:
            case_id = case_file.parent.name
            failure_analysis = case_file.parent / "replay-failure-analysis.md"
            if not failure_analysis.is_file():
                continue
            try:
                fa_text = failure_analysis.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not oracle_comparison_pattern.search(fa_text):
                self.add(
                    "blocker",
                    "phase12_completed_failure_analysis_no_oracle_comparison",
                    f"{case_id}: Phase 12 completed but replay-failure-analysis.md "
                    "does not contain explicit oracle comparison (English or Chinese equivalents)",
                )

        # ── Canonical template section checks (when Phase 12 completed) ──
        # Every case with a replay run must have canonical sections/fields
        for case_file in case_files:
            case_id = case_file.parent.name
            run_dir = runs_dir / case_id
            if not run_dir.is_dir() or not (run_dir / "exit-code").is_file():
                continue

            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                case_text = ""

            # --- history-replay-case: Case Readiness Gate ---
            crg_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Case validity")
            if not crg_val:
                self.add("blocker", "phase12_completed_case_validity_missing",
                         f"{case_id}: history-replay-case.md missing canonical 'Case validity' field")
            elif crg_val != "valid":
                self.add("blocker", "phase12_completed_case_invalid",
                         f"{case_id}: Case validity={crg_val!r}, must be 'valid' when Phase 12 completed")

            readiness_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Readiness")
            if readiness_val != "ready":
                self.add("blocker", "phase12_completed_case_not_ready",
                         f"{case_id}: Readiness={readiness_val!r}, must be 'ready' when Phase 12 completed")

            final_read = CaseLeakAnalyzer._parse_structured_choice(
                case_text, "Final artifact fully read"
            )
            if final_read != "yes":
                self.add(
                    "blocker",
                    "phase12_completed_final_artifact_not_read",
                    f"{case_id}: Final artifact fully read={final_read!r}, must be 'yes'",
                )
            extraction = CaseLeakAnalyzer._parse_structured_field(
                case_text, "Final artifact extraction command / pointer"
            )
            if not extraction or self._is_placeholder_value(extraction):
                self.add(
                    "blocker",
                    "phase12_completed_final_extraction_missing",
                    f"{case_id}: final artifact extraction command/pointer is missing or placeholder",
                )

            pfc_section = self._extract_section_text(
                case_text, r'#+\s*Visible\s+Packet\s+Fact\s+Closure'
            )
            pfc_rows = self._parse_table_data_rows(pfc_section, min_columns=4) if pfc_section else []
            if not pfc_rows:
                self.add(
                    "blocker",
                    "phase12_completed_packet_fact_closure_empty",
                    f"{case_id}: Visible Packet Fact Closure table is missing or empty",
                )
            else:
                for row in pfc_rows:
                    if any(self._is_placeholder_value(cell) for cell in row[:3]) or row[3].strip().lower() != "supported":
                        self.add(
                            "blocker",
                            "phase12_completed_packet_fact_closure_invalid",
                            f"{case_id}: Visible Packet Fact Closure contains an incomplete or unsupported row",
                        )
                        break

            hidden_excluded_section = self._extract_section_text(
                case_text, r'#+\s*Hidden\s+Facts\s+Excluded\s+From\s+Visible\s+Packet'
            )
            hidden_excluded_rows = (
                self._parse_table_data_rows(hidden_excluded_section, min_columns=4)
                if hidden_excluded_section else []
            )
            if not hidden_excluded_rows:
                self.add(
                    "blocker",
                    "phase12_completed_hidden_facts_review_empty",
                    f"{case_id}: Hidden Facts Excluded From Visible Packet table is missing or empty",
                )
            else:
                for row in hidden_excluded_rows:
                    if any(self._is_placeholder_value(cell) for cell in row[:3]) or row[3].strip().lower() != "absent":
                        self.add(
                            "blocker",
                            "phase12_completed_hidden_facts_review_invalid",
                            f"{case_id}: Hidden Facts Excluded table contains an incomplete or non-absent row",
                        )
                        break

            # --- replay-failure-analysis canonical sections ---
            fa_file = case_file.parent / "replay-failure-analysis.md"
            if fa_file.is_file():
                try:
                    fa_text = fa_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    fa_text = ""
                # Execution Gate section
                if not re.search(r'#+\s*Execution\s+Gate', fa_text):
                    self.add("blocker", "phase12_completed_fa_missing_execution_gate",
                             f"{case_id}: replay-failure-analysis.md missing 'Execution Gate' section")
                # Final Output Evidence section
                if not re.search(r'#+\s*Final\s+Output\s+Evidence', fa_text):
                    self.add("blocker", "phase12_completed_fa_missing_final_output_evidence",
                             f"{case_id}: replay-failure-analysis.md missing 'Final Output Evidence' section")
                # Historical Outcome Evidence section
                if not re.search(r'#+\s*Historical\s+Outcome\s+Evidence', fa_text):
                    self.add("blocker", "phase12_completed_fa_missing_historical_outcome_evidence",
                             f"{case_id}: replay-failure-analysis.md missing 'Historical Outcome Evidence' section")
                # Oracle Comparison section
                if not re.search(r'#+\s*Oracle\s+Comparison', fa_text):
                    self.add("blocker", "phase12_completed_fa_missing_oracle_comparison",
                             f"{case_id}: replay-failure-analysis.md missing 'Oracle Comparison' section")
                # Structured fields in failure analysis
                fa_case_validity = CaseLeakAnalyzer._parse_structured_choice(fa_text, "Case validity")
                if fa_case_validity != "valid":
                    self.add("blocker", "phase12_completed_fa_case_validity_invalid",
                             f"{case_id}: replay-failure-analysis.md 'Case validity'={fa_case_validity!r}, must be 'valid'")
                fa_exec_gate = CaseLeakAnalyzer._parse_structured_choice(fa_text, "Execution gate")
                if fa_exec_gate != "executed":
                    self.add("blocker", "phase12_completed_fa_exec_gate_not_executed",
                             f"{case_id}: replay-failure-analysis.md 'Execution gate'={fa_exec_gate!r}, must be 'executed'")
                fa_outcome_suff = CaseLeakAnalyzer._parse_structured_choice(
                    fa_text, "Outcome verification sufficient for skill judgment")
                if fa_outcome_suff != "yes":
                    self.add("blocker", "phase12_completed_fa_outcome_insufficient",
                             f"{case_id}: 'Outcome verification sufficient for skill judgment'={fa_outcome_suff!r}, must be 'yes'")

                final_output_section = self._extract_section_text(
                    fa_text, r'#+\s*Final\s+Output\s+Evidence'
                )
                historical_section = self._extract_section_text(
                    fa_text, r'#+\s*Historical\s+Outcome\s+Evidence'
                )
                for label, section in (
                    ("replay final output", final_output_section),
                    ("historical outcome", historical_section),
                ):
                    pointer = CaseLeakAnalyzer._parse_structured_field(
                        section, "Exact command or artifact pointer"
                    ) if section else None
                    fully_read = CaseLeakAnalyzer._parse_structured_choice(
                        section, "确认已完整读取"
                    ) if section else None
                    if not pointer or self._is_placeholder_value(pointer) or fully_read != "yes":
                        self.add(
                            "blocker",
                            "phase12_completed_outcome_evidence_incomplete",
                            f"{case_id}: {label} needs a non-placeholder exact pointer and fully-read=yes",
                        )

            # --- skill-update-decision canonical sections ---
            sd_file = case_file.parent / "skill-update-decision.md"
            if sd_file.is_file():
                try:
                    sd_text = sd_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    sd_text = ""
                # Decision Summary section
                if not re.search(r'#+\s*Decision\s+Summary', sd_text):
                    self.add("blocker", "phase12_completed_sd_missing_decision_summary",
                             f"{case_id}: skill-update-decision.md missing 'Decision Summary' section")
                sd_case_validity = CaseLeakAnalyzer._parse_structured_choice(sd_text, "Case validity")
                if sd_case_validity != "valid":
                    self.add("blocker", "phase12_completed_sd_case_validity_invalid",
                             f"{case_id}: skill-update-decision.md 'Case validity'={sd_case_validity!r}, must be 'valid'")
                sd_outcome_suff = CaseLeakAnalyzer._parse_structured_choice(
                    sd_text, "Outcome verification sufficient for skill judgment")
                if sd_outcome_suff != "yes":
                    self.add("blocker", "phase12_completed_sd_outcome_insufficient",
                             f"{case_id}: 'Outcome verification sufficient for skill judgment'={sd_outcome_suff!r}, must be 'yes'")

        # Verify valid run's case also has the binding check satisfied
        if valid_run_case_id:
            calib_missing = []
            for filename in ["replay-failure-analysis.md", "skill-update-decision.md"]:
                cal_file = cases_dir / valid_run_case_id / filename
                if not cal_file.is_file():
                    calib_missing.append(filename)
                elif cal_file.stat().st_size == 0:
                    calib_missing.append(f"{filename} (empty)")
            if calib_missing:
                self.add(
                    "blocker",
                    "phase12_completed_valid_run_no_calibration",
                    f"{valid_run_case_id}: valid isolated run exists but calibration missing: "
                    + ", ".join(calib_missing),
                )

    def _is_phase12_completed(self, result: dict[str, Any] | None, state: dict[str, Any] | None) -> bool:
        if isinstance(result, dict):
            phase_summary = result.get("phase_summary")
            if isinstance(phase_summary, dict) and phase_summary.get("phase-12-history-replay") == "completed":
                return True
        if isinstance(state, dict):
            phase_statuses = state.get("phase_status")
            if isinstance(phase_statuses, dict) and phase_statuses.get("phase-12-history-replay") == "completed":
                return True
        return False

    def verify_day2_operation(self) -> None:
        day2_op = self.jarvis_home / "_bootstrap" / "day2-operation.md"
        if not day2_op.is_file():
            return
        try:
            op_text = day2_op.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        # ── Parse Install-owned Capability Status table by header names ──
        # Find the table under "Install-owned Capability Status" heading
        cap_section = self._extract_section_text(
            op_text, r'#+\s*Install-owned\s+Capability\s+Status',
        )
        if not cap_section:
            cap_section = self._extract_section_text(
                op_text, r'#+\s*Install-owned\s+能力|Install-owned.*能力',
            )

        # Parse table rows from the capability section
        capability_rows: list[dict[str, str]] = []
        if cap_section:
            capability_rows = self._parse_day2_capability_table(cap_section)

        # The seven required capability rows from the canonical template
        REQUIRED_CAPABILITIES = [
            "service lifecycle",
            "agent registry / routing / failover",
            "task lifecycle",
            "runtime sync",
            "jarvis maintenance launcher",
            "session self-improvement",
            "workspace cleanup",
        ]

        # Check if Phase 14 is completed
        phase14_completed = self._is_phase14_completed()

        if phase14_completed:
            # Require exactly the 7 required capability rows
            found_cap_list = [r.get("capability", "").strip().lower() for r in capability_rows]
            found_caps = set(found_cap_list)
            required_caps = set(REQUIRED_CAPABILITIES)
            if len(found_cap_list) != len(REQUIRED_CAPABILITIES) or found_caps != required_caps:
                self.add(
                    "blocker",
                    "day2_capability_row_set_invalid",
                    "_bootstrap/day2-operation.md must contain exactly the seven canonical capability rows",
                )
            for required in REQUIRED_CAPABILITIES:
                if required not in found_caps:
                    self.add(
                        "blocker",
                        "day2_required_capability_row_missing",
                        f"_bootstrap/day2-operation.md: required capability row missing: '{required}'",
                    )

            # Each capability row must have non-placeholder evidence cells
            for row in capability_rows:
                cap_name = row.get("capability", "").strip()
                if not cap_name:
                    continue
                # Check readiness field
                readiness = row.get("readiness", "").strip().lower()
                if readiness not in ("ready", "ready-with-explicit-alternative"):
                    if readiness:
                        self.add(
                            "blocker",
                            "day2_capability_not_ready",
                            f"_bootstrap/day2-operation.md: '{cap_name}' readiness is '{readiness}', "
                            f"required ready or ready-with-explicit-alternative when Phase 14 completed",
                        )
                    else:
                        self.add(
                            "blocker",
                            "day2_capability_readiness_empty",
                            f"_bootstrap/day2-operation.md: '{cap_name}' readiness cell is empty",
                        )
                # Check non-placeholder evidence cells
                for col in ("install_authority_evidence", "observed_current_state",
                            "last_execution_proof", "owner_recovery"):
                    val = row.get(col, "")
                    if not val or self._is_placeholder_value(val):
                        self.add(
                            "blocker",
                            "day2_capability_cell_placeholder",
                            f"_bootstrap/day2-operation.md: '{cap_name}' has placeholder/empty '{col}'",
                        )

            # Require non-placeholder prompt probe fields
            probe_invocation = CaseLeakAnalyzer._parse_structured_field(
                op_text, "真实 prompt probe invocation",
            )
            probe_evidence = CaseLeakAnalyzer._parse_structured_field(
                op_text, "真实 prompt probe evidence",
            )
            if not probe_invocation or self._is_placeholder_value(probe_invocation):
                self.add(
                    "blocker",
                    "day2_prompt_probe_invocation_missing",
                    "_bootstrap/day2-operation.md: missing or placeholder '真实 prompt probe invocation'",
                )
            if not probe_evidence or self._is_placeholder_value(probe_evidence):
                self.add(
                    "blocker",
                    "day2_prompt_probe_evidence_missing",
                    "_bootstrap/day2-operation.md: missing or placeholder '真实 prompt probe evidence'",
                )

            # Require Cross-Artifact Consistency Review overall field
            consistency_passed = CaseLeakAnalyzer._parse_structured_choice(
                op_text, "一致性审查通过",
            )
            if consistency_passed != "yes":
                self.add(
                    "blocker",
                    "day2_cross_artifact_consistency_not_passed",
                    "_bootstrap/day2-operation.md: Cross-Artifact Consistency Review "
                    "'一致性审查通过' must be 'yes' when Phase 14 completed",
                )
        else:
            # Phase 14 not completed — still reject malformed explicit readiness tokens
            for row in capability_rows:
                cap_name = row.get("capability", "").strip()
                readiness = row.get("readiness", "").strip().lower()
                if readiness and readiness not in (
                    "ready", "ready-with-explicit-alternative",
                    "unverified", "blocked",
                ):
                    self.add(
                        "blocker",
                        "day2_capability_readiness_invalid",
                        f"_bootstrap/day2-operation.md: '{cap_name}' has invalid readiness token '{readiness}'",
                    )

    @staticmethod
    def _is_placeholder_value(val: str) -> bool:
        """Check if a value is a placeholder/empty."""
        if not val or not val.strip():
            return True
        stripped = val.strip().strip('`*_"\'').lower()
        if stripped in ('none', 'n/a', '', '无', 'tbd', 'todo'):
            return True
        if re.match(r'^[<\[]', stripped):
            return True
        if re.search(r'\.{3}|…', stripped):
            return True
        return False

    @staticmethod
    def _parse_day2_capability_table(section_text: str) -> list[dict[str, str]]:
        """Parse the Install-owned Capability Status table.
        Returns a list of dicts with keys: capability, install_authority_evidence,
        observed_current_state, last_execution_proof, readiness, owner_recovery."""
        rows: list[dict[str, str]] = []
        col_map: dict[str, int] = {}
        header_parsed = False

        COLUMN_ALIASES = {
            "能力": "capability",
            "capability": "capability",
            "install/authority 证据": "install_authority_evidence",
            "install/authority evidence": "install_authority_evidence",
            "观测当前状态": "observed_current_state",
            "observed current state": "observed_current_state",
            "最近执行证据": "last_execution_proof",
            "last execution proof": "last_execution_proof",
            "readiness": "readiness",
            "owner & recovery": "owner_recovery",
            "owner &amp; recovery": "owner_recovery",
            "owner and recovery": "owner_recovery",
        }

        for line in section_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or not stripped.endswith("|"):
                continue
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if not cells:
                continue
            # Skip separator rows
            if all(re.match(r'^[-:\s]+$', c) for c in cells if c):
                continue

            if not header_parsed:
                # Try to map columns
                for i, cell in enumerate(cells):
                    cell_lower = cell.strip().lower()
                    for alias, key in COLUMN_ALIASES.items():
                        if cell_lower == alias:
                            col_map[key] = i
                            break
                if len(col_map) >= 3:  # At least 3 columns identified → header row
                    header_parsed = True
                continue

            if not col_map:
                continue

            row: dict[str, str] = {}
            for key, idx in col_map.items():
                if idx < len(cells):
                    row[key] = cells[idx]
                else:
                    row[key] = ""
            if row.get("capability", "").strip():
                rows.append(row)

        return rows

    def _is_phase14_completed(self) -> bool:
        """Check if Phase 14 is marked completed in result or state."""
        try:
            result = self.load_json(self.jarvis_home / "bootstrap-result.json", "bootstrap-result.json")
        except Exception:
            result = None
        try:
            state = self.load_json(self.jarvis_home / "bootstrap-state.json", "bootstrap-state.json")
        except Exception:
            state = None
        for obj in [result, state]:
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if isinstance(val, dict) and val.get("phase-14-day2-operation") == "completed":
                        return True
        return False

    @staticmethod
    def _claims_replay_transport_unavailable(text: str) -> bool:
        """Detect structured claims that replay isolation transport must be provided.

        A statement that an existing helper still needs to be invoked is not an
        availability claim and must not match this check.
        """
        bridge_target = r"(?:`?request-isolated-replay`?|(?:replay|isolation)\s+bridge)"
        unavailable = r"(?:missing|unavailable|not\s+available|not\s+provided|absent|without|no)"
        patterns = [
            rf"\b{unavailable}\b[^\n]{{0,80}}{bridge_target}",
            rf"{bridge_target}[^\n]{{0,80}}\b{unavailable}\b",
            r"\b(?:need|needs|require|requires)\s+(?:an?\s+)?"
            r"(?:`?request-isolated-replay`?\s+)?(?:replay\s+|isolation\s+)?bridge\b",
            r"\b(?:need|needs|require|requires|missing|without|no)\s+(?:an?\s+)?"
            r"(?:container\s*/\s*vm|container\s+or\s+vm)\s+"
            r"(?:(?:isolation|isolated)\s+)?(?:runtime|transport)\b",
            r"\b(?:container\s*/\s*vm|container\s+or\s+vm)\s+"
            r"(?:(?:isolation|isolated)\s+)?(?:runtime|transport)\b[^\n]{0,50}"
            r"\b(?:missing|unavailable|not\s+available|absent)\b",
            r"\bisolation\s+(?:runtime|transport)\s+(?:is\s+)?unavailable\b",
            r"(?:缺少|缺失|没有|不可用|需要提供)[^\n]{0,80}"
            r"(?:request-isolated-replay|(?:replay|隔离)(?:\s+bridge|桥接))",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    def verify_replay_bridge_contract(self, result: dict[str, Any] | None) -> None:
        helper = self.replay_bridge_helper
        if helper is None or not helper.is_file() or not os.access(helper, os.X_OK):
            return

        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        for case_file in sorted(cases_dir.glob("*/history-replay-case.md")):
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if CaseLeakAnalyzer._parse_structured_choice(case_text, "Status") != "ready-for-replay":
                continue
            case_id = case_file.parent.name
            run_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id
            if not (run_dir / "exit-code").is_file():
                self.add(
                    "blocker",
                    "history_replay_bridge_available_not_invoked",
                    f"{case_id}: executable replay bridge helper was provided, but ready case has no replay exit-code evidence",
                )
            checks_path = run_dir / "replay-agent-cli-checks.md"
            if checks_path.is_file():
                try:
                    checks_text = checks_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    checks_text = ""
                if self._claims_replay_transport_unavailable(checks_text):
                    self.add(
                        "blocker",
                        "history_replay_bridge_ignored_as_unavailable",
                        f"{case_id}: CLI checks claim isolation runtime unavailable despite executable replay bridge helper",
                    )
            visible_prompt = run_dir / "visible-packet" / "replay-prompt.md"
            if visible_prompt.is_file():
                try:
                    visible_text = visible_prompt.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    visible_text = ""
                if "/e2e/customer-repos" in visible_text:
                    self.add(
                        "blocker",
                        "history_replay_visible_packet_uses_outer_path",
                        f"{case_id}: visible replay prompt points at outer /e2e/customer-repos instead of isolated /replay/worktree",
                    )

        if isinstance(result, dict):
            open_text = "\n".join(
                item
                for field in ("missing_inputs", "blockers", "unresolved_questions")
                for item in (result.get(field) if isinstance(result.get(field), list) else [])
                if isinstance(item, str)
            )
            if self._claims_replay_transport_unavailable(open_text):
                self.add(
                    "blocker",
                    "bootstrap_reports_isolation_unavailable_with_bridge",
                    "bootstrap-result.json reports isolation runtime unavailable despite executable replay bridge helper",
                )

    def _extract_jarvis_box_root_commands(self) -> set[str]:
        if not self.jarvis_box_help_file or not self.jarvis_box_help_file.is_file():
            return set()
        try:
            text = self.jarvis_box_help_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return set()
        commands: set[str] = set()
        for line in text.splitlines():
            m = re.match(r"^\s{2,}([a-z][a-z0-9-]*)\s", line)
            if m:
                commands.add(m.group(1))
        return commands

    def _verify_install_owned_skills_not_copied(self) -> None:
        """Block install-owned skills copied into company repo."""
        INSTALL_OWNED = {"jarvis-box-doctor", "jarvis-box-init", "jarvis-box-monitor", "jarvis-self-improve-skill"}
        skills_dir = self.jarvis_home / "skills"
        if not skills_dir.is_dir():
            return
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name in INSTALL_OWNED:
                self.add(
                    "blocker",
                    "install_owned_skill_copied",
                    f"install-owned skill must not be copied to company repo: skills/{skill_dir.name}",
                )

    def _verify_workflow_scaffolds_not_isomorphic(self) -> None:
        """Phase 9 check: workflows must have distinct semantics, not just copies."""
        skills_dir = self.jarvis_home / "skills"
        if not skills_dir.is_dir():
            return

        # All 12 known package kinds with companion files and semantic markers.
        # Companion list may be empty. Source/helper kinds do not force four-stage.
        KNOWN_PACKAGE_KINDS: dict[str, dict[str, Any]] = {
            "generic-workflow": {
                "companions": [],
                "force_four_stage": True,
                "markers": [],
            },
            "generic-source": {
                "companions": [],
                "force_four_stage": False,
                "markers": [],
            },
            "issue-intake": {
                "companions": [
                    "references/blocker-template.md",
                    "references/disposition-command-checklist.md",
                    "references/disposition-proof-sop.md",
                    "references/guided-question-flow.md",
                    "references/issue-type-matrix.md",
                    "references/output-template.md",
                    "references/pre-filing-judgment-card.md",
                ],
                "force_four_stage": False,
                "markers": [r"\bintake\b|\btriage\b|\bclaim\b|\bdisposition\b"],
            },
            "issue-post-check": {
                "companions": [
                    "references/environment-version-evidence-gate.md",
                    "references/peer-product-contract-check.md",
                ],
                "force_four_stage": False,
                "markers": [r"\bpost.check\b|\bverify\b|\bduplicate\b"],
            },
            "bugfix-loop": {
                "companions": ["references/reproduction-evidence.md"],
                "force_four_stage": False,
                "markers": [r"\bbug\b|\breproduce\b|\bfix\b|\bregression\b"],
            },
            "feature-delivery": {
                "companions": [],
                "force_four_stage": False,
                "markers": [r"\bfeature\b|\bPRD\b|\bspec\b|\bdeliver"],
            },
            "prd-review": {
                "companions": [
                    "references/blocking-questions-template.md",
                    "references/output-template.md",
                    "references/source-routing.md",
                    "references/spec-checklist.md",
                ],
                "force_four_stage": False,
                "markers": [r"\breview\b|\bPRD\b|\bspec\b|\bblocking"],
            },
            "release-notes": {
                "companions": [],
                "force_four_stage": False,
                "markers": [r"\brelease\b|\bversion\b|\bchangelog\b"],
            },
            "branch-neutral-docs": {
                "companions": [],
                "force_four_stage": False,
                "markers": [r"\bdocumentation\b|\bdocs\b|\bdurable\b|\bbranch"],
            },
            "outline-api": {
                "companions": [],
                "force_four_stage": False,
                "markers": [],
            },
            "jenkins-job-builder": {
                "companions": ["jobs/registry.json"],
                "force_four_stage": False,
                "markers": [],
            },
            "issue-attachment-regression-fixture": {
                "companions": ["references/example-contract.md"],
                "force_four_stage": False,
                "markers": [],
            },
        }

        def _match_kind(dirname: str) -> str | None:
            """Exact name match or ends-with -<kind> for prefixed variants."""
            if dirname in KNOWN_PACKAGE_KINDS:
                return dirname
            for kind in KNOWN_PACKAGE_KINDS:
                if dirname.endswith(f"-{kind}"):
                    return kind
            return None

        GENERIC_WORKFLOW_TERMS = {"START", "WORK", "VERIFY", "END"}
        package_placeholder_patterns = [
            (re.compile(r"\bBOOTSTRAP_REQUIRED\b"), "BOOTSTRAP_REQUIRED"),
            (re.compile(r"\[needs-evidence(?:\s*:[^\]]+)?\]", re.IGNORECASE), "[needs-evidence]"),
            (re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}"), "unrendered token"),
            (re.compile(r"<(?:outline|jenkins)-source>"), "unresolved source-route identity"),
            (
                re.compile(
                    r"\b(?:REFERENCES_PATH|MODULE_KNOWLEDGE_PATH|CROSS_CUTTING_PATH|"
                    r"SOURCE_ROUTE_PATH|CROSS_CUTTING_PEER_CONTRACTS|PROJECT_NAME|"
                    r"QUERY_ISSUES_TOOL|ISSUE_VIEW_TOOL|ISSUE_API_NOTES_TOOL|"
                    r"OUTLINE_BASE_URL|JENKINS_BASE_URL|TARGET_ENVIRONMENT_URL|"
                    r"VERSION_ROUTING|PHASE_6_NOT_YET_FILLED)\b"
                ),
                "bootstrap field name",
            ),
        ]

        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if "jarvis" in skill_dir.name.lower():
                continue  # skip entry skill
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            try:
                content = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            for package_file in sorted(skill_dir.rglob("*")):
                if (
                    not package_file.is_file()
                    or package_file.suffix.lower() not in TEXT_SUFFIXES
                ):
                    continue
                try:
                    package_text = package_file.read_text(
                        encoding="utf-8", errors="replace"
                    )
                except OSError:
                    continue
                for pattern, description in package_placeholder_patterns:
                    if pattern.search(package_text):
                        self.add(
                            "blocker",
                            "skill_package_bootstrap_placeholder",
                            f"{package_file.relative_to(self.jarvis_home)} contains {description}",
                        )
                        break

            kind = _match_kind(skill_dir.name)

            if kind is not None:
                kind_def = KNOWN_PACKAGE_KINDS[kind]

                # Companion file checks: present, non-empty, referenced
                for companion in kind_def["companions"]:
                    comp_path = skill_dir / companion
                    if not comp_path.is_file():
                        self.add(
                            "blocker",
                            "workflow_companion_file_missing",
                            f"skills/{skill_dir.name}: known kind missing companion file: {companion}",
                        )
                    elif comp_path.stat().st_size == 0:
                        self.add(
                            "blocker",
                            "workflow_companion_file_empty",
                            f"skills/{skill_dir.name}: companion file is empty: {companion}",
                        )
                for companion in kind_def["companions"]:
                    ref_name = Path(companion).name
                    ref_stem = Path(companion).stem
                    if ref_name not in content and ref_stem not in content:
                        self.add(
                            "major",
                            "workflow_companion_not_referenced",
                            f"skills/{skill_dir.name}: SKILL.md does not reference companion file: {companion}",
                        )

                # Semantic marker checks for workflow kinds
                for marker_pattern in kind_def["markers"]:
                    if not re.search(marker_pattern, content, re.IGNORECASE):
                        self.add(
                            "major",
                            "workflow_semantic_marker_missing",
                            f"skills/{skill_dir.name}: SKILL.md missing semantic marker matching {marker_pattern!r}",
                        )

                # Four-stage check: only generic-workflow
                if kind_def["force_four_stage"]:
                    missing_terms = [t for t in GENERIC_WORKFLOW_TERMS if t not in content]
                    if missing_terms:
                        self.add(
                            "blocker",
                            "generic_workflow_missing_structure",
                            f"skills/{skill_dir.name}: generic-workflow SKILL.md missing terms: {missing_terms}",
                        )
            else:
                # Unknown skill: only apply four-stage if text explicitly declares generic/fallback workflow
                if re.search(
                    r"\bgeneric.workflow\b|\bfallback.workflow\b|\b通用.workflow\b|\b通用.工作流\b",
                    content,
                    re.IGNORECASE,
                ):
                    missing_terms = [t for t in GENERIC_WORKFLOW_TERMS if t not in content]
                    if missing_terms:
                        self.add(
                            "blocker",
                            "generic_workflow_missing_structure",
                            f"skills/{skill_dir.name}: generic/fallback workflow SKILL.md missing terms: {missing_terms}",
                        )

    def _verify_root_readme_semantics(self) -> None:
        """Root README.md must contain key semantic markers."""
        readme = self.jarvis_home / "README.md"
        if not readme.is_file():
            return
        try:
            text = readme.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        required_terms = {
            "source-of-truth": [r"source-of-truth|source of truth|权威归属|每个事实只有"],
            "capability_delivery_docs_verification": [
                r"capability.*delivery|capability.*docs.*verification|capability owner.*delivery surface|职责面|capability owner"
            ],
            "workflow_first": [r"workflow-first|优先按闭环|不要先按仓库"],
            "artifact_first": [r"artifact-first|artifact.*first|从.*artifact.*路由"],
            "start_work_verify_end": [r"START.*WORK.*VERIFY.*END"],
            "writeback": [r"writeback|回写|写回"],
            "maintenance_link": [r"MAINTENANCE\.md"],
        }

        for code, patterns in required_terms.items():
            if not any(re.search(p, text, re.IGNORECASE) for p in patterns):
                self.add(
                    "blocker",
                    f"root_readme_{code}_missing",
                    f"README.md missing semantic marker: {code}",
                )

    def _verify_maintenance_semantics(self) -> None:
        """MAINTENANCE.md must contain key semantic markers."""
        maint = self.jarvis_home / "MAINTENANCE.md"
        if not maint.is_file():
            return
        try:
            text = maint.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        required_terms = {
            "history_present_future": [r"History.*Present.*Future|历史.*当前.*未来|三层.*模型|维护模型"],
            "write_contract": [r"写.*契约|write.*contract|写入契约|文件.*契约"],
            "history_replay": [r"history.replay|历史回放|replay.*case|pilot.*replay"],
            "session_self_improvement": [r"session.*self.improve|self.improve|自我改进|jarvis-self-improve"],
            "primary_home_promotion": [r"primary.home|promotion.*ladder|promotion|primary home|归属|promotion ladder"],
        }

        for code, patterns in required_terms.items():
            if not any(re.search(p, text, re.IGNORECASE) for p in patterns):
                self.add(
                    "blocker",
                    f"maintenance_{code}_missing",
                    f"MAINTENANCE.md missing semantic marker: {code}",
                )

    def _verify_jarvis_toml(self) -> None:
        """Parse jarvis.toml with tomllib, check required sections and consistency."""
        jarvis_toml = self.jarvis_home / "jarvis.toml"
        if not jarvis_toml.is_file():
            return
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                self.add("major", "tomllib_unavailable", "cannot parse jarvis.toml: tomllib/tomli not available")
                return

        try:
            parsed = tomllib.loads(jarvis_toml.read_text(encoding="utf-8"))
        except Exception as exc:
            self.add("blocker", "jarvis_toml_invalid", f"jarvis.toml is not valid TOML: {exc}")
            return

        if not isinstance(parsed, dict):
            self.add("blocker", "jarvis_toml_not_dict", "jarvis.toml must be a TOML table")
            return

        required_sections = ["project", "identity", "runtime", "vcs", "bootstrap"]
        for section in required_sections:
            if section not in parsed:
                self.add("blocker", "jarvis_toml_section_missing", f"jarvis.toml missing required section: [{section}]")

        # project section checks
        project = parsed.get("project", {})
        if isinstance(project, dict):
            if not project.get("slug"):
                self.add("blocker", "jarvis_toml_project_slug_missing", "jarvis.toml [project] slug is empty")
            elif self.expected_company_slug and project["slug"] != self.expected_company_slug:
                self.add("blocker", "jarvis_toml_slug_mismatch",
                         f"jarvis.toml project.slug={project['slug']!r}, expected {self.expected_company_slug!r}")

        # runtime section checks
        runtime = parsed.get("runtime", {})
        if isinstance(runtime, dict):
            if not runtime.get("root"):
                self.add("blocker", "jarvis_toml_runtime_root_missing", "jarvis.toml [runtime] root is empty")
            if runtime.get("type") != "jarvis-box":
                self.add("major", "jarvis_toml_runtime_type", f"jarvis.toml [runtime] type should be 'jarvis-box', got {runtime.get('type')!r}")
            if not runtime.get("entry_skill"):
                self.add("blocker", "jarvis_toml_entry_skill_missing", "jarvis.toml [runtime] entry_skill is empty")
            elif self.expected_company_slug:
                expected_entry = f"skills/{self.expected_company_slug}-jarvis/SKILL.md"
                if runtime["entry_skill"] != expected_entry:
                    self.add("blocker", "jarvis_toml_entry_skill_mismatch",
                             f"jarvis.toml runtime.entry_skill={runtime['entry_skill']!r}, expected {expected_entry!r}")

        # identity section checks
        identity = parsed.get("identity", {})
        if isinstance(identity, dict):
            if not identity.get("company"):
                self.add("major", "jarvis_toml_identity_company_missing", "jarvis.toml [identity] company is empty")

        # vcs section checks
        vcs = parsed.get("vcs", {})
        if isinstance(vcs, dict):
            if not vcs.get("host"):
                self.add("major", "jarvis_toml_vcs_host_missing", "jarvis.toml [vcs] host is empty")

        # bootstrap section checks — phase_status_file and result_file must be root files
        bootstrap = parsed.get("bootstrap", {})
        if isinstance(bootstrap, dict):
            psf = bootstrap.get("phase_status_file", "")
            rf = bootstrap.get("result_file", "")
            if psf and psf.startswith("_bootstrap/"):
                self.add(
                    "blocker",
                    "jarvis_toml_bootstrap_path_not_root",
                    f"jarvis.toml [bootstrap] phase_status_file must be a root file, got {psf!r}",
                )
            if rf and rf.startswith("_bootstrap/"):
                self.add(
                    "blocker",
                    "jarvis_toml_bootstrap_path_not_root",
                    f"jarvis.toml [bootstrap] result_file must be a root file, got {rf!r}",
                )
            if psf and "/" in psf and not psf.startswith("_bootstrap/"):
                self.add(
                    "blocker",
                    "jarvis_toml_bootstrap_path_not_root",
                    f"jarvis.toml [bootstrap] phase_status_file must be a root file, got {psf!r}",
                )
            if rf and "/" in rf and not rf.startswith("_bootstrap/"):
                self.add(
                    "blocker",
                    "jarvis_toml_bootstrap_path_not_root",
                    f"jarvis.toml [bootstrap] result_file must be a root file, got {rf!r}",
                )

    def verify_jarvis_box_commands(self) -> None:
        help_commands = self._extract_jarvis_box_root_commands()
        if not help_commands:
            return
        day2_op = self.jarvis_home / "_bootstrap" / "day2-operation.md"
        if not day2_op.is_file():
            return
        try:
            text = day2_op.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        refs: set[str] = set()
        command_patterns = [
            r"`jarvis-box\s+([a-z][a-z0-9-]*)",
            r"(?im)^\s*(?:[-*]\s*)?(?:run|command|execute|recover(?:y)?(?:\s+action)?|运行|命令|恢复动作)\s*:?\s*`?jarvis-box\s+([a-z][a-z0-9-]*)",
            r"(?m)\|\s*`?jarvis-box\s+([a-z][a-z0-9-]*)",
        ]
        for pattern in command_patterns:
            refs.update(re.findall(pattern, text))
        for cmd in sorted(refs):
            if cmd not in help_commands:
                self.add(
                    "blocker",
                    "day2_invented_command",
                    f"_bootstrap/day2-operation.md references jarvis-box {cmd} which is not a root command in --help output",
                )

    # ── phase-09 gate ────────────────────────────────────────────

    def _verify_phase09(self) -> None:
        """Run only checks whose work is due through Phase 9."""
        self.verify_company_home()
        result = self.verify_bootstrap_result()
        state = self.verify_bootstrap_state()
        self.verify_identity_reconciliation(result, state)
        self.verify_company_slug(result, state)
        self.verify_expected_customer_facts(result, state)
        self.verify_repo_skill_packages()
        self.verify_source_dump_resistance()
        self.verify_secret_boundary()
        self.verify_discovery_artifacts()
        self.verify_phase6_placeholders()
        self.verify_durable_e2e_paths()
        self.verify_precise_module_claims()
        self._check_root_placeholders(result, state)
        # Customer-fact safety checks
        self._verify_customer_fact_safety()
        self._verify_module_evidence_pointers()
        self._verify_crosscutting_fact_safety()
        self._verify_routing_repo_mentions()
        self._verify_durable_e2e_customer_paths()
        self._verify_discovery_evidence_pointers()
        # semantic gate checks applicable at Phase 9
        self._verify_generic_module_phrases()
        self._verify_route_section_duplication()
        self._verify_routing_repo_evidence_consistency()
        # Do NOT require Phase 10-14 artifacts

    # ── phase-12-preflight gate ──────────────────────────────────

    def _verify_phase12_preflight(self) -> dict[str, Any]:
        """Only inspect the selected case and visible packet; reject before bridge."""
        case_id = self.case_id
        if not case_id:
            self.add("blocker", "preflight_missing_case_id", "--case-id is required for phase-12-preflight")
            return self._make_report(None)

        case_file = self.jarvis_home / "evals" / "history-replay" / "cases" / case_id / "history-replay-case.md"
        if not case_file.is_file():
            self.add("blocker", "preflight_case_missing", f"case file not found: {case_file}")
            return self._make_report(None)
        try:
            case_text = case_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            self.add("blocker", "preflight_case_unreadable", f"case file cannot be read: {case_file}")
            return self._make_report(None)

        # ── structured field parsing ──
        status_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Status")
        eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Eligibility")
        replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Replay eligibility")

        # ── Must be ready-for-replay (structured field only) ──
        if status_val != "ready-for-replay":
            self.add("blocker", "preflight_case_not_ready",
                     f"{case_id}: Status={status_val!r}, must be ready-for-replay")

        # ── Reject ineligible / low-confidence / needs-better-start / blocked ──
        ineligible_markers = {"ineligible-leaky", "needs-better-start", "low-confidence", "blocked"}
        effective_eligibility = eligibility_val or replay_eligibility_val
        if effective_eligibility in ineligible_markers:
            self.add("blocker", "preflight_case_ineligible",
                     f"{case_id}: eligibility={effective_eligibility!r} — must not call bridge")

        # ── Contradictory state: eligible-reconstructed + low-confidence ──
        # Only from explicit structured fields (Eligibility vs Confidence)
        confidence_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Confidence")
        if replay_eligibility_val == "eligible-reconstructed" and confidence_val == "low-confidence":
            self.add("blocker", "preflight_contradictory_state",
                     f"{case_id}: claims eligible-reconstructed but Confidence={confidence_val!r}")

        # ── Run CaseLeakAnalyzer for verbatim leaks ──
        visible_section = self._extract_section(
            case_text,
            r"#+\s*(?:visible\s*START|visible\s*start|START)",
            r"#+\s*(?:[Hh]idden\s+[Oo]utcome\s+[Oo]racle|[Hh]idden\s+[Oo]racle|隐藏结果)",
        )
        visible_text = visible_section or ""

        # Collect visible-packet text recursively
        visible_packet_text = ""
        visible_packet_dir = (
            self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id / "visible-packet"
        )
        if visible_packet_dir.is_dir():
            for vp_file in visible_packet_dir.rglob("*"):
                if vp_file.is_file() and vp_file.suffix.lower() in TEXT_SUFFIXES:
                    try:
                        visible_packet_text += "\n" + vp_file.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass

        leak_reasons = CaseLeakAnalyzer.analyze(case_text, visible_text, visible_packet_text)
        for lr in leak_reasons:
            self.add("blocker", f"preflight_{lr.code}", f"{case_id}: {lr.message}")

        # ── Structured leak admission field ──
        leak_admitted = CaseLeakAnalyzer._parse_structured_choice(case_text, "Leak admission")
        if leak_admitted in ("yes", "true", "admitted", "partial"):
            self.add("blocker", "preflight_admitted_leak",
                     f"{case_id}: structured field admits oracle leak (Leak admission={leak_admitted!r})")

        # ── Case Readiness Gate fields ──
        case_validity = CaseLeakAnalyzer._parse_structured_choice(case_text, "Case validity")
        if case_validity != "valid":
            self.add("blocker", "preflight_case_validity_invalid",
                     f"{case_id}: Case validity={case_validity!r}, must be 'valid'")
        readiness = CaseLeakAnalyzer._parse_structured_choice(case_text, "Readiness")
        if readiness != "ready":
            self.add("blocker", "preflight_readiness_not_ready",
                     f"{case_id}: Readiness={readiness!r}, must be 'ready'")
        final_artifact_fully_read = CaseLeakAnalyzer._parse_structured_choice(
            case_text, "Final artifact fully read")
        if final_artifact_fully_read != "yes":
            self.add("blocker", "preflight_final_artifact_not_fully_read",
                     f"{case_id}: 'Final artifact fully read'={final_artifact_fully_read!r}, must be 'yes'")
        final_extraction_cmd = CaseLeakAnalyzer._parse_structured_field(
            case_text, "Final artifact extraction command / pointer")
        if not final_extraction_cmd or self._is_placeholder_value(final_extraction_cmd):
            self.add("blocker", "preflight_final_extraction_command_missing",
                     f"{case_id}: missing or placeholder 'Final artifact extraction command / pointer'")

        # ── Visible Packet Fact Closure table check ──
        pfc_section = self._extract_section_text(
            case_text, r'#+\s*Visible\s+Packet\s+Fact\s+Closure',
        )
        pfc_rows = self._parse_table_data_rows(pfc_section, min_columns=4) if pfc_section else []
        if not pfc_rows:
            self.add("blocker", "preflight_packet_fact_closure_empty",
                     f"{case_id}: Visible Packet Fact Closure table missing or has no data rows")
        else:
            for row in pfc_rows:
                closure_result = (row[3] if len(row) > 3 else "").strip().lower()
                if any(self._is_placeholder_value(cell) for cell in row[:3]):
                    self.add("blocker", "preflight_packet_fact_closure_incomplete",
                             f"{case_id}: Packet Fact Closure row has empty/placeholder fact mapping")
                if closure_result != "supported":
                    self.add("blocker", "preflight_packet_fact_closure_unsupported",
                             f"{case_id}: Packet Fact Closure row has Closure Result='{closure_result}', "
                             f"every row must be 'supported'")

        # ── Hidden Facts Excluded From Visible Packet table check ──
        hf_section = self._extract_section_text(
            case_text, r'#+\s*Hidden\s+Facts\s+Excluded\s+From\s+Visible\s+Packet',
        )
        hf_rows = self._parse_table_data_rows(hf_section, min_columns=4) if hf_section else []
        if not hf_rows:
            self.add("blocker", "preflight_hidden_facts_excluded_empty",
                     f"{case_id}: Hidden Facts Excluded From Visible Packet table missing or has no data rows")
        else:
            for row in hf_rows:
                result = (row[3] if len(row) > 3 else "").strip().lower()
                if any(self._is_placeholder_value(cell) for cell in row[:3]):
                    self.add("blocker", "preflight_hidden_fact_review_incomplete",
                             f"{case_id}: Hidden Facts Excluded row has empty/placeholder evidence")
                if result != "absent":
                    self.add("blocker", "preflight_hidden_fact_leaked",
                             f"{case_id}: Hidden Facts Excluded row has Result='{result}', "
                             f"every Result must be 'absent'")

        return self._make_report(None)

    @staticmethod
    def _parse_table_data_rows(section_text: str, min_columns: int = 1) -> list[list[str]]:
        """Parse markdown table, returning only data rows (no header/separator)."""
        rows: list[list[str]] = []
        for line in section_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or not stripped.endswith("|"):
                continue
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if not cells:
                continue
            # Skip separator rows
            if all(re.match(r'^[-:\s]+$', c) for c in cells if c):
                continue
            # Skip header rows: first cell contains a known header token
            first = cells[0].strip().lower() if cells else ""
            if re.match(r'^(?:packet\s+file|事实声明|hidden\s+fact|fact\s+id|file|来源|'
                        r'capability|能力|命令|command|证据指针|evidence\s+pointer|'
                        r'能力|job|managed\s+job|活动|activity)\s*$', first):
                continue
            if len(cells) >= min_columns:
                rows.append(cells)
        return rows

    def _extract_section(self, text: str, start_pattern: str, end_pattern: str | None) -> str | None:
        """Extract a markdown section by heading pattern."""
        start_m = re.search(start_pattern, text, re.IGNORECASE)
        if not start_m:
            return None
        start_pos = start_m.start()
        if end_pattern:
            end_m = re.search(end_pattern, text[start_pos:], re.IGNORECASE)
            if end_m:
                return text[start_pos:start_pos + end_m.start()]
        # Find next heading of same or higher level
        heading_level = len(start_m.group(0).split()[0]) if start_m.group(0).startswith('#') else 2
        rest = text[start_pos + len(start_m.group(0)):]
        next_heading = re.search(rf'^(#{{{1},{heading_level}}})\s', rest, re.MULTILINE)
        if next_heading:
            return text[start_pos:start_pos + len(start_m.group(0)) + next_heading.start()]
        return text[start_pos:]

    # ── customer-fact safety checks (phase-09 and final) ─────────

    # Patterns that indicate fabricated/placeholder customer facts
    CUSTOMER_FACT_PLACEHOLDER_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"BOOTSTRAP_REQUIRED"), "bootstrap_required_sentinel"),
        (re.compile(r"<repo>|<endpoint>|<confirmed\s+company>|<company>|<product>"), "angle_placeholder"),
        (re.compile(r"module-[a-f]\b"), "module_letter_placeholder"),
        (re.compile(r"product-[a-d]\b"), "product_letter_placeholder"),
    ]

    # Old fabricated-template signatures from r5 era
    R5_FABRICATED_SIGNATURES: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"(?i)Placeholder\s+Issue\s+Pattern", re.IGNORECASE), "r5_placeholder_issue_patterns"),
        (re.compile(r"(?i)Placeholder\s+Decision", re.IGNORECASE), "r5_placeholder_decisions"),
        (re.compile(r"(?i)(?:Stale\s+Cache|Timeout\s+Under|Schema\s+Drift|Webhook\s+Duplicate|Configuration\s+Not\s+Reflected)", re.IGNORECASE), "r5_fabricated_issue_pattern"),
        (re.compile(r"(?i)(?:Real-Time\s+Sync|GraphQL\s+API|Self-Service\s+Admin\s+UI)", re.IGNORECASE), "r5_fabricated_rejected_feature"),
        (re.compile(r"(?i)(?:Single\s+Table\s+vs|API\s+Versioning\s+Strategy|Event\s+Bus\s+Choice|Configuration\s+.*File-Based)", re.IGNORECASE), "r5_fabricated_decision"),
        (re.compile(r"(?i)(?:Kafka|GraphQL|Kubernetes)\s+(?:infrastructure|cluster|deployment)", re.IGNORECASE), "r5_fabricated_tech_stack"),
    ]

    FABRICATED_FACT_FILE_GLOBS = [
        "modules/*/overview.md",
        "modules/*/known-issues.md",
        "modules/*/decisions.md",
        "modules/*/rejected-features.md",
        "modules/*/test-coverage.md",
    ]

    def _verify_customer_fact_safety(self) -> None:
        """Reject BOOTSTRAP_REQUIRED, angle placeholders, and r5 fabricated signatures in module files."""
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        for glob_pattern in self.FABRICATED_FACT_FILE_GLOBS:
            for path in sorted(self.jarvis_home.glob(glob_pattern)):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                rel = path.relative_to(self.jarvis_home)
                for pattern, code in self.CUSTOMER_FACT_PLACEHOLDER_PATTERNS:
                    if pattern.search(text):
                        self.add(
                            "blocker",
                            code,
                            f"{rel}: contains customer-fact placeholder matching {pattern.pattern!r}",
                        )
                for pattern, code in self.R5_FABRICATED_SIGNATURES:
                    if pattern.search(text):
                        self.add(
                            "blocker",
                            code,
                            f"{rel}: contains r5-era fabricated template signature matching {pattern.pattern!r}",
                        )

    REQUIRED_OVERVIEW_SECTIONS = [
        (re.compile(r"业务定位|Business\s+Purpose", re.IGNORECASE), "业务定位"),
        (re.compile(r"首跳路由|First.?Hop\s+Routing", re.IGNORECASE), "首跳路由"),
        (re.compile(r"First\s+Proof|首个验证|first.?proof", re.IGNORECASE), "first proof"),
        (re.compile(r"常见\s*False\s*Owner|False\s+Owner", re.IGNORECASE), "常见 false owner"),
        (re.compile(r"证据与入口|Evidence\s*(?:&|and)\s*Entry|证据.*指针|Evidence\s+Pointer", re.IGNORECASE), "证据与入口"),
        (re.compile(r"模块关系|Module\s+(?:Relations|Interactions|Dependencies)", re.IGNORECASE), "模块关系"),
        (re.compile(r"搜索与验证|Search\s*(?:&|and)\s*Verif", re.IGNORECASE), "搜索与验证"),
    ]

    # ── shared evidence pointer extraction from Markdown structure ──

    @staticmethod
    def _extract_section_text(text: str, section_pattern: str) -> str:
        """Extract text under a markdown section heading."""
        m = re.search(section_pattern, text, re.IGNORECASE)
        if not m:
            return ""
        start = m.end()
        rest = text[start:]
        next_heading = re.search(r'^#{1,4}\s', rest, re.MULTILINE)
        if next_heading:
            return rest[:next_heading.start()]
        return rest

    @staticmethod
    def _parse_evidence_table_row_pointers(section_text: str) -> list[str]:
        """Parse evidence/证据与入口 section table rows, returning the first cell
        of EVERY data row (after stripping header/separator rows and wrapping backticks).
        Non-pointer cells are returned as-is — the caller decides validity."""
        pointers: list[str] = []
        for line in section_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or not stripped.endswith("|"):
                continue
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if not cells or not cells[0]:
                continue
            first_cell = cells[0]
            # Skip separator rows (e.g. |---|---|)
            if re.match(r'^[-:\s]+$', first_cell):
                continue
            # Skip header row (exact match for common header labels)
            if re.match(r'^(?:证据指针|evidence\s*pointer|pointer|repo|仓库|Evidence\s+Source)\s*$', first_cell, re.IGNORECASE):
                continue
            # Strip one layer of wrapping backticks
            first_cell = re.sub(r'^`([^`]+)`$', r'\1', first_cell)
            pointers.append(first_cell)
        return pointers

    @staticmethod
    def _parse_routing_target_repos(section_text: str, known_repo_names: set[str]) -> set[str]:
        """Parse 首跳路由/First-Hop Routing section, extract repo names from
        the '路由到' / 'Route to' target column. Only matches known repos as
        whole tokens, not substrings."""
        mentioned: set[str] = set()
        for line in section_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or not stripped.endswith("|"):
                continue
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if len(cells) < 2:
                continue
            # Check the target column (usually column 2, index 1)
            target = cells[1] if len(cells) > 1 else ""
            if not target:
                continue
            # Look for known repo names as whole tokens
            for repo_name in known_repo_names:
                # Whole-word match: repo_name appears as a standalone token in target
                pattern = r'(?:^|\s|[/`(])' + re.escape(repo_name) + r'(?:$|\s|[)/`:,.])'
                if re.search(pattern, target, re.IGNORECASE):
                    mentioned.add(repo_name)
        return mentioned

    @staticmethod
    def _resolve_pointer(repo_name: str, repo_path: str, repos: list[Path]) -> Path | None:
        """Resolve a repo:path pointer against the repo list. repo_name must
        match repo.name exactly (not substring)."""
        for repo in repos:
            if repo.name == repo_name:
                candidate = repo / repo_path
                if candidate.exists():
                    return candidate
        return None

    def _verify_module_evidence_pointers(self) -> None:
        """Every module overview must have required sections, and every evidence-table
        data row must be a canonical <repo>:<repo-relative-path>.  Accepts both
        files and directories.  This single method replaces the old lax check and
        the separate structured check."""
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        for overview_path in sorted(modules_dir.glob("*/overview.md")):
            if not overview_path.is_file():
                continue
            try:
                text = overview_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            module_name = overview_path.parent.name
            rel = f"modules/{module_name}/overview.md"

            # Required sections
            for pattern, section_name in self.REQUIRED_OVERVIEW_SECTIONS:
                if not pattern.search(text):
                    self.add(
                        "blocker",
                        "module_overview_missing_section",
                        f"{rel}: missing required section '{section_name}'",
                    )

            # Parse evidence section table — every data row
            evidence_section = self._extract_section_text(
                text, r'#+\s*(?:证据与入口|Evidence\s*(?:&|and)\s*Entry|Evidence\s+Pointer)',
            )
            cells = self._parse_evidence_table_row_pointers(evidence_section)

            if not cells:
                self.add(
                    "blocker",
                    "module_overview_no_evidence_pointer",
                    f"{rel}: no evidence table data rows found (expected format: repo-name:repo-relative-path in first column)",
                )
                continue

            has_valid = False
            has_bad = False
            for cell in cells:
                # Strip one layer of wrapping backticks (in case parser didn't)
                cell_clean = re.sub(r'^`([^`]+)`$', r'\1', cell)

                # Must have exactly one colon separator
                if ":" not in cell_clean:
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: evidence cell '{cell_clean}' is not a canonical <repo>:<path> pointer")
                    has_bad = True
                    continue

                repo_name, repo_path = cell_clean.split(":", 1)
                # Ellipsis
                if EVIDENCE_POINTER_ELLIPSIS_RE.search(cell_clean):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: ellipsis in evidence pointer '{cell_clean}'")
                    has_bad = True
                    continue
                # Glob
                if EVIDENCE_POINTER_GLOB_RE.search(repo_path):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: glob pattern in evidence pointer '{cell_clean}'")
                    has_bad = True
                    continue
                # Absolute path
                if repo_path.startswith("/"):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: absolute path in evidence pointer '{cell_clean}'")
                    has_bad = True
                    continue
                # Parent-dir segment
                if "/../" in repo_path or repo_path.startswith("../"):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: parent-dir segment in evidence pointer '{cell_clean}'")
                    has_bad = True
                    continue
                # Explanatory suffix
                if re.search(r'(?:—|–|\s-\s)', cell_clean):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: explanatory suffix in evidence pointer '{cell_clean}'")
                    has_bad = True
                    continue
                # Multiple colons or other junk
                if cell_clean.count(":") > 1:
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"{rel}: multiple colons in evidence cell '{cell_clean}'")
                    has_bad = True
                    continue
                # Try resolution
                if self.repos:
                    candidate = self._resolve_pointer(repo_name, repo_path, self.repos)
                    if candidate is None:
                        self.add("blocker", "module_evidence_pointer_invalid",
                                 f"{rel}: unresolvable evidence pointer '{cell_clean}'")
                        has_bad = True
                        continue
                has_valid = True

            if self.repos and not has_valid and not has_bad:
                self.add(
                    "blocker",
                    "module_overview_pointer_unresolvable",
                    f"{rel}: evidence pointers do not resolve to any existing path in provided repos",
                )

    CROSSCUTTING_FACT_FILES = [
        "cross-cutting/module-interactions.md",
        "cross-cutting/peer-product-contracts.md",
        "cross-cutting/version-changelog.md",
    ]

    REFERENCE_FACT_FILES = [
        "references/jarvis-first-routing.md",
        "references/canonical-repo-fleet.md",
    ]

    TOOLS_FACT_FILES = [
        "tools/README.md",
    ]

    def _verify_crosscutting_fact_safety(self) -> None:
        """Fact-bearing cross-cutting/routing/fleet/tools files must not retain BOOTSTRAP_REQUIRED or placeholders."""
        all_files = self.CROSSCUTTING_FACT_FILES + self.REFERENCE_FACT_FILES + self.TOOLS_FACT_FILES
        for rel_path in all_files:
            path = self.jarvis_home / rel_path
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern, code in self.CUSTOMER_FACT_PLACEHOLDER_PATTERNS:
                if pattern.search(text):
                    self.add(
                        "blocker",
                        code,
                        f"{rel_path}: fact-bearing file still contains placeholder matching {pattern.pattern!r}",
                    )
            # Also check for old r5 fabricated signatures in these files
            for pattern, code in self.R5_FABRICATED_SIGNATURES:
                if pattern.search(text):
                    self.add(
                        "blocker",
                        code,
                        f"{rel_path}: contains r5-era fabricated template signature matching {pattern.pattern!r}",
                    )

    WORKFLOW_ROUTE_RE = re.compile(
        r"skills/[A-Za-z0-9_.-]+/SKILL\.md",
    )
    REPO_LOCAL_HANDOFF_RE = re.compile(
        r"(?:repo-local\s+(?:skill|handoff)|Repo-local\s+handoff).*?(?:skills/SKILL\.md|`[^`]+/skills/SKILL\.md`)",
        re.IGNORECASE,
    )

    def _verify_routing_repo_mentions(self) -> None:
        """jarvis-first-routing.md and canonical-repo-fleet.md must mention every customer repo basename."""
        if not self.repos:
            return
        repo_names = {repo.name for repo in self.repos}
        routing_file = self.jarvis_home / "references" / "jarvis-first-routing.md"
        fleet_file = self.jarvis_home / "references" / "canonical-repo-fleet.md"

        for label, path in [("jarvis-first-routing.md", routing_file), ("canonical-repo-fleet.md", fleet_file)]:
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            missing = [name for name in sorted(repo_names) if name not in text]
            if missing:
                self.add(
                    "blocker",
                    "routing_missing_repo_mention",
                    f"{label}: does not mention customer repo(s): {', '.join(missing)}",
                )

        # jarvis-first-routing must contain a real workflow route and repo-local handoff
        if routing_file.is_file():
            try:
                routing_text = routing_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                routing_text = ""
            if not self.WORKFLOW_ROUTE_RE.search(routing_text):
                self.add(
                    "blocker",
                    "routing_no_workflow_route",
                    "references/jarvis-first-routing.md: no real workflow skill route found (expected skills/<name>/SKILL.md)",
                )
            if not self.REPO_LOCAL_HANDOFF_RE.search(routing_text):
                self.add(
                    "blocker",
                    "routing_no_repo_local_handoff",
                    "references/jarvis-first-routing.md: no repo-local handoff evidence found",
                )

    def _verify_durable_e2e_customer_paths(self) -> None:
        """Durable modules/sources/cross-cutting/customer-routing/tools files must not contain /e2e/."""
        for dirname in ("modules", "sources", "cross-cutting", "references", "skills", "tools"):
            root = self.jarvis_home / dirname
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if E2E_ABSOLUTE_PATH_RE.search(text):
                    self.add(
                        "blocker",
                        "durable_output_e2e_absolute_path",
                        f"{path.relative_to(self.jarvis_home)} contains bootstrap-only /e2e/ absolute path",
                    )

    # ── deferred source / replay decision checks (final stage) ───

    def _verify_deferred_source_inputs(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """If a source is deferred-needs-access and result still lists it as missing_input, add blocker."""
        if result is None:
            return
        sources_dir = self.jarvis_home / "sources"
        if not sources_dir.is_dir():
            return
        missing_inputs = result.get("missing_inputs")
        blockers_list = result.get("blockers")
        if not isinstance(missing_inputs, list) and not isinstance(blockers_list, list):
            return
        open_text = ""
        if isinstance(missing_inputs, list):
            open_text += "\n".join(item for item in missing_inputs if isinstance(item, str))
        if isinstance(blockers_list, list):
            open_text += "\n" + "\n".join(item for item in blockers_list if isinstance(item, str))

        for source_readme in sorted(sources_dir.glob("*/README.md")):
            if not source_readme.is_file():
                continue
            try:
                text = source_readme.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "deferred-needs-access" not in text:
                continue
            source_name = source_readme.parent.name
            # If still listed as missing input / blocker for access/credentials
            if re.search(
                rf"{re.escape(source_name)}.*(?:access|credentials?|凭证|权限|不可访问)",
                open_text, re.IGNORECASE,
            ):
                self.add(
                    "blocker",
                    "deferred_source_still_missing_input",
                    f"sources/{source_name}: marked deferred-needs-access but still listed as missing input/blocker for access/credentials",
                )

    def _verify_replay_decision_contradictions(
        self, result: dict[str, Any] | None
    ) -> None:
        """If a low-confidence/ineligible/needs-better case has no_skill_gap/closed decision, add blocker."""
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        if not cases_dir.is_dir():
            return
        for case_file in sorted(cases_dir.glob("*/history-replay-case.md")):
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            case_id = case_file.parent.name
            # Check structured Eligibility / Replay eligibility fields for ineligible markers
            eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Eligibility")
            replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Replay eligibility")
            effective = eligibility_val or replay_eligibility_val
            ineligible_markers = {"ineligible-leaky", "low-confidence", "needs-better-start", "blocked"}
            if effective not in ineligible_markers:
                continue

            # An ineligible case may be fully constructed, but it cannot claim
            # a valid/ready Case Readiness Gate. This contradiction otherwise
            # lets a later agent accidentally invoke the replay bridge.
            status_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Status")
            case_validity = CaseLeakAnalyzer._parse_structured_choice(case_text, "Case validity")
            readiness = CaseLeakAnalyzer._parse_structured_choice(case_text, "Readiness")
            if status_val == "ready-for-replay" or (case_validity == "valid" and readiness == "ready"):
                self.add(
                    "blocker",
                    "ineligible_case_readiness_contradiction",
                    f"{case_id}: eligibility={effective!r} contradicts a valid/ready replay gate",
                )

            decision_file = case_file.parent / "skill-update-decision.md"
            if not decision_file.is_file():
                continue
            try:
                decision_text = decision_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            # Reject no_skill_gap / closed / "skills are validated/sufficient"
            if re.search(
                r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?(?:decision|primary\s*(?:failure\s*)?classification)(?:\*\*)?\s*:\s*`?no_skill_gap\b",
                decision_text,
            ):
                self.add(
                    "blocker",
                    "low_confidence_contradicts_no_skill_gap",
                    f"{case_id}: low-confidence/ineligible case must not have no_skill_gap decision",
                )
            if re.search(r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*:\s*`?closed\b", decision_text):
                self.add(
                    "blocker",
                    "low_confidence_contradicts_closed",
                    f"{case_id}: low-confidence/ineligible case must not have closed status",
                )
            if re.search(
                r"(?i)(?:skills?\s*(?:are|is)\s*(?:validated|sufficient)|existing\s+skills?\s*(?:are|is)\s*(?:sufficient|adequate))",
                decision_text,
            ):
                self.add(
                    "blocker",
                    "low_confidence_contradicts_skills_sufficient",
                    f"{case_id}: low-confidence case claims skills are validated/sufficient",
                )

    def _verify_oracle_inspection_gaps(
        self, result: dict[str, Any] | None
    ) -> None:
        """When failure analysis declares no_skill_gap=yes, require explicit outcome
        evidence pointer.  Structured-field only — no natural-language inference."""
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        if not cases_dir.is_dir():
            return
        for fa_file in sorted(cases_dir.glob("*/replay-failure-analysis.md")):
            if not fa_file.is_file():
                continue
            try:
                fa_text = fa_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            case_id = fa_file.parent.name

            decision_file = fa_file.parent / "skill-update-decision.md"
            decision_text = ""
            if decision_file.is_file():
                try:
                    decision_text = decision_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass

            fa_no_skill_gap = CaseLeakAnalyzer._parse_structured_choice(fa_text, "no_skill_gap")
            decision_no_skill_gap = CaseLeakAnalyzer._parse_structured_choice(
                decision_text, "no_skill_gap"
            )
            if fa_no_skill_gap != "yes" and decision_no_skill_gap != "yes":
                continue

            # Check for outcome evidence via structured pointer field.
            # Accepts: Exact command or artifact pointer, or old equivalent fields.
            # Must be non-empty and not a placeholder (no <...> or [...] wrapping).
            pointer_val = None
            for field_name in [
                "Exact command or artifact pointer",
                "Outcome artifact pointer",
                "Final diff pointer",
                "Final diff / commit pointer",
                "命令",
            ]:
                pointer_val = CaseLeakAnalyzer._parse_structured_field(fa_text, field_name)
                if pointer_val:
                    break

            def _is_valid_pointer(val: str | None) -> bool:
                if not val or not val.strip():
                    return False
                stripped = val.strip()
                if re.match(r'^[<\[]', stripped):
                    return False
                if stripped.lower() in ("<pointer or none>", "<placeholder>", "none", "n/a", ""):
                    return False
                return True

            if _is_valid_pointer(pointer_val):
                continue

            # Also check skill-update-decision.md for evidence.
            if decision_text:
                for field_name in [
                    "Exact command or artifact pointer",
                    "Outcome artifact pointer",
                    "Final diff pointer",
                    "Final diff / commit pointer",
                    "命令",
                ]:
                    pointer_val = CaseLeakAnalyzer._parse_structured_field(decision_text, field_name)
                    if _is_valid_pointer(pointer_val):
                        break

            if not _is_valid_pointer(pointer_val):
                self.add(
                    "major",
                    "oracle_comparison_missing_outcome_evidence",
                    f"{case_id}: no_skill_gap=yes but no non-placeholder outcome evidence "
                    "pointer (Exact command or artifact pointer / Outcome artifact pointer "
                    "/ Final diff pointer) found in failure analysis or decision",
                )

    # ── semantic gate methods ─────────────────────────────────────

    def _normalize_routing_section(self, text: str) -> str:
        """Extract and normalize the first-hop routing section for dedup comparison."""
        m = re.search(
            r'(?:首跳路由|First.?Hop\s+Routing|First.?Hop\s+Route)[:\s]*\n(.*?)(?=\n(?:#{1,4}\s|\Z))',
            text, re.IGNORECASE | re.DOTALL,
        )
        if not m:
            return ""
        section = m.group(1).strip()
        # Normalize: collapse whitespace, lower case, remove markdown formatting
        section = re.sub(r'\s+', ' ', section).lower()
        section = re.sub(r'[*_`|]', '', section)
        return section

    def _verify_generic_module_phrases(self) -> None:
        """Rule 1: when repos are readable, intercept generic module phrases that
        indicate no module-specific evidence was gathered."""
        if not self.repos:
            return
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        for overview_path in sorted(modules_dir.glob("*/overview.md")):
            if not overview_path.is_file():
                continue
            try:
                text = overview_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            module_name = overview_path.parent.name
            rel = f"modules/{module_name}/overview.md"
            for pattern, code in GENERIC_MODULE_PHRASE_PATTERNS:
                if pattern.search(text):
                    self.add(
                        "blocker",
                        code,
                        f"{rel}: contains generic placeholder phrase matching '{code}' — "
                        f"repos are readable, module-specific evidence is required",
                    )

    def _verify_route_section_duplication(self) -> None:
        """Rule 3: 3+ modules sharing identical normalized first-hop routing section
        is a blocker."""
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        route_map: dict[str, list[str]] = {}
        for overview_path in sorted(modules_dir.glob("*/overview.md")):
            if not overview_path.is_file():
                continue
            try:
                text = overview_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            normalized = self._normalize_routing_section(text)
            if normalized:
                route_map.setdefault(normalized, []).append(overview_path.parent.name)

        for route_text, module_names in route_map.items():
            if len(module_names) >= 3 and len(route_text) > 20:
                self.add(
                    "blocker",
                    "route_section_duplication",
                    f"modules {module_names} share identical normalized first-hop routing section — "
                    f"each module needs distinct, evidence-backed routing",
                )

    def _verify_routing_repo_evidence_consistency(self) -> None:
        """Customer repos explicitly mentioned in first-hop routing '路由到' column
        must be supported by that module's own evidence pointers.
        Uses shared table parser for exact token matching."""
        if not self.repos:
            return
        repo_names = {repo.name for repo in self.repos}
        modules_dir = self.jarvis_home / "modules"
        if not modules_dir.is_dir():
            return
        for overview_path in sorted(modules_dir.glob("*/overview.md")):
            if not overview_path.is_file():
                continue
            try:
                text = overview_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            module_name = overview_path.parent.name
            # Use shared parser: extract routing section and parse target column
            routing_section = self._extract_section_text(
                text, r'#+\s*(?:首跳路由|First.?Hop\s+Rout(?:ing|e))',
            )
            mentioned_repos = self._parse_routing_target_repos(routing_section, repo_names)
            # Also validate explicit <repo>:<path> pointers in the routing target column
            routing_target_repo_pointers: list[tuple[str, str, str]] = []  # (repo, path, raw)
            for line in routing_section.splitlines():
                stripped = line.strip()
                if not stripped.startswith("|") or not stripped.endswith("|"):
                    continue
                cells = [c.strip() for c in stripped[1:-1].split("|")]
                if len(cells) < 2:
                    continue
                target = cells[1] if len(cells) > 1 else ""
                if ":" not in target:
                    continue
                # Find <known-repo>:<path> even when the pointer is wrapped in
                # backticks and followed by explanatory prose in the same cell.
                for rn in repo_names:
                    m = re.search(
                        r'(?<![A-Za-z0-9_.-])`?' + re.escape(rn) + r':([^`\s|]+)`?',
                        target,
                    )
                    if m:
                        routing_target_repo_pointers.append((rn, m.group(1), target))
                        break

            # Validate each explicit repo:path in routing target
            for rn, rp, raw in routing_target_repo_pointers:
                ptr = f"{rn}:{rp}"
                if EVIDENCE_POINTER_ELLIPSIS_RE.search(ptr):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"modules/{module_name}: routing target pointer has ellipsis: '{ptr}'")
                elif EVIDENCE_POINTER_GLOB_RE.search(rp):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"modules/{module_name}: routing target pointer has glob: '{ptr}'")
                elif rp.startswith("/") or "/../" in rp or rp.startswith("../"):
                    self.add("blocker", "module_evidence_pointer_invalid",
                             f"modules/{module_name}: routing target pointer is not repo-relative: '{ptr}'")
                elif self.repos:
                    candidate = self._resolve_pointer(rn, rp, self.repos)
                    if candidate is None:
                        self.add("blocker", "module_evidence_pointer_invalid",
                                 f"modules/{module_name}: routing target pointer unresolvable: '{ptr}'")

            if not mentioned_repos:
                continue
            # Check if module's own evidence section covers the mentioned repos
            evidence_section = self._extract_section_text(
                text, r'#+\s*(?:证据与入口|Evidence\s*(?:&|and)\s*Entry|Evidence\s+Pointer)',
            )
            evidence_pointers = self._parse_evidence_table_row_pointers(evidence_section)
            evidence_repos = set()
            for ptr in evidence_pointers:
                if ":" in ptr:
                    evidence_repos.add(ptr.split(":", 1)[0])
            for mentioned_repo in mentioned_repos:
                if mentioned_repo not in evidence_repos:
                    self.add(
                        "blocker",
                        "routing_repo_not_in_evidence",
                        f"modules/{module_name}: routing target mentions repo '{mentioned_repo}' "
                        f"but module evidence pointers do not include it",
                    )

    def _is_case_leaky(self, case_id: str) -> bool:
        """Check if a case has oracle leaks using the shared CaseLeakAnalyzer.
        Considers both explicit ineligible/low-confidence markers (via structured
        field parsing) AND verbatim leaks found by the analyzer."""
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        case_file = cases_dir / case_id / "history-replay-case.md"
        if not case_file.is_file():
            return False
        try:
            case_text = case_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False

        # Explicit markers via structured field parsing
        eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Eligibility")
        replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Replay eligibility")
        effective_eligibility = eligibility_val or replay_eligibility_val
        ineligible_markers = {"ineligible-leaky", "needs-better-start", "low-confidence"}
        if effective_eligibility in ineligible_markers:
            return True

        # Use shared analyzer to detect verbatim leaks
        visible_section = self._extract_section(
            case_text,
            r"#+\s*(?:visible\s*START|visible\s*start|START)",
            r"#+\s*(?:[Hh]idden\s+[Oo]utcome\s+[Oo]racle|[Hh]idden\s+[Oo]racle|隐藏结果)",
        )
        visible_text = visible_section or ""

        # Collect visible-packet text
        visible_packet_text = ""
        vp_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id / "visible-packet"
        if vp_dir.is_dir():
            for vp_file in vp_dir.rglob("*"):
                if vp_file.is_file() and vp_file.suffix.lower() in TEXT_SUFFIXES:
                    try:
                        visible_packet_text += "\n" + vp_file.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass

        leak_reasons = CaseLeakAnalyzer.analyze(case_text, visible_text, visible_packet_text)
        return len(leak_reasons) > 0

    def _verify_replay_leaked_start(self) -> None:
        """For every started replay, check if the case is leaky (explicit markers
        or analyzer-detected). Leaked runs → Phase 12 must be failed,
        status must be failed, decision must be defer/eval-case-gap only."""
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        if not runs_dir.is_dir():
            return
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        for run_dir in sorted(runs_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            case_id = run_dir.name
            exit_code_file = run_dir / "exit-code"
            if not exit_code_file.is_file():
                continue

            if not self._is_case_leaky(case_id):
                continue

            # Leak case started replay — it's an invalid run
            self.add(
                "blocker",
                "replay_leaked_start_executed",
                f"{case_id}: case has oracle leaks (explicit or analyzer-detected) "
                f"but replay was started — this replay is invalid; Phase 12 must be failed",
            )

            # Check bootstrap-result and bootstrap-state: they must have status=failed
            try:
                result = self.load_json(self.jarvis_home / "bootstrap-result.json", "bootstrap-result.json")
            except Exception:
                result = None
            try:
                state = self.load_json(self.jarvis_home / "bootstrap-state.json", "bootstrap-state.json")
            except Exception:
                state = None

            if isinstance(result, dict) and result.get("status") != "failed":
                self.add(
                    "blocker",
                    "replay_leaked_status_not_failed",
                    f"{case_id}: leak case was executed but bootstrap-result.json status "
                    f"is {result.get('status')!r}, must be 'failed'",
                )
            if isinstance(state, dict) and state.get("status") != "failed":
                self.add(
                    "blocker",
                    "replay_leaked_state_status_not_failed",
                    f"{case_id}: leak case was executed but bootstrap-state.json status "
                    f"is {state.get('status')!r}, must be 'failed'",
                )

            # Phase 12 must also be strictly 'failed' in phase maps (missing key is also blocker)
            for source_label, phase_map in [
                ("bootstrap-result.json", result.get("phase_summary") if isinstance(result, dict) else None),
                ("bootstrap-state.json", state.get("phase_status") if isinstance(state, dict) else None),
            ]:
                if not isinstance(phase_map, dict):
                    self.add(
                        "blocker",
                        "replay_leaked_phase12_map_missing",
                        f"{case_id}: leak case was executed but {source_label} "
                        f"has no phase_summary/phase_status at all",
                    )
                    continue
                p12 = phase_map.get("phase-12-history-replay")
                if not p12:
                    self.add(
                        "blocker",
                        "replay_leaked_phase12_key_missing",
                        f"{case_id}: leak case was executed but {source_label} "
                        f"phase-12-history-replay key is missing",
                    )
                elif p12 != "failed":
                    self.add(
                        "blocker",
                        "replay_leaked_phase12_not_failed",
                        f"{case_id}: leak case was executed but {source_label} "
                        f"phase-12-history-replay is {p12!r}, must be 'failed'",
                    )

            # Check skill-update-decision for illegal conclusions
            decision_file = cases_dir / case_id / "skill-update-decision.md"
            if not decision_file.is_file():
                continue
            try:
                dtext = decision_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            # Strip Markdown formatting for robust parsing: remove **, *, ` (not _ which is part of identifiers)
            clean = re.sub(r'[*`]', '', dtext)
            clean = re.sub(r'[ \t]+', ' ', clean)

            # Extract Decision: and Status: values (case-insensitive, multi-line aware)
            decision_val = None
            status_val = None
            for m in re.finditer(r'(?im)^\s*(?:[-*]\s*)?(?:Decision|Status)\s*:\s*(\S+)', clean):
                key = m.group(1).lower()
                if 'decision' in m.group(0).lower():
                    decision_val = key
                else:
                    status_val = key

            # Positive allowlist for leak cases
            allowed_decisions = {"defer", "deferred", "eval-case-gap", "not-evaluated"}
            allowed_statuses = {"deferred", "not-evaluated", "failed"}

            if decision_val and decision_val.lower() not in allowed_decisions:
                self.add(
                    "blocker",
                    f"replay_leaked_illegal_decision_{decision_val.replace(' ', '_')}",
                    f"{case_id}: leak case has illegal Decision '{decision_val}' — "
                    f"only {sorted(allowed_decisions)} allowed",
                )
            if status_val and status_val.lower() not in allowed_statuses:
                self.add(
                    "blocker",
                    f"replay_leaked_illegal_status_{status_val.replace(' ', '_')}",
                    f"{case_id}: leak case has illegal Status '{status_val}' — "
                    f"only {sorted(allowed_statuses)} allowed",
                )

            # Check Primary Home / primary writeback section for durable claims
            primary_section = ""
            pm = re.search(r'(?i)#+\s*Primary\s+Home', dtext)
            if pm:
                rest = dtext[pm.end():]
                nh = re.search(r'^#{1,4}\s', rest, re.MULTILINE)
                primary_section = rest[:nh.start()] if nh else rest

            forbidden_homes = (
                "repo-local",
                "company jarvis",
                "source",
                "workflow",
                "upstream",
                "company",
            )
            primary_home = None
            for line in primary_section.splitlines():
                normalized_line = re.sub(r'[*`]', '', line).strip()
                if not normalized_line or re.search(
                    r'(?i)\b(?:not|none|n/?a)\b|(?:不(?:是|属于|写入)|非)',
                    normalized_line,
                ):
                    continue
                for home in forbidden_homes:
                    if re.search(rf'(?<![A-Za-z0-9_.-]){re.escape(home)}(?![A-Za-z0-9_.-])', normalized_line, re.IGNORECASE):
                        primary_home = home
                        break
                if primary_home:
                    break
            if primary_home:
                self.add(
                    "blocker",
                    f"replay_leaked_illegal_primary_home_{primary_home.replace(' ', '_')}",
                    f"{case_id}: leak case Primary Home section claims '{primary_home}' — "
                    f"durable writeback not allowed for leak cases",
                )

            # Check for explicit durable/reusable skill gap claims
            if re.search(r'(?i)\b(?:durable|reusable)\s+skill\s+gap\b', dtext):
                self.add(
                    "blocker",
                    "replay_leaked_illegal_durable_skill_gap",
                    f"{case_id}: leak case claims durable/reusable skill gap — not allowed",
                )

    def _verify_phase_status_consistency(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Rules 8-9: result/state phase map consistency, top-level status,
        summary completion claims must not overclaim."""
        result_phase_summary = None
        state_phase_status = None
        result_status = None
        state_status = None

        if isinstance(result, dict):
            result_phase_summary = result.get("phase_summary")
            result_status = result.get("status")
        if isinstance(state, dict):
            state_phase_status = state.get("phase_status")
            state_status = state.get("status")

        # Rule 9a: same-named phase must be consistent across result and state
        all_phase_keys: set[str] = set()
        if isinstance(result_phase_summary, dict):
            all_phase_keys.update(result_phase_summary.keys())
        if isinstance(state_phase_status, dict):
            all_phase_keys.update(state_phase_status.keys())

        for key in sorted(all_phase_keys):
            rv = result_phase_summary.get(key) if isinstance(result_phase_summary, dict) else None
            sv = state_phase_status.get(key) if isinstance(state_phase_status, dict) else None
            if rv and sv and rv != sv:
                self.add(
                    "blocker",
                    "phase_status_mismatch",
                    f"{key}: bootstrap-result.json has '{rv}' but bootstrap-state.json has '{sv}'",
                )

        # Rule 9b: top-level status must be consistent
        if result_status and state_status and result_status != state_status:
            self.add(
                "blocker",
                "top_level_status_mismatch",
                f"bootstrap-result.json status='{result_status}' but "
                f"bootstrap-state.json status='{state_status}'",
            )

        # Rule 9c: any prior phase not completed → summary must not claim "complete through Phase N"
        if isinstance(result, dict):
            summary = result.get("summary", "")
            complete_through = re.search(
                r"complete\s+(?:through|up\s+to)\s+(?:Phase|phase)\s*(\d+)",
                summary, re.IGNORECASE,
            )
            if complete_through:
                claimed_n = int(complete_through.group(1))
                if isinstance(result_phase_summary, dict):
                    for phase_n in range(3, claimed_n + 1):
                        phase_key = next(
                            (k for k in result_phase_summary if f"phase-{phase_n:02d}" in k), None
                        )
                        if phase_key and result_phase_summary.get(phase_key) != "completed":
                            self.add(
                                "blocker",
                                "summary_completion_overclaim",
                                f"summary claims 'complete through Phase {claimed_n}' but "
                                f"{phase_key} is {result_phase_summary.get(phase_key)!r}",
                            )
                            break

        # Rule 9d: Phase 12 not completed → Phase 13/14 must not be completed
        phase12_completed = any(
            isinstance(d, dict) and d.get(k) == "completed"
            for d in [result_phase_summary, state_phase_status] if isinstance(d, dict)
            for k in d if "phase-12" in k
        )
        if not phase12_completed:
            for d in [result_phase_summary, state_phase_status]:
                if not isinstance(d, dict):
                    continue
                for k in d:
                    if ("phase-13" in k or "phase-14" in k) and d.get(k) == "completed":
                        self.add(
                            "blocker",
                            "downstream_phase_completed_before_phase12",
                            f"{k} is completed but phase-12-history-replay is not completed",
                        )

    @staticmethod
    def _phase_number(value: Any) -> int | None:
        if not isinstance(value, str):
            return None
        if value in PHASE_KEYS:
            return PHASE_KEYS.index(value) + 3
        match = re.search(r"(?:^|\b)phase-(\d{1,2})(?:\b|-)", value, re.IGNORECASE)
        if not match:
            return None
        number = int(match.group(1))
        return number if 3 <= number <= 14 else None

    def _verify_phase_progression(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Final-stage state machine checks for Phase 3 through Phase 14."""
        in_progress_sources = []
        if isinstance(result, dict) and result.get("status") == "in-progress":
            in_progress_sources.append("bootstrap-result.json")
        if isinstance(state, dict) and state.get("status") == "in-progress":
            in_progress_sources.append("bootstrap-state.json")
        if in_progress_sources:
            self.add(
                "blocker",
                "bootstrap_still_in_progress",
                "final verifier received an unfinished checkpoint status in "
                + ", ".join(in_progress_sources),
            )

        if not isinstance(state, dict):
            return
        current_number = self._phase_number(state.get("phase"))
        if current_number is None:
            return

        phase_maps: list[tuple[str, Any]] = [
            (
                "bootstrap-result.json phase_summary",
                result.get("phase_summary") if isinstance(result, dict) else None,
            ),
            ("bootstrap-state.json phase_status", state.get("phase_status")),
        ]
        for source, phase_map in phase_maps:
            if not isinstance(phase_map, dict):
                continue
            for key, status in sorted(phase_map.items()):
                phase_number = self._phase_number(key)
                if phase_number is None or phase_number <= current_number:
                    continue
                if status != "pending":
                    self.add(
                        "blocker",
                        "future_phase_status_preclassified",
                        f"{source} marks future {key} as {status!r} while current phase is {state.get('phase')!r}; future phases must stay 'pending'",
                    )

        state_phase_status = state.get("phase_status")
        if current_number < 14 and isinstance(state_phase_status, dict):
            current_completed = any(
                self._phase_number(key) == current_number and status == "completed"
                for key, status in state_phase_status.items()
            )
            if current_completed:
                self.add(
                    "blocker",
                    "completed_current_phase_not_advanced",
                    f"bootstrap-state.json phase still points to completed {state.get('phase')!r}; it must advance to Phase {current_number + 1}",
                )

    def _is_valid_replay(self, case_id: str) -> bool:
        """A replay is valid only if: exit=0, non-empty artifacts exist,
        isolation evidence is present, AND the case is NOT leaky (checked via
        shared analyzer, not just explicit markers)."""
        run_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs" / case_id
        if not run_dir.is_dir():
            return False
        exit_code = self._read_run_exit_code(run_dir)
        if exit_code != 0:
            return False
        if not (run_dir / "replay-agent.jsonl").is_file() or \
           (run_dir / "replay-agent.jsonl").stat().st_size == 0:
            return False
        if not (run_dir / "replay-result.md").is_file() or \
           (run_dir / "replay-result.md").stat().st_size == 0:
            return False
        # Must have isolation evidence
        if not (run_dir / "host-isolation-evidence.json").is_file():
            return False
        # Must NOT be leaky
        if self._is_case_leaky(case_id):
            return False
        return True

    def _verify_missing_input_contradictions(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Self-contradicting missing inputs — each item judged individually."""
        if not isinstance(result, dict):
            return

        missing_inputs = result.get("missing_inputs")
        if isinstance(missing_inputs, list):
            for item in missing_inputs:
                if not isinstance(item, str):
                    continue
                # Flag items that declare themselves non-blocking but still appear
                if re.search(r"\bdeferred.needs.access\b.*\bnot\s+first.workflow\b", item, re.IGNORECASE) or \
                   re.search(r"\bdeferred\b.*\bnon.critical\b|\bnon.critical\b.*\bdeferred\b", item, re.IGNORECASE):
                    self.add(
                        "blocker",
                        "deferred_still_missing_input",
                        f"missing_input item marked deferred+non-critical should not block: '{item[:120]}'",
                    )
                # Scaffold-only maturation / owner-provided artifacts
                if re.search(r"create.scaffold.needs.pilot|scaffold.only.maturation|"
                             r"scaffold.only\s+workflows?\b.*\bneed\s+owner\b|"
                             r"scaffold.only.*owner.provided\s+artifacts?",
                             item, re.IGNORECASE):
                    self.add(
                        "blocker",
                        "scaffold_maturation_as_missing_input",
                        f"missing_input item is scaffold-only maturation (backlog): '{item[:120]}'",
                    )

        # Build open text for cross-item checks
        open_text = ""
        for field in ["missing_inputs", "blockers", "unresolved_questions"]:
            values = result.get(field)
            if isinstance(values, list):
                open_text += "\n".join(v for v in values if isinstance(v, str)) + "\n"

        # Already have valid replay, still requesting additional cases
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        has_valid_replay = False
        if runs_dir.is_dir():
            for run_dir in runs_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                if self._is_valid_replay(run_dir.name):
                    has_valid_replay = True
                    break
        if has_valid_replay and re.search(
            r"additional\s+(?:replay\s+)?cases?\b|more\s+(?:replay\s+)?cases?\b|"
            r"additional\s+history\s+replay|补充.*replay|更多.*case",
            open_text, re.IGNORECASE,
        ):
            self.add(
                "blocker",
                "additional_cases_after_valid_replay",
                "missing_inputs requests additional replay cases but a valid replay "
                "already exists — additional cases are backlog, not missing input",
            )

        # Confirmed alternative scheduler listed as missing input
        if re.search(
            r"(?:external\s+scheduler|Kubernetes\s+CronJob|human.run|operator.confirmed|"
            r"human.run\s+checklist)\s+(?:is|as|confirmed|available)",
            open_text, re.IGNORECASE,
        ):
            if re.search(r"(?:scheduler|schedule|cron).*(?:missing|not\s+configured|not\s+found)",
                         open_text, re.IGNORECASE):
                self.add(
                    "blocker",
                    "scheduler_contradiction",
                    "missing_inputs both confirms alternative scheduler mechanism AND "
                    "lists scheduler as missing — contradiction",
                )

    def _verify_pilot_email_redaction(self) -> None:
        """Pilot/shadow artifact authors/committers must have ALL emails redacted.
        No whitelist — any email address in a pilot artifact is a blocker."""
        pilot_dir = self.jarvis_home / "_bootstrap" / "shadow-pilot"
        if not pilot_dir.is_dir():
            return
        for path in pilot_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            emails = EMAIL_RE.findall(text)
            if emails:
                rel = path.relative_to(self.jarvis_home)
                self.add(
                    "blocker",
                    "pilot_email_unredacted",
                    f"{rel}: contains unredacted email(s): {', '.join(emails[:3])}",
                )

    def _verify_day2_runtime_root_consistency(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Day2/result runtime root must match confirmed runtime root exactly."""
        confirmed_root = None
        if isinstance(state, dict):
            paths = state.get("paths")
            if isinstance(paths, dict):
                confirmed_root = paths.get("runtime_root")
            if not confirmed_root:
                inputs = state.get("inputs")
                if isinstance(inputs, dict):
                    confirmed_root = inputs.get("jarvis_box_home") or inputs.get("runtime_root")

        if not confirmed_root:
            return
        confirmed = Path(str(confirmed_root)).resolve()

        # Helper: extract runtime root from env path patterns like <root>/envs/.env.jarvis-box
        def _extract_root_from_text(text: str) -> set[Path]:
            roots: set[Path] = set()
            # Match explicit <path>/envs/.env.jarvis-box
            for m in re.finditer(r'([/\w.-]+)/envs/\.env\.jarvis-box', text):
                roots.add(Path(m.group(1)).resolve())
            # Match runtime_root=<path> or JARVIS_RUNTIME_ROOT=<path>
            for m in re.finditer(r'(?:runtime_root|JARVIS_RUNTIME_ROOT|jarvis_box_home)\s*[=:]\s*([/\w.-]+)', text):
                roots.add(Path(m.group(1)).resolve())
            return roots

        # Check day2-operation.md
        day2_op = self.jarvis_home / "_bootstrap" / "day2-operation.md"
        if day2_op.is_file():
            try:
                op_text = day2_op.read_text(encoding="utf-8", errors="replace")
            except OSError:
                op_text = ""
            for observed in _extract_root_from_text(op_text):
                if observed != confirmed:
                    self.add(
                        "blocker",
                        "day2_runtime_root_mismatch",
                        f"_bootstrap/day2-operation.md references runtime root "
                        f"'{observed}' but confirmed root is '{confirmed}'; "
                        f"this is a check context error, not a missing input",
                    )

        # Check bootstrap-result.json open items
        if isinstance(result, dict):
            open_text = "\n".join(
                item
                for field in ("missing_inputs", "blockers")
                for item in (result.get(field) if isinstance(result.get(field), list) else [])
                if isinstance(item, str)
            )
            for observed in _extract_root_from_text(open_text):
                if observed != confirmed:
                    self.add(
                        "blocker",
                        "runtime_root_confusion_in_result",
                        f"bootstrap-result.json references runtime root '{observed}' "
                        f"but confirmed runtime_root is '{confirmed}'",
                    )

    # ── deterministic guards (r9) ──────────────────────────────────

    def _verify_discovery_retrieval_commands(self) -> None:
        """Guard 1: retrieval commands in evidence-inventory.md must be real."""
        evidence_path = self.jarvis_home / "_bootstrap" / "discovery" / "evidence-inventory.md"
        if not evidence_path.is_file():
            return
        try:
            text = evidence_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        # Find the Evidence Retrieval Commands section (EN + CN headings)
        section_pattern = re.compile(
            r"#+\s*(?:Evidence\s+Retrieval\s+Commands?|证据.*检索.*命令|检索命令|证据获取.*命令)",
            re.IGNORECASE,
        )
        m = section_pattern.search(text)
        if not m:
            return
        start = m.end()
        rest = text[start:]
        next_heading = re.search(r"^#{1,4}\s", rest, re.MULTILINE)
        section = rest[:next_heading.start()] if next_heading else rest

        for line in section.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            # Check for ASCII ellipsis or unicode ellipsis in command/table rows
            if "..." in stripped or "…" in stripped:
                self.add(
                    "blocker",
                    "discovery_retrieval_command_invalid",
                    f"_bootstrap/discovery/evidence-inventory.md: retrieval command contains ellipsis: {stripped[:120]}",
                )
            # Check for pseudo-path phrase
            if "repo checkout" in stripped.lower():
                self.add(
                    "blocker",
                    "discovery_retrieval_command_invalid",
                    f"_bootstrap/discovery/evidence-inventory.md: retrieval command uses pseudo-path 'repo checkout': {stripped[:120]}",
                )

    def _verify_discovery_evidence_pointers(self) -> None:
        """All repo:path pointers in the Phase 6 evidence package must resolve."""
        if not self.repos:
            return
        discovery_dir = self.jarvis_home / "_bootstrap" / "discovery"
        if not discovery_dir.is_dir():
            return

        repo_by_name = {repo.name: repo for repo in self.repos}
        placeholder_pattern = re.compile(
            r"<(?:module|repo|path|query|endpoint|source)(?:[-_ ][^>]*)?>|"
            r"\{\{[A-Z_][A-Z0-9_]*\}\}|\bBOOTSTRAP_REQUIRED\b",
            re.IGNORECASE,
        )
        reported: set[tuple[str, str]] = set()

        for filename in REQUIRED_DISCOVERY_FILES:
            path = discovery_dir / filename
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(path.relative_to(self.jarvis_home))

            # generation-plan.md may intentionally use <module>/<source> as
            # command metavariables. Truth-bearing discovery maps may not.
            if filename != "generation-plan.md" and placeholder_pattern.search(text):
                self.add(
                    "blocker",
                    "discovery_evidence_placeholder",
                    f"{rel}: contains an unresolved discovery placeholder",
                )

            for repo_name, repo in repo_by_name.items():
                pattern = re.compile(
                    r"(?<![A-Za-z0-9_.-])"
                    + re.escape(repo_name)
                    + r":([^`\s|,;]+)"
                )
                for match in pattern.finditer(text):
                    raw_repo_path = match.group(1).rstrip(".)]")
                    pointer = f"{repo_name}:{raw_repo_path}"
                    key = (rel, pointer)
                    if key in reported:
                        continue
                    reported.add(key)

                    repo_path = raw_repo_path.split("#", 1)[0]
                    invalid = (
                        not repo_path
                        or EVIDENCE_POINTER_ELLIPSIS_RE.search(repo_path) is not None
                        or EVIDENCE_POINTER_GLOB_RE.search(repo_path) is not None
                        or repo_path.startswith("/")
                        or repo_path.startswith("../")
                        or "/../" in repo_path
                        or not (repo / repo_path).exists()
                    )
                    if invalid:
                        self.add(
                            "blocker",
                            "discovery_evidence_pointer_invalid",
                            f"{rel}: discovery evidence pointer does not resolve: {pointer!r}",
                        )

    def _verify_confirmed_product_identity_unresolved(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Guard 2: confirmed product identity must not stay unresolved."""
        expected = self.expected_product_identity
        if not expected:
            return

        texts: list[tuple[str, str]] = []

        # Root README
        readme = self.jarvis_home / "README.md"
        if readme.is_file():
            try:
                texts.append(("README.md", readme.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                pass

        # jarvis.toml
        toml = self.jarvis_home / "jarvis.toml"
        if toml.is_file():
            try:
                texts.append(("jarvis.toml", toml.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                pass

        # Company entry SKILL.md
        if self.expected_company_slug:
            entry = self.jarvis_home / "skills" / f"{self.expected_company_slug}-jarvis" / "SKILL.md"
        else:
            # Find any jarvis entry skill
            entry = None
            skills_dir = self.jarvis_home / "skills"
            if skills_dir.is_dir():
                for p in skills_dir.glob("*/SKILL.md"):
                    if "jarvis" in p.parent.name.lower():
                        entry = p
                        break
        if entry and entry.is_file():
            try:
                texts.append((str(entry.relative_to(self.jarvis_home)), entry.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                pass

        # All module overview.md
        modules_dir = self.jarvis_home / "modules"
        if modules_dir.is_dir():
            for overview in sorted(modules_dir.glob("*/overview.md")):
                if not overview.is_file():
                    continue
                try:
                    texts.append((str(overview.relative_to(self.jarvis_home)), overview.read_text(encoding="utf-8", errors="replace")))
                except OSError:
                    pass

        for rel, text in texts:
            # Check for literal 'unresolved-product-identity'
            if "unresolved-product-identity" in text.lower():
                self.add(
                    "blocker",
                    "confirmed_product_identity_unresolved",
                    f"{rel}: contains 'unresolved-product-identity' — product identity must be confirmed",
                )
            # A generic owner-confirmation note elsewhere in the file can refer
            # to modules or routes. Only the structured identity field itself
            # may contradict a confirmed product identity.
            for line in text.splitlines():
                if not re.search(
                    r"(?:Product\s+Identity|产品[^|:\n]*(?:标识|身份))\s*[|:]",
                    line,
                    re.IGNORECASE,
                ):
                    continue
                if expected.lower() not in line.lower():
                    continue
                if re.search(r"needs-owner-confirmation", line, re.IGNORECASE):
                    self.add(
                        "blocker",
                        "confirmed_product_identity_unresolved",
                        f"{rel}: Product Identity field contains both {expected!r} and needs-owner-confirmation",
                    )
                    break

    def _verify_company_entry_references_and_handoffs(self) -> None:
        """Guard 3: company entry must have valid reference links and repo handoffs."""
        # Find company entry skill
        entry_path = None
        entry_text = ""
        skills_dir = self.jarvis_home / "skills"
        if skills_dir.is_dir():
            for p in skills_dir.glob("*/SKILL.md"):
                if "jarvis" in p.parent.name.lower():
                    entry_path = p
                    try:
                        entry_text = p.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass
                    break

        if not entry_path or not entry_text:
            return

        # Parse references/*.md paths mentioned in the entry
        ref_pattern = re.compile(r"references/([A-Za-z0-9_.-]+\.md)")
        mentioned_refs = set(ref_pattern.findall(entry_text))
        refs_dir = self.jarvis_home / "references"
        for ref_name in sorted(mentioned_refs):
            if not (refs_dir / ref_name).is_file():
                self.add(
                    "blocker",
                    "entry_reference_missing",
                    f"{entry_path.relative_to(self.jarvis_home)} references references/{ref_name} which does not exist",
                )

        # Locate repo-local execution/handoff section
        handoff_section = ""
        for heading_pat in [
            r"#+\s*(?:repo-local\s+(?:execution|handoff)|Repo-local\s+(?:Execution|Handoff)|"
            r"仓库.*执行|仓库.*交付|repo.*执行.*交付)",
        ]:
            m = re.search(heading_pat, entry_text, re.IGNORECASE)
            if m:
                start = m.end()
                rest = entry_text[start:]
                next_heading = re.search(r"^#{1,4}\s", rest, re.MULTILINE)
                handoff_section = rest[:next_heading.start()] if next_heading else rest
                break

        # If no explicit handoff section, search the entire entry for repo mentions
        search_text = handoff_section if handoff_section else entry_text

        if self.repos:
            repo_names = {repo.name for repo in self.repos}
            for repo_name in sorted(repo_names):
                # Exact word-boundary match
                if not re.search(r'\b' + re.escape(repo_name) + r'\b', search_text):
                    self.add(
                        "blocker",
                        "entry_repo_handoff_missing",
                        f"customer repo '{repo_name}' not mentioned in company entry repo-local execution/handoff section",
                    )

    def _resolve_git_default_branch(self, repo: Path) -> str | None:
        """Resolve the default branch from remote HEAD without guessing from checkout."""
        try:
            proc = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                ref = proc.stdout.strip()
                if ref.startswith("refs/remotes/origin/"):
                    return ref.removeprefix("refs/remotes/origin/")
        except (OSError, subprocess.TimeoutExpired):
            pass

        # Support lightweight fixtures and repositories whose loose ref can be read
        # even when a full git command is unavailable.
        try:
            head_ref = (repo / ".git" / "refs" / "remotes" / "origin" / "HEAD")
            if head_ref.is_file():
                ref_text = head_ref.read_text(encoding="utf-8", errors="replace").strip()
                # ref: refs/remotes/origin/main → main
                if ref_text.startswith("ref: "):
                    return ref_text.split("/")[-1]
        except OSError:
            pass
        return None

    def _verify_source_route_filling(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Guard 5: accessible source routes must have filled README.md."""
        sources_dir = self.jarvis_home / "sources"
        if not sources_dir.is_dir():
            return

        repo_names = {repo.name for repo in self.repos} if self.repos else set()

        # Parse generation-plan.md Source/Status table
        plan_path = self.jarvis_home / "_bootstrap" / "discovery" / "generation-plan.md"
        accessible_from_plan: set[str] = set()
        deferred_from_plan: set[str] = set()
        if plan_path.is_file():
            try:
                plan_text = plan_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                plan_text = ""
            # Find Source/Status table
            for line in plan_text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("|") or not stripped.endswith("|"):
                    continue
                cells = [c.strip() for c in stripped[1:-1].split("|")]
                if len(cells) < 2:
                    continue
                # Check if first cell looks like a source name (not header/separator)
                source_candidate = cells[0]
                if re.match(r'^[-:\s]+$', source_candidate):
                    continue
                if re.match(r'^(?:Source|Status|来源|状态)\s*$', source_candidate, re.IGNORECASE):
                    continue
                # Check status column (usually column 2, but could be later)
                for cell in cells[1:]:
                    if re.search(r'\b(?:included|mapped|route-created)\b', cell, re.IGNORECASE):
                        accessible_from_plan.add(source_candidate)
                        break
                    if re.search(r'\b(?:deferred-needs-access|needs-access|blocked)\b', cell, re.IGNORECASE):
                        deferred_from_plan.add(source_candidate)
                        break

        # Get gitlab_host_confirmed from state
        gitlab_host = None
        if isinstance(state, dict):
            confirmed = state.get("confirmed_answers")
            if isinstance(confirmed, dict):
                gitlab_host = confirmed.get("gitlab_host_confirmed")

        # Placeholder patterns for unfilled truth-bearing fields
        unfilled_patterns = [
            (re.compile(r"\bneeds-evidence\b", re.IGNORECASE), "needs-evidence"),
            (re.compile(r"\bREFERENCES_PATH\b"), "REFERENCES_PATH"),
            (re.compile(r"\bBOOTSTRAP_REQUIRED\b"), "BOOTSTRAP_REQUIRED"),
            (re.compile(r"<repo>|<endpoint>|<source>|<path>|<host>|<token>"), "angle_placeholder"),
        ]

        for source_readme in sorted(sources_dir.glob("*/README.md")):
            if not source_readme.is_file():
                continue
            source_name = source_readme.parent.name
            try:
                text = source_readme.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            # Determine if accessible
            is_accessible = source_name in accessible_from_plan or source_name in repo_names

            # Determine if deferred: only from generation-plan status or structured README fields.
            # Full-text scan for "blocked"/"needs-access" is NOT used — enumeration descriptions
            # like "confirmed / needs-credentials / request-pending / blocked" must not trigger deferred.
            is_deferred = source_name in deferred_from_plan
            if not is_deferred:
                # Check structured README fields: - **Access 状态**: <value> / - **Route 状态**: <value>
                access_match = re.search(
                    r'(?im)^\s*[-*]\s+\*\*(?:Access\s*(?:状态|status))\*\*\s*[:：]\s*(\S+)',
                    text,
                )
                route_match = re.search(
                    r'(?im)^\s*[-*]\s+\*\*(?:Route\s*(?:状态|status))\*\*\s*[:：]\s*(\S+)',
                    text,
                )
                deferred_values = {
                    "deferred",
                    "blocked",
                    "needs-access",
                    "needs-credentials",
                    "request-pending",
                    "deferred-needs-access",
                    "not-accessible",
                }

                def structured_status(match: re.Match[str] | None) -> str | None:
                    if not match:
                        return None
                    value = re.split(r"[（(]", match.group(1), maxsplit=1)[0]
                    return value.strip().strip("`*_\"'").lower()

                if structured_status(access_match) in deferred_values:
                    is_deferred = True
                elif structured_status(route_match) in deferred_values:
                    is_deferred = True

            if not is_accessible:
                continue  # Not accessible, skip
            if is_deferred:
                continue  # Deferred sources may keep honest deferred fields

            # Check for unfilled patterns
            for pattern, desc in unfilled_patterns:
                if pattern.search(text):
                    self.add(
                        "blocker",
                        "source_route_unfilled",
                        f"sources/{source_name}/README.md: accessible source route contains unfilled {desc}",
                    )
                    break  # one per source

            # Host mismatch check (supports plain and Markdown bold: - **Host**: gitlab.example.com)
            if gitlab_host and is_accessible:
                host_match = re.search(
                    r"(?im)^\s*(?:[-*]\s+)?(?:\*\*)?(?:Host|GitLab\s*Host|主机|host)(?:\*\*)?\s*[:|]\s*(\S+)", text,
                )
                if host_match:
                    source_host = host_match.group(1).strip().strip("`*_\"'")
                    if source_host and source_host != gitlab_host:
                        # Skip if explicitly local-only/filesystem-only
                        if re.search(r"\b(?:local-only|filesystem-only|本地)\b", text, re.IGNORECASE):
                            continue
                        self.add(
                            "blocker",
                            "source_route_host_mismatch",
                            f"sources/{source_name}/README.md: Host {source_host!r} != confirmed {gitlab_host!r}",
                        )

    # ── repo-local path and command extraction helpers ─────────────

    @staticmethod
    def _extract_repo_relative_paths(text: str) -> list[str]:
        """Extract backticked repo-relative path tokens and Markdown link targets.
        Remove #fragment before resolution. Returns deduplicated list."""
        paths: list[str] = []
        seen: set[str] = set()

        # Backticked paths: `path/to/file.java`, `path/to/dir/`
        for m in re.finditer(r'`([^`\n]+)`', text):
            token = m.group(1).strip()
            token = re.sub(r'#.*$', '', token)  # Remove fragment
            if token and token not in seen:
                seen.add(token)
                paths.append(token)

        # Markdown link targets: [text](path)
        for m in re.finditer(r'\]\(([^)\s]+)\)', text):
            target = m.group(1).strip()
            target = re.sub(r'#.*$', '', target)  # Remove fragment
            if target and target not in seen:
                seen.add(target)
                paths.append(target)

        return paths

    @staticmethod
    def _is_safe_repo_relative_path(token: str) -> bool:
        """Check if a token is a safe repo-relative path candidate.
        Rejects absolute paths, parent traversal, glob, URLs, placeholders."""
        if not token or not token.strip():
            return False
        token = token.strip()
        if token.startswith('/'):
            return False  # Absolute path
        if token.startswith('../') or '/../' in token:
            return False  # Parent traversal
        if re.search(r'[*?\[\]]', token):
            return False  # Glob
        if re.match(r'^https?://', token):
            return False  # URL
        if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', token):
            return False  # Any URI scheme
        if re.search(r'\s', token):
            return False  # Command/prose, not a path token
        if re.search(r'[;&|$(){}]', token):
            return False  # Shell-like token
        if re.search(r'[<>]', token):
            return False  # Placeholder brackets
        if re.search(r'\.{3}|…', token):
            return False  # Ellipsis
        if token == '.' or token == '..':
            return False
        return True

    @staticmethod
    def _extract_commands_from_sections(text: str) -> list[str]:
        """Extract concrete commands from Build/Test/Lint/Type Check sections.
        Parses Command/命令 table columns and fenced/backticked command lines.
        Accepts any non-placeholder concrete command; no tool-name allowlist."""
        BUILD_TEST_HEADING_RE = re.compile(
            r'^#{1,6}\s+[^\n]*(?:Build|Test|Lint|Type\s*Check|构建|测试|类型检查)[^\n]*$',
            re.IGNORECASE | re.MULTILINE,
        )
        commands: list[str] = []
        seen: set[str] = set()

        def concrete_command(raw: str) -> str | None:
            command = raw.strip().strip('`').strip()
            if command.startswith('$ '):
                command = command[2:].strip()
            lowered = command.lower()
            if lowered in {
                "", "n/a", "none", "unknown", "tbd", "todo", "无",
                "not-observed", "not-applicable", "未观察到",
            }:
                return None
            if re.fullmatch(r'<[^>]+>', command) or "{{" in command or "}}" in command:
                return None
            if re.search(r'\.{3}|…|\bplaceholder\b|占位', command, re.IGNORECASE):
                return None
            return command

        # Find all sections matching the heading patterns
        section_ranges: list[tuple[int, int]] = []
        for m in BUILD_TEST_HEADING_RE.finditer(text):
            start = m.end()
            rest = text[start:]
            next_heading = re.search(r'^#{1,6}\s', rest, re.MULTILINE)
            end = start + next_heading.start() if next_heading else len(text)
            section_ranges.append((start, end))

        if not section_ranges:
            return commands

        for sec_start, sec_end in section_ranges:
            section = text[sec_start:sec_end]

            # 1. Parse table rows: look for Command/命令 column header
            lines = section.splitlines()
            for header_index, line in enumerate(lines):
                stripped = line.strip()
                if not stripped.startswith('|') or not stripped.endswith('|'):
                    continue
                cells = [c.strip() for c in stripped[1:-1].split('|')]
                if not cells:
                    continue
                cmd_col_idx = None
                for i, cell in enumerate(cells):
                    if re.match(r'(?:命令|Command|command|指令)\s*$', cell, re.IGNORECASE):
                        cmd_col_idx = i
                        break
                if cmd_col_idx is None:
                    continue
                for data_line in lines[header_index + 1:]:
                    data_stripped = data_line.strip()
                    if not data_stripped.startswith('|') or not data_stripped.endswith('|'):
                        break
                    data_cells = [c.strip() for c in data_stripped[1:-1].split('|')]
                    if all(re.match(r'^[-:\s]+$', c) for c in data_cells if c):
                        continue
                    if len(data_cells) <= cmd_col_idx:
                        continue
                    command = concrete_command(data_cells[cmd_col_idx])
                    if command and command not in seen:
                        seen.add(command)
                        commands.append(command)

            # 2. Extract fenced code block commands
            for fm in re.finditer(r'```(?:bash|sh|shell|console|text)?\s*\n(.+?)```', section, re.DOTALL):
                for line in fm.group(1).splitlines():
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.startswith('#'):
                        continue
                    command = concrete_command(stripped)
                    if command and command not in seen:
                        seen.add(command)
                        commands.append(command)

            # 3. Extract inline backticked commands (3+ chars, contains a space = likely command)
            for bm in re.finditer(r'`([^`\n]{3,})`', section):
                token = bm.group(1).strip()
                if ' ' not in token and not token.startswith('./') and not re.fullmatch(
                    r'[A-Za-z][A-Za-z0-9_-]*', token
                ):
                    continue
                command = concrete_command(token)
                if command and command not in seen:
                    seen.add(command)
                    commands.append(command)

        return commands

    def _verify_repo_local_truth(self) -> None:
        """Guard 6: repo-local packages must contain observable repo truth."""
        if not self.repos:
            return

        TRUTH_FILES = [
            "skills/SKILL.md",
            "skills/references/architecture-map.md",
            "skills/references/test-entrypoints.md",
            "skills/references/runtime-and-testability.md",
            "skills/references/source-of-truth.md",
        ]

        # Angle placeholder patterns
        ANGLE_PLACEHOLDER_RE = re.compile(
            r"<(?:from\s+company\s+Jarvis|command|relative-path|module-\d|repo|endpoint|"
            r"confirmed\s+company|company|product|path|token|host|source)>",
            re.IGNORECASE,
        )
        GENERATED_NEEDS_OWNER_RE = re.compile(
            r"generated-needs-owner-confirmation|generated.*needs.*owner",
            re.IGNORECASE,
        )
        REPLACE_WITH_ACTUAL_RE = re.compile(
            r"replace\s+with\s+actual|替换为实际|用实际.*替换",
            re.IGNORECASE,
        )
        BOOTSTRAP_SENTINEL_RE = re.compile(r"\bBOOTSTRAP_REQUIRED\b")
        UNRENDERED_TOKEN_RE = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
        BOOTSTRAP_PHASE_NARRATION_RE = re.compile(r"\bPhase\s*8\b", re.IGNORECASE)

        DEFAULT_BRANCH_RE = re.compile(
            r"(?im)^\s*(?:[-*]\s+)?(?:\*\*)?(?:default\s+branch|默认分支|主分支)(?:\*\*)?\s*[:|]\s*(\S+)",
        )

        repo_truth_signatures: list[tuple[str, str]] = []  # (repo_name, normalized_hash)

        for repo in self.repos:
            repo_name = repo.name
            if not (repo / "skills").is_dir():
                continue

            for rel_path in TRUTH_FILES:
                path = repo / rel_path
                if not path.is_file():
                    self.add(
                        "blocker",
                        "repo_local_truth_file_missing",
                        f"{repo_name}: required repo-local truth file is missing: {rel_path}",
                    )
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue

                if BOOTSTRAP_SENTINEL_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_truth_placeholder",
                        f"{repo_name}: {rel_path} contains BOOTSTRAP_REQUIRED",
                    )
                if UNRENDERED_TOKEN_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_truth_placeholder",
                        f"{repo_name}: {rel_path} contains an unrendered template token",
                    )

                # Check for angle placeholders
                if ANGLE_PLACEHOLDER_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_truth_placeholder",
                        f"{repo_name}: {rel_path} contains angle placeholder",
                    )
                # Check for "replace with actual"
                if REPLACE_WITH_ACTUAL_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_truth_placeholder",
                        f"{repo_name}: {rel_path} contains 'replace with actual' example",
                    )
                # Check for generated-needs-owner-confirmation
                if GENERATED_NEEDS_OWNER_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_truth_placeholder",
                        f"{repo_name}: {rel_path} has generated-needs-owner-confirmation state",
                    )

            narration_files = [*TRUTH_FILES, "skills/code-review/SKILL.md"]
            for rel_path in narration_files:
                path = repo / rel_path
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if BOOTSTRAP_PHASE_NARRATION_RE.search(text):
                    self.add(
                        "blocker",
                        "repo_local_bootstrap_narration",
                        f"{repo_name}: {rel_path} retains Phase 8 bootstrap narration",
                    )

            # Default branch check in skills/SKILL.md
            skill_md = repo / "skills" / "SKILL.md"
            if skill_md.is_file():
                try:
                    skill_text = skill_md.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    skill_text = ""
                branch_match = DEFAULT_BRANCH_RE.search(skill_text)
                if not branch_match:
                    self.add(
                        "blocker",
                        "repo_local_default_branch_missing",
                        f"{repo_name}: skills/SKILL.md does not state the default branch",
                    )
                else:
                    stated_raw = branch_match.group(1).strip().strip('`')
                    # Extract just the branch token: strip parenthetical notes
                    # e.g. "main (confirm from repo config)" → "main"
                    stated_branch = re.sub(r'\s*\(.*$', '', stated_raw).strip().rstrip('.,;:')
                    observed_branch = self._resolve_git_default_branch(repo)
                    if not observed_branch:
                        self.add(
                            "blocker",
                            "repo_local_default_branch_unverified",
                            f"{repo_name}: no remote HEAD evidence is available to verify stated default branch '{stated_branch}'",
                        )
                    elif stated_branch != observed_branch:
                        self.add(
                            "blocker",
                            "repo_local_default_branch_mismatch",
                            f"{repo_name}: skills/SKILL.md states default branch '{stated_branch}' but observed branch is '{observed_branch}'",
                        )

            # Architecture-map must have a concrete repo-relative path.
            # Accepts any safe existing repo-relative file or directory, including
            # top-level files (pom.xml, README.md, .gitlab-ci.yml) and directories
            # (bootstrap/, service/, action/).
            arch_map = repo / "skills" / "references" / "architecture-map.md"
            if arch_map.is_file():
                try:
                    arch_text = arch_map.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    arch_text = ""
                has_concrete = False
                for token in self._extract_repo_relative_paths(arch_text):
                    if not self._is_safe_repo_relative_path(token):
                        continue
                    candidate = token.strip()
                    if candidate.startswith('./'):
                        candidate = candidate[2:]
                    if candidate and (repo / candidate).exists():
                        has_concrete = True
                        break
                if not has_concrete:
                    self.add(
                        "blocker",
                        "repo_local_architecture_unmapped",
                        f"{repo_name}: skills/references/architecture-map.md has no concrete repo-relative path that resolves",
                    )

            # Test-entrypoints must have a concrete build/test/lint/typecheck command.
            # Parses Build/Test/Lint/Type Check sections (and Chinese equivalents),
            # accepting any non-placeholder concrete command from table cells or
            # fenced/backticked command lines. No tool-name allowlist.
            test_ep = repo / "skills" / "references" / "test-entrypoints.md"
            if test_ep.is_file():
                try:
                    test_text = test_ep.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    test_text = ""
                commands = self._extract_commands_from_sections(test_text)
                if not commands:
                    self.add(
                        "blocker",
                        "repo_local_test_command_missing",
                        f"{repo_name}: skills/references/test-entrypoints.md has no concrete build/test/lint/typecheck command",
                    )

            # Source-of-truth must have a concrete repo-relative pointer.
            # Accepts any safe existing repo-relative file or directory, including
            # top-level files (pom.xml, README.md, .gitlab-ci.yml) and directories
            # (bootstrap/, service/, action/).
            sot = repo / "skills" / "references" / "source-of-truth.md"
            if sot.is_file():
                try:
                    sot_text = sot.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    sot_text = ""
                has_pointer = False
                for token in self._extract_repo_relative_paths(sot_text):
                    if not self._is_safe_repo_relative_path(token):
                        continue
                    candidate = token.strip()
                    if candidate.startswith('./'):
                        candidate = candidate[2:]
                    if candidate and (repo / candidate).exists():
                        has_pointer = True
                        break
                if not has_pointer:
                    self.add(
                        "blocker",
                        "repo_local_source_truth_unmapped",
                        f"{repo_name}: skills/references/source-of-truth.md has no concrete repo-relative pointer that resolves",
                    )

            # Collect normalized truth for dedup
            normalized_parts: list[str] = []
            for rel_path in TRUTH_FILES:
                path = repo / rel_path
                if path.is_file():
                    try:
                        t = path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        t = ""
                    # Normalize: replace repo name, collapse whitespace
                    t = re.sub(r'\b' + re.escape(repo_name) + r'\b', 'REPO', t, flags=re.IGNORECASE)
                    t = re.sub(r'\s+', ' ', t)
                    normalized_parts.append(t)
            norm_hash = hashlib.sha256("".join(normalized_parts).encode()).hexdigest()
            repo_truth_signatures.append((repo_name, norm_hash))

        # Dedup check: 3+ repos with identical normalized truth
        sig_groups: dict[str, list[str]] = {}
        for rname, sig in repo_truth_signatures:
            sig_groups.setdefault(sig, []).append(rname)
        for sig, rnames in sig_groups.items():
            if len(rnames) >= 3:
                self.add(
                    "blocker",
                    "repo_local_truth_duplicated",
                    f"repos {sorted(rnames)} have identical normalized truth-bearing content",
                )

    def _verify_pilot_structure(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Guard 7: completed Phase 11 must have structurally honest pilot artifacts."""
        # Check if Phase 11 is completed
        phase11_completed = False
        if isinstance(result, dict):
            ps = result.get("phase_summary")
            if isinstance(ps, dict) and ps.get("phase-11-shadow-pilot") == "completed":
                phase11_completed = True
        if isinstance(state, dict):
            ps = state.get("phase_status")
            if isinstance(ps, dict) and ps.get("phase-11-shadow-pilot") == "completed":
                phase11_completed = True

        if not phase11_completed:
            return

        pilot_dir = self.jarvis_home / "_bootstrap" / "shadow-pilot"
        registry = pilot_dir / "pilot-registry.md"
        if not registry.is_file():
            self.add(
                "blocker",
                "pilot_required_artifact_missing",
                "_bootstrap/shadow-pilot/pilot-registry.md must exist when Phase 11 is completed",
            )

        # At least one pilot dir must have shadow-pilot-run.md and pilot-evidence.md
        pilot_dirs = sorted(p for p in pilot_dir.glob("pilot-*") if p.is_dir()) if pilot_dir.is_dir() else []
        has_complete = False
        for pdir in pilot_dirs:
            run_file = pdir / "shadow-pilot-run.md"
            evidence_file = pdir / "pilot-evidence.md"
            if run_file.is_file() and evidence_file.is_file():
                has_complete = True
                break

        if not has_complete:
            self.add(
                "blocker",
                "pilot_required_artifact_missing",
                "Phase 11 completed but no pilot dir contains both shadow-pilot-run.md and pilot-evidence.md",
            )
            return

        for pdir in pilot_dirs:
            run_file = pdir / "shadow-pilot-run.md"
            if not run_file.is_file():
                continue
            try:
                run_text = run_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            missing_sections = []
            for pattern, name in PILOT_SECTION_PATTERNS:
                if not pattern.search(run_text):
                    missing_sections.append(name)

            if missing_sections:
                self.add(
                    "blocker",
                    "pilot_section_missing",
                    f"{pdir.name}/shadow-pilot-run.md: missing sections: {', '.join(missing_sections)}",
                )

            # Check PASS/not-run contradiction: only when both appear on the SAME line.
            # Skip quote/reference lines (starting with >).
            # Different items having PASS vs not-run separately is legitimate.
            evidence_file = pdir / "pilot-evidence.md"
            evidence_text = ""
            if evidence_file.is_file():
                try:
                    evidence_text = evidence_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    pass
            combined = run_text + "\n" + evidence_text

            for line in combined.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith(">"):
                    continue
                has_pass = bool(re.search(
                    r"(?i)\bPASS\b|✅.*PASS|通过",
                    stripped,
                ))
                has_not_run = bool(re.search(
                    r"(?i)(?:not\s+run|not\s+executed|did\s+not\s+run|was\s+not\s+run|"
                    r"not\s+tested|未运行|未执行|没有运行|没有执行)",
                    stripped,
                ))
                if has_pass and has_not_run:
                    self.add(
                        "blocker",
                        "pilot_verification_contradiction",
                        f"{pdir.name}: same line claims PASS/通过 but also says not run/未运行",
                    )
                    break

    @staticmethod
    def _normalize_coverage_cell(value: str) -> str:
        return value.strip().strip("`*_\"' ").strip()

    def _valid_search_coverage_sources(
        self,
        registry_text: str,
        section_pattern: str,
        min_columns: int,
    ) -> set[str]:
        """Return sources whose canonical search-coverage row proves work ran."""
        section = self._extract_section_text(registry_text, section_pattern)
        if not section:
            return set()
        valid_sources: set[str] = set()
        allowed_statuses = {"scanned", "eligible-found", "needs-input", "blocked"}
        unscanned_values = {
            "not-scanned",
            "not scanned",
            "unscanned",
            "not-observed",
            "not observed",
            "not-run",
            "not run",
            "not-applicable",
            "not applicable",
            "deferred",
            "pending",
            "未扫描",
            "未执行",
        }
        for row in self._parse_table_data_rows(section, min_columns=min_columns):
            source = self._normalize_coverage_cell(row[0])
            command = self._normalize_coverage_cell(row[1])
            boundary = self._normalize_coverage_cell(row[2])
            status = self._normalize_coverage_cell(row[-1]).lower()
            if any(self._is_placeholder_value(value) for value in (source, command, boundary)):
                continue
            if any(
                self._normalize_coverage_cell(value).lower() in unscanned_values
                for value in (command, boundary, row[-1])
            ):
                continue
            if status not in allowed_statuses:
                continue
            valid_sources.add(source)
        return valid_sources

    def _has_complete_pilot_artifact_closure(self) -> bool:
        pilot_dir = self.jarvis_home / "_bootstrap" / "shadow-pilot"
        if not pilot_dir.is_dir():
            return False
        for pdir in sorted(path for path in pilot_dir.glob("pilot-*") if path.is_dir()):
            run_file = pdir / "shadow-pilot-run.md"
            evidence_file = pdir / "pilot-evidence.md"
            if not run_file.is_file() or not evidence_file.is_file():
                continue
            if run_file.stat().st_size == 0 or evidence_file.stat().st_size == 0:
                continue
            try:
                run_text = run_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if all(pattern.search(run_text) for pattern, _ in PILOT_SECTION_PATTERNS):
                return True
        return False

    def _verify_shadow_pilot_repo_scan(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Phase 11 cannot request an artifact before exhausting authorized repos."""
        phase11_stopped = False
        for phase_map in (
            result.get("phase_summary") if isinstance(result, dict) else None,
            state.get("phase_status") if isinstance(state, dict) else None,
        ):
            if isinstance(phase_map, dict) and phase_map.get("phase-11-shadow-pilot") in {
                "needs-input",
                "blocked",
            }:
                phase11_stopped = True
        if not phase11_stopped or not self.repos or self._has_complete_pilot_artifact_closure():
            return

        registry = self.jarvis_home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md"
        valid_sources: set[str] = set()
        if registry.is_file():
            try:
                registry_text = registry.read_text(encoding="utf-8", errors="replace")
            except OSError:
                registry_text = ""
            valid_sources = self._valid_search_coverage_sources(
                registry_text,
                r"(?m)^#{1,6}\s+Artifact\s+Search\s+Coverage\s*$",
                min_columns=6,
            )

        for repo_name in sorted({repo.name for repo in self.repos}):
            if repo_name not in valid_sources:
                self.add(
                    "blocker",
                    "shadow_pilot_repo_scan_missing",
                    f"{repo_name}: Phase 11 stopped without a canonical Artifact Search Coverage row proving the repo was scanned",
                )

    def _has_valid_eligible_replay_closure(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> bool:
        """Check if there's at least one valid eligible replay closure."""
        runs_dir = self.jarvis_home / "_bootstrap" / "history-replay-runs"
        if not runs_dir.is_dir():
            return False
        cases_dir = self.jarvis_home / "evals" / "history-replay" / "cases"
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            case_id = run_dir.name
            case_file = cases_dir / case_id / "history-replay-case.md"
            if not case_file.is_file():
                continue
            try:
                case_text = case_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Must have eligibility (structured fields only)
            eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Eligibility")
            replay_eligibility_val = CaseLeakAnalyzer._parse_structured_choice(case_text, "Replay eligibility")
            effective = eligibility_val or replay_eligibility_val
            if effective not in {"eligible-direct", "eligible-reconstructed"}:
                continue
            # Must have exit-code=0 and non-empty artifacts
            exit_code = self._read_run_exit_code(run_dir)
            if exit_code != 0:
                continue
            if not (run_dir / "replay-agent.jsonl").is_file():
                continue
            if (run_dir / "replay-agent.jsonl").stat().st_size == 0:
                continue
            if not (run_dir / "replay-result.md").is_file():
                continue
            if (run_dir / "replay-result.md").stat().st_size == 0:
                continue
            return True
        return False

    def _verify_history_replay_repo_scan(
        self, result: dict[str, Any] | None, state: dict[str, Any] | None
    ) -> None:
        """Guard 8: Phase 12 can't claim missing input after scanning only part of repo fleet."""
        # Check if there's already a valid eligible replay closure
        if self._has_valid_eligible_replay_closure(result, state):
            return  # One valid closure completes Phase 12; additional cases are backlog

        # Check if Phase 12 is needs-input or blocked
        phase12_needs_input = False
        if isinstance(result, dict):
            ps = result.get("phase_summary")
            if isinstance(ps, dict):
                p12 = ps.get("phase-12-history-replay")
                if p12 in ("needs-input", "blocked"):
                    phase12_needs_input = True
        if isinstance(state, dict):
            ps = state.get("phase_status")
            if isinstance(ps, dict):
                p12 = ps.get("phase-12-history-replay")
                if p12 in ("needs-input", "blocked"):
                    phase12_needs_input = True

        if not phase12_needs_input:
            return

        if not self.repos:
            return

        registry = self.jarvis_home / "evals" / "history-replay" / "replay-case-registry.md"
        if not registry.is_file():
            # No registry at all when there are repos → every repo is missing
            for repo in self.repos:
                self.add(
                    "blocker",
                    "history_replay_repo_scan_missing",
                    f"{repo.name}: not recorded in evals/history-replay/replay-case-registry.md (registry missing)",
                )
            return

        try:
            registry_text = registry.read_text(encoding="utf-8", errors="replace")
        except OSError:
            registry_text = ""

        valid_sources = self._valid_search_coverage_sources(
            registry_text,
            r"(?m)^#{1,6}\s+Search\s+Coverage\s*$",
            min_columns=7,
        )
        for repo_name in sorted({repo.name for repo in self.repos}):
            if repo_name not in valid_sources:
                self.add(
                    "blocker",
                    "history_replay_repo_scan_missing",
                    f"{repo_name}: missing a canonical Search Coverage row proving the repo was scanned",
                )

    def _make_report(self, result: dict[str, Any] | None) -> dict[str, Any]:
        blocker_count = sum(1 for f in self.findings if f.severity == "blocker")
        major_count = sum(1 for f in self.findings if f.severity == "major")
        minor_count = sum(1 for f in self.findings if f.severity == "minor")
        status = "pass" if blocker_count == 0 and major_count == 0 else "fail"
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "scope": "machine checks only; final acceptance is acceptance.md",
            "jarvis_home": str(self.jarvis_home),
            "repo_count": len(self.repos),
            "bootstrap_status": result.get("status") if isinstance(result, dict) else None,
            "finding_counts": {
                "blocker": blocker_count,
                "major": major_count,
                "minor": minor_count,
            },
            "findings": [f.to_dict() for f in self.findings],
        }

    def load_json(self, path: Path, label: str) -> dict[str, Any] | None:
        if not path.exists():
            self.add("blocker", "json_missing", f"{label} missing: {path}")
            return None
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.add("blocker", "json_invalid", f"{label} is invalid JSON: {exc}")
            return None
        if not isinstance(parsed, dict):
            self.add("blocker", "json_not_object", f"{label} must be a JSON object")
            return None
        return parsed


def discover_repos(customer_repos_dir: Path | None, explicit_repos: list[Path]) -> list[Path]:
    repos: list[Path] = []
    seen: set[Path] = set()
    for repo in explicit_repos:
        resolved = repo.resolve()
        if resolved not in seen:
            seen.add(resolved)
            repos.append(resolved)
    if customer_repos_dir and customer_repos_dir.exists():
        for child in sorted(customer_repos_dir.iterdir()):
            if not child.is_dir():
                continue
            if not (child / ".git").exists():
                continue
            resolved = child.resolve()
            if resolved not in seen:
                seen.add(resolved)
                repos.append(resolved)
    return repos


def write_report_md(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Bootstrap Output Verification",
        "",
        f"- status: {report['status']}",
        f"- scope: {report.get('scope')}",
        f"- jarvis_home: {report['jarvis_home']}",
        f"- repo_count: {report['repo_count']}",
        f"- bootstrap_status: {report.get('bootstrap_status') or 'unknown'}",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    if not findings:
        lines.append("- no findings")
    else:
        for finding in findings:
            lines.append(f"- {finding['severity']} [{finding['code']}]: {finding['message']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify company Jarvis bootstrap output.")
    parser.add_argument("--jarvis-home", required=True, type=Path, help="Generated company Jarvis home.")
    parser.add_argument("--customer-repos-dir", type=Path, help="Directory containing customer repo checkouts.")
    parser.add_argument("--repo", action="append", default=[], type=Path, help="Explicit customer repo checkout. Can be repeated.")
    parser.add_argument("--expected-company-slug", help="Expected confirmed company slug from jarvis-box/runtime handoff.")
    parser.add_argument("--expected-product-identity", help="Expected confirmed product identity from runtime/customer facts.")
    parser.add_argument("--expected-module", action="append", default=[], help="Expected module directory name. Can be repeated.")
    parser.add_argument("--expected-source", action="append", default=[], help="Expected source route directory name. Can be repeated.")
    parser.add_argument("--expected-skill", action="append", default=[], help="Expected skill directory name. Can be repeated.")
    parser.add_argument("--skip-precheck", action="store_true", help="Do not execute repo-local precheck scripts.")
    parser.add_argument("--jarvis-box-help-file", type=Path, help="Path to jarvis-box --help output for command validation.")
    parser.add_argument("--replay-bridge-helper", type=Path, help="Optional executable host-isolation bridge helper available to bootstrap.")
    parser.add_argument("--stage", choices=["final", "phase-09", "phase-12-preflight"], default="final",
                       help="Verification stage: phase-09 (Phase 3-9 checks only), phase-12-preflight (pre-bridge safety gate), final (default, all checks).")
    parser.add_argument("--case-id", help="Case ID for phase-12-preflight stage.")
    parser.add_argument("--report-json", type=Path, help="Write machine-readable verification report.")
    parser.add_argument("--report-md", type=Path, help="Write human-readable verification report.")
    args = parser.parse_args()

    if args.stage == "phase-12-preflight" and not args.case_id:
        parser.error("--case-id is required when --stage=phase-12-preflight")

    repos = discover_repos(args.customer_repos_dir, args.repo)
    verifier = Verifier(
        args.jarvis_home.resolve(),
        repos,
        run_precheck=not args.skip_precheck,
        expected_company_slug=args.expected_company_slug,
        expected_product_identity=args.expected_product_identity,
        expected_modules=args.expected_module,
        expected_sources=args.expected_source,
        expected_skills=args.expected_skill,
        jarvis_box_help_file=args.jarvis_box_help_file.resolve() if args.jarvis_box_help_file else None,
        replay_bridge_helper=args.replay_bridge_helper.resolve() if args.replay_bridge_helper else None,
        stage=args.stage,
        case_id=args.case_id,
    )
    report = verifier.verify()

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.report_md:
        args.report_md.parent.mkdir(parents=True, exist_ok=True)
        write_report_md(args.report_md, report)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
