#!/usr/bin/env python3
"""Run one Company Jarvis-owned scheduled job with the selected Jarvis Box agent."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import time


FOUNDATION_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = FOUNDATION_ROOT / "config" / "runtime-foundation.json"
JARVIS_BOX_ENV_FILE = pathlib.Path.home() / ".jarvis-box" / "envs" / ".env.jarvis-box"


def load_jarvis_box_env() -> dict[str, str]:
    """Load provider auth env vars from jarvis-box env file."""
    env = {}
    env_file = pathlib.Path(os.environ.get("JARVIS_ENV_FILE", JARVIS_BOX_ENV_FILE))
    if not env_file.is_file():
        return env
    try:
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:]
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    env[key] = os.path.expandvars(value)
    except OSError:
        pass
    return env


def load_config() -> dict[str, object]:
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法读取 Runtime Foundation 配置 {CONFIG_PATH}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Runtime Foundation 配置必须是 JSON object: {CONFIG_PATH}")
    return payload


def required_text(config: dict[str, object], key: str) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Runtime Foundation 配置缺少 {key}")
    return value.strip()


def selected_agent(jarvis_box_cli: str) -> tuple[str, list[str]]:
    completed = subprocess.run(
        [jarvis_box_cli, "agent", "current"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "无法读取 Jarvis Box 当前 Agent: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    fields: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            fields[key.strip()] = value.strip()
    agent = fields.get("runtime_agent") or os.environ.get("JARVIS_RUNTIME_AGENT", "")
    command = fields.get("command") or agent
    if not agent or not command:
        raise RuntimeError("Jarvis Box 未配置当前 Agent；请先完成 create-jarvis 的 Agent 选择与认证")
    return agent, shlex.split(command)


def agent_command(
    agent: str,
    base: list[str],
    workspace: pathlib.Path,
    prompt: str,
    run_dir: pathlib.Path,
) -> list[str]:
    if agent == "copilot":
        return base + [
            "-C",
            str(workspace),
            "-p",
            prompt,
            "--autopilot",
            "--max-autopilot-continues",
            "12",
            "--yolo",
            "--no-ask-user",
            "--no-bash-env",
            "-s",
        ]
    if agent == "claude":
        return base + [
            "-p",
            prompt,
            "--allow-dangerously-skip-permissions",
            "--dangerously-skip-permissions",
            "--add-dir",
            str(workspace),
            "--add-dir",
            str(pathlib.Path.home()),
        ]
    if agent == "codex":
        return base + [
            "exec",
            "-C",
            str(workspace),
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "--dangerously-bypass-hook-trust",
            "-c",
            "shell_environment_policy.inherit=all",
            "-c",
            "shell_environment_policy.ignore_default_excludes=true",
            "-o",
            str(run_dir / "agent-last-message.md"),
            prompt,
        ]
    if agent == "opencode":
        return base + [
            "run",
            "--format",
            "json",
            "--dangerously-skip-permissions",
            "--dir",
            str(workspace),
            prompt,
        ]
    if agent == "openclaw":
        return base + ["agent", "--local", "--json", "--message", prompt]
    if agent == "gemini":
        return base + ["-p", prompt, "--yolo"]
    if agent in {"hermes", "kimi", "kiro"}:
        acp_agent = {
            "hermes": "hermes acp",
            "kimi": "kimi acp",
            "kiro": "kiro-cli acp --trust-all-tools",
        }[agent]
        return base + [
            "--format",
            "text",
            "--auth-policy",
            "skip",
            "--approve-all",
            "--non-interactive-permissions",
            "deny",
            "--cwd",
            str(workspace),
            "--agent",
            acp_agent,
            "exec",
            prompt,
        ]
    return base + ["-p", prompt]


def acquire_lock(job: str) -> pathlib.Path:
    lock = FOUNDATION_ROOT / "locks" / f"{job}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"{job} 已在运行，拒绝重入: {lock}") from exc
    (lock / "owner").write_text(
        f"pid={os.getpid()}\nstarted_at={int(time.time())}\n", encoding="utf-8"
    )
    return lock


def compose_prompt(job: str, workspace: pathlib.Path, run_dir: pathlib.Path) -> str:
    prompt_path = FOUNDATION_ROOT / "prompts" / f"jarvis-{job}.md"
    try:
        base = prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"缺少 {job} prompt: {prompt_path}") from exc
    return (
        base
        + "\n\n## 本次运行事实\n\n"
        + f"- Company Jarvis workspace: `{workspace}`\n"
        + f"- Runtime Foundation root: `{FOUNDATION_ROOT}`\n"
        + f"- Run evidence directory: `{run_dir}`\n"
        + f"- Scheduled job: `{job}`\n"
        + "- 你继承当前 OS 用户或容器 Agent HOME 中已有的 Git/Agent 认证；不得回显凭据。\n"
    )


def jarvis_box_workspace_root(jarvis_box_cli: str) -> pathlib.Path:
    """Derive the jarvis-box workspace root from its runtime environment."""
    completed = subprocess.run(
        [jarvis_box_cli, "status"],
        capture_output=True, text=True, check=False,
    )
    if completed.returncode == 0:
        for line in completed.stdout.splitlines():
            if line.startswith("workspace_root="):
                return pathlib.Path(line.split("=", 1)[1].strip())
    return pathlib.Path.home() / ".jarvis-box" / "workspace"


def run(job: str) -> int:
    config = load_config()
    company_repo = required_text(config, "company_repo")
    jarvis_box_cli = str(config.get("jarvis_box_cli") or "jarvis-box")
    run_id = time.strftime("%Y%m%d-%H%M%S")
    task_id = f"{job}-{run_id}"
    run_dir = FOUNDATION_ROOT / "logs" / job / run_id
    workspace_root = jarvis_box_workspace_root(jarvis_box_cli)
    workspace = workspace_root / f"{job}-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    lock = acquire_lock(job)
    success = False
    try:
        # Register as a jarvis-box Task
        create_result = subprocess.run(
            [jarvis_box_cli, "tasks", "create", task_id,
             "--reason", f"scheduled {job}", "--lane", "maintenance"],
            capture_output=True, text=True, check=False,
        )
        if create_result.returncode != 0:
            print(
                f"STATUS=TASK_CREATE_FAILED job={job} task_id={task_id} "
                f"detail={create_result.stderr.strip() or create_result.stdout.strip()}",
                file=sys.stderr,
            )
        subprocess.run(
            ["git", "clone", "--quiet", company_repo, str(workspace)],
            check=True,
        )
        agent, base = selected_agent(jarvis_box_cli)
        prompt = compose_prompt(job, workspace, run_dir)
        (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
        print(f"STATUS=RUNNING job={job} runtime_agent={agent} task_id={task_id} workspace={workspace}", flush=True)
        agent_env = os.environ.copy()
        agent_env.update(load_jarvis_box_env())
        completed = subprocess.run(
            agent_command(agent, base, workspace, prompt, run_dir),
            cwd=workspace,
            env=agent_env,
            check=False,
        )
        if completed.returncode != 0:
            print(
                f"STATUS=RUNTIME_AGENT_FAILED job={job} exit_code={completed.returncode} "
                f"task_id={task_id} workspace={workspace}",
                file=sys.stderr,
            )
            return completed.returncode
        success = True
        print(f"STATUS=OK job={job} task_id={task_id} run_dir={run_dir}")
        return 0
    finally:
        shutil.rmtree(lock, ignore_errors=True)
        if success:
            shutil.rmtree(workspace, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("job", choices=("maintenance", "self-improve"))
    parser.add_argument("--doctor", action="store_true")
    args = parser.parse_args()
    try:
        if args.doctor:
            config = load_config()
            jarvis_box_cli = str(config.get("jarvis_box_cli") or "jarvis-box")
            agent, command = selected_agent(jarvis_box_cli)
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "job": args.job,
                        "runtime_agent": agent,
                        "command": command[0],
                        "foundation_root": str(FOUNDATION_ROOT),
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        return run(args.job)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"STATUS=FAILED detail={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
