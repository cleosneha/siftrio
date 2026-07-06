from datetime import date, datetime, time, timezone
from uuid import UUID

from langchain_mistralai import ChatMistralAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.repositories.meeting_analysis_repository import MeetingAnalysisRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.meeting_suggestion_repository import MeetingSuggestionRepository
from src.schemas.meeting_analysis_schema import MeetingAnalysisOutput, MeetingAnalysisResponse
from src.services.knowledge_service import KnowledgeService


ANALYSIS_PROMPT = """You are an AI meeting analyst. Analyze the following meeting transcript and extract structured information.

Return ONLY a valid JSON object with these exact fields:
- summary: A brief 2-3 sentence summary of the meeting
- goal: The main goal or purpose of the meeting
- outcomes: List of key outcomes achieved
- blockers: List of blockers or impediments
- future_meetings: List of future meetings mentioned (simple strings)
- requirements: List of objects with title, description (optional), priority (optional - low/medium/high/critical)
- structured_action_items: List of objects with title, description (optional), assignee (optional), due_date (optional)
- structured_decisions: List of objects with title, description (optional), decision_date (optional)
- structured_risks: List of objects with title, description (optional), severity (optional - low/medium/high/critical), mitigation (optional)
- structured_questions: List of objects with title, description (optional), answer (optional)
- suggested_meetings: List of objects with title, description (optional), meeting_date (optional - resolved ISO date YYYY-MM-DD), start_time (optional - HH:MM), end_time (optional - HH:MM), confidence (float 0-1), reason (string)

Extract the suggested_meetings field when participants agree to schedule a follow-up meeting. Resolve relative dates (e.g. "next Wednesday", "tomorrow", "next month") using the meeting date as reference. Resolve relative times (e.g. "4 PM" -> "16:00", "afternoon" -> "15:00"). If a date or time cannot be confidently determined, leave the field null. Do NOT guess or invent values.

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
        suggestion_repo: MeetingSuggestionRepository | None = None,
    ) -> None:
        self.db = db
        self.repo = repo
        self.meeting_repo = meeting_repo
        self.knowledge_service = knowledge_service
        self.suggestion_repo = suggestion_repo
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

        if self.suggestion_repo and result.suggested_meetings:
            await self._save_suggestions(meeting, result.suggested_meetings)

        return MeetingAnalysisResponse.model_validate(analysis).model_dump()

    async def _save_suggestions(self, meeting, suggested_meetings) -> None:
        for item in suggested_meetings:
            if not item.title or item.confidence < 0.3:
                continue

            parsed_date = None
            if item.meeting_date:
                try:
                    parsed_date = date.fromisoformat(item.meeting_date)
                except (ValueError, TypeError):
                    pass

            parsed_start = None
            if item.start_time:
                try:
                    parts = item.start_time.split(":")
                    parsed_start = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
                except (ValueError, IndexError, TypeError):
                    pass

            parsed_end = None
            if item.end_time:
                try:
                    parts = item.end_time.split(":")
                    parsed_end = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
                except (ValueError, IndexError, TypeError):
                    pass

            await self.suggestion_repo.create(
                meeting_id=meeting.id,
                client_id=meeting.client_id,
                project_id=meeting.project_id,
                title=item.title,
                description=item.description,
                suggested_date=parsed_date,
                start_time=parsed_start,
                end_time=parsed_end,
                confidence=item.confidence,
                reason=item.reason,
            )

    async def get_analysis(self, meeting_id: UUID) -> dict | None:
        analysis = await self.repo.get_by_meeting(meeting_id)
        if analysis is None:
            return None
        return MeetingAnalysisResponse.model_validate(analysis).model_dump()
