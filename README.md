# AddonRelay for Arma Reforger

Conflict Operations built AddonRelay to troubleshoot Arma Reforger mods. When a server starts with a valid configuration but fails to load its mission, the free browser workspace can read the startup log and point you to the first recognized failure and its line number. You can also look up a prefab or compare the addon versions a client and server expect.

**[Try the failed server boot sample](https://addonrelay.freeddns.org/workspace?sample=northbank-boot)**. Run the Northbank example to see where the mission header fails. The sample works without an account, a download or your own server logs.

[Open AddonRelay](https://addonrelay.freeddns.org/) · [Read the live handbook](https://addonrelay.freeddns.org/docs) · [Connect your coding agent](https://addonrelay.freeddns.org/docs/handbook/agent-start)

## Use it on your project

- **Server admins** can inspect a selected log, check a server configuration, or compare two addon lists in the browser. A configuration can pass its checks even when the game fails to start.
- **Mod developers** can trace resource references and symbols in selected files. Open the active project in Workbench to resolve the resource, compile the scripts, or confirm the repair in a fresh run.
- **AI users** can connect a compatible coding assistant to the local companion over stdio MCP. It can inspect the project directory you select. Local diagnostics require no AddonRelay account, API key or credits. Your chosen AI provider sets its own terms.

## Public documentation and roadmap

The live handbook above describes the current distribution. This repository preserves the public integration contract and the roadmap for the broader framework. The [agent guide](Docs/AddonRelay/AGENT_GUIDE.md) documents the original six read-only checks. The [documentation index](Docs/AddonRelay/README.md) covers compatibility, privacy and expert use.

The [framework roadmap](Docs/AddonRelay/ROADMAP.md) sets out native Workbench execution and recovery on Windows, persistent project knowledge, and a linked dashboard for project activity, connections and usage. It also records plans for GitHub and Google sign-in, scoped agent credentials and optional hosted work. Qualification is specific to each feature and artifact. See the [capability record](Docs/AddonRelay/CAPABILITIES.md) and [commercial direction](Docs/AddonRelay/COMMERCIAL.md).

## Optional Discord release announcements

Maintainers can send a public GitHub release to a text channel in the Conflict Operations Discord. The announcement includes the release title, tag, link and a link to the sample investigation in the browser. It uses a standard GitHub-hosted runner, which is free for public repositories.

1. In Discord, open **Server Settings → Integrations → Webhooks**. Create a webhook for the announcements text channel and copy its URL.
2. In this GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `DISCORD_RELEASE_WEBHOOK` and paste the URL there. Keep the URL out of issues, releases and source files.
3. With GitHub Actions enabled, publish a stable release under **Releases → Draft a new release**. The workflow posts when the release is published. Drafts, prereleases and routine commits produce no announcement. Removing the secret turns delivery off.

If a delivery fails, check the channel before rerunning the job to avoid a duplicate. [Discord webhook setup](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) · [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)

## Support and rights

Use [Issues](https://github.com/synlo/conflict-operations-api-public/issues) for documentation and product questions. Share a small, non-sensitive reproduction. For security findings, use the [security policy](SECURITY.md). Public visibility does not grant an open-source license. See the [rights notice](NOTICE.md).
