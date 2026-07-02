from datetime import datetime, timezone
from uuid import UUID

from langchain_mistralai import ChatMistralAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.repositories.meeting_analysis_repository import MeetingAnalysisRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.meeting_analysis_schema import MeetingAnalysisOutput, MeetingAnalysisResponse
from src.services.knowledge_service import KnowledgeService


ANALYSIS_PROMPT = """You are an AI meeting analyst. Analyze the following meeting transcript and extract structured information.

Return ONLY a valid JSON object with these exact fields:
- summary: A brief 2-3 sentence summary of the meeting
- goal: The main goal or purpose of the meeting
- outcomes: List of key outcomes achieved
- blockers: List of blockers or impediments
- future_meetings: List of future meetings mentioned
- requirements: List of objects with title, description (optional), priority (optional - low/medium/high/critical)
- structured_action_items: List of objects with title, description (optional), assignee (optional), due_date (optional)
- structured_decisions: List of objects with title, description (optional), decision_date (optional)
- structured_risks: List of objects with title, description (optional), severity (optional - low/medium/high/critical), mitigation (optional)
- structured_questions: List of objects with title, description (optional), answer (optional)

If a field has no information, use an empty list [].

Meeting Title: {title}
Meeting Date: {date}

Transcript:
{transcript}"""


class MeetingAnalysisService:
    def __init__(
        self,
        db: AsyncSession,
        repo: MeetingAnalysisRepository,
        meeting_repo: MeetingRepository,
        knowledge_service: KnowledgeService,
    ) -> None:
        self.db = db
        self.repo = repo
        self.meeting_repo = meeting_repo
        self.knowledge_service = knowledge_service
        self.llm = ChatMistralAI(
            model=settings.MISTRAL_LLM_MODEL,
            temperature=0.1,
        ).with_structured_output(MeetingAnalysisOutput)

    async def generate_analysis(self, meeting_id: UUID) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")
        if not meeting.transcript:
            raise ValueError("Meeting has no transcript")

        date_str = meeting.meeting_date.strftime("%Y-%m-%d") if meeting.meeting_date else "Not specified"

        result: MeetingAnalysisOutput = await self.llm.ainvoke(
            ANALYSIS_PROMPT.format(
                title=meeting.title,
                date=date_str,
                transcript=meeting.transcript,
            )
        )

        decisions_str = [d.title for d in result.structured_decisions]
        action_items_str = [a.title for a in result.structured_action_items]
        risks_str = [r.title for r in result.structured_risks]
        answered = [q.title for q in result.structured_questions if q.answer]
        unanswered = [q.title for q in result.structured_questions if not q.answer]

        analysis = await self.repo.upsert(
            meeting_id=meeting_id,
            summary=result.summary,
            goal=result.goal,
            outcomes=result.outcomes,
            decisions=decisions_str,
            action_items=action_items_str,
            answered_questions=answered,
            unanswered_questions=unanswered,
            risks=risks_str,
            blockers=result.blockers,
            future_meetings=result.future_meetings,
        )

        now = datetime.now(timezone.utc)
        analysis.generated_at = now
        await self.db.flush()

        await self.knowledge_service.extract_from_analysis(
            meeting_id=meeting_id,
            requirements=[r.model_dump() for r in result.requirements] if result.requirements else None,
            action_items=[a.model_dump() for a in result.structured_action_items] if result.structured_action_items else None,
            decisions=[d.model_dump() for d in result.structured_decisions] if result.structured_decisions else None,
            risks=[r.model_dump() for r in result.structured_risks] if result.structured_risks else None,
            questions=[q.model_dump() for q in result.structured_questions] if result.structured_questions else None,
        )

        return MeetingAnalysisResponse.model_validate(analysis).model_dump()

    async def get_analysis(self, meeting_id: UUID) -> dict | None:
        analysis = await self.repo.get_by_meeting(meeting_id)
        if analysis is None:
            return None
        return MeetingAnalysisResponse.model_validate(analysis).model_dump()
