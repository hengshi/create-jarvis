from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_skill_depth", ROOT / "templates" / "replay" / "audit_skill_depth.py"
)
assert SPEC and SPEC.loader
AUDITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)


class RepositorySkillDepthTests(unittest.TestCase):
    def fixture(self, root: pathlib.Path) -> tuple[pathlib.Path, str]:
        repo = root / "repo"
        router = "sample-development"
        packages = [router, "sample-close-loop"]
        (repo / "src").mkdir(parents=True)
        (repo / "src" / "owner.py").write_text("STATE='ready'\n", encoding="utf-8")
        for package in packages:
            package_root = repo / "skills" / package
            package_root.mkdir(parents=True)
            (package_root / "SKILL.md").write_text(
                "Read skill-depth records and evals/evals.json; run audit_skill_depth.py.\n",
                encoding="utf-8",
            )
        router_root = repo / "skills" / router
        (router_root / "SKILL.md").write_text(
            "Route sample-close-loop. Read skill-depth records and evals/evals.json; "
            "run audit_skill_depth.py.\n",
            encoding="utf-8",
        )
        (router_root / "references").mkdir()
        (router_root / "references" / "skill-depth.md").write_text(
            "# Depth\n\n[owner](../../../src/owner.py)\n", encoding="utf-8"
        )
        categories = [
            {"name": name, "status": "covered" if name == "repo-specific" else "not-applicable", "evidence": ["src/owner.py" if name == "repo-specific" else "not used by fixture"]}
            for name in sorted(AUDITOR.REQUIRED_CATEGORIES)
        ]
        coverage = {
            "schema_version": 1,
            "categories": categories,
            "capabilities": [
                {"id": "close", "category": "repo-specific", "task_family": "close", "disposition": "skill", "primary_home": "sample-close-loop", "evidence": ["src/owner.py"]}
            ],
        }
        (router_root / "references" / "capability-coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (router_root / "evals").mkdir()
        evals = {"evals": [{"id": "forward-1", "kind": "forward", "status": "executed-pass"}]}
        (router_root / "evals" / "evals.json").write_text(json.dumps(evals), encoding="utf-8")
        (router_root / "scripts").mkdir()
        (router_root / "scripts" / "audit_skill_depth.py").write_text("# installed auditor\n", encoding="utf-8")
        dimensions = {name: name for name in AUDITOR.REQUIRED_DIMENSIONS}
        record = lambda name, risk, level, controls, ids: {
            "name": name,
            "risk": risk,
            "level": level,
            "authority": ["src/owner.py#STATE"],
            "entrypoints": ["src/owner.py"],
            "transitions": ["ready -> closed"],
            "mechanical_controls": controls,
            "forward_eval_ids": ids,
            "cross_repo": ["none: local"],
            "drift_watch": ["src/owner.py#STATE"],
        }
        contract = {
            "dimensions": dimensions,
            "coverage_file": "references/capability-coverage.json",
            "evals_file": "evals/evals.json",
            "skills": [
                record(router, "medium: routing", "L1", ["observed-not-executed: route matrix"], []),
                record("sample-close-loop", "high: lifecycle", "L3", ["executed-pass: focused test"], ["forward-1"]),
            ],
        }
        (router_root / "references" / "skill-depth.json").write_text(json.dumps(contract), encoding="utf-8")
        return repo, router

    def test_complete_contract_passes_without_a_fixed_skill_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.fixture(pathlib.Path(temporary))
            self.assertEqual(AUDITOR.audit(repo, router), [])

    def test_missing_category_and_weak_high_risk_evidence_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.fixture(pathlib.Path(temporary))
            router_root = repo / "skills" / router
            coverage_path = router_root / "references" / "capability-coverage.json"
            coverage = json.loads(coverage_path.read_text())
            coverage["categories"] = coverage["categories"][1:]
            coverage_path.write_text(json.dumps(coverage))
            contract_path = router_root / "references" / "skill-depth.json"
            contract = json.loads(contract_path.read_text())
            contract["skills"][1]["level"] = "L1"
            contract["skills"][1]["mechanical_controls"] = ["observed-not-executed: test"]
            contract_path.write_text(json.dumps(contract))
            problems = AUDITOR.audit(repo, router)
            self.assertTrue(any("coverage categories missing" in item for item in problems))
            self.assertTrue(any("high-risk skill" in item for item in problems))

    def test_authority_and_markdown_links_cannot_escape_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            repo, router = self.fixture(root)
            outside = root / "outside.py"
            outside.write_text("secret\n")
            router_root = repo / "skills" / router
            contract_path = router_root / "references" / "skill-depth.json"
            contract = json.loads(contract_path.read_text())
            contract["skills"][1]["authority"] = ["../outside.py"]
            contract_path.write_text(json.dumps(contract))
            (router_root / "references" / "skill-depth.md").write_text("[outside](../../../../outside.py)\n")
            problems = AUDITOR.audit(repo, router)
            self.assertTrue(any("escapes repository root" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
