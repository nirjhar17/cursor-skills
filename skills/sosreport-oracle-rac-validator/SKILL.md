---
name: sosreport-oracle-rac-validator
description: >-
  Holistic architect-level validation of sosreports for Oracle RAC on RHEL
  bare metal environments. Reads data from Red Hat supportshell (read-only),
  generates CSV comparison tables locally. Use when reviewing multiple
  sosreports at scale, validating Oracle RAC migration readiness, checking
  OS-layer configuration across DB and APP tiers, or preparing for
  performance testing sign-off.
---

# Oracle RAC sosreport Validator — Architect View

## Purpose

Validate OS-layer readiness across multiple sosreports for Oracle RAC on RHEL bare metal. The focus is **cross-node consistency and capacity verification**, not individual parameter correctness — that is support team scope.

## Environment

- **Supportshell (read-only):** Run `xsos -a`, `cat`, `grep`, read files inside sosreport directories. Do NOT create any files, scripts, or artifacts on supportshell.
- **Local machine:** All output artifacts (CSV files, reports) are created locally in the project directory.
- Agent reads supportshell terminal output from Cursor's terminal panel, then builds CSVs locally.

## When to Use

- Multiple sosreports from DB and/or APP nodes need reviewing
- HP-UX to RHEL migration validation
- Pre-performance-test OS sign-off
- Post-incident holistic environment review

## Inputs Required

1. **Case number** — sosreports yanked on supportshell
2. **Path to extracted sosreports** on supportshell
3. **Tier classification** — auto-detect from hostnames:
   - DB nodes: hostnames containing `db` (e.g., `cbtrdrdb01`)
   - APP nodes: hostnames containing `app` or `APP` (e.g., `DRNEWPRODAPP04`)
4. **Optional:** target connection count and SGA size for capacity math

## Output

Two CSV files created **locally** in the project directory:

- `db-nodes-comparison.csv` — all DB nodes side by side
- `app-nodes-comparison.csv` — all APP nodes side by side

Plus a summary report: `sosreport-validation-report.md`

### CSV Format

Leftmost column: check name. Each subsequent column: one server. Final column: MATCH (YES/NO).

```
Check,cbtrdrdb01,cbtrdrdb02,cbtrdrdb03,...,cbtrdrdb08,MATCH
RHEL version,9.7,9.7,9.7,...,9.7,YES
Kernel,5.14.0-427,5.14.0-427,5.14.0-427,...,5.14.0-427,YES
nr_hugepages,24578,24578,0,...,24578,NO
THP,[never],[never],[always],...,[never],NO
```

## Workflow

```
Task Progress:
- [ ] Step 0: Confirm sosreports yanked and extracted on supportshell
- [ ] Step 1: Discover and classify nodes
- [ ] Step 2: Lens 1 — Consistency within each tier
- [ ] Step 3: Lens 2 — Cross-tier alignment
- [ ] Step 4: Lens 3 — Capacity and sizing math
- [ ] Step 5: Lens 4 — Migration anti-patterns
- [ ] Step 6: Lens 5 — Test readiness
- [ ] Step 7: Generate CSV and summary report locally
```

### Step 0: Confirm sosreports on Supportshell

Verify sosreports are yanked and extracted. Read the yank output from terminal to get:
- List of all sosreport directories
- Base path on supportshell

### Step 1: Discover and Classify

From the yank listing, classify hostnames into DB and APP tiers. Report counts. Flag if any expected nodes are missing in the sequence.

### Step 2: Lens 1 — Consistency Within Each Tier

For each tier, read the same value from every sosreport on supportshell and compare. Run read-only commands like:

```bash
for sos in /path/to/sosreport-cbtrdrdb*/; do
  host=$(basename "$sos" | cut -d'-' -f2)
  val=$(cat "$sos/proc/sys/vm/nr_hugepages" 2>/dev/null)
  echo "$host: $val"
done
```

Use `xsos -a <sosreport_dir>` on one representative node per tier for a full baseline view. Then loop specific checks across all nodes.

**DB node checks:**

| Check | sosreport Path |
|---|---|
| RHEL version | `etc/redhat-release` |
| Kernel | `proc/version` |
| Total RAM | `proc/meminfo` (MemTotal) |
| Swap | `proc/meminfo` (SwapTotal) |
| HugePages Total | `proc/meminfo` (HugePages_Total) |
| HugePages Free | `proc/meminfo` (HugePages_Free) |
| HugePages Rsvd | `proc/meminfo` (HugePages_Rsvd) |
| THP | `sys/kernel/mm/transparent_hugepage/enabled` |
| tuned profile | `sos_commands/tuned/tuned-adm_active` |
| SELinux | `etc/selinux/config` |
| nr_hugepages | `proc/sys/vm/nr_hugepages` |
| shmmax | `proc/sys/kernel/shmmax` |
| shmall | `proc/sys/kernel/shmall` |
| sem | `proc/sys/kernel/sem` |
| swappiness | `proc/sys/vm/swappiness` |
| dirty_ratio | `proc/sys/vm/dirty_ratio` |
| dirty_background_ratio | `proc/sys/vm/dirty_background_ratio` |
| numa_balancing | `proc/sys/kernel/numa_balancing` |
| aio-max-nr | `proc/sys/fs/aio-max-nr` |
| file-max | `proc/sys/fs/file-max` |
| ip_local_port_range | `proc/sys/net/ipv4/ip_local_port_range` |
| rp_filter | `proc/sys/net/ipv4/conf/all/rp_filter` |
| memlock (oracle) | `etc/security/limits.conf` + `etc/security/limits.d/*` |
| nofile (oracle) | `etc/security/limits.conf` + `etc/security/limits.d/*` |
| nproc (oracle) | `etc/security/limits.conf` + `etc/security/limits.d/*` |
| chrony sources | `etc/chrony.conf` (server/pool lines) |
| I/O scheduler | `sys/block/*/queue/scheduler` |
| multipath devices | `sos_commands/multipath/multipath_-ll` (device count) |
| Key RPMs | `installed-rpms` (oracle, tuned, kexec-tools, sysstat, chrony) |
| /dev/shm usage | `proc/mounts` or `df` output for /dev/shm |

**APP node checks:**

Same OS basics (RHEL, kernel, RAM, tuned, SELinux, chrony) plus:

| Check | sosreport Path |
|---|---|
| tcp_keepalive_time | `proc/sys/net/ipv4/tcp_keepalive_time` |
| tcp_keepalive_intvl | `proc/sys/net/ipv4/tcp_keepalive_intvl` |
| tcp_keepalive_probes | `proc/sys/net/ipv4/tcp_keepalive_probes` |
| tcp_tw_reuse | `proc/sys/net/ipv4/tcp_tw_reuse` |
| somaxconn | `proc/sys/net/core/somaxconn` |
| ip_local_port_range | `proc/sys/net/ipv4/ip_local_port_range` |
| nofile (app user) | `etc/security/limits.conf` + `etc/security/limits.d/*` |
| nproc (app user) | `etc/security/limits.conf` + `etc/security/limits.d/*` |

### Step 3: Lens 2 — Cross-Tier Alignment

Compare values between APP and DB tiers that must align:

| Check | What to compare |
|---|---|
| Chrony NTP sources | Same servers on both tiers? |
| DNS resolv.conf | Same nameservers? |
| /etc/hosts | SCAN/VIP entries present and consistent? |
| nsswitch.conf | Same `hosts:` lookup order? |
| TCP keepalive (APP) | Aligned with DB listener/connection timeout? |
| ip_local_port_range (APP) | Enough ports for connection count to DB? |
| MTU | Same across interconnect interfaces on all nodes? |

Add cross-tier findings to the summary report.

### Step 4: Lens 3 — Capacity and Sizing Math

Calculate on DB nodes:

1. **HugePages reservation:** `nr_hugepages x 2MB`
2. **memlock check:** `memlock (KB) >= nr_hugepages x 2048`?
3. **Remaining RAM:** `MemTotal - HugePages reservation`
4. **Swap ratio:** deduct HugePages from RAM first
5. **Port range capacity:** `upper - lower` of ip_local_port_range
6. **File descriptors:** nofile vs expected load

Add capacity findings to summary report.

### Step 5: Lens 4 — Migration Anti-Patterns

Check all DB nodes:

| Anti-Pattern | Detection | Severity |
|---|---|---|
| THP enabled | `transparent_hugepage/enabled` not `[never]` | CRITICAL |
| HugePages unused | `HugePages_Free == HugePages_Total` (nobody using them) | CRITICAL |
| HugePages not configured | `nr_hugepages = 0` on DB node | CRITICAL |
| NUMA balancing on | `numa_balancing != 0` | HIGH |
| oracle-database-preinstall missing | not in installed-rpms | HIGH |
| tuned not oracle | profile not `oracle` or `throughput-performance` | HIGH |
| /dev/shm heavy use | large tmpfs at /dev/shm suggests AMM active | HIGH |
| Wrong I/O scheduler | default scheduler on DB storage devices | MEDIUM |

### Step 6: Lens 5 — Test Readiness

Check all nodes:

| Check | Detection | Impact if Missing |
|---|---|---|
| sysstat installed | in installed-rpms | No OS perf data |
| sar data present | `var/log/sa/` has files | Cannot correlate OS metrics |
| kdump configured | kexec-tools installed + kdump.conf exists | No crash dump |
| dnf-automatic off | no enabled timer | Patch mid-test breaks results |
| AV/endpoint agents | fapolicyd, clamd, falcon-sensor in rpms | I/O distortion |
| firewalld | active or not | May block Oracle ports |

### Step 7: Generate Output Locally

Create three files in the project directory:

1. **`db-nodes-comparison.csv`** — DB tier comparison table
2. **`app-nodes-comparison.csv`** — APP tier comparison table
3. **`sosreport-validation-report.md`** — summary with cross-tier alignment, capacity math, anti-patterns, test readiness, and prioritized recommendations

## Key Principle

> You look **across**, not **into**. Support looks into individual values. The architect looks across all nodes for consistency, alignment, capacity, and risk.

## Additional Resources

- For sosreport path edge cases, see [reference.md](reference.md)
