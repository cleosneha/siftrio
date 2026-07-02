from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.knowledge_controller import KnowledgeController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.knowledge_schema import (
    ActionItemUpdate,
    DecisionUpdate,
    QuestionUpdate,
    RequirementUpdate,
    RiskUpdate,
)
from src.utils.uuid_validator import parse_optional_uuid

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/requirements", response_model=BaseResponse)
async def list_requirements(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.list_requirements(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )


@router.get("/requirements/{entity_id}", response_model=BaseResponse)
async def get_requirement(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.get_requirement(entity_id)


@router.patch("/requirements/{entity_id}", response_model=BaseResponse)
async def update_requirement(
    body: RequirementUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.update_requirement(
        entity_id, body.model_dump(exclude_none=True)
    )


@router.get("/action-items", response_model=BaseResponse)
async def list_action_items(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.list_action_items(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )


@router.get("/action-items/{entity_id}", response_model=BaseResponse)
async def get_action_item(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.get_action_item(entity_id)


@router.patch("/action-items/{entity_id}", response_model=BaseResponse)
async def update_action_item(
    body: ActionItemUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.update_action_item(
        entity_id, body.model_dump(exclude_none=True)
    )


@router.get("/decisions", response_model=BaseResponse)
async def list_decisions(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.list_decisions(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )


@router.get("/decisions/{entity_id}", response_model=BaseResponse)
async def get_decision(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.get_decision(entity_id)


@router.patch("/decisions/{entity_id}", response_model=BaseResponse)
async def update_decision(
    body: DecisionUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.update_decision(
        entity_id, body.model_dump(exclude_none=True)
    )


@router.get("/risks", response_model=BaseResponse)
async def list_risks(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.list_risks(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )


@router.get("/risks/{entity_id}", response_model=BaseResponse)
async def get_risk(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.get_risk(entity_id)


@router.patch("/risks/{entity_id}", response_model=BaseResponse)
async def update_risk(
    body: RiskUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.update_risk(
        entity_id, body.model_dump(exclude_none=True)
    )


@router.get("/questions", response_model=BaseResponse)
async def list_questions(
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.list_questions(
        parse_optional_uuid(project_id, "project_id") if project_id else None,
        parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None,
        status, limit=limit, offset=offset,
    )


@router.get("/questions/{entity_id}", response_model=BaseResponse)
async def get_question(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.get_question(entity_id)


@router.patch("/questions/{entity_id}", response_model=BaseResponse)
async def update_question(
    body: QuestionUpdate,
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = KnowledgeController(db)
    return await controller.update_question(
        entity_id, body.model_dump(exclude_none=True)
    )
