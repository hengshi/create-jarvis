#!/usr/bin/env python3
"""Tests for deterministic repo-local skill instantiator."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
INSTANTIATOR = SCRIPTS_DIR / "instantiate_repo_local_skill.py"


def _load_module():
    """Load the instantiator as a module for direct function testing."""
    spec = importlib.util.spec_from_file_location(
        "instantiate_repo_local_skill", INSTANTIATOR
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestInstantiateRepoLocalSkill(unittest.TestCase):
    """Repo-local skill instantiator tests."""

    @classmethod
    def setUpClass(cls):
        if not INSTANTIATOR.is_file():
            raise unittest.SkipTest("instantiator script not found")

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(
            ["git", "init"],
            cwd=self.tmpdir,
            capture_output=True,
            check=True,
            timeout=10,
        )

    def tearDown(self):
        if self.tmpdir.exists():
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(INSTANTIATOR)] + list(args),
            capture_output=True,
            text=True,
            timeout=30,
        )

    # ── CLI tests ─────────────────────────────────────────────────

    def test_creates_canonical_10_files_with_repo_flag(self):
        """Creates all 10 canonical files using --repo and explicit --repo-name."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

        expected = [
            "skills/SKILL.md",
            "skills/code-review/SKILL.md",
            "skills/code-review/scripts/precheck.sh",
            "skills/eval-loop.md",
            "skills/references/source-of-truth.md",
            "skills/references/architecture-map.md",
            "skills/references/test-entrypoints.md",
            "skills/references/runtime-and-testability.md",
            "skills/references/history-replay-loop.md",
            "skills/self-skills-improve/SKILL.md",
        ]
        for rel in expected:
            path = self.tmpdir / rel
            self.assertTrue(path.is_file(), f"missing: {rel}")

    def test_repo_name_basename_fallback(self):
        """Without --repo-name, name is inferred from directory basename."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        result = self._run("--repo", str(self.tmpdir))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        expected_name = self.tmpdir.resolve().name
        self.assertIn(f"repo: {expected_name}", result.stdout)

    def test_repo_name_explicit_override(self):
        """Explicit --repo-name overrides inference."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/inferred-name.git"],
            cwd=self.tmpdir, capture_output=True, timeout=10,
        )
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "explicit-override")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: explicit-override", result.stdout)
        self.assertNotIn("inferred-name", result.stdout)

    def test_repo_name_inference_from_https_origin(self):
        """Name inferred from HTTPS Git origin URL."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/my-repo.git"],
            cwd=self.tmpdir, capture_output=True, timeout=10,
        )
        result = self._run("--repo", str(self.tmpdir))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: my-repo", result.stdout)

    def test_repo_name_inference_from_ssh_origin(self):
        """Name inferred from SSH Git origin URL."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "remote", "add", "origin", "ssh://git@github.com/org/ssh-repo.git"],
            cwd=self.tmpdir, capture_output=True, timeout=10,
        )
        result = self._run("--repo", str(self.tmpdir))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: ssh-repo", result.stdout)

    def test_repo_name_inference_from_scp_like_origin(self):
        """Name inferred from scp-like origin URL (user@host:path)."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "remote", "add", "origin", "user@host.example.com:path/to/scp-repo"],
            cwd=self.tmpdir, capture_output=True, timeout=10,
        )
        result = self._run("--repo", str(self.tmpdir))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: scp-repo", result.stdout)

    def test_repo_name_inference_from_file_origin(self):
        """Name inferred from file:// Git origin URL."""
        shutil.rmtree(self.tmpdir)
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-"))
        subprocess.run(["git", "init"], cwd=self.tmpdir, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "remote", "add", "origin", "file:///path/to/local-repo.git"],
            cwd=self.tmpdir, capture_output=True, timeout=10,
        )
        result = self._run("--repo", str(self.tmpdir))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: local-repo", result.stdout)

    def test_repo_name_with_dots_valid(self):
        """Ordinary dots inside repo names are valid."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "my.repo.v2.0")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("repo: my.repo.v2.0", result.stdout)

    # ── explicit-name rejection: surrounding whitespace ───────────

    def test_repo_name_leading_whitespace_rejected(self):
        """Explicit name with leading whitespace is rejected, not normalized."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", " my-repo")
        self.assertNotEqual(result.returncode, 0, "should reject leading space")
        self.assertFalse(
            (self.tmpdir / "skills").exists(),
            "no skills/ dir on rejected name",
        )

    def test_repo_name_trailing_whitespace_rejected(self):
        """Explicit name with trailing whitespace is rejected, not normalized."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "my-repo ")
        self.assertNotEqual(result.returncode, 0, "should reject trailing space")
        self.assertFalse(
            (self.tmpdir / "skills").exists(),
            "no skills/ dir on rejected name",
        )

    def test_repo_name_surrounding_whitespace_rejected(self):
        """Explicit name with surrounding whitespace is rejected, not normalized."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", " my-repo ")
        self.assertNotEqual(result.returncode, 0, "should reject surrounding spaces")
        self.assertFalse(
            (self.tmpdir / "skills").exists(),
            "no skills/ dir on rejected name",
        )

    # ── existing name-rejection tests ─────────────────────────────

    def test_repo_name_dot_rejected(self):
        """Exact '.' as repo name is rejected."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", ".")
        self.assertNotEqual(result.returncode, 0, "should reject '.'")

    def test_repo_name_dotdot_rejected(self):
        """Exact '..' as repo name is rejected."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "..")
        self.assertNotEqual(result.returncode, 0, "should reject '..'")

    def test_repo_name_slash_rejected(self):
        """Name containing '/' is rejected."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "a/b")
        self.assertNotEqual(result.returncode, 0, "should reject '/'")

    def test_repo_name_newline_rejected(self):
        """Name containing newline is rejected."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "bad\nname")
        self.assertNotEqual(result.returncode, 0, "should reject newline")

    def test_repo_name_empty_rejected(self):
        """Empty repo name is rejected."""
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "")
        self.assertNotEqual(result.returncode, 0, "should reject empty")

    # ── full-path tests ───────────────────────────────────────────

    def test_precheck_executable(self):
        """precheck.sh is executable after instantiation."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        precheck = self.tmpdir / "skills" / "code-review" / "scripts" / "precheck.sh"
        self.assertTrue(precheck.is_file())
        self.assertTrue(os.access(precheck, os.X_OK), "precheck.sh not executable")

    def test_precheck_rejects_unfilled_skeleton_and_outputs_repo_name(self):
        """The deterministic skeleton is not a completed Phase 8 package."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        precheck = self.tmpdir / "skills" / "code-review" / "scripts" / "precheck.sh"
        result = subprocess.run(
            [str(precheck)], capture_output=True, text=True, timeout=30,
            cwd=str(self.tmpdir),
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("repo: test-repo", result.stdout,
                      f"precheck output missing repo marker: {result.stdout}")
        self.assertIn("unfilled bootstrap value", result.stdout)

    def test_precheck_passes_after_phase8_values_are_filled(self):
        """Contract check passes after every bootstrap sentinel is resolved."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        for path in (self.tmpdir / "skills").rglob("*"):
            if path.is_file() and path.suffix in {".md", ".sh"}:
                content = path.read_text(encoding="utf-8")
                path.write_text(
                    content.replace("BOOTSTRAP_REQUIRED", "not-observed"),
                    encoding="utf-8",
                )

        precheck = self.tmpdir / "skills" / "code-review" / "scripts" / "precheck.sh"
        result = subprocess.run(
            [str(precheck)], capture_output=True, text=True, timeout=30,
            cwd=str(self.tmpdir),
        )
        self.assertEqual(
            result.returncode,
            0,
            f"precheck failed: {result.stderr}\nstdout: {result.stdout}",
        )
        self.assertIn("product build/test not executed", result.stdout)

    def test_idempotent_preserve(self):
        """Second run preserves user edits."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")

        # Modify a file
        skill_md = self.tmpdir / "skills" / "SKILL.md"
        original = skill_md.read_text(encoding="utf-8")
        modified = original + "\n\n## User Custom Section\nCustom content.\n"
        skill_md.write_text(modified, encoding="utf-8")

        # Run again
        result = self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        self.assertEqual(result.returncode, 0)
        self.assertIn("preserved", result.stdout.lower())

        # Content preserved
        current = skill_md.read_text(encoding="utf-8")
        self.assertEqual(current, modified)

    def test_no_private_company_references(self):
        """No HENGSHI/hengshi/heglabs/etc in rendered content."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")

        PRIVATE_PATTERNS = [
            "HENGSHI", "hengshi", "henglabs",
            "gitlab.hengshi.org", "everest", "lhotse",
            "~/.hengshi", "pullall",
        ]
        for path in self.tmpdir.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".sh"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in PRIVATE_PATTERNS:
                rel = path.relative_to(self.tmpdir)
                self.assertNotIn(pattern, text,
                               f"private pattern '{pattern}' in {rel}")

    def test_non_git_repo_rejected(self):
        """Non-git directory is rejected."""
        no_git = Path(tempfile.mkdtemp(prefix="test-nogit-"))
        try:
            result = self._run("--repo", str(no_git))
            self.assertNotEqual(result.returncode, 0,
                              "should reject non-git directory")
        finally:
            shutil.rmtree(no_git, ignore_errors=True)

    def test_repo_name_rendered(self):
        """{{REPO_NAME}} token is rendered."""
        self._run("--repo", str(self.tmpdir), "--repo-name", "my-custom-repo")
        skill_md = self.tmpdir / "skills" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("my-custom-repo", content)
        self.assertNotIn("{{REPO_NAME}}", content)

    # ── full-path instantiate failure: no files created ───────────

    def test_instantiate_missing_template_no_files_created(self):
        """Invoking the actual instantiate function with a missing template creates no target files.

        Uses an isolated temporary copy of the template directory so that no
        real file under templates/ is ever renamed, deleted, or mutated.
        """
        mod = _load_module()
        original_template = mod.REPO_LOCAL_TEMPLATE

        # Create an isolated temp copy of the template directory
        with tempfile.TemporaryDirectory(prefix="test-template-copy-") as temp_dir:
            temp_template = Path(temp_dir)
            shutil.copytree(original_template, temp_template, dirs_exist_ok=True)

            # Remove a canonical file from the copy to simulate a missing template
            (temp_template / "SKILL.md").unlink()

            # Patch the module constant so the real instantiate() sees the
            # isolated copy rather than the canonical source template.
            with unittest.mock.patch.object(
                mod, "REPO_LOCAL_TEMPLATE", temp_template
            ):
                result = mod.instantiate(self.tmpdir, "test-repo")
                self.assertTrue(
                    result.get("errors"),
                    "should report errors when template file is missing",
                )
                self.assertFalse(
                    (self.tmpdir / "skills").exists(),
                    "no skills/ dir on template error",
                )

        # Canonical source template must remain untouched
        self.assertTrue(
            (original_template / "SKILL.md").is_file(),
            "canonical source template must remain present",
        )

    def test_existing_invalid_destination_rejected(self):
        """Directory at a destination file path fails preflight; no files created."""
        # Pre-create skills/SKILL.md as a directory
        dst_dir = self.tmpdir / "skills" / "SKILL.md"
        dst_dir.parent.mkdir(parents=True, exist_ok=True)
        dst_dir.mkdir()

        result = self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
        self.assertNotEqual(result.returncode, 0,
                          "should reject directory at destination path")
        # Verify no other files were created (the pre-existing dir should be alone)
        # Check that known canonical files besides SKILL.md were NOT written
        self.assertFalse(
            (self.tmpdir / "skills" / "code-review" / "SKILL.md").exists(),
            "no files beyond pre-existing dir on preflight failure",
        )

    def test_symlink_escape_rejected(self):
        """Destination resolving outside repo via symlink fails preflight."""
        # Pre-create skills/references as a symlink to an outside directory
        outside_dir = Path(tempfile.mkdtemp(prefix="test-escape-"))
        try:
            skills_dir = self.tmpdir / "skills"
            skills_dir.mkdir(parents=True)
            (skills_dir / "references").symlink_to(outside_dir, target_is_directory=True)

            result = self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
            self.assertNotEqual(result.returncode, 0,
                              "should reject symlink escape")
        finally:
            shutil.rmtree(outside_dir, ignore_errors=True)

    def test_skills_symlink_outside_repo_rejected(self):
        """skills/ itself resolving outside repo via symlink fails preflight."""
        outside_dir = Path(tempfile.mkdtemp(prefix="test-escape-"))
        try:
            # Create skills as a symlink to outside
            (self.tmpdir / "skills").symlink_to(outside_dir, target_is_directory=True)

            result = self._run("--repo", str(self.tmpdir), "--repo-name", "test-repo")
            self.assertNotEqual(result.returncode, 0,
                              "should reject skills/ symlink escape")
        finally:
            shutil.rmtree(outside_dir, ignore_errors=True)

    # ── preflight direct-call tests ───────────────────────────────

    def test_preflight_no_partial_write_on_template_missing(self):
        """Preflight failure prevents any file creation."""
        mod = _load_module()
        errors, _plan = mod._preflight(
            Path("/nonexistent/template/dir"), self.tmpdir, "test"
        )
        self.assertTrue(errors, "preflight should report errors for missing template dir")
        self.assertFalse(
            (self.tmpdir / "skills").exists(),
            "no files should be written on preflight failure",
        )

    def test_preflight_passes_for_valid_template(self):
        """Preflight passes when template is intact."""
        mod = _load_module()
        errors, plan = mod._preflight(
            mod.REPO_LOCAL_TEMPLATE, self.tmpdir, "test-repo"
        )
        self.assertEqual(errors, [], f"preflight should pass: {errors}")
        self.assertEqual(len(plan), len(mod.CANONICAL_FILES),
                       "rendered plan should cover all canonical files")
        # Spot-check: no unresolved tokens in rendered content
        for rel, content in plan.items():
            self.assertNotIn("{{REPO_NAME}}", content,
                           f"{{REPO_NAME}} not rendered in {rel}")

    # ── git URL parsing tests ─────────────────────────────────────

    def test_parse_git_url_https(self):
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("https://github.com/org/repo.git"), "repo")
        self.assertEqual(mod._parse_git_url("https://github.com/org/repo"), "repo")

    def test_parse_git_url_ssh(self):
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("ssh://git@github.com/org/repo.git"), "repo")

    def test_parse_git_url_scp_like(self):
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("git@github.com:org/repo.git"), "repo")
        self.assertEqual(mod._parse_git_url("user@host:path/to/repo"), "repo")

    def test_parse_git_url_file(self):
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("file:///path/to/repo.git"), "repo")
        self.assertEqual(mod._parse_git_url("file:///path/to/repo"), "repo")

    def test_parse_git_url_plain_path(self):
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("/home/user/repos/my-project.git"), "my-project")
        self.assertEqual(mod._parse_git_url("/home/user/repos/my-project"), "my-project")
        self.assertEqual(mod._parse_git_url("../relative/other-repo"), "other-repo")

    def test_parse_git_url_colon_no_at(self):
        """host:path (no user@) is a valid scp-like remote; bare host:word is not."""
        mod = _load_module()
        self.assertEqual(mod._parse_git_url("host.example.com:path/to/repo"), "repo")
        self.assertIsNone(mod._parse_git_url("host:bareword"))

    def test_parse_git_url_unparseable(self):
        mod = _load_module()
        self.assertIsNone(mod._parse_git_url(""))
        self.assertIsNone(mod._parse_git_url("just-a-string"))

    # ── name validation tests (stderr captured) ───────────────────

    def test_validate_name_ordinary_dots(self):
        mod = _load_module()
        self.assertEqual(mod._validate_name("com.example.repo", "test"), "com.example.repo")
        self.assertEqual(mod._validate_name("v1.2.3", "test"), "v1.2.3")

    def test_validate_name_rejects_empty(self):
        mod = _load_module()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            mod._validate_name("", "test")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            mod._validate_name("   ", "test")

    def test_validate_name_rejects_whitespace(self):
        mod = _load_module()
        for name in [" name", "name ", " name "]:
            with self.subTest(name=name):
                with self.assertRaises(SystemExit, msg=f"should reject {name!r}"):
                    with contextlib.redirect_stderr(io.StringIO()):
                        mod._validate_name(name, "test")

    def test_validate_name_rejects_forbidden(self):
        mod = _load_module()
        for name in [".", "..", "a/b", "a\x00b", "a\nb", "a\r\nb"]:
            with self.subTest(name=name):
                with self.assertRaises(SystemExit, msg=f"should reject {name!r}"):
                    with contextlib.redirect_stderr(io.StringIO()):
                        mod._validate_name(name, "test")

    # ── documentation consistency test ────────────────────────────

    def test_doc_consistency_no_old_cli_forms(self):
        """Authoritative runtime docs/E2E must not contain old repo-local CLI forms.

        The canonical form is: instantiate_repo_local_skill.py --repo <path>
        This test fails if any doc/E2E file references the script without --repo.
        """
        repo_root = Path(__file__).resolve().parent.parent
        scan_dirs = [
            repo_root / "playbooks",
            repo_root / "e2e",
        ]
        scan_files = [
            repo_root / "SKILL.md",
            repo_root / "README.md",
        ]

        violations: list[str] = []
        script_name = "instantiate_repo_local_skill.py"

        # Collect all .md and .sh files from scan directories
        doc_files: list[Path] = list(scan_files)
        for d in scan_dirs:
            if d.is_dir():
                doc_files.extend(d.rglob("*.md"))
                doc_files.extend(d.rglob("*.sh"))

        for f in doc_files:
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            if script_name not in text:
                continue

            # Find every line that mentions the script
            for i, line in enumerate(text.split("\n"), start=1):
                if script_name not in line:
                    continue
                # Only flag lines that look like CLI invocations:
                # contains "scripts/" path or "python" alongside the script name
                stripped = line.strip()
                if "--repo" in line:
                    continue
                # Prose references and directory-tree illustrations are fine
                if "scripts/" not in stripped and "python" not in stripped.lower():
                    continue
                rel = f.relative_to(repo_root)
                violations.append(
                    f"{rel}:{i}: reference without --repo flag: {stripped[:120]}"
                )

        self.assertEqual(
            [], violations,
            f"old CLI forms found ({len(violations)}):\n" + "\n".join(violations),
        )


class TestPrecheckSelfContained(unittest.TestCase):
    """precheck.sh is self-contained - no reference-company deps."""

    @classmethod
    def setUpClass(cls):
        if not INSTANTIATOR.is_file():
            raise unittest.SkipTest("instantiator script not found")

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-rls-pc-"))
        (self.tmpdir / ".git").mkdir(parents=True, exist_ok=True)
        (self.tmpdir / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
        subprocess.run(
            [sys.executable, str(INSTANTIATOR), "--repo", str(self.tmpdir),
             "--repo-name", "test-repo"],
            capture_output=True, timeout=30,
        )

    def tearDown(self):
        if self.tmpdir.exists():
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_precheck_no_forbidden_references(self):
        """precheck.sh does not contain reference-company paths."""
        precheck = self.tmpdir / "skills" / "code-review" / "scripts" / "precheck.sh"
        text = precheck.read_text(encoding="utf-8")
        forbidden = ["hengshi-jarvis", "precheck-diff.sh", "pullall", "~/.hengshi"]
        for ref in forbidden:
            self.assertNotIn(ref, text, f"precheck.sh contains forbidden ref: {ref}")

    def test_precheck_bash_syntax(self):
        """precheck.sh passes bash -n syntax check."""
        precheck = self.tmpdir / "skills" / "code-review" / "scripts" / "precheck.sh"
        result = subprocess.run(
            ["bash", "-n", str(precheck)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0,
                        f"bash -n failed: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
