#!/usr/bin/env python3
"""Install pinned create-jarvis method skills into one Agent skill root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = ROOT / "templates" / "skill-packages"
METHOD_PACKAGES = {
    "jarvis-self-improve-skill": "self-improve-skill",
    "ponytail": "ponytail",
    "stop-slop": "stop-slop",
    "writing-durable-docs": "writing-durable-docs",
}
MANIFEST_NAME = "create-jarvis-method-skills.json"
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def method_revision() -> str:
    revision = git_output("rev-parse", "HEAD").lower()
    if not COMMIT_RE.fullmatch(revision):
        raise RuntimeError("create-jarvis HEAD is not a full Git commit")
    if git_output("status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError(
            "refusing to install method skills from a dirty create-jarvis checkout"
        )
    return revision


def normalize_method_commit(value: str | None) -> str:
    revision = (value or method_revision()).strip().lower()
    if not COMMIT_RE.fullmatch(revision):
        raise RuntimeError("method commit must be a full 40-character Git commit")
    return revision


def package_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            raise RuntimeError(f"method skill source must not contain symlinks: {child}")
        if not child.is_file():
            continue
        relative = child.relative_to(path).as_posix().encode("utf-8")
        payload = child.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def expected_manifest(method_commit: str | None = None) -> dict[str, object]:
    packages: dict[str, dict[str, str]] = {}
    for output_name, template_name in sorted(METHOD_PACKAGES.items()):
        source = PACKAGES_ROOT / template_name
        if not (source / "SKILL.md").is_file():
            raise RuntimeError(f"missing method skill template: {source}")
        packages[output_name] = {
            "source": f"templates/skill-packages/{template_name}",
            "sha256": package_digest(source),
        }
    return {
        "schema_version": 1,
        "source": "create-jarvis",
        "method_commit": normalize_method_commit(method_commit),
        "packages": packages,
    }


def write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.chmod(temporary, 0o600)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def require_current_user_root(skills_root: Path, *, create: bool) -> Path:
    if os.geteuid() == 0:
        raise RuntimeError("refusing to install or inspect method skills as root")
    if skills_root.is_symlink():
        raise RuntimeError(f"skills root must not be a symlink: {skills_root}")
    if create:
        skills_root.mkdir(parents=True, exist_ok=True)
    if not skills_root.is_dir():
        raise RuntimeError(f"skills root is not a directory: {skills_root}")
    skills_root = skills_root.resolve()
    if skills_root.stat().st_uid != os.geteuid():
        raise RuntimeError(f"skills root is not owned by the current OS user: {skills_root}")
    return skills_root


def read_previous_manifest(path: Path) -> dict[str, object] | None:
    if path.is_symlink():
        raise RuntimeError(f"ownership manifest must not be a symlink: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"refusing upgrade with unreadable ownership manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("refusing upgrade with invalid ownership manifest")
    return value


def install(skills_root: Path, method_commit: str | None = None) -> dict[str, object]:
    skills_root = require_current_user_root(skills_root, create=True)
    manifest = expected_manifest(method_commit)
    manifest_path = skills_root / MANIFEST_NAME
    previous = read_previous_manifest(manifest_path)
    previous_packages = previous.get("packages") if previous else None

    for output_name in METHOD_PACKAGES:
        destination = skills_root / output_name
        if not destination.exists():
            continue
        if destination.is_symlink() or not destination.is_dir():
            raise RuntimeError(f"refusing to replace non-directory skill: {destination}")
        if destination.stat().st_uid != os.geteuid():
            raise RuntimeError(f"method skill is not owned by the current OS user: {destination}")
        record = (
            previous_packages.get(output_name)
            if isinstance(previous_packages, dict)
            else None
        )
        previous_digest = record.get("sha256") if isinstance(record, dict) else None
        if not previous_digest or package_digest(destination) != previous_digest:
            raise RuntimeError(
                f"refusing to overwrite unowned or drifted method skill: {destination}"
            )

    transaction = Path(tempfile.mkdtemp(prefix=".create-jarvis-method.", dir=skills_root))
    staged_root = transaction / "staged"
    backup_root = transaction / "backup"
    staged_root.mkdir()
    backup_root.mkdir()
    manifest_backup = manifest_path.read_bytes() if manifest_path.is_file() else None
    swapped: list[str] = []
    try:
        for output_name, template_name in sorted(METHOD_PACKAGES.items()):
            shutil.copytree(PACKAGES_ROOT / template_name, staged_root / output_name)

        for output_name in sorted(METHOD_PACKAGES):
            destination = skills_root / output_name
            backup = backup_root / output_name
            replacement = staged_root / output_name
            if destination.exists():
                destination.replace(backup)
            replacement.replace(destination)
            swapped.append(output_name)
        write_json_atomic(manifest_path, manifest)
    except Exception:
        for output_name in reversed(sorted(METHOD_PACKAGES)):
            destination = skills_root / output_name
            backup = backup_root / output_name
            if output_name in swapped and destination.exists():
                shutil.rmtree(destination)
            if backup.exists():
                backup.replace(destination)
        if manifest_backup is None:
            manifest_path.unlink(missing_ok=True)
        else:
            handle, temporary_name = tempfile.mkstemp(
                prefix=f".{MANIFEST_NAME}.rollback.", dir=skills_root
            )
            with os.fdopen(handle, "wb") as stream:
                stream.write(manifest_backup)
            Path(temporary_name).replace(manifest_path)
        raise
    finally:
        shutil.rmtree(transaction, ignore_errors=True)
    return manifest


def doctor(skills_root: Path, method_commit: str | None = None) -> dict[str, object]:
    skills_root = require_current_user_root(skills_root, create=False)
    expected = expected_manifest(method_commit)
    problems: list[str] = []
    try:
        installed = read_previous_manifest(skills_root / MANIFEST_NAME)
    except RuntimeError as exc:
        installed = None
        problems.append(str(exc))
    if installed != expected:
        problems.append("installed manifest does not match the pinned create-jarvis source")
    packages = expected["packages"]
    assert isinstance(packages, dict)
    for name, record in packages.items():
        destination = skills_root / name
        if not (destination / "SKILL.md").is_file():
            problems.append(f"missing skill: {name}")
            continue
        assert isinstance(record, dict)
        if package_digest(destination) != record["sha256"]:
            problems.append(f"content drift: {name}")
    return {
        "status": "ok" if not problems else "failed",
        "skills_root": str(skills_root),
        "method_commit": expected["method_commit"],
        "packages": sorted(packages),
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("install", "doctor"))
    parser.add_argument("--skills-root", required=True, type=Path)
    parser.add_argument(
        "--method-commit",
        help="Exact commit for a source materialized with git archive",
    )
    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args.skills_root, args.method_commit)
        report = doctor(args.skills_root, args.method_commit)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        report = {"status": "failed", "problems": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
