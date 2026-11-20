# Privacy and permissions

## Local diagnostics

The existing companion receives a selected project directory and exposes read-only diagnostic tools. Path-based tools accept project-relative inputs and enforce their documented bounds. The supported local diagnostic path does not require an AddonRelay account or API key.

To keep that existing path local, do not inherit legacy `ADDONRELAY_KEY` or `ADDONRELAY_URL` settings. A hosted mode, where separately available, has a different data path and must be reviewed before use.

## Your AI client

Your AI client receives the tool results. It may send those results and conversation content to its model provider under that client's settings and terms. A local companion does not make a remotely hosted model local. Review what you share with the client, especially logs, identifiers, paths, and project details.

## Planned project knowledge

Project Brain is planned to keep project knowledge separate, with deliberate sharing and documented retention/export/removal behavior. Those behaviors must be qualified with the release that offers them. This page does not claim that a complete Brain service is already available.

## Public reports

Share only the smallest reviewed reproduction that explains a problem. Keep credentials, raw logs, private project archives, server settings, personal identifiers, and third-party assets out of public issues and attachments. Use the [security policy](../../SECURITY.md) for a sensitive finding.

Public integration documentation describes the supported interface. The implementation, private operational knowledge, and detailed development plan are maintained separately. Customer materials are not automatically made public by connecting an agent.
