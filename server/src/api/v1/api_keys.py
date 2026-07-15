import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.schemas.api_key_schema import ApiKeyCreate, ApiKeyResponse
from src.schemas.base_response import BaseResponse
from src.services.api_key_service import ApiKeyService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api-keys",
    tags=["api-keys"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_api_key(
    body: ApiKeyCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = ApiKeyService(db)
    result = await service.create(user_id, body.name)
    return BaseResponse(
        message="API key created successfully. Copy the secret now — it will not be shown again.",
        data=result.model_dump(),
    )


@router.get("", response_model=BaseResponse)
async def list_api_keys(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = ApiKeyService(db)
    keys = await service.list_by_user(user_id)
    return BaseResponse(data=keys)


@router.post("/{api_key_id}/revoke", response_model=BaseResponse)
async def revoke_api_key(
    api_key_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = ApiKeyService(db)
    result = await service.revoke(api_key_id, user_id)
    return BaseResponse(message="API key revoked successfully", data=result)


@router.delete("/{api_key_id}", response_model=BaseResponse)
async def delete_api_key(
    api_key_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = ApiKeyService(db)
    await service.delete(api_key_id, user_id)
    return BaseResponse(message="API key deleted successfully")
