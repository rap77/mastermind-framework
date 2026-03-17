"""Smoke tests for authentication flow.

Tests will be implemented after Plan 02 Task 2.

Requirements: UI-02, UI-03

Note: These tests require a running server at localhost:8000.
Run manually with: uv run pytest tests/e2e/test_auth_smoke.py --no-cov
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def test_auth_smoke(page: Page):
    """Test authentication flow works (<30s smoke test)."""
    page.goto("http://localhost:8000")

    # Test login form visible
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("input[name='password']")).to_be_visible()

    # Test token storage after login
    # TODO: Implement after user creation
