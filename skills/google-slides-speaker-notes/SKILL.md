---
name: google-slides-speaker-notes
description: >-
  Write and add speaker notes to Google Slides presentations. Use when the user
  asks to "add speaker notes", "write speaker notes", "add presenter notes",
  "add talking points", or any request to add notes to a Google Slides deck.
---

# Google Slides — Speaker Notes

Write speaker notes that serve as natural talking points for explaining content
to customers. Notes should read like the presenter is speaking directly to the
audience — not like a script, not like a study guide, just clear explanations.

## Voice and Tone Rules

**Write as the presenter explaining to the customer.** First-person, direct,
conversational.

- YES: "This is a side-by-side comparison of the capabilities. The key
  takeaway is that Satellite operates at the errata and advisory level, not
  just the package level."
- YES: "We're not asking you to replace SSM. SSM is great at executing
  patches and running commands at scale."
- NO: "Ask the customer what their current patching process looks like."
- NO: "Key talking point: mention errata-level intelligence."
- NO: "This slide shows a comparison table. The presenter should highlight..."

### What to include

- Context the slide visual doesn't say — the "why" behind bullet points
- Concrete examples, numbers, or scenarios relevant to the customer
- Transitions that connect this slide to the next one
- Product clarifications (e.g. rebrandings, licensing, what's included)

### What to exclude

- Questions to ask the audience
- Prompts like "Pause here" or "Click to next slide"
- Repetition of text already visible on the slide
- Generic filler ("This is an important slide because...")
- Meta-commentary about the presentation structure

## Length Guidelines

| Slide type        | Notes length        |
|-------------------|---------------------|
| Title slide       | 2-3 sentences       |
| Section divider   | 1-2 sentences       |
| Content slide     | 3-5 sentences       |
| Comparison/table  | 4-6 sentences       |
| Thank you / close | 2-3 sentences       |

Keep individual notes under 100 words. The presenter glances at these — they
shouldn't need to read an essay.

## Which Slides Get Notes

**Every slide gets speaker notes.** No exceptions.

- Custom-built slides — full explanatory notes (3-6 sentences)
- Section dividers — brief transition context (1-2 sentences)
- Imported content slides — summarize the key point the presenter should
  emphasize; read the slide's visible text to understand the content, then
  write notes that add presenter context on top (2-4 sentences)
- Thank you / closing slides — wrap-up and next steps (2-3 sentences)

For imported slides, read the on-slide text first, then write notes that
explain *why* this content matters to the customer — not what the slide says,
but what the presenter should say about it.

## Technical Implementation

Speaker notes are added via the Google Slides API `insertText` on the notes
page body shape.

### Step 1: Get notes page shape IDs

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,slideProperties(notesPage(pageElements(objectId,shape(placeholder(type))))))'
    })], capture_output=True, text=True)
```

### Step 2: Map slide IDs to BODY placeholder on the notesPage

```python
notes_shapes = {}
for slide in data.get('slides', []):
    sid = slide['objectId']
    notes_page = slide.get('slideProperties', {}).get('notesPage', {})
    for el in notes_page.get('pageElements', []):
        ph = el.get('shape', {}).get('placeholder', {})
        if ph.get('type') == 'BODY':
            notes_shapes[sid] = el['objectId']
            break
```

### Step 3: Batch insert all notes

```python
reqs = []
for slide_id, note_text in notes.items():
    shape_id = notes_shapes.get(slide_id)
    if not shape_id:
        continue
    reqs.append({
        "insertText": {
            "objectId": shape_id,
            "text": note_text,
            "insertionIndex": 0
        }
    })
```

Send all requests in a single `batchUpdate` call.

### Important: Clear existing notes first

If notes already exist on a slide, clear them before inserting new ones:

```python
reqs.append({
    "deleteText": {
        "objectId": shape_id,
        "textRange": {"type": "ALL"}
    }
})
```

Put all `deleteText` requests before `insertText` requests in the batch.

## Example Notes (Globe Telecom deck)

These illustrate the correct voice and level of detail:

**Title slide:**
> Welcome everyone. Today we'll walk through Red Hat Satellite and
> Lightspeed — two solutions that directly address your RHEL management
> challenges in the cloud.

**Comparison slide:**
> This is a side-by-side comparison. The key takeaway is that Satellite
> operates at the errata and advisory level, not just the package level.
> When you have a P0 vulnerability, Satellite tells you exactly which
> advisory fixes it, its CVSS score, and which CVEs it addresses. SSM just
> tells you a newer package is available.

**Complement slide:**
> This is important — we're not asking you to replace SSM. SSM is great at
> executing patches and running commands at scale, and it's already deployed
> across your environment. Satellite adds the intelligence layer on top.

**Section divider:**
> Let's move to Red Hat Lightspeed. If you've heard of Red Hat Insights
> before, this is the same platform — it was rebranded to Lightspeed in 2026.

**Closing slide:**
> Thank you for your time. I'm happy to dive deeper into any of these
> topics, or we can schedule a hands-on session to see Satellite and
> Lightspeed in action with your environment.

## Checklist

Before delivering notes, verify:

- [ ] **Every single slide has speaker notes** — no slide left empty
- [ ] Every note reads as natural speech, not bullet points
- [ ] No questions to the audience
- [ ] No meta-commentary ("this slide shows...")
- [ ] No repetition of on-slide text
- [ ] Divider slides have brief 1-2 sentence transitions
- [ ] Content slides have 3-5 sentence explanations
- [ ] Imported slides have 2-4 sentences of presenter context
- [ ] All notes are under 100 words each
- [ ] Notes reference customer-specific context where available
