# Backend architecture

The backend framework has four narrow layers:

1. **Contract and mode policy** — a strict task contract binds branch, starting commit, permissions, budgets, allowed paths, required outputs, and terminal states. RECOVERY is local-only, DEVELOPMENT permits bounded source work and private review delivery, and RELEASE is required for public-repository or runtime authority.
2. **Single-writer and bounded execution** — repository, Workbench, and release locks use process identity and start time. Commands have finite timeouts, normalized fingerprints, input hashes, operation budgets, and a two-attempt hypothesis ceiling.
3. **Tamper-evident evidence** — operation entries form an append-only SHA-256 chain. Expected transition artifacts are inside the repository, allowlisted by the contract, and hashed only after successful creation.
4. **Public-source boundary** — an exact path allowlist, exact provenance record, placeholder transformation, content scanner, workflow policy, and deterministic manifest create a new-history source snapshot.

No layer treats source presence as runtime proof. The public framework contains no package, deployment, provider, or server-control adapter.
