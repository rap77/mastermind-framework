#!/usr/bin/env python3
"""Seed a minimal project memory item for Docker/Postgres smoke testing."""

from __future__ import annotations

import asyncio
import json
import os
from typing import TypedDict

from mastermind_cli.memory_layer.runtime import build_memory_store_from_env
from mastermind_cli.memory_layer.service import MemoryService


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
    for item in build_smoke_seed_items(project_id):
        seeded = await service.record_learning(**item)
        seeded_items.append({"memory_id": seeded.memory_id, "title": seeded.title})

    print(
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
