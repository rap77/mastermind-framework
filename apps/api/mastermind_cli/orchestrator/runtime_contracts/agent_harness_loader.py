"""Standard content loader for Agent Harness bundles."""

from __future__ import annotations

from pathlib import Path


class AgentHarnessLoader:
    """Load files, routing files, and leaf primary files from a harness root."""

    _ROUTING_FILES = {
        "skills": "SKILLS.md",
        "references": "REFERENCES.md",
        "data": "DATA.md",
        "verification": "VERIFICATION.md",
    }

    def __init__(self, root: Path | str) -> None:
        """Initialize the loader with an Agent Harness root directory."""
        self.root = Path(root).resolve()

    def load_content(self, path: Path | str) -> str:
        """Load standard Agent Harness content for a relative path."""
        target = self._resolve_inside_root(path)
        if target.is_file():
            return target.read_text(encoding="utf-8")
        if target.is_dir():
            primary_file = self._primary_file_for_directory(target)
            if primary_file is not None:
                return primary_file.read_text(encoding="utf-8")
            return self._minimal_listing(target)
        raise ValueError(f"Path does not exist inside harness root: {path}")

    def _resolve_inside_root(self, path: Path | str) -> Path:
        """Resolve a path and reject traversal outside the harness root."""
        target = (self.root / path).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError(f"Path is outside harness root: {path}")
        return target

    def _primary_file_for_directory(self, directory: Path) -> Path | None:
        """Return the primary file for a harness directory when one exists."""
        if directory == self.root:
            return self._existing_file(directory / "HARNESS.md")

        routing_name = self._ROUTING_FILES.get(directory.name)
        if routing_name is not None:
            return self._existing_file(directory / routing_name)

        detector_file = self._find_leaf_detector(directory)
        if detector_file is not None:
            primary_name = self._primary_name_from_leaf_detector(detector_file)
            if primary_name is not None:
                return self._existing_file(directory / primary_name)
        return None

    def _find_leaf_detector(self, directory: Path) -> Path | None:
        """Find the nearest `.leaf-detectors` file from a directory upward."""
        current = directory
        while current == self.root or self.root in current.parents:
            detector_file = current / ".leaf-detectors"
            if detector_file.is_file():
                return detector_file
            if current == self.root:
                break
            current = current.parent
        return None

    @staticmethod
    def _primary_name_from_leaf_detector(detector_file: Path) -> str | None:
        """Return the primary filename declared by a leaf detector."""
        for line in detector_file.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == "skill" and value.strip():
                return value.strip()
        return None

    @staticmethod
    def _existing_file(path: Path) -> Path | None:
        """Return the file path when it exists."""
        if path.is_file():
            return path
        return None

    @staticmethod
    def _minimal_listing(directory: Path) -> str:
        """Return a deterministic minimal listing for directories without routing."""
        entries = sorted(child.name for child in directory.iterdir())
        return "\n".join(entries) + ("\n" if entries else "")
