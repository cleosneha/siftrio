from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.schemas.knowledge_schema import (
    ActionItemUpdate,
    DecisionUpdate,
    QuestionUpdate,
    RequirementUpdate,
    RiskUpdate,
)
from src.services.knowledge_service import KnowledgeService
from src.utils.uuid_validator import parse_optional_uuid

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
    dependencies=[Depends(require_authenticated_user)],
)


def _get_knowledge_service(db: AsyncSession) -> KnowledgeService:
    return KnowledgeService(
        db=db,
        repo=KnowledgeRepository(db),
        meeting_repo=MeetingRepository(db),
        chunk_repo=MeetingChunkRepository(db),
    )


def _entity_response(data: dict | None, label: str) -> BaseResponse:
    if data is None:
        return BaseResponse(success=False, message=f"{label} not found", data=None)
    return BaseResponse(data=data)


@router.get("/requirements", response_model=BaseResponse)
async def list_requirements(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.list_requirements(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )
    return BaseResponse(data=data)


@router.get("/requirements/{entity_id}", response_model=BaseResponse)
async def get_requirement(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    return _entity_response(await service.get_requirement(entity_id), "Requirement")


@router.patch("/requirements/{entity_id}", response_model=BaseResponse)
async def update_requirement(
    body: RequirementUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.update_requirement(
        entity_id, body.model_dump(exclude_none=True)
    )
    return BaseResponse(message="Requirement updated", data=data)


@router.get("/action-items", response_model=BaseResponse)
async def list_action_items(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.list_action_items(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )
    return BaseResponse(data=data)


@router.get("/action-items/{entity_id}", response_model=BaseResponse)
async def get_action_item(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    return _entity_response(await service.get_action_item(entity_id), "Action item")


@router.patch("/action-items/{entity_id}", response_model=BaseResponse)
async def update_action_item(
    body: ActionItemUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.update_action_item(
        entity_id, body.model_dump(exclude_none=True)
    )
    return BaseResponse(message="Action item updated", data=data)


@router.get("/decisions", response_model=BaseResponse)
async def list_decisions(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.list_decisions(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )
    return BaseResponse(data=data)


@router.get("/decisions/{entity_id}", response_model=BaseResponse)
async def get_decision(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    return _entity_response(await service.get_decision(entity_id), "Decision")


@router.patch("/decisions/{entity_id}", response_model=BaseResponse)
async def update_decision(
    body: DecisionUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.update_decision(
        entity_id, body.model_dump(exclude_none=True)
    )
    return BaseResponse(message="Decision updated", data=data)


@router.get("/risks", response_model=BaseResponse)
async def list_risks(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.list_risks(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )
    return BaseResponse(data=data)


@router.get("/risks/{entity_id}", response_model=BaseResponse)
async def get_risk(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    return _entity_response(await service.get_risk(entity_id), "Risk")


@router.patch("/risks/{entity_id}", response_model=BaseResponse)
async def update_risk(
    body: RiskUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.update_risk(
        entity_id, body.model_dump(exclude_none=True)
    )
    return BaseResponse(message="Risk updated", data=data)


@router.get("/questions", response_model=BaseResponse)
async def list_questions(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.list_questions(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )
    return BaseResponse(data=data)


@router.get("/questions/{entity_id}", response_model=BaseResponse)
async def get_question(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    return _entity_response(await service.get_question(entity_id), "Question")


@router.patch("/questions/{entity_id}", response_model=BaseResponse)
async def update_question(
    body: QuestionUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = _get_knowledge_service(db)
    data = await service.update_question(
        entity_id, body.model_dump(exclude_none=True)
    )
    return BaseResponse(message="Question updated", data=data)
