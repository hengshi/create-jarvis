#!/usr/bin/env python3
"""Behavior tests for Construction Workspace instantiation and verification."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTANTIATOR = REPO_ROOT / "scripts" / "instantiate_construction_workspace.py"
VERIFIER = REPO_ROOT / "scripts" / "verify_construction_workspace.py"
METHOD_COMMIT = subprocess.run(
    ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
CREATED_AT = "2026-07-30T10:00:00+00:00"


class ConstructionWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="construction-workspace-")
        self.root = Path(self.temp.name)
        self.workspace = self.root / "jarvis-build"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def init(self) -> subprocess.CompletedProcess:
        return self.run_script(
            INSTANTIATOR,
            "init",
            "--workspace",
            str(self.workspace),
            "--method-repository",
            str(REPO_ROOT),
            "--method-commit",
            METHOD_COMMIT,
            "--coordinator",
            "test Host Agent",
            "--created-at",
            CREATED_AT,
        )

    def add_repo(self, name: str = "acme-api") -> subprocess.CompletedProcess:
        return self.run_script(
            INSTANTIATOR,
            "add-repository",
            "--workspace",
            str(self.workspace),
            "--name",
            name,
            "--repository",
            "https://git.example.test/acme/api.git",
            "--history-range",
            "2025-08-01..2026-07-30",
            "--delivery-policy",
            "branch-review",
            "--target-workspace",
            str(self.root / "worktrees" / "acme-api"),
            "--target-branch",
            "create-jarvis/repo-learning-acme-api",
            "--added-at",
            CREATED_AT,
        )

    def verify(self, *args: str) -> tuple[subprocess.CompletedProcess, dict]:
        completed = self.run_script(
            VERIFIER,
            "--workspace",
            str(self.workspace),
            *args,
        )
        return completed, json.loads(completed.stdout)

    def test_init_creates_recoverable_workspace_that_verifies(self) -> None:
        completed = self.init()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertFalse(
            (self.workspace / "work" / "repositories" / "REPOSITORY-WORK-CARD.md").exists()
        )
        continuation = (self.workspace / "CONTINUE-JARVIS.md").read_text(encoding="utf-8")
        self.assertIn(str(self.workspace), continuation)
        self.assertIn(str(REPO_ROOT), continuation)
        self.assertNotIn("{{", continuation)
        verified, report = self.verify()
        self.assertEqual(verified.returncode, 0, verified.stdout)
        self.assertEqual(report["status"], "pass", report)
        onboarding = (self.workspace / "work" / "jarvis-box-onboarding.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Selected deployment mode: `unresolved`", onboarding)
        self.assertIn("Native", onboarding)
        self.assertIn("Docker", onboarding)
        self.assertNotIn("container-side probes", onboarding)

    def test_init_refuses_to_overwrite_existing_workspace(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        note = self.workspace / "customer-note.md"
        note.write_text("preserve me\n", encoding="utf-8")
        repeated = self.init()
        self.assertNotEqual(repeated.returncode, 0)
        self.assertEqual(note.read_text(encoding="utf-8"), "preserve me\n")

    def test_init_rejects_commit_that_is_not_in_method_checkout(self) -> None:
        completed = self.run_script(
            INSTANTIATOR,
            "init",
            "--workspace",
            str(self.workspace),
            "--method-repository",
            str(REPO_ROOT),
            "--method-commit",
            "b" * 40,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("method commit is not available", completed.stderr)
        self.assertFalse(self.workspace.exists())

    def test_add_repository_creates_and_indexes_one_independent_card(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        added = self.add_repo()
        self.assertEqual(added.returncode, 0, added.stderr)
        card = self.workspace / "work" / "repositories" / "acme-api.md"
        self.assertTrue(card.is_file())
        self.assertIn(
            "https://git.example.test/acme/api.git",
            card.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "| acme-api | https://git.example.test/acme/api.git |",
            (self.workspace / "BUILD-CONTEXT.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "| `work/repositories/acme-api.md` |",
            (self.workspace / "CONSTRUCTION-JOURNAL.md").read_text(encoding="utf-8"),
        )
        verified, report = self.verify()
        self.assertEqual(verified.returncode, 0, verified.stdout)
        self.assertEqual(report["repository_card_count"], 1)

        duplicate = self.add_repo()
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual(
            (self.workspace / "CONSTRUCTION-JOURNAL.md")
            .read_text(encoding="utf-8")
            .count("work/repositories/acme-api.md"),
            1,
        )

    def test_repository_name_cannot_escape_workspace(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        escaped = self.add_repo("../outside")
        self.assertNotEqual(escaped.returncode, 0)
        self.assertFalse((self.root / "outside.md").exists())

    def test_verifier_rejects_stale_repository_indexes(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        self.assertEqual(self.add_repo().returncode, 0)
        (self.workspace / "work" / "repositories" / "acme-api.md").unlink()
        completed, report = self.verify()
        self.assertEqual(completed.returncode, 1)
        self.assertIn(
            "repository_index_mismatch",
            {finding["code"] for finding in report["findings"]},
        )

    def test_verifier_rejects_pointer_drift_tokens_and_symlinks(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        continuation = self.workspace / "CONTINUE-JARVIS.md"
        continuation.write_text(
            continuation.read_text(encoding="utf-8").replace(
                str(self.workspace), str(self.root / "other"), 1
            )
            + "\n- Owner: {{OWNER}}\n",
            encoding="utf-8",
        )
        os.symlink(
            self.workspace / "BUILD-CONTEXT.md",
            self.workspace / "linked-context.md",
        )
        completed, report = self.verify()
        self.assertEqual(completed.returncode, 1)
        codes = {finding["code"] for finding in report["findings"]}
        self.assertTrue(
            {"workspace_pointer_mismatch", "template_token_unresolved", "symlink_not_allowed"}
            <= codes,
            report,
        )

    def test_dispatch_ready_mode_distinguishes_intake_from_structure(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        structural, structural_report = self.verify()
        self.assertEqual(structural.returncode, 0, structural_report)
        dispatch, dispatch_report = self.verify("--require-dispatch-ready")
        self.assertEqual(dispatch.returncode, 1)
        self.assertIn(
            "dispatch_fact_unresolved",
            {finding["code"] for finding in dispatch_report["findings"]},
        )


if __name__ == "__main__":
    unittest.main()
