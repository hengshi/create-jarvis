#!/usr/bin/env python3
"""Cross-surface contract tests for formal runtime onboarding."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
METHOD_SURFACES = (
    "README.md",
    "SKILL.md",
    "acceptance.md",
    "e2e/README.md",
    "playbooks/prompts/formal-runtime-deployment.md",
    "playbooks/runtime-method-contract.md",
)


class RuntimeDeploymentContractTests(unittest.TestCase):
    def test_method_surfaces_share_one_native_docker_contract(self) -> None:
        for relative in METHOD_SURFACES:
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(path=relative):
                self.assertIn("Native", text)
                self.assertIn("Docker", text)

        combined = "\n".join(
            (REPO_ROOT / relative).read_text(encoding="utf-8")
            for relative in METHOD_SURFACES
        )
        for obsolete in (
            "company-context.json",
            "deployment-lock.json",
            "container-side probes",
            "separate formal identity",
            "独立正式身份",
            "~/.hengshi",
        ):
            self.assertNotIn(obsolete, combined)

    def test_part_four_delegates_operations_to_public_release(self) -> None:
        prompt = (
            REPO_ROOT / "playbooks" / "prompts" / "formal-runtime-deployment.md"
        ).read_text(encoding="utf-8")
        for required in (
            "public release",
            "runtime owner",
            "actual runtime root",
            "credential",
            "writeback",
            "cleanup",
        ):
            self.assertIn(required, prompt)
        for copied_implementation in (
            "compose.yaml",
            "deployment.env",
            "runtime.env",
            "connector.env",
        ):
            self.assertNotIn(copied_implementation, prompt)


if __name__ == "__main__":
    unittest.main()
