# HSC Server Performance Incident - Hosting-Side Investigation Brief

**Audience:** HSC server owner / hosting provider  
**Incident date:** 2026-09-25  
**Time zone used below:** Mountain Daylight Time, MDT, UTC-6  
**Status:** Active investigation  
**Primary symptom:** Severe server simulation FPS degradation on the live HSC Arma Reforger server

## Executive summary

The live HSC server has recently reported server simulation FPS falling far below what we can reproduce in controlled local testing.

The most important current observation is the size of the gap:

| Environment | Approximate workload | Observed server / simulation FPS |
| --- | --- | ---: |
| Controlled local combat | 36 active soldiers | about 60 FPS |
| Controlled local larger battle | 108 active soldiers | about 55-60 FPS |
| Full Arland environment | 108 active soldiers | about 57 FPS |
| Full campaign test | peak 126 active soldiers | about 58-60 FPS |
| Live HSC | roughly 40-50 active soldiers during a reported incident | as low as 9-10 server FPS |

This does **not** prove that hosting hardware or virtualization is the root cause. It does show that ordinary AI quantity, infantry combat, and the campaign workload alone have not reproduced the live degradation so far.

The investigation is therefore shifting toward the parts of the live environment that local tests do not fully reproduce, especially:

1. Player connection and replication workload
2. Host CPU scheduling, single-core saturation, CPU quota or throttling
3. Virtualization steal / ready time or noisy-neighbor behavior
4. Effective CPU clock behavior and power management
5. Memory pressure, paging, or host-level limits
6. Long-running server state or entity accumulation
7. Network packet processing and per-player replicated-entity cost
8. Provider-specific caps, cgroup limits, container limits, or VM resource contention
9. Background host tasks that coincide with FPS collapses
10. An interaction between the above rather than one isolated subsystem

## What we are asking the HSC host owner to investigate

Please check whether the low server-FPS periods line up with any infrastructure-side limit or resource anomaly.

The most useful evidence is **per-core CPU data and host-level scheduling data**, not only total CPU percentage.

Arma Reforger can become simulation-thread limited while the machine still appears to have plenty of total CPU capacity. For example, a server with one critical thread saturated can show low total CPU utilization across many cores while server FPS collapses.

Please capture or export the following during a low-FPS event if possible:

- CPU usage per logical core
- Effective CPU clock / frequency
- Server-process CPU usage
- CPU steal time, CPU ready time, or equivalent hypervisor scheduling delay
- CPU throttling or cgroup quota counters
- VM / container CPU entitlement and any burst-credit system
- Available RAM, committed RAM, swap / pagefile usage
- Major page faults or hard faults
- Disk latency and I/O queue depth
- Network bandwidth, packets per second, packet loss, errors, and retransmits if available
- Arma Reforger server FPS at the same timestamps
- Connected player count at the same timestamps
- Active AI / soldier count at the same timestamps
- Server uptime since last clean restart
- Any scheduled backup, snapshot, antivirus scan, log rotation, maintenance, or control-panel task
- Any host migration, node maintenance, or capacity event

A more detailed collection checklist is in [HOST_CHECKLIST.md](./HOST_CHECKLIST.md).

## Current evidence

### AI population is not running away

The investigation began by checking whether the AI population was simply growing without bounds. Current logs do not support that explanation.

A test-harness bug was also found and corrected. Squads spawned members gradually, so an early version of the test protected only 11 of 36 soldiers. The later arrivals could die and change the workload during measurement. After correcting the benchmark so all 36 remained present, the test stayed around 60 FPS during combat.

This matters because the benchmark now holds the intended AI workload stable instead of accidentally reducing load while it runs.

### 108-soldier test still performs normally

The workload was increased to 108 soldiers. The larger battle remained around 55-60 FPS locally and returned toward 60 FPS when the extra test units were removed.

This significantly weakens the hypothesis that "a lot of AI by itself" is enough to explain the live HSC slowdown.

### Full map environment still does not reproduce the issue

The same large battle was tested with the full Arland environment loaded. It remained around 57 FPS.

A cleanup issue was found in the test where queued radio calls referenced soldiers that the test had just deleted. The benchmark was changed so those test characters remained present but inactive during recovery measurements. That cleanup issue is currently treated as a benchmark correctness problem, not as proof of the live root cause.

### Full campaign test still remains near 60 FPS

A private test of the deployed campaign behavior, including normal AI management, was added so the investigation would not rely only on isolated terrain tests.

The full campaign test remained around 58-60 FPS and reached approximately 126 active soldiers at peak.

Infantry scripts measured so far account for only a small share of frame time.

### Live HSC remains dramatically slower

By approximately **13:50 MDT on 2026-09-25**, fresh live monitoring / Discord alerts reported HSC dropping as low as **9-10 server FPS** with roughly **40-50 active soldiers**.

That is the strongest current discrepancy:

> The controlled campaign can run near 60 FPS with approximately 126 active soldiers, while the live server has fallen to 9-10 FPS with far fewer active soldiers.

The two environments are not identical. Most importantly, the local campaign test does not fully reproduce real-player replication and hosting infrastructure. That is why the next investigation lane is focused on replication, connected-player work, and host conditions.

## Current investigation direction

Bohemia's diagnostic virtual-connection option has been identified as a way to exercise part of the replication workload without launching many full graphical clients on the test machine.

This should help answer whether adding connection / replication pressure causes the controlled test to move toward the live HSC behavior.

It will **not** replace real-player validation. A synthetic or virtual connection can exercise only part of what real players cause.

## High-value hosting-side hypotheses

### 1. Single-core or main-thread saturation

This is one of the first things to check.

Do not rely only on a dashboard that says "CPU 30%". On an 8-core host, one fully saturated critical core can be hidden inside a much lower total percentage.

Please provide per-core graphs if the hosting platform supports them.

### 2. VM / container throttling

If HSC runs in a VM or container, check for:

- CPU quota limits
- CPU burst credits
- cgroup throttled time
- hypervisor CPU ready time
- hypervisor steal time
- oversubscribed host nodes
- dynamic CPU frequency restrictions
- provider-side fair-use caps

A server process can appear to request CPU normally while the hypervisor does not schedule it often enough.

### 3. Clock-speed collapse or power limits

Please verify the **effective clock** during low FPS.

A CPU can show moderate utilization while running at a much lower frequency because of:

- power-saving policy
- thermal throttling
- package power limits
- host firmware policy
- cloud / VM frequency behavior

### 4. Memory pressure and paging

The full local Arland test used about 1.5 GiB in the measured test context and did not reproduce the low FPS.

That does not rule out memory pressure on HSC. Please check host-wide memory availability, commit, swap / pagefile activity, hard faults, and whether another process is competing for RAM.

### 5. Long-running live state

Compare:

- FPS immediately after a clean server restart
- FPS after the same mission has run for several hours
- entity count / AI count / connected players at both points

If FPS starts healthy and degrades over time at similar population, that would point toward accumulated state, stale entities, growing replication sets, queues, or another lifecycle problem.

### 6. Player / replication scaling

Please correlate server FPS against connected players even when AI count is similar.

A useful sample would be:

| Time | Players | Active soldiers | Server FPS | CPU per-core peak | RAM | Network pps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0-2 | record | record | record | record | record |
| moderate | 6-8 | record | record | record | record | record |
| higher | 12-16 | record | record | record | record | record |

If server FPS falls primarily with player count while AI remains similar, replication becomes a much stronger lead.

## Most useful controlled host tests

If the owner can run controlled tests without disrupting players, these would be especially valuable:

1. **Fresh restart baseline**  
   Record server FPS, per-core CPU, RAM, disk, network, players, and AI immediately after a clean restart.

2. **Same mission, increasing real-player count**  
   Hold the mission and AI conditions as stable as practical. Compare 0-2, 4, 8, 12, and 16 players.

3. **Same mission on alternate hardware / node**  
   If the provider can temporarily clone or migrate the exact server configuration to a different physical host, compare server FPS under similar load. A large improvement would strongly implicate infrastructure or resource scheduling.

4. **Long-run comparison**  
   Capture the same metrics after 1 hour, 3 hours, 6 hours, and immediately before a low-FPS event.

5. **Host-limit comparison**  
   Confirm whether the VM/container has explicit vCPU quotas, CPU shares, burst credits, RAM hard limits, or I/O limits.

## What not to conclude yet

Current evidence does **not** justify the following conclusions:

- "The AI count is definitely too high."
- "The host hardware is definitely bad."
- "The network is definitely the cause."
- "The radio cleanup warning is the live root cause."
- "The local 60 FPS test proves the live server should also be 60 FPS."

The purpose of this document is to narrow the investigation and collect evidence from the one environment we cannot fully reproduce locally: the live HSC host with real players and the actual hosting stack.

## What would be most useful to send back

Please provide any of the following that are available:

- Screenshot or CSV of per-core CPU graphs during a low-FPS period
- Host CPU model
- Number of physical cores / logical cores / assigned vCPUs
- VM or container type
- CPU quota / share / burst policy
- Effective CPU clock during the incident
- CPU steal / ready / throttled time
- RAM assigned and RAM actually used
- Swap / pagefile usage
- Disk latency
- Network usage and packet rate
- Player count
- Active soldier / AI count
- Server FPS
- Exact timestamp and time zone
- Server uptime
- Whether a restart immediately restores FPS
- Whether another server on the same node was affected
- Any provider-side incident or maintenance notification

A fill-in template is available in [DATA_CAPTURE_TEMPLATE.md](./DATA_CAPTURE_TEMPLATE.md).

## Safety and privacy

Do **not** post passwords, RCON credentials, API keys, SFTP credentials, control-panel tokens, private IP-management credentials, or private customer data in this public repository.

Public screenshots should redact anything sensitive.

## Bottom line

We have been able to run increasingly heavy AI and campaign tests locally without reproducing HSC's severe server-FPS collapse. The current evidence therefore makes the live-only parts of the system much more important: player replication, long-running state, and hosting / virtualization behavior.

The highest-value next step from the HSC owner is synchronized infrastructure telemetry during a real low-FPS event.
