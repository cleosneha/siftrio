from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.project_chat.schemas import ParsedQuery, RetrievalScope
from src.agents.project_chat.services.entity_resolver import EntityResolverService
from src.agents.project_chat.services.scope_service import ScopeService
from src.services.membership_service import MembershipService


class ScopeBuilderService:
    def __init__(self) -> None:
        self._resolver = EntityResolverService()
        self._scope_service = ScopeService()

    async def build(
        self,
        db: AsyncSession,
        question: str,
        parsed_query: ParsedQuery,
        user_context: dict,
    ) -> RetrievalScope:
        user_id = user_context.get("id")
        user_workspace_ids = await self._scope_service.get_user_workspace_ids(db, user_id)

        resolved = await self._resolver.resolve(db, parsed_query, user_workspace_ids)
        scope = self._scope_service.build_scope(
            parsed_query, resolved, user_workspace_ids,
        )
        await self._apply_visible_boundary(db, user_id, scope)
        return scope

    async def _apply_visible_boundary(
        self,
        db: AsyncSession,
        user_id: str | UUID | None,
        scope: RetrievalScope,
    ) -> None:
        if user_id is None or not scope.workspace_ids:
            return
        membership = MembershipService(db)
        uid = UUID(user_id) if isinstance(user_id, str) else user_id
        visible_projects: set[str] = set()
        visible_clients: set[str] = set()
        for ws_id in scope.workspace_ids:
            for pid in await membership.get_visible_project_ids(uid, UUID(ws_id)):
                visible_projects.add(str(pid))
            for cid in await membership.get_visible_client_ids(uid, UUID(ws_id)):
                visible_clients.add(str(cid))
        scope.visible_project_ids = sorted(visible_projects)
        scope.visible_client_ids = sorted(visible_clients)
