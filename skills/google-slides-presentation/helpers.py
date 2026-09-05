"""
Reusable helper functions for building Google Slides via batchUpdate API.

USAGE: Every build script MUST start with:
    from helpers import *

This module provides ALL layout constants, color palettes, and mandatory
functions for building Red Hat branded Google Slides presentations on
10" × 5.625" (default Google Slides widescreen) canvases.

DO NOT redefine any constants or functions from this module in your build
script. If you need a value, import it from here.
"""

import json
import subprocess
import uuid
import sys

# ================================================================
# UNIT CONSTANTS
# ================================================================
EMU = 914400   # 1 inch in EMU
PT  = 12700    # 1 point in EMU

# ================================================================
# LAYOUT CONSTANTS — 10" × 5.625" (default Google Slides widescreen)
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


# ================================================================
# RED HAT BRAND COLOR PALETTE
# ================================================================

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

# Pastel panel backgrounds
PANEL_BLUE   = {"red": 0.902, "green": 0.957, "blue": 0.961}   # #E6F4F5
PANEL_GREEN  = {"red": 0.910, "green": 0.961, "blue": 0.914}   # #E8F5E9
PANEL_ORANGE = {"red": 0.996, "green": 0.961, "blue": 0.898}   # #FEF5E5
PANEL_RED    = {"red": 0.992, "green": 0.929, "blue": 0.929}   # #FDEDED
PANEL_GRAY   = {"red": 0.910, "green": 0.922, "blue": 0.941}   # #E8EBF0

# Expressive Dark mode extras
PURPLE_80      = {"red": 0.106, "green": 0.051, "blue": 0.200}  # #1b0d33
PURPLE_70      = {"red": 0.129, "green": 0.075, "blue": 0.302}  # #21134d
BLACK          = {"red": 0.0,   "green": 0.0,   "blue": 0.0}    # #000000
PURPLE_20      = {"red": 0.816, "green": 0.773, "blue": 0.957}  # #d0c5f4
PURPLE_30      = {"red": 0.714, "green": 0.651, "blue": 0.914}  # #b6a6e9


# ================================================================
# RED HAT LOGO CONSTANTS
# ================================================================
#
# Two real "Red Hat" wordmark images (hat icon + text baked into one PNG,
# extracted from the official Red Hat Slides template, 4.25:1 aspect ratio),
# one per text color, hosted on a plain public GitHub repo:
#   - WHITE variant  -> use on RH_RED / dark backgrounds (title slide, etc.)
#   - BLACK variant   -> use on white/light backgrounds (content slides,
#                        the white footer band of the Thank You slide)
# raw.githubusercontent.com serves anonymous HTTPS GETs with no auth/token/
# expiry — verified with `curl` (HTTP 200) before being wired in here. This
# replaces prior attempts that used tokenized googleusercontent.com/Drive
# URLs, which is the root cause documented in Known API Gotcha #3 (SKILL.md).
RH_LOGO_URL_WHITE = "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/redhat/redhat-logo-wordmark-white.png"
RH_LOGO_URL_BLACK = "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/redhat/redhat-logo-wordmark-black.png"
# Footprint (bottom-RIGHT corner of every content slide)
RH_LOGO_W = 1185206    # 1.296" width — 4.25:1 aspect ratio matches the asset
RH_LOGO_H = 279575     # 0.306" height
RH_LOGO_X = SLIDE_W - MARGIN_R - RH_LOGO_W   # 7501994 EMU = ~8.20"
RH_LOGO_Y = 4623206    # 5.056"


# ================================================================
# COLOR MODE SETUP — call setup_color_mode() at the top of every script
# ================================================================

# These are module-level defaults (light mode). Build scripts MUST call
# setup_color_mode("light"|"dark"|"expressive_dark") to set them properly.
BG_PRIMARY     = WHITE
BG_SECONDARY   = GRAY_10
TEXT_PRIMARY    = GRAY_95
TEXT_SECONDARY  = GRAY_60
TEXT_MUTED      = RH_GRAY
ACCENT         = RH_RED

# Expressive Dark extras (set by setup_color_mode if needed)
BG_SURFACE       = None
HIGHLIGHT_TEAL   = None
HIGHLIGHT_PURPLE = None


def setup_color_mode(mode="light"):
    """MUST be called at the top of every build script to configure colors.
    mode: "light", "dark", or "expressive_dark"
    Returns a dict of all color variables for convenience."""
    global BG_PRIMARY, BG_SECONDARY, TEXT_PRIMARY, TEXT_SECONDARY
    global TEXT_MUTED, ACCENT, BG_SURFACE, HIGHLIGHT_TEAL, HIGHLIGHT_PURPLE

    ACCENT = RH_RED  # always

    if mode == "light":
        BG_PRIMARY     = WHITE
        BG_SECONDARY   = GRAY_10
        TEXT_PRIMARY    = GRAY_95
        TEXT_SECONDARY  = GRAY_60
        TEXT_MUTED      = RH_GRAY
    elif mode == "dark":
        BG_PRIMARY     = GRAY_95
        BG_SECONDARY   = GRAY_80
        TEXT_PRIMARY    = WHITE
        TEXT_SECONDARY  = GRAY_40
        TEXT_MUTED      = GRAY_60
    elif mode == "expressive_dark":
        BG_PRIMARY     = PURPLE_80
        BG_SECONDARY   = BLACK
        BG_SURFACE     = PURPLE_70
        TEXT_PRIMARY    = WHITE
        TEXT_SECONDARY  = PURPLE_20
        TEXT_MUTED      = PURPLE_30
        HIGHLIGHT_TEAL   = TEAL_50
        HIGHLIGHT_PURPLE = PURPLE_40

    return {
        "BG_PRIMARY": BG_PRIMARY, "BG_SECONDARY": BG_SECONDARY,
        "TEXT_PRIMARY": TEXT_PRIMARY, "TEXT_SECONDARY": TEXT_SECONDARY,
        "TEXT_MUTED": TEXT_MUTED, "ACCENT": ACCENT,
    }


# ================================================================
# BASIC UTILITIES
# ================================================================

def uid():
    """Generate a unique object ID (must start with a letter)."""
    return "e" + uuid.uuid4().hex[:10]

def inches(v):
    """Convert inches to EMU."""
    return int(v * EMU)

def pts(v):
    """Convert points to EMU."""
    return int(v * PT)

def rgb(color):
    """Wrap a color dict for the API. color = {"red": float, "green": float, "blue": float}"""
    return {"rgbColor": color}


# ================================================================
# CONTENT SIZING — prevents text overflow (the #1 defect)
# ================================================================

def calc_box_height(text, font_size_pt, box_width_inches):
    """Calculate minimum box height in EMU. ALWAYS use this before creating text boxes.

    Args:
        text: The text content (may contain newlines)
        font_size_pt: Font size in points
        box_width_inches: Box width in inches (e.g., COL2_W / EMU)

    Returns:
        Height in EMU
    """
    avg_char_width_pt = font_size_pt * 0.55  # average char width ~ 55% of font size
    chars_per_line = int((box_width_inches * 72) / avg_char_width_pt)
    if chars_per_line <= 0:
        chars_per_line = 1
    lines = text.split('\n')
    total_lines = 0
    for line in lines:
        if len(line) == 0:
            total_lines += 1
        else:
            total_lines += max(1, -(-len(line) // chars_per_line))  # ceiling division
    line_height_emu = int(font_size_pt * 1.5 * PT)  # 1.5x line spacing
    padding_emu = 100000  # ~0.11" padding
    return total_lines * line_height_emu + padding_emu


def set_text_autofit(shape_id):
    """No-op: Google Slides API only supports autofitType NONE.
    Overflow prevention relies on calc_box_height() sizing instead."""
    return None


# ================================================================
# SLIDE-LEVEL OPERATIONS
# ================================================================

def create_slide(slide_id):
    """Create a BLANK slide. ALWAYS use predefinedLayout BLANK. NEVER use layoutId."""
    return {"createSlide": {
        "objectId": slide_id,
        "slideLayoutReference": {"predefinedLayout": "BLANK"}
    }}

def slide_bg(slide_id, color):
    """Set explicit slide background. MUST be called immediately after create_slide."""
    return {"updatePageProperties": {
        "objectId": slide_id,
        "pageProperties": {
            "pageBackgroundFill": {
                "solidFill": {"color": rgb(color), "alpha": 1.0}
            }
        },
        "fields": "pageBackgroundFill.solidFill.color,pageBackgroundFill.solidFill.alpha"
    }}

def slide_bg_image(slide_id, url):
    """Set a full-bleed image as the slide background (stretched to fill
    the entire page). MUST be called immediately after create_slide. Used
    for the title/closing slide template art — always pass a stable,
    anonymously-fetchable URL (verify with `curl` first), never a
    tokenized contentUrl."""
    return {"updatePageProperties": {
        "objectId": slide_id,
        "pageProperties": {
            "pageBackgroundFill": {
                "stretchedPictureFill": {"contentUrl": url}
            }
        },
        "fields": "pageBackgroundFill.stretchedPictureFill.contentUrl"
    }}


# ================================================================
# SHAPE CREATION — low-level
# ================================================================

def create_shape(shape_id, slide_id, shape_type, left, top, width, height):
    """Create a shape at specific coordinates. Prefer the higher-level helpers
    (add_content_panel, add_content_text, etc.) which enforce layout boundaries."""
    return {"createShape": {
        "objectId": shape_id,
        "shapeType": shape_type,
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
    }}


# ================================================================
# TEXT OPERATIONS — low-level
# ================================================================

def insert_text(shape_id, text):
    """Insert text into a shape. GUARD: only call if text is non-empty."""
    return {"insertText": {"objectId": shape_id, "text": text, "insertionIndex": 0}}

def style_text(shape_id, font_size, color, bold=False, font="Red Hat Text"):
    """Style all text in a shape."""
    return {"updateTextStyle": {
        "objectId": shape_id,
        "style": {
            "fontSize": {"magnitude": font_size, "unit": "PT"},
            "foregroundColor": {"opaqueColor": rgb(color)},
            "bold": bold,
            "fontFamily": font
        },
        "fields": "fontSize,foregroundColor,bold,fontFamily"
    }}

def style_text_range(shape_id, start, end, font_size, color, bold=False, font=None):
    """Style a specific text range within a shape. `font` is optional —
    only set when the range needs a different font than the shape default."""
    style = {
        "fontSize": {"magnitude": font_size, "unit": "PT"},
        "foregroundColor": {"opaqueColor": rgb(color)},
        "bold": bold
    }
    fields = "fontSize,foregroundColor,bold"
    if font is not None:
        style["fontFamily"] = font
        fields += ",fontFamily"
    return {"updateTextStyle": {
        "objectId": shape_id,
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end},
        "style": style,
        "fields": fields
    }}

def align_text(shape_id, alignment="CENTER"):
    """Set paragraph alignment. alignment: "CENTER", "LEFT", "RIGHT"."""
    align_map = {"CENTER": "CENTER", "LEFT": "START", "RIGHT": "END"}
    return {"updateParagraphStyle": {
        "objectId": shape_id,
        "style": {"alignment": align_map.get(alignment, "START")},
        "fields": "alignment"
    }}


# ================================================================
# SHAPE STYLING — low-level
# ================================================================

def shape_fill(shape_id, color):
    """Set shape background fill color."""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {
            "shapeBackgroundFill": {
                "solidFill": {"color": rgb(color), "alpha": 1.0}
            }
        },
        "fields": "shapeBackgroundFill.solidFill.color,shapeBackgroundFill.solidFill.alpha"
    }}

def shape_no_border(shape_id):
    """Remove shape outline/border."""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "outline.propertyState"
    }}

def shape_border(shape_id, color, weight=1):
    """Set shape border with color and weight (in points)."""
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {
            "outline": {
                "outlineFill": {"solidFill": {"color": rgb(color), "alpha": 1.0}},
                "weight": {"magnitude": weight, "unit": "PT"}
            }
        },
        "fields": "outline"
    }}


# ================================================================
# MANDATORY SLIDE ELEMENT FUNCTIONS
# These enforce correct positions. ALWAYS use these instead of
# creating shapes with custom coordinates.
# ================================================================

def add_red_accent_bar(reqs, slide_id):
    """Red accent bar at top of content slides (full width, 0.06" tall).
    MUST be called on every content slide."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "RECTANGLE",
                             0, ACCENT_BAR_Y, ACCENT_BAR_W, ACCENT_BAR_H))
    reqs.append(shape_fill(sid, RH_RED))
    reqs.append(shape_no_border(sid))
    return sid


def add_slide_title(reqs, slide_id, title_text, font_size=28):
    """Add title at the CORRECT position. MUST be used for every content slide title.
    Font size 28pt fits ~55 chars. If title is longer, auto-downsizes.
    Uses TITLE_X, TITLE_Y, TITLE_W, TITLE_H constants."""
    if len(title_text) > 40 and font_size >= 28:
        font_size = 24  # auto-downsize for long titles
    if len(title_text) > 55 and font_size >= 24:
        font_size = 20  # further downsize
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX",
                             TITLE_X, TITLE_Y, TITLE_W, TITLE_H))
    reqs.append(insert_text(sid, title_text))
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
    """Add subtitle at the CORRECT position (below title). MUST use for every subtitle.
    Uses SUBTITLE_X, SUBTITLE_Y, SUBTITLE_W, SUBTITLE_H constants."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX",
                             SUBTITLE_X, SUBTITLE_Y, SUBTITLE_W, SUBTITLE_H))
    reqs.append(insert_text(sid, subtitle_text))
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
    Automatically clamps coordinates to prevent overflow."""
    if y < CONTENT_TOP_Y:
        y = CONTENT_TOP_Y  # FORCE content below title area
    if y + h > CONTENT_BOT_Y:
        h = CONTENT_BOT_Y - y  # CLAMP to content zone
    if h <= 0:
        return None  # nothing to draw
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "RECTANGLE", x, y, w, h))
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
            "fields": "outline.propertyState",
            "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}}
        }})
    return sid


def add_content_text(reqs, slide_id, x, y, w, text, font_size=12,
                     font_family="Red Hat Text", color=None, bold=False,
                     alignment="LEFT"):
    """Add a text box in the CONTENT ZONE. Auto-calculates height.
    ENFORCES: y >= CONTENT_TOP_Y. Clamps height to CONTENT_BOT_Y.

    Args:
        reqs: request list to append to
        slide_id: slide object ID
        x: left position in EMU
        y: top position in EMU
        w: width in EMU
        text: text content
        font_size: font size in points (default 12)
        font_family: font family (default "Red Hat Text")
        color: color dict (default TEXT_PRIMARY)
        bold: bold flag (default False)
        alignment: "LEFT", "CENTER", or "RIGHT" (default "LEFT")
    """
    if color is None:
        color = TEXT_PRIMARY
    if y < CONTENT_TOP_Y:
        y = CONTENT_TOP_Y
    h = calc_box_height(text, font_size, w / EMU)
    if y + h > CONTENT_BOT_Y:
        h = CONTENT_BOT_Y - y
    if h <= 0:
        return None
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX", x, y, w, h))
    if text:
        reqs.append(insert_text(sid, text))
        reqs.append({"updateTextStyle": {
            "objectId": sid,
            "fields": "fontFamily,fontSize,foregroundColor,bold",
            "style": {"fontFamily": font_family,
                      "fontSize": {"magnitude": font_size, "unit": "PT"},
                      "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                      "bold": bold}
        }})
        if alignment != "LEFT":
            reqs.append(align_text(sid, alignment))
    reqs.append(set_text_autofit(sid))
    return sid


def add_slide_number(reqs, slide_id, number):
    """Add page number in bottom-LEFT corner.
    Position: SLIDENUM_X, SLIDENUM_Y (0.50", 5.10") for 10" × 5.625" slides."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX",
                             SLIDENUM_X, SLIDENUM_Y, 457200, 228600))
    reqs.append(insert_text(sid, str(number)))
    reqs.append({"updateTextStyle": {
        "objectId": sid,
        "fields": "fontFamily,fontSize,foregroundColor",
        "style": {
            "fontFamily": "Red Hat Text",
            "fontSize": {"magnitude": 8, "unit": "PT"},
            "foregroundColor": {"opaqueColor": {"rgbColor": TEXT_MUTED}}
        }
    }})
    return sid


# ================================================================
# RED HAT LOGO FUNCTIONS
# ================================================================

def add_rh_logo(reqs, slide_id, color_mode="light"):
    """Add the real Red Hat wordmark logo IMAGE to the bottom-RIGHT of the
    slide. Picks the white-text variant for dark/red backgrounds or the
    black-text variant for light backgrounds — both are the same official
    hat-icon+text lockup, just recolored, so this always renders the true
    logo rather than an approximation.
    MUST be called on every content slide (not title, not Thank You —
    those use build_title_slide()/build_thank_you_slide() which place the
    correctly-colored logo internally)."""
    url = RH_LOGO_URL_WHITE if color_mode != "light" else RH_LOGO_URL_BLACK
    return add_rh_logo_image(reqs, slide_id, url)


def add_rh_logo_image(reqs, slide_id, url=None):
    """Insert the Red Hat logo wordmark IMAGE at the standard footprint
    (RH_LOGO_X/Y/W/H, bottom-right corner). `url` defaults to the
    black-text (light-background) variant if not given."""
    if url is None:
        url = RH_LOGO_URL_BLACK
    sid = uid()
    reqs.append({"createImage": {
        "objectId": sid,
        "url": url,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": RH_LOGO_W, "unit": "EMU"},
                     "height": {"magnitude": RH_LOGO_H, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": RH_LOGO_X, "translateY": RH_LOGO_Y,
                          "unit": "EMU"}
        }
    }})
    return sid


def add_rh_logo_text(reqs, slide_id, color):
    """Text-only 'Red Hat' wordmark. LAST-RESORT fallback ONLY — use if
    createImage ever fails despite the stable GitHub-hosted URL. Position
    matches the image logo's footprint."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX",
                             RH_LOGO_X, RH_LOGO_Y, RH_LOGO_W, RH_LOGO_H))
    reqs.append(insert_text(sid, "Red Hat"))
    reqs.append(style_text(sid, 14, color, bold=True, font="Red Hat Display"))
    reqs.append(align_text(sid, "RIGHT"))
    return sid


# ================================================================
# ICON INSERTION (optional — for Red Hat product/tech icons)
# ================================================================

def add_icon(reqs, slide_id, image_url, left, top, width, height):
    """Insert an icon image from a URL (e.g., from the Icon Repository)."""
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


# ================================================================
# COMPOSITE HELPERS (convenience wrappers for common patterns)
# ================================================================

def add_text_box(reqs, slide_id, text, left, top, width, height,
                 font_size, color, bold=False, alignment="LEFT", font="Red Hat Text"):
    """Create a text box with styled text. Returns the shape ID.
    NOTE: For content zone text, prefer add_content_text() which enforces boundaries."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "TEXT_BOX", left, top, width, height))
    if text:
        reqs.append(insert_text(sid, text))
        reqs.append(style_text(sid, font_size, color, bold, font))
        reqs.append(align_text(sid, alignment))
    reqs.append(shape_no_border(sid))
    reqs.append(set_text_autofit(sid))
    return sid

def add_rect(reqs, slide_id, left, top, width, height,
             fill_color, border_color=None):
    """Create a plain rectangle (no text). Returns the shape ID."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "RECTANGLE", left, top, width, height))
    reqs.append(shape_fill(sid, fill_color))
    if border_color:
        reqs.append(shape_border(sid, border_color))
    else:
        reqs.append(shape_no_border(sid))
    return sid

def add_rect_with_text(reqs, slide_id, text, left, top, width, height,
                       fill_color, text_color, font_size, bold=True,
                       alignment="CENTER", border_color=None):
    """Create a rectangle with centered text. Returns the shape ID."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "RECTANGLE", left, top, width, height))
    reqs.append(shape_fill(sid, fill_color))
    if border_color:
        reqs.append(shape_border(sid, border_color))
    else:
        reqs.append(shape_no_border(sid))
    if text:
        reqs.append(insert_text(sid, text))
        reqs.append(style_text(sid, font_size, text_color, bold))
        reqs.append(align_text(sid, alignment))
    reqs.append(set_text_autofit(sid))
    return sid

def add_rounded_rect(reqs, slide_id, text, left, top, width, height,
                     fill_color, text_color, font_size, bold=True):
    """Create a rounded rectangle badge with optional text. Returns shape ID."""
    sid = uid()
    reqs.append(create_shape(sid, slide_id, "ROUND_RECTANGLE", left, top, width, height))
    reqs.append(shape_fill(sid, fill_color))
    reqs.append(shape_no_border(sid))
    if text:
        reqs.append(insert_text(sid, text))
        reqs.append(style_text(sid, font_size, text_color, bold))
        reqs.append(align_text(sid, "CENTER"))
    reqs.append(set_text_autofit(sid))
    return sid


# ================================================================
# SLIDE BUILD PATTERNS — complete reusable slide builders
# ================================================================

def build_two_column_slide(reqs, slide_id, title, subtitle,
                           left_header, left_body, right_header, right_body,
                           left_color, right_color, slide_num,
                           color_mode="light", callout_text=None):
    """Standard two-column comparison slide."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    add_slide_subtitle(reqs, slide_id, subtitle)

    panel_h = CONTENT_ZONE_H
    if callout_text:
        panel_h = CONTENT_ZONE_H - 457200  # leave 0.50" for callout

    add_content_panel(reqs, slide_id, COL2_LEFT_X, CONTENT_TOP_Y, COL2_W, panel_h, left_color)
    add_content_panel(reqs, slide_id, COL2_RIGHT_X, CONTENT_TOP_Y, COL2_W, panel_h, right_color)

    add_content_text(reqs, slide_id, COL2_LEFT_X + 91440, CONTENT_TOP_Y + 45720,
                     COL2_W - 182880, left_header, font_size=16,
                     font_family="Red Hat Display", bold=True)
    add_content_text(reqs, slide_id, COL2_LEFT_X + 91440, CONTENT_TOP_Y + 365760,
                     COL2_W - 182880, left_body, font_size=12)
    add_content_text(reqs, slide_id, COL2_RIGHT_X + 91440, CONTENT_TOP_Y + 45720,
                     COL2_W - 182880, right_header, font_size=16,
                     font_family="Red Hat Display", bold=True)
    add_content_text(reqs, slide_id, COL2_RIGHT_X + 91440, CONTENT_TOP_Y + 365760,
                     COL2_W - 182880, right_body, font_size=12)

    if callout_text:
        callout_y = CONTENT_BOT_Y - 411480
        add_content_panel(reqs, slide_id, CONTENT_X, callout_y, CONTENT_W, 365760, RH_RED_TINT)
        add_content_text(reqs, slide_id, CONTENT_X + 91440, callout_y + 45720,
                         CONTENT_W - 182880, callout_text, font_size=12,
                         color=RH_RED_DARK, bold=True)

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


def build_three_column_slide(reqs, slide_id, title, subtitle,
                             headers, bodies, colors, slide_num,
                             color_mode="light"):
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
                         COL3_W - 182880, bodies[i], font_size=12)

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


def build_four_column_slide(reqs, slide_id, title, subtitle,
                            headers, bodies, colors, slide_num,
                            color_mode="light"):
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
                         COL4_W - 137160, bodies[i], font_size=12)

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


def build_card_grid_slide(reqs, slide_id, title, subtitle,
                          card_headers, card_bodies, card_colors, slide_num,
                          color_mode="light"):
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
                         COL2_W - 182880, card_bodies[i], font_size=12)

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


# ================================================================
# AGENDA SLIDE PATTERN (icon lookup is MANDATORY-FIRST — see SKILL.md A4b)
# ================================================================

AGENDA_ICON_MAX = 508000    # 0.556" — cap on icon/badge square size
AGENDA_TEXT_GAP = 182880    # 0.20" gap between icon column and text column
AGENDA_ROW_GAP = 91440      # 0.10" minimum vertical breathing room between rows


def build_agenda_slide(reqs, slide_id, title, subtitle, items, slide_num, color_mode="light"):
    """Agenda / table-of-contents slide. `items` is a list of dicts:
        {"title": str, "description": str (optional), "icon_url": str or None}

    Icon lookup is MANDATORY-FIRST: resolve `icon_url` for every item from
    the Red Hat Icon Repository (see SKILL.md A4b) BEFORE calling this
    function. Items with `icon_url=None` fall back to a numbered circular
    badge (red fill, white number) — a TRUE LAST RESORT for items with no
    reasonable icon match, never a default shortcut. This dual path exists
    because the Icon Repository is a real Red Hat PRODUCT/TECHNOLOGY icon
    library (OpenShift, Ansible, RHEL, etc.) plus a grab-bag of unrelated
    generic icons — it does NOT have generic business-concept icons like
    "customer," "roadmap," or "checklist," so some agenda items will
    legitimately have no match.

    Row slots subdivide the content zone evenly (CONTENT_ZONE_H / len(items))
    so agendas with any item count never overflow, matching the mandatory
    content-sizing rules used elsewhere in this module.

    ALL-OR-NOTHING ENFORCEMENT: icons and numbered badges are NEVER mixed
    on the same slide — that looks unpolished and defeats the numbering.
    If even one item is missing icon_url, ALL items fall back to numbered
    badges, ignoring any icon_urls that were provided. This is a safety
    net, not the intended path: before calling this function, keep
    searching the Icon Repository (approximate/metaphorical matches are
    fine — e.g. a connectivity icon for a cross-site replication topic)
    until every item has a reasonable icon, so this fallback is rarely hit."""
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    if subtitle:
        add_slide_subtitle(reqs, slide_id, subtitle)

    if not all(item.get("icon_url") for item in items):
        items = [dict(item, icon_url=None) for item in items]

    n = len(items)
    slot_h = CONTENT_ZONE_H // n
    icon_size = min(AGENDA_ICON_MAX, slot_h - AGENDA_ROW_GAP)
    text_x = CONTENT_X + icon_size + AGENDA_TEXT_GAP
    text_w = CONTENT_W - icon_size - AGENDA_TEXT_GAP

    for i, item in enumerate(items):
        slot_y = CONTENT_TOP_Y + i * slot_h
        icon_y = slot_y + (slot_h - icon_size) // 2
        icon_url = item.get("icon_url")
        if icon_url:
            iid = uid()
            reqs.append({"createImage": {
                "objectId": iid,
                "url": icon_url,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": icon_size, "unit": "EMU"},
                             "height": {"magnitude": icon_size, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": CONTENT_X, "translateY": icon_y,
                                  "unit": "EMU"}
                }
            }})
        else:
            bid = uid()
            reqs.append(create_shape(bid, slide_id, "ELLIPSE",
                                      CONTENT_X, icon_y, icon_size, icon_size))
            reqs.append(shape_fill(bid, RH_RED))
            reqs.append(shape_no_border(bid))
            reqs.append(insert_text(bid, str(i + 1)))
            reqs.append(style_text(bid, 16, WHITE, bold=True, font="Red Hat Display"))
            reqs.append(align_text(bid, "CENTER"))

        description = item.get("description")
        text_block = item["title"] + ("\n" + description if description else "")
        text_h = calc_box_height(text_block, 14, text_w / EMU)
        text_y = slot_y + max(0, (slot_h - min(text_h, slot_h)) // 2)
        tid = uid()
        reqs.append(create_shape(tid, slide_id, "TEXT_BOX",
                                  text_x, text_y, text_w, min(text_h, slot_h)))
        reqs.append(insert_text(tid, text_block))
        reqs.append(style_text(tid, 14, TEXT_PRIMARY, bold=True, font="Red Hat Display"))
        if description:
            split = len(item["title"]) + 1
            reqs.append(style_text_range(tid, split, split + len(description),
                                          11, TEXT_SECONDARY, bold=False, font="Red Hat Text"))

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)
    return slide_id


# ================================================================
# DIAGRAM & VISUAL SLIDE PATTERNS — v2.0
# ================================================================
#
# New patterns developed from test deck iterations:
#   - create_connector: node-to-node arrows between shapes
#   - build_split_image_slide: text + image side-by-side
#   - build_diagram_image_slide: full-width diagram image
#   - build_diagram_from_data: data-driven node-edge diagrams
#
# All functions follow the same conventions as the v1.0 patterns above:
#   - respect color_mode parameter
#   - use module-level color globals (BG_PRIMARY, TEXT_PRIMARY, etc.)
#   - take slide_num for footer numbering
#   - call add_footer helpers (logo, slide number)

def create_connector(reqs, slide_id, start_shape_id, end_shape_id,
                     start_site=2, end_site=0,
                     line_color=None, weight_pt=1.5,
                     start_arrow="NONE", end_arrow="OPEN_ARROW",
                     line_category="STRAIGHT"):
    """Create a connected line (arrow) between two shapes on the same slide.

    Connection site indices for rectangular shapes:
        0 = top-center, 1 = right-center,
        2 = bottom-center, 3 = left-center.

    Args:
        reqs: request list to append to
        slide_id: slide object ID
        start_shape_id: objectId of the shape where the line begins
        end_shape_id: objectId of the shape where the line ends
        start_site: connection site index on start shape (default 2 = bottom)
        end_site: connection site index on end shape (default 0 = top)
        line_color: color dict (default TEXT_MUTED)
        weight_pt: line weight in points (default 1.5)
        start_arrow: arrow style at start ("NONE", "OPEN_ARROW", "FILL_ARROW", etc.)
        end_arrow: arrow style at end (default "OPEN_ARROW")
        line_category: "STRAIGHT", "BENT", or "CURVED" (default "STRAIGHT")

    Returns:
        The line object ID.
    """
    if line_color is None:
        line_color = TEXT_MUTED

    lid = uid()

    reqs.append({"createLine": {
        "objectId": lid,
        "lineCategory": line_category,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": 914400, "unit": "EMU"},
                "height": {"magnitude": 914400, "unit": "EMU"}
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": 0, "translateY": 0,
                "unit": "EMU"
            }
        }
    }})

    line_props = {
        "startConnection": {
            "connectedObjectId": start_shape_id,
            "connectionSiteIndex": start_site
        },
        "endConnection": {
            "connectedObjectId": end_shape_id,
            "connectionSiteIndex": end_site
        },
        "lineFill": {
            "solidFill": {"color": rgb(line_color), "alpha": 1.0}
        },
        "weight": {"magnitude": weight_pt, "unit": "PT"},
        "startArrow": start_arrow,
        "endArrow": end_arrow
    }

    reqs.append({"updateLineProperties": {
        "objectId": lid,
        "lineProperties": line_props,
        "fields": "startConnection,endConnection,lineFill.solidFill.color,"
                  "weight,startArrow,endArrow"
    }})

    return lid


def build_split_image_slide(reqs, slide_id, title, subtitle, bullets, image_url,
                            slide_num, color_mode="light", image_side="right"):
    """Text bullets on one side, image on the other — ideal for concept
    explanations paired with an AI-generated illustration or photo.

    Args:
        reqs: request list to append to
        slide_id: slide object ID (caller must append create_slide first)
        title: slide title text (assertion-style, <55 chars)
        subtitle: optional subtitle text (None to skip)
        bullets: list of bullet-point strings (no leading "•")
        image_url: publicly-fetchable URL of the image
        slide_num: slide number for footer
        color_mode: "light", "dark", or "expressive_dark"
        image_side: "right" (default) or "left"
    """
    reqs.append(slide_bg(slide_id, BG_PRIMARY))
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    if subtitle:
        add_slide_subtitle(reqs, slide_id, subtitle)

    text_w = int(CONTENT_W * 0.52)
    img_w = CONTENT_W - text_w - 182880   # 0.20" gap

    if image_side == "right":
        text_x = CONTENT_X
        img_x = CONTENT_X + text_w + 182880
    else:
        img_x = CONTENT_X
        text_x = CONTENT_X + img_w + 182880

    bullet_text = "\n".join(f"• {b}" for b in bullets)
    add_content_text(reqs, slide_id, text_x, CONTENT_TOP_Y, text_w,
                     bullet_text, font_size=13, color=TEXT_PRIMARY)

    img_h = min(CONTENT_ZONE_H, img_w)
    img_y = CONTENT_TOP_Y + (CONTENT_ZONE_H - img_h) // 2
    img_id = uid()
    reqs.append({"createImage": {
        "objectId": img_id,
        "url": image_url,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": img_w, "unit": "EMU"},
                     "height": {"magnitude": img_h, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": img_x, "translateY": img_y,
                          "unit": "EMU"}
        }
    }})

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


def build_diagram_image_slide(reqs, slide_id, title, subtitle, image_url,
                              slide_num, color_mode="light",
                              image_scale=0.85):
    """Full-width diagram image with title and subtitle — ideal for
    draw.io sketch exports, architecture diagrams, or any pre-rendered
    diagram PNG/SVG.

    Args:
        reqs: request list to append to
        slide_id: slide object ID (caller must append create_slide first)
        title: slide title text
        subtitle: optional subtitle text (None to skip)
        image_url: publicly-fetchable URL of the diagram image
        slide_num: slide number for footer
        color_mode: "light", "dark", or "expressive_dark"
        image_scale: fraction of content zone to fill (default 0.85)
    """
    reqs.append(slide_bg(slide_id, BG_PRIMARY))
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    if subtitle:
        add_slide_subtitle(reqs, slide_id, subtitle)

    img_w = int(CONTENT_W * image_scale)
    img_h = int(CONTENT_ZONE_H * image_scale)
    img_x = CONTENT_X + (CONTENT_W - img_w) // 2
    img_y = CONTENT_TOP_Y + (CONTENT_ZONE_H - img_h) // 2

    img_id = uid()
    reqs.append({"createImage": {
        "objectId": img_id,
        "url": image_url,
        "elementProperties": {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": img_w, "unit": "EMU"},
                     "height": {"magnitude": img_h, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": img_x, "translateY": img_y,
                          "unit": "EMU"}
        }
    }})

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


def build_diagram_from_data(reqs, slide_id, title, subtitle,
                            nodes, edges, slide_num,
                            color_mode="light",
                            default_node_color=None,
                            default_text_color=None,
                            connector_color=None):
    """Data-driven node-edge diagram built from structured data.

    Creates labeled boxes for each node and connected arrows for each edge,
    all within the standard content zone boundaries.

    Args:
        reqs: request list to append to
        slide_id: slide object ID (caller must append create_slide first)
        title: slide title text
        subtitle: optional subtitle text (None to skip)
        nodes: list of dicts, each with:
            - id (str): unique identifier for connector references
            - label (str): text displayed inside the node
            - x (float): left position in inches relative to content zone
            - y (float): top position in inches relative to content zone
            - w (float): width in inches
            - h (float): height in inches
            - color (dict, optional): fill color (default BG_SURFACE or BG_SECONDARY)
            - text_color (dict, optional): text color (default TEXT_PRIMARY)
            - font_size (int, optional): font size in pt (default 11)
            - shape (str, optional): "RECTANGLE", "ROUND_RECTANGLE", "ELLIPSE"
                                     (default "ROUND_RECTANGLE")
        edges: list of dicts, each with:
            - from_id (str): node id where the line starts
            - to_id (str): node id where the line ends
            - start_site (int, optional): connection site index (default 2 = bottom)
            - end_site (int, optional): connection site index (default 0 = top)
            - label (str, optional): text label on the edge (not yet supported
              natively — rendered as a small text box near midpoint)
        slide_num: slide number for footer
        color_mode: "light", "dark", or "expressive_dark"
        default_node_color: fallback fill for nodes without explicit color
        default_text_color: fallback text color for nodes without explicit text_color
        connector_color: color for all connector lines (default TEXT_MUTED)
    """
    reqs.append(slide_bg(slide_id, BG_PRIMARY))
    add_red_accent_bar(reqs, slide_id)
    add_slide_title(reqs, slide_id, title)
    if subtitle:
        add_slide_subtitle(reqs, slide_id, subtitle)

    if default_node_color is None:
        default_node_color = BG_SURFACE if BG_SURFACE else BG_SECONDARY
    if default_text_color is None:
        default_text_color = TEXT_PRIMARY
    if connector_color is None:
        connector_color = TEXT_MUTED

    node_shape_ids = {}

    for node in nodes:
        nid = node["id"]
        label = node.get("label", "")
        nx = CONTENT_X + inches(node["x"])
        ny = CONTENT_TOP_Y + inches(node["y"])
        nw = inches(node["w"])
        nh = inches(node["h"])
        fill = node.get("color", default_node_color)
        text_c = node.get("text_color", default_text_color)
        font_sz = node.get("font_size", 11)
        shape_type = node.get("shape", "ROUND_RECTANGLE")

        if ny < CONTENT_TOP_Y:
            ny = CONTENT_TOP_Y
        if ny + nh > CONTENT_BOT_Y:
            nh = CONTENT_BOT_Y - ny
        if nh <= 0:
            continue

        sid = uid()
        node_shape_ids[nid] = sid
        reqs.append(create_shape(sid, slide_id, shape_type, nx, ny, nw, nh))
        reqs.append(shape_fill(sid, fill))
        reqs.append(shape_no_border(sid))
        if label:
            reqs.append(insert_text(sid, label))
            reqs.append(style_text(sid, font_sz, text_c, bold=True))
            reqs.append(align_text(sid, "CENTER"))

    for edge in edges:
        from_sid = node_shape_ids.get(edge["from_id"])
        to_sid = node_shape_ids.get(edge["to_id"])
        if from_sid and to_sid:
            create_connector(
                reqs, slide_id, from_sid, to_sid,
                start_site=edge.get("start_site", 2),
                end_site=edge.get("end_site", 0),
                line_color=connector_color
            )

    add_rh_logo(reqs, slide_id, color_mode)
    add_slide_number(reqs, slide_id, slide_num)


# ================================================================
# TITLE & THANK-YOU SLIDE PATTERNS (mandatory — first/last slide of every deck)
# ================================================================
#
# Both patterns are measured directly from the official Red Hat Slides
# template (illustration title slide + red/white closing slide) so they
# match the real brand deck pixel-for-pixel, not an approximation. All
# background art, wordmark logos, and social icons are hosted on the same
# public GitHub repo as RH_LOGO_URL_* (see top of file) — anonymous HTTPS
# GETs, no auth/token/expiry.
#
# NEVER add add_red_accent_bar(), add_slide_title(), add_slide_subtitle(),
# add_rh_logo(), or add_slide_number() to these two slides — they are
# fully self-contained and use their own logo/footer treatment.

TITLE_SLIDE_BG_URL = "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/backgrounds/title-slide-bg.png"
CLOSING_SLIDE_BG_URL = "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/backgrounds/closing-slide-bg.png"

SOCIAL_ICON_URLS = {
    "linkedin": "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/icons/social-linkedin.png",
    "youtube":  "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/icons/social-youtube.png",
    "facebook": "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/icons/social-facebook.png",
    "twitter":  "https://raw.githubusercontent.com/nirjhar17/slide-assets/main/icons/social-twitter.png",
}
DEFAULT_SOCIAL_LINKS = [
    ("linkedin", "linkedin.com/company/red-hat"),
    ("youtube", "youtube.com/user/RedHatVideos"),
    ("facebook", "facebook.com/redhatinc"),
    ("twitter", "twitter.com/RedHat"),
]

ACCENT_MAROON = {"red": 0.502, "green": 0.0, "blue": 0.0}   # #800000 — closing-slide accent bars

# Thin decorative accent bar shared by both templates (bottom-left corner)
TEMPLATE_ACCENT_X = 335825      # 0.367"
TEMPLATE_ACCENT_W = 27432       # 0.03" — thin but reliably rendered (cf. ACCENT_BAR_H)
ACCENT_BOTTOM_Y = 4801200       # 5.25"
ACCENT_BOTTOM_H = 342300        # 0.374" — spans to the bottom edge (5.625")
THANKYOU_ACCENT_TOP_H = 1712062   # 1.872" — closing slide only, brackets "Thank you"

# Title slide: presenter name/role lockup (right half of the two-tone bg)
TITLE_NAME_X = 4400000     # 4.811"
TITLE_NAME_Y = 3000000     # 3.281"
TITLE_NAME_W = 3200100     # 3.499"

# Title slide: optional deck title/subtitle, above the name/role block
TITLE_HEADLINE_X = TITLE_NAME_X
TITLE_HEADLINE_Y = 1600000    # 1.750"
TITLE_HEADLINE_W = SLIDE_W - MARGIN_R - TITLE_HEADLINE_X   # 4286800 EMU = 4.686"

# Closing slide: "Thank you" headline + body paragraph (left half)
THANKYOU_TITLE_X = 1562906     # 1.709"
THANKYOU_TITLE_Y = 1395225     # 1.526"
THANKYOU_TITLE_W = 3678900     # 4.023"
THANKYOU_TITLE_H = 634500      # 0.694"
THANKYOU_BODY_X = 1562794      # 1.709"
THANKYOU_BODY_Y = 2484919      # 2.718"
THANKYOU_BODY_W = 3036000      # 3.319"
THANKYOU_BODY_H = 778800       # 0.852"

# Closing slide: social-link rows (right half), top-to-bottom
THANKYOU_SOCIAL_ICON_X = 5592003    # 6.115"
THANKYOU_SOCIAL_ICON_SIZE = 341963  # 0.374" square
THANKYOU_SOCIAL_TEXT_X = 5970354    # 6.528"
# Widened vs. the template's original 2245200 (2.455") — at our 12pt label
# size that box wrapped "linkedin.com/company/red-hat" etc. to 2 lines.
# Extend to the right margin instead so every default label fits on one line.
THANKYOU_SOCIAL_TEXT_W = SLIDE_W - MARGIN_R - THANKYOU_SOCIAL_TEXT_X   # 2716446 EMU = 2.971"
THANKYOU_SOCIAL_TEXT_H = 342000     # 0.374"
THANKYOU_SOCIAL_ROW_Y = [1499876, 2018782, 2537688, 3056594]  # up to 4 rows


def build_title_slide(reqs, slide_id, deck_title, deck_subtitle=None,
                       presenter_name=None, presenter_role=None):
    """MANDATORY pattern for slide 1 of every deck. Caller must append
    create_slide(slide_id) to reqs first. Draws the two-tone illustration
    background, an optional deck title/subtitle, an optional presenter
    name/role lockup, and the white wordmark logo bottom-right."""
    reqs.append(slide_bg_image(slide_id, TITLE_SLIDE_BG_URL))

    accent_id = uid()
    reqs.append(create_shape(accent_id, slide_id, "RECTANGLE",
                              TEMPLATE_ACCENT_X, ACCENT_BOTTOM_Y,
                              TEMPLATE_ACCENT_W, ACCENT_BOTTOM_H))
    reqs.append(shape_fill(accent_id, WHITE))
    reqs.append(shape_no_border(accent_id))

    if deck_title:
        headline_text = deck_title + ("\n" + deck_subtitle if deck_subtitle else "")
        headline_h = calc_box_height(headline_text, 32, TITLE_HEADLINE_W / EMU)
        hid = uid()
        reqs.append(create_shape(hid, slide_id, "TEXT_BOX",
                                  TITLE_HEADLINE_X, TITLE_HEADLINE_Y,
                                  TITLE_HEADLINE_W, headline_h))
        reqs.append(insert_text(hid, headline_text))
        reqs.append(style_text(hid, 32, WHITE, bold=True, font="Red Hat Display"))
        if deck_subtitle:
            split = len(deck_title) + 1
            reqs.append(style_text_range(hid, split, split + len(deck_subtitle),
                                          16, WHITE, bold=False, font="Red Hat Text"))

    if presenter_name:
        full = presenter_name + ("\n" + presenter_role if presenter_role else "")
        name_h = calc_box_height(full, 16, TITLE_NAME_W / EMU)
        nid = uid()
        reqs.append(create_shape(nid, slide_id, "TEXT_BOX",
                                  TITLE_NAME_X, TITLE_NAME_Y, TITLE_NAME_W, name_h))
        reqs.append(insert_text(nid, full))
        reqs.append(style_text(nid, 13, WHITE, bold=False, font="Red Hat Text"))
        reqs.append(style_text_range(nid, 0, len(presenter_name) + 1,
                                      16, WHITE, bold=True, font="Red Hat Text"))

    add_rh_logo_image(reqs, slide_id, RH_LOGO_URL_WHITE)
    return slide_id


def build_thank_you_slide(reqs, slide_id, slide_num, body_text=None, social_links=None):
    """MANDATORY pattern for the LAST slide of every deck. Caller must
    append create_slide(slide_id) to reqs first. Draws the red/white
    closing background, 'Thank you' headline, a body paragraph, up to 4
    social-link rows, and the slide number + black-text logo on the
    white footer band."""
    if body_text is None:
        body_text = ("Red Hat is the world's leading provider of enterprise open "
                      "source software solutions. Award-winning support, training, "
                      "and consulting services make Red Hat a trusted adviser to "
                      "the Fortune 500.")
    if social_links is None:
        social_links = DEFAULT_SOCIAL_LINKS

    reqs.append(slide_bg_image(slide_id, CLOSING_SLIDE_BG_URL))

    top_accent = uid()
    reqs.append(create_shape(top_accent, slide_id, "RECTANGLE",
                              TEMPLATE_ACCENT_X, 0,
                              TEMPLATE_ACCENT_W, THANKYOU_ACCENT_TOP_H))
    reqs.append(shape_fill(top_accent, ACCENT_MAROON))
    reqs.append(shape_no_border(top_accent))

    bottom_accent = uid()
    reqs.append(create_shape(bottom_accent, slide_id, "RECTANGLE",
                              TEMPLATE_ACCENT_X, ACCENT_BOTTOM_Y,
                              TEMPLATE_ACCENT_W, ACCENT_BOTTOM_H))
    reqs.append(shape_fill(bottom_accent, ACCENT_MAROON))
    reqs.append(shape_no_border(bottom_accent))

    title_id = uid()
    reqs.append(create_shape(title_id, slide_id, "TEXT_BOX",
                              THANKYOU_TITLE_X, THANKYOU_TITLE_Y,
                              THANKYOU_TITLE_W, THANKYOU_TITLE_H))
    reqs.append(insert_text(title_id, "Thank you"))
    reqs.append(style_text(title_id, 40, WHITE, bold=False, font="Red Hat Display"))

    body_id = uid()
    body_h = max(THANKYOU_BODY_H, calc_box_height(body_text, 12, THANKYOU_BODY_W / EMU))
    reqs.append(create_shape(body_id, slide_id, "TEXT_BOX",
                              THANKYOU_BODY_X, THANKYOU_BODY_Y,
                              THANKYOU_BODY_W, body_h))
    reqs.append(insert_text(body_id, body_text))
    reqs.append(style_text(body_id, 12, WHITE, bold=False, font="Red Hat Display"))

    for i, (network, label) in enumerate(social_links[:4]):
        y = THANKYOU_SOCIAL_ROW_Y[i]
        icon_url = SOCIAL_ICON_URLS.get(network)
        if icon_url:
            icon_id = uid()
            reqs.append({"createImage": {
                "objectId": icon_id,
                "url": icon_url,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": THANKYOU_SOCIAL_ICON_SIZE, "unit": "EMU"},
                             "height": {"magnitude": THANKYOU_SOCIAL_ICON_SIZE, "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": THANKYOU_SOCIAL_ICON_X, "translateY": y,
                                  "unit": "EMU"}
                }
            }})
        text_id = uid()
        reqs.append(create_shape(text_id, slide_id, "TEXT_BOX",
                                  THANKYOU_SOCIAL_TEXT_X, y,
                                  THANKYOU_SOCIAL_TEXT_W, THANKYOU_SOCIAL_TEXT_H))
        reqs.append(insert_text(text_id, label))
        reqs.append(style_text(text_id, 12, WHITE, bold=False, font="Red Hat Text"))

    add_slide_number(reqs, slide_id, slide_num)
    add_rh_logo_image(reqs, slide_id, RH_LOGO_URL_BLACK)
    return slide_id


# ================================================================
# BATCH SENDER
# ================================================================

def send_batch(pres_id, reqs, chunk_size=200):
    """Send batchUpdate requests in chunks via gws CLI."""
    reqs = [r for r in reqs if r is not None]
    for i in range(0, len(reqs), chunk_size):
        chunk = reqs[i:i+chunk_size]
        payload = json.dumps({"requests": chunk})
        cmd = [
            "gws", "slides", "presentations", "batchUpdate",
            "--params", json.dumps({"presentationId": pres_id}),
            "--json", payload
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR at chunk {i//chunk_size}: {result.stderr[:500]}")
            print(f"stdout: {result.stdout[:500]}")
            sys.exit(1)
        print(f"Chunk {i//chunk_size + 1} sent ({len(chunk)} requests)")


# ================================================================
# PRESENTATION CREATION
# ================================================================

def create_presentation(title):
    """Create a fresh blank Google Slides presentation via gws CLI.
    Returns the presentation ID."""
    cmd = [
        "gws", "slides", "presentations", "create",
        "--json", json.dumps({"title": title})
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR creating presentation: {result.stderr[:500]}")
        sys.exit(1)
    lines = result.stdout.strip().split('\n')
    start = next((i for i, l in enumerate(lines) if l.strip().startswith('{')), 0)
    data = json.loads('\n'.join(lines[start:]))
    return data.get('presentationId')


def delete_default_slide(pres_id):
    """Delete the default first slide (objectId='p') from a new presentation.
    Call AFTER creating your first real slide."""
    return {"deleteObject": {"objectId": "p"}}
