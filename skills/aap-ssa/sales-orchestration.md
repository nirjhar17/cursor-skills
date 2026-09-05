# Sales Nine-Agent Orchestration Playbook

This file defines how the AAP SSA Skill works with the agency-agents **Sales department's 9 Cursor Rules**.  
**Pack-local rule path** (Google Drive / enablement): [`../rules/*.mdc`](../rules/)  
(Upstream maintainer copy still lives in workspace `.cursor/rules/*.mdc` — re-sync before republishing.)

---

## Nine-agent mapping table

| # | Agent name | Cursor `@` mention | Rule file (pack) | Strengths | Typical AAP SSA use |
|---|------------|--------------------|------------------|-----------|---------------------|
| 1 | Outbound Strategist | `@outbound-strategist` | `../rules/outbound-strategist.mdc` | Signal-driven outbound, ICP, multi-channel outreach | Define AAP ICP (RHEL estate, MLPS, ops headcount pressure) and trigger signals |
| 2 | Discovery Coach | `@discovery-coach` | `../rules/discovery-coach.mdc` | SPIN / Gap Selling / Sandler | First-call / workshop question lists; surface open-source Ansible, credential, and compliance pain |
| 3 | Deal Strategist | `@deal-strategist` | `../rules/deal-strategist.mdc` | MEDDPICC, competitive positioning, win planning | Large-deal qualification, Xinchuang veto risk, buying-committee risk |
| 4 | Sales Engineer | `@sales-engineer` | `../rules/sales-engineer.mdc` | Demo, POC, battlecard | Starter Pack / EUC selection, FIA competitive comparison, POC success criteria |
| 5 | Proposal Strategist | `@proposal-strategist` | `../rules/proposal-strategist.mdc` | RFP, win themes, narrative structure | Core technical proposal chapters, differentiated value narrative |
| 6 | Pipeline Analyst | `@pipeline-analyst` | `../rules/pipeline-analyst.mdc` | Forecast, pipeline health, RevOps | Quarterly pipeline review, stage-stall diagnosis |
| 7 | Account Strategist | `@account-strategist` | `../rules/account-strategist.mdc` | Upsell, QBR, NRR | Expand AAP into RHEL accounts; EDA / AIOps phase two |
| 8 | Sales Coach | `@sales-coach` | `../rules/sales-coach.mdc` | Call coaching, pipeline review | Review Discovery calls; improve next-round questioning |
| 9 | Offer & Lead Gen Strategist | `@offer-lead-gen-strategist` | `../rules/offer-lead-gen-strategist.mdc` | Lead magnets, top-of-funnel Offer | AAP maturity-assessment Offer; whitepaper / workshop themes |

---

## Sales funnel × rule mapping

```
┌─────────────────────────────────────────────────────────────────┐
│  Top of Funnel                                                  │
│  @offer-lead-gen-strategist  →  Lead magnets / assessment Offer │
│  @outbound-strategist        →  ICP + outbound sequences        │
├─────────────────────────────────────────────────────────────────┤
│  Middle of Funnel                                               │
│  @discovery-coach            →  Discovery                        │
│  @sales-engineer             →  Demo / POC / battlecard         │
│  @deal-strategist            →  MEDDPICC / win planning         │
├─────────────────────────────────────────────────────────────────┤
│  Bottom of Funnel                                               │
│  @proposal-strategist        →  RFP / proposal                   │
│  @pipeline-analyst           →  Pipeline health / forecast      │
│  @sales-coach                →  Call and review coaching        │
├─────────────────────────────────────────────────────────────────┤
│  Post-Sale                                                      │
│  @account-strategist         →  Expand / QBR / stakeholder map  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fusion methods (Agent execution instructions)

When the `aap-ssa-en` (or primary `aap-ssa`) Skill is active, the Agent "invokes" the nine agents as follows:

### Method 1: In-skill fusion (recommended — user states the need only)

User describes the task without explicitly `@`-mentioning sales rules. The Agent should:

1. Use the task-routing table to decide which `.mdc` files to read
2. Use the `Read` tool for the full rule text or relevant sections
3. Generate content in that rule's **framework and deliverable format**, with the outer frame synthesized by **AAP SSA**

### Method 2: Explicit `@` stacking (power mode)

User includes multiple `@` mentions in the same turn, for example:

```
@outbound-strategist @discovery-coach @sales-engineer
[with aap-ssa skill] Design a full opportunity progression plan for a manufacturing RHEL customer
```

Honor the user's explicit `@` rules first; `aap-ssa` / `aap-ssa-en` owns sequencing and AAP solution-asset hooks.

### Method 3: Multi-turn progression (long opportunities)

Same opportunity across multiple turns; each turn focuses one stage. Prior-turn output becomes next-turn input:

| Turn | Suggested `@` | Input |
|------|---------------|-------|
| 1 | outbound + offer-lead-gen | Industry, region |
| 2 | discovery-coach | Turn-1 ICP |
| 3 | sales-engineer | Turn-2 pain list |
| 4 | deal-strategist | Turn-3 POC scope |
| 5 | proposal-strategist | Turn-4 MEDDPICC |

---

## AAP solution × Sales Agent hook matrix

| Customer pain | Preferred asset / EUC | Primary Sales Agent(s) |
|---------------|----------------------|------------------------|
| Scattered ops scripts, no audit | AAP platform + Starter Pack 01/06 · EUC-05 | sales-engineer, discovery-coach |
| No governed content / Collections | EUC-01 Hub + EE | sales-engineer, proposal-strategist |
| MLPS / CIS / STIG baseline drift | EUC-02 + Starter Pack compliance band | proposal-strategist, deal-strategist |
| Patch windows, CVEs, rollback | EUC-03 + Satellite + UC2 Simulator | sales-engineer, account-strategist |
| Shared passwords / secret sprawl | EUC-04 credential hygiene | discovery-coach, sales-engineer |
| Windows ops silo | EUC-11 · Starter Pack 81–85 | sales-engineer |
| VMware lifecycle | EUC-12 · Starter Pack 101–103 | sales-engineer |
| Alert fatigue, manual firefighting | EUC-10 · AIOps UC3 + EDA | sales-engineer, proposal-strategist |
| Financial HITL / policy block | AIOps UC2/UC4 · EUC-05 | deal-strategist, proposal-strategist |
| Network CLI snowflakes (Cisco / Arista) | EUC-06 | sales-engineer, discovery-coach |
| Azure + DC clickops / hybrid governance | EUC-07 | sales-engineer, proposal-strategist |
| Identity joiner-mover-leaver lag | EUC-08 | discovery-coach, deal-strategist |
| OpenShift Day-2 manual ops | EUC-09 | sales-engineer, account-strategist |
| Content / Collections chaos | EUC-01 | sales-engineer, proposal-strategist |
| Secrets in tickets / Git | EUC-04 | discovery-coach, sales-engineer |
| Expand AAP into RHEL estate | AAP for Linux + Account planning | account-strategist, outbound-strategist |

EUC definitions: [enterprise-use-cases.md](enterprise-use-cases.md).

---

## Full Playbook section length guidance

Avoid oversized single replies; emit by section:

| Section | Agent lens | Suggested length |
|---------|------------|------------------|
| Executive Summary | SSA synthesis | 150–250 words |
| Leads + Offer | Outbound + Lead Gen | 300–500 words |
| Discovery list | Discovery Coach | 15–25 questions |
| Technical plan | Sales Engineer | Demo outline + 2 scenarios + battlecard table |
| Qualification | Deal Strategist | MEDDPICC eight-dimension table |
| Bid narrative | Proposal Strategist | Win themes + 3 differentiators |
| Pipeline | Pipeline Analyst | Stage / risk / next step |
| Expansion | Account Strategist | 12-month land-expand path |

---

## Relationship to the SSA role handbook

| Document | Role |
|----------|------|
| [role-handbook-zh.md](role-handbook-zh.md) | **Who + What**: identity, solution catalog, competitive positioning (Chinese) |
| [enterprise-use-cases.md](enterprise-use-cases.md) | **What else**: enterprise EUC catalog beyond Starter Pack / AIOps (review draft) |
| This file | **How**: when to read which sales rule, how to chain them |
| [SKILL.md](SKILL.md) | **When**: triggers, output templates, prohibitions |
| [`../rules/`](../rules/) | **Methodologies**: Sales nine-agent rule bodies |
