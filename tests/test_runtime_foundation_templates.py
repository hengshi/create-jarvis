from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import plistlib
import subprocess

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_company(tmp_path: pathlib.Path) -> pathlib.Path:
    instantiate = load_module(
        REPO_ROOT / "scripts" / "instantiate_company_jarvis.py",
        "instantiate_company_jarvis_runtime_foundation_test",
    )
    fixture = json.loads(
        (REPO_ROOT / "tests" / "fixtures" / "acme-company-render-input.json").read_text(
            encoding="utf-8"
        )
    )
    destination = tmp_path / "company-jarvis"
    result = instantiate.copy_and_render(
        REPO_ROOT / "templates" / "company-jarvis" / "repo",
        destination,
        instantiate.extract_globals(fixture),
    )
    assert result["errors"] == []
    return destination


def install_args(root: pathlib.Path, mode: str) -> argparse.Namespace:
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


def fake_launchd(monkeypatch: pytest.MonkeyPatch, manager):
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
            return subprocess.CompletedProcess(command, code, "", "container unavailable" if code else "")
        if command[0].endswith(("jarvis-maintenance", "jarvis-self-improve")) and "--doctor" in command:
            return subprocess.CompletedProcess(command, 0, "", "")
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(manager.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(manager, "run", fake_run)
    return active, docker_probe


def last_json(output: str) -> dict[str, object]:
    start = output.rfind("\n{")
    return json.loads(output[start + 1 :] if start >= 0 else output)


def test_generated_runtime_foundation_is_executable_and_customer_neutral(tmp_path):
    company = render_company(tmp_path)
    foundation = company / "runtime-foundation"
    for relative in (
        "manage.py",
        "bin/jarvis-company-job.py",
        "bin/jarvis-maintenance",
        "bin/jarvis-self-improve",
    ):
        path = foundation / relative
        assert path.is_file()
        assert path.stat().st_mode & 0o111
    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in foundation.rglob("*")
        if path.is_file()
    )
    assert "{{" not in all_text
    assert "~/.hengshi" not in all_text
    assert "/Users/thomaschan" not in all_text


def test_native_install_reaches_one_healthy_scheduler_owner(tmp_path, monkeypatch, capsys):
    company = render_company(tmp_path)
    manager = load_module(company / "runtime-foundation" / "manage.py", "native_manager")
    active, _docker_probe = fake_launchd(monkeypatch, manager)
    root = tmp_path / "runtime-root"

    manager.install(install_args(root, "native"), inner=False)
    manager.status(root)
    status = last_json(capsys.readouterr().out)

    assert status["configured_mode"] == "native"
    assert status["scheduler_owner"] == "native"
    assert status["healthy"] is True
    assert len(active) == 2
    assert all("-native-" in label for label in active)


def test_cross_mode_install_is_rejected_without_changing_native_owner_or_config(tmp_path, monkeypatch):
    company = render_company(tmp_path)
    manager = load_module(company / "runtime-foundation" / "manage.py", "rollback_manager")
    active, docker_probe = fake_launchd(monkeypatch, manager)
    root = tmp_path / "runtime-root"
    manager.install(install_args(root, "native"), inner=False)
    docker_probe["returncode"] = 0
    with pytest.raises(ValueError, match="不支持原地改为 docker"):
        manager.install(install_args(root, "docker"), inner=False)

    assert all("-native-" in label for label in active)
    assert json.loads(manager.config_path(root).read_text(encoding="utf-8"))["mode"] == "native"


def test_initial_docker_install_requires_reachable_inner_jobs_and_has_one_owner(
    tmp_path, monkeypatch, capsys
):
    company = render_company(tmp_path)
    manager = load_module(company / "runtime-foundation" / "manage.py", "docker_manager")
    active, _docker_probe = fake_launchd(monkeypatch, manager)
    root = tmp_path / "runtime-root"
    manager.install(install_args(root, "docker"), inner=False)
    manager.status(root)
    status = last_json(capsys.readouterr().out)

    assert status["configured_mode"] == "docker"
    assert status["scheduler_owner"] == "docker"
    assert status["transport_reachable"] is True
    assert status["healthy"] is True
    assert len(active) == 2
    assert all("-docker-" in label for label in active)


def test_initial_docker_install_failure_creates_no_scheduler_owner_or_config(
    tmp_path, monkeypatch
):
    company = render_company(tmp_path)
    manager = load_module(company / "runtime-foundation" / "manage.py", "docker_failure_manager")
    active, docker_probe = fake_launchd(monkeypatch, manager)
    root = tmp_path / "runtime-root"
    docker_probe["returncode"] = 7

    with pytest.raises(ValueError, match="目标模式探活失败"):
        manager.install(install_args(root, "docker"), inner=False)

    assert active == set()
    assert not manager.config_path(root).exists()
