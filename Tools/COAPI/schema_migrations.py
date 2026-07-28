#!/usr/bin/env python3
"""Explicit, fail-closed COAPI schema migrations."""

from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from coapi_control import ControlError, read_json, state_root, validate_schema, write_json_atomic


CURRENT_SCHEMA_VERSION = 3

PERMISSION_DEFAULTS = {
    "repositoryWrite": False,
    "publicMirrorExport": False,
    "privateGitPush": False,
    "draftPullRequest": False,
    "publicRepositoryCreate": False,
    "publicRepositoryPush": False,
    "workbench": False,
    "gameClient": False,
    "serverBoot": False,
    "packageBuild": False,
    "workshopPublish": False,
    "credentialRead": False,
    "liveDeploy": False,
    "serverRestart": False,
    "providerEdit": False,
    "pullRequestMerge": False,
    "forcePush": False,
    "subagents": False,
    "recursiveCodex": False,
}


def semantic_diff(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if type(before) is not type(after):
        return [{"path": path or "/", "before": before, "after": after}]
    if isinstance(before, dict):
        for key in sorted(set(before) | set(after)):
            child = f"{path}/{key}"
            if key not in before:
                rows.append({"path": child, "before": None, "after": after[key]})
            elif key not in after:
                rows.append({"path": child, "before": before[key], "after": None})
            else:
                rows.extend(semantic_diff(before[key], after[key], child))
    elif isinstance(before, list):
        if before != after:
            rows.append({"path": path or "/", "before": before, "after": after})
    elif before != after:
        rows.append({"path": path or "/", "before": before, "after": after})
    return rows


def migrate_task_contract(document: dict[str, Any]) -> dict[str, Any]:
    version = document.get("schemaVersion")
    if not isinstance(version, int):
        raise ControlError("schemaVersion must be an integer")
    if version > CURRENT_SCHEMA_VERSION:
        raise ControlError(f"Unknown future schemaVersion {version}")
    if version < 1:
        raise ControlError(f"Unsupported schemaVersion {version}")
    migrated = copy.deepcopy(document)
    if version == 1:
        migrated["schemaVersion"] = 2
        migrated["consumed"] = {
            name: int(migrated.get("consumed", {}).get(name, 0))
            for name in migrated.get("budgets", {})
        }
        migrated.setdefault("requiredOutputs", [])
        migrated.setdefault("releaseAuthorization", None)
        if "terminalStatuses" not in migrated:
            migrated["terminalStatuses"] = migrated.pop(
                "terminalClassifications",
                ["MIGRATED_TASK_COMPLETE", "MIGRATED_TASK_BLOCKED"],
            )
    if version <= 2:
        migrated["schemaVersion"] = 3
        current_permissions = migrated.get("permissions", {})
        migrated["permissions"] = {
            name: bool(current_permissions.get(name, default))
            for name, default in PERMISSION_DEFAULTS.items()
        }
        migrated.setdefault("publicMirrorAuthorization", None)
    return migrated


MIGRATORS = {
    "task-contract": migrate_task_contract,
}


def migrate_document(schema_name: str, document: dict[str, Any]) -> dict[str, Any]:
    if schema_name not in MIGRATORS:
        raise ControlError(f"No explicit migration exists for schema {schema_name}")
    return MIGRATORS[schema_name](document)


def migrate_file(
    *,
    schema_name: str,
    input_path: Path,
    output_path: Path,
    schema_path: Path,
    diff_path: Path,
    apply: bool,
    backup_root: Path | None = None,
) -> dict[str, Any]:
    if not apply:
        raise ControlError("Schema migration requires explicit --apply")
    before = read_json(input_path)
    after = migrate_document(schema_name, before)
    validate_schema(after, schema_path)
    changes = semantic_diff(before, after)
    backup_path: Path | None = None
    if output_path.exists():
        selected_backup_root = backup_root or (
            state_root()
            / "SchemaBackups"
            / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        )
        selected_backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = selected_backup_root / output_path.name
        backup_path.write_bytes(output_path.read_bytes())
    write_json_atomic(output_path, after)
    diff = {
        "schemaVersion": 1,
        "schemaName": schema_name,
        "input": str(input_path),
        "output": str(output_path),
        "backup": str(backup_path) if backup_path else None,
        "changes": changes,
    }
    write_json_atomic(diff_path, diff)
    return {
        "status": "PASS",
        "schemaName": schema_name,
        "fromVersion": before["schemaVersion"],
        "toVersion": after["schemaVersion"],
        "changeCount": len(changes),
        "backupPath": str(backup_path) if backup_path else None,
        "diffPath": str(diff_path),
    }
