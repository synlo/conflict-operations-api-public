#!/usr/bin/env python3
"""Mechanically enforced COAPI V2.1 task, lock, ledger, and command controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import psutil


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[2]
SENSITIVE_PERMISSIONS = {
    "WORKBENCH": "workbench",
    "GAME_CLIENT": "gameClient",
    "SERVER_BOOT": "serverBoot",
    "PACKAGE_BUILD": "packageBuild",
    "WORKSHOP_PUBLISH": "workshopPublish",
    "CREDENTIAL_READ": "credentialRead",
    "LIVE_DEPLOY": "liveDeploy",
    "SERVER_RESTART": "serverRestart",
    "PROVIDER_EDIT": "providerEdit",
}
SOURCE_CONTROL_PERMISSIONS = {
    "PUBLIC_MIRROR_EXPORT": "publicMirrorExport",
    "PRIVATE_GIT_PUSH": "privateGitPush",
    "DRAFT_PULL_REQUEST": "draftPullRequest",
    "PUBLIC_REPOSITORY_CREATE": "publicRepositoryCreate",
    "PUBLIC_REPOSITORY_PUSH": "publicRepositoryPush",
}
OPERATION_PERMISSIONS = {**SENSITIVE_PERMISSIONS, **SOURCE_CONTROL_PERMISSIONS}
PERMISSION_NAMES = {
    "repositoryWrite",
    "publicMirrorExport",
    "privateGitPush",
    "draftPullRequest",
    "publicRepositoryCreate",
    "publicRepositoryPush",
    *SENSITIVE_PERMISSIONS.values(),
    "pullRequestMerge",
    "forcePush",
    "subagents",
    "recursiveCodex",
}
MODE_ALLOWED_TRUE_PERMISSIONS = {
    "RECOVERY": {
        "repositoryWrite",
    },
    "DEVELOPMENT": {
        "repositoryWrite",
        "publicMirrorExport",
        "privateGitPush",
        "draftPullRequest",
    },
    "RELEASE": {
        "repositoryWrite",
        "publicMirrorExport",
        "privateGitPush",
        "draftPullRequest",
        "publicRepositoryCreate",
        "publicRepositoryPush",
        *SENSITIVE_PERMISSIONS.values(),
    },
}
OPERATION_BUDGETS = {
    "STATIC_VALIDATION": "staticValidations",
    "POLICY_VALIDATION": "policyValidations",
    "REPOSITORY_WRITE": "repositoryWrites",
    "WORKBENCH": "workbenchInvocations",
    "GAME_CLIENT": "gameClientLaunches",
    "SERVER_BOOT": "serverBoots",
    "PACKAGE_BUILD": "packageBuilds",
    "WORKSHOP_PUBLISH": "publicationAttempts",
    "CREDENTIAL_READ": "credentialReads",
    "LIVE_DEPLOY": "liveTransactions",
    "SERVER_RESTART": "serverRestarts",
    "PROVIDER_EDIT": "providerEdits",
    "PUBLIC_MIRROR_EXPORT": "publicMirrorExports",
    "PRIVATE_EXPOSURE_SCAN": "privateExposureScans",
    "TEST_SUITE": "testSuiteExecutions",
    "PRIVATE_GIT_PUSH": "privateGitPushes",
    "DRAFT_PULL_REQUEST": "draftPullRequests",
    "PUBLIC_REPOSITORY_CREATE": "publicRepositoryCreates",
    "PUBLIC_REPOSITORY_PUSH": "publicRepositoryPushes",
}
TERMINAL_OUTCOMES = {"SUCCEEDED", "FAILED", "REJECTED", "TIMED_OUT", "CANCELLED"}
PROGRESS_TYPES = {
    "INPUT_HASH_CHANGED",
    "UNIQUE_EVIDENCE_FOUND",
    "OWNER_IDENTIFIED",
    "TEST_STATE_CHANGED",
    "INTENDED_PATCH_WRITTEN",
    "STATE_TRANSITION",
}
LOCK_DOMAINS = {"repository", "workbench", "release"}
LOCK_CONFLICTS = {
    "repository": {"repository", "release"},
    "workbench": {"workbench", "release"},
    "release": {"repository", "workbench", "release"},
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SECRET_PATTERNS = (
    re.compile(r"gh[oprsu]_[A-Za-z0-9]{20,}", re.I),
    re.compile(r"https://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+(?!\[REDACTED\])\S+", re.I),
)


class ControlError(RuntimeError):
    """A fail-closed policy refusal."""


def repo_root() -> Path:
    return Path(os.environ.get("COAPI_REPO_ROOT", DEFAULT_ROOT)).resolve()


def contract_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    return Path(os.environ.get("COAPI_CONTRACT_PATH", base / ".coapi/contracts/current.json")).resolve()


def state_root() -> Path:
    default = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    return Path(
        os.environ.get("COAPI_STATE_ROOT", default / "ConflictOperations")
    ).resolve()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ControlError(f"Timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ControlError(f"Required JSON file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ControlError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ControlError(f"JSON root must be an object: {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_schema(instance: Any, schema_path: Path) -> None:
    schema = read_json(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
        errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    except jsonschema.SchemaError as exc:
        raise ControlError(f"Invalid schema {schema_path}: {exc.message}") from exc
    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors[:10]
        )
        raise ControlError(f"Schema validation failed for {schema_path.name}: {details}")


def load_contract(
    path: Path | None = None,
    *,
    allow_terminal: bool = False,
    allow_expired: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    selected = path or contract_path(selected_root)
    contract = read_json(selected)
    validate_schema(contract, selected_root / ".coapi/schemas/task-contract.schema.json")
    if not allow_expired and parse_timestamp(contract["expiresAt"]) <= datetime.now(timezone.utc):
        raise ControlError(f"Task contract expired at {contract['expiresAt']}")
    budgets = contract["budgets"]
    consumed = contract["consumed"]
    if set(budgets) != set(consumed):
        raise ControlError("Task contract budgets and consumed counters must use identical keys")
    overdrawn = [
        name for name, limit in budgets.items()
        if consumed[name] > limit
    ]
    if overdrawn:
        raise ControlError(f"Task contract has overdrawn budgets: {', '.join(overdrawn)}")
    if not allow_terminal and contract["state"] in contract["terminalStatuses"]:
        raise ControlError(f"Task contract is terminal: {contract['state']}")
    permissions = contract["permissions"]
    unknown_permissions = sorted(set(permissions) - PERMISSION_NAMES)
    if unknown_permissions:
        raise ControlError(
            f"Task contract contains unknown permissions: {', '.join(unknown_permissions)}"
        )
    enabled_permissions = {name for name, enabled in permissions.items() if enabled}
    allowed_permissions = MODE_ALLOWED_TRUE_PERMISSIONS[contract["mode"]]
    disallowed_permissions = sorted(enabled_permissions - allowed_permissions)
    if disallowed_permissions:
        raise ControlError(
            f"Permissions are not allowed in {contract['mode']} mode: "
            f"{', '.join(disallowed_permissions)}"
        )
    runtime_release_enabled = any(
        permissions.get(permission, False)
        for permission in SENSITIVE_PERMISSIONS.values()
    )
    if runtime_release_enabled:
        authorization = contract.get("releaseAuthorization")
        if not isinstance(authorization, dict):
            raise ControlError(
                "RELEASE sensitive permissions require a complete releaseAuthorization"
            )
        validate_schema(
            authorization,
            selected_root / ".coapi/schemas/release-contract.schema.json",
        )
        if parse_timestamp(authorization["expiresAt"]) <= datetime.now(timezone.utc):
            raise ControlError("releaseAuthorization is expired")
        if parse_timestamp(authorization["expiresAt"]) > parse_timestamp(contract["expiresAt"]):
            raise ControlError("releaseAuthorization outlives the task contract")
        if authorization["repository"]["branch"] != contract["repository"]["branch"]:
            raise ControlError("releaseAuthorization branch does not match the task contract")
        if authorization["repository"]["commit"].lower() != contract["repository"]["head"].lower():
            raise ControlError("releaseAuthorization commit does not match the task contract")
        package = authorization.get("package")
        if not isinstance(package, dict) or not SHA256_PATTERN.fullmatch(
            str(package.get("packageSha256", "")).lower()
        ):
            raise ControlError(
                "releaseAuthorization requires an exact packageSha256"
            )
    public_release_enabled = any(
        permissions.get(permission, False)
        for permission in ("publicRepositoryCreate", "publicRepositoryPush")
    )
    if public_release_enabled:
        authorization = contract.get("publicMirrorAuthorization")
        if not isinstance(authorization, dict):
            raise ControlError(
                "Public repository permissions require a complete publicMirrorAuthorization"
            )
        validate_schema(
            authorization,
            selected_root / ".coapi/schemas/public-mirror-authorization.schema.json",
        )
        if parse_timestamp(authorization["expiresAt"]) <= datetime.now(timezone.utc):
            raise ControlError("publicMirrorAuthorization is expired")
        if parse_timestamp(authorization["expiresAt"]) > parse_timestamp(contract["expiresAt"]):
            raise ControlError("publicMirrorAuthorization outlives the task contract")
        if authorization["repository"]["privateBranch"] != contract["repository"]["branch"]:
            raise ControlError("publicMirrorAuthorization branch does not match the task contract")
        if authorization["repository"]["privateCommit"].lower() != contract["repository"]["head"].lower():
            raise ControlError("publicMirrorAuthorization commit does not match the task contract")
        authorized_permissions = authorization["permissions"]
        if permissions.get("publicRepositoryCreate", False) and not authorized_permissions["create"]:
            raise ControlError("publicMirrorAuthorization does not authorize repository creation")
        if permissions.get("publicRepositoryPush", False) and not authorized_permissions["push"]:
            raise ControlError("publicMirrorAuthorization does not authorize repository push")
    return contract


def ensure_inside_root(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ControlError(f"{label} escaped repository root: {resolved}") from exc


def contract_root_matches(claimed_root: str, actual_root: Path) -> bool:
    normalized = claimed_root.replace("\\", "/").strip()
    if normalized in {".", "${REPO_ROOT}"}:
        return True
    claimed = Path(claimed_root)
    if not claimed.is_absolute():
        claimed = actual_root / claimed
    return claimed.resolve() == actual_root.resolve()


def allowed_repository_path(relative: Path, allowed_paths: Iterable[str]) -> bool:
    candidate = relative.as_posix().strip("/")
    for raw in allowed_paths:
        rendered = str(raw).replace("\\", "/")
        directory_rule = rendered.endswith("/")
        normalized = rendered.strip("/")
        if not normalized:
            continue
        if candidate == normalized or (
            directory_rule and candidate.startswith(normalized + "/")
        ):
            return True
    return False


def git_output(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="replace",
        shell=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def repository_key(root: Path) -> str:
    common = git_output(root, "rev-parse", "--git-common-dir")
    if common:
        common_path = Path(common)
        if not common_path.is_absolute():
            common_path = (root / common_path).resolve()
        identity = str(common_path).lower()
    else:
        identity = str(root.resolve()).lower()
    return sha256_text(identity)[:16]


def lock_directory(root: Path | None = None, state: Path | None = None) -> Path:
    selected_root = root or repo_root()
    selected_state = state or state_root()
    return selected_state / "Locks" / repository_key(selected_root)


def lock_path(domain: str, root: Path | None = None, state: Path | None = None) -> Path:
    if domain not in LOCK_DOMAINS:
        raise ControlError(f"Unknown lock domain: {domain}")
    return lock_directory(root, state) / f"{domain}.json"


def process_start_time(pid: int) -> float:
    try:
        return float(psutil.Process(pid).create_time())
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        raise ControlError(f"Cannot verify process identity for PID {pid}") from exc


def lock_owner_alive(receipt: dict[str, Any]) -> bool:
    try:
        actual = process_start_time(int(receipt["ownerPid"]))
        expected = float(receipt["ownerProcessStartEpoch"])
    except (ControlError, KeyError, TypeError, ValueError):
        return False
    return abs(actual - expected) < 0.01


def read_lock(domain: str, root: Path | None = None, state: Path | None = None) -> dict[str, Any] | None:
    path = lock_path(domain, root, state)
    if not path.is_file():
        return None
    try:
        value = read_json(path)
    except ControlError:
        return {"domain": domain, "state": "CORRUPT", "active": False}
    value["active"] = lock_owner_alive(value)
    value["state"] = "ACTIVE" if value["active"] else "STALE"
    return value


def acquire_lock(
    domain: str,
    task_id: str,
    mode: str,
    owner_pid: int,
    *,
    root: Path | None = None,
    state: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    selected_state = state or state_root()
    if domain not in LOCK_DOMAINS:
        raise ControlError(f"Unknown lock domain: {domain}")
    if mode not in {"RECOVERY", "DEVELOPMENT", "RELEASE"}:
        raise ControlError(f"Unknown task mode: {mode}")
    start_epoch = process_start_time(owner_pid)
    directory = lock_directory(selected_root, selected_state)
    directory.mkdir(parents=True, exist_ok=True)
    stale_dir = directory / "stale"
    for other_domain in LOCK_CONFLICTS[domain]:
        existing = read_lock(other_domain, selected_root, selected_state)
        if existing and existing.get("active"):
            if (
                other_domain == domain
                and int(existing.get("ownerPid", -1)) == owner_pid
                and existing.get("taskId") == task_id
            ):
                existing["idempotent"] = True
                return existing
            raise ControlError(
                f"Cannot acquire {domain} lock while active {other_domain} lock is owned "
                f"by PID {existing.get('ownerPid')} for task {existing.get('taskId')}"
            )
    target = lock_path(domain, selected_root, selected_state)
    if target.exists():
        stale_dir.mkdir(parents=True, exist_ok=True)
        stale_hash = sha256_file(target)
        preserved = stale_dir / (
            f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-"
            f"{domain}-{stale_hash[:12]}.json"
        )
        os.replace(target, preserved)
    receipt = {
        "schemaVersion": 2,
        "domain": domain,
        "taskId": task_id,
        "mode": mode,
        "ownerPid": owner_pid,
        "ownerProcessStartEpoch": start_epoch,
        "ownerProcessStartUtc": datetime.fromtimestamp(
            start_epoch, timezone.utc
        ).isoformat().replace("+00:00", "Z"),
        "branch": git_output(selected_root, "branch", "--show-current"),
        "head": git_output(selected_root, "rev-parse", "HEAD"),
        "repositoryKey": repository_key(selected_root),
        "acquiredAt": utc_now(),
        "nonce": secrets.token_hex(16),
    }
    payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as exc:
        raise ControlError(f"Lock acquisition raced for domain {domain}") from exc
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    receipt["active"] = True
    receipt["state"] = "ACTIVE"
    receipt["idempotent"] = False
    return receipt


def release_lock(
    domain: str,
    owner_pid: int,
    nonce: str | None,
    *,
    root: Path | None = None,
    state: Path | None = None,
) -> dict[str, Any]:
    path = lock_path(domain, root, state)
    receipt = read_lock(domain, root, state)
    if not receipt:
        raise ControlError(f"No {domain} lock exists")
    if not receipt.get("active"):
        raise ControlError(f"Refusing to release stale or corrupt {domain} lock")
    if int(receipt.get("ownerPid", -1)) != owner_pid:
        raise ControlError(f"PID {owner_pid} does not own the {domain} lock")
    if nonce and receipt.get("nonce") != nonce:
        raise ControlError(f"Nonce does not match the {domain} lock")
    path.unlink()
    return {"domain": domain, "released": True, "releasedAt": utc_now()}


def lock_status(root: Path | None = None, state: Path | None = None) -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "repositoryKey": repository_key(root or repo_root()),
        "domains": {
            domain: read_lock(domain, root, state) or {
                "domain": domain,
                "state": "UNLOCKED",
                "active": False,
            }
            for domain in sorted(LOCK_DOMAINS)
        },
    }


def sanitize_text(value: str) -> str:
    sanitized = value
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    profile = str(Path.home())
    sanitized = re.sub(re.escape(profile), "<USER_PROFILE>", sanitized, flags=re.I)
    return sanitized


def ledger_path(contract: dict[str, Any], state: Path | None = None) -> Path:
    selected = state or state_root()
    return selected / "TaskEvidence" / contract["taskId"] / "operations.jsonl"


def compute_entry_hash(entry: dict[str, Any]) -> str:
    unsigned = dict(entry)
    unsigned.pop("entrySha256", None)
    return sha256_text(canonical_json(unsigned))


def read_ledger(
    path: Path,
    *,
    schema_path: Path | None = None,
    require_valid: bool = True,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines()):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ControlError(f"Invalid ledger JSON at line {index + 1}: {exc}") from exc
        if not isinstance(value, dict):
            raise ControlError(f"Ledger line {index + 1} is not an object")
        rows.append(value)
    if require_valid:
        expected_previous: str | None = None
        for index, row in enumerate(rows):
            if row.get("sequence") != index:
                raise ControlError(f"Ledger sequence mismatch at row {index}")
            if row.get("previousEntrySha256") != expected_previous:
                raise ControlError(f"Ledger previous hash mismatch at row {index}")
            computed = compute_entry_hash(row)
            if row.get("entrySha256") != computed:
                raise ControlError(f"Ledger entry hash mismatch at row {index}")
            if schema_path:
                validate_schema(row, schema_path)
            expected_previous = computed
    return rows


def append_ledger(
    contract: dict[str, Any],
    entry: dict[str, Any],
    *,
    state: Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    path = ledger_path(contract, state)
    path.parent.mkdir(parents=True, exist_ok=True)
    append_guard = path.with_suffix(".append.lock")
    try:
        descriptor = os.open(append_guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as exc:
        raise ControlError("Operation ledger append lock is already held") from exc
    os.close(descriptor)
    try:
        schema = selected_root / ".coapi/schemas/operation-ledger-entry.schema.json"
        rows = read_ledger(path, schema_path=schema)
        previous = rows[-1]["entrySha256"] if rows else None
        complete = {
            "schemaVersion": 2,
            "ledgerId": f"{contract['taskId']}-ledger",
            "sequence": len(rows),
            "timestamp": utc_now(),
            "taskId": contract["taskId"],
            "mode": contract["mode"],
            "phase": entry.get("phase", "UNKNOWN"),
            "hypothesisId": entry.get("hypothesisId"),
            "operationKind": entry.get("operationKind", "UNKNOWN"),
            "normalizedCommandSha256": entry.get(
                "normalizedCommandSha256", sha256_text("NO_COMMAND")
            ),
            "inputSetSha256": entry.get("inputSetSha256", sha256_text("NO_INPUTS")),
            "previousEntrySha256": previous,
            "budgetName": entry.get("budgetName"),
            "budgetBefore": entry.get("budgetBefore"),
            "budgetAfter": entry.get("budgetAfter"),
            "outcome": entry.get("outcome", "REJECTED"),
            "exitCode": entry.get("exitCode"),
            "progressType": entry.get("progressType"),
            "artifactHashes": entry.get("artifactHashes", {}),
        }
        complete["entrySha256"] = compute_entry_hash(complete)
        validate_schema(complete, schema)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical_json(complete) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return complete
    finally:
        append_guard.unlink(missing_ok=True)


def verify_ledger(
    contract: dict[str, Any],
    *,
    state: Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    path = ledger_path(contract, state)
    rows = read_ledger(
        path,
        schema_path=selected_root / ".coapi/schemas/operation-ledger-entry.schema.json",
    )
    return {
        "status": "PASS",
        "path": str(path),
        "entries": len(rows),
        "headSha256": rows[-1]["entrySha256"] if rows else None,
    }


def parse_input_hashes(values: Iterable[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise ControlError(f"Input hash must use name=sha256: {raw}")
        name, digest = raw.split("=", 1)
        lowered = digest.lower()
        if not name or not SHA256_PATTERN.fullmatch(lowered):
            raise ControlError(f"Invalid input hash: {raw}")
        parsed[name] = lowered
    return dict(sorted(parsed.items()))


def ensure_no_recursive_codex(argv: list[str]) -> None:
    for value in argv:
        executable = Path(value).name.lower()
        if executable in {"codex", "codex.exe", "codex.cmd", "codex.bat"}:
            raise ControlError("Recursive Codex invocation is forbidden")


def operation_fingerprint(
    argv: list[str],
    cwd: Path,
    phase: str,
    hypothesis_id: str,
    operation_kind: str,
    input_hashes: dict[str, str],
    mode: str,
) -> tuple[str, str, str]:
    normalized_command = {
        "argv": argv,
        "cwd": str(cwd.resolve()).lower(),
        "phase": phase,
        "hypothesisId": hypothesis_id,
        "operationKind": operation_kind,
        "mode": mode,
        "toolVersion": 2,
    }
    command_hash = sha256_text(canonical_json(normalized_command))
    input_hash = sha256_text(canonical_json(input_hashes))
    fingerprint = sha256_text(f"{command_hash}:{input_hash}")
    return fingerprint, command_hash, input_hash


def required_lock_for_operation(operation_kind: str) -> str | None:
    if operation_kind in {
        "STATIC_VALIDATION",
        "POLICY_VALIDATION",
        "PRIVATE_EXPOSURE_SCAN",
        "TEST_SUITE",
    }:
        return None
    if operation_kind in {
        "PACKAGE_BUILD",
        "WORKSHOP_PUBLISH",
        "LIVE_DEPLOY",
        "SERVER_RESTART",
        "PUBLIC_REPOSITORY_CREATE",
        "PUBLIC_REPOSITORY_PUSH",
    }:
        return "release"
    if operation_kind == "WORKBENCH":
        return "workbench"
    return "repository"


def terminate_owned_tree(process: subprocess.Popen[str]) -> None:
    try:
        owner = psutil.Process(process.pid)
        descendants = owner.children(recursive=True)
        for child in reversed(descendants):
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        try:
            owner.kill()
        except psutil.NoSuchProcess:
            pass
        psutil.wait_procs([*descendants, owner], timeout=5)
    except psutil.NoSuchProcess:
        return


def bounded_run(
    *,
    task_id: str,
    phase: str,
    hypothesis_id: str,
    operation_kind: str,
    timeout_seconds: float,
    expected_transition: str,
    argv: list[str],
    cwd: Path,
    input_hashes: dict[str, str],
    expected_artifacts: list[Path],
    lock_owner_pid: int | None,
    root: Path | None = None,
    state: Path | None = None,
    selected_contract_path: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    selected_state = state or state_root()
    contract = load_contract(selected_contract_path, root=selected_root)
    if contract["taskId"] != task_id:
        raise ControlError(
            f"Task ID {task_id} does not match active contract {contract['taskId']}"
        )
    if timeout_seconds <= 0 or timeout_seconds > 3600:
        raise ControlError("TimeoutSeconds must be between 0 and 3600")
    if not argv:
        raise ControlError("Command argv is required")
    ensure_inside_root(cwd, selected_root, "Working directory")
    if not contract_root_matches(contract["repository"]["root"], selected_root):
        raise ControlError("Task contract repository root does not match current root")
    current_branch = git_output(selected_root, "branch", "--show-current")
    if current_branch and current_branch != contract["repository"]["branch"]:
        raise ControlError("Task contract branch does not match current branch")
    for artifact in expected_artifacts:
        relative = ensure_inside_root(artifact, selected_root, "Expected artifact")
        if not allowed_repository_path(relative, contract["allowedPaths"]):
            raise ControlError(
                f"Expected artifact is outside contract allowedPaths: {relative.as_posix()}"
            )
    if operation_kind == "REPOSITORY_WRITE" and (
        expected_transition == "NONE" or not expected_artifacts
    ):
        raise ControlError(
            "Repository writes require an expected transition and allowlisted artifact"
        )
    ensure_no_recursive_codex(argv)
    if operation_kind in OPERATION_PERMISSIONS:
        permission = OPERATION_PERMISSIONS[operation_kind]
        if not contract["permissions"].get(permission, False):
            raise ControlError(
                f"Operation {operation_kind} requires disabled permission {permission}"
            )
    if operation_kind == "REPOSITORY_WRITE" and not contract["permissions"].get(
        "repositoryWrite", False
    ):
        raise ControlError("Repository write permission is disabled")
    lock_domain = required_lock_for_operation(operation_kind)
    if lock_domain:
        receipt = read_lock(lock_domain, selected_root, selected_state)
        if not receipt or not receipt.get("active"):
            raise ControlError(f"Operation {operation_kind} requires active {lock_domain} lock")
        if lock_owner_pid is not None and int(receipt.get("ownerPid", -1)) != lock_owner_pid:
            raise ControlError(
                f"PID {lock_owner_pid} does not own required {lock_domain} lock"
            )
        if receipt.get("taskId") != task_id or receipt.get("mode") != contract["mode"]:
            raise ControlError(f"{lock_domain} lock does not match active task and mode")
    fingerprint, command_hash, input_hash = operation_fingerprint(
        argv,
        cwd,
        phase,
        hypothesis_id,
        operation_kind,
        input_hashes,
        contract["mode"],
    )
    path = ledger_path(contract, selected_state)
    schema = selected_root / ".coapi/schemas/operation-ledger-entry.schema.json"
    rows = read_ledger(path, schema_path=schema)
    terminal_rows = [row for row in rows if row.get("outcome") in TERMINAL_OUTCOMES]
    identical = [
        row
        for row in terminal_rows
        if row.get("normalizedCommandSha256") == command_hash
        and row.get("inputSetSha256") == input_hash
    ]
    identical_limit = int(contract["budgets"].get("identicalCommandAttempts", 1))
    if len(identical) >= identical_limit:
        raise ControlError(
            f"Identical operation with unchanged inputs already reached its limit "
            f"({len(identical)}/{identical_limit})"
        )
    hypothesis_attempts = [
        row
        for row in terminal_rows
        if row.get("phase") == phase and row.get("hypothesisId") == hypothesis_id
    ]
    if len(hypothesis_attempts) >= 2:
        raise ControlError(f"Hypothesis {hypothesis_id} already used two attempts")
    budget_name = OPERATION_BUDGETS.get(operation_kind)
    budget_before: int | None = None
    budget_after: int | None = None
    if budget_name:
        if budget_name not in contract["budgets"]:
            raise ControlError(f"Operation budget is missing from contract: {budget_name}")
        used = sum(1 for row in terminal_rows if row.get("budgetName") == budget_name)
        budget_before = int(contract["consumed"][budget_name]) + used
        limit = int(contract["budgets"][budget_name])
        if budget_before >= limit:
            raise ControlError(f"Operation budget exhausted: {budget_name}")
        budget_after = budget_before + 1
    append_ledger(
        contract,
        {
            "phase": phase,
            "hypothesisId": hypothesis_id,
            "operationKind": operation_kind,
            "normalizedCommandSha256": command_hash,
            "inputSetSha256": input_hash,
            "budgetName": budget_name,
            "budgetBefore": budget_before,
            "budgetAfter": budget_before,
            "outcome": "STARTED",
        },
        state=selected_state,
        root=selected_root,
    )
    evidence_dir = selected_state / "TaskEvidence" / task_id / "commands" / fingerprint
    evidence_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="replace",
        shell=False,
    )
    outcome = "FAILED"
    exit_code: int | None = None
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        exit_code = process.returncode
        outcome = "SUCCEEDED" if exit_code == 0 else "FAILED"
    except subprocess.TimeoutExpired:
        terminate_owned_tree(process)
        stdout, stderr = process.communicate()
        outcome = "TIMED_OUT"
        exit_code = None
    stdout_path = evidence_dir / "stdout.txt"
    stderr_path = evidence_dir / "stderr.txt"
    stdout_path.write_text(sanitize_text(stdout), encoding="utf-8")
    stderr_path.write_text(sanitize_text(stderr), encoding="utf-8")
    artifact_hashes: dict[str, str] = {}
    if outcome == "SUCCEEDED":
        for artifact in expected_artifacts:
            resolved = artifact.resolve()
            try:
                relative = resolved.relative_to(selected_root)
            except ValueError as exc:
                raise ControlError(f"Expected artifact escaped repository: {resolved}") from exc
            if not resolved.is_file():
                outcome = "FAILED"
                stderr_path.write_text(
                    stderr_path.read_text(encoding="utf-8")
                    + f"\nMissing expected transition artifact: {relative}\n",
                    encoding="utf-8",
                )
                break
            artifact_hashes[str(relative).replace("\\", "/")] = sha256_file(resolved)
        if expected_transition != "NONE" and not expected_artifacts:
            outcome = "FAILED"
            stderr_path.write_text(
                stderr_path.read_text(encoding="utf-8")
                + "\nExpectedTransition requires at least one expected artifact.\n",
                encoding="utf-8",
            )
    terminal = append_ledger(
        contract,
        {
            "phase": phase,
            "hypothesisId": hypothesis_id,
            "operationKind": operation_kind,
            "normalizedCommandSha256": command_hash,
            "inputSetSha256": input_hash,
            "budgetName": budget_name,
            "budgetBefore": budget_before,
            "budgetAfter": budget_after,
            "outcome": outcome,
            "exitCode": exit_code,
            "artifactHashes": artifact_hashes,
        },
        state=selected_state,
        root=selected_root,
    )
    return {
        "status": "PASS" if outcome == "SUCCEEDED" else "FAIL",
        "outcome": outcome,
        "exitCode": exit_code,
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "fingerprint": fingerprint,
        "ledgerEntrySha256": terminal["entrySha256"],
        "stdoutSha256": sha256_file(stdout_path),
        "stderrSha256": sha256_file(stderr_path),
        "artifactHashes": artifact_hashes,
        "expectedTransition": expected_transition,
    }


def register_progress(
    progress_type: str,
    phase: str,
    hypothesis_id: str | None,
    summary: str,
    *,
    root: Path | None = None,
    state: Path | None = None,
    selected_contract_path: Path | None = None,
) -> dict[str, Any]:
    selected_root = root or repo_root()
    contract = load_contract(selected_contract_path)
    if progress_type not in PROGRESS_TYPES:
        raise ControlError(f"Progress type is not allowed: {progress_type}")
    lowered = summary.lower()
    forbidden = ("regenerated report", "renumbered post", "waited", "repeated summary")
    if any(phrase in lowered for phrase in forbidden):
        raise ControlError("Report regeneration, Post renumbering, waiting, or summary repetition is not progress")
    summary_hash = sha256_text(sanitize_text(summary))
    entry = append_ledger(
        contract,
        {
            "phase": phase,
            "hypothesisId": hypothesis_id,
            "operationKind": "PROGRESS",
            "normalizedCommandSha256": sha256_text("PROGRESS"),
            "inputSetSha256": summary_hash,
            "outcome": "SUCCEEDED",
            "progressType": progress_type,
        },
        state=state,
        root=selected_root,
    )
    return {
        "status": "PASS",
        "progressType": progress_type,
        "summarySha256": summary_hash,
        "ledgerEntrySha256": entry["entrySha256"],
    }


def instruction_candidates(root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for pattern in ("AGENTS.md", "AGENTS.override.md"):
        candidates.update(path.resolve() for path in root.rglob(pattern) if path.is_file())
    config = root / ".codex/config.toml"
    if config.is_file():
        candidates.add(config.resolve())
    agents = root / ".codex/agents"
    if agents.is_dir():
        candidates.update(path.resolve() for path in agents.glob("*.toml") if path.is_file())
    for parent in root.parents:
        for name in ("AGENTS.md", "AGENTS.override.md"):
            candidate = parent / name
            if candidate.is_file():
                candidates.add(candidate.resolve())
    return sorted(candidates, key=lambda item: str(item).lower())


def validate_instruction_chain(
    root: Path,
    allowlist_path: Path,
) -> dict[str, Any]:
    allowlist = read_json(allowlist_path)
    if allowlist.get("schemaVersion") != 2:
        raise ControlError("Instruction allowlist schemaVersion must be 2")
    approved = {
        item["path"].replace("\\", "/"): item["sha256"].lower()
        for item in allowlist.get("approved", [])
    }
    discovered: list[dict[str, Any]] = []
    unknown: list[str] = []
    hash_mismatch: list[str] = []
    total_bytes = 0
    active_candidates = instruction_candidates(root)
    for candidate in active_candidates:
        try:
            relative = candidate.relative_to(root).as_posix()
        except ValueError:
            relative = str(candidate)
        digest = sha256_file(candidate)
        size = candidate.stat().st_size
        total_bytes += size
        discovered.append({"path": relative, "bytes": size, "sha256": digest})
        if relative not in approved:
            unknown.append(relative)
        elif approved[relative] != digest:
            hash_mismatch.append(relative)
    missing = sorted(set(approved) - {row["path"] for row in discovered})
    maximum = int(allowlist.get("maxInstructionBytes", 65536))
    errors = []
    if unknown:
        errors.append(f"unknown active instruction/config files: {', '.join(unknown)}")
    if missing:
        errors.append(f"allowlisted instruction/config files missing: {', '.join(missing)}")
    if hash_mismatch:
        errors.append(f"instruction/config hash mismatch: {', '.join(hash_mismatch)}")
    if total_bytes > maximum:
        errors.append(f"instruction bytes {total_bytes} exceed maximum {maximum}")
    config_path = root / ".codex/config.toml"
    if config_path.is_file():
        import tomllib

        config = tomllib.loads(config_path.read_text(encoding="utf-8-sig"))
        if config.get("project_doc_fallback_filenames") not in ([], None):
            errors.append("project_doc_fallback_filenames must be empty")
        if config.get("agents", {}).get("enabled") is not False:
            errors.append("agents.enabled must be false during Stage 1")
        if config.get("features", {}).get("multi_agent") is not False:
            errors.append("features.multi_agent must be false during Stage 1")
    custom_agent_files = list((root / ".codex/agents").glob("*.toml")) if (root / ".codex/agents").is_dir() else []
    if custom_agent_files:
        errors.append("custom agent files are active")
    global_sources: list[str] = []
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).resolve()
    for name in ("AGENTS.md", "AGENTS.override.md", "config.toml"):
        candidate = codex_home / name
        if candidate.is_file() and candidate.resolve() not in active_candidates:
            global_sources.append(str(candidate))
    warnings = (
        [
            "Global Codex sources can affect this project and were inventoried but not edited: "
            + ", ".join(global_sources)
        ]
        if global_sources
        else []
    )
    return {
        "status": "PASS" if not errors else "FAIL",
        "discovered": discovered,
        "globalSources": global_sources,
        "totalBytes": total_bytes,
        "maxBytes": maximum,
        "warnings": warnings,
        "errors": errors,
    }


def validate_stage1_wrapper_ownership(root: Path) -> list[str]:
    errors: list[str] = []
    tools_root = root / "Tools/COAPI"
    for file in sorted(tools_root.glob("*")):
        if not file.is_file() or file.name == "coapi_control.py":
            continue
        if file.suffix.lower() not in {".py", ".ps1"}:
            continue
        source = file.read_text(encoding="utf-8-sig", errors="replace")
        if re.search(r"\bsubprocess\.(?:Popen|run|call|check_call|check_output)\s*\(", source):
            errors.append(
                f"{file.relative_to(root)} launches a process outside coapi_control.py"
            )
        if re.search(r"(?im)\b(?:Start-Process|System\.Diagnostics\.Process)\b", source):
            errors.append(
                f"{file.relative_to(root)} bypasses the bounded process owner"
            )
        high_risk_name = re.search(
            r"(?im)(?:ArmaReforger(?:Server)?|ArmaReforgerWorkbench|Workbench|"
            r"WinSCP|sftp|ssh|rcon|codex)(?:\.exe|\.cmd|\.bat)?",
            source,
        )
        process_route = re.search(
            r"(?im)(?:subprocess\.(?:Popen|run|call|check_call|check_output)|"
            r"os\.system|Start-Process|System\.Diagnostics\.Process|^\s*&\s*)",
            source,
        )
        if high_risk_name and process_route and file.name not in {
            "Acquire-COAPILock.ps1",
            "Invoke-COAPIBounded.ps1",
            "Register-COAPIProgress.ps1",
        }:
            errors.append(
                f"{file.relative_to(root)} contains a direct high-risk process route"
            )
    return errors


def validate_schema_directory(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / ".coapi/schemas").glob("*.json")):
        try:
            schema = read_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
        except (ControlError, jsonschema.SchemaError) as exc:
            errors.append(f"{path.name}: {exc}")
    if not list((root / ".coapi/schemas").glob("*.json")):
        errors.append("no schemas found")
    return errors


def validate_production_lock(path: Path) -> list[str]:
    if not path.is_file():
        return []
    data = read_json(path)
    errors: list[str] = []
    seen: set[str] = set()
    for index, mod in enumerate(data.get("mods", [])):
        mod_id = str(mod.get("modId", "")).upper()
        if not mod.get("version"):
            errors.append(f"{path.name} mod {index} has no exact version")
        if mod_id in seen:
            errors.append(f"{path.name} duplicates mod ID {mod_id}")
        seen.add(mod_id)
    return errors


def validate_policy(root: Path | None = None) -> dict[str, Any]:
    selected_root = root or repo_root()
    errors = validate_schema_directory(selected_root)
    try:
        contract = load_contract(
            contract_path(selected_root),
            allow_terminal=True,
        )
    except ControlError as exc:
        contract = None
        errors.append(str(exc))
    if contract:
        if not contract_root_matches(contract["repository"]["root"], selected_root):
            errors.append("contract repository root does not match current root")
        current_branch = git_output(selected_root, "branch", "--show-current") or ""
        ci_branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or ""
        observed_branch = current_branch or ci_branch
        if observed_branch and contract["repository"]["branch"] != observed_branch:
            errors.append("contract branch does not match current branch")
        for permission in SENSITIVE_PERMISSIONS.values():
            if contract["mode"] != "RELEASE" and contract["permissions"].get(permission, False):
                errors.append(f"sensitive permission {permission} enabled outside RELEASE")
    instruction_path = selected_root / ".coapi/policy/instruction-allowlist.json"
    try:
        instruction = validate_instruction_chain(selected_root, instruction_path)
        errors.extend(instruction["errors"])
    except ControlError as exc:
        instruction = {"status": "FAIL", "errors": [str(exc)]}
        errors.append(str(exc))
    allowlist = selected_root / ".coapi/policy/package-source-allowlist.txt"
    denylist = selected_root / ".coapi/policy/package-denylist.txt"
    if not allowlist.is_file() or not denylist.is_file():
        errors.append("package source allowlist and denylist are required")
    else:
        allowed = allowlist.read_text(encoding="utf-8-sig").lower()
        denied = denylist.read_text(encoding="utf-8-sig").lower()
        for forbidden in (".codex/", ".coapi/", "reports/", "tools/", "workbenchplugins/"):
            if forbidden in allowed:
                errors.append(f"package source allowlist contains forbidden root {forbidden}")
        for required in (".codex/", ".coapi/", "reports/", "tools/", "workbenchplugins/"):
            if required not in denied:
                errors.append(f"package denylist is missing {required}")
    for path in (
        selected_root / "Tools/COAPI",
        selected_root / "coapi.ps1",
    ):
        files = list(path.rglob("*")) if path.is_dir() else [path]
        for file in files:
            if not file.is_file() or file.name == "coapi_control.py":
                continue
            if file.suffix.lower() not in {".py", ".ps1"}:
                continue
            text = file.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"(?im)^\s*(?:&\s*)?codex(?:\.exe)?\b", text):
                errors.append(f"recursive Codex invocation detected in {file.relative_to(selected_root)}")
    errors.extend(validate_stage1_wrapper_ownership(selected_root))
    for lock in (
        selected_root / "Modsets/production.direct.lock.json",
        selected_root / "Modsets/production.effective.lock.json",
    ):
        errors.extend(validate_production_lock(lock))
    identity = read_json(selected_root / ".codex/ADDON_IDENTITY.json")
    gproj = (selected_root / "addon.gproj").read_text(encoding="utf-8-sig")
    if identity["activeGuid"] not in gproj:
        errors.append("addon.gproj does not contain canonical active GUID")
    if identity["legacyGuid"] in gproj:
        errors.append("addon.gproj still uses legacy GUID")
    return {
        "schemaVersion": 2,
        "status": "PASS" if not errors else "FAIL",
        "mode": contract.get("mode") if contract else None,
        "taskId": contract.get("taskId") if contract else None,
        "contractState": contract.get("state") if contract else None,
        "instructionChain": instruction,
        "productionLocks": (
            "VALIDATED"
            if (selected_root / "Modsets/production.direct.lock.json").is_file()
            else "NOT_CREATED_STAGE3"
        ),
        "errors": errors,
    }


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def command_contract(args: argparse.Namespace) -> int:
    contract = load_contract(
        Path(args.path).resolve() if args.path else None,
        allow_terminal=True,
        allow_expired=args.allow_expired,
    )
    print_json(contract)
    return 0


def command_lock(args: argparse.Namespace) -> int:
    if args.lock_action == "status":
        print_json(lock_status())
    elif args.lock_action == "acquire":
        print_json(acquire_lock(args.domain, args.task_id, args.mode, args.owner_pid))
    elif args.lock_action == "release":
        print_json(release_lock(args.domain, args.owner_pid, args.nonce))
    return 0


def command_ledger(args: argparse.Namespace) -> int:
    contract = load_contract(allow_terminal=True, allow_expired=True)
    print_json(verify_ledger(contract))
    return 0


def command_bounded(args: argparse.Namespace) -> int:
    argv = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv
    if not argv:
        raise ControlError("Bounded operation requires a command after --")
    result = bounded_run(
        task_id=args.task_id,
        phase=args.phase,
        hypothesis_id=args.hypothesis_id,
        operation_kind=args.operation_kind,
        timeout_seconds=args.timeout_seconds,
        expected_transition=args.expected_transition,
        argv=argv,
        cwd=Path(args.cwd).resolve(),
        input_hashes=parse_input_hashes(args.input_hash),
        expected_artifacts=[Path(item).resolve() for item in args.expected_artifact],
        lock_owner_pid=args.lock_owner_pid,
    )
    print_json(result)
    return 0 if result["status"] == "PASS" else 2


def command_progress(args: argparse.Namespace) -> int:
    print_json(
        register_progress(
            args.progress_type,
            args.phase,
            args.hypothesis_id,
            args.summary,
        )
    )
    return 0


def command_instruction(args: argparse.Namespace) -> int:
    root = repo_root()
    result = validate_instruction_chain(
        root,
        root / ".coapi/policy/instruction-allowlist.json",
    )
    print_json(result)
    return 0 if result["status"] == "PASS" else 2


def command_policy(_args: argparse.Namespace) -> int:
    result = validate_policy()
    print_json(result)
    return 0 if result["status"] == "PASS" else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)

    contract = sub.add_parser("contract")
    contract.add_argument("--path")
    contract.add_argument("--allow-expired", action="store_true")
    contract.set_defaults(func=command_contract)

    lock = sub.add_parser("lock")
    lock_sub = lock.add_subparsers(dest="lock_action", required=True)
    lock_sub.add_parser("status").set_defaults(func=command_lock)
    acquire = lock_sub.add_parser("acquire")
    acquire.add_argument("--domain", choices=sorted(LOCK_DOMAINS), required=True)
    acquire.add_argument("--task-id", required=True)
    acquire.add_argument("--mode", choices=["RECOVERY", "DEVELOPMENT", "RELEASE"], required=True)
    acquire.add_argument("--owner-pid", type=int, required=True)
    acquire.set_defaults(func=command_lock)
    release = lock_sub.add_parser("release")
    release.add_argument("--domain", choices=sorted(LOCK_DOMAINS), required=True)
    release.add_argument("--owner-pid", type=int, required=True)
    release.add_argument("--nonce")
    release.set_defaults(func=command_lock)

    ledger = sub.add_parser("ledger")
    ledger.set_defaults(func=command_ledger)

    bounded = sub.add_parser("bounded")
    bounded.add_argument("--task-id", required=True)
    bounded.add_argument("--phase", required=True)
    bounded.add_argument("--hypothesis-id", required=True)
    bounded.add_argument("--operation-kind", required=True)
    bounded.add_argument("--timeout-seconds", type=float, required=True)
    bounded.add_argument("--expected-transition", required=True)
    bounded.add_argument("--cwd", required=True)
    bounded.add_argument("--input-hash", action="append", default=[])
    bounded.add_argument("--expected-artifact", action="append", default=[])
    bounded.add_argument("--lock-owner-pid", type=int)
    bounded.add_argument("argv", nargs=argparse.REMAINDER)
    bounded.set_defaults(func=command_bounded)

    progress = sub.add_parser("progress")
    progress.add_argument("--progress-type", required=True)
    progress.add_argument("--phase", required=True)
    progress.add_argument("--hypothesis-id")
    progress.add_argument("--summary", required=True)
    progress.set_defaults(func=command_progress)

    instruction = sub.add_parser("instruction")
    instruction.set_defaults(func=command_instruction)

    policy = sub.add_parser("policy")
    policy.set_defaults(func=command_policy)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except ControlError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
