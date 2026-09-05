# Red Hat Standard Presentation Template -- Layout Reference

This document catalogs all available layouts in the official Red Hat Google Slides template. When building presentations, duplicate this template and use its layouts to get correct branding, fonts, logos, and color treatment automatically.

## Template Details

- Drive File ID: `1qQVmS7LI9KE4zOjJarALRNOI69UbV_452-Bp02IKEaI`
- Masters: Two (light mode and dark mode)
- Branding elements (Red Hat logo, corporate fonts, color palette) are baked into the master slides and inherited by every layout.

## How to Create a New Presentation from This Template

Duplicate the template into the user's Drive:

```
gws drive files copy \
  --params '{"fileId": "1qQVmS7LI9KE4zOjJarALRNOI69UbV_452-Bp02IKEaI"}' \
  --json '{"name": "Your Deck Title"}'
```

The response returns the new file's `id`. Use that ID for all subsequent Slides API calls.

## Skill Pattern to Layout Mapping

When the skill needs a particular slide type, use the layout listed below. Light mode layouts are the default; use dark mode equivalents when the user requests a dark theme.

- Title / opening slide --> "Title" (g3b0f681f8ea_0_321 or g3b0f681f8ea_0_371)
- Title slide with background image --> "Title slide with image" (g3b0f681f8ea_0_439)
- Webinar / event title --> "Webinar title slide" (g3b0f681f8ea_0_580)
- Closing / thank-you slide --> "Closing" (g3b0f681f8ea_0_330 or g3b0f681f8ea_0_380)
- Closing with background image --> "Closing slide with image" (g3b0f681f8ea_0_543)
- Section divider --> "Divider with title" (g3b0f681f8ea_0_605)
- Section divider with subtitle --> "Divider with title and subhead" (g3b0f681f8ea_0_704)
- Agenda / table of contents --> "Interior agenda" (g3b0f681f8ea_0_970 or g3b62c9604b6_0_44)
- Overview / executive summary --> "Interior overview" (g3925d247048_4_16 or g3b62c9604b6_0_25)
- Callout / key message --> "Interior callout" (g3b0f681f8ea_0_740)
- Body text (title + body) --> "Interior title and body" (g3925d247048_4_235)
- Body text (title, subhead, body) --> "Interior title, subhead, and body" (g3925d247048_4_202)
- Body text only --> "Interior body" (g3925d247048_4_254)
- Two-column body --> "Interior title and two column body" (g3925d247048_4_273)
- Column body --> "Interior title and column body" (g3925d247048_4_299)
- Comparison / 2x2 grid --> "Interior two by two" (g3925d247048_4_747)
- Three-column layout --> "Interior three column" (g3925d247048_4_922)
- Four-column layout --> "Interior four column" (g3925d247048_4_800)
- Timeline (vertical) --> "Interior timeline vertical" (g3925d247048_4_321)
- Timeline (horizontal) --> "Interior timeline horizontal" (g3925d247048_4_351)
- Data with three callouts --> "Interior data three callouts" (g3925d247048_4_394)
- Data with two callouts --> "Interior data two callouts" (g3925d247048_4_449)
- Pie charts (two) --> "Interior data two pies" (g3925d247048_4_498)
- Pie chart (large) --> "Interior data large pie" (g3925d247048_4_545)
- Quote (three-column) --> "Interior quote three column" (g3925d247048_4_600)
- Quote (two-column) --> "Interior quote two column" (g3925d247048_4_658)
- Quote (large / single) --> "Interior quote large" (g3925d247048_4_708)
- Full-width image --> "Full-width image" (g3b0f681f8ea_0_902)
- Image with text on right --> "Interior image left" (g3925d247048_4_975)
- Title left-aligned --> "Interior title left" (g3925d247048_4_862)
- Large text / headline --> "Interior large text" (g3925d247048_4_1004)
- Process (three steps) --> "Interior three chevrons" (g3925d247048_4_47)
- Process (two steps) --> "Interior two chevrons" (g3925d247048_4_85)
- Blank with header --> "Interior blank" (g3925d247048_4_176)
- Interior title only --> "Interior title" (g3b0f681f8ea_0_915)

## Light Mode Layouts (First Master)

### Title Slides

| Layout Name | Predefined Type | objectId |
|---|---|---|
| Title | TITLE_1 | g3b0f681f8ea_0_321 |
| Title | TITLE_3 | g3b0f681f8ea_0_371 |
| Title slide with image | TITLE_1_2_2_1 | g3b0f681f8ea_0_439 |
| Webinar title slide | -- | g3b0f681f8ea_0_580 |

### Closing Slides

| Layout Name | Predefined Type | objectId |
|---|---|---|
| Closing | TITLE_1_1 | g3b0f681f8ea_0_330 |
| Closing | TITLE_1_2 | g3b0f681f8ea_0_380 |
| Closing slide with image | -- | g3b0f681f8ea_0_543 |

### Divider Slides

| Layout Name | Predefined Type | objectId |
|---|---|---|
| Divider with title | CUSTOM | g3b0f681f8ea_0_605 |
| Divider with title | -- | g3b0f681f8ea_0_672 |
| Divider with title and subhead | -- | g3b0f681f8ea_0_704 |
| Divider with title | -- | g3b0f681f8ea_0_880 |
| Divider with title | -- | g3b0f681f8ea_0_933 |

### Interior Content Layouts

| Layout Name | objectId |
|---|---|
| Interior callout | g3b0f681f8ea_0_740 |
| Interior agenda | g3b0f681f8ea_0_970 |
| Interior agenda | g3b62c9604b6_0_44 |
| Interior overview | g3925d247048_4_16 |
| Interior overview | g3b62c9604b6_0_25 |
| Full-width image | g3b0f681f8ea_0_902 |
| Interior title | g3b0f681f8ea_0_915 |
| Interior three chevrons | g3925d247048_4_47 |
| Interior two chevrons | g3925d247048_4_85 |
| Interior blank | g3925d247048_4_176 |
| Interior title, subhead, and body | g3925d247048_4_202 |
| Interior title and body | g3925d247048_4_235 |
| Interior body | g3925d247048_4_254 |
| Interior title and two column body | g3925d247048_4_273 |
| Interior title and column body | g3925d247048_4_299 |
| Interior timeline vertical | g3925d247048_4_321 |
| Interior timeline horizontal | g3925d247048_4_351 |
| Interior data three callouts | g3925d247048_4_394 |
| Interior data two callouts | g3925d247048_4_449 |
| Interior data two pies | g3925d247048_4_498 |
| Interior data large pie | g3925d247048_4_545 |
| Interior quote three column | g3925d247048_4_600 |
| Interior quote two column | g3925d247048_4_658 |
| Interior quote large | g3925d247048_4_708 |
| Interior two by two | g3925d247048_4_747 |
| Interior four column | g3925d247048_4_800 |
| Interior three column | g3925d247048_4_922 |
| Interior title left | g3925d247048_4_862 |
| Interior image left | g3925d247048_4_975 |
| Interior large text | g3925d247048_4_1004 |

## Dark Mode Layouts (Second Master)

Use these when the user requests a dark-themed presentation. They mirror the light mode layouts above.

### Title Slides

| Layout Name | objectId |
|---|---|
| Title | g3d4353ea7fc_0_1496 |
| Title slide with image | g3d4353ea7fc_0_1521 |

### Closing Slides

| Layout Name | objectId |
|---|---|
| Closing | g3d4353ea7fc_0_1505 |
| Closing slide with image | g3d4353ea7fc_0_1531 |

### Divider and Content Layouts

| Layout Name | objectId |
|---|---|
| Divider with title | g3d4353ea7fc_0_1548 |
| Interior callout | g3d4353ea7fc_0_1556 |
| Divider with title and subhead | g3d4353ea7fc_0_1563 |
| Divider with title | g3d4353ea7fc_0_1572 |
| Interior agenda | g3d4353ea7fc_0_1580 |
| Interior overview | g3d4353ea7fc_0_1590 |

Additional dark interior layouts follow the same naming convention as their light counterparts. Query the template's layouts via the API to discover the full set:

```
gws slides presentations get \
  --presentation-id '1qQVmS7LI9KE4zOjJarALRNOI69UbV_452-Bp02IKEaI' \
  --params '{"fields": "layouts(layoutProperties,objectId)"}'
```

## Notes

- When you create a slide with `createSlide` and reference a layout by its `objectId`, all placeholder shapes defined in that layout appear on the new slide automatically.
- You do not need to manually add the Red Hat logo, set fonts, or apply brand colors -- these are inherited from the master.
- To populate placeholder text, use `insertText` targeting the placeholder's `objectId` on the newly created slide (retrieve it from the `createSlide` response or a subsequent `get` call).
- Prefer light mode layouts unless the user explicitly requests dark mode.
