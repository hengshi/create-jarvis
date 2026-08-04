from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_auditor():
    path = ROOT / "templates" / "replay" / "audit_skill_depth.py"
    spec = importlib.util.spec_from_file_location("audit_skill_depth", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepositorySkillDepthTests(unittest.TestCase):
    def build_fixture(self, root: pathlib.Path) -> tuple[pathlib.Path, str]:
        repo = root / "repo"
        router = "sample-development"
        router_root = repo / "skills" / router
        focused_root = repo / "skills" / "sample-close-loop"
        (repo / "src").mkdir(parents=True)
        (repo / "src" / "owner.py").write_text("STATE = 'ready'\n", encoding="utf-8")
        for package in (router_root, focused_root):
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(
                f"---\nname: {package.name}\ndescription: Use when sample work arrives.\n---\n",
                encoding="utf-8",
            )
        router_skill = router_root / "SKILL.md"
        router_skill.write_text(
            router_skill.read_text(encoding="utf-8")
            + "\nRoute `sample-close-loop`. Read references/skill-depth.md and references/skill-depth.json. "
            + "Keep evals/evals.json hidden and run scripts/audit_skill_depth.py.\n",
            encoding="utf-8",
        )
        (router_root / "references").mkdir()
        (router_root / "references" / "skill-depth.md").write_text(
            "# Depth\n\n[owner](../../../src/owner.py)\n", encoding="utf-8"
        )
        (router_root / "evals").mkdir()
        evals = {
            "evals": [
                {
                    "id": "route-1",
                    "kind": "should-trigger",
                    "prompt": "close it",
                    "expected_route": ["sample-close-loop"],
                    "forbidden_routes": [router],
                    "invariants": ["close once"],
                    "proof": ["test"],
                    "oracle_source": "src/owner.py",
                },
                {
                    "id": "negative-1",
                    "kind": "must-not-trigger",
                    "prompt": "unrelated docs",
                    "expected_route": [router],
                    "forbidden_routes": ["sample-close-loop"],
                    "invariants": ["no lifecycle edit"],
                    "proof": ["diff"],
                    "oracle_source": "src/owner.py",
                },
                {
                    "id": "forward-1",
                    "kind": "forward",
                    "prompt": "new close path",
                    "expected_route": ["sample-close-loop"],
                    "forbidden_routes": [router],
                    "invariants": ["wake then join"],
                    "proof": ["test"],
                    "oracle_source": "src/owner.py",
                },
            ]
        }
        (router_root / "evals" / "evals.json").write_text(json.dumps(evals), encoding="utf-8")
        record = lambda name, ids: {
            "name": name,
            "risk": "high: lifecycle" if name != router else "normal: routing",
            "level": "L3" if name != router else "L1",
            "authority": ["src/owner.py#STATE"],
            "entrypoints": ["src/owner.py"],
            "transitions": ["ready -> closing -> closed"],
            "mechanical_controls": ["executed-pass: sample test"],
            "forward_eval_ids": ids,
            "cross_repo": ["none: local"],
            "drift_watch": ["src/owner.py#STATE"],
        }
        contract = {
            "schema_version": 1,
            "repository": "sample",
            "fixed_revision": "a" * 40,
            "router": router,
            "dimensions": {
                "implementation_anchors": "references/skill-depth.md",
                "mechanical_controls": "scripts/audit_skill_depth.py",
                "risk_promotion": "per skill",
                "runtime_hidden_forward_eval": "evals/evals.json",
                "cross_repository_closure": "per skill",
                "drift_self_improve": "per skill",
            },
            "skills": [record(router, ["negative-1"]), record("sample-close-loop", ["route-1", "forward-1"])],
            "evals_file": "evals/evals.json",
        }
        (router_root / "references" / "skill-depth.json").write_text(json.dumps(contract), encoding="utf-8")
        (router_root / "scripts").mkdir()
        shutil.copy2(ROOT / "templates" / "replay" / "audit_skill_depth.py", router_root / "scripts" / "audit_skill_depth.py")
        return repo, router

    def test_complete_depth_contract_passes(self) -> None:
        auditor = load_auditor()
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.build_fixture(pathlib.Path(temporary))
            self.assertEqual(auditor.audit(repo, router), [])

    def test_missing_authority_and_eval_are_reported(self) -> None:
        auditor = load_auditor()
        with tempfile.TemporaryDirectory() as temporary:
            repo, router = self.build_fixture(pathlib.Path(temporary))
            contract_path = repo / "skills" / router / "references" / "skill-depth.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["skills"][1]["authority"] = ["src/missing.py#STATE"]
            contract["skills"][1]["forward_eval_ids"] = ["missing-eval"]
            contract_path.write_text(json.dumps(contract), encoding="utf-8")

            problems = auditor.audit(repo, router)
            self.assertTrue(any("authority path missing" in problem for problem in problems))
            self.assertTrue(any("unknown eval id" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
