#!/usr/bin/env python3
"""Audit repository capability coverage and skill depth without executing evals."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_CATEGORIES = {
    "build",
    "runtime",
    "lifecycle",
    "config",
    "concurrency",
    "security",
    "diagnostics",
    "compatibility",
    "repo-specific",
}
ALLOWED_CATEGORY_STATUS = {"covered", "not-applicable"}
ALLOWED_DISPOSITIONS = {
    "skill",
    "router",
    "reference",
    "mechanical-gate",
    "no-skill",
    "candidate",
}
ALLOWED_LEVELS = {"L0", "L1", "L2", "L3"}
ALLOWED_EVAL_STATUS = {"executed-pass", "executed-fail", "prepared-not-executed"}
CONTROL_STATUS = ("executed-pass:", "executed-fail:", "observed-not-executed:")
REQUIRED_DIMENSIONS = {
    "implementation_anchors",
    "mechanical_controls",
    "risk_promotion",
    "runtime_hidden_forward_eval",
    "cross_repository_closure",
    "drift_self_improve",
}


def load_json(path: Path, problems: list[str], label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"{label} unreadable: {exc}")
        return {}
    if not isinstance(value, dict):
        problems.append(f"{label} must be a JSON object")
        return {}
    return value


def confined_path(
    base: Path,
    raw: str,
    boundary: Path,
    problems: list[str],
    label: str,
) -> Path | None:
    candidate = Path(raw.split("#", 1)[0])
    if candidate.is_absolute():
        problems.append(f"{label} must be repository-relative: {raw}")
        return None
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(boundary.resolve())
    except ValueError:
        problems.append(f"{label} escapes repository root: {raw}")
        return None
    if not resolved.exists():
        problems.append(f"{label} path missing: {raw}")
        return None
    return resolved


def risk_level(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("level", "")).strip().lower()
    return str(value).split(":", 1)[0].strip().lower()


def audit(repo: Path, router: str) -> list[str]:
    problems: list[str] = []
    repo = repo.resolve()
    router_root = repo / "skills" / router
    contract_path = router_root / "references" / "skill-depth.json"
    contract = load_json(contract_path, problems, "skill depth contract")
    if not contract:
        return problems

    dimensions = contract.get("dimensions")
    if not isinstance(dimensions, dict) or set(dimensions) != REQUIRED_DIMENSIONS:
        problems.append("skill depth contract must declare exactly the six depth dimensions")

    coverage_file = str(contract.get("coverage_file", "")).strip()
    evals_file = str(contract.get("evals_file", "")).strip()
    coverage_path = confined_path(
        router_root, coverage_file, repo, problems, "coverage file"
    ) if coverage_file else None
    evals_path = confined_path(
        router_root, evals_file, repo, problems, "evals file"
    ) if evals_file else None
    if not coverage_file:
        problems.append("skill depth contract missing coverage_file")
    if not evals_file:
        problems.append("skill depth contract missing evals_file")

    coverage = load_json(coverage_path, problems, "capability coverage") if coverage_path else {}
    eval_payload = load_json(evals_path, problems, "eval suite") if evals_path else {}
    eval_rows = eval_payload.get("evals", []) if eval_payload else []
    if not isinstance(eval_rows, list):
        problems.append("eval suite evals must be a list")
        eval_rows = []
    evals: dict[str, dict] = {}
    for row in eval_rows:
        if not isinstance(row, dict) or not str(row.get("id", "")).strip():
            problems.append("every eval must have an id")
            continue
        eval_id = str(row["id"])
        if eval_id in evals:
            problems.append(f"duplicate eval id: {eval_id}")
        evals[eval_id] = row
        if row.get("status") not in ALLOWED_EVAL_STATUS:
            problems.append(f"eval {eval_id} has invalid execution status")

    categories = coverage.get("categories", []) if coverage else []
    if not isinstance(categories, list):
        categories = []
    category_names: set[str] = set()
    for row in categories:
        if not isinstance(row, dict):
            problems.append("coverage category row must be an object")
            continue
        name = str(row.get("name", "")).strip()
        status = str(row.get("status", "")).strip()
        evidence = row.get("evidence")
        category_names.add(name)
        if status not in ALLOWED_CATEGORY_STATUS:
            problems.append(f"coverage category {name or '<missing>'} has invalid status")
        if not isinstance(evidence, list) or not any(str(item).strip() for item in evidence):
            problems.append(f"coverage category {name or '<missing>'} lacks evidence/reason")
    missing_categories = sorted(REQUIRED_CATEGORIES - category_names)
    if missing_categories:
        problems.append("coverage categories missing: " + ", ".join(missing_categories))

    skills = contract.get("skills", [])
    if not isinstance(skills, list):
        skills = []
        problems.append("skill depth contract skills must be a list")
    records: dict[str, dict] = {}
    for record in skills:
        if not isinstance(record, dict) or not str(record.get("name", "")).strip():
            problems.append("skill inventory record missing name")
            continue
        name = str(record["name"])
        records[name] = record
        level = str(record.get("level", ""))
        if level not in ALLOWED_LEVELS:
            problems.append(f"skill {name} has invalid level: {level}")
        for authority in record.get("authority", []) if isinstance(record.get("authority"), list) else []:
            confined_path(repo, str(authority), repo, problems, f"skill {name} authority")
        controls = record.get("mechanical_controls")
        if not isinstance(controls, list) or not controls:
            problems.append(f"skill {name} has no mechanical controls")
            controls = []
        for control in controls:
            if not str(control).startswith(CONTROL_STATUS):
                problems.append(f"skill {name} mechanical control lacks execution status: {control}")
        forward_ids = record.get("forward_eval_ids")
        if not isinstance(forward_ids, list):
            problems.append(f"skill {name} forward_eval_ids must be a list")
            forward_ids = []
        for eval_id in forward_ids:
            if str(eval_id) not in evals:
                problems.append(f"skill {name} references unknown eval id: {eval_id}")
        if risk_level(record.get("risk")) in {"high", "critical"}:
            if level not in {"L2", "L3"}:
                problems.append(f"high-risk skill {name} must be L2/L3 or remain a candidate")
            if not any(str(control).startswith("executed-pass:") for control in controls):
                problems.append(f"high-risk skill {name} lacks executed-pass mechanical evidence")
            if level == "L3" and not any(
                evals.get(str(eval_id), {}).get("status") == "executed-pass"
                for eval_id in forward_ids
            ):
                problems.append(f"L3 skill {name} lacks an executed-pass hidden eval")

    actual_packages = {
        path.parent.name
        for path in (repo / "skills").glob("*/SKILL.md")
        if path.is_file()
    }
    if set(records) != actual_packages:
        problems.append(
            "skill inventory mismatch: expected="
            + repr(sorted(actual_packages))
            + " recorded="
            + repr(sorted(records))
        )
    if router not in records:
        problems.append(f"router missing from skill inventory: {router}")

    capabilities = coverage.get("capabilities", []) if coverage else []
    if not isinstance(capabilities, list):
        capabilities = []
        problems.append("capability coverage capabilities must be a list")
    primary_homes: set[str] = set()
    for row in capabilities:
        if not isinstance(row, dict):
            problems.append("capability row must be an object")
            continue
        cap_id = str(row.get("id", "")).strip() or "<missing>"
        category = str(row.get("category", "")).strip()
        disposition = str(row.get("disposition", "")).strip()
        primary_home = str(row.get("primary_home", "")).strip()
        evidence = row.get("evidence")
        if category not in REQUIRED_CATEGORIES:
            problems.append(f"capability {cap_id} has invalid category: {category}")
        if disposition not in ALLOWED_DISPOSITIONS:
            problems.append(f"capability {cap_id} has invalid disposition: {disposition}")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"capability {cap_id} lacks evidence")
        if disposition in {"skill", "router"}:
            if primary_home not in records:
                problems.append(f"capability {cap_id} has unknown primary_home: {primary_home}")
            else:
                primary_homes.add(primary_home)
        elif not str(row.get("reason", "")).strip():
            problems.append(f"capability {cap_id} disposition requires a reason")
    unowned_packages = sorted(actual_packages - {router} - primary_homes)
    if unowned_packages:
        problems.append("delivered skill packages lack capability primary homes: " + ", ".join(unowned_packages))

    router_text = (router_root / "SKILL.md").read_text(encoding="utf-8") if (router_root / "SKILL.md").is_file() else ""
    for package in sorted(actual_packages - {router}):
        if package not in router_text:
            problems.append(f"router does not name delivered package: {package}")
    for package in sorted(actual_packages):
        text_path = repo / "skills" / package / "SKILL.md"
        text = text_path.read_text(encoding="utf-8") if text_path.is_file() else ""
        for marker in ("skill-depth", "evals/evals.json", "audit_skill_depth.py"):
            if marker not in text:
                problems.append(f"skill {package} does not link {marker}")

    depth_doc = router_root / "references" / "skill-depth.md"
    if depth_doc.is_file():
        for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", depth_doc.read_text(encoding="utf-8")):
            if "://" not in link and not link.startswith("#"):
                confined_path(depth_doc.parent, link, repo, problems, "depth document link")
    else:
        problems.append("router depth document missing")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--router", required=True)
    args = parser.parse_args()
    problems = audit(args.repo, args.router)
    print(json.dumps({"status": "failed" if problems else "ok", "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
