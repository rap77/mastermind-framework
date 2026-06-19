"""Manual domain-knowledge ingestion preview helpers.

Builds an auditable preview of how a distilled FUENTE markdown file would be
chunked for ``domain_knowledge`` ingestion. This first slice is intentionally
manual-first: it prepares deterministic chunks and hashes without writing to
``brain_embeddings`` or embedding anything automatically.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from pathlib import Path
from typing import Any

from mastermind_cli.rag.embed import compute_hash
from mastermind_cli.utils.yaml import read_yaml_frontmatter

_CONOCIMIENTO_HEADING = "## Conocimiento Destilado"
_NOTES_HEADING = "## Notas de Destilación"
_SECTION_PATTERN = re.compile(
    r"^###\s+(?P<title>.+?)\n(?P<body>.*?)(?=^###\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)
_SUBSECTION_PATTERN = re.compile(
    r"^####\s+(?P<title>.+?)\n(?P<body>.*?)(?=^####\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True)
class IngestionChunkPreview:
    """A single auditable chunk candidate for manual ingestion."""

    index: int
    heading_path: str
    chunk_text: str
    chunk_hash: str
    source_ref: str
    char_count: int


@dataclass(frozen=True)
class IngestionPreviewReport:
    """A deterministic report describing manual domain-knowledge ingestion."""

    source_id: str
    brain_id: str
    collection_type: str
    source_path: str
    title: str
    distillation_quality: str | None
    chunk_count: int
    warnings: list[str]
    chunks: list[IngestionChunkPreview]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary representation."""
        return {
            "source_id": self.source_id,
            "brain_id": self.brain_id,
            "collection_type": self.collection_type,
            "source_path": self.source_path,
            "title": self.title,
            "distillation_quality": self.distillation_quality,
            "chunk_count": self.chunk_count,
            "warnings": self.warnings,
            "chunks": [asdict(chunk) for chunk in self.chunks],
        }

    def to_json(self) -> str:
        """Serialize the report to pretty-printed JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def build_domain_knowledge_preview(
    source_file: Path, max_chunk_chars: int = 1200
) -> IngestionPreviewReport:
    """Build an auditable domain-knowledge ingestion preview for one source.

    Args:
        source_file: Path to a distilled FUENTE markdown file.
        max_chunk_chars: Maximum size for each emitted chunk.

    Returns:
        Deterministic preview report with chunk text and hashes.

    Raises:
        ValueError: If the source file lacks required metadata or extractable
            distilled knowledge content.
    """
    if max_chunk_chars <= 0:
        raise ValueError("max_chunk_chars must be greater than 0")

    metadata, content = read_yaml_frontmatter(str(source_file))
    if metadata is None:
        raise ValueError(f"No YAML front matter found in {source_file}")

    source_id = _require_metadata_field(metadata, "source_id", source_file)
    brain_id = _require_metadata_field(metadata, "brain", source_file)
    title = _require_metadata_field(metadata, "title", source_file)

    knowledge_block = _extract_distilled_knowledge_block(content)
    chunks = _build_chunks(
        source_id=source_id,
        knowledge_block=knowledge_block,
        max_chunk_chars=max_chunk_chars,
    )
    if not chunks:
        raise ValueError(
            f"No chunkable distilled knowledge blocks found in {source_file}"
        )

    warnings: list[str] = []
    distillation_quality = metadata.get("distillation_quality")
    if distillation_quality != "complete":
        warnings.append(
            "distillation_quality is not 'complete'; review before DB ingestion"
        )

    return IngestionPreviewReport(
        source_id=source_id,
        brain_id=brain_id,
        collection_type="domain_knowledge",
        source_path=str(source_file),
        title=title,
        distillation_quality=distillation_quality,
        chunk_count=len(chunks),
        warnings=warnings,
        chunks=chunks,
    )


def _require_metadata_field(
    metadata: dict[str, Any], field: str, source_file: Path
) -> str:
    """Return a required metadata field as a non-empty string."""
    value = metadata.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Required metadata field '{field}' is missing in {source_file}"
        )
    return value.strip()


def _extract_distilled_knowledge_block(content: str) -> str:
    """Return the markdown block inside ``## Conocimiento Destilado``."""
    start = content.find(_CONOCIMIENTO_HEADING)
    if start == -1:
        raise ValueError("Required section '## Conocimiento Destilado' is missing")

    trimmed = content[start + len(_CONOCIMIENTO_HEADING) :].strip()
    notes_start = trimmed.find(_NOTES_HEADING)
    if notes_start != -1:
        trimmed = trimmed[:notes_start].strip()

    return trimmed


def _build_chunks(
    source_id: str, knowledge_block: str, max_chunk_chars: int
) -> list[IngestionChunkPreview]:
    """Split a knowledge block into deterministic chunk previews."""
    chunks: list[IngestionChunkPreview] = []
    next_index = 1

    for section_match in _SECTION_PATTERN.finditer(knowledge_block):
        section_title = section_match.group("title").strip()
        section_body = section_match.group("body").strip()
        subsection_chunks = _split_section_body(section_title, section_body)
        for heading_path, chunk_text in subsection_chunks:
            for piece in _split_large_chunk(chunk_text, max_chunk_chars):
                normalized = _normalize_chunk_text(piece)
                if not normalized:
                    continue
                chunks.append(
                    IngestionChunkPreview(
                        index=next_index,
                        heading_path=heading_path,
                        chunk_text=normalized,
                        chunk_hash=compute_hash(
                            f"{source_id}\n{heading_path}\n{normalized}"
                        ),
                        source_ref=source_id,
                        char_count=len(normalized),
                    )
                )
                next_index += 1

    return chunks


def _split_section_body(section_title: str, section_body: str) -> list[tuple[str, str]]:
    """Split a section into chunkable units, preferring H4 subsections."""
    subsection_matches = list(_SUBSECTION_PATTERN.finditer(section_body))
    if not subsection_matches:
        return [(section_title, section_body)]

    chunks: list[tuple[str, str]] = []
    prelude_end = subsection_matches[0].start()
    prelude = section_body[:prelude_end].strip()
    if prelude:
        chunks.append((section_title, prelude))

    for match in subsection_matches:
        subsection_title = match.group("title").strip()
        subsection_body = match.group("body").strip()
        heading_path = f"{section_title} > {subsection_title}"
        chunks.append((heading_path, subsection_body))

    return chunks


def _split_large_chunk(chunk_text: str, max_chunk_chars: int) -> list[str]:
    """Split oversized chunks by paragraph while preserving auditability."""
    normalized = chunk_text.strip()
    if len(normalized) <= max_chunk_chars:
        return [normalized]

    paragraphs = [
        part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()
    ]
    pieces: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chunk_chars:
            current = candidate
            continue

        if current:
            pieces.append(current)
            current = ""

        if len(paragraph) <= max_chunk_chars:
            current = paragraph
            continue

        pieces.extend(_split_long_paragraph(paragraph, max_chunk_chars))

    if current:
        pieces.append(current)

    return pieces or [normalized]


def _split_long_paragraph(paragraph: str, max_chunk_chars: int) -> list[str]:
    """Split a very long paragraph into deterministic sentence-like pieces."""
    pieces: list[str] = []
    remaining = paragraph.strip()
    while len(remaining) > max_chunk_chars:
        split_at = remaining.rfind(". ", 0, max_chunk_chars)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, max_chunk_chars)
        if split_at == -1:
            split_at = max_chunk_chars
        piece = remaining[:split_at].strip()
        if not piece:
            break
        pieces.append(piece)
        remaining = remaining[split_at:].strip()

    if remaining:
        pieces.append(remaining)
    return pieces


def _normalize_chunk_text(text: str) -> str:
    """Normalize whitespace without destroying markdown semantics."""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    normalized_lines: list[str] = []
    blank_pending = False

    for line in lines:
        if not line.strip():
            blank_pending = True
            continue
        if blank_pending and normalized_lines:
            normalized_lines.append("")
        normalized_lines.append(line.strip())
        blank_pending = False

    return "\n".join(normalized_lines).strip()
