# AAP SSA Reference Index

Authoritative Chinese role handbook (pack-local): [role-handbook-zh.md](role-handbook-zh.md).  
Enterprise use-case catalog (EUC-01…14, APAC): [enterprise-use-cases.md](enterprise-use-cases.md).

---

## Role at a glance

| Item | Value |
|------|-------|
| Title | AAP Specialist Solution Architect (SSA) |
| Organization | Technical Sales BU |
| Scope | Lead to Cash |
| Region | Mainland · Hong Kong · Taiwan · APAC enablement |
| Customers | Commercial — manufacturing, financial, government & enterprise, multinationals |

**Mission**: Act as solution architect at the customer interface; identify automation pain points; drive POC → commercial → delivery closed loop.

---

## Product in one line

**AAP** = enterprise Ansible automation platform: RBAC, credential vaulting, audit, Automation Hub, Execution Environments, Collections, EDA. Replaces scattered scripts and self-hosted AWX.

---

## Solutions owned

### Core (deep assets)

| # | Solution | What to remember |
|---|----------|------------------|
| 1 | **AAP Starter Pack v3.0** | 40+ Job Templates — "App Store inside AAP". Linux 01–33 · Windows 81–85 · VMware 101–103. GA dir: `02_AAP_Starter_Pack/10_GA_version_APAC_AAP_Starter_Pack-main/` |
| 2 | **AIOps Solution** | RHEL + AAP + EDA + observability/ChatOps stack. Repo: https://github.com/adiooooos/AIOps_Enterprise_Practices · UC1 health · UC2 patch/HITL · UC3 self-heal · UC4 policy block |
| 3 | **AAP for Linux / Linux + Satellite** | Baseline, patching, RCA, app deploy; Satellite = content authority, AAP = governed execution |
| 4 | **AAP for Windows / VMware** | Windows 81–85 (WinRM agentless) · VMware 101–103 (provisioning / DR) |

### Enterprise plays (all in v1 — see EUC catalog)

Use [enterprise-use-cases.md](enterprise-use-cases.md) IDs in outputs. Capability narrative only (no invented Collection names).

| ID | Theme | APAC emphasis |
|----|-------|---------------|
| EUC-01 | Collections / Automation Hub / content governance | — |
| EUC-02 | Security & hardening (CIS/STIG/MLPS-oriented) | — |
| EUC-03 | Patch & vulnerability orchestration | — |
| EUC-04 | Credential & secrets hygiene | — |
| EUC-05 | Compliance evidence / audit trail | — |
| EUC-06 | Network automation | **Cisco · Arista** first |
| EUC-07 | Hybrid / multi-cloud ops | **Azure** + on-prem first |
| EUC-08 | Identity & access lifecycle | — |
| EUC-09 | OpenShift / container Day-2 | — |
| EUC-10 | Event-driven ops (EDA beyond AIOps kit) | — |
| EUC-11 | Windows estate unification | Starter Pack 81–85 |
| EUC-12 | VMware / virt lifecycle | Starter Pack 101–103 |
| EUC-13 | App / middleware standardized deploy | — |
| EUC-14 | GitOps + AAP execution governance | — |

---

## Competitive positioning cheatsheet

| vs | AAP advantage |
|----|---------------|
| Open-source Ansible / AWX | RBAC, audit, support, Hub-certified content, EE |
| Cloud-vendor orchestration | Hybrid-cloud unification, less lock-in |
| Tencent BlueKing | Agentless, lower security-review friction, RHEL-native |
| Scattered scripts | Central governance, visibility, compliance traceability |

---

## Related pack assets (self-contained)

| Type | Path |
|------|------|
| This Skill | `skills/aap-ssa/SKILL.md` |
| Sales nine-agent Rules | `skills/rules/*.mdc` |
| Sales Skill-format texts | `skills/sales/*.md` |
| Pack README | `skills/README.md` |
| Simulator / Excel / HTML | `9012_AAP_usecase_Simulator/` (parent) |

> When publishing to Google Drive, ship the **entire `skills/`** tree so relative links keep working.
