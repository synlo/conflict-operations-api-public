# Start here

## The product in one paragraph

AddonRelay helps an AI agent or experienced developer work with an Arma Reforger addon. The existing local tools inspect selected project files and explain useful diagnostic signals. The planned framework adds controlled native Workbench checks and durable results. Brain adds project knowledge that connects a problem, a correction, and what happened when it was tested.

The aim is a short setup followed by useful work. It still matters which project, dependencies, engine, and client are selected. The framework should discover and explain those prerequisites instead of asking a new user to reconstruct the maintainer's machine.

## What this repository gives you now

You can read the public product design, integration guidance, release milestones, and historical backend source. The full AddonRelay application and Brain are not installed by cloning this repository. There is no public native-framework installation command to run from these files yet.

If you already have an authentic local companion ZIP, the [agent guide](AGENT_GUIDE.md) and [developer guide](DEVELOPERS.md) describe its existing diagnostic path. Before a general download launch, the public distribution milestone must provide a stable download, matching checksum, component versions, and supported-environment record. This preview does not substitute an unverified package address.

## Choose your path

### Connect an AI agent

Use a coding client that can launch a local stdio MCP server. Configure the companion with one selected project directory and use its read-only tools to inspect the project. Start with `guidance` and a symbol or resource lookup. Read the result's scope before asking the agent to propose a correction.

The AI client supplies the language model and conversation. AddonRelay supplies project tools and, as the native roadmap is completed, controlled operations and persistent project knowledge. Changing the AI provider should not require rebuilding the project's engineering history.

### Use the developer tools

Open the local client, select the files or inputs you want checked, and run the relevant diagnostic category. You can continue editing and testing through your normal Workbench workflow. You do not need to prompt an AI to use a deterministic inspection.

The planned native CLI and local interface will use the same operation contracts as the agent connection. That shared native path is a roadmap item, not an existing public command reference.

### Evaluate the framework

Read the [architecture](ARCHITECTURE.md), [Brain design](BRAIN.md), and [roadmap](ROADMAP.md). The first useful public framework demonstration must work on an unrelated addon, not only on the project's own development environment.

## Requirements for the existing local package

- A complete, verified Windows companion ZIP.
- Node.js 24 or newer, as required by the inspected package.
- A selected local project directory you are authorized to inspect.
- For the agent path, a client with local stdio MCP support and a trusted per-user configuration.

Dependencies are bundled in the companion ZIP. The documented package flow does not require an npm install or a custom executable. Extract the complete archive rather than copying one entry point away from its supporting files.

Workbench is needed when you carry out native validation. A static diagnostic finding can be useful before Workbench is opened, but it cannot replace an engine observation.

## Your first useful check

1. Choose a small project you are authorized to inspect.
2. Open the local interface, or connect the companion to your agent.
3. Run a symbol/resource lookup or starter guidance.
4. Check the selected project and the scope of the inspected files.
5. Read the observation and recommended next check.
6. If you make a change, verify it through your normal Workbench process.
7. Keep or export a reviewed report if useful.

A successful lookup means a match was found in the inspected scope. A successful configuration check means those configuration checks passed. Neither means that the complete addon is fixed or that a server is ready for players.

## What the native launch will add

The planned first native journey is:

1. Select an addon and discover installed tools.
2. Grant a bounded local-development scope for supported operations.
3. Prepare one supported check and inspect any prerequisite failures.
4. Run it through the framework and receive a scoped receipt.
5. Reconnect after an interruption and recover the existing operation.
6. Retrieve the result and any relevant prior project lesson.

Recurring approved local checks should not require a fresh prompt every time. Publishing, production deployment, sharing private knowledge, and paid work have separate scopes. This design keeps routine development moving while making the actual action reviewable.

## Where to go next

Use [Capabilities](CAPABILITIES.md) to distinguish the current implementation from future behavior. Use [Compatibility](COMPATIBILITY.md) before relying on a client or engine combination. Use [Privacy](PRIVACY.md) to understand what stays local and what an AI client or optional service may receive.

Ordinary feedback belongs in repository Issues. Include the component, expected behavior, actual result, and a small reviewed example. Do not post credentials, full operational logs, player data, or private project archives.
