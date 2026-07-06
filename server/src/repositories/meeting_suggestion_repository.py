from datetime import date, time
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting_suggestion import MeetingSuggestion, SuggestionStatus


class MeetingSuggestionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        meeting_id: UUID,
        client_id: UUID,
        project_id: UUID | None,
        title: str,
        description: str | None,
        suggested_date: date | None,
        start_time: time | None,
        end_time: time | None,
        confidence: float,
        reason: str,
    ) -> MeetingSuggestion:
        suggestion = MeetingSuggestion(
            meeting_id=meeting_id,
            client_id=client_id,
            project_id=project_id,
            title=title,
            description=description,
            suggested_date=suggested_date,
            start_time=start_time,
            end_time=end_time,
            confidence=confidence,
            reason=reason,
        )
        self._db.add(suggestion)
        await self._db.flush()
        await self._db.refresh(suggestion)
        return suggestion

    async def get_by_meeting(self, meeting_id: UUID) -> list[MeetingSuggestion]:
        result = await self._db.execute(
            select(MeetingSuggestion)
            .where(MeetingSuggestion.meeting_id == meeting_id)
            .order_by(MeetingSuggestion.confidence.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, suggestion_id: UUID) -> MeetingSuggestion | None:
        result = await self._db.execute(
            select(MeetingSuggestion).where(MeetingSuggestion.id == suggestion_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        suggestion_id: UUID,
        status: SuggestionStatus,
    ) -> MeetingSuggestion | None:
        suggestion = await self.get_by_id(suggestion_id)
        if suggestion is None:
            return None
        suggestion.status = status
        await self._db.flush()
        await self._db.refresh(suggestion)
        return suggestion
