#!/usr/bin/env python3
"""
Tally estimated Cursor agent usage and costs across all sessions.

Scans ~/.cursor/projects/*/agent-transcripts/*/*.jsonl for transcript records
and estimates costs based on character-to-token approximation and Anthropic pricing.

Usage:
  python3 scripts/tally-costs.py              # summary
  python3 scripts/tally-costs.py --by-project # breakdown by project
  python3 scripts/tally-costs.py --by-session # breakdown by session
  python3 scripts/tally-costs.py --by-month   # breakdown by month
  python3 scripts/tally-costs.py --tools      # tool usage breakdown
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CHARS_PER_TOKEN = 4

# Anthropic pricing per million tokens (May 2026)
# Cursor primarily uses Sonnet for agent mode; adjust if needed
PRICING = {
    "opus": {"input": 5.00, "output": 25.00},
    "sonnet": {"input": 3.00, "output": 15.00},
    "haiku": {"input": 1.00, "output": 5.00},
}

DEFAULT_MODEL = "sonnet"

TIMESTAMP_RE = re.compile(r"<timestamp>(.*?)</timestamp>")


def parse_timestamp(text):
    """Extract and parse timestamp from user message text."""
    match = TIMESTAMP_RE.search(text)
    if not match:
        return None
    ts_str = match.group(1).strip()
    formats = [
        "%A, %B %d, %Y, %I:%M %p (UTC%z)",
        "%A, %B %d, %Y, %I:%M %p",
    ]
    for fmt in formats:
        try:
            cleaned = re.sub(r"\(UTC([+-]\d+)\)", r"\1", ts_str)
            return datetime.strptime(cleaned, "%A, %B %d, %Y, %I:%M %p%z")
        except ValueError:
            pass
    try:
        cleaned = re.sub(r"\s*\(UTC[+-]?\d*\)", "", ts_str)
        return datetime.strptime(cleaned, "%A, %B %d, %Y, %I:%M %p")
    except ValueError:
        return None


def process_session(filepath):
    """Process a single session .jsonl file and return usage stats."""
    stats = {
        "input_chars": 0,
        "output_chars": 0,
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_calls": 0,
        "tools": defaultdict(int),
        "first_timestamp": None,
        "last_timestamp": None,
        "lines": 0,
    }

    try:
        with open(filepath, "r") as f:
            for line in f:
                stats["lines"] += 1
                try:
                    obj = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                role = obj.get("role")
                msg = obj.get("message", {})
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content", [])
                if not isinstance(content, list):
                    continue

                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "text":
                        text = c.get("text", "")
                        if role == "user":
                            stats["input_chars"] += len(text)
                            stats["user_messages"] += 1
                            ts = parse_timestamp(text)
                            if ts:
                                if stats["first_timestamp"] is None:
                                    stats["first_timestamp"] = ts
                                stats["last_timestamp"] = ts
                        elif role == "assistant":
                            stats["output_chars"] += len(text)
                            stats["assistant_messages"] += 1
                    elif c.get("type") == "tool_use":
                        stats["tool_calls"] += 1
                        tool_name = c.get("name", "unknown")
                        stats["tools"][tool_name] += 1
                        input_data = c.get("input", {})
                        if isinstance(input_data, dict):
                            stats["output_chars"] += len(json.dumps(input_data))
    except Exception as e:
        print(f"  Warning: could not read {filepath}: {e}", file=sys.stderr)

    return stats


def estimate_cost(stats, model_tier=None):
    """Estimate cost in USD from character counts."""
    if model_tier is None:
        model_tier = DEFAULT_MODEL
    prices = PRICING.get(model_tier, PRICING[DEFAULT_MODEL])

    input_tokens = stats["input_chars"] // CHARS_PER_TOKEN
    output_tokens = stats["output_chars"] // CHARS_PER_TOKEN

    cost = 0.0
    cost += (input_tokens / 1_000_000) * prices["input"]
    cost += (output_tokens / 1_000_000) * prices["output"]
    return cost, model_tier, input_tokens, output_tokens


def format_tokens(n):
    """Format token count with K/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def project_name(path_name):
    """Extract a readable project name from the directory path."""
    name = path_name
    name = re.sub(r"^Users-\w+-", "", name)
    name = name.replace("-", " ").strip()
    if not name:
        name = path_name
    if len(name) > 50:
        name = name[:47] + "..."
    return name


def find_all_transcripts():
    """Find all transcript .jsonl files across all Cursor projects."""
    cursor_dir = Path.home() / ".cursor" / "projects"
    if not cursor_dir.exists():
        print(f"No Cursor projects directory found at {cursor_dir}")
        sys.exit(1)

    transcripts = []
    for proj_dir in cursor_dir.iterdir():
        if not proj_dir.is_dir():
            continue
        at_dir = proj_dir / "agent-transcripts"
        if not at_dir.exists():
            continue
        for session_dir in at_dir.iterdir():
            if not session_dir.is_dir():
                continue
            jsonl = session_dir / f"{session_dir.name}.jsonl"
            if jsonl.exists():
                transcripts.append((proj_dir.name, jsonl))
    return transcripts


def main():
    mode = "summary"
    if "--by-project" in sys.argv:
        mode = "by-project"
    elif "--by-session" in sys.argv:
        mode = "by-session"
    elif "--by-month" in sys.argv:
        mode = "by-month"
    elif "--tools" in sys.argv:
        mode = "tools"

    transcripts = find_all_transcripts()
    print(f"Scanning {len(transcripts)} sessions...\n")

    grand_total = {
        "input_chars": 0,
        "output_chars": 0,
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_calls": 0,
        "tools": defaultdict(int),
    }
    grand_cost = 0.0
    grand_input_tokens = 0
    grand_output_tokens = 0

    project_totals = defaultdict(lambda: {
        "input_tokens": 0, "output_tokens": 0,
        "user_messages": 0, "assistant_messages": 0,
        "tool_calls": 0, "sessions": 0, "cost": 0.0,
    })
    month_totals = defaultdict(lambda: {
        "input_tokens": 0, "output_tokens": 0,
        "user_messages": 0, "assistant_messages": 0,
        "tool_calls": 0, "sessions": 0, "cost": 0.0,
    })
    session_details = []
    all_tools = defaultdict(int)

    for proj_name, sf in transcripts:
        stats = process_session(sf)
        if stats["user_messages"] == 0 and stats["assistant_messages"] == 0:
            continue

        cost, tier, input_tokens, output_tokens = estimate_cost(stats)
        grand_cost += cost
        grand_input_tokens += input_tokens
        grand_output_tokens += output_tokens

        for k in ["input_chars", "output_chars", "user_messages", "assistant_messages", "tool_calls"]:
            grand_total[k] += stats[k]
        for tool, count in stats["tools"].items():
            grand_total["tools"][tool] += count
            all_tools[tool] += count

        proj = project_name(proj_name)
        pt = project_totals[proj]
        pt["sessions"] += 1
        pt["cost"] += cost
        pt["input_tokens"] += input_tokens
        pt["output_tokens"] += output_tokens
        pt["user_messages"] += stats["user_messages"]
        pt["assistant_messages"] += stats["assistant_messages"]
        pt["tool_calls"] += stats["tool_calls"]

        month_key = "unknown"
        if stats["first_timestamp"]:
            month_key = stats["first_timestamp"].strftime("%Y-%m")
        elif stats["last_timestamp"]:
            month_key = stats["last_timestamp"].strftime("%Y-%m")
        else:
            mtime = os.path.getmtime(sf)
            month_key = datetime.fromtimestamp(mtime).strftime("%Y-%m")

        mt = month_totals[month_key]
        mt["sessions"] += 1
        mt["cost"] += cost
        mt["input_tokens"] += input_tokens
        mt["output_tokens"] += output_tokens
        mt["user_messages"] += stats["user_messages"]
        mt["assistant_messages"] += stats["assistant_messages"]
        mt["tool_calls"] += stats["tool_calls"]

        session_details.append({
            "file": sf.parent.name[:12] + "...",
            "project": proj,
            "cost": cost,
            "tier": tier,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "stats": stats,
        })

    active_sessions = len(session_details)

    print("=" * 70)
    print("  Cursor Agent — Estimated Usage & Cost Summary")
    print("=" * 70)
    print(f"  Sessions:             {active_sessions}")
    print(f"  User messages:        {grand_total['user_messages']:,}")
    print(f"  Assistant messages:   {grand_total['assistant_messages']:,}")
    print(f"  Tool calls:           {grand_total['tool_calls']:,}")
    print(f"  Est. input tokens:    {format_tokens(grand_input_tokens)}")
    print(f"  Est. output tokens:   {format_tokens(grand_output_tokens)}")
    print(f"  Est. total tokens:    {format_tokens(grand_input_tokens + grand_output_tokens)}")
    print(f"  Model assumed:        {DEFAULT_MODEL}")
    print(f"  ─────────────────────────────────────────────────────────")
    print(f"  Estimated cost:       ${grand_cost:,.2f}")
    print("=" * 70)
    print(f"  Note: Token counts estimated from character length (~{CHARS_PER_TOKEN} chars/token).")
    print(f"  Actual usage may differ. This does not include cache read/write pricing")
    print(f"  or system prompt overhead. Check Cursor settings for actual billing.")
    print()

    if mode == "by-project":
        print("By Project (sorted by cost):")
        print(f"  {'Project':<40} {'Sessions':>8} {'Messages':>9} {'Tools':>7} {'Cost':>10}")
        print(f"  {'─' * 40} {'─' * 8} {'─' * 9} {'─' * 7} {'─' * 10}")
        for proj, pt in sorted(project_totals.items(), key=lambda x: -x[1]["cost"]):
            msgs = pt["user_messages"] + pt["assistant_messages"]
            print(f"  {proj:<40} {pt['sessions']:>8} {msgs:>9} {pt['tool_calls']:>7} ${pt['cost']:>9,.2f}")
        print()

    elif mode == "by-session":
        print("By Session (top 20 by cost):")
        print(f"  {'Cost':>10} {'In Tok':>8} {'Out Tok':>8} {'Msgs':>6} {'Tools':>6} {'Project'}")
        print(f"  {'─' * 10} {'─' * 8} {'─' * 8} {'─' * 6} {'─' * 6} {'─' * 35}")
        for sd in sorted(session_details, key=lambda x: -x["cost"])[:20]:
            s = sd["stats"]
            msgs = s["user_messages"] + s["assistant_messages"]
            print(f"  ${sd['cost']:>9,.2f} {format_tokens(sd['input_tokens']):>8} {format_tokens(sd['output_tokens']):>8} {msgs:>6} {s['tool_calls']:>6} {sd['project'][:35]}")
        print()

    elif mode == "by-month":
        print("By Month:")
        print(f"  {'Month':<10} {'Sessions':>8} {'Messages':>9} {'Tokens':>12} {'Cost':>10}")
        print(f"  {'─' * 10} {'─' * 8} {'─' * 9} {'─' * 12} {'─' * 10}")
        for month in sorted(month_totals.keys()):
            mt = month_totals[month]
            total_tokens = mt["input_tokens"] + mt["output_tokens"]
            msgs = mt["user_messages"] + mt["assistant_messages"]
            print(f"  {month:<10} {mt['sessions']:>8} {msgs:>9} {format_tokens(total_tokens):>12} ${mt['cost']:>9,.2f}")
        print()

    elif mode == "tools":
        print("Tool Usage (sorted by frequency):")
        print(f"  {'Tool':<30} {'Calls':>8} {'%':>7}")
        print(f"  {'─' * 30} {'─' * 8} {'─' * 7}")
        total_calls = sum(all_tools.values())
        for tool, count in sorted(all_tools.items(), key=lambda x: -x[1]):
            pct = (count / total_calls * 100) if total_calls > 0 else 0
            print(f"  {tool:<30} {count:>8} {pct:>6.1f}%")
        print(f"\n  Total tool calls: {total_calls:,}")
        print()


if __name__ == "__main__":
    main()
