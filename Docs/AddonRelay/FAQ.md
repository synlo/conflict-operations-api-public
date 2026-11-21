# Frequently asked questions

## Do I need a desktop application?

No separate AddonRelay desktop GUI is required. Your supported agent starts the headless local companion. A responsive browser dashboard is planned for project visibility, activity, usage, credits and connections. Local tools remain usable without signing in to it.

The website is the AddonRelay visual interface. The companion is the small local connection needed to access the selected project and authorized Workbench installation; a website login cannot replace that connection.

## Can I check my project from a phone?

That is the intended dashboard experience. Sign in from a phone to see work reported by a linked project and its last-update time. Workbench still runs on an authorized development host; the phone is the viewing interface. The new project dashboard remains planned, not announced as live.

## Is an API key my dashboard login?

No. People use account sign-in. Agents or backends will use credentials limited to their permitted projects and actions. An activity key should not grant access to account administration, purchases or other projects.

## Can I sign in with Google or GitHub?

GitHub is the initial planned public account path. Google is planned as an additional sign-in option for the same AddonRelay account. These docs do not announce open registration or a completed Google integration. Adding a second sign-in method should require deliberate authenticated linking, rather than combining accounts solely because their email addresses match.

## Will I need a subscription?

Local tools and basic linked-project monitoring are intended to remain free. Optional paid hosted work is planned around prepaid usage first. A monthly plan with included usage may follow if it offers useful recurring value, while prepaid access remains an option. No subscription, price, included allowance or timed trial is launched by these docs. See [commercial direction](COMMERCIAL.md).

## What usage and credits will it show?

Reported project activity and AddonRelay credits, with free local work separated from billable hosted jobs. Reserved amounts and final charges should be distinct. It will not claim to show your Codex, Claude or other provider balance without an actual supported provider connection.

## What if the development computer or connection goes offline?

The planned view will show the last received update and a stale/disconnected indication. Missing updates do not prove that a run failed or succeeded. Later synchronization should recover retained results without repeating native work.

## Can an API key replace the local companion?

A key authenticates access to a service. It cannot by itself inspect a local project or operate Workbench. A local connection is still needed for those tasks. Existing local diagnostics do not need an AddonRelay key.

## Will it be an executable?

The inspected companion runs through Node.js. Final packaging should make setup straightforward, but no native executable or new installer is announced here. Packaging does not guarantee that distributed behavior cannot be inspected.

## Does it work with every AI agent?

Use a client that supports the documented local MCP invocation and is qualified for the artifact. The examples show configuration shapes; they do not certify every client version. See [compatibility](COMPATIBILITY.md).

## Can an experienced developer use it?

Yes, the same published contract is intended for expert integrations. A supporting setup and diagnostics CLI is planned. The planned browser dashboard can provide project visibility, and there is no desktop GUI requirement or current public implementation SDK announced by these documents.

## Is Brain another AI model?

Brain is the planned persistent project-knowledge capability. It helps retain useful findings and results; it is not a new model service or automatic proof that a suggested repair works.

## Can I run native checks today using these docs alone?

This repository documents the existing read-only companion and the native framework roadmap. It does not supply the complete native distribution. Use [capability status](CAPABILITIES.md) and the record for your actual artifact.

## Is the implementation open source?

The implementation and detailed development plan are maintained privately. Public documentation does not grant an open-source license. See the [rights notice](../../NOTICE.md).

## How do I report a problem?

Use [Issues](https://github.com/synlo/conflict-operations-api-public/issues), name the component and version, and provide a minimal reviewed reproduction. Follow the [security policy](../../SECURITY.md) for security findings.
