# Connect an AI agent

This guide covers the **existing read-only local companion**. It assumes you already obtained a complete, verified companion ZIP. This repository preview does not yet supply the complete framework or a public native execution installer.

## Connection model

Your coding client starts `companion.mjs` as a local process and communicates over stdio MCP. The companion receives the selected project directory as its second process argument, after the script path. Use absolute paths for the executable, script, and project.

The selected directory is a working boundary, not permission for arbitrary system access. Use a separate trusted configuration for each project. A cloud chat window cannot launch a process on your Windows computer merely because it uses a model that also appears in a local coding client.

## Prerequisites

1. Install the runtime required by the package: Node.js 24 or newer for the inspected local package.
2. Extract the entire companion ZIP into a location you control. The archive contains an `addonrelay` directory; use the actual path after extraction or relocation.
3. Identify the actual `companion.mjs` file and the project directory.
4. Use a client that supports a local stdio MCP server.

The AI client starts the companion directly. No AddonRelay browser workspace or graphical launcher is required for this connection.

You can identify the installed Node executable with:

```powershell
node -p process.execPath
```

## Configure the client

The following illustrates the actual command and argument shape. These paths are examples; replace them with your installation. Client configuration locations and surrounding formats differ, so use the instructions for your client version.

```json
{
  "mcpServers": {
    "addonrelay": {
      "command": "C:/Program Files/nodejs/node.exe",
      "args": [
        "C:/Tools/AddonRelay/companion.mjs",
        "D:/Mods/YourAddon"
      ]
    }
  }
}
```

For a client that uses TOML server definitions, the equivalent process configuration is:

```toml
[mcp_servers.addonrelay]
command = 'C:\Program Files\nodejs\node.exe'
args = ['C:\Tools\AddonRelay\companion.mjs', 'D:\Mods\YourAddon']
```

The local diagnostic path needs no AddonRelay key, account, or credits. Do not inherit legacy `ADDONRELAY_KEY` or `ADDONRELAY_URL` settings into a setup you intend to keep local. Existing legacy hosted integrations are a separate mode; new hosted customer access is closed.

Keep machine-specific connection settings in the client's trusted local configuration, rather than committing credentials or private paths to a shared project. The optional `ADDONRELAY_TOOLS` environment value restricts discovery to a comma-separated subset of the implemented tools.

## Verify the connection

Use your client's tool-discovery or connection-status facilities to confirm that the expected server is running and the expected tools are listed. A successful connection proves that the client can communicate with the companion. It does not prove native Workbench execution or full project compatibility.

The current tool set is:

| Tool | Use it for | It does not establish |
|---|---|---|
| `find_symbol` | Locate symbol declarations or references in the selected project | A successful compile or correct runtime behavior |
| `resolve_resource` | Locate project resource references or files | Effective inheritance, dependency completeness, or native loading |
| `guidance` | Request a workflow recipe such as `starter` | Permission to execute the guidance |
| `diagnose_log` | Classify supported signals from a supplied local log | Cause of every warning or a verified repair |
| `check_server_config` | Check a selected configuration and addon list | A healthy running server or authenticated join |
| `compare_addons` | Compare supplied client/server addon manifests | Identity of every downloaded byte |

Use the server's discovered input schemas. Do not guess argument names from these descriptions or pass full project contents into a field intended for a reference or selected local path.

### Current input examples

These are examples of implemented tool arguments, not native framework commands:

| Tool | Example arguments |
|---|---|
| `find_symbol` | `{"symbol":"MyComponent"}` |
| `resolve_resource` | `{"query":"addon.gproj"}` |
| `guidance` | `{"recipe":"starter"}` |
| `diagnose_log` | `{"path":"Logs/workbench.log","source":"workbench"}` |
| `check_server_config` | `{"path":"Server.json"}` |
| `compare_addons` | `{"client":[],"server":[]}` |

Replace symbol names, filenames, and empty addon lists with the actual inputs you intend to inspect. Empty lists are a syntax example, not a meaningful dependency test. Guidance recipes are `starter`, `script`, `prefab`, `dependencies`, and `release`; the `release` recipe returns guidance, not publication authority.

Log and configuration paths must be relative to the selected project, using forward slashes. Absolute paths, parent traversal, and targets outside that project are rejected. The current readers bound individual files at 1 MiB. Lookup traversal and result counts are also bounded, so inspect any truncation or coverage information.

Each addon-list entry uses `id` and `version`: a 16-character hexadecimal addon identifier and a numeric version with two to four components. Use actual declared identities from the intended input lists. An accepted list does not prove the installed package bytes match it.

Current companion responses serialize their report as JSON in an MCP text content block. Consumers should parse that returned report where appropriate and must not assume the implementation supplies an MCP `structuredContent` object. Exact result and protocol behavior belongs in each supported release's compatibility record.

## A useful first prompt

> Use AddonRelay's read-only tools for the selected project. Call `guidance` with the `starter` recipe, then look up a symbol or resource I identify. Summarize the observation, the inspected scope, and the next Workbench check that would validate it. Keep hypotheses separate from verified results.

If you do not know a useful symbol yet, start with guidance. A fabricated resource identifier makes a poor connection test. An empty lookup can be a correct result for the selected scope.

## How the agent should use a finding

An agent should first identify what the tool actually inspected. It can then form a testable explanation, propose the smallest relevant change, and ask the existing development workflow for the appropriate validation. It should preserve failed observations and distinguish:

- What was found in selected files.
- What a prior record says happened.
- What it thinks may explain the problem.
- What still requires an engine, runtime, or multiplayer observation.

Static local report records explicitly use `engine-not-tested`. Treat that as part of the result, not text to remove from the summary. A local report is also separate from the planned durable native operation receipt.

## Connection troubleshooting

| Symptom | First useful check |
|---|---|
| Server process does not start | Confirm Node is installed at the configured absolute path and meets the package requirement |
| Script cannot be found | Confirm the complete ZIP was extracted and the configured file is `companion.mjs` |
| Project cannot be selected | Check the directory exists, permissions allow access, and the path is the intended project |
| Expected tool is missing | Inspect `ADDONRELAY_TOOLS` and the installed companion version |
| Lookup finds nothing | Check spelling, selected scope, dependencies, and whether the file type is supported |
| Unexpected hosted behavior | Inspect inherited legacy hosted environment settings; a local-only setup should not provide them |
| Client accepts a different config shape | Follow that client's current MCP configuration documentation; preserve the same executable and arguments |

Do not solve a connection problem by disabling certificate checks, broadening filesystem access, or adding secrets to a public repository.

## Planned native integration

Supported native checks, interruption recovery, and persistent project knowledge will be documented with the qualified distribution. No compile, packaging, publication, deployment, or Brain tool is added by this guide. The initial launch requires no AddonRelay graphical interface.

See [capability status](CAPABILITIES.md), [compatibility](COMPATIBILITY.md), and [privacy](PRIVACY.md) for the current boundary and AI-provider data path.

## Protocol reference

The [official MCP stdio specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) explains the subprocess transport. That reference describes the protocol; it does not claim this companion already implements every feature of that specification version. Use the installed release's actual client/protocol compatibility record.
