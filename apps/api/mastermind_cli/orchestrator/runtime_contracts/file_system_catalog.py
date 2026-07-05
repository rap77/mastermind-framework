"""Filesystem-backed Agent Harness library catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from .models import HarnessPackage, HarnessPackageType, SkillPackage


class FileSystemHarnessCatalog:
    """Load harness and skill packages from a filesystem harness library."""

    def __init__(self, root: Path | str) -> None:
        """Initialize the catalog with a harness library root directory."""
        self.root = Path(root)

    def list_harnesses(self) -> tuple[HarnessPackage, ...]:
        """Return harness packages declared in `registry.yaml`."""
        registry = self._load_registry()
        entries = registry.get("harnesses", [])
        if not isinstance(entries, list):
            raise ValueError("registry.yaml harnesses must be a list")
        return tuple(self._load_harness(entry) for entry in entries)

    def list_skills(self) -> tuple[SkillPackage, ...]:
        """Return shared skill packages declared in `registry.yaml`."""
        registry = self._load_registry()
        entries = registry.get("skills", [])
        if not isinstance(entries, list):
            raise ValueError("registry.yaml skills must be a list")
        return tuple(self._load_skill(entry) for entry in entries)

    def _load_registry(self) -> dict[str, Any]:
        """Load the catalog registry file."""
        registry_path = self.root / "registry.yaml"
        if not registry_path.is_file():
            raise ValueError(f"Missing registry.yaml at {registry_path}")
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        if raw is None:
            return {}
        if not isinstance(raw, dict):
            raise ValueError("registry.yaml must contain a mapping")
        return raw

    def _load_harness(self, entry: object) -> HarnessPackage:
        """Load one harness package from a registry entry."""
        data = self._require_mapping(entry, "harness")
        package_id = self._require_str(data, "id")
        rel_path = self._require_str(data, "path")
        package_dir = self.root / rel_path
        metadata = self._read_frontmatter(package_dir / "HARNESS.md")
        skills = self._str_tuple(data.get("skills", ()))
        if skills:
            self._require_leaf_detector(package_dir)
        return HarnessPackage(
            package_id=package_id,
            name=str(metadata.get("name") or package_id),
            package_type=cast(HarnessPackageType, self._require_str(data, "type")),
            path=rel_path,
            description=str(metadata.get("description") or ""),
            domains=self._str_tuple(data.get("domains", ())),
            phases=self._str_tuple(data.get("phases", ())),
            outputs=self._str_tuple(data.get("outputs", ())),
            supported_loops=self._str_tuple(data.get("supported_loops", ())),
            skills=skills,
            references=self._str_tuple(data.get("references", ())),
            constraints=self._str_tuple(data.get("constraints", ())),
        )

    def _load_skill(self, entry: object) -> SkillPackage:
        """Load one shared skill package from a registry entry."""
        data = self._require_mapping(entry, "skill")
        skill_id = self._require_str(data, "id")
        rel_path = self._require_str(data, "path")
        metadata = self._read_frontmatter(self.root / rel_path / "SKILL.md")
        return SkillPackage(
            skill_id=skill_id,
            name=str(metadata.get("name") or skill_id),
            path=rel_path,
            description=str(metadata.get("description") or ""),
            domains=self._str_tuple(data.get("domains", ())),
            phases=self._str_tuple(data.get("phases", ())),
            supported_harnesses=self._str_tuple(data.get("supported_harnesses", ())),
            requires_mcp=bool(data.get("requires_mcp", False)),
            requires_write=bool(data.get("requires_write", False)),
        )

    def _read_frontmatter(self, path: Path) -> dict[str, Any]:
        """Read YAML frontmatter from a required markdown file."""
        if not path.is_file():
            raise ValueError(f"Missing {path.name} at {path}")
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            raise ValueError(f"Missing YAML frontmatter in {path}")
        try:
            _, raw_metadata, _ = content.split("---\n", 2)
        except ValueError as exc:
            raise ValueError(f"Invalid YAML frontmatter in {path}") from exc
        metadata = yaml.safe_load(raw_metadata)
        if not isinstance(metadata, dict):
            raise ValueError(f"YAML frontmatter in {path} must be a mapping")
        return metadata

    def _require_leaf_detector(self, package_dir: Path) -> None:
        """Require `.leaf-detectors` with the standard skill detector."""
        leaf_path = package_dir / ".leaf-detectors"
        if not leaf_path.is_file():
            raise ValueError(f"Missing .leaf-detectors at {leaf_path}")
        content = leaf_path.read_text(encoding="utf-8")
        if "skill=SKILL.md" not in content.splitlines():
            raise ValueError(f"Missing skill=SKILL.md in {leaf_path}")

    @staticmethod
    def _require_mapping(value: object, label: str) -> dict[str, Any]:
        """Return a registry entry mapping or fail loudly."""
        if not isinstance(value, dict):
            raise ValueError(f"{label} registry entry must be a mapping")
        return value

    @staticmethod
    def _require_str(data: dict[str, Any], key: str) -> str:
        """Return a required string field from a registry entry."""
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"registry entry missing required string field: {key}")
        return value

    @staticmethod
    def _str_tuple(value: object) -> tuple[str, ...]:
        """Normalize a registry scalar/list into a tuple of strings."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError("registry list values must be strings")
            return tuple(value)
        if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
            return value
        raise ValueError("registry value must be a string or list of strings")
