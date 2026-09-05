#!/usr/bin/env python3
"""
Deep Research Pipeline Orchestrator

Local state manager for the Cursor deep-research skill. Manages session lifecycle,
source inventory, findings, synthesis, and report assembly between pipeline stages.
Does not call LLMs — the Cursor agent invokes subagents via the Task tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent
SESSIONS_DIR = SKILL_DIR / "sessions"
CONFIG_PATH = SKILL_DIR / "config.yaml"
TEMPLATE_PATH = SKILL_DIR / "templates" / "report-template.md"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

TERMINAL_STATUSES = frozenset({"complete", "failed"})

STAGE_ORDER = [
    "initialized",
    "intake_complete",
    "ingesting",
    "ingestion_complete",
    "clarifying",
    "clarification_complete",
    "synthesizing",
    "synthesis_complete",
    "reporting",
    "complete",
]

VALID_SOURCE_TYPES = frozenset({
    "file", "url", "slack", "github", "gdrive", "huggingface",
    "dataverse", "kubernetes",
})

# ANSI colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"


def _color(text: str, *codes: str) -> str:
    if not sys.stdout.isatty():
        return text
    return "".join(codes) + text + C.RESET


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit_json(data: Any, *, pretty: bool = True) -> None:
    """Print JSON to stdout for agent consumption."""
    if pretty:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, ensure_ascii=False))


def _die(message: str, code: int = 1) -> None:
    print(_color(f"Error: {message}", C.RED, C.BOLD), file=sys.stderr)
    sys.exit(code)


_QUIET = False


def _info(message: str) -> None:
    if not _QUIET:
        print(_color(message, C.CYAN))


def _success(message: str) -> None:
    if not _QUIET:
        print(_color(message, C.GREEN))


def _warn(message: str) -> None:
    if not _QUIET:
        print(_color(message, C.YELLOW))


# ---------------------------------------------------------------------------
# Config (minimal YAML — stdlib only)
# ---------------------------------------------------------------------------

def load_config() -> dict[str, Any]:
    """Load config.yaml if present; return empty dict on failure."""
    if not CONFIG_PATH.is_file():
        return {}
    try:
        text = CONFIG_PATH.read_text(encoding="utf-8")
    except OSError:
        return {}
    return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a subset of YAML sufficient for config.yaml (nested key: value)."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        if ":" not in content:
            continue
        key, _, rest = content.partition(":")
        key = key.strip()
        value_str = rest.strip()

        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if not value_str:
            new_dict: dict[str, Any] = {}
            parent[key] = new_dict
            stack.append((indent, new_dict))
        else:
            parent[key] = _yaml_scalar(value_str)

    return root


def _yaml_scalar(s: str) -> Any:
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_yaml_scalar(p.strip().strip('"').strip("'")) for p in inner.split(",")]
    return s


def default_models() -> dict[str, str]:
    cfg = load_config()
    models = cfg.get("models", {})
    if isinstance(models, dict):
        return {str(k): str(v) for k, v in models.items()}
    return {}


def default_max_sources() -> int:
    cfg = load_config()
    defaults = cfg.get("defaults", {})
    if isinstance(defaults, dict):
        return int(defaults.get("max_sources", 20))
    return 20


# ---------------------------------------------------------------------------
# Session I/O (atomic writes)
# ---------------------------------------------------------------------------

def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def _ensure_sessions_dir() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def validate_session_id(session_id: str) -> str:
    sid = session_id.strip().lower()
    if not UUID_RE.match(sid):
        _die(f"Invalid session ID (expected UUID): {session_id}")
    return sid


def load_session(session_id: str) -> dict[str, Any]:
    sid = validate_session_id(session_id)
    path = _session_path(sid)
    if not path.is_file():
        _die(f"Session not found: {sid}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _die(f"Corrupt session file {path}: {e}")
    if data.get("session_id") != sid:
        _die(f"Session ID mismatch in file (expected {sid})")
    return data


def save_session(session: dict[str, Any]) -> None:
    _ensure_sessions_dir()
    sid = session["session_id"]
    path = _session_path(sid)
    session["updated_at"] = _now_iso()
    tmp = path.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    except OSError as e:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        _die(f"Failed to save session {sid}: {e}")


def new_session_state(question: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    sid = str(uuid.uuid4())
    now = _now_iso()
    models = default_models()
    return {
        "session_id": sid,
        "created_at": now,
        "updated_at": now,
        "status": "initialized",
        "research_question": question,
        "sources": sources,
        "intake": None,
        "findings": [],
        "clarification": None,
        "synthesis": None,
        "report": None,
        "pipeline_metadata": {
            "models_used": models,
            "total_sources": len(sources),
            "total_findings": 0,
            "total_duration_seconds": None,
            "started_at": now,
        },
    }


# ---------------------------------------------------------------------------
# Source helpers
# ---------------------------------------------------------------------------

def source_id_from_reference(reference: str) -> str:
    """Deterministic source ID from normalized reference (re-add is idempotent)."""
    normalized = reference.strip().lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]
    return f"src-{digest}"


def detect_source_type(reference: str, explicit: str | None = None) -> str:
    if explicit:
        t = explicit.lower()
        if t not in VALID_SOURCE_TYPES:
            _die(f"Invalid source type '{explicit}'. Valid: {', '.join(sorted(VALID_SOURCE_TYPES))}")
        return t

    ref = reference.strip()
    lower = ref.lower()

    if lower.startswith(("http://", "https://")):
        if "github.com" in lower:
            return "github"
        if "huggingface.co" in lower:
            return "huggingface"
        if "drive.google.com" in lower or "docs.google.com" in lower:
            return "gdrive"
        return "url"
    if ref.startswith("#") or "slack.com" in lower or lower.startswith("slack:"):
        return "slack"
    if "github.com" in lower:
        return "github"
    if Path(ref).expanduser().is_file():
        return "file"
    if "huggingface.co" in lower:
        return "huggingface"

    _warn(f"Could not auto-detect type for: {reference}")
    print("Specify type with --type (file|url|slack|github|gdrive|huggingface|dataverse|kubernetes)")
    _die("Source type required when auto-detection fails")


def build_source(reference: str, source_type: str | None = None, title: str | None = None) -> dict[str, Any]:
    ref = reference.strip()
    stype = detect_source_type(ref, source_type)
    sid = source_id_from_reference(ref)
    return {
        "id": sid,
        "type": stype,
        "reference": ref,
        "title": title or ref,
        "ingested": False,
        "ingested_at": None,
    }


def upsert_source(session: dict[str, Any], source: dict[str, Any]) -> bool:
    """Add or update source. Returns True if newly added."""
    for i, existing in enumerate(session["sources"]):
        if existing["id"] == source["id"]:
            merged = {**existing, **source}
            merged["id"] = existing["id"]
            if existing.get("ingested"):
                merged["ingested"] = True
                merged["ingested_at"] = existing.get("ingested_at")
            session["sources"][i] = merged
            return False
    session["sources"].append(source)
    session["pipeline_metadata"]["total_sources"] = len(session["sources"])
    return True


def parse_json_payload(args: argparse.Namespace) -> Any:
    """Load JSON from --output, --output-file, or stdin."""
    if getattr(args, "output_file", None):
        path = Path(args.output_file).expanduser()
        if not path.is_file():
            _die(f"Output file not found: {path}")
        raw = path.read_text(encoding="utf-8")
    elif getattr(args, "output", None):
        raw = args.output
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        _die("Provide JSON via --output, --output-file, or stdin")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        _die(f"Invalid JSON: {e}")


def _finding_key(f: dict[str, Any]) -> str:
    return f.get("finding_id") or f"{f.get('source_id', '')}:{f.get('sub_question', '')}"


def merge_findings(session: dict[str, Any], new_findings: list[dict[str, Any]]) -> int:
    """Idempotent merge by finding_id or source_id+sub_question. Returns count added/updated."""
    index = {_finding_key(f): i for i, f in enumerate(session["findings"])}
    updated = 0
    for f in new_findings:
        if not isinstance(f, dict):
            continue
        key = _finding_key(f)
        if key in index:
            session["findings"][index[key]] = {**session["findings"][index[key]], **f}
        else:
            index[key] = len(session["findings"])
            session["findings"].append(f)
        updated += 1
    session["pipeline_metadata"]["total_findings"] = len(session["findings"])
    return updated


def ingestion_progress(session: dict[str, Any]) -> tuple[int, int]:
    sources = session.get("sources", [])
    total = len(sources)
    done = sum(1 for s in sources if s.get("ingested"))
    return done, total


def _duration_seconds(session: dict[str, Any]) -> int | None:
    started = session.get("pipeline_metadata", {}).get("started_at")
    if not started:
        return None
    try:
        t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
        t1 = datetime.now(timezone.utc)
        return int((t1 - t0).total_seconds())
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    _ensure_sessions_dir()
    question = args.research_question.strip()
    if not question:
        _die("Research question cannot be empty")

    sources: list[dict[str, Any]] = []
    for ref in args.sources or []:
        sources.append(build_source(ref))

    session = new_session_state(question, sources)
    save_session(session)

    _success(f"Session created: {session['session_id']}")
    _info(f"Question: {question[:80]}{'...' if len(question) > 80 else ''}")
    _info(f"Sources: {len(sources)}")

    result = {
        "ok": True,
        "command": "init",
        "session_id": session["session_id"],
        "status": session["status"],
        "research_question": question,
        "sources": [
            {"id": s["id"], "type": s["type"], "reference": s["reference"], "title": s["title"]}
            for s in sources
        ],
        "source_count": len(sources),
        "session_path": str(_session_path(session["session_id"])),
    }
    _emit_json(result)


def cmd_sources(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    if session["status"] in TERMINAL_STATUSES:
        _die(f"Session is in terminal state: {session['status']}")

    source = build_source(args.add, args.type, getattr(args, "title", None))
    is_new = upsert_source(session, source)
    save_session(session)

    action = "added" if is_new else "updated"
    _success(f"Source {action}: {source['id']} ({source['type']})")

    _emit_json({
        "ok": True,
        "command": "sources",
        "session_id": session["session_id"],
        "action": action,
        "source": source,
        "total_sources": len(session["sources"]),
    })


def cmd_status(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    ingested, total = ingestion_progress(session)

    sub_questions: list[str] = []
    if session.get("intake") and session["intake"].get("sub_questions"):
        sub_questions = session["intake"]["sub_questions"]
    elif session.get("clarification") and session["clarification"].get("refined_questions"):
        sub_questions = session["clarification"]["refined_questions"]

    summary = {
        "ok": True,
        "command": "status",
        "session_id": session["session_id"],
        "status": session["status"],
        "research_question": session["research_question"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "sources_total": total,
        "sources_ingested": ingested,
        "sources_pending": total - ingested,
        "findings_count": len(session.get("findings", [])),
        "sub_questions_count": len(sub_questions),
        "has_intake": session.get("intake") is not None,
        "has_clarification": session.get("clarification") is not None,
        "has_synthesis": session.get("synthesis") is not None,
        "report_path": (session.get("report") or {}).get("file_path"),
        "is_terminal": session["status"] in TERMINAL_STATUSES,
    }
    _emit_json(summary)


def cmd_intake(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    payload = parse_json_payload(args)

    intake = {
        "depth": payload.get("depth", "deep"),
        "sub_questions": payload.get("sub_questions", []),
        "source_relevance_map": payload.get("source_relevance_map", {}),
        "ambiguity_flags": payload.get("ambiguity_flags", []),
    }
    if payload.get("models_used"):
        session["pipeline_metadata"]["models_used"].update(payload["models_used"])

    session["intake"] = intake
    session["status"] = "intake_complete"
    save_session(session)

    _success("Intake complete")
    _info(f"Depth: {intake['depth']}")
    _info(f"Sub-questions: {len(intake['sub_questions'])}")
    _info(f"Ambiguity flags: {len(intake['ambiguity_flags'])}")

    _emit_json({
        "ok": True,
        "command": "intake",
        "session_id": session["session_id"],
        "status": session["status"],
        "intake_summary": {
            "depth": intake["depth"],
            "sub_questions": intake["sub_questions"],
            "sub_question_count": len(intake["sub_questions"]),
            "ambiguity_flags": intake["ambiguity_flags"],
        },
    })


def cmd_ingest(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    payload = parse_json_payload(args)
    source_id = args.source_id.strip()

    source = next((s for s in session["sources"] if s["id"] == source_id), None)
    if not source:
        _die(f"Unknown source_id: {source_id}")

    findings = payload.get("findings", [])
    if isinstance(findings, list):
        merge_findings(session, findings)
    elif payload.get("finding"):
        merge_findings(session, [payload["finding"]])

    source["ingested"] = True
    source["ingested_at"] = _now_iso()
    if payload.get("title"):
        source["title"] = payload["title"]

    done, total = ingestion_progress(session)
    session["status"] = "ingesting"
    if done >= total and total > 0:
        session["status"] = "ingestion_complete"

    save_session(session)

    _success(f"Ingested {source_id}: {done}/{total} sources complete")

    _emit_json({
        "ok": True,
        "command": "ingest",
        "session_id": session["session_id"],
        "status": session["status"],
        "source_id": source_id,
        "findings_added": len(findings) if isinstance(findings, list) else 0,
        "total_findings": len(session["findings"]),
        "ingestion_progress": {"done": done, "total": total, "pending": total - done},
    })


def cmd_clarify(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    payload = parse_json_payload(args)

    clarification = {
        "refined_questions": payload.get("refined_questions", payload.get("sub_questions", [])),
        "user_responses": payload.get("user_responses", {}),
    }
    session["clarification"] = clarification
    session["status"] = "clarification_complete"
    save_session(session)

    _success("Clarification complete")
    _info(f"Refined questions: {len(clarification['refined_questions'])}")

    _emit_json({
        "ok": True,
        "command": "clarify",
        "session_id": session["session_id"],
        "status": session["status"],
        "refined_questions": clarification["refined_questions"],
        "refined_count": len(clarification["refined_questions"]),
    })


def cmd_synthesize(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    payload = parse_json_payload(args)

    synthesis = {
        "per_question": payload.get("per_question", []),
        "agreements": payload.get("agreements", []),
        "contradictions": payload.get("contradictions", []),
        "gaps": payload.get("gaps", []),
    }
    session["synthesis"] = synthesis
    session["status"] = "synthesis_complete"
    save_session(session)

    _success("Synthesis complete")
    _info(f"Per-question syntheses: {len(synthesis['per_question'])}")
    _info(f"Agreements: {len(synthesis['agreements'])}, Contradictions: {len(synthesis['contradictions'])}, Gaps: {len(synthesis['gaps'])}")

    _emit_json({
        "ok": True,
        "command": "synthesize",
        "session_id": session["session_id"],
        "status": session["status"],
        "synthesis_summary": {
            "per_question_count": len(synthesis["per_question"]),
            "agreements_count": len(synthesis["agreements"]),
            "contradictions_count": len(synthesis["contradictions"]),
            "gaps_count": len(synthesis["gaps"]),
        },
    })


def _sub_questions_for_session(session: dict[str, Any]) -> list[str]:
    if session.get("clarification") and session["clarification"].get("refined_questions"):
        return session["clarification"]["refined_questions"]
    if session.get("intake") and session["intake"].get("sub_questions"):
        return session["intake"]["sub_questions"]
    return []


def cmd_prepare_report(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)

    template = ""
    if TEMPLATE_PATH.is_file():
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    else:
        _warn(f"Report template not found at {TEMPLATE_PATH}")

    duration = _duration_seconds(session)
    if duration is not None:
        session["pipeline_metadata"]["total_duration_seconds"] = duration

    sub_questions = _sub_questions_for_session(session)
    intake = session.get("intake") or {}
    depth = intake.get("depth", "deep")

    briefing = {
        "research_question": session["research_question"],
        "session_id": session["session_id"],
        "depth": depth,
        "sub_questions": sub_questions,
        "findings": session.get("findings", []),
        "synthesis": session.get("synthesis") or {},
        "sources": session.get("sources", []),
        "intake": intake,
        "clarification": session.get("clarification"),
        "citation_index": _build_citation_index(session),
        "pipeline_metadata": session.get("pipeline_metadata", {}),
        "report_template": template,
        "report_template_path": str(TEMPLATE_PATH),
        "generated_at": _now_iso(),
    }

    session["status"] = "reporting"
    save_session(session)

    _success("Report briefing package ready")
    _info(f"Findings: {len(briefing['findings'])}, Sources: {len(briefing['sources'])}")

    _emit_json({
        "ok": True,
        "command": "prepare-report",
        "session_id": session["session_id"],
        "status": session["status"],
        "briefing": briefing,
    })


def _build_citation_index(session: dict[str, Any]) -> dict[str, Any]:
    """Map source_id -> metadata and finding_ids for report writer."""
    by_source: dict[str, list[str]] = {}
    for f in session.get("findings", []):
        sid = f.get("source_id")
        fid = f.get("finding_id")
        if sid and fid:
            by_source.setdefault(sid, []).append(fid)

    sources_by_id = {s["id"]: s for s in session.get("sources", [])}
    return {
        "sources": sources_by_id,
        "findings_by_source": by_source,
        "all_finding_ids": [f.get("finding_id") for f in session.get("findings", []) if f.get("finding_id")],
    }


def cmd_save_report(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    report_path = Path(args.file).expanduser()
    if not report_path.parent.exists():
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            _die(f"Cannot create directory for report: {e}")

    content = ""
    if getattr(args, "content_file", None):
        content = Path(args.content_file).expanduser().read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    elif report_path.is_file():
        content = report_path.read_text(encoding="utf-8")
    else:
        _die("Provide report markdown via --content-file, stdin, or an existing --file to confirm")

    try:
        report_path.write_text(content, encoding="utf-8")
    except OSError as e:
        _die(f"Failed to write report: {e}")

    session["report"] = {
        "file_path": str(report_path.resolve()),
        "generated_at": _now_iso(),
    }
    session["status"] = "complete"
    session["pipeline_metadata"]["total_duration_seconds"] = _duration_seconds(session)
    save_session(session)

    _success(f"Research complete — report saved to {report_path}")

    _emit_json({
        "ok": True,
        "command": "save-report",
        "session_id": session["session_id"],
        "status": session["status"],
        "report_path": session["report"]["file_path"],
        "generated_at": session["report"]["generated_at"],
        "pipeline_metadata": session["pipeline_metadata"],
    })


def cmd_list(args: argparse.Namespace) -> None:
    _ensure_sessions_dir()
    sessions: list[dict[str, Any]] = []

    for path in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        q = data.get("research_question", "")
        sessions.append({
            "session_id": data.get("session_id", path.stem),
            "status": data.get("status", "unknown"),
            "research_question": q[:72] + ("..." if len(q) > 72 else ""),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "source_count": len(data.get("sources", [])),
            "findings_count": len(data.get("findings", [])),
        })

    if args.json:
        _emit_json({"ok": True, "command": "list", "sessions": sessions, "count": len(sessions)})
        return

    if not sessions:
        if not _QUIET:
            _info("No research sessions found.")
        _emit_json({"ok": True, "command": "list", "sessions": sessions, "count": 0})
        return

    if _QUIET or args.json:
        _emit_json({"ok": True, "command": "list", "sessions": sessions, "count": len(sessions)})
        return

    print(_color(f"\n{'Session ID':<38} {'Status':<22} {'Sources':>7} {'Findings':>8}  Question", C.BOLD))
    print(_color("-" * 110, C.DIM))
    for s in sessions:
        print(
            f"{s['session_id']:<38} {s['status']:<22} {s['source_count']:>7} {s['findings_count']:>8}  "
            f"{s['research_question']}"
        )
    print()
    _emit_json({"ok": True, "command": "list", "sessions": sessions, "count": len(sessions)})


def cmd_export(args: argparse.Namespace) -> None:
    session = load_session(args.session_id)
    out_path = getattr(args, "out", None)

    if out_path:
        dest = Path(out_path).expanduser()
        dest.write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _success(f"Exported session to {dest}")

    _emit_json({"ok": True, "command": "export", "session": session})


# ---------------------------------------------------------------------------
# Argument parsers
# ---------------------------------------------------------------------------

def _add_json_input(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", help="JSON string from agent subagent")
    group.add_argument("--output-file", help="Path to JSON file from agent subagent")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orchestrator.py",
        description="Deep Research pipeline state manager (local, no LLM calls)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 orchestrator.py init "What are the tradeoffs of X?" --sources https://example.com ./paper.pdf
  python3 orchestrator.py intake <session_id> --output-file intake.json
  python3 orchestrator.py ingest <session_id> --source-id src-abc12345 --output '{"findings":[...]}'
  python3 orchestrator.py prepare-report <session_id>
  python3 orchestrator.py save-report <session_id> --file ./report.md < report.md
""",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress human-readable messages; emit JSON only (for agent parsing)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new research session")
    p_init.add_argument("research_question", help="Primary research question")
    p_init.add_argument("--sources", nargs="*", default=[], metavar="SOURCE", help="Initial sources (paths, URLs, etc.)")
    p_init.set_defaults(func=cmd_init)

    p_sources = sub.add_parser("sources", help="Add sources to an existing session")
    p_sources.add_argument("session_id", help="Session UUID")
    p_sources.add_argument("--add", required=True, metavar="SOURCE", help="Source reference to add")
    p_sources.add_argument("--type", choices=sorted(VALID_SOURCE_TYPES), help="Source type (auto-detected if omitted)")
    p_sources.add_argument("--title", help="Human-readable title")
    p_sources.set_defaults(func=cmd_sources)

    p_status = sub.add_parser("status", help="Show session status (JSON)")
    p_status.add_argument("session_id", help="Session UUID")
    p_status.set_defaults(func=cmd_status)

    p_intake = sub.add_parser("intake", help="Save intake classifier output")
    p_intake.add_argument("session_id", help="Session UUID")
    _add_json_input(p_intake)
    p_intake.set_defaults(func=cmd_intake)

    p_ingest = sub.add_parser("ingest", help="Save source ingester output for one source")
    p_ingest.add_argument("session_id", help="Session UUID")
    p_ingest.add_argument("--source-id", required=True, help="Source ID (e.g. src-abc12345)")
    _add_json_input(p_ingest)
    p_ingest.set_defaults(func=cmd_ingest)

    p_clarify = sub.add_parser("clarify", help="Save clarifier output")
    p_clarify.add_argument("session_id", help="Session UUID")
    _add_json_input(p_clarify)
    p_clarify.set_defaults(func=cmd_clarify)

    p_synth = sub.add_parser("synthesize", help="Save reasoning synthesizer output")
    p_synth.add_argument("session_id", help="Session UUID")
    _add_json_input(p_synth)
    p_synth.set_defaults(func=cmd_synthesize)

    p_prep = sub.add_parser("prepare-report", help="Assemble briefing package for report writer")
    p_prep.add_argument("session_id", help="Session UUID")
    p_prep.set_defaults(func=cmd_prepare_report)

    p_save = sub.add_parser("save-report", help="Save final report markdown and mark complete")
    p_save.add_argument("session_id", help="Session UUID")
    p_save.add_argument("--file", required=True, help="Output path for report markdown")
    p_save.add_argument("--content-file", help="Markdown file to copy (alternative to stdin)")
    p_save.set_defaults(func=cmd_save_report)

    p_list = sub.add_parser("list", help="List all research sessions")
    p_list.add_argument("--json", action="store_true", help="JSON-only output (no table)")
    p_list.set_defaults(func=cmd_list)

    p_export = sub.add_parser("export", help="Export full session JSON")
    p_export.add_argument("session_id", help="Session UUID")
    p_export.add_argument("--out", help="Optional file path to write export")
    p_export.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    global _QUIET
    parser = build_parser()
    args = parser.parse_args()
    _QUIET = getattr(args, "quiet", False)
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
