# Changelog

## v2.2 — 2026-09-06
- Added Diagram Selection Framework to SKILL.md:
  - Decision tree for choosing between draw.io sketch, native connectors, Sheets charts, and AI illustrations
  - Draw.io sketch mode guidelines (colors, fonts, export settings)
  - Three reusable draw.io XML templates: linear pipeline, architecture with nesting, hub-and-spokes
  - "When NOT to use draw.io" guidance for routing to simpler patterns
- Added diagram helper functions to `helpers.py`:
  - `select_diagram_approach()` — returns recommended diagram approach based on content characteristics
  - `generate_drawio_xml()` — generates complete draw.io XML with sketch mode styling from structured node/edge data
  - `export_drawio_to_png()` — exports .drawio files to PNG via the draw.io desktop CLI at configurable scale

## v2.1 — 2026-09-06
- Fixed setup_color_mode import bug — return dict for caller rebinding

## v2.0 — 2026-09-06
- Added diagram helper functions to `helpers.py`:
  - `create_connector()` — connected line (arrow) between two shapes with configurable arrow styles and connection sites
  - `build_split_image_slide()` — text bullets on one side + image on the other (AI illustrations, photos)
  - `build_diagram_image_slide()` — full-width diagram image with title/subtitle (draw.io exports, architecture PNGs)
  - `build_diagram_from_data()` — data-driven node-edge diagram built from structured node/edge lists
- Integrated hybrid visual approach: AI illustrations, draw.io sketch diagrams, connected connectors
- Updated SKILL.md with new pattern documentation, usage examples, and function reference

## v1.0 — 2026-09-06
- Initial commit: 24 skills, 1 agent suite, 10 rules
- Google Slides suite with helpers.py (1,196 lines)
- Deep research pipeline with 5-stage orchestration
- Sales engineering suite with 10 methodology rules
- Infrastructure validation (sosreport, RHEL performance)
- Draw.io diagram generation skill with 30+ scripts
- Workspace-level .cursorrules for Medium blog workflow
