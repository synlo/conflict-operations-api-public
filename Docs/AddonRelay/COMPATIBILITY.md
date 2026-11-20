# Compatibility and evidence scope

Compatibility must describe a tested combination, not just a technology name. This page records the current documentation boundary and the release information the public framework needs.

## Present boundary

| Component | Current documented requirement or scope |
|---|---|
| Local package | Complete Windows companion ZIP; dependencies bundled |
| Runtime | Node.js 24 or newer for the inspected package |
| Agent transport | Local stdio MCP |
| Client setup | Absolute runtime, companion, and project paths in trusted local configuration |
| Current agent tools | Six read-only inspections/guidance tools |
| Human interface | Local compact client and expanded workspace |
| Native game tooling | Existing developer Workbench workflow; public adapter remains planned |
| Initial native target | Supported Windows Arma Reforger Workbench installation |
| Full Enfusion coverage | Not established |
| Hosted access | Closed for new public customers |

Source instructions contain example configuration shapes for common local coding clients. This documentation publication is not a fresh acceptance run of each client's latest version. The release matrix should name each tested client and build before it is promoted as supported.

## Results answer different questions

| Result type | What it can prove | What it cannot prove by itself |
|---|---|---|
| Static lookup | A match or absence within the inspected scope | Whole-project validity or runtime behavior |
| Configuration inspection | The implemented structural/list checks passed | Server startup, authentication, or healthy gameplay |
| Synthetic sample | The sample path produces its expected explanation | An unrelated addon works in the engine |
| MCP connection | The client discovers and calls the companion | Native launch or persistent Brain integration |
| Native compile | The bound source compiled in the specified environment | Resource instantiation, gameplay, or replication |
| Native resource/runtime observation | The observed operation worked under the bound conditions | Unobserved inputs, states, platforms, or multiplayer paths |
| Authenticated multiplayer observation | The specified peer/server transition was observed | All player routes, controller behavior, or performance |
| Matched performance comparison | Behavior under the measured configuration and workload | Every population, machine, or gameplay route |

Current local report records use `engine-not-tested`. A future native recipe must emit its own appropriate scope rather than reusing that record as a native pass.

## Release compatibility record

Each application release should include a reviewed manifest covering:

- Product, client, companion, framework, recipe, and memory-schema versions.
- Artifact identity and expected checksum.
- Supported Windows and runtime versions.
- Exact engine/tool versions for native recipes.
- Tested client versions and their configuration shape.
- Owned sample identity and the workflow it demonstrates.
- Known limitations, unsupported paths, and migration requirements.
- Date and kind of the observation supporting each compatibility claim.

Different components can have different versions. The release manifest should explain that relationship rather than hiding inconsistent hard-coded labels behind a single marketing version.

## Reusing evidence

The planned framework should compare the relevant source, providers, engine, recipe, fixture, configuration, and execution environment before reusing a result. It should explain which dependency changed and which observation must be repeated.

A reporting-only change should not force an unrelated gameplay rerun. A change to the parser that decides whether an observation passed can require reviewing that observation even when the game package is unchanged. Archived results remain historical evidence; a new check requiring their original bytes needs a verified original or established archive reference.

Repeated input is not new evidence. A new successful run does not erase an earlier unsuccessful one. Gate counts should not be presented as a percentage of engineering effort or a release estimate.

## Required launch exercises

The public native distribution should be exercised with an unrelated addon, paths containing spaces and non-ASCII characters, missing prerequisites, non-administrator use, interrupted sessions, changed inputs, and unavailable optional services. Unsupported combinations should fail with a useful explanation.

Hardware-specific behavior needs its own observation. Synthetic input, static code, and mouse-based automation do not qualify physical controller or console behavior. See the [roadmap](ROADMAP.md) for which tests belong to each milestone.
