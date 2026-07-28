#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PUBLIC_TOOLS = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PUBLIC_TOOLS))

import audit_public_export as audit  # noqa: E402


class PublicExportRefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.patterns = audit.load_content_patterns(
            ROOT / ".publicmirror/public-content-deny-patterns.json"
        )

    def categories(self, relative: str, text: str | bytes) -> set[str]:
        data = text if isinstance(text, bytes) else text.encode("utf-8")
        return {
            row["category"]
            for row in audit.scan_bytes(relative, data, patterns=self.patterns)
        }

    def test_plaintext_credential_is_refused(self):
        payload = ("pass" + "word") + " = correct-horse-battery-staple"
        self.assertIn("PASSWORD_ASSIGNMENT", self.categories("config.txt", payload))

    def test_webhook_url_is_refused(self):
        payload = "https://" + "discord.com/api/" + "webhooks/" + "123456/abcdef"
        self.assertIn("WEBHOOK_URL", self.categories("hook.txt", payload))

    def test_private_key_is_refused(self):
        payload = "-----BE" + "GIN PRIVATE KEY-----\nnot-a-real-key"
        self.assertIn("PRIVATE_KEY", self.categories("key.txt", payload))

    def test_raw_server_json_is_refused(self):
        self.assertIn("RAW_SERVER_JSON", self.categories("config/Server.json", "{}"))

    def test_live_provider_endpoint_is_refused(self):
        payload = "https://" + "panel." + "gtxgaming.co.uk/account"
        self.assertIn("PROVIDER_PANEL_URL", self.categories("endpoint.txt", payload))

    def test_personal_home_path_is_refused(self):
        payload = "C:" + "\\Users\\" + "ExamplePerson\\private.txt"
        self.assertIn("PERSONAL_HOME_PATH", self.categories("path.txt", payload))

    def test_email_and_phone_are_refused(self):
        payload = ("person" + "@" + "example.com") + "\n" + ("555" + "-867-5309")
        categories = self.categories("contact.txt", payload)
        self.assertIn("EMAIL_ADDRESS", categories)
        self.assertIn("PHONE_NUMBER", categories)

    def test_hidden_env_is_refused(self):
        categories = self.categories("nested/.env", "SAFE=0")
        self.assertIn("HIDDEN_FILE", categories)
        self.assertIn("CREDENTIAL_FILE", categories)

    def test_symlink_or_reparse_source_is_refused(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "safe.txt"
            target.write_text("safe\n", encoding="utf-8")
            with mock.patch.object(
                audit,
                "is_reparse_point",
                side_effect=lambda path: Path(path).name == "safe.txt",
            ):
                with self.assertRaisesRegex(audit.AuditError, "symlink, junction, or reparse"):
                    audit.ensure_contained_file(root, "safe.txt")

    def write_fixture(self, root: Path, provenance_status: str = "COAPI_OWNED") -> dict[str, Path]:
        policy = root / ".publicmirror"
        policy.mkdir(parents=True)
        (root / "README.md").write_text("safe public source\n", encoding="utf-8")
        (policy / "allow.txt").write_text("README.md\n", encoding="utf-8")
        (policy / "deny.txt").write_text("Reports/**\n**/*.pak\n", encoding="utf-8")
        (policy / "patterns.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "patterns": [
                        {
                            "category": "PASSWORD_ASSIGNMENT",
                            "regex": r"password\\s*[:=]\\s*\\S+",
                            "rotationRequired": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (policy / "provenance.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "entries": [
                        {
                            "source": "README.md",
                            "destination": "README.md",
                            "status": provenance_status,
                            "basis": "fixture",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (policy / "placeholders.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "replacements": [
                        {"token": "{{SAFE_TOKEN}}", "replacement": "<SAFE_TOKEN>"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        return {
            "allowlist_path": policy / "allow.txt",
            "denylist_path": policy / "deny.txt",
            "patterns_path": policy / "patterns.json",
            "provenance_path": policy / "provenance.json",
            "placeholders_path": policy / "placeholders.json",
        }

    def test_unknown_third_party_source_is_refused(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "source"
            root.mkdir()
            policies = self.write_fixture(root, "EXCLUDED_THIRD_PARTY")
            with self.assertRaisesRegex(audit.AuditError, "excluded provenance"):
                audit.export_public_mirror(root, Path(raw) / "export", **policies)

    def test_binary_package_is_refused(self):
        categories = self.categories("package.pak", b"PK\x00binary")
        self.assertIn("FORBIDDEN_BINARY_PACKAGE", categories)
        self.assertIn("BINARY_CONTENT", categories)

    def test_report_folder_is_refused(self):
        self.assertIn("FORBIDDEN_PATH", self.categories("Reports/result.md", "safe"))

    def test_dev_bridge_leakage_is_refused(self):
        self.assertIn("DEV_BRIDGE_LEAKAGE", self.categories("Tools/mcp/output.json", "{}"))

    def test_changed_file_after_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "source"
            root.mkdir()
            policies = self.write_fixture(root)
            destination = Path(raw) / "export"
            audit.export_public_mirror(root, destination, **policies)
            (destination / "README.md").write_text("changed\n", encoding="utf-8")
            self.assertEqual("FAIL", audit.verify_manifest(destination)["status"])

    def test_public_workflow_secret_runner_and_unpinned_action_are_refused(self):
        secret_expression = "${{ sec" + "rets.KEY }}"
        workflow = (
            "on:\n  pull_request:\npermissions:\n  contents: read\n"
            "jobs:\n  test:\n    runs-on: self-" + "hosted\n"
            "    steps:\n      - uses: actions/checkout@v4\n"
            f"      - run: echo {secret_expression}\n"
        )
        categories = self.categories(".github/workflows/bad.yml", workflow)
        self.assertIn("PUBLIC_WORKFLOW_SELF_HOSTED", categories)
        self.assertIn("PUBLIC_WORKFLOW_SECRET_OR_ENVIRONMENT", categories)
        self.assertIn("PUBLIC_WORKFLOW_UNPINNED_ACTION", categories)

    def test_public_workflow_live_authority_is_refused(self):
        live_command = "sf" + "tp upload && rc" + "on restart && work" + "shop publish"
        workflow = (
            "on:\n  push:\npermissions:\n  contents: read\n"
            "jobs:\n  test:\n    runs-on: windows-latest\n"
            f"    steps:\n      - run: {live_command}\n"
        )
        self.assertIn(
            "PUBLIC_WORKFLOW_LIVE_AUTHORITY",
            self.categories(".github/workflows/live.yml", workflow),
        )

    def test_safe_fixture_exports_twice_with_same_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "source"
            root.mkdir()
            policies = self.write_fixture(root)
            first = audit.export_public_mirror(root, Path(raw) / "export-one", **policies)
            second = audit.export_public_mirror(root, Path(raw) / "export-two", **policies)
            self.assertEqual(first["exportIdentitySha256"], second["exportIdentitySha256"])
            self.assertEqual(first["manifestSha256"], second["manifestSha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
