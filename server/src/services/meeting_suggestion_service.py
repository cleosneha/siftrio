from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.models.meeting_suggestion import SuggestionStatus
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.meeting_suggestion_repository import MeetingSuggestionRepository
from src.schemas.meeting_suggestion_schema import MeetingSuggestionResponse


class MeetingSuggestionService:
    def __init__(
        self,
        db: AsyncSession,
        repo: MeetingSuggestionRepository,
    ) -> None:
        self.db = db
        self.repo = repo

    async def list_suggestions(self, meeting_id: UUID) -> list[dict]:
        suggestions = await self.repo.get_by_meeting(meeting_id)
        return [MeetingSuggestionResponse.model_validate(s).model_dump() for s in suggestions]

    async def schedule(
        self,
        suggestion_id: UUID,
        title: str | None = None,
        description: str | None = None,
        meeting_date: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict:
        suggestion = await self.repo.get_by_id(suggestion_id)
        if suggestion is None:
            raise BaseAPIException(message="Suggestion not found", status_code=404)
        if suggestion.status != SuggestionStatus.PENDING:
            raise BaseAPIException(
                message=f"Suggestion is already {suggestion.status.value}",
                status_code=400,
            )

        suggestion.status = SuggestionStatus.SCHEDULED
        if title is not None:
            suggestion.title = title
        if description is not None:
            suggestion.description = description
        if meeting_date is not None:
            try:
                suggestion.suggested_date = date.fromisoformat(meeting_date)
            except (ValueError, TypeError):
                pass
        if start_time is not None:
            try:
                parts = start_time.split(":")
                suggestion.start_time = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
            except (ValueError, IndexError, TypeError):
                pass
        if end_time is not None:
            try:
                parts = end_time.split(":")
                suggestion.end_time = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
            except (ValueError, IndexError, TypeError):
                pass

        await self.db.flush()
        await self.db.refresh(suggestion)
        return MeetingSuggestionResponse.model_validate(suggestion).model_dump()

    async def dismiss(self, suggestion_id: UUID) -> dict:
        suggestion = await self.repo.get_by_id(suggestion_id)
        if suggestion is None:
            raise BaseAPIException(message="Suggestion not found", status_code=404)
        if suggestion.status != SuggestionStatus.PENDING:
            raise BaseAPIException(
                message=f"Suggestion is already {suggestion.status.value}",
                status_code=400,
            )

        suggestion.status = SuggestionStatus.DISMISSED
        await self.db.flush()
        await self.db.refresh(suggestion)
        return MeetingSuggestionResponse.model_validate(suggestion).model_dump()
