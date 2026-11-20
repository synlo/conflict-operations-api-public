# Capability status

This page distinguishes the existing companion implementation from the planned public framework distribution. Documentation publication does not itself qualify a downloadable release.

| Capability | Status |
|---|---|
| Local stdio MCP connection | Implemented in the existing companion; configure against your supplied artifact. |
| Symbol and resource lookup | Implemented read-only tools within the selected project. |
| Workflow guidance, log/configuration checks, addon-list comparison | Implemented read-only tools with bounded inspection scope. |
| Local use without an AddonRelay key | Existing diagnostic path; omit legacy hosted settings. |
| Complete standalone native framework installer | Planned; not supplied by this repository. |
| Supported Workbench execution and interruption recovery | Planned public integration, requiring its own qualification. |
| Persistent project Brain | Planned public integration. |
| Supporting setup/diagnostics CLI | Planned; no general CLI commands are announced here. |
| AddonRelay graphical application | Deferred from the initial launch. |
| New public hosted accounts and billing | Closed; optional hosted value is a separate future track. |

## What a result means

The six existing tools are `find_symbol`, `resolve_resource`, `guidance`, `diagnose_log`, `check_server_config`, and `compare_addons`. Their actual arguments and connection instructions are in the [agent guide](AGENT_GUIDE.md).

A static finding does not establish a successful native compile, runtime behavior, multiplayer compatibility, or a repaired defect. Current local report records use `engine-not-tested`. Read coverage and limitations with the result.

No complete controller source, Brain implementation, private corpus, game addon, provider bundle, or production access is distributed by this documentation repository.
