---
name: google-slides-architecture-diagram
description: >-
  Build customer-ready architecture diagrams in Google Slides using the
  interactive-architecture mental model (nodes, named flows, steps, modes,
  active/participant/dimmed states) adapted for static slides and optional
  storyboard sequences. Use when the user asks for an architecture diagram,
  service map, data-flow walkthrough, MTC/MTA topology, system flow on slides,
  click-through architecture in Google Slides, or to redesign a messy
  boxes-and-arrows slide. Do NOT use for interactive HTML diagrams (use the
  HTML architecture-diagram skill) or for generic non-diagram slide content.
---

# Google Slides Architecture Diagrams

Adapt the [interactive architecture diagram](https://github.com/konraddzbik/architecture-diagram-skill) mental model to **Google Slides**.

Slides cannot run animated packets or a live player. They CAN teach the same way: clear topology, named flows, step-by-step storyboards, and mode variants with consistent node placement.

**Inspired by:** konraddzbik/architecture-diagram-skill (MIT). This skill reuses its planning model; the output medium is Google Slides + optional companion markdown.

---

## When to use

| Situation | Use this skill? |
|---|---|
| Architecture / data-flow diagram on Google Slides | **Yes** |
| Customer walkthrough of how components connect | **Yes** |
| Stage → cutover → rollback storyboard in a deck | **Yes** |
| Direct vs Indirect (or similar) mode comparison | **Yes** |
| Interactive HTML click-through in a browser | No — use HTML architecture-diagram skill |
| Static Mermaid in a README | No — Mermaid is simpler |
| Generic text/agenda slides | No — use `google-slides-presentation` |

---

## Mental model (same four primitives)

1. **Nodes** — services, CRs, datastores, users, external systems. Each has a **role** (color) and short metadata (tech / purpose).
2. **Flows** — named scenarios (`Stage`, `Cutover`, `Indirect copy`). Each flow is an ordered list of **steps**.
3. **Steps** — `{from, to, title, desc, chips?}`. One handoff: X sends/refers/configures Y.
4. **Modes** — orthogonal toggles (`direct`/`indirect`, `dev`/`prod`). Same topology; highlight different path or swap labels — do **not** invent a different system unless you build a second diagram.

Modes ≠ flows. Flows = scenarios. Modes = deployment / path shape.

---

## Hard constraints (Red Hat slides)

Always compose with workspace helpers from `google-slides-presentation` / `slides-script/helpers.py`:

- Slide size **10″ × 5.625″**, content zone **y 1.00″ → 4.80″**, margins **0.50″**
- Every content slide: red accent bar + title + subtitle + RH logo
- Fonts: Red Hat Display (titles) / Red Hat Text (body); **≥ 12pt**
- Light/dark: follow the deck’s existing `COLOR_MODE` (do not flip without asking)
- Create slides with `predefinedLayout: "BLANK"` + explicit background
- After build: run **Quick Verify** from `google-slides-verify` on affected slide IDs

**Default safety rule:** never delete or rewrite existing slides unless the user explicitly asks. Prefer **append** or **insert** a new slide.

---

## Workflow

### Step 1 — Capture intent

If the user provided docs / prior diagram / deck context, extract nodes, flows, and modes first. Ask only gaps:

- What system are we drawing?
- Which 1–2 flows matter for this audience?
- Any mode toggle (e.g. Direct vs Indirect)?
- Overview only, or overview + storyboard steps?
- Insert where? (default: after the related existing architecture slide, or before Thank You)

### Step 2 — Write a planning spec (required)

Create a JSON planning file before drawing. Save under the working dir (e.g. `slides-script/specs/<name>.json`).

Schema outline:

```json
{
  "system": "MTC same-cluster storage class conversion",
  "audience": "Customer platform team",
  "color_mode": "light",
  "modes": ["direct", "indirect"],
  "nodes": [
    {
      "id": "mtc_ui",
      "role": "orch",
      "label": "MTC UI + Controller",
      "subtitle": "Host cluster operator",
      "zone": "control",
      "x_pct": 8,
      "y_pct": 12
    }
  ],
  "flows": [
    {
      "key": "sc_conversion",
      "name": "Storage class conversion",
      "steps": [
        {
          "from": "mtc_ui",
          "to": "mig_plan",
          "title": "creates",
          "desc": "Operator defines namespaces, PVs, copy method, target SC."
        }
      ]
    }
  ],
  "slide_plan": {
    "overview": true,
    "storyboard_flow": "sc_conversion",
    "mode_compare_slides": false
  }
}
```

Rules:

- ≤ **12 nodes**
- ≤ **6 flows** (usually 1–3 for a customer deck)
- **3–9 steps** per flow
- Positions use percentages of the **diagram canvas** (not the whole slide)
- See `references/flow-design-patterns.md`

### Step 3 — Choose render strategy

| Strategy | When | How |
|---|---|---|
| **A — Single PNG (preferred for overview)** | Dense wiring, customer overview, avoid shape clutter | Render with PIL + Red Hat fonts; upload to stable raw URL (e.g. `nirjhar17/slide-assets`); `createImage` into content zone |
| **B — Native shapes** | ≤ 6 nodes, simple left→right | Use helpers panels + arrows; fixed grid; no overlapping labels |
| **C — Storyboard sequence** | Teaching a flow step-by-step | Same node layout every slide; only active hop + callout change |

**Prefer A for overview.** Prefer C when the user wants the “click-through” feel. Combine A (overview) + C (2–5 step slides) for workshops.

Never recreate the HTML template’s player/JS in Slides.

### Step 4 — Map visual states to slides

From the HTML skill’s state model:

| State | Meaning | Slides treatment |
|---|---|---|
| `active` | Target of current step | Full color, accent ring / stronger border, optional step badge in callout |
| `active-from` | Source of current step | Full color, slightly softer than active |
| `participant` | Elsewhere in this flow | Normal opacity; show preview wires at ~50% |
| `dimmed` | Not in this flow | Grey fill, muted text, no emphasis |
| `hidden` | Excluded by mode | Omit from that mode slide |

**Overview slide:** show full topology; preview the primary flow’s wires at medium emphasis; do not dim everything.

**Storyboard slide N:** dim non-participants; emphasize current `from→to`; put step title + 1–2 sentence desc in a right or bottom callout (the “side panel”).

### Step 5 — Layout heuristics (five zones)

Place by data direction, not by org chart:

| Zone | Typical X% | Occupants |
|---|---|---|
| Entry | 0–15 | User, operator UI |
| Edge / control | 15–40 | Controllers, plans, gateways |
| Core | 40–65 | Apps, migration runners, Velero |
| Data plane | 65–85 | PVCs, volumes |
| Backing store | 85–100 | S3 / repo / external DB |

- Mainline through the vertical center
- Rare/one-shot nodes in a corner
- Avoid wire crossings; if crossed, move nodes before adding more labels
- Keep ≥ ~0.25″ gap between node boxes on the canvas

Role colors (keep ≤ 6 roles):

| Role | Use for | Light-mode accent |
|---|---|---|
| `user` | Operator / admin persona | Teal-green |
| `orch` | Controllers, plans, orchestrators | Sky / RH-adjacent blue-teal |
| `compute` | Heavy workers, restore agents | Magenta-leaning or RH red accent sparingly |
| `embed` | Transformers / converters | Amber |
| `vector` | Storage, PVC, S3, DB | Violet or warm orange for object storage |
| `seed` | One-shot jobs / migrations | Orange |

On Red Hat customer decks, prefer the existing deck palette (RH red, teal, orange, greens) over inventing a seventh neon color.

### Step 6 — Build slides

1. If overview: render/upload image OR draw shapes from the planning spec.
2. Create a **new** BLANK slide; set background; accent bar; title; subtitle; diagram; logo.
3. If storyboard: create additional slides with **identical** node coordinates; update highlights + callout only.
4. Title pattern:
   - Overview: `MTC Architecture — How Everything Connects`
   - Step: `SC Conversion — Step 3 of 6 · Cutover`
   - Mode: `Data Path — Indirect (via replication repo)`
5. Write companion `architecture.md` next to the planning JSON (components, flows, mode differences). Required unless user says HTML/MD not needed.

### Step 7 — Validate before delivery

- [ ] Every step is one handoff (X → Z), not a vague “does work”
- [ ] Node IDs in steps exist in `nodes`
- [ ] No overlapping labels on the overview
- [ ] Content stays inside y 1.00–4.80; logo in footer
- [ ] Fonts ≥ 12pt
- [ ] Existing slides untouched (unless user asked to replace)
- [ ] Quick Verify on new slide IDs; visually inspect thumbnail

---

## Storyboard recipe (click-through without HTML)

For flow `F` with N steps:

1. **Slide 0 — Overview** — all nodes; all flow wires as preview
2. **Slides 1..N** — identical layout; highlight step i; callout = title + desc + ≤3 chips
3. Optional **Mode A / Mode B** pair — same nodes; different emphasized path

Cap storyboard at **6 step slides** for a customer deck. More belongs in an appendix or HTML.

---

## Integration with other skills

| Skill | Role |
|---|---|
| `google-slides-presentation` | Helpers, branding, create/insert slide primitives |
| `google-slides-workflow` | Build → troubleshoot → verify orchestration |
| `google-slides-verify` | Mandatory checks after insert |
| `google-slides-red-hat-advanced` | Recover from layout/logo/master issues |

This skill owns **diagram planning + visual-state treatment**. It does not replace the Slides workflow skill.

---

## Common pitfalls

- **Shape spaghetti** — too many native arrows/labels → switch to Strategy A (PNG)
- **Different node positions per step slide** — breaks the “click-through” illusion; lock coordinates
- **Modes that rebuild the system** — split into two diagrams
- **More than 12 nodes** — split by concern (control plane vs data plane)
- **Editing the customer’s good overview** — add a new slide to compare; don’t silently replace
- **Promising HTML animations in Slides** — be explicit about storyboard limits

---

## Output checklist

When finished, tell the user:

1. Planning spec path
2. Companion `architecture.md` path (if written)
3. New slide objectId(s) + deck URL with `#slide=id.`
4. Whether overview / storyboard / mode slides were created
5. Honest quality notes (clarity, wire crossings, text density, verify result)

---

## References

- `references/flow-design-patterns.md` — topology, flows, steps, modes (Slides-adapted)
- `references/visual-states.md` — active/participant/dimmed mapping + callout copy rules
- `examples/mtc-storage-class-conversion.json` — worked planning spec
