#!/usr/bin/env python3
"""Validate the generic knowledge-workspace structure and core skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_DIRS = [
    "00-Inbox",
    "10-Sources/assets",
    "10-Sources/notes",
    "20-Knowledge/objects",
    "20-Knowledge/topics",
    "30-Work/change-proposals",
    "30-Work/context-packs",
    "30-Work/tasks",
    "40-Outputs/drafts",
    "40-Outputs/reviewed",
    "40-Outputs/final",
    "90-Archive",
    "90-Archive/outputs",
    "_System/skills/knowledge-workflow/agents",
    "_System/skills/knowledge-workflow/references",
    "_System/skills/knowledge-workflow/assets",
    "_System/skills/knowledge-workflow/scripts",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "_System/skills/knowledge-workflow/SKILL.md",
    "_System/skills/knowledge-workflow/agents/openai.yaml",
    "_System/skills/knowledge-workflow/references/knowledge-contract.md",
    "_System/skills/knowledge-workflow/references/storage-and-consumption.md",
    "_System/skills/knowledge-workflow/references/reader-contract.md",
    "_System/skills/knowledge-workflow/references/schema-contract.md",
    "_System/skills/knowledge-workflow/references/recipe-contract.md",
    "_System/skills/knowledge-workflow/references/validator-contract.md",
    "_System/skills/knowledge-workflow/references/extension-governance.md",
    "_System/skills/knowledge-workflow/assets/source-note.md",
    "_System/skills/knowledge-workflow/assets/source-batch.md",
    "_System/skills/knowledge-workflow/assets/object-note.md",
    "_System/skills/knowledge-workflow/assets/topic-note.md",
    "_System/skills/knowledge-workflow/assets/change-proposal.md",
    "_System/skills/knowledge-workflow/assets/context-pack.md",
    "_System/skills/knowledge-workflow/assets/task-note.md",
    "_System/skills/knowledge-workflow/assets/output-manifest.yaml",
    "_System/skills/knowledge-workflow/scripts/validate_artifacts.py",
    "_System/skills/knowledge-workflow/scripts/validate_skill.py",
]

ALLOWED_ROOT_FILES = {"AGENTS.md", ".gitignore", ".gitattributes"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_issue(issues: list[dict[str, str]], level: str, code: str, message: str) -> None:
    issues.append({"level": level, "code": code, "message": message})


def validate(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    for relative in REQUIRED_DIRS:
        path = root / relative
        if not path.is_dir():
            add_issue(issues, "error", "missing-directory", relative)

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            add_issue(issues, "error", "missing-file", relative)

    agents_path = root / "AGENTS.md"
    if agents_path.is_file():
        text = read_text(agents_path)
        required_terms = [
            "架构不变量",
            "核心处理管线",
            "知识消费类型",
            "扩展类型与路由公式",
            "完成定义",
        ]
        for term in required_terms:
            if term not in text:
                add_issue(issues, "error", "agents-missing-section", term)

    skill_path = root / "_System/skills/knowledge-workflow/SKILL.md"
    if skill_path.is_file():
        text = read_text(skill_path)
        placeholder_token = "TO" + "DO"
        if placeholder_token in text:
            add_issue(
                issues,
                "error",
                "skill-placeholder",
                f"SKILL.md contains {placeholder_token}",
            )
        frontmatter = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not frontmatter:
            add_issue(issues, "error", "skill-frontmatter", "Missing YAML frontmatter")
        else:
            block = frontmatter.group(1)
            if not re.search(r"^name:\s*knowledge-workflow\s*$", block, re.MULTILINE):
                add_issue(issues, "error", "skill-name", "Expected knowledge-workflow")
            if not re.search(r"^description:\s*\S.+$", block, re.MULTILINE):
                add_issue(issues, "error", "skill-description", "Description is missing")

        for relative in re.findall(r"\((references/[^)]+|assets/[^)]+)\)", text):
            if not (skill_path.parent / relative).is_file():
                add_issue(issues, "error", "broken-skill-reference", relative)

    openai_path = root / "_System/skills/knowledge-workflow/agents/openai.yaml"
    if openai_path.is_file():
        text = read_text(openai_path)
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in text:
                add_issue(issues, "error", "openai-metadata", f"Missing {key}")
        if "$knowledge-workflow" not in text:
            add_issue(
                issues,
                "error",
                "openai-default-prompt",
                "default_prompt must mention $knowledge-workflow",
            )

    if root.is_dir():
        for path in root.iterdir():
            if not path.is_file():
                continue
            if path.name in ALLOWED_ROOT_FILES or path.name.startswith("~$"):
                continue
            add_issue(
                issues,
                "warning",
                "unexpected-root-file",
                f"Move task material to its responsibility directory: {path.name}",
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    default_root = Path(__file__).resolve().parents[4]
    root = (args.root or default_root).resolve()
    issues = validate(root)
    errors = [item for item in issues if item["level"] == "error"]
    warnings = [item for item in issues if item["level"] == "warning"]

    result = {
        "root": str(root),
        "status": "fail" if errors else "pass",
        "errors": len(errors),
        "warnings": len(warnings),
        "issues": issues,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Workspace: {root}")
        print(f"Status: {result['status']} | errors={len(errors)} warnings={len(warnings)}")
        for item in issues:
            print(f"[{item['level'].upper()}] {item['code']}: {item['message']}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
