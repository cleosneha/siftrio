from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.middleware.rbac import assert_minimum_role
from src.models.base import MemberRole, rank
from src.services.membership_service import MembershipService


PERMISSION_MIN_ROLES: dict[str, MemberRole] = {
    "workspace.read": MemberRole.VIEWER,
    "project.read": MemberRole.VIEWER,
    "meeting.read": MemberRole.VIEWER,
    "knowledge.read": MemberRole.VIEWER,
    "action_item.read": MemberRole.VIEWER,
    "action_item.update": MemberRole.MEMBER,
    "jira.status.read": MemberRole.MEMBER,
    "jira.project.list": MemberRole.MEMBER,
    "jira.mapping.read": MemberRole.MEMBER,
    "jira.issue.read": MemberRole.MEMBER,
}


async def require_permission(
    user_id: UUID,
    permission: str,
    level: str,
    resource_id: UUID,
    db: AsyncSession,
) -> None:
    min_role = PERMISSION_MIN_ROLES.get(permission)
    if min_role is None:
        raise HTTPException(
            status_code=500, detail=f"Unknown permission: {permission}"
        )
    role = await MembershipService(db).get_effective_role(
        level, resource_id, user_id
    )
    assert_minimum_role(role, min_role)


async def user_has_permission_in_workspaces(
    user_id: UUID,
    permission: str,
    workspace_ids: list[UUID],
    db: AsyncSession,
) -> bool:
    """Unfiltered list tools: user must hold the permission in at least one workspace."""
    min_role = PERMISSION_MIN_ROLES.get(permission)
    if min_role is None:
        return False
    membership = MembershipService(db)
    for ws_id in workspace_ids:
        role = await membership.get_effective_role("workspace", ws_id, user_id)
        if rank(role) >= rank(min_role):
            return True
    return False
