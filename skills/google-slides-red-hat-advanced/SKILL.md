---
name: google-slides-red-hat-advanced
disable-model-invocation: true
description: >-
  Advanced troubleshooting and recovery for Google Slides builds using the
  Red Hat template. Covers layout ID discovery after copy, inherited element
  cleanup, background rectangle layering, logo management, Playwright-based
  slide import, font sizing, and the rebuild-vs-patch strategy. Sub-skill
  invoked by google-slides-workflow when errors occur during build.
---

# Google Slides — Red Hat Advanced Playbook

Fixes for known pitfalls when building on the Red Hat template. Read the
primary skill (`google-slides-presentation`) first — this skill extends it
with error recovery and complex workflows.

## Layout IDs Change on Copy

After `gws drive files copy`, every object ID changes. Discover layout IDs
from the copied presentation:

```python
import json, subprocess

r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'layouts(objectId,layoutProperties(name,displayName))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

for layout in data.get('layouts', []):
    props = layout.get('layoutProperties', {})
    print(f"{layout['objectId']:30s} {props.get('name',''):20s} {props.get('displayName','')}")
```

Use the `CUSTOM` layout for clean blank slides. `predefinedLayout: "BLANK"`
does NOT exist in this template — always use explicit `layoutId`.

## Inherited Element Cleanup

Custom slides inherit elements from master → layout → slide. You will see
decorative images, red blobs, placeholder text boxes (`SLIDES_API*` prefix),
and patterns from the master.

### The Background Rectangle Technique

Add a full-page opaque RECTANGLE to every custom slide, sent to the back:

```python
def add_background_rect(reqs, slide_id, color):
    rid = uid()
    reqs.append({"createShape": {"objectId": rid, "shapeType": "RECTANGLE",
        "elementProperties": {"pageObjectId": slide_id,
            "size": {"width": {"magnitude": inches(13.33), "unit": "EMU"},
                     "height": {"magnitude": inches(7.5), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": 0, "translateY": 0, "unit": "EMU"}}}})
    reqs.append({"updateShapeProperties": {"objectId": rid,
        "shapeProperties": {
            "shapeBackgroundFill": {"solidFill": {
                "color": {"rgbColor": color}, "alpha": 1.0}},
            "outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "shapeBackgroundFill,outline"}})
    reqs.append({"updatePageElementsZOrder": {
        "pageElementObjectIds": [rid], "operation": "SEND_TO_BACK"}})
    return rid
```

- **Light-background slides** → WHITE fill
- **Dark-background slides** (dividers, closing) → GRAY_95 fill

Using white on dark slides makes white text invisible.

### Delete Layout Decorative Elements (Optional)

Clean the layout once if many slides share it:

```python
# Query layout elements, find images/decorative shapes, then:
reqs = [{"deleteObject": {"objectId": eid}} for eid in elements_to_remove]
```

### Delete SLIDES_API Placeholders

```python
for el in slide.get('pageElements', []):
    if el['objectId'].startswith('SLIDES_API'):
        reqs.append({"deleteObject": {"objectId": el['objectId']}})
```

## Logo Management

Background rectangles cover the inherited Red Hat logo. You must manually
add the logo to every custom slide.

### Get a Working Logo URL

Template URLs are NOT publicly accessible for `createImage` on a copied
presentation. Extract the `sourceUrl` from an existing image element in
the same presentation:

```python
for el in slide.get('pageElements', []):
    img = el.get('image', {})
    if img:
        logo_url = img.get('sourceUrl', '')
```

### Standard Logo Position (Bottom-Right)

```python
LOGO_W = inches(1.5)
LOGO_H = inches(0.5)
LOGO_X = inches(11.5)
LOGO_Y = inches(6.8)
```

### Light vs Dark Logos

- **Light-background slides** → dark Red Hat logo (from light master/layout)
- **Dark-background slides** → white/reverse Red Hat logo (from dark master/layout)

Extract both URLs from different layouts in the copied template.

## API Gotchas

### Outline Weight Cannot Be Zero

```python
# WRONG — API rejects this
{"outline": {"weight": {"magnitude": 0, "unit": "PT"}}}

# CORRECT — hides the outline
{"outline": {"propertyState": "NOT_RENDERED"}}
```

### createImage URL Must Be Accessible

`createImage` fetches the URL server-side. Template-internal URLs with
`?key=<template-key>` only work within that presentation. Get the URL
from an existing image element in the copy (see Logo Management above).

### Text Styling on Empty Shapes

Never call `updateTextStyle` on a shape with no text:

```python
if text:
    reqs.append({"insertText": {"objectId": sid, "text": text}})
    reqs.append({"updateTextStyle": {"objectId": sid, ...}})
```

### gws CLI Output Parsing

Always skip non-JSON lines (keyring messages):

```python
lines = result.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))
```

## Hybrid Workflow: API + Playwright Import

For decks merging existing presentations with custom slides:

### Custom Slides → API

Build title, agenda, divider, comparison, and closing slides via
`batchUpdate`. Full control over content and layout.

### Existing Decks → Playwright Import

Import existing presentations using Google Slides' native Import Slides
feature via Playwright browser automation. This preserves perfect visual
fidelity — fonts, images, colors, and layout are handled by Google's
rendering engine.

```
1. Open the target presentation in browser
2. File → Import slides
3. Search for the source deck by name
4. Select desired slides (or "Select all")
5. Click "Import slides"
6. Repeat for each source deck
```

API element-by-element copy loses formatting fidelity. Always prefer
native import for existing content.

### After Import: Reorder Slides

Imported slides appear at the end. Use `updateSlidesPosition`:

```python
for i, slide_id in enumerate(final_order):
    reqs.append({"updateSlidesPosition": {
        "slideObjectIds": [slide_id],
        "insertionIndex": i
    }})
```

## Font Size Standards

At 13.33" × 7.5" page size, minimum **12pt** for any visible text:

- **Slide title**: 30-36pt (Red Hat Display, Bold)
- **Section heading**: 26-32pt (Red Hat Display, Bold)
- **Body text**: 14-16pt sparse, 12-14pt dense
- **Subtitle**: 16-22pt (Red Hat Text)
- **Table/comparison**: 12-15pt depending on content volume
- **Badge/label**: 14-18pt (Red Hat Text, Bold)
- **Numbered circles**: 18-20pt (Red Hat Display, Bold, white on red)
- **Footer/confidential**: 12-14pt

## Rebuild vs Patch

When a slide needs significant changes (font overhaul, layout restructure),
delete all elements and rebuild from scratch:

```python
reqs = [{"deleteObject": {"objectId": eid}} for eid in element_ids]
# Then recreate with corrected dimensions, fonts, spacing
# Re-add background rectangle
# Re-add logo
```

This avoids cascading text range index issues and produces clean output.
