from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.base import MemberRole, rank
from src.services.audit_service import AuditService, resolve_workspace_id
from src.services.membership_service import MembershipService


async def _audit_rbac_denial(
    request: Request,
    db: AsyncSession,
    level: str,
    resource_id: UUID,
    required: MemberRole,
    actual: MemberRole | None,
) -> None:
    workspace_id = await resolve_workspace_id(db, level, resource_id)
    if workspace_id is None:
        return
    user = getattr(request.state, "user", None)
    AuditService(db).record(
        workspace_id=workspace_id,
        action="rbac.denied",
        resource_type=level,
        resource_id=resource_id,
        actor_user_id=UUID(user.id) if user else None,
        new_value={
            "required": required.value,
            "actual": actual.value if actual else None,
        },
    )
    await db.commit()


def assert_minimum_role(actual: MemberRole | None, required: MemberRole) -> None:
    if rank(actual) < rank(required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def _noop_plan_guard(workspace_id: UUID, role: MemberRole | None) -> None:
    pass


async def _resolve_effective_role(
    request: Request,
    db: AsyncSession,
    level: str,
    resource_id: UUID,
) -> MemberRole | None:
    user = request.state.user
    cache = request.state.effective_roles
    key = (level, resource_id)
    if key not in cache:
        cache[key] = await MembershipService(db).get_effective_role(
            level, resource_id, UUID(user.id)
        )
    return cache[key]


def require_workspace_role(
    min_role: MemberRole,
    plan_guard: Callable[[UUID, MemberRole | None], None] = _noop_plan_guard,
):
    async def dependency(
        workspace_id: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ) -> None:
        role = await _resolve_effective_role(request, db, "workspace", workspace_id)
        if rank(role) < rank(min_role):
            await _audit_rbac_denial(
                request, db, "workspace", workspace_id, min_role, role
            )
        assert_minimum_role(role, min_role)
        plan_guard(workspace_id, role)

    return dependency


def require_client_role(
    min_role: MemberRole,
    plan_guard: Callable[[UUID, MemberRole | None], None] = _noop_plan_guard,
):
    async def dependency(
        client_id: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ) -> None:
        role = await _resolve_effective_role(request, db, "client", client_id)
        if rank(role) < rank(min_role):
            await _audit_rbac_denial(
                request, db, "client", client_id, min_role, role
            )
        assert_minimum_role(role, min_role)
        plan_guard(client_id, role)

    return dependency


def require_project_role(
    min_role: MemberRole,
    plan_guard: Callable[[UUID, MemberRole | None], None] = _noop_plan_guard,
):
    async def dependency(
        project_id: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ) -> None:
        role = await _resolve_effective_role(request, db, "project", project_id)
        if rank(role) < rank(min_role):
            await _audit_rbac_denial(
                request, db, "project", project_id, min_role, role
            )
        assert_minimum_role(role, min_role)
        plan_guard(project_id, role)

    return dependency
