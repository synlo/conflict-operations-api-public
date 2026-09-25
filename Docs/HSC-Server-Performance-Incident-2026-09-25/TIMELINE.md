# Investigation Timeline

**Date:** 2026-09-25  
**Time zone:** MDT, UTC-6

These timestamps summarize the active investigation session. They are intended to help the HSC hosting owner line up infrastructure graphs with the period in which live degradation and controlled tests were being compared.

## 12:31 MDT

- Core AI population was observed staying bounded in available logs.
- Investigation shifted from simple AI-count growth toward AI-provider update behavior.
- An isolated test fixture was being prepared to measure suspected bottlenecks.

## 13:05 MDT

- A benchmark-validity problem was found.
- Squads spawn their members gradually.
- A one-time protection step had protected only 11 of 36 soldiers.
- Later arrivals could be killed, which changed the workload during measurement.
- The test was corrected to keep the intended population stable.
- Corrected 36-soldier combat stayed around 60 FPS.
- Next step was to increase load to 108 soldiers.

## 13:27 MDT

- Larger local battle remained around 55-60 FPS.
- FPS recovered toward 60 after extra test units were removed.
- The test was tightened so a changing AI count could no longer hide behind an otherwise passing sequence.
- The full-map test initially encountered the laptop's memory safety threshold before launch.
- Optional local applications were closed while preserving required tooling.
- With the full Arland environment loaded, the 108-soldier battle stayed around 57 FPS.
- A cleanup issue was discovered where queued radio calls referenced soldiers deleted by the test.
- Recovery logic was adjusted so test characters remained present but inactive, preventing the benchmark itself from invalidating the measurement.

## 13:32 MDT

- Full-Arland test completed with valid timing evidence.
- Measured test memory usage was about 1.5 GiB in that test context.
- The test still did not reproduce HSC's previously observed 20-28 FPS range.
- The same workload was being moved to Everon and inactive-entity cleanup was being checked.

## By 13:50 MDT

- Infantry scripts measured so far accounted for only a small share of frame time.
- A private test of the exact deployed campaign behavior, including normal AI management, was added.
- Fresh live monitoring / Discord alerts reported HSC server FPS falling as low as approximately 9-10 FPS.
- That low-FPS report occurred with roughly 40-50 active soldiers.
- The local full-campaign test remained near 58-60 FPS.
- The campaign test reached approximately 126 active soldiers at peak.
- Bohemia's diagnostic virtual-connection option was identified for partial replication-load testing without needing many full graphical clients.
- Investigation focus shifted toward replication and player-related work rather than lowering AI counts without evidence.

## Current interpretation

The most important result is not a specific suspect. It is the repeated failure to reproduce the live FPS collapse with heavy local AI and campaign workloads.

At this point:

- AI quantity alone has not reproduced the issue.
- 108 active soldiers have not reproduced the issue.
- Full Arland plus 108 soldiers has not reproduced the issue.
- Full campaign behavior plus a peak of about 126 soldiers has not reproduced the issue.
- Live HSC can still fall to 9-10 server FPS with substantially fewer active soldiers.

The remaining difference between controlled tests and live HSC deserves focused measurement of real players, replication, long-running state, and host resource scheduling.
