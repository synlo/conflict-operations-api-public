# OpenAI Support: Codex Parallel-Agent Usage Review

This page is an explanatory support submission, not an original Codex session transcript or an OpenAI usage ledger. The original project benchmark linked below is published separately, without changes to its contents.

## Original evidence available without private-repository access

[Open the unmodified benchmark407.json at its public publication commit](https://github.com/synlo/conflict-operations-api-public/blob/e97f15b85e0eab9a0b014c248e88d11d9748e204/Docs/support-evidence/2026-09-11/benchmark407.json)

[Raw JSON at the same pinned commit](https://raw.githubusercontent.com/synlo/conflict-operations-api-public/e97f15b85e0eab9a0b014c248e88d11d9748e204/Docs/support-evidence/2026-09-11/benchmark407.json)

### Provenance and copy-integrity verification

- Original repository: `synlo/conflict-operations-api` (private).
- Original path: `Reports/2_1_6_hotfix/benchmark407.json`.
- Original source commit used for this export: `3bd4f916a245d858f82ea6f88f91067eca7db777`.
- Original Git blob SHA: `ad8e4e2efe27da79c564c14eb34b8a209d0630b9`.
- Public copy commit: `e97f15b85e0eab9a0b014c248e88d11d9748e204`.
- Public copy Git blob SHA, verified by fetching it after publication: `ad8e4e2efe27da79c564c14eb34b8a209d0630b9`.
- Export treatment: no reformatting, redaction, omitted fields, or changed measurements. The file's limitations and unknowns are retained.

The matching Git blob identities verify that the public copy matches the original stored file. They do not independently authenticate the underlying execution, certify a commit timestamp, or prove any OpenAI billing or usage-accounting error. This is an original project-generated benchmark report, not the complete raw engine logs or model telemetry.

## What the original benchmark records

The report compares one successful baseline vehicle procedure with one successful integrated-diagnostics procedure.

| Metric | Baseline procedure | Integrated procedure |
| --- | ---: | ---: |
| Total run time | 320.861 s | 192.331 s |
| Driving command submissions after viewport preparation | 4 | 1 |
| Recording bytes | 84,081,266 | 48,275,381 |
| Cleanup time | 40.280 s | 34.897 s |
| Preflight time | 21.617 s | 25.556 s |

Run identifiers in the original report are `wb-probe-hotfix216-input-387` and `wb-probe-hotfix216-diagnose-395`. Package and provider identities are also retained in the JSON.

Important limitations:

- This is not a controlled parallel-agent-versus-single-agent experiment. The workflow and automation changed as well.
- There is one successful sample per path; unsuccessful qualification attempts are excluded from this paired comparison.
- The round-trip metric counts driving-command submissions after viewport preparation, not every model or tool call.
- The report has no token totals, credits consumed, account allowance history, or OpenAI metering records.
- Although the original JSON contains percentile fields, one sample per path does not establish a meaningful latency distribution.

Accordingly, the benchmark supports a narrow workflow-efficiency observation. It must not be presented as proof of a 40% credit saving, a 75% reduction in total model calls, or duplicate billing.

## Recorded single-agent workflow

A separate private project status record, `Reports/2_1_6_hotfix/status.json`, was previously retrieved with Git blob SHA `d430697e1a1d63abb7889b7cd9cf1b111ac54a86`. The following are selected reported fields, not a complete unmodified public copy of that file:

- `workflow.singleAgent: true`
- `parallelAgents: false`
- `workflow.automaticStopAndSeal: true`
- `workflow.diagnosticCLI: diagnose plan/run/ready/explain/resource`

The complete operational status file is not being published. These fields document the recorded workflow decision; they are not an independently verified count of all agents that actually ran.

## User-reported problem for OpenAI to investigate

The user reports that concurrent agents consumed a disproportionately large part of their 20x Codex allowance while repeatedly revisiting tests, investigating overlapping issues, and reconciling separate work. They report improved practical progress after moving to one agent and reusable procedures, and state that they will no longer use parallel agents.

Those descriptions are the user's account of their experience, not conclusions established by the benchmark. The initial support summary described some of them too categorically; this revision separates the account from what the published artifact actually shows. GitHub preserves the earlier revision in the page's history.

## Requested account-side investigation

Please review the corresponding recent Codex sessions and available parent/subagent usage records, including repeated work, retries, and accounting. The user requests restoration of affected usage, a reset if available under an applicable exception, or another permitted remedy if a fault is confirmed. No entitlement or outcome is asserted here.

To correlate this material with account-side records, obtain the user's account email through the private support channel, the affected session identifiers or links, client/model information, usage-dashboard screenshots, and dates/times with time zone. Do not publish account credentials, tokens, player identifiers, private server details, or unreviewed session logs in this public repository.

The main project repository and its history remain private. This public evidence page and the original benchmark are deliberately limited support material, not a public replication of the full project.
