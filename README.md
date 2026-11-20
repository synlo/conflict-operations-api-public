# AddonRelay

**Connect your AI agent to your Arma Reforger development project.**

AddonRelay is being developed as a lightweight local connection for AI-assisted inspection, supported Workbench checks, and project knowledge. **The planned product combines agent-first tools with a browser dashboard for project activity, usage and credits. No separate desktop GUI is required.** Experienced developers can use the same supported integration, with a small command-line setup and diagnostics path planned alongside it.

This is the public documentation and integration home. Implementation source, the detailed development plan, and private project knowledge are maintained separately.

## Start here

- [Getting started](Docs/AddonRelay/START_HERE.md): prerequisites and first connection.
- [Agent integration](Docs/AddonRelay/AGENT_GUIDE.md): the existing companion's invocation and six read-only tools.
- [Capability status](Docs/AddonRelay/CAPABILITIES.md): what exists and what is planned.
- [Roadmap](Docs/AddonRelay/ROADMAP.md): the outcomes required for launch.
- [Documentation index](Docs/AddonRelay/README.md): compatibility, privacy, expert use, and support.

## Current availability

The existing companion implementation supports local symbol/resource lookup, workflow guidance, log inspection, configuration checks, and addon-list comparison over stdio MCP. It can connect directly to an AI client without opening a product window. Local diagnostic use requires no AddonRelay account or API key.

Native Workbench execution, interruption recovery, persistent project Brain integration and the responsive project dashboard are planned capabilities of the complete framework product. This repository does not supply that installer or claim those workflows are already qualified for public use. Installation and client support must follow the record for the exact artifact you obtain.

The initial native target is Arma Reforger Workbench on Windows. Other Enfusion products need their own compatibility evidence. Bring your own supported AI client and any model access it requires.

## Planned browser dashboard

Sign in from a computer or phone to see explicitly linked projects, agent activity, result scope, last synchronization, connections and AddonRelay credit information. Humans use account sign-in; agents use credentials limited to approved projects and actions. Local tools remain usable without a dashboard account.

Activity shown in the dashboard covers work reported through supported integrations. It does not imply access to every agent conversation or to an AI provider’s subscription balance. Local activity and paid hosted usage remain distinct. See the [FAQ](Docs/AddonRelay/FAQ.md) and [privacy](Docs/AddonRelay/PRIVACY.md). This is the product direction, not an announcement that the new dashboard or public accounts are live.

## Support and rights

Use [Issues](https://github.com/synlo/conflict-operations-api-public/issues) for public documentation and product questions. Share only reviewed, non-sensitive reproductions. Use the [security policy](SECURITY.md) for security findings.

Local use remains the intended free offering; optional hosted services are a separate future track. See [commercial direction](Docs/AddonRelay/COMMERCIAL.md). Public visibility does not grant an open-source license; the existing [rights notice](NOTICE.md) applies.
