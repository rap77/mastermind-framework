# Generated proto types for Python
# TODO: Generate from proto/mastermind/v1/brain_runtime.proto using protoc
# Setup blocker: buf CLI and protoc not available, documented in velocity-baseline.md

from dataclasses import dataclass


@dataclass
class DispatchTaskRequest:
    brief: str
    user_id: str
    flow: str = "auto"


@dataclass
class DispatchTaskResponse:
    task_id: str
    status: str
    accepted_at_unix_ms: int
