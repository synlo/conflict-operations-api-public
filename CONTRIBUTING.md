# Contributing

Public contributions should improve customer documentation, supported agent integration examples, and reproducible product reports. The initial product direction is a headless local connector for AI agents, with a supporting command-line path. Graphical application work is deferred.

## Before proposing a change

Check the [capability status](Docs/AddonRelay/CAPABILITIES.md) and [compatibility notes](Docs/AddonRelay/COMPATIBILITY.md). Name the exact installed component or documentation version when reporting behavior. Keep a hypothesis separate from an observed result.

Use the issue templates for problems and workflow suggestions. Provide the smallest owned, non-sensitive example that helps explain the result. Do not post private source, raw operational logs, personal data, credentials, server settings, or third-party assets. Security reports follow [SECURITY.md](SECURITY.md).

## Documentation changes

1. Keep the change focused on a customer question or supported interface.
2. Check commands and arguments against the release they describe.
3. Keep working relative links and accurate available/planned labels.
4. Stage the intended files and run `python .github/scripts/check_public_docs.py`.
5. Review the whole diff and pull-request text before publishing.

The current file allowlist is deliberately narrow. A new documentation path requires deliberate review of both its purpose and contents. Implementation code, detailed internal designs, private knowledge, and operational investigations belong in the private development workflow.

The public workflow validates documentation only. It does not build the application, run Workbench, publish packages, or reach production systems. The [rights notice](NOTICE.md) remains unchanged in substance; submitting a public change does not establish a new license for the project.
