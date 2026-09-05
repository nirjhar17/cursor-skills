---
name: rhel-performance-framework
description: "Applies a reusable RHEL Performance Framework (RH442 / USE method) for Linux performance tuning across CPU, memory, I/O, network, and kernel/TuneD. Use when the user mentions RHEL performance, Linux performance tuning, RH442, TuneD, sysctl, NUMA, HugePages, Oracle RAC OS tuning, %sys, run queue, C-states, NIC ring buffers, mpstat, perf, or architecture review of RHEL for databases."
---

# RHEL Performance Framework

Distilled from [RHEL Performance Tuning Course](2311eeda-bdf5-4d5d-8517-803427266637) (RH442). Apply this framework; do not dump the transcript.

Command cheat sheet: [reference.md](reference.md)

## Coverage (do not invent skipped chapters)

Covered in the source chat:

- Ch 1 — concepts, USE method, units
- Ch 2 — metrics tools (`top`/`ps`/`free`/`vmstat`, sysstat, PCP)
- Ch 3 — hardware inventory (`dmesg`, `lscpu`, `dmidecode`, `lspci`, `lstopo`, `rasdaemon`/`ras-mc-ctl`)
- Ch 4 — sysctl, TuneD, custom profiles, Ansible `kernel_settings`
- Ch 8 — CPU scheduling, real-time, affinity/isolation, cache/`perf`
- Ch 9 — virtual memory, paging, NUMA, overcommit
- Ch 11 — network latency/throughput, jumbo frames, C-states, NIC offload

Skipped (never taught in that chat): **Ch 5, 6, 7, 10**, and anything after Ch 11. Do not invent their titles or content. I/O in this skill is only what appeared as side material (`iostat`, FIO, I/O scheduler from Oracle KCS).

## Architect vs GSS/support

- GSS / support: debug one host, one symptom, one tunable; live `sysctl -w` experiments; prove a single parameter is wrong; fix the incident.
- Architect: consistency and capacity across the estate; same TuneD profile, HugePages, NUMA, buffers, and kernel on every peer; persistent TuneD custom profiles with documented trade-offs; sign off that the platform can hold the workload.

Use USE to find the bottleneck class. Then argue architecture (sizing, consistency, persistence), not a magic sysctl.

## USE method (errors first)

For every resource (CPU, memory, storage, network):

1. Errors first — ECC, `rasdaemon`, NIC drops/errors, disk errors. Errors fake high utilization (retries). Fix the cable before tuning buffers.
2. Utilization — percent busy. Sustained ~70%+ is suspicious (averages hide 100% bursts). Disks cannot be interrupted mid-I/O, so moderate disk util already queues.
3. Saturation — any queue is a problem. CPU run queue, memory reclaim/swap, disk await, network backlog/drops.

Change process: baseline, change one thing, re-measure the same workload, revert to confirm, persist and document. No free lunch: bigger network buffers steal RAM from databases.

Human factor: 95% CPU is not automatically bad. Ask what the CPU is doing (`%usr` vs `%sys`) and whether the run queue is growing.

## Tool selection

- Snapshot of processes: `ps`
- Live CPU/memory hogs: `top` (press `1` for per-CPU, Shift-M for memory)
- Available RAM: `free -h` — use **available**, not free
- Run queue, swap, wait: `vmstat 1` — ignore first line (boot average). `r` greater than CPU count = CPU saturation. Sustained `si`/`so` = RAM pressure. `wa` = disk stall
- Per-core `%usr`/`%sys`: `mpstat -P ALL 1`
- Disk IOPS / await: `iostat -xz 1`
- One process over time: `pidstat -p PID 1`
- History / what happened at 14:00: `sar` (sysstat timer writes `/var/log/sa/`)
- Unified metrics, remote, replay: PCP (`pmcd`/`pmlogger`, `pcp dstat`, `pmrep`)
- CPU / cache / TLB: `perf stat`, `perf record`/`report` (last-level cache = LLC)
- Hardware map: `lscpu`, `lstopo`, `numactl --hardware`, `dmidecode`
- NIC rings / offload / drops: `ethtool -g` `-k` `-S` `-i`
- Active TuneD profile: `tuned-adm active` / `tuned-adm verify`
- Storage proof before Oracle: `fio` with `--direct=1`, `libaio`, 8k random (Oracle block), not page cache

Install path: `sysstat` for `mpstat`/`iostat`/`sar`/`pidstat`. PCP when you need archives and Grafana, not as a replacement for first-look sysstat.

## Persistence: TuneD vs one-off sysctl

- `echo` to `/proc/sys` or `sysctl -w`: does not survive reboot — test only
- `/etc/sysctl.d/*.conf` plus `sysctl --system`: survives reboot — single knobs, can fight TuneD
- TuneD profile (`tuned-adm profile ...`): survives reboot — preferred bundle for a workload
- Kernel cmdline (`grubby`): HugePages, `numa=off`, `isolcpus`, `processor.max_cstate`
- `/etc/modprobe.d/`: NIC driver params

Rules:

- Never edit `/usr/lib/tuned/profiles/` or `/usr/lib/sysctl.d/`. Override in `/etc/tuned/profiles/` and `/etc/sysctl.d/`.
- Custom profile: `/etc/tuned/profiles/<name>/tuned.conf` with `include=` a parent (often `throughput-performance` or `oracle`), then `[sysctl]`, `[cpu]`, `[disk]`, `[net]`.
- `tuned-adm verify` after apply. Dynamic TuneD is off by default — keep it off on databases (predictability).
- Ansible `kernel_settings` (RHEL System Roles) writes a TuneD profile and is additive: removing a var from the playbook does not unset it on the host.

## Layers

### CPU

- Scheduler classes: deadline > real-time (`SCHED_FIFO`/`SCHED_RR`) > fair (`SCHED_OTHER`, EEVDF on RHEL 10) > idle.
- Run queue = tasks waiting for a core. Saturation is `r` / load vs CPU count, not "%CPU is high".
- Nice: -20 more CPU, +19 less. Real-time always beats nice -20. Do not put apps above RT priority ~49 (IRQ territory). RT throttling (~95% of a period) is the starvation safety net — do not set `kernel.sched_rt_runtime_us=-1` on Oracle hosts.
- Pin for cache/NUMA locality (`CPUAffinity`, cpusets, `tuna`). Isolation (`tuned-profiles-cpu-partitioning`, `isolcpus`/`nohz_full`) is for latency-critical apps, not typical OLTP Oracle.
- Governors: `performance` = stay high clock; `schedutil`/`ondemand` = save power, add latency. Pair with C-state policy.

### Memory

- Page cache = file-backed, reclaimable (`buff/cache`). Anonymous pages = process heap / SGA not on hugetlb / PGA — only freed by exit, reclaim, or swap.
- `free`: worry when **available** is low and swap is active.
- HugePages (static HugeTLB): lock RAM for SGA; not swappable; fewer TLB misses. Size = SGA / 2 MiB. Unused HugePages are wasted — they cannot become PGA or page cache.
- THP: disable for Oracle (`never`). Compaction causes latency spikes.
- `vm.swappiness`: low (Oracle profile ~10) prefers dropping page cache over swapping anonymous. `0` does not disable swap.
- Dirty pages: Oracle profile flushes early (`vm.dirty_background_ratio=3`) with a high hard stop (`vm.dirty_ratio=40`) so writes trickle instead of stall.
- Overcommit: default `vm.overcommit_memory=0` is normal for Oracle if HugePages plus PGA limits are sized. Mode `2` is extra safety (alloc fails instead of OOM) only if the commit limit is calculated.
- Never `drop_caches` in production. Kernel already reclaims cold page cache. Dropping everything causes a disk-read stampede and does not free Oracle PGA/SGA.

### I/O (only what the chat covered)

- `iostat -xz`: `await`, `%util`, queue. High `wa` in `vmstat` = disk, not CPU shortage.
- Scheduler: deadline / `mq-deadline` on physical disks (Oracle); `none`/`noop` on VMs and NVMe (hypervisor or device already queues).
- FIO: prove storage before blaming Oracle. `--direct=1` or you measure RAM.

### Network

Three buffer levels — tune all three or the lowest one drops:

1. NIC ring — `ethtool -g` / `-G`. Drops: `ethtool -S` and grep drop counters.
2. Kernel — `net.core.rmem_max`/`wmem_max` (ceiling), `net.ipv4.tcp_rmem`/`tcp_wmem` (min/default/max), `net.core.netdev_max_backlog`. TCP max cannot exceed core max. `net.ipv4.tcp_mem` is in pages.
3. Application — Oracle `sqlnet.ora`: `RECV_BUF_SIZE`, `SEND_BUF_SIZE`, `SDU`, `TCP.NODELAY=YES`. Oracle silently gets `wmem_max` if it asks for more.

Size to BDP (`bandwidth x RTT`), not as big as possible (bufferbloat). Jumbo MTU 9000 only if every hop agrees (isolated RAC interconnect / storage net).

C-states: deep sleep (C6+) adds wakeup latency and jitter. Symptom: idle latency worse than busy. Limit with TuneD `force_latency` or `processor.max_cstate`. Offload (TSO/GRO) on unless diagnosing a bug.

### Kernel / TuneD

Oracle path: `dnf install tuned-profiles-oracle && tuned-adm profile oracle` (KCS recommended), then a custom child profile for site-specific HugePages/sysctls. Manual sysctl list is the fallback, not the first choice.

## Oracle-on-RHEL defaults (from the chat plus KCS walkthrough)

- Profile: `tuned-profiles-oracle` / `oracle`.
- HugePages for SGA; THP `never`.
- `vm.swappiness=10`; Oracle dirty_* as in the profile.
- `kernel.numa_balancing=0`. Large SGA spanning sockets: disabling NUMA (`numa=off` plus BIOS node interleave) is a valid DBA choice — consistent average latency beats sometimes local, sometimes remote. Confirm `numactl --hardware` shows one node. Cost: lose true local-memory speed.
- Shared memory (`kernel.shmmax`/`kernel.shmall`), semaphores (`kernel.sem`), file descriptors for `oracle`.
- I/O scheduler as above.
- Cap PGA: `PGA_AGGREGATE_TARGET` and `PGA_AGGREGATE_LIMIT`. SGA in HugePages does not cap PGA.
- Do not shrink HugePages to "free RAM" without recapping PGA — leftover RAM becomes anonymous PGA, not available.

## Argue %sys vs %usr vs run queue (SBI UPI-class)

Do not treat "CPU is high" as one finding.

1. `mpstat -P ALL`: `%usr` = application; `%sys` = kernel (syscalls, locking, networking, interrupts, reclaim). High `%sys` is not "need more cores" until you know which kernel work.
2. Run queue (`vmstat r`, `sar -q`): if `%usr+%sys` is high but `r` stays at or below CPU count, the machine is busy but keeping up. If `r` is much greater than CPU count, it is saturated — extra work waits. UPI-style latency SLAs break on saturation and `%sys`, not on a pretty `%idle`.
3. Balance: one core 100% / others idle = not a capacity problem; affinity or single-thread bottleneck (`mpstat`).
4. Steal (`st`) only on VMs. `wa` is disk, counted in CPU stats but not compute demand.
5. Architect follow-up: same picture on every RAC/app node? Capacity headroom vs one noisy neighbor vs kernel/network tax (`%sys` from softirqs, small packets, C-state jitter).

## Worked pattern: 900 GB available to 0 (customer OLTP)

Facts from the chat (do not generalize as "Linux ate memory"):

- Before test: ~900 GB `available`. During OLTP: `available` went to 0.
- `drop_caches` did nothing useful.
- DBA cut HugePages 1.07 TB (550k) to ~312 GB (160k); ~94% of remaining HugePages in use.
- Hundreds of Oracle processes ~321-325 MB RSS; cumulative RSS ~2.8 TiB; PGA estimated ~2.47 TB in anonymous memory.
- Same window: `No buffer space available` (kernel could not allocate socket buffers).

Chain: shrink HugePages, SGA/buffer cache shrinks, more disk plus more sort/hash in PGA, PGA (anonymous) fills regular RAM, page cache already reclaimed, `available=0`, `drop_caches` cannot touch PGA, network alloc fails.

Fix class: restore HugePages for SGA, cap PGA, never drop caches in prod. Symptom was memory, not NIC.

## How to apply

1. State the goal (latency vs throughput) and the workload.
2. USE: errors, then utilization, then saturation on CPU, memory, I/O, network.
3. Pick tools from the list; baseline before change.
4. Prefer TuneD custom profiles for persistence.
5. For Oracle: check profile, HugePages vs THP, NUMA policy, swappiness, PGA limits, three-level buffers, scheduler — consistently on every node.
6. If a chapter was skipped in the RH442 chat, say so and do not fake course content.
