---
name: google-slides-agenda
description: >-
  Create a professional Red Hat branded agenda slide in Google Slides with official
  Red Hat icons from the Icon Repository. Use when the user asks to "create an agenda",
  "add agenda slide", "make an agenda", or any request to add an agenda/table-of-contents
  slide to a Google Slides presentation.
---

# Google Slides Agenda Slide Creator

Create a polished agenda slide using official Red Hat icons sourced from the
Red Hat Icon Repository presentation in Google Drive.

## Design Specification

The agenda slide follows Red Hat brand guidelines with this exact layout:

- White background (use presentation's built-in blank layout)
- Full-width Red Hat Red header banner at top (10" wide, 0.8" tall)
- "Agenda" text inside the header: white, Red Hat Display Bold, 28pt, positioned at x=0.5"
- Agenda items listed vertically below the header, filling the slide height
- Each item has: an official Red Hat icon (0.32" x 0.32") + text label (Red Hat Text, 18pt, dark)
- Items start at y=1.0" with ~0.47" spacing (adjust based on item count to fill slide)
- Icon position: x=0.4", text position: x=1.1"
- Text color: near-black `{"red": 0.102, "green": 0.102, "blue": 0.102}`
- Header color: Red Hat Red `{"red": 0.933, "green": 0.0, "blue": 0.0}`
- No red accent bar/tape below header — just the header block itself
- Cover "V0000000" footer text with a white rectangle (1.5" x 0.35" at x=10.2", y=6.85")

## Icon Source

Icons come from the **Red Hat Icon Repository** presentation in Google Drive:
- Presentation ID: `1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM`
- DO NOT modify this presentation — only read from it

### How to get icon thumbnails

1. Get the Icon Repository presentation structure:
   ```
   gws slides presentations get --params '{"presentationId":"1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM"}'
   ```

2. Each slide in the Icon Repository contains one icon. The slide's text content
   or speaker notes describe the icon name/category.

3. Get a thumbnail URL for a specific slide:
   ```
   gws slides presentations pages getThumbnail --params '{"presentationId":"1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM","pageObjectId":"<SLIDE_ID>","thumbnailProperties.thumbnailSize":"LARGE"}'
   ```

4. Use the thumbnail URL in `createImage` to insert the icon into the target presentation.

### Common icon mappings

Use these icon categories as a guide when selecting icons for agenda items:

| Topic Type | Suggested Icon Name | Category |
|---|---|---|
| Overview / Intro | Info | Shapes and signage |
| Architecture | Architecture | Diagrams and graphs |
| Deployment | Cloud | Software and technologies |
| Configuration / Integration | Gear | Objects |
| Backup / Recovery / Rollback | Backup recovery | Software and technologies |
| Security / RBAC | Secured | Software and technologies |
| Multiple apps / Sets | Apps | Software and technologies |
| Webhooks / Automation | Web hooks | Software and technologies |
| Best practices / Validation | Checkbox (Checked) | Shapes and signage |
| Monitoring / Observability | Monitoring | Software and technologies |
| Networking | Network | Software and technologies |
| Storage | Storage | Software and technologies |
| Users / Teams | Users | People |

## Implementation Steps

### Step 1 — Identify target presentation and slide position

Get the target presentation ID and determine where the agenda slide should go
(typically index 1, making it slide 2 after the title).

### Step 2 — Gather agenda items from user

Ask the user for the list of agenda topics, or infer from the presentation content.

### Step 3 — Match icons to agenda items

Search the Icon Repository for icons matching each agenda topic. Use the
common mappings table above as a starting point.

### Step 4 — Write Python builder script

Create a Python script that:

1. Creates a new slide at the target position
2. Adds the red header rectangle with "Agenda" text
3. For each agenda item:
   - Gets the icon thumbnail URL from the Icon Repository
   - Inserts the icon image at the correct position using `createImage`
   - Adds the text label using `createShape` (TEXT_BOX) + `insertText`
4. Adds the V0000000 cover rectangle
5. Executes via `gws slides presentations batchUpdate`

### Key API details

- Object IDs: `"e" + uuid.uuid4().hex[:10]`
- Units: EMU (1 inch = 914400 EMU, 1 pt = 12700 EMU)
- Slide dimensions: 10" wide x 5.625" tall (widescreen)
- Chunk size: max 200 requests per batchUpdate
- Never `insertText` with empty string
- Guard text operations: `if text:`
- Use `gws slides presentations batchUpdate --params '{"presentationId":"<ID>"}' --json '<body>'`

### Step 5 — Execute and verify

Run the script. If it fails, create a fresh slide and retry (do not retry on
the same broken slide).

## Example Usage

When the user says: "Create an agenda slide for my GitOps presentation"

1. Read the presentation to understand existing content
2. Ask/infer agenda items (or use presentation section titles)
3. Match each item to a Red Hat icon
4. Build the slide with header + icons + labels
5. Confirm success and share the slide URL
