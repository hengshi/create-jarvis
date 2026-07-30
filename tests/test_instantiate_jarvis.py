#!/usr/bin/env python3
"""Behavior tests for deterministic Jarvis template rendering."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTANTIATOR = REPO_ROOT / "scripts" / "instantiate_jarvis.py"
INPUT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "acme-jarvis-render-input.json"


class JarvisInstantiationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(INPUT_FIXTURE.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="jarvis-")
        self.root = Path(self.temp.name)
        self.home = self.root / "acme-jarvis"
        self.input_path = self.root / "construction-input.json"
        self.write_input()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_input(self, mutate=None) -> dict:
        value = copy.deepcopy(self.fixture)
        value["paths"]["target"] = str(self.home)
        value["paths"]["workspace_root"] = str(self.root)
        if mutate:
            mutate(value)
        self.input_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return value

    def run_instantiator(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(INSTANTIATOR), *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def run_base(self) -> subprocess.CompletedProcess:
        return self.run_instantiator("base", "--input", str(self.input_path))

    @staticmethod
    def frontmatter_name(path: Path) -> str | None:
        match = re.search(r"(?m)^name:\s*([^\n]+)$", path.read_text(encoding="utf-8"))
        return match.group(1).strip() if match else None

    def test_base_creates_jarvis_owned_shape_without_runtime_state(self) -> None:
        completed = self.run_base()
        self.assertEqual(completed.returncode, 0, completed.stderr)

        required = {
            "README.md",
            "MAINTENANCE.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".github/copilot-instructions.md",
            ".gitignore",
            "SKILL.md",
            "references/canonical-repo-fleet.md",
            "references/runtime-governance.md",
            "references/runtime-governance-quick.md",
            "tools/README.md",
            "skills/acme-claude-e2e-jarvis/SKILL.md",
            "skills/acme-claude-e2e-workflow-issue-post-check/SKILL.md",
            "skills/acme-claude-e2e-workflow-bugfix-loop/SKILL.md",
            "skills/acme-claude-e2e-workflow-feature-delivery/SKILL.md",
        }
        self.assertEqual(
            sorted(relative for relative in required if not (self.home / relative).is_file()),
            [],
        )
        obsolete = ("jarvis.toml", "bootstrap-state.json", "bootstrap-result.json")
        self.assertEqual([name for name in obsolete if (self.home / name).exists()], [])

    def test_repeat_preserves_jarvis_owned_edits(self) -> None:
        self.assertEqual(self.run_base().returncode, 0)
        readme = self.home / "README.md"
        edited = readme.read_text(encoding="utf-8") + "\nJarvis-owned note\n"
        readme.write_text(edited, encoding="utf-8")
        second = self.run_base()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(readme.read_text(encoding="utf-8"), edited)

    def test_repeat_without_edits_is_byte_stable(self) -> None:
        self.assertEqual(self.run_base().returncode, 0)
        before = {
            path.relative_to(self.home): path.read_bytes()
            for path in self.home.rglob("*")
            if path.is_file()
        }
        self.assertEqual(self.run_base().returncode, 0)
        after = {
            path.relative_to(self.home): path.read_bytes()
            for path in self.home.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_late_jarvis_discovery_updates_navigation(self) -> None:
        def remove_scopes(value: dict) -> None:
            for key in ("modules", "sources", "workflows"):
                value["scope"].pop(key, None)

        self.write_input(remove_scopes)
        self.assertEqual(self.run_base().returncode, 0)
        commands = (
            ("module", "--input", str(self.input_path), "--name", "analytics"),
            ("source", "--input", str(self.input_path), "--name", "docs"),
            (
                "package",
                "--input",
                str(self.input_path),
                "--kind",
                "generic-workflow",
                "--name",
                "acme-claude-e2e-workflow-issue-loop",
            ),
        )
        for command in commands:
            completed = self.run_instantiator(*command)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        readme = (self.home / "README.md").read_text(encoding="utf-8")
        for route in (
            "modules/analytics/overview.md",
            "sources/docs/README.md",
            "skills/acme-claude-e2e-workflow-issue-loop/SKILL.md",
        ):
            self.assertIn(route, readme)

    def test_generated_tree_has_no_unrendered_or_reference_jarvis_tokens(self) -> None:
        completed = self.run_base()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        forbidden = (
            "{{",
            "HENGSHI",
            "hengshi",
            "henglabs",
            "gitlab.hengshi.org",
            "~/.hengshi",
            "Part 1",
            "Part 2",
            "Part 3",
            "Part 4",
            "Reconciliation Gate",
            "Repository learning",
        )
        violations: list[str] = []
        for path in self.home.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".sh"}:
                continue
            text = path.read_text(encoding="utf-8")
            violations.extend(
                f"{path.relative_to(self.home)}: {token}"
                for token in forbidden
                if token in text
            )
        self.assertEqual(violations, [])

    def test_module_and_source_preserve_confirmed_names(self) -> None:
        self.assertEqual(self.run_base().returncode, 0)
        module = self.run_instantiator(
            "module", "--input", str(self.input_path), "--name", "HQL"
        )
        source = self.run_instantiator(
            "source", "--input", str(self.input_path), "--name", "customer-docs"
        )
        self.assertEqual(module.returncode, 0, module.stderr)
        self.assertEqual(source.returncode, 0, source.stderr)
        self.assertTrue((self.home / "modules" / "HQL" / "overview.md").is_file())
        self.assertTrue((self.home / "sources" / "customer-docs" / "README.md").is_file())
        self.assertFalse((self.home / "sources" / "customer-docs" / "SKILL.md").exists())

    def test_extension_packages_use_jarvis_namespace(self) -> None:
        self.assertEqual(self.run_base().returncode, 0)
        for kind, name in (
            ("generic-workflow", "acme-claude-e2e-workflow-customer-deploy"),
            ("generic-source", "acme-claude-e2e-customer-docs"),
        ):
            completed = self.run_instantiator(
                "package", "--input", str(self.input_path), "--kind", kind, "--name", name
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(
                self.frontmatter_name(self.home / "skills" / name / "SKILL.md"),
                name,
            )

    def test_names_and_targets_cannot_escape_workspace(self) -> None:
        for name in ("../escape", "nested/name", ".", ".."):
            completed = self.run_instantiator(
                "module", "--input", str(self.input_path), "--name", name
            )
            self.assertNotEqual(completed.returncode, 0)
        self.assertFalse((self.root / "escape").exists())

        workspace = self.root / "allowed"
        workspace.mkdir()
        outside = self.root / "outside" / "jarvis"

        def escape(value: dict) -> None:
            value["paths"]["workspace_root"] = str(workspace)
            value["paths"]["target"] = str(outside)

        self.write_input(escape)
        self.assertNotEqual(self.run_base().returncode, 0)
        self.assertFalse(outside.exists())

    def test_unsafe_slug_fails_before_writing(self) -> None:
        def wrong_entry(value: dict) -> None:
            value["jarvis"]["slug"] = "../another-jarvis"

        self.write_input(wrong_entry)
        self.assertNotEqual(self.run_base().returncode, 0)
        self.assertFalse(self.home.exists())

    def test_render_preflight_fails_without_partial_output(self) -> None:
        spec = importlib.util.spec_from_file_location("instantiate_jarvis", INSTANTIATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        template = self.root / "bad-template"
        (template / "sub").mkdir(parents=True)
        (template / "README.md").write_text("{{UNKNOWN_TOKEN}}\n", encoding="utf-8")
        (template / "sub" / "ok.md").write_text("ok\n", encoding="utf-8")
        target = self.root / "target"
        result = module.copy_and_render(template, target, {})
        self.assertTrue(result["errors"])
        self.assertFalse(target.exists())

    def test_missing_purpose_remains_explicitly_unresolved(self) -> None:
        def mutate(value: dict) -> None:
            value["jarvis"].pop("purpose")

        self.write_input(mutate)
        completed = self.run_base()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "UNRESOLVED — establish from customer evidence",
            (self.home / "README.md").read_text(encoding="utf-8"),
        )

    def test_non_string_purpose_fails_cleanly(self) -> None:
        def mutate(value: dict) -> None:
            value["jarvis"]["purpose"] = {"name": "Acme Analytics"}

        self.write_input(mutate)
        completed = self.run_base()
        self.assertNotEqual(completed.returncode, 0)
        self.assertNotRegex(completed.stderr, r"Traceback")
        self.assertFalse(self.home.exists())


if __name__ == "__main__":
    unittest.main()
