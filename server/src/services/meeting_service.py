from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.models.meeting import MeetingType
from src.repositories.client_repository import ClientRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.project_repository import ProjectRepository


class MeetingService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = MeetingRepository(db)
        self.client_repo = ClientRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create(
        self,
        client_id: str,
        project_id: str | None,
        title: str,
        meeting_type: str,
        tags: list[str],
        meeting_date: str | None = None,
    ) -> dict:
        cl_id = UUID(client_id)
        client = await self.client_repo.get_by_id(cl_id)
        if client is None:
            raise BaseAPIException(
                message="Client not found",
                status_code=404,
            )

        if meeting_type == "project":
            if not project_id:
                raise BaseAPIException(
                    message="Project ID is required for project meetings",
                    status_code=400,
                )
            pr_id = UUID(project_id)
            project = await self.project_repo.get_by_id(pr_id)
            if project is None:
                raise BaseAPIException(
                    message="Project not found",
                    status_code=404,
                )

        mt = MeetingType(meeting_type) if meeting_type == "miscellaneous" else MeetingType.PROJECT
        pr_id = UUID(project_id) if project_id else None
        parsed_date = datetime.fromisoformat(meeting_date) if meeting_date else None

        meeting = await self.repo.create(
            client_id=cl_id,
            project_id=pr_id,
            title=title,
            meeting_type=mt,
            tags=tags,
            meeting_date=parsed_date,
        )

        return {
            "id": str(meeting.id),
            "client_id": str(meeting.client_id),
            "project_id": str(meeting.project_id) if meeting.project_id else None,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type.value,
            "tags": meeting.tags,
            "transcript": meeting.transcript,
            "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
            "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
        }

    async def get_by_id(self, meeting_id: UUID) -> dict | None:
        meeting = await self.repo.get_by_id(meeting_id)
        if meeting is None:
            return None
        return {
            "id": str(meeting.id),
            "client_id": str(meeting.client_id),
            "project_id": str(meeting.project_id) if meeting.project_id else None,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type.value,
            "tags": meeting.tags,
            "transcript": meeting.transcript,
            "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
            "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
        }

    async def list_by_client(self, client_id: UUID) -> list[dict]:
        meetings = await self.repo.list_by_client(client_id)
        return [
            {
                "id": str(m.id),
                "client_id": str(m.client_id),
                "project_id": str(m.project_id) if m.project_id else None,
                "title": m.title,
                "meeting_type": m.meeting_type.value,
                "tags": m.tags,
                "transcript": m.transcript,
                "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in meetings
        ]

    async def list_by_project(self, project_id: UUID) -> list[dict]:
        meetings = await self.repo.list_by_project(project_id)
        return [
            {
                "id": str(m.id),
                "client_id": str(m.client_id),
                "project_id": str(m.project_id) if m.project_id else None,
                "title": m.title,
                "meeting_type": m.meeting_type.value,
                "tags": m.tags,
                "transcript": m.transcript,
                "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in meetings
        ]

    async def list_miscellaneous_by_client(self, client_id: UUID) -> list[dict]:
        meetings = await self.repo.list_miscellaneous_by_client(client_id)
        return [
            {
                "id": str(m.id),
                "client_id": str(m.client_id),
                "project_id": str(m.project_id) if m.project_id else None,
                "title": m.title,
                "meeting_type": m.meeting_type.value,
                "tags": m.tags,
                "transcript": m.transcript,
                "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in meetings
        ]

    async def delete(self, meeting_id: UUID) -> None:
        await self.repo.delete(meeting_id)
