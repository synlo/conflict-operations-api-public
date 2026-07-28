# Conflict Operations API backend framework

This repository contains the public-safe backend control framework used by the Conflict Operations Arma Reforger project. It focuses on deterministic policy, task contracts, single-writer locking, bounded commands, tamper-evident receipts, schemas, tests, and sanitized source export.

The public repository is a fresh-history snapshot. It deliberately excludes the private control repository's history, operational reports, server configuration, credentials, provider details, packaged game content, downloaded addons, generated databases, logs, and deployment authority.

## Safety model

- Paths are excluded unless they appear in the exact public allowlist.
- Every exported file must have an allowed provenance classification.
- Content and workflow scans fail closed on credentials, personal data, private endpoints, forbidden binaries, unknown ownership, or live authority.
- RECOVERY, DEVELOPMENT, and RELEASE contracts have distinct permission sets.
- Public CI is static, read-only, GitHub-hosted, and does not use secrets or environments.
- A deterministic manifest binds every exported byte to one export identity.

## Local checks

Install the pinned validation dependencies:

```powershell
py -3 -m pip install -r requirements-public.txt
```

Run the framework and public-export refusal tests:

```powershell
py -3 -m unittest Tests.policy.test_stage1_control_plane Tools.COAPI.Public.test_audit_public_export
```

Create a clean export outside the source repository:

```powershell
pwsh -NoProfile -File Tools/COAPI/Public/Export-COAPIPublicMirror.ps1
```

Operational examples must use placeholders such as `<WORKSHOP_ID>`, `<EXACT_VERSION>`, `<SERVER_PROFILE>`, `<PROVIDER_TARGET>`, and `<SECRET_FROM_ENVIRONMENT>`. The exporter converts them to the angle-bracket public form.

## Scope and rights

This snapshot contains source owned by the Conflict Operations API project or material with separately verified redistribution status. Publication alone does not grant permission to copy, modify, or redistribute the material. See [NOTICE.md](NOTICE.md), [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [Docs/PUBLIC_MIRROR_POLICY.md](Docs/PUBLIC_MIRROR_POLICY.md).
