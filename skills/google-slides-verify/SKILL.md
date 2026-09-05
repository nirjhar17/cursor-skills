---
name: google-slides-verify
disable-model-invocation: true
description: >-
  Mandatory post-build verification for Google Slides presentations. Checks
  visual fidelity via thumbnails, content overflow, Red Hat logo presence,
  branding consistency, PDF export, text selectability, placeholder text,
  headline coherence, and color contrast. Supports Full Verify (all checks)
  and Quick Verify (subset of checks on affected slides). Sub-skill invoked
  by google-slides-workflow after the build is complete. Never skip this.
---

# Google Slides — Verification Checklist

Run every check below after the presentation is built. Report any failures
back to the orchestrator for fixing. Do NOT deliver the presentation URL
until all checks pass.

**Required inputs:** `PRES_ID` (the Google Slides presentation ID).

## Verification Modes

This skill supports two modes. The orchestrator specifies which mode to use.

### Full Verify (default)

Run ALL checks (1-12, including 3b-3e) on the entire presentation. Used
after building a new presentation from scratch.

**Required inputs:** `PRES_ID`

### Quick Verify

Run Checks 2, 3, 3c, 3d, 3e, 3f, and 5 on the affected slides. Used after
modifying an existing presentation (adding, editing, reordering, or deleting
slides). The overlap (3c), footer zone (3d), title wrap (3e), and title
overlap (3f) checks are included because these are the most common defects.

**Required inputs:** `PRES_ID`, `VERIFY_MODE = "quick"`,
`AFFECTED_SLIDE_IDS` (list of slide objectIds that were changed)

When in Quick Verify mode:
- Check 2 (Thumbnails): only download thumbnails for affected slides
- Check 3 (Overflow): only check elements on affected slides
- Check 3c (Overlap): only check elements on affected slides
- Check 3d (Footer zone): only check elements on affected slides
- Check 3e (Title wrap): only check titles on affected slides
- Check 3f (Title overlap): only check content panels on affected slides
- Check 5 (Font size): only check text on affected slides
- Skip all other checks

## Check 1: Slide Count

Verify the presentation has the expected number of slides:

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId)'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

slide_count = len(data.get('slides', []))
print(f"Total slides: {slide_count}")
```

**Pass criteria:** Slide count matches the planned deck structure.

## Check 2: Visual Spot Check (Thumbnails)

Download thumbnails for at least 4 key slides — title, one content slide,
one comparison/table slide, and the closing slide:

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'pages', 'getThumbnail',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'pageObjectId': slide_id,
        'thumbnailProperties.thumbnailSize': 'LARGE'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))
url = data.get('contentUrl', '')
# Download with: subprocess.run(['curl', '-sL', '-o', filename, url])
```

Visually inspect each thumbnail for:

- Content cut off at edges (overflow)
- Missing Red Hat logo
- Wrong background color (white text on white, dark text on dark)
- Inherited decorative elements bleeding through
- Text rendering in wrong font (Arial instead of Red Hat fonts)
- Blank or empty slides

**Pass criteria:** All thumbnails look correct with no visual issues.

## Check 3: Content Overflow Detection

Verify no element exceeds the slide boundaries (10" × 5.625"):

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

EMU = 914400
SLIDE_W_INCHES = 10.0    # slide width in inches
SLIDE_H_INCHES = 5.625   # slide height in inches
CONTENT_TOP = 1.0         # content must not start above this
overflow_found = False

for slide in data.get('slides', []):
    sid = slide['objectId']
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        sz = el.get('size', {})
        tr = el.get('transform', {})
        w = sz.get('width', {}).get('magnitude', 0) * abs(tr.get('scaleX', 1))
        h = sz.get('height', {}).get('magnitude', 0) * abs(tr.get('scaleY', 1))
        tx = tr.get('translateX', 0)
        ty = tr.get('translateY', 0)
        right = (tx + w) / EMU
        bottom = (ty + h) / EMU
        top = ty / EMU
        
        if right > SLIDE_W_INCHES + 0.2:
            print(f"RIGHT OVERFLOW: slide {sid} element {eid} "
                  f"right edge at {right:.1f}\" (max {SLIDE_W_INCHES}\")")
            overflow_found = True
        if bottom > SLIDE_H_INCHES + 0.2:
            print(f"BOTTOM OVERFLOW: slide {sid} element {eid} "
                  f"bottom edge at {bottom:.1f}\" (max {SLIDE_H_INCHES}\")")
            overflow_found = True

if not overflow_found:
    print("No overflow detected.")
```

**Pass criteria:** No elements extend beyond 10.2" wide or 5.825" tall
(small tolerance for rounding).

## Check 3b: Text Box Content Density

Verify that text boxes don't appear to be over-packed. For each TEXT_BOX,
estimate whether the content fits based on character count and font size:

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,shape(shapeType,text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

PT_TO_EMU = 12700
LINE_HEIGHT_FACTOR = 1.5  # typical line height multiplier

warnings = []
for slide in data.get('slides', []):
    sid = slide['objectId']
    for el in slide.get('pageElements', []):
        shape = el.get('shape', {})
        if shape.get('shapeType') not in ['TEXT_BOX', None]:
            continue
        h_emu = el.get('size', {}).get('height', {}).get('magnitude', 0)
        texts = shape.get('text', {}).get('textElements', [])
        total_chars = 0
        avg_font = 12
        for te in texts:
            tr = te.get('textRun', {})
            content = tr.get('content', '')
            total_chars += len(content)
            fs = tr.get('style', {}).get('fontSize', {}).get('magnitude', 0)
            if fs > 0:
                avg_font = fs
        if total_chars > 0 and h_emu > 0:
            # Estimate chars per line using actual box width
            w_emu = el.get('size', {}).get('width', {}).get('magnitude', 0)
            w_inches = w_emu / 914400 if w_emu > 0 else 4.0
            avg_char_width_pt = avg_font * 0.55
            chars_per_line = max(20, int((w_inches * 72) / avg_char_width_pt))
            est_lines = (total_chars / chars_per_line) + 1
            est_height_emu = est_lines * avg_font * PT_TO_EMU * LINE_HEIGHT_FACTOR
            if est_height_emu > h_emu * 1.2:  # 20% tolerance
                warnings.append(
                    f"POSSIBLE OVERFLOW: slide {sid} element {el['objectId']} "
                    f"est_height={est_height_emu/914400:.2f}\" box_height={h_emu/914400:.2f}\" "
                    f"({total_chars} chars at {avg_font}pt)"
                )

if warnings:
    for w in warnings:
        print(w)
    print(f"\n{len(warnings)} potential overflow warnings — review thumbnails carefully")
else:
    print("Text density check passed — no overflow risk detected.")
```

**Pass criteria:** No text boxes flagged. Any flagged boxes must be visually
confirmed in thumbnails. If overflow is visible in thumbnail, fix by reducing
content, increasing box height, or reducing font size.

## Check 3c: Element-to-Element Overlap Detection

Verify that no content elements on the same slide overlap each other. Overlap
causes text to be unreadable and is the second most common visual defect.

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform,shape(shapeType)))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

EMU = 914400
overlap_count = 0

# Elements to exclude from overlap checking (decorative / background)
SKIP_TYPES = {'LINE', 'STRAIGHT_CONNECTOR_1'}

def get_bbox(el):
    """Return (left, top, right, bottom) in inches."""
    sz = el.get('size', {})
    tr = el.get('transform', {})
    w = sz.get('width', {}).get('magnitude', 0) * abs(tr.get('scaleX', 1))
    h = sz.get('height', {}).get('magnitude', 0) * abs(tr.get('scaleY', 1))
    tx = tr.get('translateX', 0)
    ty = tr.get('translateY', 0)
    return (tx / EMU, ty / EMU, (tx + w) / EMU, (ty + h) / EMU)

def boxes_overlap(a, b, min_overlap_inches=0.3):
    """Return True if two bounding boxes overlap by at least min_overlap_inches in BOTH axes."""
    x_overlap = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    y_overlap = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return x_overlap >= min_overlap_inches and y_overlap >= min_overlap_inches

for slide in data.get('slides', []):
    sid = slide['objectId']
    elements = []
    for el in slide.get('pageElements', []):
        shape_type = el.get('shape', {}).get('shapeType', '')
        if shape_type in SKIP_TYPES:
            continue
        bbox = get_bbox(el)
        # Skip tiny decorative elements (accent bars, dots, connectors)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width < 0.2 or height < 0.15:
            continue
        elements.append((el['objectId'], bbox))

    # Pairwise overlap check
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            id_a, bbox_a = elements[i]
            id_b, bbox_b = elements[j]
            if boxes_overlap(bbox_a, bbox_b):
                print(f"OVERLAP: slide {sid} — {id_a} and {id_b} "
                      f"overlap by {max(0, min(bbox_a[2],bbox_b[2])-max(bbox_a[0],bbox_b[0])):.1f}\"x"
                      f"{max(0, min(bbox_a[3],bbox_b[3])-max(bbox_a[1],bbox_b[1])):.1f}\"")
                overlap_count += 1

if overlap_count == 0:
    print("No element overlaps detected.")
else:
    print(f"\n{overlap_count} element overlaps found — fix by adjusting positions or splitting content.")
```

**Pass criteria:** No content elements overlap by more than 0.3" in both
dimensions. Small overlaps (< 0.3") are tolerated for intentional layering
(e.g., text over a background rectangle). Significant overlaps indicate
content collision that must be fixed.

## Check 3c-ii: Image Element Spacing (Icons)

Icons from the Icon Repository have varying internal padding — some have solid
dark backgrounds that visually bleed to the edges while others are transparent
line-art. Two icons can pass the 0.3" overlap threshold yet still LOOK like
they're colliding.

Run this additional check for slides with 3+ image elements (agenda/icon slides):

```python
# After the main overlap check, run icon-specific spacing check
for slide in data.get('slides', []):
    sid = slide['objectId']
    images = []
    for el in slide.get('pageElements', []):
        if 'image' in el:
            bbox = get_bbox(el)
            height = bbox[3] - bbox[1]
            if height > 0.3:  # skip logo-sized images
                images.append((el['objectId'], bbox))

    if len(images) >= 3:
        # Sort by vertical position
        images.sort(key=lambda x: x[1][1])
        for i in range(len(images) - 1):
            id_a, bbox_a = images[i]
            id_b, bbox_b = images[i + 1]
            icon_height = bbox_a[3] - bbox_a[1]
            gap = bbox_b[1] - bbox_a[1]  # top-to-top distance
            min_gap = icon_height + 0.05  # icon height + 0.05" breathing room
            if gap < min_gap:
                print(f"ICON SPACING: slide {sid} — {id_a} and {id_b} "
                      f"are {gap:.2f}\" apart (need {min_gap:.2f}\")")
```

**Pass criteria:** Vertically stacked icons must be spaced at least
`icon_height + 0.05"` apart (top-to-top). If this fails, reduce icon size
or increase the item gap in the build script.

## Check 3d: Footer Zone Invasion

Verify that no content elements (other than the slide number and logo) extend
below the footer protection boundary at y = 4.80". This is the most common
cause of content being cut off or colliding with branding elements.

```python
EMU = 914400
FOOTER_BOUNDARY = 4.80  # inches — hard stop for all content

r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform,shape(shapeType,text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

invasion_count = 0
for slide in data.get('slides', []):
    sid = slide['objectId']
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        sz = el.get('size', {})
        tr = el.get('transform', {})
        h = sz.get('height', {}).get('magnitude', 0) * abs(tr.get('scaleY', 1))
        ty = tr.get('translateY', 0)
        bottom = (ty + h) / EMU

        if bottom <= FOOTER_BOUNDARY:
            continue

        # Allow slide number (small text box at bottom-left, font <= 10pt)
        shape = el.get('shape', {})
        texts = shape.get('text', {}).get('textElements', [])
        is_slide_number = False
        is_logo_text = False
        for te in texts:
            tr_text = te.get('textRun', {})
            content = tr_text.get('content', '').strip()
            fs = tr_text.get('style', {}).get('fontSize', {}).get('magnitude', 0)
            if content.isdigit() and fs <= 10:
                is_slide_number = True
            if content.lower() in ['red hat']:
                is_logo_text = True

        # Allow image elements (likely the logo)
        if el.get('image'):
            continue
        if is_slide_number or is_logo_text:
            continue

        # This element is invading the footer zone
        print(f"FOOTER INVASION: slide {sid} element {eid} "
              f"bottom={bottom:.2f}\" exceeds {FOOTER_BOUNDARY}\" boundary")
        invasion_count += 1

if invasion_count == 0:
    print("Footer zone clear — no content below 4.80\".")
else:
    print(f"\n{invasion_count} elements invade the footer zone — "
          f"move content above y=4.80\" or reduce content to fit.")
```

**Pass criteria:** No content elements (text boxes, rectangles, shapes) extend
below y = 4.80" except for the slide number and Red Hat logo.

## Check 3e: Title Wrapping Detection

Verify that slide titles fit on a single line. A wrapped title pushes all
content down and causes cascade overflow on the rest of the slide.

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform,shape(text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

EMU = 914400
wrap_warnings = 0

# Title character limits by font size (assuming Red Hat Display)
TITLE_LIMITS = {32: 45, 28: 55, 24: 65, 20: 80, 18: 95}

for slide in data.get('slides', []):
    sid = slide['objectId']
    # Find the element with the largest font — that's the title
    largest_font = 0
    title_text = ""
    title_eid = ""
    title_width = 0
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        sz = el.get('size', {})
        tr = el.get('transform', {})
        w = sz.get('width', {}).get('magnitude', 0) * abs(tr.get('scaleX', 1))
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            trn = te.get('textRun', {})
            fs = trn.get('style', {}).get('fontSize', {}).get('magnitude', 0)
            content = trn.get('content', '').strip()
            if fs > largest_font and content:
                largest_font = fs
                title_text = content
                title_eid = eid
                title_width = w / EMU

    if largest_font >= 20 and title_text:
        # Estimate using box width and font size
        avg_char_w = largest_font * 0.55  # approximate char width
        chars_that_fit = int((title_width * 72) / avg_char_w)

        if len(title_text) > chars_that_fit:
            print(f"TITLE WRAP: slide {sid} — \"{title_text[:50]}...\" "
                  f"({len(title_text)} chars at {largest_font}pt in {title_width:.1f}\" box, "
                  f"fits ~{chars_that_fit} chars)")
            wrap_warnings += 1
        else:
            # Also check against recommended limits
            limit = TITLE_LIMITS.get(int(largest_font), 50)
            if len(title_text) > limit:
                print(f"TITLE LONG: slide {sid} — \"{title_text[:50]}...\" "
                      f"({len(title_text)} chars at {largest_font}pt, recommended max {limit})")
                wrap_warnings += 1

if wrap_warnings == 0:
    print("All titles fit within their boxes — no wrapping detected.")
else:
    print(f"\n{wrap_warnings} title wrapping risks — shorten titles or reduce font size.")
```

**Pass criteria:** All titles fit on a single line within their text box width.

## Check 3f: Content Panels Overlapping Title Area

Verify that content panels (rectangles, text boxes with body text) do NOT
start above y=1.00" (CONTENT_TOP_Y = 914400 EMU). This is the #1 defect
seen in broken builds — content panels placed at y values that overlap or
clip the title area.

```python
EMU = 914400
CONTENT_TOP = 1.0  # inches — content MUST start at or below this

r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform,shape(shapeType,text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

violations = 0
for slide in data.get('slides', []):
    sid = slide['objectId']
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        tr = el.get('transform', {})
        ty = tr.get('translateY', 0) / EMU
        sz = el.get('size', {})
        w = sz.get('width', {}).get('magnitude', 0) / EMU
        h = sz.get('height', {}).get('magnitude', 0) / EMU
        shape = el.get('shape', {})
        shape_type = shape.get('shapeType', '')
        
        # Skip the accent bar (very thin rectangle at y=0)
        if h < 0.1:
            continue
        # Skip title and subtitle (they are EXPECTED above CONTENT_TOP)
        texts = shape.get('text', {}).get('textElements', [])
        max_font = 0
        for te in texts:
            fs = te.get('textRun', {}).get('style', {}).get('fontSize', {}).get('magnitude', 0)
            if fs > max_font:
                max_font = fs
        if max_font >= 20:  # title font — expected above content line
            continue
        if max_font >= 11 and h < 0.35 and ty < 0.90:  # subtitle — expected above content
            continue
        
        # Content panels/boxes with top edge above CONTENT_TOP
        if ty < CONTENT_TOP and shape_type in ['RECTANGLE', 'TEXT_BOX', 'ROUND_RECTANGLE', '']:
            if w > 1.0 and h > 0.3:  # skip tiny decorative elements
                print(f"TITLE OVERLAP: slide {sid} element {eid} "
                      f"starts at y={ty:.2f}\" (must be >= {CONTENT_TOP}\")")
                violations += 1

if violations == 0:
    print("No content panels overlapping title area.")
else:
    print(f"\n{violations} content panels start above y=1.00\" — "
          f"they overlap the title. Move all content below CONTENT_TOP_Y (914400 EMU).")
```

**Pass criteria:** No content panels (rectangles, text boxes with body text)
start above y = 1.00". Only the title, subtitle, and accent bar are allowed
above this line.

## Check 4: Red Hat Logo / Wordmark Presence

Verify every custom-built slide has a Red Hat logo — either as an image
element with a valid source URL, or as a text-based "Red Hat" wordmark.

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,image(contentUrl,sourceUrl),shape(text(textElements(textRun(content,style(fontFamily,fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

for slide in data.get('slides', []):
    sid = slide['objectId']
    if sid not in custom_slide_ids:
        continue

    has_valid_logo = False
    has_text_wordmark = False
    has_broken_image = False

    for el in slide.get('pageElements', []):
        # Check for image-based logo
        img = el.get('image', {})
        if img:
            source = img.get('sourceUrl', '') or img.get('contentUrl', '')
            if source and ('red' in source.lower() or 'hat' in source.lower()
                           or '1PJzabDSRJUiXLPGRqb_mgXbKqHGY-oxq' in source):
                has_valid_logo = True
            elif not source:
                has_broken_image = True

        # Check for text-based wordmark
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            tr = te.get('textRun', {})
            content = tr.get('content', '').strip()
            font = tr.get('style', {}).get('fontFamily', '')
            if content.lower() in ['red hat'] and 'Red Hat' in font:
                has_text_wordmark = True

    if has_valid_logo or has_text_wordmark:
        print(f"Slide {sid}: OK ({'image' if has_valid_logo else 'text wordmark'})")
    elif has_broken_image:
        print(f"Slide {sid}: WARNING — image element exists but may have broken source URL")
    else:
        print(f"Slide {sid}: MISSING — no logo image or text wordmark found")
```

**Pass criteria:** Every custom-built slide has either a valid logo image
(with a non-empty source URL) or a text-based "Red Hat" wordmark in Red Hat
Display font. Imported slides are exempt. Any slide with a broken/empty
image source URL should be flagged as a warning.

## Check 5: Font Size Minimum

Verify no text on custom slides is below 12pt:

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,shape(text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

for slide in data.get('slides', []):
    sid = slide['objectId']
    if sid not in custom_slide_ids:
        continue
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            tr = te.get('textRun', {})
            content = tr.get('content', '').strip()
            fs = tr.get('style', {}).get('fontSize', {}).get('magnitude', 0)
            if content and 0 < fs < 12:
                print(f"SMALL FONT: slide {sid} element {eid} "
                      f"'{content[:30]}' at {fs}pt")
```

**Pass criteria:** No text below 12pt on custom slides.

## Check 6: PDF Export and Text Selectability

Export the presentation as PDF and verify text is selectable (not rasterized):

```bash
gws drive files export \
    --params '{"fileId": "PRES_ID", "mimeType": "application/pdf"}' \
    --output 'deck_verify.pdf'
```

```python
import fitz  # PyMuPDF

doc = fitz.open("deck_verify.pdf")
print(f"Total pages: {doc.page_count}")

test_pages = [0, 1, doc.page_count // 2, doc.page_count - 1]
for p in test_pages:
    if p < doc.page_count:
        page = doc[p]
        text = page.get_text().strip()
        has_text = len(text) > 10
        print(f"Page {p+1}: {'OK' if has_text else 'NO TEXT'} "
              f"({len(text)} chars)")
        if has_text:
            print(f"  Preview: {text[:80]}...")

doc.close()
```

**Pass criteria:** At least 3 of 4 sampled pages have extractable text
(imported image-heavy slides may have less text — that's acceptable).

## Check 7: Branding Consistency

Visual review of thumbnails for:

- Red accent line at top of every custom light-mode slide
- Correct fonts (Red Hat Display for headings, Red Hat Text for body)
- No fallback Arial or default fonts
- Correct color scheme (light mode = white bg, dark text; dark mode = dark bg, white text)
- "CUSTOMER CONFIDENTIAL" badge on the title slide

**Pass criteria:** All custom slides follow Red Hat branding guidelines.

## Check 8: Content Accuracy

Verify against the original brief/plan:

- Slide order matches the agenda
- Section dividers are in the correct positions
- Imported slides match their source decks
- No placeholder text ("Lorem ipsum", "TODO", "TBD") remains
- Presenter name and details are correct (if applicable)

**Pass criteria:** Content matches the planned structure and user's requirements.

## Check 9: Placeholder Text Detection

Scan all text elements for leftover placeholder text that should have
been replaced with real content:

```python
PLACEHOLDER_PATTERNS = [
    "Lorem ipsum", "TODO", "TBD", "PLACEHOLDER", "INSERT",
    "[Your ", "XXX", "FIXME", "sample text", "replace this"
]

r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,shape(text(textElements(textRun(content))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

found = False
for slide in data.get('slides', []):
    sid = slide['objectId']
    for el in slide.get('pageElements', []):
        eid = el['objectId']
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            content = te.get('textRun', {}).get('content', '')
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern.lower() in content.lower():
                    print(f"PLACEHOLDER: slide {sid} element {eid} "
                          f"contains '{pattern}' in: '{content.strip()[:50]}'")
                    found = True

if not found:
    print("No placeholder text detected.")
```

**Pass criteria:** No placeholder text patterns found in the presentation.

## Check 10: Headline Narrative Coherence

Extract all slide headlines and verify they tell a coherent story when
read in sequence. Headlines should be assertions, not labels.

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,shape(text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

LABEL_PATTERNS = [
    "overview", "introduction", "summary", "agenda", "appendix",
    "background", "details", "next steps", "conclusion", "q&a"
]

print("Slide Headlines (read these in sequence — they should tell a story):")
print("-" * 60)
for i, slide in enumerate(data.get('slides', []), 1):
    largest_font = 0
    headline = ""
    for el in slide.get('pageElements', []):
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            tr = te.get('textRun', {})
            fs = tr.get('style', {}).get('fontSize', {}).get('magnitude', 0)
            content = tr.get('content', '').strip()
            if fs > largest_font and content:
                largest_font = fs
                headline = content

    flag = ""
    if headline:
        hl_lower = headline.lower().strip()
        if any(hl_lower == p or hl_lower.startswith(p + " ")
               for p in LABEL_PATTERNS):
            flag = " <-- WARNING: label, not assertion"
    print(f"  Slide {i}: {headline or '(no headline found)'}{flag}")

print("-" * 60)
print("Review: Do these headlines tell a complete story?")
```

**Pass criteria:** No headlines flagged as labels. Headlines read as a
coherent narrative when taken in sequence. Report any flagged headlines
for manual review.

## Check 11: Color Contrast (WCAG AA)

Verify that text colors have sufficient contrast against their background.
WCAG AA requires 4.5:1 for body text and 3:1 for large text (18pt+ or
14pt+ bold).

```python
def relative_luminance(r, g, b):
    """Calculate relative luminance per WCAG 2.1."""
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

def contrast_ratio(l1, l2):
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageProperties(pageBackgroundFill(solidFill(color))),pageElements(objectId,shape(text(textElements(textRun(content,style(fontSize,bold,foregroundColor)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

fail_count = 0
for slide in data.get('slides', []):
    sid = slide['objectId']
    bg_fill = (slide.get('pageProperties', {})
               .get('pageBackgroundFill', {})
               .get('solidFill', {}).get('color', {})
               .get('rgbColor', {}))
    bg_r = bg_fill.get('red', 1.0)
    bg_g = bg_fill.get('green', 1.0)
    bg_b = bg_fill.get('blue', 1.0)
    bg_lum = relative_luminance(bg_r, bg_g, bg_b)

    for el in slide.get('pageElements', []):
        texts = el.get('shape', {}).get('text', {}).get('textElements', [])
        for te in texts:
            tr = te.get('textRun', {})
            content = tr.get('content', '').strip()
            if not content:
                continue
            style = tr.get('style', {})
            fg = style.get('foregroundColor', {}).get('opaqueColor', {}).get('rgbColor', {})
            fg_r = fg.get('red', 0.0)
            fg_g = fg.get('green', 0.0)
            fg_b = fg.get('blue', 0.0)
            fg_lum = relative_luminance(fg_r, fg_g, fg_b)

            ratio = contrast_ratio(fg_lum, bg_lum)
            fs = style.get('fontSize', {}).get('magnitude', 12)
            is_bold = style.get('bold', False)
            is_large = fs >= 18 or (fs >= 14 and is_bold)
            threshold = 3.0 if is_large else 4.5

            if ratio < threshold:
                print(f"LOW CONTRAST: slide {sid} "
                      f"'{content[:30]}' ratio={ratio:.1f}:1 "
                      f"(need {threshold}:1 for {'large' if is_large else 'body'} text)")
                fail_count += 1

if fail_count == 0:
    print("All text meets WCAG AA contrast requirements.")
else:
    print(f"\n{fail_count} contrast issues found.")
```

**Pass criteria:** All text elements meet WCAG AA contrast ratios.
Note: elements on colored shapes (not slide background) may show false
positives — review those manually.

## Check 12: Red Hat Bookend Slides

Every Red Hat presentation must open with a branded title slide and close
with a branded Thank You slide. These use `RH_RED` backgrounds — they are
NOT regular content slides. This check verifies both exist and are correct.

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId,pageElements(objectId,size,transform,shape(shapeType,shapeProperties(shapeBackgroundFill(solidFill(color))),text(textElements(textRun(content,style(fontSize)))))))'
    })], capture_output=True, text=True)

lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))

slides = data.get('slides', [])
EMU = 914400
RH_RED_R, RH_RED_G, RH_RED_B = 0.933, 0.0, 0.0
WHITE_R, WHITE_G, WHITE_B = 1.0, 1.0, 1.0

def is_rh_red(color, tolerance=0.15):
    r = color.get('red', 0)
    g = color.get('green', 0)
    b = color.get('blue', 0)
    return abs(r - RH_RED_R) < tolerance and g < tolerance and b < tolerance

def is_white(color, tolerance=0.1):
    r = color.get('red', 0)
    g = color.get('green', 0)
    b = color.get('blue', 0)
    return abs(r - 1.0) < tolerance and abs(g - 1.0) < tolerance and abs(b - 1.0) < tolerance

def check_bookend(slide, label, expect_text_pattern):
    """Check a bookend slide for RH_RED bg rect, white footer bar, and expected text."""
    issues = []
    has_red_bg = False
    has_white_footer = False
    has_expected_text = False

    for el in slide.get('pageElements', []):
        shape = el.get('shape', {})
        fill_color = (shape.get('shapeProperties', {})
                      .get('shapeBackgroundFill', {})
                      .get('solidFill', {}).get('color', {})
                      .get('rgbColor', {}))

        # Compute actual dimensions (Slides API stores base size + scale transform)
        sz = el.get('size', {})
        tr = el.get('transform', {})
        raw_w = sz.get('width', {}).get('magnitude', 0)
        raw_h = sz.get('height', {}).get('magnitude', 0)
        w = raw_w * abs(tr.get('scaleX', 1))
        h = raw_h * abs(tr.get('scaleY', 1))
        ty = tr.get('translateY', 0)

        # Check for full-width RH_RED rectangle (background)
        if w > 12 * EMU and h > 4 * EMU and is_rh_red(fill_color):
            has_red_bg = True

        # Check for white footer bar (full-width, short, near bottom)
        if w > 12 * EMU and h < 1.5 * EMU and ty > 5.5 * EMU and is_white(fill_color):
            has_white_footer = True

        # Check for expected text content
        texts = shape.get('text', {}).get('textElements', [])
        for te in texts:
            content = te.get('textRun', {}).get('content', '').strip().lower()
            if expect_text_pattern.lower() in content:
                has_expected_text = True

    if not has_red_bg:
        issues.append(f"{label}: MISSING full-width RH_RED background rectangle")
    if not has_white_footer:
        issues.append(f"{label}: MISSING white footer bar")
    if not has_expected_text:
        issues.append(f"{label}: MISSING expected text containing '{expect_text_pattern}'")
    return issues

all_issues = []

# Check first slide (Title)
if slides:
    all_issues += check_bookend(slides[0], "Title slide (slide 1)", "")
    # Title slide: just check structure, no specific text pattern required
    # Remove the text issue since title text varies
    all_issues = [i for i in all_issues if "MISSING expected text" not in i
                  or "Title slide" not in i]

# Check last slide (Thank You)
if len(slides) > 1:
    all_issues += check_bookend(slides[-1], "Thank You slide (last)", "thank you")

if all_issues:
    for issue in all_issues:
        print(f"FAIL: {issue}")
else:
    print("Red Hat bookend slides verified: title slide and Thank You slide present.")
```

**Pass criteria:**
- Slide 1 has a full-width `RH_RED` background rectangle and a white footer bar
- Last slide has a full-width `RH_RED` background, white footer bar, and "Thank You" text
- Both slides follow the layout defined in the presentation skill's "Title & Thank You Slides" section

**Common failures:**
- Builder created content slides without bookends (most common)
- Title slide uses content-mode background instead of `RH_RED`
- Thank You slide missing or replaced with a generic closing slide

## Reporting Results

After running all checks, report a summary.

**Full Verify example:**
```
Verification Results (Full):
  Check 1  (Slide count):     PASS — 35 slides
  Check 2  (Visual):          PASS — 4 thumbnails reviewed
  Check 3  (Overflow):        PASS — no overflow detected
  Check 3b (Text density):    PASS — no overflow risk detected
  Check 3c (Overlap):         PASS — no element overlaps
  Check 3d (Footer zone):     PASS — no content below 4.80"
  Check 3e (Title wrap):      PASS — all titles single-line
  Check 4  (Logo/wordmark):   PASS — all 10 custom slides have logos or wordmarks
  Check 5  (Font size):       PASS — no text below 12pt
  Check 6  (PDF/text):        PASS — text selectable on all sampled pages
  Check 7  (Branding):        PASS — consistent Red Hat branding
  Check 8  (Content):         PASS — matches planned structure
  Check 9  (Placeholders):    PASS — no placeholder text found
  Check 10 (Headlines):       PASS — all headlines are assertions
  Check 11 (Contrast):        PASS — all text meets WCAG AA
  Check 12 (Bookends):        PASS — title + Thank You slides verified
```

**Quick Verify example:**
```
Verification Results (Quick — 3 slides modified):
  Check 2  (Visual):       PASS — 3 thumbnails reviewed
  Check 3  (Overflow):     PASS — no overflow on modified slides
  Check 3c (Overlap):      PASS — no element overlaps on modified slides
  Check 3d (Footer zone):  PASS — no footer invasion on modified slides
  Check 3e (Title wrap):   PASS — titles fit on modified slides
  Check 5  (Font size):    PASS — no text below 12pt on modified slides
```

If any check fails, report the specific failure details so the orchestrator
can route to the advanced skill for fixing.
