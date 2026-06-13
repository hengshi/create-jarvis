#!/usr/bin/env python3
"""Score create-jarvis-skill outputs against deterministic JSON fixtures."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TEXT_EXTENSIONS = {
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".env",
}


@dataclass
class Finding:
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "message": self.message}


def load_cases(cases_dir: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(cases_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            case = json.load(handle)
        case["_case_file"] = str(path)
        cases.append(case)
    return cases


def read_text_files(root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    if not root.exists():
        return texts
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {"SKILL.md", "README.md", "MAINTENANCE.md"}:
            continue
        try:
            texts[str(path.relative_to(root))] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return texts


def pattern_matches(pattern: str, texts: dict[str, str]) -> bool:
    compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    return any(compiled.search(text) for text in texts.values())


def load_json_file(path: Path, findings: list[Finding], label: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
    except json.JSONDecodeError as exc:
        findings.append(Finding("blocker", f"{label} is invalid JSON: {exc}"))
        return None
    if not isinstance(parsed, dict):
        findings.append(Finding("blocker", f"{label} must be a JSON object"))
        return None
    return parsed


def has_field(obj: dict[str, Any], dotted_path: str) -> bool:
    cursor: Any = obj
    for part in dotted_path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return False
        cursor = cursor[part]
    return True


def score_case(case: dict[str, Any], outputs_root: Path) -> dict[str, Any]:
    case_id = case["id"]
    output_dir = outputs_root / case_id
    expected = case.get("expected", {})
    findings: list[Finding] = []

    if not output_dir.exists():
        return {
            "id": case_id,
            "title": case.get("title", case_id),
            "status": "not-run",
            "score": 0,
            "max_score": 100,
            "findings": [Finding("major", f"output directory missing: {output_dir}").to_dict()],
        }

    for rel_path in expected.get("required_files", []):
        if not (output_dir / rel_path).exists():
            findings.append(Finding("blocker", f"required file missing: {rel_path}"))

    texts = read_text_files(output_dir)
    if not texts:
        findings.append(Finding("major", "no readable text artifacts found"))

    for pattern in expected.get("required_patterns", []):
        if not pattern_matches(pattern, texts):
            findings.append(Finding("major", f"required pattern not found: {pattern}"))

    for pattern in expected.get("forbidden_patterns", []):
        if pattern_matches(pattern, texts):
            findings.append(Finding("blocker", f"forbidden pattern found: {pattern}"))

    result = load_json_file(output_dir / "bootstrap-result.json", findings, "bootstrap-result.json")
    expected_status = expected.get("status")
    if expected_status:
        if result is None:
            findings.append(Finding("blocker", "bootstrap-result.json missing, cannot verify expected status"))
        elif result.get("status") != expected_status:
            findings.append(Finding("blocker", f"expected status {expected_status!r}, got {result.get('status')!r}"))

    for field in expected.get("bootstrap_result_required_fields", []):
        if result is None:
            findings.append(Finding("blocker", "bootstrap-result.json missing, cannot verify required fields"))
            break
        if not has_field(result, field):
            findings.append(Finding("blocker", f"bootstrap-result.json missing required field: {field}"))

    state = load_json_file(output_dir / "bootstrap-state.json", findings, "bootstrap-state.json")
    for field in expected.get("bootstrap_state_required_fields", []):
        if state is None:
            findings.append(Finding("blocker", "bootstrap-state.json missing, cannot verify required fields"))
            break
        if not has_field(state, field):
            findings.append(Finding("blocker", f"bootstrap-state.json missing required field: {field}"))

    blocker_count = sum(1 for finding in findings if finding.severity == "blocker")
    major_count = sum(1 for finding in findings if finding.severity == "major")
    minor_count = sum(1 for finding in findings if finding.severity == "minor")
    score = max(0, 100 - blocker_count * 35 - major_count * 15 - minor_count * 5)
    status = "pass" if blocker_count == 0 and major_count == 0 else "fail"

    return {
        "id": case_id,
        "title": case.get("title", case_id),
        "status": status,
        "score": score,
        "max_score": 100,
        "findings": [finding.to_dict() for finding in findings],
    }


def write_report(report_dir: Path, case_results: list[dict[str, Any]]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    pass_count = sum(1 for result in case_results if result["status"] == "pass")
    fail_count = sum(1 for result in case_results if result["status"] == "fail")
    not_run_count = sum(1 for result in case_results if result["status"] == "not-run")
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "not_run_count": not_run_count,
        "cases": case_results,
    }
    (report_dir / "scorecard.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# create-jarvis-skill eval findings",
        "",
        f"- pass: {pass_count}",
        f"- fail: {fail_count}",
        f"- not-run: {not_run_count}",
        "",
    ]
    for result in case_results:
        lines.append(f"## {result['id']} - {result['status']} ({result['score']}/{result['max_score']})")
        if result["findings"]:
            for finding in result["findings"]:
                lines.append(f"- {finding['severity']}: {finding['message']}")
        else:
            lines.append("- no findings")
        lines.append("")
    (report_dir / "findings.md").write_text("\n".join(lines), encoding="utf-8")


def write_prompts(cases: list[dict[str, Any]], prompts_dir: Path) -> None:
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for case in cases:
        (prompts_dir / f"{case['id']}.md").write_text(case["prompt"].rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score create-jarvis-skill eval outputs.")
    parser.add_argument("--cases", required=True, type=Path, help="Directory containing eval case JSON files.")
    parser.add_argument("--outputs", type=Path, help="Directory containing generated outputs keyed by case id.")
    parser.add_argument("--report", type=Path, help="Directory to write scorecard.json and findings.md.")
    parser.add_argument("--write-prompts", type=Path, help="Write eval prompts to this directory and exit.")
    parser.add_argument("--allow-missing-outputs", action="store_true", help="Exit 0 even when output dirs are missing.")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    if not cases:
        raise SystemExit(f"no cases found in {args.cases}")

    if args.write_prompts:
        write_prompts(cases, args.write_prompts)
        return 0

    if not args.outputs or not args.report:
        raise SystemExit("--outputs and --report are required unless --write-prompts is used")

    results = [score_case(case, args.outputs) for case in cases]
    write_report(args.report, results)
    has_failures = any(result["status"] == "fail" for result in results)
    has_missing = any(result["status"] == "not-run" for result in results)
    if has_failures or (has_missing and not args.allow_missing_outputs):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
