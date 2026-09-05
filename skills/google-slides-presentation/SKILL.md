---
name: google-slides-presentation
description: >-
  Create high-quality Google Slides presentations programmatically using the
  Google Slides API via the gws CLI. Use when the user asks to "create a
  presentation", "make a deck", "build slides", "Google Slides", "generate a
  slide deck", or any request to produce a presentation in Google Slides.
---

# Google Slides Presentation Generator

Build polished, branded Google Slides presentations by generating a Python
script that calls the Slides API `batchUpdate` via the `gws` CLI.

## When to Use

- "Create a presentation about X"
- "Make me a slide deck for Y"
- "Build Google Slides for Z"
- "Generate a deck on topic T"
- Any request where the deliverable is a Google Slides presentation.

## Architecture — Two Approaches

Use **Approach A (REST API via gws)** by default. Everything runs inside
Cursor — no browser steps, link delivered in chat. Use **Approach B
(Apps Script)** only when the user explicitly requests it or needs
advanced features like inserting images from URLs.

---

## Approach A — REST API via gws (Default)

This approach generates a Python script that calls the Slides REST API
`batchUpdate` via the `gws` CLI. Everything stays inside Cursor.

### A1 — Gather Content

Before writing any code, understand:

1. **Topic and audience** — who will see the deck and what is the goal
2. **Source material** — documents, notes, data the user has shared
3. **Branding** — default to Red Hat branding unless user specifies otherwise
4. **Slide count** — aim for 10-15 slides for a strategic deck
5. **Color mode** — always ask the user: "Light mode or dark mode?" before generating any slides. Do not assume a default — wait for their answer.

Synthesize all source material into a clear narrative structure before
touching any code. Outline the slide titles and key content for each.

### A2 — Create the Presentation (Blank Slides + Manual Branding)

Create a **fresh blank Google Slides presentation** — do NOT copy the Red Hat
template. The template master (`simple-light-2`) does not support
`predefinedLayout: "BLANK"`, which causes 400 errors. Red Hat Display and
Red Hat Text are Google Fonts and load correctly in any fresh Slides file.

Save the presentation ID. The fresh presentation starts with one default slide:

```python
r = subprocess.run(['gws', 'slides', 'presentations', 'get',
    '--params', json.dumps({
        'presentationId': PRES_ID,
        'fields': 'slides(objectId)'
    })], capture_output=True, text=True)
lines = r.stdout.strip().split('\n')
start = next((i for i,l in enumerate(lines) if l.strip().startswith('{')), 0)
data = json.loads('\n'.join(lines[start:]))
existing_slides = [s['objectId'] for s in data.get('slides', [])]
```

**Create slides using `predefinedLayout: "BLANK"` only — and ALWAYS set background:**

```python
def create_blank_slide(slide_id):
    """ALWAYS use predefinedLayout BLANK. NEVER use layoutId from template."""
    return {"createSlide": {
        "objectId": slide_id,
        "slideLayoutReference": {"predefinedLayout": "BLANK"}
    }}

def slide_bg(slide_id, color):
    """Set explicit slide background. MUST be called immediately after create_blank_slide."""
    return {"updatePageProperties": {
        "objectId": slide_id,
        "pageProperties": {
            "pageBackgroundFill": {
                "solidFill": {"color": {"rgbColor": color}, "alpha": 1.0}
            }
        },
        "fields": "pageBackgroundFill.solidFill.color,pageBackgroundFill.solidFill.alpha"
    }}
```

**MANDATORY SLIDE CREATION PATTERN — follow this for EVERY slide:**

```python
# Step 1: Set BG_PRIMARY at the top of the script based on COLOR_MODE
COLOR_MODE = "light"  # or "dark" — set once, use everywhere

if COLOR_MODE == "light":
    BG_PRIMARY    = {"red": 1.0,   "green": 1.0,   "blue": 1.0}    # WHITE
    TEXT_PRIMARY  = {"red": 0.082, "green": 0.082, "blue": 0.082}  # GRAY_95
    TEXT_SECONDARY= {"red": 0.302, "green": 0.302, "blue": 0.302}  # GRAY_60
elif COLOR_MODE == "dark":
    BG_PRIMARY    = {"red": 0.082, "green": 0.082, "blue": 0.082}  # GRAY_95
    TEXT_PRIMARY  = {"red": 1.0,   "green": 1.0,   "blue": 1.0}    # WHITE
    TEXT_SECONDARY= {"red": 0.639, "green": 0.639, "blue": 0.639}  # GRAY_40

ACCENT = {"red": 0.933, "green": 0.0, "blue": 0.0}  # RH_RED

# Step 2: For every content slide, create and immediately set background:
slide_id = uid()
reqs.append(create_blank_slide(slide_id))   # 1. BLANK layout — never layoutId
reqs.append(slide_bg(slide_id, BG_PRIMARY)) # 2. ALWAYS set bg — prevents master bleedthrough
# 3. Add content shapes...
```

**For special slides that override the color (title, closing):**
```python
title_id = uid()
reqs.append(create_blank_slide(title_id))
reqs.append(slide_bg(title_id, ACCENT))   # Red override for title/closing only
```

The template master's background MUST NEVER control any slide's color.
The script owns every slide's background, always.

**NEVER use `layoutId` pointing to a named template layout** (Interior blank,
Interior agenda, Interior callout, etc.) — they carry inherited background
and positional constraints that break both color mode and margins. Use ONLY
`predefinedLayout: "BLANK"`.

This gives you a completely empty canvas with zero placeholder elements
and zero inherited constraints. Red Hat fonts are inherited from the master.

**Add branding manually to each slide:**

```python
def add_red_accent_bar(reqs, slide_id):
    """Red accent bar at top of content slides (full width, 0.06" tall)."""
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid,
        "shapeType": "RECTANGLE",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": 9144000, "unit": "EMU"},
                     "height": {"magnitude": 54864, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": 0, "translateY": 0, "unit": "EMU"}
        }
    }})
    reqs.append({"updateShapeProperties": {
        "objectId": sid,
        "fields": "shapeBackgroundFill.solidFill.color",
        "shapeProperties": {"shapeBackgroundFill": {"solidFill": {
            "color": {"rgbColor": {"red": 0.933, "green": 0.0, "blue": 0.0}}
        }}}
    }})
    reqs.append({"updateShapeProperties": {
        "objectId": sid,
        "fields": "outline.outlineFill.solidFill.color,outline.weight",
        "shapeProperties": {"outline": {"outlineFill": {"solidFill": {
            "color": {"rgbColor": {"red": 0.933, "green": 0.0, "blue": 0.0}}
        }}, "weight": {"magnitude": 0, "unit": "EMU"}}}
    }})
```

**Do NOT use template content layouts** (Interior agenda, Interior callout,
Interior two column, etc.) — they contain placeholder elements that show
through as "Click to add subtitle" and cannot be reliably removed via the
API. Build all layouts from scratch with shapes and text boxes.

**IMPORTANT — Template does NOT support `predefinedLayout: "BLANK"`:**
The Red Hat template's master (`simple-light-2`) does NOT include `predefinedLayout: "BLANK"` as a valid layout. Using it will cause a 400 error. Therefore:

- Do NOT try to use `predefinedLayout: "BLANK"` on a presentation copied from the Red Hat template
- Instead, create a **fresh blank Google Slides presentation** using `gws slides presentations create`
- Red Hat Display and Red Hat Text are Google Fonts — they render correctly in any Slides file, so a fresh presentation is fully equivalent for branding purposes

**Always create a fresh blank presentation:**

```bash
gws slides presentations create --json '{"title": "Your Title Here"}' 2>&1 | \
  python3 -c "
import sys, json
lines = sys.stdin.readlines()
start = next(i for i, l in enumerate(lines) if l.strip().startswith('{'))
data = json.loads(''.join(lines[start:]))
print(data.get('presentationId'))
"
```

The default first slide has `objectId: "p"` — delete it after creating your first real slide.

### A3 — Write the Builder Script

Create a Python script at `<workspace>/slides-script/build_slides.py`.
**Copy `helpers.py` into the same directory** and import everything from it.

**⚠️ MANDATORY: Every build script MUST start with this exact template:**

```python
#!/usr/bin/env python3
"""Google Slides builder script — generated from presentation skill."""

import sys
import os

# Copy helpers.py to the same directory as this script, then import:
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import *

# ---- Configuration ----
COLOR_MODE = "light"  # "light", "dark", or "expressive_dark"
setup_color_mode(COLOR_MODE)

# ---- Create presentation ----
PRES_ID = create_presentation("Your Title Here")

# ---- Build slides ----
reqs = []

# Slide 1: Title slide — MANDATORY build_title_slide() pattern, see below
s1 = uid()
reqs.append(create_slide(s1))
build_title_slide(reqs, s1, "Your Deck Title", "Optional deck subtitle",
                   presenter_name="Presenter Name", presenter_role="Title, Red Hat")

# Slide 2+: Content slides — ALWAYS use this pattern:
s2 = uid()
reqs.append(create_slide(s2))
reqs.append(slide_bg(s2, BG_PRIMARY))
add_red_accent_bar(reqs, s2)
add_slide_title(reqs, s2, "Your Slide Title")
add_slide_subtitle(reqs, s2, "Optional subtitle")
# ... add content using add_content_panel(), add_content_text(), etc. ...
add_rh_logo(reqs, s2, COLOR_MODE)
add_slide_number(reqs, s2, 2)

# Last slide: Thank You — MANDATORY build_thank_you_slide() pattern, see below
s_last = uid()
reqs.append(create_slide(s_last))
build_thank_you_slide(reqs, s_last, slide_num=3)

# Delete the default blank slide
reqs.append(delete_default_slide(PRES_ID))

# ---- Send ----
send_batch(PRES_ID, reqs)
print(f"https://docs.google.com/presentation/d/{PRES_ID}")
```

**DO NOT redefine ANY constants or functions that exist in helpers.py.**
The helpers module provides: all layout constants (SLIDE_W, CONTENT_TOP_Y,
COL2_W, etc.), all color constants (RH_RED, GRAY_95, etc.), all mandatory
functions (add_slide_title, add_content_panel, add_rh_logo, etc.), all
slide build patterns (build_two_column_slide, etc.), and the batch sender.

**DO NOT create shapes with raw coordinates.** Use the provided functions:
- `add_slide_title()` — title at correct position
- `add_slide_subtitle()` — subtitle at correct position
- `add_content_panel()` — background panel with boundary enforcement
- `add_content_text()` — text box with auto-height and boundary enforcement
- `add_red_accent_bar()` — accent bar at top
- `add_rh_logo()` — logo at bottom-right
- `add_slide_number()` — slide number at bottom-left
- `build_two_column_slide()` — complete two-column slide
- `build_three_column_slide()` — complete three-column slide
- `build_four_column_slide()` — complete four-column slide
- `build_card_grid_slide()` — complete 2×3 card grid slide
- `build_title_slide()` — complete first slide (MANDATORY, see below)
- `build_thank_you_slide()` — complete last slide (MANDATORY, see below)
- `build_agenda_slide()` — complete agenda slide with icon-or-badge items (MANDATORY icon lookup first, see A4b below)
- `build_split_image_slide()` — text bullets + image side-by-side (v2.0)
- `build_diagram_image_slide()` — full-width diagram image with title (v2.0)
- `build_diagram_from_data()` — data-driven node-edge diagram (v2.0)
- `create_connector()` — connected arrow between two shapes (v2.0)

Key rules for the builder script:

- **Delete template sample slides** — remove the template's sample slides
  before adding your own (see A2). If using fallback blank mode, delete the
  default slide with `{"deleteObject": {"objectId": "p"}}`
- **Use BLANK slides only** — always create slides with
  `predefinedLayout: "BLANK"`. NEVER use `layoutId` pointing to any named
  template layout (even "Interior blank") — those carry inherited backgrounds
  and positional constraints that break color mode and margins. Only
  `predefinedLayout: "BLANK"` gives a true empty canvas.
- **Always set BG_PRIMARY immediately after create_blank_slide** — call
  `slide_bg(slide_id, BG_PRIMARY)` as the very next request after creating
  each slide. Without this, the template master's dark background bleeds
  through regardless of COLOR_MODE. Only override with a different color
  (e.g., ACCENT/red) on intentionally colored slides (title, closing).
- **Object IDs** — generate with `"e" + uuid.uuid4().hex[:10]` (must start with a letter)
- **Units** — all positions/sizes in EMU (1 inch = 914400 EMU, 1 pt = 12700 EMU)
- **Slide dimensions** — widescreen: 10" × 5.625" (9144000 × 5143500 EMU). This is the DEFAULT Google Slides size. Do NOT change the page size — all coordinates in this skill are calibrated for 10" × 5.625". NEVER use 13.33" × 7.5" coordinates
- **Empty text** — never call `insertText` with empty string, never call `updateTextStyle` on a shape with no text. Guard with `if text:` before text operations
- **Chunk size** — send batchUpdate in chunks of 200 requests max
- **Shape types** — use `TEXT_BOX` for text, `RECTANGLE` for boxes, `ROUND_RECTANGLE` for badges/buttons, `ELLIPSE` for dots
- **Text overflow prevention** — MANDATORY for every TEXT_BOX and RECTANGLE with text:

  1. **`shrinkTextOnOverflow: true`** — set on EVERY shape that contains text, no exceptions
  2. **Calculate height using `calc_box_height()`** — see MANDATORY Content Sizing Rules section below
  3. **Never hardcode text box heights** — always derive from content length and font size
  4. **Add autofit properties** after creating each text shape:

```python
def set_text_autofit(shape_id):
    """MUST be called for every shape that contains text."""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "fields": "autofit",
        "shapeProperties": {
            "autofit": {"autofitType": "TEXT_AUTOFIT"}
        }
    }}
```

  5. **Content budget per slide** — before building any slide, compute total content height:
     - Title: 0.50" at TITLE_Y (separate from content zone — handled by `add_slide_title()`)
     - Subtitle: 0.25" at SUBTITLE_Y (separate — handled by `add_slide_subtitle()`)
     - Content zone: 3.80" (CONTENT_TOP_Y=1.00" to CONTENT_BOT_Y=4.80")
     - Each bullet line: font_size_pt × 1.5 / 72 inches
     - Spacing between sections: 0.2"
     - Content MUST NOT exceed 3.80" total height
     - If total exceeds 3.80", split the slide into two slides BEFORE building

- **Red Hat logo on every content slide** — every content slide (not title, not Thank You) must have the Red Hat logo in the **bottom-right corner**, via `add_rh_logo(reqs, slide_id, color_mode)`. The logo is now a single, real wordmark IMAGE (hat icon + "Red Hat" text baked into one PNG, extracted from the official Red Hat Slides template) — two color variants (`RH_LOGO_URL_WHITE` / `RH_LOGO_URL_BLACK`) picked automatically by `color_mode`. Both are hosted on a plain public GitHub repo (`raw.githubusercontent.com`), which serves anonymous HTTPS GETs with no auth/token/expiry — this is what fixed the recurring "logo renders as plain text" defect, whose root cause was a tokenized/expiring `googleusercontent.com` URL (see Gotcha #3 below). `add_rh_logo()`, `add_rh_logo_image()`, and the constants (`RH_LOGO_URL_WHITE/BLACK`, `RH_LOGO_W/H/X/Y`) all live in `helpers.py` — do not redefine them in a build script.

**Logo placement rules:**
- Position: **bottom-right corner** of every content slide (`RH_LOGO_X/Y`, unchanged across redesigns so footer-zone math elsewhere never needs to move)
- Always call `add_rh_logo(reqs, slide_id, COLOR_MODE)` — it auto-selects white-text vs. black-text based on `color_mode`
- If `createImage` ever fails despite the stable URL, fall back to `add_rh_logo_text()` (native text, no image) rather than skipping the logo entirely
- Before EVER changing `RH_LOGO_URL_WHITE`/`RH_LOGO_URL_BLACK`, verify the new URL empirically first: `curl -s -o /dev/null -w "%{http_code}\n" <url>` must print `200` with NO auth headers attached (this is what Google's fetcher does) — do not trust a URL just because it opens in a logged-in browser
- The title slide and Thank You slide do NOT call `add_rh_logo()` — `build_title_slide()`/`build_thank_you_slide()` place the correctly-colored logo image internally

- **Title slide** (slide 1 of every deck) — MANDATORY: use `build_title_slide(reqs, slide_id, deck_title, deck_subtitle=None, presenter_name=None, presenter_role=None)` from `helpers.py`. NEVER hand-build this slide with `add_slide_title()`/`add_red_accent_bar()`/raw shapes — those are content-slide-only conventions and will not match the brand template. This function reproduces the official Red Hat title-slide template pixel-for-pixel (verified by rendering a real test presentation and comparing thumbnails):
  - Full-bleed two-tone illustration background (`TITLE_SLIDE_BG_URL`, via `slide_bg_image()`)
  - White decorative accent bar, bottom-left
  - Optional deck title (32pt bold) + subtitle (16pt) in the right-hand dark-red panel
  - Optional presenter name (16pt bold) + role (13pt regular) below the title
  - White wordmark logo, bottom-right (`RH_LOGO_URL_WHITE`)
  - Do NOT add a slide number to the title slide

- **Thank You slide** (last slide of every deck, NOT "closing slide") — MANDATORY: use `build_thank_you_slide(reqs, slide_id, slide_num, body_text=None, social_links=None)` from `helpers.py`. NEVER hand-build this slide. This function reproduces the official Red Hat closing-slide template pixel-for-pixel:
  - Full-bleed red (left ~62%) / white-footer (bottom strip) background (`CLOSING_SLIDE_BG_URL`, via `slide_bg_image()`)
  - Maroon decorative accent bars, top-left (tall) and bottom-left (short)
  - "Thank you" headline (40pt, white, Red Hat Display)
  - Body paragraph (12pt white) — defaults to standard Red Hat boilerplate if `body_text` omitted
  - Up to 4 social-link rows (icon + text), right side — defaults to Red Hat's official LinkedIn/YouTube/Facebook/Twitter if `social_links` omitted; pass your own `[(network, label), ...]` list (network must be one of the keys in `SOCIAL_ICON_URLS`) to customize
  - Slide number + black-text wordmark logo on the white footer band

Example:

```python
build_title_slide(reqs, s1, "SBI Shared File-System Analysis",
                   "GFS2 vs. IBM Storage Scale",
                   presenter_name="Nirjhar Jajodia",
                   presenter_role="Adoption Architect, Red Hat")
...
build_thank_you_slide(reqs, s_last, slide_num=len(all_slides))
```

### A4 — Execute

```bash
cd <workspace>/slides-script && python3 build_slides.py
```

The script calls `gws` as a subprocess. Verify all chunks succeed.
On error, read the error message (usually wrong objectId or text styling
on empty shape), fix the script, create a new presentation, and re-run.

If a run fails partway, do NOT retry on the same presentation — create a
fresh one and delete the broken one:

```bash
gws drive files delete --params '{"fileId": "<broken-id>"}'
```

### A4b — Add Icons

For any Agenda slide, icon lookup is MANDATORY-FIRST, not optional: before
writing the agenda slide's batchUpdate requests, you MUST search the Red
Hat Icon Repository for a matching icon per agenda item. Only fall back to
numbered circular badges (see the Agenda slide pattern below) if the
Icon Repository genuinely has no reasonable match after searching — never
default to badges/dots just because it's less work. This is the fix for
the recurring "agenda slides use red dots instead of icons" defect.

For every other icon use (product/tech accents, diagram labels, etc.),
sourcing from the Icon Repository remains optional/as-needed.

**Icon Repository ID:** `1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM`

See [references/icon-inventory.md](references/icon-inventory.md) for the
full inventory and extraction pattern.

To insert an icon into your presentation:

1. Get the icon's image contentUrl from the Icon Repository
2. Use `createImage` in your batchUpdate to place it on the target slide

```python
def add_icon(reqs, slide_id, image_url, left, top, width, height):
    """Insert an icon image from a URL."""
    sid = uid()
    reqs.append({"createImage": {
        "objectId": sid,
        "url": image_url,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": width, "unit": "EMU"},
                "height": {"magnitude": height, "unit": "EMU"}
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": left, "translateY": top,
                "unit": "EMU"
            }
        }
    }})
    return sid
```

Use icons sparingly -- 1-2 per slide maximum. Best uses: stat slide accents,
feature list markers, architecture diagram labels, comparison column headers.

### A4b — Known API Gotchas (MUST READ)

These are confirmed issues with the Google Slides batchUpdate API that will
cause build failures if not handled:

1. **TEXT_AUTOFIT is not supported** — `updateShapeProperties` with
   `autofit.autofitType: "TEXT_AUTOFIT"` returns error "Autofit types other
   than NONE are not supported." The `set_text_autofit()` helper is a no-op.
   Overflow prevention relies entirely on `calc_box_height()` sizing. Keep
   text boxes generously sized (5-6 bullets max per box).

2. **Outline weight 0 is invalid** — `outline.weight: 0` returns error
   "should not be less than or equal to zero." To hide borders, use
   `shape_no_border()` which sets `outline.propertyState: "NOT_RENDERED"`.

3. **Drive/googleusercontent URLs fail or expire in createImage** — URLs like
   `https://lh3.googleusercontent.com/d/FILE_ID` or `drive.google.com/uc?export=download`
   require public sharing and still often fail with "Access to the provided
   image was forbidden," or work once and then break later. The `contentUrl`
   values extracted from existing Google Slides presentations (Icon Repository,
   Red Hat template) are Google-hosted, but they are tokenized and expire
   (documented ~30 min window) — fine for a one-off same-session insert, NOT
   safe to hardcode into `helpers.py` for reuse across builds. **Preferred
   fix: host the static asset yourself on a plain public GitHub repo and
   reference it via `raw.githubusercontent.com/<user>/<repo>/<branch>/<path>`.**
   That host serves anonymous HTTPS GETs with no auth/token/expiry — the
   exact conditions `createImage` needs. See `RH_LOGO_URL_WHITE`/`_BLACK`,
   `TITLE_SLIDE_BG_URL`, `CLOSING_SLIDE_BG_URL`, and `SOCIAL_ICON_URLS` in
   `helpers.py` for working examples, all hosted on the `nirjhar17/slide-assets`
   public repo. Whichever host you use, ALWAYS verify empirically before
   wiring a URL in: `curl -s -o /dev/null -w "%{http_code}\n" <url>` must
   print `200` with no auth headers attached — do not trust "it opens in
   my browser." This exact discipline (real `createImage` call + thumbnail
   render + pixel comparison against the reference template) was used to
   validate `build_title_slide()`/`build_thank_you_slide()` before they
   were adopted here.

4. **Icon search terms must match actual titles** — The Icon Repository icons
   have titles like `Technology_icon-Red_Hat-Ansible_Automation_Platform-Standard-RGB.png`,
   `Icon-Red_Hat-IT_modernization-Red-RGB.Large-icon.png`, etc. Search by these
   exact substrings, not generic terms like "clock" or "arrow."

### A5 — Deliver

Return the presentation URL to the user:
`https://docs.google.com/presentation/d/<PRES_ID>`

Remind them to:
- Add speaker notes if presenting live
- Review any sensitive names/data before sharing externally
- Logos are included via the template master slides; add product-specific
  logos manually if needed beyond what the template provides

---

## Approach B — Google Apps Script (Advanced / On Request)

Use only when the user explicitly requests Apps Script or needs advanced
features like inserting images from URLs. Requires first-time browser
authorization — not seamless from Cursor.

### B1 — Create an Apps Script Project

```bash
gws script projects create --json '{"title": "slide-builder"}' 2>&1 | \
  python3 -c "
import sys, json
lines = sys.stdin.readlines()
start = next(i for i, l in enumerate(lines) if l.strip().startswith('{'))
data = json.loads(''.join(lines[start:]))
print(data.get('scriptId'))
"
```

### B2 — Write Code.gs

Apps Script uses `SlidesApp` — simpler code, positions in points (not EMU),
chainable styling. Can insert images via `slide.insertImage(url)`.

### B3 — Push and Execute

```bash
gws script projects updateContent --params '{"scriptId": "<SCRIPT_ID>"}' \
  --json '{"files": [{"name":"Code","type":"SERVER_JS","source":"<code>"}]}'
```

First run requires browser authorization at:
`https://script.google.com/d/<SCRIPT_ID>/edit`

### B4 — Deliver

Return the presentation URL from the script output.

## Design System

### Color Mode

Before generating any slides, **always ask the user** which color mode they prefer. Do not assume a default — wait for their answer:

- **Light mode** — clean white backgrounds, dark text, best for print and email sharing
- **Dark mode** — cinematic dark backgrounds, white text, best for presenting on screen
- **Expressive Dark mode** — purple/teal-accented dark backgrounds, more colorful and energetic, best for creative or forward-looking topics

Set a `COLOR_MODE` variable at the top of the builder script. All slide
background, text, and accent colors derive from this choice.

### Color Palette (Red Hat Brand)

**Core colors** (used in both modes):

```python
# Brand red
RH_RED         = {"red": 0.933, "green": 0.0,   "blue": 0.0}    # #ee0000 red-50
RH_RED_DARK    = {"red": 0.651, "green": 0.0,   "blue": 0.0}    # #a60000 red-60
RH_RED_LIGHT   = {"red": 0.961, "green": 0.431, "blue": 0.431}  # #f56e6e red-40
RH_RED_TINT    = {"red": 0.988, "green": 0.890, "blue": 0.890}  # #fce3e3 red-10

# Grays
RH_DARK        = {"red": 0.102, "green": 0.102, "blue": 0.102}  # #1a1a1a
GRAY_95        = {"red": 0.082, "green": 0.082, "blue": 0.082}  # #151515
GRAY_90        = {"red": 0.122, "green": 0.122, "blue": 0.122}  # #1f1f1f
GRAY_80        = {"red": 0.161, "green": 0.161, "blue": 0.161}  # #292929
GRAY_60        = {"red": 0.302, "green": 0.302, "blue": 0.302}  # #4d4d4d
RH_GRAY        = {"red": 0.29,  "green": 0.29,  "blue": 0.29}   # #4a4a4a
GRAY_40        = {"red": 0.639, "green": 0.639, "blue": 0.639}  # #a3a3a3
GRAY_20        = {"red": 0.878, "green": 0.878, "blue": 0.878}  # #e0e0e0
GRAY_10        = {"red": 0.949, "green": 0.949, "blue": 0.949}  # #f2f2f2
RH_LIGHT_GRAY  = {"red": 0.96,  "green": 0.96,  "blue": 0.96}   # #f5f5f5
WHITE          = {"red": 1.0,   "green": 1.0,   "blue": 1.0}    # #ffffff

# Teal
TEAL_10        = {"red": 0.855, "green": 0.949, "blue": 0.949}  # #daf2f2
TEAL_40        = {"red": 0.388, "green": 0.741, "blue": 0.741}  # #63bdbd
TEAL_50        = {"red": 0.216, "green": 0.639, "blue": 0.639}  # #37a3a3
TEAL_60        = {"red": 0.078, "green": 0.471, "blue": 0.471}  # #147878

# Purple
PURPLE_10      = {"red": 0.925, "green": 0.902, "blue": 1.0}    # #ece6ff
PURPLE_40      = {"red": 0.529, "green": 0.435, "blue": 0.831}  # #876fd4
PURPLE_50      = {"red": 0.369, "green": 0.251, "blue": 0.745}  # #5e40be
PURPLE_60      = {"red": 0.239, "green": 0.153, "blue": 0.522}  # #3d2785

# Orange
ORANGE_10      = {"red": 1.0,   "green": 0.910, "blue": 0.800}  # #ffe8cc
ORANGE_40      = {"red": 0.961, "green": 0.573, "blue": 0.106}  # #f5921b
ORANGE_50      = {"red": 0.792, "green": 0.424, "blue": 0.059}  # #ca6c0f
ORANGE_60      = {"red": 0.620, "green": 0.290, "blue": 0.024}  # #9e4a06

# Yellow
YELLOW_10      = {"red": 1.0,   "green": 0.957, "blue": 0.800}  # #fff4cc
YELLOW_40      = {"red": 0.863, "green": 0.651, "blue": 0.078}  # #dca614
YELLOW_50      = {"red": 0.725, "green": 0.518, "blue": 0.071}  # #b98412
YELLOW_60      = {"red": 0.588, "green": 0.392, "blue": 0.059}  # #96640f

# Utility
RH_BLUE        = {"red": 0.0,   "green": 0.4,   "blue": 0.8}    # #0066cc
RH_GREEN       = {"red": 0.243, "green": 0.525, "blue": 0.208}  # #3e8635
```

**Dark mode palette** (when dark mode chosen):

```python
BG_PRIMARY     = GRAY_95       # slide backgrounds
BG_SECONDARY   = GRAY_80       # alternate/card backgrounds
TEXT_PRIMARY   = WHITE          # main text
TEXT_SECONDARY = GRAY_40        # subtitles, descriptions
TEXT_MUTED     = GRAY_60        # footers, references
ACCENT         = RH_RED         # highlights, accent bars
```

**Light mode palette**:

```python
BG_PRIMARY     = WHITE          # slide backgrounds
BG_SECONDARY   = GRAY_10        # alternate/card backgrounds
TEXT_PRIMARY   = GRAY_95         # main text
TEXT_SECONDARY = GRAY_60         # subtitles, descriptions
TEXT_MUTED     = RH_GRAY         # footers, references
ACCENT         = RH_RED          # highlights, accent bars
```

**Expressive Dark mode palette** (purple/teal accents for creative decks):

```python
PURPLE_80      = {"red": 0.106, "green": 0.051, "blue": 0.200}  # #1b0d33
PURPLE_70      = {"red": 0.129, "green": 0.075, "blue": 0.302}  # #21134d
BLACK          = {"red": 0.0,   "green": 0.0,   "blue": 0.0}    # #000000
PURPLE_20      = {"red": 0.816, "green": 0.773, "blue": 0.957}  # #d0c5f4
PURPLE_30      = {"red": 0.714, "green": 0.651, "blue": 0.914}  # #b6a6e9

BG_PRIMARY     = PURPLE_80      # slide backgrounds
BG_SECONDARY   = BLACK          # alternate/card backgrounds
BG_SURFACE     = PURPLE_70      # card/panel backgrounds
TEXT_PRIMARY   = WHITE           # main text
TEXT_SECONDARY = PURPLE_20       # subtitles, descriptions
TEXT_MUTED     = PURPLE_30       # footers, references
ACCENT         = RH_RED          # highlights, accent bars
HIGHLIGHT_TEAL = TEAL_50         # secondary accent for data, positive indicators
HIGHLIGHT_PURPLE = PURPLE_40     # tertiary accent for tags, categories
```

Use Expressive Dark for topics like AI, innovation, future strategy, or
creative workshops where a more energetic visual tone is appropriate.
Standard Dark mode remains the default for most corporate presentations.

If the user specifies a different brand, derive a palette from their brand
colors using the same light-tint / dark-shade pattern above.

### Slide Patterns

Use these proven patterns for professional layouts. Every pattern is built
entirely from shapes and text boxes on a BLANK slide — never rely on
template layout placeholders.

- **Title slide** — MANDATORY: use `build_title_slide()` from `helpers.py` (see A3 above). Do NOT hand-build this slide.
- **Agenda slide** — MANDATORY: use `build_agenda_slide()` from `helpers.py`. Icon lookup is MANDATORY-FIRST (see A4b): search the Icon Repository for EVERY agenda item BEFORE calling this function, and pass each resolved `contentUrl` as that item's `icon_url`. **NEVER mix icons and numbered badges on the same slide** — `build_agenda_slide()` enforces this: if even one item is missing `icon_url`, it silently forces ALL items to numbered badges instead of rendering a mixed slide (verified — see below). This means the real work is upstream: keep searching until every item has a reasonable icon, including approximate/metaphorical matches (e.g. a connectivity/link icon for a cross-site replication topic, a generic info icon for a scope/requirements item) — don't settle for `None` just because there's no exact-name match. Only fall back to a fully-badged slide when the topic set genuinely has no reasonable icon coverage at all. Verified by rendering two real test agendas: a mixed one (confirmed broken/inconsistent-looking) and the corrected all-icons version where every one of 4 items — including two initially-"no match" topics — got a real, on-topic icon:

```python
items = [
    {"title": "Requirements & Constraints", "description": "...", "icon_url": INFO_ICON_URL},
    {"title": "Red Hat GFS2 Architecture", "description": "...", "icon_url": RHEL_ICON_URL},
    {"title": "IBM Storage Scale (GPFS)", "description": "...", "icon_url": CONNECTIVITY_ICON_URL},  # metaphorical match: cross-site link
    {"title": "Backup, DR & Support Boundaries", "description": "...", "icon_url": BACKUP_ICON_URL},
]
build_agenda_slide(reqs, slide_id, "Agenda", "What we will cover today", items, slide_num=2)
```

Row slots subdivide the content zone evenly so any item count (2-8) fits without overflow.
- **Comparison / two-column** — colored header rectangles (one per column, e.g., green vs orange), bullet points below each header as text boxes, background panel rectangles behind each column in pastel tint
- **Card grid** — 2×2 layout with colored header bars and white body with border
- **Timeline (horizontal)** — horizontal gray line as axis, colored circles (dots) at each milestone, pastel-filled rectangles above the line for version info, text labels for dates below. Use distinct colors per status (green=active, orange=warning, red=EOL)
- **Split columns** — left problem / right solution, colored headers
- **Metric callouts** — rounded-rect with large number + label beside it
- **FROM → TO table** — alternating rows, red tint for "from", green tint for "to"
- **Thank You slide** (last slide) — MANDATORY: use `build_thank_you_slide()` from `helpers.py` (see A3 above). Do NOT hand-build this slide.
- **Quote slide** — large pull quote (18-22pt Red Hat Display, light weight), attribution below in smaller Red Hat Text, red accent bar on left edge, BG_SECONDARY background
- **Big Number / Stat slide** — one giant number (36-48pt Red Hat Display Bold, ACCENT color), context label below (10-12pt), optional delta indicator (arrow or +/- in TEAL_50 or RH_RED)
- **Flowchart / Decision slide** — dark rectangle for decision question at top, colored rectangles for options below, small arrow shapes (triangle/rectangle) connecting elements vertically, 3 destination boxes at bottom
- **Upgrade/Process Path diagram** — colored background panels per path (pastel), white boxes for each state/step, small filled rectangles as directional arrows between boxes, label text below or beside each path, "RECOMMENDED" badge (green rounded-rect) on preferred path

### v2.0 Diagram & Visual Patterns

These patterns were added in v2.0 and live in `helpers.py` alongside the
existing build patterns. Import them via `from helpers import *`.

#### Pattern: Split-Layout with Image (text + illustration)

Use for concept slides where one half explains in bullets and the other
half shows an AI-generated illustration, photo, or screenshot.

```python
s = uid()
reqs.append(create_slide(s))
build_split_image_slide(reqs, s,
    title="Prefill Is Compute, Decode Is Memory",
    subtitle=None,
    bullets=[
        "PREFILL: processes entire input in parallel on GPU",
        "Produces the first token (TTFT metric)",
        "DECODE: generates tokens one at a time",
        "Memory-bound — limited by KV cache access speed",
    ],
    image_url="https://example.com/illustration.png",
    slide_num=4,
    color_mode=COLOR_MODE,
    image_side="right")   # or "left"
```

Image must be a publicly-fetchable URL (raw.githubusercontent.com is best).
The image auto-centers vertically in the content zone and respects the
footer boundary.

#### Pattern: Diagram Image Slide (full-width diagram)

Use for pre-rendered diagrams (draw.io exports, architecture PNGs, etc.)
that should fill most of the content zone.

```python
s = uid()
reqs.append(create_slide(s))
build_diagram_image_slide(reqs, s,
    title="KServe Separates Runtime from Model",
    subtitle="Platform teams own ServingRuntime, data scientists own InferenceService",
    image_url="https://example.com/kserve-sketch.png",
    slide_num=5,
    color_mode=COLOR_MODE,
    image_scale=0.85)   # 0.0-1.0, fraction of content zone
```

For draw.io sketch diagrams, export at 2x scale for crisp display. Use
`sketch=1, curveFitting=1, jiggle=2` in draw.io XML for hand-drawn style.
Set `fontColor=#FFFFFF` on edge labels when using dark backgrounds.

#### Pattern: Connected Connectors (node-to-node arrows)

Use `create_connector()` to draw real connected lines between shapes.
Connection site indices: 0=top, 1=right, 2=bottom, 3=left.

```python
box_a = add_rounded_rect(reqs, slide_id, "Step A", ...)
box_b = add_rounded_rect(reqs, slide_id, "Step B", ...)
create_connector(reqs, slide_id, box_a, box_b,
    start_site=2, end_site=0,      # bottom of A → top of B
    end_arrow="OPEN_ARROW",
    line_color=TEXT_MUTED,
    weight_pt=1.5)
```

Arrow styles: `"NONE"`, `"OPEN_ARROW"`, `"FILL_ARROW"`,
`"FILL_CIRCLE"`, `"FILL_SQUARE"`, `"FILL_DIAMOND"`.

#### Pattern: Data-Driven Diagram (nodes + edges)

Use for architecture diagrams, flowcharts, or any graph that can be
expressed as a list of positioned nodes and edges between them.

```python
nodes = [
    {"id": "user",  "label": "User Request",     "x": 3.5, "y": 0.0, "w": 2.0, "h": 0.5,
     "color": TEAL_50, "text_color": WHITE},
    {"id": "route", "label": "Istio Gateway",     "x": 3.5, "y": 0.9, "w": 2.0, "h": 0.5},
    {"id": "kserve","label": "KServe Predictor",  "x": 3.5, "y": 1.8, "w": 2.0, "h": 0.5,
     "color": PURPLE_50, "text_color": WHITE},
    {"id": "gpu",   "label": "GPU Pod (vLLM)",    "x": 3.5, "y": 2.7, "w": 2.0, "h": 0.5,
     "color": RH_RED, "text_color": WHITE},
]
edges = [
    {"from_id": "user",  "to_id": "route"},
    {"from_id": "route", "to_id": "kserve"},
    {"from_id": "kserve","to_id": "gpu"},
]
s = uid()
reqs.append(create_slide(s))
build_diagram_from_data(reqs, s,
    title="Request Flows Through Four Layers",
    subtitle="Each layer adds routing, scaling, or runtime logic",
    nodes=nodes, edges=edges,
    slide_num=6, color_mode=COLOR_MODE)
```

Node coordinates (`x`, `y`) are in inches relative to the content zone
origin (top-left of content area). The function clamps all nodes to
`CONTENT_TOP_Y` / `CONTENT_BOT_Y`. Optional per-node keys: `shape`
(`"ROUND_RECTANGLE"`, `"RECTANGLE"`, `"ELLIPSE"`), `font_size` (int, pt).

### Diagram Building Technique (Layered Shapes)

Diagrams are built using a layered approach — background panels first,
then content elements on top:

1. **Background panel** — large `RECTANGLE` with pastel fill (e.g., #E6F4F5
   for blue-tint, #E8F5E9 for green-tint, #FEF5E5 for orange-tint,
   #FDEDED for red-tint). No outline or thin gray outline.
2. **Content boxes** — smaller `RECTANGLE` with white fill (#FFFFFF) and
   light gray outline, placed inside the background panel.
3. **Text labels** — `TEXT_BOX` positioned on top of or inside each box.
4. **Connector arrows** — small filled `RECTANGLE` (e.g., 0.6"×0.35")
   with solid color matching the path's theme color, placed between boxes.
5. **Accent dots** — small `ELLIPSE` shapes with solid fill, used as
   timeline markers or status indicators.
6. **Red accent bar** — every content slide gets a full-width (10") red rectangle
   at y=0, height 0.06". Use `add_red_accent_bar()` function — do NOT hardcode.

```python
# Pastel background colors for diagram panels
PANEL_BLUE   = {"red": 0.902, "green": 0.957, "blue": 0.961}   # #E6F4F5
PANEL_GREEN  = {"red": 0.910, "green": 0.961, "blue": 0.914}   # #E8F5E9
PANEL_ORANGE = {"red": 0.996, "green": 0.961, "blue": 0.898}   # #FEF5E5
PANEL_RED    = {"red": 0.992, "green": 0.929, "blue": 0.929}   # #FDEDED
PANEL_GRAY   = {"red": 0.910, "green": 0.922, "blue": 0.941}   # #E8EBF0
```

### Typography

Always use the official Red Hat font families (available in Google Slides via Google Fonts).
Do not use Arial — Red Hat fonts are always available in Google Slides.

- **Red Hat Display** — slide titles, headlines, large impact text (bold, expressive)
- **Red Hat Text** — body copy, descriptions, bullet points (readable at small sizes)
- **Red Hat Mono** — code snippets, technical labels, tags

| Element        | Font Family      | Font Size | Weight | Color          |
|---------------|-----------------|-----------|--------|----------------|
| Slide title    | Red Hat Display  | 24-32 pt  | Bold   | TEXT_PRIMARY    |
| Section header | Red Hat Display  | 14-18 pt  | Bold   | TEXT_PRIMARY    |
| Body text      | Red Hat Text     | 12-14 pt  | Regular| TEXT_PRIMARY    |
| Subtitle/desc  | Red Hat Text     | 11-12 pt  | Regular| TEXT_SECONDARY  |
| Metric number  | Red Hat Display  | 20-28 pt  | Bold   | ACCENT or WHITE |
| Code/tags      | Red Hat Mono     | 10-12 pt  | Regular| TEXT_SECONDARY  |
| Slide number   | Red Hat Text     | 8 pt      | Regular| TEXT_MUTED      |

Font size guidance: use the LARGER end of each range when the slide has
fewer items (3-4 bullets). Only use the smaller end when fitting 6+ items.
The goal is to fill the full slide canvas — avoid leaving large empty areas.

### Slide Headlines

Headlines are **assertions, not labels**. A reader who only reads the slide
headlines should understand the full message of the deck.

**Per slide type:**

- **Title slide** — Bad: "Project Update" / Good: "Satellite 6.16 Cuts Patch Cycles From Days to Minutes"
- **Agenda slide** — Bad: "Agenda" / Good: "Three Shifts That Change How We Operate"
- **Comparison slide** — Bad: "Before and After" / Good: "Migration Cuts Deployment Time From 4 Hours to 12 Minutes"
- **Big Number slide** — Bad: "Key Metrics" / Good: "73% of Enterprise AI Runs Behind the Firewall"
- **Architecture slide** — Bad: "System Architecture" / Good: "Three Layers Separate Data Gravity From Compute"
- **Quote slide** — Bad: "Expert Opinion" / Good: "The Future of AI Is Local — Gartner VP, 2026"
- **Timeline slide** — Bad: "Project Timeline" / Good: "From Pilot to Production in 90 Days"
- **Card grid slide** — Bad: "Features" / Good: "Four Capabilities That Eliminate Manual Toil"
- **Split columns slide** — Bad: "Problem and Solution" / Good: "Legacy VMs Lock You In; OpenShift Virtualization Sets You Free"
- **Metric callouts slide** — Bad: "Performance Numbers" / Good: "3.2x Throughput With Half the Infrastructure"
- **Closing slide** — Bad: "Next Steps" / Good: "Start With a 30-Day Proof of Concept — Zero Commitment"

### MANDATORY LAYOUT CONSTANTS (10" × 5.625")

**CRITICAL: Copy this ENTIRE constants block into the top of every build script.
ALL coordinates in this skill are for 10" × 5.625" slides. Do NOT use any
other coordinate system. Do NOT guess positions — use ONLY these constants.**

```python
# ================================================================
# LAYOUT CONSTANTS — COPY THIS BLOCK VERBATIM INTO EVERY SCRIPT
# Slide size: 10" × 5.625" (default Google Slides widescreen)
# 1 inch = 914400 EMU
# ================================================================

SLIDE_W = 9144000   # 10.00" — full slide width
SLIDE_H = 5143500   # 5.625" — full slide height

# ---- Margins ----
MARGIN_L = 457200    # 0.50" left margin
MARGIN_R = 457200    # 0.50" right margin

# ---- Usable content area ----
CONTENT_X = MARGIN_L                         # 457200 EMU = 0.50"
CONTENT_W = SLIDE_W - MARGIN_L - MARGIN_R    # 8229600 EMU = 9.00"

# ---- Red accent bar (top of every content slide) ----
ACCENT_BAR_Y = 0
ACCENT_BAR_W = SLIDE_W    # 9144000 = full slide width
ACCENT_BAR_H = 54864      # 0.06"

# ---- Title zone ----
TITLE_X = MARGIN_L         # 457200 EMU = 0.50"
TITLE_Y = 137160           # 0.15" from top (below accent bar)
TITLE_W = 7772400          # 8.50" — leaves room on right
TITLE_H = 457200           # 0.50" — fits one line at 24-32pt

# ---- Subtitle zone (immediately below title) ----
SUBTITLE_X = MARGIN_L      # 457200 EMU = 0.50"
SUBTITLE_Y = 594360        # 0.65" from top = TITLE_Y + TITLE_H
SUBTITLE_W = CONTENT_W     # 8229600 EMU = 9.00"
SUBTITLE_H = 228600        # 0.25"

# ---- Content zone HARD BOUNDARIES ----
CONTENT_TOP_Y = 914400     # 1.00" — ABSOLUTE MINIMUM y for content panels
CONTENT_BOT_Y = 4389120    # 4.80" — ABSOLUTE MAXIMUM bottom edge for content
CONTENT_ZONE_H = CONTENT_BOT_Y - CONTENT_TOP_Y  # 3474720 EMU = 3.80"

# ---- Footer zone (below 4.80" — logo and slide number ONLY) ----
LOGO_Y = 4663440            # 5.10" (logo Y — X is computed from logo width)
SLIDENUM_X = 457200         # 0.50" (slide number: bottom-LEFT)
SLIDENUM_Y = 4663440        # 5.10"

# ---- Column presets (x positions and widths) ----
# Two columns (0.20" gap)
COL2_GAP = 182880
COL2_W = (CONTENT_W - COL2_GAP) // 2            # 4023360 EMU = 4.40"
COL2_LEFT_X = CONTENT_X                          # 457200
COL2_RIGHT_X = CONTENT_X + COL2_W + COL2_GAP     # 4663440

# Three columns (0.15" gap)
COL3_GAP = 137160
COL3_W = (CONTENT_W - 2 * COL3_GAP) // 3         # 2651760 EMU = 2.90"
COL3_1_X = CONTENT_X                              # 457200
COL3_2_X = CONTENT_X + COL3_W + COL3_GAP          # 3246120
COL3_3_X = CONTENT_X + 2 * (COL3_W + COL3_GAP)    # 6035040

# Four columns (0.13" gap)
COL4_GAP = 118872
COL4_W = (CONTENT_W - 3 * COL4_GAP) // 4          # 1968246 EMU = 2.15"
COL4_1_X = CONTENT_X                               # 457200
COL4_2_X = CONTENT_X + 1 * (COL4_W + COL4_GAP)     # 2544318
COL4_3_X = CONTENT_X + 2 * (COL4_W + COL4_GAP)     # 4631436
COL4_4_X = CONTENT_X + 3 * (COL4_W + COL4_GAP)     # 6718554
```

**RULES — VIOLATIONS PRODUCE BROKEN SLIDES:**
1. Every content element's `translateY` MUST be >= `CONTENT_TOP_Y` (914400 EMU = 1.00")
2. Every content element's bottom edge (`translateY + height`) MUST be <= `CONTENT_BOT_Y` (4389120 EMU = 4.80")
3. Title MUST use `TITLE_X`, `TITLE_Y`, `TITLE_W`, `TITLE_H` — no other position
4. Subtitle MUST use `SUBTITLE_X`, `SUBTITLE_Y` — no other position
5. Column widths MUST use `COL2_W`, `COL3_W`, or `COL4_W` — no manual calculation
6. Do NOT leave large empty areas — content should fill 80%+ of the content zone

### MANDATORY Content Sizing Rules

These rules prevent the #1 visual defect — text overflowing its box. The model
MUST follow every rule below. Violations produce broken slides that require
manual cleanup.

#### Title Sizing

| Font Size | Max Characters | Max Width |
|-----------|---------------|-----------|
| 32 pt     | 45 chars      | 8.5"      |
| 28 pt     | 55 chars      | 8.5"      |
| 24 pt     | 65 chars      | 9.0"      |
| 20 pt     | 80 chars      | 9.0"      |

If a title exceeds these limits, either shorten the text or reduce the font
size. Titles MUST fit on a single line — never allow a title to wrap to a
second line. A wrapped title pushes all content down and causes cascade
overflow on the rest of the slide.

#### Text Box Height Formula (MANDATORY)

For EVERY text box, calculate the required height BEFORE creating it:

```python
def calc_box_height(text, font_size_pt, box_width_inches):
    """Calculate minimum box height in EMU. ALWAYS use this before creating text boxes."""
    avg_char_width_pt = font_size_pt * 0.55  # average char width ~ 55% of font size
    chars_per_line = int((box_width_inches * 72) / avg_char_width_pt)
    lines = text.split('\n')
    total_lines = 0
    for line in lines:
        if len(line) == 0:
            total_lines += 1
        else:
            total_lines += max(1, -(-len(line) // chars_per_line))  # ceiling division
    line_height_emu = int(font_size_pt * 1.5 * 12700)  # 1.5x line spacing
    padding_emu = 100000  # ~0.11" padding
    return total_lines * line_height_emu + padding_emu
```

NEVER hardcode text box heights. ALWAYS compute them from the actual text
content using the formula above or equivalent logic. This is the single most
important rule for preventing overflow.

#### Bullet Content Limits Per Column

| Column Width | Font Size | Max Bullets | Max Chars Per Bullet |
|-------------|-----------|-------------|---------------------|
| 4.0-4.5"    | 12 pt     | 7           | 180                 |
| 4.0-4.5"    | 14 pt     | 6           | 140                 |
| 2.5-3.0"    | 12 pt     | 6           | 120                 |
| 2.5-3.0"    | 14 pt     | 5           | 90                  |
| Full 9.0"   | 12 pt     | 8           | 350                 |
| Full 9.0"   | 14 pt     | 7           | 280                 |

When content exceeds these limits, SPLIT into two slides rather than
shrinking fonts below 12pt or overflowing the box.

#### Footer Protection Zone (HARD BOUNDARY)

```
                    10.00" (9144000 EMU)
y = 0.00" (0)      +----------------------------------+
                    |  Red accent bar (0.06")          |
y = 0.15" (137160) |  TITLE (0.50" tall)               |
y = 0.65" (594360) |  SUBTITLE (0.25" tall)            |
y = 1.00" (914400) |==================================| <- CONTENT STARTS HERE
                    |                                    |
                    |  CONTENT ZONE (3.80" tall)         |
                    |  All panels, boxes, text HERE      |
                    |                                    |
y = 4.80" (4389120)|==================================| <- CONTENT STOPS HERE
                    |  FOOTER ZONE (0.825")              |
y = 5.10" (4663440)|  Slide# (left)    Logo (right)    |
y = 5.625"(5143500)+----------------------------------+
```

**ABSOLUTE RULES:**
- NO content element may have `translateY` < 914400 (1.00") except title/subtitle
- NO content element bottom edge (`translateY + height`) > 4389120 (4.80")
- ONLY logo and slide number may exist below y=4.80"

#### MANDATORY Slide Element Functions

**EVERY content slide MUST use these functions. Do NOT create title, subtitle,
or content panels with custom coordinates. These functions enforce the correct
positions.**

```python
def add_slide_title(reqs, slide_id, title_text, font_size=28):
    """Add title at the CORRECT position. MUST be used for every content slide title.
    Font size 28pt fits ~55 chars. If title is longer, use 24pt (65 chars max)."""
    if len(title_text) > 55 and font_size >= 28:
        font_size = 24  # auto-downsize for long titles
    if len(title_text) > 65 and font_size >= 24:
        font_size = 20  # further downsize
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid, "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": TITLE_W, "unit": "EMU"},
                     "height": {"magnitude": TITLE_H, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": TITLE_X, "translateY": TITLE_Y, "unit": "EMU"}
        }
    }})
    reqs.append({"insertText": {"objectId": sid, "text": title_text}})
    reqs.append({"updateTextStyle": {
        "objectId": sid,
        "fields": "fontFamily,fontSize,foregroundColor,bold",
        "style": {"fontFamily": "Red Hat Display",
                  "fontSize": {"magnitude": font_size, "unit": "PT"},
                  "foregroundColor": {"opaqueColor": {"rgbColor": TEXT_PRIMARY}},
                  "bold": True}
    }})
    reqs.append(set_text_autofit(sid))
    return sid

def add_slide_subtitle(reqs, slide_id, subtitle_text):
    """Add subtitle at the CORRECT position (below title). MUST use for every subtitle."""
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid, "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": SUBTITLE_W, "unit": "EMU"},
                     "height": {"magnitude": SUBTITLE_H, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": SUBTITLE_X, "translateY": SUBTITLE_Y, "unit": "EMU"}
        }
    }})
    reqs.append({"insertText": {"objectId": sid, "text": subtitle_text}})
    reqs.append({"updateTextStyle": {
        "objectId": sid,
        "fields": "fontFamily,fontSize,foregroundColor",
        "style": {"fontFamily": "Red Hat Text",
                  "fontSize": {"magnitude": 12, "unit": "PT"},
                  "foregroundColor": {"opaqueColor": {"rgbColor": TEXT_SECONDARY}}}
    }})
    reqs.append(set_text_autofit(sid))
    return sid

def add_content_panel(reqs, slide_id, x, y, w, h, bg_color, outline_color=None):
    """Add a background panel/card in the CONTENT ZONE.
    ENFORCES: y >= CONTENT_TOP_Y and y+h <= CONTENT_BOT_Y.
    Will raise ValueError if coordinates violate boundaries."""
    if y < CONTENT_TOP_Y:
        y = CONTENT_TOP_Y  # FORCE content below title area
    if y + h > CONTENT_BOT_Y:
        h = CONTENT_BOT_Y - y  # CLAMP to content zone
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid, "shapeType": "RECTANGLE",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": w, "unit": "EMU"},
                     "height": {"magnitude": h, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": x, "translateY": y, "unit": "EMU"}
        }
    }})
    reqs.append({"updateShapeProperties": {
        "objectId": sid,
        "fields": "shapeBackgroundFill.solidFill.color",
        "shapeProperties": {"shapeBackgroundFill": {"solidFill": {
            "color": {"rgbColor": bg_color}}}}
    }})
    if outline_color:
        reqs.append({"updateShapeProperties": {
            "objectId": sid,
            "fields": "outline.outlineFill.solidFill.color,outline.weight",
            "shapeProperties": {"outline": {"outlineFill": {"solidFill": {
                "color": {"rgbColor": outline_color}}},
                "weight": {"magnitude": 12700, "unit": "EMU"}}}
        }})
    else:
        reqs.append({"updateShapeProperties": {
            "objectId": sid,
            "fields": "outline.outlineFill.solidFill.color,outline.weight",
            "shapeProperties": {"outline": {"outlineFill": {"solidFill": {
                "color": {"rgbColor": bg_color}}},
                "weight": {"magnitude": 0, "unit": "EMU"}}}
        }})
    return sid

def add_content_text(reqs, slide_id, x, y, w, text, font_size=12,
                     font_family="Red Hat Text", color=None, bold=False):
    """Add a text box in the CONTENT ZONE. Auto-calculates height.
    ENFORCES: y >= CONTENT_TOP_Y."""
    if color is None:
        color = TEXT_PRIMARY
    if y < CONTENT_TOP_Y:
        y = CONTENT_TOP_Y
    h = calc_box_height(text, font_size, w / 914400)
    if y + h > CONTENT_BOT_Y:
        h = CONTENT_BOT_Y - y
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid, "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": w, "unit": "EMU"},
                     "height": {"magnitude": h, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": x, "translateY": y, "unit": "EMU"}
        }
    }})
    if text:
        reqs.append({"insertText": {"objectId": sid, "text": text}})
        reqs.append({"updateTextStyle": {
            "objectId": sid,
            "fields": "fontFamily,fontSize,foregroundColor,bold",
            "style": {"fontFamily": font_family,
                      "fontSize": {"magnitude": font_size, "unit": "PT"},
                      "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                      "bold": bold}
        }})
    reqs.append(set_text_autofit(sid))
    return sid
```

**STOP-AND-CHECK BEFORE EVERY SLIDE:** Before generating code for any slide,
mentally verify: (1) title uses `add_slide_title()`, (2) subtitle uses
`add_slide_subtitle()`, (3) ALL content panels use `add_content_panel()` or
`add_content_text()` with y >= CONTENT_TOP_Y, (4) no element bottom exceeds
CONTENT_BOT_Y. If any check fails, fix BEFORE writing the code.

### MANDATORY Slide Build Patterns

**Every slide MUST follow one of these patterns. Copy the function calls
exactly — do NOT create shapes with custom coordinates.**

#### Pattern: Two-Column Comparison Slide

```python
def build_two_column_slide(reqs, slide_id, title, subtitle, 
                           left_header, left_body, right_header, right_body,
                           left_color, right_color, callout_text=None):
    """Standard two-column slide. COPY THIS PATTERN."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    add_slide_subtitle(reqs, slide_id, subtitle)
    
    panel_h = CONTENT_ZONE_H  # 3474720 EMU = fills content zone
    if callout_text:
        panel_h = CONTENT_ZONE_H - 457200  # leave 0.50" for callout at bottom
    
    # Left panel background
    add_content_panel(reqs, slide_id, COL2_LEFT_X, CONTENT_TOP_Y, COL2_W, panel_h, left_color)
    # Right panel background
    add_content_panel(reqs, slide_id, COL2_RIGHT_X, CONTENT_TOP_Y, COL2_W, panel_h, right_color)
    
    # Left header
    add_content_text(reqs, slide_id, COL2_LEFT_X + 91440, CONTENT_TOP_Y + 45720,
                     COL2_W - 182880, left_header, font_size=16,
                     font_family="Red Hat Display", bold=True)
    # Left body
    add_content_text(reqs, slide_id, COL2_LEFT_X + 91440, CONTENT_TOP_Y + 365760,
                     COL2_W - 182880, left_body, font_size=12)
    # Right header
    add_content_text(reqs, slide_id, COL2_RIGHT_X + 91440, CONTENT_TOP_Y + 45720,
                     COL2_W - 182880, right_header, font_size=16,
                     font_family="Red Hat Display", bold=True)
    # Right body
    add_content_text(reqs, slide_id, COL2_RIGHT_X + 91440, CONTENT_TOP_Y + 365760,
                     COL2_W - 182880, right_body, font_size=12)
    
    # Optional callout at bottom of content zone
    if callout_text:
        callout_y = CONTENT_BOT_Y - 411480  # 0.45" tall box at bottom
        add_content_panel(reqs, slide_id, CONTENT_X, callout_y, CONTENT_W, 365760,
                         {"red": 0.988, "green": 0.890, "blue": 0.890})
        add_content_text(reqs, slide_id, CONTENT_X + 91440, callout_y + 45720,
                         CONTENT_W - 182880, callout_text, font_size=12,
                         color={"red": 0.651, "green": 0.0, "blue": 0.0}, bold=True)
    
    add_rh_logo(reqs, slide_id, COLOR_MODE)
    add_slide_number(reqs, slide_id, slide_num)
```

#### Pattern: Three-Column Slide

```python
def build_three_column_slide(reqs, slide_id, title, subtitle,
                             headers, bodies, colors):
    """Three-column layout. headers/bodies/colors are 3-element lists."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    add_slide_subtitle(reqs, slide_id, subtitle)
    
    col_xs = [COL3_1_X, COL3_2_X, COL3_3_X]
    for i in range(3):
        add_content_panel(reqs, slide_id, col_xs[i], CONTENT_TOP_Y,
                         COL3_W, CONTENT_ZONE_H, colors[i])
        add_content_text(reqs, slide_id, col_xs[i] + 91440, CONTENT_TOP_Y + 45720,
                         COL3_W - 182880, headers[i], font_size=14,
                         font_family="Red Hat Display", bold=True)
        add_content_text(reqs, slide_id, col_xs[i] + 91440, CONTENT_TOP_Y + 365760,
                         COL3_W - 182880, bodies[i], font_size=11)
    
    add_rh_logo(reqs, slide_id, COLOR_MODE)
    add_slide_number(reqs, slide_id, slide_num)
```

#### Pattern: Four-Column Slide

```python
def build_four_column_slide(reqs, slide_id, title, subtitle,
                            headers, bodies, colors):
    """Four-column layout. headers/bodies/colors are 4-element lists."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    add_slide_subtitle(reqs, slide_id, subtitle)
    
    col_xs = [COL4_1_X, COL4_2_X, COL4_3_X, COL4_4_X]
    for i in range(4):
        add_content_panel(reqs, slide_id, col_xs[i], CONTENT_TOP_Y,
                         COL4_W, CONTENT_ZONE_H, colors[i])
        add_content_text(reqs, slide_id, col_xs[i] + 68580, CONTENT_TOP_Y + 45720,
                         COL4_W - 137160, headers[i], font_size=13,
                         font_family="Red Hat Display", bold=True)
        add_content_text(reqs, slide_id, col_xs[i] + 68580, CONTENT_TOP_Y + 320040,
                         COL4_W - 137160, bodies[i], font_size=11)
    
    add_rh_logo(reqs, slide_id, COLOR_MODE)
    add_slide_number(reqs, slide_id, slide_num)
```

#### Pattern: Six-Card Grid (2×3) Slide

```python
def build_card_grid_slide(reqs, slide_id, title, subtitle,
                          card_headers, card_bodies, card_colors):
    """2×3 card grid. card_headers/bodies/colors are 6-element lists."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    add_slide_subtitle(reqs, slide_id, subtitle)
    
    col_xs = [COL2_LEFT_X, COL2_RIGHT_X]
    row_h = (CONTENT_ZONE_H - 2 * 91440) // 3  # 3 rows with gaps
    
    for i in range(6):
        col = i % 2
        row = i // 2
        x = col_xs[col]
        y = CONTENT_TOP_Y + row * (row_h + 91440)
        add_content_panel(reqs, slide_id, x, y, COL2_W, row_h, card_colors[i])
        add_content_text(reqs, slide_id, x + 91440, y + 45720,
                         COL2_W - 182880, card_headers[i], font_size=13,
                         font_family="Red Hat Display", bold=True)
        add_content_text(reqs, slide_id, x + 91440, y + 274320,
                         COL2_W - 182880, card_bodies[i], font_size=11)
    
    add_rh_logo(reqs, slide_id, COLOR_MODE)
    add_slide_number(reqs, slide_id, slide_num)
```

**IMPORTANT: These patterns are EXAMPLES of the correct coordinate usage.
For custom layouts, you MUST still use CONTENT_TOP_Y, CONTENT_BOT_Y,
CONTENT_X, CONTENT_W, and the COL*_X/COL*_W constants. NEVER hardcode
EMU values for element positions — always reference the named constants.**

### Template Artifacts — Must Remove

After duplicating the Red Hat template, the master slide contains placeholder
elements that bleed through onto every slide. You MUST remove these:

- **"Version number here V00000"** — a text placeholder from the master that
  shows on all slides. After creating the presentation, query the slide
  masters/layouts for text elements containing "Version" or "V00000" and
  delete them, OR on each created slide find and delete any inherited text
  element that contains version placeholder text.

Recommended approach — delete version text from all layouts after copying:

```python
def remove_version_placeholders(pres_id):
    """Remove 'Version number' placeholders from all slide layouts."""
    r = subprocess.run(['gws', 'slides', 'presentations', 'get',
        '--params', json.dumps({
            'presentationId': pres_id,
            'fields': 'layouts(objectId,pageElements(objectId,shape(text(textElements(textRun(content))))))'
        })], capture_output=True, text=True)
    lines = r.stdout.strip().split('\n')
    start = next((i for i, l in enumerate(lines) if l.strip().startswith('{')), 0)
    data = json.loads('\n'.join(lines[start:]))
    
    delete_reqs = []
    for layout in data.get('layouts', []):
        for elem in layout.get('pageElements', []):
            shape = elem.get('shape', {})
            text_content = ''
            for te in shape.get('text', {}).get('textElements', []):
                tr = te.get('textRun', {})
                text_content += tr.get('content', '')
            if 'ersion' in text_content or 'V00000' in text_content:
                delete_reqs.append({"deleteObject": {"objectId": elem['objectId']}})
    
    if delete_reqs:
        # Execute deletion
        batch_update(pres_id, delete_reqs)
```

Also add slide numbers manually in the bottom-right corner of each content
slide (skip title slide and closing slide):

```python
def add_slide_number(reqs, slide_id, number):
    """Add page number in bottom-right corner.
    Position: SLIDENUM_X, SLIDENUM_Y (9.10", 5.10") for 10" × 5.625" slides."""
    sid = uid()
    reqs.append({"createShape": {
        "objectId": sid,
        "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": 457200, "unit": "EMU"},
                     "height": {"magnitude": 228600, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": SLIDENUM_X, "translateY": SLIDENUM_Y,
                          "unit": "EMU"}
        }
    }})
    reqs.append({"insertText": {
        "objectId": sid,
        "text": str(number)
    }})
    reqs.append({"updateTextStyle": {
        "objectId": sid,
        "fields": "fontFamily,fontSize,foregroundColor",
        "style": {
            "fontFamily": "Red Hat Text",
            "fontSize": {"magnitude": 8, "unit": "PT"},
            "foregroundColor": {"opaqueColor": {"rgbColor": TEXT_MUTED}}
        }
    }})
```

## Gotchas

### REST API via gws (Approach A)

1. **`gws` prints keyring messages to stdout** — when parsing JSON output,
   skip lines until you find one starting with `{`
2. **`insertText` with empty string** — does NOT add text but the API
   returns success. Subsequent `updateTextStyle` will fail with "object has
   no text". Always guard: `if text:`
3. **batchUpdate is sequential** — requests execute in order. Create slide
   before adding shapes to it. Create shape before styling it.
4. **Object IDs must be unique** and start with a letter — use `"e" + uuid`
5. **Chunk boundaries** — if a create + style pair spans a chunk boundary,
   the style request references an object from the previous chunk, which is
   fine (already committed). But `insertText` + `updateTextStyle` for the
   same shape should be in the same chunk.
6. **Max ~2000 requests per batchUpdate** — keep chunks at 200 for safety
7. **Colors are 0-1 float RGB** — not 0-255. Convert hex: `0xEE/255 = 0.933`

### Apps Script (Approach B)

1. **First-run authorization** — the script needs manual authorization the
   first time. Open it in the browser and run once to grant permissions.
2. **Execution time limit** — Apps Script has a 6-minute execution limit.
   For very large decks (30+ slides), split into multiple function calls.
3. **Colors are hex strings** — use `"#ee0000"` format, not RGB floats.
4. **Image insertion** — `slide.insertImage(url)` works directly.
