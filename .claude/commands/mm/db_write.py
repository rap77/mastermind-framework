#!/usr/bin/env python3
"""CLI bridge for MasterMind DB writes from agents.

Agents cannot import psycopg2 directly. This script provides a Bash-callable
interface so task-executor, code-reviewer, and ship-executor can persist data
to PostgreSQL by invoking a single shell command.

Usage:
    python3 db_write.py --type <operation> --payload '<json>'

Operations:
    session_open        Open dev session, returns session UUID
    session_close       Close/update existing dev session
    brain_consultation  Save brain consultation record
    brain_feedback      Save brain feedback (insight, risk, lesson)
    artifact            Save artifact reference
    decision            Save technical/architectural decision
    experience          Save brain experience record
    audit_log           Save audit log entry

Output (machine-parseable):
    STATUS: ok
    ID: <uuid>          (when the operation returns a UUID)

On error:
    STATUS: error
    ERROR: <message>

Example:
    python3 db_write.py --type session_open \\
        --payload '{"started_by": "task-executor", "phase_number": 19}'

    python3 db_write.py --type brain_consultation \\
        --payload '{"brain_id": 6, "phase": 19, "input": "...", "output": "..."}'
"""

import argparse
import json
import sys
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent.parent.parent


def _read_project_id() -> str | None:
    """Read project_id from .mastermind/config.yaml."""
    config_path = _find_project_root() / ".mastermind" / "config.yaml"
    if not config_path.exists():
        return None
    for line in config_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("project_id:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return value if value else None
    return None


def _ok(record_id: str | None = None) -> None:
    print("STATUS: ok", flush=True)
    if record_id:
        print(f"ID: {record_id}", flush=True)


def _error(msg: str) -> None:
    print("STATUS: error", flush=True)
    print(f"ERROR: {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MasterMind DB write bridge for agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=[
            "session_open",
            "session_close",
            "brain_consultation",
            "brain_feedback",
            "artifact",
            "decision",
            "experience",
            "audit_log",
        ],
        help="Operation type",
    )
    parser.add_argument(
        "--payload",
        required=True,
        help="JSON payload for the operation",
    )
    parser.add_argument(
        "--project-id",
        default=None,
        help="Override project UUID (default: read from .mastermind/config.yaml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        payload: dict = json.loads(args.payload)
    except json.JSONDecodeError as e:
        _error(f"Invalid JSON payload: {e}")
        sys.exit(1)

    # Resolve project_id: CLI flag > config.yaml > None (db_client falls back to seed)
    project_id: str | None = (
        args.project_id or _read_project_id() or payload.get("project_id")
    )

    # Import db_client from same directory
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from db_client import MasterMindDB
    except ImportError as e:
        _error(f"Cannot import db_client: {e}")
        sys.exit(1)

    with MasterMindDB() as db:
        if not db.available:
            _error("PostgreSQL not available — DB operations disabled")
            sys.exit(0)  # Non-fatal: agents should continue without DB

        op = args.type

        if op == "session_open":
            record_id = db.save_session(
                started_by=payload.get("started_by", "unknown"),
                phase_number=payload.get("phase_number"),
                backend_used=payload.get("backend_used"),
                project_id=project_id,
            )
            _ok(record_id)

        elif op == "session_close":
            session_id = payload.get("session_id")
            if not session_id:
                _error("session_id required for session_close")
                sys.exit(1)
            success = db.update_session(
                session_id=session_id,
                status=payload.get("status", "completed"),
                tasks_completed=payload.get("tasks_completed", 0),
                tasks_total=payload.get("tasks_total", 0),
                commits_count=payload.get("commits_count", 0),
                discoveries=payload.get("discoveries"),
                next_steps=payload.get("next_steps"),
            )
            _ok() if success else _error("update_session returned False")

        elif op == "brain_consultation":
            record_id = db.save_brain_consultation(
                brain_id=int(payload.get("brain_id", 0)),
                phase=int(payload.get("phase", 0)),
                consultation_input=payload.get("input", ""),
                consultation_output=payload.get("output", ""),
                confidence=float(payload.get("confidence", 0.0)),
                backend_used=payload.get("backend_used"),
                tokens_used=int(payload.get("tokens_used", 0)),
                project_id=project_id,
            )
            _ok(record_id)

        elif op == "brain_feedback":
            record_id = db.save_brain_feedback(
                brain_id=int(payload.get("brain_id", 0)),
                feedback_type=payload.get("feedback_type", "insight"),
                title=payload.get("title", ""),
                content=payload.get("content", ""),
                confidence=payload.get("confidence"),
                impact_on_phase=payload.get("impact_on_phase"),
                engram_sync_id=payload.get("engram_sync_id"),
                metadata=payload.get("metadata"),
                project_id=project_id,
            )
            _ok(record_id)

        elif op == "artifact":
            record_id = db.save_artifact(
                artifact_type=payload.get("artifact_type", "other"),
                name=payload.get("name", "unnamed"),
                description=payload.get("description"),
                file_path=payload.get("file_path"),
                git_commit_hash=payload.get("git_commit_hash"),
                git_commit_message=payload.get("git_commit_message"),
                created_by=payload.get("created_by"),
                metadata=payload.get("metadata"),
                project_id=project_id,
            )
            _ok(record_id)

        elif op == "decision":
            record_id = db.save_decision(
                decision_type=payload.get("decision_type", "technical"),
                title=payload.get("title", ""),
                rationale=payload.get("rationale", ""),
                chosen_option=payload.get("chosen_option", ""),
                made_by=payload.get("made_by", "system"),
                alternatives=payload.get("alternatives"),
                impact_level=payload.get("impact_level", "medium"),
                impact_description=payload.get("impact_description"),
                confidence=float(payload.get("confidence", 0.5)),
                tags=payload.get("tags"),
                project_id=project_id,
            )
            _ok(record_id)

        elif op == "experience":
            record_id = db.save_experience(
                brain_id=payload.get("brain_id", "unknown"),
                session_id=payload.get("session_id", ""),
                quality_score=payload.get("quality_score"),
                insights=payload.get("insights"),
                patterns=payload.get("patterns"),
            )
            _ok(record_id)

        elif op == "audit_log":
            record_id = db.save_audit_log(
                action_type=payload.get("action_type", "unknown"),
                actor=payload.get("actor", "system"),
                description=payload.get("description", ""),
                actor_type=payload.get("actor_type", "system"),
                phase_number=payload.get("phase_number"),
                related_entity_type=payload.get("related_entity_type"),
                related_entity_id=payload.get("related_entity_id"),
                severity=payload.get("severity", "info"),
                metadata=payload.get("metadata"),
                project_id=project_id,
            )
            _ok(record_id)


if __name__ == "__main__":
    main()
