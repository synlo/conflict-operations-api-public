# Public mirror policy

The public mirror is rebuilt from the current private working tree through an allowlist-first export. It is never created by changing the private repository's visibility, cloning private history, mirroring refs, or copying GitHub Actions artifacts.

## Required gates

An export is eligible only when:

- every source/destination mapping is exact and present in `.publicmirror/public-source-allowlist.txt`;
- every mapping has exactly one allowed status in `.publicmirror/public-provenance.json`;
- source paths are regular files inside the repository and do not traverse a symlink, junction, or reparse point;
- placeholder transformations are drawn only from `.publicmirror/public-placeholders.json`;
- the path denylist, content scanner, workflow audit, UTF-8 gate, binary gate, provenance gate, and manifest verification all pass;
- two unchanged safe-fixture exports produce the same identity;
- the exact Git index is rescanned before a public commit.

Allowed provenance statuses are `COAPI_OWNED`, `REDISTRIBUTION_LICENSE_VERIFIED`, and `GENERATED_PUBLIC_SAFE`. Unknown, third-party, and private-operational statuses are terminal export refusals.

## Always excluded

Private history, branches, tags, reports, handoffs, runtime configuration, backups, logs, proof runs, provider information, credentials, personal identifiers, generated databases, binary packages, downloaded content, base-game material, Workshop material, and dev-bridge output are excluded. The private repository's issues, pull requests, releases, Actions runs, and artifacts are not imported.

## Workflows

Public workflows use GitHub-hosted runners, read-only default permissions, pinned action commits, and static checks only. Repository secrets, environments, self-hosted runners, publication, deployment, SFTP, RCON, provider access, webhook calls, and server control are forbidden.

## Rights

The exporter does not infer a license from publication. If a license is not already deliberate and proven, the public snapshot carries the repository rights notice instead of inventing one.
