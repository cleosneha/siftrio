from datetime import datetime

from pydantic import BaseModel, Field


class MeetingAnalysisCreate(BaseModel):
    summary: str | None = None
    goal: str | None = None
    outcomes: list = []
    decisions: list = []
    action_items: list = []
    answered_questions: list = []
    unanswered_questions: list = []
    risks: list = []
    blockers: list = []
    future_meetings: list = []


class MeetingAnalysisResponse(BaseModel):
    id: str
    meeting_id: str
    summary: str | None = None
    goal: str | None = None
    outcomes: list = []
    decisions: list = []
    action_items: list = []
    answered_questions: list = []
    unanswered_questions: list = []
    risks: list = []
    blockers: list = []
    future_meetings: list = []
    generated_at: str | None = None

class MeetingAnalysisOutput(BaseModel):
    summary: str = Field(description="Brief summary of the meeting")
    goal: str = Field(description="Main goal or purpose of the meeting")
    outcomes: list[str] = Field(default_factory=list, description="Key outcomes achieved")
    decisions: list[str] = Field(default_factory=list, description="Decisions made during the meeting")
    action_items: list[str] = Field(default_factory=list, description="Action items assigned")
    answered_questions: list[str] = Field(default_factory=list, description="Questions that were answered")
    unanswered_questions: list[str] = Field(default_factory=list, description="Questions left unanswered")
    risks: list[str] = Field(default_factory=list, description="Risks identified")
    blockers: list[str] = Field(default_factory=list, description="Blockers or impediments")
    future_meetings: list[str] = Field(default_factory=list, description="Future meetings mentioned")