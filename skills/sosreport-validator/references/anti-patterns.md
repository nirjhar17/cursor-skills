# Anti-Pattern Detection

| Anti-Pattern | Detection | Severity |
|---|---|---|
| THP enabled on DB/memory-intensive hosts | `transparent_hugepage/enabled` not `[never]` | HIGH |
| HugePages allocated but unused | `HugePages_Free == HugePages_Total` | HIGH |
| NUMA balancing on | `numa_balancing != 0` | MEDIUM |
| Wrong tuned profile | Not matching workload (e.g., `balanced` on DB server) | MEDIUM |
| DHCP on parent with static VLAN child | NM profile shows `ipv4.method: auto` on parent, `manual` on child | HIGH |
| RHEL N-1 packages on RHEL N | Packages from older major release in `installed-rpms` | LOW |
| SELinux disabled without justification | `SELINUX=disabled` | LOW |
| Stale/large swap usage | SwapUsed > 1 GB on memory-rich host | MEDIUM |
| NIC ring buffer not maximized | Current ring buffer << max ring buffer | MEDIUM |
| Packet drops on active interfaces | Non-zero RxDrop or TxDrop on traffic-carrying NICs | HIGH |
| TCP buffer overruns | "pruned from receive queue" count > 0 | HIGH |
| No buffer space errors in logs | ENOBUFS (error 105) in journal/messages | CRITICAL |
| netdev_budget insufficient | xsos SOFTIRQ warning about budget | MEDIUM |
| Boot device timeout | `dev-mapper-*.device` timeout in journal | MEDIUM |
