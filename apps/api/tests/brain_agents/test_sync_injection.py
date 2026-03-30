"""
Phase 12 — SYNC tag resolution verification stubs (DISP-01, DISP-02)

These tests verify SYNC fragment isolation — each brain only receives its own SYNC content.
"""

import re
from pathlib import Path

import pytest


# Matches SYNC tags that are actual cross-reference pointers (not documentation examples).
# Excludes matches inside backtick code spans (e.g. `[SYNC: BF-NN-ID]` in docs).
SYNC_PATTERN = re.compile(r"(?<!`)\[SYNC:\s+BF-(\d{2})-(\w+)\](?!`)")


class TestSyncInjection:
    """DISP-02: SYNC tags resolved inline, no cross-talk between agent prompts."""

    def test_brain04_sync_tags_point_only_to_brain05(self):
        """
        Brain #4 Frontend feed has 4 SYNC tags.
        All must point to BF-05 (Backend). Zero cross-domain leakage.
        This is a static check — reads the feed file directly.
        """
        # ⚠️ CORRECCIÓN Brain #7: 5 niveles desde apps/api/tests/brain_agents/ hasta repo root
        # test file → brain_agents/ → tests/ → api/ → apps/ → repo_root
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        feed_04 = repo_root / ".planning" / "BRAIN-FEED-04-frontend.md"
        assert feed_04.exists(), f"BRAIN-FEED-04-frontend.md not found at {feed_04}"

        content = feed_04.read_text()
        sync_tags = SYNC_PATTERN.findall(content)

        assert (
            len(sync_tags) > 0
        ), "BRAIN-FEED-04-frontend.md has no SYNC tags — expected 4 from Phase 10"

        for owner_id, section_id in sync_tags:
            assert owner_id == "05", (
                f"Brain #4 has SYNC tag pointing to BF-{owner_id}-{section_id}, "
                f"expected only BF-05 (Backend). Cross-talk detected."
            )

    def test_sync_characterization_brain04_cites_injected_bf05_fragment(self):
        """
        SYNC characterization test (from Brain #6 QA spec):
        WITHOUT SYNC injection: Brain #4 returns "No impact" for BF-05-WS-AUTH question.
        WITH SYNC injection (correct): Brain #4 cites the BF-05 fragment explicitly.

        This test documents the requirement — real execution requires moment-2.md to be written.
        Manual acceptance: temporarily modify BF-05-WS-AUTH, invoke Brain #4,
        verify citation of the injected fragment appears in response.
        """
        pytest.fail(
            "STUB — Not yet implemented. "
            "Manual characterization test after moment-2.md implements SYNC injection. "
            "Steps: (1) Modify .planning/BRAIN-FEED-05-backend.md BF-05-WS-AUTH section. "
            "(2) Invoke Brain #4 with a WS auth question. "
            "(3) Verify Brain #4 cites the BF-05 fragment explicitly. "
            "No citation = SYNC injection failed."
        )

    def test_no_sync_tags_in_global_feed(self):
        """
        Global BRAIN-FEED.md must have zero SYNC tags.
        SYNC tags are a domain-feed-only construct.
        """
        # ⚠️ CORRECCIÓN Brain #7: 5 niveles hasta repo root (misma lógica que test_brain04_sync_tags)
        # test file → brain_agents/ → tests/ → api/ → apps/ → repo_root
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        global_feed = repo_root / ".planning" / "BRAIN-FEED.md"
        assert global_feed.exists(), f"BRAIN-FEED.md not found at {global_feed}"

        content = global_feed.read_text()
        sync_tags = SYNC_PATTERN.findall(content)

        assert (
            len(sync_tags) == 0
        ), f"Global BRAIN-FEED.md contains SYNC tags (must be zero): {sync_tags}"
