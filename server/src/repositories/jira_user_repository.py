from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.jira_user import JiraUser


class JiraUserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_account_id(self, account_id: str) -> JiraUser | None:
        result = await self._db.execute(
            select(JiraUser).where(JiraUser.account_id == account_id),
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        account_id: str,
        workspace_id: UUID,
        display_name: str | None = None,
        email_address: str | None = None,
    ) -> JiraUser:
        existing = await self.get_by_account_id(account_id)
        if existing:
            existing.display_name = display_name or existing.display_name
            existing.email_address = email_address or existing.email_address
            existing.last_refreshed_at = datetime.now(timezone.utc)
            return existing

        user = JiraUser(
            account_id=account_id,
            display_name=display_name,
            email_address=email_address,
            workspace_id=workspace_id,
            last_refreshed_at=datetime.now(timezone.utc),
        )
        self._db.add(user)
        await self._db.flush()
        return user

    async def delete(self, user: JiraUser) -> None:
        await self._db.delete(user)
        await self._db.flush()
