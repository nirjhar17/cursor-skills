---
name: cursor-usage
description: Show Cursor agent token usage, estimated costs, and activity patterns across all sessions on this machine. Supports summary, by-project, by-month, by-session, daily-activity, and tool-usage views. Use when asked about spending, costs, tokens, daily activity, usage patterns, or missing days.
license: MIT
compatibility: Requires Python 3.10+ and Cursor agent transcripts in ~/.cursor/projects/*/agent-transcripts/
metadata:
  author: njajodia (adapted from bsutter's Claude Code usage skill)
  version: "1.0"
---

# Cursor Agent Usage & Cost Report

Show estimated token usage and costs across all Cursor agent sessions stored on this machine (`~/.cursor/projects/*/agent-transcripts/*/*.jsonl`).

## How It Works

Cursor agent transcripts don't include raw token counts like Claude Code sessions. This skill estimates tokens from character length (~4 characters per token) and applies Anthropic's published Sonnet pricing to approximate costs. It also tracks message counts, tool usage, and activity patterns.

## Trigger Prompts

Run this skill when the user asks about any of these topics:
- "How much have I spent on Cursor?"
- "Show my Cursor usage / costs / tokens"
- "What's my daily activity?"
- "How much did I spend this week / month?"
- "Which projects cost the most?"
- "Show my most expensive sessions"
- "Any days I didn't use Cursor?"
- "What are my usage patterns?"
- "What tools do I use the most?"
- "/usage"

## Reports Available

Based on what the user asks, run the appropriate script from this skill's `scripts/` directory:

### Summary (default)
```bash
python3 scripts/tally-costs.py
```
Shows total sessions, estimated tokens, and estimated cost. Use when the user asks a general "how much" question.

### By Project
```bash
python3 scripts/tally-costs.py --by-project
```
Use when the user asks which projects cost the most or where tokens are being spent.

### By Month
```bash
python3 scripts/tally-costs.py --by-month
```
Use when the user asks about monthly trends or spending over time.

### By Session (Top 20)
```bash
python3 scripts/tally-costs.py --by-session
```
Use when the user asks about their most expensive sessions.

### Tool Usage
```bash
python3 scripts/tally-costs.py --tools
```
Use when the user asks which tools are used most, or wants a breakdown of Shell vs Read vs Write etc.

### Daily Activity
```bash
python3 scripts/daily-activity.py
```
Use when the user asks about daily patterns, missing days, heavy usage days, or day-of-week breakdown.

## Presenting Results

- Run the appropriate script and show the output directly — it's already formatted for terminal display.
- If the user asks a specific question (e.g., "how much did I spend last week?"), extract the relevant data from the output and answer concisely rather than dumping the full table.
- If the user asks to compare projects or time periods, run multiple reports if needed.
- Remind the user these are **estimates** based on character-to-token approximation and published per-token pricing — actual billing will differ.

## Limitations

- Token counts are approximated (~4 chars/token) since Cursor transcripts don't include API usage metadata
- Does not account for system prompts, context window overhead, or cache read/write pricing
- Only captures sessions with agent transcripts (excludes inline completions, tab completions, etc.)
- Cost estimates assume Sonnet pricing; actual model mix may vary
- Session data availability depends on Cursor's transcript retention policy
