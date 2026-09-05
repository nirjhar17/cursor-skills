---
name: btw
description: >-
  Answers brief by-the-way / side questions with minimal context use.
  Use only when the user invokes /btw or explicitly asks for a BTW-style
  lightweight answer without derailing the main task.
disable-model-invocation: true
---

# BTW (by the way)

Answer a side question with the smallest possible extra context cost, then stop.

## When to use

- User invokes `/btw` or clearly asks for a BTW-style lightweight side answer
- Question is adjacent to the main task but should not expand it
- Do not auto-apply this skill from ambient chat

## Hard rules (minimal context)

- Only load when explicitly invoked (`disable-model-invocation: true`)
- Do not read other skills, digests, Miro, Google Docs, transcripts unless absolutely required to answer
- Prefer zero tool calls; answer from what's already in the message
- Ultra-short answer; do not expand into the main ongoing task
- Do not spawn research, Miro edits, or follow-up workstreams unless user asks
- After answering the BTW, stop — do not continue the prior main task unless asked

## How to answer

1. Read only the BTW question and any facts already present in the message/thread needed for a direct answer.
2. Reply in 1–5 sentences. No preamble, no tool dump, no “while I’m at it” extras.
3. If a tool is truly required (e.g. a path/status the user named and you cannot know otherwise), use the single cheapest call — then stop.
4. Do not propose a plan, open new todos, or resume the main task after the answer.

## What this cannot do

A skill cannot prevent the user's BTW message text from entering the chat transcript. What it CAN do is minimize *additional* context burn beyond that message (no extra skill reads, research, or main-task continuation).

## Examples

**User:** `/btw what's the default port for Postgres?`  
**Agent:** `5432.`

**User:** `/btw is `layout: default` required for Jekyll Pages?`  
**Agent:** `Yes for theme layouts that expect it; Cayman's pages typically use `layout: default` in front matter.`

**User:** `/btw also finish the Miro board and push the PR`  
**Agent:** Answer only the BTW part if there is one; do not start Miro/PR work unless they clearly asked outside BTW — and even then, treat non-BTW work as a separate explicit request, not something this skill expands into.
