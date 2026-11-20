#!/usr/bin/env python3
"""Check this documentation-only tree with the Python standard library.

The disclosure checks cover selected common mistakes, not every sensitive value.
Passing this script does not replace a review of material intended for publication.
Only tracked files are checked; local Git metadata and scratch files are ignored.
"""

import argparse
import ipaddress
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


PAGES = (
    "README", "START_HERE", "AGENT_GUIDE", "DEVELOPERS", "ARCHITECTURE",
    "BRAIN", "ROADMAP", "CAPABILITIES", "COMPATIBILITY", "PRIVACY",
    "COMMERCIAL", "FAQ",
)
ALLOWED = {
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "NOTICE.md", "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/workflows/public-policy.yml",
    ".github/scripts/check_public_docs.py",
    *(f"Docs/AddonRelay/{name}.md" for name in PAGES),
}
MAX_FILE_BYTES = 256 * 1024
PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-fine-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("api-secret", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b")),
    ("discord-webhook", re.compile(
        r"https://(?:(?:canary|ptb)\.)?discord(?:app)?\.com/api/webhooks/"
        r"[0-9]{15,22}/[A-Za-z0-9._-]{30,}")),
    ("private-windows-workspace", re.compile(r"(?i)\b[A-Z]:[\\/]w[\\/]")),
    ("private-user-path", re.compile(
        r"(?i)(?:[A-Z]:[\\/]Users[\\/]|/(?:home|Users)/)"
        r"(?!Public(?:[\\/]|$)|Default(?:[\\/]|$)|<|\{|\[|%)"
        r"[^\\/\s`'\"]+[\\/]")),
    ("private-session-path", re.compile(r"/(?:workspace/scratch|mnt/data)/")),
)
URL = re.compile(r"https?://[^\s<>\"'`]+")
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\s*\)")
REFERENCE_LINK = re.compile(r"(?m)^ {0,3}\[(?!\^)[^\]\n]+\]:\s*(<[^>\n]+>|\S+)")


def placeholder(value):
    """Recognize deliberate examples without allowing arbitrary redaction labels."""
    upper = value.upper()
    return any(word in upper for word in (
        "YOUR_USERNAME", "YOUR_USER", "EXAMPLE_USER", "EXAMPLEUSER",
        "YOUR_TOKEN", "TOKEN_FROM_ENV", "REPLACE_WITH", "EXAMPLE_TOKEN",
    ))


def disclosure_errors(name, text):
    errors = []
    for rule, pattern in PATTERNS:
        for match in pattern.finditer(text):
            if not placeholder(match.group()):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{name}:{line}: review {rule}")
    documentation_ranges = (
        ipaddress.ip_network("192.0.2.0/24"),
        ipaddress.ip_network("198.51.100.0/24"),
        ipaddress.ip_network("203.0.113.0/24"),
        ipaddress.ip_network("2001:db8::/32"),
    )
    for match in URL.finditer(text):
        try:
            host = urlsplit(match.group().rstrip(".,;)")).hostname
            address = ipaddress.ip_address(host or "")
        except ValueError:
            continue
        if address.is_loopback or address.is_unspecified:
            continue
        if any(address.version == net.version and address in net for net in documentation_ranges):
            continue
        line = text.count("\n", 0, match.start()) + 1
        errors.append(f"{name}:{line}: review literal-host-address")
    return errors


def without_code_fences(text):
    result = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append("")
        else:
            result.append("" if fence else line)
    return "\n".join(result)


def link_errors(root, name, text):
    errors = []
    prose = without_code_fences(text)
    targets = [m.group(1).strip("<>") for pattern in (INLINE_LINK, REFERENCE_LINK)
               for m in pattern.finditer(prose)]
    for target in targets:
        try:
            parsed = urlsplit(target)
        except ValueError:
            errors.append(f"{name}: malformed link")
            continue
        if parsed.scheme in {"http", "https", "mailto"} or target.startswith("//"):
            continue
        if not parsed.path and not parsed.scheme:
            continue
        if parsed.scheme or "\\" in parsed.path or parsed.path.startswith("/"):
            errors.append(f"{name}: unsupported local link")
            continue
        candidate = (root / name).parent / unquote(parsed.path)
        try:
            relative = candidate.resolve().relative_to(root).as_posix()
        except ValueError:
            errors.append(f"{name}: link escapes repository")
            continue
        if relative not in ALLOWED or not candidate.is_file():
            errors.append(f"{name}: missing or unapproved relative link target: {parsed.path}")
    return errors


def check(root):
    root = Path(root).resolve()
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=True, capture_output=True,
    )
    entries = result.stdout.decode("utf-8").split("\0")
    tracked = {}
    errors = []
    for entry in filter(None, entries):
        metadata, name = entry.split("\t", 1)
        mode, _, stage = metadata.split()
        if name in tracked or stage != "0":
            errors.append(f"{name}: unresolved index entry")
        tracked[name] = mode
    errors.extend(f"unexpected tracked file: {name}" for name in sorted(set(tracked) - ALLOWED))
    errors.extend(f"required document missing from index: {name}" for name in sorted(ALLOWED - set(tracked)))
    for name in sorted(set(tracked) & ALLOWED):
        path = root / name
        ancestors = [path, *path.parents]
        if tracked[name] not in {"100644", "100755"} or any(p.is_symlink() for p in ancestors if p != root):
            errors.append(f"{name}: tracked content must be a regular file without symlinks")
            continue
        if not path.is_file() or not path.resolve().is_relative_to(root):
            errors.append(f"{name}: missing or out-of-root tracked file")
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"{name}: file exceeds documentation size limit")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"{name}: content must be UTF-8")
            continue
        errors.extend(disclosure_errors(name, text))
        if name.endswith(".md"):
            errors.extend(link_errors(root, name, text))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        errors = check(args.root)
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError):
        print("FAIL: could not inspect the tracked documentation tree")
        return 1
    if errors:
        print("FAIL: public documentation checks")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(ALLOWED)} tracked documentation files; boundary, relative links and selected disclosure checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
