# Compatibility

A supported configuration must identify the actual artifact, runtime, client, and any native tools used. A technology name alone is not a compatibility test.

## Existing companion requirements

| Item | Documented boundary |
|---|---|
| Artifact | Complete verified companion package obtained through its supported delivery path. |
| Runtime | Node.js 24 or newer for the inspected package. |
| Agent transport | Local stdio MCP. |
| Invocation | Absolute runtime and script paths plus the selected project directory. |
| Tools | Six read-only diagnostics/guidance tools. |
| Results | JSON report in an MCP text content block; inspect scope and limitations. |
| Local account requirement | No AddonRelay account or key for local diagnostics. |
| Initial native target | Windows Arma Reforger Workbench; public native integration is planned. |
| Other Enfusion products | No general compatibility claim. |

The examples describe a process configuration, not a fresh qualification of every current client version. Use the installed artifact's supported-client record. If that record is absent, treat the combination as unqualified.

## Required release information

A public artifact should state its version and checksum, runtime and operating-system requirements, supported client versions, available tools, relevant engine versions, and known limitations. Setup, upgrade, removal, and data-retention instructions should match those exact bytes.

## Planned browser dashboard

The target is a responsive browser interface for phones and computers, without a desktop GUI install. Actual browser versions, mobile behavior, sign-in, reconnect and access controls need acceptance before support is claimed. This plan does not certify every browser or provide native Workbench execution on a phone.

## Result scope

A successful MCP call demonstrates that communication and that tool invocation worked. A static check describes the inputs it inspected. A native compile, resource observation, multiplayer test, and performance comparison each answer separate questions. Reuse earlier evidence only when it remains applicable to the current operation and inputs.

Hardware-specific claims need corresponding hardware evidence. Headless AddonRelay setup does not remove native Workbench's own platform requirements or window behavior.
