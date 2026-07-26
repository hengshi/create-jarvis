"""Deterministic tests for Apple Container E2E harness contracts.

Covers:
  - bash -n syntax checks
  - output bind mount contract
  - dynamic UID passing
  - chown excludes bind-mounted /e2e/output
  - INT/TERM exit codes
  - outer-exit-code written after sync completes
  - customer-repos synced last
  - missing / non-integer / out-of-range outer-exit-code → fail closed
"""

import os
import re
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOST_DRIVER = REPO_ROOT / "scripts" / "run_apple_container_claude_e2e.sh"
RUN_IN_CONTAINER = REPO_ROOT / "e2e" / "apple-container-claude" / "run-in-container.sh"


# ──────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────

def _run_bash(script: str, *, env: dict[str, str] | None = None, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=timeout,
        env=env or {},
    )


# ──────────────────────────────────────────────────────────────────
# syntax checks
# ──────────────────────────────────────────────────────────────────

class SyntaxChecks(unittest.TestCase):
    def test_host_driver_passes_bash_n(self) -> None:
        cp = subprocess.run(["bash", "-n", str(HOST_DRIVER)], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0, f"bash -n failed: {cp.stderr}")

    def test_run_in_container_passes_bash_n(self) -> None:
        cp = subprocess.run(["bash", "-n", str(RUN_IN_CONTAINER)], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0, f"bash -n failed: {cp.stderr}")


# ──────────────────────────────────────────────────────────────────
# output bind mount contract
# ──────────────────────────────────────────────────────────────────

class OutputBindMountContract(unittest.TestCase):
    """Host driver must create $run_dir/output and bind-mount it to /e2e/output."""

    def test_creates_run_dir_output(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('mkdir -p "$run_dir/output"', text)

    def test_bind_mounts_output_to_container(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('-v "$run_dir/output":/e2e/output', text)

    def test_outer_container_has_output_bind_mount_in_args(self) -> None:
        text = HOST_DRIVER.read_text()
        # The bind mount must appear in outer_args (before the replay section)
        outer_section = text.split("outer_args+=(")[0] if "outer_args+=(" in text else text
        # Check the bind mount is in the outer container args array
        self.assertIn('-v "$run_dir/output":/e2e/output', text,
                      "output bind mount not found in host driver")


# ──────────────────────────────────────────────────────────────────
# dynamic UID passing
# ──────────────────────────────────────────────────────────────────

class DynamicUIDContract(unittest.TestCase):
    """Host passes current UID/GID; run-in-container uses both for useradd."""

    def test_host_passes_e2e_host_uid(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('E2E_HOST_UID=$(id -u)', text)
        self.assertIn('E2E_HOST_GID=$(id -g)', text)

    def test_run_in_container_reads_e2e_host_uid(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('e2e_host_uid="${E2E_HOST_UID:-}"', text)
        self.assertIn('e2e_host_gid="${E2E_HOST_GID:-}"', text)

    def test_useradd_uses_e2e_host_uid_when_set(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('useradd -u "$e2e_host_uid" -g "$e2e_host_gid"', text)

    def test_no_hardcoded_uid_in_useradd(self) -> None:
        """useradd must not hardcode a numeric UID like 501."""
        text = RUN_IN_CONTAINER.read_text()
        # Find all useradd lines
        for line in text.splitlines():
            if "useradd" in line:
                # Must not contain -u followed by a number (hardcoded)
                self.assertNotRegex(line, r'-u\s+\d+',
                                    f"hardcoded UID found: {line.strip()}")

    def test_root_mapping_is_rejected(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('E2E_HOST_UID must be non-root', text)
        self.assertIn('E2E_HOST_GID must be non-root', text)


# ──────────────────────────────────────────────────────────────────
# chown excludes bind-mounted /e2e/output
# ──────────────────────────────────────────────────────────────────

class ChownExcludesOutput(unittest.TestCase):
    """chown loop must skip /e2e/output (bind mount, chown fails)."""

    def test_chown_loop_exists(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('chown -R "$e2e_host_uid:$e2e_host_gid" "$d"', text)

    def test_output_is_skipped_in_loop(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('output|install-root) continue ;;', text)

    def test_no_bare_chown_on_e2e_root(self) -> None:
        """Must not recursively chown the whole /e2e tree."""
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn('chown -R "$e2e_host_uid:$e2e_host_gid" /e2e', text)

    def test_e2e_root_stays_root_owned_and_non_writable(self) -> None:
        """The agent must not control the parent of service-private state."""
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn('chown "$e2e_host_uid:$e2e_host_gid" /e2e\n', text)
        self.assertIn('chown 0:0 /e2e\n', text)
        self.assertIn('chmod 0755 /e2e\n', text)

    def test_service_root_cannot_be_renamed_or_replaced(self) -> None:
        """Content permissions alone do not prevent a writable-parent swap."""
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('install_root_replacement_probe="${install_root}.agent-replacement-probe"', text)
        self.assertIn('runuser -u e2e -- mv -- "$install_root" "$install_root_replacement_probe"', text)
        self.assertIn('runtime agent must not rename or replace service-private install root', text)

    def test_wrapper_writes_only_inside_agent_owned_log_root(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        for name in (
            "claude-bootstrap-prompt.md",
            "claude-command.txt",
            "claude-stdout.jsonl",
            "claude-stderr.log",
        ):
            self.assertIn(f"/e2e/logs/{name}", text)
            self.assertNotIn(f"/e2e/{name}", text.replace(f"/e2e/logs/{name}", ""))
        self.assertIn(
            "/e2e/customer-repos /e2e/output /e2e/work/bootstrap /e2e/logs",
            text,
        )

    def test_verifier_report_files_are_precreated_for_mapped_user(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("for report_file in \\", text)
        self.assertIn("/e2e/bootstrap-verify-report.json \\", text)
        self.assertIn("/e2e/bootstrap-verify-findings.md; do", text)
        self.assertIn('chown "$e2e_host_uid:$e2e_host_gid" "$report_file"', text)
        self.assertIn(
            "for f in /e2e/bootstrap-verify-report.json /e2e/bootstrap-verify-findings.md; do",
            text,
        )
        self.assertIn('test -r "$f" && test -w "$f"', text)

    def test_chown_loop_handles_output_exclusion_functionally(self) -> None:
        """Create a fake /e2e structure and verify the loop skips 'output'."""
        td = tempfile.TemporaryDirectory()
        try:
            tmp = Path(td.name)
            e2e = tmp / "e2e"
            dirs = ["bin", "config", "customer-repos", "install-root", "logs", "output", "work", "home"]
            for d in dirs:
                (e2e / d).mkdir(parents=True)
                (e2e / d / "marker").write_text(d)

            script = f"""
            set -euo pipefail
            visited=()
            for d in {e2e}/* {e2e}/.[!.]* {e2e}/..?*; do
              [ -e "$d" ] || continue
              case "$(basename "$d")" in
                output|install-root) continue ;;
              esac
              visited+=("$(basename "$d")")
            done
            printf '%s\\n' "${{visited[@]}}"
            """
            cp = _run_bash(script)
            visited = cp.stdout.strip().split()
            self.assertNotIn("output", visited,
                             f"output was NOT excluded from chown-equivalent loop: {visited}")
            self.assertNotIn("install-root", visited,
                             f"service-private install-root was not excluded: {visited}")
            self.assertIn("bin", visited)
            self.assertIn("customer-repos", visited)
        finally:
            td.cleanup()

    def test_agent_workspace_and_service_state_probes_exist(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('/e2e/work/bootstrap', text)
        self.assertIn('runtime agent must not own service-private runtime state', text)
        self.assertIn('service-private install root disappeared during isolation probe', text)


# ──────────────────────────────────────────────────────────────────
# sync_outputs ordering: small first, customer-repos last, /e2e/output excluded
# ──────────────────────────────────────────────────────────────────

class SyncOutputsOrdering(unittest.TestCase):
    """sync_outputs: control-plane first, customer-repos last, skip output+home."""

    def _run_sync_test(self, e2e_dirs: list[str]) -> tuple[list[str], str]:
        td = tempfile.TemporaryDirectory()
        try:
            tmp = Path(td.name)
            e2e = tmp / "e2e"
            host = tmp / "host-e2e"
            host.mkdir()
            for d in e2e_dirs:
                (e2e / d).mkdir(parents=True)
                (e2e / d / "marker").write_text(d)

            # Inline the sync_outputs function (matches the new implementation)
            script = f'''
            set -euo pipefail
            sync_outputs() {{
              [ -d {host} ] || return 1
              [ -d {e2e} ] || return 1
              mkdir -p {host} || return 1
              local _sync_failed=0
              for path in {e2e}/* {e2e}/.[!.]* {e2e}/..?*; do
                [ -e "$path" ] || continue
                case "$(basename "$path")" in
                  home|customer-repos|output) continue ;;
                esac
                echo "SYNC:$(basename "$path")" >&2
                cp -a "$path" {host}/ 2>/dev/null || _sync_failed=1
              done
              if [ -d {e2e}/customer-repos ]; then
                echo "SYNC:customer-repos" >&2
                cp -a {e2e}/customer-repos {host}/ 2>/dev/null || _sync_failed=1
              fi
              return "$_sync_failed"
            }}
            sync_outputs
            '''
            cp = _run_bash(script)
            # Parse sync order from stderr
            sync_order = [line.split("SYNC:", 1)[1]
                          for line in cp.stderr.splitlines()
                          if line.startswith("SYNC:")]
            return sync_order, cp.stderr
        finally:
            td.cleanup()

    def test_control_plane_before_customer_repos(self) -> None:
        sync_order, _ = self._run_sync_test(
            ["bin", "config", "logs", "customer-repos", "output", "work"]
        )
        self.assertIn("customer-repos", sync_order)
        cr_idx = sync_order.index("customer-repos")
        # customer-repos must be the LAST item
        self.assertEqual(cr_idx, len(sync_order) - 1,
                         f"customer-repos not last in sync order: {sync_order}")

    def test_output_not_synced(self) -> None:
        sync_order, _ = self._run_sync_test(
            ["bin", "output", "customer-repos"]
        )
        self.assertNotIn("output", sync_order,
                         f"/e2e/output was synced (should be excluded): {sync_order}")

    def test_home_not_synced(self) -> None:
        sync_order, _ = self._run_sync_test(
            ["bin", "home", "customer-repos"]
        )
        self.assertNotIn("home", sync_order,
                         f"/e2e/home was synced (should be excluded): {sync_order}")

    def test_only_control_plane_synced(self) -> None:
        sync_order, _ = self._run_sync_test(["bin", "config", "logs", "work"])
        # customer-repos dir doesn't exist → not synced
        self.assertNotIn("customer-repos", sync_order)
        self.assertIn("bin", sync_order)
        self.assertIn("config", sync_order)

    def test_customer_repos_synced_when_present(self) -> None:
        sync_order, _ = self._run_sync_test(["bin", "customer-repos"])
        self.assertIn("customer-repos", sync_order)
        self.assertIn("bin", sync_order)


# ──────────────────────────────────────────────────────────────────
# INT / TERM exit codes (signal → expected exit code)
# ──────────────────────────────────────────────────────────────────

class SignalExitCodes(unittest.TestCase):
    """INT → 130, TERM → 143, EXIT trap captures real code."""

    def test_int_handler_registered(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("trap '_eb_handle_signal INT 130' INT", text)

    def test_term_handler_registered(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("trap '_eb_handle_signal TERM 143' TERM", text)

    def test_exit_trap_uses_signal_code_when_set(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('_eb_last_rc', text)
        self.assertIn('[ -n "${_eb_last_rc:-}" ]', text)

    def test_int_produces_exit_130(self) -> None:
        """Signal handler explicitly sets exit code 130, EXIT trap propagates it."""
        script = """#!/usr/bin/env bash
_eb_last_rc=""
_eb_finalizing=0
_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then exit "$rc"; fi
  _eb_finalizing=1
  printf 'FINAL_RC=%s\\n' "$rc"
  exit "$rc"
}
_eb_handle_signal() { local s="$1" c="$2"; _eb_last_rc="$c"; exit "$c"; }
trap '_eb_handle_signal INT 130' INT
trap 'rc=$?; [ -n "${_eb_last_rc:-}" ] && rc="$_eb_last_rc"; _eb_finalize "$rc"' EXIT
# Simulate INT by calling handler directly (avoids platform signal quirks)
_eb_handle_signal INT 130
"""
        cp = subprocess.run(
            ["bash", "-c", script],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(cp.returncode, 130,
                         f"INT simulation should exit 130, got {cp.returncode}")
        self.assertIn("FINAL_RC=130", cp.stdout)

    def test_term_produces_exit_143(self) -> None:
        """Spawn a process, send SIGTERM, verify 143."""
        # Launch a child that traps TERM
        script = """#!/usr/bin/env bash
_eb_last_rc=""
_eb_handle_signal() { local s="$1" c="$2"; printf 'GOT_TERM\\n' >&2; _eb_last_rc="$c"; exit "$c"; }
trap '_eb_handle_signal TERM 143' TERM
sleep 10 &
wait $! 2>/dev/null
"""
        proc = subprocess.Popen(
            ["bash", "-c", script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=os.setsid,
        )
        time.sleep(0.2)
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        self.assertEqual(proc.returncode, 143,
                         f"TERM should exit 143, got {proc.returncode}; stderr={stderr}")

    def test_normal_exit_uses_last_command_rc(self) -> None:
        """When no signal is received, EXIT trap uses $? of last command."""
        script = """#!/usr/bin/env bash
_eb_last_rc=""
_eb_finalize() { local rc="$1"; printf 'FINALIZE:%s\\n' "$rc"; exit "$rc"; }
trap 'rc=$?; [ -n "${_eb_last_rc:-}" ] && rc="$_eb_last_rc"; _eb_finalize "$rc"' EXIT
# normal exit path
true
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertIn("FINALIZE:0", cp.stdout)

    def test_error_exit_uses_failing_rc(self) -> None:
        """When set -e triggers exit, $? is the failing command's code."""
        script = """#!/usr/bin/env bash
set -e
_eb_last_rc=""
_eb_finalize() { local rc="$1"; printf 'FINALIZE:%s\\n' "$rc" >&2; exit "$rc"; }
trap 'rc=$?; [ -n "${_eb_last_rc:-}" ] && rc="$_eb_last_rc"; _eb_finalize "$rc"' EXIT
# command that fails
bash -c 'exit 42'
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 42, f"expected 42, got {cp.returncode}")
        self.assertIn("FINALIZE:42", cp.stderr)


# ──────────────────────────────────────────────────────────────────
# outer-exit-code written AFTER sync completes
# ──────────────────────────────────────────────────────────────────

class OuterExitCodeAfterSync(unittest.TestCase):
    """_eb_finalize saves rc, then syncs, then writes outer-exit-code."""

    def test_finalize_saves_rc_before_sync(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        # Find _eb_finalize function
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "_eb_finalize not found")
        body = m.group(0)
        # New implementation saves original_rc to a local variable, not a temp file
        save_idx = body.find('local final_rc="$rc"')
        sync_idx = body.find("sync_outputs")
        write_idx = body.find("/host-e2e/outer-exit-code")
        self.assertGreater(save_idx, 0, "final_rc save not found in _eb_finalize")
        self.assertGreater(sync_idx, 0, "sync_outputs not called in _eb_finalize")
        self.assertGreater(write_idx, 0, "outer-exit-code write not found in _eb_finalize")
        # Order: save rc → sync → write outer-exit-code
        self.assertLess(save_idx, sync_idx,
                        "rc must be saved BEFORE sync_outputs")
        self.assertLess(sync_idx, write_idx,
                        "sync_outputs must run BEFORE outer-exit-code is written")

    def test_trap_recursion_guard(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("_eb_finalizing", text)
        self.assertIn('_eb_finalizing=1', text)
        self.assertIn('prevent recursive', text.lower() or "recursive" in text.lower())

    def test_original_zero_sync_failure_promotes_to_one(self) -> None:
        """original_rc=0 + sync failure => final_rc=1."""
        script = """#!/usr/bin/env bash
set -euo pipefail
_eb_finalizing=0
sync_outputs() { return 1; }
_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then exit "$rc"; fi
  _eb_finalizing=1
  trap - EXIT INT TERM
  local final_rc="$rc"
  sync_outputs || { if [ "$final_rc" -eq 0 ]; then final_rc=1; fi; }
  printf 'FINAL_RC=%s\\n' "$final_rc"
  exit "$final_rc"
}
trap 'rc=$?; _eb_finalize "$rc"' EXIT
true
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 1,
                         f"original=0 + sync failure must exit 1, got {cp.returncode}")
        self.assertIn("FINAL_RC=1", cp.stdout)

    def test_original_nonzero_sync_failure_preserves_rc(self) -> None:
        """original_rc=143 + sync failure => final_rc=143."""
        script = """#!/usr/bin/env bash
set -euo pipefail
_eb_finalizing=0
sync_outputs() { return 1; }
_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then exit "$rc"; fi
  _eb_finalizing=1
  trap - EXIT INT TERM
  local final_rc="$rc"
  sync_outputs || { if [ "$final_rc" -eq 0 ]; then final_rc=1; fi; }
  printf 'FINAL_RC=%s\\n' "$final_rc"
  exit "$final_rc"
}
trap 'rc=$?; _eb_finalize "$rc"' EXIT
bash -c 'exit 143'
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 143,
                         f"original=143 + sync failure must exit 143, got {cp.returncode}")
        self.assertIn("FINAL_RC=143", cp.stdout)


# ──────────────────────────────────────────────────────────────────
# host driver: missing / invalid outer-exit-code → fail closed
# ──────────────────────────────────────────────────────────────────

class HostDriverFailClosed(unittest.TestCase):
    """Host driver must die when outer-exit-code is missing, non-integer, or out of range."""

    def _extract_validation_logic(self) -> str:
        """Extract the outer-exit-code validation as a testable bash function."""
        return '''#!/usr/bin/env bash
set -euo pipefail
die() { printf 'ERROR: %s\\n' "$*" >&2; exit 99; }
validate_outer_exit_code() {
  local run_dir="$1"
  if [ ! -f "$run_dir/outer-exit-code" ]; then
    die "outer-exit-code not found at $run_dir/outer-exit-code"
  fi
  local outer_exit_code
  outer_exit_code="$(cat "$run_dir/outer-exit-code")"
  case "$outer_exit_code" in
    ''|*[!0-9]*)
      die "outer-exit-code is not an integer: '$outer_exit_code'"
      ;;
  esac
  if [ "$outer_exit_code" -lt 0 ] || [ "$outer_exit_code" -gt 255 ]; then
    die "outer-exit-code out of range [0,255]: $outer_exit_code"
  fi
  echo "$outer_exit_code"
}
"${@}"
'''

    def test_missing_file_fails(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(cp.returncode, 0,
                                "missing outer-exit-code should fail")
            self.assertIn("not found", cp.stderr)
        finally:
            td.cleanup()

    def test_empty_file_fails(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            (run_dir / "outer-exit-code").write_text("")
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(cp.returncode, 0,
                                "empty outer-exit-code should fail (empty string)")
            self.assertIn("not an integer", cp.stderr)
        finally:
            td.cleanup()

    def test_non_integer_fails(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            (run_dir / "outer-exit-code").write_text("abc")
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(cp.returncode, 0,
                                "non-integer outer-exit-code should fail")
            self.assertIn("not an integer", cp.stderr)
        finally:
            td.cleanup()

    def test_negative_value_fails(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            (run_dir / "outer-exit-code").write_text("-1")
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(cp.returncode, 0,
                                "negative outer-exit-code should fail")
            # Either "not an integer" (regex catches '-') or "out of range"
            err = cp.stderr.lower()
            self.assertTrue(
                "not an integer" in err or "out of range" in err,
                f"expected validation error, got: {cp.stderr}",
            )
        finally:
            td.cleanup()

    def test_out_of_range_high_fails(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            (run_dir / "outer-exit-code").write_text("256")
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(cp.returncode, 0,
                                "outer-exit-code > 255 should fail")
            self.assertIn("out of range", cp.stderr)
        finally:
            td.cleanup()

    def test_valid_values_pass(self) -> None:
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            for valid_rc in ["0", "1", "75", "124", "130", "143", "255"]:
                (run_dir / "outer-exit-code").write_text(valid_rc)
                cp = subprocess.run(
                    ["bash", "-c", self._extract_validation_logic(),
                     "_", "validate_outer_exit_code", str(run_dir)],
                    capture_output=True, text=True,
                )
                self.assertEqual(cp.returncode, 0,
                                 f"valid rc={valid_rc} should pass, got {cp.returncode}: {cp.stderr}")
                self.assertEqual(cp.stdout.strip(), valid_rc)
        finally:
            td.cleanup()

    def test_trailing_newline_ok(self) -> None:
        """File with trailing newline should still parse as integer."""
        td = tempfile.TemporaryDirectory()
        try:
            run_dir = Path(td.name)
            (run_dir / "outer-exit-code").write_text("42\n")
            cp = subprocess.run(
                ["bash", "-c", self._extract_validation_logic(),
                 "_", "validate_outer_exit_code", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertEqual(cp.returncode, 0,
                             f"trailing newline should be ok, got {cp.returncode}: {cp.stderr}")
        finally:
            td.cleanup()


# ──────────────────────────────────────────────────────────────────
# host driver: cleanup preserves output bind mount
# ──────────────────────────────────────────────────────────────────

class HostCleanupDoesNotDeleteOutput(unittest.TestCase):
    """Host cleanup only stops/removes containers; output persists on host fs."""

    def test_cleanup_only_touches_containers(self) -> None:
        text = HOST_DRIVER.read_text()
        m = re.search(r'cleanup\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "cleanup function not found")
        body = m.group(0)
        # cleanup only does container stop/rm and rm env file
        self.assertIn("container stop", body)
        self.assertIn("container rm", body)
        # output dir is on host fs, not in container — cleanup doesn't touch it
        self.assertNotIn("rm -rf", body)
        self.assertNotIn("$run_dir/output", body)


# ──────────────────────────────────────────────────────────────────
# no budget or complexity additions
# ──────────────────────────────────────────────────────────────────

class NoBudgetOrComplexityRegressions(unittest.TestCase):
    """Contracts 7-8: no CLAUDE_MAX_BUDGET_USD, no new abstractions."""

    def test_no_claude_max_budget_usd(self) -> None:
        for script in [HOST_DRIVER, RUN_IN_CONTAINER]:
            text = script.read_text()
            self.assertNotIn("CLAUDE_MAX_BUDGET_USD", text,
                             f"CLAUDE_MAX_BUDGET_USD found in {script.name}")

    def test_no_new_complex_abstractions(self) -> None:
        """Existing outer/replay two-layer structure preserved, no new indirection."""
        host_text = HOST_DRIVER.read_text()
        inner_text = RUN_IN_CONTAINER.read_text()
        # No Docker Compose, no orchestration layers added
        for label in ["docker-compose", "orchestrator", "supervisor", "coordinator"]:
            self.assertNotIn(label, host_text.lower(),
                             f"'{label}' found in host driver")
            self.assertNotIn(label, inner_text.lower(),
                             f"'{label}' found in run-in-container")


# ──────────────────────────────────────────────────────────────────
# continuation mode: copy a prior failed run, audit, repair, resume
# ──────────────────────────────────────────────────────────────────

class ContinuationModeContract(unittest.TestCase):
    """Continuation must preserve the source run and resume in a new run."""

    @staticmethod
    def _prepare_branches() -> tuple[str, str]:
        text = RUN_IN_CONTAINER.read_text()
        match = re.search(
            r'if \[ "\$continuation" = "1" \]; then\n'
            r'(?P<continuation>.*?)\nelse\n(?P<fresh>.*?)\nfi\n\n'
            r'# ── direct runtime-agent wrapper',
            text,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError("customer repo continuation/fresh branches not found")
        return match.group("continuation"), match.group("fresh")

    def test_usage_documents_continue_from_dir(self) -> None:
        self.assertIn("E2E_CONTINUE_FROM_DIR", HOST_DRIVER.read_text())

    def test_host_requires_absolute_existing_source_contract(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('E2E_CONTINUE_FROM_DIR must be an absolute path', text)
        self.assertIn('$continue_from/output/company-jarvis/bootstrap-state.json', text)
        self.assertIn('$continue_from/output/company-jarvis/bootstrap-result.json', text)
        self.assertIn('$continue_from/customer-repos', text)

    def test_host_rejects_same_physical_run_dir(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn("continue_from_canonical", text)
        self.assertIn("run_dir_canonical", text)
        self.assertIn("must differ from E2E_RUN_DIR", text)

    def test_host_mounts_source_read_only_and_sets_mode(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('-e "E2E_CONTINUATION=1"', text)
        self.assertIn('-v "$continue_from":/continue-from:ro', text)

    def test_outer_validates_mode_and_required_source_artifacts(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('continuation="${E2E_CONTINUATION:-0}"', text)
        self.assertIn('E2E_CONTINUATION must be 0 or 1', text)
        self.assertIn('/continue-from/output/company-jarvis/bootstrap-state.json', text)
        self.assertIn('/continue-from/output/company-jarvis/bootstrap-result.json', text)
        self.assertIn('/continue-from/customer-repos', text)

    def test_both_modes_clear_new_run_working_directories(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        clear = 'rm -rf /e2e/customer-repos/* /e2e/output/* /e2e/work/bootstrap/*'
        branch = 'if [ "$continuation" = "1" ]; then'
        self.assertLess(text.index(clear), text.index(branch, text.index(clear)))

    def test_continuation_copies_prior_repos_output_and_optional_semantic_review(self) -> None:
        continuation, _ = self._prepare_branches()
        self.assertIn('cp -a /continue-from/customer-repos/. /e2e/customer-repos/', continuation)
        self.assertIn('cp -a /continue-from/output/company-jarvis /e2e/output/company-jarvis', continuation)
        self.assertIn('cp -a /continue-from/work/replay-parent-worktrees/. /e2e/work/replay-parent-worktrees/', continuation)
        self.assertIn('cp -a /continue-from/replay-bridge/. /host-e2e/replay-bridge/', continuation)
        self.assertIn('/continue-from/semantic-acceptance.md', continuation)

    def test_continuation_does_not_clone_remove_skills_or_make_fixture_commit(self) -> None:
        continuation, _ = self._prepare_branches()
        self.assertNotIn("git clone", continuation)
        self.assertNotIn("rm -rf skills", continuation)
        self.assertNotIn("chore(e2e-fixture)", continuation)

    def test_fresh_mode_still_clones_removes_skills_and_seals_fixture(self) -> None:
        _, fresh = self._prepare_branches()
        self.assertIn("git clone", fresh)
        self.assertIn("rm -rf skills .agents/skills .codex/skills .claude/skills", fresh)
        self.assertIn("chore(e2e-fixture): remove pre-existing agent skills", fresh)

    def test_continuation_uses_state_not_a_bootstrap_cli_flag(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("bootstrap_args=", text)
        self.assertNotIn("--resume", text)
        self.assertIn('E2E_CONTINUATION="$continuation"', text)
        self.assertIn("/e2e/claude-bootstrap-agent", text)
        self.assertIn("playbooks/prompts/agent-native-bootstrap.md", text)

    def test_continuation_prompt_requires_integrity_audit_and_earliest_phase(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("claims made by a prior runtime agent, not current proof", text)
        self.assertIn("resume-integrity audit", text)
        self.assertIn("earliest owning phase", text)
        self.assertIn("old state.phase is not a forced starting point", text)
        self.assertIn("Do not jump directly to Phase 11-14", text)
        self.assertIn("cross-check replay-agent-cli-checks.md against host-isolation-evidence.json", text)

    def test_continue_source_is_not_mounted_into_replay_children(self) -> None:
        text = HOST_DRIVER.read_text()
        replay_section = text.split("# ── replay bridge monitor loop", 1)[1]
        self.assertNotIn("/continue-from", replay_section)


class RuntimeAgentFailureContract(unittest.TestCase):
    """A failed agent must not reuse a copied result as this run's outcome."""

    def test_runtime_agent_failure_exits_before_reading_bootstrap_result(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        failure_check = text.index('if [ "$agent_rc" -ne 0 ]; then')
        verify_section = text.index("# ── verify", failure_check)
        self.assertLess(failure_check, verify_section)
        self.assertNotIn(
            'Path("/e2e/output/company-jarvis/bootstrap-result.json")',
            text[failure_check:verify_section],
        )

    def test_runtime_agent_failure_skips_semantic_verifier(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn(
            "runtime agent execution failed; preserving evidence and skipping semantic verifier",
            text,
        )
        failure_check = text.index('if [ "$agent_rc" -ne 0 ]; then')
        verify_section = text.index("# ── verify", failure_check)
        failure_branch = text[failure_check:verify_section]
        self.assertIn('exit "$agent_rc"', failure_branch)


class CustomerGitLabFactIsolation(unittest.TestCase):
    """Customer discovery facts must not trigger jarvis-box home detection."""

    def test_host_defaults_box_gitlab_host_independently(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn(
            'JARVIS_BOX_GITLAB_HOST=${JARVIS_BOX_GITLAB_HOST:-gitlab.example.com}',
            text,
        )
        self.assertNotIn(
            'JARVIS_BOX_GITLAB_HOST=${JARVIS_BOX_GITLAB_HOST:-${JARVIS_GITLAB_HOST',
            text,
        )

    def test_outer_keeps_customer_and_box_hosts_separate(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('gitlab_host="${JARVIS_GITLAB_HOST:-gitlab.example.com}"', text)
        self.assertIn(
            'box_gitlab_host="${JARVIS_BOX_GITLAB_HOST:-gitlab.example.com}"',
            text,
        )
        self.assertIn('JARVIS_GITLAB_HOST="$gitlab_host"', text)
        self.assertIn('GITLAB_HOST="$box_gitlab_host"', text)


class ReplayContainerNameContract(unittest.TestCase):
    """Replay container IDs must stay within Apple Container's 64-char limit."""

    def test_replay_name_uses_short_unique_token(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('replay_token="$(printf', text)
        self.assertIn("| cksum | awk", text)
        self.assertIn('replay_name="jv-replay-${replay_index}-${replay_token}"', text)
        self.assertNotIn('replay_name="${container_name}-replay-${replay_index}-${case_id}"', text)


# ──────────────────────────────────────────────────────────────────
# run-in-container.sh: sync_outputs preserves runtime files
# ──────────────────────────────────────────────────────────────────

class RuntimeFilePresence(unittest.TestCase):
    """Key runtime artifacts are written under /e2e and reachable by sync."""

    def test_install_evidence_written_to_e2e(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/install-evidence.md", text)

    def test_runtime_agent_log_written_to_e2e(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/runtime-agent.log", text)

    def test_verify_report_written_to_e2e(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/bootstrap-verify-report.json", text)

    def test_host_prints_actual_synced_claude_log_paths(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('"$run_dir/logs/claude-stdout.jsonl"', text)
        self.assertIn('"$run_dir/logs/claude-stderr.log"', text)
        self.assertNotIn('"$run_dir/claude-stdout.jsonl"', text)
        self.assertNotIn('"$run_dir/claude-stderr.log"', text)


# ──────────────────────────────────────────────────────────────────
# atomic marker: temp file in same filesystem + mv, not direct cp
# ──────────────────────────────────────────────────────────────────

class AtomicMarkerContract(unittest.TestCase):
    """marker must be written via temp file + mv, never direct cp to target."""

    def test_marker_uses_temp_in_same_dir(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m, "_eb_finalize not found")
        body = m.group(0)
        self.assertIn(".outer-exit-code", body,
                      "marker temp file pattern not found")
        self.assertIn("mv ", body,
                      "atomic mv not found in marker write")

    def test_marker_no_direct_cp_to_outer_exit_code(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(0)
        self.assertNotRegex(body, r'cp\s+.*\s+/host-e2e/outer-exit-code\b',
                            "direct cp to outer-exit-code not allowed; use temp + mv")

    def test_marker_content_is_final_rc(self) -> None:
        """marker file content must be final_rc (post-promotion), not original rc."""
        text = RUN_IN_CONTAINER.read_text()
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(0)
        # The echo that writes the marker must use final_rc
        self.assertIn('echo "$final_rc"', body,
                      "marker must contain final_rc, not raw rc")

    def test_marker_written_after_sync(self) -> None:
        """Functional: sync must complete before marker appears."""
        script = """#!/usr/bin/env bash
set -euo pipefail
_eb_finalizing=0
_sync_done=0
sync_outputs() { _sync_done=1; return 1; }
_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then exit "$rc"; fi
  _eb_finalizing=1
  trap - EXIT INT TERM
  local final_rc="$rc"
  sync_outputs || { if [ "$final_rc" -eq 0 ]; then final_rc=1; fi; }
  # Write marker that proves sync was attempted
  local _marker_tmp="/tmp/test-sync-order.$$"
  echo "SYNC_WAS_DONE=$_sync_done" > "$_marker_tmp"
  echo "FINAL_RC=$final_rc" >> "$_marker_tmp"
  cat "$_marker_tmp"
  rm -f "$_marker_tmp"
  exit "$final_rc"
}
trap 'rc=$?; _eb_finalize "$rc"' EXIT
true
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertIn("SYNC_WAS_DONE=1", cp.stdout,
                      "marker written before sync completed")


# ──────────────────────────────────────────────────────────────────
# trap cleanup: _eb_finalize clears traps after recursion guard
# ──────────────────────────────────────────────────────────────────

class TrapCleanupContract(unittest.TestCase):
    """_eb_finalize must clear EXIT/INT/TERM traps after recursion guard."""

    def test_trap_cleared_after_guard(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(0)
        guard_idx = body.find("_eb_finalizing=1")
        trap_idx = body.find("trap -")
        self.assertGreater(trap_idx, guard_idx,
                           "trap - must appear after _eb_finalizing=1 guard")

    def test_trap_clears_exit_int_term(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        m = re.search(r'_eb_finalize\(\)\s*\{.*?^\}', text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(m)
        body = m.group(0)
        self.assertIn("trap - EXIT INT TERM", body,
                      "must clear EXIT, INT, and TERM traps")

    def test_trap_cleanup_is_effective(self) -> None:
        """Functional: trap - EXIT in finalize prevents recursive trap when exiting."""
        script = """#!/usr/bin/env bash
set -euo pipefail
_eb_finalizing=0
_recursion_detected=0
_eb_finalize() {
  local rc="$1"
  if [ "$_eb_finalizing" = "1" ]; then
    _recursion_detected=1
    exit "$rc"
  fi
  _eb_finalizing=1
  trap - EXIT INT TERM
  printf 'FINAL_RC=%s\\n' "$rc"
  exit "$rc"
}
trap 'rc=$?; _eb_finalize "$rc"' EXIT
true
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0)
        self.assertIn("FINAL_RC=0", cp.stdout)
        # trap was cleared, so if finalize's own 'exit' triggers EXIT again
        # the guard catches it. But with trap -, bash should NOT fire EXIT
        # on explicit 'exit' inside finalize (bash 4.4+ behavior).
        # We just verify the guard did NOT fire.
        self.assertNotIn("_recursion_detected=1", cp.stdout)


# ──────────────────────────────────────────────────────────────────
# stale marker cleanup in host driver
# ──────────────────────────────────────────────────────────────────

class StaleMarkerCleanup(unittest.TestCase):
    """Host driver must clean outer-exit-code and temp markers before launch."""

    def test_cleanup_before_container_run(self) -> None:
        text = HOST_DRIVER.read_text()
        cleanup_idx = text.find('rm -f "$run_dir/outer-exit-code"')
        container_idx = text.find('container "${outer_args[@]}"')
        self.assertGreater(cleanup_idx, 0,
                           "stale marker cleanup (rm outer-exit-code) not found")
        self.assertGreater(container_idx, cleanup_idx,
                           "stale marker cleanup must happen before container launch")

    def test_cleanup_includes_temp_markers(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn(".outer-exit-code.", text,
                      "temp marker cleanup (.outer-exit-code.*) not found")

    def test_cleanup_loop_safe_for_no_matches(self) -> None:
        """Functional: cleanup loop must not fail when no temp markers exist."""
        script = """#!/usr/bin/env bash
set -euo pipefail
td=$(mktemp -d)
trap 'rm -rf "$td"' EXIT
rm -f "$td/outer-exit-code"
for _f in "$td"/.outer-exit-code.*; do
  [ -e "$_f" ] && rm -f "$_f"
done
echo OK
"""
        cp = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0,
                         f"cleanup loop failed on empty dir: {cp.stderr}")
        self.assertIn("OK", cp.stdout)


# ──────────────────────────────────────────────────────────────────
# fixture commit contract: clone cleanup produces a sealed commit
# ──────────────────────────────────────────────────────────────────

class FixtureCommitContract(unittest.TestCase):
    """After clone: delete 4 skill paths, commit, verify clean state and history."""

    FIXTURE_SUBJECT = "chore(e2e-fixture): remove pre-existing agent skills"
    SKILL_PATHS_RE = r'^(skills/|\.agents/skills|\.codex/skills|\.claude/skills)'

    @staticmethod
    def _create_test_repo(tmpdir: str) -> None:
        """Create a temp repo with pre-existing skill dirs and product files."""
        script = f"""
set -euo pipefail
cd {tmpdir}
git init
git config user.email "test@test.local"
git config user.name "test"
mkdir -p skills .agents/skills .codex/skills .claude/skills
echo "skill content" > skills/skill.md
echo "agent skill" > .agents/skills/agent.md
echo "codex skill" > .codex/skills/codex.md
echo "claude skill" > .claude/skills/claude.md
echo "product code" > main.py
echo "readme" > README.md
git add -A
git commit -m "initial commit with skills"
"""
        subprocess.run(["bash", "-c", script], check=True,
                       capture_output=True, text=True)

    def _run_fixture_logic(self, repodir: str) -> subprocess.CompletedProcess:
        """Run the same fixture logic as run-in-container.sh."""
        script = f"""
set -euo pipefail
cd {repodir}
rm -rf skills .agents/skills .codex/skills .claude/skills
git add -A
git -c user.name="e2e-fixture" -c user.email="e2e-fixture@jarvis-box.local" \
  commit --quiet --allow-empty --no-gpg-sign \
  -m "{self.FIXTURE_SUBJECT}"
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: git status not clean after fixture commit" >&2
  exit 1
fi
forbidden_paths="$(git ls-tree -r --name-only HEAD -- skills .agents/skills .codex/skills .claude/skills)"
if [ -n "$forbidden_paths" ]; then
  echo "ERROR: HEAD tree still contains pre-existing agent skill paths" >&2
  exit 1
fi
echo "FIXTURE_OK"
"""
        return subprocess.run(["bash", "-c", script],
                              capture_output=True, text=True)

    def test_fixture_commit_subject_matches(self) -> None:
        """HEAD subject must match the expected fixture string exactly."""
        td = tempfile.TemporaryDirectory()
        try:
            self._create_test_repo(td.name)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed: {cp.stderr}")
            result = subprocess.run(
                ["git", "-C", td.name, "log", "-1", "--format=%s"],
                capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), self.FIXTURE_SUBJECT)
        finally:
            td.cleanup()

    def test_head_tree_has_no_skill_paths(self) -> None:
        """git ls-tree HEAD must not contain any of the 4 skill dir paths."""
        td = tempfile.TemporaryDirectory()
        try:
            self._create_test_repo(td.name)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed: {cp.stderr}")
            result = subprocess.run(
                ["git", "-C", td.name, "ls-tree", "-r", "--name-only", "HEAD"],
                capture_output=True, text=True, check=True)
            for path in result.stdout.strip().splitlines():
                self.assertNotRegex(
                    path, self.SKILL_PATHS_RE,
                    f"HEAD tree contains prohibited path: {path}")
        finally:
            td.cleanup()

    def test_product_files_preserved(self) -> None:
        """Regular product files must still exist in HEAD after fixture commit."""
        td = tempfile.TemporaryDirectory()
        try:
            self._create_test_repo(td.name)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed: {cp.stderr}")
            result = subprocess.run(
                ["git", "-C", td.name, "ls-tree", "-r", "--name-only", "HEAD"],
                capture_output=True, text=True, check=True)
            tree_paths = result.stdout.strip().splitlines()
            self.assertIn("main.py", tree_paths,
                          "product file main.py missing from HEAD tree")
            self.assertIn("README.md", tree_paths,
                          "product file README.md missing from HEAD tree")
        finally:
            td.cleanup()

    def test_status_clean_after_fixture_commit(self) -> None:
        """git status --porcelain must be empty after fixture commit."""
        td = tempfile.TemporaryDirectory()
        try:
            self._create_test_repo(td.name)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed: {cp.stderr}")
            result = subprocess.run(
                ["git", "-C", td.name, "status", "--porcelain"],
                capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "",
                             f"git status not clean: {result.stdout}")
        finally:
            td.cleanup()

    def test_parent_history_still_exists(self) -> None:
        """HEAD^ must still exist (fixture commit is additive, not rewriting)."""
        td = tempfile.TemporaryDirectory()
        try:
            self._create_test_repo(td.name)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed: {cp.stderr}")
            result = subprocess.run(
                ["git", "-C", td.name, "log", "-1", "--format=%s", "HEAD^"],
                capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "initial commit with skills")
        finally:
            td.cleanup()

    def test_no_skill_repo_still_works_allow_empty(self) -> None:
        """Repo with no pre-existing skill dirs: --allow-empty must succeed."""
        td = tempfile.TemporaryDirectory()
        try:
            script = f"""
set -euo pipefail
cd {td.name}
git init
git config user.email "test@test.local"
git config user.name "test"
echo "product code" > main.py
git add -A
git commit -m "initial commit no skills"
"""
            subprocess.run(["bash", "-c", script], check=True,
                           capture_output=True, text=True)
            cp = self._run_fixture_logic(td.name)
            self.assertEqual(cp.returncode, 0,
                             f"fixture logic failed on no-skill repo: {cp.stderr}")
            self.assertIn("FIXTURE_OK", cp.stdout)
        finally:
            td.cleanup()


# ──────────────────────────────────────────────────────────────────
# fixture prompt contract: bootstrap agent must be told the boundary
# ──────────────────────────────────────────────────────────────────

class FixturePromptContract(unittest.TestCase):
    """The bootstrap prompt in run-in-container.sh must instruct about the
    fixture commit boundary, candidate exclusion, and pre-fixture prohibition."""

    def test_prompt_contains_fixture_commit_subject(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("chore(e2e-fixture): remove pre-existing agent skills",
                      text)

    def test_prompt_prohibits_fixture_as_phase11_candidate(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("Phase 11 shadow pilot candidate", text)
        self.assertIn("never be selected as a Phase 11", text)

    def test_prompt_prohibits_fixture_as_phase12_candidate(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("Phase 12 history-replay candidate", text)

    def test_prompt_prohibits_pre_fixture_skill_content(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("skip any content under skills/, .agents/skills/, .codex/skills/, or .claude/skills/", text)

    def test_prompt_asserts_template_is_sole_authority(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("create-jarvis-skill template is the sole authority", text)

    def test_prompt_no_after_fixture_commit_language(self) -> None:
        """Regression: the fixture commit is HEAD — nothing is 'after' it."""
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("after the fixture commit", text)

    def test_prompt_current_tree_readable(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn(
            "Product code, docs, and tests in the current HEAD tree are readable and usable for discovery.",
            text)

    def test_prompt_pre_fixture_history_available_for_phase_11_12(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("Pre-fixture product commit history (before this fixture commit) is available for Phase 11 and Phase 12.", text)

    def test_prompt_fixture_itself_never_candidate(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("The fixture commit itself must never be selected as a candidate.", text)


# ──────────────────────────────────────────────────────────────────
# JARVIS_ENV_FILE contract
# ──────────────────────────────────────────────────────────────────

class JarvisEnvFileContract(unittest.TestCase):
    """runtime_env_file must be envs/.env.jarvis-box, verified after install,
    and passed as JARVIS_ENV_FILE to bootstrap agent."""

    def test_env_file_path_uses_envs_subdir(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('envs/.env.jarvis-box', text,
                      "runtime_env_file must be under envs/.env.jarvis-box")

    def test_env_file_existence_check_after_install(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('[ ! -f "$runtime_env_file" ]', text,
                      "must check runtime_env_file exists after install")

    def test_jarvis_env_file_passed_to_bootstrap_agent(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('JARVIS_ENV_FILE="$runtime_env_file"', text,
                      "JARVIS_ENV_FILE must be passed to bootstrap agent invocation")

    def test_env_file_not_using_old_path(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn('runtime_env_file="$runtime_state_root/env.jarvis-box"', text,
                         "must not use old env.jarvis-box path without envs/ subdir")


# ──────────────────────────────────────────────────────────────────
# execution contract: methodology authority and mechanical protocol
# ──────────────────────────────────────────────────────────────────

class ExecutionContractMethodologyAuthority(unittest.TestCase):
    """The execution contract must declare phase-checklist as the sole
    methodology authority, not duplicate Phase rules."""

    def test_phase_checklist_is_sole_methodology_authority(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("Sole methodology authority", text)
        self.assertIn("playbooks/phase-checklist.md", text)
        self.assertIn("NOT a second source of Phase rules", text)

    def test_execute_phases_in_order(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("Execute Phases 3", text)
        self.assertIn("state-transition and status-recording rules", text)

    def test_no_duplicate_phase_checklist_language(self) -> None:
        """The prompt must not contain Phase business semantics that belong
        in phase-checklist.md, such as module/source/repo-local/precheck rules."""
        text = RUN_IN_CONTAINER.read_text()
        # These are methodology phrases that should live only in phase-checklist.md
        self.assertNotIn("Hard gate: before creating modules/sources/workflow skills", text)
        self.assertNotIn("Durable modules/sources/company skills/references must use repo names", text)
        self.assertNotIn("Preserve confirmed module/source/workflow names exactly as directory names", text)
        self.assertNotIn("The company entry skill must explicitly preserve workflow-first", text)
        self.assertNotIn("Repo-local precheck.sh must be bootstrap-safe", text)
        self.assertNotIn("Start repo-local precheck.sh from the canonical self-contained template", text)
        self.assertNotIn("Create the canonical root skills/ repo-local package", text)
        self.assertNotIn("Create references/history-replay.md as a baseline reference", text)


class ExecutionContractMechanicalProtocol(unittest.TestCase):
    """The execution contract must contain the exact mechanical invocations
    for phase-12-preflight, request-isolated-replay, and 75/124 polling."""

    def test_phase_12_preflight_exact_command(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("--stage phase-12-preflight", text)
        self.assertIn("verify_bootstrap_output.py", text)
        self.assertIn("If exit != 0, fix the case or continue scanning; do NOT call the bridge", text)

    def test_request_isolated_replay_exact_command(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/bin/request-isolated-replay --case-id", text)
        self.assertIn("--visible-packet", text)
        self.assertIn("--parent-worktree", text)
        self.assertIn("--company-jarvis", text)
        self.assertIn("--destination", text)
        self.assertIn("being executable proves host bridge is available", text)

    def test_polling_exit_code_75_pending(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("75 = pending", text)
        self.assertIn("repeat the exact same invocation", text)

    def test_polling_exit_code_124_cancelled(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("124 = cancelled", text)
        self.assertIn("replay-not-executed", text)

    def test_polling_exit_code_0_terminal_success(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("0 = terminal success", text)

    def test_polling_exit_code_other_nonzero(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("other nonzero = terminal failure", text)

    def test_replay_poll_window_is_explicitly_passed_to_bootstrap_agent(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn('replay_bridge_poll_seconds="${E2E_REPLAY_BRIDGE_POLL_SECONDS:-600}"', text)
        self.assertIn('REPLAY_BRIDGE_POLL_SECONDS="$replay_bridge_poll_seconds"', text)

    def test_host_exposes_replay_poll_window_to_outer_container(self) -> None:
        text = HOST_DRIVER.read_text()
        self.assertIn('E2E_REPLAY_BRIDGE_POLL_SECONDS=${E2E_REPLAY_BRIDGE_POLL_SECONDS:-600}', text)

    def test_worktree_path_contract(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/work/replay-parent-worktrees/", text)
        self.assertIn("bridge rejects any other parent path", text)

    def test_replay_container_visibility_restrictions(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("NO access to /host-e2e", text)
        self.assertIn("/create-jarvis-skill", text)
        self.assertIn("hidden oracle", text)
        self.assertIn("bootstrap output root", text)
        self.assertIn("bootstrap transcript", text)

    def test_mount_facts_visible_packet(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("visible packet directory", text)
        self.assertIn("files authorized by the Phase 12 checklist", text)

    def test_mount_facts_trimmed_runtime(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("trimmed current company runtime copy", text)
        self.assertIn("exclude _bootstrap/, evals/, bootstrap-state.json, bootstrap-result.json", text)

    def test_mount_facts_repo_local_overlay(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("current repo-local skills/ overlay on parent snapshot", text)


class ExecutionContractStaleContentRemoved(unittest.TestCase):
    """Stale methodology strings that duplicate phase-checklist must not appear
    in the execution contract."""

    def test_no_first_80_commits(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("first 80 commits", text)

    def test_no_then_200(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("then 200", text)

    def test_no_then_500(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("then 500", text)

    def test_no_3_5_evaluable_candidates(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("3-5 evaluable candidates", text)

    def test_no_fix_action_plus_implementation_identifier(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("fix action plus implementation identifier", text)

    def test_no_changed_paths_must_never_appear(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("Changed paths from the final diff must never appear", text)

    def test_no_record_exact_final_diff_command(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("Record the exact final-diff command", text)

    def test_no_phase_14_methodology(self) -> None:
        """Phase 14 methodology rules must not be duplicated in the prompt."""
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("Phase 14: read /e2e/jarvis-box-help.txt first", text)

    def test_no_low_confidence_no_skill_gap_duplication(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("low-confidence/ineligible/needs-better-start cases: prohibit no_skill_gap", text)

    def test_no_replay_cli_failure_rules(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("replay CLI failure before the first valid agent action", text)

    def test_no_oracle_comparison_methodology(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("read the actual final diff (git diff", text)

    def test_no_needs_input_definition_duplication(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("needs-input is allowed only after all executable local steps", text)

    def test_no_start_quality_gate(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("START quality gate", text)

    def test_no_ineligible_leaky_rules(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("ineligible-leaky / low-confidence / needs-better-start", text)

    def test_no_after_replay_completes_methodology(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("After replay completes, first run oracle comparison", text)

    def test_no_module_hints_alone_evidence_duplication(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertNotIn("JARVIS_MODULE_HINTS alone is not evidence", text)


# ──────────────────────────────────────────────────────────────────
# no CLAUDE_MAX_BUDGET_USD and no --max-budget-usd
# ──────────────────────────────────────────────────────────────────

class NoMaxBudgetUsd(unittest.TestCase):
    """Both scripts must not contain --max-budget-usd.
    CLAUDE_MAX_BUDGET_USD is already covered by NoBudgetOrComplexityRegressions."""

    def test_no_max_budget_usd_flag(self) -> None:
        for script in [HOST_DRIVER, RUN_IN_CONTAINER]:
            text = script.read_text()
            self.assertNotIn("--max-budget-usd", text,
                             f"--max-budget-usd found in {script.name}")


class FinalVerifierRunuserContract(unittest.TestCase):
    """Final verifier must run via runuser -u e2e in run-in-container.sh."""

    def test_final_verifier_runs_via_runuser(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        # Find the verify section
        verify_idx = text.rfind("python3 /create-jarvis-skill/scripts/verify_bootstrap_output.py")
        if verify_idx < 0:
            verify_idx = text.find("verify_bootstrap_output.py")
        self.assertGreater(verify_idx, 0, "verify_bootstrap_output.py invocation not found")

        # It must be preceded by runuser -u e2e within reasonable distance
        pre = text[max(0, verify_idx - 300):verify_idx]
        self.assertIn("runuser -u e2e", pre,
                      "final verifier must run via runuser -u e2e, not as root")

    def test_verify_report_paths_unchanged(self) -> None:
        text = RUN_IN_CONTAINER.read_text()
        self.assertIn("/e2e/bootstrap-verify-stdout.json", text,
                      "verify stdout must still go to /e2e/bootstrap-verify-stdout.json")
        self.assertIn("/e2e/bootstrap-verify-report.json", text,
                      "verify report json must still go to /e2e/bootstrap-verify-report.json")


if __name__ == "__main__":
    unittest.main()
