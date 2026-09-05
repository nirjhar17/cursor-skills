# OS, Kernel, Memory, Sysctl, Limits & Time Sync Checks

## OS & Kernel

| Check | sosreport Path |
|---|---|
| RHEL version | `etc/redhat-release` |
| Kernel version | `proc/version` or `uname` |
| Boot parameters | `proc/cmdline` |
| SELinux | `etc/selinux/config` |
| tuned profile | `sos_commands/tuned/tuned-adm_active` |

## Memory

| Check | sosreport Path |
|---|---|
| Total RAM | `proc/meminfo` → MemTotal |
| Swap total | `proc/meminfo` → SwapTotal |
| Swap used | `proc/meminfo` → SwapFree vs SwapTotal |
| HugePages Total | `proc/meminfo` → HugePages_Total |
| HugePages Free | `proc/meminfo` → HugePages_Free |
| THP | `sys/kernel/mm/transparent_hugepage/enabled` |
| nr_hugepages | `proc/sys/vm/nr_hugepages` |

## Sysctl — VM

| Check | sosreport Path |
|---|---|
| swappiness | `proc/sys/vm/swappiness` |
| dirty_ratio | `proc/sys/vm/dirty_ratio` |
| dirty_background_ratio | `proc/sys/vm/dirty_background_ratio` |
| dirty_expire_centisecs | `proc/sys/vm/dirty_expire_centisecs` |
| dirty_writeback_centisecs | `proc/sys/vm/dirty_writeback_centisecs` |
| numa_balancing | `proc/sys/kernel/numa_balancing` |
| overcommit_memory | `proc/sys/vm/overcommit_memory` |
| min_free_kbytes | `proc/sys/vm/min_free_kbytes` |

## Sysctl — Kernel

| Check | sosreport Path |
|---|---|
| shmmax | `proc/sys/kernel/shmmax` |
| shmall | `proc/sys/kernel/shmall` |
| sem | `proc/sys/kernel/sem` |
| pid_max | `proc/sys/kernel/pid_max` |
| threads-max | `proc/sys/kernel/threads-max` |

## Sysctl — FS

| Check | sosreport Path |
|---|---|
| aio-max-nr | `proc/sys/fs/aio-max-nr` |
| file-max | `proc/sys/fs/file-max` |

## Limits

| Check | sosreport Path |
|---|---|
| nofile (key users) | `etc/security/limits.conf` + `etc/security/limits.d/*` |
| nproc (key users) | same |
| memlock (key users) | same |

## Time Sync

| Check | sosreport Path |
|---|---|
| chrony sources | `etc/chrony.conf` (server/pool lines) |
| chrony sync status | `sos_commands/chrony/chronyc_sources` |

## Key RPMs

| Check | sosreport Path |
|---|---|
| sysstat | `installed-rpms` |
| kexec-tools | `installed-rpms` |
| chrony | `installed-rpms` |
| tuned | `installed-rpms` |
