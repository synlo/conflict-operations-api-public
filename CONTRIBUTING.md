# Contributing

Contributions should remain within the public backend framework: contracts, schemas, deterministic policy, safe examples, static tests, and documentation.

Before proposing a change:

1. Run both Python unit-test modules documented in the README.
2. Run the public export twice and confirm the export identity is unchanged.
3. Verify the exact staged tree with `audit_public_export.py staged`.
4. Do not add operational reports, server configuration, credentials, provider details, personal paths, game packages, third-party assets, generated databases, logs, or unverified source.
5. Add provenance before adding a path to the allowlist.

Pull requests must explain the failure mode being addressed, the fail-closed behavior, and the exact tests that prove it. Do not weaken a gate to make a fixture pass.
