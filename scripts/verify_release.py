#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


TAG_PATTERN = re.compile(r"^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def verify(tag: str, changelog: str) -> None:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ValueError(f"release tag must be semantic version vX.Y.Z, got {tag!r}")
    version = tag[1:]
    if not re.search(rf"^## {re.escape(version)}(?:\s|$)", changelog, re.MULTILINE):
        raise ValueError(f"CHANGELOG.md has no release section for {version}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: scripts/verify_release.py vX.Y.Z", file=sys.stderr)
        return 2
    try:
        verify(argv[1], Path("CHANGELOG.md").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"create_jarvis_release=ok tag={argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
