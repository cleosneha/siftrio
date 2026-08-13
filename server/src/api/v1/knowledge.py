from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_project_role
from src.models.base import MemberRole
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.resource_repository import ResourceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.knowledge_schema import (
    ActionItemUpdate,
    DecisionUpdate,
    QuestionUpdate,
    RequirementUpdate,
    RiskUpdate,
)
from src.services.knowledge_service import KnowledgeService
from src.services.membership_service import MembershipService
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


async def _assert_project_access(
    db: AsyncSession,
    request: Request,
    user_id: UUID,
    project_id: UUID,
    min_role: MemberRole,
) -> None:
    await MembershipService(db).assert_workspace_boundary("project", project_id, user_id)
    await require_project_role(min_role)(project_id, request, db)


async def _resolve_entity_project(
    db: AsyncSession, resource_type: str, entity_id: UUID
) -> UUID | None:
    return await ResourceRepository(db).get_project_id(resource_type, entity_id)


async def _resolve_list_scope(
    db: AsyncSession,
    request: Request,
    user_id: UUID,
    project_id: UUID | None,
    meeting_id: UUID | None,
) -> list[UUID] | None:
    """Returns visible_project_ids, or None when the caller has no valid project scope."""
    if project_id is not None:
        await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
        return [project_id]
    if meeting_id is not None:
        meeting = await MeetingRepository(db).get_by_id(meeting_id)
        if meeting is None or meeting.project_id is None:
            return None
        await _assert_project_access(db, request, user_id, meeting.project_id, MemberRole.VIEWER)
        return [meeting.project_id]
    return await MembershipService(db).get_accessible_project_ids(user_id)


@router.get("/requirements", response_model=BaseResponse)
async def list_requirements(
    request: Request,
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None
    mt_id = parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None
    visible = await _resolve_list_scope(db, request, user_id, pr_id, mt_id)
    if visible is None:
        return BaseResponse(data=[])
    service = _get_knowledge_service(db)
    data = await service.list_requirements(
        pr_id, mt_id, status, limit=limit, offset=offset,
        visible_project_ids=visible,
    )
    return BaseResponse(data=data)


@router.get("/requirements/{entity_id}", response_model=BaseResponse)
async def get_requirement(
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "requirement", entity_id)
    if project_id is None:
        return _entity_response(None, "Requirement")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
    data = await _get_knowledge_service(db).get_requirement(entity_id, visible_project_ids=[project_id])
    return _entity_response(data, "Requirement")


@router.patch("/requirements/{entity_id}", response_model=BaseResponse)
async def update_requirement(
    body: RequirementUpdate,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "requirement", entity_id)
    if project_id is None:
        return _entity_response(None, "Requirement")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.MEMBER)
    data = await _get_knowledge_service(db).update_requirement(
        entity_id, body.model_dump(exclude_none=True), visible_project_ids=[project_id]
    )
    return BaseResponse(message="Requirement updated", data=data)


@router.get("/action-items", response_model=BaseResponse)
async def list_action_items(
    request: Request,
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None
    mt_id = parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None
    visible = await _resolve_list_scope(db, request, user_id, pr_id, mt_id)
    if visible is None:
        return BaseResponse(data=[])
    service = _get_knowledge_service(db)
    data = await service.list_action_items(
        pr_id, mt_id, status, limit=limit, offset=offset,
        visible_project_ids=visible,
    )
    return BaseResponse(data=data)


@router.get("/action-items/{entity_id}", response_model=BaseResponse)
async def get_action_item(
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "action_item", entity_id)
    if project_id is None:
        return _entity_response(None, "Action item")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
    data = await _get_knowledge_service(db).get_action_item(entity_id, visible_project_ids=[project_id])
    return _entity_response(data, "Action item")


@router.patch("/action-items/{entity_id}", response_model=BaseResponse)
async def update_action_item(
    body: ActionItemUpdate,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "action_item", entity_id)
    if project_id is None:
        return _entity_response(None, "Action item")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.MEMBER)
    data = await _get_knowledge_service(db).update_action_item(
        entity_id, body.model_dump(exclude_none=True), visible_project_ids=[project_id]
    )
    return BaseResponse(message="Action item updated", data=data)


@router.get("/decisions", response_model=BaseResponse)
async def list_decisions(
    request: Request,
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None
    mt_id = parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None
    visible = await _resolve_list_scope(db, request, user_id, pr_id, mt_id)
    if visible is None:
        return BaseResponse(data=[])
    service = _get_knowledge_service(db)
    data = await service.list_decisions(
        pr_id, mt_id, status, limit=limit, offset=offset,
        visible_project_ids=visible,
    )
    return BaseResponse(data=data)


@router.get("/decisions/{entity_id}", response_model=BaseResponse)
async def get_decision(
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "decision", entity_id)
    if project_id is None:
        return _entity_response(None, "Decision")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
    data = await _get_knowledge_service(db).get_decision(entity_id, visible_project_ids=[project_id])
    return _entity_response(data, "Decision")


@router.patch("/decisions/{entity_id}", response_model=BaseResponse)
async def update_decision(
    body: DecisionUpdate,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "decision", entity_id)
    if project_id is None:
        return _entity_response(None, "Decision")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.MEMBER)
    data = await _get_knowledge_service(db).update_decision(
        entity_id, body.model_dump(exclude_none=True), visible_project_ids=[project_id]
    )
    return BaseResponse(message="Decision updated", data=data)


@router.get("/risks", response_model=BaseResponse)
async def list_risks(
    request: Request,
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None
    mt_id = parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None
    visible = await _resolve_list_scope(db, request, user_id, pr_id, mt_id)
    if visible is None:
        return BaseResponse(data=[])
    service = _get_knowledge_service(db)
    data = await service.list_risks(
        pr_id, mt_id, status, limit=limit, offset=offset,
        visible_project_ids=visible,
    )
    return BaseResponse(data=data)


@router.get("/risks/{entity_id}", response_model=BaseResponse)
async def get_risk(
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "risk", entity_id)
    if project_id is None:
        return _entity_response(None, "Risk")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
    data = await _get_knowledge_service(db).get_risk(entity_id, visible_project_ids=[project_id])
    return _entity_response(data, "Risk")


@router.patch("/risks/{entity_id}", response_model=BaseResponse)
async def update_risk(
    body: RiskUpdate,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "risk", entity_id)
    if project_id is None:
        return _entity_response(None, "Risk")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.MEMBER)
    data = await _get_knowledge_service(db).update_risk(
        entity_id, body.model_dump(exclude_none=True), visible_project_ids=[project_id]
    )
    return BaseResponse(message="Risk updated", data=data)


@router.get("/questions", response_model=BaseResponse)
async def list_questions(
    request: Request,
    project_id: str | None = Query(None),
    meeting_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None
    mt_id = parse_optional_uuid(meeting_id, "meeting_id") if meeting_id else None
    visible = await _resolve_list_scope(db, request, user_id, pr_id, mt_id)
    if visible is None:
        return BaseResponse(data=[])
    service = _get_knowledge_service(db)
    data = await service.list_questions(
        pr_id, mt_id, status, limit=limit, offset=offset,
        visible_project_ids=visible,
    )
    return BaseResponse(data=data)


@router.get("/questions/{entity_id}", response_model=BaseResponse)
async def get_question(
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "question", entity_id)
    if project_id is None:
        return _entity_response(None, "Question")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.VIEWER)
    data = await _get_knowledge_service(db).get_question(entity_id, visible_project_ids=[project_id])
    return _entity_response(data, "Question")


@router.patch("/questions/{entity_id}", response_model=BaseResponse)
async def update_question(
    body: QuestionUpdate,
    entity_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    project_id = await _resolve_entity_project(db, "question", entity_id)
    if project_id is None:
        return _entity_response(None, "Question")
    await _assert_project_access(db, request, user_id, project_id, MemberRole.MEMBER)
    data = await _get_knowledge_service(db).update_question(
        entity_id, body.model_dump(exclude_none=True), visible_project_ids=[project_id]
    )
    return BaseResponse(message="Question updated", data=data)
