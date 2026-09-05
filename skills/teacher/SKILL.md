---
name: teacher
description: >-
  Write documents in a clear, connected teacher voice — plain language, flowing
  paragraphs, enough context to follow — and apply a clarity pass that catches
  reader confusion, jammed paragraphs, missing bridges, and undefined jargon.
  Use when the user asks for teacher style, explain like chat, teach-through
  writing, clarity edit, fix confusing prose, untangle jammed paragraphs, or
  rewrite deep-research / outline output into readable docs (HTML, markdown, or other).
---

# Teacher

Write the document the way a good explanation happens in chat: plain language, sentences that lead into each other, and enough context that a reader can follow without already knowing the topic.

This is a voice skill with an editorial clarity pass — not a content checklist. Do not invent section templates, bullet taxonomies, or rigid "must include" inventories. Structure the doc to fit the subject; keep the voice consistent throughout.

When applying this skill, rewrite freely. Add concrete examples when they help comprehension. Do not settle for fluent prose that still leaves a careful non-expert lost.

## Voice

Write as if walking someone through an idea out loud.

- Prefer connected paragraphs over fragments and note dumps.
- Explain what something is, why it matters, and how the pieces relate — in the same breath of prose, not as disconnected labels.
- Keep language simple and concrete. Short words beat jargon when both work.
- Give enough context that a careful reader stays oriented. Skip padding; do not skip the connective tissue that makes the next sentence make sense.
- Headings are fine for navigation. Under each heading, still write full explanatory prose.

Lists are allowed when a real enumeration helps (steps, options, named items). They should support the explanation, not replace it. If a bullet list would stand alone without surrounding sentences, rewrite it as paragraphs (or add the paragraphs that make the list make sense).

### Intuition first, then precision

Explain the intuition first in plain language, then briefly unpack any technical term you use. Lead with "here is what is happening and why it matters" before introducing the formal name or mechanism. A reader who grasps the intuition will absorb the precise term; a reader handed the term first will skim past the explanation.

### Thoroughness and completeness

Answer thoroughly: identify every distinct part of the question and cover each one, including all the relevant points the context provides for answering it. If the question has multiple parts, address all of them rather than stopping at the first. Do not leave a sub-question dangling because the first part already felt like a full answer.

### Economy — cover what is needed, then stop

Do not pad the answer with unrelated information or repeat yourself. Cover what the question needs, then stop. Extra tangents dilute the explanation and signal that the writer is filling space rather than teaching. If the available context does not contain enough information to answer, say so honestly rather than fabricating or hedging with vague generalities.

## Clarity pass

Fluent sentences can still confuse. Before finishing, edit for reader comprehension — not just polish.

### Flag and fix confusion points

Watch for stretches that make a careful reader think "wait, what?":

- Logic that jumps — a claim appears without the step that earns it
- Jargon or acronyms used before they are defined
- Missing context or assumed knowledge the reader was never given
- A sentence that needs two reads, or buries the point at the end
- A section that does not earn the next (topic shifts without a bridge)

When you find a confusing spot, diagnose it directly (quote the problem line or paraphrase it), then rewrite. Do not give empty praise. Do not leave the confusion and hope the surrounding prose covers it.

### One idea per paragraph

Prefer one main idea per paragraph. If a paragraph packs two or more distinct concepts, split them.

Example of the failure mode: one paragraph that mixes an unauthorized-tool block, authorized-tool misuse, and unrelated MCP history. Those are separate ideas — give each its own paragraph (or a short sequence) so the reader can track which claim applies to which case.

### Bridge topic changes

When the topic changes, add an explicit bridge so the reader does not have to guess the relationship:

- "This is different from…"
- "Separately…"
- "That only covers X; Y still needs…"
- "The previous point was about A; now look at B…"

A heading alone is not always enough. The first sentence after a shift should orient the reader.

### Prefer small concrete examples

When explaining a boundary, control, security idea, or abstract mechanism, prefer a small concrete example. One grounded case usually teaches faster than another layer of abstraction.

### Non-expert skim

Before finishing, do a careful non-expert skim: would someone get lost even though the sentences sound fine? Fix those spots. Sounding smooth is not the same as being clear.

## Avoid

Do not slip into these modes when this skill is active:

- Telegraphic notes ("Config: X. Result: Y. Next: Z.")
- Slide-caption fragments or headline-only lines pretending to be body text
- Bullet-heavy "Key takeaway" / "TL;DR strip" style that substitutes for explanation
- Deep-research finding voice: short claim lines stacked as if they were the finished document
- Jammed paragraphs that sound polished but pack multiple unrelated ideas
- Topic jumps with no bridge, leaving the reader to reconnect the logic

Research notes and findings are inputs. The document should read like a teacher explaining those findings, not like the findings list pasted into a file.

## Bad vs good

Bad (notes voice):

> RAG retrieves chunks. Then the LLM answers. Grounding matters. Watch latency.

Good (teacher voice):

> Retrieval-augmented generation works by first fetching relevant passages from your own documents, then asking the model to answer using that material. The point of the extra step is grounding: the model is less likely to invent facts when the source text is sitting in front of it. The tradeoff is latency and retrieval quality — a wrong chunk leads to a confidently wrong answer.

Bad (fluent but jammed — two+ ideas, no bridge):

> The gateway blocks unauthorized tools, and even authorized tools can be misused if prompts are crafted carefully, which is why MCP's early history emphasized discovery protocols before policy hardened.

Good (split + bridge + concrete example):

> The gateway blocks unauthorized tools. If a tool is not on the allow list, the request never reaches it.

> That is different from misuse of an authorized tool. Once a tool is allowed, a crafted prompt can still make the agent call it in a harmful way — for example, an allowed "send email" tool used to exfiltrate a file. Blocking unknown tools does not solve that case; you still need tighter prompts, scopes, or human approval for sensitive actions.

## Applying this skill

1. Read the skill before drafting or rewriting.
2. Draft (or rewrite) the whole document in this voice — HTML, markdown, or other formats the user requested. Rewrite freely; add examples when they aid comprehension.
3. Run the clarity pass: split jammed paragraphs, add bridges at topic changes, define jargon on first use, unbury buried points, and add a small concrete example where an abstract boundary would otherwise stay fuzzy.
4. Before finishing, skim once as a non-expert: if any stretch reads like notes, captions, stacked claims, or "wait, what?" prose, turn it back into connected, followable explanation.
