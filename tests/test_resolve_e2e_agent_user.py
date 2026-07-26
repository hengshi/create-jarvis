"""Tests for safe runtime-agent UID/GID mapping in the Linux E2E image."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER = REPO_ROOT / "scripts" / "resolve_e2e_agent_user.sh"
CONTROLLED_E2E = REPO_ROOT / "scripts" / "run_customer_bootstrap_e2e.sh"


class ResolveE2EAgentUserTests(unittest.TestCase):
    def _write_command(self, root: Path, name: str, body: str) -> None:
        path = root / name
        path.write_text("#!/usr/bin/env bash\nset -eu\n" + body, encoding="utf-8")
        path.chmod(0o755)

    def test_reuses_matching_uid_1000_container_user(self) -> None:
        """Typical Ubuntu UID/GID 1000 collision must not abort the E2E."""
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp)
            self._write_command(
                fake_bin,
                "getent",
                """
case "$1:$2" in
  passwd:1000) printf '%s\n' 'ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash' ;;
  group:1000) printf '%s\n' 'ubuntu:x:1000:' ;;
  *) exit 2 ;;
esac
""",
            )
            self._write_command(
                fake_bin,
                "id",
                """
case "$1:$2" in
  -u:jarvis-box) printf '%s\n' '10001' ;;
  -g:ubuntu) printf '%s\n' '1000' ;;
  *) exit 2 ;;
esac
""",
            )
            for command in ("groupadd", "useradd"):
                self._write_command(fake_bin, command, "exit 97\n")
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"
            result = subprocess.run(
                ["bash", str(RESOLVER), "1000", "1000", "jarvis-box", "e2e-agent"],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ubuntu")

    def test_controlled_e2e_persists_and_reuses_resolved_user(self) -> None:
        text = CONTROLLED_E2E.read_text(encoding="utf-8")
        self.assertIn("resolve_e2e_agent_user.sh", text)
        self.assertIn("/e2e/runtime-agent-user", text)
        self.assertIn(r'runuser -u \"\$runtime_agent_user\"', text)
        self.assertNotIn("requested agent UID already belongs", text)


if __name__ == "__main__":
    unittest.main()
