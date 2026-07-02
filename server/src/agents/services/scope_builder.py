from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import ParsedQuery, RetrievalScope
from src.agents.services.entity_resolver import EntityResolverService
from src.agents.services.scope_service import ScopeService


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
        return self._scope_service.build_scope(
            parsed_query, resolved, user_workspace_ids,
        )
