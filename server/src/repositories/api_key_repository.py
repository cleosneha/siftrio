from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.api_key import ApiKey


class ApiKeyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        user_id: UUID,
        name: str,
        key_prefix: str,
        hashed_secret: str,
    ) -> ApiKey:
        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            hashed_secret=hashed_secret,
        )
        self._db.add(api_key)
        await self._db.flush()
        await self._db.refresh(api_key)
        return api_key

    async def get_by_id(self, api_key_id: UUID) -> ApiKey | None:
        result = await self._db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id)
        )
        return result.scalar_one_or_none()

    async def get_by_hashed_secret(self, hashed_secret: str) -> ApiKey | None:
        result = await self._db.execute(
            select(ApiKey).where(ApiKey.hashed_secret == hashed_secret)
        )
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: UUID) -> list[ApiKey]:
        result = await self._db.execute(
            select(ApiKey)
            .where(ApiKey.user_id == user_id)
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, api_key_id: UUID) -> bool:
        api_key = await self.get_by_id(api_key_id)
        if api_key is None:
            return False
        await self._db.delete(api_key)
        await self._db.flush()
        return True
