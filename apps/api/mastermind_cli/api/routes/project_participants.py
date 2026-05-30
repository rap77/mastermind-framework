"""REST endpoints for project participants (collaboration-rbac slice)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from mastermind_cli.api.dependencies import get_project_state_db_url
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.project_state.database.session import get_session_factory
from mastermind_cli.project_state.repositories.participants import (
    ParticipantsRepository,
)
from mastermind_cli.project_state.schemas.participants import (
    AddParticipantRequest,
    ParticipantListResponse,
    ParticipantResponse,
)

router = APIRouter()


@router.post(
    "/{project_id}/participants",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_participant(
    project_id: str,
    body: AddParticipantRequest,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ParticipantResponse:
    """Add a participant to a project with an explicit role."""
    del user_id  # Reserved for future permission checks.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        repo = ParticipantsRepository(session)
        participant = repo.add(
            project_id=project_id,
            participant_id=body.participant_id,
            participant_type=body.participant_type,
            role=body.role.value,
        )
        session.commit()
        return ParticipantResponse.model_validate(participant)


@router.get(
    "/{project_id}/participants",
    response_model=ParticipantListResponse,
)
async def list_participants(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ParticipantListResponse:
    """Return all participants for a project."""
    del user_id  # Reserved for future permission checks.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        repo = ParticipantsRepository(session)
        items = repo.list_by_project(project_id)
        total = repo.count_by_project(project_id)
        return ParticipantListResponse(
            items=[ParticipantResponse.model_validate(p) for p in items],
            total=total,
        )


@router.delete(
    "/{project_id}/participants/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_participant(
    project_id: str,
    participant_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> Response:
    """Remove a participant from a project."""
    del user_id  # Reserved for future permission checks.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        repo = ParticipantsRepository(session)
        deleted = repo.remove(project_id, participant_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found",
            )
        session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
