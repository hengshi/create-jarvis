"""Deterministic verifier tests — tempfile only, no real customer repos."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# ponytail: importlib so we can load a non-package script
import importlib.util as _iu

_SPEC = _iu.spec_from_file_location(
    "verify_bootstrap_output",
    Path(__file__).resolve().parents[1] / "scripts" / "verify_bootstrap_output.py",
)
_MOD = _iu.module_from_spec(_SPEC)
sys.modules["verify_bootstrap_output"] = _MOD  # ponytail: dataclass needs __module__ in sys.modules
_SPEC.loader.exec_module(_MOD)
Verifier = _MOD.Verifier  # type: ignore[name-defined]


def _touch(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _touch_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


class DiscoveryArtifactsTests(unittest.TestCase):
    def test_missing_discovery_directory_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "jarvis"
            _touch(home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
            _touch(home / "bootstrap-state.json", "{}")
            v = Verifier(home, [], run_precheck=False)
            report = v.verify()
            codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
            self.assertIn("discovery_dir_missing", codes)

    def test_missing_discovery_files_are_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "jarvis"
            _touch(home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
            _touch(home / "bootstrap-state.json", "{}")
            (home / "_bootstrap" / "discovery").mkdir(parents=True)
            # none of the required files exist
            v = Verifier(home, [], run_precheck=False)
            report = v.verify()
            codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
            self.assertIn("discovery_file_missing", codes)
            # all 5 should be missing
            missing = [f for f in report["findings"] if f["code"] == "discovery_file_missing"]
            self.assertEqual(len(missing), 5)

    def test_empty_discovery_files_are_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "jarvis"
            _touch(home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
            _touch(home / "bootstrap-state.json", "{}")
            disco = home / "_bootstrap" / "discovery"
            for name in _MOD.REQUIRED_DISCOVERY_FILES:
                _touch(disco / name, "")  # empty
            v = Verifier(home, [], run_precheck=False)
            report = v.verify()
            codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
            self.assertIn("discovery_file_empty", codes)
            self.assertEqual(len([f for f in report["findings"] if f["code"] == "discovery_file_empty"]), 5)

    def test_nonempty_discovery_files_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "jarvis"
            _touch(home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
            _touch(home / "bootstrap-state.json", "{}")
            disco = home / "_bootstrap" / "discovery"
            for name in _MOD.REQUIRED_DISCOVERY_FILES:
                _touch(disco / name, "present")
            v = Verifier(home, [], run_precheck=False)
            report = v.verify()
            codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
            self.assertNotIn("discovery_file_missing", codes)
            self.assertNotIn("discovery_file_empty", codes)


class Phase6PlaceholderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "modules" / "app").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self) -> Path:
        repo = Path(self.td.name) / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        return repo

    def test_placeholder_in_overview_with_repos_is_blocker(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "待 Phase 6 扫描补充证据")
        repo = self._make_repo()
        v = Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase6_placeholder_cn_scan", codes)

    def test_placeholder_without_repos_is_not_checked(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "pending Phase 6 work")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase6_placeholder_en", codes)

    def test_e2e_absolute_path_in_overview_is_blocker(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "source at /e2e/customer-repos/app")
        repo = self._make_repo()
        v = Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("durable_output_e2e_absolute_path", codes)

    def test_english_pending_phase6_is_blocker(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "pending Phase 6 analysis")
        repo = self._make_repo()
        v = Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase6_placeholder_en", codes)

    def test_clean_overview_passes(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "evidence confirmed from customer repo analysis")
        repo = self._make_repo()
        v = Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase6_placeholder_cn_scan", codes)
        self.assertNotIn("durable_output_e2e_absolute_path", codes)

    def test_e2e_absolute_path_in_source_is_blocker(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "evidence confirmed")
        _touch(self.home / "sources" / "docs" / "README.md", "path: /e2e/customer-repos/docs")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("durable_output_e2e_absolute_path", codes)

    def test_precise_route_without_discovery_evidence_is_blocker(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "- API / contract: `/api/app/create`")
        discovery = self.home / "_bootstrap" / "discovery"
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(discovery / name, "app module evidence without endpoint")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_route_without_discovery_evidence", codes)

    def test_precise_route_with_discovery_evidence_passes(self) -> None:
        _touch(self.home / "modules" / "app" / "overview.md", "- API / contract: `/api/app/create`")
        discovery = self.home / "_bootstrap" / "discovery"
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(discovery / name, "observed endpoint /api/app/create")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("module_route_without_discovery_evidence", codes)


class HistoryReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "evals" / "history-replay" / "cases" / "case-1").mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-1").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_nonzero_exit_with_no_skill_gap_is_blocker(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "decision: no_skill_gap")
        _touch(case_dir / "replay-failure-analysis.md", "analysis")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("nonzero_replay_no_skill_gap", codes)

    def test_ineligible_case_cannot_claim_ready_gate(self) -> None:
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(
            case_dir / "history-replay-case.md",
            "Replay eligibility: ineligible-leaky\n"
            "Case validity: valid\n"
            "Readiness: ready\n",
        )
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("ineligible_case_readiness_contradiction", codes)

    def test_nonzero_exit_with_closed_is_blocker(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "status: closed")
        _touch(case_dir / "replay-failure-analysis.md", "analysis")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("nonzero_replay_closed", codes)

    def test_nonzero_exit_missing_defer_is_blocker(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "decision: not_sure")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("nonzero_replay_no_defer", codes)

    def test_nonzero_exit_with_deferred_passes(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "decision: deferred pending better start")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("nonzero_replay_no_skill_gap", codes)
        self.assertNotIn("nonzero_replay_closed", codes)
        self.assertNotIn("nonzero_replay_no_defer", codes)

    def test_nonzero_exit_with_not_evaluated_passes(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "decision: not-evaluated")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("nonzero_replay_no_defer", codes)

    def test_nonzero_exit_template_heading_does_not_imply_no_skill_gap(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "Decision: defer\nStatus: deferred")
        _touch(case_dir / "replay-failure-analysis.md", "## no_skill_gap check\nPrimary classification: not-evaluated")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("nonzero_replay_no_skill_gap", codes)

    def test_zero_exit_missing_jsonl_is_blocker(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        # replay-agent.jsonl missing
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("zero_exit_replay_missing_jsonl", codes)

    def test_zero_exit_missing_result_is_blocker(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        # replay-result.md missing
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("zero_exit_replay_missing_result", codes)

    def test_zero_exit_with_both_artifacts_passes(self) -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("zero_exit_replay_missing_jsonl", codes)
        self.assertNotIn("zero_exit_replay_missing_result", codes)

    def test_phase12_completed_without_valid_run_is_blocker(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-12-history-replay": "completed"}},
        )
        # eligible case needed for eligibility check
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nEvidence: direct pre-fix artifact")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        # host-isolation-evidence.json missing
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_no_valid_isolated_run", codes)

    def test_phase12_completed_with_valid_isolated_run_passes(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-12-history-replay": "completed"}},
        )
        # eligible case + calibration files
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nEvidence: direct pre-fix artifact")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "oracle comparison completed")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md",
               "Decision: no_skill_gap")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        _touch_json(
            run_dir / "host-isolation-evidence.json",
            {
                "mechanism": "secondary-apple-container",
                "allowed_mounts": [
                    {"container": "/replay/visible", "mode": "ro"},
                    {"container": "/replay/worktree", "mode": "rw"},
                    {"container": "/replay/company-runtime", "mode": "ro"},
                    {"container": "/replay/output", "mode": "rw"},
                ],
            },
        )
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_no_valid_isolated_run", codes)

    def test_phase12_completed_wrong_mechanism_is_blocker(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-12-history-replay": "completed"}},
        )
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nEvidence: direct pre-fix artifact")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        _touch_json(
            run_dir / "host-isolation-evidence.json",
            {
                "mechanism": "docker-container",
                "allowed_mounts": [
                    {"container": "/replay/visible", "mode": "ro"},
                    {"container": "/replay/worktree", "mode": "rw"},
                    {"container": "/replay/company-runtime", "mode": "ro"},
                    {"container": "/replay/output", "mode": "rw"},
                ],
            },
        )
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_no_valid_isolated_run", codes)

    def test_phase12_disallowed_mount_is_blocker(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-12-history-replay": "completed"}},
        )
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nEvidence: direct pre-fix artifact")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        _touch_json(
            run_dir / "host-isolation-evidence.json",
            {
                "mechanism": "secondary-apple-container",
                "allowed_mounts": [
                    {"container": "/replay/visible", "mode": "ro"},
                    {"container": "/replay/worktree", "mode": "rw"},
                    {"container": "/replay/company-runtime", "mode": "ro"},
                    {"container": "/replay/output", "mode": "rw"},
                    {"container": "/host-e2e", "mode": "ro"},
                ],
            },
        )
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_no_valid_isolated_run", codes)

    def _bridge_helper(self) -> Path:
        helper = Path(self.td.name) / "request-isolated-replay"
        _touch(helper, "#!/bin/sh\nexit 0\n")
        helper.chmod(0o755)
        return helper

    def test_ready_case_must_invoke_available_bridge(self) -> None:
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        v = Verifier(self.home, [], run_precheck=False, replay_bridge_helper=self._bridge_helper())
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_bridge_available_not_invoked", codes)

    def test_bridge_makes_isolation_unavailable_claim_invalid(self) -> None:
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "replay-agent-cli-checks.md", "Isolation status: isolation runtime unavailable")
        v = Verifier(self.home, [], run_precheck=False, replay_bridge_helper=self._bridge_helper())
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_bridge_ignored_as_unavailable", codes)

    def test_result_cannot_request_bridge_that_is_already_available(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "needs-input",
                "paths": {},
                "summary": "",
                "missing_inputs": [
                    "History replay isolation bridge (Phase 12): need request-isolated-replay bridge or container/VM runtime"
                ],
                "blockers": [],
                "unresolved_questions": [],
            },
        )
        v = Verifier(
            self.home,
            [],
            run_precheck=False,
            replay_bridge_helper=self._bridge_helper(),
        )
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("bootstrap_reports_isolation_unavailable_with_bridge", codes)

    def test_result_may_say_existing_bridge_must_be_invoked(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "needs-input",
                "paths": {},
                "summary": "",
                "missing_inputs": ["Need to invoke the existing request-isolated-replay helper"],
                "blockers": [],
                "unresolved_questions": [],
            },
        )
        v = Verifier(
            self.home,
            [],
            run_precheck=False,
            replay_bridge_helper=self._bridge_helper(),
        )
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("bootstrap_reports_isolation_unavailable_with_bridge", codes)

    def test_ready_case_ineligible_is_blocker(self) -> None:
        """ready-for-replay with explicit ineligible eligibility → blocker."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay\nEligibility: ineligible-leaky")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_low_confidence_ready_for_replay", codes)

    def test_nl_partial_leak_no_longer_blocker(self) -> None:
        """NL text about partial leak no longer auto-fails
        (broad NL admitted-leak scan removed — only structured eligibility + verbatim checks)."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay\nSTART/oracle separation: commit title partially leaks the fix")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_admitted_leak_ready_for_replay", codes)

    def test_bridge_visible_packet_must_use_isolated_path(self) -> None:
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        _touch(run_dir / "visible-packet" / "replay-prompt.md", "Repo: /e2e/customer-repos/everest")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: defer")
        v = Verifier(self.home, [], run_precheck=False, replay_bridge_helper=self._bridge_helper())
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_visible_packet_uses_outer_path", codes)



class JarvisBoxCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "_bootstrap").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_help_file(self, commands: list[str]) -> Path:
        p = Path(self.td.name) / "help.txt"
        lines = ["jarvis-box — enterprise decision intelligence brain", "", "Usage:", "  jarvis-box <command> [args]", "", "Commands:"]
        for c in commands:
            lines.append(f"  {c}           description of {c}")
        p.write_text("\n".join(lines), encoding="utf-8")
        return p

    def test_invented_command_in_day2_is_blocker(self) -> None:
        help_file = self._make_help_file(["bootstrap", "doctor", "status", "agent", "version", "help", "self-improve"])
        _touch(self.home / "_bootstrap" / "day2-operation.md", "run jarvis-box sync daily\nrun jarvis-box cleanup weekly")
        v = Verifier(self.home, [], run_precheck=False, jarvis_box_help_file=help_file)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_invented_command", codes)
        msgs = [f["message"] for f in report["findings"] if f["code"] == "day2_invented_command"]
        self.assertTrue(any("sync" in m for m in msgs))
        self.assertTrue(any("cleanup" in m for m in msgs))

    def test_valid_commands_pass(self) -> None:
        help_file = self._make_help_file(["bootstrap", "doctor", "status", "agent"])
        _touch(self.home / "_bootstrap" / "day2-operation.md", "run jarvis-box doctor daily\nrun jarvis-box status hourly")
        v = Verifier(self.home, [], run_precheck=False, jarvis_box_help_file=help_file)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_invented_command", codes)

    def test_no_help_file_skips_check(self) -> None:
        _touch(self.home / "_bootstrap" / "day2-operation.md", "run jarvis-box sync daily")
        v = Verifier(self.home, [], run_precheck=False)  # no jarvis_box_help_file
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_invented_command", codes)

    def test_product_ownership_prose_is_not_treated_as_command(self) -> None:
        help_file = self._make_help_file(["doctor", "status", "agent"])
        _touch(self.home / "_bootstrap" / "day2-operation.md", "这些能力由 jarvis-box install 托管。")
        v = Verifier(self.home, [], run_precheck=False, jarvis_box_help_file=help_file)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_invented_command", codes)

    def test_missing_day2_op_skips_check(self) -> None:
        help_file = self._make_help_file(["bootstrap", "doctor"])
        # no day2-operation.md
        v = Verifier(self.home, [], run_precheck=False, jarvis_box_help_file=help_file)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_invented_command", codes)



class HistoryReplayRegressionTests(unittest.TestCase):
    """Regression tests for Phase 12 verifier changes."""
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json", '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "evals" / "history-replay" / "cases" / "case-1").mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-1").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_ineligible_case_with_replay_run_is_blocker(self) -> None:
        """ineligible-leaky case that started replay is a blocker."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay\nEligibility: ineligible-leaky\nSTART reconstruction: commit title contains fix action")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: defer")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_ineligible_case_started_replay", codes)

    def test_low_confidence_case_with_replay_run_is_blocker(self) -> None:
        """low-confidence case that started replay is a blocker."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay\nEligibility: low-confidence\nSTART: needs better artifact")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: defer")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_ineligible_case_started_replay", codes)

    def test_visible_packet_with_verbatim_leak_is_blocker(self) -> None:
        """Visible packet containing hidden oracle marker verbatim → oracle leak blocker."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch(run_dir / "visible-packet" / "replay-prompt.md",
               "## Context\n## Hidden Outcome Oracle\nAllowed repos: test-app\n")
        # registry + CLI checks to avoid unrelated blockers
        _touch(self.home / "evals" / "history-replay" / "replay-case-registry.md", "case-1: candidate")
        _touch(run_dir / "replay-agent-cli-checks.md",
               "Isolated replay possible: yes\nMechanism: secondary-apple-container")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: no_skill_gap")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "analysis")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_visible_packet_oracle_leak", codes)

    def test_visible_packet_nl_text_no_longer_blocker(self) -> None:
        """NL fix description in visible packet no longer auto-fails
        (NL leak patterns removed — only verbatim checks remain)."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch(run_dir / "visible-packet" / "replay-prompt.md",
               "The fix is to skip the redundant null check in the handler.")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: no_skill_gap")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "analysis")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_visible_packet_oracle_leak", codes)

    def test_clean_visible_packet_passes(self) -> None:
        """Visible packet with only pre-outcome facts does not trigger leak blocker."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file, "Status: ready-for-replay")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch(run_dir / "visible-packet" / "replay-prompt.md",
               "## Context\nDashboard returns 500 error.\n## Allowed repos\n- acme-app\n## Skills available\n- acme-jarvis")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: no_skill_gap")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "analysis")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_visible_packet_oracle_leak", codes)

    def test_eval_case_gap_accepted_in_nonzero_exit_decision(self) -> None:
        """eval-case-gap in skill-update-decision should be accepted like defer."""
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        _touch(case_dir / "skill-update-decision.md", "Decision: eval-case-gap\nStatus: deferred")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("nonzero_replay_no_skill_gap", codes)
        self.assertNotIn("nonzero_replay_no_defer", codes)

    def test_nonzero_exit_decision_missing_is_blocker(self) -> None:
        """Nonzero exit without decision file is still a blocker."""
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        _touch(run_dir / "exit-code", "1")
        # no skill-update-decision.md
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("nonzero_replay_decision_missing", codes)


class Phase12CompletedRegressionTests(unittest.TestCase):
    """Phase 12 completed must have eligible case, isolation evidence, trace/result, oracle comparison, failure analysis, skill decision."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "evals" / "history-replay" / "cases" / "case-1").mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-1").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _setup_completed_state(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-12-history-replay": "completed"}},
        )
        _touch(self.home / "bootstrap-state.json", "{}")

    def _setup_valid_run(self, case_id: str = "case-1") -> None:
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / case_id
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")
        _touch_json(
            run_dir / "host-isolation-evidence.json",
            {
                "mechanism": "secondary-apple-container",
                "allowed_mounts": [
                    {"container": "/replay/visible", "mode": "ro"},
                    {"container": "/replay/worktree", "mode": "rw"},
                    {"container": "/replay/company-runtime", "mode": "ro"},
                    {"container": "/replay/output", "mode": "rw"},
                ],
            },
        )

    def _setup_eligible_case(self, case_id: str = "case-1", status: str = "eligible-direct") -> None:
        case_file = self.home / "evals" / "history-replay" / "cases" / case_id / "history-replay-case.md"
        _touch(
            case_file,
            f"Status: ready-for-replay\n"
            f"Eligibility: {status}\n"
            "Case validity: valid\n"
            "Readiness: ready\n"
            "Final artifact fully read: yes\n"
            "Final artifact extraction command / pointer: git show abc123\n"
            "## Visible START\nObserved failure from a pre-fix artifact.\n"
            "## Visible Packet Fact Closure\n"
            "| Packet File | Claim | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
            "| replay-prompt.md | observed failure | fact-1 | supported |\n"
            "## Hidden Outcome Oracle\n"
            "- **Actual outcome**: historical change landed\n"
            "- **Actual changed surfaces**: `src/Fix.java`\n"
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Exact Packet Review | Result |\n"
            "|---|---|---|---|\n"
            "| src/Fix.java | git show abc123 | replay-prompt.md checked | absent |\n"
            "## Case Readiness Gate\nAll checks complete.\n",
        )

    def _setup_calibration(self, case_id: str = "case-1",
                           fa_text: str = (
                               "## Execution Gate\n"
                               "Execution gate: executed\n"
                               "Case validity: valid\n"
                               "## Final Output Evidence\n"
                               "Exact command or artifact pointer: _bootstrap/history-replay-runs/case-1/replay-result.md\n"
                               "确认已完整读取: yes\n"
                               "## Historical Outcome Evidence\n"
                               "Exact command or artifact pointer: git show abc123\n"
                               "确认已完整读取: yes\n"
                               "## Oracle Comparison\ncompared with oracle\n"
                               "Outcome verification sufficient for skill judgment: yes\n"
                           ),
                           sd_text: str = (
                               "## Decision Summary\n"
                               "Execution gate: executed\n"
                               "Case validity: valid\n"
                               "Outcome verification sufficient for skill judgment: yes\n"
                               "Decision: no_skill_gap\n"
                           )) -> None:
        case_dir = self.home / "evals" / "history-replay" / "cases" / case_id
        _touch(case_dir / "replay-failure-analysis.md", fa_text)
        _touch(case_dir / "skill-update-decision.md", sd_text)

    # ── no cases / no eligible case ──

    def test_no_cases_dir_is_blocker(self) -> None:
        self._setup_completed_state()
        import shutil
        shutil.rmtree(self.home / "evals" / "history-replay" / "cases")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_no_cases", codes)

    def test_no_case_files_is_blocker(self) -> None:
        self._setup_completed_state()
        # Remove case file
        (self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md").unlink(missing_ok=True)
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_no_cases", codes)

    def test_no_eligible_case_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        # Case has no eligibility marker
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: draft\nDescription: just a draft case")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_no_eligible_case", codes)

    # ── eligible-direct binding ──

    def test_eligible_direct_binds_to_valid_run(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_no_valid_isolated_run", codes)
        self.assertNotIn("phase12_completed_no_eligible_case", codes)

    def test_eligible_reconstructed_binds_to_valid_run(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-reconstructed")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_no_valid_isolated_run", codes)
        self.assertNotIn("phase12_completed_no_eligible_case", codes)

    def test_ready_for_replay_without_bad_markers_binds(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEvidence: pre-fix issue available")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_no_valid_isolated_run", codes)
        self.assertNotIn("phase12_completed_ineligible_case", codes)

    # ── ready-for-replay with ineligible markers ──

    def test_ready_for_replay_with_ineligible_leaky_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: ineligible-leaky\n")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_ineligible_case", codes)

    def test_ready_for_replay_with_low_confidence_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: low-confidence\n")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_ineligible_case", codes)

    # ── empty calibration artifacts ──

    def test_empty_failure_analysis_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: no_skill_gap")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_empty_calibration_artifact", codes)

    def test_empty_skill_decision_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "oracle comparison done")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_empty_calibration_artifact", codes)

    # ── oracle comparison in failure analysis ──

    def test_failure_analysis_without_oracle_comparison_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1",
                                fa_text="failure analysis content\nrouting failure detected\nskills gap identified without cross-referencing hidden answer")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_failure_analysis_no_oracle_comparison", codes)

    def test_failure_analysis_with_english_oracle_comparison_passes(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1",
                                fa_text="## Oracle Comparison\nCompared replay result with hidden oracle.\nFindings: routing gap detected.")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_completed_failure_analysis_no_oracle_comparison", codes)

    def test_failure_analysis_with_chinese_oracle_comparison_passes(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1",
                                fa_text="## 与 Oracle 对比\n将重放结果与隐藏 oracle 进行对比。发现 routing 缺口。")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_completed_failure_analysis_no_oracle_comparison", codes)

    def test_failure_analysis_with_compared_against_oracle_passes(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1",
                                fa_text="Results compared against the oracle show boundary gap.")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_completed_failure_analysis_no_oracle_comparison", codes)

    # ── valid run without calibration ──

    def test_valid_run_without_calibration_on_bound_case_is_blocker(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        # No calibration files at all
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_valid_run_no_calibration", codes)

    # ── still-missing calibration (old path) ──

    def test_phase12_completed_without_failure_analysis_is_blocker(self) -> None:
        """Phase 12 completed with replay run but missing failure analysis is blocker."""
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md", "Decision: no_skill_gap")
        # replay-failure-analysis.md missing
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_missing_calibration_artifact", codes)

    def test_phase12_completed_without_skill_decision_is_blocker(self) -> None:
        """Phase 12 completed with replay run but missing skill-update-decision is blocker."""
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md", "oracle comparison")
        # skill-update-decision.md missing
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_missing_calibration_artifact", codes)

    def test_phase12_completed_with_both_calibration_files_passes(self) -> None:
        """Phase 12 completed with replay, isolation evidence, failure analysis with oracle comparison, and skill decision passes."""
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        self._setup_calibration("case-1")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase12_completed_missing_calibration_artifact", codes)
        self.assertNotIn("phase12_no_valid_isolated_run", codes)
        self.assertNotIn("phase12_completed_no_eligible_case", codes)
        self.assertNotIn("phase12_completed_packet_fact_closure_invalid", codes)
        self.assertNotIn("phase12_completed_outcome_evidence_incomplete", codes)

    def test_phase12_completed_rejects_placeholder_fact_mapping(self) -> None:
        self._setup_completed_state()
        self._setup_valid_run()
        self._setup_eligible_case("case-1", "eligible-direct")
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        case_file.write_text(
            case_file.read_text(encoding="utf-8").replace("fact-1", "<fact-id>"),
            encoding="utf-8",
        )
        self._setup_calibration("case-1")
        report = Verifier(self.home, [], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase12_completed_packet_fact_closure_invalid", codes)


class RootPlaceholderLifecycleTests(unittest.TestCase):
    """Phase 7 customer identity/routing and Phase 14 rollout have different fill gates."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        self.phase7_files = [
            "README.md",
            "jarvis.toml",
            "references/jarvis-first-routing.md",
            "references/canonical-repo-fleet.md",
            "skills/acme-jarvis/SKILL.md",
        ]
        for rel_path in self.phase7_files:
            _touch(self.home / rel_path, "filled customer value\n")
        _touch(self.home / "MAINTENANCE.md", "# Maintenance\nBOOTSTRAP_REQUIRED\n")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _write_status(self, overall: str, phase14: str = "needs-input") -> None:
        phase_status = {
            "phase-07-company-jarvis-repo": "completed",
            "phase-14-day2-operation": phase14,
        }
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": overall,
                "paths": {},
                "summary": "",
                "missing_inputs": [],
                "blockers": [],
                "phase_summary": phase_status,
            },
        )
        _touch_json(
            self.home / "bootstrap-state.json",
            {"status": overall, "phase_status": phase_status},
        )

    def test_phase7_rejects_sentinel_in_each_identity_or_routing_file(self) -> None:
        self._write_status("needs-input")
        for rel_path in self.phase7_files:
            with self.subTest(rel_path=rel_path):
                path = self.home / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "BOOTSTRAP_REQUIRED\n", encoding="utf-8")
                report = Verifier(
                    self.home,
                    [],
                    run_precheck=False,
                    expected_company_slug="acme",
                ).verify()
                matching = [
                    finding for finding in report["findings"]
                    if finding["severity"] == "blocker"
                    and finding["code"] == "phase7_root_placeholder"
                    and rel_path in finding["message"]
                ]
                self.assertTrue(matching, report["findings"])
                path.write_text(original, encoding="utf-8")

    def test_phase7_allows_maintenance_rollout_sentinel_before_phase14(self) -> None:
        self._write_status("needs-input", phase14="needs-input")
        report = Verifier(
            self.home, [], run_precheck=False, expected_company_slug="acme"
        ).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("phase7_root_placeholder", codes)
        self.assertNotIn("phase14_maintenance_placeholder", codes)

    def test_phase14_completed_rejects_maintenance_rollout_sentinel(self) -> None:
        self._write_status("completed", phase14="completed")
        report = Verifier(
            self.home, [], run_precheck=False, expected_company_slug="acme"
        ).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase14_maintenance_placeholder", codes)


class R4OldOutputStyleTests(unittest.TestCase):
    """r4 regression: old output patterns must be caught by the verifier."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "completed", "paths": {}, "summary": "", "missing_inputs": [], "blockers": [],
             "phase_summary": {"phase-07-company-jarvis-repo": "completed"}},
        )
        _touch_json(
            self.home / "bootstrap-state.json",
            {"status": "completed", "phase": "phase-07-company-jarvis-repo",
             "paths": {}, "confirmed_answers": {}, "method_repo": {},
             "phase_status": {"phase-07-company-jarvis-repo": "completed"}},
        )
        (self.home / "skills").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_stop_slop_missing_companion_caught(self) -> None:
        """A mandatory method skill missing companion files is caught."""
        skill_dir = self.home / "skills" / "stop-slop"
        skill_dir.mkdir(parents=True)
        _touch(skill_dir / "SKILL.md", "name: stop-slop\n\n# Stop Slop AI 写作模式")
        # Missing all companion references
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("workflow_companion_file_missing", codes)

    def test_old_company_bracket_root_caught(self) -> None:
        """Old [Company] literal in README.md is caught as Phase 7 placeholder."""
        _touch(self.home / "README.md", "# [Company] JARVIS\n\nThis is the [Company] knowledge router.")
        _touch(self.home / "MAINTENANCE.md", "# Maintenance")
        _touch(self.home / "jarvis.toml", "[project]\nname = \"Test\"")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase7_root_placeholder", codes)

    def test_old_confirmed_company_placeholder_caught(self) -> None:
        """Old <confirmed company name / slug> in README.md caught."""
        _touch(self.home / "README.md", "company identity: <confirmed company name / slug>")
        _touch(self.home / "MAINTENANCE.md", "# Maintenance")
        _touch(self.home / "jarvis.toml", "[project]\nname = \"Test\"")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase7_root_placeholder", codes)

    def test_installed_prose_no_false_day2_blockers(self) -> None:
        """Prose-only day2-operation.md (no canonical table) should not trigger false blockers."""
        _touch(self.home / "_bootstrap" / "day2-operation.md",
               "## Install-owned 能力清单\n\n这些能力由 jarvis-box install 托管。")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # Should not have day2-blockers for prose-only content (no canonical table)
        for code in codes:
            self.assertNotIn("day2_", code)

    def test_prefixed_generic_workflow_missing_structure_caught(self) -> None:
        """Generic workflow without START/WORK/VERIFY/END is caught."""
        skill_dir = self.home / "skills" / "custom-generic-workflow"
        skill_dir.mkdir(parents=True)
        _touch(skill_dir / "SKILL.md", "# Custom Generic Workflow\n\nJust a simple workflow.")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("generic_workflow_missing_structure", codes)

    def test_skill_package_bootstrap_placeholder_caught_in_companion(self) -> None:
        """Phase 9 output cannot retain template-time needs-evidence fields."""
        skill_dir = self.home / "skills" / "custom-generic-workflow"
        _touch(
            skill_dir / "SKILL.md",
            "# Generic workflow\nSTART\nWORK\nVERIFY\nEND\n",
        )
        _touch(
            skill_dir / "references" / "route.md",
            "Read [needs-evidence: REFERENCES_PATH]runtime-governance.md\n",
        )
        report = Verifier(self.home, [], run_precheck=False).verify()
        matching = [
            finding for finding in report["findings"]
            if finding["severity"] == "blocker"
            and finding["code"] == "skill_package_bootstrap_placeholder"
            and "references/route.md" in finding["message"]
        ]
        self.assertTrue(matching, report["findings"])

    def test_unknown_skill_not_forced_four_stage(self) -> None:
        """Unknown skill without generic/fallback declaration is NOT forced four-stage."""
        skill_dir = self.home / "skills" / "random-unknown-skill"
        skill_dir.mkdir(parents=True)
        _touch(skill_dir / "SKILL.md", "# Random Skill\n\nDoes random stuff.")
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("generic_workflow_missing_structure", codes,
                        "unknown skill without generic/fallback declaration must not get four-stage check")

    def test_bootstrap_paths_not_root_caught(self) -> None:
        """jarvis.toml with _bootstrap/ paths in phase_status_file/result_file is caught."""
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[],'
               '"phase_summary":{"phase-07-company-jarvis-repo":"completed"}}')
        _touch(self.home / "bootstrap-state.json",
               '{"status":"completed","phase":"phase-07-company-jarvis-repo",'
               '"paths":{},"confirmed_answers":{},"method_repo":{},'
               '"phase_status":{"phase-07-company-jarvis-repo":"completed"}}')
        _touch(self.home / "README.md", "# Test\nworkflow-first\nartifact-first\nSTART WORK VERIFY END\nwriteback\nmaintenance_link: MAINTENANCE.md\nsource-of-truth\ncapability delivery")
        _touch(self.home / "MAINTENANCE.md", "# Test\nHistory Present Future\nwrite contract\nhistory replay\nsession self-improvement\nprimary-home promotion")
        _touch(self.home / "jarvis.toml",
               '[project]\nname = "test"\nslug = "test"\n'
               '[identity]\ncompany = "Test"\nproduct = "Test"\nowner = "test"\n'
               '[runtime]\nroot = "/tmp"\ntype = "jarvis-box"\nentry_skill = "skills/test-jarvis/SKILL.md"\n'
               '[vcs]\nhost = "gitlab.test.com"\n'
               '[bootstrap]\nphase_status_file = "_bootstrap/bootstrap-state.json"\nresult_file = "_bootstrap/bootstrap-result.json"\n')
        v = Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("jarvis_toml_bootstrap_path_not_root", codes)


class Phase09StageTests(unittest.TestCase):
    """Phase 9 stage gate: runs only Phase 3-9 checks, does not require Phase 10-14."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "modules" / "app").mkdir(parents=True)
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True)
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(self.home / "_bootstrap" / "discovery" / name, "evidence present")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self) -> Path:
        repo = Path(self.td.name) / "test-repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        return repo

    def _make_phase09_verifier(self) -> _MOD.Verifier:
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        return _MOD.Verifier(self.home, [], run_precheck=False, stage="phase-09")

    def test_phase09_runs_without_requiring_phase10_14_artifacts(self) -> None:
        """Phase 9 stage does not require day2-operation, history replay, or jarvis-box-help."""
        v = self._make_phase09_verifier()
        report = v.verify()
        # phase-09 should not have day2 / replay / command checks that require Phase 10-14
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_checks_missing", codes)
        self.assertNotIn("day2_checks_empty", codes)
        self.assertNotIn("history_replay_registry_missing", codes)

    def test_phase09_accepts_checkpoint_in_progress_status(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "in-progress",
                "paths": {},
                "summary": "Phase 9 checkpoint",
                "missing_inputs": [],
                "blockers": [],
            },
        )
        _touch_json(self.home / "bootstrap-state.json", {"status": "in-progress"})
        report = _MOD.Verifier(
            self.home, [], run_precheck=False, stage="phase-09"
        ).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("result_status_invalid", codes)
        self.assertNotIn("bootstrap_still_in_progress", codes)

    def test_phase09_fails_r5_shape_placeholder_module(self) -> None:
        """Phase 9 rejects a module overview with r5-era placeholder patterns."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## Placeholder Issue Patterns\n"
               "### Pattern A: Stale Cache in app Lookup\n"
               "- Root cause: cache invalidation hook issue\n"
               "## Placeholder Decisions\n"
               "### Decision 1: Data Model choice\n"
               "## 业务定位\nBOOTSTRAP_REQUIRED")
        repo = self._make_repo()
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="phase-09")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("r5_placeholder_issue_patterns", codes)
        self.assertIn("r5_placeholder_decisions", codes)

    def test_phase09_passes_minimal_evidence_filled_module(self) -> None:
        """Phase 9 passes a module overview with required sections and evidence pointer."""
        repo = self._make_repo()
        # Create a real file at the evidence pointer path
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp module handles user-facing operations.\n"
               "## 首跳路由\n| 触发信号 | 路由到 | 首个验证 |\n|---|---|---|\n| issue | skills/app-jarvis/SKILL.md | test |\n"
               "## First Proof\n- 证据类型: commit\n"
               "## 常见 False Owner\n| 误路由信号 | 实际归属 | 原因 |\n|---|---|---|\n| auth error | auth module | separate service |\n"
               "## 证据与入口\n| 证据指针 | 观察到的事实 | 获取/检查方式 |\n|---|---|---|\n| test-repo:src/main/handler.go | handler entry | git grep |\n"
               "## 模块关系\n| 方向 | 关联模块 | 耦合性质 | 接口 |\n|---|---|---|---|\n| downstream | auth | API | REST |\n"
               "## 搜索与验证\n- 代码搜索: grep handler\n- Issue 追踪: label:app\n"
               "## Notes\nNo placeholders. Evidence from test-repo.")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="phase-09")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("bootstrap_required_sentinel", codes)
        self.assertNotIn("angle_placeholder", codes)
        self.assertNotIn("module_overview_missing_section", codes)
        self.assertNotIn("module_overview_no_evidence_pointer", codes)
        self.assertNotIn("module_overview_pointer_unresolvable", codes)
        self.assertNotIn("r5_placeholder_issue_patterns", codes)

    def test_phase09_missing_evidence_pointer_fails(self) -> None:
        """Module overview with no evidence pointer fails."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp module.\n## 首跳路由\nNone.\n## First Proof\nNone.\n"
               "## 常见 False Owner\nNone.\n## 证据与入口\nNone.\n## 模块关系\nNone.\n## 搜索与验证\nNone.")
        repo = self._make_repo()
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="phase-09")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_overview_no_evidence_pointer", codes)

    def test_phase09_broad_path_pointer_fails(self) -> None:
        """Evidence pointer pointing to broad top-level path like 'service/' fails."""
        repo = self._make_repo()
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx.\n## First Proof\nx.\n"
               "## 常见 False Owner\nx.\n## 证据与入口\n| 证据指针 | 事实 | 获取 |\n|---|---|---|\n| test-repo:service/ | svc dir | ls |\n"
               "## 模块关系\nx.\n## 搜索与验证\nx.")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="phase-09")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # Broad path without specific file extension should fail — unresolvable
        self.assertIn("module_evidence_pointer_invalid", codes)

    def test_phase09_rejects_bootstrap_required_in_module(self) -> None:
        """Phase 9 rejects BOOTSTRAP_REQUIRED sentinel remaining in module files."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nBOOTSTRAP_REQUIRED\n## 首跳路由\nBOOTSTRAP_REQUIRED\n"
               "## First Proof\nBOOTSTRAP_REQUIRED\n## 常见 False Owner\nBOOTSTRAP_REQUIRED\n"
               "## 证据与入口\n| 证据指针 | 事实 | 获取 |\n|---|---|---|\n| test-repo:src/main.go | handler | grep |\n"
               "## 模块关系\nBOOTSTRAP_REQUIRED\n## 搜索与验证\nBOOTSTRAP_REQUIRED")
        repo = self._make_repo()
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="phase-09")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("bootstrap_required_sentinel", codes)


class Phase12PreflightTests(unittest.TestCase):
    """Phase 12 preflight stage: catches oracle leaks before calling bridge."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "evals" / "history-replay" / "cases").mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_verifier(self, case_id: str = "case-1") -> _MOD.Verifier:
        return _MOD.Verifier(self.home, [], run_precheck=False, stage="phase-12-preflight", case_id=case_id)

    def _make_case(self, case_id: str, case_text: str) -> None:
        case_dir = self.home / "evals" / "history-replay" / "cases" / case_id
        case_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md", case_text)

    def test_preflight_catches_r5_leaked_class_identifier(self) -> None:
        """eligible-reconstructed case with verbatim changed path in visible START → blocker."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "The service/src/main/java/DatasetProxyImpl.java has issues.\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234def\n"
            "### Actual Changed Surfaces\n"
            "- service/src/main/java/DatasetProxyImpl.java — add null guard\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_changed_path_in_visible", codes)

    def test_preflight_rejects_low_confidence(self) -> None:
        """needs-better-start case must not pass preflight."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Eligibility: needs-better-start\n"
            "START cannot be reliably separated from outcome.\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_ineligible", codes)

    def test_preflight_rejects_ineligible_leaky(self) -> None:
        """ineligible-leaky case must not pass preflight."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Eligibility: ineligible-leaky\n"
            "Commit title contains fix action: skip redundant nullReplace in formatting pipeline\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_ineligible", codes)

    def test_preflight_rejects_not_ready_for_replay(self) -> None:
        """Case not marked ready-for-replay must not pass preflight."""
        self._make_case("case-1",
            "Status: draft\n"
            "Eligibility: eligible-direct\n"
            "## Visible START\nDashboard shows 500 error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_not_ready", codes)

    def test_preflight_clean_eligible_reconstructed_passes(self) -> None:
        """Symptom-only eligible-reconstructed case with no verbatim leaks passes preflight."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard returns 500 error when date range is empty.\n"
            "Allowed repos: test-app\n"
            "Available skills: skills/test-jarvis/SKILL.md\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234567890def\n"
            "Changed files:\n"
            "  - src/server/DateFormatUtil.java\n"
            "  - src/server/DateFormatUtilTest.java\n"
            "Actual fix: added null check for empty date range in DateFormatUtil\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # No verbatim hash or path in visible → clean
        self.assertNotIn("preflight_final_commit_hash_in_visible", codes)
        self.assertNotIn("preflight_changed_path_in_visible", codes)
        self.assertNotIn("preflight_hidden_oracle_marker_in_visible", codes)
        self.assertNotIn("preflight_case_ineligible", codes)
        self.assertNotIn("preflight_case_not_ready", codes)

    def test_preflight_contradictory_eligible_reconstructed_low_confidence(self) -> None:
        """Replay eligibility=eligible-reconstructed + low-confidence text → contradictory state."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n"
            "Confidence: low-confidence\n"
            "Note: commit title may contain a partial directional hint.\n\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_contradictory_state", codes)

    def test_preflight_admitted_leak_is_blocker(self) -> None:
        """Structured Leak admission=yes field → preflight reject."""
        self._make_case("case-1",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n"
            "Leak admission: yes\n\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n")
        v = self._make_verifier("case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_admitted_leak", codes)

    def test_preflight_missing_case_id_is_blocker(self) -> None:
        """Missing --case-id for preflight stage is a blocker."""
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="phase-12-preflight", case_id=None)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_missing_case_id", codes)

    def test_preflight_missing_case_file_is_blocker(self) -> None:
        """Non-existent case file is a blocker."""
        v = self._make_verifier("nonexistent-case")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_missing", codes)


class CustomerFactSafetyTests(unittest.TestCase):
    """Final stage must catch fabricated facts and contradictions."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "modules" / "app").mkdir(parents=True)
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True)
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(self.home / "_bootstrap" / "discovery" / name, "present")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_verifier(self) -> _MOD.Verifier:
        return _MOD.Verifier(self.home, [], run_precheck=False, stage="final")

    def test_angle_placeholder_in_overview_is_blocker(self) -> None:
        """Angle bracket placeholder like <repo>/<endpoint> in module overview → blocker."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp module.\n## 首跳路由\nRoute to <repo>/src/<endpoint>\n"
               "## First Proof\nx\n## 常见 False Owner\nx\n## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("angle_placeholder", codes)

    def test_r5_fabricated_cache_issue_is_rejected(self) -> None:
        """Module known-issues with r5 fabricated Stale Cache pattern → blocker."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n## 常见 False Owner\nx\n## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        _touch(self.home / "modules" / "app" / "known-issues.md",
               "## 模式索引\n### Pattern A: Stale Cache in app Lookup\n- Symptoms: outdated data after update\n- Root cause: cache invalidation\n- First affected version: v2.1.0\n- Status: monitored")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("r5_fabricated_issue_pattern", codes)

    def test_r5_fabricated_kafka_decision_is_rejected(self) -> None:
        """Module decisions with r5 Kafka infrastructure text → blocker."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n## 常见 False Owner\nx\n## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        _touch(self.home / "modules" / "app" / "decisions.md",
               "## 决策表\n| Date | Decision |\n|---|---|\n| 2025-10-05 | Use Kafka infrastructure for events |")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("r5_fabricated_tech_stack", codes)

    def test_r5_fabricated_rejected_graphql_feature_is_rejected(self) -> None:
        """Module rejected-features with r5 GraphQL API text → blocker."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n## 常见 False Owner\nx\n## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        _touch(self.home / "modules" / "app" / "rejected-features.md",
               "## 已拒绝的功能\n### Entry 2: GraphQL API for module\n| Feature name | GraphQL endpoint |")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("r5_fabricated_rejected_feature", codes)

    def test_crosscutting_with_module_letter_placeholder_is_blocker(self) -> None:
        """Cross-cutting file with module-a placeholder → blocker."""
        _touch(self.home / "cross-cutting" / "module-interactions.md",
               "## 模块依赖矩阵\n| ↓依赖方 | module-a | module-b |\n|---|---|---|\n| **module-a** | — | ● |")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_letter_placeholder", codes)

    def test_crosscutting_with_product_letter_placeholder_is_blocker(self) -> None:
        """Peer-product-contracts with product-a placeholder → blocker."""
        _touch(self.home / "cross-cutting" / "peer-product-contracts.md",
               "## 契约表单\n| `<product-a>` | API | REST | read | token | >= v1.0 | escal | notes |")
        v = self._make_verifier()
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("product_letter_placeholder", codes)


class DeferredSourceTests(unittest.TestCase):
    """Deferred source still listed as missing input → blocker."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_deferred_source_in_missing_input_is_blocker(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "needs-input", "paths": {}, "summary": "",
             "missing_inputs": ["external-api-docs access credentials not available"],
             "blockers": []},
        )
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "sources" / "external-api-docs" / "README.md",
               "## Status\nThis source is deferred-needs-access — not required for first workflow.")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("deferred_source_still_missing_input", codes)

    def test_deferred_source_not_in_missing_input_passes(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {"status": "needs-input", "paths": {}, "summary": "",
             "missing_inputs": ["owner confirmation needed for writeback policy"],
             "blockers": []},
        )
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "sources" / "external-api-docs" / "README.md",
               "## Status\nThis source is deferred-needs-access — not required for first workflow.")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("deferred_source_still_missing_input", codes)


class ReplayDecisionContradictionTests(unittest.TestCase):
    """Low-confidence/ineligible case with no_skill_gap/closed → blocker."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_low_confidence_no_skill_gap_is_blocker(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: low-confidence\nSTART reconstruction: commit title partially leaks the fix\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md",
               "Decision: no_skill_gap\nStatus: closed\nExisting guidance sufficient.")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("low_confidence_contradicts_no_skill_gap", codes)

    def test_low_confidence_closed_status_is_blocker(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: ineligible-leaky\nCommit title: add userId guard to GetDashboard handler\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md",
               "Decision: defer\nStatus: closed\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("low_confidence_contradicts_closed", codes)

    def test_low_confidence_skills_sufficient_is_blocker(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: low-confidence\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md",
               "Decision: defer\nExisting skills are sufficient for this case.\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("low_confidence_contradicts_skills_sufficient", codes)

    def test_eligible_direct_no_skill_gap_passes(self) -> None:
        """eligible-direct case with no_skill_gap is NOT a contradiction."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nEvidence: direct pre-fix issue artifact\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "skill-update-decision.md",
               "Decision: no_skill_gap\nVerified: existing guidance covered the fix.\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("low_confidence_contradicts_no_skill_gap", codes)


class OracleInspectionGapTests(unittest.TestCase):
    """Failure analysis says oracle surface was missed but diff was not inspected → blocker."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_uninspected_diff_with_cosmetic_speculation_no_longer_nl_blocker(self) -> None:
        """NL-based 'did not inspect' + 'cosmetic' speculation no longer auto-fails
        (machine-only structured field checks replace natural-language inference)."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\n"
               "Missed file: config/runtime.yaml\n"
               "We did not inspect the actual diff, but it may be cosmetic only.\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("oracle_comparison_uninspected_speculation", codes)

    def test_uninspected_diff_supporting_speculation_no_longer_nl_blocker(self) -> None:
        """NL-based 'without reading actual diff' + 'supporting changes' no longer auto-fails."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\n"
               "The replay missed some files. Without reading the actual diff,\n"
               "the missed surfaces are likely supporting changes only.\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("oracle_comparison_uninspected_speculation", codes)

    def test_no_skill_gap_without_pointer_is_major(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\nCompared replay with oracle.\nAll files matched.\n"
               "no_skill_gap: yes\nExact command or artifact pointer: <pointer or none>\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertIn("oracle_comparison_missing_outcome_evidence", codes)

    def test_failure_analysis_with_diff_command_no_speculation_passes(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\n"
               "Final diff command: git diff abc1234^..abc1234\n"
               "Exact command or artifact pointer: git diff abc1234^..abc1234\n"
               "## Changed-surface purpose\n"
               "| src/handler.go | bug fix — null guard | yes | matched |\n"
               "| src/handler_test.go | test for null guard | yes | matched |\n"
               "Compared replay with oracle. All changed surfaces accounted for.\n"
               "no_skill_gap: yes\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("oracle_comparison_uninspected_speculation", codes)
        major_codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertNotIn("oracle_comparison_missing_outcome_evidence", major_codes)

    def test_no_skill_gap_with_oracle_artifact_passes(self) -> None:
        """Non-code episode: no_skill_gap=yes with Exact command or artifact pointer passes."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\n"
               "## Final Output Evidence\n"
               "Evidence type: oracle-artifact\n"
               "Exact command or artifact pointer: cat /replay/output/route-decision.json\n"
               "Compared replay with oracle.\n"
               "no_skill_gap: yes\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        major_codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertNotIn("oracle_comparison_missing_outcome_evidence", major_codes)

    def test_no_skill_gap_no_evidence_fails(self) -> None:
        """no_skill_gap=yes without any outcome evidence pointer → major."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\nReplay matched oracle expectations.\n"
               "no_skill_gap: yes\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertIn("oracle_comparison_missing_outcome_evidence", codes)

    def test_no_skill_gap_non_code_outcome_pointer_passes(self) -> None:
        """no_skill_gap=yes with explicit non-code Outcome artifact pointer non-placeholder → passes."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## Oracle comparison\n"
               "## Final Output Evidence\n"
               "Evidence type: oracle-artifact\n"
               "Exact command or artifact pointer: /replay/output/route-decision.json\n"
               "Compared replay with oracle.\n"
               "no_skill_gap: yes\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertNotIn("oracle_comparison_missing_outcome_evidence", codes)


class E2EScriptPathTests(unittest.TestCase):
    """E2E script uses installed runtime/state paths and contains both stage invocations."""

    def setUp(self) -> None:
        self.e2e_dir = Path(__file__).resolve().parents[1] / "e2e" / "apple-container-claude"

    def test_e2e_script_uses_install_root_paths(self) -> None:
        script = self.e2e_dir / "run-in-container.sh"
        self.assertTrue(script.is_file(), f"E2E script missing: {script}")
        text = script.read_text(encoding="utf-8")
        # Must reference install-root paths for runtime/state
        self.assertIn("install-root/var/lib/jarvis-box", text,
                      "E2E script must use actual install-root/var/lib/jarvis-box runtime path")
        # Must NOT invent /e2e/runtime or /e2e/state as runtime roots
        self.assertNotRegex(text, r"JARVIS_RUNTIME_ROOT=/e2e/runtime\b",
                           "E2E script must not use invented /e2e/runtime as JARVIS_RUNTIME_ROOT")

    def test_e2e_script_contains_phase09_verifier_invocation(self) -> None:
        script = self.e2e_dir / "run-in-container.sh"
        text = script.read_text(encoding="utf-8")
        self.assertIn("--stage phase-09", text,
                      "E2E script must contain phase-09 verifier stage invocation")

    def test_e2e_script_contains_phase12_preflight_invocation(self) -> None:
        script = self.e2e_dir / "run-in-container.sh"
        text = script.read_text(encoding="utf-8")
        self.assertIn("--stage phase-12-preflight", text,
                      "E2E script must contain phase-12-preflight verifier stage invocation")


class TemplateSafetyRegressionTests(unittest.TestCase):
    """Ensure templates contain no fabricated facts or angle placeholders."""

    def setUp(self) -> None:
        self.template_root = Path(__file__).resolve().parents[1] / "templates"

    def test_module_overview_no_angle_placeholders(self) -> None:
        overview = self.template_root / "company-jarvis" / "module" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        self.assertNotIn("<repo>", text)
        self.assertNotIn("<endpoint>", text)
        self.assertNotIn("<confirmed company", text)

    def test_module_overview_has_required_sections(self) -> None:
        overview = self.template_root / "company-jarvis" / "module" / "overview.md"
        text = overview.read_text(encoding="utf-8")
        for section in ["业务定位", "首跳路由", "First Proof", "常见 False Owner", "证据与入口", "模块关系", "搜索与验证"]:
            self.assertIn(section, text, f"Module overview template missing section: {section}")

    def test_repo_local_templates_have_no_phase8_generation_narration(self) -> None:
        repo_skill_root = self.template_root / "repo-local-skill" / "skills"
        for path in sorted(repo_skill_root.rglob("*.md")):
            with self.subTest(path=path.relative_to(repo_skill_root)):
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"\bPhase\s*8\b")

    def test_known_issues_no_fabricated_patterns(self) -> None:
        path = self.template_root / "company-jarvis" / "module" / "known-issues.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("Stale Cache", text)
        self.assertNotIn("Timeout Under", text)
        self.assertNotIn("Schema Drift", text)
        self.assertNotIn("Webhook Duplicate", text)

    def test_decisions_no_fabricated_decisions(self) -> None:
        path = self.template_root / "company-jarvis" / "module" / "decisions.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("Single Table vs", text)
        self.assertNotIn("API Versioning Strategy", text)
        self.assertNotIn("Event Bus Choice", text)

    def test_rejected_features_no_fabricated_features(self) -> None:
        path = self.template_root / "company-jarvis" / "module" / "rejected-features.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("Real-Time Sync", text)
        self.assertNotIn("GraphQL API", text)
        self.assertNotIn("Self-Service Admin", text)

    def test_test_coverage_no_fabricated_data(self) -> None:
        path = self.template_root / "company-jarvis" / "module" / "test-coverage.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("<repo>/tests/", text)
        self.assertNotIn("```bash", text)

    def test_crosscutting_no_module_letter_placeholders(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "cross-cutting" / "module-interactions.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("module-a", text)
        self.assertNotIn("module-b", text)
        self.assertNotIn("module-c", text)
        self.assertNotIn("module-d", text)
        self.assertNotIn("module-e", text)
        self.assertNotIn("module-f", text)

    def test_peer_product_no_product_placeholders(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "cross-cutting" / "peer-product-contracts.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("product-a", text)
        self.assertNotIn("product-b", text)
        self.assertNotIn("product-c", text)
        self.assertNotIn("product-d", text)

    def test_version_changelog_no_fake_commands(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "cross-cutting" / "version-changelog.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("glab api", text)

    def test_jarvis_first_routing_no_angle_placeholders(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "references" / "jarvis-first-routing.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("<repo>", text)
        self.assertNotIn("<endpoint>", text)
        self.assertNotIn("<confirmed company>", text)

    def test_canonical_repo_fleet_no_fabricated_scripts(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "references" / "canonical-repo-fleet.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("fleet-update.sh", text)
        self.assertNotIn("install-and-sync.sh", text)
        self.assertNotIn("LEGACY.md", text)

    def test_tools_readme_no_placeholder_tools(self) -> None:
        path = self.template_root / "company-jarvis" / "repo" / "tools" / "README.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("`<tool>`", text)
        self.assertNotIn("<url-or-path>", text)


class SemanticGateTests(unittest.TestCase):
    """semantic gate: evidence pointers, generic phrases, route duplication,
    Phase 12 preflight enhanced leak detection, Phase 11 overclaim/email, consistency."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "modules").mkdir(parents=True, exist_ok=True)
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True, exist_ok=True)
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(self.home / "_bootstrap" / "discovery" / name, "present")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str = "test-repo") -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def _make_verifier(self, stage: str = "final") -> _MOD.Verifier:
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        return _MOD.Verifier(self.home, [], run_precheck=False, stage=stage)

    # ── evidence pointer checks ──

    def test_valid_pointer_plus_ellipsis_pointer_still_fails(self) -> None:
        """One valid pointer does not excuse an ellipsis pointer in the same module."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n"
               "| test-repo:src/main/handler.go | handler | grep |\n"
               "| test-repo:src/main/... | ellipsis |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_evidence_pointer_invalid", codes)

    def test_directory_pointer_passes(self) -> None:
        """A pointer to an existing directory (not file) is acceptable."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main").mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n| test-repo:src/main/ | handler dir | ls |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("module_evidence_pointer_invalid", codes)

    def test_glob_pointer_fails(self) -> None:
        """A pointer with glob pattern is rejected."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n| test-repo:src/**/*.go | glob pattern |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_evidence_pointer_invalid", codes)

    # ── route duplication ──

    def test_three_duplicate_routes_fail(self) -> None:
        """3 modules with identical normalized routing → blocker."""
        routing_text = (
            "## 首跳路由\n"
            "| 触发信号 | 路由到 | 首个验证 |\n"
            "|---|---|---|\n"
            "| issue | skills/test-jarvis/SKILL.md | precheck |\n"
        )
        for mod in ["app", "api", "core"]:
            mod_dir = self.home / "modules" / mod
            mod_dir.mkdir(parents=True, exist_ok=True)
            _touch(mod_dir / "overview.md",
                   f"## 业务定位\n{mod} module.\n{routing_text}"
                   "## First Proof\nx\n## 常见 False Owner\nx\n"
                   "## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        v = self._make_verifier("final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("route_section_duplication", codes)

    def test_two_duplicate_routes_pass(self) -> None:
        """2 modules with identical routing — below the 3 threshold, no blocker."""
        routing_text = (
            "## 首跳路由\n"
            "| 触发信号 | 路由到 | 首个验证 |\n"
            "|---|---|---|\n"
            "| issue | skills/test-jarvis/SKILL.md | precheck |\n"
        )
        for mod in ["app", "api"]:
            mod_dir = self.home / "modules" / mod
            mod_dir.mkdir(parents=True, exist_ok=True)
            _touch(mod_dir / "overview.md",
                   f"## 业务定位\n{mod} module.\n{routing_text}"
                   "## First Proof\nx\n## 常见 False Owner\nx\n"
                   "## 证据与入口\nx\n## 模块关系\nx\n## 搜索与验证\nx")
        v = self._make_verifier("final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("route_section_duplication", codes)

    # ── generic phrase detection ──

    def test_generic_module_phrase_with_repo_readable_fails(self) -> None:
        """Generic CN phrase '本模块相关问题' with repo readable → blocker."""
        repo = self._make_repo("test-repo")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp module.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n## 证据与入口\nx\n"
               "## 模块关系\n本模块相关问题待首次 pilot 后确认\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("generic_module_phrase_cn_issues", codes)

    def test_generic_phrase_without_repo_passes(self) -> None:
        """Generic phrase without repos is not checked (no evidence to scan)."""
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\n本模块尚未通过 pilot\n## 证据与入口\nx\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("generic_module_phrase_cn_no_pilot", codes)

    # ── routing repo evidence ──

    def test_routing_mentions_repo_not_in_evidence_fails(self) -> None:
        """First-hop routing target column mentions a repo not in module's own evidence → blocker."""
        repo = self._make_repo("mentioned-repo")
        (repo / "src").mkdir(parents=True)
        _touch(repo / "src" / "main.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n"
               "## 首跳路由\n"
               "| 触发信号 | 路由到 | 首个验证 |\n"
               "|---|---|---|\n"
               "| issue | mentioned-repo:src/main | precheck |\n"
               "## First Proof\nx\n## 常见 False Owner\nx\n"
               "## 证据与入口\n| other-repo:src/main.go | handler | grep |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("routing_repo_not_in_evidence", codes)

    # ── Phase 12 preflight: verbatim leak detection ──

    def test_final_commit_hash_verbatim_in_visible_fails(self) -> None:
        """Final commit hash from hidden oracle appears verbatim in visible START → blocker."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-1").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard error, see commit abc1234567890def.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234567890def\n"
            "Changed files: src/server/Handler.java\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_final_commit_hash_in_visible", codes)

    def test_changed_path_verbatim_in_visible_reconstructed_fails(self) -> None:
        """Changed path from hidden oracle appears verbatim in visible START → blocker for reconstructed."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-2"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-2").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Issue with src/server/Handler.java.\n\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/server/Handler.java — add null guard\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-2")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_changed_path_in_visible", codes)

    def test_clean_symptom_only_reconstructed_passes(self) -> None:
        """Symptom-only reconstructed case with no verbatim leaks passes."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-3"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-3").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard returns 500 error when date range is empty.\n"
            "Allowed repos: test-app\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234deadbeef\n"
            "Changed files:\n"
            "  - src/server/DateUtil.java\n"
            "  - src/server/DateUtilTest.java\n"
            "Actual fix: added null check for empty date range in DateUtil\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-3")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # No verbatim hash or path in visible → clean
        self.assertNotIn("preflight_final_commit_hash_in_visible", codes)
        self.assertNotIn("preflight_changed_path_in_visible", codes)
        self.assertNotIn("preflight_hidden_oracle_marker_in_visible", codes)

    def test_cn_action_verb_not_caught(self) -> None:
        """Reconstructed START with Chinese action verb '完善' no longer auto-fails
        (verb blacklist removed — only verbatim checks remain)."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-4"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-4").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n"
            "START construction: reconstructed-from-outcome-subject\n\n"
            "## Visible START\nLog format needs improvement.\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-4")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # CN action verb blacklist removed — no auto-fail
        self.assertNotIn("preflight_reconstructed_subject_cn_action_verb", codes)

    def test_outcome_provenance_not_caught(self) -> None:
        """'inferred from fix context' in visible START no longer auto-fails
        (outcome-derived provenance NL check removed)."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-5"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-5").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard error. Provenance: inferred from fix context and final diff.\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-5")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("preflight_outcome_derived_provenance", codes)

    def test_hidden_oracle_marker_in_visible_fails(self) -> None:
        """Structured 'Hidden Outcome Oracle' heading text in visible START → blocker."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-6"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-6").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "- **Actual outcome**: copied future answer.\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-6")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_hidden_oracle_marker_in_visible", codes)

    def test_ineligible_case_blocked_in_preflight(self) -> None:
        """Explicit Eligibility=ineligible-leaky → preflight rejects."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-7"
        case_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: ineligible-leaky\n\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-7")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_ineligible", codes)

    # ── replay leakage analysis ──

    def test_leaky_case_replay_with_no_skill_gap_fails(self) -> None:
        """ineligible-leaky case with replay run and no_skill_gap decision → blocker."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: ineligible-leaky\nCommit title: add null guard to handler\n")
        _touch(run_dir / "exit-code", "0")
        _touch(case_dir / "skill-update-decision.md",
               "Decision: no_skill_gap\nStatus: closed\n")
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("replay_leaked_start_executed", codes)
        self.assertIn("replay_leaked_illegal_decision_no_skill_gap", codes)

    # ── phase consistency ──

    def test_phase_status_mismatch_fails(self) -> None:
        """result and state disagree on same phase → blocker."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "completed"}})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input",
                     "phase_status": {"phase-12-history-replay": "needs-input"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("phase_status_mismatch", codes)

    def test_final_verifier_rejects_in_progress_checkpoint(self) -> None:
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "in-progress",
                "paths": {},
                "summary": "Phase 10 checkpoint",
                "missing_inputs": [],
                "blockers": [],
                "phase_summary": {"phase-10-onboarding-report": "needs-input"},
            },
        )
        _touch_json(
            self.home / "bootstrap-state.json",
            {
                "status": "in-progress",
                "phase": "phase-10-onboarding-report",
                "phase_status": {"phase-10-onboarding-report": "needs-input"},
            },
        )
        report = _MOD.Verifier(self.home, [], run_precheck=False, stage="final").verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("bootstrap_still_in_progress", codes)
        self.assertNotIn("result_status_invalid", codes)

    def test_future_phase_status_cannot_be_preclassified(self) -> None:
        phase_status = {
            "phase-10-onboarding-report": "completed",
            "phase-11-shadow-pilot": "needs-input",
            "phase-12-history-replay": "needs-input",
            "phase-13-controlled-writeback": "needs-input",
            "phase-14-day2-operation": "needs-input",
        }
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "needs-input",
                "paths": {},
                "summary": "Stopped after Phase 10",
                "missing_inputs": [],
                "blockers": [],
                "phase_summary": phase_status,
            },
        )
        _touch_json(
            self.home / "bootstrap-state.json",
            {
                "status": "needs-input",
                "phase": "phase-10-onboarding-report",
                "phase_status": phase_status,
            },
        )
        report = _MOD.Verifier(self.home, [], run_precheck=False, stage="final").verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("future_phase_status_preclassified", codes)
        self.assertIn("completed_current_phase_not_advanced", codes)

    def test_pending_future_phases_are_not_preclassified(self) -> None:
        phase_status = {
            "phase-10-onboarding-report": "needs-input",
            "phase-11-shadow-pilot": "pending",
            "phase-12-history-replay": "pending",
            "phase-13-controlled-writeback": "pending",
            "phase-14-day2-operation": "pending",
        }
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "needs-input",
                "paths": {},
                "summary": "Phase 10 needs input",
                "missing_inputs": ["owner confirmation"],
                "blockers": [],
                "phase_summary": phase_status,
            },
        )
        _touch_json(
            self.home / "bootstrap-state.json",
            {
                "status": "needs-input",
                "phase": "phase-10-onboarding-report",
                "phase_status": phase_status,
            },
        )
        report = _MOD.Verifier(self.home, [], run_precheck=False, stage="final").verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("future_phase_status_preclassified", codes)
        self.assertNotIn("completed_current_phase_not_advanced", codes)

    def test_summary_overclaim_fails(self) -> None:
        """Summary claims 'complete through Phase 12' but Phase 06 is not completed."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {
                         "phase-06-business-discovery": "needs-input",
                         "phase-12-history-replay": "in-progress",
                     }})
        _touch(self.home / "bootstrap-state.json", "{}")
        # patch summary after json write
        result_path = self.home / "bootstrap-result.json"
        data = json.loads(result_path.read_text())
        data["summary"] = "complete through Phase 12 pending owner review"
        result_path.write_text(json.dumps(data))
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("summary_completion_overclaim", codes)

    def test_runtime_root_mismatch_fails(self) -> None:
        """day2 checks reference alternate root different from confirmed root — exact comparison."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": []})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input", "paths": {"runtime_root": "/opt/customer/jarvis-box"},
                     "phase": "phase-14", "confirmed_answers": {}, "method_repo": {},
                     "phase_status": {"phase-14-day2-operation": "needs-input"}})
        _touch(self.home / "_bootstrap" / "day2-operation.md",
               "check ran on /var/lib/jarvis-box/envs/.env.jarvis-box\n"
               "doctor output references /var/lib/jarvis-box\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_runtime_root_mismatch", codes)

    def test_non_blocking_missing_inputs_pass(self) -> None:
        """Deferred/non-critical items listed as missing input → blocker caught."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [
                         "external-docs access is deferred and non-critical for first workflow",
                         "scaffold-only maturation for create-scaffold-needs-pilot skills is backlog",
                     ],
                     "blockers": []})
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("deferred_still_missing_input", codes)

    # ── Phase 11 dry-run overclaim ──


    def test_phase11_email_unredacted_fails(self) -> None:
        """Pilot artifact with unredacted real email → blocker."""
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-20250101-002"
        pilot_dir.mkdir(parents=True)
        _touch(pilot_dir / "shadow-pilot-run.md",
               "Author: alice@customer-company.com\nReviewer: bob@example.org\n")
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_email_unredacted", codes)

    def test_fixture_email_still_fails(self) -> None:
        """All emails fail — no whitelist for fixture/system emails."""
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-20250101-003"
        pilot_dir.mkdir(parents=True)
        _touch(pilot_dir / "shadow-pilot-run.md",
               "Committer: e2e-fixture@jarvis-box.local\n")
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_email_unredacted", codes)

    # ── new round-2 tests ──

    def test_backtick_wrapped_file_pointer_passes(self) -> None:
        """Backtick-wrapped file pointer in evidence section table passes."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n| `test-repo:src/main/handler.go` | handler | grep |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("module_evidence_pointer_invalid", codes)
        self.assertNotIn("module_overview_pointer_unresolvable", codes)

    def test_backtick_wrapped_dir_pointer_passes(self) -> None:
        """Backtick-wrapped directory pointer passes and old check also accepts it."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main").mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp.\n## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n| `test-repo:src/main/` | handler dir | ls |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("module_evidence_pointer_invalid", codes)
        self.assertNotIn("module_overview_pointer_unresolvable", codes)

    def test_docs_build_outside_evidence_section_ignored(self) -> None:
        """npm run docs:build outside evidence section is not treated as pointer."""
        repo = self._make_repo("test-repo")
        (repo / "src").mkdir(parents=True)
        _touch(repo / "src" / "main.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp\nRun `npm run docs:build` to generate docs.\n"
               "## 首跳路由\nx\n## First Proof\nx\n"
               "## 常见 False Owner\nx\n"
               "## 证据与入口\n| test-repo:src/main.go | handler | grep |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("module_evidence_pointer_invalid", codes)

    def test_repo_app_not_matched_by_application(self) -> None:
        """Repo 'app' is NOT matched by 'application' in routing (exact token matching)."""
        repo_app = self._make_repo("app")
        (repo_app / "src").mkdir(parents=True)
        _touch(repo_app / "src" / "main.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nApp module.\n"
               "## 首跳路由\n"
               "| 触发信号 | 路由到 | 首个验证 |\n"
               "|---|---|---|\n"
               "| issue | application-repo:src/main | precheck |\n"
               "## First Proof\nx\n## 常见 False Owner\nx\n"
               "## 证据与入口\n| app:src/main.go | handler | grep |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo_app], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # 'app' should NOT appear as mentioned because routing says 'application-repo'
        self.assertNotIn("routing_repo_not_in_evidence", codes)

    def test_fix_verb_in_subject_not_caught(self) -> None:
        """**Subject:** 'fix: dashboard error' — action verb 'fix' no longer auto-fails
        (verb blacklist removed)."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-5"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-5").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "### Reconstructed START (from eligible-reconstructed subject)\n"
            "**Subject:** \"fix: dashboard 500 error\"\n\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-5")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # EN action verb blacklist removed — no auto-fail
        self.assertNotIn("preflight_reconstructed_subject_en_action_verb", codes)

    def test_eligible_direct_clean_passes(self) -> None:
        """eligible-direct with real pre-outcome issue/log provenance passes."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-6"
        case_dir.mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-6").mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-direct\n"
            "Pre-outcome evidence: original issue #1234 with error log\n\n"
            "## Visible START\n"
            "Dashboard returns 500. ErrorHandler class throws NPE.\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "1. **ErrorHandler.java** — add null guard\n"
            "2. **DateUtil.java** — handle empty range\n"
            "Final commit: abc1234\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-6")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # eligible-direct should NOT trigger reconstructed leak rules
        self.assertNotIn("preflight_hidden_identifier_in_visible", codes)
        self.assertNotIn("preflight_direct_case_outcome_provenance", codes)

    def test_final_leaky_case_but_still_claims_eligible_reconstructed(self) -> None:
        """Final: case claims eligible-reconstructed but verbatim path leak found, replay was run → all blockers."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Bug in src/main/DataServiceImpl.java.\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/main/DataServiceImpl.java — add null guard\n"
            "Final commit: abc1234\n")
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch(case_dir / "skill-update-decision.md",
               "Decision: no_skill_gap\nStatus: closed\n")
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "completed"}})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input", "phase_status": {"phase-12-history-replay": "completed"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("replay_leaked_start_executed", codes)
        self.assertIn("replay_leaked_status_not_failed", codes)
        self.assertIn("replay_leaked_phase12_not_failed", codes)
        self.assertIn("replay_leaked_illegal_decision_no_skill_gap", codes)

    def test_final_clean_eligible_replay_no_leak_findings(self) -> None:
        """Final: clean eligible-direct replay produces no leaked-start findings."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\nEligibility: eligible-direct\n"
            "Pre-outcome evidence: original issue #1234\n\n"
            "## Visible START\n"
            "Dashboard returns 500 when date range is empty.\n"
            "## Hidden Outcome Oracle\n"
            "- src/server/DateUtil.java — add null check\n"
            "Final commit: abc1234\n")
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch_json(run_dir / "host-isolation-evidence.json",
                    {"mechanism": "secondary-apple-container",
                     "allowed_mounts": [
                         {"container": "/replay/visible", "mode": "ro"},
                         {"container": "/replay/worktree", "mode": "rw"},
                         {"container": "/replay/company-runtime", "mode": "ro"},
                         {"container": "/replay/output", "mode": "rw"}]})
        _touch(case_dir / "replay-failure-analysis.md", "oracle comparison done")
        _touch(case_dir / "skill-update-decision.md", "Decision: no_skill_gap")
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "completed"}})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input", "phase_status": {"phase-12-history-replay": "completed"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("replay_leaked_start_executed", codes)
        self.assertNotIn("replay_leaked_status_not_failed", codes)
        self.assertNotIn("replay_leaked_illegal_decision_no_skill_gap", codes)

    def test_runtime_root_suffix_overlap_fails(self) -> None:
        """Exact comparison: /var/lib/jarvis-box/envs/... under confirmed /e2e/install-root/var/lib/jarvis-box → mismatch."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": []})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input",
                     "paths": {"runtime_root": "/e2e/install-root/var/lib/jarvis-box"},
                     "phase": "phase-14", "confirmed_answers": {}, "method_repo": {},
                     "phase_status": {"phase-14-day2-operation": "needs-input"}})
        _touch(self.home / "_bootstrap" / "day2-operation.md",
               "check ran on /var/lib/jarvis-box/envs/.env.jarvis-box\n"
               "doctor output references /var/lib/jarvis-box\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_runtime_root_mismatch", codes)


    # ── round-3 tests ──

    def test_bold_decision_repo_local_fails(self) -> None:
        """**Decision:** `repo-local` — bold label + backtick value, leaked case → illegal decision."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Bug in src/main/ReporterServiceImpl.java.\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/main/ReporterServiceImpl.java — fix edge case\n"
            "Final commit: abc1234\n")
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result")
        _touch(case_dir / "skill-update-decision.md",
            "**Decision:** `repo-local` — durable skill gap\n"
            "**Status:** `deferred` — pending owner\n\n"
            "## Primary Home\n"
            "- **repo-local** skills/code-review/SKILL.md\n")
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "completed"}})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "needs-input",
                     "phase_status": {"phase-12-history-replay": "completed"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("replay_leaked_start_executed", codes)
        self.assertIn("replay_leaked_illegal_decision_repo-local", codes)
        self.assertIn("replay_leaked_illegal_primary_home_repo-local", codes)
        self.assertIn("replay_leaked_illegal_durable_skill_gap", codes)

    def test_leaked_case_negative_home_explanations_do_not_create_primary_home_finding(self) -> None:
        """A compliant deferred decision may explain rejected homes without selecting one."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-reconstructed\n\n"
               "## Visible START\nBug in src/main/ReporterServiceImpl.java.\n"
               "## Hidden Outcome Oracle\n"
               "### Actual Changed Surfaces\n"
               "- src/main/ReporterServiceImpl.java — fix edge case\n"
               "Final commit: abc1234\n")
        _touch(run_dir / "exit-code", "0")
        _touch(case_dir / "skill-update-decision.md",
               "**Decision:** `defer`\n**Status:** `deferred`\n\n"
               "## Primary Home\n- none\n- NOT company Jarvis\n- NOT upstream\n")
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "failed", "paths": {}, "summary": "", "missing_inputs": [],
                     "blockers": [], "phase_summary": {"phase-12-history-replay": "failed"}})
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "failed", "phase_status": {"phase-12-history-replay": "failed"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertFalse(any(code.startswith("replay_leaked_illegal_primary_home_") for code in codes))

    def test_routing_target_ellipsis_pointer_fails(self) -> None:
        """Routing target column with <repo>:src/... (ellipsis) → blocker even without generic phrase."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nUnique routing test module.\n"
               "## 首跳路由\n"
               "| 触发信号 | 路由到 | 首个验证 |\n"
               "|---|---|---|\n"
               "| issue | test-repo:src/... | precheck |\n"
               "## First Proof\nx\n## 常见 False Owner\nx\n"
               "## 证据与入口\n| test-repo:src/main/handler.go | handler |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_evidence_pointer_invalid", codes)

    def test_backtick_routing_pointer_with_explanation_still_fails(self) -> None:
        """A backtick-wrapped bad route pointer cannot hide behind prose in its table cell."""
        repo = self._make_repo("test-repo")
        (repo / "src" / "main" / "handler.go").parent.mkdir(parents=True)
        _touch(repo / "src" / "main" / "handler.go", "package main")
        _touch(self.home / "modules" / "app" / "overview.md",
               "## 业务定位\nUnique routing test module.\n"
               "## 首跳路由\n"
               "| 触发信号 | 路由到 | 首个验证 |\n"
               "|---|---|---|\n"
               "| issue | `test-repo:src/...` 对应实现 | precheck |\n"
               "## First Proof\nx\n## 常见 False Owner\nx\n"
               "## 证据与入口\n| test-repo:src/main/handler.go | handler |\n"
               "## 模块关系\nx\n## 搜索与验证\nx")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("module_evidence_pointer_invalid", codes)

    def test_missing_input_scaffold_owner_artifacts_fails(self) -> None:
        """'scaffold-only workflows ... need owner-provided artifacts' listed as missing_input → blocker."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [
                         "scaffold-only starter workflows need owner-provided artifacts to mature",
                     ],
                     "blockers": []})
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("scaffold_maturation_as_missing_input", codes)

    def test_missing_input_deferred_non_first_workflow_fails(self) -> None:
        """'deferred-needs-access ... not first-workflow critical' listed as missing_input → blocker."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [
                         "external-api-docs deferred-needs-access — not first-workflow critical",
                     ],
                     "blockers": []})
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("deferred_still_missing_input", codes)

    def test_deferred_first_workflow_critical_passes(self) -> None:
        """'deferred access is first-workflow critical' — NOT treated as backlog, should still be valid missing_input."""
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [
                         "source repo access deferred but access is first-workflow critical",
                     ],
                     "blockers": []})
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("deferred_still_missing_input", codes)

    # ── item 8: new structured-field tests ──

    def test_prose_final_diff_unavailable_no_marker_leak(self) -> None:
        """Prose 'final diff unavailable to replay agent' in visible does NOT trigger marker leak."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "The final diff is unavailable to the replay agent.\n"
            "## Hidden Outcome Oracle\n"
            "Final diff / commit pointer: abc1234567890def\n"
            "### Actual Changed Surfaces\n"
            "- src/server/Handler.java\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("preflight_hidden_oracle_marker_in_visible", codes,
                         "prose 'final diff unavailable' must not trigger field-label marker")

    def test_untouched_option_list_not_eligible(self) -> None:
        """Eligibility field with option-list value like 'eligible-direct / eligible-reconstructed'
        is NOT treated as eligible (exact match required, not substring)."""
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n")
        # No Status field at all — should fail preflight as not-ready
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_not_ready", codes)

    def test_no_skill_gap_heading_but_placeholder_pointer_fails(self) -> None:
        """no_skill_gap: yes with <pointer or none> placeholder → missing evidence."""
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "replay-failure-analysis.md",
               "## no_skill_gap Check\n"
               "no_skill_gap: yes\n"
               "Exact command or artifact pointer: <pointer or none>\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False, stage="final")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "major"}
        self.assertIn("oracle_comparison_missing_outcome_evidence", codes)


# ═══════════════════════════════════════════════════════════════════════
# Guards 1–9 tests (r9 deterministic guards)
# ═══════════════════════════════════════════════════════════════════════


class DiscoveryRetrievalCommandTests(unittest.TestCase):
    """Guard 1: retrieval commands must not contain ellipsis or pseudo-paths."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True)
        for name in _MOD.REQUIRED_DISCOVERY_FILES:
            _touch(self.home / "_bootstrap" / "discovery" / name, "present")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str = "repo-a") -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def test_ascii_ellipsis_in_retrieval_command_fails(self) -> None:
        _touch(self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
               "## Evidence Retrieval Commands\n"
               "```bash\n"
               "find ... -name '*.go' | xargs grep -l handler\n"
               "```\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("discovery_retrieval_command_invalid", codes)

    def test_unicode_ellipsis_in_retrieval_command_fails(self) -> None:
        _touch(self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
               "## 证据检索命令\n"
               "```bash\n"
               "grep -r 'pattern' src/…\n"
               "```\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("discovery_retrieval_command_invalid", codes)

    def test_repo_checkout_pseudo_path_fails(self) -> None:
        _touch(self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
               "## Evidence Retrieval Commands\n"
               "- Clone with `git clone <url> repo checkout` and then scan\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("discovery_retrieval_command_invalid", codes)

    def test_ellipsis_outside_command_section_passes(self) -> None:
        _touch(self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
               "## Overview\nSome evidence was gathered... but more work is needed.\n\n"
               "## Evidence Retrieval Commands\n"
               "grep -r Handler src/\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("discovery_retrieval_command_invalid", codes)

    def test_clean_retrieval_commands_pass(self) -> None:
        _touch(self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
               "## Evidence Retrieval Commands\n"
               "grep -r handler src/\n"
               "git log --since=\"2024-01-01\" -- src/\n"
               "rg TODO src/\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("discovery_retrieval_command_invalid", codes)

    def test_discovery_pseudo_pointer_fails(self) -> None:
        repo = self._make_repo()
        _touch(
            self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
            "Implementation anchor: `repo-a:src/.../Handler.java`\n",
        )
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("discovery_evidence_pointer_invalid", codes)

    def test_discovery_resolvable_pointer_passes(self) -> None:
        repo = self._make_repo()
        _touch(repo / "src" / "Handler.java", "class Handler {}\n")
        _touch(
            self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
            "Implementation anchor: `repo-a:src/Handler.java`\n",
        )
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("discovery_evidence_pointer_invalid", codes)

    def test_discovery_placeholder_fails(self) -> None:
        repo = self._make_repo()
        _touch(
            self.home / "_bootstrap" / "discovery" / "evidence-inventory.md",
            "Retrieval: `grep -ril <module> /checkout/<repo>/`\n",
        )
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("discovery_evidence_placeholder", codes)

    def test_generation_plan_command_metavariable_is_allowed(self) -> None:
        repo = self._make_repo()
        _touch(
            self.home / "_bootstrap" / "discovery" / "generation-plan.md",
            "Run `instantiate_company_jarvis.py module --name <module>` for each confirmed module.\n",
        )
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        matching = [
            finding
            for finding in report["findings"]
            if finding["code"] == "discovery_evidence_placeholder"
            and "generation-plan.md" in finding["message"]
        ]
        self.assertFalse(matching)


class ConfirmedProductIdentityTests(unittest.TestCase):
    """Guard 2: confirmed product identity must not stay unresolved."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_unresolved_product_identity_literal_fails(self) -> None:
        _touch(self.home / "README.md",
               "# Company Jarvis\nStatus: unresolved-product-identity\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          expected_product_identity="HENGSHI SENSE")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("confirmed_product_identity_unresolved", codes)

    def test_generic_needs_owner_confirmation_elsewhere_passes(self) -> None:
        _touch(self.home / "README.md",
               "## Identity\n| Product Identity | HENGSHI SENSE |\n\n"
               "Note: needs-owner-confirmation for module routing.\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          expected_product_identity="HENGSHI SENSE")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("confirmed_product_identity_unresolved", codes)

    def test_product_identity_field_with_needs_owner_confirmation_fails(self) -> None:
        _touch(
            self.home / "README.md",
            "## Identity\n| Product Identity | HENGSHI SENSE — needs-owner-confirmation |\n",
        )
        v = _MOD.Verifier(
            self.home, [], run_precheck=False, expected_product_identity="HENGSHI SENSE"
        )
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("confirmed_product_identity_unresolved", codes)

    def test_clean_product_identity_passes(self) -> None:
        _touch(self.home / "README.md",
               "# HENGSHI SENSE JARVIS\nProduct identity confirmed: HENGSHI SENSE\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          expected_product_identity="HENGSHI SENSE")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("confirmed_product_identity_unresolved", codes)

    def test_no_expected_identity_skips(self) -> None:
        _touch(self.home / "README.md",
               "Status: unresolved-product-identity\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)  # no expected_product_identity
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("confirmed_product_identity_unresolved", codes)


class CompanyEntryReferencesHandoffTests(unittest.TestCase):
    """Guard 3: entry must have valid reference links and repo handoffs."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "skills" / "test-jarvis").mkdir(parents=True)
        (self.home / "references").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str) -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def test_entry_reference_missing_fails(self) -> None:
        _touch(self.home / "skills" / "test-jarvis" / "SKILL.md",
               "See references/nonexistent.md for details.\n\n"
               "## Repo-local Execution\n- repo-a: skills/SKILL.md\n")
        repo = self._make_repo("repo-a")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("entry_reference_missing", codes)

    def test_entry_repo_handoff_missing_fails(self) -> None:
        _touch(self.home / "skills" / "test-jarvis" / "SKILL.md",
               "## Repo-local Execution\n- repo-a: skills/SKILL.md\n")
        _touch(self.home / "references" / "test.md", "placeholder")
        repo_a = self._make_repo("repo-a")
        repo_b = self._make_repo("repo-b")  # not mentioned in entry
        v = _MOD.Verifier(self.home, [repo_a, repo_b], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("entry_repo_handoff_missing", codes)

    def test_valid_references_and_handoffs_pass(self) -> None:
        _touch(self.home / "references" / "test.md", "present")
        _touch(self.home / "skills" / "test-jarvis" / "SKILL.md",
               "See references/test.md for details.\n\n"
               "## Repo-local Execution\n- repo-a: skills/SKILL.md\n"
               "- repo-b: skills/SKILL.md\n")
        repo_a = self._make_repo("repo-a")
        repo_b = self._make_repo("repo-b")
        v = _MOD.Verifier(self.home, [repo_a, repo_b], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("entry_reference_missing", codes)
        self.assertNotIn("entry_repo_handoff_missing", codes)


class SourceRouteFillingTests(unittest.TestCase):
    """Guard 5: accessible source routes must have filled README.md."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "sources" / "source-a").mkdir(parents=True)
        (self.home / "sources" / "source-b").mkdir(parents=True)
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str) -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def test_source_route_unfilled_bootstrap_required_fails(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Host\nBOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included | visible |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes)

    def test_source_route_angle_placeholder_fails(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Connection\nHost: `<repo>`\n")
        repo = self._make_repo("source-a")  # same-name repo makes it accessible
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes)

    def test_source_route_host_mismatch_fails(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Connection\n- **Host**: `gitlab.other.com`\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included | visible |\n")
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "completed",
                     "confirmed_answers": {"gitlab_host_confirmed": "gitlab.customer.com"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_host_mismatch", codes)

    def test_deferred_source_skips(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Status\n- **Access 状态**: `deferred-needs-access`\n\nBOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes)

    def test_not_accessible_source_skips(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "BOOTSTRAP_REQUIRED\n")
        # No generation-plan entry and no matching repo → not accessible
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes)

    def test_local_only_source_skips_host_check(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Connection\nHost: gitlab.other.com\n\nSource is local-only.\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | route-created |\n")
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "completed",
                     "confirmed_answers": {"gitlab_host_confirmed": "gitlab.customer.com"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_host_mismatch", codes)

    def test_source_route_needs_evidence_fails(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Status\nneeds-evidence\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | mapped |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes)

    def test_source_route_references_path_fails(self) -> None:
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Path\nREFERENCES_PATH\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | route-created |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes)


class RepoLocalTruthTests(unittest.TestCase):
    """Guard 6: repo-local packages must contain observable repo truth."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str) -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        (repo / "skills").mkdir()
        (repo / "skills" / "references").mkdir(parents=True)
        # Default branch: main
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
        (repo / ".git" / "refs" / "remotes" / "origin").mkdir(parents=True)
        (repo / ".git" / "refs" / "remotes" / "origin" / "HEAD").write_text("ref: refs/remotes/origin/main\n")
        return repo

    def _write_valid_truth_files(self, repo: Path, branch: str = "main") -> None:
        _touch(repo / "skills" / "SKILL.md", f"# Skill\nDefault branch: {branch}\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- `src/main/` — core service\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "Runtime evidence: package.json\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- `src/main/` — primary code\n")
        (repo / "src" / "main").mkdir(parents=True, exist_ok=True)

    def test_bootstrap_required_fails_in_each_core_truth_file(self) -> None:
        repo = self._make_repo("test-repo")
        self._write_valid_truth_files(repo)
        core_files = [
            "skills/SKILL.md",
            "skills/references/architecture-map.md",
            "skills/references/test-entrypoints.md",
            "skills/references/runtime-and-testability.md",
            "skills/references/source-of-truth.md",
        ]

        for rel_path in core_files:
            with self.subTest(rel_path=rel_path):
                path = repo / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\nBOOTSTRAP_REQUIRED\n", encoding="utf-8")
                report = _MOD.Verifier(
                    self.home, [repo], run_precheck=False
                ).verify()
                matching = [
                    finding for finding in report["findings"]
                    if finding["severity"] == "blocker"
                    and finding["code"] == "repo_local_truth_placeholder"
                    and rel_path in finding["message"]
                    and "BOOTSTRAP_REQUIRED" in finding["message"]
                ]
                self.assertTrue(matching, report["findings"])
                path.write_text(original, encoding="utf-8")

    def test_missing_core_truth_file_fails(self) -> None:
        repo = self._make_repo("test-repo")
        self._write_valid_truth_files(repo)
        missing = repo / "skills" / "references" / "runtime-and-testability.md"
        missing.unlink()

        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        matching = [
            finding for finding in report["findings"]
            if finding["severity"] == "blocker"
            and finding["code"] == "repo_local_truth_file_missing"
            and "runtime-and-testability.md" in finding["message"]
        ]
        self.assertTrue(matching, report["findings"])

    def test_unrendered_token_in_core_truth_file_fails(self) -> None:
        repo = self._make_repo("test-repo")
        self._write_valid_truth_files(repo)
        path = repo / "skills" / "references" / "source-of-truth.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n{{REPO_NAME}}\n",
                        encoding="utf-8")

        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_truth_placeholder", codes)

    def test_phase8_generation_narration_in_repo_skill_fails(self) -> None:
        repo = self._make_repo("test-repo")
        self._write_valid_truth_files(repo)
        _touch(
            repo / "skills" / "code-review" / "SKILL.md",
            "Phase 8 用仓库实际证据替换下表。\n",
        )
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_bootstrap_narration", codes)

    def test_checkout_branch_is_not_default_branch_evidence(self) -> None:
        repo = self._make_repo("test-repo")
        self._write_valid_truth_files(repo, branch="feature/current-work")
        (repo / ".git" / "HEAD").write_text(
            "ref: refs/heads/feature/current-work\n", encoding="utf-8"
        )
        (repo / ".git" / "refs" / "remotes" / "origin" / "HEAD").unlink()

        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_default_branch_unverified", codes)

    def test_truth_angle_placeholder_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main: `<from company Jarvis>`\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- src/main/\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_truth_placeholder", codes)

    def test_truth_replace_with_actual_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "replace with actual repo path here\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_truth_placeholder", codes)

    def test_truth_generated_needs_owner_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "generated-needs-owner-confirmation\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_truth_placeholder", codes)

    def test_default_branch_mismatch_fails(self) -> None:
        repo = self._make_repo("test-repo")
        # Observed branch is 'main', stated branch is 'develop'
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: develop\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_default_branch_mismatch", codes)

    def test_main_confirm_when_not_main_fails(self) -> None:
        repo = self._make_repo("test-repo")
        # Override HEAD to a non-main branch
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/develop\n")
        (repo / ".git" / "refs" / "remotes" / "origin" / "HEAD").write_text("ref: refs/remotes/origin/develop\n")
        _touch(repo / "skills" / "SKILL.md", "# Skill\n- **Default branch**: `main` (confirm with owner)\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_default_branch_mismatch", codes)

    def test_architecture_unmapped_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\n- **Default branch**: `main`\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "## Architecture\nNo concrete paths here.\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_architecture_unmapped", codes)

    def test_test_command_missing_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "# Test Entrypoints\n<!-- npm test -->\n# <command>\nNormal prose.\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)

    def test_source_truth_unmapped_fails(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "## Source of Truth\nNo pointers.\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_source_truth_unmapped", codes)

    def test_truth_duplicated_three_repos_fails(self) -> None:
        identical = "Default branch: main\n\n## Architecture\n- src/main\n\nnpm test\n\n- src/main\n\npresent\n"
        repos = []
        for name in ["repo-a", "repo-b", "repo-c"]:
            repo = self._make_repo(name)
            _touch(repo / "skills" / "SKILL.md", identical)
            _touch(repo / "skills" / "references" / "architecture-map.md", identical)
            _touch(repo / "skills" / "references" / "test-entrypoints.md", identical)
            _touch(repo / "skills" / "references" / "source-of-truth.md", identical)
            _touch(repo / "skills" / "references" / "runtime-and-testability.md", identical)
            (repo / "src" / "main").mkdir(parents=True)
            repos.append(repo)
        v = _MOD.Verifier(self.home, repos, run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_truth_duplicated", codes)

    def test_no_repos_skips(self) -> None:
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("repo_local_truth_placeholder", codes)
        self.assertNotIn("repo_local_truth_duplicated", codes)

    def test_clean_repo_local_passes(self) -> None:
        repo = self._make_repo("test-repo")
        _touch(repo / "skills" / "SKILL.md", "# Skill\nDefault branch: main\n")
        _touch(repo / "skills" / "references" / "architecture-map.md",
               "- `src/main/` — core service\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md",
               "## Test\n| Command | Description |\n|---|---|\n| npm test | run tests |\n"
               "## Build\n| Command | Description |\n|---|---|\n| npm run build | build project |\n"
               "## Lint\n| Command | Description |\n|---|---|\n| npm run lint | lint code |\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md",
               "- `src/main/` — primary code\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md",
               "Runtime: node 18\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        for bad in ["repo_local_truth_placeholder", "repo_local_default_branch_mismatch",
                     "repo_local_architecture_unmapped", "repo_local_test_command_missing",
                     "repo_local_source_truth_unmapped", "repo_local_truth_duplicated"]:
            self.assertNotIn(bad, codes)


class SourceRouteFillingRegressionTests(unittest.TestCase):
    """Regression: deterministic parsing fixes for source route filling and repo-local truth."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "sources" / "source-a").mkdir(parents=True)
        (self.home / "sources" / "source-b").mkdir(parents=True)
        (self.home / "_bootstrap" / "discovery").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str, branch: str = "main") -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        (repo / ".git" / "HEAD").write_text(f"ref: refs/heads/{branch}\n")
        (repo / ".git" / "refs" / "remotes" / "origin").mkdir(parents=True)
        (repo / ".git" / "refs" / "remotes" / "origin" / "HEAD").write_text(f"ref: refs/remotes/origin/{branch}\n")
        (repo / "skills").mkdir()
        (repo / "skills" / "references").mkdir(parents=True)
        return repo

    # ── source route filling: enumeration must not trigger deferred ──

    def test_included_source_enumeration_with_blocked_still_fails_unfilled(self) -> None:
        """Included source README with enum listing 'blocked' must still report source_route_unfilled."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Access\nAccess can be: confirmed / needs-credentials / request-pending / blocked\n\n"
               "## Route\n- **Access 状态**: needs-evidence\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included | visible |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes,
                      "enumeration mentioning 'blocked' must not exempt unfilled fields")

    def test_included_source_enumeration_with_needs_access_still_fails_unfilled(self) -> None:
        """Included source with 'needs-access' only in enum description, not actual status → unfilled."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Status Options\nStatus values: confirmed / needs-access / blocked\n\n"
               "Host: BOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | mapped | visible |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_unfilled", codes)

    def test_deferred_readme_field_allows_unfilled(self) -> None:
        """README with an explicit needs-access state may retain deferred fields."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "- **Access 状态**: `needs-access`\n\nBOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included | visible |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes,
                         "deferred Access 状态 field must allow unfilled fields")

    def test_deferred_route_status_field_allows_unfilled(self) -> None:
        """README with - **Route 状态**: blocked is deferred, unfilled fields permitted."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "- **Route 状态**: blocked\n\nBOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | mapped |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes,
                         "deferred Route 状态 field must allow unfilled fields")

    def test_generation_plan_deferred_allows_unfilled(self) -> None:
        """generation-plan status = deferred-needs-access allows unfilled fields."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "## Route\nBOOTSTRAP_REQUIRED\nSome other content.\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | deferred-needs-access |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes)

    def test_generation_plan_blocked_allows_unfilled(self) -> None:
        """generation-plan status = blocked allows unfilled fields."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "BOOTSTRAP_REQUIRED\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | blocked | no access yet |\n")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_unfilled", codes)

    # ── Host regex: bold Markdown format ──

    def test_bold_host_mismatch_detected(self) -> None:
        """- **Host**: gitlab.wrong.com with bold Markdown is detected as mismatch."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "- **Host**: `gitlab.wrong.com`\n\nRoute verified.\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | included |\n")
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "completed",
                     "confirmed_answers": {"gitlab_host_confirmed": "gitlab.customer.com"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("source_route_host_mismatch", codes)

    def test_bold_host_matching_passes(self) -> None:
        """- **Host**: gitlab.customer.com matching confirmed host passes."""
        _touch(self.home / "sources" / "source-a" / "README.md",
               "- **Host**: `gitlab.customer.com`\n\nRoute verified.\n")
        _touch(self.home / "_bootstrap" / "discovery" / "generation-plan.md",
               "| Source | Status | Notes |\n|---|---|---|\n| source-a | route-created |\n")
        _touch_json(self.home / "bootstrap-state.json",
                    {"status": "completed",
                     "confirmed_answers": {"gitlab_host_confirmed": "gitlab.customer.com"}})
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("source_route_host_mismatch", codes)

    # ── Default branch: bold format with confirm parenthetical ──

    def test_bold_default_branch_mismatch_fails(self) -> None:
        """- **Default branch**: develop with bold, observed main → mismatch."""
        repo = self._make_repo("test-repo", branch="main")
        _touch(repo / "skills" / "SKILL.md",
               "# Skill\n- **Default branch**: `develop`\n")
        _touch(repo / "skills" / "references" / "architecture-map.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md", "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md", "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_default_branch_mismatch", codes)

    def test_bold_default_branch_with_confirm_mismatch_fails(self) -> None:
        """- **Default branch**: main (confirm from repo config) when observed is develop → mismatch."""
        repo = self._make_repo("test-repo", branch="develop")
        _touch(repo / "skills" / "SKILL.md",
               "# Skill\n- **Default branch**: `main` (confirm from repo config)\n")
        _touch(repo / "skills" / "references" / "architecture-map.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md", "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md", "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("repo_local_default_branch_mismatch", codes)

    def test_bold_default_branch_matching_passes(self) -> None:
        """- **Default branch**: main with bold, observed main → pass."""
        repo = self._make_repo("test-repo", branch="main")
        _touch(repo / "skills" / "SKILL.md",
               "# Skill\n- **Default branch**: `main`\n")
        _touch(repo / "skills" / "references" / "architecture-map.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md", "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md", "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("repo_local_default_branch_mismatch", codes)

    def test_bold_default_branch_with_confirm_matching_passes(self) -> None:
        """- **Default branch**: main (confirm from repo config) when observed is main → pass."""
        repo = self._make_repo("test-repo", branch="main")
        _touch(repo / "skills" / "SKILL.md",
               "# Skill\n- **Default branch**: `main` (confirm from repo config)\n")
        _touch(repo / "skills" / "references" / "architecture-map.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "test-entrypoints.md", "npm test\n")
        _touch(repo / "skills" / "references" / "source-of-truth.md", "- src/main\n")
        _touch(repo / "skills" / "references" / "runtime-and-testability.md", "present\n")
        (repo / "src" / "main").mkdir(parents=True)
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("repo_local_default_branch_mismatch", codes)


class PilotStructureTests(unittest.TestCase):
    """Guard 7: completed Phase 11 must have structurally honest pilot artifacts."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "_bootstrap" / "shadow-pilot").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _completed_phase11(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "completed", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-11-shadow-pilot": "completed"}})
        _touch(self.home / "bootstrap-state.json", "{}")

    def test_registry_missing_fails(self) -> None:
        self._completed_phase11()
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_required_artifact_missing", codes)

    def test_no_complete_pilot_dir_fails(self) -> None:
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md", "run content")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_required_artifact_missing", codes)

    def test_missing_sections_fails(self) -> None:
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "## OBSERVED EXECUTION\nRan precheck.\n")
        # Missing ROUTE / WORK / VERIFICATION PLAN and END / PILOT EVALUATION
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_section_missing", codes)

    def test_complete_diff_before_end_is_legal(self) -> None:
        """Phase 11: complete diff / changed paths appearing before END section is legal.
        Pilot may have observed full commit/MR diff as visible input."""
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "Full commit diff: src/handler.go changed with null guard.\n"
               "## ROUTE / WORK / VERIFICATION PLAN\nRun shadow pilot.\n"
               "## OBSERVED EXECUTION\nVerified routing.\n"
               "Final diff: git diff abc..def\n"
               "## END / PILOT EVALUATION\nAll checks passed.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("pilot_oracle_before_evaluator", codes)

    def test_pass_not_run_same_line_fails(self) -> None:
        """PASS + not-run on the SAME line → contradiction."""
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "## ROUTE / WORK / VERIFICATION PLAN\nRun shadow pilot.\n"
               "## OBSERVED EXECUTION\nIntegration test: PASS but the test was not run.\n"
               "## END / PILOT EVALUATION\nEvaluated.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_verification_contradiction", codes)

    def test_pass_and_not_run_different_lines_passes(self) -> None:
        """One item PASS, another item not-run, on DIFFERENT lines → no contradiction."""
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "## ROUTE / WORK / VERIFICATION PLAN\nRun shadow pilot.\n"
               "## OBSERVED EXECUTION\nRouting check: PASS\n"
               "Integration test: not executed (optional)\n"
               "## END / PILOT EVALUATION\nPartial verification.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Routing passed. Integration timeout — not run.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("pilot_verification_contradiction", codes)

    def test_quote_reference_line_ignored(self) -> None:
        """Quote lines (> ...) with PASS+not-run are ignored."""
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "## ROUTE / WORK / VERIFICATION PLAN\nRun shadow pilot.\n"
               "## OBSERVED EXECUTION\nVerified routing.\n"
               "> Template note: if test is PASS but not run, mark as not-evaluated.\n"
               "## END / PILOT EVALUATION\nDone.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("pilot_verification_contradiction", codes)

    def test_no_phase11_skips(self) -> None:
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("pilot_required_artifact_missing", codes)
        self.assertNotIn("pilot_section_missing", codes)

    def test_clean_pilot_passes(self) -> None:
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## PILOT INPUT / START\nInitial state.\n"
               "## ROUTE / WORK / VERIFICATION PLAN\nRun shadow pilot against repo-a.\n"
               "## OBSERVED EXECUTION\nAll checks passed. Integration test ran successfully.\n"
               "## END / PILOT EVALUATION\nCompared pilot results with expected behavior. All routing correct.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered. Tests executed successfully.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        for bad in ["pilot_required_artifact_missing", "pilot_section_missing",
                     "pilot_verification_contradiction"]:
            self.assertNotIn(bad, codes)

    def test_bare_start_work_end_headings_fail(self) -> None:
        """Bare ## START / ## WORK / ## END headings do NOT satisfy section requirements.
        Must match complete four-section role names."""
        self._completed_phase11()
        _touch(self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md", "registry")
        pilot_dir = self.home / "_bootstrap" / "shadow-pilot" / "pilot-001"
        pilot_dir.mkdir()
        _touch(pilot_dir / "shadow-pilot-run.md",
               "## START\nInitial state.\n"
               "## WORK\nRun shadow pilot.\n"
               "## OBSERVED EXECUTION\nRan checks.\n"
               "## END\nDone.\n")
        _touch(pilot_dir / "pilot-evidence.md", "Evidence gathered.")
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("pilot_section_missing", codes,
                      "bare START/WORK/END headings must not satisfy section requirements")


class ShadowPilotRepoScanTests(unittest.TestCase):
    """Phase 11 must search authorized repo history before requesting an artifact."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch_json(
            self.home / "bootstrap-result.json",
            {
                "status": "needs-input",
                "paths": {},
                "summary": "",
                "missing_inputs": ["shadow pilot artifact"],
                "blockers": [],
                "phase_summary": {"phase-11-shadow-pilot": "needs-input"},
            },
        )
        _touch(self.home / "bootstrap-state.json", "{}")

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str) -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def test_needs_input_without_registry_fails(self) -> None:
        repo = self._make_repo("repo-a")
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("shadow_pilot_repo_scan_missing", codes)

    def test_canonical_all_repo_coverage_passes(self) -> None:
        _touch(
            self.home / "_bootstrap" / "shadow-pilot" / "pilot-registry.md",
            "## Artifact Search Coverage\n"
            "| 来源 | 实际命令/查询 | 查询边界 | 候选或零结果 | 停止理由 | 状态 |\n"
            "|---|---|---|---|---|---|\n"
            "| repo-a | `git log --all` | all refs through HEAD | 0 | exhausted | scanned |\n"
            "| repo-b | `git log --all` | all refs through HEAD | 0 | exhausted | scanned |\n",
        )
        repos = [self._make_repo("repo-a"), self._make_repo("repo-b")]
        report = _MOD.Verifier(self.home, repos, run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("shadow_pilot_repo_scan_missing", codes)


class HistoryReplayRepoScanTests(unittest.TestCase):
    """Guard 8: Phase 12 can't claim missing input after scanning only part of fleet."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "evals" / "history-replay" / "cases").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _make_repo(self, name: str) -> Path:
        repo = Path(self.td.name) / name
        repo.mkdir(parents=True)
        (repo / ".git").mkdir()
        return repo

    def test_repo_scan_missing_fails(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "needs-input"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "evals" / "history-replay" / "replay-case-registry.md",
               "## Search Coverage\n"
               "| 来源 | 实际命令/查询 | 查询边界 | 候选 | 排除理由 | 停止理由 | 状态 |\n"
               "|---|---|---|---|---|---|---|\n"
               "| repo-a | `git log --all` | all refs through HEAD | 0 | none | exhausted | scanned |\n")
        repo_a = self._make_repo("repo-a")
        repo_b = self._make_repo("repo-b")  # not in registry
        v = _MOD.Verifier(self.home, [repo_a, repo_b], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_repo_scan_missing", codes)

    def test_repo_scan_all_present_passes(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "needs-input"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "evals" / "history-replay" / "replay-case-registry.md",
               "## Search Coverage\n"
               "| 来源 | 实际命令/查询 | 查询边界 | 候选 | 排除理由 | 停止理由 | 状态 |\n"
               "|---|---|---|---|---|---|---|\n"
               "| repo-a | `git log --all` | all refs through HEAD | 0 | none | exhausted | scanned |\n"
               "| repo-b | `git log --all` | all refs through HEAD | 0 | none | exhausted | scanned |\n")
        repo_a = self._make_repo("repo-a")
        repo_b = self._make_repo("repo-b")
        v = _MOD.Verifier(self.home, [repo_a, repo_b], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_repo_scan_missing", codes)

    def test_registry_not_scanned_rows_fail(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "needs-input"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "evals" / "history-replay" / "replay-case-registry.md",
               "## Search Coverage\n"
               "| Repo | Scanned | Candidates Found | Cases Created | Notes | Status | Extra |\n"
               "|---|---|---|---|---|---|---|\n"
               "| repo-a | not-scanned | 0 | 0 | bridge deferred | deferred | not-scanned |\n")
        repo = self._make_repo("repo-a")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_repo_scan_missing", codes)

    def test_not_observed_is_not_an_exact_search_command(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "needs-input"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        _touch(self.home / "evals" / "history-replay" / "replay-case-registry.md",
               "## Search Coverage\n"
               "| 来源 | 实际命令/查询 | 查询边界 | 候选 | 排除理由 | 停止理由 | 状态 |\n"
               "|---|---|---|---|---|---|---|\n"
               "| repo-a | not-observed | all refs | 0 | none | exhausted | scanned |\n")
        repo = self._make_repo("repo-a")
        report = _MOD.Verifier(self.home, [repo], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_repo_scan_missing", codes)

    def test_has_valid_replay_closure_skips_scan_check(self) -> None:
        # Set up a valid replay closure
        case_dir = self.home / "evals" / "history-replay" / "cases" / "case-1"
        case_dir.mkdir(parents=True)
        _touch(case_dir / "history-replay-case.md",
               "Status: ready-for-replay\nEligibility: eligible-direct\nPre-outcome evidence: issue #1234\n")
        run_dir = self.home / "_bootstrap" / "history-replay-runs" / "case-1"
        run_dir.mkdir(parents=True)
        _touch(run_dir / "exit-code", "0")
        _touch(run_dir / "replay-agent.jsonl", '{"action":"test"}')
        _touch(run_dir / "replay-result.md", "result ok")

        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "needs-input", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "needs-input"}})
        _touch(self.home / "bootstrap-state.json", "{}")

        repo = self._make_repo("repo-a")  # not in any registry
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_repo_scan_missing", codes)

    def test_phase12_not_needs_input_skips(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "completed", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "completed"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        repo = self._make_repo("repo-a")  # not in registry
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("history_replay_repo_scan_missing", codes)

    def test_registry_missing_all_repos_fail(self) -> None:
        _touch_json(self.home / "bootstrap-result.json",
                    {"status": "blocked", "paths": {}, "summary": "",
                     "missing_inputs": [], "blockers": [],
                     "phase_summary": {"phase-12-history-replay": "blocked"}})
        _touch(self.home / "bootstrap-state.json", "{}")
        # No registry file at all
        repo = self._make_repo("repo-a")
        v = _MOD.Verifier(self.home, [repo], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("history_replay_repo_scan_missing", codes)


class CaseLeakAnalyzerProvenanceTests(unittest.TestCase):
    """Verbatim-only leak detection: hidden oracle markers, final commit hash, changed path in reconstructed cases."""

    def setUp(self) -> None:
        self.CLA = _MOD.CaseLeakAnalyzer

    # ── structured hidden oracle markers in visible ──

    def test_hidden_oracle_heading_in_visible_fails(self) -> None:
        """'## Hidden Outcome Oracle' heading in visible START → verbatim leak."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "## Hidden Outcome Oracle\nSee details.\n\n"
            "## Hidden Outcome Oracle\n"
            "Commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "## Hidden Outcome Oracle\nSee details.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("hidden_oracle_marker_in_visible", codes)

    def test_actual_changed_surfaces_marker_in_visible_fails(self) -> None:
        """Structured '**Actual changed surfaces**:' field label in visible → verbatim leak."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "- **Actual changed surfaces**: unknown\n\n"
            "## Hidden Outcome Oracle\n"
            "Commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "- **Actual changed surfaces**: unknown\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("hidden_oracle_marker_in_visible", codes)

    # ── final commit hash verbatim in visible ──

    def test_final_commit_hash_verbatim_in_visible_fails(self) -> None:
        """Final commit hash from hidden oracle appears verbatim in visible."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard error. Related to commit abc1234567890def.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234567890def\n"
        )
        reasons = self.CLA.analyze(case_text, "Dashboard error. Related to commit abc1234567890def.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("final_commit_hash_in_visible", codes)

    def test_final_commit_hash_not_in_visible_passes(self) -> None:
        """Final commit hash not present in visible text → no leak."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard error.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234567890def\n"
        )
        reasons = self.CLA.analyze(case_text, "Dashboard error.\n", "")
        codes = {r.code for r in reasons}
        self.assertNotIn("final_commit_hash_in_visible", codes)

    # ── changed path verbatim in visible: reconstructed case ──

    def test_reconstructed_changed_path_verbatim_in_visible_fails(self) -> None:
        """Reconstructed case: hidden oracle changed path appears verbatim in visible."""
        case_text = (
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Issue with src/server/Handler.java.\n\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/server/Handler.java — add null guard\n"
            "Final commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "Issue with src/server/Handler.java.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("changed_path_in_visible", codes)

    # ── direct case: changed path NOT treated as leak ──

    def test_direct_case_changed_path_in_visible_passes(self) -> None:
        """eligible-direct case: same changed path in visible is NOT a leak
        (path may be pre-outcome fact)."""
        case_text = (
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-direct\n\n"
            "## Visible START\n"
            "Issue with src/server/Handler.java.\n\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/server/Handler.java — add null guard\n"
            "Final commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "Issue with src/server/Handler.java.\n", "")
        codes = {r.code for r in reasons}
        self.assertNotIn("changed_path_in_visible", codes)

    # ── natural words / PascalCase / fix verbs: NOT auto-fail ──

    def test_same_domain_words_no_auto_fail(self) -> None:
        """Same business domain words ('dataset', 'handler', 'fix') in START and
        oracle do NOT auto-fail — no verbatim match."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "The dataset handler needs fixing for null input.\n\n"
            "## Hidden Outcome Oracle\n"
            "- src/main/DatasetHandler.java — fix null check\n"
            "Final commit: abc1234\n"
        )
        visible = "The dataset handler needs fixing for null input.\n"
        reasons = self.CLA.analyze(case_text, visible, "")
        # 'dataset', 'handler', 'fix' are common words — no verbatim path match
        self.assertEqual(len(reasons), 0)

    def test_pascal_case_class_name_no_auto_fail(self) -> None:
        """PascalCase class name in both START and oracle without full path → no auto-fail."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "The DataSetRouter class throws an error.\n\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "1. **DataSetRouter.java** — add null guard\n"
            "Final commit: abc1234\n"
        )
        visible = "The DataSetRouter class throws an error.\n"
        reasons = self.CLA.analyze(case_text, visible, "")
        # DataSetRouter is a class name, not a full path → no verbatim path match
        self.assertEqual(len(reasons), 0)

    # ── reconstructed via structured START construction field ──

    def test_start_construction_reconstructed_triggers_path_leak(self) -> None:
        """Structured START construction=reconstructed-from-outcome-subject triggers
        changed path leak check."""
        case_text = (
            "Status: ready-for-replay\n"
            "START construction: reconstructed-from-outcome-subject\n\n"
            "## Visible START\n"
            "Issue with src/server/Handler.java.\n\n"
            "## Hidden Outcome Oracle\n"
            "### Actual Changed Surfaces\n"
            "- src/server/Handler.java — add null guard\n"
            "Final commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "Issue with src/server/Handler.java.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("changed_path_in_visible", codes)

    # ── clean case passes ──

    def test_clean_eligible_reconstructed_passes(self) -> None:
        """Symptom-only reconstructed case with no verbatim leaks passes."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard returns 500 error when date range is empty.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234567890def\n"
            "Changed files:\n"
            "  - src/server/DateFormatUtil.java\n"
            "Actual fix: added null check for empty date range\n"
        )
        visible = "Dashboard returns 500 error when date range is empty.\n"
        reasons = self.CLA.analyze(case_text, visible, "")
        self.assertEqual(len(reasons), 0)

    # ── item 8: new verbatim-leak edge cases ──

    def test_oracle_comparison_heading_not_hidden_section(self) -> None:
        """## Oracle Comparison heading in case is NOT treated as hidden section start."""
        # Only explicit Hidden Outcome Oracle / Hidden Oracle / 隐藏结果 starts hidden section
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Dashboard error.\n\n"
            "## Oracle Comparison\n"
            "This is an oracle comparison section, not a hidden oracle.\n"
            "Commit: abc1234\n"
        )
        reasons = self.CLA.analyze(case_text, "Dashboard error.\n", "")
        # No hidden section to extract → no leaks found
        self.assertEqual(len(reasons), 0,
                         "Oracle Comparison heading must not be treated as hidden oracle")

    def test_final_diff_commit_pointer_field_hash_leak_fails(self) -> None:
        """Final diff / commit pointer field with hash in visible → verbatim leak."""
        case_text = (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Related to commit abc1234567890def.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final diff / commit pointer: abc1234567890def\n"
        )
        reasons = self.CLA.analyze(case_text, "Related to commit abc1234567890def.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("final_commit_hash_in_visible", codes)

    def test_actual_changed_surfaces_inline_path_leak_fails(self) -> None:
        """Inline path in Actual Changed Surfaces subsection → changed-path leak in reconstructed."""
        case_text = (
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Bug in src/server/DateUtil.java reported by users.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: deadbeef1234\n"
            "### Actual Changed Surfaces\n"
            "1. **src/server/DateUtil.java** — add null check\n"
            "2. **src/server/DateUtilTest.java** — add test\n"
        )
        reasons = self.CLA.analyze(case_text, "Bug in src/server/DateUtil.java reported by users.\n", "")
        codes = {r.code for r in reasons}
        self.assertIn("changed_path_in_visible", codes)

    def test_hidden_verification_bullet_path_same_as_visible_no_leak(self) -> None:
        """Path in hidden oracle verification bullet (not in Actual Changed Surfaces) same
        as visible does NOT trigger changed-path leak."""
        case_text = (
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed\n\n"
            "## Visible START\n"
            "Pipeline fails at src/build/verify.sh.\n\n"
            "## Hidden Outcome Oracle\n"
            "Final commit: abc1234\n"
            "### Actual Changed Surfaces\n"
            "1. **src/server/Handler.java** — fix null guard\n"
            "### Verification\n"
            "- src/build/verify.sh — CI pipeline script\n"
        )
        reasons = self.CLA.analyze(case_text, "Pipeline fails at src/build/verify.sh.\n", "")
        codes = {r.code for r in reasons}
        self.assertNotIn("changed_path_in_visible", codes,
                         "verification bullet path outside Actual Changed Surfaces must not trigger path leak")


class EmDashChoiceRegressionTests(unittest.TestCase):
    """Structured choice parser must handle em-dash / en-dash explanations."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "evals" / "history-replay" / "cases" / "case-1").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_em_dash_explanation_passes_preflight(self) -> None:
        """'Eligibility: eligible-reconstructed — reconstructed from symptom'
        must parse as eligible-reconstructed, not be rejected as option list."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file,
            "Status: ready-for-replay\n"
            "Eligibility: eligible-reconstructed — reconstructed from symptom\n"
            "Case validity: valid\n"
            "Readiness: ready\n"
            "Final artifact fully read: yes\n"
            "Final artifact extraction command / pointer: git show abc1234\n"
            "## Visible Packet Fact Closure\n"
            "| Packet File | 事实声明或 narrowing instruction | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
            "| replay-prompt.md | Dashboard returns 500 error | fact-1 | supported |\n"
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Exact Packet Review | Result |\n"
            "|---|---|---|---|\n"
            "| src/main/Foo.java | git show abc | checked replay-prompt.md | absent |\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n"
        )
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # Must not be rejected as case_not_ready or case_ineligible
        self.assertNotIn("preflight_case_ineligible", codes)
        self.assertNotIn("preflight_case_not_ready", codes)

    def test_en_dash_explanation_also_stripped(self) -> None:
        """En dash explanation also stripped: 'eligible-reconstructed – symptom' → eligible-reconstructed."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file,
            "Status: ready-for-replay\n"
            "Replay eligibility: eligible-reconstructed – from symptom\n"
            "Case validity: valid\n"
            "Readiness: ready\n"
            "Final artifact fully read: yes\n"
            "Final artifact extraction command / pointer: git diff abc1234\n"
            "## Visible Packet Fact Closure\n"
            "| Packet File | 声明 | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
            "| replay-prompt.md | Dashboard 500 | fact-1 | supported |\n"
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Packet Review | Result |\n"
            "|---|---|---|---|\n"
            "| src/Foo.java | git diff | checked | absent |\n"
            "## Visible START\nDashboard.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n"
        )
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("preflight_case_ineligible", codes)

    def test_backticked_choice_with_em_dash_explanation_is_parsed(self) -> None:
        value = _MOD.CaseLeakAnalyzer._parse_structured_choice(
            "- **Eligibility**: `eligible-reconstructed` — reconstructed from symptom\n",
            "Eligibility",
        )
        self.assertEqual(value, "eligible-reconstructed")

    def test_parenthetical_choice_explanation_is_parsed(self) -> None:
        value = _MOD.CaseLeakAnalyzer._parse_structured_choice(
            "- **Replay eligibility**: `ineligible-leaky` (commit subject leaks fix area)\n",
            "Replay eligibility",
        )
        self.assertEqual(value, "ineligible-leaky")

    def test_slash_option_list_still_rejected(self) -> None:
        """Value with slash list like 'eligible / ineligible' still rejected as option list."""
        case_file = self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md"
        _touch(case_file,
            "Status: ready-for-replay\n"
            "Eligibility: eligible / ineligible\n"
            "## Visible START\nDashboard.\n"
            "## Hidden Outcome Oracle\nCommit: abc1234\n"
        )
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # Slash option list is caught because eligibility parses as None
        # (not a valid choice), which causes readiness gate failures.
        blocked = bool(codes)
        self.assertTrue(blocked, "slash option list must still be rejected, got empty codes")


class PreflightReadinessTableTests(unittest.TestCase):
    """Phase 12 preflight must require Case Readiness Gate fields and tables."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        (self.home / "evals" / "history-replay" / "cases" / "case-1").mkdir(parents=True)
        (self.home / "_bootstrap" / "history-replay-runs" / "case-1").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _minimal_valid_case(self) -> str:
        return (
            "Status: ready-for-replay\n"
            "Eligibility: eligible-direct\n"
            "Case validity: valid\n"
            "Readiness: ready\n"
            "Final artifact fully read: yes\n"
            "Final artifact extraction command / pointer: git show abc123\n"
            "## Visible Packet Fact Closure\n"
            "| Packet File | 声明 | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
            "| replay-prompt.md | Dashboard error | fact-1 | supported |\n"
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Packet Review | Result |\n"
            "|---|---|---|---|\n"
            "| src/Foo.java | git diff | checked | absent |\n"
            "## Visible START\nDashboard error.\n"
            "## Hidden Outcome Oracle\nCommit: abc123\n"
        )

    def test_missing_case_validity_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace("Case validity: valid\n", "")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_validity_invalid", codes)

    def test_invalid_case_validity_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "Case validity: valid\n", "Case validity: invalid\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_case_validity_invalid", codes)

    def test_readiness_not_ready_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "Readiness: ready\n", "Readiness: not-ready\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_readiness_not_ready", codes)

    def test_final_artifact_not_fully_read_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "Final artifact fully read: yes\n", "Final artifact fully read: no\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_final_artifact_not_fully_read", codes)

    def test_placeholder_extraction_command_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "Final artifact extraction command / pointer: git show abc123\n",
            "Final artifact extraction command / pointer: <placeholder>\n")
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_final_extraction_command_missing", codes)

    def test_empty_packet_fact_closure_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "## Visible Packet Fact Closure\n"
            "| Packet File | 声明 | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
            "| replay-prompt.md | Dashboard error | fact-1 | supported |\n",
            "## Visible Packet Fact Closure\n"
            "| Packet File | 声明 | Supporting Fact ID(s) | Closure Result |\n"
            "|---|---|---|---|\n"
        )
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_packet_fact_closure_empty", codes)

    def test_empty_hidden_facts_excluded_is_blocker(self) -> None:
        case_text = self._minimal_valid_case().replace(
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Packet Review | Result |\n"
            "|---|---|---|---|\n"
            "| src/Foo.java | git diff | checked | absent |\n",
            "## Hidden Facts Excluded From Visible Packet\n"
            "| Hidden Fact | Outcome Evidence | Packet Review | Result |\n"
            "|---|---|---|---|\n"
        )
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md", case_text)
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertIn("preflight_hidden_facts_excluded_empty", codes)

    def test_all_valid_passes_preflight(self) -> None:
        _touch(self.home / "evals" / "history-replay" / "cases" / "case-1" / "history-replay-case.md",
               self._minimal_valid_case())
        v = _MOD.Verifier(self.home, [], run_precheck=False,
                          stage="phase-12-preflight", case_id="case-1")
        codes = {f["code"] for f in v.verify()["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("preflight_case_not_ready", codes)
        self.assertNotIn("preflight_case_ineligible", codes)
        self.assertNotIn("preflight_case_validity_invalid", codes)
        self.assertNotIn("preflight_readiness_not_ready", codes)


class RepoLocalPathAcceptanceTests(unittest.TestCase):
    """Architecture-map and source-of-truth must accept top-level files
    and directories, not just hard-coded path prefixes."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        self.repo = Path(self.td.name) / "test-repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        (self.repo / "skills" / "references").mkdir(parents=True)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _setup_truth_files(self) -> None:
        for f in ["skills/SKILL.md", "skills/references/architecture-map.md",
                   "skills/references/test-entrypoints.md", "skills/references/runtime-and-testability.md",
                   "skills/references/source-of-truth.md"]:
            path = self.repo / f
            path.parent.mkdir(parents=True, exist_ok=True)
            _touch(path, "content")

    def test_pom_xml_accepted_as_repo_relative(self) -> None:
        """Top-level pom.xml backticked in architecture-map should be accepted."""
        self._setup_truth_files()
        (self.repo / "pom.xml").write_text("<project></project>")
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "Main build file is `pom.xml`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "Source root: `pom.xml`")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n| 命令 | 说明 |\n|---|---|\n| mvn compile | compile |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_architecture_unmapped", codes)
        self.assertNotIn("repo_local_source_truth_unmapped", codes)

    def test_readme_md_accepted_as_repo_relative(self) -> None:
        """Top-level README.md as path should be accepted."""
        self._setup_truth_files()
        (self.repo / "README.md").write_text("# README")
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "Root doc: `README.md`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "See [README](README.md)")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test\n```bash\nnpm test\n```\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_architecture_unmapped", codes)
        self.assertNotIn("repo_local_source_truth_unmapped", codes)

    def test_gitlab_ci_yml_accepted(self) -> None:
        """Top-level .gitlab-ci.yml should be accepted."""
        self._setup_truth_files()
        (self.repo / ".gitlab-ci.yml").write_text("stages: [test]")
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "CI config: `.gitlab-ci.yml`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "CI: [config](.gitlab-ci.yml)")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test\n| 命令 | 说明 |\n|---|---|\n| pytest | run tests |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_architecture_unmapped", codes)
        self.assertNotIn("repo_local_source_truth_unmapped", codes)

    def test_directory_accepted(self) -> None:
        """Top-level directory like bootstrap/ should be accepted."""
        self._setup_truth_files()
        (self.repo / "bootstrap").mkdir()
        (self.repo / "service").mkdir()
        (self.repo / "action").mkdir()
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "Boot dir: `bootstrap/`\nService: `service/`\nActions: `action/`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "Source: [bootstrap/](bootstrap/)")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Lint\n`npm run lint`\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_architecture_unmapped", codes)
        self.assertNotIn("repo_local_source_truth_unmapped", codes)

    def test_nonexistent_path_still_blocked(self) -> None:
        """A path that doesn't exist in the repo is still a blocker."""
        self._setup_truth_files()
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "Path: `src/main/nonexistent.java`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "Config: `config/missing.yml`")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n```bash\nmvn compile\n```\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_architecture_unmapped", codes)
        self.assertIn("repo_local_source_truth_unmapped", codes)

    def test_absolute_path_rejected(self) -> None:
        """Absolute paths like /etc/hosts must be rejected."""
        self._setup_truth_files()
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "Path: `/etc/hosts`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "Config: `/usr/local/etc`")
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n```bash\nmake build\n```\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_architecture_unmapped", codes)
        self.assertIn("repo_local_source_truth_unmapped", codes)

    def test_command_like_backtick_is_not_a_path_even_if_file_exists(self) -> None:
        self._setup_truth_files()
        (self.repo / "mvn clean verify").write_text("not a path pointer")
        _touch(self.repo / "skills" / "references" / "architecture-map.md", "`mvn clean verify`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md", "`mvn clean verify`")
        _touch(self.repo / "skills" / "SKILL.md", "**Default branch**: main")
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test\n| Command | Notes |\n|---|---|\n| pytest | tests |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_architecture_unmapped", codes)
        self.assertIn("repo_local_source_truth_unmapped", codes)


class CommandExtractionTests(unittest.TestCase):
    """Build/Test/Lint/Type Check sections must extract commands without tool allowlist."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{},"summary":"","missing_inputs":[],"blockers":[]}')
        _touch(self.home / "bootstrap-state.json", "{}")
        self.repo = Path(self.td.name) / "test-repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        self.truth_files = {}
        for f in ["skills/SKILL.md", "skills/references/architecture-map.md",
                   "skills/references/test-entrypoints.md", "skills/references/runtime-and-testability.md",
                   "skills/references/source-of-truth.md"]:
            path = self.repo / f
            path.parent.mkdir(parents=True, exist_ok=True)
            self.truth_files[f] = path

    def tearDown(self) -> None:
        self.td.cleanup()

    def _fill_minimal_truth(self) -> None:
        _touch(self.repo / "skills" / "SKILL.md",
               "**Default branch**: main\n**Repo role**: backend service\n")
        _touch(self.repo / "skills" / "references" / "architecture-map.md",
               "`src/main/java`")
        _touch(self.repo / "skills" / "references" / "source-of-truth.md",
               "`pom.xml`")
        (self.repo / "src" / "main" / "java").mkdir(parents=True)
        (self.repo / "pom.xml").write_text("<project></project>")

    def test_maven_command_in_table_accepted(self) -> None:
        """Maven package command in a Build section table should be accepted."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n"
               "| 命令 | 说明 |\n"
               "|---|---|\n"
               "| mvn clean package | package the project |\n"
               "| mvn test | run tests |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_test_command_missing", codes)

    def test_arbitrary_npm_docs_command_accepted(self) -> None:
        """An arbitrary npm docs command should be accepted (no tool allowlist)."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n"
               "| Command | Description |\n"
               "|---|---|\n"
               "| npm run docs:build | build documentation |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_test_command_missing", codes)

    def test_playwright_command_in_fenced_block_accepted(self) -> None:
        """Playwright test command in a fenced code block should be accepted."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test\n"
               "```bash\n"
               "npx playwright test\n"
               "npx playwright test --ui\n"
               "```\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_test_command_missing", codes)

    def test_wrapper_command_accepted(self) -> None:
        """Custom wrapper like ./scripts/ci-test.sh should be accepted."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Type Check\n"
               "| Command | Description |\n"
               "|---|---|\n"
               "| ./scripts/typecheck.sh | custom type checker wrapper |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertNotIn("repo_local_test_command_missing", codes)

    def test_placeholder_command_still_rejected(self) -> None:
        """Placeholder commands like <your-build-command> should be rejected."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build\n"
               "| Command | Description |\n"
               "|---|---|\n"
               "| <your-build-command> | placeholder |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)

    def test_no_section_with_commands_is_blocker(self) -> None:
        """Test-entrypoints with no Build/Test/Lint/Type Check section is blocked."""
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Overview\nNo commands here.\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)

    def test_header_only_command_table_is_blocker(self) -> None:
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Build Commands\n| Command | Description |\n|---|---|\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)

    def test_not_observed_command_row_is_blocker(self) -> None:
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test Commands\n| Command | Description |\n|---|---|\n| not-observed | none found |\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)

    def test_comment_only_fenced_block_is_blocker(self) -> None:
        self._fill_minimal_truth()
        _touch(self.repo / "skills" / "references" / "test-entrypoints.md",
               "## Test Commands\n```bash\n# no test command observed\n```\n")
        v = _MOD.Verifier(self.home, [self.repo], run_precheck=False)
        v._verify_repo_local_truth()
        codes = {f.code for f in v.findings if f.severity == "blocker"}
        self.assertIn("repo_local_test_command_missing", codes)


class Phase14CanonicalTableTests(unittest.TestCase):
    """Phase 14 must read only day2-operation.md, parse canonical Install-owned table."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name) / "jarvis"
        (self.home / "_bootstrap").mkdir(parents=True, exist_ok=True)
        _touch(self.home / "README.md", "# Test")
        _touch(self.home / "MAINTENANCE.md", "# Maintenance\nHistory Present Future\nwrite contract\nhistory replay\nsession self-improvement\nprimary-home promotion")
        _touch(self.home / "jarvis.toml", '[project]\nslug = "test"\n[identity]\ncompany = "Test"\n[runtime]\nroot = "/tmp"\ntype = "jarvis-box"\nentry_skill = "skills/test-jarvis/SKILL.md"\n[vcs]\nhost = "gitlab.test.com"\n[bootstrap]\nphase_status_file = "bootstrap-state.json"\nresult_file = "bootstrap-result.json"')
        _touch(self.home / "AGENTS.md", "# AGENTS")
        _touch(self.home / "CLAUDE.md", "# CLAUDE")
        _touch(self.home / ".gitignore", "*~")
        _touch(self.home / "SKILL.md", "# SKILL")
        _touch(self.home / ".github/copilot-instructions.md", "# CI")
        _touch(self.home / "cross-cutting/module-interactions.md", "# MI")
        _touch(self.home / "cross-cutting/peer-product-contracts.md", "# PC")
        _touch(self.home / "cross-cutting/version-changelog.md", "# VC")
        _touch(self.home / "tools/README.md", "# Tools")
        _touch(self.home / "evals/evals.json", "{}")
        (self.home / "references").mkdir(parents=True, exist_ok=True)
        for ref in ["agent-engineering-quality-gate.md", "canonical-repo-fleet.md", "capability-delivery-surfaces.md", "completion-standard.md", "history-replay.md", "issue-claim-normalization.md", "jarvis-box.md", "jarvis-first-routing.md", "minimal-closure-card.md", "module-boundary-routing.md", "next-hop-compression.md", "redaction-rules.md", "repo-pre-push-review-loop.md", "runtime-governance-quick.md", "runtime-governance.md", "verify-evidence-matrix.md", "writeback-governance.md"]:
            _touch(self.home / "references" / ref, "content")
        (self.home / "skills" / "test-jarvis").mkdir(parents=True, exist_ok=True)
        _touch(self.home / "skills" / "test-jarvis" / "SKILL.md", "runtime-governance-quick.md\nworkflow-first\nartifact-first\nrepo-local execution truth\ncapability delivery\nEND writeback")
        (self.home / "modules" / "test-mod").mkdir(parents=True, exist_ok=True)
        for f in ["overview.md", "known-issues.md", "decisions.md", "rejected-features.md", "test-coverage.md"]:
            _touch(self.home / "modules" / "test-mod" / f, "evidence confirmed\nmodule overview content")
        (self.home / "sources" / "test-source").mkdir(parents=True, exist_ok=True)
        _touch(self.home / "sources" / "test-source" / "README.md", "source route")
        _touch(self.home / "bootstrap-result.json",
               '{"status":"completed","paths":{"jarvis_home":"/tmp","jarvis_target_home":"/tmp","entry_skill":"skills/test-jarvis/SKILL.md"},"summary":"","missing_inputs":[],"blockers":[],'
               '"phase_summary":{"phase-12-history-replay":"completed","phase-14-day2-operation":"completed"}}')
        _touch(self.home / "bootstrap-state.json", '{"status":"completed","phase":"phase-14","paths":{"entry_skill":"skills/test-jarvis/SKILL.md"},"confirmed_answers":{},"method_repo":{},"phase_status":{"phase-12-history-replay":"completed","phase-14-day2-operation":"completed"},"identity_reconciliation":{"status":"confirmed"}}')
    def tearDown(self) -> None:
        self.td.cleanup()

    def _canonical_day2(self, extra: str = "") -> str:
        return ("## Install-owned Capability Status\n\n"
                "| 能力 | Install/Authority 证据 | 观测当前状态 | 最近执行证据 | Readiness | Owner & Recovery |\n"
                "|---|---|---|---|---|---|\n"
                "| service lifecycle | install-state.json | stopped | unexercised | ready-with-explicit-alternative | e2e-owner |\n"
                "| agent registry / routing / failover | agent list --check | working | probe-success | ready | e2e-owner |\n"
                "| Task lifecycle | CLI help | zero tasks | unexercised | ready-with-explicit-alternative | e2e-owner |\n"
                "| runtime sync | env file | synced | recent-sync | ready | e2e-owner |\n"
                "| Jarvis maintenance launcher | binary exists | available | unexercised | ready | e2e-owner |\n"
                "| session self-improvement | script exists | available | unexercised | ready | e2e-owner |\n"
                "| workspace cleanup | reap --help | available | unexercised | ready | e2e-owner |\n\n"
                + extra)

    def test_all_seven_capabilities_present_passes(self) -> None:
        day2 = self._canonical_day2(
            "## Runtime Agent Prompt Probe\n\n"
            "- **真实 prompt probe invocation**: `claude -p 'hello'`\n"
            "- **真实 prompt probe evidence**: exit 0, response OK\n\n"
            "## Cross-Artifact Consistency Review\n\n"
            "| 产物 | 状态摘要 | 与根 state 一致？ | 备注 |\n"
            "|---|---|---|---|\n"
            "| MAINTENANCE.md | current | yes | |\n"
            "| bootstrap-state.json | completed | yes | |\n\n"
            "- **一致性审查通过**: yes\n"
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertNotIn("day2_required_capability_row_missing", codes)
        self.assertNotIn("day2_capability_not_ready", codes)
        self.assertNotIn("day2_capability_cell_placeholder", codes)

    def test_missing_capability_row_is_blocker(self) -> None:
        day2 = self._canonical_day2().replace(
            "| workspace cleanup | reap --help | available | unexercised | ready | e2e-owner |\n", "")
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_required_capability_row_missing", codes)

    def test_unverified_readiness_is_blocker_when_completed(self) -> None:
        day2 = self._canonical_day2().replace(
            "| ready | e2e-owner |\n",
            "| unverified | e2e-owner |\n",
            2,  # second occurrence
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_capability_not_ready", codes)

    def test_missing_prompt_probe_invocation_is_blocker(self) -> None:
        day2 = self._canonical_day2(
            "## Runtime Agent Prompt Probe\n\n"
            "- **真实 prompt probe invocation**: <placeholder>\n"
            "- **真实 prompt probe evidence**: exit 0\n\n"
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_prompt_probe_invocation_missing", codes)

    def test_missing_cross_artifact_consistency_is_blocker(self) -> None:
        day2 = self._canonical_day2(
            "## Runtime Agent Prompt Probe\n\n"
            "- **真实 prompt probe invocation**: `claude -p 'hello'`\n"
            "- **真实 prompt probe evidence**: exit 0, response OK\n\n"
            "## Cross-Artifact Consistency Review\n\n"
            "- **一致性审查通过**: no\n"
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_cross_artifact_consistency_not_passed", codes)

    def test_phase14_not_completed_allows_unverified(self) -> None:
        """When Phase 14 is not completed, readiness tokens are checked but unverified is not forced."""
        # Override both result.json and state.json to not have Phase 14 completed
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{"jarvis_home":"/tmp","jarvis_target_home":"/tmp","entry_skill":"skills/test-jarvis/SKILL.md"},'
               '"summary":"","missing_inputs":[],"blockers":[],'
               '"phase_summary":{"phase-12-history-replay":"completed","phase-14-day2-operation":"needs-input"}}')
        _touch(self.home / "bootstrap-state.json",
               '{"status":"needs-input","phase":"phase-14","paths":{"entry_skill":"skills/test-jarvis/SKILL.md"},'
               '"confirmed_answers":{},"method_repo":{},"identity_reconciliation":{"status":"confirmed"},'
               '"phase_status":{"phase-12-history-replay":"completed","phase-14-day2-operation":"needs-input"}}')
        day2 = self._canonical_day2().replace(
            "| ready | e2e-owner |\n",
            "| unverified | e2e-owner |\n",
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        # Not completed, so unverified readiness is not a blocker
        self.assertNotIn("day2_capability_not_ready", codes)

    def test_malformed_readiness_still_rejected_when_not_completed(self) -> None:
        """Even when Phase 14 is not completed, malformed explicit readiness tokens are rejected."""
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{"jarvis_home":"/tmp","jarvis_target_home":"/tmp","entry_skill":"skills/test-jarvis/SKILL.md"},'
               '"summary":"","missing_inputs":[],"blockers":[],'
               '"phase_summary":{"phase-12-history-replay":"completed","phase-14-day2-operation":"needs-input"}}')
        _touch(self.home / "bootstrap-state.json",
               '{"status":"needs-input","phase":"phase-14","paths":{"entry_skill":"skills/test-jarvis/SKILL.md"},'
               '"confirmed_answers":{},"method_repo":{},"identity_reconciliation":{"status":"confirmed"},'
               '"phase_status":{"phase-12-history-replay":"completed","phase-14-day2-operation":"needs-input"}}')
        day2 = self._canonical_day2().replace(
            "| ready | e2e-owner |\n",
            "| configured | e2e-owner |\n",
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        v = _MOD.Verifier(self.home, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_capability_readiness_invalid", codes)

    def test_arbitrary_readiness_is_blocker_when_completed(self) -> None:
        day2 = self._canonical_day2().replace(
            "| ready | e2e-owner |\n",
            "| configured | e2e-owner |\n",
            1,
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        report = _MOD.Verifier(self.home, [], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_capability_not_ready", codes)

    def test_extra_capability_row_is_blocker_when_completed(self) -> None:
        day2 = self._canonical_day2().replace(
            "| workspace cleanup | reap --help | available | unexercised | ready | e2e-owner |\n",
            "| workspace cleanup | reap --help | available | unexercised | ready | e2e-owner |\n"
            "| invented capability | artifact | available | probe | ready | e2e-owner |\n",
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        report = _MOD.Verifier(self.home, [], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_capability_row_set_invalid", codes)

    def test_unexercised_is_not_a_readiness_token(self) -> None:
        _touch(self.home / "bootstrap-result.json",
               '{"status":"needs-input","paths":{},"summary":"","missing_inputs":[],"blockers":[],'
               '"phase_summary":{"phase-14-day2-operation":"needs-input"}}')
        _touch(self.home / "bootstrap-state.json",
               '{"status":"needs-input","phase_status":{"phase-14-day2-operation":"needs-input"}}')
        day2 = self._canonical_day2().replace(
            "| ready | e2e-owner |\n", "| unexercised | e2e-owner |\n", 1
        )
        _touch(self.home / "_bootstrap" / "day2-operation.md", day2)
        report = _MOD.Verifier(self.home, [], run_precheck=False).verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("day2_capability_readiness_invalid", codes)


if __name__ == "__main__":
    unittest.main()
