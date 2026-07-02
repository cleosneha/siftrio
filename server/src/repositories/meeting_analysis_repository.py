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
        decisions: list | None = None,
        action_items: list | None = None,
        answered_questions: list | None = None,
        unanswered_questions: list | None = None,
        risks: list | None = None,
        blockers: list | None = None,
        future_meetings: list | None = None,
    ) -> MeetingAnalysis:
        analysis = MeetingAnalysis(
            meeting_id=meeting_id,
            summary=summary,
            goal=goal,
            outcomes=outcomes or [],
            decisions=decisions or [],
            action_items=action_items or [],
            answered_questions=answered_questions or [],
            unanswered_questions=unanswered_questions or [],
            risks=risks or [],
            blockers=blockers or [],
            future_meetings=future_meetings or [],
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
        decisions: list | None = None,
        action_items: list | None = None,
        answered_questions: list | None = None,
        unanswered_questions: list | None = None,
        risks: list | None = None,
        blockers: list | None = None,
        future_meetings: list | None = None,
    ) -> MeetingAnalysis:
        existing = await self.get_by_meeting(meeting_id)
        if existing:
            existing.summary = summary
            existing.goal = goal
            existing.outcomes = outcomes or []
            existing.decisions = decisions or []
            existing.action_items = action_items or []
            existing.answered_questions = answered_questions or []
            existing.unanswered_questions = unanswered_questions or []
            existing.risks = risks or []
            existing.blockers = blockers or []
            existing.future_meetings = future_meetings or []
            existing.generated_at = None
            await self._db.flush()
            await self._db.refresh(existing)
            return existing
        return await self.create(
            meeting_id=meeting_id,
            summary=summary,
            goal=goal,
            outcomes=outcomes,
            decisions=decisions,
            action_items=action_items,
            answered_questions=answered_questions,
            unanswered_questions=unanswered_questions,
            risks=risks,
            blockers=blockers,
            future_meetings=future_meetings,
        )
