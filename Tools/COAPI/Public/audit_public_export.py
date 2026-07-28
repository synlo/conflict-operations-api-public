#!/usr/bin/env python3
"""Fail-closed scanner and deterministic exporter for the COAPI public mirror.

Findings never contain matched text. A category, stable redacted fingerprint,
object/path identifier, and line number are the most this module emits.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ALLOWED_PROVENANCE = {
    "COAPI_OWNED",
    "REDISTRIBUTION_LICENSE_VERIFIED",
    "GENERATED_PUBLIC_SAFE",
}
FORBIDDEN_PROVENANCE = {
    "EXCLUDED_UNKNOWN",
    "EXCLUDED_THIRD_PARTY",
    "EXCLUDED_PRIVATE_OPERATIONAL",
}
FORBIDDEN_BINARY_SUFFIXES = {
    ".pak",
    ".rdb",
    ".crx",
    ".zip",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".pfx",
    ".p12",
    ".key",
    ".dmp",
    ".mdmp",
}
FORBIDDEN_PATH_SEGMENTS = {
    ".git",
    "reports",
    "localserver",
    "backups",
    "backup",
    "logs",
    "proof-runs",
    "proof_runs",
    "workbenchplugins",
    "devbridge",
    "dev-bridge",
    "bridge-output",
    "artifacts",
}
APPROVED_HIDDEN_SEGMENTS = {".coapi", ".github", ".publicmirror"}
CREDENTIAL_CATEGORIES = {
    "PASSWORD_ASSIGNMENT",
    "API_TOKEN_OR_KEY",
    "WEBHOOK_URL",
    "PRIVATE_KEY",
    "SFTP_RCON_ADMIN_CREDENTIAL",
    "SESSION_COOKIE",
    "GITHUB_TOKEN",
}
PUBLIC_METADATA_FILES = {
    "public_export_manifest.json",
    "public_provenance_manifest.json",
}
SAFE_MARKERS = (
    "[redacted]",
    "<redacted>",
    "<secret_from_environment>",
    "<provider_target>",
    "<server_profile>",
    "<workshop_id>",
    "<exact_version>",
    "example.invalid",
    "127.0.0.1",
    "placeholder",
    "changeme",
)


class AuditError(RuntimeError):
    """A deterministic, secret-safe policy refusal."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise AuditError(f"Required policy file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AuditError(f"Invalid JSON policy file {path}: line {exc.lineno}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"JSON policy root must be an object: {path}")
    return value


def normalize_relative(raw: str, label: str) -> str:
    rendered = raw.replace("\\", "/").strip()
    candidate = PurePosixPath(rendered)
    if not rendered or candidate.is_absolute() or ".." in candidate.parts:
        raise AuditError(f"{label} must be a repository-relative path")
    normalized = candidate.as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or normalized == ".":
        raise AuditError(f"{label} cannot be empty")
    return normalized


def is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def ensure_contained_file(root: Path, relative: str) -> Path:
    root = root.resolve()
    candidate = root / relative
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if is_reparse_point(current):
            raise AuditError(f"Source path uses a symlink, junction, or reparse point: {relative}")
    try:
        candidate.resolve(strict=True).relative_to(root)
    except (FileNotFoundError, ValueError) as exc:
        raise AuditError(f"Source path is missing or escapes the repository: {relative}") from exc
    if not candidate.is_file():
        raise AuditError(f"Allowlisted source is not a regular file: {relative}")
    return candidate


def parse_allowlist(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen_sources: set[str] = set()
    seen_destinations: set[str] = set()
    for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = [part.strip() for part in stripped.split("=>", 1)]
        source = normalize_relative(parts[0], f"allowlist source at line {line_number}")
        destination = normalize_relative(
            parts[1] if len(parts) == 2 else parts[0],
            f"allowlist destination at line {line_number}",
        )
        if source in seen_sources:
            raise AuditError(f"Duplicate allowlist source at line {line_number}")
        if destination in seen_destinations:
            raise AuditError(f"Duplicate allowlist destination at line {line_number}")
        seen_sources.add(source)
        seen_destinations.add(destination)
        entries.append((source, destination))
    if not entries:
        raise AuditError("Public source allowlist is empty")
    return entries


def load_denylist(path: Path) -> list[str]:
    patterns = [
        line.strip().replace("\\", "/")
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not patterns:
        raise AuditError("Public path denylist is empty")
    return patterns


def path_matches_denylist(relative: str, patterns: Iterable[str]) -> bool:
    lowered = relative.lower()
    return any(
        fnmatch.fnmatchcase(lowered, pattern.lower())
        or fnmatch.fnmatchcase("/" + lowered, pattern.lower())
        for pattern in patterns
    )


def load_content_patterns(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if data.get("schemaVersion") != 1 or not isinstance(data.get("patterns"), list):
        raise AuditError("Content deny-pattern policy must use schemaVersion 1 and a patterns array")
    compiled: list[dict[str, Any]] = []
    for index, entry in enumerate(data["patterns"]):
        if not isinstance(entry, dict):
            raise AuditError(f"Content pattern {index} is not an object")
        category = str(entry.get("category", "")).strip()
        expression = str(entry.get("regex", ""))
        if not category or not expression:
            raise AuditError(f"Content pattern {index} is incomplete")
        try:
            regex = re.compile(expression, re.IGNORECASE | re.MULTILINE)
        except re.error as exc:
            raise AuditError(f"Content pattern {category} is invalid") from exc
        compiled.append(
            {
                "category": category,
                "regex": regex,
                "rotationRequired": bool(entry.get("rotationRequired", False)),
            }
        )
    return compiled


def load_provenance(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    data = load_json(path)
    if data.get("schemaVersion") != 1 or not isinstance(data.get("entries"), list):
        raise AuditError("Public provenance policy must use schemaVersion 1 and an entries array")
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for index, entry in enumerate(data["entries"]):
        if not isinstance(entry, dict):
            raise AuditError(f"Provenance entry {index} is not an object")
        source = normalize_relative(str(entry.get("source", "")), f"provenance source {index}")
        destination = normalize_relative(
            str(entry.get("destination", "")), f"provenance destination {index}"
        )
        status = str(entry.get("status", ""))
        if status not in ALLOWED_PROVENANCE | FORBIDDEN_PROVENANCE:
            raise AuditError(f"Unknown provenance status for {source}")
        key = (source, destination)
        if key in result:
            raise AuditError(f"Duplicate provenance entry for {source}")
        result[key] = {
            "source": source,
            "destination": destination,
            "status": status,
            "basis": str(entry.get("basis", "")).strip(),
        }
    return result


def load_placeholders(path: Path) -> list[tuple[str, str]]:
    data = load_json(path)
    if data.get("schemaVersion") != 1 or not isinstance(data.get("replacements"), list):
        raise AuditError("Public placeholder policy must use schemaVersion 1 and a replacements array")
    replacements: list[tuple[str, str]] = []
    for index, entry in enumerate(data["replacements"]):
        if not isinstance(entry, dict):
            raise AuditError(f"Placeholder replacement {index} is not an object")
        token = str(entry.get("token", ""))
        replacement = str(entry.get("replacement", ""))
        if not token or not replacement or token == replacement:
            raise AuditError(f"Placeholder replacement {index} is invalid")
        replacements.append((token, replacement))
    return replacements


def redacted_fingerprint(category: str, matched: str) -> str:
    return sha256_bytes((category + "\0" + matched).encode("utf-8", errors="replace"))[:16]


def finding(
    category: str,
    identifier: str,
    *,
    line: int | None,
    matched: str,
    location: str,
    disposition: str,
    rotation_required: bool = False,
) -> dict[str, Any]:
    return {
        "category": category,
        "objectIdentifier": identifier,
        "line": line,
        "redactedFingerprint": redacted_fingerprint(category, matched),
        "location": location,
        "publicMirrorDisposition": disposition,
        "rotationRequired": rotation_required,
    }


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in SAFE_MARKERS) or "{{" in value or "${" in value


def path_policy_findings(
    relative: str,
    *,
    identifier: str,
    location: str,
    disposition: str,
) -> list[dict[str, Any]]:
    normalized = relative.replace("\\", "/")
    lowered = normalized.lower()
    parts = PurePosixPath(normalized).parts
    lowered_parts = {part.lower() for part in parts}
    rows: list[dict[str, Any]] = []

    def add(category: str, marker: str = "path") -> None:
        rows.append(
            finding(
                category,
                identifier,
                line=None,
                matched=f"{marker}:{lowered}",
                location=location,
                disposition=disposition,
            )
        )

    if lowered_parts & FORBIDDEN_PATH_SEGMENTS:
        add("FORBIDDEN_PATH")
    if any(part.startswith(".") and part.lower() not in APPROVED_HIDDEN_SEGMENTS for part in parts):
        add("HIDDEN_FILE")
    if PurePosixPath(lowered).name == "server.json":
        add("RAW_SERVER_JSON")
    if PurePosixPath(lowered).name in {".env", "credentials", "credentials.json", "id_rsa"}:
        add("CREDENTIAL_FILE")
    suffix = PurePosixPath(lowered).suffix
    if suffix in FORBIDDEN_BINARY_SUFFIXES:
        add("FORBIDDEN_BINARY_PACKAGE", suffix)
    if suffix in {".log", ".dmp", ".mdmp", ".crash"}:
        add("RAW_LOG_OR_CRASH_DUMP", suffix)
    if "resourcedatabase.rdb" in lowered:
        add("GENERATED_DATABASE")
    if any(part in {"mcp", "mcp-handlers", "dev-bridge", "devbridge"} for part in lowered_parts):
        add("DEV_BRIDGE_LEAKAGE")
    return rows


def workflow_findings(
    relative: str,
    text: str,
    *,
    identifier: str,
    location: str,
    disposition: str,
) -> list[dict[str, Any]]:
    if not relative.replace("\\", "/").lower().startswith(".github/workflows/"):
        return []
    rows: list[dict[str, Any]] = []

    def add(category: str, line: int, marker: str) -> None:
        rows.append(
            finding(
                category,
                identifier,
                line=line,
                matched=marker,
                location=location,
                disposition=disposition,
            )
        )

    noncomment = [(index, line) for index, line in enumerate(text.splitlines(), 1) if not line.lstrip().startswith("#")]
    has_read_permissions = False
    for index, raw in noncomment:
        lowered = raw.lower()
        if re.search(r"\bruns-on\s*:\s*.*self-hosted", lowered):
            add("PUBLIC_WORKFLOW_SELF_HOSTED", index, "self-hosted")
        if "${{ secrets." in lowered or re.search(r"\benvironment\s*:", lowered):
            add("PUBLIC_WORKFLOW_SECRET_OR_ENVIRONMENT", index, "secret-or-environment")
        if re.search(r"\b(contents|actions|checks|deployments|id-token|packages|pull-requests|statuses)\s*:\s*write\b", lowered):
            add("PUBLIC_WORKFLOW_WRITE_PERMISSION", index, "write-permission")
        if re.search(r"\bcontents\s*:\s*read\b", lowered):
            has_read_permissions = True
        if re.search(r"^\s*(workflow_dispatch|repository_dispatch|schedule|workflow_call)\s*:", lowered):
            add("PUBLIC_WORKFLOW_NONPASSIVE_TRIGGER", index, "nonpassive-trigger")
        uses = re.search(r"\buses\s*:\s*([^\s#]+)", raw, re.IGNORECASE)
        if uses:
            target = uses.group(1).strip("'\"")
            if not target.startswith("./"):
                reference = target.rsplit("@", 1)[-1] if "@" in target else ""
                if not re.fullmatch(r"[0-9a-fA-F]{40}", reference):
                    add("PUBLIC_WORKFLOW_UNPINNED_ACTION", index, "unpinned-action")
        if re.search(
            r"\b(sftp|rcon|gtx|workshop|webhook|deploy(?:ment)?|publish(?:ing)?|server\s+restart)\b",
            lowered,
        ):
            add("PUBLIC_WORKFLOW_LIVE_AUTHORITY", index, "live-authority")
    if not has_read_permissions:
        add("PUBLIC_WORKFLOW_PERMISSIONS_NOT_READ_ONLY", 1, "missing-read-permissions")
    return rows


def scan_bytes(
    relative: str,
    data: bytes,
    *,
    patterns: list[dict[str, Any]],
    identifier: str | None = None,
    location: str = "current_tree",
    disposition: str = "EXCLUDE",
    report_generic_binary: bool = True,
) -> list[dict[str, Any]]:
    shown_identifier = identifier or relative
    rows = path_policy_findings(
        relative,
        identifier=shown_identifier,
        location=location,
        disposition=disposition,
    )
    if b"\x00" in data:
        if report_generic_binary:
            rows.append(
                finding(
                    "BINARY_CONTENT",
                    shown_identifier,
                    line=None,
                    matched=sha256_bytes(data),
                    location=location,
                    disposition=disposition,
                )
            )
        return rows
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        if report_generic_binary:
            rows.append(
                finding(
                    "NON_UTF8_CONTENT",
                    shown_identifier,
                    line=None,
                    matched=sha256_bytes(data),
                    location=location,
                    disposition=disposition,
                )
            )
        return rows

    for policy in patterns:
        for match in policy["regex"].finditer(text):
            matched = match.group(0)
            if is_placeholder(matched):
                continue
            rows.append(
                finding(
                    policy["category"],
                    shown_identifier,
                    line=line_number(text, match.start()),
                    matched=matched,
                    location=location,
                    disposition=disposition,
                    rotation_required=policy["rotationRequired"],
                )
            )
    rows.extend(
        workflow_findings(
            relative,
            text,
            identifier=shown_identifier,
            location=location,
            disposition=disposition,
        )
    )
    return rows


def deduplicate_findings(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in rows:
        key = (
            row["category"],
            row["objectIdentifier"],
            row["line"],
            row["redactedFingerprint"],
            row["location"],
        )
        if key not in seen:
            seen.add(key)
            result.append(row)
    result.sort(
        key=lambda item: (
            item["location"],
            item["objectIdentifier"],
            item["line"] or 0,
            item["category"],
        )
    )
    return result


def scan_tree(
    root: Path,
    *,
    patterns: list[dict[str, Any]],
    denylist: Iterable[str] = (),
    location: str = "export",
    disposition: str = "BLOCK_EXPORT",
) -> tuple[list[dict[str, Any]], int]:
    selected_root = root.resolve()
    rows: list[dict[str, Any]] = []
    count = 0
    for current, directories, files in os.walk(selected_root, followlinks=False):
        current_path = Path(current)
        retained: list[str] = []
        for directory in directories:
            path = current_path / directory
            relative = path.relative_to(selected_root).as_posix()
            if is_reparse_point(path):
                rows.append(
                    finding(
                        "REPARSE_OR_SYMLINK",
                        relative,
                        line=None,
                        matched=relative.lower(),
                        location=location,
                        disposition=disposition,
                    )
                )
            else:
                retained.append(directory)
        directories[:] = retained
        for name in files:
            path = current_path / name
            relative = path.relative_to(selected_root).as_posix()
            count += 1
            if is_reparse_point(path):
                rows.append(
                    finding(
                        "REPARSE_OR_SYMLINK",
                        relative,
                        line=None,
                        matched=relative.lower(),
                        location=location,
                        disposition=disposition,
                    )
                )
                continue
            if path_matches_denylist(relative, denylist):
                rows.append(
                    finding(
                        "DENYLISTED_PATH",
                        relative,
                        line=None,
                        matched=relative.lower(),
                        location=location,
                        disposition=disposition,
                    )
                )
            rows.extend(
                scan_bytes(
                    relative,
                    path.read_bytes(),
                    patterns=patterns,
                    location=location,
                    disposition=disposition,
                )
            )
    return deduplicate_findings(rows), count


def apply_placeholders(data: bytes, replacements: list[tuple[str, str]], relative: str) -> bytes:
    if b"\x00" in data:
        raise AuditError(f"Allowlisted source is binary: {relative}")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AuditError(f"Allowlisted source is not UTF-8 text: {relative}") from exc
    for token, replacement in replacements:
        text = text.replace(token, replacement)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.encode("utf-8")


def verify_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    selected_root = root.resolve()
    selected_manifest = manifest_path or selected_root / "public_export_manifest.json"
    manifest = load_json(selected_manifest)
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("files"), list):
        raise AuditError("Public export manifest is invalid")
    expected_paths = {str(row.get("path", "")) for row in manifest["files"]}
    expected_paths.add("public_export_manifest.json")
    actual_paths = {
        path.relative_to(selected_root).as_posix()
        for path in selected_root.rglob("*")
        if path.is_file() and not is_reparse_point(path)
    }
    errors: list[dict[str, Any]] = []
    for row in manifest["files"]:
        relative = str(row.get("path", ""))
        target = selected_root / relative
        actual = sha256_file(target) if target.is_file() else None
        if actual != row.get("sha256"):
            errors.append({"category": "MANIFEST_HASH_MISMATCH", "path": relative})
    for relative in sorted(expected_paths - actual_paths):
        errors.append({"category": "MANIFEST_FILE_MISSING", "path": relative})
    for relative in sorted(actual_paths - expected_paths):
        errors.append({"category": "MANIFEST_UNEXPECTED_FILE", "path": relative})
    identity_payload = {
        "files": manifest["files"],
        "provenanceManifest": manifest.get("provenanceManifest"),
    }
    computed_identity = sha256_bytes(canonical_json(identity_payload).encode("utf-8"))
    if computed_identity != manifest.get("exportIdentitySha256"):
        errors.append({"category": "EXPORT_IDENTITY_MISMATCH", "path": "public_export_manifest.json"})
    return {
        "status": "PASS" if not errors else "FAIL",
        "exportIdentitySha256": computed_identity,
        "fileCount": len(actual_paths),
        "errors": errors,
    }


def export_public_mirror(
    source_root: Path,
    destination_root: Path,
    *,
    allowlist_path: Path,
    denylist_path: Path,
    patterns_path: Path,
    provenance_path: Path,
    placeholders_path: Path,
) -> dict[str, Any]:
    source = source_root.resolve()
    destination = destination_root.resolve()
    try:
        destination.relative_to(source)
    except ValueError:
        pass
    else:
        raise AuditError("Public export destination must be outside the private repository")
    if destination.exists() and any(destination.iterdir()):
        raise AuditError("Public export destination must be new or empty")
    destination.mkdir(parents=True, exist_ok=True)

    allowlist = parse_allowlist(allowlist_path)
    denylist = load_denylist(denylist_path)
    patterns = load_content_patterns(patterns_path)
    provenance = load_provenance(provenance_path)
    placeholders = load_placeholders(placeholders_path)
    if set(allowlist) != set(provenance):
        missing = sorted(set(allowlist) - set(provenance))
        extra = sorted(set(provenance) - set(allowlist))
        raise AuditError(
            f"Allowlist/provenance mismatch (missing={len(missing)}, extra={len(extra)})"
        )

    provenance_rows: list[dict[str, Any]] = []
    for source_relative, destination_relative in allowlist:
        policy = provenance[(source_relative, destination_relative)]
        if policy["status"] not in ALLOWED_PROVENANCE:
            raise AuditError(f"Export refused unknown or excluded provenance: {source_relative}")
        if path_matches_denylist(destination_relative, denylist):
            raise AuditError(f"Export destination is denylisted: {destination_relative}")
        source_path = ensure_contained_file(source, source_relative)
        if source_path.stat().st_size > 5 * 1024 * 1024:
            raise AuditError(f"Allowlisted source exceeds the 5 MiB public limit: {source_relative}")
        output = apply_placeholders(source_path.read_bytes(), placeholders, source_relative)
        target = destination / destination_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(output)
        provenance_rows.append(
            {
                "source": source_relative,
                "destination": destination_relative,
                "status": policy["status"],
                "basis": policy["basis"],
                "sourceSha256": sha256_file(source_path),
                "outputSha256": sha256_bytes(output),
            }
        )

    findings, _ = scan_tree(destination, patterns=patterns, denylist=denylist)
    if findings:
        raise AuditError(f"Public export content gate found {len(findings)} finding(s)")
    provenance_manifest = {
        "schemaVersion": 1,
        "entries": sorted(provenance_rows, key=lambda item: item["destination"]),
    }
    provenance_manifest_path = destination / "public_provenance_manifest.json"
    write_json(provenance_manifest_path, provenance_manifest)

    files = [
        {
            "path": path.relative_to(destination).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(destination.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file() and path.name != "public_export_manifest.json"
    ]
    provenance_summary = {
        "path": "public_provenance_manifest.json",
        "sha256": sha256_file(provenance_manifest_path),
        "entryCount": len(provenance_rows),
    }
    identity_payload = {"files": files, "provenanceManifest": provenance_summary}
    identity = sha256_bytes(canonical_json(identity_payload).encode("utf-8"))
    manifest = {
        "schemaVersion": 1,
        "exportIdentitySha256": identity,
        "files": files,
        "provenanceManifest": provenance_summary,
    }
    manifest_path = destination / "public_export_manifest.json"
    write_json(manifest_path, manifest)

    findings, file_count = scan_tree(destination, patterns=patterns, denylist=denylist)
    if findings:
        raise AuditError(f"Final public export gate found {len(findings)} finding(s)")
    verification = verify_manifest(destination, manifest_path)
    if verification["status"] != "PASS":
        raise AuditError("Final public export manifest verification failed")
    return {
        "status": "PASS",
        "destination": str(destination),
        "exportIdentitySha256": identity,
        "manifestSha256": sha256_file(manifest_path),
        "provenanceManifestSha256": sha256_file(provenance_manifest_path),
        "fileCount": file_count,
        "findingCount": 0,
    }


def git_bytes(repository: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        raise AuditError(f"Git command failed safely: {' '.join(arguments[:2])}")
    return completed.stdout


def git_paths(repository: Path, *arguments: str) -> list[str]:
    raw = git_bytes(repository, *arguments)
    return [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]


def scan_git_index(repository: Path, patterns: list[dict[str, Any]]) -> dict[str, Any]:
    raw = git_bytes(repository, "ls-files", "-s", "-z")
    rows: list[dict[str, Any]] = []
    file_count = 0
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, blob, _stage = metadata.decode("ascii").split()
        relative = raw_path.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        file_count += 1
        if mode == "120000":
            rows.append(
                finding(
                    "REPARSE_OR_SYMLINK",
                    relative,
                    line=None,
                    matched=relative.lower(),
                    location="staged_tree",
                    disposition="BLOCK_PUBLIC_PUSH",
                )
            )
            continue
        data = git_bytes(repository, "cat-file", "blob", blob)
        rows.extend(
            scan_bytes(
                relative,
                data,
                patterns=patterns,
                identifier=relative,
                location="staged_tree",
                disposition="BLOCK_PUBLIC_PUSH",
            )
        )
    findings = deduplicate_findings(rows)
    return {
        "status": "PASS" if not findings else "FAIL",
        "fileCount": file_count,
        "findingCount": len(findings),
        "findings": findings,
    }


def git_history_blobs(repository: Path) -> list[tuple[str, str, int]]:
    raw = git_bytes(repository, "rev-list", "--objects", "--all")
    objects: dict[str, str] = {}
    for line in raw.decode("utf-8", errors="replace").splitlines():
        object_id, separator, path = line.partition(" ")
        if re.fullmatch(r"[0-9a-f]{40,64}", object_id):
            objects.setdefault(object_id, path if separator else f"object:{object_id[:12]}")
    if not objects:
        return []
    request = "".join(f"{object_id}\n" for object_id in objects).encode("ascii")
    checked = git_bytes(repository, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)", input_bytes=request)
    blobs: list[tuple[str, str, int]] = []
    for line in checked.decode("ascii", errors="replace").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "blob":
            blobs.append((parts[0], objects.get(parts[0], f"object:{parts[0][:12]}"), int(parts[2])))
    return blobs


def read_git_blobs(
    repository: Path, blobs: Iterable[tuple[str, str, int]]
) -> Iterable[tuple[str, str, int, bytes | None]]:
    process = subprocess.Popen(
        ["git", "-C", str(repository), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    assert process.stdin is not None and process.stdout is not None
    try:
        for object_id, path, expected_size in blobs:
            if expected_size > 25 * 1024 * 1024:
                yield object_id, path, expected_size, None
                continue
            process.stdin.write((object_id + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii", errors="replace").strip()
            parts = header.split()
            if len(parts) != 3 or parts[1] != "blob":
                raise AuditError("Git blob batch returned an invalid header")
            size = int(parts[2])
            data = process.stdout.read(size)
            process.stdout.read(1)
            yield object_id, path, size, data
    finally:
        process.stdin.close()
        process.wait(timeout=10)


def private_repository_audit(
    repository: Path,
    *,
    patterns: list[dict[str, Any]],
    metadata_files: Iterable[Path] = (),
) -> dict[str, Any]:
    selected = repository.resolve()
    rows: list[dict[str, Any]] = []
    tracked = set(git_paths(selected, "ls-files", "-z"))
    candidates = git_paths(selected, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    current_count = 0
    for relative in candidates:
        path = selected / relative
        if not path.is_file() or is_reparse_point(path):
            if is_reparse_point(path):
                rows.append(
                    finding(
                        "REPARSE_OR_SYMLINK",
                        relative,
                        line=None,
                        matched=relative.lower(),
                        location="current_tree" if relative in tracked else "local_only",
                        disposition="EXCLUDE",
                    )
                )
            continue
        current_count += 1
        location = "current_tree" if relative in tracked else "local_only"
        disposition = "EXCLUDE" if relative in tracked else "NOT_COPIED"
        if path.stat().st_size > 25 * 1024 * 1024:
            rows.extend(
                path_policy_findings(
                    relative,
                    identifier=relative,
                    location=location,
                    disposition=disposition,
                )
            )
            rows.append(
                finding(
                    "LARGE_FILE",
                    relative,
                    line=None,
                    matched=str(path.stat().st_size),
                    location=location,
                    disposition=disposition,
                )
            )
            continue
        rows.extend(
            scan_bytes(
                relative,
                path.read_bytes(),
                patterns=patterns,
                location=location,
                disposition=disposition,
                report_generic_binary=False,
            )
        )

    staged_paths = git_paths(selected, "diff", "--cached", "--name-only", "-z")
    if staged_paths:
        index = scan_git_index(selected, patterns)
        staged_set = set(staged_paths)
        rows.extend(
            row
            for row in index["findings"]
            if row["objectIdentifier"] in staged_set
        )

    history_blobs = git_history_blobs(selected)
    history_count = 0
    for object_id, relative, size, data in read_git_blobs(selected, history_blobs):
        history_count += 1
        identifier = f"{object_id[:16]}:{relative or '<unnamed>'}"
        if data is None:
            rows.extend(
                path_policy_findings(
                    relative or f"object-{object_id[:12]}",
                    identifier=identifier,
                    location="history",
                    disposition="NOT_COPIED_FRESH_HISTORY",
                )
            )
            rows.append(
                finding(
                    "LARGE_FILE",
                    identifier,
                    line=None,
                    matched=str(size),
                    location="history",
                    disposition="NOT_COPIED_FRESH_HISTORY",
                )
            )
            continue
        rows.extend(
            scan_bytes(
                relative or f"object-{object_id[:12]}",
                data,
                patterns=patterns,
                identifier=identifier,
                location="history",
                disposition="NOT_COPIED_FRESH_HISTORY",
                report_generic_binary=False,
            )
        )

    metadata_count = 0
    for path in metadata_files:
        if not path.is_file():
            continue
        metadata_count += 1
        rows.extend(
            scan_bytes(
                path.name,
                path.read_bytes(),
                patterns=patterns,
                identifier=f"github-metadata:{path.name}",
                location="github_metadata",
                disposition="NOT_COPIED",
            )
        )
    findings = deduplicate_findings(rows)
    category_counts: dict[str, int] = {}
    location_counts: dict[str, int] = {}
    for row in findings:
        category_counts[row["category"]] = category_counts.get(row["category"], 0) + 1
        location_counts[row["location"]] = location_counts.get(row["location"], 0) + 1
    current_rotation_categories = sorted(
        {
            row["category"]
            for row in findings
            if row["location"] in {"current_tree", "staged_tree", "local_only"}
            and row["category"] in CREDENTIAL_CATEGORIES
            and row["rotationRequired"]
        }
    )
    refs = git_bytes(selected, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").decode(
        "utf-8", errors="replace"
    ).splitlines()
    return {
        "schemaVersion": 1,
        "status": "COMPLETE_FINDINGS_RECORDED" if findings else "COMPLETE_NO_FINDINGS",
        "scope": {
            "currentCandidateFiles": current_count,
            "stagedChangedFiles": len(staged_paths),
            "reachableHistoryBlobs": history_count,
            "refsScanned": len(refs),
            "githubMetadataFiles": metadata_count,
        },
        "findingCount": len(findings),
        "categoryCounts": dict(sorted(category_counts.items())),
        "locationCounts": dict(sorted(location_counts.items())),
        "currentCredentialCategoriesRequiringRotation": current_rotation_categories,
        "findings": findings,
        "secretValuesIncluded": False,
    }


def command_export(args: argparse.Namespace) -> int:
    result = export_public_mirror(
        Path(args.source_root),
        Path(args.destination_root),
        allowlist_path=Path(args.allowlist),
        denylist_path=Path(args.denylist),
        patterns_path=Path(args.patterns),
        provenance_path=Path(args.provenance),
        placeholders_path=Path(args.placeholders),
    )
    if args.output:
        write_json(Path(args.output), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_audit(args: argparse.Namespace) -> int:
    patterns = load_content_patterns(Path(args.patterns))
    denylist = load_denylist(Path(args.denylist)) if args.denylist else []
    findings, count = scan_tree(Path(args.root), patterns=patterns, denylist=denylist)
    result = {
        "schemaVersion": 1,
        "status": "PASS" if not findings else "FAIL",
        "fileCount": count,
        "findingCount": len(findings),
        "findings": findings,
        "secretValuesIncluded": False,
    }
    if args.output:
        write_json(Path(args.output), result)
    print(json.dumps({key: value for key, value in result.items() if key != "findings"}, indent=2, sort_keys=True))
    return 0 if not findings else 2


def command_verify(args: argparse.Namespace) -> int:
    result = verify_manifest(Path(args.root), Path(args.manifest) if args.manifest else None)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


def command_staged(args: argparse.Namespace) -> int:
    result = scan_git_index(Path(args.repository), load_content_patterns(Path(args.patterns)))
    if args.output:
        write_json(Path(args.output), result)
    print(json.dumps({key: value for key, value in result.items() if key != "findings"}, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


def command_private(args: argparse.Namespace) -> int:
    result = private_repository_audit(
        Path(args.repository),
        patterns=load_content_patterns(Path(args.patterns)),
        metadata_files=[Path(value) for value in args.metadata],
    )
    write_json(Path(args.output), result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "findingCount": result["findingCount"],
                "categoryCounts": result["categoryCounts"],
                "locationCounts": result["locationCounts"],
                "currentCredentialCategoriesRequiringRotation": result[
                    "currentCredentialCategoriesRequiringRotation"
                ],
                "secretValuesIncluded": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    export = commands.add_parser("export", help="Create a deterministic allowlisted export")
    export.add_argument("--source-root", required=True)
    export.add_argument("--destination-root", required=True)
    export.add_argument("--allowlist", required=True)
    export.add_argument("--denylist", required=True)
    export.add_argument("--patterns", required=True)
    export.add_argument("--provenance", required=True)
    export.add_argument("--placeholders", required=True)
    export.add_argument("--output")
    export.set_defaults(handler=command_export)

    audit = commands.add_parser("audit", help="Audit an exported tree")
    audit.add_argument("--root", required=True)
    audit.add_argument("--patterns", required=True)
    audit.add_argument("--denylist")
    audit.add_argument("--output")
    audit.set_defaults(handler=command_audit)

    verify = commands.add_parser("verify", help="Verify a deterministic export manifest")
    verify.add_argument("--root", required=True)
    verify.add_argument("--manifest")
    verify.set_defaults(handler=command_verify)

    staged = commands.add_parser("staged", help="Audit the exact Git index")
    staged.add_argument("--repository", required=True)
    staged.add_argument("--patterns", required=True)
    staged.add_argument("--output")
    staged.set_defaults(handler=command_staged)

    private = commands.add_parser("private-audit", help="Run one redacted tree/ref/history audit")
    private.add_argument("--repository", required=True)
    private.add_argument("--patterns", required=True)
    private.add_argument("--output", required=True)
    private.add_argument("--metadata", action="append", default=[])
    private.set_defaults(handler=command_private)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.handler(args))
    except (AuditError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "secretValuesIncluded": False}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
