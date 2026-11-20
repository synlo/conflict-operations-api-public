# Working in the AddonRelay public documentation

This repository contains customer documentation and the supported integration contract. Read `README.md`, `Docs/AddonRelay/CAPABILITIES.md`, and `NOTICE.md` before making changes.

## Product direction

- The current product direction combines agent-first local tools with a planned responsive browser dashboard for project activity, usage, credits and connections. No separate desktop GUI is required. The dashboard is optional for local use, but part of the intended full product.
- A supporting command-line path is planned for setup and diagnostics. Do not invent commands or describe them as released.
- Distinguish existing read-only tools from planned native execution, project Brain, scoped activity connections and browser monitoring. Documentation does not activate public accounts, hosted jobs or billing.
- Describe human sign-in and scoped agent credentials separately. Local activity is not a credit charge; AddonRelay credits are not third-party model credits. Do not invent endpoints, live behavior or account access.
- Publish instructions customers need to connect safely: actual inputs, outputs, permissions, compatibility, availability, and useful errors.

## Publication boundary

- Keep implementation source, internal architecture, detailed implementation plans, controller algorithms, internal schemas, and private knowledge outside this repository.
- Never import operational reports, raw logs, customer projects, server settings, credentials, private endpoints, game assets, or downloaded addons.
- Public issue and pull-request descriptions, screenshots, attachments, workflow output, and releases need the same review as files.
- Do not automatically mirror a private checkout here. An allowed filename does not make its contents suitable for publication.
- Do not promise that public documentation or distributed executables cannot be inspected or independently reproduced.

## Validation and reporting

Use one writer for a file set. Stage only intended files, review the complete diff, run `python .github/scripts/check_public_docs.py`, and check example accuracy against the supported artifact. The checker covers tracked paths, links, and selected disclosure patterns; it is not a confidentiality guarantee.

Keep CI read-only and independent of production credentials, self-hosted runners, native Workbench, and deployment. Documentation changes do not establish a new application, game, or engine test result. Report only work and checks actually completed.
