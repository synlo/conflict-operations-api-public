# Security policy

Do not open a public issue containing a credential, private endpoint, personal identifier, server configuration, log excerpt, or reproduction artifact with operational data.

Use the repository's private security-advisory channel for a suspected vulnerability: <https://github.com/synlo/conflict-operations-api-public/security/advisories/new>.

Reports should identify the affected public commit, file, and behavior without including secret values. The maintainers may request a sanitized reproducer through the advisory.

The public mirror has no live deployment authority. A public workflow or source change that introduces repository secrets, self-hosted runners, environments, deployment commands, provider access, or server-control commands is a security defect.
