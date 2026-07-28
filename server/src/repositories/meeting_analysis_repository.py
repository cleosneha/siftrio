from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting_analysis import MeetingAnalysis


class MeetingAnalysisRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        meeting_id: UUID,
        summary: str | None = None,
        goal: str | None = None,
        outcomes: list | None = None,
        blockers: list | None = None,
        confidence: float | None = None,
        raw_ai_response: dict | None = None,
    ) -> MeetingAnalysis:
        analysis = MeetingAnalysis(
            meeting_id=meeting_id,
            summary=summary,
            goal=goal,
            outcomes=outcomes or [],
            blockers=blockers or [],
            confidence=confidence,
            raw_ai_response=raw_ai_response,
        )
        self._db.add(analysis)
        await self._db.flush()
        await self._db.refresh(analysis)
        return analysis

    async def get_by_meeting(self, meeting_id: UUID) -> MeetingAnalysis | None:
        result = await self._db.execute(
            select(MeetingAnalysis).where(MeetingAnalysis.meeting_id == meeting_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        meeting_id: UUID,
        summary: str | None = None,
        goal: str | None = None,
        outcomes: list | None = None,
        blockers: list | None = None,
        confidence: float | None = None,
        raw_ai_response: dict | None = None,
    ) -> MeetingAnalysis:
        existing = await self.get_by_meeting(meeting_id)
        if existing:
            existing.summary = summary
            existing.goal = goal
            existing.outcomes = outcomes or []
            existing.blockers = blockers or []
            existing.confidence = confidence
            existing.raw_ai_response = raw_ai_response
            await self._db.flush()
            await self._db.refresh(existing)
            return existing
        return await self.create(
            meeting_id=meeting_id,
            summary=summary,
            goal=goal,
            outcomes=outcomes,
            blockers=blockers,
            confidence=confidence,
            raw_ai_response=raw_ai_response,
        )
