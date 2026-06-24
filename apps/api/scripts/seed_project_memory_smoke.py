#!/usr/bin/env python3
"""Seed a minimal project memory item for Docker/Postgres smoke testing."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import NotRequired, TypedDict

from mastermind_cli.memory_layer.runtime import build_memory_store_from_env
from mastermind_cli.memory_layer.service import MemoryService


logger = logging.getLogger(__name__)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


class SmokeSeedItem(TypedDict):
    """Typed payload accepted by MemoryService.record_learning()."""

    title: str
    content: str
    project_id: str
    memory_type: str
    visibility: str
    source_kind: str
    source_ref: str
    tags: list[str]
    related_memory_ids: NotRequired[list[str]]


def build_smoke_seed_items(project_id: str) -> list[SmokeSeedItem]:
    """Return a small canonical corpus for semantic-memory smoke testing."""
    return [
        {
            "title": "Prueba inicial de memoria semantica",
            "content": (
                "Estamos usando Postgres en Docker con pgvector habilitado. "
                "Esta memoria valida el flujo canonico a embeddings y query semantico."
            ),
            "project_id": project_id,
            "memory_type": "note",
            "visibility": "project",
            "source_kind": "manual",
            "source_ref": "docker-smoke-test",
            "tags": ["smoke-test", "pgvector"],
        },
        {
            "title": "Embeddings locales con Ollama",
            "content": (
                "El proyecto usa embeddings locales con Ollama y el modelo "
                "mxbai-embed-large para evitar dependencia de proveedores remotos."
            ),
            "project_id": project_id,
            "memory_type": "decision",
            "visibility": "project",
            "source_kind": "manual",
            "source_ref": "docker-smoke-test",
            "tags": ["smoke-test", "ollama", "embeddings"],
        },
        {
            "title": "Backfill requerido tras cambiar de modelo",
            "content": (
                "Si cambia la dimension del modelo de embeddings, puede ser "
                "necesario truncar mm_memory_embeddings y ejecutar backfill otra vez."
            ),
            "project_id": project_id,
            "memory_type": "lesson",
            "visibility": "project",
            "source_kind": "manual",
            "source_ref": "docker-smoke-test",
            "tags": ["smoke-test", "backfill", "pgvector"],
        },
    ]


async def main() -> None:
    """Insert a small canonical memory corpus for the configured project."""
    database_url = os.environ["MM_MEMORY_DATABASE_URL"]
    project_id = os.environ["MM_MEMORY_PROJECT_ID"]

    store = build_memory_store_from_env(
        database_url,
        enable_vector=False,
        enable_index=True,
    )
    service = MemoryService(store)

    seeded_items = []
    seeded_memory_ids: list[str] = []
    for item in build_smoke_seed_items(project_id):
        related_memory_ids = list(seeded_memory_ids) if seeded_memory_ids else None
        if related_memory_ids is None:
            seeded = await service.record_learning(
                title=item["title"],
                content=item["content"],
                project_id=item["project_id"],
                memory_type=item["memory_type"],
                visibility=item["visibility"],
                source_kind=item["source_kind"],
                source_ref=item["source_ref"],
                tags=item["tags"],
            )
        else:
            seeded = await service.record_learning(
                title=item["title"],
                content=item["content"],
                project_id=item["project_id"],
                memory_type=item["memory_type"],
                visibility=item["visibility"],
                source_kind=item["source_kind"],
                source_ref=item["source_ref"],
                tags=item["tags"],
                related_memory_ids=related_memory_ids,
            )
        seeded_items.append({"memory_id": seeded.memory_id, "title": seeded.title})
        if seeded.memory_id:
            seeded_memory_ids.append(seeded.memory_id)

    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = sys.stdout
    logger.info(
        json.dumps(
            {
                "project_id": project_id,
                "seeded": seeded_items,
                "count": len(seeded_items),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
