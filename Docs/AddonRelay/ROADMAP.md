# Framework and Brain roadmap

This roadmap describes the proposed public framework launch. It is organized by completed user journeys and their evidence, not promised dates or a percentage derived from task counts.

The existing local companion implements six read-only diagnostic tools. The roadmap adds a general connection to supported Windows Workbench operations and persistent project memory. Source inspection or a passing static test does not establish that a proposed native capability works for external developers. See [Capabilities](CAPABILITIES.md) for the current boundary.

## The first complete milestone

**An unrelated addon completes a real compile through the shared agent/developer interface, recovers correctly after an interruption, and retrieves the resulting project lesson.**

This is a deliberately small complete workflow. It proves that the framework can operate outside its original project and that its useful state survives the conversation. It does not require a new website, payment activation, production server deployment or a hosted model.

## Phase 1: define the distributable boundary

### Deliverables

- A selected, reviewed subset of the execution and memory components.
- A deliberate rights and dependency inventory for every distributed file.
- One component manifest covering product, framework, recipes, runtime dependencies and memory schema.
- A narrow initial support scope: Arma Reforger Workbench on Windows, with named client and engine configurations.
- A generic workspace binding for the selected project, installed tools, providers, local state and allowed outputs.

Preserve the existing read-only tools. External developers must not need the original project's campaign, credentials, provider collection or historical release records. Existing project-specific workflows should retain their compatibility settings.

### Completion evidence

Two disposable unrelated projects can be selected without editing framework source. Their state remains separate. Paths with spaces and invalid or escaping paths are handled correctly. The distribution inventory states what may be shipped and what stays outside it. A public reuse license is not implied by making source readable; the existing [notice](../../NOTICE.md) remains in effect until deliberately changed.

Internal adapter work can proceed while a final distribution decision is pending. Public distribution depends on that decision.

## Phase 2: connect one native operation

### Deliverables

- A shared operation facade over the existing preflight, controller and journal.
- Preparation, start, status, reconciliation and cancellation behavior.
- One real compile recipe for an owned disposable sample.
- Companion and human-accessible entry points using the same operation definition.
- A versioned native result envelope that preserves existing `engine-not-tested` diagnostic reports.

The sample must be an actual qualified Workbench project. A synthetic log or configuration example alone cannot establish native execution. Each operation declares its source, tools, outputs, deadline, permission scope, observations and recovery behavior.

### Completion evidence

A supported agent calls the operation, and a developer can invoke its equivalent without an AI subscription. The sample produces a successful compile, an actual compile failure and a rejection before launch for a missing prerequisite. Results distinguish execution from observation validity and behavior established.

A controlled interruption followed by reconnect recovers the same operation without duplicate execution. Cancellation affects only owned work and reports the observed outcome. Two projects competing for a native resource respect the workstation lease. Normal manual Workbench work and unsaved edits are preserved.

## Phase 3: retain the first useful project lesson

### Deliverables

- Project-scoped repair memory connected to durable operation results.
- Exact and related lookup with applicability and evidence references.
- Preservation of failures, attempted corrections and successful scoped observations.
- A small original or redistribution-cleared reference collection, clearly separate from private project evidence.

Standalone memory components need source and distribution review before inclusion. The public interface must not expose an internal production knowledge service or copy its private collection.

### Completion evidence

The sample failure and correction remain available after reconnect. Replayed imports produce no duplicate counts or false freshness. A changed engine or input is displayed as a difference, not silently treated as a match. Another project may consult a deliberately shared example but cannot reuse the sample's compile as its own proof.

If memory indexing is unavailable, the original sealed result remains intact and the import can recover. See [Brain](BRAIN.md) for the intended data and evidence boundaries.

## Phase 4: package and document the local product

### Deliverables

- A downloadable artifact with an exact component manifest, dependency notices and integrity checks.
- Prerequisite detection and a supported runtime setup that does not silently replace global installations.
- Project selection and client configuration that preserve unrelated settings.
- Current agent and developer quickstarts, a recovery walkthrough and useful troubleshooting.
- Focused native recipes for the configurations actually advertised.
- Update, schema migration, export and uninstall behavior.

The initial recipe set can expand from the proven compile to accepted PC/HEADLESS configurations, resource inspection and private sample startup. Packaging is a separate recipe. Publication and production deployment remain advanced future scope rather than prerequisites for a useful local development product.

### Completion evidence

A clean Windows user installs without private repository access or hidden maintainer setup. The downloaded bytes match the accepted artifact. Prerequisites are reported before native launch. Project memory survives updates, and an interrupted migration produces a recoverable state.

Uninstall does not silently remove project data. Basic local tools and memory continue when the website or an optional shared service is unavailable. Every advertised recipe has a meaningful successful observation, failure/refusal behavior and recovery evidence at its own scope.

The [agent guide](AGENT_GUIDE.md), [developer guide](DEVELOPERS.md) and [compatibility record](COMPATIBILITY.md) must describe the same supported behavior.

## Phase 5: qualify the external developer experience

### Deliverables

- A pilot covering agent users and experienced manual Workbench developers.
- Actual client-version acceptance for discovery, results, errors, long operations, cancellation and reconnect.
- Evidence from unrelated addons and a clean Windows environment.
- A short authentic demonstration of inspection, native checking, interruption and memory lookup.
- A support template that requests bounded, reviewed evidence.

### Completion evidence

At least one independent environment completes the full documented workflow without undeclared maintainer intervention. Each advertised client combination has a real session result. A configuration snippet or standalone protocol test is not sufficient to claim client acceptance.

Wrong-project actions, lost evidence, duplicate native launches and unsupported success claims must be corrected before the affected capability is promoted. Other supported limitations remain visible with a concrete next test. Pilot feedback should improve the same interfaces and documentation rather than create a second control system.

## Phase 6: launch the free local framework

### Deliverables

- Frozen accepted component and reference-pack identities.
- A public download, usable documentation, compatibility matrix and declared rights.
- Website copy that accurately distinguishes available tools from future work.
- Release notes, known limits and bounded support procedures.

### Completion evidence

An external developer can reach the product documentation, obtain the intended artifact and complete the supported quickstart. Artifact contents and identities match those accepted during qualification. Installation requires no private operational material.

The headline and feature list describe observed behavior. Local use remains free and does not depend on a customer account, payment or a particular model provider. Publishing new documentation alone does not close implementation work or qualify a native capability.

## Separate track: optional hosted investigations

Hosted work can add reviewed analysis of explicitly submitted material through optional prepaid jobs. It is a separate release from the free local framework. Accounts, job processing and checkout must remain accurately labelled until their actual acceptance is complete. See [Commercial direction](COMMERCIAL.md).

Required work includes isolated customer data, bounded submissions, quoted work, idempotent job creation, cancellation and recovery, measured capacity and a qualified analysis implementation. Payment-provider capture, replay, reversal and unresolved-response handling need real provider evidence where applicable.

Hosted findings remain diagnostic observations, historical evidence or hypotheses. They do not become native Workbench proof because a remote service produced them. Remote control of a customer's Workbench is outside this initial hosted-analysis track.

Customer investigations do not automatically become shared lessons or training material. Hosted retention, support submission and public contribution are distinct choices described in [Privacy](PRIVACY.md).

## How progress will be reported

For each milestone, report the component version, scope, observation, outcome and remaining acceptance. Preserve failed attempts and distinguish a corrected implementation from its verified result. Reuse completed evidence only while the relevant inputs still match.

An unsupported combination can stay outside the advertised surface without blocking unrelated supported capabilities. A reproduced problem in an advertised capability remains attached to that capability until corrected or accurately removed from its promised scope.

The next implementation target is the complete milestone at the top of this page: **bind one unrelated addon, compile through the shared interface, recover the operation and retrieve its lesson**. The [architecture](ARCHITECTURE.md) supplies the design boundaries; the milestone supplies the proof that the connection works.
