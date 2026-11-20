# Capabilities and availability

**Current public stage: documentation and roadmap preview.** This repository contains a historical COAPI backend subset. It does not contain a complete AddonRelay application distribution or a public native framework installer.

The local companion and browser workspace have existing implementations. Describing those implementations here is different from claiming that every current client, operating system, or engine build has completed release qualification. A future downloadable release must name the exact combinations that were tested.

## Current local implementation

| Capability | What it does | Evidence scope |
|---|---|---|
| Selected-project symbol lookup | Finds matching declarations or references within the configured project boundary | Static local inspection; no compilation |
| Resource lookup | Finds selected-project resource files or references | A match is not proof of effective inherited resource loading |
| Log diagnosis | Classifies recognized startup and resource signals and suggests checks | Analysis of supplied evidence; no engine execution |
| Configuration check | Checks selected configuration structure and addon-list consistency | Does not authenticate a player or establish server health |
| Addon comparison | Compares two supplied addon lists | Does not download or validate the content of every package |
| Workflow guidance | Returns guidance for supported diagnostic categories | Advice; no permission to execute an operation |
| Local browser workspace | Exposes diagnostic categories to a human developer | Does not require an AI agent |
| Optional local history and reviewed reports | Retains and exchanges scoped diagnostic records | Report history; not the full proposed Brain |
| Synthetic examples | Demonstrates findings without using a customer's project | Sample evidence; not a playable native acceptance fixture |
| Local stdio MCP companion | Exposes six read-only tools to compatible clients | Client must be able to start the local companion process |

The current MCP tool names are `find_symbol`, `resolve_resource`, `guidance`, `diagnose_log`, `check_server_config`, and `compare_addons`. See the [agent guide](AGENT_GUIDE.md) for setup and result interpretation.

## Planned public framework

| Capability | Target outcome | What must be demonstrated |
|---|---|---|
| Generic project binding | Select an unrelated addon without private repository assumptions | Correct project and dependency identity on a clean supported setup |
| Native Workbench recipes | Run a small supported set of compile and inspection operations | Exact engine/tool combination, bounded launch, native observations, meaningful failures |
| Shared agent and developer operations | Use one execution path from MCP and the developer interface/CLI | Equivalent permissions, identities, results, and recovery |
| Durable native recovery | Reconnect and determine what happened before relaunching | Interrupted, finished, rejected, failed, and uncertain outcomes handled accurately |
| Project Brain | Retrieve relevant problems, attempted corrections, and verified outcomes | Input applicability, event deduplication, persistence, and project isolation |
| Team knowledge | Deliberately share selected knowledge with collaborators | Access controls and revocation without cross-project leakage |
| Reviewed reference packs | Reuse versioned techniques and examples | Provenance, redistribution rights, and explicit applicability |
| Extension recipes | Add reviewed workflows without giving arbitrary tool authority | Declared permissions, bounded outputs, cancellation, recovery, and acceptance |
| Packaging and private runtime checks | Extend native workflows after the basic path is qualified | Recipe-specific evidence and supported installations |

Workshop publication and production deployment are advanced future scopes. They are not included in the first public local-development promise.

## Hosted availability

| Item | Status |
|---|---|
| Free local diagnostic direction | Established product direction |
| New public hosted accounts | Closed |
| Paid hosted investigations | Planned |
| Customer billing and checkout | Closed |
| Shared hosted Brain access | Planned; not enabled by connecting the local companion |
| Mandatory AI subscription | Not part of AddonRelay's local developer path |

The existence of a prepared payment or job-processing module does not establish service availability. Commercial launch has its own proof for isolation, accounting, recovery, capacity, privacy, and support.

## How a capability becomes available

Each supported release should publish:

1. The downloadable artifact and its expected checksum.
2. Product and component versions, including companion and recipe identities.
3. Supported operating system, runtime, client, and engine combinations.
4. A reproducible first-use workflow that needs no private project access.
5. The behavior actually tested, its known limitations, and the relevant result type.
6. Upgrade and recovery instructions that preserve existing project work.

Source inspection, a sample response, a successful MCP connection, and a native runtime test answer different questions. Product claims should name the evidence that supports them.

See [Compatibility](COMPATIBILITY.md) for the result vocabulary and [Roadmap](ROADMAP.md) for launch milestones.
