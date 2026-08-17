#!/usr/bin/env python3
"""Validate generic knowledge-workspace artifact structure and output traceability."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


TYPE_RULES = {
    "source-batch": {
        "required": {
            "batch_id",
            "asset_directory",
            "received_at",
            "processing_status",
            "asset_count",
            "classification",
            "access_scope",
        },
        "enums": {
            "processing_status": {
                "pending-ingest",
                "in-progress",
                "completed",
                "superseded",
            }
        },
        "nonempty": {
            "batch_id",
            "asset_directory",
            "received_at",
            "processing_status",
            "asset_count",
            "classification",
            "access_scope",
        },
        "sections": ["# 范围", "# 处理状态"],
        "one_of_sections": [("# 资产", "# 资产清单")],
    },
    "source-note": {
        "required": {
            "source_id",
            "asset",
            "logical_dataset",
            "source_role",
            "classification",
            "access_scope",
            "processed_at",
            "review_status",
        },
        "enums": {
            "source_role": {
                "evidence",
                "snapshot",
                "view",
                "reference",
                "superseded",
            },
            "review_status": {"proposed", "reviewed"},
        },
        "nonempty": {
            "source_id",
            "asset",
            "logical_dataset",
            "source_role",
            "classification",
            "access_scope",
            "processed_at",
            "review_status",
        },
        "sections": ["# 范围与角色", "# 来源结构", "# 来源定位"],
    },
    "knowledge-object": {
        "required": {
            "uid",
            "object_type",
            "name",
            "identity_status",
            "classification",
            "access_scope",
            "review_status",
        },
        "enums": {
            "identity_status": {"confirmed", "provisional", "ambiguous"},
            "review_status": {"proposed", "reviewed"},
        },
        "nonempty": {
            "uid",
            "object_type",
            "name",
            "identity_status",
            "classification",
            "access_scope",
            "review_status",
        },
        "sections": ["# 当前视图", "# 关系", "# 时间线", "# 来源", "# 人工备注"],
    },
    "knowledge-topic": {
        "required": {
            "topic_id",
            "title",
            "classification",
            "access_scope",
            "review_status",
        },
        "enums": {"review_status": {"proposed", "reviewed"}},
        "nonempty": {
            "topic_id",
            "title",
            "classification",
            "access_scope",
            "review_status",
        },
        "sections": ["# 定义与范围", "# 当前有效知识", "# 来源", "# 人工备注"],
    },
    "change-proposal": {
        "required": {
            "proposal_id",
            "created_at",
            "status",
            "classification",
            "access_scope",
        },
        "enums": {
            "status": {"proposed", "approved", "rejected", "applied", "superseded"}
        },
        "nonempty": {
            "proposal_id",
            "created_at",
            "status",
            "classification",
            "access_scope",
        },
        "sections": ["# 目标与范围", "# 建议变更", "# 审核结论", "# 应用记录"],
        "body_tokens": ["change_id:", "item_status:", "source_locator:", "application_evidence:"],
    },
    "context-pack": {
        "required": {
            "context_id",
            "purpose",
            "scope",
            "as_of",
            "classification",
            "access_scope",
            "sources",
            "created_at",
        },
        "enums": {},
        "nonempty": {
            "context_id",
            "purpose",
            "scope",
            "as_of",
            "classification",
            "access_scope",
            "sources",
            "created_at",
        },
        "sections": ["# 任务目标", "# 当前有效状态", "# 冲突、缺口、限制与待核验", "# 来源"],
    },
    "work-task": {
        "required": {
            "task_id",
            "title",
            "status",
            "classification",
            "access_scope",
            "created_at",
        },
        "enums": {
            "status": {"open", "in-progress", "blocked", "completed", "cancelled"}
        },
        "nonempty": {
            "task_id",
            "title",
            "status",
            "classification",
            "access_scope",
            "created_at",
        },
        "sections": ["# 目标与完成标准", "# 当前状态", "# 执行记录", "# 完成证据"],
    },
}

SCAN_DIRS = [
    "10-Sources/notes",
    "20-Knowledge/objects",
    "20-Knowledge/topics",
    "30-Work/change-proposals",
    "30-Work/context-packs",
    "30-Work/tasks",
]

MANIFEST_REQUIRED = {
    "40-Outputs/reviewed": "reviewed",
    "40-Outputs/final": "final",
    "90-Archive/outputs": "archived",
}

EMPTY_VALUES = {"", "[]", "{}", "null", "~"}


def add_issue(issues: list[dict[str, str]], level: str, code: str, path: Path, message: str) -> None:
    issues.append(
        {"level": level, "code": code, "path": str(path), "message": message}
    )


def clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return None
    return parse_top_level_fields(match.group(1).splitlines()), match.group(2)


def is_placeholder(value: str) -> bool:
    return value.startswith("<") and value.endswith(">")


def parse_top_level_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t", "-")):
            field = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
            if field:
                current_key = field.group(1)
                fields[current_key] = clean_value(field.group(2) or "")
            else:
                current_key = None
            continue
        if current_key is None:
            continue
        list_item = re.match(r"^\s+-\s*(.+?)\s*$", line)
        if list_item:
            item = clean_value(list_item.group(1))
            existing = fields.get(current_key, "")
            if existing in EMPTY_VALUES:
                fields[current_key] = f"[{item}]"
            else:
                fields[current_key] = f"{existing[:-1]}, {item}]" if existing.endswith("]") else f"[{existing}, {item}]"
    return fields


def validate_markdown(path: Path, root: Path, issues: list[dict[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if parsed is None:
        add_issue(issues, "error", "missing-frontmatter", path, "Markdown artifact needs frontmatter")
        return

    fields, body = parsed
    artifact_type = fields.get("type", "")
    if artifact_type not in TYPE_RULES:
        add_issue(issues, "error", "unknown-artifact-type", path, artifact_type or "missing type")
        return

    rules = TYPE_RULES[artifact_type]
    for field in sorted(rules["required"]):
        if field not in fields:
            add_issue(issues, "error", "missing-field", path, field)
        elif is_placeholder(fields[field]):
            add_issue(issues, "error", "unresolved-placeholder", path, field)

    for field, allowed in rules.get("enums", {}).items():
        value = fields.get(field, "")
        if value and not is_placeholder(value) and value not in allowed:
            add_issue(
                issues,
                "error",
                "invalid-enum",
                path,
                f"{field}={value}; expected one of {sorted(allowed)}",
            )

    for field in rules.get("nonempty", set()):
        value = fields.get(field, "")
        if field in fields and value in EMPTY_VALUES:
            add_issue(issues, "error", "empty-required-field", path, field)

    for heading in rules.get("sections", []):
        if heading not in body:
            add_issue(issues, "error", "missing-section", path, heading)

    for choices in rules.get("one_of_sections", []):
        if not any(choice in body for choice in choices):
            add_issue(
                issues,
                "error",
                "missing-section-choice",
                path,
                " or ".join(choices),
            )

    for token in rules.get("body_tokens", []):
        if token not in body:
            add_issue(issues, "error", "missing-body-contract", path, token)

    if artifact_type in {"knowledge-object", "knowledge-topic"}:
        if fields.get("review_status") == "reviewed" and not fields.get("updated_at"):
            add_issue(issues, "error", "missing-reviewed-time", path, "updated_at")

    if artifact_type == "source-batch":
        asset_directory = fields.get("asset_directory", "")
        if asset_directory and not is_placeholder(asset_directory):
            asset_path = (root / asset_directory).resolve()
            assets_root = (root / "10-Sources/assets").resolve()
            if asset_path != root and root not in asset_path.parents:
                add_issue(issues, "error", "asset-directory-outside-root", path, asset_directory)
            elif asset_path != assets_root and assets_root not in asset_path.parents:
                add_issue(
                    issues,
                    "error",
                    "asset-directory-wrong-boundary",
                    path,
                    "source-batch asset_directory must be under 10-Sources/assets",
                )
            elif not asset_path.is_dir():
                add_issue(issues, "error", "missing-asset-directory", path, asset_directory)
            else:
                assets = sorted(item for item in asset_path.iterdir() if item.is_file())
                try:
                    declared_count = int(fields.get("asset_count", ""))
                except ValueError:
                    add_issue(issues, "error", "invalid-asset-count", path, fields.get("asset_count", ""))
                else:
                    if declared_count != len(assets):
                        add_issue(
                            issues,
                            "error",
                            "asset-count-mismatch",
                            path,
                            f"declared={declared_count} actual={len(assets)}",
                        )
                for asset in assets:
                    if asset.name not in body:
                        add_issue(issues, "error", "asset-missing-from-list", path, asset.name)
                        continue
                    try:
                        digest = hashlib.sha256(asset.read_bytes()).hexdigest().upper()
                    except OSError as exc:
                        add_issue(issues, "warning", "asset-hash-unavailable", path, f"{asset.name}: {exc}")
                    else:
                        if digest not in body.upper():
                            add_issue(issues, "error", "asset-hash-mismatch", path, asset.name)


def parse_simple_yaml(path: Path) -> dict[str, str]:
    return parse_top_level_fields(path.read_text(encoding="utf-8").splitlines())


def validate_manifest(path: Path, expected_status: str, issues: list[dict[str, str]]) -> None:
    fields = parse_simple_yaml(path)
    required = {
        "manifest_version",
        "output_id",
        "purpose",
        "status",
        "version",
        "created_at",
        "created_by",
        "context_pack",
        "recipe",
        "classification",
        "access_scope",
        "source_notes",
        "source_assets",
        "validators_run",
    }
    for field in sorted(required):
        if field not in fields:
            add_issue(issues, "error", "manifest-missing-field", path, field)
        elif is_placeholder(fields[field]):
            add_issue(issues, "error", "manifest-placeholder", path, field)

    for field in (
        "output_id",
        "purpose",
        "status",
        "version",
        "created_at",
        "created_by",
        "context_pack",
        "recipe",
        "classification",
        "access_scope",
    ):
        if field in fields and fields[field] in EMPTY_VALUES:
            add_issue(issues, "error", "manifest-empty-field", path, field)

    if fields.get("source_notes", "") in EMPTY_VALUES and fields.get("source_assets", "") in EMPTY_VALUES:
        add_issue(
            issues,
            "error",
            "manifest-missing-sources",
            path,
            "At least one of source_notes or source_assets must be populated",
        )

    status = fields.get("status", "")
    if status and status != expected_status:
        add_issue(
            issues,
            "error",
            "manifest-status-mismatch",
            path,
            f"status={status}; directory requires {expected_status}",
        )

    if expected_status in {"reviewed", "final", "archived"}:
        for field in ("reviewer", "reviewed_at"):
            if not fields.get(field):
                add_issue(issues, "error", "manifest-review-metadata", path, field)
    if expected_status == "final" and not fields.get("approval"):
        add_issue(issues, "error", "manifest-approval", path, "approval")
    if expected_status in {"reviewed", "final"} and fields.get("validators_run", "") in EMPTY_VALUES:
        add_issue(issues, "error", "manifest-validators", path, "validators_run")


def validate_output_packages(root: Path, issues: list[dict[str, str]]) -> None:
    for relative, expected_status in MANIFEST_REQUIRED.items():
        state_dir = root / relative
        if not state_dir.is_dir():
            continue
        for item in state_dir.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_file():
                add_issue(
                    issues,
                    "error",
                    "unpackaged-output",
                    item,
                    "Controlled output must be inside its own directory with manifest.yaml",
                )
                continue
            manifests = [item / "manifest.yaml", item / "output-manifest.yaml"]
            manifest = next((candidate for candidate in manifests if candidate.is_file()), None)
            if manifest is None:
                add_issue(issues, "error", "missing-manifest", item, expected_status)
                continue
            validate_manifest(manifest, expected_status, issues)
            deliverables = [
                child
                for child in item.iterdir()
                if child.is_file() and child.name not in {"manifest.yaml", "output-manifest.yaml"}
            ]
            if not deliverables:
                add_issue(
                    issues,
                    "error",
                    "missing-deliverable",
                    item,
                    "Output package requires at least one non-manifest file",
                )

    drafts_dir = root / "40-Outputs/drafts"
    if drafts_dir.is_dir():
        for item in drafts_dir.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_file():
                add_issue(
                    issues,
                    "error",
                    "unpackaged-output",
                    item,
                    "Draft output must be inside its own directory",
                )
                continue
            manifests = [item / "manifest.yaml", item / "output-manifest.yaml"]
            manifest = next((candidate for candidate in manifests if candidate.is_file()), None)
            if manifest is not None:
                validate_manifest(manifest, "draft", issues)
            deliverables = [
                child
                for child in item.iterdir()
                if child.is_file() and child.name not in {"manifest.yaml", "output-manifest.yaml"}
            ]
            if not deliverables:
                add_issue(
                    issues,
                    "error",
                    "missing-deliverable",
                    item,
                    "Draft package requires at least one non-manifest file",
                )


def validate(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not root.is_dir():
        add_issue(issues, "error", "missing-root", root, "Workspace root does not exist")
        return issues
    for relative in SCAN_DIRS:
        directory = root / relative
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.md"):
            validate_markdown(path, root, issues)
    validate_output_packages(root, issues)
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
        print(f"Artifacts: {root}")
        print(f"Status: {result['status']} | errors={len(errors)} warnings={len(warnings)}")
        for item in issues:
            print(
                f"[{item['level'].upper()}] {item['code']}: "
                f"{item['path']} - {item['message']}"
            )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
