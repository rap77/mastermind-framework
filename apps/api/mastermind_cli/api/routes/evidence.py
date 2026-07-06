"""Evidence registry API endpoints for canonical workflow automation."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.mm_flow.evidence_registry_service import EvidenceRegistryService

router = APIRouter()

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    """Resolve the repository root via git, with a filesystem fallback."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, TimeoutError, ValueError) as exc:
        logger.debug(
            "git root resolution failed, using fallback path: %s", exc, exc_info=True
        )
    return Path(__file__).resolve().parents[5]


def get_evidence_registry_service() -> EvidenceRegistryService:
    """Build the service backed by the active planning registry file."""
    registry_path = (
        _project_root() / ".planning" / "evidence" / "evidence-registry.json"
    )
    return EvidenceRegistryService(registry_path)


@router.get("/versions")
async def list_versions(
    user_id: str = Depends(get_current_user_any),
    service: EvidenceRegistryService = Depends(get_evidence_registry_service),
) -> dict[str, object]:
    """Return registered evidence versions."""
    del user_id
    return service.list_versions()


@router.get("/deltas")
async def list_deltas(
    source_id: str | None = None,
    delta_type: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_any),
    service: EvidenceRegistryService = Depends(get_evidence_registry_service),
) -> dict[str, object]:
    """Return evidence deltas with optional filters."""
    del user_id
    return service.list_deltas(
        source_id=source_id,
        delta_type=delta_type,
        decision=decision,
    )


@router.get("/versions/{version_id}/readiness")
async def get_readiness(
    version_id: str,
    user_id: str = Depends(get_current_user_any),
    service: EvidenceRegistryService = Depends(get_evidence_registry_service),
) -> dict[str, object]:
    """Return deterministic readiness for one evidence version."""
    del user_id
    try:
        return service.readiness(version_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
