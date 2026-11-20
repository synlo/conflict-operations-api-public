# Working in the AddonRelay public repository

This repository is a public documentation and roadmap home with a historical COAPI backend subset. Read `README.md`, `Docs/AddonRelay/CAPABILITIES.md`, `NOTICE.md`, and the existing public mirror policy before proposing a change.

## Scope

- Preserve the distinction between existing local diagnostics, the historical backend subset, and planned native framework/Brain capabilities.
- Do not describe a roadmap contract or illustrative command as an available tool.
- Do not import private repositories, operational reports, customer/project knowledge, raw logs, server settings, credentials, downloaded addons, or game assets.
- Keep the public workflow static, read-only, and independent of production systems.
- Preserve historical failures and evidence. New documentation is not a new engine acceptance result.

## Changes and validation

Use one writer for a given file set. Keep changes scoped, review the exact diff, and follow `CONTRIBUTING.md`. New files need explicit allowlist and provenance entries; changed bytes need a regenerated public manifest. Never weaken a scanner or change a failure into a pass merely to publish a document.

For product documentation, check relative links, code examples, status consistency, and accidental private data. For policy or exporter behavior changes, run the relevant existing tests and a focused regression that proves the failure being corrected.

Do not launch native Workbench, modify a game project, publish a Workshop package, access production hosts, or start a paid service as part of a public documentation task. Such operations are not provided by this repository.

## Reporting

Report the exact files changed, checks actually run, and any remaining publication limitation. Distinguish source inspection, local validation, remote CI, and runtime evidence. Do not claim that public visibility grants an open-source license.
