---
name: google-slides-workflow
description: >-
  Create or modify Google Slides presentations with automatic error recovery and
  mandatory verification. Orchestrates three sub-skills in sequence: build,
  troubleshoot, and verify. Use when the user asks to "create a presentation",
  "make a deck", "build slides", "Google Slides", "generate a slide deck",
  "modify slides", "add slides", "update presentation", "edit slide", or any
  request to produce or modify a presentation in Google Slides.
---

# Google Slides — Orchestrated Workflow

Every NEW presentation goes through three phases: **Build → Troubleshoot → Verify**.
Modifications to existing presentations go through: **Modify → Quick Verify**.
NEVER deliver the presentation URL until verification passes.

## Phase 1: Build

**Entry criteria:** User has requested a presentation.

**Action:** Read and follow the `google-slides-presentation` skill at
[../google-slides-presentation/SKILL.md](../google-slides-presentation/SKILL.md).

**Exit criteria:** All slides are created, no API errors remain.

If ANY of these occur during Phase 1, enter Phase 2 before continuing:

- Layout ID not found or "object could not be found" errors
- `predefinedLayout` errors (e.g., "BLANK is not present in the current master")
- Inherited decorative elements or placeholders overlapping content
- Logo missing, covered, or `createImage` URL errors
- Content overflow or font rendering issues
- Need to merge/import slides from existing decks
- Background rectangle or z-order issues

## Phase 2: Troubleshoot (conditional)

**Entry criteria:** Phase 1 encountered an error listed above.

**Action:** Read and follow the `google-slides-red-hat-advanced` skill at
[../google-slides-red-hat-advanced/SKILL.md](../google-slides-red-hat-advanced/SKILL.md).
Apply the relevant fix, then return to Phase 1 to continue building.

**Exit criteria:** The error is resolved and Phase 1 can proceed.

You may enter Phase 2 multiple times during a single build. Each time,
read the advanced skill, apply the fix, and return to Phase 1.

## Phase 3: Verify (MANDATORY — never skip)

**Entry criteria:** Phase 1 is complete — all slides built, no errors.

**Action:** Read and follow the `google-slides-verify` skill at
[../google-slides-verify/SKILL.md](../google-slides-verify/SKILL.md).

Run ALL checks (1-12, including 3b-3f). The most critical checks for common failures are:
- **Check 2 (thumbnails)** — download and visually inspect at minimum the title slide, one diagram slide, one text-heavy slide, and the last slide
- **Check 3 (overflow)** — verify no element exceeds slide boundaries (10" × 5.625")
- **Check 3c (overlap)** — verify no content elements overlap each other
- **Check 3d (footer zone)** — verify no content below y=4.80" (footer protection boundary)
- **Check 3e (title wrap)** — verify all titles fit on a single line
- **Check 3f (title overlap)** — verify no content panels start above y=1.00" (overlapping title area)
- **Check 4 (logo/wordmark)** — every content slide must have a logo image or text wordmark
- **Check 5 (font size)** — no text below 12pt
- **Check 12 (bookends)** — first slide must be RH_RED title, last slide must be RH_RED Thank You with "Thank You" text

**Exit criteria:** ALL verification checks pass.

If verification finds issues:

1. Return to Phase 2 to fix them
2. Re-run Phase 3
3. Repeat until all checks pass

## CRITICAL — Subagent Isolation

**This skill ONLY works if the agent following it also runs verification.**
If this workflow is being followed inside a subagent, that subagent MUST
complete Phase 3 before returning. Subagents have isolated context — they
do not inherit verification requirements from the parent. The subagent must
self-verify and self-fix before returning the URL to the parent agent.

The parent agent must include this explicit requirement in every subagent
prompt: "After building, read and run the full verify skill at
`/Users/njajodia/Cursor Experiments/.cursor/skills/google-slides-verify/SKILL.md`.
Fix all failures. Only return the URL when all 12 checks pass."

## Delivery

Only after Phase 3 passes with zero issues:

1. Return the presentation URL: `https://docs.google.com/presentation/d/<PRES_ID>`
2. Summarize what was built (slide count, sections, key content)
3. Remind the user to add speaker notes and review sensitive data before sharing

---

## Modifying Existing Presentations

When the user asks to add, edit, reorder, or delete slides in an EXISTING
presentation, follow this workflow instead of the full build pipeline.

### Entry criteria

The user references an existing presentation by URL, ID, or name, AND asks
to make changes (add slides, update content, move slides, delete slides).

### Step 1: Read the Current Deck

Before making any changes, fetch the current deck structure:

1. Get the presentation metadata (slide count, slide IDs, layout IDs)
2. Identify which slides are affected by the requested change
3. Note the color mode (light/dark) of existing slides to maintain consistency

### Step 2: Apply Changes

Perform the requested modifications using batchUpdate:

- **Add slides** — insert at the correct position using `insertionIndex`.
  Match the existing deck's color mode, fonts, and branding. Use template
  layouts from the Red Hat standard template when available (see
  `references/red-hat-template-layouts.md`).
- **Edit content** — update text, shapes, or styling on existing slides.
  Delete old elements and recreate if structural changes are needed.
- **Reorder slides** — use `updateSlidesPosition` with the target index.
- **Delete slides** — use `deleteObject` with the slide's objectId.

If errors occur during modification, enter Phase 2 (Troubleshoot) as with
new builds.

### Step 3: Quick Verify (MANDATORY — never skip)

After modifications are complete, run Quick Verify. Read and follow the
`google-slides-verify` skill at
[../google-slides-verify/SKILL.md](../google-slides-verify/SKILL.md)
with `VERIFY_MODE = "quick"` and pass the list of affected slide IDs.

Quick Verify runs Checks 2 (thumbnails), 3 (overflow), 3c (overlap),
3d (footer zone), 3e (title wrap), 3f (title overlap), and 5 (font size)
on the affected slides. It skips full-deck checks like PDF export.

### Step 4: Deliver

After Quick Verify passes:

1. Return the presentation URL
2. Summarize what changed (slides added/modified/deleted, content updates)
3. Confirm total slide count after changes
