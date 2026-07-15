import hashlib
import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.api_key_repository import ApiKeyRepository
from src.schemas.api_key_schema import ApiKeyCreatedResponse, ApiKeyResponse


class ApiKeyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ApiKeyRepository(db)

    async def create(self, user_id: UUID, name: str) -> ApiKeyCreatedResponse:
        raw_secret = f"sk_live_{secrets.token_urlsafe(32)}"
        key_prefix = raw_secret[:12]
        hashed_secret = hashlib.sha256(raw_secret.encode()).hexdigest()

        api_key = await self.repo.create(
            user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            hashed_secret=hashed_secret,
        )
        await self.db.commit()

        return ApiKeyCreatedResponse(
            id=api_key.id,
            name=api_key.name,
            secret=raw_secret,
            key_prefix=api_key.key_prefix,
            created_at=api_key.created_at,
        )

    async def list_by_user(self, user_id: UUID) -> list[dict]:
        keys = await self.repo.list_by_user_id(user_id)
        return [ApiKeyResponse.model_validate(k).model_dump() for k in keys]

    async def revoke(self, api_key_id: UUID, user_id: UUID) -> dict:
        api_key = await self.repo.get_by_id(api_key_id)
        if api_key is None:
            raise BaseAPIException(message="API key not found", status_code=404)
        if api_key.user_id != user_id:
            raise BaseAPIException(message="Access denied", status_code=403)
        if api_key.revoked_at is not None:
            raise BaseAPIException(message="API key is already revoked", status_code=400)

        api_key.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()
        return ApiKeyResponse.model_validate(api_key).model_dump()

    async def delete(self, api_key_id: UUID, user_id: UUID) -> None:
        api_key = await self.repo.get_by_id(api_key_id)
        if api_key is None:
            raise BaseAPIException(message="API key not found", status_code=404)
        if api_key.user_id != user_id:
            raise BaseAPIException(message="Access denied", status_code=403)

        await self.repo.delete(api_key_id)
        await self.db.commit()
