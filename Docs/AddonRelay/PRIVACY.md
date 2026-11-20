# Privacy and permissions

## Local diagnostics

The existing companion receives a selected project directory and exposes read-only diagnostic tools. Path-based tools accept project-relative inputs and enforce their documented bounds. The supported local diagnostic path does not require an AddonRelay account or API key.

To keep that existing path local, do not inherit legacy `ADDONRELAY_KEY` or `ADDONRELAY_URL` settings. A hosted mode, where separately available, has a different data path and must be reviewed before use.

## Your AI client

Your AI client receives the tool results. It may send those results and conversation content to its model provider under that client's settings and terms. A local companion does not make a remotely hosted model local. Review what you share with the client, especially logs, identifiers, paths, and project details.

## Planned project knowledge

Project Brain is planned to keep project knowledge separate, with deliberate sharing and documented retention/export/removal behavior. Those behaviors must be qualified with the release that offers them. This page does not claim that a complete Brain service is already available.

## Planned browser project visibility

Project linking will be an explicit choice. The dashboard is intended to receive approved activity and result summaries for the permitted account/project, with source and last-update information. Full source files, raw logs, credentials and entire Brain collections will not be uploaded by default. The integration must state its fields, limits, retention, export, unlink and deletion behavior before activation.

Humans use account sign-in; agents and backends use scoped credentials. A project key must not expose other projects or the owner’s whole account. Browser access does not make the underlying project public. Submitted activity covers only what the supported integration reports.

The planned monitoring flow is separate from paid hosted processing and from contributing a shared lesson. AddonRelay credits do not disclose your AI provider’s balance or conversation history. See [capability status](CAPABILITIES.md) for availability.

## Public reports

Share only the smallest reviewed reproduction that explains a problem. Keep credentials, raw logs, private project archives, server settings, personal identifiers, and third-party assets out of public issues and attachments. Use the [security policy](../../SECURITY.md) for a sensitive finding.

Public integration documentation describes the supported interface. The implementation, private operational knowledge, and detailed development plan are maintained separately. Customer materials are not automatically made public by connecting an agent.
