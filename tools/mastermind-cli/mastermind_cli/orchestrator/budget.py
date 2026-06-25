"""Token budget enforcement with append-only persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class BudgetVerdict(str, Enum):
    """Possible budget enforcement outcomes."""

    ALLOW = "allow"
    DENY = "deny"
    PAUSE_AND_ASK = "pause_and_ask"


@dataclass(frozen=True, slots=True)
class BudgetContext:
    """Minimal execution context for budget tracking."""

    session_id: str
    task_id: str


@dataclass(frozen=True, slots=True)
class BudgetSnapshot:
    """Current budget state for a context."""

    session_id: str
    task_id: str
    task_consumed: int
    session_consumed: int
    task_budget_tokens: int
    session_budget_tokens: int


@dataclass(frozen=True, slots=True)
class BudgetEvent:
    """Append-only budget record."""

    timestamp: str
    event_type: str
    context: BudgetContext
    tokens: int
    task_consumed: int
    session_consumed: int


class BudgetLedger:
    """Append-only JSONL ledger for budget events."""

    def __init__(self, filepath: str | Path) -> None:
        """Initialize the ledger path used for append-only persistence."""
        self.filepath = Path(filepath)

    def append_event(self, event: BudgetEvent) -> None:
        """Append one budget event."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(self._to_jsonable(event), ensure_ascii=False))
            handle.write("\n")

    def load_events(self) -> list[BudgetEvent]:
        """Load all recorded events."""
        if not self.filepath.exists():
            return []

        events: list[BudgetEvent] = []
        for line in self.filepath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            events.append(self._from_dict(payload))
        return events

    def _to_jsonable(self, value: Any) -> Any:
        """Convert dataclasses and enums into JSON serializable values."""
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value):
            return {key: self._to_jsonable(item) for key, item in asdict(value).items()}
        if isinstance(value, dict):
            return {key: self._to_jsonable(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        return value

    def _from_dict(self, payload: dict[str, Any]) -> BudgetEvent:
        """Rehydrate a budget event from JSON."""
        return BudgetEvent(
            timestamp=payload["timestamp"],
            event_type=payload["event_type"],
            context=BudgetContext(**payload["context"]),
            tokens=payload["tokens"],
            task_consumed=payload["task_consumed"],
            session_consumed=payload["session_consumed"],
        )


class BudgetEnforcer:
    """Track budget consumption and block overages."""

    def __init__(
        self,
        task_budget_tokens: int,
        session_budget_tokens: int,
        ledger: BudgetLedger | None = None,
    ) -> None:
        """Initialize budget thresholds and in-memory consumption state."""
        self.task_budget_tokens = task_budget_tokens
        self.session_budget_tokens = session_budget_tokens
        self.ledger = ledger or BudgetLedger(
            Path(".mm-flow") / "planning" / "audit" / "budget-events.jsonl"
        )
        self._task_consumed: dict[tuple[str, str], int] = {}
        self._session_consumed: dict[str, int] = {}
        self._load_state()

    def pre_call(self, estimated_tokens: int, context: BudgetContext) -> BudgetVerdict:
        """Evaluate projected cost before a call."""
        task_consumed = self._task_consumed.get(self._task_key(context), 0)
        session_consumed = self._session_consumed.get(context.session_id, 0)

        projected_task = task_consumed + estimated_tokens
        projected_session = session_consumed + estimated_tokens

        if projected_session >= self.session_budget_tokens:
            return BudgetVerdict.DENY
        if projected_task > self.task_budget_tokens * 2:
            return BudgetVerdict.DENY
        if projected_task > self.task_budget_tokens:
            return BudgetVerdict.PAUSE_AND_ASK
        return BudgetVerdict.ALLOW

    def post_call(self, actual_tokens: int, context: BudgetContext) -> None:
        """Record actual consumption after a call."""
        task_key = self._task_key(context)
        task_consumed = self._task_consumed.get(task_key, 0) + actual_tokens
        session_consumed = (
            self._session_consumed.get(context.session_id, 0) + actual_tokens
        )

        self._task_consumed[task_key] = task_consumed
        self._session_consumed[context.session_id] = session_consumed
        self.ledger.append_event(
            BudgetEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type="post_call",
                context=context,
                tokens=actual_tokens,
                task_consumed=task_consumed,
                session_consumed=session_consumed,
            )
        )

    def snapshot(self, context: BudgetContext) -> BudgetSnapshot:
        """Return the current budget snapshot."""
        task_consumed = self._task_consumed.get(self._task_key(context), 0)
        session_consumed = self._session_consumed.get(context.session_id, 0)
        return BudgetSnapshot(
            session_id=context.session_id,
            task_id=context.task_id,
            task_consumed=task_consumed,
            session_consumed=session_consumed,
            task_budget_tokens=self.task_budget_tokens,
            session_budget_tokens=self.session_budget_tokens,
        )

    def _load_state(self) -> None:
        """Restore counts from the append-only ledger."""
        for event in self.ledger.load_events():
            task_key = self._task_key(event.context)
            self._task_consumed[task_key] = event.task_consumed
            self._session_consumed[event.context.session_id] = event.session_consumed

    def _task_key(self, context: BudgetContext) -> tuple[str, str]:
        """Build a stable key for the task/session pair."""
        return (context.session_id, context.task_id)
