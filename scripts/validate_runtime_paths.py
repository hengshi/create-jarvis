#!/usr/bin/env python3
"""Validate physical separation of construction, source and runtime paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROLES = ("construction_workspace", "company_repository", "deployment_home")


def absolute_path(value: str, role: str) -> Path:
    raw = Path(value).expanduser()
    if not raw.is_absolute():
        raise ValueError(f"{role} must be absolute")
    resolved = raw.resolve(strict=False)
    if resolved in {Path(resolved.anchor), Path.home().resolve()}:
        raise ValueError(f"{role} must not be a filesystem root or the user HOME")
    return resolved


def overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def validate(construction: str, company: str, deployment: str) -> dict[str, str]:
    paths = {
        "construction_workspace": absolute_path(construction, "construction workspace"),
        "company_repository": absolute_path(company, "Company Jarvis repository"),
        "deployment_home": absolute_path(deployment, "Jarvis Box deployment home"),
    }
    for index, left_role in enumerate(ROLES):
        for right_role in ROLES[index + 1 :]:
            if overlaps(paths[left_role], paths[right_role]):
                raise ValueError(
                    f"{left_role} and {right_role} must be physically disjoint: "
                    f"{paths[left_role]} <> {paths[right_role]}"
                )
    return {role: str(paths[role]) for role in ROLES}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--construction-workspace", required=True)
    parser.add_argument("--company-repository", required=True)
    parser.add_argument("--deployment-home", required=True)
    args = parser.parse_args()
    try:
        paths = validate(
            args.construction_workspace,
            args.company_repository,
            args.deployment_home,
        )
        report = {"status": "ok", "paths": paths}
        code = 0
    except ValueError as exc:
        report = {"status": "failed", "problems": [str(exc)]}
        code = 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
