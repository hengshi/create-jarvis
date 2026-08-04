from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "install_runtime_method_skills", ROOT / "scripts" / "install_runtime_method_skills.py"
)
assert SPEC and SPEC.loader
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


@unittest.skipIf(os.geteuid() == 0, "installer deliberately rejects root")
class RuntimeMethodSkillsTests(unittest.TestCase):
    def test_install_and_doctor_close_owned_content_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            manifest = INSTALLER.install(skills_root)
            report = INSTALLER.doctor(skills_root)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["method_commit"], manifest["method_commit"])
            self.assertIn("jarvis-self-improve-skill", report["packages"])

    def test_dirty_checkout_cannot_be_claimed_as_head(self) -> None:
        with mock.patch.object(INSTALLER, "git_output", side_effect=["a" * 40, " M SKILL.md"]):
            with self.assertRaisesRegex(RuntimeError, "dirty create-jarvis checkout"):
                INSTALLER.method_revision()

    def test_mid_swap_failure_rolls_back_every_package_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            original = INSTALLER.install(skills_root)
            before = {
                name: INSTALLER.package_digest(skills_root / name)
                for name in INSTALLER.METHOD_PACKAGES
            }
            original_replace = pathlib.Path.replace
            calls = 0

            def fail_mid_swap(source: pathlib.Path, destination: pathlib.Path):
                nonlocal calls
                if source.parent.name == "staged":
                    calls += 1
                    if calls == 2:
                        raise OSError("injected swap failure")
                return original_replace(source, destination)

            with mock.patch.object(pathlib.Path, "replace", fail_mid_swap):
                with self.assertRaisesRegex(OSError, "injected swap failure"):
                    INSTALLER.install(skills_root)
            after = {
                name: INSTALLER.package_digest(skills_root / name)
                for name in INSTALLER.METHOD_PACKAGES
            }
            self.assertEqual(after, before)
            installed = json.loads(
                (skills_root / INSTALLER.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(installed, original)

    def test_unowned_same_name_skill_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skills_root = pathlib.Path(temporary) / "skills"
            collision = skills_root / "jarvis-self-improve-skill"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("customer-owned\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unowned or drifted"):
                INSTALLER.install(skills_root)
            self.assertEqual(
                (collision / "SKILL.md").read_text(encoding="utf-8"),
                "customer-owned\n",
            )

    def test_docker_transport_installs_and_doctors_persistent_agent_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            runtime_home = root / "agent-home"
            runtime_home.mkdir()
            deployment_home = root / "deployment"
            deployment_home.mkdir()
            helper = root / "deploy-production.sh"
            helper.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail
                    shift
                    test "$1" = runtime-job
                    shift
                    test "$1" = sh
                    shift
                    test "$1" = -ceu
                    script="$2"
                    shift 3
                    command_name="$1"
                    skills_root="${2/\/home\/jarvis/$FAKE_RUNTIME_HOME}"
                    method_commit="$3"
                    HOME="$FAKE_RUNTIME_HOME" sh -ceu "$script" -- "$command_name" "$skills_root" "$method_commit"
                    """
                ),
                encoding="utf-8",
            )
            helper.chmod(0o700)
            environment = {**os.environ, "FAKE_RUNTIME_HOME": str(runtime_home)}
            wrapper = ROOT / "scripts" / "install_runtime_method_skills_docker.sh"
            base = [
                str(wrapper),
                "--jarvis-box-helper",
                str(helper),
                "--deployment-home",
                str(deployment_home),
                "--agent",
                "codex",
            ]
            installed = subprocess.run(
                [str(wrapper), "install", *base[1:]],
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            discovered = runtime_home / ".codex" / "skills" / "jarvis-self-improve-skill" / "SKILL.md"
            self.assertTrue(discovered.is_file())
            checked = subprocess.run(
                [str(wrapper), "doctor", *base[1:]],
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)


if __name__ == "__main__":
    unittest.main()
