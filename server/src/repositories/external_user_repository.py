from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.external_user import ExternalUser


class ExternalUserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_external_id(
        self, external_id: str, provider: str, workspace_id: UUID,
    ) -> ExternalUser | None:
        result = await self._db.execute(
            select(ExternalUser).where(
                ExternalUser.external_id == external_id,
                ExternalUser.provider == provider,
                ExternalUser.workspace_id == workspace_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        external_id: str,
        provider: str,
        workspace_id: UUID,
        display_name: str | None = None,
        email_address: str | None = None,
    ) -> ExternalUser:
        existing = await self.get_by_external_id(external_id, provider, workspace_id)
        if existing:
            if display_name is not None:
                existing.display_name = display_name
            if email_address is not None:
                existing.email_address = email_address
            await self._db.flush()
            await self._db.refresh(existing)
            return existing

        user = ExternalUser(
            external_id=external_id,
            provider=provider,
            workspace_id=workspace_id,
            display_name=display_name,
            email_address=email_address,
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def delete(self, user: ExternalUser) -> None:
        await self._db.delete(user)
        await self._db.flush()
