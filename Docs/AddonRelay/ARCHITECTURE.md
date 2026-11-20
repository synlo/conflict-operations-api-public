# Connection model

AddonRelay's initial product is a **local companion your AI client starts when needed**. It has no AddonRelay graphical interface in the launch scope. The website provides product information, documentation, and qualified downloads.

## What connects

Your supported client communicates with the companion through stdio MCP. The companion receives the selected project directory and exposes the tools available in its installed version. The existing tools perform local inspection and diagnostic guidance.

A supporting command-line path is planned for setup and troubleshooting. It will use the same supported operations as the agent connection. A separate client application for every AI vendor is unnecessary.

## What remains local

Project access and future native Workbench execution belong on the developer's machine. The developer supplies the supported Workbench installation and their own project and providers. Hosted credentials cannot replace that local connection.

Project Brain and native execution are planned capabilities of the full distribution. Their accepted customer interfaces will be published with the release. The internal implementation and private knowledge are not part of this documentation repository.

The connector being headless does not mean every native Workbench operation is invisible. Native tools may display their own windows according to the operation and platform.

See [agent setup](AGENT_GUIDE.md), [capability status](CAPABILITIES.md), and [privacy](PRIVACY.md).
