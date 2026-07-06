from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.project_chat.schemas import (
    EntityCandidate,
    ParsedQuery,
    ResolvedEntities,
    RetrievalScope,
)
from src.exceptions.base import AuthorizationError
from src.models.workspace import Workspace


class ScopeService:
    async def get_user_workspace_ids(
        self,
        db: AsyncSession,
        user_id: str | UUID | None,
    ) -> list[str]:
        if user_id is None:
            return []

        if isinstance(user_id, str):
            user_id = UUID(user_id)

        result = await db.execute(
            select(Workspace.id).where(Workspace.created_by == user_id)
        )
        return [str(ws_id) for ws_id in result.scalars().all()]

    def build_scope(
        self,
        parsed_query: ParsedQuery,
        resolved: ResolvedEntities,
        user_workspace_ids: list[str],
    ) -> RetrievalScope:
        if not user_workspace_ids:
            raise AuthorizationError("You don't have access to any workspaces")

        if resolved.workspace_id and str(resolved.workspace_id) in user_workspace_ids:
            workspace_ids = [str(resolved.workspace_id)]
        elif resolved.workspace_candidates:
            valid = [
                c for c in resolved.workspace_candidates
                if str(c.id) in user_workspace_ids
            ]
            if valid:
                workspace_ids = [str(c.id) for c in valid]
                resolved.workspace_candidates = valid
            else:
                workspace_ids = user_workspace_ids
        else:
            workspace_ids = user_workspace_ids

        ambiguous: dict[str, list[EntityCandidate]] = {}
        if resolved.workspace_candidates:
            ambiguous["workspace"] = resolved.workspace_candidates
        if resolved.client_candidates:
            ambiguous["client"] = resolved.client_candidates
        if resolved.project_candidates:
            ambiguous["project"] = resolved.project_candidates
        if resolved.meeting_candidates:
            ambiguous["meeting"] = resolved.meeting_candidates

        client_ids: list[str] = []
        if resolved.client_id and not resolved.client_candidates:
            client_ids = [str(resolved.client_id)]

        project_ids: list[str] = []
        if resolved.project_id and not resolved.project_candidates:
            project_ids = [str(resolved.project_id)]

        meeting_ids: list[str] = []
        if resolved.meeting_id and not resolved.meeting_candidates:
            meeting_ids = [str(resolved.meeting_id)]

        return RetrievalScope(
            query_text=parsed_query.original_question,
            workspace_ids=workspace_ids,
            client_ids=client_ids,
            project_ids=project_ids,
            meeting_ids=meeting_ids,
            keywords=parsed_query.keywords,
            date_range=parsed_query.date_range,
            ambiguous_entities=ambiguous,
        )
