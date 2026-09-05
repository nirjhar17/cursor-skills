---
name: vmware-to-openshift-framework
description: >-
  Build a Day 2 Operational Confidence Framework for VMware administrators
  managing OpenShift Virtualization workloads after migration. Use when the user
  mentions VMware Artifact, knowledge pipeline, knowledge snapshots, Day 2
  confidence workshop, VMware-to-OpenShift adoption, concept mapping, operational
  readiness scorecard, or refers to course extracts (DO156, DO256, DO346, DO432).
---

# VMware-to-OpenShift Day 2 Confidence Framework

## Objective

Build a reusable **Day 2 Operational Confidence Framework** for VMware administrators who have migrated their virtualization workloads to OpenShift Virtualization. The framework gives these admins confidence to operate, troubleshoot, and optimize their VM workloads on OpenShift in production.

This is **not** about any single OpenShift distribution (not ROSA-specific, not bare-metal-specific). It targets OpenShift Virtualization on any deployment model.

## The Problem Being Solved

VMware admins are skilled operators, but their mental model is built around vSphere, vCenter, vMotion, NSX, datastores, and VMDK. After migration to OpenShift Virtualization, the concepts still exist but are named differently and behave differently. The confidence gap is real — Day 1 migration can be handled by engineers, but Day 2 operations (patching, scaling, troubleshooting, observing) is where admins feel lost and where adoption fails quietly.

## Knowledge Pipeline

The framework is built by synthesizing three authoritative input sources into a consolidated knowledge base, then producing final deliverables from that synthesis.

### Three Input Sources (Snapshots)

| # | Source | Purpose |
|---|--------|---------|
| 01 | ROSA Best Practices PDF (Red Hat, Mar 2023) | General OpenShift best practices as a baseline reference |
| 02 | Red Hat Virtualization Courses (DO156, DO256, DO346, DO432) | Hands-on operational knowledge, lab patterns, VMware-to-OpenShift feature mapping |
| 03 | Red Hat Official Documentation | Fill remaining gaps not covered by courses or the best practices PDF |
| 04 | Real-World Consulting Engagement HLD (sanitized) | Migration benchmarks, workload classification, Migration Factory methodology, production recommendations |
| 05 | Adoption Maturity Model + Field Engineering Patterns | 5-level maturity ladder, GitOps lifecycle maturity, MTV+ acceleration, large-scale migration patterns, networking best practices |
| 06 | OpenShift Virtualization Tuning & Scaling Guide (KCS 6994974) | Cluster scaling (etcd, MCP, scheduling), virt control plane highBurst, migration tuning (multifd, postCopy, autoConverge), CPU/NUMA/hugepage pinning, IOThread policies, VolumeSnapshot cloning, Windows Hyper-V enlightenments |

### Final Deliverables

| # | Artifact | File | Purpose |
|---|----------|------|---------|
| 1 | Rosetta Stone (Concept Mapping) | `concept-mapping/rosetta-stone.md` | VMware → OpenShift concept lookup across compute, networking, storage, operations, migration, backup, security, automation, monitoring |
| 2 | Operational Readiness Scorecard | `checklist/operational-readiness-scorecard.md` | 5-level maturity assessment (Initial→Innovator) across 9 domains with checkable items, metrics, and training recommendations |
| 3 | Networking Decision Guide | `networking-guide/networking-decision-guide.md` | Architecture decisions (br-ex, bonding, VLANs, load balancing), do's/don'ts, YAML examples, pitfall checklist |
| 4 | Migration Planning Calculator | `migration-calculator/migration-planning-calculator.md` | Workload classification, migration time benchmarks, FTE models (conservative vs aggressive), MTV+ acceleration, risk factors |

## Working Directory

All files live under:

```
VMware Artifact/
├── README.md
└── knowledge-snapshots/
    ├── snapshot-01-rosa-best-practices.md
    ├── snapshot-02-rh-courses.md
    ├── snapshot-02a-do156-course.md
    ├── snapshot-02b-do256-course.md
    ├── snapshot-02c-do346-course.md
    ├── snapshot-02d-do432-course.md
    ├── snapshot-05-maturity-model-and-field-patterns.md
    ├── snapshot-06-tuning-scaling-guide.md
    ├── veterans-affairs-vma.txt
    ├── do156-4.18-raw-extract.txt
    ├── do256-4.18-raw-extract.txt
    ├── do346-4.16-raw-extract.txt
    └── do432-2.13-raw-extract.txt
```

## How to Resume This Work

1. Read this skill and the `VMware Artifact/README.md`
2. Check which snapshots are complete vs pending
3. If the user provides new source material (docs, course pages), create the next snapshot
4. When all three input sources are captured, begin cross-referencing and building final artifacts

## Key Domain Knowledge

### Courses Extracted (Snapshot 02)

- **DO156** — OpenShift Virtualization Administration I: VM basics, creation, networking, storage fundamentals
- **DO256** — OpenShift Virtualization Administration II: Auth, RBAC, advanced networking, MTV migration, OADP backup/restore, HA, scheduling, fencing
- **DO346** — Migrating VMs to OpenShift Virtualization: Full MTV lifecycle, VDDK image, VMware CBT, virt-v2v driver conversion, Ansible AAP automation
- **DO432 Ch6** — Multicluster VM Management with RHACM: GitOps operator deployment, governance policies, Argo CD ApplicationSet for VMs across clusters

### Core VMware-to-OpenShift Concept Map (reference, not exhaustive)

- vCenter → OpenShift Web Console / oc CLI
- ESXi Host → OpenShift Worker Node (KVM)
- VMDK → PVC (wrapped in Data Volume)
- Datastore → Storage Class
- vSAN / NFS Datastore → ODF/Ceph (RWX required for live migration)
- vSwitch / dvSwitch → OVN-Kubernetes / Linux Bridge
- NSX-T → OVN-Kubernetes + Network Policies
- VMware Tools → QEMU Guest Agent
- vMotion → Live Migration (requires RWX storage)
- DRS → Descheduler Operator
- VMXNET3 / PVSCSI → virtio-net / virtio-blk (virt-v2v converts automatically)
- CBT snapshots → MTV warm migration with CBT
- vRealize Orchestrator → Ansible Automation Platform
- Host Profiles → RHACM Governance Policies
- vCenter Tags → OpenShift Labels

### Key Technical Areas for Day 2

- Authentication and RBAC for VM namespaces
- Networking: pod network, secondary networks (Multus, SR-IOV, NMState)
- Storage: PV/PVC, Data Volumes, storage profiles, RWX for live migration
- Migration: MTV operator, Provider/NetworkMap/StorageMap/Plan/Migration CRs
- Backup and restore: OADP, Velero, Data Mover
- High availability: health probes, PDB, node maintenance, fencing (SNR, FAR, MDR)
- Scheduling: node selectors, affinity/anti-affinity, taints/tolerations, descheduler
- Monitoring and alerting: Prometheus, Alertmanager, VM-specific metrics
- Automation: Ansible AAP, GitOps with Argo CD
- Multi-cluster: RHACM policies, ApplicationSets

## Workflow for Building Snapshots

When the user provides new source material:

1. Extract content (if from Red Hat Learning portal, use osascript + Chrome automation to click through pages)
2. Save raw extract as `<course>-<version>-raw-extract.txt`
3. Create structured snapshot as `snapshot-<id>-<name>.md` with:
   - Course/source metadata
   - Chapter-by-chapter structured summary
   - VMware-to-OpenShift feature mapping where applicable
   - Cross-reference table showing what this snapshot adds vs previous snapshots
   - Identified gaps for remaining snapshots
4. Update `README.md` snapshot table

## Workflow for Building Final Artifacts

When all snapshots are complete:

1. Read all snapshot files to build a unified knowledge graph
2. Identify high-confidence items validated across multiple sources
3. Identify gaps that remain even after all three sources
4. Build the three final deliverables, referencing specific snapshots as evidence
5. Save final artifacts under `VMware Artifact/concept-mapping/`, `VMware Artifact/checklist/`, `VMware Artifact/networking-guide/`, and `VMware Artifact/migration-calculator/`
