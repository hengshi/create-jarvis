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
        categories = []
        for name in sorted(AUDITOR.REQUIRED_CATEGORIES):
            covered = name == "repo-specific"
            categories.append(
                {
                    "name": name,
                    "status": "covered" if covered else "not-applicable",
                    "surface_ids": ["close-surface"] if covered else [],
                    "capability_ids": ["close"] if covered else [],
                    "evidence": ["src/owner.py" if covered else "not used by fixture"],
                }
            )
        coverage = {
            "schema_version": 2,
            "repository": "sample",
            "fixed_revision": "a" * 40,
            "categories": categories,
            "surface_inventory": [
                {
                    "id": "close-surface",
                    "category": "repo-specific",
                    "name": "sample closure lifecycle",
                    "status": "present",
                    "entrypoints": ["src/owner.py#STATE"],
                    "evidence": ["src/owner.py"],
                    "capability_ids": ["close"],
                }
            ],
            "capabilities": [
                {
                    "id": "close",
                    "category": "repo-specific",
                    "task_family": "close sample lifecycle",
                    "trigger_examples": ["close a ready sample"],
                    "authority": ["src/owner.py#STATE"],
                    "entrypoints": ["src/owner.py#STATE"],
                    "state_or_resource_model": "ready -> closed; reject invalid state",
                    "proof": ["executed focused test"],
                    "route_eval_ids": ["forward-1"],
                    "disposition": "focused-loop",
                    "primary_home": "sample-close-loop",
                    "evidence": ["src/owner.py"],
                    "merge_split_rationale": "independent trigger and terminal-state proof",
                    "current_state": "valid at fixed revision",
                }
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

    def test_generic_category_without_semantic_capability_fields_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.fixture(pathlib.Path(temporary))
            coverage_path = (
                repo
                / "skills"
                / router
                / "references"
                / "capability-coverage.json"
            )
            coverage = json.loads(coverage_path.read_text())
            capability = coverage["capabilities"][0]
            for field in (
                "trigger_examples",
                "authority",
                "state_or_resource_model",
                "proof",
                "merge_split_rationale",
            ):
                capability.pop(field)
            coverage_path.write_text(json.dumps(coverage))
            problems = AUDITOR.audit(repo, router)
            for field in (
                "trigger_examples",
                "authority",
                "state_or_resource_model",
                "proof",
                "merge_split_rationale",
            ):
                self.assertTrue(
                    any(f"lacks {field}" in item for item in problems),
                    (field, problems),
                )

    def test_present_surface_and_delivered_capability_require_real_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.fixture(pathlib.Path(temporary))
            coverage_path = (
                repo
                / "skills"
                / router
                / "references"
                / "capability-coverage.json"
            )
            coverage = json.loads(coverage_path.read_text())
            coverage["surface_inventory"][0]["capability_ids"] = []
            coverage["capabilities"][0]["route_eval_ids"] = ["missing-route"]
            coverage_path.write_text(json.dumps(coverage))
            problems = AUDITOR.audit(repo, router)
            self.assertTrue(any("present surface close-surface lacks capability_ids" in item for item in problems))
            self.assertTrue(any("unknown route eval" in item for item in problems))
            self.assertTrue(any("lacks an executed-pass representative route eval" in item for item in problems))

    def test_schema_identity_and_surface_ownership_are_mechanically_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.fixture(pathlib.Path(temporary))
            coverage_path = (
                repo
                / "skills"
                / router
                / "references"
                / "capability-coverage.json"
            )
            coverage = json.loads(coverage_path.read_text())
            coverage["schema_version"] = 1
            coverage["repository"] = ""
            coverage["fixed_revision"] = "short"
            coverage["categories"][0]["evidence"] = ["REPLACE_WITH_REASON"]
            coverage["surface_inventory"][0]["capability_ids"] = []
            coverage_path.write_text(json.dumps(coverage))
            problems = AUDITOR.audit(repo, router)
            self.assertTrue(any("schema_version 2" in item for item in problems))
            self.assertTrue(any("missing repository identity" in item for item in problems))
            self.assertTrue(any("fixed_revision must be a full commit" in item for item in problems))
            self.assertTrue(any("unresolved template placeholders" in item for item in problems))
            self.assertTrue(any("capabilities lack surface inventory ownership" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
