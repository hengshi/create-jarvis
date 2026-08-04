#!/usr/bin/env python3
"""Deterministically audit a delivered repository skill depth contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LEVELS = {"L1", "L2", "L3"}
EVAL_KINDS = {"should-trigger", "must-not-trigger", "adjacent-route", "forward", "cross-repo"}
REQUIRED_FIELDS = {
    "name",
    "risk",
    "level",
    "authority",
    "entrypoints",
    "transitions",
    "mechanical_controls",
    "forward_eval_ids",
    "cross_repo",
    "drift_watch",
}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def nonempty_list(record: dict[str, object], key: str) -> bool:
    value = record.get(key)
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def audit(repo_root: Path, router: str) -> list[str]:
    problems: list[str] = []
    router_root = repo_root / "skills" / router
    contract_path = router_root / "references" / "skill-depth.json"
    evals_path = router_root / "evals" / "evals.json"
    guide_path = router_root / "references" / "skill-depth.md"
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"depth contract unreadable: {exc}"]
    try:
        eval_payload = json.loads(evals_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"eval file unreadable: {exc}"]

    if contract.get("schema_version") != 1:
        problems.append("unsupported schema_version")
    if contract.get("router") != router:
        problems.append("contract router does not match package")
    fixed = contract.get("fixed_revision")
    if not isinstance(fixed, str) or re.fullmatch(r"[0-9a-f]{40}", fixed) is None:
        problems.append("fixed_revision must be an exact 40-character commit")
    dimensions = contract.get("dimensions")
    required_dimensions = {
        "implementation_anchors",
        "mechanical_controls",
        "risk_promotion",
        "runtime_hidden_forward_eval",
        "cross_repository_closure",
        "drift_self_improve",
    }
    if not isinstance(dimensions, dict) or set(dimensions) != required_dimensions:
        problems.append("all six depth dimensions must be declared exactly once")

    router_skill = router_root / "SKILL.md"
    router_text = router_skill.read_text(encoding="utf-8") if router_skill.is_file() else ""
    for required_link in ("references/skill-depth.md", "references/skill-depth.json", "evals/evals.json", "scripts/audit_skill_depth.py"):
        if required_link not in router_text:
            problems.append(f"router does not link {required_link}")

    evals = eval_payload.get("evals")
    if not isinstance(evals, list):
        evals = []
        problems.append("evals must be a list")
    eval_ids: set[str] = set()
    eval_kinds: set[str] = set()
    for case in evals:
        if not isinstance(case, dict):
            problems.append("eval entry must be an object")
            continue
        case_id = case.get("id")
        kind = case.get("kind")
        if not isinstance(case_id, str) or not case_id:
            problems.append("eval id missing")
        elif case_id in eval_ids:
            problems.append(f"duplicate eval id: {case_id}")
        else:
            eval_ids.add(case_id)
        if kind not in EVAL_KINDS:
            problems.append(f"unsupported eval kind: {kind}")
        else:
            eval_kinds.add(kind)
        for field in ("prompt", "expected_route", "forbidden_routes", "invariants", "proof", "oracle_source"):
            if field not in case or case[field] in (None, "", []):
                problems.append(f"eval {case_id} missing {field}")
    if "should-trigger" not in eval_kinds or "must-not-trigger" not in eval_kinds:
        problems.append("eval suite needs should-trigger and must-not-trigger cases")
    if not ({"forward", "adjacent-route"} & eval_kinds):
        problems.append("eval suite needs forward or adjacent-route coverage")

    skills = contract.get("skills")
    if not isinstance(skills, list) or not skills:
        return problems + ["contract skills must be a non-empty list"]
    contract_names: set[str] = set()
    for record in skills:
        if not isinstance(record, dict):
            problems.append("skill record must be an object")
            continue
        name = record.get("name")
        if not isinstance(name, str) or not name:
            problems.append("skill record name missing")
            continue
        contract_names.add(name)
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            problems.append(f"{name}: missing fields {sorted(missing)}")
        if record.get("level") not in LEVELS:
            problems.append(f"{name}: invalid evidence level")
        for field in REQUIRED_FIELDS - {"name", "risk", "level"}:
            if not nonempty_list(record, field):
                problems.append(f"{name}: {field} must be a non-empty string list")
        package = repo_root / "skills" / name / "SKILL.md"
        if not package.is_file():
            problems.append(f"{name}: package missing")
        if name != router and name not in router_text:
            problems.append(f"{name}: absent from router")
        for authority in record.get("authority", []):
            if not isinstance(authority, str):
                continue
            path_text = authority.split("#", 1)[0]
            if path_text and not (repo_root / path_text).exists():
                problems.append(f"{name}: authority path missing: {path_text}")
        for eval_id in record.get("forward_eval_ids", []):
            if isinstance(eval_id, str) and eval_id not in eval_ids:
                problems.append(f"{name}: unknown eval id: {eval_id}")

    delivered = {path.parent.name for path in (repo_root / "skills").glob("*/SKILL.md")}
    if contract_names != delivered:
        problems.append(
            f"contract/package coverage mismatch: missing={sorted(delivered-contract_names)} extra={sorted(contract_names-delivered)}"
        )

    if not guide_path.is_file():
        problems.append("skill-depth.md missing")
    else:
        for target in LINK_RE.findall(guide_path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (guide_path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                problems.append(f"broken guide link: {target}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--router", required=True)
    args = parser.parse_args()
    problems = audit(args.repo_root.resolve(), args.router)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print(f"PASS: {args.router} skill depth contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
