from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.assistant_controller import AssistantController
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.schemas.assistant_schema import AssistantQueryRequest, AssistantQueryResponse

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("/query", response_model=AssistantQueryResponse)
async def query_assistant(
    body: AssistantQueryRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AssistantQueryResponse:
    controller = AssistantController(db, user_context=request.state.user.model_dump())
    return await controller.query(body)


@router.post("/query/stream")
async def query_assistant_stream(
    body: AssistantQueryRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    controller = AssistantController(db, user_context=request.state.user.model_dump())
    return StreamingResponse(
        controller.query_stream(body),
        media_type="text/event-stream",
    )