"""Isolated replay helper tests — tempfile + test mode, no real /e2e or /host-e2e."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HELPER = Path(__file__).resolve().parents[1] / "e2e" / "apple-container-claude" / "request-isolated-replay.sh"


def _setup_env(e2e_root: Path, bridge_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["REQUEST_ISOLATED_REPLAY_TEST_MODE"] = "1"
    env["REQUEST_ISOLATED_REPLAY_E2E_ROOT"] = str(e2e_root)
    env["REQUEST_ISOLATED_REPLAY_BRIDGE_ROOT"] = str(bridge_root)
    env["REPLAY_BRIDGE_POLL_SECONDS"] = "0"
    return env


def _run_helper(env: dict[str, str], **kwargs: str) -> subprocess.CompletedProcess:
    """Run the replay helper with --key value pairs from kwargs."""
    cmd = [str(HELPER)]
    for key, value in kwargs.items():
        cmd.extend([f"--{key.replace('_', '-')}", value])
    return subprocess.run(
        cmd,
        capture_output=True, text=True, env=env, timeout=10,
    )


class FirstSubmitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        tmp = Path(self.td.name)
        self.e2e = tmp / "e2e"
        self.bridge = tmp / "bridge"
        self.case_id = "test-case-1"
        self._create_dirs()
        self.env = _setup_env(self.e2e, self.bridge)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _create_dirs(self) -> None:
        visible = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"
        visible.mkdir(parents=True, exist_ok=True)
        (visible / "replay-prompt.md").write_text("## START context\nSymptom only.\n")
        parent = self.e2e / "work" / "replay-parent-worktrees" / self.case_id
        parent.mkdir(parents=True, exist_ok=True)
        (parent / "README.md").write_text("# Parent Snapshot\n")
        company = self.e2e / "output" / "company-jarvis"
        company.mkdir(parents=True, exist_ok=True)
        (company / "SKILL.md").write_text("entry skill")
        (company / "jarvis.toml").write_text('[runtime]\ncompany_slug = "test"\n')

    def _args_dict(self) -> dict[str, str]:
        return {
            "case_id": self.case_id,
            "visible_packet": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"),
            "parent_worktree": str(self.e2e / "work" / "replay-parent-worktrees" / self.case_id),
            "company_jarvis": str(self.e2e / "output" / "company-jarvis"),
            "destination": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id),
        }

    def test_first_submit_returns_75_and_creates_ready(self) -> None:
        args = self._args_dict()
        cp = _run_helper(self.env, **args)
        self.assertEqual(cp.returncode, 75, f"expected exit 75, got {cp.returncode}; stderr={cp.stderr}")
        req_root = self.bridge / self.case_id
        self.assertTrue((req_root / "READY").exists(), "READY file not created")
        self.assertTrue((req_root / "request.json").exists(), "request.json not created")
        self.assertTrue((req_root / "params-manifest.json").exists(), "params-manifest.json not created")
        self.assertTrue((req_root / "CREATED_AT").exists(), "CREATED_AT not created")
        self.assertTrue((req_root / "output").is_dir(), "output dir not created")
        self.assertTrue((req_root / "visible-packet").is_dir(), "visible-packet not copied")
        self.assertTrue((req_root / "parent-worktree").is_dir(), "parent-worktree not copied")

    def test_first_submit_writes_exact_manifest(self) -> None:
        args = self._args_dict()
        cp = _run_helper(self.env, **args)
        self.assertEqual(cp.returncode, 75)
        manifest_path = self.bridge / self.case_id / "params-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["case_id"], self.case_id)
        self.assertIn("visible-packet", manifest["visible_packet"])

    def test_empty_parent_fails_before_creating_partial_request(self) -> None:
        parent = self.e2e / "work" / "replay-parent-worktrees" / self.case_id
        (parent / "README.md").unlink()

        cp = _run_helper(self.env, **self._args_dict())

        self.assertEqual(cp.returncode, 1)
        self.assertIn("parent-worktree is empty", cp.stderr)
        self.assertFalse(
            (self.bridge / self.case_id).exists(),
            "invalid input must not leave a retry-blocking bridge request",
        )

    def test_second_call_same_params_still_returns_75(self) -> None:
        args = self._args_dict()
        cp1 = _run_helper(self.env, **args)
        self.assertEqual(cp1.returncode, 75)
        cp2 = _run_helper(self.env, **args)
        self.assertEqual(cp2.returncode, 75, f"second call should also exit 75, got {cp2.returncode}; stderr={cp2.stderr}")
        self.assertNotIn("CANCELLED", cp2.stderr)

    def test_done_collects_replay_code(self) -> None:
        args = self._args_dict()
        # First call - creates request
        cp1 = _run_helper(self.env, **args)
        self.assertEqual(cp1.returncode, 75)

        # Simulate host completing the replay
        req_root = self.bridge / self.case_id
        (req_root / "output" / "exit-code").write_text("3")
        (req_root / "output" / "replay-result.md").write_text("replay completed with findings")
        (req_root / "output" / "host-isolation-evidence.json").write_text(
            '{"mechanism": "secondary-apple-container"}'
        )
        (req_root / "DONE").touch()

        # Second call - should collect and return replay code
        cp2 = _run_helper(self.env, **args)
        self.assertEqual(cp2.returncode, 3, f"should exit with replay code 3, got {cp2.returncode}; stderr={cp2.stderr}")
        # Verify destination received the output
        dest = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id
        self.assertEqual((dest / "exit-code").read_text().strip(), "3")
        self.assertTrue((dest / "replay-result.md").exists())

    def test_override_vars_without_test_mode_fail(self) -> None:
        env = os.environ.copy()
        # NOT setting TEST_MODE=1
        env["REQUEST_ISOLATED_REPLAY_E2E_ROOT"] = "/tmp/test-e2e"
        cp = subprocess.run(
            [str(HELPER), "--case-id", "x", "--visible-packet", "/tmp/x", "--parent-worktree", "/tmp/x",
             "--company-jarvis", "/tmp/x", "--destination", "/tmp/x"],
            capture_output=True, text=True, env=env, timeout=10,
        )
        self.assertEqual(cp.returncode, 1, f"override without test mode should exit 1, got {cp.returncode}")
        self.assertIn("only allowed in test mode", cp.stderr)


class ParamMismatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        tmp = Path(self.td.name)
        self.e2e = tmp / "e2e"
        self.bridge = tmp / "bridge"
        self.case_id = "test-case-1"
        self._create_dirs()
        self.env = _setup_env(self.e2e, self.bridge)

    def tearDown(self) -> None:
        self.td.cleanup()

    def _create_dirs(self) -> None:
        visible = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"
        visible.mkdir(parents=True, exist_ok=True)
        (visible / "replay-prompt.md").write_text("START\n")
        parent = self.e2e / "work" / "replay-parent-worktrees" / self.case_id
        parent.mkdir(parents=True, exist_ok=True)
        (parent / "README.md").write_text("parent\n")
        company = self.e2e / "output" / "company-jarvis"
        company.mkdir(parents=True, exist_ok=True)
        (company / "SKILL.md").write_text("entry")
        (company / "jarvis.toml").write_text('[runtime]\ncompany_slug = "test"\n')

    def _args_dict(self, case_id: str | None = None) -> dict[str, str]:
        cid = case_id or self.case_id
        return {
            "case_id": cid,
            "visible_packet": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / cid / "visible-packet"),
            "parent_worktree": str(self.e2e / "work" / "replay-parent-worktrees" / cid),
            "company_jarvis": str(self.e2e / "output" / "company-jarvis"),
            "destination": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / cid),
        }

    def _setup_request(self, case_id: str) -> Path:
        # Create a valid first request so we can test replay
        # Create dirs for a different case
        cid2 = "test-case-2"
        visible2 = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / cid2 / "visible-packet"
        visible2.mkdir(parents=True, exist_ok=True)
        (visible2 / "replay-prompt.md").write_text("START\n")
        parent2 = self.e2e / "work" / "replay-parent-worktrees" / cid2
        parent2.mkdir(parents=True, exist_ok=True)
        (parent2 / "README.md").write_text("parent\n")
        dest2 = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / cid2
        dest2.mkdir(parents=True, exist_ok=True)

        args2 = {
            "case_id": cid2,
            "visible_packet": str(visible2),
            "parent_worktree": str(parent2),
            "company_jarvis": str(self.e2e / "output" / "company-jarvis"),
            "destination": str(dest2),
        }
        cp = _run_helper(self.env, **args2)
        assert cp.returncode == 75, f"setup failed: {cp.stderr}"
        return self.bridge / cid2

    def test_different_visible_packet_mismatch_fail_closed(self) -> None:
        # First create a valid request
        args = self._args_dict()
        cp1 = _run_helper(self.env, **args)
        self.assertEqual(cp1.returncode, 75)

        # Tamper with manifest
        manifest_path = self.bridge / self.case_id / "params-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["visible_packet"] = manifest["visible_packet"] + "-tampered"
        manifest_path.write_text(json.dumps(manifest))

        # Replay with same (original) args should detect manifest mismatch
        cp2 = _run_helper(self.env, **args)
        self.assertEqual(cp2.returncode, 1, f"param mismatch should exit 1, got {cp2.returncode}")
        self.assertIn("parameter mismatch", cp2.stderr)

    def test_different_case_id_mismatch_fail_closed(self) -> None:
        args = self._args_dict()
        cp1 = _run_helper(self.env, **args)
        self.assertEqual(cp1.returncode, 75)

        # Tamper manifest
        manifest_path = self.bridge / self.case_id / "params-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["case_id"] = "different-case"
        manifest_path.write_text(json.dumps(manifest))

        cp2 = _run_helper(self.env, **args)
        self.assertEqual(cp2.returncode, 1)
        self.assertIn("parameter mismatch", cp2.stderr)


class CorruptRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        tmp = Path(self.td.name)
        self.e2e = tmp / "e2e"
        self.bridge = tmp / "bridge"
        self.case_id = "test-case-1"
        self._create_dirs()
        self.env = _setup_env(self.e2e, self.bridge)
        self.args = {
            "case_id": self.case_id,
            "visible_packet": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"),
            "parent_worktree": str(self.e2e / "work" / "replay-parent-worktrees" / self.case_id),
            "company_jarvis": str(self.e2e / "output" / "company-jarvis"),
            "destination": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id),
        }

    def tearDown(self) -> None:
        self.td.cleanup()

    def _create_dirs(self) -> None:
        visible = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"
        visible.mkdir(parents=True, exist_ok=True)
        (visible / "replay-prompt.md").write_text("START\n")
        parent = self.e2e / "work" / "replay-parent-worktrees" / self.case_id
        parent.mkdir(parents=True, exist_ok=True)
        (parent / "README.md").write_text("parent\n")
        company = self.e2e / "output" / "company-jarvis"
        company.mkdir(parents=True, exist_ok=True)
        (company / "SKILL.md").write_text("entry")
        (company / "jarvis.toml").write_text('[runtime]\ncompany_slug = "test"\n')

    def _create_partial_request(self) -> Path:
        # Create a request dir by running first submit
        cp = _run_helper(self.env, **self.args)
        assert cp.returncode == 75, f"setup failed: {cp.stderr}"
        return self.bridge / self.case_id

    def test_missing_request_json_fail_closed(self) -> None:
        req_root = self._create_partial_request()
        (req_root / "request.json").unlink()
        cp = _run_helper(self.env, **self.args)
        self.assertEqual(cp.returncode, 1, f"missing request.json should exit 1, got {cp.returncode}")
        self.assertIn("corrupt", cp.stderr.lower())

    def test_missing_params_manifest_fail_closed(self) -> None:
        req_root = self._create_partial_request()
        (req_root / "params-manifest.json").unlink()
        cp = _run_helper(self.env, **self.args)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("corrupt", cp.stderr.lower())

    def test_missing_created_at_fail_closed(self) -> None:
        req_root = self._create_partial_request()
        (req_root / "CREATED_AT").unlink()
        cp = _run_helper(self.env, **self.args)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("corrupt", cp.stderr.lower())

    def test_missing_output_dir_fail_closed(self) -> None:
        req_root = self._create_partial_request()
        import shutil
        shutil.rmtree(req_root / "output")
        cp = _run_helper(self.env, **self.args)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("corrupt", cp.stderr.lower())


class TimeoutValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        tmp = Path(self.td.name)
        self.e2e = tmp / "e2e"
        self.bridge = tmp / "bridge"
        self.case_id = "test-case-1"
        visible = self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"
        visible.mkdir(parents=True, exist_ok=True)
        (visible / "replay-prompt.md").write_text("START\n")
        parent = self.e2e / "work" / "replay-parent-worktrees" / self.case_id
        parent.mkdir(parents=True, exist_ok=True)
        (parent / "README.md").write_text("parent\n")
        company = self.e2e / "output" / "company-jarvis"
        company.mkdir(parents=True, exist_ok=True)
        (company / "SKILL.md").write_text("entry")
        (company / "jarvis.toml").write_text('[runtime]\ncompany_slug = "test"\n')
        self.env = _setup_env(self.e2e, self.bridge)
        self.args = {
            "case_id": self.case_id,
            "visible_packet": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id / "visible-packet"),
            "parent_worktree": str(self.e2e / "work" / "replay-parent-worktrees" / self.case_id),
            "company_jarvis": str(self.e2e / "output" / "company-jarvis"),
            "destination": str(self.e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / self.case_id),
        }

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_negative_poll_seconds_fails(self) -> None:
        env = dict(self.env)
        env["REPLAY_BRIDGE_POLL_SECONDS"] = "-1"
        cp = _run_helper(env, **self.args)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("non-negative integer", cp.stderr)

    def test_zero_timeout_fails(self) -> None:
        env = dict(self.env)
        env["REPLAY_BRIDGE_TIMEOUT_SECONDS"] = "0"
        cp = _run_helper(env, **self.args)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("positive integer", cp.stderr)

    def test_non_numeric_poll_seconds_fails(self) -> None:
        env = dict(self.env)
        env["REPLAY_BRIDGE_POLL_SECONDS"] = "abc"
        cp = _run_helper(env, **self.args)
        self.assertEqual(cp.returncode, 1)

    def test_absolute_timeout_kills_with_124(self) -> None:
        env = dict(self.env)
        env["REPLAY_BRIDGE_TIMEOUT_SECONDS"] = "3600"  # generous for first call
        # First call creates request
        cp1 = _run_helper(env, **self.args)
        self.assertEqual(cp1.returncode, 75)

        # Manually backdate CREATED_AT to trigger timeout on next call
        req_root = self.bridge / self.case_id
        (req_root / "CREATED_AT").write_text("1")  # epoch 1 → way past any timeout

        env["REPLAY_BRIDGE_TIMEOUT_SECONDS"] = "1"
        cp2 = _run_helper(env, **self.args)
        self.assertEqual(cp2.returncode, 124, f"absolute timeout should exit 124, got {cp2.returncode}; stderr={cp2.stderr}")
        self.assertTrue((req_root / "CANCELLED").exists(), "CANCELLED should be written on timeout")
        self.assertFalse((req_root / "DONE").exists(), "the host monitor owns the terminal DONE marker")


class TestModeGateTests(unittest.TestCase):
    def test_no_test_mode_uses_production_paths(self) -> None:
        td = tempfile.TemporaryDirectory()
        tmp = Path(td.name)
        # Create minimal production-like structure
        prod_e2e = tmp / "production-e2e"
        case_id = "test-case-1"
        visible = prod_e2e / "output" / "company-jarvis" / "_bootstrap" / "history-replay-runs" / case_id / "visible-packet"
        visible.mkdir(parents=True, exist_ok=True)
        (visible / "replay-prompt.md").write_text("START\n")
        parent = prod_e2e / "work" / "replay-parent-worktrees" / case_id
        parent.mkdir(parents=True, exist_ok=True)
        (parent / "README.md").write_text("parent\n")
        company = prod_e2e / "output" / "company-jarvis"
        company.mkdir(parents=True, exist_ok=True)
        (company / "SKILL.md").write_text("entry")
        (company / "jarvis.toml").write_text('[runtime]\ncompany_slug = "test"\n')

        # Without test mode, production paths /e2e and /host-e2e are required
        env = os.environ.copy()
        env["REPLAY_BRIDGE_POLL_SECONDS"] = "0"
        # NOT setting test mode env vars
        cp = subprocess.run(
            [str(HELPER),
             "--case-id", case_id,
             "--visible-packet", f"/e2e/output/company-jarvis/_bootstrap/history-replay-runs/{case_id}/visible-packet",
             "--parent-worktree", f"/e2e/work/replay-parent-worktrees/{case_id}",
             "--company-jarvis", "/e2e/output/company-jarvis",
             "--destination", f"/e2e/output/company-jarvis/_bootstrap/history-replay-runs/{case_id}"],
            capture_output=True, text=True, env=env, timeout=10,
        )
        # Should fail because /e2e doesn't exist
        self.assertNotEqual(cp.returncode, 0)
        td.cleanup()


if __name__ == "__main__":
    unittest.main()
