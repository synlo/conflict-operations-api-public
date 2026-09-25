# HSC Hosting-Side Performance Checklist

**Incident:** HSC Arma Reforger server simulation FPS degradation  
**Date:** 2026-09-25  
**Time zone:** MDT, UTC-6

This checklist is designed for the person who controls the HSC hosting account, VM, container, or physical server.

## Priority 1: capture these during the next low-FPS event

Record all values against the **same timestamp**:

- Server FPS
- Connected players
- Active AI / soldiers
- Total CPU
- CPU per logical core
- Arma Reforger server process CPU
- Effective CPU clock
- Available RAM
- Swap / pagefile use
- Disk read/write latency
- Network bytes per second
- Network packets per second
- Server uptime
- Any host warning, CPU cap, or maintenance event

If the provider dashboard only keeps 5-minute averages, export the highest-resolution graph available.

## CPU and scheduling

### Hardware identity

Please record:

- CPU model
- Physical core count
- Logical core count
- vCPU count assigned to HSC
- Whether the server is bare metal, VM, or container
- Hypervisor / virtualization platform if known
- NUMA layout if available

### Per-core utilization

A total CPU graph is not enough.

Look for:

- One logical core pinned near 100%
- A small number of cores pinned while total CPU remains low
- Sudden drops in process CPU at the exact moment server FPS falls
- CPU usage that looks low while the process is ready to run but not being scheduled

### Effective frequency

Record CPU frequency / effective clock during:

- healthy server FPS
- degraded server FPS

Suspicious patterns include:

- frequency far below expected base / sustained clock
- frequent clock collapse under load
- thermal or power throttling
- aggressive power-saving behavior

### Virtualization scheduling

If virtualized, request or inspect:

- CPU steal time
- CPU ready time
- cgroup throttled_usec / nr_throttled
- CPU quota
- CPU shares / weight
- burst-credit balance
- host oversubscription ratio if the provider exposes it

A high steal / ready value means the VM wants CPU time but the physical host is not scheduling it promptly.

## Memory

Record:

- RAM assigned to the server
- RAM used by ArmaReforgerServer
- Total host / VM RAM used
- Available memory
- Commit / committed bytes
- Swap or pagefile size and usage
- Hard faults / major faults
- OOM or memory-pressure events

Questions:

- Does swap activity begin when server FPS drops?
- Does the server approach a hard memory limit?
- Is a different process consuming memory at the same time?
- Does memory usage grow steadily over many hours?

## Disk and storage

Record:

- Storage type if known: local NVMe, SATA SSD, network volume, etc.
- Read/write throughput
- Average read latency
- Average write latency
- Queue depth
- I/O wait
- Provider IOPS / throughput cap if applicable

Check whether the low-FPS event coincides with:

- backup / snapshot
- antivirus or endpoint scan
- large log rotation
- persistence save
- host migration
- storage throttling

## Network and replication

Record:

- inbound bandwidth
- outbound bandwidth
- inbound packets per second
- outbound packets per second
- dropped packets
- interface errors
- retransmits if available
- provider DDoS / filtering event if shown
- connected players

The current local tests do not reproduce the full real-player replication workload. Player scaling is therefore a priority.

Useful comparison:

1. 0-2 players
2. 4 players
3. 8 players
4. 12 players
5. 16 players or normal peak

At each step, record server FPS and the infrastructure metrics above.

## Process configuration

Please confirm:

- ArmaReforgerServer process priority
- CPU affinity, if any
- Whether affinity was manually restricted
- Windows power plan or Linux governor
- container CPU quota
- service resource limits
- any watchdog or wrapper that periodically changes priority / affinity
- number of server instances sharing the same VM

Do not change affinity or priority blindly. Capture the current configuration first.

## Long-running-state test

Record server performance:

- immediately after restart
- 30 minutes after restart
- 1 hour
- 3 hours
- 6 hours
- immediately before a severe FPS drop

For every sample, record:

| Timestamp | Uptime | Players | Active soldiers | Server FPS | Process CPU | Hottest core | RAM | Network pps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| | | | | | | | | |

Interpretation:

- Healthy after restart, then progressively worse at similar population can indicate state accumulation.
- Immediately bad after restart under low player count makes accumulated state less likely.
- Large FPS changes with player count but not AI count make replication / per-player systems more likely.
- Large FPS changes after moving to another host node make infrastructure more likely.

## Windows collection examples

Use these only if the HSC host exposes Windows shell access.

### Basic hardware and process

~~~powershell
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory, Manufacturer, Model
Get-Process ArmaReforgerServer -ErrorAction SilentlyContinue | Select-Object Id, CPU, WorkingSet64, PrivateMemorySize64, Threads, PriorityClass
~~~

### Quick live counters

~~~powershell
Get-Counter '\Processor Information(*)\% Processor Time','\Memory\Available MBytes','\Memory\Committed Bytes','\Paging File(_Total)\% Usage','\PhysicalDisk(_Total)\Avg. Disk sec/Transfer','\Network Interface(*)\Bytes Total/sec' -SampleInterval 1 -MaxSamples 120
~~~

### Per-process sampling

~~~powershell
Get-Counter '\Process(ArmaReforgerServer*)\% Processor Time','\Process(ArmaReforgerServer*)\Working Set - Private','\Process(ArmaReforgerServer*)\Thread Count' -SampleInterval 1 -MaxSamples 120
~~~

If the process instance name differs:

~~~powershell
(Get-Counter -ListSet Process).PathsWithInstances | Select-String Arma
~~~

## Linux collection examples

Use these only if the HSC host exposes Linux shell access.

### Hardware and virtualization

~~~bash
lscpu
free -h
cat /proc/meminfo | head -40
~~~

### Per-core CPU and steal

If sysstat is installed:

~~~bash
mpstat -P ALL 1 120
~~~

Look especially at per-core utilization and the steal percentage.

### Process threads

~~~bash
pidof ArmaReforgerServer
pidstat -p <PID> -t 1 120
~~~

### Memory and scheduling

~~~bash
vmstat 1 120
~~~

Pay attention to swap activity, run queue, I/O wait, and steal.

### Disk

If sysstat is installed:

~~~bash
iostat -xz 1 120
~~~

### Network

~~~bash
sar -n DEV 1 120
~~~

### Container / cgroup throttling

Depending on cgroup version:

~~~bash
cat /sys/fs/cgroup/cpu.stat 2>/dev/null
cat /sys/fs/cgroup/cpu.max 2>/dev/null
cat /sys/fs/cgroup/memory.current 2>/dev/null
cat /sys/fs/cgroup/memory.max 2>/dev/null
~~~

Useful fields in cpu.stat include throttling counters. If they increase quickly during low server FPS, capture the before and after values.

## Provider control-panel users

If you do not have shell access, please export screenshots / CSVs for:

- CPU total
- CPU per core if available
- RAM
- disk I/O / IOPS
- network
- VM throttling / CPU credits
- node incident log
- reboot history
- server uptime

Use a time range that includes at least **15 minutes before and 15 minutes after** the low-FPS event.

## Controlled hardware comparison

If the host can clone the server to another physical node, this is one of the strongest infrastructure tests.

Keep constant:

- same Arma Reforger version
- same exact mod versions
- same mission
- same server settings
- same save / campaign state if practical
- similar player and AI load

Then compare:

- server FPS
- per-core CPU
- effective clock
- CPU steal / ready
- memory
- network pps

A major performance improvement on a different host node would be strong evidence for infrastructure scheduling or hardware differences.

## Please do not do these before collecting evidence

- Do not reduce AI count as the first response solely to make the symptom disappear.
- Do not change multiple host settings at once.
- Do not delete campaign state before capturing a baseline.
- Do not disable security software globally.
- Do not publish credentials or private provider information.
- Do not restart repeatedly without first noting pre-restart FPS, player count, AI count, CPU, and RAM.

A restart can be a useful test, but the before / after evidence is more valuable than the restart itself.
