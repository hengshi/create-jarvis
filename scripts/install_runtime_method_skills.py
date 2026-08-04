#!/usr/bin/env python3
"""Install create-jarvis method skills into an explicit Agent skill root.

Company Jarvis repositories intentionally do not vendor generic method skills.
This installer closes the other half of that contract: the pinned create-jarvis
checkout is the source, the selected Agent skill root is the destination, and a
content manifest makes the installed revision auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def method_revision() -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def package_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        if not child.is_file() or child.is_symlink():
            continue
        relative = child.relative_to(path).as_posix().encode("utf-8")
        payload = child.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def expected_manifest() -> dict[str, object]:
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
        "method_commit": method_revision(),
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
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def install(skills_root: Path) -> dict[str, object]:
    skills_root.mkdir(parents=True, exist_ok=True)
    manifest = expected_manifest()
    previous_manifest_path = skills_root / MANIFEST_NAME
    try:
        previous = json.loads(previous_manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        previous = None
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"refusing upgrade with unreadable ownership manifest: {exc}") from exc
    previous_packages = previous.get("packages") if isinstance(previous, dict) else None

    # Never overwrite an unrelated or locally edited package merely because it
    # has the same well-known name. A prior create-jarvis manifest plus an
    # unchanged installed digest is the ownership proof for upgrades.
    for output_name in METHOD_PACKAGES:
        destination = skills_root / output_name
        if not destination.exists():
            continue
        if destination.is_symlink() or not destination.is_dir():
            raise RuntimeError(f"refusing to replace non-directory skill: {destination}")
        previous_record = (
            previous_packages.get(output_name)
            if isinstance(previous_packages, dict)
            else None
        )
        previous_digest = (
            previous_record.get("sha256") if isinstance(previous_record, dict) else None
        )
        if not previous_digest or package_digest(destination) != previous_digest:
            raise RuntimeError(
                f"refusing to overwrite unowned or drifted method skill: {destination}"
            )

    for output_name, template_name in sorted(METHOD_PACKAGES.items()):
        source = PACKAGES_ROOT / template_name
        destination = skills_root / output_name
        staged = Path(tempfile.mkdtemp(prefix=f".{output_name}.", dir=skills_root))
        backup = staged / "previous"
        try:
            shutil.copytree(source, staged / output_name)
            replacement = staged / output_name
            if destination.exists():
                destination.replace(backup)
            try:
                replacement.replace(destination)
            except Exception:
                if backup.exists() and not destination.exists():
                    backup.replace(destination)
                raise
        finally:
            shutil.rmtree(staged, ignore_errors=True)
    write_json_atomic(skills_root / MANIFEST_NAME, manifest)
    return manifest


def doctor(skills_root: Path) -> dict[str, object]:
    expected = expected_manifest()
    problems: list[str] = []
    manifest_path = skills_root / MANIFEST_NAME
    try:
        installed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        installed = None
        problems.append(f"manifest unreadable: {exc}")
    if installed != expected:
        problems.append("installed manifest does not match the pinned create-jarvis checkout")
    expected_packages = expected["packages"]
    assert isinstance(expected_packages, dict)
    for name, record in expected_packages.items():
        destination = skills_root / name
        if not (destination / "SKILL.md").is_file():
            problems.append(f"missing skill: {name}")
            continue
        assert isinstance(record, dict)
        if package_digest(destination) != record["sha256"]:
            problems.append(f"content drift: {name}")
    return {
        "status": "ok" if not problems else "failed",
        "skills_root": str(skills_root.resolve()),
        "method_commit": expected["method_commit"],
        "packages": sorted(expected_packages),
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("install", "doctor"))
    parser.add_argument("--skills-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args.skills_root)
        report = doctor(args.skills_root)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        report = {"status": "failed", "problems": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
