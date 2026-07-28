#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "Tools/COAPI"
sys.path.insert(0, str(CONTROL))

import coapi_control as control  # noqa: E402
import schema_migrations as migrations  # noqa: E402


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def fixture_contract(root: Path, state: str = "IMPLEMENTING_CONTROL_PLANE") -> dict:
    budgets = {
        "staticValidations": 10,
        "policyValidations": 10,
        "repositoryWrites": 10,
        "workbenchInvocations": 0,
        "gameClientLaunches": 0,
        "serverBoots": 0,
        "packageBuilds": 0,
        "publicationAttempts": 0,
        "credentialReads": 0,
        "liveTransactions": 0,
        "serverRestarts": 0,
        "providerEdits": 0,
        "identicalCommandAttempts": 1,
    }
    return {
        "schemaVersion": 3,
        "taskId": "FIXTURE-STAGE1",
        "mode": "DEVELOPMENT",
        "objective": "Fixture",
        "createdAt": "2026-07-28T00:00:00Z",
        "expiresAt": "2099-01-01T00:00:00Z",
        "repository": {
            "root": str(root).replace("\\", "/"),
            "branch": "fixture",
            "head": "a" * 40,
            "base": None,
        },
        "permissions": {
            "repositoryWrite": True,
            "publicMirrorExport": True,
            "privateGitPush": True,
            "draftPullRequest": True,
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
        },
        "budgets": budgets,
        "consumed": {name: 0 for name in budgets},
        "state": state,
        "allowedPaths": ["Tools/COAPI/"],
        "relevantInputHashes": {},
        "requiredOutputs": [],
        "terminalStatuses": [
            "CONTROL_PLANE_V2_COMPLETE",
            "CONTROL_PLANE_V2_PARTIAL_BLOCKED",
            "CONTROL_PLANE_V2_UNSAFE_STATE",
        ],
        "releaseAuthorization": None,
        "publicMirrorAuthorization": None,
    }


class FixtureMixin:
    def make_repo(self, raw: str) -> tuple[Path, Path, Path]:
        root = Path(raw) / "repo"
        state = Path(raw) / "state"
        schemas = root / ".coapi/schemas"
        schemas.mkdir(parents=True)
        for name in (
            "task-contract.schema.json",
            "operation-ledger-entry.schema.json",
            "release-contract.schema.json",
        ):
            shutil.copy2(ROOT / ".coapi/schemas" / name, schemas / name)
        contract = root / ".coapi/contracts/current.json"
        write_json(contract, fixture_contract(root))
        return root, state, contract


class LockTests(FixtureMixin, unittest.TestCase):
    def test_second_writer_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, _ = self.make_repo(raw)
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(10)"],
                shell=False,
            )
            try:
                control.acquire_lock(
                    "repository",
                    "FIXTURE-STAGE1",
                    "DEVELOPMENT",
                    child.pid,
                    root=root,
                    state=state,
                )
                with self.assertRaisesRegex(control.ControlError, "active repository lock"):
                    control.acquire_lock(
                        "repository",
                        "OTHER-TASK",
                        "DEVELOPMENT",
                        os.getpid(),
                        root=root,
                        state=state,
                    )
            finally:
                child.terminate()
                child.wait(timeout=5)

    def test_stale_lock_is_preserved_before_replacement(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, _ = self.make_repo(raw)
            target = control.lock_path("repository", root, state)
            write_json(
                target,
                {
                    "domain": "repository",
                    "taskId": "DEAD",
                    "ownerPid": 99999999,
                    "ownerProcessStartEpoch": 0,
                },
            )
            receipt = control.acquire_lock(
                "repository",
                "FIXTURE-STAGE1",
                "DEVELOPMENT",
                os.getpid(),
                root=root,
                state=state,
            )
            self.assertTrue(receipt["active"])
            self.assertEqual(1, len(list((target.parent / "stale").glob("*.json"))))

    def test_release_lock_conflicts_with_workbench(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, _ = self.make_repo(raw)
            control.acquire_lock(
                "workbench",
                "FIXTURE-STAGE1",
                "DEVELOPMENT",
                os.getpid(),
                root=root,
                state=state,
            )
            with self.assertRaisesRegex(control.ControlError, "active workbench lock"):
                control.acquire_lock(
                    "release",
                    "FIXTURE-RELEASE",
                    "RELEASE",
                    os.getpid(),
                    root=root,
                    state=state,
                )


class OperationLedgerTests(FixtureMixin, unittest.TestCase):
    def test_hash_chain_validates_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, _ = self.make_repo(raw)
            contract = fixture_contract(root)
            first = control.append_ledger(
                contract,
                {
                    "phase": "TEST",
                    "operationKind": "STATIC_VALIDATION",
                    "outcome": "SUCCEEDED",
                },
                root=root,
                state=state,
            )
            second = control.append_ledger(
                contract,
                {
                    "phase": "TEST",
                    "operationKind": "PROGRESS",
                    "outcome": "SUCCEEDED",
                    "progressType": "TEST_STATE_CHANGED",
                },
                root=root,
                state=state,
            )
            self.assertEqual(first["entrySha256"], second["previousEntrySha256"])
            self.assertEqual(2, control.verify_ledger(contract, root=root, state=state)["entries"])
            path = control.ledger_path(contract, state)
            rows = path.read_text(encoding="utf-8").splitlines()
            changed = json.loads(rows[0])
            changed["phase"] = "TAMPERED"
            rows[0] = json.dumps(changed, separators=(",", ":"))
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(control.ControlError, "entry hash mismatch"):
                control.verify_ledger(contract, root=root, state=state)


class BoundedOperationTests(FixtureMixin, unittest.TestCase):
    def test_expired_contract_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, contract_path = self.make_repo(raw)
            expired = fixture_contract(root)
            expired["expiresAt"] = "2000-01-01T00:00:00Z"
            write_json(contract_path, expired)
            with self.assertRaisesRegex(control.ControlError, "expired"):
                control.load_contract(contract_path, root=root)

    def test_release_permission_requires_complete_release_authorization(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, contract_path = self.make_repo(raw)
            release = fixture_contract(root)
            release["mode"] = "RELEASE"
            release["permissions"]["workbench"] = True
            write_json(contract_path, release)
            with self.assertRaisesRegex(control.ControlError, "releaseAuthorization"):
                control.load_contract(contract_path, root=root)

    def test_modes_have_distinct_fail_closed_permission_sets(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, contract_path = self.make_repo(raw)
            recovery = fixture_contract(root)
            recovery["mode"] = "RECOVERY"
            recovery["permissions"]["publicMirrorExport"] = False
            recovery["permissions"]["privateGitPush"] = False
            recovery["permissions"]["draftPullRequest"] = False
            write_json(contract_path, recovery)
            self.assertEqual("RECOVERY", control.load_contract(contract_path, root=root)["mode"])

            recovery["permissions"]["privateGitPush"] = True
            write_json(contract_path, recovery)
            with self.assertRaisesRegex(control.ControlError, "not allowed in RECOVERY"):
                control.load_contract(contract_path, root=root)

            development = fixture_contract(root)
            development["permissions"]["publicRepositoryPush"] = True
            write_json(contract_path, development)
            with self.assertRaisesRegex(control.ControlError, "not allowed in DEVELOPMENT"):
                control.load_contract(contract_path, root=root)

    def test_public_repository_permission_requires_exact_authorization(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, contract_path = self.make_repo(raw)
            release = fixture_contract(root)
            release["mode"] = "RELEASE"
            release["permissions"]["publicRepositoryPush"] = True
            write_json(contract_path, release)
            with self.assertRaisesRegex(control.ControlError, "publicMirrorAuthorization"):
                control.load_contract(contract_path, root=root)

    def test_identical_rerun_rejected_changed_input_allows_second_attempt(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            kwargs = {
                "task_id": "FIXTURE-STAGE1",
                "phase": "STATIC",
                "hypothesis_id": "H1",
                "operation_kind": "STATIC_VALIDATION",
                "timeout_seconds": 5,
                "expected_transition": "NONE",
                "argv": [sys.executable, "-c", "print('pass')"],
                "cwd": root,
                "expected_artifacts": [],
                "lock_owner_pid": None,
                "root": root,
                "state": state,
                "selected_contract_path": contract_path,
            }
            first = control.bounded_run(input_hashes={"source": "1" * 64}, **kwargs)
            self.assertEqual("PASS", first["status"])
            with self.assertRaisesRegex(control.ControlError, "Identical operation"):
                control.bounded_run(input_hashes={"source": "1" * 64}, **kwargs)
            second = control.bounded_run(input_hashes={"source": "2" * 64}, **kwargs)
            self.assertEqual("PASS", second["status"])
            with self.assertRaisesRegex(control.ControlError, "already used two attempts"):
                control.bounded_run(input_hashes={"source": "3" * 64}, **kwargs)

    def test_live_action_and_recursive_codex_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            common = {
                "task_id": "FIXTURE-STAGE1",
                "phase": "LIVE",
                "hypothesis_id": "H1",
                "timeout_seconds": 5,
                "expected_transition": "NONE",
                "cwd": root,
                "input_hashes": {},
                "expected_artifacts": [],
                "lock_owner_pid": None,
                "root": root,
                "state": state,
                "selected_contract_path": contract_path,
            }
            with self.assertRaisesRegex(control.ControlError, "disabled permission"):
                control.bounded_run(
                    operation_kind="LIVE_DEPLOY",
                    argv=[sys.executable, "-c", "raise SystemExit(99)"],
                    **common,
                )
            with self.assertRaisesRegex(control.ControlError, "Recursive Codex"):
                control.bounded_run(
                    operation_kind="STATIC_VALIDATION",
                    argv=["codex", "exec", "anything"],
                    **common,
                )

    def test_timeout_is_finite_and_owned_process_is_stopped(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            result = control.bounded_run(
                task_id="FIXTURE-STAGE1",
                phase="TIMEOUT",
                hypothesis_id="H1",
                operation_kind="STATIC_VALIDATION",
                timeout_seconds=0.2,
                expected_transition="NONE",
                argv=[sys.executable, "-c", "import time; time.sleep(5)"],
                cwd=root,
                input_hashes={},
                expected_artifacts=[],
                lock_owner_pid=None,
                root=root,
                state=state,
                selected_contract_path=contract_path,
            )
            self.assertEqual("TIMED_OUT", result["outcome"])
            self.assertLess(result["elapsedSeconds"], 3)

    def test_terminal_contract_blocks_new_operation(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            terminal = fixture_contract(root, "CONTROL_PLANE_V2_COMPLETE")
            write_json(contract_path, terminal)
            with self.assertRaisesRegex(control.ControlError, "terminal"):
                control.bounded_run(
                    task_id="FIXTURE-STAGE1",
                    phase="STATIC",
                    hypothesis_id="H1",
                    operation_kind="STATIC_VALIDATION",
                    timeout_seconds=5,
                    expected_transition="NONE",
                    argv=[sys.executable, "-c", "print('must not run')"],
                    cwd=root,
                    input_hashes={},
                    expected_artifacts=[],
                    lock_owner_pid=None,
                    root=root,
                    state=state,
                    selected_contract_path=contract_path,
                )

    def test_repository_write_requires_allowlisted_transition_artifact(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            control.acquire_lock(
                "repository",
                "FIXTURE-STAGE1",
                "DEVELOPMENT",
                os.getpid(),
                root=root,
                state=state,
            )
            with self.assertRaisesRegex(control.ControlError, "allowedPaths"):
                control.bounded_run(
                    task_id="FIXTURE-STAGE1",
                    phase="WRITE",
                    hypothesis_id="H1",
                    operation_kind="REPOSITORY_WRITE",
                    timeout_seconds=5,
                    expected_transition="PATCH_WRITTEN",
                    argv=[sys.executable, "-c", "raise SystemExit(99)"],
                    cwd=root,
                    input_hashes={},
                    expected_artifacts=[root / "Reports/out.json"],
                    lock_owner_pid=os.getpid(),
                    root=root,
                    state=state,
                    selected_contract_path=contract_path,
                )


class ProgressAndInstructionTests(FixtureMixin, unittest.TestCase):
    def test_report_only_activity_is_not_progress(self):
        with tempfile.TemporaryDirectory() as raw:
            root, state, contract_path = self.make_repo(raw)
            with self.assertRaisesRegex(control.ControlError, "is not progress"):
                control.register_progress(
                    "TEST_STATE_CHANGED",
                    "REPORT",
                    "H1",
                    "Waited and regenerated report",
                    root=root,
                    state=state,
                    selected_contract_path=contract_path,
                )

    def test_unknown_nested_agents_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".codex").mkdir()
            agents = root / "AGENTS.md"
            config = root / ".codex/config.toml"
            agents.write_text("# Root\n", encoding="utf-8")
            config.write_text(
                'project_doc_fallback_filenames = []\n'
                "[agents]\n"
                "enabled = false\n"
                "[features]\n"
                "multi_agent = false\n",
                encoding="utf-8",
            )
            allowlist = root / ".coapi/policy/instruction-allowlist.json"
            write_json(
                allowlist,
                {
                    "schemaVersion": 2,
                    "maxInstructionBytes": 65536,
                    "approved": [
                        {"path": "AGENTS.md", "sha256": control.sha256_file(agents)},
                        {
                            "path": ".codex/config.toml",
                            "sha256": control.sha256_file(config),
                        },
                    ],
                },
            )
            self.assertEqual(
                "PASS",
                control.validate_instruction_chain(root, allowlist)["status"],
            )
            nested = root / "nested/AGENTS.md"
            nested.parent.mkdir()
            nested.write_text("# Unexpected\n", encoding="utf-8")
            result = control.validate_instruction_chain(root, allowlist)
            self.assertEqual("FAIL", result["status"])
            self.assertTrue(any("unknown active" in error for error in result["errors"]))

    def test_production_lock_without_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "production.direct.lock.json"
            write_json(path, {"mods": [{"modId": "A" * 16, "name": "Bad"}]})
            errors = control.validate_production_lock(path)
            self.assertTrue(any("no exact version" in error for error in errors))

    def test_direct_process_launch_outside_core_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            tools = root / "Tools/COAPI"
            tools.mkdir(parents=True)
            (tools / "unsafe.py").write_text(
                "import subprocess\nsubprocess.run(['cmd.exe'])\n",
                encoding="utf-8",
            )
            errors = control.validate_stage1_wrapper_ownership(root)
            self.assertTrue(any("outside coapi_control.py" in error for error in errors))


class SchemaMigrationTests(FixtureMixin, unittest.TestCase):
    def version_one_contract(self, root: Path) -> dict:
        value = fixture_contract(root)
        value["schemaVersion"] = 1
        value.pop("consumed")
        value.pop("requiredOutputs")
        value.pop("releaseAuthorization")
        value["terminalClassifications"] = value.pop("terminalStatuses")
        return value

    def test_explicit_migration_writes_diff_and_backup(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, _ = self.make_repo(raw)
            input_path = root / "input.json"
            output_path = root / "output.json"
            diff_path = root / "diff.json"
            backup_root = root / "backups"
            write_json(input_path, self.version_one_contract(root))
            write_json(output_path, {"old": True})
            result = migrations.migrate_file(
                schema_name="task-contract",
                input_path=input_path,
                output_path=output_path,
                schema_path=root / ".coapi/schemas/task-contract.schema.json",
                diff_path=diff_path,
                apply=True,
                backup_root=backup_root,
            )
            self.assertEqual("PASS", result["status"])
            self.assertEqual(3, json.loads(output_path.read_text())["schemaVersion"])
            self.assertTrue(diff_path.is_file())
            self.assertEqual(1, len(list(backup_root.glob("*.json"))))

    def test_future_schema_and_implicit_apply_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            root, _, _ = self.make_repo(raw)
            with self.assertRaisesRegex(control.ControlError, "future schemaVersion"):
                migrations.migrate_document("task-contract", {"schemaVersion": 99})
            path = root / "input.json"
            write_json(path, self.version_one_contract(root))
            with self.assertRaisesRegex(control.ControlError, "explicit --apply"):
                migrations.migrate_file(
                    schema_name="task-contract",
                    input_path=path,
                    output_path=root / "output.json",
                    schema_path=root / ".coapi/schemas/task-contract.schema.json",
                    diff_path=root / "diff.json",
                    apply=False,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
