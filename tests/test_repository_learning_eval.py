#!/usr/bin/env python3
"""Behavior tests for the repository-learning logic-loop eval fixture."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER = REPO_ROOT / "evals" / "fixtures" / "build_customer_journey_fixture.py"
VERIFIER_SPEC = importlib.util.spec_from_file_location(
    "verify_eval_artifacts", REPO_ROOT / "evals" / "verify_eval_artifacts.py"
)
assert VERIFIER_SPEC and VERIFIER_SPEC.loader
VERIFIER = importlib.util.module_from_spec(VERIFIER_SPEC)
VERIFIER_SPEC.loader.exec_module(VERIFIER)


class RepositoryLearningEvalTests(unittest.TestCase):
    def test_skill_trigger_accepts_plain_and_folded_descriptions(self) -> None:
        self.assertTrue(
            VERIFIER.skill_description_has_use(
                "---\nname: focused-loop\ndescription: Use when retries arrive.\n---\n"
            )
        )
        self.assertTrue(
            VERIFIER.skill_description_has_use(
                "---\nname: focused-loop\ndescription: >\n  Handle retries. Use when duplicates arrive.\n---\n"
            )
        )
        self.assertFalse(
            VERIFIER.skill_description_has_use(
                "---\nname: focused-loop\ndescription: Handle retries.\n---\n"
            )
        )

    def test_fixture_contains_replay_loops_and_an_unprompted_current_capability(self) -> None:
        with tempfile.TemporaryDirectory(prefix="repository-learning-eval-") as temp:
            output = Path(temp) / "customer-fixture"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--case",
                    "repository-learning-worker",
                    "--output",
                    str(output),
                    "--method-repository",
                    str(REPO_ROOT),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            manifest = json.loads((output / "fixture-manifest.json").read_text())
            history = manifest["history"]

            self.assertEqual(
                set(history),
                {
                    "baseline",
                    "webhook_vulnerable",
                    "webhook_fixed",
                    "lifecycle_vulnerable",
                    "lifecycle_fixed",
                    "audit_export",
                    "head",
                },
            )
            self.assertEqual(len(set(history.values())), 7)

            repo = Path(manifest["repository"])
            commit_count = subprocess.run(
                ["git", "-C", str(repo), "rev-list", "--all", "--count"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self.assertEqual(commit_count, "7")
            self.assertTrue((repo / "invoice_service" / "webhooks.py").is_file())
            self.assertTrue((repo / "invoice_service" / "lifecycle.py").is_file())
            self.assertTrue((repo / "invoice_service" / "audit.py").is_file())

            brief = (output / "customer-input" / "customer-brief.md").read_text()
            self.assertIn("ACME-17", brief)
            self.assertIn("ACME-18", brief)
            self.assertIn("logic loops", brief)
            self.assertIn("cross-loop route", brief)
            self.assertNotIn("audit", brief.lower())
            self.assertTrue(
                (output / "customer-input" / "replay_duplicate_webhook.py").is_file()
            )
            self.assertTrue(
                (output / "customer-input" / "replay_invoice_lifecycle.py").is_file()
            )

            status = subprocess.run(
                ["git", "-C", str(repo), "status", "--short"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            self.assertIn("CUSTOMER-NOTE.md", status)


if __name__ == "__main__":
    unittest.main()
