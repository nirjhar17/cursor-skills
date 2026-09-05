---
name: clean-notes
description: >-
  Clean up rough meeting notes, voice memos, or quick jots into polished,
  structured notes. Use when the user asks to clean notes, tidy up notes,
  format meeting notes, or rewrite rough notes.
---

# Clean Notes

Transform rough, messy notes into a clean, structured format while preserving the original meaning exactly. Never fabricate information.

## Example Trigger Prompts

- "Clean up these meeting notes"
- "Tidy up my notes from today's standup"
- "Rewrite these rough notes into something readable"

## Instructions

Follow these steps in order:

1. **Read the raw notes carefully.** Understand the full context before restructuring anything.
2. **Fix grammar, spelling, and punctuation.** Correct errors without changing meaning.
3. **Identify the core elements.** Look for: topics discussed, facts stated, decisions made, unresolved questions, and assigned tasks.
4. **Organize into the five sections below.** Only include a section if there is content for it — omit empty sections entirely.
5. **Use plain business language.** No jargon, no filler, no editorializing.
6. **Never fabricate information.** If something is unclear or ambiguous in the original notes, flag it in Open Questions rather than guessing.

## Output Sections

Structure the cleaned notes using these five sections:

### Summary
2–4 sentences capturing the overall purpose and outcome of the meeting or notes.

### Key Points
Bullet list of important facts, observations, or topics discussed.

### Decisions
Bullet list of decisions that were agreed upon, with relevant context.

### Open Questions
Bullet list of unresolved items or ambiguities that need follow-up.

### Next Actions
Checklist of action items in the format: `- [ ] [Who] — [What] — [When, if mentioned]`

## Output Template

```
## Summary

[2–4 sentences capturing the overall purpose and outcome.]

## Key Points

- [Important fact, observation, or topic discussed]
- [Another key point]

## Decisions

- [Decision that was agreed upon, with any relevant context]

## Open Questions

- [Unresolved item or ambiguity that needs follow-up]

## Next Actions

- [ ] [Who] — [What] — [When, if mentioned]
```

## Rules

- Preserve meaning exactly — never invent facts, names, dates, or outcomes.
- Keep language concise and professional.
- Use proper nouns with correct capitalization when identifiable.
- Convert vague timeframes ("next week", "tuesday") into explicit dates relative to today when possible.
- If the notes cover multiple distinct meetings or topics, produce a separate set of sections for each.
- If a section would be empty, omit it entirely.
