# Connection model

AddonRelay's planned product pairs **a browser dashboard with a local companion your AI client starts when needed**. The website will be the visual interface for projects, results, connections and usage alongside product information, documentation and qualified downloads. The companion runs without an AddonRelay window. No separate desktop GUI is required.

## What connects

Your supported client communicates with the companion through stdio MCP. The companion receives the selected project directory and exposes the tools available in its installed version. The existing tools perform local inspection and diagnostic guidance.

A supporting command-line path is planned for setup and troubleshooting. It will use the same supported operations as the agent connection. A separate client application for every AI vendor is unnecessary.

## What the planned browser dashboard shows

Sign in to see explicitly linked projects, reported agent activity, result scope, synchronization freshness, connections and authorized AddonRelay usage/credit information. A phone can display this while work continues on the development host. The panel covers activity supplied by supported integrations; it is not a view into every action an agent takes.

Humans sign in to their account, initially through the planned GitHub path, with Google planned as an additional option. Adding another sign-in provider must be an explicit account-linking action. Agents and backends use credentials limited to permitted projects/actions, without purchase or account-administration authority by default. Local tools remain usable without dashboard access, and a disconnected browser does not establish that a local operation failed.

## What remains local

Project access and future native Workbench execution belong on the developer's machine. The developer supplies the supported Workbench installation and their own project and providers. Hosted credentials cannot replace that local connection.

Project Brain and native execution are planned capabilities of the full distribution. Their accepted customer interfaces will be published with the release. The internal implementation and private knowledge are not part of this documentation repository.

Supported in-game checks will use the diagnostic components qualified for that release and selected project. The public integration is intended for creators' own addons; it does not grant access to another project's campaign, private knowledge or production server. Native tests, retained knowledge and the dashboard should refer to the same scoped result.

The connector being headless does not mean every native Workbench operation is invisible. Native tools may display their own windows according to the operation and platform.

See [agent setup](AGENT_GUIDE.md), [capability status](CAPABILITIES.md), and [privacy](PRIVACY.md).
