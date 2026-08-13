from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.base import MemberRole, rank
from src.services.membership_service import MembershipService


def _emit_audit_event(event: str, **context) -> None:
    # TODO(phase3): wire into audit service
    pass


def assert_minimum_role(actual: MemberRole | None, required: MemberRole) -> None:
    if rank(actual) < rank(required):
        _emit_audit_event("rbac.denied", required=required, actual=actual)
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
        assert_minimum_role(role, min_role)
        plan_guard(project_id, role)

    return dependency


def require_api_key_scope(min_scope: str):
    async def dependency() -> None:
        # TODO(phase3): wire MCP API key scope enforcement (RBAC.md §3.1.4)
        raise NotImplementedError("API key scopes are not implemented yet")

    return dependency
