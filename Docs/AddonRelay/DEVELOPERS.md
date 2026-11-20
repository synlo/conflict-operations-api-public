# Developer workflow and extension direction

AddonRelay is designed for both agent-assisted development and developers who prefer to work directly in Workbench. The human path should provide useful deterministic tools without requiring a conversation, model subscription, or hosted account.

## Existing local diagnostic path

With a complete, verified companion package and its required Node runtime, run `launch.cmd` to open the compact local interface. The launcher starts the local client. Expand the workspace for the existing report/history controls. Use the client's Quit control to stop its local listener when finished.

Choose the relevant diagnostic category and explicitly select its inputs. The local implementation covers resource and symbol lookup, supported log diagnosis, configuration checks, addon-list comparison, and workflow guidance. These are static inspections.

A practical manual workflow is:

1. Select a small relevant input set.
2. Run the check and read its coverage.
3. Review the finding in your editor or Workbench.
4. Make the smallest justified correction.
5. Compile, load, or exercise the affected behavior in the native environment.
6. Record the result at the scope it actually proves.

Optional local history is useful for comparisons. It is not yet the proposed project Brain with durable repair relationships and native evidence applicability. Reviewed exports let you share an appropriate record with another developer; inspect the export before sharing it.

## Reading an inspection result

Input selection affects the answer. A tool that checked selected text files has not necessarily loaded every provider, traversed every inherited prefab, or examined a packed Workshop package. Read coverage and skipped-input information alongside the finding.

For example, finding a resource reference proves that the inspected text contains that reference. To show that a vehicle uses the intended effective resource, inspect its inheritance and place or exercise it in the relevant native scenario. A configuration that passes a structural check still needs startup and, where relevant, authenticated multiplayer validation.

Keep an unsuccessful test. A later successful test can establish its own result, but does not retroactively identify the original failure's cause.

## Planned shared native operations

The native framework will provide a small set of named, supported recipes. The developer interface and a future CLI should expose the same preparation, permissions, execution, status, reconciliation, and receipts as the agent connection.

The first release should let you:

- Select a generic addon and discover the supported toolchain.
- See all independently detectable prerequisite problems before launching a costly native operation.
- Grant an appropriate local-development scope that persists across routine supported checks.
- Run one recipe with declared inputs, outputs, deadline, and result expectations.
- Cancel or reconnect without guessing whether another process should be launched.
- Reuse prior evidence when its relevant identities still match.
- Retrieve a project lesson without letting memory authorize an action.

The CLI needs readable summaries and a structured result mode. A refusal before launch, an execution failure, incomplete evidence, and a successful scoped observation must remain distinct outcomes. Exact public commands will be documented after their interfaces are implemented and accepted.

## Extension boundary

Experienced developers will need additional recipes. A public extension contract should describe what the extension does, what it can touch, and how its result can be assessed. Extensions should not gain general release or system authority simply by registering a tool.

Each proposed recipe should declare:

| Contract field | Purpose |
|---|---|
| Stable identity and version | Tie observations to the evaluator that produced them |
| Supported environment | State required engine, tool, OS, and project assumptions |
| Input binding | Identify project, relevant source, providers, configuration, and fixture |
| Operation class | Distinguish inspection, local native work, and any later external side effects |
| Permission scope | Name approved reads, writes, processes, and destinations |
| Readiness checks | Detect prerequisites and conflicts before launch |
| Bounds | Define duration, output size, attempts, and cancellation behavior |
| Observation parser | Explain what native evidence means and what remains unobserved |
| Recovery | Reconcile existing process identity and receipts after interruption |
| Acceptance fixture | Demonstrate useful success, failure, refusal, and recovery behavior |
| Provenance | Establish ownership or redistribution permission for included material |

This table is a design contract, not a currently installable plugin schema. A minimal owned example and compatibility tests must accompany the first supported extension release.

## Working with the public source subset

The retained backend code demonstrates policy, contracts, locking, receipts, schemas, and public-export controls. It does not contain the complete application or a ready-made Workbench bridge. Read [historical architecture](../ARCHITECTURE.md) before assuming a module is a customer API.

Public visibility does not grant a broad reuse license. Review [NOTICE.md](../../NOTICE.md) before copying or distributing source. Technical extension design and distribution rights are separate decisions.

For documentation or policy contributions, use the existing [contribution workflow](../../CONTRIBUTING.md). Keep examples synthetic or redistribution-cleared, preserve existing historical records, and do not add local server data or private operational access.

## The first external-developer acceptance

The strongest early test is an experienced developer on a clean supported environment, using an addon unrelated to the maintainer's project. They should be able to install the accepted package, choose that addon, run a supported native check, recover from an interruption, and find the resulting project knowledge without private assistance.

Setup steps that fail, unclear prerequisites, repeated launches, misleading success labels, and excessive maintainer intervention are useful pilot findings. The [roadmap](ROADMAP.md) uses those observations to decide what is ready for broader use.
