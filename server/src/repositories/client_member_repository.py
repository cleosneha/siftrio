from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.client_member import ClientMember
from src.models.workspace_member import MemberRole


class ClientMemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self, client_id: UUID, user_id: UUID, role: MemberRole = MemberRole.MEMBER
    ) -> ClientMember:
        member = ClientMember(client_id=client_id, user_id=user_id, role=role)
        self._db.add(member)
        await self._db.flush()
        await self._db.refresh(member)
        return member

    async def get_by_client(self, client_id: UUID) -> list[ClientMember]:
        result = await self._db.execute(
            select(ClientMember)
            .options(selectinload(ClientMember.user))
            .where(ClientMember.client_id == client_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_client(
        self, client_id: UUID, user_id: UUID
    ) -> ClientMember | None:
        result = await self._db.execute(
            select(ClientMember).where(
                ClientMember.client_id == client_id,
                ClientMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, client_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            delete(ClientMember).where(
                ClientMember.client_id == client_id,
                ClientMember.user_id == user_id,
            )
        )
