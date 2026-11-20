# Contributing to the public AddonRelay home

Useful contributions include clear product documentation, reproducible diagnostic reports, focused workflow suggestions, and scoped improvements to the retained backend policy, contracts, schemas, static tests, and public-export tools.

Start with [Capabilities](Docs/AddonRelay/CAPABILITIES.md) and [Roadmap](Docs/AddonRelay/ROADMAP.md). Keep current behavior, planned behavior, and historical evidence distinct. The full application and private operational services are outside this repository.

## Report a problem or propose a change

Use the issue templates for ordinary reports. State the component, version, expected behavior, actual outcome, and smallest useful reproducer. Use owned synthetic inputs when possible. Sensitive findings follow [SECURITY.md](SECURITY.md).

Before submitting source or examples, review [NOTICE.md](NOTICE.md). Public visibility does not grant a general reuse license. Contribute only material you are authorized to provide; a product suggestion is not permission to import third-party assets or private project data.

## Public boundary

Every new file needs an exact allowlist entry and reviewed provenance. Do not add operational reports, server configuration, credentials, private provider details, personal paths, game packages, third-party assets, generated databases, raw logs, or unverified source. Preserve existing historical records without treating them as current release acceptance.

Keep public CI static and read-only. It must not acquire production credentials, self-hosted runners, deployment authority, or access to a private Brain. See [Public mirror policy](Docs/PUBLIC_MIRROR_POLICY.md).

## Validate the change

Install the pinned validation dependencies, then run the existing framework and exporter tests:

```powershell
py -3 -m pip install -r requirements-public.txt
py -3 -m unittest Tests.policy.test_stage1_control_plane Tools.COAPI.Public.test_audit_public_export
```

For documentation, also inspect relative links, example commands, availability labels, and any accidental private data. A documentation change is not a native engine test.

Create the reviewed export outside the source checkout using the existing exporter:

```powershell
pwsh -NoProfile -File Tools/COAPI/Public/Export-COAPIPublicMirror.ps1
```

Review the export's findings and generated content/provenance manifests. Export the same inputs twice into fresh destinations and confirm the export identity is stable. Keep the generated manifests synchronized with the exact reviewed public files.

After staging the intended public files and manifests, verify the Git index:

```powershell
py -3 Tools/COAPI/Public/audit_public_export.py staged --repository . --patterns .publicmirror/public-content-deny-patterns.json
py -3 Tools/COAPI/Public/audit_public_export.py verify-index --repository .
git diff --cached --check
```

`verify-index` checks the exact staged blobs in a temporary export directory. The strict `verify --root` command is for a clean export directory, not a checkout containing Git metadata. Unexpected tracked files and changed bytes must still fail.

Public sources already use placeholder forms such as `<WORKSHOP_ID>` and `<EXACT_VERSION>`. The public-only placeholder policy does not authorize private-source transformation or publication.

## Pull request summary

Explain the concrete problem, the changed behavior, and the checks actually run. Policy fixes need evidence for the failure being corrected and for the protections retained. Do not weaken a check or relabel a failed result to obtain a pass.

Product documentation should link to the existing public guide rather than create another competing roadmap. Keep the licensing notice unchanged unless an explicit licensing decision is part of the change.
