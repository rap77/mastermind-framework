"""Window Scheduler — core reusable layer for temporal execution capacity management.

This module implements the minimum viable entity set for the Window Scheduler:
- BackendSession: backend inventory
- AvailabilityState: temporal state per backend
- RunPolicy: active execution policy
- SchedulerEvent: auditable event record
- SchedulerCheckpoint: minimal resume point

Schema constraints (from docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md):
1. No backend_switch without checkpoint_id
2. No checkpoint without next_step_summary
3. All reset estimations must record estimation_source and estimation_confidence
4. Every run must have an explicit run_policy
"""

from mastermind_cli.window_scheduler.database.session import (
    dispose_engines,
    get_engine,
    get_session,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.window_scheduler.models import (
    AvailabilityState,
    BackendSession,
    RunPolicy,
    SchedulerCheckpoint,
    SchedulerEvent,
)

__all__ = [
    # Models
    "AvailabilityState",
    "BackendSession",
    "RunPolicy",
    "SchedulerCheckpoint",
    "SchedulerEvent",
    # Database
    "dispose_engines",
    "get_engine",
    "get_session",
    "get_session_factory",
    "initialize_database",
]
