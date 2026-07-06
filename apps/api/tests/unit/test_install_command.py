"""Tests for install command fallbacks."""

from __future__ import annotations

from pathlib import Path

from mastermind_cli.commands import install as install_cmd


def test_uninstall_logs_readme_update_failure(monkeypatch) -> None:
    """README cleanup failures should be logged, not crash uninstall."""
    outputs: list[str] = []

    class _Console:
        def print(self, message: str) -> None:
            outputs.append(str(message))

    monkeypatch.setattr(install_cmd, "console", lambda: _Console())
    monkeypatch.setattr(install_cmd.Path, "cwd", staticmethod(lambda: Path("/repo")))

    def _exists(self: Path) -> bool:
        return self.name in {".mastermind-active", "README.md"}

    def _read_text(self: Path, *args, **kwargs) -> str:
        del args, kwargs
        raise OSError("boom")

    monkeypatch.setattr(Path, "exists", _exists, raising=False)
    monkeypatch.setattr(Path, "read_text", _read_text, raising=False)
    monkeypatch.setattr(Path, "unlink", lambda self: None, raising=False)
    monkeypatch.setattr(install_cmd.shutil, "rmtree", lambda *args, **kwargs: None)

    install_cmd.uninstall.callback(keep_config=True, remove_readme=True)

    assert any("Could not update README.md" in line for line in outputs)
