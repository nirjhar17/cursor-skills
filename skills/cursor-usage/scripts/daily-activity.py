#!/usr/bin/env python3
"""
Daily Cursor agent activity report — shows usage patterns, missing days,
heavy usage days, and day-of-week breakdown.

Usage:
  python3 scripts/daily-activity.py
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

CHARS_PER_TOKEN = 4

PRICE_INPUT = 3.00 / 1_000_000   # Sonnet input per token
PRICE_OUTPUT = 15.00 / 1_000_000  # Sonnet output per token

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

TIMESTAMP_RE = re.compile(r"<timestamp>(.*?)</timestamp>")


def format_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def parse_timestamp(text):
    """Extract and parse timestamp from user message text."""
    match = TIMESTAMP_RE.search(text)
    if not match:
        return None
    ts_str = match.group(1).strip()
    try:
        cleaned = re.sub(r"\s*\(UTC[+-]?\d*\)", "", ts_str)
        return datetime.strptime(cleaned, "%A, %B %d, %Y, %I:%M %p")
    except ValueError:
        return None


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
    transcripts = find_all_transcripts()
    daily = defaultdict(lambda: {
        "input_chars": 0, "output_chars": 0,
        "user_messages": 0, "assistant_messages": 0,
        "tool_calls": 0, "sessions": set(),
    })

    for proj_name, sf in transcripts:
        session_id = sf.parent.name
        try:
            day_key = None
            with open(sf) as f:
                for line in f:
                    try:
                        obj = json.loads(line)
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
                                ts = parse_timestamp(text)
                                if ts:
                                    day_key = ts.strftime("%Y-%m-%d")
                                if day_key:
                                    d = daily[day_key]
                                    d["input_chars"] += len(text)
                                    d["user_messages"] += 1
                                    d["sessions"].add(session_id)
                            elif role == "assistant" and day_key:
                                d = daily[day_key]
                                d["output_chars"] += len(text)
                                d["assistant_messages"] += 1
                        elif c.get("type") == "tool_use" and day_key:
                            d = daily[day_key]
                            d["tool_calls"] += 1
                            input_data = c.get("input", {})
                            if isinstance(input_data, dict):
                                d["output_chars"] += len(json.dumps(input_data))

        except Exception:
            continue

    if not daily:
        print("No usage data found.")
        return

    all_dates = sorted(daily.keys())
    start = datetime.strptime(all_dates[0], "%Y-%m-%d")
    end = datetime.strptime(all_dates[-1], "%Y-%m-%d")

    days_data = []
    current = start
    while current <= end:
        day_str = current.strftime("%Y-%m-%d")
        dow = DAY_NAMES[current.weekday()]
        if day_str in daily:
            d = daily[day_str]
            input_tokens = d["input_chars"] // CHARS_PER_TOKEN
            output_tokens = d["output_chars"] // CHARS_PER_TOKEN
            total_tokens = input_tokens + output_tokens
            cost = input_tokens * PRICE_INPUT + output_tokens * PRICE_OUTPUT
            days_data.append({
                "date": day_str, "dow": dow, "active": True,
                "sessions": len(d["sessions"]),
                "messages": d["user_messages"] + d["assistant_messages"],
                "tool_calls": d["tool_calls"],
                "tokens": total_tokens, "cost": cost,
            })
        else:
            days_data.append({
                "date": day_str, "dow": dow, "active": False,
                "sessions": 0, "messages": 0, "tool_calls": 0,
                "tokens": 0, "cost": 0,
            })
        current += timedelta(days=1)

    active_days = [d for d in days_data if d["active"]]
    inactive_days = [d for d in days_data if not d["active"]]
    total_days = len(days_data)
    costs = [d["cost"] for d in active_days]
    avg_cost = sum(costs) / len(costs) if costs else 0
    median_cost = sorted(costs)[len(costs) // 2] if costs else 0
    heavy_threshold = avg_cost * 1.5

    dow_totals = defaultdict(lambda: {"days": 0, "cost": 0, "tokens": 0, "sessions": 0, "tools": 0})
    for d in days_data:
        dt = dow_totals[d["dow"]]
        if d["active"]:
            dt["days"] += 1
            dt["cost"] += d["cost"]
            dt["tokens"] += d["tokens"]
            dt["sessions"] += d["sessions"]
            dt["tools"] += d["tool_calls"]

    print("=" * 80)
    print("  Cursor Agent — Daily Activity Report")
    print(f"  {all_dates[0]} to {all_dates[-1]} ({total_days} days)")
    print("=" * 80)
    print(f"  Active days:   {len(active_days)} / {total_days}")
    print(f"  Inactive days: {len(inactive_days)}")
    print(f"  Avg cost/day:  ${avg_cost:.2f}")
    print(f"  Median cost:   ${median_cost:.2f}")
    print(f"  Total cost:    ${sum(costs):.2f}")
    all_tokens = sum(d["tokens"] for d in active_days)
    print(f"  Total tokens:  {format_tokens(all_tokens)}")
    total_tools = sum(d["tool_calls"] for d in active_days)
    print(f"  Total tools:   {total_tools:,}")
    print()

    print("  Day-of-Week Summary:")
    print(f"  {'Day':<5} {'Active':>6} {'Sessions':>9} {'Tokens':>10} {'Tools':>7} {'Cost':>10} {'Avg/day':>10}")
    print(f"  {'─'*5} {'─'*6} {'─'*9} {'─'*10} {'─'*7} {'─'*10} {'─'*10}")
    for dow in DAY_NAMES:
        dt = dow_totals[dow]
        avg = dt["cost"] / dt["days"] if dt["days"] > 0 else 0
        print(f"  {dow:<5} {dt['days']:>6} {dt['sessions']:>9} {format_tokens(dt['tokens']):>10} {dt['tools']:>7} ${dt['cost']:>9.2f} ${avg:>9.2f}")
    print()

    print(f"  {'Date':<12} {'Day':<4} {'Sessions':>8} {'Messages':>8} {'Tools':>7} {'Tokens':>10} {'Cost':>10} {'':>8}")
    print(f"  {'─'*12} {'─'*4} {'─'*8} {'─'*8} {'─'*7} {'─'*10} {'─'*10} {'─'*8}")
    for d in days_data:
        if not d["active"]:
            print(f"  {d['date']:<12} {d['dow']:<4} {'—':>8} {'—':>8} {'—':>7} {'—':>10} {'—':>10}   off")
        else:
            flag = ""
            if d["cost"] >= heavy_threshold:
                flag = "HEAVY"
            elif d["cost"] >= avg_cost:
                flag = "above"
            else:
                flag = "normal"
            print(f"  {d['date']:<12} {d['dow']:<4} {d['sessions']:>8} {d['messages']:>8} {d['tool_calls']:>7} {format_tokens(d['tokens']):>10} ${d['cost']:>9.2f}   {flag}")
    print()

    if inactive_days:
        print(f"  Missing Days ({len(inactive_days)}):")
        for d in inactive_days:
            print(f"    {d['date']} ({d['dow']})")
        print()

    print("  Top 5 Heaviest Days:")
    print(f"  {'Date':<12} {'Day':<4} {'Sessions':>8} {'Tools':>7} {'Tokens':>10} {'Cost':>10}")
    print(f"  {'─'*12} {'─'*4} {'─'*8} {'─'*7} {'─'*10} {'─'*10}")
    for d in sorted(active_days, key=lambda x: -x["cost"])[:5]:
        print(f"  {d['date']:<12} {d['dow']:<4} {d['sessions']:>8} {d['tool_calls']:>7} {format_tokens(d['tokens']):>10} ${d['cost']:>9.2f}")
    print()


if __name__ == "__main__":
    main()
