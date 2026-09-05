# Storage Checks

## Multipath & Devices

| Check | sosreport Path |
|---|---|
| Multipath device count | `sos_commands/multipath/multipath_-ll` or `sos_commands/devicemapper/multipath_-v4_-ll` |
| Multipath path health | same — count active/failed/ghost paths |
| I/O scheduler | `sys/block/*/queue/scheduler` |
| Filesystem layout | `df` output in `sos_commands/filesys/` |

## Capacity & Sizing

| Check | Calculation |
|---|---|
| HugePages reservation | `nr_hugepages × 2 MB` |
| memlock adequacy | `memlock (KB) >= nr_hugepages × 2048`? |
| Remaining RAM | `MemTotal − HugePages reservation` |
| Swap ratio | Swap relative to non-HugePages RAM |
| Port range capacity | `upper − lower` of ip_local_port_range |
| File descriptor headroom | nofile vs expected process count |

## Test / Production Readiness

| Check | Detection | Impact if Missing |
|---|---|---|
| sysstat installed + collecting | `installed-rpms` + `var/log/sa/` has files | No OS perf data |
| kdump configured | kexec-tools installed + `kdump.conf` exists | No crash dump |
| dnf-automatic / auto-updates | Enabled timer or cron | Patch mid-test risk |
| AV/endpoint agents | fapolicyd, clamd, falcon-sensor, TrendMicro in rpms/ps | I/O distortion |
| firewalld state | Active or inactive | May block app ports |
| Subscription status | `sos_commands/subscription_manager/` | Cannot patch |
