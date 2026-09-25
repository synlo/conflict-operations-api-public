# HSC Host Data Capture Template

Copy this file into a reply, issue comment, or private message after removing anything sensitive.

## Incident identity

- Date:
- Local time:
- Time zone:
- Server FPS:
- Connected players:
- Active soldiers / AI:
- Server uptime:
- Time since last restart:
- Did a restart immediately restore FPS? Yes / No / Not tested

## Hosting environment

- Hosting provider:
- Bare metal / VM / container:
- CPU model:
- Physical cores:
- Logical cores:
- vCPUs assigned:
- RAM assigned:
- Storage type:
- Operating system:
- Hypervisor / container platform if known:
- Other game servers sharing the same VM / machine:

## CPU at the exact incident time

- Total CPU %:
- Highest single-core %:
- Number of cores above 90%:
- Arma server process CPU %:
- Effective CPU clock:
- CPU steal %:
- CPU ready %:
- cgroup throttling before:
- cgroup throttling after:
- CPU quota / shares:
- Burst credits or equivalent:

Attach per-core screenshot / CSV if possible.

## Memory

- Arma server working set:
- Total used RAM:
- Available RAM:
- Commit / committed bytes:
- Swap or pagefile used:
- Major / hard faults:
- Any OOM / memory-pressure alert:

## Disk

- Read throughput:
- Write throughput:
- Read latency:
- Write latency:
- Queue depth:
- I/O wait:
- IOPS cap:
- Any backup / snapshot running:

## Network

- Inbound bandwidth:
- Outbound bandwidth:
- Inbound packets/sec:
- Outbound packets/sec:
- Packet drops:
- Interface errors:
- Retransmits:
- Any DDoS / filtering event:
- Any network cap / shaping policy:

## Host / provider events

- Node maintenance:
- Live migration:
- Scheduled backup:
- Snapshot:
- Security scan:
- Log rotation:
- Provider incident:
- Another tenant / noisy-neighbor warning:
- CPU-credit exhaustion:
- Other:

## Before / after restart comparison

| Metric | Before restart | 5 min after restart |
| --- | ---: | ---: |
| Server FPS | | |
| Players | | |
| Active soldiers | | |
| Highest core % | | |
| Process CPU % | | |
| RAM used | | |
| Network pps | | |
| Disk latency | | |
| CPU steal / ready | | |

## Player-scaling comparison

| Players | Active soldiers | Server FPS | Highest core % | Process CPU % | Network pps |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0-2 | | | | | |
| 4 | | | | | |
| 8 | | | | | |
| 12 | | | | | |
| 16 | | | | | |

## Notes

Please include anything that changed around the incident, even if it seems unrelated.

Do not include credentials, tokens, passwords, private keys, or control-panel secrets.
