from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import pathlib
import plistlib
import subprocess
import tempfile
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeFoundationTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def render_company(self) -> pathlib.Path:
        instantiate = load_module(
            REPO_ROOT / "scripts" / "instantiate_company_jarvis.py",
            f"instantiate_company_jarvis_runtime_foundation_{id(self)}",
        )
        fixture = json.loads(
            (REPO_ROOT / "tests" / "fixtures" / "acme-company-render-input.json").read_text(
                encoding="utf-8"
            )
        )
        destination = self.tmp_path / "company-jarvis"
        result = instantiate.copy_and_render(
            REPO_ROOT / "templates" / "company-jarvis" / "repo",
            destination,
            instantiate.extract_globals(fixture),
        )
        self.assertEqual(result["errors"], [])
        return destination

    def install_args(self, root: pathlib.Path, mode: str) -> argparse.Namespace:
        return argparse.Namespace(
            root=str(root),
            company_repo="git@example.test:acme/company-jarvis.git",
            jarvis_box_cli="jarvis-box",
            mode=mode,
            release_helper=str(root.parent / "release-helper") if mode == "docker" else None,
            deployment_home=str(root.parent / "deployment") if mode == "docker" else None,
            container_root="/root/.acme-jarvis" if mode == "docker" else None,
            maintenance_cron="30 10 * * 1-5",
            self_improve_cron="30 18 * * 1-5",
        )

    def fake_launchd(self, manager):
        active: set[str] = set()
        docker_probe = {"returncode": 0}

        def fake_run(command, *, check=True, input_text=None):
            del check, input_text
            if command[:2] == ["launchctl", "print"]:
                label = command[2].rsplit("/", 1)[-1]
                code = 0 if label in active else 113
                return subprocess.CompletedProcess(command, code, "", "")
            if command[:2] == ["launchctl", "bootout"]:
                active.discard(command[2].rsplit("/", 1)[-1])
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[:2] == ["launchctl", "bootstrap"]:
                payload = plistlib.loads(pathlib.Path(command[3]).read_bytes())
                active.add(payload["Label"])
                return subprocess.CompletedProcess(command, 0, "", "")
            if "runtime-job" in command and "/usr/bin/test" in command:
                code = docker_probe["returncode"]
                return subprocess.CompletedProcess(
                    command,
                    code,
                    "",
                    "container unavailable" if code else "",
                )
            if command[0].endswith(("jarvis-maintenance", "jarvis-self-improve")) and "--doctor" in command:
                return subprocess.CompletedProcess(command, 0, "", "")
            raise AssertionError(f"unexpected command: {command}")

        system_patch = mock.patch.object(manager.platform, "system", return_value="Darwin")
        run_patch = mock.patch.object(manager, "run", side_effect=fake_run)
        system_patch.start()
        run_patch.start()
        self.addCleanup(system_patch.stop)
        self.addCleanup(run_patch.stop)
        return active, docker_probe

    @staticmethod
    def status_json(manager, root: pathlib.Path) -> dict[str, object]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            manager.status(root)
        return json.loads(output.getvalue())

    def test_generated_runtime_foundation_is_executable_and_customer_neutral(self):
        company = self.render_company()
        foundation = company / "runtime-foundation"
        for relative in (
            "manage.py",
            "bin/jarvis-company-job.py",
            "bin/jarvis-maintenance",
            "bin/jarvis-self-improve",
        ):
            path = foundation / relative
            self.assertTrue(path.is_file())
            self.assertTrue(path.stat().st_mode & 0o111)
        all_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in foundation.rglob("*")
            if path.is_file()
        )
        self.assertNotIn("{{", all_text)
        self.assertNotIn("~/.hengshi", all_text)
        self.assertNotIn("/Users/thomaschan", all_text)

    def test_native_install_reaches_one_healthy_scheduler_owner(self):
        company = self.render_company()
        manager = load_module(company / "runtime-foundation" / "manage.py", "native_manager")
        active, _docker_probe = self.fake_launchd(manager)
        root = self.tmp_path / "runtime-root"

        manager.install(self.install_args(root, "native"), inner=False)
        status = self.status_json(manager, root)

        self.assertEqual(status["configured_mode"], "native")
        self.assertEqual(status["scheduler_owner"], "native")
        self.assertIs(status["healthy"], True)
        self.assertEqual(len(active), 2)
        self.assertTrue(all("-native-" in label for label in active))

    def test_cross_mode_install_is_rejected_without_changing_native_owner_or_config(self):
        company = self.render_company()
        manager = load_module(company / "runtime-foundation" / "manage.py", "rollback_manager")
        active, _docker_probe = self.fake_launchd(manager)
        root = self.tmp_path / "runtime-root"

        manager.install(self.install_args(root, "native"), inner=False)
        with self.assertRaisesRegex(ValueError, "不支持原地改为 docker"):
            manager.install(self.install_args(root, "docker"), inner=False)

        self.assertTrue(all("-native-" in label for label in active))
        config = json.loads(manager.config_path(root).read_text(encoding="utf-8"))
        self.assertEqual(config["mode"], "native")

    def test_initial_docker_install_requires_reachable_inner_jobs_and_has_one_owner(self):
        company = self.render_company()
        manager = load_module(company / "runtime-foundation" / "manage.py", "docker_manager")
        active, _docker_probe = self.fake_launchd(manager)
        root = self.tmp_path / "runtime-root"

        manager.install(self.install_args(root, "docker"), inner=False)
        status = self.status_json(manager, root)

        self.assertEqual(status["configured_mode"], "docker")
        self.assertEqual(status["scheduler_owner"], "docker")
        self.assertIs(status["transport_reachable"], True)
        self.assertIs(status["healthy"], True)
        self.assertEqual(len(active), 2)
        self.assertTrue(all("-docker-" in label for label in active))

    def test_initial_docker_install_failure_creates_no_scheduler_owner_or_config(self):
        company = self.render_company()
        manager = load_module(company / "runtime-foundation" / "manage.py", "docker_failure_manager")
        active, docker_probe = self.fake_launchd(manager)
        root = self.tmp_path / "runtime-root"
        docker_probe["returncode"] = 7

        with self.assertRaisesRegex(ValueError, "目标模式探活失败"):
            manager.install(self.install_args(root, "docker"), inner=False)

        self.assertEqual(active, set())
        self.assertFalse(manager.config_path(root).exists())


if __name__ == "__main__":
    unittest.main()
