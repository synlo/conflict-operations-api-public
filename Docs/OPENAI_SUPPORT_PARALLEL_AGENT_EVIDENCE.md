# OpenAI Support Evidence: Parallel Agent Usage Review

This document is a public-safe summary supporting a request for OpenAI to review unusually high Codex / Parallel Agent usage on the Conflict Operations project.

The full working repository remains private because it contains operational reports, server configuration, provider details, deployment state, logs, and other material that is intentionally excluded from the public mirror. This public repository is the sanitized mirror used to demonstrate the project and its automation framework without exposing that private material.

## What changed

During earlier development, multiple concurrent agents were used for investigation and validation. In practice, that workflow repeatedly reloaded overlapping project context, duplicated investigations, produced separate evidence trails, and required reconciliation before changes could be accepted.

The project later moved to a single-agent workflow with reusable diagnostics, evidence reuse, bounded procedures, automatic cleanup, and automatic evidence sealing. The private canonical status for the 2.1.6 release records:

- `singleAgent: true`
- `parallelAgents: false`
- `automaticStopAndSeal: true`
- diagnostic CLI: `diagnose plan/run/ready/explain/resource`
- driving command round trips after viewport preparation: `4 -> 1`
- package round trip: `PASS_426_EXACT_PAYLOADS`
- PC compile: `PASS`
- HEADLESS compile: `PASS`

The canonical private status file used for this summary has blob SHA:

`d430697e1a1d63abb7889b7cd9cf1b111ac54a86`

## Measured workflow improvement

A controlled M998 Workbench comparison measured one successful baseline run against one successful integrated-diagnostics run:

| Metric | Baseline | Single-agent framework |
| --- | ---: | ---: |
| Total run time | 320.861 s | 192.331 s |
| Driving command round trips | 4 | 1 |
| Recording size | 84,081,266 bytes | 48,275,381 bytes |
| Cleanup time | 40.280 s | 34.897 s |
| Preflight time | 21.617 s | 25.556 s |

This is one paired sample, not a universal performance claim. It does show that after consolidating work into a reusable single-agent framework, the same class of validation required fewer command submissions and substantially less total execution time in that comparison.

The canonical private benchmark file used for these values has blob SHA:

`ad8e4e2efe27da79c564c14eb34b8a209d0630b9`

## Why this matters for the support request

The support request is not claiming that GitHub can prove OpenAI billing or exact credit consumption. Only OpenAI can verify account-level usage records. This repository instead provides independent project evidence showing:

1. the project is real and substantial;
2. parallel work was replaced by a deliberately single-agent architecture;
3. the replacement workflow introduced reusable infrastructure rather than repeated one-off investigations; and
4. the resulting workflow has concrete measured reductions in repeated command submissions and execution time for at least one comparable validation path.

The user is asking OpenAI to review the corresponding account-side Parallel Agent usage, identify duplicated or disproportionate consumption, and consider an appropriate usage adjustment if the internal logs confirm it.
