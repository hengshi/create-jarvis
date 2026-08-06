#!/usr/bin/env python3
"""Install and manage the customer-owned Runtime Foundation scheduler."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import plistlib
import re
import shutil
import subprocess
import sys


COMPANY_SLUG = "{{COMPANY_SLUG}}"
SOURCE_ROOT = pathlib.Path(__file__).resolve().parent
JOBS = {
    "maintenance": ("jarvis-maintenance", "30 10 * * 1-5"),
    "self-improve": ("jarvis-self-improve", "30 18 * * 1-5"),
}
CRON_BEGIN = f"# BEGIN {COMPANY_SLUG} JARVIS RUNTIME FOUNDATION"
CRON_END = f"# END {COMPANY_SLUG} JARVIS RUNTIME FOUNDATION"


def run(command: list[str], *, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
        check=check,
    )


def absolute(value: str, name: str) -> pathlib.Path:
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{name} 必须是绝对路径: {value}")
    return path.resolve()


def config_path(root: pathlib.Path) -> pathlib.Path:
    return root / "config" / "runtime-foundation.json"


def load_config(root: pathlib.Path) -> dict[str, object]:
    try:
        payload = json.loads(config_path(root).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 Runtime Foundation 配置: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Runtime Foundation 配置必须是 JSON object")
    return payload


def install_payload(root: pathlib.Path) -> None:
    for directory in ("bin", "prompts"):
        destination = root / directory
        destination.mkdir(parents=True, exist_ok=True)
        for source in (SOURCE_ROOT / directory).iterdir():
            if source.is_file():
                shutil.copy2(source, destination / source.name)
    installed_manager = root / "bin" / "jarvis-runtime-foundation"
    shutil.copy2(pathlib.Path(__file__), installed_manager)
    for executable in (root / "bin").iterdir():
        if executable.is_file():
            executable.chmod(0o755)
    for directory in ("config", "locks", "logs"):
        (root / directory).mkdir(parents=True, exist_ok=True)


def write_config(root: pathlib.Path, payload: dict[str, object]) -> None:
    path = config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def job_command(root: pathlib.Path, config: dict[str, object], job: str) -> list[str]:
    executable = JOBS[job][0]
    if config["mode"] == "native":
        return [str(root / "bin" / executable)]
    return [
        str(config["release_helper"]),
        str(config["deployment_home"]),
        "runtime-job",
        str(pathlib.PurePosixPath(str(config["container_root"])) / "bin" / executable),
    ]


def probe(root: pathlib.Path, config: dict[str, object]) -> tuple[bool, str | None]:
    for job, (executable, _schedule) in JOBS.items():
        if config["mode"] == "native":
            target = root / "bin" / executable
            if not target.is_file() or not os.access(target, os.X_OK):
                return False, f"Native inner job 不可执行: {target}"
            command = [str(target), "--doctor"]
        else:
            target = str(pathlib.PurePosixPath(str(config["container_root"])) / "bin" / executable)
            command = [
                str(config["release_helper"]),
                str(config["deployment_home"]),
                "runtime-job",
                "/usr/bin/test",
                "-x",
                target,
            ]
        completed = run(command, check=False)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
            return False, f"{job} 探活失败: {detail}"
    return True, None


def launchd_label(mode: str, job: str) -> str:
    return f"local.{COMPANY_SLUG}-jarvis-{mode}-{job}"


def launchd_path(mode: str, job: str) -> pathlib.Path:
    return pathlib.Path.home() / "Library" / "LaunchAgents" / f"{launchd_label(mode, job)}.plist"


def cron_calendar(expression: str) -> list[dict[str, int]]:
    fields = expression.split()
    if len(fields) != 5 or fields[2:4] != ["*", "*"]:
        raise ValueError("macOS schedule 仅支持 `分钟 小时 * * 星期` 格式")
    minute, hour, weekdays = fields[0], fields[1], fields[4]
    if not minute.isdigit() or not hour.isdigit():
        raise ValueError("macOS schedule 的分钟和小时必须是整数")
    if weekdays == "*":
        days = range(0, 7)
    else:
        match = re.fullmatch(r"([0-6])-([0-6])", weekdays)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            days = range(start, end + 1)
        else:
            days = [int(value) for value in weekdays.split(",")]
    return [{"Weekday": day, "Hour": int(hour), "Minute": int(minute)} for day in days]


def launchd_loaded(label: str) -> bool:
    completed = run(["launchctl", "print", f"gui/{os.getuid()}/{label}"], check=False)
    return completed.returncode == 0


def launchd_unload(mode: str, job: str) -> None:
    label = launchd_label(mode, job)
    path = launchd_path(mode, job)
    if launchd_loaded(label):
        completed = run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], check=False)
        if completed.returncode != 0:
            raise ValueError(completed.stderr.strip() or f"无法停用 {label}")


def write_launchd(root: pathlib.Path, config: dict[str, object], mode: str, job: str) -> pathlib.Path:
    label = launchd_label(mode, job)
    stdout = root / "logs" / "scheduler" / f"{job}.out.log"
    stderr = root / "logs" / "scheduler" / f"{job}.err.log"
    stdout.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "Label": label,
        "ProgramArguments": job_command(root, config, job),
        "RunAtLoad": False,
        "StartCalendarInterval": cron_calendar(str(config["schedules"][job])),
        "StandardOutPath": str(stdout),
        "StandardErrorPath": str(stderr),
        "EnvironmentVariables": {"HOME": str(pathlib.Path.home()), "PATH": os.environ.get("PATH", "")},
    }
    path = launchd_path(mode, job)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".plist.tmp")
    temporary.write_bytes(plistlib.dumps(payload, sort_keys=True))
    temporary.replace(path)
    return path


def activate_launchd(root: pathlib.Path, config: dict[str, object]) -> None:
    target_mode = str(config["mode"])
    target_paths = {job: write_launchd(root, config, target_mode, job) for job in JOBS}
    previous = [
        (target_mode, job)
        for job in JOBS
        if launchd_loaded(launchd_label(target_mode, job))
    ]
    loaded: list[tuple[str, str]] = []
    try:
        for mode, job in previous:
            launchd_unload(mode, job)
        for job, path in target_paths.items():
            completed = run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)], check=False)
            if completed.returncode != 0:
                raise ValueError(completed.stderr.strip() or f"无法激活 {launchd_label(target_mode, job)}")
            loaded.append((target_mode, job))
    except ValueError:
        for mode, job in loaded:
            launchd_unload(mode, job)
        for mode, job in previous:
            path = launchd_path(mode, job)
            if path.is_file():
                run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)], check=False)
        raise


def crontab_text() -> str:
    completed = run(["crontab", "-l"], check=False)
    return completed.stdout if completed.returncode == 0 else ""


def without_managed_cron(text: str) -> str:
    lines = []
    managed = False
    for line in text.splitlines():
        if line == CRON_BEGIN:
            managed = True
            continue
        if line == CRON_END:
            managed = False
            continue
        if not managed:
            lines.append(line)
    return "\n".join(lines).strip()


def activate_cron(root: pathlib.Path, config: dict[str, object]) -> None:
    lines = [without_managed_cron(crontab_text()), CRON_BEGIN, f"# mode={config['mode']}"]
    for job in JOBS:
        command = " ".join(shlex_quote(value) for value in job_command(root, config, job))
        log = root / "logs" / "scheduler" / f"{job}.cron.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        lines.append(f"{config['schedules'][job]} {command} >> {shlex_quote(str(log))} 2>&1")
    lines.append(CRON_END)
    run(["crontab", "-"], input_text="\n".join(line for line in lines if line) + "\n")


def shlex_quote(value: str) -> str:
    import shlex

    return shlex.quote(value)


def activate(root: pathlib.Path) -> None:
    config = load_config(root)
    if config.get("mode") not in {"native", "docker"}:
        raise ValueError("只有 host 配置可以激活 scheduler")
    owner, conflict = scheduler_owner()
    if conflict:
        raise ValueError("检测到多个 scheduler owner；拒绝安装，请先恢复为所选部署模式")
    if owner not in {"none", config["mode"]}:
        raise ValueError(
            f"已有 {owner} scheduler owner，与所选 {config['mode']} 部署模式冲突；"
            "不支持自动改变部署模式"
        )
    reachable, detail = probe(root, config)
    if not reachable:
        raise ValueError(f"目标模式探活失败；当前 scheduler owner 保持不变: {detail}")
    if platform.system() == "Darwin":
        activate_launchd(root, config)
    else:
        activate_cron(root, config)


def stop(root: pathlib.Path) -> None:
    config = load_config(root)
    mode = str(config.get("mode"))
    if mode not in {"native", "docker"}:
        raise ValueError("只有 host 配置可以停止 scheduler")
    if platform.system() == "Darwin":
        for job in JOBS:
            launchd_unload(mode, job)
    else:
        remaining = without_managed_cron(crontab_text())
        run(["crontab", "-"], input_text=(remaining + "\n") if remaining else "")


def scheduler_owner() -> tuple[str, bool]:
    if platform.system() == "Darwin":
        active_modes = {
            mode
            for mode in ("native", "docker")
            if any(launchd_loaded(launchd_label(mode, job)) for job in JOBS)
        }
        if len(active_modes) > 1:
            return "conflict", True
        return (next(iter(active_modes)) if active_modes else "none"), False
    block = crontab_text()
    if CRON_BEGIN not in block:
        return "none", False
    match = re.search(r"^# mode=(native|docker)$", block, re.MULTILINE)
    return (match.group(1) if match else "unknown"), False


def status(root: pathlib.Path) -> None:
    config = load_config(root)
    owner, conflict = scheduler_owner()
    reachable = None
    detail = None
    if owner == "docker":
        reachable, detail = probe(root, config)
    healthy = not conflict and owner == config.get("mode") and (owner != "docker" or reachable is True)
    print(
        json.dumps(
            {
                "configured_mode": config.get("mode"),
                "scheduler_owner": owner,
                "conflict": conflict,
                "transport_reachable": reachable,
                "healthy": healthy,
                "detail": detail,
                "root": str(root),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def install(args: argparse.Namespace, *, inner: bool) -> None:
    root = absolute(args.root, "Runtime Foundation root")
    if inner:
        install_payload(root)
        payload: dict[str, object] = {
            "schema_version": 1,
            "company_slug": COMPANY_SLUG,
            "company_repo": args.company_repo,
            "jarvis_box_cli": args.jarvis_box_cli,
            "mode": "inner",
        }
        write_config(root, payload)
        print(json.dumps({"action": "installed-inner", "root": str(root)}, ensure_ascii=False))
        return
    existing = load_config(root) if config_path(root).is_file() else None
    if existing and existing.get("mode") in {"native", "docker"} and existing.get("mode") != args.mode:
        raise ValueError(
            f"Runtime Foundation 已按 {existing['mode']} 部署；不支持原地改为 {args.mode}。"
            "请先完成正式的 Jarvis Box 重新部署流程"
        )
    owner, conflict = scheduler_owner()
    if conflict or owner not in {"none", args.mode}:
        raise ValueError(
            f"现有 scheduler owner={owner} 与所选部署模式 {args.mode} 不一致；拒绝自动切换"
        )
    install_payload(root)
    payload = {
        "schema_version": 1,
        "company_slug": COMPANY_SLUG,
        "company_repo": args.company_repo,
        "jarvis_box_cli": args.jarvis_box_cli,
        "mode": args.mode,
        "schedules": {
            "maintenance": args.maintenance_cron,
            "self-improve": args.self_improve_cron,
        },
    }
    if args.mode == "docker":
        if not args.release_helper or not args.deployment_home or not args.container_root:
            raise ValueError("Docker 模式必须提供 --release-helper、--deployment-home 和 --container-root")
        payload.update(
            {
                "release_helper": str(absolute(args.release_helper, "release helper")),
                "deployment_home": str(absolute(args.deployment_home, "deployment home")),
                "container_root": args.container_root,
            }
        )
    path = config_path(root)
    previous_config = path.read_bytes() if path.is_file() else None
    write_config(root, payload)
    try:
        activate(root)
    except (OSError, ValueError, subprocess.CalledProcessError):
        if previous_config is None:
            path.unlink(missing_ok=True)
        else:
            temporary = path.with_suffix(".json.rollback")
            temporary.write_bytes(previous_config)
            temporary.chmod(0o600)
            temporary.replace(path)
        raise
    print(
        json.dumps(
            {"action": "installed-and-activated", "mode": args.mode, "root": str(root)},
            ensure_ascii=False,
        )
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="安装和管理 {{COMPANY_NAME}} Runtime Foundation")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("install", "install-inner"):
        command = commands.add_parser(name)
        command.add_argument("--root", required=True)
        command.add_argument("--company-repo", required=True)
        command.add_argument("--jarvis-box-cli", default="jarvis-box")
        if name == "install":
            command.add_argument("--mode", choices=("native", "docker"), required=True)
            command.add_argument("--release-helper")
            command.add_argument("--deployment-home")
            command.add_argument("--container-root")
            command.add_argument("--maintenance-cron", default=JOBS["maintenance"][1])
            command.add_argument("--self-improve-cron", default=JOBS["self-improve"][1])
    for name in ("stop", "status"):
        command = commands.add_parser(name)
        command.add_argument("--root", required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        root = absolute(args.root, "Runtime Foundation root")
        if args.command == "install":
            install(args, inner=False)
        elif args.command == "install-inner":
            install(args, inner=True)
        elif args.command == "stop":
            stop(root)
        else:
            status(root)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"STATUS=FAILED detail={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
