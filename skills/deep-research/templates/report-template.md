# {{REPORT_TITLE}}

**Generated:** {{DATE}}  
**Session ID:** {{SESSION_ID}}  
**Research depth:** {{DEPTH}}

---

## Executive Summary

{{EXECUTIVE_SUMMARY_PARAGRAPH_1}}

{{EXECUTIVE_SUMMARY_PARAGRAPH_2}}

{{EXECUTIVE_SUMMARY_PARAGRAPH_3_OPTIONAL}}

---

## What Problem It Is Solving

This section is **mandatory** in every deep-research deliverable (markdown report, HTML guide, or presentation). Answer it before diving into mechanisms.

### The pain / gap

{{PROBLEM_PAIN_PARAGRAPH}}

Who feels it, what breaks or stays exposed today, and why existing controls are not enough. Use concrete stakes (security, compliance, multi-tenancy, ops risk) rather than product slogans.

### Why this topic / solution exists

{{PROBLEM_WHY_EXISTS_PARAGRAPH}}

What the researched subject is trying to change. One clear “before → after” framing helps. Cite sources when the problem statement comes from docs or blogs (`[src-xxx]`).

### One-line problem statement

> {{PROBLEM_ONE_LINER}}

---

## Research Question

{{MAIN_RESEARCH_QUESTION}}

---

## Sub-Questions Investigated

1. {{SUB_QUESTION_1}}
2. {{SUB_QUESTION_2}}
3. {{SUB_QUESTION_3}}
<!-- Add or remove numbered items as needed (typically 3–7) -->

---

## Key Findings

Each finding must cite its source. Use inline citations: `[source_id]` or `[source_id, p.N]` for paginated documents.

### Finding 1: {{FINDING_HEADLINE}}

{{FINDING_BODY_WITH_CITATIONS}}

**Sources:** {{SOURCE_IDS}}

### Finding 2: {{FINDING_HEADLINE}}

{{FINDING_BODY_WITH_CITATIONS}}

**Sources:** {{SOURCE_IDS}}

<!-- Repeat per major finding -->

---

## Cross-Source Analysis

### Agreements

Sources that independently support the same conclusion:

- **Claim:** {{CLAIM}}  
  **Supporting sources:** {{SOURCE_IDS}}  
  **Strength:** {{high|medium|low}}

### Contradictions

Sources that conflict; note which evidence is stronger and why:

- **Topic:** {{TOPIC}}  
  **Position A:** {{SUMMARY}} — {{SOURCE_IDS}}  
  **Position B:** {{SUMMARY}} — {{SOURCE_IDS}}  
  **Resolution:** {{HOW_TO_INTERPRET_OR_WHAT_TO_VERIFY}}

### Gaps

Sub-questions or claims with insufficient evidence:

- **Gap:** {{DESCRIPTION}}  
  **Affected sub-question(s):** {{SUB_QUESTION_IDS}}  
  **What would close the gap:** {{SUGGESTED_SOURCES_OR_DATA}}

---

## Detailed Analysis per Sub-Question

### {{SUB_QUESTION_1}}

{{SYNTHESIS_NARRATIVE_WITH_CITATIONS}}

**Confidence:** {{high|medium|low}} — {{ONE_LINE_RATIONALE}}

### {{SUB_QUESTION_2}}

{{SYNTHESIS_NARRATIVE_WITH_CITATIONS}}

**Confidence:** {{high|medium|low}} — {{ONE_LINE_RATIONALE}}

<!-- Repeat for each sub-question -->

---

## Source Inventory

| ID | Type | Title | URI / Path | Date Accessed | Notes |
|----|------|-------|------------|---------------|-------|
| src-001 | file | {{TITLE}} | `{{PATH_OR_URL}}` | {{YYYY-MM-DD}} | {{NOTES}} |
| src-002 | url | {{TITLE}} | {{FULL_URL}} | {{YYYY-MM-DD}} | {{NOTES}} |
| src-003 | slack | {{CHANNEL_THREAD}} | {{SLACK_LINK}} | {{YYYY-MM-DD}} | {{NOTES}} |
| src-004 | github | {{REPO_ISSUE_PR}} | {{FULL_URL}} | {{YYYY-MM-DD}} | {{NOTES}} |
| src-005 | gdrive | {{DOC_TITLE}} | {{GDRIVE_LINK}} | {{YYYY-MM-DD}} | {{NOTES}} |

**Rules:** Never truncate URLs. Include every source consulted, including sources that yielded no relevant findings.

---

## Methodology

- **Pipeline:** AI-Q-inspired multi-agent research (Cursor-native, no external server)
- **Stages completed:** Intake → Ingestion{{#if clarification}} → Clarification{{/if}} → Reasoning → Report
- **Sources processed:** {{N}} of {{MAX}} (see Source Inventory)
- **Models used:**
  - Intake: {{INTAKE_MODEL}}
  - Ingestion (×{{N}} parallel): {{INGESTION_MODEL}}
  - Clarification: {{CLARIFIER_MODEL_OR_N/A}}
  - Reasoning: {{REASONING_MODEL}}
  - Report: {{REPORT_MODEL}}
- **Citation policy:** Every factual claim traced to `source_id`; quotes marked with excerpts
- **Session directory:** `.cursor/skills/deep-research/sessions/{{SESSION_ID}}/`

---

## Confidence Assessment

| Area | Level | Rationale |
|------|-------|-----------|
| Overall conclusion | {{high\|medium\|low}} | {{RATIONALE}} |
| {{SUB_QUESTION_1}} | {{high\|medium\|low}} | {{RATIONALE}} |
| {{SUB_QUESTION_2}} | {{high\|medium\|low}} | {{RATIONALE}} |

**Limitations:** {{EXPLICIT_LIMITATIONS_EG_SINGLE_SOURCE_STALE_DATA_CONFLICTING_SOURCES}}

**Recommended follow-up:** {{OPTIONAL_NEXT_STEPS}}
