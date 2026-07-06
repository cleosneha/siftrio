from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.project_chat.schemas import EntityCandidate, ParsedQuery, ResolvedEntities
from src.models.client import Client
from src.models.meeting import Meeting
from src.models.project import Project
from src.models.workspace import Workspace


def _escape_like(pattern: str) -> str:
    escaped = pattern.replace("/", "//").replace("%", "/%").replace("_", "/_")
    return f"%{escaped}%"


class EntityResolverService:
    async def resolve(
        self,
        db: AsyncSession,
        parsed_query: ParsedQuery,
        accessible_workspace_ids: list[str],
    ) -> ResolvedEntities:
        result = ResolvedEntities()

        if not accessible_workspace_ids:
            return result

        if parsed_query.workspace_name:
            matches = await self._resolve_workspace(
                db, parsed_query.workspace_name, accessible_workspace_ids
            )
            if len(matches) == 1:
                result.workspace_id = matches[0].id
            elif len(matches) > 1:
                result.workspace_candidates = [
                    EntityCandidate(id=m.id, name=m.name) for m in matches
                ]

        if parsed_query.client_name:
            matches = await self._resolve_client(
                db, parsed_query.client_name, accessible_workspace_ids
            )
            if len(matches) == 1:
                result.client_id = matches[0].id
            elif len(matches) > 1:
                result.client_candidates = [
                    EntityCandidate(id=c.id, name=c.name) for c in matches
                ]
            elif not matches and parsed_query.workspace_name:
                matches = await self._resolve_workspace(
                    db, parsed_query.client_name, accessible_workspace_ids
                )
                if len(matches) == 1:
                    result.workspace_id = matches[0].id
                elif len(matches) > 1:
                    result.workspace_candidates = [
                        EntityCandidate(id=m.id, name=m.name) for m in matches
                    ]

        if parsed_query.project_name:
            matches = await self._resolve_project(
                db, parsed_query.project_name, accessible_workspace_ids
            )
            if len(matches) == 1:
                result.project_id = matches[0].id
            elif len(matches) > 1:
                result.project_candidates = [
                    EntityCandidate(id=p.id, name=p.name) for p in matches
                ]
            elif not matches:
                matches = await self._resolve_client(
                    db, parsed_query.project_name, accessible_workspace_ids
                )
                if len(matches) == 1:
                    result.client_id = matches[0].id
                elif len(matches) > 1:
                    result.client_candidates = [
                        EntityCandidate(id=c.id, name=c.name) for c in matches
                    ]

        if parsed_query.meeting_name:
            matches = await self._resolve_meeting(
                db, parsed_query.meeting_name, accessible_workspace_ids
            )
            if len(matches) == 1:
                result.meeting_id = matches[0].id
            elif len(matches) > 1:
                result.meeting_candidates = [
                    EntityCandidate(id=m.id, name=m.title) for m in matches
                ]
            elif not matches:
                matches = await self._resolve_project(
                    db, parsed_query.meeting_name, accessible_workspace_ids
                )
                if len(matches) == 1:
                    result.project_id = matches[0].id
                elif len(matches) > 1:
                    result.project_candidates = [
                        EntityCandidate(id=p.id, name=p.name) for p in matches
                    ]

        for name in parsed_query.ambiguous_names:
            client_matches = await self._resolve_client(db, name, accessible_workspace_ids)
            project_matches = await self._resolve_project(db, name, accessible_workspace_ids)
            meeting_matches = await self._resolve_meeting(db, name, accessible_workspace_ids)

            if len(client_matches) == 1 and len(project_matches) == 0 and len(meeting_matches) == 0:
                result.client_id = client_matches[0].id
            elif len(client_matches) == 0 and len(project_matches) == 1 and len(meeting_matches) == 0:
                result.project_id = project_matches[0].id
            elif len(client_matches) == 0 and len(project_matches) == 0 and len(meeting_matches) == 1:
                result.meeting_id = meeting_matches[0].id
            else:
                if client_matches:
                    result.client_candidates.extend(
                        EntityCandidate(id=c.id, name=c.name) for c in client_matches
                    )
                if project_matches:
                    result.project_candidates.extend(
                        EntityCandidate(id=p.id, name=p.name) for p in project_matches
                    )
                if meeting_matches:
                    result.meeting_candidates.extend(
                        EntityCandidate(id=m.id, name=m.title) for m in meeting_matches
                    )

        return result

    async def _resolve_workspace(
        self,
        db: AsyncSession,
        name: str,
        accessible_workspace_ids: list[str],
    ) -> list[Workspace]:
        stmt = (
            select(Workspace)
            .where(Workspace.id.in_([UUID(wid) for wid in accessible_workspace_ids]))
            .where(Workspace.name.ilike(_escape_like(name), escape="/"))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def _resolve_client(
        self,
        db: AsyncSession,
        name: str,
        accessible_workspace_ids: list[str],
    ) -> list[Client]:
        stmt = (
            select(Client)
            .where(Client.workspace_id.in_([UUID(wid) for wid in accessible_workspace_ids]))
            .where(Client.name.ilike(_escape_like(name), escape="/"))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def _resolve_project(
        self,
        db: AsyncSession,
        name: str,
        accessible_workspace_ids: list[str],
    ) -> list[Project]:
        stmt = (
            select(Project)
            .join(Client)
            .where(Client.workspace_id.in_([UUID(wid) for wid in accessible_workspace_ids]))
            .where(Project.name.ilike(_escape_like(name), escape="/"))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def _resolve_meeting(
        self,
        db: AsyncSession,
        name: str,
        accessible_workspace_ids: list[str],
    ) -> list[Meeting]:
        stmt = (
            select(Meeting)
            .join(Client)
            .where(Client.workspace_id.in_([UUID(wid) for wid in accessible_workspace_ids]))
            .where(Meeting.title.ilike(_escape_like(name), escape="/"))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
