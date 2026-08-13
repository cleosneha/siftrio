from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_event import RbacAuditEvent
from src.repositories.resource_repository import ResourceRepository
from src.utils.request_context import get_request_meta


async def resolve_workspace_id(
    db: AsyncSession, level: str, resource_id: UUID
) -> UUID | None:
    return await ResourceRepository(db).get_workspace_id(level, resource_id)


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def record(
        self,
        *,
        workspace_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        actor_user_id: UUID | None = None,
        actor_api_key_id: UUID | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> None:
        meta = get_request_meta()
        self.db.add(
            RbacAuditEvent(
                workspace_id=workspace_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_user_id=actor_user_id,
                actor_api_key_id=actor_api_key_id,
                old_value=old_value,
                new_value=new_value,
                ip_address=meta.ip_address if meta else None,
                user_agent=meta.user_agent if meta else None,
            )
        )
