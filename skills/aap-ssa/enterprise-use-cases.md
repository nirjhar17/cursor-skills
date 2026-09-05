# AAP Enterprise Use-Case Catalog (APAC SSA)

> **Status**: Approved for APAC enablement pack (9012) — capability narrative only.  
> **Purpose**: Expand `aap-ssa` beyond Starter Pack + AIOps four UCs so SSP/SSA can map enterprise automation plays.  
> **Language**: English for APAC delivery. Chinese role depth (maintainer review): [role-handbook-zh.md](role-handbook-zh.md).  
> **Content rule**: Capability + outcome language only. Do **not** invent SKUs, certified Collection names, or unsupported integrations. Named product examples may be added later by the owner.  
> **Scope**: EUC-01…14 all in v1.  
> **Vendor emphasis (APAC)**: Network — **Cisco**, **Arista**; Cloud — **Azure** (with on-prem / hybrid). Other vendors = “same governance pattern” unless owner adds them.

When SSA outputs cite a use case, prefer IDs below (`EUC-*`) plus a concrete Starter Pack / AIOps / Simulator asset when available.

---

## How to use this catalog

1. Discovery: map pain → one primary `EUC-*` (+ optional secondary).
2. Technical: pick demo asset (Starter Pack JT / AIOps UC / Simulator HTML) or a **platform + one golden path** POC if no local artifact yet.
3. Proposal: win theme from **Outcome** + **AAP differentiator** — not feature lists.
4. Never promise a named Collection / Hub package unless the owner has added it to this file.

---

## EUC index

| ID | Theme | Typical buyer pain | Primary AAP hooks |
|----|-------|--------------------|-------------------|
| EUC-01 | Content & Collections governance | Playbooks scattered; no content lifecycle | Automation Hub, EE, Collections (capability) |
| EUC-02 | Security & hardening automation | CIS/STIG/MLPS drift; manual audits | Baseline Workflows, audit, vaulting |
| EUC-03 | Patch & vulnerability orchestration | CVE windows; no rollback story | Workflow + content source + HITL |
| EUC-04 | Credential & secrets hygiene | Shared passwords; ticket sprawl | Credential types, RBAC, rotation plays |
| EUC-05 | Compliance evidence / audit trail | “Show who ran what” for regulators | Job history, RBAC, approvals |
| EUC-06 | Network automation | Multi-vendor CLI snowflakes | Network ops under AAP governance — **Cisco / Arista** first |
| EUC-07 | Hybrid / multi-cloud ops | Cloud consoles ≠ on-prem process | Unified control plane — **Azure** + DC first |
| EUC-08 | Identity & access lifecycle | Joiner-mover-leaver ticket lag | IdM/AD/SSO-oriented orchestration |
| EUC-09 | OpenShift / container Day-2 | Cluster ops still manual | AAP + OCP Day-2 patterns |
| EUC-10 | Event-driven ops (beyond AIOps kit) | Alert → chat → human only | EDA rulebooks + AAP actions |
| EUC-11 | Windows estate unification | Windows silo vs Linux automation | WinRM agentless + same RBAC |
| EUC-12 | VMware / virt lifecycle | Provision/DR outside change control | vSphere JTs + approval/audit |
| EUC-13 | App / middleware standardized deploy | Snowflake installs | Reusable deploy Workflows |
| EUC-14 | GitOps + AAP execution | Git is source; runtime lacks governance | SCM projects + RBAC + EE |

**Deep assets elsewhere (link, don’t duplicate):**

| Theme | Where |
|-------|--------|
| Starter Pack Linux 01–33 / Windows 81–85 / VMware 101–103 | [reference.md](reference.md), [role-handbook-zh.md](role-handbook-zh.md) |
| AIOps UC1–UC4 | [reference.md](reference.md), AIOps repo |

---

## EUC-01 — Content & Collections governance

| | |
|--|--|
| **Outcome** | Teams consume **governed** automation content instead of copy-paste roles. |
| **Story** | Content lifecycle: author → review → publish → consume via Job Templates on pinned Execution Environments. Collections (and roles) versioned like application packages. Private Hub for air-gapped / regulated estates. |
| **Discovery probes** | Where do playbooks live today? Who certifies them? How do you promote sandbox → prod? Offline / air-gap needs? |
| **Differentiator vs AWX/scripts** | Hub + EE + support lifecycle — not “YAML on a jump host”. |
| **Demo angle** | Content → Job Template → EE; contrast with unmanaged laptop Git clone. |
| **Assets** | Capability narrative only until owner adds named Hub/Collection examples. |

---

## EUC-02 — Security & hardening automation

| | |
|--|--|
| **Outcome** | Baseline drift detected and remediated with **evidence**, not spreadsheets. |
| **Story** | CIS / STIG / MLPS-oriented configuration as code; scheduled scan + remediate Workflow; exceptions via approval. |
| **Discovery probes** | Which baseline standard? Audit frequency? Who owns exceptions? |
| **Differentiator** | Agentless reach + credential vaulting + job audit for security boards. |
| **Demo angle** | Drift signal → remediate Job → Job output as evidence pack. |
| **Assets** | Starter Pack compliance-oriented Linux scenarios; AIOps UC4 for “unsafe automation blocked” story. |

---

## EUC-03 — Patch & vulnerability orchestration

| | |
|--|--|
| **Outcome** | CVE → batch → maintain window → health check → **rollback** under change control. |
| **Story** | Content authority (e.g. Satellite / repos) + AAP Workflow orchestration + optional HITL. |
| **Discovery probes** | Patch SLA? Rollback practice? How do you prove completion to risk? |
| **Differentiator** | Orchestration + audit + HITL — not “yum update” scripts. |
| **Demo angle** | Gold Simulator UC2 (Success + Rollback) + ChatOps outputs. |
| **Assets** | `AAP_UC2_Pathing_management.html`; Starter Pack patch scenarios; Linux + Satellite joint story. |

---

## EUC-04 — Credential & secrets hygiene

| | |
|--|--|
| **Outcome** | No shared root passwords in tickets; least-privilege machine creds under RBAC. |
| **Story** | Credential objects, Org/Team RBAC, optional external vault pattern; rotation / revoke plays. |
| **Discovery probes** | How are SSH / WinRM / cloud keys distributed? Who can see prod secrets? |
| **Differentiator** | Central credential custody vs plaintext in Git / tickets. |
| **Demo angle** | Credential used by Job without revealing secret; RBAC deny for unauthorized Team. |
| **Assets** | Capability narrative; owner may later list vault products by name. |

---

## EUC-05 — Compliance evidence / audit trail

| | |
|--|--|
| **Outcome** | Every automation run answers who / what / when / on which hosts / with which approval. |
| **Story** | Controller Job history + RBAC + approval nodes; exportable evidence for audit. |
| **Discovery probes** | Last audit finding on ops changes? Screenshots vs system of record? |
| **Differentiator** | Platform-grade trail vs ad-hoc terminal logs. |
| **Tied industries** | Financial, government, regulated manufacturing. |

---

## EUC-06 — Network automation (Cisco · Arista first)

| | |
|--|--|
| **Outcome** | Backup, compliance drift, and change windows for network devices under the **same** AAP RBAC / audit / approval model as compute. |
| **APAC vendor focus** | **Cisco** and **Arista** as primary discovery/demo narratives. Other vendors: same pattern when content exists — do not invent module lists. |
| **Story** | Inventory from a source of truth → backup / show-run capture → drift vs golden intent → change in maintain window with approval → evidence in Job history. |
| **Discovery probes** | Cisco vs Arista mix? CAB process? Who owns golden config? NetDevOps maturity (Git vs CLI culture)? |
| **Differentiator** | Network changes stop being “SSH heroics”; they become governed Jobs. |
| **Demo angle** | One golden path: backup + diff + approved change (lab or Simulator later). Prefer capability story until a portable demo artifact exists. |
| **Caveat** | Capability narrative only — no named network Collections until owner adds them. |

---

## EUC-07 — Hybrid / multi-cloud ops (Azure + on-prem first)

| | |
|--|--|
| **Outcome** | Same approval / RBAC / audit for **Azure** resource operations and on-prem DC ops. |
| **APAC cloud focus** | **Azure** first. Other clouds = same control-plane story when customer asks — do not over-build AWS/GCP/Alibaba narratives in v1 decks unless requested. |
| **Story** | AAP as hybrid control plane: reduce console clickops; bind cloud credentials; run env-promotion Workflows (dev → prod) with human gates. |
| **Discovery probes** | Azure landing zone / subscriptions? Who can click in portal today? Terraform/Bicep ownership vs Day-2 ops? |
| **Differentiator** | Governance across hybrid — not “replace every IaC tool”. |
| **Positioning line** | IaC may **define**; AAP **executes with enterprise controls** (who, where, approval, evidence). |
| **Caveat** | Capability narrative only — no named cloud Collections until owner adds them. |

---

## EUC-08 — Identity & access lifecycle

| | |
|--|--|
| **Outcome** | Joiner / mover / leaver and privileged access requests leave an **automation trail**. |
| **Story** | ITSM / IdM / AD / SSO signals → AAP Jobs for account, group, sudo/host-access patterns; optional HITL for privileged paths. |
| **Discovery probes** | Ticket SLA for access? Shared privileged accounts? Audit asks for access evidence? |
| **Differentiator** | Orchestrated lifecycle vs mailbox + manual AD clicks. |
| **Caveat** | AAP **orchestrates** access changes; it does not replace the IdP / IAM product. |

---

## EUC-09 — OpenShift / container Day-2

| | |
|--|--|
| **Outcome** | Cluster Day-2 tasks under AAP change control (users, projects, operator-assisted ops, backup/restore hooks — as customer scope allows). |
| **Story** | Complementary RH stack: OpenShift runs platforms; AAP standardizes **who can change what** across cluster and traditional estates. |
| **Discovery probes** | Day-1 vs Day-2 pain? Platform team vs app team split? Existing GitOps (Argo/ACM) — where does AAP add governance? |
| **Differentiator** | Same RBAC/audit plane as Linux/Windows/network — not a second snowflake toolchain. |
| **Caveat** | Day-2 automation story; do not oversell “AAP installs every cluster” unless scoped. |

---

## EUC-10 — Event-driven ops (EDA)

| | |
|--|--|
| **Outcome** | Alerts become **governed actions** (optional HITL), not only chat pages. |
| **Story** | Event streams → Rulebooks → AAP Job Templates. AIOps kit is the flagship demo; pattern also works with lighter stacks. |
| **Discovery probes** | Alert volume? Auto-remediation appetite vs approval culture? |
| **Assets** | AIOps UC1–UC4; EDA rulebooks in AIOps repo. |
| **Extend** | “Prometheus / Alertmanager / ITSM → AAP” without full AIOps stack when customer isn’t ready. |

---

## EUC-11 — Windows estate unification

| | |
|--|--|
| **Outcome** | Windows Server ops join the same automation governance as Linux. |
| **Story** | Agentless WinRM under AAP: services, IIS, software, package, Windows Update/KB — Starter Pack 81–85 as demo SKUs. |
| **Discovery probes** | Separate Windows tools today? Domain cred sprawl? Patch islands? |
| **Sell** | Unified control plane (RBAC / creds / audit) — not “we have five Windows playbooks”. |
| **Assets** | Starter Pack 81–85. |

---

## EUC-12 — VMware / virt lifecycle

| | |
|--|--|
| **Outcome** | VM provision / DR steps sit inside change control and audit — same plane as OS automation. |
| **Story** | vSphere automation via AAP Workflows; Starter Pack 101–103 as demo SKUs. |
| **Discovery probes** | Who provisions VMs? DR drill frequency? Approval gaps? |
| **Sell** | Virt ops as governed products; ideal for manufacturing private cloud / financial VMware estates. |
| **Assets** | Starter Pack 101–103. |

---

## EUC-13 — App / middleware standardized deploy

| | |
|--|--|
| **Outcome** | Middleware / DB / web tier installs become Workflow products with env promotion. |
| **Discovery probes** | How many snowflake installs last quarter? Rollback story? |
| **Hook** | Starter Pack app-oriented Linux scenarios + customer-stack Workflow in POC. |
| **Differentiator** | Repeatable promote path with evidence vs tribal install notes. |

---

## EUC-14 — GitOps + AAP execution

| | |
|--|--|
| **Outcome** | Git remains source of truth; AAP provides **runtime governance** (who can run, where, which EE). |
| **Story** | SCM-backed Projects + version pin + RBAC — CI produces content; AAP runs it safely in prod. |
| **Differentiator vs CI-only** | Human approvals, inventory RBAC, credential custody, audit for production. |

---

## Competitive one-liners (reuse)

| vs | Line |
|----|------|
| AWX / DIY Ansible | Enterprise RBAC, Hub/EE, support, audit — content with a lifecycle. |
| Cloud orchestrators alone | Hybrid control plane (Azure + DC first); avoid lock-in for on-prem + cloud. |
| BlueKing / heavy agents | Agentless preference; often lower security-review friction. |
| Scripts / tribal knowledge | Productize ops as Job Templates with owners and evidence. |
| Network CLI heroes | Cisco/Arista changes as governed Jobs — backup, drift, approved change. |

---

## Owner backlog (optional later)

- Named Automation Hub / Collection examples for EUC-01 / 06 / 07  
- Exact Starter Pack JT IDs for EUC-02 compliance band  
- Vault / IdP product names for EUC-04  
- Portable network Simulator or lab steps for Cisco / Arista  
- Azure golden-path demo outline
