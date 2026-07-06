from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.agents.project_chat.schemas import RetrievedMeeting
from src.models.meeting import Meeting


class MeetingRetriever:
    async def get_by_ids(
        self,
        db: AsyncSession,
        meeting_ids: list[str],
        date_range: dict | None = None,
    ) -> list[RetrievedMeeting]:
        if not meeting_ids:
            return []

        uuids = list({UUID(mid) for mid in meeting_ids})

        stmt = (
            select(Meeting)
            .options(joinedload(Meeting.analysis))
            .where(Meeting.id.in_(uuids))
        )

        if date_range:
            if date_range.get("start"):
                stmt = stmt.where(Meeting.meeting_date >= date_range["start"])
            if date_range.get("end"):
                stmt = stmt.where(Meeting.meeting_date <= date_range["end"])

        result = await db.execute(stmt)
        meetings = list(result.unique().scalars().all())

        return [
            RetrievedMeeting(
                meeting_id=str(m.id),
                title=m.title,
                summary=m.analysis.summary if m.analysis else None,
                meeting_date=m.meeting_date.isoformat() if m.meeting_date else None,
                meeting_type=m.meeting_type.value if m.meeting_type else None,
            )
            for m in meetings
        ]
