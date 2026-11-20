# AddonRelay

## Connect your AI agent to local Arma Reforger diagnostics

AddonRelay is being built to give AI agents and experienced developers a practical connection to their addon projects: inspect a problem, run an appropriate check, keep the result, and continue from verified work when a session ends.

**This is the public documentation and roadmap preview.** It also preserves the historical public COAPI backend subset. It is not yet an installable release of the complete Workbench framework and Brain.

The existing local companion implements six read-only diagnostic tools. Public native Workbench operations and persistent project repair memory are the next product milestones. [See exactly what is available and what is planned.](Docs/AddonRelay/CAPABILITIES.md)

**[Start here](Docs/AddonRelay/START_HERE.md) · [Connect an agent](Docs/AddonRelay/AGENT_GUIDE.md) · [Developer workflow](Docs/AddonRelay/DEVELOPERS.md) · [Public roadmap](Docs/AddonRelay/ROADMAP.md)**

## What the product is for

- Help an agent understand symbols, resource references, log categories, addon lists, and configuration in a selected project.
- Give developers useful inspections through a local interface, without requiring an AI subscription.
- Develop a controlled path for supported Workbench operations, with declared inputs, bounded execution, and results tied to the check performed.
- Build project memory that connects a failure, an attempted correction, and its actual validation, so repeated work can be avoided when the evidence still applies.

The first native target is an unrelated Arma Reforger addon on a supported Windows installation. Compatibility with other Enfusion products, arbitrary providers, or every AI client requires separate evidence.

## Three parts, one workflow

| Part | Responsibility | Public status |
|---|---|---|
| **AddonRelay** | The local client, agent connection, developer interface, documentation, and optional service experience | Local diagnostic implementation documented; full framework distribution is being prepared |
| **COAPI framework** | Project binding, readiness checks, controlled operations, receipts, and recovery | Historical backend subset is in this repository; general public native adapter is planned |
| **Brain** | Relevant project knowledge: problems, attempted repairs, outcomes, and evidence applicability | Public project-memory integration is planned |

Brain is an engineering-memory design. Connecting it does not require buying a new model, and local report history is not the same feature as the proposed persistent repair memory. [Read the Brain design.](Docs/AddonRelay/BRAIN.md)

## What a first useful result looks like

Today, a developer with a verified local companion package can connect a compatible stdio MCP client, select a project, find a symbol or resource, and receive a scoped diagnostic result. The local interface provides a human path to the same diagnostic categories. These checks do not compile or run the project.

The next native milestone is concrete: a developer selects an unrelated addon, completes a supported Workbench compile, reconnects after an interruption without launching a duplicate, and retrieves the result with its applicable project context. The [roadmap](Docs/AddonRelay/ROADMAP.md) describes the proof required before that workflow is advertised as available.

## Documentation

| I want to… | Read |
|---|---|
| Understand the product and get started | [Start here](Docs/AddonRelay/START_HERE.md) |
| Check current feature and delivery status | [Capabilities](Docs/AddonRelay/CAPABILITIES.md) |
| Connect my existing AI coding client | [Agent guide](Docs/AddonRelay/AGENT_GUIDE.md) |
| Work without an AI agent or extend the future framework | [Developer guide](Docs/AddonRelay/DEVELOPERS.md) |
| Understand execution, permissions, and recovery | [Architecture](Docs/AddonRelay/ARCHITECTURE.md) |
| Understand persistent project knowledge | [Brain](Docs/AddonRelay/BRAIN.md) |
| See launch milestones and their acceptance | [Roadmap](Docs/AddonRelay/ROADMAP.md) |
| Check prerequisites and result meaning | [Compatibility](Docs/AddonRelay/COMPATIBILITY.md) |
| Understand data handling | [Privacy and security boundaries](Docs/AddonRelay/PRIVACY.md) |
| Understand free local use and optional paid work | [Commercial direction](Docs/AddonRelay/COMMERCIAL.md) |
| Ask a common product question | [FAQ](Docs/AddonRelay/FAQ.md) |

## Repository scope

The retained code covers contracts, policy, single-writer locking, bounded commands, receipts, schemas, and sanitized export. The [historical backend architecture](Docs/ARCHITECTURE.md) explains that subset. Historical incident and support documents remain historical evidence; they are not current AddonRelay compatibility or release claims.

This repository does not include the complete AddonRelay application, private operational knowledge, customer data, game packages, or a complete native Workbench adapter. Public documentation changes do not publish a game update or activate a hosted service.

Public checks remain static and run without production credentials. [Contributing](CONTRIBUTING.md) explains the validation and exact export inventory. Every public addition needs a reviewed source classification and manifest coverage.

## Support, pricing, and rights

Use this repository's **Issues** for ordinary questions, reproducible product problems, and focused suggestions. Follow the templates and share only a reviewed minimal example. See [SECURITY.md](SECURITY.md) for sensitive findings.

The product direction is **free local tools, with optional prepaid hosted investigations when available**. Hosted accounts and billing are not opened by this documentation preview. No active paid offer is being announced here.

No open-source license has been selected for the retained source. Public visibility is not a general reuse grant. [NOTICE.md](NOTICE.md) remains unchanged. AddonRelay is an independent project and is not presented as an official Bohemia Interactive product.
