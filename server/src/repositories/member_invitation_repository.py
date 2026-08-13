from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import MemberRole
from src.models.member_invitation import (
    InvitationStatus,
    MemberInvitation,
    ResourceType,
)


class MemberInvitationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        email: str,
        user_id: UUID | None,
        resource_type: ResourceType,
        resource_id: UUID,
        invited_by: UUID | None,
        token: str,
        expires_at,
        role: MemberRole = MemberRole.MEMBER,
    ) -> MemberInvitation:
        invitation = MemberInvitation(
            email=email,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            invited_by=invited_by,
            token=token,
            expires_at=expires_at,
            status=InvitationStatus.PENDING,
            role=role,
        )
        self._db.add(invitation)
        await self._db.flush()
        await self._db.refresh(invitation)
        return invitation

    async def get_by_id(self, invitation_id: UUID) -> MemberInvitation | None:
        result = await self._db.execute(
            select(MemberInvitation).where(MemberInvitation.id == invitation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> MemberInvitation | None:
        result = await self._db.execute(
            select(MemberInvitation).where(MemberInvitation.token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_email_and_resource(
        self, email: str, resource_type: ResourceType, resource_id: UUID
    ) -> MemberInvitation | None:
        result = await self._db.execute(
            select(MemberInvitation).where(
                MemberInvitation.email == email,
                MemberInvitation.resource_type == resource_type,
                MemberInvitation.resource_id == resource_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, invitation: MemberInvitation) -> None:
        await self._db.delete(invitation)
        await self._db.flush()

    async def get_by_resource(
        self, resource_type: ResourceType, resource_id: UUID
    ) -> list[MemberInvitation]:
        result = await self._db.execute(
            select(MemberInvitation)
            .where(
                MemberInvitation.resource_type == resource_type,
                MemberInvitation.resource_id == resource_id,
            )
            .order_by(MemberInvitation.created_at.desc())
        )
        return list(result.scalars().all())
