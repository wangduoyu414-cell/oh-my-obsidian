#!/usr/bin/env python3
"""Validate this skill without third-party Python dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def issue(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = re.match(r"^([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
        if field:
            result[field.group(1)] = field.group(2).strip().strip('"').strip("'")
    return result


def validate(skill_dir: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not skill_dir.is_dir():
        return [issue("error", "missing-skill-directory", str(skill_dir))]

    skill_path = skill_dir / "SKILL.md"
    if not skill_path.is_file():
        return [issue("error", "missing-skill-file", str(skill_path))]

    text = skill_path.read_text(encoding="utf-8")
    placeholder_token = "TO" + "DO"
    if placeholder_token in text:
        issues.append(issue("error", "placeholder", f"SKILL.md contains {placeholder_token}"))

    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        issues.append(issue("error", "frontmatter", "Missing or invalid frontmatter"))
    else:
        allowed = {"name", "description"}
        extra = sorted(set(frontmatter) - allowed)
        if extra:
            issues.append(issue("error", "frontmatter-extra-keys", ", ".join(extra)))
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if name != "knowledge-workflow":
            issues.append(issue("error", "name", f"Expected knowledge-workflow, got {name!r}"))
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            issues.append(issue("error", "name-format", name))
        if not description:
            issues.append(issue("error", "description", "Description is required"))

    if len(text.splitlines()) >= 500:
        issues.append(issue("warning", "skill-length", "SKILL.md should remain under 500 lines"))

    for relative in re.findall(r"\((references/[^)]+|assets/[^)]+)\)", text):
        if not (skill_dir / relative).is_file():
            issues.append(issue("error", "broken-reference", relative))

    metadata_path = skill_dir / "agents/openai.yaml"
    if not metadata_path.is_file():
        issues.append(issue("error", "metadata", "agents/openai.yaml is missing"))
    else:
        metadata = metadata_path.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in metadata:
                issues.append(issue("error", "metadata-field", key))
        if "$knowledge-workflow" not in metadata:
            issues.append(issue("error", "default-prompt", "Missing $knowledge-workflow"))

    for directory in ("references", "assets", "scripts"):
        if not (skill_dir / directory).is_dir():
            issues.append(issue("error", "missing-resource-directory", directory))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_dir = (args.skill_dir or Path(__file__).resolve().parents[1]).resolve()
    issues = validate(skill_dir)
    errors = [item for item in issues if item["level"] == "error"]
    warnings = [item for item in issues if item["level"] == "warning"]
    result = {
        "skill_dir": str(skill_dir),
        "status": "fail" if errors else "pass",
        "errors": len(errors),
        "warnings": len(warnings),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Skill: {skill_dir}")
        print(f"Status: {result['status']} | errors={len(errors)} warnings={len(warnings)}")
        for item in issues:
            print(f"[{item['level'].upper()}] {item['code']}: {item['message']}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
