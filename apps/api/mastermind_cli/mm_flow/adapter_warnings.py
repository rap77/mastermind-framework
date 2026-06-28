"""Project-specific adapter warnings for the unified harness boundary."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal


AdapterWarningSeverity = Literal["info", "warning", "error"]


@dataclass(frozen=True, slots=True)
class AdapterWarning:
    """One project-specific adapter warning."""

    code: str
    message: str
    severity: AdapterWarningSeverity


@dataclass(frozen=True, slots=True)
class AdapterWarnings:
    """Collection of project-specific warnings surfaced by an adapter."""

    items: tuple[AdapterWarning, ...]

    @property
    def passed(self) -> bool:
        """Return True when no warning has error severity."""
        return not any(item.severity == "error" for item in self.items)

    @property
    def errors(self) -> tuple[AdapterWarning, ...]:
        """Return the error-severity warnings."""
        return tuple(item for item in self.items if item.severity == "error")

    @property
    def warnings(self) -> tuple[AdapterWarning, ...]:
        """Return the warning-severity warnings."""
        return tuple(item for item in self.items if item.severity == "warning")

    def __bool__(self) -> bool:
        """Allow truthiness checks based on the passed flag."""
        return self.passed

    def __iter__(self) -> Iterable[AdapterWarning]:
        """Iterate over the contained warnings."""
        return iter(self.items)
