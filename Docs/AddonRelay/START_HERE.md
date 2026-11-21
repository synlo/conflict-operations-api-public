# Start here

**Connect your agent through the headless local companion. A browser project dashboard is planned for optional visibility on computers and phones; local connection does not require it.**

## Check availability

The existing companion provides six read-only diagnostic tools. The complete native framework, persistent project Brain and responsive project dashboard remain planned. This repository contains documentation, not a complete framework installer. Use a verified companion artifact and its matching installation record when one has been supplied to you.

## Connect the existing companion

1. Use a supported local client that can start a stdio MCP server.
2. Install the runtime required by your artifact. The inspected companion requires Node.js 24 or newer.
3. Extract the complete artifact and locate `companion.mjs`.
4. Select the project directory the companion may inspect.
5. Configure the client to start the companion directly, following the [agent guide](AGENT_GUIDE.md).
6. Confirm tool discovery, request the `starter` guidance, then inspect a known symbol or resource.

The local diagnostic path needs no AddonRelay account, API key, or credits. Any AI provider access belongs to your chosen client. An API key is not a replacement for the local program that reads the selected project or, in a qualified future release, operates Workbench.

A successful connection proves the tool link works. Read each result's scope before treating it as a project or engine acceptance result.

## Optional browser visibility, planned

The intended flow is to sign in, select an account-owned project, and explicitly link an agent or backend with a credential limited to the permitted project/actions. GitHub is the initial account direction, with Google planned as an additional option for the same account. Public signup and exact provider-linking instructions will be published only with the accepted feature.

Then open the dashboard on another device to see reported activity, scoped results, freshness, connections and authorized credit information. The website is the AddonRelay visual interface; the headless local companion continues to provide access to the development host.

A key is not the human account login, and project linking does not upload all source files or private memory. Activity connections receive no purchase or account-administration permission by default. Local activity and basic monitoring are intended to remain free within the published limits. Exact linking instructions will be published with the accepted feature; no new event endpoint or command is announced here.

## Where to go next

Read [capability status](CAPABILITIES.md) before planning native automation, [compatibility](COMPATIBILITY.md) for version requirements, and [privacy](PRIVACY.md) for what your AI client may transmit. Experienced developers can use the [same integration contract](DEVELOPERS.md).
