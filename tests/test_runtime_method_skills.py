from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_installer():
    path = ROOT / "scripts" / "install_runtime_method_skills.py"
    spec = importlib.util.spec_from_file_location("install_runtime_method_skills", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeMethodSkillsTests(unittest.TestCase):
    def test_install_and_doctor_close_runtime_discovery_contract(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            manifest = installer.install(skills_root)
            report = installer.doctor(skills_root)

            self.assertEqual(report["status"], "ok")
            self.assertEqual(
                report["packages"],
                [
                    "jarvis-self-improve-skill",
                    "ponytail",
                    "stop-slop",
                    "writing-durable-docs",
                ],
            )
            self.assertEqual(report["method_commit"], manifest["method_commit"])

    def test_doctor_detects_method_skill_drift(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            installer.install(skills_root)
            skill = skills_root / "jarvis-self-improve-skill" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")

            report = installer.doctor(skills_root)
            self.assertEqual(report["status"], "failed")
            self.assertIn("content drift: jarvis-self-improve-skill", report["problems"])

    def test_install_refuses_to_overwrite_an_unowned_same_name_skill(self) -> None:
        installer = load_installer()
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            collision = skills_root / "jarvis-self-improve-skill"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("customer-owned\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "unowned or drifted"):
                installer.install(skills_root)
            self.assertEqual(
                (collision / "SKILL.md").read_text(encoding="utf-8"),
                "customer-owned\n",
            )


if __name__ == "__main__":
    unittest.main()
