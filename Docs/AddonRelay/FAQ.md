# Frequently asked questions

## Do I need another graphical application?

No AddonRelay graphical interface is required for the initial launch. The agent starts a local companion directly. The website remains the documentation and download surface. A graphical client is deferred.

## Can an API key replace the local companion?

A key authenticates access to a service. It cannot by itself inspect a local project or operate Workbench. A local connection is still needed for those tasks. Existing local diagnostics do not need an AddonRelay key.

## Will it be an executable?

The inspected companion runs through Node.js. Final packaging should make setup straightforward, but no native executable or new installer is announced here. Packaging does not guarantee that distributed behavior cannot be inspected.

## Does it work with every AI agent?

Use a client that supports the documented local MCP invocation and is qualified for the artifact. The examples show configuration shapes; they do not certify every client version. See [compatibility](COMPATIBILITY.md).

## Can an experienced developer use it?

Yes, the same published contract is intended for expert integrations. A supporting setup and diagnostics CLI is planned. There is no separate GUI requirement or current public implementation SDK announced by these documents.

## Is Brain another AI model?

Brain is the planned persistent project-knowledge capability. It helps retain useful findings and results; it is not a new model service or automatic proof that a suggested repair works.

## Can I run native checks today using these docs alone?

This repository documents the existing read-only companion and the native framework roadmap. It does not supply the complete native distribution. Use [capability status](CAPABILITIES.md) and the record for your actual artifact.

## Is the implementation open source?

The implementation and detailed development plan are maintained privately. Public documentation does not grant an open-source license. See the [rights notice](../../NOTICE.md).

## How do I report a problem?

Use [Issues](https://github.com/synlo/conflict-operations-api-public/issues), name the component and version, and provide a minimal reviewed reproduction. Follow the [security policy](../../SECURITY.md) for security findings.
