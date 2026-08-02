from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEGACY_NAME = "create-jarvis" + "-skill"


class MethodIdentityContractTest(unittest.TestCase):
    def test_root_skill_has_one_canonical_identity(self):
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("\nname: create-jarvis\n", root_skill)

    def test_durable_method_guidance_does_not_use_legacy_identity(self):
        roots = [
            ROOT / "SKILL.md",
            ROOT / "playbooks",
            ROOT / "templates" / "company-jarvis",
            ROOT / "templates" / "skill-packages",
        ]
        violations = []
        for root in roots:
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or "evals" in path.parts:
                    continue
                if path.suffix not in {".md", ".json", ".yaml", ".yml", ".toml", ".py"}:
                    continue
                if LEGACY_NAME in path.read_text(encoding="utf-8"):
                    violations.append(str(path.relative_to(ROOT)))
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
