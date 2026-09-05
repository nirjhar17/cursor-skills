---
name: sosreport-validator
description: >-
  General-purpose architect-level validation of RHEL sosreports for any Linux
  workload. Reads sosreport data from Red Hat supportshell (read-only), generates
  CSV comparison tables and summary reports locally. Use when reviewing multiple
  sosreports, validating OS-layer configuration across server groups, checking
  cross-node consistency, or preparing for performance testing sign-off.
compatibility: Requires Red Hat supportshell with xsos and Insights rules installed
metadata:
  author: njajodia
  version: "2.0"
---

# sosreport Validator — General Purpose

## Purpose

Validate OS-layer configuration across multiple sosreports for any RHEL workload. Focus is **cross-node consistency, network health, capacity verification, and anti-pattern detection** — not individual parameter correctness.

## Environment

- **Supportshell (read-only):** Run `xsos -a`, `cat`, `grep`, read files. Do NOT create files on supportshell.
- **Local machine:** All output artifacts (CSV, reports) created locally in the project directory.

## Tools Available on Supportshell

| Tool | Path | Purpose |
|---|---|---|
| xsos | `/usr/local/bin/xsos` | Quick full-system summary from sosreport |
| Insights | `/usr/share/analysis/insights/env/bin/activate` | Full Insights rule engine (venv with telemetry + shared + prodsec rules) |
| yank | system PATH | Download and extract sosreports by case number |

### xsos Usage

```bash
xsos -a /path/to/sosreport-dir
```

### Insights Usage

```bash
source /usr/share/analysis/insights/env/bin/activate
insights run -p telemetry.rules.plugins,shared_rules,prodsec /path/to/sosreport-dir
deactivate
```

**Do NOT install packages or clone repos on supportshell.** Use only what is already available.

## Inputs Required

1. **Case number** — for `yank` on supportshell
2. **Path to extracted sosreports** on supportshell
3. **Tier classification** — auto-detect from hostnames or ask user (e.g., DB vs APP, web vs backend, or single tier)

## Output

Per-tier CSV files and a summary report, created **locally**:

- `<tier>-sosreport-comparison.csv` — all nodes side by side
- `sosreport-validation-report.md` — findings, cross-tier alignment, prioritized issues

### CSV Format

```
Check,host01,host02,host03,...,MATCH,Red Hat Recommends,Status,Reference
RHEL version,9.7,9.7,9.7,...,YES,-,OK,-
Kernel,5.14.0-427,5.14.0-427,...,YES,-,OK,-
```

## Workflow

```
Task Progress:
- [ ] Step 0: Confirm sosreports on supportshell
- [ ] Step 1: Discover and classify nodes
- [ ] Step 2: Run xsos -a on one representative node per tier
- [ ] Step 3: Run Insights rules on one representative node per tier
- [ ] Step 4: Lens 1 — Consistency within each tier
- [ ] Step 5: Lens 2 — Cross-tier alignment
- [ ] Step 6: Lens 3 — Capacity and sizing
- [ ] Step 7: Lens 4 — Anti-patterns
- [ ] Step 8: Lens 5 — Test / production readiness
- [ ] Step 9: Generate CSV and summary report locally
```

### Step 0–1: Setup and Discovery

Verify sosreports are yanked and extracted. Classify hostnames into tiers. Flag missing nodes in sequences.

### Step 2–3: Automated Scans

Run `xsos -a` and `insights run` on one representative node per tier. Capture output. These provide a baseline and may surface issues the manual checks miss.

### Step 4: Lens 1 — Consistency Within Each Tier

Read the same value from every sosreport and compare. Flag any node that differs.

See [checks-os.md](references/checks-os.md) for OS, kernel, memory, sysctl, limits, and time sync checks.
See [checks-network.md](references/checks-network.md) for NIC, bonding, VLAN, NM, and traffic health checks.
See [checks-storage.md](references/checks-storage.md) for multipath, I/O scheduler, and filesystem checks.

### Step 5: Lens 2 — Cross-Tier Alignment

If multiple tiers exist, compare values that must align across tiers.

See the "Cross-Tier Network Alignment" section in [checks-network.md](references/checks-network.md).

### Step 6: Lens 3 — Capacity and Sizing

See the "Capacity & Sizing" section in [checks-storage.md](references/checks-storage.md).

### Step 7: Lens 4 — Anti-Patterns

See [anti-patterns.md](references/anti-patterns.md) for the full detection table with severity levels.

### Step 8: Lens 5 — Test / Production Readiness

See the "Test / Production Readiness" section in [checks-storage.md](references/checks-storage.md).

### Step 9: Generate Output

Create locally:

1. **Per-tier CSV** — one row per check, one column per server, MATCH/Status/Reference columns
2. **Summary report** — prioritized findings with KCS links where available

## Key Principles

1. **Look across, not into.** Compare nodes for consistency. Individual tuning is support scope.
2. **Verify everything against actual sosreport data.** Never assume or hallucinate values.
3. **No recommendations without explicit documentation.** If no Red Hat or vendor reference exists, mark as VERIFY.
4. **Network config is first-class.** Check NM profiles, parent/child interface conflicts, DHCP logs, bond config, and packet drops — not just sysctl values.
5. **Do not install anything on supportshell.** Use only pre-existing tools.
