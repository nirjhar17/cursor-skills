# Visual States → Google Slides

## State table

| State | HTML skill | Slides overview | Slides storyboard step |
|---|---|---|---|
| active | Full ring + badge | Primary flow target slightly stronger | Strong fill + accent bar + callout focus |
| active-from | Soft ring | Source of primary hop normal-strong | Strong fill, no badge |
| participant | Near-full opacity | All primary-flow nodes visible | Normal fill |
| dimmed | 25% opacity | Unused alternate-mode nodes muted | Grey fill + muted subtitle |
| hidden | Invisible | Omit for that mode slide | Omit |

## Color guidance (light decks)

- Active hop wire: RH red or role accent at full strength
- Preview wires (rest of flow): same hue at ~40–50% / thinner stroke
- Dimmed nodes: gray fill `#F2F2F2`, text `#9B9B9B`, no accent bar (or gray bar)
- Callout panel: light tint matching active role; title bold; body 12pt

## Callout (“side panel”) copy

```
Step 3 of 6 · Cutover
PVC old SC → PVC new SC
Workloads keep the same namespace; storage class changes when cutover runs.
Chips: same-cluster · low-downtime · rollback-ready
```

Max 3 chips. No walls of API JSON on the slide — put deep payload examples in `architecture.md`.

## PNG overview checklist

- Zones labeled (CONTROL / RUNTIME) without cluttering nodes
- Legend optional if ≤4 roles and colors are obvious
- No text smaller than ~14px in the source PNG (scales down on slide)
- Transparent-free white/light background matching slide BG
