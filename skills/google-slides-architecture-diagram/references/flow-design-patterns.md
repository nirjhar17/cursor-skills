# Flow Design Patterns (Google Slides)

Adapted from the interactive architecture-diagram skill for static slides and storyboards.

## Topology

Place nodes by **direction of data**, not by team ownership.

```
[Operator/UI] → [Control CRs] → [Cluster agents] → [PVC / data]
                                            ↘ [Replication repo]
```

### Five-zone canvas (diagram area inside content zone)

| Zone | X% | Occupants |
|---|---|---|
| Entry | 0–15 | Operator, UI |
| Edge / control | 15–40 | Controllers, plans, cluster/storage CRs |
| Core | 40–65 | Velero, app, migration runner |
| Data plane | 65–85 | PVC old/new |
| Backing store | 85–100 | S3 / external systems |

Vertical: mainline center; side concerns above/below; one-shot jobs in a corner.

## Flows vs steps vs modes

- **Flow** = user-meaningful journey ("Storage class conversion", "Stage then cutover")
- **Step** = one handoff ("MigPlan → MigCluster refers to")
- **Mode** = same journey, different path shape ("direct" vs "indirect")

### Is this a flow?

- ✅ Named after a goal with start and end → flow
- ❌ Sub-step of a bigger story → step
- ❌ Same shape with different parameter → same flow + mode/chips

### Step count

3–9 steps per flow. Each step description answers: what happened, why (if non-obvious), what’s worth noting.

## Slides-specific layout

- Lock node `(x_pct, y_pct)` for all storyboard slides
- Put step narrative in a **callout panel** (right 2.2″ or bottom 0.55″), not on wires
- Wire labels: one short verb (`creates`, `targets`, `data`) — never a sentence on the arrow
- If labels collide, drop arrow text and keep the callout only

## Mode slides

Same nodes and positions. Change:

- Which wires are emphasized
- Callout title (`Direct path` vs `Indirect path`)
- Optional subtitle chips (latency, prerequisites)

If topology changes (different services), build a second planning spec / diagram.
