# Red Hat Icon Repository -- Reference

This document describes the Red Hat Icon Repository, a shared Google Slides presentation containing official Red Hat icons. Use it to source branded icons when building presentations.

## Repository Details

- Presentation ID: `1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM`
- Total slides: 49
- This is a shared Red Hat resource. Do not modify, delete, or rearrange slides in this presentation.

## Icon Categories

The 49 slides organize icons across a range of domains. Expected categories include:

- Platform and infrastructure
- Cloud services
- Security and compliance
- Automation and orchestration
- AI and machine learning
- Containers and Kubernetes
- Networking
- Storage
- Development and CI/CD
- Integration and middleware
- Edge computing
- General UI and abstract concepts

Browse the repository to confirm exact slide-to-category mappings for a given project.

## How to Use Icons from the Repository

The workflow for extracting an icon and placing it into a target presentation has three steps.

### Step 1 -- Identify the source slide

Determine which slide in the Icon Repository contains the icon you need. You can retrieve all slides and their content with:

```
gws slides presentations get \
  --presentation-id '1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM' \
  --params '{"fields": "slides(objectId,pageElements(objectId,title,description,image(contentUrl),size,transform))"}'
```

This returns every page element on every slide, including image elements with their `contentUrl`, `title`, and `description` fields. Use the title or description to locate the icon by name.

### Step 2 -- Extract the icon image URL

Once you have identified the target image element, read its `contentUrl` value. This is a Google-hosted URL that serves the image and can be used directly in API calls.

To fetch a single slide's elements (avoiding a large payload for all 49 slides):

```
gws slides presentations pages get \
  --presentation-id '1SRhy8-bYBgaA3Jsi1t_Fxz-Yo9ORgdRy5Kec9hg_wSM' \
  --page-object-id 'SLIDE_OBJECT_ID' \
  --params '{"fields": "pageElements(objectId,title,description,image(contentUrl),size,transform)"}'
```

Replace `SLIDE_OBJECT_ID` with the objectId of the slide containing the desired icon.

### Step 3 -- Insert the icon into the target presentation

Use a `createImage` request in a `batchUpdate` call on the target presentation:

```json
{
  "requests": [
    {
      "createImage": {
        "url": "ICON_CONTENT_URL",
        "elementProperties": {
          "pageObjectId": "TARGET_SLIDE_OBJECT_ID",
          "size": {
            "width":  { "magnitude": 50, "unit": "PT" },
            "height": { "magnitude": 50, "unit": "PT" }
          },
          "transform": {
            "scaleX": 1,
            "scaleY": 1,
            "translateX": 100,
            "translateY": 100,
            "unit": "PT"
          }
        }
      }
    }
  ]
}
```

Adjust `size` and `transform` values to position and scale the icon appropriately on the target slide.

## API Pattern Summary

The complete extraction pattern in pseudocode:

```
1. GET Icon Repository presentation (filtered to image elements)
2. Find the pageElement whose title/description matches the desired icon
3. Read its image.contentUrl
4. POST batchUpdate to the target presentation with a createImage request using that URL
```

## Notes

- Icon content URLs are tokenized and time-limited (Google documents ~30 min),
  the same as any other `contentUrl` — see Gotcha #3 in SKILL.md. They are
  fine to extract and use immediately in the SAME build session (fetch,
  then `createImage` right away), but NEVER cache/hardcode one into
  `helpers.py` or a build script for reuse across sessions — it will
  eventually 400 with "There was a problem retrieving the image."
- Always use the FULL, untruncated `contentUrl` from the API response —
  do not print/log it with `[:N]` truncation and then copy the truncated
  string into a build script; a truncated URL fails `createImage` with
  the same "problem retrieving the image" error as an expired one.
- When placing multiple icons on one slide, offset each icon's `translateX` and `translateY` so they do not overlap.
- The Icon Repository is read-only for automation purposes. Never issue write calls against its presentation ID.
- This repository is Red Hat's PRODUCT/TECHNOLOGY icon library (OpenShift,
  Ansible, RHEL, etc.) plus a grab-bag of unrelated generic icons — it does
  NOT reliably have generic business-concept icons ("customer," "roadmap,"
  "checklist"). Search it first for every agenda item (mandatory-first,
  see SKILL.md A4b), but expect some items to legitimately have no match
  and require the numbered-badge fallback in `build_agenda_slide()`.
