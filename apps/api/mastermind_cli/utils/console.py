"""Console utility for MasterMind CLI.

Provides a test-isolated Console getter that ensures Rich output is
properly captured by Click's CliRunner during tests.

The problem: When Rich Console is created at module import time with
sys.stdout, and then pytest's output capture replaces sys.stdout,
the Console writes to a stale file descriptor and output disappears.

The solution: Create Console objects on-demand using the CURRENT sys.stdout,
not a cached reference from import time.
"""

import sys
from rich.console import Console


def get_console() -> Console:
    """Get a Console instance for output.

    Creates a fresh Console instance on each call, using the current
    sys.stdout. This ensures proper test isolation - even if pytest's
    output capture replaces sys.stdout between tests, we always use
    the current (correct) stdout.

    Test isolation strategy:
    - Always uses stdout (Click's CliRunner captures stdout)
    - Creates a new Console instance each call (no module-level caching)
    - Uses width=None to auto-detect terminal width
    - Explicitly sets stderr=False to avoid output redirection

    Performance impact: negligible (Console creation is cheap).

    Returns:
        Console: A Rich Console instance configured for output.
    """
    # Always use stdout - CliRunner captures it
    # width=None auto-detects, force_terminal=False respects environment
    # stderr=False ensures output goes to stdout, not stderr
    return Console(
        file=sys.stdout,
        width=None,
        force_terminal=False,
        stderr=False,
        legacy_windows=False,
    )
