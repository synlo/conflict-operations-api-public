# Experienced developer integration

The first AddonRelay launch is agent-first. Developers who prefer terminal tools can use the same published integration and the planned setup/diagnostics CLI. A separate desktop GUI is outside the initial launch; the responsive browser project dashboard is planned for shared visibility.

## Use the supported interface

The existing companion exposes the read-only MCP tools in the [agent guide](AGENT_GUIDE.md). Use tool discovery and the documented input/output contract for your installed release. The process receives a selected project directory; path-based tools use project-relative paths.

Current reports are JSON inside an MCP text content block. Respect coverage, limitations, errors, and `engine-not-tested`. Do not assume native execution, full dependency resolution, or a verified repair from a static inspection.

There is no released general command-line operation suite or public implementation SDK announced by these documents. Native operation and project-memory interfaces will be documented with the artifact that qualifies them. Avoid depending on internal files, undocumented endpoints, or inferred command names.

The planned browser connection lets an authorized agent or backend report scoped activity for a selected project. It will not grant account administration or native publication merely through possession of an activity key. Exact external contracts will be published with the qualified capability.

## Integration expectations

- Bind a connection to the intended project and keep machine-specific settings local.
- Request only the available tools and permissions needed for the task.
- Preserve the distinction between a finding, a proposed explanation, and a verified outcome.
- Report useful errors without copying private input into public issues.
- Follow supported version and upgrade instructions when they are published.

Arma Reforger Workbench on Windows is the first planned native target. An experienced developer still needs the relevant engine, project, and third-party permissions. The public [rights notice](../../NOTICE.md) does not license private implementation source or redistribute game/provider assets.
