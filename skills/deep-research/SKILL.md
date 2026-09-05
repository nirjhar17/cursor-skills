---
name: deep-research
description: >-
  Multi-agent deep research pipeline (AI-Q-inspired) that synthesizes local files,
  URLs, Slack, GitHub, Google Drive, and other sources into a cited research report.
  Use when the user says deep research, research this, synthesize these sources,
  deep dive on, research report, or asks for multi-source investigation with citations.
---

# Deep Research

Cursor-native multi-agent research pipeline. No external server — orchestration runs in the parent agent; specialized work runs in **Task** subagents with stage-specific prompts and models from [config.yaml](config.yaml).

## Quick start

```text
User: "Deep research: How does feature X compare across our docs and #team Slack?"
      Sources: ./docs/x.md, https://example.com/paper, slack:#team-thread
```

1. Parse question + sources → run `orchestrator.py init`
2. Five stages (clarification optional) → `collect` after each → `status` to verify
3. Deliver `sessions/<id>/report.md` — every report **must** include a **What Problem It Is Solving** section (see report template)

**Working directory** for all orchestrator commands:

```bash
cd "/Users/njajodia/Cursor Experiments/.cursor/skills/deep-research"
```

---

## Phase 0: Parse user input

Extract from the user message:

| Field | How to identify |
|-------|-----------------|
| Research question | Explicit question, or infer from "research / deep dive on X" |
| Sources | File paths, URLs, `@` references, "check Slack #channel", GitHub links, Drive doc names |
| Constraints | Audience, version, date range, must-include/exclude sources |

Normalize each source to:

```json
{
  "source_id": "src-001",
  "source_type": "file|url|slack|github|gdrive|huggingface|dataverse|kubernetes",
  "title": "Short label",
  "uri": "Full path or URL — never truncate"
}
```

Assign `source_id` sequentially (`src-001` …). Cap at `defaults.max_sources` in [config.yaml](config.yaml) (default 20); ask user which to drop if over limit.

**Source type hints**

- `file` — workspace paths, PDF, md, txt, csv, code
- `url` — http(s) links → WebFetch in ingester
- `slack` — channel/thread → Slack MCP
- `github` — repo, issue, PR → GitHub MCP
- `gdrive` — Google Docs/Sheets → `gws` CLI (never Drive MCP)
- `huggingface` — models, datasets → HF MCP
- `dataverse` — people/org lookup → Dataverse MCP
- `kubernetes` — cluster state → Kubernetes MCP

---

## Orchestrator CLI

Run from the skill directory. The orchestrator manages session state under `sessions/<session_id>/`.

### Initialize session

```bash
python3 orchestrator.py init \
  --question "Main research question here" \
  --sources '[{"source_id":"src-001","source_type":"file","title":"...","uri":"..."}]'
```

Creates `sessions/<session_id>/session.json`, classifies intent placeholder, returns `session_id` and paths. **Capture `session_id`** for all later commands.

### Collect stage output

After each subagent returns, persist its JSON:

```bash
python3 orchestrator.py collect \
  --session <session_id> \
  --stage intake \
  --input /path/to/subagent-output.json
```

Stages: `intake` | `ingestion` | `clarification` | `reasoning` | `report`

For parallel ingestion, call `collect` once per source (or pass batch if orchestrator supports `--batch`).

### Check progress

```bash
python3 orchestrator.py status --session <session_id>
```

Shows completed stages, source ingestion counts, errors, report path if done.

### Package inputs for next stage

```bash
python3 orchestrator.py export --session <session_id> --stage reasoning
```

Use exported JSON as the payload appended to the subagent prompt (or read files from `sessions/<id>/` directly).

---

## Pipeline overview

```text
[User] → init → Stage1 Intake → collect
              → Stage2 Ingestion (parallel) → collect × N
              → Stage3 Clarifier? → collect
              → Stage4 Reasoning → collect
              → Stage4.5 AskQuestion: format?
              ├─ markdown → Stage5 Report → report.md
              ├─ presentation → Stage5-P → Google Slides URL
              └─ both → Stage5 Report + Stage5-P → both
```

**Mandatory rules**

1. **Read** the stage's agent prompt file immediately before dispatching that subagent.
2. **Never** skip `collect` after a stage completes successfully.
3. **Track citations** from ingestion onward — every claim links to `source_id` / `finding_id`.
4. **Ingestion:** dispatch **all** source subagents in **one parent message** (parallel Task calls).
5. **Failures:** show error to user; ask retry/skip/abort; do not silently continue critical stages.
6. **Final report:** preserve full URLs; never truncate citations.
7. **What Problem It Is Solving:** every deliverable (markdown report, HTML guide, presentation) must include this section early — pain/gap, why the solution exists, and a one-line problem statement. Reasoning emits `problem_being_solved`; the report writer must not skip it.

---

## Models (from config.yaml)

| Stage | Config key | Default model | Role |
|-------|------------|---------------|------|
| 1 Intake | `intake` | Composer 2.5 Fast | Cheap triage |
| 2 Ingestion | `ingestion` | Haiku 4.5 | Parallel read/extract |
| 3 Clarifier | `clarifier` | Sonnet 4.5 | User scope questions |
| 4 Reasoning | `reasoning` | Opus 4.6 | Cross-source synthesis |
| 5 Report | `report` | Sonnet 4.6 | Prose + template |

Alternatives: see `alternatives` in [config.yaml](config.yaml). Override only when user requests.

---

## Stage 1: Intake

**Prompt file:** [.cursor/agents/deep-research/intake-classifier.md](../../agents/deep-research/intake-classifier.md)

**Before dispatch:** Read the full prompt file.

**Task dispatch:**

```text
Task(
  subagent_type: "generalPurpose",
  model: <config.models.intake>,
  prompt: """
  Follow the instructions in intake-classifier.md exactly.

  RESEARCH QUESTION: ...
  SOURCES: [JSON array]
  USER CONTEXT: ...

  Return ONLY valid JSON per the spec.
  """
)
```

**After:** `orchestrator.py collect --stage intake` → `status`

**Branch:** If `ambiguity_flags` contains any `severity: "blocking"` → Stage 3. Else → Stage 2.

---

## Stage 2: Ingestion (parallel)

**Prompt file:** [.cursor/agents/deep-research/source-ingester.md](../../agents/deep-research/source-ingester.md)

**Before dispatch:** Read the full prompt file once.

**Dispatch ALL sources in a SINGLE message** — one Task per source:

```text
# Example: 3 sources → 3 parallel Task calls in one response
Task(model: haiku-4.5, prompt: "... ONE source: src-001 ... sub_questions: [...]")
Task(model: haiku-4.5, prompt: "... ONE source: src-002 ...")
Task(model: haiku-4.5, prompt: "... ONE source: src-003 ...")
```

Each prompt must include:

- Full ingester instructions (or explicit "follow source-ingester.md")
- Exactly **one** `source` object
- `sub_questions` from intake (or post-clarification)
- `research_question`

**After all complete:** `collect --stage ingestion` for each → `status`

**Partial failures:** Retry failed sources if user agrees; record errors in session; reasoning stage must note missing sources.

---

## Stage 3: Clarification (optional)

**Only when:** intake `ambiguity_flags` has `severity: "blocking"`, OR user scope is unclear.

**Prompt file:** [.cursor/agents/deep-research/clarifier.md](../../agents/deep-research/clarifier.md)

**Model:** `config.models.clarifier` (Sonnet 4.5)

If subagent returns `status: "pending_user"`, present questions to user, then re-dispatch clarifier with `user_responses`.

**After resolved:** `collect --stage clarification` → proceed to ingestion (if not done) or reasoning (if ingestion already done — prefer **clarify before ingestion** when blocking).

**Recommended order:** Intake → **Clarifier** (if needed) → Ingestion → Reasoning → Report.

---

## Stage 4: Reasoning

**Prompt file:** [.cursor/agents/deep-research/reasoning-synthesizer.md](../../agents/deep-research/reasoning-synthesizer.md)

**Model:** `config.models.reasoning` (**Opus 4.6** — do not downgrade)

**Input:** ALL `ingestion_results` + `sub_questions` + `research_question` + optional clarification JSON.

```bash
python3 orchestrator.py export --session <id> --stage reasoning
```

Attach export to Task prompt. This stage performs agreements, contradictions, gaps, and per-sub-question synthesis.

**After:** `collect --stage reasoning` → `status`

---

## Stage 4.5: Output format choice

**Before generating the report, ask the user which format they want.**

Use the **AskQuestion** tool:

```text
AskQuestion(
  title: "Research Report Format",
  questions: [{
    id: "output_format",
    prompt: "Your research synthesis is ready. How would you like the final report delivered?",
    options: [
      { id: "markdown",     label: "Markdown report (saved as .md file)" },
      { id: "presentation", label: "Google Slides presentation" },
      { id: "both",         label: "Both — markdown report + presentation" }
    ]
  }]
)
```

**Based on user choice:**

- **`markdown`** → proceed to Stage 5 (Report) as normal
- **`presentation`** → skip Stage 5, invoke the `google-slides-presentation` skill (see below)
- **`both`** → run Stage 5 first, then invoke the presentation skill

---

## Stage 5: Report (markdown)

**Prompt file:** [.cursor/agents/deep-research/report-writer.md](../../agents/deep-research/report-writer.md)

**Template:** [templates/report-template.md](templates/report-template.md)

**Model:** `config.models.report` (Sonnet 4.6)

**Input:** Reasoning JSON + ingestion metadata + `models_used` + `session_id`

Instruct subagent to **Read** the template file, write report markdown, save to `sessions/<session_id>/report.md`.

The report template's **What Problem It Is Solving** section is mandatory. If reasoning omitted `problem_being_solved`, the report writer must still draft that section from the synthesis and cite sources — never drop it.

**After:** `collect --stage report` → present report path to user.

---

## Stage 5-P: Presentation (Google Slides)

**When:** User chose `presentation` or `both` in Stage 4.5.

**How:** Invoke the **google-slides-presentation** skill by reading it:

```text
Read skill: .cursor/skills/google-slides-presentation/SKILL.md
```

Then follow that skill's instructions, passing it the research synthesis as source content. Specifically:

1. Read the `google-slides-presentation` SKILL.md
2. Follow its pipeline to create a Google Slides deck
3. Use the reasoning synthesis JSON as the content source — map:
   - Research question → title slide
   - `problem_being_solved` → dedicated “What problem it is solving” slide (mandatory; one-liner + pain/gap)
   - Executive summary (from synthesis) → overview slide
   - Each sub-question + synthesis → one content slide
   - Agreements → key findings slide
   - Contradictions → "open questions" slide
   - Gaps → "areas for further research" slide
   - Source inventory → references slide
4. Ensure citations appear as speaker notes or footnotes on each slide

**After:** Share the Google Slides URL with the user.

---

## Subagent dispatch checklist

Copy and track:

```text
[ ] init session
[ ] Read intake-classifier.md → Task (intake) → collect intake
[ ] Blocking ambiguity? → Read clarifier.md → Task → user answers → collect clarification
[ ] Read source-ingester.md → N parallel Tasks (ingestion) → collect each
[ ] Read reasoning-synthesizer.md → Task (reasoning) → collect reasoning
[ ] AskQuestion: output format? → markdown / presentation / both
[ ] If markdown or both: Read report-writer.md + template → Task (report) → verify **What Problem It Is Solving** section → collect report
[ ] If presentation or both: Read google-slides-presentation SKILL.md → create deck (include problem slide)
[ ] status → share report.md and/or Slides URL
```

---

## MCP and tools (ingesters)

| Source | Tool |
|--------|------|
| Slack | Slack MCP — read schema in `mcps/project-0-Cursor_Experiments-slack/tools/` |
| GitHub | `user-github-repo-mcp` |
| Hugging Face | `user-hugging-face` |
| Google Drive | `gws` CLI via Shell |
| Dataverse | `user-DataverseMCP` |
| Kubernetes | `user-kubernetes` |
| URL | WebFetch |
| File | Read |

Parent agent: ensure MCP auth if subagent reports auth errors.

---

## Error handling

| Failure | Action |
|---------|--------|
| Subagent invalid JSON | Retry once with "JSON only"; if fail, ask user |
| Source fetch 403/404 | Record in ingestion `errors`; offer skip/retry |
| Opus timeout | Ask user to retry reasoning or split sub-questions |
| > max_sources | Ask user to prioritize |
| orchestrator.py missing | Inform user; run stages manually saving JSON under `sessions/manual/` |

Always show the **error message** and ask: **Retry**, **Skip source**, or **Abort**.

---

## Shallow vs deep fast path

| Intake `depth` | Pipeline |
|----------------|----------|
| `shallow` | Intake → 1–2 ingesters → shortened reasoning → report |
| `deep` | Full pipeline, all sources in parallel |

Even shallow runs require citations.

---

## Progressive disclosure

| Topic | File |
|-------|------|
| Model defaults | [config.yaml](config.yaml) |
| Report structure | [templates/report-template.md](templates/report-template.md) |
| Stage 1 prompt | [intake-classifier.md](../../agents/deep-research/intake-classifier.md) |
| Stage 2 prompt | [source-ingester.md](../../agents/deep-research/source-ingester.md) |
| Stage 3 prompt | [clarifier.md](../../agents/deep-research/clarifier.md) |
| Stage 4 prompt | [reasoning-synthesizer.md](../../agents/deep-research/reasoning-synthesizer.md) |
| Stage 5 prompt | [report-writer.md](../../agents/deep-research/report-writer.md) |

---

## Example user triggers

- "Deep research on Kubernetes Gateway API vs Route for our migration docs"
- "Research this: [links] — synthesize into a report"
- "Deep dive on RHOAI 3.x serving; sources in ./refs and GitHub org/repo#12"
- "Synthesize these sources" (with attachments/paths)

---

## Session artifacts

```text
.cursor/skills/deep-research/sessions/<session_id>/
  session.json
  intake.json
  ingestion/src-001.json ...
  clarification.json      # optional
  reasoning.json
  report.md
```

---

## Parent agent responsibilities

You are the **orchestrator**. Do not do full-source reading yourself — delegate to ingesters. Do synthesize user-facing progress ("Stage 2/5: ingesting 4 sources…"). After report, offer: export path, rerun with new sources, or narrow scope.

**Citation rule:** If you summarize before the report is done, still cite `[src-XXX]`.
