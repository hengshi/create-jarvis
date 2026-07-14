#!/usr/bin/env python3
"""Tests for deterministic company Jarvis instantiator."""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
INSTANTIATOR = SCRIPTS_DIR / "instantiate_company_jarvis.py"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
STATE_PATH = FIXTURES_DIR / "acme-bootstrap-state.json"


class TestInstantiateCompanyJarvis(unittest.TestCase):
    """Deterministic instantiator tests."""

    @classmethod
    def setUpClass(cls):
        if not INSTANTIATOR.is_file():
            raise unittest.SkipTest("instantiator script not found")
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-cj-"))
        # Write state with updated target
        state = dict(self.state)
        state["paths"] = dict(self.state["paths"])
        state["paths"]["jarvis_target_home"] = str(self.tmpdir)
        state["paths"]["jarvis_home"] = str(self.tmpdir)
        self.state_path = self.tmpdir / "state.json"
        self.state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        if self.tmpdir.exists():
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(INSTANTIATOR)] + list(args),
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(self.tmpdir),
        )

    def _count_files(self, root: Path) -> int:
        return sum(1 for _ in root.rglob("*") if _.is_file())

    def test_base_creates_repo_structure(self):
        """base subcommand creates expected root files and 17 references."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")

        # Root files
        for f in ["README.md", "MAINTENANCE.md", "jarvis.toml", "AGENTS.md", "CLAUDE.md",
                   ".github/copilot-instructions.md", ".gitignore", "SKILL.md"]:
            self.assertTrue((self.tmpdir / f).is_file(), f"missing root file: {f}")

        # Entry skill
        entry = self.tmpdir / "skills" / "acme-claude-e2e-jarvis" / "SKILL.md"
        self.assertTrue(entry.is_file(), f"missing entry skill: {entry}")

        # 17 references
        refs_dir = self.tmpdir / "references"
        self.assertTrue(refs_dir.is_dir())
        ref_count = len(list(refs_dir.glob("*.md")))
        self.assertEqual(ref_count, 17, f"expected 17 references, got {ref_count}")

        # Entry skill semantics - check for key routing/writeback concepts
        entry_text = entry.read_text(encoding="utf-8")
        # Key concepts that must be present in any rendered entry skill
        semantic_checks = [
            (r"runtime-governance-quick\.md", "mandatory pre-read"),
            (r"next-hop-compression|next-hop", "next-hop routing"),
            (r"END|writeback|回写", "END writeback"),
            (r"closed[- ]?loop|闭环", "closed-loop routing"),
            (r"workflow-first", "workflow-first routing"),
            (r"artifact-first", "artifact-first routing"),
        ]
        for pattern, desc in semantic_checks:
            self.assertTrue(
                re.search(pattern, entry_text, re.IGNORECASE),
                f"entry skill missing concept: {desc}",
            )

    def test_base_creates_root_runtime_contracts_and_build_brief(self):
        """Phase 7 base creates the durable resume contracts and build brief."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")

        state_path = self.tmpdir / "bootstrap-state.json"
        result_path = self.tmpdir / "bootstrap-result.json"
        brief_path = self.tmpdir / "_bootstrap" / "jarvis-build-brief.md"
        self.assertTrue(state_path.is_file())
        self.assertTrue(result_path.is_file())
        self.assertTrue(brief_path.is_file())

        state = json.loads(state_path.read_text(encoding="utf-8"))
        runtime_result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(state["phase_status"]["phase-07-company-jarvis-repo"], "in-progress")
        self.assertEqual(state["phase_status"]["phase-08-repo-local-skills"], "pending")
        self.assertEqual(runtime_result["status"], "in-progress")
        self.assertEqual(runtime_result["paths"]["jarvis_target_home"], str(self.tmpdir))
        self.assertEqual(runtime_result["paths"]["entry_skill"], "skills/acme-claude-e2e-jarvis/SKILL.md")
        self.assertIn("bootstrap-state.json", runtime_result["created_files"])
        self.assertIn("bootstrap-result.json", runtime_result["created_files"])
        self.assertIn("_bootstrap/jarvis-build-brief.md", runtime_result["created_files"])
        self.assertIn("Acme Corp", brief_path.read_text(encoding="utf-8"))

    def test_base_preserves_build_brief_on_repeat(self):
        """A repeated base invocation does not overwrite agent or human edits."""
        first = self._run("base", "--state", str(self.state_path))
        self.assertEqual(first.returncode, 0)
        brief = self.tmpdir / "_bootstrap" / "jarvis-build-brief.md"
        edited = brief.read_text(encoding="utf-8") + "\noperator note\n"
        brief.write_text(edited, encoding="utf-8")

        second = self._run("base", "--state", str(self.state_path))
        self.assertEqual(second.returncode, 0, f"stderr: {second.stderr}")
        self.assertEqual(brief.read_text(encoding="utf-8"), edited)

    def test_no_unresolved_tokens(self):
        """After base render, no {{...}} tokens remain."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

        for path in self.tmpdir.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".toml", ".json"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "{{" in text:
                unresolved = [t.split("}}")[0] for t in text.split("{{")[1:] if "}}" in t]
                if unresolved:
                    self.fail(f"unresolved tokens in {path.relative_to(self.tmpdir)}: {unresolved}")

    def test_no_private_company_facts(self):
        """No HENGSHI/衡石 private facts in rendered output."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

        PRIVATE_PATTERNS = [
            "HENGSHI",
            "hengshi",
            "henglabs",
            "gitlab.hengshi.org",
            "~/.hengshi",
        ]
        skip_dirs = {"_bootstrap"}  # bootstrap artifacts may reference template source

        for path in self.tmpdir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".toml", ".json", ".sh"}:
                continue
            # Skip README of templates/company-jarvis which describes source
            rel = path.relative_to(self.tmpdir)
            if any(p in skip_dirs for p in rel.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in PRIVATE_PATTERNS:
                if pattern in text:
                    self.fail(f"private pattern '{pattern}' found in {rel}")

    def test_resume_preserves_user_edit(self):
        """Idempotent: existing user content is preserved, not overwritten."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0)

        # Modify a file
        readme = self.tmpdir / "README.md"
        original = readme.read_text(encoding="utf-8")
        modified = original + "\n<!-- USER ADDED SECTION -->\nUser customization here.\n"
        readme.write_text(modified, encoding="utf-8")

        # Run again
        result2 = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result2.returncode, 0)
        self.assertIn("preserved", result2.stdout.lower())

        # Content should be preserved
        current = readme.read_text(encoding="utf-8")
        self.assertEqual(current, modified, "user edit was overwritten")

    def test_hql_casing_preserved(self):
        """Module name HQL keeps its casing."""
        result = self._run("module", "--state", str(self.state_path), "--name", "HQL")
        self.assertEqual(result.returncode, 0)

        modules_dir = self.tmpdir / "modules"
        module_dirs = [d.name for d in modules_dir.iterdir() if d.is_dir()] if modules_dir.is_dir() else []
        # HQL must exist with exact casing
        self.assertIn("HQL", module_dirs, f"modules/HQL/ should exist. Found: {module_dirs}")
        # No lowercase variant should exist
        self.assertNotIn("hql", module_dirs, f"should not create lowercase hql. Found: {module_dirs}")

        overview = self.tmpdir / "modules" / "HQL" / "overview.md"
        self.assertTrue(overview.is_file(), "overview.md should exist")

    def test_module_template_exposes_confidence_and_status_contract(self):
        """Module contracts must expose fillable evidence confidence/status fields."""
        result = self._run("module", "--state", str(self.state_path), "--name", "analytics")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        overview = (self.tmpdir / "modules" / "analytics" / "overview.md").read_text(encoding="utf-8")
        self.assertRegex(overview, r"证据置信度")
        self.assertRegex(overview, r"确认状态")

    def test_source_subcommand(self):
        """Source subcommand creates sources/<name>/README.md (route contract, not SKILL.md)."""
        # Must run base first for target directory and _bootstrap discovery
        self._run("base", "--state", str(self.state_path))
        result = self._run("source", "--state", str(self.state_path), "--name", "customer-docs")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")

        source_readme = self.tmpdir / "sources" / "customer-docs" / "README.md"
        self.assertTrue(source_readme.is_file(), "source route should create README.md, not SKILL.md")
        # Must NOT create SKILL.md in sources
        source_skill = self.tmpdir / "sources" / "customer-docs" / "SKILL.md"
        self.assertFalse(source_skill.is_file(), "source subcommand must not create SKILL.md in sources")

    def test_package_issue_intake_with_companion_refs(self):
        """Package subcommand creates issue-intake with all companion references."""
        self._run("base", "--state", str(self.state_path))
        result = self._run("package", "--state", str(self.state_path),
                          "--kind", "issue-intake", "--name", "issue-intake")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

        pkg = self.tmpdir / "skills" / "issue-intake"
        self.assertTrue((pkg / "SKILL.md").is_file())
        for ref in ["blocker-template", "disposition-command-checklist", "disposition-proof-sop",
                     "guided-question-flow", "issue-type-matrix", "output-template",
                     "pre-filing-judgment-card"]:
            self.assertTrue((pkg / "references" / f"{ref}.md").is_file(),
                          f"missing companion ref: {ref}")

    def test_package_generic_workflow(self):
        """Generic workflow package creates a non-thin SKILL.md."""
        self._run("base", "--state", str(self.state_path))
        result = self._run("package", "--state", str(self.state_path),
                          "--kind", "generic-workflow", "--name", "customer-deploy")
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

        skill = self.tmpdir / "skills" / "customer-deploy" / "SKILL.md"
        self.assertTrue(skill.is_file())
        content = skill.read_text(encoding="utf-8")
        # Not a thin scaffold
        self.assertGreater(len(content.strip()), 500,
                          f"generic-workflow SKILL.md too thin: {len(content.strip())} bytes")
        # Has START->WORK->VERIFY->END structure
        for keyword in ["START", "WORK", "VERIFY", "END"]:
            self.assertIn(keyword, content, f"missing workflow keyword: {keyword}")

    def test_path_traversal_rejected(self):
        """Names with .. or / are rejected."""
        for bad_name in ["../escape", "foo/bar"]:
            result = self._run("module", "--state", str(self.state_path), "--name", bad_name)
            self.assertNotEqual(result.returncode, 0,
                              f"should reject path traversal: {bad_name!r}")
        # NUL byte: tested via instantiator validation, not subprocess arg

    def test_validate_name_allows_dots(self):
        """Names containing regular dots (like foo.bar) are allowed."""
        result = self._run("module", "--state", str(self.state_path),
                          "--name", "foo.bar")
        # Should succeed — dots in names are valid
        self.assertEqual(result.returncode, 0,
                       f"foo.bar should be allowed, got: {result.stderr}")

    def test_preflight_no_partial_write(self):
        """Preflight prevents partial writes: UNKNOWN_TOKEN error with no target files."""
        import importlib.util as _iu
        _spec = _iu.spec_from_file_location(
            "instantiate_company_jarvis",
            Path(__file__).resolve().parent.parent / "scripts" / "instantiate_company_jarvis.py",
        )
        _ij = _iu.module_from_spec(_spec)
        _spec.loader.exec_module(_ij)

        # Create a temp template source with an unresolvable token
        src_dir = Path(self.tmpdir) / "bad-template"
        (src_dir / "sub").mkdir(parents=True)
        (src_dir / "README.md").write_text("# {{UNKNOWN_TOKEN}} test\n", encoding="utf-8")
        (src_dir / "sub" / "info.md").write_text("ok file\n", encoding="utf-8")

        result = _ij.copy_and_render(src_dir, Path(self.tmpdir) / "target",
                                     {"UNKNOWN_TOKEN": "{{STILL_UNRESOLVED}}"})
        self.assertIn("errors", result)
        self.assertTrue(len(result["errors"]) > 0,
                      f"should have preflight errors, got: {result}")
        # Target directory should NOT exist or be empty (no partial write)
        target = Path(self.tmpdir) / "target"
        if target.exists():
            files = list(target.rglob("*"))
            self.assertEqual(len(files), 0,
                           f"target should be empty after failed preflight, got: {files}")

    def test_unknown_package_kind_rejected(self):
        """Unknown package kind fails with helpful message."""
        self._run("base", "--state", str(self.state_path))
        result = self._run("package", "--state", str(self.state_path),
                          "--kind", "nonexistent-kind-xyz", "--name", "test")
        self.assertNotEqual(result.returncode, 0)

    def test_package_frontmatter_name_matches_output_dir(self):
        """Rendered SKILL.md YAML name matches the output directory name."""
        self._run("base", "--state", str(self.state_path))

        # Test issue-intake
        self._run("package", "--state", str(self.state_path),
                  "--kind", "issue-intake", "--name", "prefixed-issue-intake")
        skill_md = self.tmpdir / "skills" / "prefixed-issue-intake" / "SKILL.md"
        self.assertTrue(skill_md.is_file())
        content = skill_md.read_text(encoding="utf-8")
        m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        self.assertIsNotNone(m, "SKILL.md should have a YAML name field")
        self.assertEqual(m.group(1).strip(), "prefixed-issue-intake",
                         f"frontmatter name should be 'prefixed-issue-intake', got {m.group(1).strip()!r}")

        # Test generic custom name
        self._run("package", "--state", str(self.state_path),
                  "--kind", "generic-workflow", "--name", "custom-deploy-loop")
        skill_md2 = self.tmpdir / "skills" / "custom-deploy-loop" / "SKILL.md"
        self.assertTrue(skill_md2.is_file())
        content2 = skill_md2.read_text(encoding="utf-8")
        m2 = re.search(r"^name:\s*(.+)$", content2, re.MULTILINE)
        self.assertIsNotNone(m2, "SKILL.md should have a YAML name field")
        self.assertEqual(m2.group(1).strip(), "custom-deploy-loop",
                         f"frontmatter name should be 'custom-deploy-loop', got {m2.group(1).strip()!r}")

    def test_jarvis_toml_valid_and_complete(self):
        """jarvis.toml is valid TOML with required sections."""
        result = self._run("base", "--state", str(self.state_path))
        self.assertEqual(result.returncode, 0)

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                raise unittest.SkipTest("tomllib/tomli not available")

        toml_path = self.tmpdir / "jarvis.toml"
        self.assertTrue(toml_path.is_file())
        parsed = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        for section in ["project", "identity", "runtime", "vcs", "bootstrap"]:
            self.assertIn(section, parsed, f"jarvis.toml missing [{section}]")

        # Check key values
        self.assertEqual(parsed["project"]["slug"], "acme-claude-e2e")
        self.assertEqual(parsed["project"]["name"], "acme-claude-e2e-jarvis")
        self.assertEqual(parsed["runtime"]["type"], "jarvis-box")
        self.assertEqual(parsed["runtime"]["entry_skill"], "skills/acme-claude-e2e-jarvis/SKILL.md")
        self.assertEqual(parsed["identity"]["product"], "Acme Analytics Platform")
        # Bootstrap paths are root files (not _bootstrap/ subdirectory)
        self.assertEqual(parsed["bootstrap"]["phase_status_file"], "bootstrap-state.json")
        self.assertEqual(parsed["bootstrap"]["result_file"], "bootstrap-result.json")

    def test_hengshi_real_shape_regression(self):
        """Hengshi-real-state regression: 4th-round actual key shape renders correctly with literal RUNTIME_ROOT."""
        hengshi_state = {
            "schema_version": 1,
            "phase": "phase-07-company-jarvis-repo",
            "status": "in-progress",
            "paths": {
                "jarvis_home": str(self.tmpdir / "hengshi-jarvis"),
                "jarvis_target_home": str(self.tmpdir / "hengshi-jarvis"),
                "entry_skill": "skills/hengshi-jarvis/SKILL.md",
                "runtime_root": "/e2e/runtime"
            },
            "inputs": {
                "company_slug": "hengshi",
                "company_name": "Hengshi"
            },
            "confirmed_answers": {
                "company_slug": "hengshi",
                "company_name": "Hengshi",
                "gitlab_host": "gitlab.hengshi.org",
                "gitlab_host_confirmed": "gitlab-confirmed.hengshi.org",
                "owners": ["hengshi-platform-team"],
                "runtime_root": "/e2e/runtime"
            },
            "identity_reconciliation": {
                "status": "confirmed",
                "company_identity": {
                    "name": "Hengshi",
                    "slug": "hengshi"
                },
                "confirmed_product_identity": "Hengshi Sense",
                "source_detected_identities": [],
                "conflicts": []
            },
            "method_repo": {
                "repo": "create-jarvis-skill",
                "commit": "HEAD"
            },
            "phase_status": {}
        }
        state_path = self.tmpdir / "hengshi-state.json"
        state_path.write_text(json.dumps(hengshi_state, ensure_ascii=False), encoding="utf-8")

        result = self._run("base", "--state", str(state_path))
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")

        target = self.tmpdir / "hengshi-jarvis"

        # Durable templates use the runtime env contract, not a bootstrap-machine path.
        for f in ["README.md", "jarvis.toml"]:  # only files that use RUNTIME_ROOT token
            path = target / f
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/e2e/runtime", text,
                           f"{f} must NOT contain /e2e/runtime (RUNTIME_ROOT is fixed literal)")
            self.assertIn("$JARVIS_RUNTIME_ROOT", text,
                          f"{f} must contain the symbolic runtime root")
            self.assertNotIn("/Users/thomaschan", text,
                             f"{f} must not contain a bootstrap author's home path")

        # VCS host: gitlab_host_confirmed must win over stale gitlab_host
        toml_path = target / "jarvis.toml"
        if toml_path.is_file():
            text = toml_path.read_text(encoding="utf-8")
            self.assertIn("gitlab-confirmed.hengshi.org", text,
                        "jarvis.toml should use confirmed gitlab host (gitlab_host_confirmed)")
            self.assertNotIn("gitlab.hengshi.org", text,
                           "jarvis.toml must NOT contain stale gitlab_host when confirmed value exists")

        # owners from owners list should render
        readme = target / "README.md"
        if readme.is_file():
            text = readme.read_text(encoding="utf-8")
            self.assertIn("hengshi-platform-team", text,
                        "README.md should contain hengshi-platform-team as owner")

        # No unresolved tokens
        for path in target.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".toml"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "{{" in text:
                unresolved = [t.split("}}")[0] for t in text.split("{{")[1:] if "}}" in t]
                if unresolved:
                    self.fail(f"unresolved tokens in {path.relative_to(target)}: {unresolved}")

        # jarvis.toml must be valid TOML with required sections
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return
        toml_path = target / "jarvis.toml"
        self.assertTrue(toml_path.is_file())
        parsed = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        for section in ["project", "identity", "runtime", "vcs", "bootstrap"]:
            self.assertIn(section, parsed, f"jarvis.toml missing [{section}]")

    def test_extract_globals_index_generation(self):
        """extract_globals generates MODULE/SOURCE/WORKFLOW/REPO_INDEX preserving order and casing."""
        import importlib.util as _iu
        _spec = _iu.spec_from_file_location(
            "instantiate_company_jarvis",
            Path(__file__).resolve().parent.parent / "scripts" / "instantiate_company_jarvis.py",
        )
        _ij = _iu.module_from_spec(_spec)
        _spec.loader.exec_module(_ij)

        globals_ = _ij.extract_globals(self.state)

        # MODULE_INDEX: "payroll,benefits, HQL,payroll" → deduped, order preserved, HQL casing kept, payroll once
        mi = globals_["MODULE_INDEX"]
        self.assertIn("- modules/payroll/overview.md", mi)
        self.assertIn("- modules/benefits/overview.md", mi)
        self.assertIn("- modules/HQL/overview.md", mi)
        self.assertEqual(mi.count("payroll"), 1, "payroll should appear only once (dedup)")
        # Verify order: payroll before benefits before HQL
        pi = mi.index("payroll")
        bi = mi.index("benefits")
        hi = mi.index("HQL")
        self.assertLess(pi, bi, "payroll should come before benefits")
        self.assertLess(bi, hi, "benefits should come before HQL")

        # SOURCE_INDEX: "customer-docs, api-reference, customer-docs" → dedup, order preserved
        si = globals_["SOURCE_INDEX"]
        self.assertIn("- sources/customer-docs/README.md", si)
        self.assertIn("- sources/api-reference/README.md", si)
        self.assertEqual(si.count("customer-docs"), 1, "customer-docs should appear only once (dedup)")

        # WORKFLOW_INDEX: "deploy-loop, deploy-loop, prd-review" → dedup, order preserved
        wi = globals_["WORKFLOW_INDEX"]
        self.assertIn("- skills/deploy-loop/SKILL.md", wi)
        self.assertIn("- skills/prd-review/SKILL.md", wi)
        self.assertEqual(wi.count("deploy-loop"), 1, "deploy-loop should appear only once (dedup)")

        # REPO_INDEX keeps VCS identity but uses checkout basename for the local entry.
        ri = globals_["REPO_INDEX"]
        self.assertIn("- `web-frontend` — VCS project `acme/web-frontend`;", ri)
        self.assertIn("- `backend-api` — VCS project `acme/backend-api`;", ri)
        self.assertEqual(ri.count("repo-local entry `skills/SKILL.md` inside that repo"), 2)
        self.assertNotIn("acme/web-frontend/skills/SKILL.md", ri)

    def test_missing_product_identity_fail_closed(self):
        """Missing confirmed_product_identity causes immediate exit with error."""
        state = dict(self.state)
        state["identity_reconciliation"] = dict(state["identity_reconciliation"])
        del state["identity_reconciliation"]["confirmed_product_identity"]
        state_path = self.tmpdir / "no-pi-state.json"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        result = self._run("base", "--state", str(state_path))
        self.assertNotEqual(result.returncode, 0, "should exit non-zero when confirmed_product_identity is missing")
        self.assertIn("PRODUCT_IDENTITY", result.stderr,
                     "error output should mention PRODUCT_IDENTITY")


class IntegrationVerifierNoFalsePositiveTests(unittest.TestCase):
    """Integration: instantiator renders base + source + module + 12 packages,
    then verifier runs and asserts no template-congruence false positive."""

    @classmethod
    def setUpClass(cls):
        if not INSTANTIATOR.is_file():
            raise unittest.SkipTest("instantiator script not found")
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="test-cj-int-"))
        state = dict(self.state)
        state["paths"] = dict(self.state["paths"])
        state["paths"]["jarvis_target_home"] = str(self.tmpdir)
        state["paths"]["jarvis_home"] = str(self.tmpdir)
        self.state_path = self.tmpdir / "state.json"
        self.state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        if self.tmpdir.exists():
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_inst(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(INSTANTIATOR)] + list(args),
            capture_output=True, text=True, timeout=30, cwd=str(self.tmpdir),
        )

    ALL_12_KINDS = [
        "generic-workflow",
        "generic-source",
        "issue-intake",
        "issue-post-check",
        "bugfix-loop",
        "feature-delivery",
        "prd-review",
        "release-notes",
        "branch-neutral-docs",
        "outline-api",
        "jenkins-job-builder",
        "issue-attachment-regression-fixture",
    ]

    def test_all_12_packages_no_false_positive(self):
        """Instantiate base + source + module + 12 packages; verifier finds no false positive."""
        # Base
        r = self._run_inst("base", "--state", str(self.state_path))
        self.assertEqual(r.returncode, 0, f"base failed: {r.stderr}")

        # Source
        r = self._run_inst("source", "--state", str(self.state_path), "--name", "customer-docs")
        self.assertEqual(r.returncode, 0, f"source failed: {r.stderr}")

        # Module
        r = self._run_inst("module", "--state", str(self.state_path), "--name", "analytics")
        self.assertEqual(r.returncode, 0, f"module failed: {r.stderr}")

        # 12 packages with prefixed/custom names
        for kind in self.ALL_12_KINDS:
            pkg_name = f"prefixed-{kind}" if kind != "generic-workflow" else "custom-generic-workflow"
            r = self._run_inst("package", "--state", str(self.state_path),
                              "--kind", kind, "--name", pkg_name)
            self.assertEqual(r.returncode, 0, f"package {kind} failed: {r.stderr}")

        # Run verifier on the output
        import importlib.util as _iu
        _spec = _iu.spec_from_file_location(
            "verify_bootstrap_output",
            Path(__file__).resolve().parent.parent / "scripts" / "verify_bootstrap_output.py",
        )
        _vmod = _iu.module_from_spec(_spec)
        sys.modules["verify_bootstrap_output"] = _vmod
        _spec.loader.exec_module(_vmod)
        Verifier = _vmod.Verifier

        v = Verifier(self.tmpdir, [], run_precheck=False,
                     expected_company_slug="acme-claude-e2e",
                     expected_product_identity="Acme Analytics Platform",
                     expected_modules=["analytics"],
                     expected_sources=["customer-docs"])
        report = v.verify()

        # No template-congruence false positives
        false_positive_codes = {
            "workflow_companion_file_missing",
            "workflow_companion_file_empty",
            "generic_workflow_missing_structure",
            "workflow_companion_not_referenced",
            "workflow_semantic_marker_missing",
        }
        fp_findings = [f for f in report["findings"]
                       if f["code"] in false_positive_codes]
        self.assertEqual(len(fp_findings), 0,
                         f"template-congruence false positives: {fp_findings}")

    def test_r4_prefixed_issue_intake_companion_caught(self):
        """r4: prefixed issue-intake missing companion MUST still be caught."""
        # Base first
        r = self._run_inst("base", "--state", str(self.state_path))
        self.assertEqual(r.returncode, 0, f"base failed: {r.stderr}")

        # Instantiate issue-intake normally
        r = self._run_inst("package", "--state", str(self.state_path),
                          "--kind", "issue-intake", "--name", "prefixed-issue-intake")
        self.assertEqual(r.returncode, 0, f"package failed: {r.stderr}")

        # Delete one companion file
        comp = self.tmpdir / "skills" / "prefixed-issue-intake" / "references" / "blocker-template.md"
        comp.unlink()

        import importlib.util as _iu
        _spec = _iu.spec_from_file_location(
            "verify_bootstrap_output",
            Path(__file__).resolve().parent.parent / "scripts" / "verify_bootstrap_output.py",
        )
        _vmod = _iu.module_from_spec(_spec)
        sys.modules["verify_bootstrap_output"] = _vmod
        _spec.loader.exec_module(_vmod)
        Verifier = _vmod.Verifier

        v = Verifier(self.tmpdir, [], run_precheck=False)
        report = v.verify()
        codes = {f["code"] for f in report["findings"] if f["severity"] == "blocker"}
        self.assertIn("workflow_companion_file_missing", codes,
                      "prefixed-issue-intake with missing companion must be caught")


if __name__ == "__main__":
    unittest.main()
