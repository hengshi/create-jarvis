#!/usr/bin/env python3
"""Black-box behavior tests for deterministic output verification."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_SCRIPT = REPO_ROOT / "scripts" / "verify_company_output.py"
INSTANTIATOR = REPO_ROOT / "scripts" / "instantiate_company_jarvis.py"
INPUT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "acme-company-render-input.json"

SPEC = importlib.util.spec_from_file_location("verify_company_output", VERIFIER_SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["verify_company_output"] = MODULE
SPEC.loader.exec_module(MODULE)
Verifier = MODULE.Verifier


class VerifierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "acme-jarvis"
        value = json.loads(INPUT_FIXTURE.read_text(encoding="utf-8"))
        value["paths"]["target"] = str(self.home)
        value["paths"]["workspace_root"] = str(self.root)
        self.input_path = self.root / "construction-input.json"
        self.write_json(self.input_path, value)
        completed = subprocess.run(
            [sys.executable, str(INSTANTIATOR), "base", "--input", str(self.input_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def report(self, **kwargs) -> dict:
        return Verifier(self.home, [], run_precheck=False, **kwargs).verify()

    @staticmethod
    def finding_codes(report: dict) -> list[str]:
        return [finding["code"] for finding in report["findings"]]

    def assert_finding(self, report: dict, code: str) -> None:
        self.assertIn(code, self.finding_codes(report), report)

    def test_generated_base_satisfies_structural_contract(self) -> None:
        report = self.report(expected_company_slug="acme-claude-e2e")
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["findings"], [])

    def test_missing_home_and_entry_fail_closed(self) -> None:
        missing = Verifier(self.root / "missing", [], run_precheck=False).verify()
        self.assert_finding(missing, "jarvis_home_missing")
        shutil.rmtree(self.home / "skills" / "acme-claude-e2e-jarvis")
        self.assert_finding(
            self.report(expected_company_slug="acme-claude-e2e"),
            "company_entry_missing",
        )

    def test_obsolete_runtime_contracts_are_rejected(self) -> None:
        for name in ("jarvis.toml", "bootstrap-state.json", "bootstrap-result.json"):
            (self.home / name).write_text("obsolete\n", encoding="utf-8")
        findings = [
            finding
            for finding in self.report()["findings"]
            if finding["code"] == "obsolete_contract_present"
        ]
        self.assertEqual(len(findings), 3)

    def test_runtime_owned_skill_copies_are_rejected(self) -> None:
        for name in ("skill-creator", "ponytail", "jarvis-box-doctor"):
            path = self.home / "skills" / name / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text("runtime-owned\n", encoding="utf-8")
        findings = [
            finding
            for finding in self.report()["findings"]
            if finding["code"] == "runtime_skill_copied"
        ]
        self.assertEqual(len(findings), 3)

    def test_declared_expected_outputs_must_exist(self) -> None:
        report = self.report(
            expected_modules=["missing-module"],
            expected_sources=["missing-source"],
            expected_skills=["missing-skill"],
        )
        self.assert_finding(report, "expected_module_missing")
        self.assert_finding(report, "expected_source_missing")
        self.assert_finding(report, "expected_skill_missing")

    def make_repo(self, name: str = "customer-repo") -> Path:
        repo = self.root / name
        (repo / ".git").mkdir(parents=True)
        return repo

    def test_repo_without_fixed_skill_skeleton_is_valid(self) -> None:
        repo = self.make_repo()
        report = Verifier(self.home, [repo], run_precheck=False).verify()
        self.assertEqual(report["status"], "pass", report)

    def test_eval_loop_skill_is_rejected(self) -> None:
        repo = self.make_repo()
        legacy = repo / "skills" / "eval-loop.md"
        legacy.parent.mkdir()
        legacy.write_text("method loop\n", encoding="utf-8")
        report = Verifier(self.home, [repo], run_precheck=False).verify()
        self.assert_finding(report, "legacy_eval_loop_skill_present")

    def test_discovered_repo_precheck_is_executed(self) -> None:
        repo = self.make_repo()
        precheck = repo / "skills" / "repo-guidance" / "scripts" / "precheck.sh"
        precheck.parent.mkdir(parents=True)
        precheck.write_text("#!/usr/bin/env bash\nexit 7\n", encoding="utf-8")
        report = Verifier(self.home, [repo], run_precheck=True).verify()
        self.assert_finding(report, "repo_precheck_failed")

    def test_filesystem_safety_checks_generated_surfaces(self) -> None:
        os.symlink(self.home / "README.md", self.home / "linked-readme.md")
        (self.home / "leak.env").write_text(
            "api_key=0123456789abcdef\n", encoding="utf-8"
        )
        (self.home / "unfinished.md").write_text(
            "owner: {{OWNER_NAME}}\n", encoding="utf-8"
        )
        unresolved = self.home / "skills" / "__COMPANY_SLUG__-jarvis"
        unresolved.mkdir()
        report = self.report()
        for code in (
            "symlink_not_allowed",
            "secret_exposure",
            "template_token_unresolved",
            "template_path_unresolved",
        ):
            self.assert_finding(report, code)

    def test_program_identifier_is_not_mistaken_for_template(self) -> None:
        (self.home / "debug-contract.md").write_text(
            "Use window.__HST_DEBUG__ for the observed bridge.\n",
            encoding="utf-8",
        )
        self.assertEqual(self.report()["status"], "pass")

    def test_cli_returns_failure_and_writes_reports(self) -> None:
        (self.home / "README.md").unlink()
        report_json = self.root / "report.json"
        report_md = self.root / "report.md"
        completed = subprocess.run(
            [
                sys.executable,
                str(VERIFIER_SCRIPT),
                "--jarvis-home",
                str(self.home),
                "--skip-precheck",
                "--report-json",
                str(report_json),
                "--report-md",
                str(report_md),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertEqual(json.loads(report_json.read_text(encoding="utf-8"))["status"], "fail")
        self.assertTrue(report_md.is_file())


if __name__ == "__main__":
    unittest.main()
