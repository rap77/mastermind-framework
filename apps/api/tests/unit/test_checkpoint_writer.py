"""Tests for checkpoint_writer.py — behavioral criteria from Brain #7 C6."""

from mastermind_cli.mm_flow.checkpoint_writer import (
    has_write_operations,
    write_checkpoint,
)


# ---- C6: Mock transcripts with Write in position 8 of 10 ----


def make_transcript(write_pos: int | None, total: int = 10) -> list[dict]:
    """Create synthetic transcript. If write_pos given, inject Write tool call there."""
    msgs = []
    for i in range(total):
        if i == write_pos:
            msgs.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "name": "Write",
                            "input": {"file_path": "foo.py", "content": "x"},
                        }
                    ],
                }
            )
        else:
            msgs.append(
                {
                    "role": "assistant",
                    "tool_calls": [{"name": "Read", "input": {"file_path": "bar.py"}}],
                }
            )
    return msgs


def test_write_in_position_8_triggers_detection():
    """C6: Write tool call in position 8 of 10 must be detected."""
    transcript = make_transcript(write_pos=8, total=10)
    assert has_write_operations(transcript) is True


def test_read_only_transcript_no_trigger():
    """C6: 10/10 Read-only messages must NOT trigger checkpoint."""
    transcript = make_transcript(write_pos=None, total=10)
    assert has_write_operations(transcript) is False


def test_edit_tool_triggers_detection():
    transcript = [{"role": "assistant", "tool_calls": [{"name": "Edit", "input": {}}]}]
    assert has_write_operations(transcript) is True


def test_bash_with_redirect_triggers():
    transcript = [
        {
            "role": "assistant",
            "tool_calls": [
                {"name": "Bash", "input": {"command": "echo foo > output.txt"}}
            ],
        }
    ]
    assert has_write_operations(transcript) is True


def test_bash_grep_no_trigger():
    transcript = [
        {
            "role": "assistant",
            "tool_calls": [
                {"name": "Bash", "input": {"command": "grep -r pattern src/"}}
            ],
        }
    ]
    assert has_write_operations(transcript) is False


def test_write_checkpoint_creates_file(tmp_path):
    transcript = make_transcript(write_pos=0, total=3)
    checkpoint = tmp_path / "SESSION-CHECKPOINT.md"
    write_checkpoint(transcript, checkpoint_path=checkpoint)
    assert checkpoint.exists()
    content = checkpoint.read_text()
    assert "saved: false" in content


def test_write_checkpoint_contains_last_updated(tmp_path):
    transcript = make_transcript(write_pos=0, total=1)
    checkpoint = tmp_path / "SESSION-CHECKPOINT.md"
    write_checkpoint(
        transcript, checkpoint_path=checkpoint, timestamp="2026-04-14T13:00:00"
    )
    assert "2026-04-14T13:00:00" in checkpoint.read_text()
