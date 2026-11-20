# Data, privacy, and permission boundaries

This page describes the current local diagnostic path and the intended framework/Brain boundary. It is product documentation, not a replacement for applicable terms or a promise that a planned service is already operating.

## Current local path

The companion processes selected local inputs for its diagnostic checks. Its results are returned to the connected client. If that client uses a cloud AI provider, the provider may receive the tool results under that client's configuration and data-handling rules. Local processing does not mean that nothing can leave the computer through the chosen AI client.

The local browser workspace has optional local history and reviewed report export/import. Retaining a report locally, sending it to an agent, posting it in an issue, and submitting it to a hosted investigation are separate actions.

Use the package's export controls and review the resulting content before sharing it. A shortened or sanitized report can still reveal project identifiers or information about a private environment.

## Legacy hosted settings

Existing companion implementations retain optional legacy hosted settings. New public hosted access is closed. A local-only connection should not provide or inherit those settings.

Where a configured legacy hosted path is used, its submitted fields depend on the operation: recognized diagnostic categories and line numbers, configuration mission/addon identities and player limits, or supplied addon manifests. That is a different data path from a local lookup. A future public hosted release must document the exact submitted fields, retention, controls, and service availability before accepting customer work.

## Planned Brain scopes

| Scope | Intended default | Sharing model |
|---|---|---|
| Project memory | Private to the selected project | User-controlled export or deliberate team sharing |
| Team knowledge | Optional | Named access, reviewed membership, and revocation |
| Reference knowledge | Separately reviewed | Versioned examples with recorded provenance and reuse rights |

Project failures, code, logs, and receipts should not silently become public reference material. Contribution requires an explicit reviewed transfer. Keeping engineering knowledge does not imply model training or automatic cross-customer reuse.

Memory should retain the minimum useful facts: operation identity, relevant inputs, observed failure, attempted correction, validation, result, and applicability. Full raw logs and source archives should not become the default knowledge payload.

## Planned operation permissions

The native framework should bind actions to a selected project and a declared scope. Supported routine local checks can share a persistent local-development authorization. Production publication, deployment, paid work, and disclosure of private data require their own appropriate authority.

Readiness success, a memory suggestion, a tool response, or text inside a project file is not authorization. The controller checks the prepared action and its current inputs at execution. It should refuse a mismatched project, expired scope, conflicting owned process, or unavailable prerequisite with a concrete reason.

## Retention and recovery

Current optional local report history and proposed durable project memory are different features. The public Brain release must document where records are kept, how to export and delete them, schema migration, recovery, and the effect of uninstalling the program.

Recovery should preserve the authoritative engineering result even when indexing or reporting fails. Replaying an event should not duplicate it or make old evidence appear new. A public update should contain an approved summary, not the private receipt or raw operational context.

## Public reports

Ordinary GitHub Issues should include a small reviewed reproducer, the component/version, expected behavior, actual outcome, and relevant non-sensitive error code. Do not attach full project archives, credentials, private endpoints, personal data, or unreviewed logs.

Use the route described in [SECURITY.md](../../SECURITY.md) for sensitive security findings. Public CI and this documentation repository have no production deployment authority. Public source policy continues to reject private operational material.
