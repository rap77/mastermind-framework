"""Event emission integration for task executor."""

import time
import uuid
from typing import Any, Dict

from .event_emitter import EventEmitter


class EventIntegration:
    """Integrates event emission into brain execution."""

    def __init__(self, event_emitter: EventEmitter | None = None):
        """Initialize event integration.

        Args:
            event_emitter: Optional event emitter (creates new if None)
        """
        self.event_emitter = event_emitter or EventEmitter()

    async def execute_brain_with_events(
        self,
        execute_brain_fn: Any,
        task_id: str,
        brain_id: str,
        query: str,
        provider_name: str = "notebooklm",
        session_id: str | uuid.UUID | None = None,
    ) -> Dict[str, Any]:
        """Execute brain with event emission.

        Args:
            execute_brain_fn: Original execute_brain function
            task_id: Unique task identifier
            brain_id: Brain to execute
            query: Query string
            provider_name: Provider for rate limiting
            session_id: Optional session ID (generates if None)

        Returns:
            Dictionary with brain_id, status, and result/error
        """
        if session_id is None:
            session_id = uuid.uuid4()

        start_time = time.time()

        # Emit brain_started event
        try:
            await self.event_emitter.emit_brain_started(
                brain_id=brain_id,
                session_id=session_id,
                brief=query,
                flow_config={"provider": provider_name},
            )
        except Exception as e:
            # Don't fail execution if event emission fails
            print(f"Warning: Failed to emit brain_started event: {e}")

        # Execute brain
        try:
            result: Dict[str, Any] = await execute_brain_fn(
                task_id, brain_id, query, provider_name
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Emit brain_completed event
            try:
                await self.event_emitter.emit_brain_completed(
                    brain_id=brain_id,
                    session_id=session_id,
                    duration_ms=duration_ms,
                    result={
                        "status": result.get("status"),
                        "summary": str(result.get("result", ""))[:200],
                    },
                )
            except Exception as e:
                print(f"Warning: Failed to emit brain_completed event: {e}")

            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Emit brain_failed event
            try:
                await self.event_emitter.emit_brain_failed(
                    brain_id=brain_id,
                    session_id=session_id,
                    error=str(e),
                    stage="execution",
                )
            except Exception as event_err:
                print(f"Warning: Failed to emit brain_failed event: {event_err}")

            raise

    async def close(self) -> None:
        """Close event emitter."""
        await self.event_emitter.close()
